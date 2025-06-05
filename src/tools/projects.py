from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""

"""
)
async def create_project(
    project_name: str,
    project_key: str,
    main_branch: str = "main",
    new_code_definition_type: Optional[str] = None,
    new_code_definition_value: Optional[str] = None,
) -> Dict[str, Any]:
    response = await sonar_client.create_project(
        project_name=project_name,
        project_key=project_key,
        main_branch=main_branch,
        new_code_definition_type=new_code_definition_type,
        new_code_definition_value=new_code_definition_value,
    )
    return response


@mcp.tool(
    description="""
Search for SonarQube projects with optional name or key filtering.
Parameters:
- projects (str, comma-separated project keys, e.g., 'my_project,other_project')
- search (str, partial project name or key, e.g., 'my_proj')
- analyzed_before (str, date or datetime for last analysis, e.g., '2017-10-19' or '2017-10-19T13:00:00+0200')
- page (int, positive integer, default=1)
- page_size (int, positive integer, max 500, default=100)
Exactly one of projects or search must be provided.
Returns: Dictionary with project list and pagination info.
Use to find projects by name, key, or last analysis date.
"""
)
async def get_projects(
    projects: Optional[str] = None,
    search: Optional[str] = None,
    analyzed_before: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
) -> Dict[str, Any]:
    """Search for projects in SonarQube, with optional filtering by name.

    Retrieves a paginated list of projects the authenticated user can access.

    Args:
    projects (str, optional): Comma-separated list of project keys to filter results (e.g., 'my_project,other_project'). Defaults to None.
    search (str, optional): Partial project name or key to filter results (e.g., 'my_proj'). Defaults to None.
    analyzed_before (str, optional): Filter projects where the last analysis of all branches is older than this date (exclusive, server timezone). Accepts date ('YYYY-MM-DD') or datetime ('YYYY-MM-DDThh:mm:ssZ'). Example: '2017-10-19' or '2017-10-19T13:00:00+0200'. Defaults to None.
    page (int, optional): Page number for pagination (positive integer). Defaults to 1.
    page_size (int, optional): Number of projects per page (positive integer, max 500). Defaults to 100.

    Returns:
    Dict[str, Any]: A dictionary with project details and pagination info.
    """
    response = await sonar_client.get_projects(
        analyzed_before=analyzed_before,
        page=page,
        page_size=page_size,
        search=search,
        projects=projects,
    )
    return response


@mcp.tool(
    description="""
List projects accessible to the authenticated user
Parameters:
- page (int, positive integer, default=1)
- page_size (int, positive integer, max 500, default=100)
Returns: Dictionary with project list and pagination info.
Use to view projects the user can administer.
"""
)
async def get_user_projects(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """Lists projects accessible to the authenticated user.

    Retrieves a paginated list of projects the user can administer.

    Args:
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of projects per page (positive integer, max 500). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with project details and pagination info.
    """
    response = await sonar_client.get_user_projects(page=page, page_size=page_size)
    return response


@mcp.tool(
    description="""
List projects the authenticated user can scan.
Parameters:
- search (str, optional) partial project name or key, e.g., 'my_proj')
Returns: Dictionary with project list.
Use to identify projects where the user can perform analysis.
"""
)
async def get_user_scannable_projects(search: Optional[str] = None) -> Dict[str, Any]:
    """List projects the authenticated user has permission to scan.

    Retrieves a list of projects where the user can perform analysis (scanning).

    Args:
        search (str, optional): Partial project name or key to filter results. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with project keys.
    """
    response = await sonar_client.list_user_scannable_projects(search=search)
    return response


@mcp.tool(
    description="""
List analyses for a SonarQube project with optional filters.
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- category (str, optional, event category, e.g., 'VERSION', 'QUALITY_GATE'). Possible values: VERSION, OTHER, QUALITY_PROFILE, QUALITY_GATE, DEFINITION_CHANGE, ISSUE_DETECTION, SQ_UPGRADE
- page (int, positive integer, default=1)
- page_size (int, positive integer, max 500, default=100)
Returns: Dictionary with analysis list and pagination info.
Use to review a project's analysis history.
"""
)
async def get_project_analyses(
    project_key: str,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
):
    """List analyses for a specified SonarQube project, with optional filters.

    Retrieves a paginated list of analyses for a project, optionally filtered by event category or branch.

    Args:
        project_key (str): The key of the project (e.g., 'my_project').
        category (str, optional): Event category to filter analyses (e.g., 'VERSION', 'QUALITY_GATE'). Possible values: VERSION, OTHER, QUALITY_PROFILE, QUALITY_GATE, DEFINITION_CHANGE, ISSUE_DETECTION, SQ_UPGRADE. Defaults to None.
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of analyses per page (positive integer, max 500). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with analysis details and pagination info.
    """
    response = await sonar_client.get_project_analyses(
        project_key=project_key,
        category=category,
        page=page,
        page_size=page_size,
    )

    return response
