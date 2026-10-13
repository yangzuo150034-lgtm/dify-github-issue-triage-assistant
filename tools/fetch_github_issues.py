import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from github_api import GitHubApiClient, GitHubApiError


class FetchGithubIssuesTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            max_issues = int(tool_parameters.get("max_issues", 10))
        except (TypeError, ValueError) as exc:
            raise RuntimeError("Maximum issues must be a whole number.") from exc

        token = str(self.runtime.credentials.get("github_token") or "")
        try:
            result = GitHubApiClient(token).fetch_issues(
                owner=str(tool_parameters.get("owner") or ""),
                repository=str(tool_parameters.get("repository") or ""),
                state=str(tool_parameters.get("state") or "open"),
                max_issues=max_issues,
                labels=str(tool_parameters.get("labels") or ""),
            )
        except GitHubApiError as exc:
            # The plugin runtime converts uncaught exceptions into a failed tool
            # invocation. SDK 0.9.x does not expose a ToolInvokeError class.
            raise RuntimeError(str(exc)) from exc

        payload = {
            "repository": (
                f"{str(tool_parameters.get('owner') or '').strip()}/"
                f"{str(tool_parameters.get('repository') or '').strip()}"
            ),
            "state": str(tool_parameters.get("state") or "open"),
            "labels_filter": str(tool_parameters.get("labels") or ""),
            "issue_count": len(result.issues),
            "pages_fetched": result.pages_fetched,
            "api_items_scanned": result.api_items_scanned,
            "issues": result.issues,
        }

        # Dify exposes the generic `text` output most consistently across Cloud
        # versions. Emit the same structured payload as both JSON and JSON text
        # so workflows can consume it without losing any fields.
        yield self.create_json_message(payload)
        yield self.create_text_message(json.dumps(payload, ensure_ascii=False))
