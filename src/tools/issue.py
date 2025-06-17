from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Search for issues in SonarQube projects with detailed filters.
"""
)
async def get_issues(
    additional_fields: Optional[str] = None,
    assigned: Optional[bool] = None,
    assignees: Optional[str] = None,
    authors: Optional[str] = None,
    components: Optional[str] = None,
    issue_statuses: Optional[str] = None,
    issues: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    resolutions: Optional[str] = None,
    resolved: Optional[bool] = None,
    scopes: Optional[str] = None,
    severities: Optional[str] = None,
    tags: Optional[str] = None,
    types: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search for issues in SonarQube projects with customizable filters.

    Retrieves a paginated list of issues, filtered by components, status, severity, and other criteria.
    A component can be a portfolio, project (use project key as a component value), module, directory (use project key:directory as a component value) or file (use project key:file path as a component value).

    Args:
        additional_fields (str, optional): Comma-separated fields to include (e.g., 'comments,rules'). Defaults to None. Possible values: _all, comments, languages, rules, ruleDescriptionContextKey, transitions, actions, users.
        assigned (bool, optional): True for assigned issues, False for unassigned. Defaults to None.
        assignees (str, optional): Comma-separated assignee logins (e.g., 'user1,__me__'). Defaults to None.  The value '__me__' can be used as a placeholder for user who performs the request.
        authors (str, optional): Comma-separated SCM author accounts (e.g., 'author1@example.com'). Defaults to None.
        components (str, optional): components (str, optional): Comma-separated list of component keys. Retrieve issues associated to a specific list of components (and all its descendants). A component can be a portfolio, project (use project key as a component value), module, directory (use project key:directory as a component value) or file (use project key:file path as a component value).
        issue_statuses (str, optional): Comma-separated statuses (e.g., 'OPEN,FIXED'). Defaults to None. Possible values: OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED.
        issues (str, optional): Comma-separated issue keys (e.g., '5bccd6e8-f525-43a2-8d76-fcb13dde79ef'). Defaults to None.
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of issues per page (positive integer, max 20). Defaults to 20.
        resolutions (str, optional): Comma-separated resolutions (e.g., 'FIXED,FALSE-POSITIVE'). Defaults to None. Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED.
        resolved (bool, optional): True for resolved issues, False for unresolved. Defaults to None.
        scopes (str, optional): Comma-separated scopes (e.g., 'MAIN,TEST'). Defaults to None. Possible values: MAIN, TEST.
        severities (str, optional): Comma-separated severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
        tags (str, optional): Comma-separated tags (e.g., 'security,bug'). Defaults to None.
        types (str, optional): Comma-separated types (e.g., 'BUG,VULNERABILITY'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY.

    Returns:
        Dict[str, Any]: A dictionary with issue details and pagination info.
    """
    response = await sonar_client.get_issues(
        additional_fields=additional_fields,
        assigned=assigned,
        assignees=assignees,
        authors=authors,
        components=components,
        issue_statuses=issue_statuses,
        issues=issues,
        page=page,
        page_size=page_size,
        resolutions=resolutions,
        resolved=resolved,
        scopes=scopes,
        severities=severities,
        tags=tags,
        types=types,
    )

    return response


@mcp.tool(
    description="""
Retrieve SCM authors of issues for a SonarQube project.
"""
)
async def get_issues_authors(
    project_key: Optional[str] = None, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """Retrieve SCM authors associated with issues in a SonarQube project.

    Lists unique SCM accounts (e.g., email addresses) of authors for issues.

    Args:
        project_key (str, optional): Project key to filter authors (e.g., 'my_project'). Defaults to None.
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of authors per page (positive integer, max 20). Defaults to 20.

    Returns:
        Dict[str, Any]: A dictionary with a list of SCM author accounts.
    """
    response = await sonar_client.get_issues_authors(
        project_key=project_key, page=page, page_size=page_size
    )

    return response
