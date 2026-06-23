# Worker Contract

Give each worker a short packet:

- local issue ID/title and Epic ID
- wave or dispatch ID
- branch and worktree path
- exclusive write scope
- spec, issue ledger, ADR/glossary paths
- short required behavior and acceptance criteria summary
- verification commands
- stop conditions
- report format

## Rules

- Re-read assigned issue and spec from durable paths.
- Keep the packet paths-first and within `context_policy.max_worker_packet_words`.
- Do not paste full spec, ledger, ADR, glossary, or unrelated code into the worker packet unless the approved context policy explicitly allows it.
- Stay inside write scope.
- Do not edit coordinator-owned envelope, runtime snapshot, event log, or shared ledger unless explicitly assigned.
- Use `tdd` or an approved equivalent for behavior changes.
- Run targeted verification, update issue-owned docs/progress, then run fresh final verification.
- Produce a local scoped commit before issue review, blocker release, completion, or PR readiness. Review ranges use committed `BASE_SHA..HEAD_SHA`, not `working-tree`.

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

Keep normal reports within `context_policy.max_worker_report_words`; write bulky evidence to report files and cite paths.
