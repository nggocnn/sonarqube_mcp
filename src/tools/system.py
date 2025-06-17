from typing import Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Check the health status of a SonarQube server.
"""
)
async def get_system_health() -> Dict[str, Any]:
    """Retrieve the health status of the SonarQube server.
    Returns:
        sDict[str, Any]: A dictionary containing the health status
    """
    response = await sonar_client.get_system_health()
    return response


@mcp.tool(
    description="""
Retrieve the operational status of a SonarQube server.
"""
)
async def get_system_status() -> Dict[str, Any]:
    """Retrieve the operational status of the SonarQube server.

    Provides the current system status (e.g., 'UP', 'DOWN', 'STARTING') with a human-readable description.
    Returns:
        Dict[str, Any]: A dictionary with the system status, version, and description.
    """
    response = await sonar_client.get_system_status()
    return response


@mcp.tool(
    description="""
Ping the SonarQube server to verify connectivity.
"""
)
async def system_ping() -> bool:
    """Ping the SonarQube server to check if it is reachable.

    Sends a simple request to confirm server availability.
    Returns:
        bool: True if the server responds with 'pong', False otherwise.
    """
    response = await sonar_client.system_ping()
    return response
