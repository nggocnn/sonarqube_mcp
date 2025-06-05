from typing import Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
List all quality gates defined in SonarQube.
Parameters: None
Returns: Dictionary with list of quality gate names and IDs.
Use to view available quality gates for project assignments.
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
Parameters:
- name (Required[str], quality gate name, e.g., 'Sonar way')
Returns: Dictionary with quality gate conditions and thresholds.
Use to inspect quality gate criteria for compliance checks.
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
Parameters:
- project_key (Required[str, project key, e.g., 'my_project')
Returns: Dictionary with assigned quality gate details.
Use to check which quality gate is applied to a project.
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
Parameters:
- analysis_id (str, optional, analysis ID)
- project_key (str, optional, project key, e.g., 'my_project')
Exactly one of analysis_id or project_key must be provided.
Returns: Dictionary with quality gate status (e.g., 'OK', 'ERROR') and conditions.
Use to evaluate quality gate results for a project or analysis.
"""
)
async def get_quality_gates_project_status(
    analysis_id: str = None,
    project_key: str = None,
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
