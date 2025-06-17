import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubePermission(SonarQubeBase):

    async def add_group_permission(
        self, group_name: str, permission: str, project_key: Optional[str] = None
    ):
        """Grants a permission to a group for a specific project or globally.

        Args:
            group_name (str): The name of the group to receive the permission.
            permission (str): The permission to grant (e.g., 'admin', 'scan').
                - Possible values for global permissions: admin, gateadmin, profileadmin, provisioning, scan, applicationcreator, portfoliocreator
                - Possible values for project permissions admin, codeviewer, issueadmin, securityhotspotadmin, scan, user
            project_key (str, optional): The key of the project for the permission. If None, the permission is global. Defaults to None.
        """
        endpoint = "/api/permissions/add_group"

        params = {
            "groupName": group_name,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Assign group permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def remove_group_permission(
        self, group_name: str, permission: str, project_key: Optional[str] = None
    ):
        """Revokes a permission from a group for a specific project or globally.

        Args:
            group_name (str): The name of the group to remove the permission from.
            permission (str): The permission to grant (e.g., 'admin', 'scan').
                - Possible values for global permissions: admin, gateadmin, profileadmin, provisioning, scan, applicationcreator, portfoliocreator
                - Possible values for project permissions admin, codeviewer, issueadmin, securityhotspotadmin, scan, user
            project_key (str, optional): The key of the project for the permission. If None, the permission is global. Defaults to None.
        """
        endpoint = "/api/permissions/remove_group"

        params = {
            "groupName": group_name,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Remove group permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_group_permission(
        self, project_key: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Fetches a list of group permissions for a specific project or globally.

        Args:
            project_key (str, optional): The key of the project to fetch permissions for. If None, global permissions are returned. Defaults to None.
            page (int, optional): Page number for pagination (positive integer). Defaults to 1.
            page_size (int, optional): Number of results per page (positive integer, max 20). Defaults to 20.

        Returns:
            Dict[str, Any]: A dictionary with group permission details.
        """

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 20:
            logger.warning("Page size capped at 20")
            page_size = 20

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

    async def add_user_permission(
        self, username: str, permission: str, project_key: Optional[str] = None
    ):
        """Grants a permission to a user for a specific project or globally.

        Args:
            username (str): The name of the user to receive the permission.
            permission (str): The permission to grant (e.g., 'admin', 'scan').
                - Possible values for global permissions: admin, gateadmin, profileadmin, provisioning, scan, applicationcreator, portfoliocreator
                - Possible values for project permissions admin, codeviewer, issueadmin, securityhotspotadmin, scan, user
            project_key (str, optional): The key of the project for the permission. If None, the permission is global. Defaults to None.
        """
        endpoint = "/api/permissions/add_user"

        params = {
            "login": username,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Assign user permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def remove_user_permission(
        self, username: str, permission: str, project_key: Optional[str] = None
    ):
        """Revokes a permission from a user for a specific project or globally.

        Args:
            username (str): The name of the user to remove the permission from.
            permission (str): The permission to grant (e.g., 'admin', 'scan').
                - Possible values for global permissions: admin, gateadmin, profileadmin, provisioning, scan, applicationcreator, portfoliocreator
                - Possible values for project permissions admin, codeviewer, issueadmin, securityhotspotadmin, scan, user
            project_key (str, optional): The key of the project for the permission. If None, the permission is global. Defaults to None.
        """
        endpoint = "/api/permissions/remove_user"

        params = {
            "login": username,
            "permission": permission,
            "projectKey": project_key,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Remove user permission failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_user_permission(
        self, project_key: Optional[str] = None, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """Fetches a list of users permissions for a specific project or globally.

        Args:
            project_key (str, optional): The key of the project to fetch permissions for. If None, global permissions are returned. Defaults to None.
            page (int, optional): Page number for pagination (positive integer). Defaults to 1.
            page_size (int, optional): Number of results per page (positive integer, max 20). Defaults to 20.

        Returns:
            Dict[str, Any]: A dictionary with users permission details.
        """

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 20:
            logger.warning("Page size capped at 20")
            page_size = 20

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
