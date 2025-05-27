import logging
import httpx
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SonarQubeClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        organization: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.organization = organization
        self.timeout = timeout
        self.connection_message = ""
        self.version = ""
        self.connected = False
        self.session = None

    @classmethod
    def create(
        cls,
        base_url: str,
        token: str,
        organization: Optional[str] = None,
        timeout: float = 10.0,
    ):
        instance = cls(base_url, token, organization, timeout)
        instance.__setup()
        return instance

    def __setup(self):
        self.session = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=httpx.Timeout(timeout=self.timeout),
        )
        self.__validate_connection()

    def __make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
        health_check: bool = True,
        raw_response: bool = False,
        timeout: Optional[float] = None,
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

        request_args = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "headers": headers,
            "timeout": httpx.Timeout(timeout=timeout or self.timeout),
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

        try:
            response = self.session.request(**request_args)
            response.raise_for_status()

            if raw_response:
                return response.text

            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()

            return response

        except httpx.TimeoutException as e:
            error_msg = f"Request timed out after {timeout or self.timeout} seconds"
            logger.error(f"{error_msg}: {str(e)}")
            return {"error": "Timeout", "details": error_msg}
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            return {"error": f"HTTP {e.response.status_code}", "details": error_msg}
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return {"error": "Request failed", "details": error_msg}
        except json.JSONDecodeError as e:
            error_msg = f"JSON serialization error: {str(e)}"
            logger.error(error_msg)
            return {"error": "JSON serialization error", "details": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {"error": "Exception", "details": error_msg}

    def __enter__(self):
        self.__setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.aclose()

    def __validate_connection(self) -> bool:
        """Validate SonarQube connection and access token.

        Returns:
            bool: True if connection and authentication are valid, False otherwise.
        """
        if not self.base_url or not self.token:
            self.connection_message = "Missing SONARQUBE_URL or SONARQUBE_TOKEN"
            logger.error(self.connection_message)
            return False

        auth_response = self.__make_request(
            endpoint="/api/authentication/validate", health_check=False
        )

        if isinstance(auth_response, dict) and "error" in auth_response:
            self.connection_message = auth_response.get(
                "details", "Authentication validation failed."
            )
            logger.error(f"Authentication failed: {self.connection_message}")
            return False

        if not (isinstance(auth_response, dict) and auth_response.get("valid", False)):
            self.connection_message = "Invalid authentication response from SonarQube"
            logger.error(self.connection_message)
            return False

        user_response = self.__make_request(
            endpoint="/api/users/current", health_check=False
        )

        if isinstance(user_response, dict) and "error" not in user_response:
            self.connection_message = f"Connected to SonarQube server at {self.base_url}. Authenticated as {user_response.get('login', 'unknown user')}"
            logger.info(self.connection_message)
        else:
            self.connection_message = (
                f"Connected to SonarQube server at {self.base_url}"
            )
            logger.warning(self.connection_message)

        try:
            version_response = self.__make_request(
                endpoint="/api/server/version", health_check=False, raw_response=True
            )
            if isinstance(version_response, str):
                self.version = version_response
            else:
                logger.warning(
                    "Failed to fetch server version: Invalid response format"
                )
        except Exception as e:
            logger.warning(f"Failed to fetch server version: {str(e)}")

        self.connected = True
        return True

    def get_system_health(self) -> Dict[str, Any]:
        """Retrieve SonarQube system health status.

        Returns:
            Dict[str, Any]: System health information with mapped status descriptions.
        """
        endpoint = "/api/system/health"
        response = self.__make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"System health check failed: {response.get('details', 'Unknown error')}"
            )
            return response

        if not isinstance(response, dict):
            error_msg = f"Invalid response format from {endpoint}: expected dict, got {type(response)}"
            logger.error(error_msg)
            return {"error": "Invalid response", "details": error_msg}

        health_status_map = {
            "GREEN": "SonarQube is fully operational",
            "YELLOW": "SonarQube is usable, but it needs attention in order to be fully operational",
            "RED": "SonarQube is not operational",
            None: "Unknown health status",
        }

        health_status = response.get("health")
        response["health_status"] = health_status_map.get(
            health_status, health_status_map[None]
        )

        nodes = response.get("nodes", [])
        if not isinstance(nodes, list):
            logger.warning(
                f"Invalid nodes format in response: expected list, got {type(nodes)}"
            )
            nodes = []

        for node in nodes:
            if isinstance(node, dict):
                node_health_status = node.get("health")
                node["health_status"] = health_status_map.get(
                    node_health_status, health_status_map[None]
                )
            else:
                logger.warning(f"Invalid node format: expected dict, got {type(node)}")
                node["health_status"] = health_status_map[None]

        logger.info(f"SonarQube health: {health_status} - {response['health_status']}")
        return response

    def get_system_status(self) -> Dict[str, Any]:
        """Retrieve SonarQube system status.

        Returns:
            Dict[str, Any]: System status information with mapped status description.
        """
        endpoint = "/api/system/status"
        response = self.__make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(f"System status check failed: {response}")
            return response

        if not isinstance(response, dict):
            error_msg = f"Invalid response format from {endpoint}: expected dict, got {type(response)}"
            logger.error(error_msg)
            return {"error": "Invalid response", "details": error_msg}

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

        logger.info(f"SonarQube status: {system_status} - {response['system_status']}")
        return response

    def system_ping(self) -> bool:
        """Ping the SonarQube server to check if it is reachable.

        Returns:
            bool: True if the server responds with 'pong', False otherwise.
        """
        endpoint = "/api/system/ping"
        response = self.__make_request(endpoint=endpoint, raw_response=True)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"System ping failed: {response.get('details', 'Unknown error')}"
            )
            return False

        if not isinstance(response, str):
            logger.error(
                f"System ping failed: Expected string response, got {type(response)}"
            )
            return False

        return "pong" == response

    def list_projects(
        self,
        analyzed_before: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List SonarQube projects with optional filters.

        Args:
            analyzed_before: Optional ISO-8601 date string to filter projects analyzed before this date.
            page: Page number for pagination (must be positive).
            page_size: Number of projects per page (must be positive, max 500).
            search: Optional search query to filter projects by name.

        Returns:
            Dict[str, Any]: Project list or error response.
        """

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/projects/search"

        params = {
            "analyzedBefore": analyzed_before,
            "organization": self.organization,
            "p": page,
            "ps": page_size,
            "q": search,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def list_user_projects(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """List projects accessible to the authenticated user.

        Args:
            page: Page number for pagination (must be positive).
            page_size: Number of projects per page (must be positive, max 500).

        Returns:
            Dict[str, Any]: User project list or error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/projects/search_my_projects"

        params = {"p": page, "ps": page_size}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List user projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def list_user_scannable_projects(
        self, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List scannable projects for the authenticated user.

        Args:
            search: Optional search query to filter projects by name.

        Returns:
            Dict[str, Any]: Scannable project list or error response.
        """
        endpoint = "/api/projects/search_my_scannable_projects"
        params = {"q": search} if search else {}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List scannable projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def list_project_analyses(
        self,
        project_key: str,
        category: Optional[str] = None,
        branch: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ):

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/project_analyses/search"

        params = {
            "project": project_key,
            "category": category,
            "branch": branch,
            "p": page,
            "ps": page_size,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List project analyses failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_issues(
        self,
        project_keys: str,
        additional_fields: Optional[str] = None,
        assigned: Optional[bool] = None,
        assignees: Optional[str] = None,
        authors: Optional[str] = None,
        branch: Optional[str] = None,
        issue_statuses: Optional[str] = None,
        issues: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        resolutions: Optional[str] = None,
        resolved: Optional[bool] = None,
        scopes: Optional[str] = None,
        severities: Optional[str] = None,
        tags: Optional[str] = None,
        types: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for issues in SonarQube.

        Args:
            project_keys: List of project keys to filter issues.
            additional_fields: Additional fields to include in response.
            assigned: Filter issues by assignment status.
            assignees: List of assignees to filter issues.
            authors: List of authors to filter issues.
            branch: Branch to filter issues.
            issue_statuses: List of issue statuses to filter.
            issues: List of issue keys to filter.
            page: Page number for pagination (must be positive).
            page_size: Number of issues per page (must be positive, max 500).
            resolutions: List of resolutions to filter issues.
            resolved: Filter issues by resolved status.
            scopes: List of scopes to filter issues.
            severities: List of severities to filter issues.
            tags: List of tags to filter issues.
            types: List of issue types to filter.

        Returns:
            Dict[str, Any]: Issue list or error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/issues/search"

        params = [
            ("additionalFields", additional_fields),
            ("assigned", str(assigned) if assigned else None),
            ("assignees", assignees),
            ("branch", branch),
            ("issueStatuses", issue_statuses),
            ("issues", issues),
            ("componentKeys", project_keys),
            ("organization", self.organization),
            ("p", page),
            ("ps", page_size),
            ("resolutions", resolutions),
            ("resolved", str(resolved) if resolved else None),
            ("scopes", scopes),
            ("severities", severities),
            ("tags", tags),
            ("types", types),
        ]

        if authors:
            params += [("author", a) for a in authors]

        params = [(k, v) for k, v in params if v is not None]

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get issues failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_issues_authors(
        self,
        project_key: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 100,
    ) -> Dict[str, Any]:
        """Retrieve SCM authors for a project.

        Args:
            project_key: Optional project key to filter authors.
            page: Page number for pagination (must be positive).
            page_size: Number of authors per page (must be positive, max 500).

        Returns:
            Dict[str, Any]: List of SCM authors or error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/issues/authors"

        params = {"project": project_key, "p": page, "ps": page_size}
        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get SCM authors failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_metrics_type(self) -> Dict[str, Any]:
        """Retrieve available metric types.

        Returns:
            Dict[str, Any]: List of metric types or error response.
        """
        endpoint = "/api/metrics/types"
        response = self.__make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get metrics types failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_metrics(
        self, page: Optional[int] = 1, page_size: Optional[int] = 100
    ) -> Dict[str, Any]:
        """Retrieve available metrics.

        Args:
            page: Page number for pagination (must be positive).
            page_size: Number of metrics per page (must be positive, max 500).

        Returns:
            Dict[str, Any]: List of metrics or error response.
        """
        if page < 1 or page_size < 1:
            logger.error("Page and page_size must be positive integers")
            return {
                "error": "Invalid parameters",
                "details": "Page and page_size must be positive",
            }
        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/metrics/search"
        params = {"p": page, "ps": page_size}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get metrics failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_quality_gates(self) -> Dict[str, Any]:
        """Retrieve list of quality gates.

        Returns:
            Dict[str, Any]: List of quality gates or error response.
        """
        endpoint = "/api/qualitygates/list"

        response = self.__make_request(endpoint=endpoint)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gates failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_quality_gates_details(self, name: str) -> Dict[str, Any]:
        """Retrieve details of a specific quality gate.

        Args:
            name: Name of the quality gate.

        Returns:
            Dict[str, Any]: Quality gate details or error response.
        """
        if not name:
            logger.error("Quality gate name must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "Quality gate name must not be empty",
            }

        endpoint = "/api/qualitygates/show"
        params = {"name": name}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate details failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_quality_gates_by_project(self, project_key: str) -> Dict[str, Any]:
        """Retrieve quality gate associated with a project.

        Args:
            project_key: Key of the project.

        Returns:
            Dict[str, Any]: Quality gate details or error response.
        """
        if not project_key:
            logger.error("Project key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "Project key must not be empty",
            }

        endpoint = "/api/qualitygates/get_by_project"
        params = {"project": project_key}
        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate by project failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_quality_gates_project_status(
        self,
        analysis_id: Optional[str] = None,
        branch: Optional[str] = None,
        project_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve quality gate status for a project or analysis.

        Args:
            analysis_id: ID of the analysis.
            branch: Branch name.
            project_key: Key of the project.

        Returns:
            Dict[str, Any]: Quality gate status or error response.
        """
        if not (analysis_id or project_key):
            logger.error("At least one of analysis_id or project_key must be provided")
            return {
                "error": "Invalid parameters",
                "details": "At least one parameter must be provided",
            }

        endpoint = "/api/qualitygates/project_status"
        params = {
            "analysisId": analysis_id,
            "branch": branch,
            "projectKey": project_key,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate project status failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_source(
        self, file_key: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retrieve source code for a file.

        Args:
            file_key: Key of the file.
            start: Starting line number (must be positive if provided).
            end: Ending line number (must be positive and >= start if provided).

        Returns:
            Dict[str, Any]: Source code or error response.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        if start is not None and start < 1:
            logger.error("Start line must be positive")
            start = None

        if end is not None and (end < 1 or (start is not None and end < start)):
            logger.error(
                "End line must be positive and greater than or equal to start line"
            )
            end = None

        endpoint = "/api/sources/show"
        params = {"key": file_key, "from": start, "to": end}
        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get source failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_scm_info(
        self,
        file_key: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        commits_by_line: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """Retrieve SCM information for a file.

        Args:
            file_key: Key of the file.
            start: Starting line number (must be positive if provided).
            end: Ending line number (must be positive and >= start if provided).
            commits_by_line: Whether to include commits by line.

        Returns:
            Dict[str, Any]: SCM information or error response.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        if start is not None and start < 1:
            logger.warning("Start line must be positive")
            start = None

        if end is not None and (end < 1 or (start is not None and end < start)):
            logger.warning(
                "End line must be positive and greater than or equal to start line."
            )
            end = None

        endpoint = "/api/sources/scm"

        params = {
            "key": file_key,
            "from": start,
            "to": end,
            "commits_by_line": commits_by_line,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get SCM info failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_source_raw(self, file_key) -> str:
        """Retrieve raw source code for a file.

        Args:
            file_key: Key of the file.

        Returns:
            str: Raw source code or error response as a string.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        endpoint = "/api/sources/raw"

        response = self.__make_request(
            endpoint=endpoint, params={"key": file_key}, raw_response=True
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get raw source failed: {response.get('details', 'Unknown error')}"
            )
        return response
