# Sample GitHub Issue triage report

This is a **handwritten example with fictional issues**. It shows the expected report structure without running the hosted app, installing Dify, or supplying a GitHub token. This is not a recorded model run, and the issue numbers below do not refer to real issues.

## Example input

- Repository: `example/sample-project` (fictional)
- State: `open`
- Maximum issues: `3`
- Label filter: none

| Issue | Title | Evidence available to the reviewer |
| --- | --- | --- |
| #101 | CSV import fails after upgrading | Reporter lists a version and a minimal example with a quoted field; maintainers have not reproduced it yet. |
| #102 | Setup guide omits a dependency | Reporter identifies the command and quotes the missing dependency error. |
| #103 | Add a bulk retry action | Reporter describes the repeated manual clicks, but does not list constraints or expected failure handling. |

## Example output

### Executive summary

Start with #101 because it could prevent existing users from importing files. #102 is a scoped documentation check. #103 needs more information before implementation.

| Issue | Proposed category | Proposed priority | Suggested owner | Next action |
| --- | --- | --- | --- | --- |
| #101 | Bug | High | Import subsystem | Try the minimal example on the affected and current versions; record whether the problem reproduces. |
| #102 | Documentation | Medium | Docs or packaging | Confirm the dependency on a clean installation, then update the setup guide. |
| #103 | Feature request | Low | Product or frontend | Ask how users select retries and what should happen when a subset fails. |

### Evidence and limits

- **#101:** The minimal example makes the report actionable, but severity is provisional until reproduced.
- **#102:** An installation error supports investigating the setup guide. It does not establish that every platform has the same dependency.
- **#103:** The use case is plausible, but evidence does not yet support a design decision.

In a live report, follow the original issue links before acting. The workflow is read-only and does not apply labels or change issue state.

[Back to the project README](../README.md)
