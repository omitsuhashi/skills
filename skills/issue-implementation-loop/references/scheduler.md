# Event-Driven Scheduler

Waves are launch cohorts, not completion barriers. Recompute runnable work after every event.

Before reading issue status, dependencies, human requests, or write scopes,
require Envelope v4 and Runtime State v2 to have the same
`approved_spec_binding`, Epic ID, and envelope revision. Runtime validation also
requires every Human Request v2 binding to match. Return `BINDING_MISMATCH` or
`AUXILIARY_ARTIFACT_BINDING_MISMATCH` instead of producing a runnable set from
mixed epochs.

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
references. It fresh-verifies the active binding before explicit `deliver`, `status`, or `resume` routing. An invalid binding returns a reapproval blocker for every
state-changing mode. `status` remains diagnostic and returns `binding_valid: false`
with `state_advance_blocked: true`. After that gate, selection considers explicit mode,
missing reservation, state mismatch, reviewable, fixable, human wait, runnable,
terminal, then reconcile. The result includes the context-contract read set and word
budget check for the selected operation.

## Dispatch Rules

- Dispatch only issues whose dependencies are released and whose write scope does not conflict with active implementation/fix work.
- Keep review lane separate from implementation lane.
- Do not let issue-scoped human wait block unrelated runnable issues.
- If parallel workers are unavailable and `serial_fallback_preapproved=true`, continue serially only through worker contexts.
- If worker contexts are unavailable, stop before implementation.
- If parallel execution is mandatory, stop before execution during capability preflight.
