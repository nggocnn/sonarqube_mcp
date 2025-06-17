import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeRule(SonarQubeBase):

    async def get_rules(
        self,
        page: int = 1,
        page_size: int = 20,
        severities: Optional[str] = None,
        statuses: Optional[str] = None,
        languages: Optional[str] = None,
        types: Optional[str] = None,
    ):
        """Search for rules in SonarQube.

        Retrieves a paginated list of rules, optionally filtered by severity, status, or type.

        Args:
            page (int, optional): Page number for pagination (positive integer, default 1).
            page_size (int, optional): Number of rules per page (positive integer, max 20, default 20).
            severities (str, optional): Comma-separated list of severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
            statuses (str, optional): Comma-separated list of statuses (e.g., 'BETA,READY'). Defaults to None. Possible values: BETA, DEPRECATED, READY, REMOVED.
            languages (str, optional): Comma-separated list of languages (e.g. 'java,js'). Defaults to None
            types (str, optional): Comma-separated list of rule types (e.g., 'BUG,CODE_SMELL'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY, SECURITY_HOTSPOT.

        Returns:
            Dict[str, Any]: A dictionary with rule details and pagination info.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 20:
            logger.warning("Page size capped at 20")
            page_size = 20

        endpoint = "/api/rules/search"

        params = {
            "p": page,
            "ps": page_size,
            "severities": severities.upper() if severities else None,
            "statuses": statuses.upper() if statuses else None,
            "languages": languages.lower() if languages else None,
            "types": types.upper() if types else None,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"List rules failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_rule_details(self, rule_key: str, actives: Optional[bool] = False):
        """Retrieve detailed information about a specific SonarQube rule.

        Provides rule details, including description and active status in profiles if requested.

        Args:
            rule_key (str): The key of the rule (e.g., 'squid:S1234'). Must be non-empty.
            actives (Optional[bool], optional): If True, include active status in quality profiles. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary with rule details.
        """
        if not rule_key or not rule_key.strip():
            logger.error("rule_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "rule_key must be a non-empty string",
            }

        endpoint = "/api/rules/show"

        params = {
            "key": rule_key,
            "actives": str(actives).lower(),
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get rule details failed: {response.get('details', 'Unknown error')}"
            )
        return response
