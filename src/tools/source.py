from typing import Optional, Dict, Any
from server import mcp, sonar_client


@mcp.tool(
    description="""
Retrieve source code for a file in a SonarQube project.
"""
)
async def get_source(
    project_key: str,
    file_path: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
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
    response = await sonar_client.get_source(file_key=file_key, start=start, end=end)

    return response


@mcp.tool(
    description="""
Retrieve SCM information for a file in a SonarQube project.
"""
)
async def get_scm_info(
    project_key: str,
    file_path: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
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
    response = await sonar_client.get_scm_info(
        file_key=file_key,
        start=start,
        end=end,
        commits_by_line=commits_by_line,
    )

    return response


@mcp.tool(
    description="""
Retrieve raw source code as plain text for a file in a SonarQube project.
"""
)
async def get_source_raw(project_key: str, file_path: str) -> str:
    """Retrieve raw source code as plain text for a file in a SonarQube project.

    Args:
        project_key (str): Key of the project (e.g., 'my_project').
        file_path (str): Path to the file within the project (e.g., 'src/main.java').
    Returns:
        str: Raw source code as a plain text.
    """
    file_key = f"{project_key}:{file_path}"
    response = await sonar_client.get_source_raw(file_key=file_key)

    return response


@mcp.tool(
    description="""
Retrieve code snippets for a specific SonarQube issue.
"""
)
async def get_source_issue_snippets(issue_key: str):
    """Retrieve code snippets associated with a specific SonarQube issue.

    Provides source code snippets around the issue's location for context.

    Args:
        issue_key (str): The key of the issue. Must be non-empty.

    Returns:
        Dict[str, Any]: A dictionary with code snippets for the issue.
    """

    response = await sonar_client.get_source_issue_snippets(issue_key=issue_key)

    return response


@mcp.tool(
    description="""
Retrieve issues, rule details, source code snippets, and full file source for a specific file in a SonarQube project.
"""
)
async def get_file_issues_information(
    project_key: str,
    file_path: str,
    include_source: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """Retrieve issues, rule details, source code snippets, and full file source for a specific file in a SonarQube project.

    Calls the SonarQube client to fetch all issues for the specified file, including detailed rule information,
    source code snippets around issue locations, and the full source code of the file to provide context for
    recommending fixes. Handles cases where snippet responses lack `startLine` and `endLine` by inferring them.

    Args:
        project_key (str): The key of the project (e.g., 'my_project'). Must be non-empty.
        file_path (str): The file path within the project (e.g., 'src/main/java/Example.java'). Must be non-empty.
        include_source(bool, opitional): Whether include raw source code or not. Default to True.
        page (int, optional): Page number for pagination (must be positive). Defaults to 1.
        page_size (int, optional): Number of issues per page (must be positive, max 20). Defaults to 20.

    Returns:
        Dict[str, Any]: A dictionary containing issues with their rule details, source code snippets, and full file source.
    """
    response = await sonar_client.get_file_issues_information(
        project_key=project_key, file_path=file_path
    )

    return response
