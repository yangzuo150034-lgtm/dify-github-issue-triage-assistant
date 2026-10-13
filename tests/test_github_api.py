from __future__ import annotations

from typing import Any

import pytest
import requests

from github_api import GitHubApiClient, GitHubApiError


class FakeResponse:
    def __init__(
        self,
        payload: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}
        self.ok = 200 <= status_code < 300

    def json(self) -> Any:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse] | None = None) -> None:
        self.responses = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        return self.responses.pop(0)


def issue(number: int, *, pull_request: bool = False) -> dict[str, Any]:
    value: dict[str, Any] = {
        "number": number,
        "title": f"Issue {number}",
        "body": "Example body",
        "state": "open",
        "labels": [{"name": "bug"}],
        "comments": 2,
        "user": {"login": "octocat"},
        "created_at": "2026-10-01T00:00:00Z",
        "updated_at": "2026-10-02T00:00:00Z",
        "html_url": f"https://github.com/example/repo/issues/{number}",
    }
    if pull_request:
        value["pull_request"] = {"url": "https://api.github.com/pulls/1"}
    return value


def test_fetches_issues_and_excludes_pull_requests() -> None:
    session = FakeSession([FakeResponse([issue(3, pull_request=True), issue(2), issue(1)])])
    result = GitHubApiClient("secret", session=session).fetch_issues(
        "example", "repo", max_issues=2
    )

    assert [item["number"] for item in result.issues] == [2, 1]
    assert result.pages_fetched == 1
    assert result.api_items_scanned == 3
    assert "Authorization" in session.calls[0]["headers"]
    assert "secret" not in str(result.issues)


def test_uses_another_page_when_first_page_contains_only_pull_requests() -> None:
    first_page = [issue(number, pull_request=True) for number in range(100)]
    second_page = [issue(101)]
    session = FakeSession([FakeResponse(first_page), FakeResponse(second_page)])

    result = GitHubApiClient("secret", session=session).fetch_issues(
        "example", "repo", max_issues=1
    )

    assert [item["number"] for item in result.issues] == [101]
    assert result.pages_fetched == 2


def test_reports_rate_limit_without_exposing_token() -> None:
    response = FakeResponse(
        {"message": "rate limited"},
        status_code=403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1893456000"},
    )
    client = GitHubApiClient("do-not-leak", session=FakeSession([response]))

    with pytest.raises(GitHubApiError, match="rate limit exceeded") as error:
        client.fetch_issues("example", "repo")
    assert "do-not-leak" not in str(error.value)


def test_converts_timeout_to_clear_error() -> None:
    class TimeoutSession:
        def get(self, *_args: Any, **_kwargs: Any) -> FakeResponse:
            raise requests.Timeout("network detail")

    client = GitHubApiClient("secret", session=TimeoutSession())
    with pytest.raises(GitHubApiError, match="timed out"):
        client.fetch_issues("example", "repo")


@pytest.mark.parametrize("value", [0, 31])
def test_rejects_invalid_maximum(value: int) -> None:
    with pytest.raises(GitHubApiError, match="between 1 and 30"):
        GitHubApiClient("secret", session=FakeSession()).fetch_issues(
            "example", "repo", max_issues=value
        )


def test_dify_provider_and_tool_modules_load() -> None:
    """Catch SDK import incompatibilities before starting remote debug."""
    from provider.github_issue_triage import GithubIssueTriageProvider
    from tools.fetch_github_issues import FetchGithubIssuesTool

    assert GithubIssueTriageProvider.__name__ == "GithubIssueTriageProvider"
    assert FetchGithubIssuesTool.__name__ == "FetchGithubIssuesTool"
