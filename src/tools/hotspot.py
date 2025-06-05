from typing import Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Retrieve security hotspots in a SonarQube project.
Parameters:
- project_key (Required[str, project key, e.g., 'my_project')
- file_paths (str, optional, comma-separated file paths, e.g., 'src/main.java,src/utils.js')
- only_mine (bool, optional, True to show only current user's hotspots, default=None)
- page (int, optional, positive integer for page number, default=1)
- page_size (int, optional, positive integer, max 500, default=100)
- resolution (str, optional, resolution filter, e.g., 'FIXED', 'SAFE'). Possible values: FIXED, SAFE, ACKNOWLEDGED
- status (str, optional, status filter, e.g., 'TO_REVIEW', 'REVIEWED'). Possible values: TO_REVIEW, REVIEWED
Returns: Dictionary with hotspot list and pagination info.
Use to identify and filter security hotspots in a project.
"""
)
async def get_project_hotspots(
    project_key: str,
    file_paths: str = None,
    only_mine: bool = None,
    page: int = 1,
    page_size: int = 100,
    resolution: str = None,
    status: str = None,
):
    """Retrieve security hotspots in a SonarQube project.

    Retrieves a paginated list of security hotspots, filtered by project, file paths, ownership, resolution, or status.

    Args:
        project_key (str): The key of the project (e.g., 'my_project'). Must be non-empty.
        file_paths (str, optional): Comma-separated list of file paths to filter hotspots (e.g., 'src/main.java,src/utils.js'). Defaults to None.
        only_mine (bool, optional): If True, return only hotspots assigned to the authenticated user. Defaults to None.
        page (int, optional): Page number for pagination (positive integer, default=1).
        page_size (int, optional): Number of hotspots per page (positive integer, max 500, default=100).
        resolution (str, optional): Filter by resolution (e.g., 'FIXED', 'SAFE'). Possible values: FIXED, SAFE, ACKNOWLEDGED.
        status (str, optional): Filter by status (e.g., 'TO_REVIEW', 'REVIEWED'). Possible values: TO_REVIEW, REVIEWED.

    Returns:
        Dict[str, Any]: A dictionary with hotspot details and pagination info.
    """
    response = await sonar_client.get_project_hotspots(
        project_key=project_key,
        file_paths=file_paths,
        only_mine=only_mine,
        page=page,
        page_size=page_size,
        resolution=resolution,
        status=status,
    )

    return response


@mcp.tool(
    description="""
Retrieve details of a specific SonarQube security hotspot.
Parameters:
- hotspot_key (Required[str], hotspot key)
Returns: Dictionary with hotspot details.
Use to inspect a specific hotspot's properties.
"""
)
async def get_hotspot_detail(hotspot_key: str):
    """Retrieve detailed information about a specific security hotspot.

    Provides details such as the hotspot's location, rule, and status.

    Args:
        hotspot_key (str): The key of the hotspot. Must be non-empty.

    Returns:
        Dict[str, Any]: A dictionary with hotspot details.
    """
    response = await sonar_client.get_hotspot_detail(hotspot_key=hotspot_key)

    return response
