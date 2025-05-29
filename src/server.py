import os
from mcp.server.fastmcp import FastMCP
from sonarqube.client import SonarQubeClient
from typing import Optional, Dict, Any

mcp = FastMCP()


SONARQUBE_URL = os.environ.get("SONARQUBE_URL", "http://localhost:9000")
SONARQUBE_TOKEN = os.environ.get("SONARQUBE_TOKEN", "")
SONARQUBE_ORGANIZATION = os.environ.get("SONARQUBE_ORGANIZATION", None)


sonar_client = SonarQubeClient.create(
    base_url=SONARQUBE_URL,
    token=SONARQUBE_TOKEN,
    organization=SONARQUBE_ORGANIZATION,
)


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
def get_system_health() -> Dict[str, Any]:
    """Retrieve the health status of the SonarQube server.

    Args:
        None

    Returns:
        Dict[str, Any]: A dictionary containing the health status
    """
    response = sonar_client.get_system_health()
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
def get_system_status() -> Dict[str, Any]:
    """Retrieve the operational status of the SonarQube server.

    Provides the current system status (e.g., 'UP', 'DOWN', 'STARTING') with a human-readable description.

    Args:
        None

    Returns:
        Dict[str, Any]: A dictionary with the system status, version, and description.
    """
    response = sonar_client.get_system_status()
    return response


