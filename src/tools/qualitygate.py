from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
List all quality gates defined in SonarQube.
"""
)
async def get_quality_gates() -> Dict[str, Any]:
    """List all quality gates defined in SonarQube.

    Retrieves a list of quality gates with their names and IDs.
    Returns:
        Dict[str, Any]: A dictionary with quality gate details.
    """
    response = await sonar_client.get_quality_gates()
    return response


@mcp.tool(
    description="""
Retrieve details of a specific SonarQube quality gate.
"""
)
async def get_quality_gates_details(name: str) -> Dict[str, Any]:
    """Retrieve detailed information about a specific quality gate in SonarQube.

    Includes conditions and thresholds defined in the quality gate.

    Args:
        name (str): Name of the quality gate (e.g., 'Sonar way').

    Returns:
        Dict[str, Any]: A dictionary with quality gate details, including conditions.
    """
    response = await sonar_client.get_quality_gates_details(name=name)
    return response


@mcp.tool(
    description="""
Get the quality gate associated with a SonarQube project.
"""
)
async def get_quality_gates_by_project(project_key: str) -> Dict[str, Any]:
    """Retrieve the quality gate associated with a specific SonarQube project.

    Returns the quality gate assigned to the project, if any.

    Args:
        project_key (str): The key of the project (e.g., 'my_project').

    Returns:
        Dict[str, Any]: A dictionary with the associated quality gate details.
    """
    response = await sonar_client.get_quality_gates_by_project(project_key=project_key)
    return response


@mcp.tool(
    description="""
Retrieve quality gate status for a SonarQube project or analysis.
"""
)
async def get_quality_gates_project_status(
    analysis_id: str = "",
    project_key: str = "",
) -> Dict[str, Any]:
    """Retrieve the quality gate status for a project or specific analysis.

    Exactly one of `analysis_id` or `project_key` must be provided.

    Args:
        analysis_id (str, optional): ID of the analysis to check. Defaults to None.
        project_key (str, optional): Key of the project to check (e.g., 'my_project'). Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with quality gate status details.
    """
    response = await sonar_client.get_quality_gates_project_status(
        analysis_id=analysis_id,
        project_key=project_key,
    )

    return response
