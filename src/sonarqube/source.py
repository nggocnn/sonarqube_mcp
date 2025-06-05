import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeSource(SonarQubeBase):

    async def get_source(
        self, file_key: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> Dict[str, Any]:
        """Retrieve source code for a specified file in a SonarQube project.

        Args:
            file_key (str): Key of the file to retrieve source code for (e.g., 'my_project:src/main/java/Example.java').
            start (Optional[int], optional): Starting line number (must be positive if provided). Defaults to None.
            end (Optional[int], optional): Ending line number (must be positive and >= start if provided). Defaults to None.

        Returns:
            Dict[str, Any]: Dictionary containing source code lines, or an error response.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        if start is not None and start < 1:
            logger.warning("Start line must be positive")
            start = None

        if end is not None and (end < 1 or (start is not None and end < start)):
            logger.warning(
                "End line must be positive and greater than or equal to start line"
            )
            start = None
            end = None

        endpoint = "/api/sources/show"
        params = {"key": file_key, "from": start, "to": end}
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get source failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_scm_info(
        self,
        file_key: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        commits_by_line: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """Retrieve SCM information for a specified file in a SonarQube project.

        Args:
            file_key (str): Key of the file to retrieve SCM information for (e.g., 'my_project:src/main/java/Example.java').
            start (Optional[int], optional): Starting line number (must be positive, starts at 1). Defaults to None.
            end (Optional[int], optional): Ending line number (must be positive and >= start, inclusive). Defaults to None.
            commits_by_line (Optional[bool], optional): If True, include commits for each line even if consecutive lines share
            the same commit; if False, group lines by commit. Defaults to False.

        Returns:
            Dict[str, Any]: Dictionary containing SCM information for the file, or an error response.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        if start is not None and start < 1:
            logger.warning("Start line must be positive")
            start = None

        if end is not None and (end < 1 or (start is not None and end < start)):
            logger.warning(
                "End line must be positive and greater than or equal to start line."
            )
            start = None
            end = None

        endpoint = "/api/sources/scm"

        params = {
            "key": file_key,
            "from": start,
            "to": end,
            "commits_by_line": commits_by_line,
        }

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get SCM info failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_source_raw(self, file_key) -> Any:
        """Retrieve raw source code for a specified file in a SonarQube project as plain text.

        Args:
            file_key (str): Key of the file to retrieve raw source code for (e.g., 'my_project:src/main/java/Example.java').

        Returns:
            str: Raw source code as a plain text string, or an error message as a string if the request fails.
        """
        if not file_key:
            logger.error("File key must not be empty")
            return {
                "error": "Invalid parameters",
                "details": "File key must not be empty",
            }

        endpoint = "/api/sources/raw"

        response = await self._make_request(
            endpoint=endpoint, params={"key": file_key}, raw_response=True
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get raw source failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_source_issue_snippets(self, issue_key: str):
        """Retrieve code snippets associated with a specific SonarQube issue.

        Provides source code snippets around the issue's location for context.

        Args:
            issue_key (str): The key of the issue. Must be non-empty.

        Returns:
            Dict[str, Any]: A dictionary with code snippets for the issue.
        """
        if not issue_key or not issue_key.strip():
            logger.error("issue_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "issue_key must be a non-empty string",
            }

        endpoint = "/api/sources/issue_snippets"

        response = await self._make_request(
            endpoint=endpoint, params={"issueKey": issue_key}
        )
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get issue snippets failed: {response.get('details', 'Unknown error')}"
            )
        return response
