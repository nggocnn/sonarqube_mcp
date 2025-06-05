from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Retrieve SonarQube rules with optional filters.
Parameters:
- page (int, optional, positive integer for page number, default=1)
- page_size (int, optional, positive integer, max 500, default=100)
- severities (str, optional, comma-separated severities, e.g., 'BLOCKER,CRITICAL'). Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
- statuses (str, optional, comma-separated statuses, e.g., 'BETA,READY'). Possible values: BETA, DEPRECATED, READY, REMOVED.
- types (str, optional, comma-separated types, e.g., 'BUG,CODE_SMELL'). Possible values: CODE_SMELL, BUG, VULNERABILITY, SECURITY_HOTSPOT.
Returns: Dictionary with rule list and pagination info.
Use to find rules by severity, status, or type.
"""
)
async def get_rules(
    page: int = 1,
    page_size: int = 100,
    severities: Optional[str] = None,
    statuses: Optional[str] = None,
    languages: Optional[str] = None,
    types: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve for rules in SonarQube.

    Retrieves a paginated list of rules, optionally filtered by severity, status, or type.

    Args:
        page (int, optional): Page number for pagination (positive integer, default=1).
        page_size (int, optional): Number of rules per page (positive integer, max 500, default=100).
        severities (str, optional): Comma-separated list of severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
        statuses (str, optional): Comma-separated list of statuses (e.g., 'BETA,READY'). Defaults to None. Possible values: BETA, DEPRECATED, READY, REMOVED.
        languages (str, optional): Comma-separated list of languages (e.g. 'java,js'). Defaults to None
        types (str, optional): Comma-separated list of rule types (e.g., 'BUG,CODE_SMELL'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY, SECURITY_HOTSPOT.

    Returns:
        Dict[str, Any]: A dictionary with rule details and pagination info.
    """
    response = await sonar_client.get_rules(
        page=page,
        page_size=page_size,
        severities=severities,
        statuses=statuses,
        languages=languages,
        types=types,
    )

    return response


@mcp.tool(
    description="""
Retrieve details of a specific SonarQube rule.
Parameters:
- rule_key (Required[str], rule key, e.g., 'squid:S1234')
- actives (bool, optional, True to include active profile status, default=False)
Returns: Dictionary with rule details (e.g., name, severity, active profiles).
Use to inspect a specific rule's properties.
"""
)
async def get_rule_details(rule_key: str, actives: bool = False) -> Dict[str, Any]:
    """Retrieve detailed information about a specific SonarQube rule.

    Provides rule details, including description and active status in profiles if requested.

    Args:
        rule_key (str): The key of the rule. Must be non-empty.
        actives (bool, optional): If True, include active status in quality profiles. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary with rule details.
    """

    response = await sonar_client.get_rule_details(rule_key=rule_key, actives=actives)

    return response
