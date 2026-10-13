"""Small, testable GitHub REST API client used by the Dify tool plugin."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import requests


API_BASE_URL = "https://api.github.com"
API_VERSION = "2026-03-10"
USER_AGENT = "dify-github-issue-triage/0.1.0"
CONNECT_TIMEOUT_SECONDS = 5
READ_TIMEOUT_SECONDS = 15
MAX_PAGES = 10
MAX_BODY_CHARACTERS = 4_000


class GitHubApiError(RuntimeError):
    """A safe, user-facing GitHub API error that never includes credentials."""


@dataclass(frozen=True)
class FetchResult:
    issues: list[dict[str, Any]]
    pages_fetched: int
    api_items_scanned: int


class GitHubApiClient:
    def __init__(self, token: str, session: requests.Session | None = None) -> None:
        token = token.strip()
        if not token:
            raise GitHubApiError("GitHub token is required.")

        self._session = session or requests.Session()
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        }

    def get_authenticated_login(self) -> str:
        response = self._request("/user")
        payload = self._parse_json(response)
        login = payload.get("login") if isinstance(payload, dict) else None
        if not isinstance(login, str) or not login:
            raise GitHubApiError("GitHub returned an unexpected authentication response.")
        return login

    def fetch_issues(
        self,
        owner: str,
        repository: str,
        *,
        state: str = "open",
        max_issues: int = 10,
        labels: str = "",
    ) -> FetchResult:
        owner = self._required_name(owner, "Repository owner")
        repository = self._required_name(repository, "Repository name")
        if state not in {"open", "closed", "all"}:
            raise GitHubApiError("State must be one of: open, closed, or all.")
        if not 1 <= max_issues <= 30:
            raise GitHubApiError("Maximum issues must be between 1 and 30.")

        path = f"/repos/{quote(owner, safe='')}/{quote(repository, safe='')}/issues"
        issues: list[dict[str, Any]] = []
        pages_fetched = 0
        api_items_scanned = 0

        for page in range(1, MAX_PAGES + 1):
            params: dict[str, Any] = {
                "state": state,
                "sort": "created",
                "direction": "desc",
                "per_page": 100,
                "page": page,
            }
            if labels.strip():
                params["labels"] = labels.strip()

            response = self._request(path, params=params)
            payload = self._parse_json(response)
            if not isinstance(payload, list):
                raise GitHubApiError("GitHub returned an unexpected issues response.")

            pages_fetched += 1
            api_items_scanned += len(payload)
            for item in payload:
                if not isinstance(item, dict) or "pull_request" in item:
                    continue
                issues.append(self._normalize_issue(item))
                if len(issues) >= max_issues:
                    return FetchResult(issues, pages_fetched, api_items_scanned)

            if len(payload) < 100:
                break

        return FetchResult(issues, pages_fetched, api_items_scanned)

    def _request(self, path: str, params: dict[str, Any] | None = None) -> requests.Response:
        try:
            response = self._session.get(
                f"{API_BASE_URL}{path}",
                headers=self._headers,
                params=params,
                timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
            )
        except requests.Timeout as exc:
            raise GitHubApiError(
                "GitHub API request timed out. Please try again."
            ) from exc
        except requests.RequestException as exc:
            raise GitHubApiError(
                "Could not connect to the GitHub API. Check the network and try again."
            ) from exc

        if response.ok:
            return response
        raise self._http_error(response)

    @staticmethod
    def _parse_json(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise GitHubApiError("GitHub returned an invalid JSON response.") from exc

    @staticmethod
    def _http_error(response: requests.Response) -> GitHubApiError:
        status = response.status_code
        if status == 401:
            return GitHubApiError(
                "GitHub rejected the token. Create a new token and update the plugin credential."
            )
        if status == 403:
            if response.headers.get("X-RateLimit-Remaining") == "0":
                reset = response.headers.get("X-RateLimit-Reset")
                reset_hint = ""
                if reset and reset.isdigit():
                    reset_time = datetime.fromtimestamp(int(reset), tz=UTC).isoformat()
                    reset_hint = f" The limit resets at {reset_time}."
                return GitHubApiError(f"GitHub API rate limit exceeded.{reset_hint}")
            return GitHubApiError(
                "GitHub denied this request. Check the token and repository access."
            )
        if status == 404:
            return GitHubApiError(
                "Repository not found or the token cannot access it. Check owner and repository."
            )
        if status == 422:
            return GitHubApiError(
                "GitHub rejected the request parameters. Check state, labels, and repository values."
            )
        if status >= 500:
            return GitHubApiError(
                f"GitHub API is temporarily unavailable (HTTP {status}). Please try again."
            )
        return GitHubApiError(f"GitHub API request failed (HTTP {status}).")

    @staticmethod
    def _required_name(value: str, field_name: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise GitHubApiError(f"{field_name} is required.")
        if len(cleaned) > 100:
            raise GitHubApiError(f"{field_name} is too long.")
        return cleaned

    @staticmethod
    def _normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
        body = item.get("body") or ""
        body = body if isinstance(body, str) else str(body)
        body_truncated = len(body) > MAX_BODY_CHARACTERS
        if body_truncated:
            body = f"{body[:MAX_BODY_CHARACTERS]}\n\n[Body truncated by plugin]"

        labels = []
        for label in item.get("labels") or []:
            if isinstance(label, dict) and isinstance(label.get("name"), str):
                labels.append(label["name"])
            elif isinstance(label, str):
                labels.append(label)

        user = item.get("user") if isinstance(item.get("user"), dict) else {}
        return {
            "number": item.get("number"),
            "title": item.get("title") or "",
            "body": body,
            "body_truncated": body_truncated,
            "state": item.get("state") or "",
            "labels": labels,
            "comments": item.get("comments") or 0,
            "author": user.get("login") or "unknown",
            "created_at": item.get("created_at") or "",
            "updated_at": item.get("updated_at") or "",
            "url": item.get("html_url") or "",
        }

