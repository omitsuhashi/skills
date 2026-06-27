# Governance

## Draft First

Default task creation is draft-first:

1. Normalize source text into `TaskDraft`.
2. Show the draft and rationale for human review.
3. Create, update, or comment in the backend only after approval.
4. Return `TaskRef` and write only source trail or decision logs to local systems.

## Approval Required

Require human approval for external writes, customer contact, permission changes, secrets, paid actions, irreversible actions, production actions, publication, and task backend schema changes.

## Automation Phases

- `recommend`: Suggest what should happen.
- `draft`: Prepare a draft artifact or response.
- `execute_with_approval`: Execute only after explicit approval.
- `trusted_automation`: Execute only for low-risk, reversible, pre-approved rules.

The helper default is `draft_only` because it is safe for review-first workflows.
