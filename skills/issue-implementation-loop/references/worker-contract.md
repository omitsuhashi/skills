# Worker Contract

Give each worker a normalized dispatch packet built from:

- `assets/templates/worker-packet.json`
- `assets/schemas/worker-packet.schema.json`
- `scripts/build_worker_packet.py`
- `scripts/validate_worker_packet.py`

The packet contains issue ID/title, Epic ID, dispatch ID, branch, worktree path,
exclusive write scope, durable read paths, short task summary, acceptance
criteria, verification commands, stop conditions, and report contract.

## Rules

- Re-read assigned issue and spec from durable paths.
- Keep the packet paths-first and validate it before dispatch.
- Enforce default packet budget 450 words and hard budget 800 words.
- Keep `read_paths` to 8 entries or fewer.
- Keep each inline excerpt to 120 words or fewer and all inline excerpts to 300 words or fewer.
- Do not paste full spec, ledger, ADR, glossary, or unrelated code into the worker packet.
- Treat `PACKET_CONTEXT_BUDGET_EXCEEDED` as fail-fast; do not auto-truncate packet text.
- Stay inside write scope.
- Do not edit coordinator-owned envelope, runtime snapshot, event log, or shared ledger unless explicitly assigned.
- Use `tdd` or an approved equivalent for behavior changes.
- Run targeted verification, update issue-owned docs/progress, then run fresh final verification.
- Produce a local scoped commit before issue review, blocker release, completion, or PR readiness. Review ranges use committed `BASE_SHA..HEAD_SHA`, not `working-tree`.
- For `PR_READY`, `COMPLETE`, or `DONE`, report matching `base_sha`, `head_sha`, and implementation review range.

## Worker Report

Report:

- issue ID/title and Epic ID
- branch and worktree path
- changed files
- verification commands and results
- base/head SHA for success statuses
- implementation review state and range
- fixed findings and accepted residual risks
- PR readiness
- new blockers or released blockers

Keep normal reports within `context_policy.max_worker_report_words`; write bulky evidence to report files and cite paths.

Validate before coordinator intake:

```bash
python3 <skill-dir>/scripts/validate_worker_report.py <worker-report.json>
```
