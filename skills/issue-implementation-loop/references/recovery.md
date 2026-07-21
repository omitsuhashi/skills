# Resume And Recovery

On resume, compare:

- active `approved_spec_binding` and current sealed packet/spec bytes
- approved envelope revision/hash
- runtime snapshot
- event log
- `git worktree list --porcelain`
- branch/head/base SHA
- dirty state
- worker/reviewer reports
- active leases
- remote state only when needed and approved

## Rules

- Rebuild snapshot from event log if snapshot is missing or corrupt.
- Ignore duplicate event IDs.
- Ignore stale attempt reports.
- Inspect dirty worktrees; do not reset or clean them.
- If a valid commit/report exists, advance to the next safe state.
- If incomplete, redispatch the same attempt or start a new attempt within retry policy.
- Escalate only the affected issue unless state corruption affects the whole epic.

Use:

```bash
python3 <skill-dir>/scripts/rebuild_runtime_state.py <events.jsonl>
python3 <skill-dir>/scripts/reconcile_git_state.py <execution-envelope.json> --json
```

## Resume Brief Investigation

On resume, read `<runtime-root>/resume-brief.md` first when present. It is a bounded cache for orientation only: use it to find active work, reviewable/fixable issues, waiting human requests, pending remote actions, verified commit ranges, latest report paths, and the recommended next operation.

`<runtime-root>/resume-brief.meta.json` v3 is required. Validate it before using
the brief:

```bash
python3 <skill-dir>/scripts/validate_resume_brief.py <runtime-root>
```

Meta-less and v2 caches return `SCHEMA_UNSUPPORTED`; do not use them for
orientation or resume. A stale approved packet/spec binding blocks cache use
independently of otherwise fresh runtime, envelope, and event source hashes. If
the brief lists inconsistencies or validation reports stale runtime, envelope,
or event sources, do not continue from the brief alone. Compare the execution envelope, `runtime-state.json`,
`events.jsonl`, worker/reviewer reports, and git state. Rebuild the snapshot
from `events.jsonl` when the snapshot is corrupt or stale, then regenerate the
brief. If the brief is missing, stale, over budget, or contradicts canonical
state, discard and regenerate it rather than editing it by hand.
