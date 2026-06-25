# Event-Driven Scheduler

Waves are launch cohorts, not completion barriers. Recompute runnable work after every event.

## Parent Loop

1. Reconcile runtime snapshot, event log, worker reports, review reports, and git state.
2. Apply human decisions.
3. Expire or recover stale leases.
4. Evaluate dependency release conditions.
5. Compute runnable, reviewable, fixable, waiting, and blocked sets.
6. Dispatch work up to approved slot limits.
7. Append event and atomically update snapshot.

Use:

```bash
python3 <skill-dir>/scripts/compute_next_actions.py <execution-envelope.json> <runtime-state.json>
```

For mode routing, use `scripts/select_operation.py` before loading operation-specific
references. It is read-only and selects in this order: explicit `deliver`/`status`,
missing envelope, missing reservation, state mismatch, reviewable, fixable, human wait,
runnable, terminal, then reconcile. The result includes the context-contract read set
and word budget check for the selected operation.

## Dispatch Rules

- Dispatch only issues whose dependencies are released and whose write scope does not conflict with active implementation/fix work.
- Keep review lane separate from implementation lane.
- Do not let issue-scoped human wait block unrelated runnable issues.
- If parallel workers are unavailable and `serial_fallback_preapproved=true`, continue serially only through worker contexts.
- If worker contexts are unavailable, stop before implementation.
- If parallel execution is mandatory, stop before execution during capability preflight.
