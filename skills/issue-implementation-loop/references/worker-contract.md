# Worker Contract

Build and validate bounded handoffs with:

- `assets/templates/worker-packet.json`
- `assets/schemas/worker-packet.schema.json`
- `scripts/build_worker_packet.py`
- `scripts/validate_worker_packet.py`

Worker Packet v3 is current-only. V1/V2 return `SCHEMA_UNSUPPORTED`. Executor and
reviewer packets share this schema; only `task_kind`, access policy, and write
scope differ.

## Packet Rules

- Require `source_revision.approved_spec_binding` plus envelope, runtime, and issue-source revisions.
- Revalidate packet/spec projection and gate ancestry in the assigned worktree before start.
- Use `task_kind=implement|fix` with `access_mode=read_write` and non-empty `write_scope`.
- Use `task_kind=review|inspect` with `access_mode=read_only` and `write_scope=[]`.
- `issue_title`、`task.summary`、`task.acceptance_criteria`、`task.stop_conditions` などの user-facing packet string は日本語をベースにする。keys、paths、commands、IDs、branches は維持する。
- Keep `context_policy` packet-local; never include `session_compaction` or session decision state.
- Default/hard packet budgets are 450/800 words; `read_paths` allows at most 8 entries and requires `purpose`.
- Inline excerpts allow 120 words per path and 300 total. Never paste full spec, ledger, ADR, glossary, or unrelated code.
- `PACKET_CONTEXT_BUDGET_EXCEEDED` fails without truncation.
- Reject path traversal and paths outside the assigned worktree. Stay inside write scope.
- Workers do not edit coordinator-owned envelope, runtime, events, or shared ledger unless assigned.
- Use `tdd` or an approved equivalent, run fresh verification, and commit locally before review or success.

## Worker Report v2

Require `schema_version: 2`, `approved_spec_binding`, `dispatch_id`, issue/Epic
identity, branch/worktree, changed files, verification, status, and residual
risks in the required `residual_risks` string list. Success also requires matching base/head SHA and approved implementation
review range.

Validate intake against both dispatch and active runtime:

```bash
python3 <skill-dir>/scripts/validate_worker_report.py <worker-report.json> \
  --dispatch-packet <worker-or-reviewer-packet.json> \
  --runtime-state <runtime-state.json>
```

Report, dispatch, and runtime bindings plus dispatch identity must match;
otherwise return `BINDING_MISMATCH`. Old reports return `SCHEMA_UNSUPPORTED`.
