# Demo Video Script

Target length: 4–5 minutes. Record the screen in English and keep all tokens,
API keys, and credential values hidden.

## 1. Introduction — 20 seconds

**Show:** The GitHub repository home page.

**Say:**

> Hello, I am presenting GitHub Issue AI Triage Assistant, a Dify plugin and
> Workflow built for the Dify DevRel Intern technical assessment. It retrieves
> real issues from a public GitHub repository and uses an LLM to turn them into
> an actionable English triage report.

## 2. Problem and Architecture — 35 seconds

**Show:** The architecture section in `README.md`.

**Say:**

> Maintainers often need to review many new issues and decide their category,
> priority, owner, and next action. This project separates deterministic data
> collection from AI analysis. A Python tool plugin calls the GitHub REST API,
> and a four-node Dify Workflow passes the structured issue data to an LLM and
> returns a Markdown report. The Workflow is hosted on Dify Cloud, so a full
> local Dify deployment is not required.

## 3. Plugin Implementation — 70 seconds

**Show:** `manifest.yaml`, `tools/fetch_github_issues.yaml`,
`tools/fetch_github_issues.py`, and `github_api.py`.

**Say:**

> The plugin is implemented with Python and the Dify Plugin SDK. Its inputs are
> repository owner, repository name, issue state, maximum issue count, and an
> optional label filter. The GitHub token is configured as a secret credential
> in Dify and is never committed to the repository.
>
> The API client uses HTTPS, explicit connection and read timeouts, pagination,
> and clear error handling for invalid credentials, missing repositories, rate
> limits, validation errors, server errors, and malformed responses. GitHub's
> issues endpoint also returns pull requests, so the plugin explicitly removes
> every item containing the pull request field. It emits both JSON and text
> messages so the structured result remains compatible with the Dify Workflow
> tool node.

## 4. Tests and Documentation — 35 seconds

**Show:** `tests/test_github_api.py`, then run this command in the VS Code
terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**Say:**

> The automated tests cover successful retrieval, pull request exclusion,
> pagination, label forwarding, token failures, rate limits, not-found errors,
> and timeouts. The repository also includes an English README, privacy policy,
> MIT license, environment example, and the exported Workflow DSL.

## 5. Dify Workflow — 45 seconds

**Show:** The Dify Studio canvas and click each node from left to right. Do not
open any credential value.

**Say:**

> The Workflow has four nodes. User Input collects the repository and filters.
> Fetch GitHub Issues runs the custom plugin. The LLM node follows an English
> triage prompt that treats issue content as untrusted data, assigns a category
> and priority, explains its evidence, and recommends an owner and next action.
> Finally, the Output node returns the generated Markdown report.

## 6. Live Demo — 75 seconds

**Show:** Open the published Web App and enter:

- Repository owner: `langgenius`
- Repository name: `dify`
- Issue state: `open`
- Maximum issues: `3`
- Labels: leave blank

Click **Run**, then scroll through the result.

**Say:**

> I will now run the published Web App against the public langgenius slash dify
> repository. I am requesting three open issues without a label filter. The
> plugin fetches live GitHub data, excludes pull requests, and the LLM produces
> the report.
>
> The result begins with an executive summary and an overview table. Each issue
> includes its real GitHub URL, category, priority, suggested owner, evidence,
> and a concrete recommended action. This output helps a maintainer understand
> what needs attention while keeping the final decision with the human team.

## 7. Closing — 20 seconds

**Show:** Return to the repository home page, with the README and DSL visible.

**Say:**

> The source code, setup instructions, tests, privacy documentation, and Dify
> Workflow DSL are available in this public repository. The published Web App
> is linked from the README. Thank you for watching.

## Recording Checklist

- Use 1080p if possible and enlarge the browser or editor text before recording.
- Close unrelated tabs and disable desktop notifications.
- Never show the GitHub token, Dify debug key, or any credential configuration.
- Confirm the Web App works immediately before recording.
- Keep the terminal command and test result visible for two or three seconds.
- Verify that narration, interface text, and report discussion are all English.
- Upload the final video with link access enabled, then add its URL to the README.
