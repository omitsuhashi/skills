# Remote Delivery

Default terminal state is local `PR_READY`. Remote writes are optional and require explicit current approval.

## Modes

- `local_only`: no remote writes.
- `per_action`: approve each push/PR/link action separately.
- `batch_draft_prs`: approve exact branches, target, draft PR creation, and issue linkage as a batch.
- `batch_issue_prs`: approve issue PR creation/guarded issue PR merge into `codex/<epic-id>/epic-base`, plus final PR creation to `main`.

## Batch Issue PRs

Required policy:

- `epic_base.ref`: `codex/<epic-id>/epic-base`
- `remote_write_policy.approved_actions`: include `final_pr_push_head` and `final_pr_create_draft` before final PR delivery
- issue PR base: `epic_base.ref`
- issue PR merge: `agent_default_with_human_escalation`
- final PR head: `epic_base.ref`
- final PR base: `main`
- final PR merge: `human_only`
- final PR creation default: draft

Before creating any issue PR or draft final PR, write the exact action to a delivery plan file, validate it with `--json`, and record/report the `ok: true` output before creating the PR. Draft final PR auto-creation is allowed when delivery plan validation returns `ok: true`, `epic_base.ref` is active, every issue in the delivery candidate set is integrated, and the approved remote policy includes both `final_pr_push_head` and `final_pr_create_draft`. Use `assets/templates/delivery-plan.json` as the starting point for final PRs:

```bash
python3 <skill-dir>/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json>
python3 <skill-dir>/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json> --json
```

Delivery plan shape:

```json
{
  "action": "final_pr",
  "head": "codex/<epic-id>/epic-base",
  "base": "main",
  "draft": true,
  "issue_scope": ["G2PR-001"]
}
```

For issue PRs, use `"action": "issue_pr"` plus `"issue": "<local-id>"`; the head must be that issue's reserved branch and the base must be `epic_base.ref`. For final PRs, `issue_scope` is the delivery candidate set; omit it only when the entire envelope work item set is in scope.

Agent issue PR merge is allowed only when the PR is mergeable, required checks pass, issue implementation review is approved, scope is unchanged, and no unresolved review or permission ambiguity remains. Escalate to the human when judgment is needed.

Before final PR creation, reconcile `epic_base.ref`, set `epic_base.branch_state: active`, and confirm every issue in the delivery candidate set has `pr_merged: true` in runtime state or an equivalent approved ledger record. When using `validate_delivery_plan.py`, first reflect any approved ledger-equivalent merge record into runtime state; the validator does not infer final integration from local `PR_READY`. Do not treat local `PR_READY` alone as proof that `epic_base.ref` contains the issue head.

Draft final PR preflight also reads `<runtime-root>/decisions/hardening-candidates.json` when present. `pending_decision` or unresolved `safety_escalation` does not block draft PR creation; it must appear in `pending_hardening_candidates` and `decision_gate_blockers` so the human can judge the integrated PR diff. `approved_for_current_pr` is unresolved until its `implementation_issue` is `PR_READY`, integrated, or review approved. For `hardening_candidate`, `deferred_follow_up`, `declined`, and `risk_accepted` do not block draft PR creation, but must be copied into the completion report residual risk summary. For `safety_escalation`, only `risk_accepted`, `implemented`, or `approved_for_current_pr` with ready implementation clears the ready-for-review / merge blocker.

After creating a draft final PR, synchronize the PR URL, draft state, delivery plan validation evidence, pending hardening candidate summary, decision gate blockers, and residual risk summary into the local ledger, runtime state, and completion report before reporting delivery complete. Do not mark the final PR ready for review in this step.

For `local_only` completion, no remote delivery plan is required, but the completion report still must include `pending_hardening_candidates` when unresolved candidates remain and residual risks for `deferred_follow_up`, `declined`, or `risk_accepted` candidates.

## Always Separate Approval

- final PR merge: human action
- force push: human action
- ready-for-review change: human action
- deploy
- billing, credential, permission, or production action
- destructive remote action

Remote failure should not stop local implementation/review lanes unless the envelope explicitly makes that remote state a dependency.
