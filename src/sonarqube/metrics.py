import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeMetric(SonarQubeBase):

    async def get_metrics_type(self) -> Dict[str, Any]:
        """Retrieve a list of available metric types in SonarQube.

        Returns:
            Dict[str, Any]: Dictionary containing a list of metric types, or an error response.
        """
        endpoint = "/api/metrics/types"
        response = await self._make_request(endpoint=endpoint)

        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get metrics types failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_metrics(
        self, page: Optional[int] = 1, page_size: Optional[int] = 100
    ) -> Dict[str, Any]:
        """Search for available metrics in SonarQube.

        Args:
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of metrics per page (must be positive, max 500). Defaults to 100.

        Returns:
            Dict[str, Any]: Dictionary containing a list of metrics and pagination details, or an error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 100

        if page_size > 500:
            logger.warning("Page size capped at 500 by SonarQube API")
            page_size = 500

        endpoint = "/api/metrics/search"
        params = {"p": page, "ps": page_size}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get metrics failed: {response.get('details', 'Unknown error')}"
            )
        return response
