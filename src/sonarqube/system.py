import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeSystem(SonarQubeBase):

    async def get_system_health(self) -> Dict[str, Any]:
        """Retrieve SonarQube system health status.

        Returns:
            Dict[str, Any]: Dictionary with system health details, including:
            - health: Overall status ("GREEN", "YELLOW", "RED", or None).
            - health_status: Human-readable status description.
            - nodes: List of application node details with their health and status.
            - causes: List of reasons for the current health status, if applicable.
            - On error, returns a dictionary with 'error' and 'details' keys.
        """
        endpoint = "/api/system/health"
        response = await self._make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"System health check failed: {response.get('details', 'Unknown error')}"
            )
            return response

        if not isinstance(response, dict):
            error_msg = f"Invalid response format from {endpoint}: expected dict, got {type(response)}"
            logger.error(error_msg)
            return {"error": "Invalid response", "details": error_msg}

        health_status_map = {
            "GREEN": "SonarQube is fully operational",
            "YELLOW": "SonarQube is usable, but it needs attention in order to be fully operational",
            "RED": "SonarQube is not operational",
            None: "Unknown health status",
        }

        health_status = response.get("health")
        response["health_status"] = health_status_map.get(
            health_status, health_status_map[None]
        )

        nodes = response.get("nodes", [])
        if not isinstance(nodes, list):
            logger.warning(
                f"Invalid nodes format in response: expected list, got {type(nodes)}"
            )
            nodes = []

        for node in nodes:
            if isinstance(node, dict):
                node_health_status = node.get("health")
                node["health_status"] = health_status_map.get(
                    node_health_status, health_status_map[None]
                )
            else:
                logger.warning(f"Invalid node format: expected dict, got {type(node)}")
                node["health_status"] = health_status_map[None]

        logger.info(f"SonarQube health: {health_status} - {response['health_status']}")
        return response

    async def get_system_status(self) -> Dict[str, Any]:
        """Retrieve SonarQube system status.

        Returns:
            Dict[str, Any]: Dictionary containing system status information, including:
            - id: Unique identifier for the SonarQube instance.
            - version: SonarQube server version.
            - status: The running status ("STARTING", "UP", "DOWN", "RESTARTING", "DB_MIGRATION_NEEDED", "DB_MIGRATION_RUNNING").
            - system_status: Human-readable description of the status.
            - On error, returns a dictionary with 'error' and 'details' keys.
        """
        endpoint = "/api/system/status"
        response = await self._make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(f"System status check failed: {response}")
            return response

        if not isinstance(response, dict):
            error_msg = f"Invalid response format from {endpoint}: expected dict, got {type(response)}"
            logger.error(error_msg)
            return {"error": "Invalid response", "details": error_msg}

        system_status_map = {
            "STARTING": "SonarQube Web Server is up and serving some Web Services but initialization is still ongoing",
            "UP": "SonarQube instance is up and running",
            "DOWN": "SonarQube instance is up but not running because migration has failed or some other reason (check logs).",
            "RESTARTING": "SonarQube instance is still up but a restart has been requested.",
            "DB_MIGRATION_NEEDED": "Database migration is required.",
            "DB_MIGRATION_RUNNING": "DB migration is runnings",
        }

        system_status = response.get("status")
        response["system_status"] = system_status_map.get(system_status)

        logger.info(f"SonarQube status: {system_status} - {response['system_status']}")
        return response

    async def system_ping(self) -> bool:
        """Check if the SonarQube server is reachable by sending a ping request.

        Returns:
            bool: True if the server responds with 'pong', False if the response is invalid or an error occurs.
        """
        endpoint = "/api/system/ping"
        response = await self._make_request(endpoint=endpoint, raw_response=True)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"System ping failed: {response.get('details', 'Unknown error')}"
            )
            return False

        if not isinstance(response, str):
            logger.error(
                f"System ping failed: Expected string response, got {type(response)}"
            )
            return False

        return "pong" == response
