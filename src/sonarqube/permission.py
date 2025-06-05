import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubePermission(SonarQubeBase):

    async def add_group_permission(
        self, group_name: str, permission: str, project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        endpoint = "/api/permissions/add_group"

        params = {
            "groupName": group_name,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, method="POST", params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Assign group permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def remove_group_permission(
        self, group_name: str, permission: str, project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        endpoint = "/api/permissions/remove_group"

        params = {
            "groupName": group_name,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, method="POST", params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Remove group permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_group_permission(
        self, project_key: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 100:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 100

        endpoint = "/api/permissions/groups"

        params = {
            "projectKey": project_key,
            "p": page,
            "ps": page_size,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get group permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def add_user_permission(self, username: str, permission: str, project_key: Optional[str] = None) -> Dict[str, Any]:
        endpoint = "/api/permissions/add_user"

        params = {
            "login": username,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, method="POST", params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Assign user permission failed: {response.get('details', 'Unknown error')}"
            )
        return response
    
    async def remove_user_permission(
        self, username: str, permission: str, project_key: Optional[str] = None
    ) -> Dict[str, Any]:
        endpoint = "/api/permissions/remove_user"

        params = {
            "login": username,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, method="POST", params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Remove user permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_user_permission(
        self, project_key: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 100:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 100

        endpoint = "/api/permissions/users"

        params = {
            "projectKey": project_key,
            "p": page,
            "ps": page_size,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get users permission failed: {response.get('details', 'Unknown error')}"
            )
        return response
