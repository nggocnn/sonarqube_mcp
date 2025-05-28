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
        """Initialize a SonarQube client instance.

        Args:
            base_url (str): The base URL of the SonarQube server (e.g., 'https://sonarqube.example.com').
            token (str): The authentication token for accessing the SonarQube API.
            organization (Optional[str], optional): The organization key for organization-specific requests. Defaults to None.
            timeout (float, optional): The timeout for API requests in seconds. Defaults to 10.0.

        Returns:
            None
        """
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
        """Set up the SonarQube client session and validate connection.

        Args:
            None

        Returns:
            None
        """
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
        """Send an HTTP request to a SonarQube API endpoint.

        Args:
            endpoint (str): The API endpoint path (e.g., '/api/system/health').
            method (str, optional): The HTTP method to use (e.g., 'GET', 'POST'). Defaults to 'GET'.
            params (Optional[Any], optional): Query parameters for the request. Defaults to None.
            payload (Optional[Dict[str, Any]], optional): The request body for POST requests. Defaults to None.
            content_type (str, optional): The Content-Type header for the request (e.g., 'application/json'). Defaults to 'application/json'.
            health_check (bool, optional): Whether to check client connection status before making the request. Defaults to True.
            raw_response (bool, optional): If True, return the raw response text; otherwise, parse JSON. Defaults to False.
            timeout (Optional[float], optional): Custom timeout for this request in seconds. Defaults to None (uses instance timeout).

        Returns:
            Any: The parsed JSON response if successful and raw_response is False, raw text if raw_response is True,
                or a dictionary with 'error' and 'details' keys on failure.
        """
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
        """Validate connection and authentication with SonarQube server.

        Args:
            None

        Returns:
            bool: True if connection and authentication are successful, False otherwise.
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

        Args:
            None

        Returns:
            Dict[str, Any]: Dictionary with system health details, including:
                - health: Overall status ("GREEN", "YELLOW", "RED", or None).
                - health_status: Human-readable status description.
                - nodes: List of application node details with their health and status.
                - causes: List of reasons for the current health status, if applicable.
                - On error, returns a dictionary with 'error' and 'details' keys.
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

        Args:
            None

        Returns:
            Dict[str, Any]: Dictionary containing system status information, including:
                - id: Unique identifier for the SonarQube instance.
                - version: SonarQube server version.
                - status: The running status ("STARTING", "UP", "DOWN", "RESTARTING", "DB_MIGRATION_NEEDED", "DB_MIGRATION_RUNNING").
                - system_status: Human-readable description of the status.
                - On error, returns a dictionary with 'error' and 'details' keys.
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
        """Check if the SonarQube server is reachable by sending a ping request.

        Args:
            None

        Returns:
            bool: True if the server responds with 'pong', False if the response is invalid or an error occurs.
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
        projects: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List SonarQube projects with optional filters.

        Args:
            analyzed_before (Optional[str], optional): ISO-8601 date string (e.g., '2023-10-19') to filter projects analyzed before this date. Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of projects per page (must be positive, max 500). Defaults to 100.
            search (Optional[str], optional): Search query to filter projects by name or key. Defaults to None.
            projects (Optional[str], optional): Comma-separated list of project keys to retrieve specific projects. Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary containing project list and pagination details, or an error response with 'error' and 'details' keys.
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
            "projects": projects,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def list_user_projects(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """Retrieve a list of SonarQube projects for which the authenticated user has 'Administer' permission.

        Args:
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of projects per page (must be positive, max 500). Defaults to 100.

        Returns:
            Dict[str, Any]: Dictionary containing a list of projects and pagination details, or an error response.
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
        """Retrieve a list of SonarQube projects that the authenticated user has permission to scan.

        Args:
            search (Optional[str], optional): Search query to filter projects by name or key. Defaults to None.

        Returns: Dict[str, Any]: Dictionary containing a list of scannable projects, or an error response.
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
        """Retrieve a list of analyses for a specified SonarQube project, with optional filters.

        Args:
            project_key (str): The key of the project to retrieve analyses for.
            category (Optional[str], optional): Event category to filter analyses (e.g., 'VERSION,QUALITY_GATE,OTHER'). Defaults to None. Possible values: VERSION, OTHER, QUALITY_PROFILE, QUALITY_GATE, DEFINITION_CHANGE, ISSUE_DETECTION, SQ_UPGRADE
            branch (Optional[str], optional): Branch key to filter analyses (not available in Community Edition). Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of analyses per page (must be positive, max 500). Defaults to 100.

        Returns:
            Dict[str, Any]: Dictionary containing a list of project analyses and pagination details, or an error response.
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

        endpoint = "/api/project_analyses/search"

        params = {
            "project": project_key,
            "category": str(category).upper() if category else None,
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

    def get_project_hotspots(
        self,
        project_key: str,
        file_paths: Optional[str] = None,
        only_mine: Optional[bool] = None,
        page: int = 1,
        page_size: int = 100,
        resolution: Optional[str] = None,
        status: Optional[str] = None,
    ):
        """
        Retrieve security hotspots in a SonarQube project.

        Retrieves a paginated list of security hotspots for a project, with optional filters by file paths, ownership, resolution, or status.

        Args:
            project_key (str): The key of the project (e.g., 'my_project'). Must be non-empty.
            file_paths (Optional[str], optional): Comma-separated list of file paths to filter hotspots (e.g., 'src/main.java,src/utils.js'). Defaults to None.
            only_mine (Optional[bool], optional): If True, return only hotspots assigned to the authenticated user. Defaults to None.
            page (int, optional): Page number for pagination (positive integer, default=1).
            page_size (int, optional): Number of hotspots per page (positive integer, max 500, default=100).
            resolution (Optional[str], optional): Filter by resolution (e.g., 'FIXED', 'SAFE'). Defaults to None. Possible values: FIXED, SAFE, ACKNOWLEDGED.
            status (Optional[str], optional): Filter by status (e.g., 'TO_REVIEW', 'REVIEWED'). Defaults to None. Possible values: TO_REVIEW, REVIEWED

        Returns:
            Dict[str, Any]: A dictionary with hotspot details and pagination info.
        """
        if not project_key or not project_key.strip():
            logger.error("project_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "project_key must be a non-empty string",
            }

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        endpoint = "/api/hotspots/search"

        params = {
            "project": project_key,
            "files": file_paths,
            "onlyMine": str(only_mine).lower() if only_mine is not None else None,
            "p": page,
            "ps": page_size,
            "resolution": resolution,
            "status": status,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List project hotspots failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_hotspot_detail(self, hotspot_key: str):
        """Retrieve detailed information about a specific security hotspot.

        Provides details such as the hotspot's location, rule, and status.

        Args:
            hotspot_key (str): The key of the hotspot (e.g., 'HOTSPOT123'). Must be non-empty.

        Returns:
            Dict[str, Any]: A dictionary with hotspot details.
        """
        if not hotspot_key or not hotspot_key.strip():
            logger.error("hotspot_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "hotspot_key must be a non-empty string",
            }

        endpoint = "/api/hotspots/show"

        response = self.__make_request(
            endpoint=endpoint, params={"hotspot": hotspot_key}
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get hotspot details failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_issues(
        self,
        additional_fields: Optional[str] = None,
        assigned: Optional[bool] = None,
        assignees: Optional[str] = None,
        authors: Optional[str] = None,
        branch: Optional[str] = None,
        components: Optional[str] = None,
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
        """Search for issues in SonarQube projects with specified filters.

        Args:
            additional_fields (Optional[str], optional): Comma-separated list of optional fields to include in the response (e.g., 'comments,rules'). Defaults to None. Possible values: _all, comments, languages, rules, ruleDescriptionContextKey, transitions, actions, users.
            assigned (Optional[bool], optional): Filter for assigned (True) or unassigned (False) issues. Defaults to None.
            assignees (Optional[str], optional): Comma-separated list of assignee logins, '__me__' for the current user. Defaults to None.
            authors (Optional[str], optional): Comma-separated list of SCM author accounts. For example: torvalds@linux-foundation.org,linux@fondation.org . Defaults to None.
            branch (Optional[str], optional): Branch key to filter issues (not available in Community Edition). Defaults to None.
            components (Optional[str], optional): Comma-separated list of component keys. Retrieve issues associated to a specific list of components (and all its descendants). A component can be a portfolio, project, module, directory or file.
            issue_statuses (Optional[str], optional): Comma-separated list of issue statuses (e.g., 'OPEN,CONFIRMED,FIXED'). Defaults to None. Possible values: OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED.
            issues (Optional[str], optional): Comma-separated list of issue keys to retrieve specific issues. Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of issues per page (must be positive, max 500). Defaults to 100.
            resolutions (Optional[str], optional): Comma-separated list of resolutions (e.g., 'FIXED,FALSE-POSITIVE'). Defaults to None. Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED.
            resolved (Optional[bool], optional): Filter for resolved (True) or unresolved (False) issues. Defaults to None.
            scopes (Optional[str], optional): Comma-separated list of scopes (e.g., 'MAIN,TEST'). Defaults to None. Possible values: MAIN, TEST.
            severities (Optional[str], optional): Comma-separated list of severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
            tags (Optional[str], optional): Comma-separated list of issue tags (e.g., 'security,convention'). Defaults to None.
            types (Optional[str], optional): Comma-separated list of issue types (e.g., 'BUG,VULNERABILITY'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY.

        Returns:
            Dict[str, Any]: Dictionary containing a list of issues and pagination details, or an error response.
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
            (
                "additionalFields",
                additional_fields.lower() if additional_fields else None,
            ),
            ("assigned", str(assigned).lower() if assigned is not None else None),
            ("assignees", assignees),
            ("branch", branch),
            ("components", components),
            ("issueStatuses", issue_statuses.upper() if issue_statuses else None),
            ("issues", issues),
            ("organization", self.organization),
            ("p", page),
            ("ps", page_size),
            ("resolutions", resolutions.upper() if resolutions else None),
            ("resolved", str(resolved).lower() if resolved is not None else None),
            ("scopes", scopes.upper() if scopes else None),
            ("severities", severities.upper() if severities else None),
            ("tags", tags),
            ("types", types.upper() if types else None),
        ]

        if authors:
            authors = authors.split(",")
            params.extend(("author", a) for a in authors)

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
        page_size: Optional[int] = 10,
    ) -> Dict[str, Any]:
        """Retrieve SCM authors for issues in a SonarQube project, with optional filtering.

        Args:
            project_key (Optional[str], optional): Project key to filter authors. Defaults to None.
            query (Optional[str], optional): Search query to filter authors by SCM account (partial match). Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of authors per page (must be positive, max 100). Defaults to 10.

        Returns:
            Dict[str, Any]: Dictionary containing a list of SCM authors, or an error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 10

        if page_size > 100:
            logger.warning("Page size capped at 100 by SonarQube API")
            page_size = 100

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
        """Retrieve a list of available metric types in SonarQube.

        Args:
            None

        Returns:
            Dict[str, Any]: Dictionary containing a list of metric types, or an error response.
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
        """Search for available metrics in SonarQube.

        Args:
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of metrics per page (must be positive, max 500). Defaults to 100.

        Returns:
            Dict[str, Any]: Dictionary containing a list of metrics and pagination details, or an error response.
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
        project_key: Optional[str] = None,
        analysis_id: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve quality gate status for a project or analysis.

        Args:
            project_key: Key of the project.
            analysis_id: ID of the analysis.
            branch: Branch name.

        Returns:
            Dict[str, Any]: Quality gate status or error response.
        """
        if (project_key is None) == (analysis_id is None):
            logger.error("Exactly one of analysis_id or project_key must be provided.")
            return {
                "error": "Invalid parameters",
                "details": "Exactly one of analysis_id or project_key must be provided.",
            }

        endpoint = "/api/qualitygates/project_status"
        params = {
            "projectKey": project_key,
            "analysisId": analysis_id,
            "branch": branch,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate project status failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_quality_profiles(
        self,
        defaults: bool = False,
        language: Optional[str] = None,
        project_key: Optional[str] = None,
    ):
        """Retrieve quality profiles in SonarQube.

        Retrieves quality profiles, optionally filtered by default profiles, language, or associated project.

        Args:
            defaults (bool, optional): If True, return only default profiles. Defaults to False.
            language (Optional[str], optional): Filter by programming language (e.g., 'java', 'py'). Defaults to None.
            project_key (Optional[str], optional): Filter by project key (e.g., 'my_project'). Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary with quality profile details.
        """

        endpoint = "/api/qualityprofiles/search"
        params = {
            "defaults": str(defaults).lower(),
            "language": language.lower() if language else None,
            "project": project_key,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List quality profiles failed: {response.get('details', 'Unknown error')}"
            )

        return response

    def get_rules(
        self,
        page: int = 1,
        page_size: int = 100,
        severities: Optional[str] = None,
        statuses: Optional[str] = None,
        types: Optional[str] = None,
    ):
        """Search for rules in SonarQube.

        Retrieves a paginated list of rules, optionally filtered by severity, status, or type.

        Args:
            page (int, optional): Page number for pagination (positive integer, default=1).
            page_size (int, optional): Number of rules per page (positive integer, max 500, default=100).
            severities (Optional[str], optional): Comma-separated list of severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
            statuses (Optional[str], optional): Comma-separated list of statuses (e.g., 'BETA,READY'). Defaults to None. Possible values: BETA, DEPRECATED, READY, REMOVED.
            types (Optional[str], optional): Comma-separated list of rule types (e.g., 'BUG,CODE_SMELL'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY, SECURITY_HOTSPOT.

        Returns:
            Dict[str, Any]: A dictionary with rule details and pagination info.
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

        endpoint = "/api/rules/search"

        params = {
            "p": page,
            "ps": page_size,
            "severities": severities.upper() if severities else None,
            "statuses": statuses.upper() if statuses else None,
            "types": types.upper() if types else None,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List rules failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_rule_details(self, rule_key: str, actives: Optional[bool] = False):
        """Retrieve detailed information about a specific SonarQube rule.

        Provides rule details, including description and active status in profiles if requested.

        Args:
            rule_key (str): The key of the rule (e.g., 'squid:S1234'). Must be non-empty.
            actives (Optional[bool], optional): If True, include active status in quality profiles. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary with rule details.
        """
        if not rule_key or not rule_key.strip():
            logger.error("rule_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "rule_key must be a non-empty string",
            }

        endpoint = "/api/rules/show"

        params = {
            "key": rule_key,
            "actives": str(actives).lower(),
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = self.__make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get rule details failed: {response.get('details', 'Unknown error')}"
            )
        return response

    def get_source(
        self, file_key: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retrieve source code for a specified file in a SonarQube project.

        Args:
            file_key (str): Key of the file to retrieve source code for (e.g., 'my_project:src/main/java/Example.java').
            start (Optional[int], optional): Starting line number (must be positive if provided). Defaults to None.
            end (Optional[int], optional): Ending line number (must be positive and >= start if provided). Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary containing source code lines, or an error response.
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
                "End line must be positive and greater than or equal to start line"
            )
            start = None
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
        """Retrieve SCM information for a specified file in a SonarQube project.

        Args:
            file_key (str): Key of the file to retrieve SCM information for (e.g., 'my_project:src/main/java/Example.java').
            start (Optional[int], optional): Starting line number (must be positive, starts at 1). Defaults to None.
            end (Optional[int], optional): Ending line number (must be positive and >= start, inclusive). Defaults to None.
            commits_by_line (Optional[bool], optional): If True, include commits for each line even if consecutive lines share
                the same commit; if False, group lines by commit. Defaults to False.

        Returns:
            Dict[str, Any]: Dictionary containing SCM information for the file, or an error response.
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
            start = None
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

    def get_source_raw(self, file_key) -> Any:
        """Retrieve raw source code for a specified file in a SonarQube project as plain text.

        Args:
            file_key (str): Key of the file to retrieve raw source code for (e.g., 'my_project:src/main/java/Example.java').

        Returns:
            str: Raw source code as a plain text string, or an error message as a string if the request fails.
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

    def get_source_issue_snippets(self, issue_key: str):
        """Retrieve code snippets associated with a specific SonarQube issue.

        Provides source code snippets around the issue's location for context.

        Args:
            issue_key (str): The key of the issue. Must be non-empty.

        Returns:
            Dict[str, Any]: A dictionary with code snippets for the issue.
        """
        if not issue_key or not issue_key.strip():
            logger.error("issue_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "issue_key must be a non-empty string",
            }

        endpoint = "/api/sources/issue_snippets"

        response = self.__make_request(
            endpoint=endpoint, params={"issueKey": issue_key}
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get issue snippets failed: {response.get('details', 'Unknown error')}"
            )
        return response
