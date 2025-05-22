import logging
import os
import requests
import json
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urljoin
from utils import utils


logger = logging.getLogger(__name__)

class SonarQubeClient:
    def __init__(self, base_url: str, token: str, orgnization: Optional[str]):
        self.base_url = base_url
        self.token = token
        self.orgnization = orgnization
        self.is_healthy = False
        self.health_message = ""
        self.edition = ""

    def check_health(self) -> bool:
        """Validate SonarQube connection and access token"""
        if not self.base_url or not self.token:
            self.health_message = "Missing SONARQUBE_URL or SONARQUBE_TOKEN"
            logger.error(self.health_message)
            return False

        authen_validation = self.__make_request(endpoint="/api/authentication/validate", health_check=False)
        if "error" in authen_validation:
            self.health_message = authen_validation["details"]
            logger.error(self.health_message)
            return False
        
        self.is_healthy = True

        current_user = self.__make_request(endpoint="/api/users/current", health_check=False)
        if "error" not in current_user:
            self.health_message = f"Connected to SonarQube server at {self.base_url}. Athenticated as {current_user.get("login", "unknown user")}"
        else:
            self.health_message = f"Connected to SonarQube server at {self.base_url}"    
        
        logger.info(self.health_message)
        
    def __make_request(
        self,
        endpoint: str,
        method: str="GET",
        params: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
        timeout: int = 10,
        health_check: bool = True,
        raw_response: bool = False
    ) -> Any:
        if health_check and not self.is_healthy:
            return {
                "error": "SonarQube client is not healthy", 
                "detail": self.health_message
            }

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        auth = requests.auth.HTTPBearerAuth(self.token)
        headers = {"Accept": "application/json"}

        if content_type:
            headers["Content-Type"] = content_type

        try:
            request_args = {
                "method": method,
                "url": url,
                "auth": auth,
                "params": params,
                "headers": headers,
                "timeout": timeout
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
                            "details": f"Content-Type {content_type} is not supported."
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
                return {
                    "text": response.text
                }

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return {"error": f"HTTP {status_code} {response.get(status_code, 'Unknown HTTP error')}", "details": str(e)}
        except requests.exceptions.JSONDecodeError as e:
            return {"error": "JSON serialization error", "details": str(e)}
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "details": str(e)}
        except ValueError as e:
            return {"error": "Invalid request", "details": str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        endpoint = "/api/system/health"
        response = self.__make_request(endpoint=endpoint)

        if "error" in response:
            logger.error(f"System health check failed: {response}")
            return response

        health_status_map = {
            "GREEN": "SonarQube is fully operational",
            "YELLOW": "SonarQube is usable, but it needs attention in order to be fully operational",
            "RED": "SonarQube is not operational"
        }

        health_status = response.get("health")
        response["health_status"] = health_status_map.get(health_status)

        for node in response.get("nodes", []):
            node_health_status = node.get("health")
            node["health_status"] = health_status_map.get(node_health_status)

        logger.info(f"SonarQube health: {health_status} - {response["description"]}")

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
            "DB_MIGRATION_RUNNING": "DB migration is runnings"
        }

        system_status = response.get("status")
        response["system_status"] = system_status_map.get(system_status)

        logger.info(f"SonarQube status: {system_status} - {response["system_status"]}")
        return response

    def system_ping(self) -> bool:
        endpoint = "/api/system/ping"
        response = self.__make_request(endpoint=endpoint, raw_response=True)
        return "pong" == response.lower()


    def list_projects(self, analyzed_before: str = None, organization: str = None, page: int = 1, page_size: int = 100, search: str = None) -> Dict[str, Any]:
        endpoint = "/api/projects/search"

        params = {
            "analyzedBefore": analyzed_before,
            "organization": organization,
            "p": page,
            "ps": page_size,
            "q": search
        }

        params = {k: v for k, v in params.items() if v is not None}

        return self.__make_request(endpoint=endpoint, params=params)

    def list_user_projects(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        endpoint = "/api/projects/search_my_projects"

        params = {
            "p": page,
            "ps": page_size
        }

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
        orgnization: str = None,
        page: int = 1,
        page_size: int = 100,
        resolutions: Optional[List[str]] = None,
        resolved: Optional[bool] = None,
        scopes: Optional[List[str]] = None,
        serverities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        endpoint = "/api/issues/search"

        params = Union[Dict[str, Any], List[tuple]] = [
            ("additionalFields", utils.join_string_list(additional_fields)),
            ("assigned", str(assigned) if assigned else None),
            ("assignees", utils.join_string_list(assignees)),
            ("branch", branch),
            ("issueStatuses", utils.join_string_list(issue_statuses)),
            ("issues", utils.join_string_list(issues)),
            ("componentKeys", utils.join_string_list(project_keys)),
            ("issueStatuses", issue_statuses.join("'")),
            ("orgnization", orgnization),
            ("p", page),
            ("ps", page_size),
            ("resolutions", utils.join_string_list(resolutions)),
            ("resolved", str(resolved) if resolved else None),
            ("scopes", utils.join_string_list(scopes)),
            ("serverities", utils.join_string_list(serverities)),
            ("tags", utils.join_string_list(tags)),
            ("type", utils.join_string_list(type))
        ]

        if authors:
            params += [("author", a) for a in authors]


        params = [(k, v) for k, v in params if v is not None]

        return self.__make_request(endpoint=endpoint, params=params)







