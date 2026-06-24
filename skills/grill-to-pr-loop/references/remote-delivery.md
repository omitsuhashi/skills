# Remote Delivery

Use this reference for GitHub issue mirroring, issue PR delivery, final PR creation, and remote-write approval policy.

Remote writes are optional. Push, GitHub issue creation, PR creation, ready-for-review, issue PR merge, force push, deploy, credential, permission, billing, production, and destructive actions require approved remote policy. Final PR merge always requires current human action.

## PR Delivery

Create issue PRs only after `issue-implementation-loop` returns `PR_READY` for every issue in the PR scope and after explicit remote-write approval.

For `batch_issue_prs`:

- `epic_base.ref` must be `codex/<epic-id>/epic-base`.
- Issue PRs use head `codex/<epic-id>/<local-id>-<slug>` and base `epic_base.ref`.
- The agent may merge issue PRs when checks/review/mergeability pass and the approved policy says `agent_default_with_human_escalation`.
- Escalate to the human for scope drift, spec ambiguity, failed checks, conflicts, unresolved review, missing permissions, or any uncertain judgment.
- After every issue PR creation or merge, update the local ledger and runtime state before continuing.
- Before every issue PR or final PR, validate the exact delivery plan with `issue-implementation-loop/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json> --json`, then preserve/report the `ok: true` result before creating the PR.
- For final PR plans, `issue_scope` is the delivery candidate set; omit it only when the entire envelope work item set is in scope.
- After all issue PRs are merged and `epic_base.ref` reconciles as an existing branch, create the final PR from `epic_base.ref` to `main`.
- If a final PR plan uses an issue branch (`codex/<epic-id>/<local-id>-<slug>`) as the head, stop; do not reinterpret the last issue branch as the integration branch.
- Final PR merge is human-only.

Include:

- what changed
- spec/local issue/remote issue links
- blocker or stacked PR relationship
- verification results
- implementation review summary
- known risks

Use `Closes #<n>` only when merge should close the issue. Use `Refs #<n>` for partial, stacked, exploratory, or non-closing PRs.
