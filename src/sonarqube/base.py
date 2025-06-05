import httpx
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import json

logger = logging.getLogger(__name__)


class SonarQubeBase:
    def __init__(
        self,
        base_url: str,
        token: str,
        organization: Optional[str] = None,
        timeout: float = 10.0,
        max_connections: int = 20,
    ):
        """Initialize a SonarQube client instance.

        Args:
          base_url (str): The base URL of the SonarQube server (e.g., 'https://sonarqube.example.com').
          token (str): The authentication token for accessing the SonarQube API.
          organization (Optional[str], optional): The organization key for organization-specific requests. Defaults to None.
          timeout (float, optional): The timeout for API requests in seconds. Defaults to 10.0.
          max_connections (int, optional): Maximum number of concurrent HTTP connections. Defaults to 20.
        """
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.organization = organization.strip() if organization else None
        self.timeout = timeout
        self.max_connections = max_connections
        self.connection_message = ""
        self.version = ""
        self._session = None

    @classmethod
    async def create(cls, **kwargs):
        """Create and initialize a SonarQube client instance asynchronously."""
        instance = cls(**kwargs)
        await instance._setup()
        return instance

    async def _setup(self):
        """Set up the SonarQube client session and validate connection."""
        if self._session:
            await self._session.aclose()

        self._session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(timeout=self.timeout),
            limits=httpx.Limits(
                max_connections=self.max_connections, max_keepalive_connections=5
            ),
        )

        if not await self._validate_connection():
            await self._session.aclose()
            self._session = None
            raise ConnectionError(
                f"Failed to connect to SonarQube server at {self.base_url}: {self.connection_message}"
            )

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        payload: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
        health_check: bool = False,
        timeout: Optional[float] = None,
    ) -> Any:
        """Send an async HTTP request to a SonarQube API endpoint.

        Args:
            endpoint (str): The API endpoint path (e.g., '/api/system/health').
            method (str, optional): The HTTP method to use (e.g., 'GET', 'POST'). Defaults to 'GET'.
            params (Dict[str, Any], optional): Query parameters for the request. Defaults to None.
            payload (Dict[str, Any], optional): The request body for POST requests. Defaults to None.
            raw_response (bool, optional): If True, return the raw response text; otherwise, parse JSON. Defaults to False.
            max_retries (int, optional): Maximum number of retries for failed requests. Defaults to 3.
            backoff_factor (float, optional): Factor for exponential backoff between retries. Defaults to 1.0.
            timeout (float, optional): Custom timeout for this request in seconds. Defaults to None (uses instance timeout).

        Returns:
            Any: The parsed JSON response if successful and raw_response is False, raw text if raw_response is True,
            or a dictionary with 'error' and 'details' keys on failure.
        """
        if not self._session:
            await self._setup()

        url = urljoin(self.base_url, endpoint.lstrip("/"))

        request_args = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "timeout": httpx.Timeout(timeout=timeout or self.timeout),
        }

        if method.upper() == "POST" and payload is not None:
            request_args["json"] = payload
            request_args["headers"] = {
                **request_args["headers"],
                "Content-Type": "application/json",
            }

        try:
            response = await self._session.request(**request_args)
            response.raise_for_status()

            if raw_response:
                return response.text

            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()

            return response

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            if e.response.status_code not in (500, 502, 503, 504) or health_check:
                return {"error": f"HTTP {e.response.status_code}", "details": error_msg}
            raise

        except httpx.TimeoutException as e:
            error_msg = f"Request timed out after {timeout or self.timeout} seconds"
            logger.error(f"{error_msg}: {str(e)}")
            raise

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

    async def _validate_connection(self) -> bool:
        """Validate connection and authentication with SonarQube server.

        Returns:
            bool: True if connection and authentication are successful, False otherwise.
        """
        if not self.base_url or not self.token:
            self.connection_message = "Missing SONARQUBE_URL or SONARQUBE_TOKEN"
            logger.error(self.connection_message)
            return False

        auth_response = await self._make_request(
            endpoint="/api/authentication/validate", health_check=True
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

        user_response = await self._make_request(
            endpoint="/api/users/current", health_check=True
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
            version_response = await self._make_request(
                endpoint="/api/server/version", health_check=True, raw_response=True
            )
            if isinstance(version_response, str):
                self.version = version_response
            else:
                logger.warning(
                    "Failed to fetch server version: Invalid response format"
                )
        except Exception as e:
            logger.warning(f"Failed to fetch server version: {str(e)}")

        return True
