from typing import Dict, Any
from server import mcp, sonar_client


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
    language: str = None,
    project_key: str = None,
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
