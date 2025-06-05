from typing import Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Retrieve all available metric types in SonarQube.
Parameters: None
Returns: Dictionary with list of metric types (e.g., 'INT', 'FLOAT').
Use to understand metric data formats before querying metrics.
"""
)
async def get_metrics_type() -> Dict[str, Any]:
    """Retrieve all available metric types in SonarQube.

    Lists the types of metrics (e.g., 'INT', 'FLOAT') supported by SonarQube.
    Returns:
        Dict[str, Any]: A dictionary with a list of metric type names.
    """
    response = await sonar_client.get_metrics_type()
    return response


@mcp.tool(
    description="""
Retrieve all available metrics in SonarQube with pagination.
Parameters:
- page (int, positive integer, default=1)
- page_size (int, positive integer, max 500, default=100)
Returns: Dictionary with metric list and pagination info.
Use to explore metrics like 'ncloc', 'complexity' for analysis.
"""
)
async def get_metrics(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """Retrieve all available metrics in SonarQube with pagination.

    Lists metrics (e.g., 'complexity') with details like name, type, and domain.

    Args:
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of metrics per page (positive integer, max 500). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with metric details and pagination info.
    """
    response = await sonar_client.get_metrics(page=page, page_size=page_size)
    return response
