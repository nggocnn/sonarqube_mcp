from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
"""
)
async def add_quality_profile_project(
    language: str,
    project_key: str,
    quality_profile: str,
) -> Dict[str, Any]:
    response = await sonar_client.add_quality_profile_project(
        language=language,
        project_key=project_key,
        quality_profile=quality_profile,
    )

    return response


@mcp.tool(
    description="""
"""
)
async def remove_quality_profile_project(
    language: str,
    project_key: str,
    quality_profile: str,
) -> Dict[str, Any]:
    response = await sonar_client.remove_quality_profile_project(
        language=language,
        project_key=project_key,
        quality_profile=quality_profile,
    )

    return response


@mcp.tool(
    description="""
Retrieve SonarQube quality profiles.
Parameters:
- defaults (bool, optional, True to show only default profiles, default=False)
- language (str, optional, programming language, e.g., 'java', 'py')
- project_key (str, project key, e.g., 'my_project')
Returns: Dictionary with quality profile details.
Use to find quality profiles by language or project associations.
"""
)
async def get_quality_profiles(
    defaults: bool = False,
    language: Optional[str] = None,
    project_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for quality profiles in SonarQube.

    Retrieves quality profiles, optionally filtered by default profiles, language, or associated project.

    Args:
        defaults (bool, optional): If True, return only default profiles. Defaults to False.
        language (str, optional): Filter by programming language (e.g., 'java', 'py'). Defaults to None.
        project_key (str, optional): Filter by project key (e.g., 'my_project'). Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with quality profile details.
    """
    response = await sonar_client.get_quality_profiles(
        defaults=defaults,
        language=language,
        project_key=project_key,
    )

    return response
