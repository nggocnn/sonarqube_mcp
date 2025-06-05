from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Associate a quality profile with a project in SonarQube.
Parameters:
- language (str, required, programming language, e.g., 'java', 'py')
- project_key (str, required, project key, e.g., 'my_project')
- quality_profile (str, required, quality profile name, e.g., 'Sonar way')
Use to link a quality profile to a project for code analysis.
"""
)
async def add_quality_profile_project(
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

    response = await sonar_client.add_quality_profile_project(
        language=language,
        project_key=project_key,
        quality_profile=quality_profile,
    )

    return response


@mcp.tool(
    description="""
Remove a quality profile association from a project in SonarQube.
Parameters:
- language (str, required, programming language, e.g., 'java', 'py')
- project_key (str, required, project key, e.g., 'my_project')
- quality_profile (str, required, quality profile name, e.g., 'Sonar way')
Use to disassociate a quality profile from a project.
"""
)
async def remove_quality_profile_project(
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
