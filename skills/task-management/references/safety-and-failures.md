# Safety And Failures

## Approval policy

- High-confidence safe single-item writes run automatically.
- Uncertain target or content requires confirmation.
- Destructive or bulk mutation requires confirmation.
- An explicit user instruction is the approval for that exact operation. Do not ask twice.

Every write route emits exactly one guard outcome. Only `eligible`, `explicit`, or
`inferred` is write-eligible. `blocked`, `ambiguous`, `duplicate`, `bulk`,
`destructive`, and `confirmation-needed` are declared zero-write outcomes. A
missing, empty, or unknown guard outcome fails closed as `blocked` with zero
writes; never treat a new string as allowed by default.

Safe automatic operations include reads, searches, capability checks, an explicit single Issue create/edit/comment, adding that Issue to the resolved Project, non-terminal field updates, and repair of Project Status after an already closed Issue with a reliable reason.

An inferred create returns `inferred` only when the target, Outcome, observable acceptance criteria, single-item scope for one task, non-destructive scope, duplicate result, and idempotency key are all exact. Otherwise return `confirmation-needed` without creating a draft item. An explicit bounded instruction returns `explicit`; a separately established safe authorization returns `eligible`.

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

When Issue creation returns an unknown result, search the exact idempotency marker
within the exact repository. One match may bind its positive Issue number or node
ID; then read that exact Issue and validate repository, marker, and identity before
success or continuation. The marker search is resolution, never final readback.
Zero or multiple matches fail closed without retrying Issue creation.

If Issue close and terminal Project Status diverge, do not roll back the successful side automatically. Report the mismatch and complete only the missing side after the applicable confirmation rule.
