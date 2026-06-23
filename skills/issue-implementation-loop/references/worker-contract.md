# Worker Contract

Give each worker a short packet:

- local issue ID/title and Epic ID
- wave or dispatch ID
- branch and worktree path
- exclusive write scope
- spec, issue ledger, ADR/glossary paths
- required behavior and acceptance criteria
- verification commands
- stop conditions
- report format

## Rules

- Re-read assigned issue and spec from durable paths.
- Stay inside write scope.
- Do not edit coordinator-owned envelope, runtime snapshot, event log, or shared ledger unless explicitly assigned.
- Use `tdd` or an approved equivalent for behavior changes.
- Run targeted verification, update issue-owned docs/progress, then run fresh final verification.
- Produce a local scoped commit when review needs a base/head range.

## Worker Report

Report:

- issue ID/title and Epic ID
- branch and worktree path
- changed files
- verification commands and results
- base/head SHA when committed
- implementation review state and range
- fixed findings and accepted residual risks
- PR readiness
- new blockers or released blockers
