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
- issue PR base: `epic_base.ref`
- issue PR merge: `agent_default_with_human_escalation`
- final PR head: `epic_base.ref`
- final PR base: `main`
- final PR merge: `human_only`

Agent issue PR merge is allowed only when the PR is mergeable, required checks pass, issue implementation review is approved, scope is unchanged, and no unresolved review or permission ambiguity remains. Escalate to the human when judgment is needed.

Before final PR creation, reconcile `epic_base.ref` and confirm every issue in the delivery candidate set has `pr_merged: true` in runtime state or an equivalent approved ledger record. Do not treat local `PR_READY` alone as proof that `epic_base.ref` contains the issue head.

## Always Separate Approval

- final PR merge
- force push
- ready-for-review change
- deploy
- billing, credential, permission, or production action
- destructive remote action

Remote failure should not stop local implementation/review lanes unless the envelope explicitly makes that remote state a dependency.
