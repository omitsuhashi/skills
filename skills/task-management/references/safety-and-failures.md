# Safety And Failures

## Approval policy

- High-confidence safe single-item writes run automatically.
- Uncertain target or content requires confirmation.
- Destructive or bulk mutation requires confirmation.
- An explicit user instruction is the approval for that exact operation. Do not ask twice.

Safe automatic operations include reads, searches, capability checks, a high-confidence single Issue create/edit/comment, adding that Issue to the resolved Project, non-terminal field updates, and repair of Project Status after an already closed Issue with a reliable reason.

Confirmation is required for ambiguous Project or repository selection, unclear outcome or acceptance criteria, inferred close/transfer/delete, Project item removal/archive, destructive body replacement, Project schema or visibility change, private-content exposure, and multi-Issue mutation. If an explicit instruction reveals a different target, unexpected permission identity, or unexpectedly large item count, stop and reconfirm.

## Fail closed

- Missing MCP: name GitHub MCP as unavailable.
- Missing capability: list the absent Issue or Projects operation.
- Authentication or permission failure: name the target and rejected operation without requesting or storing a credential.
- Schema mismatch: list missing fields or options and route to separate setup.
- Ambiguous result: show candidates without writing.
- Pagination, result-limit, deferred-page, provider hard-limit, or page-retrieval stop: preserve fetched results and return `partial`, the precise stop reason, truncation state, provider continuation when available, and whether resumption is possible.
- Schema ambiguity during Status normalization: stop the operation and return `partial`; do not select an option by similarity.

Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Partial success

Do not delete the created Issue if Issue creation succeeds but Project add or field update fails. Return its URL, successful steps, unfinished steps, and the safe resume action. On retry, continue only the unfinished steps. Do not reset completed or current fields. Do not create a duplicate Issue.

For a terminal or reopen operation, exact-read the Issue state, close reason when
applicable, and Project Status before writing. Attempt only sides that differ
from the target. If the sides diverge, do not roll back the successful side.
Return `partial`, the completed sides, `first_remaining_sides`, and exact
readback. A two-side partial success is never `complete`.

On retry, exact-read both sides again, put the remaining side only in
`retry_attempted_sides`, and write only that side. Continue only the unfinished steps.
Do not retry a side already confirmed successful. Preserve the successful side
even when the remaining side keeps failing.

For duplicate discovery or another completeness-required query, only confirmed
raw source exhaustion may produce `complete`. A 50-item display/return limit is
not an investigation limit: continue across opaque provider continuations while
keeping the returned buffer at 50. If discovery is `partial` or `truncated`, or
its exhausted outcome is `ambiguous_or_multiple`, do not claim no duplicate and
do not continue to create.
