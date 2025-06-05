from typing import Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Check the health status of a SonarQube server.
Returns: Dictionary with health status ('GREEN', 'YELLOW', 'RED') and node details.
- GREEN: SonarQube is fully operational
- YELLOW: SonarQube is usable, but it needs attention in order to be fully operational
- RED: SonarQube is not operational
Use to monitor server availability and performance.
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
Returns: Dictionary with status ('UP', 'DOWN', 'STARTING'), version, and description.
- STARTING: SonarQube Web Server is up and serving some Web Services (eg. api/system/status) but initialization is still ongoing
- UP: SonarQube instance is up and running
- DOWN: SonarQube instance is up but not running because migration has failed or some other reason (check logs).
- RESTARTING: SonarQube instance is still up but a restart has been requested.
- DB_MIGRATION_NEEDED: database migration is required.
- DB_MIGRATION_RUNNING: DB migration is running.
Use to verify if the server is fully operational.
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
Parameters: None
Returns: Boolean (True for 'pong', False otherwise).
Use for quick server reachability checks before other operations.
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
