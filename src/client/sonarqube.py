import logging
import requests
from typing import Optional, List, Dict, Any
from src.utils import utils


logger = logging.getLogger(__name__)


class SonarQubeClient:
    def __init__(self, base_url: str, token: str, organization: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.organization = organization
        self.connection_message = ""
        self.edition = ""
        self.connected = False

    def __make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
        timeout: int = 10,
        health_check: bool = True,
        raw_response: bool = False,
    ) -> Any:
        if health_check and not self.connected:
            return {
                "error": "SonarQube client is not healthy",
                "details": self.connection_message,
            }

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        if content_type:
            headers["Content-Type"] = content_type

        try:
            request_args = {
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }

            if method.upper() in ["POST"]:
                if payload is not None:
                    if content_type == "application/json":
                        request_args["json"] = payload
                    elif content_type == "application/x-www-form-urlencoded":
                        request_args["data"] = payload
                    else:
                        return {
                            "error": "Unsupported content type",
                            "details": f"Content-Type {content_type} is not supported.",
                        }
                else:
                    request_args["data"] = None

            response = requests.request(**request_args)
            response.raise_for_status()

            if raw_response:
                return response.text
            elif "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            else:
                return {"text": response.text}

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return {"error": f"HTTP {status_code}", "details": str(e)}
        except requests.exceptions.JSONDecodeError as e:
            return {"error": "JSON serialization error", "details": str(e)}
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "details": str(e)}
        except ValueError as e:
            return {"error": "Invalid request", "details": str(e)}

    def validate_connection(self) -> bool:
        """Validate SonarQube connection and access token"""
        if not self.base_url or not self.token:
            self.connection_message = "Missing SONARQUBE_URL or SONARQUBE_TOKEN"
            logger.error(self.connection_message)
            return False

        authN_validation = self.__make_request(
            endpoint="/api/authentication/validate", health_check=False
        )
        if "error" in authN_validation:
            self.connection_message = authN_validation["details"]
            logger.error(self.connection_message)
            return False

        current_user = self.__make_request(
            endpoint="/api/users/current", health_check=False
        )
        if "error" not in current_user:
            self.connection_message = f"Connected to SonarQube server at {self.base_url}. Authenticated as {current_user.get('login', 'unknown user')}"
        else:
            self.connection_message = f"Connected to SonarQube server at {self.base_url}"

        logger.info(self.connection_message)

        self.connected = True

        return True

    def get_system_health(self) -> Dict[str, Any]:
        endpoint = "/api/system/health"
        response = self.__make_request(endpoint=endpoint)

        if "error" in response:
            logger.error(f"System health check failed: {response}")
            return response

        health_status_map = {
            "GREEN": "SonarQube is fully operational",
            "YELLOW": "SonarQube is usable, but it needs attention in order to be fully operational",
            "RED": "SonarQube is not operational",
        }

        health_status = response.get("health")
        response["health_status"] = health_status_map.get(health_status)

        for node in response.get("nodes", []):
            node_health_status = node.get("health")
            node["health_status"] = health_status_map.get(node_health_status)

        logger.info(f"SonarQube health: {health_status} - {response["health_status"]}")

        return response

    def get_system_status(self) -> Dict[str, Any]:
        endpoint = "/api/system/status"
        response = self.__make_request(endpoint=endpoint)

        if "error" in response:
            logger.error(f"System status check failed: {response}")
            return response

        system_status_map = {
            "STARTING": "SonarQube Web Server is up and serving some Web Services but initialization is still ongoing",
            "UP": "SonarQube instance is up and running",
            "DOWN": "SonarQube instance is up but not running because migration has failed or some other reason (check logs).",
            "RESTARTING": "SonarQube instance is still up but a restart has been requested.",
            "DB_MIGRATION_NEEDED": "Database migration is required.",
            "DB_MIGRATION_RUNNING": "DB migration is runnings",
        }

        system_status = response.get("status")
        response["system_status"] = system_status_map.get(system_status)

        logger.info(f"SonarQube status: {system_status} - {response["system_status"]}")
        return response

    def system_ping(self) -> bool:
        endpoint = "/api/system/ping"
        response = self.__make_request(endpoint=endpoint, raw_response=True)
        return self.connected and "pong" == response.lower()

    def list_projects(
        self,
        analyzed_before: str = None,
        page: int = 1,
        page_size: int = 100,
        search: str = None,
    ) -> Dict[str, Any]:
        endpoint = "/api/projects/search"

        params = {
            "analyzedBefore": analyzed_before,
            "organization": self.organization,
            "p": page,
            "ps": page_size,
            "q": search,
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self.__make_request(endpoint=endpoint, params=params)

    def list_user_projects(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        endpoint = "/api/projects/search_my_projects"

        params = {"p": page, "ps": page_size}

        return self.__make_request(endpoint=endpoint, params=params)

    def list_user_scannable_projects(self, search: str = None) -> Dict[str, Any]:
        endpoint = "/api/projects/search_my_scannable_projects"

        params = {"q": search} if search else {}

        return self.__make_request(endpoint=endpoint, params=params)

    def get_issues(
        self,
        project_keys: Optional[List[str]],
        additional_fields: Optional[List[str]] = None,
        assigned: Optional[bool] = None,
        assignees: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        branch: str = None,
        issue_statuses: Optional[List[str]] = None,
        issues: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 100,
        resolutions: Optional[List[str]] = None,
        resolved: Optional[bool] = None,
        scopes: Optional[List[str]] = None,
        severities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        endpoint = "/api/issues/search"

        params[
            ("additionalFields", utils.join_string_list(additional_fields)),
            ("assigned", str(assigned) if assigned else None),
            ("assignees", utils.join_string_list(assignees)),
            ("branch", branch),
            ("issueStatuses", utils.join_string_list(issue_statuses)),
            ("issues", utils.join_string_list(issues)),
            ("componentKeys", utils.join_string_list(project_keys)),
            ("organization", self.organization),
            ("p", page),
            ("ps", page_size),
            ("resolutions", utils.join_string_list(resolutions)),
            ("resolved", str(resolved) if resolved else None),
            ("scopes", utils.join_string_list(scopes)),
            ("severities", utils.join_string_list(severities)),
            ("tags", utils.join_string_list(tags)),
            ("types", utils.join_string_list(types)),
        ]

        if authors:
            params += [("author", a) for a in authors]

        params = [(k, v) for k, v in params if v is not None]

        return self.__make_request(endpoint=endpoint, params=params)

    def get_scm_authors(
        self,
        project_key: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 100,
    ) -> Dict[str, Any]:
        endpoint = "/api/issues/authors"

        params = {"project": project_key, "p": page, "ps": page_size}

        params = [(k, v) for k, v in params if v is not None]

        return self.__make_request(endpoint=endpoint, params=params)

    def get_metrics_type(self) -> Dict[str, Any]:
        endpoint = "/api/metrics/types"

        return self.__make_request(endpoint=endpoint)

    def get_metrics(
        self, page: Optional[int] = 1, page_size: Optional[int] = 100
    ) -> Dict[str, Any]:
        endpoint = "/api/metrics/search"
        params = {"p": page, "ps": page_size}

        return self.__make_request(endpoint=endpoint, params=params)

    def get_quality_gates(self) -> Dict[str, Any]:
        endpoint = "/api/qualitygates/list"

        return self.__make_request(endpoint=endpoint)

    def get_quality_gates_details(self, name: str) -> Dict[str, Any]:
        endpoint = "/api/qualitygates/show"

        params = {"name": name}

        return self.__make_request(endpoint=endpoint, params=params)

    def get_quality_gates_by_project(self, project_key: str):
        endpoint = "api/qualitygates/get_by_project"

        params = {"project": project_key}

        return self.__make_request(endpoint=endpoint, params=params)

    def get_quality_gates_project_status(
        self,
        analysis_id: Optional[str] = None,
        branch: Optional[str] = None,
        project_id: Optional[str] = None,
        project_key: Optional[str] = None,
        pull_request: Optional[str] = None,
    ) -> Dict[str, Any]:
        endpoint = "/api/qualitygates/project_status"

        params = {
            "analysisId": analysis_id,
            "branch": branch,
            "projectId": project_id,
            "projectKey": project_key,
            "pullRequest": pull_request,
        }

        params = [(k, v) for k, v in params if v is not None]

        return self.__make_request(endpoint=endpoint, params=params)

    def get_source(
        self, file_key: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> Dict[str, Any]:
        endpoint = "/api/sources/show"

        params = {"key": file_key, "from": start, "to": end}

        params = [(k, v) for k, v in params if v is not None]

        return self.__make_request(endpoint=endpoint, params=params)

    def get_scm_info(
        self,
        file_key: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        commits_by_line: Optional[bool] = False,
    ) -> Dict[str, Any]:
        endpoint = "/api/sources/scm"

        params = {
            "key": file_key,
            "from": start,
            "to": end,
            "commits_by_line": str(commits_by_line),
        }

        params = [(k, v) for k, v in params if v is not None]
        return self.__make_request(endpoint=endpoint, params=params)

    def get_source_raw(self, file_key) -> Dict[str, Any]:
        endpoint = "/api/sources/raw"

        return self.__make_request(endpoint=endpoint, params={"key": file_key})
