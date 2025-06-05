import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeHotSpot(SonarQubeBase):

    async def get_project_hotspots(
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

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List project hotspots failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_hotspot_detail(self, hotspot_key: str):
        """Retrieve detailed information about a specific security hotspot.

        Provides details such as the hotspot's location, rule, and status.

        Args:
            hotspot_key (str): The key of the hotspot (e.g., 'HOTSPOT123'). Must be non-empty.

        Returns:
            sDict[str, Any]: A dictionary with hotspot details.
        """
        if not hotspot_key or not hotspot_key.strip():
            logger.error("hotspot_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "hotspot_key must be a non-empty string",
            }

        endpoint = "/api/hotspots/show"

        response = await self._make_request(
            endpoint=endpoint, params={"hotspot": hotspot_key}
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get hotspot details failed: {response.get('details', 'Unknown error')}"
            )
        return response
