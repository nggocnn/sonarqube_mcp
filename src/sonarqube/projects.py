import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeProjects(SonarQubeBase):

    async def create_project(
        self,
        project_name: str,
        project_key: str,
        main_branch: str = "main",
        new_code_definition_type: Optional[str] = None,
        new_code_definition_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new SonarQube project.

        Args:
            project_name (str): The name of the project (max length: 500 characters, abbreviated if longer).
            project_key (str): A unique key identifier for the project (max length: 400 characters).
            main_branch (str, optional): The name of the main branch (default: "main").
            new_code_definition_type (str, optional): The type of new code definition. Allowed values: "PREVIOUS_VERSION", "NUMBER_OF_DAYS", "REFERENCE_BRANCH" (defaults to main branch).
            new_code_definition_value (str, optional new code definition.
                Expected values:
                - None for "PREVIOUS_VERSION" or "REFERENCE_BRANCH".
                - A number between 1 and 90 for "NUMBER_OF_DAYS".

        Returns:
            Dict[str, Any]: Dictionary containing details of the created project.
        """
        endpoint = "/api/projects/create"

        params = {
            "name": project_name,
            "project": project_key,
            "mainBranch": main_branch,
            "newCodeDefinitionType": new_code_definition_type,
            "newCodeDefinitionValue": new_code_definition_value,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Create project failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_projects(
        self,
        analyzed_before: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        projects: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List SonarQube projects with optional filters.

        Args:
            analyzed_before (str, optional1 date string (e.g., '2023-10-19') to filter projects analyzed before this date. Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of projects per page (must be positive, max 20). Defaults to 20.
            search (str, optional): Search query to filter projects by name or key. Defaults to None.
            projects (str, optional): Comma-separated list of project keys to retrieve specific projects. Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary containing project list and pagination details, or an error response with 'error' and 'details' keys.
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

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_user_projects(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
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
            page_size = 20

        if page_size > 20:
            logger.warning("Page size capped at 20")
            page_size = 20

        endpoint = "/api/projects/search_my_projects"

        params = {"p": page, "ps": page_size}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List user projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_user_scannable_projects(
        self, search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve a list of SonarQube projects that the authenticated user has permission to scan.

        Args:
            search (str, optional): Search query to filter projects by name or key. Defaults to None.

        Returns: Dict[str, Any]: Dictionary containing a list of scannable projects, or an error response.
        """
        endpoint = "/api/projects/search_my_scannable_projects"
        params = {"q": search} if search else {}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List scannable projects failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_project_analyses(
        self,
        project_key: str,
        category: Optional[str] = None,
        branch: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """Retrieve a list of analyses for a specified SonarQube project, with optional filters.

        Args:
            project_key (str): The key of the project to retrieve analyses for.
            category (str, optional): Event category to filter analyses (e.g., 'VERSION,QUALITY_GATE,OTHER'). Defaults to None. Possible values: VERSION, OTHER, QUALITY_PROFILE, QUALITY_GATE, DEFINITION_CHANGE, ISSUE_DETECTION, SQ_UPGRADE
            branch (str, optional): Branch key to filter analyses (not available in Community Edition). Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of analyses per page (must be positive, max 20). Defaults to 20.

        Returns:
            Dict[str, Any]: Dictionary containing a list of project analyses and pagination details, or an error response.
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

        endpoint = "/api/project_analyses/search"

        params = {
            "project": project_key,
            "category": str(category).upper() if category else None,
            "branch": branch,
            "p": page,
            "ps": page_size,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List project analyses failed: {response.get('details', 'Unknown error')}"
            )
        return response
