# Safety And Failures

## Approval policy

- High-confidence safe single-item writes run automatically.
- Uncertain target or content requires confirmation.
- Destructive or bulk mutation requires confirmation.
- An explicit user instruction is the approval for that exact operation. Do not ask twice.

Safe automatic operations include reads, searches, capability checks, an explicit single Issue create/edit/comment, adding that Issue to the resolved Project, non-terminal field updates, and repair of Project Status after an already closed Issue with a reliable reason.

An inferred create is automatic only when the target, Outcome, observable acceptance criteria, single-item scope for one task, non-destructive scope, duplicate result, and idempotency key are all exact. Otherwise return `confirmation-needed` without creating a draft item.

Confirmation is required for ambiguous Project or repository selection, unclear outcome or acceptance criteria, inferred close/transfer/delete, Project item removal/archive, destructive body replacement, Project schema or visibility change, private-content exposure, and multi-Issue mutation. If an explicit instruction reveals a different target, unexpected permission identity, or unexpectedly large item count, stop and reconfirm.

## Fail closed

- Missing MCP: name GitHub MCP as unavailable.
- Missing capability: list the absent Issue or Projects operation.
- Authentication or permission failure: name the target and rejected operation without requesting or storing a credential.
- Schema mismatch: list missing fields or options and route to separate setup.
- Ambiguous result: show candidates without writing.

Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Partial success

Do not delete the created Issue if Issue creation succeeds but Project add or field update fails. Return its URL, successful steps, unfinished steps, and the safe resume action. On retry, continue only the unfinished steps. Do not reset completed or current fields. Do not create a duplicate Issue.

If Issue close and terminal Project Status diverge, do not roll back the successful side automatically. Report the mismatch and complete only the missing side after the applicable confirmation rule.