@mcp.tool(
    description="""
Ping the SonarQube server to verify connectivity.
Parameters: None
Returns: Boolean (True for 'pong', False otherwise).
Use for quick server reachability checks before other operations.
"""
)
def system_ping() -> bool:
    """Ping the SonarQube server to check if it is reachable.

    Sends a simple request to confirm server availability.

    Args:
        None

    Returns:
        bool: True if the server responds with 'pong', False otherwise.
    """
    response = sonar_client.system_ping()
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
def list_projects(
    projects: str = None,
    search: str = None,
    analyzed_before: str = None,
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
    response = sonar_client.list_projects(
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
def list_user_projects(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """Lists projects accessible to the authenticated user.

    Retrieves a paginated list of projects the user can administer.

    Args:
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of projects per page (positive integer, max 500). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with project details and pagination info.
    """
    response = sonar_client.list_user_projects(page=page, page_size=page_size)
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
def list_user_scannable_projects(search: str = None) -> Dict[str, Any]:
    """List projects the authenticated user has permission to scan.

    Retrieves a list of projects where the user can perform analysis (scanning).

    Args:
        search (str, optional): Partial project name or key to filter results. Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with project keys.
    """
    response = sonar_client.list_user_scannable_projects(search=search)
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
def list_project_analyses(
    project_key: str,
    category: str = None,
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
    response = sonar_client.list_project_analyses(
        project_key=project_key,
        category=category,
        page=page,
        page_size=page_size,
    )

    return response


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
def get_project_hotspots(
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
    response = sonar_client.get_project_hotspots(
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
def get_hotspot_detail(hotspot_key: str):
    """Retrieve detailed information about a specific security hotspot.

    Provides details such as the hotspot's location, rule, and status.

    Args:
        hotspot_key (str): The key of the hotspot. Must be non-empty.

    Returns:
        Dict[str, Any]: A dictionary with hotspot details.
    """
    response = sonar_client.get_hotspot_detail(hotspot_key=hotspot_key)

    return response


@mcp.tool(
    description="""
Search for issues in SonarQube projects with detailed filters.
Parameters:
- additional_fields (str, optional, comma-separated fields, e.g., 'comments,rules'). Possible values: _all, comments, languages, rules, ruleDescriptionContextKey, transitions, actions, users.
- assigned (bool, optional, True for assigned, False for unassigned)
- assignees (str, optional, comma-separated logins, e.g., 'user1,__me__').  The value '__me__' can be used as a placeholder for current user who performs the request
- authors (str, optional, comma-separated SCM accounts, e.g., 'author1@example.com,linux@fondation.org')
- components (str, optional, comma-separated list of component keys). Retrieve issues associated to a specific list of components (and all its descendants). A component can be a portfolio, project (use project_key), module, directory (use project_key:directory) or file (use_project_key:file_path).
- issue_statuses (str, optional, comma-separated statuses, e.g., 'OPEN,FIXED'). Possible values: OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED.
- issues (str, optional, comma-separated issue keys, e.g., '5bccd6e8-f525-43a2-8d76-fcb13dde79ef')
- page (int, optional, positive integer, default=1)
- page_size (int, optional, positive integer, max 500, default=100)
- resolutions (str, optional, comma-separated resolutions, e.g., 'FIXED,FALSE-POSITIVE'). Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED.
- resolved (bool, optional, True for resolved, False for unresolved)
- scopes (str, optional, comma-separated scopes, e.g., 'MAIN,TEST'). Possible values: MAIN, TEST.
- severities (str, optional, comma-separated severities, e.g., 'BLOCKER,CRITICAL'). Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
- tags (str, optional, comma-separated tags, e.g., 'security,bug')
- types (str, optional, comma-separated types, e.g., 'BUG,VULNERABILITY'). Possible values: CODE_SMELL, BUG, VULNERABILITY.
Returns: Dictionary with issue list and pagination info.
Use to find specific issues based on multiple criteria.
"""
)
def get_issues(
    additional_fields: str = None,
    assigned: bool = None,
    assignees: str = None,
    authors: str = None,
    components: str = None,
    issue_statuses: str = None,
    issues: str = None,
    page: int = 1,
    page_size: int = 100,
    resolutions: str = None,
    resolved: bool = None,
    scopes: str = None,
    severities: str = None,
    tags: str = None,
    types: str = None,
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
        page_size (int, optional): Number of issues per page (positive integer, max 500). Defaults to 100.
        resolutions (str, optional): Comma-separated resolutions (e.g., 'FIXED,FALSE-POSITIVE'). Defaults to None. Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED.
        resolved (bool, optional): True for resolved issues, False for unresolved. Defaults to None.
        scopes (str, optional): Comma-separated scopes (e.g., 'MAIN,TEST'). Defaults to None. Possible values: MAIN, TEST.
        severities (str, optional): Comma-separated severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
        tags (str, optional): Comma-separated tags (e.g., 'security,bug'). Defaults to None.
        types (str, optional): Comma-separated types (e.g., 'BUG,VULNERABILITY'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY.

    Returns:
        Dict[str, Any]: A dictionary with issue details and pagination info.
    """
    response = sonar_client.get_issues(
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
Parameters:
- project_key (str, optional, project key, e.g., 'my_project')
- page (int, optional, positive integer, default=1)
- page_size (int, optional, positive integer, max 100, default=10)
Returns: Dictionary with list of SCM author accounts (e.g., emails).
Use to identify contributors to issues in a project.
"""
)
def get_issues_authors(
    project_key: str = None, page: int = 1, page_size: int = 10
) -> Dict[str, Any]:
    """Retrieve SCM authors associated with issues in a SonarQube project.

    Lists unique SCM accounts (e.g., email addresses) of authors for issues.

    Args:
        project_key (str, optional): Project key to filter authors (e.g., 'my_project'). Defaults to None.
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of authors per page (positive integer, max 100). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with a list of SCM author accounts.
    """
    response = sonar_client.get_issues_authors(
        project_key=project_key, page=page, page_size=page_size
    )

    return response


@mcp.tool(
    description="""
Retrieve all available metric types in SonarQube.
Parameters: None
Returns: Dictionary with list of metric types (e.g., 'INT', 'FLOAT').
Use to understand metric data formats before querying metrics.
"""
)
def get_metrics_type() -> Dict[str, Any]:
    """Retrieve all available metric types in SonarQube.

    Lists the types of metrics (e.g., 'INT', 'FLOAT') supported by SonarQube.

    Args:
        None

    Returns:
        Dict[str, Any]: A dictionary with a list of metric type names.
    """
    response = sonar_client.get_metrics_type()
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
def get_metrics(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """Retrieve all available metrics in SonarQube with pagination.

    Lists metrics (e.g., 'complexity') with details like name, type, and domain.

    Args:
        page (int, optional): Page number for pagination (positive integer). Defaults to 1.
        page_size (int, optional): Number of metrics per page (positive integer, max 500). Defaults to 100.

    Returns:
        Dict[str, Any]: A dictionary with metric details and pagination info.
    """
    response = sonar_client.get_metrics(page=page, page_size=page_size)
    return response


@mcp.tool(
    description="""
List all quality gates defined in SonarQube.
Parameters: None
Returns: Dictionary with list of quality gate names and IDs.
Use to view available quality gates for project assignments.
"""
)
def get_quality_gates() -> Dict[str, Any]:
    """List all quality gates defined in SonarQube.

    Retrieves a list of quality gates with their names and IDs.

    Args:
        None

    Returns:
        Dict[str, Any]: A dictionary with quality gate details.
    """
    response = sonar_client.get_quality_gates()
    return response


@mcp.tool(
    description="""
Retrieve details of a specific SonarQube quality gate.
Parameters:
- name (Required[str], quality gate name, e.g., 'Sonar way')
Returns: Dictionary with quality gate conditions and thresholds.
Use to inspect quality gate criteria for compliance checks.
"""
)
def get_quality_gates_details(name: str) -> Dict[str, Any]:
    """Retrieve detailed information about a specific quality gate in SonarQube.

    Includes conditions and thresholds defined in the quality gate.

    Args:
        name (str): Name of the quality gate (e.g., 'Sonar way').

    Returns:
        Dict[str, Any]: A dictionary with quality gate details, including conditions.
    """
    response = sonar_client.get_quality_gates_details(name=name)
    return response


@mcp.tool(
    description="""
Get the quality gate associated with a SonarQube project.
Parameters:
- project_key (Required[str, project key, e.g., 'my_project')
Returns: Dictionary with assigned quality gate details.
Use to check which quality gate is applied to a project.
"""
)
def get_quality_gates_by_project(project_key: str) -> Dict[str, Any]:
    """Retrieve the quality gate associated with a specific SonarQube project.

    Returns the quality gate assigned to the project, if any.

    Args:
        project_key (str): The key of the project (e.g., 'my_project').

    Returns:
        Dict[str, Any]: A dictionary with the associated quality gate details.
    """
    response = sonar_client.get_quality_gates_by_project(project_key=project_key)
    return response


@mcp.tool(
    description="""
Retrieve quality gate status for a SonarQube project or analysis.
Parameters:
- analysis_id (str, optional, analysis ID)
- project_key (str, optional, project key, e.g., 'my_project')
Exactly one of analysis_id or project_key must be provided.
Returns: Dictionary with quality gate status (e.g., 'OK', 'ERROR') and conditions.
Use to evaluate quality gate results for a project or analysis.
"""
)
def get_quality_gates_project_status(
    analysis_id: str = None,
    project_key: str = None,
) -> Dict[str, Any]:
    """Retrieve the quality gate status for a project or specific analysis.

    Exactly one of `analysis_id` or `project_key` must be provided.

    Args:
        analysis_id (str, optional): ID of the analysis to check. Defaults to None.
        project_key (str, optional): Key of the project to check (e.g., 'my_project'). Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with quality gate status details.
    """
    response = sonar_client.get_quality_gates_project_status(
        analysis_id=analysis_id,
        project_key=project_key,
    )

    return response


@mcp.tool(
    description="""
Retrieve SonarQube quality profiles.
Parameters:
- defaults (bool, optional, True to show only default profiles, default=False)
- language (str, optional, programming language, e.g., 'java', 'py')
- project_key (str, project key, e.g., 'my_project')
Returns: Dictionary with quality profile details.
Use to find quality profiles by language or project association.
"""
)
def get_quality_profiles(
    defaults: bool = False,
    language: str = None,
    project_key: str = None,
):
    """Search for quality profiles in SonarQube.

    Retrieves quality profiles, optionally filtered by default profiles, language, or associated project.

    Args:
        defaults (bool, optional): If True, return only default profiles. Defaults to False.
        language (str, optional): Filter by programming language (e.g., 'java', 'py'). Defaults to None.
        project_key (str, optional): Filter by project key (e.g., 'my_project'). Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with quality profile details.
    """
    response = sonar_client.get_quality_profiles(
        defaults=defaults,
        language=language,
        project_key=project_key,
    )

    return response


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
def get_rules(
    page: int = 1,
    page_size: int = 100,
    severities: str = None,
    statuses: str = None,
    languages: str = None,
    types: str = None,
):
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
    response = sonar_client.get_rules(
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
def get_rule_details(rule_key: str, actives: bool = False):
    """Retrieve detailed information about a specific SonarQube rule.

    Provides rule details, including description and active status in profiles if requested.

    Args:
        rule_key (str): The key of the rule. Must be non-empty.
        actives (bool, optional): If True, include active status in quality profiles. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary with rule details."""

    response = sonar_client.get_rule_details(rule_key=rule_key, actives=actives)

    return response


@mcp.tool(
    description="""
Retrieve source code for a file in a SonarQube project.
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main.java')
- start (int, optional, positive integer for start line)
- end (int, optional, positive integer, >= start, for end line)
Returns: Dictionary with source code lines and line numbers.
Use to view specific lines of a file's source code.
"""
)
def get_source(
    project_key: str,
    file_path: str,
    start: int = None,
    end: int = None,
) -> Dict[str, Any]:
    """Retrieve source code for a file in a SonarQube project.

    Returns the source code lines with line numbers, optionally limited to a range.

    Args:
        project_key (str): Key of the project (e.g., 'my_project').
        file_path (str): Path to the file within the project (e.g., 'src/main.java').
        start (int, optional): Starting line number (positive integer). Defaults to None.
        end (int, optional): Ending line number (positive integer, >= start). Defaults to None.

    Returns:
        Dict[str, Any]: A dictionary with source code lines.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_source(file_key=file_key, start=start, end=end)

    return response


@mcp.tool(
    description="""
Retrieve SCM information for a file in a SonarQube project.
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main.java')
- start (int, optional, positive integer for start line)
- end (int, optional, positive integer, >= start, for end line)
- commits_by_line (bool, True to list commits per line, False to group by commit, default=False)
Returns: Dictionary with SCM details (author, date, revision) per line.
Use to track changes and contributors for a file.
"""
)
def get_scm_info(
    project_key: str,
    file_path: str,
    start: int = None,
    end: int = None,
    commits_by_line: bool = False,
) -> Dict[str, Any]:
    """Retrieve SCM information for a file in a SonarQube project.

    Returns SCM details (author, date, revision) per line, optionally for a range.

    Args:
        project_key (str): Key of the project (e.g., 'my-project').
        file_path (str): Path to the file within the project (e.g., "src/main.java").
        start (int]): Starting line number (positive integer). Defaults to None.
        end (int]): Ending line number (positive integer, >= start). Defaults to None.
        commits_by_line (bool, optional): If True, include commits for each line; if False, group by commit. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary with SCM details per line.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_scm_info(
        file_key=file_key,
        start=start,
        end=end,
        commits_by_line=commits_by_line,
    )

    return response


@mcp.tool(
    description="""
Retrieve raw source code as plain text for a file in a SonarQube project.
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main.java')
Returns: String with raw source code.
Use to get the full file content as plain text.
"""
)
def get_source_raw(project_key: str, file_path: str) -> str:
    """Retrieve raw source code as plain text for a file in a SonarQube project.

    Args:
        project_key (str): Key of the project (e.g., 'my_project').
        file_path (str): Path to the file within the project (e.g., 'src/main.java').
    Returns:
        str: Raw source code as a plain text.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_source_raw(file_key=file_key)

    return response


@mcp.tool(
    description="""
Retrieve code snippets for a specific SonarQube issue.
Parameters:
- issue_key (Required[str], issue key)
Returns: Dictionary with code snippets around the issue location.
Use to view source code context for an issue.
"""
)
def get_source_issue_snippets(issue_key: str):
    """Retrieve code snippets associated with a specific SonarQube issue.

    Provides source code snippets around the issue's location for context.

    Args:
        issue_key (str): The key of the issue. Must be non-empty.

    Returns:
        Dict[str, Any]: A dictionary with code snippets for the issue.
    """

    response = sonar_client.get_source_issue_snippets(issue_key=issue_key)

    return response


@mcp.tool(description="""
Retrieve issues, rule details, source code snippets, and full file source for a specific file in a SonarQube project.
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main/java/Example.java')
Returns: Dictionary with issues (including rule details and snippets) and full file source.
Use to gather comprehensive issue data for a file to recommend code fixes.
""")
def get_file_issues_information(project_key: str, file_path: str) -> Dict[str, Any]:
    """Retrieve issues, rule details, source code snippets, and full file source for a specific file in a SonarQube project.

    Calls the SonarQube client to fetch all issues for the specified file, including detailed rule information,
    source code snippets around issue locations, and the full source code of the file to provide context for
    recommending fixes. Handles cases where snippet responses lack `startLine` and `endLine` by inferring them.

    Args:
        project_key (str): The key of the project (e.g., 'my_project'). Must be non-empty.
        file_path (str): The file path within the project (e.g., 'src/main/java/Example.java'). Must be non-empty.

    Returns:
        Dict[str, Any]: A dictionary containing issues with their rule details, source code snippets, and full file source.
    """
    response = sonar_client.get_file_issues_information(project_key=project_key, file_path=file_path)

    return response
