from typing import Dict, Any
from server import mcp, sonar_client


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
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main.java')
Returns: String with raw source code.
Use to get the full file content as plain text.
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
Parameters:
- issue_key (Required[str], issue key)
Returns: Dictionary with code snippets around the issue location.
Use to view source code context for an issue.
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
Parameters:
- project_key (Required[str], project key, e.g., 'my_project')
- file_path (Required[str], file path, e.g., 'src/main/java/Example.java')
Returns: Dictionary with issues (including rule details and snippets) and full file source.
Use to gather comprehensive issue data for a file to recommend code fixes.
"""
)
async def get_file_issues_information(
    project_key: str, file_path: str
) -> Dict[str, Any]:
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
    response = await sonar_client.get_file_issues_information(
        project_key=project_key, file_path=file_path
    )

    return response
