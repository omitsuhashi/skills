# Remote Delivery

Use this reference for GitHub issue mirroring, issue PR delivery, final PR creation, and remote-write approval policy.

Remote writes are optional. Push, GitHub issue creation, PR creation, ready-for-review, issue PR merge, force push, deploy, credential, permission, billing, production, and destructive actions require approved remote policy. Final PR merge always requires current human action.

## GitHub Mirror Gate

Optional. Before creating GitHub issues:

1. Confirm the remote points to GitHub.
2. Confirm GitHub tool/CLI auth.
3. Present exact local issues to publish.
4. Ask for explicit approval.
5. Create one issue per approved local issue.
6. Update the local ledger before continuing.

If publication fails, keep the local ledger intact and ask whether to continue local-only.

## PR Delivery

Create issue PRs only after `issue-implementation-loop` returns `PR_READY` for every issue in the PR scope and after explicit remote-write approval.

For `batch_issue_prs`:

- `epic_base.ref` must be `codex/<epic-id>/epic-base`.
- Issue PRs use head `codex/<epic-id>/<local-id>-<slug>` and base `epic_base.ref`.
- The agent may merge issue PRs when checks/review/mergeability pass and the approved policy says `agent_default_with_human_escalation`.
- Escalate to the human for scope drift, spec ambiguity, failed checks, conflicts, unresolved review, missing permissions, or any uncertain judgment.
- After every issue PR creation or merge, update the local ledger and runtime state before continuing.
- Before every issue PR or final PR, validate the exact delivery plan with `issue-implementation-loop/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <execution-result.json> <delivery-plan.json> --repo-root <trusted-worktree-root> --json`, then preserve/report the `ok: true` result before creating the PR.
- For final PR plans, `issue_scope` is the delivery candidate set; omit it only when the entire envelope work item set is in scope.
- After all issue PRs are merged and before creating the final PR, route to the `final-review` operation and use `superpowers:requesting-code-review` for a final spec alignment review. Ask for requirements fit without omission or excess, material simplicity, and material risk, in that order.
- Report only `Critical` / `Important` findings. A material simplicity finding must include evidence, material impact, required fix, and a concrete simpler alternative that meets the same requirements and risk boundary; classify it as `intent_gap` / `Important`. Do not report `Minor`, nit, preference, or optional improvement, and do not invent a finding when none is material.
- Treat final PR creation and final PR ready-for-review as blocked until Critical/Important spec alignment findings are fixed or explicitly accepted by the human.
- After all issue PRs are merged and `epic_base.ref` reconciles as an existing branch, create the final PR from `epic_base.ref` to `main`.
- If a final PR plan uses an issue branch (`codex/<epic-id>/<local-id>-<slug>`) as the head, stop; do not reinterpret the last issue branch as the integration branch.
- Final PR merge is human-only.

Include:

- what changed
- spec/local issue/remote issue links
- blocker or stacked PR relationship
- verification results
- implementation review summary
- spec alignment review summary
- known risks

Use `Closes #<n>` only when merge should close the issue. Use `Refs #<n>` for partial, stacked, exploratory, or non-closing PRs.
