import logging
from typing import Optional, Dict, Any

from .hotspot import SonarQubeHotSpot
from .issue import SonarQubeIssue
from .metrics import SonarQubeMetric
from .permission import SonarQubePermission
from .projects import SonarQubeProjects
from .qualitygate import SonarQubeQualityGate
from .qualityprofile import SonarQubeQualityProfile
from .rule import SonarQubeRule
from .source import SonarQubeSource
from .system import SonarQubeSystem

logger = logging.getLogger(__name__)


class SonarQubeClient(
    SonarQubeHotSpot,
    SonarQubeIssue,
    SonarQubeMetric,
    SonarQubePermission,
    SonarQubeProjects,
    SonarQubeQualityGate,
    SonarQubeQualityProfile,
    SonarQubeRule,
    SonarQubeSource,
    SonarQubeSystem,
):
    """
    Unified SonarQube client providing access to all SonarQube API functionality.

    This class combines methods for system operations, projects, issues, hotspots,
    quality gates/profiles, rules, and source code management. Initialize using
    the async `create` classmethod.

    """

    async def get_file_issues_information(
        self,
        project_key: str,
        file_path: str,
        include_source: bool = True,
        page: int = 1,
        page_size: int = 20,
        branch: Optional[str] = None,
        resolved: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Retrieve issues, rule details, source code snippets, and full file source for a specific file in a SonarQube project.

        Fetches all issues for the specified file, retrieves detailed rule information for each issue,
        includes source code snippets around issue locations, and attaches the full source code of the file
        to provide context for fix recommendations.

        Args:
            project_key (str): The key of the project (e.g., 'my_project'). Must be non-empty.
            file_path (str): The file path within the project (e.g., 'src/main/java/Example.java'). Must be non-empty.
            include_source(bool, opitional): Whether include raw source code or not. Default to True.
            page (int, optional): Page number for pagination (must be positive). Defaults to 1.
            page_size (int, optional): Number of issues per page (must be positive, max 20). Defaults to 20.
            branch (str, optional): Branch key to filter issues (e.g., 'feature/branch'). Not available in Community Edition. Defaults to None.
            resolved (Optional[bool], optional): Filter for resolved (True) or unresolved (False) issues. Defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing issues with their rule details, source code snippets, and full file source.
        """
        if not project_key or not project_key.strip():
            logger.error("project_key must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "project_key must be a non-empty string",
            }

        if not file_path or not file_path.strip():
            logger.error("file_path must be a non-empty string")
            return {
                "error": "Invalid parameters",
                "details": "file_path must be a non-empty string",
            }

        if page < 1:
            logger.error("page must be positive integers")
            page = 1

        if page_size < 1:
            logger.error("page_size must be positive integers")
            page_size = 20

        if page_size > 20:
            logger.warning("Page size capped at 20")
            page_size = 20

        component = f"{project_key}:{file_path}"

        result = {
            "project_key": project_key,
            "file_path": file_path,
            "paging": {
                "page": page,
                "page_size": page_size,
            },
            "branch": branch,
            "full_source": "",
            "issues": [],
            "total_issues": 0,
            "errors": [],
        }

        result = {k: v for k, v in result.items() if v is not None}

        if include_source:

            source_response = await self.get_source_raw(file_key=component)

            if isinstance(source_response, dict) and "error" in source_response:
                logger.error(
                    f"Failed to fetch full source: {source_response.get('details', 'Unknown error')}"
                )
                result["errors"].append(
                    f"Full source fetch failed: {source_response.get('details', 'Unknown error')}"
                )
            else:
                result["full_source"] = (
                    source_response if isinstance(source_response, str) else ""
                )

        issues_response = await self.get_issues(
            additional_fields="_all",
            branch=branch,
            components=component,
            page_size=page_size,
            resolved=resolved,
        )

        if isinstance(issues_response, dict) and "error" in issues_response:
            logger.error(
                f"Failed to fetch issues: {issues_response.get('details', 'Unknown error')}"
            )
            result["errors"].append(
                f"Issue fetch failed: {issues_response.get('details', 'Unknown error')}"
            )
            return result

        issues = issues_response.get("issues", [])
        total_issues = issues_response.get("paging", {}).get("total", 0)
        result["total_issues"] = total_issues

        for issue in issues:
            issue_key = issue.get("key")
            issue_data = {
                "key": issue_key,
                "message": issue.get("message"),
                "severity": issue.get("severity"),
                "status": issue.get("status"),
                "line": issue.get("line"),
                "rule_key": issue.get("rule"),
                "rule": {},
                "source_snippet": {},
            }

            rule_response = await self.get_rule_details(rule_key=issue.get("rule"))

            if isinstance(rule_response, dict) and "error" in rule_response:
                logger.error(
                    f"Failed to fetch rule {issue.get('rule')}: {rule_response.get('details', 'Unknown error')}"
                )
                result["errors"].append(
                    f"Rule {issue.get('rule')} fetch failed: {rule_response.get('details', 'Unknown error')}"
                )
            else:
                rule = rule_response.get("rule", {})
                issue_data["rule"] = {
                    "key": rule.get("key"),
                    "name": rule.get("name"),
                    "description": rule.get("descriptionSections"),
                    "severity": rule.get("severity"),
                    "type": rule.get("type"),
                    "impacts": rule.get("impacts"),
                }

            snippet_response = await self.get_source_issue_snippets(issue_key=issue_key)
            if isinstance(snippet_response, dict) and "error" in snippet_response:
                error_msg = f"Failed to fetch snippet for issue {issue_key}: {snippet_response.get('details', 'Unknown error')}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
            else:
                snippet_key = f"{project_key}:{file_path}"
                snippet = snippet_response.get(snippet_key, {}).get("sources", {})
                if snippet:

                    issue_data["source_snippet"] = {
                        "startLine": snippet[0].get("line", 0),
                        "endLine": snippet[-1].get("line", 0),
                        "code": snippet,
                    }

            result["issues"].append(issue_data)

        return result
