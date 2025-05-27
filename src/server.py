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


@mcp.tool(description="Check SonarQube system health")
def get_system_health() -> Dict[str, Any]:
    """
    Retrieves SonarQube system health status.
    Returns:
        Dictionary with health status and node details.
    """
    response = sonar_client.get_system_health()
    return response


@mcp.tool(description="Check SonarQube system status")
def get_system_status() -> Dict[str, Any]:
    """
    Retrieves SonarQube system status.
    Returns:
        Dictionary with system status and description.
    """
    response = sonar_client.get_system_status()
    return response


@mcp.tool(description="Ping SonarQube server")
def system_ping() -> bool:
    """
    Pings the SonarQube server to check if it is reachable.
    Returns:
        List with a single string indicating "pong" or an error message.
    """
    response = sonar_client.system_ping()
    return response


@mcp.tool(description="List all SonarQube projects")
def list_projects(search: Optional[str] = None, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """
    Lists all projects in SonarQube.
    Args:
        page: Page number for pagination (default: 1).
        page_size: Number of projects per page (default: 100, max: 500).
    Returns:
        List of projects.
    """
    response = sonar_client.list_projects(page=page, page_size=page_size, search=search)
    return response


@mcp.tool(description="List projects accessible to the authenticated user")
def list_user_projects(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """
    Lists projects accessible to the authenticated user.
    Args:
        page: Page number for pagination (default: 1).
        page_size: Number of projects per page (default: 100, max: 500).
    Returns:
        List of strings with project name and key in the format "name (key)".
    """
    response = sonar_client.list_user_projects(page=page, page_size=page_size)
    return response


@mcp.tool(description="List scannable projects for the authenticated user")
def list_user_scannable_projects(search: Optional[str] = None) -> Dict[str, Any]:
    """
    Lists scannable projects for the authenticated user.
    Args:
        search: Optional search query to filter projects by name.
    Returns:
        List of strings with project name and key in the format "name (key)".
    """
    response = sonar_client.list_user_scannable_projects(search=search)
    return response


@mcp.tool(description="List project analyses")
def list_project_analyses(
    project_key: str,
    category: Optional[str] = None,
    branch: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
):
    response = sonar_client.list_project_analyses(
        project_key=project_key,
        category=category,
        branch=branch,
        page=page,
        page_size=page_size,
    )

    return response


@mcp.tool(description="Search for issues in SonarQube")
def get_issues(
    project_keys: Optional[str] = None,
    additional_fields: Optional[str] = None,
    assigned: Optional[bool] = None,
    assignees: Optional[str] = None,
    authors: Optional[str] = None,
    issue_statuses: Optional[str] = None,
    issues: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    resolutions: Optional[str] = None,
    resolved: Optional[bool] = None,
    scopes: Optional[str] = None,
    severities: Optional[str] = None,
    tags: Optional[str] = None,
    types: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Searches for issues in SonarQube with optional filters.
    Args:
        project_keys: List of project keys to filter issues.
        additional_fields: Additional fields to include in response.
        assigned: Filter issues by assignment status.
        assignees: List of assignees to filter issues.
        authors: List of authors to filter issues.
        issue_statuses: List of issue statuses to filter.
        issues: List of issue keys to filter.
        page: Page number for pagination (default: 1).
        page_size: Number of issues per page (default: 100, max: 500).
        resolutions: List of resolutions to filter issues.
        resolved: Filter issues by resolved status.
        scopes: List of scopes to filter issues.
        severities: List of severities to filter issues.
        tags: List of tags to filter issues.
        types: List of issue types to filter.
    Returns:
        List of strings with issue details in the format "key: message (severity, status)".
    """
    response = sonar_client.get_issues(
        project_keys=project_keys,
        additional_fields=additional_fields,
        assigned=assigned,
        assignees=assignees,
        authors=authors,
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


@mcp.tool(description="Retrieve issues authors for a project")
def get_issues_authors(
    project_key: Optional[str] = None, page: int = 1, page_size: int = 100
) -> Dict[str, Any]:
    """
    Retrieves issues authors for a project.
    Args:
        project_key: Optional project key to filter authors.
        page: Page number for pagination (default: 1).
        page_size: Number of authors per page (default: 100, max: 500).
    Returns:
        List of issues author names.
    """
    response = sonar_client.get_issues_authors(
        project_key=project_key, page=page, page_size=page_size
    )

    return response


@mcp.tool(description="Retrieve available metric types")
def get_metrics_type() -> Dict[str, Any]:
    """
    Retrieves available metric types in SonarQube.
    Returns:
        List of metric type names.
    """
    response = sonar_client.get_metrics_type()
    return response


@mcp.tool(description="Retrieve available metrics")
def get_metrics(page: int = 1, page_size: int = 100) -> Dict[str, Any]:
    """
    Retrieves available metrics in SonarQube.
    Args:
        page: Page number for pagination (default: 1).
        page_size: Number of metrics per page (default: 100, max: 500).
    Returns:
        List of strings with metric name and key in the format "name (key)".
    """
    response = sonar_client.get_metrics(page=page, page_size=page_size)
    return response


@mcp.tool(description="List all quality gates")
def get_quality_gates() -> Dict[str, Any]:
    """
    Retrieves the list of quality gates in SonarQube.
    Returns:
        List of quality gate names.
    """
    response = sonar_client.get_quality_gates()
    return response


@mcp.tool(description="Get details of a specific quality gate")
def get_quality_gates_details(name: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific quality gate.
    Args:
        name: Name of the quality gate.
    Returns:
        Dictionary with quality gate details.
    """
    response = sonar_client.get_quality_gates_details(name=name)
    return response


@mcp.tool(description="Get quality gate associated with a project")
def get_quality_gates_by_project(project_key: str) -> Dict[str, Any]:
    """
    Retrieves the quality gate associated with a project.
    Args:
        project_key: Key of the project.
    Returns:
        Dictionary with quality gate details for the project.
    """
    response = sonar_client.get_quality_gates_by_project(project_key=project_key)
    return response


@mcp.tool(description="Get quality gate status for a project or analysis")
def get_quality_gates_project_status(
    analysis_id: str = "",
    project_key: str = "",
) -> Dict[str, Any]:
    """
    Retrieves quality gate status for a project or analysis.
    Args:
        analysis_id: ID of the analysis.
        project_key: Key of the project.
    Returns:
        Dictionary with quality gate status details.
    """
    response = sonar_client.get_quality_gates_project_status(
        analysis_id=analysis_id,
        project_key=project_key,
    )

    return response


@mcp.tool(description="Retrieve source code for a file")
def get_source(
    project_key: str,
    file_path: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Retrieves source code for a file in SonarQube.
    Args:
        project_key: Key of the project (e.g., "my-project").
        file_path: Path to the file within the project (e.g., "src/main.py").
        start: Starting line number (optional, must be positive).
        end: Ending line number (optional, must be positive and >= start).
    Returns:
        List of source code lines.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_source(file_key=file_key, start=start, end=end)

    return response


@mcp.tool(description="Retrieve SCM information for a file")
def get_scm_info(
    project_key: str,
    file_path: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
    commits_by_line: bool = False,
) -> Dict[str, Any]:
    """
    Retrieves SCM information for a file in SonarQube.
    Args:
        project_key: Key of the project (e.g., "my-project").
        file_path: Path to the file within the project (e.g., "src/main.py").
        start: Starting line number (optional).
        end: Ending line number (optional).
        commits_by_line: Whether to include commits by line (default: False).
    Returns:
        Dictionary with SCM details per line.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_scm_info(
        file_key=file_key,
        start=start,
        end=end,
        commits_by_line=commits_by_line,
    )

    return response


@mcp.tool(description="Retrieve raw source code for a file")
def get_source_raw(project_key: str, file_path: str) -> str:
    """
    Retrieves raw source code for a file in SonarQube.
    Args:
        project_key: Key of the project (e.g., "my-project").
        file_path: Path to the file within the project (e.g., "src/main.py").
    Returns:
        List of source code lines.
    """
    file_key = f"{project_key}:{file_path}"
    response = sonar_client.get_source_raw(file_key=file_key)

    return response
