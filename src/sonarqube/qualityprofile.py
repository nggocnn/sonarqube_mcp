import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeQualityProfile(SonarQubeBase):

    async def get_quality_profiles(
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

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List quality profiles failed: {response.get('details', 'Unknown error')}"
            )

        return response
