import logging
from typing import Optional, Dict, Any
from .base import SonarQubeBase

logger = logging.getLogger(__name__)


class SonarQubeIssue(SonarQubeBase):

    async def get_issues(
        self,
        additional_fields: Optional[str] = None,
        assigned: Optional[bool] = None,
        assignees: Optional[str] = None,
        authors: Optional[str] = None,
        branch: Optional[str] = None,
        components: Optional[str] = None,
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
        """Search for issues in SonarQube projects with specified filters.

        Args:
            additional_fields (Optional[str], optional): Comma-separated list of optional fields to include in the response (e.g., 'comments,rules'). Defaults to None. Possible values: _all, comments, languages, rules, ruleDescriptionContextKey, transitions, actions, users.
            assigned (Optional[bool], optional): Filter for assigned (True) or unassigned (False) issues. Defaults to None.
            assignees (Optional[str], optional): Comma-separated list of assignee logins, '__me__' for the current user. Defaults to None.
            authors (Optional[str], optional): Comma-separated list of SCM author accounts. For example: torvalds@linux-foundation.org,linux@fondation.org . Defaults to None.
            branch (Optional[str], optional): Branch key to filter issues (not available in Community Edition). Defaults to None.
            components (Optional[str], optional): Comma-separated list of component keys. Retrieve issues associated to a specific list of components (and all its descendants). A component can be a portfolio, project, module, directory or file.
            issue_statuses (Optional[str], optional): Comma-separated list of issue statuses (e.g., 'OPEN,CONFIRMED,FIXED'). Defaults to None. Possible values: OPEN, CONFIRMED, FALSE_POSITIVE, ACCEPTED, FIXED.
            issues (Optional[str], optional): Comma-separated list of issue keys to retrieve specific issues. Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of issues per page (must be positive, max 500). Defaults to 100.
            resolutions (Optional[str], optional): Comma-separated list of resolutions (e.g., 'FIXED,FALSE-POSITIVE'). Defaults to None. Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED.
            resolved (Optional[bool], optional): Filter for resolved (True) or unresolved (False) issues. Defaults to None.
            scopes (Optional[str], optional): Comma-separated list of scopes (e.g., 'MAIN,TEST'). Defaults to None. Possible values: MAIN, TEST.
            severities (Optional[str], optional): Comma-separated list of severities (e.g., 'BLOCKER,CRITICAL'). Defaults to None. Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER.
            tags (Optional[str], optional): Comma-separated list of issue tags (e.g., 'security,convention'). Defaults to None.
            types (Optional[str], optional): Comma-separated list of issue types (e.g., 'BUG,VULNERABILITY'). Defaults to None. Possible values: CODE_SMELL, BUG, VULNERABILITY.

        Returns:
            Dict[str, Any]: Dictionary containing a list of issues and pagination details, or an error response.
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

        endpoint = "/api/issues/search"

        params = [
            (
                "additionalFields",
                additional_fields.lower() if additional_fields else None,
            ),
            ("assigned", str(assigned).lower() if assigned is not None else None),
            ("assignees", assignees),
            ("branch", branch),
            ("components", components),
            ("issueStatuses", issue_statuses.upper() if issue_statuses else None),
            ("issues", issues),
            ("organization", self.organization),
            ("p", page),
            ("ps", page_size),
            ("resolutions", resolutions.upper() if resolutions else None),
            ("resolved", str(resolved).lower() if resolved is not None else None),
            ("scopes", scopes.upper() if scopes else None),
            ("severities", severities.upper() if severities else None),
            ("tags", tags),
            ("types", types.upper() if types else None),
        ]

        if authors:
            authors = authors.split(",")
            params.extend(("author", a) for a in authors)

        params = [(k, v) for k, v in params if v is not None]

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get issues failed: {response.get('details', 'Unknown error')}"
            )
        return response

    async def get_issues_authors(
        self,
        project_key: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> Dict[str, Any]:
        """Retrieve SCM authors for issues in a SonarQube project, with optional filtering.

        Args:
            project_key (Optional[str], optional): Project key to filter authors. Defaults to None.
            query (Optional[str], optional): Search query to filter authors by SCM account (partial match). Defaults to None.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of authors per page (must be positive, max 100). Defaults to 10.

        Returns:
            Dict[str, Any]: Dictionary containing a list of SCM authors, or an error response.
        """
        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 10

        if page_size > 100:
            logger.warning("Page size capped at 100 by SonarQube API")
            page_size = 100

        endpoint = "/api/issues/authors"

        params = {"project": project_key, "p": page, "ps": page_size}

        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request(endpoint=endpoint, params=params)
        if isinstance(response, dict) and "error" in response:
            logger.error(
                f"Get SCM authors failed: {response.get('details', 'Unknown error')}"
            )
        return response
