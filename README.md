# GitHub Issue AI Triage Assistant

Turn a batch of public GitHub Issues into a maintainer's first-pass report. The [Dify](https://dify.ai/) workflow suggests a category, priority, and next action while keeping source links available for review. It does not label, close, or comment on issues.

**[Open the hosted Dify demo](https://udify.app/workflow/rRFMf12ZMNKOPkWP)** · [Read an example](#example-report) · [Install your own copy](#requirements)

## Try it

1. Open the demo and use the prefilled public repository, `langgenius/dify`.
2. Select `open`, enter `3` as the maximum, and leave the label filter empty.
3. Run the workflow. Open an original GitHub issue from the report to check the evidence before acting on a suggestion.

If the hosted demo is unavailable, you can still inspect the example below and the [exported workflow](github-issue-ai-triage-assistant.yml).

**中文速览：** 这是一个只读的 GitHub Issue 分拣工具。它用 Dify 把公开仓库的 Issue 整理成一份英文报告，给出分类、优先级和下一步建议。体验时先用默认仓库试跑 3 条；最终判断由维护者完成。

## Example report

Illustrative output only, using fictional issues. The live workflow's wording and categories may vary.

| Issue summary | Suggested category | Suggested priority | Why | Next action |
| --- | --- | --- | --- | --- |
| Import fails after upgrading | Bug | High | Report includes a reproducible failure and affected version | Confirm on the current release with a minimal sample |
| Install guide omits a prerequisite | Documentation | Normal | Reporter identifies the missing setup step | Verify the requirement, then update the quick start |

The report is a review aid. Use the source issue to confirm any proposed category, priority, or action.

## Features

- Fetches open, closed, or all issues from a selected public repository.
- Supports an optional comma-separated GitHub label filter.
- Uses pagination until the requested number of real issues is collected.
- Excludes pull requests returned by GitHub's Issues endpoint.
- Keeps the GitHub token in Dify's secret credential store.
- Handles authentication failures, rate limits, missing repositories, invalid requests, server errors, and network timeouts.
- Truncates unusually long issue bodies to keep Workflow input manageable.

## Architecture

```text
User input
   -> GitHub Issue Triage plugin
   -> GitHub REST API
   -> structured issue JSON
   -> Dify LLM analysis
   -> English triage report
```

The plugin retrieves source data only. The Workflow's LLM performs classification and prioritization, keeping API integration separate from AI reasoning.

## Requirements

- Python 3.12
- Dify Plugin CLI
- A Dify Cloud workspace
- A GitHub fine-grained personal access token

## GitHub Token Setup

Create a fine-grained personal access token at GitHub. For public repository testing, select **Public repositories (read-only)** and use the shortest practical expiration period. Never commit the token or paste it into source code, screenshots, issues, or chat messages.

If a token is exposed, revoke it immediately and create a replacement.

## Local Setup on Windows

```powershell
cd "C:\path\to\dify-github-assistant"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

To run tests:

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

The current test suite contains seven tests covering API pagination, pull
request filtering, HTTP errors, timeouts, normalization, and SDK module loading.

## Configure Remote Debugging

1. Open **Dify Cloud > Plugins > Debug Plugin**.
2. Copy `.env.example` to `.env`.
3. Put the Dify remote debugging URL and key in `.env`.
4. Do not put the GitHub token in `.env`; configure it through the plugin credential form in Dify.
5. Start the local plugin:

```powershell
.\.venv\Scripts\python.exe main.py
```

In Dify, add a GitHub Issue Triage credential and paste the GitHub token into the secret field. Dify validates it with `GET /user`.

## Tool Inputs

| Input | Required | Description |
|---|---:|---|
| `owner` | Yes | GitHub organization or username, such as `langgenius` |
| `repository` | Yes | Repository name, such as `dify` |
| `state` | Yes | `open`, `closed`, or `all` |
| `max_issues` | Yes | Number of real issues to return, from 1 to 30 |
| `labels` | No | Comma-separated labels, such as `bug,help wanted` |

## Example

Input:

```json
{
  "owner": "langgenius",
  "repository": "dify",
  "state": "open",
  "max_issues": 5,
  "labels": ""
}
```

The output contains repository metadata and an `issues` array. Each issue includes its number, title, body, labels, comment count, author, timestamps, and URL.

## Dify Workflow

The exported Workflow DSL is available at
[`github-issue-ai-triage-assistant.yml`](github-issue-ai-triage-assistant.yml).

The Workflow contains four nodes:

1. **User Input** collects the repository owner, repository name, issue state,
   maximum issue count, and optional labels.
2. **Fetch GitHub Issues** calls this plugin and returns real Issue data.
3. **LLM** categorizes each Issue, assigns priority, explains the evidence, and
   recommends a maintainer action and owner type.
4. **Output** returns the English Markdown triage report.

The exported DSL intentionally excludes credentials. After importing it, select
your own GitHub plugin credential and an available LLM model before running it.

## Package the Plugin

Run the package command from the directory that contains this repository. The
output package must be outside the plugin source directory:

```powershell
cd "C:\path\to"
dify plugin package .\dify-github-assistant -o .\github_issue_triage.difypkg
```

The generated `.difypkg` file is intentionally ignored by Git because it is a
build artifact. In Dify Cloud, open **Integrations > Install > Local Package**,
upload the package, and configure the GitHub credential through the plugin UI.

## Security and Privacy

- Credentials are sent only to GitHub over HTTPS.
- Tokens are never included in tool output or error messages.
- The plugin performs read-only API requests.
- Issue content is passed to the configured Dify Workflow and model for analysis.

See [PRIVACY.md](PRIVACY.md) for details.

## Project Status

The assessment implementation is complete and has been verified with:

- Seven passing automated tests.
- Dify remote debugging on Windows.
- Installation as a Dify Cloud local plugin package.
- A four-node Workflow using live GitHub Issue data.
- A published Web App producing an English triage report.

The step-by-step English recording plan is available in
[`DEMO_SCRIPT.md`](DEMO_SCRIPT.md).

## License

MIT
