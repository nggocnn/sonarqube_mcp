import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeQualityProfile(SonarQubeBase):

    async def add_quality_profile_project(
        self,
        language: str,
        project_key: str,
        quality_profile: str,
    ):
        """Associates a quality profile with a project in SonarQube.

        Args:
            language (str): The programming language of the quality profile (e.g., 'java', 'py').
            project_key (str): The key of the project to associate with the quality profile (e.g., 'my_project').
            quality_profile (str): The name of the quality profile to apply (e.g., 'Sonar way').
        """

        endpoint = "/api/qualityprofiles/add_project"

        params = {
            "language": language,
            "project": project_key,
            "qualityProfile": quality_profile,
        }

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Add quality profile for project failed: {response.get('details', 'Unknown error')}"
            )

        return response

    async def remove_quality_profile_project(
        self,
        language: str,
        project_key: str,
        quality_profile: str,
    ):
        """Removes a quality profile association from a project in SonarQube.

        Args:
            language (str): The programming language of the quality profile (e.g., 'java', 'py').
            project_key (str): The key of the project to remove the quality profile from (e.g., 'my_project').
            quality_profile (str): The name of the quality profile to remove (e.g., 'Sonar way').
        """

        endpoint = "/api/qualityprofiles/remove_project"

        params = {
            "language": language,
            "project": project_key,
            "qualityProfile": quality_profile,
        }

        response = await self._make_request(
            endpoint=endpoint, method="POST", params=params
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Remove quality profile for project failed: {response.get('details', 'Unknown error')}"
            )

        return response

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
            language (str, optional): Filter by programming language (e.g., 'java', 'py'). Defaults to None.
            project_key (str, optional): Filter by project key (e.g., 'my_project'). Defaults to None.

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
