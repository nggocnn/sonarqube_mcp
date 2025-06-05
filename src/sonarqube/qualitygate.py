import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeQualityGate(SonarQubeBase):

    async def get_quality_gates(self) -> Dict[str, Any]:
        """Retrieve list of quality gates.

        Returns:
            Dict[str, Any]: List of quality gates or error response.
        """
        endpoint = "/api/qualitygates/list"

        response = await self._make_request(endpoint=endpoint)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gates failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_quality_gates_details(self, name: str) -> Dict[str, Any]:
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

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate details failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_quality_gates_by_project(self, project_key: str) -> Dict[str, Any]:
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
        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate by project failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_quality_gates_project_status(
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

        endpoint = "/api/qualitygates/project_status"
        params = {
            "projectKey": project_key if project_key else None,
            "analysisId": analysis_id if analysis_id else None,
            "branch": branch,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get quality gate project status failed: {response.get('details', 'Unknown error')}"
            )
        return response
