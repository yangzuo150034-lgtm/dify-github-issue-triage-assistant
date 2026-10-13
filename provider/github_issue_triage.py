from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from github_api import GitHubApiClient, GitHubApiError


class GithubIssueTriageProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = str(credentials.get("github_token") or "")
        try:
            GitHubApiClient(token).get_authenticated_login()
        except GitHubApiError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

