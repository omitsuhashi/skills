# Runtime State

Keep mutable execution state outside tracked issue branches:

```text
$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/
```

Runtime root contents: `runtime-state.json`, `events.jsonl`, `reports/`,
`reviews/`, `decisions/`, `locks/`, `recovery/`.

Only the coordinator writes central state: validate report, append event, update
snapshot. Worker branches must not include `runtime-state.json`,
`events.jsonl`, or live decision artifacts unless approved scope owns
coordinator-state tooling.

`pr_created` sets `pr`/`pr_opened`; `pr_merged` also sets `pr_merged` and
`merge_commit`. Delivery reads runtime state, not local `PR_READY` inference.

## Hardening Candidate Registry

Path: `<runtime-root>/decisions/hardening-candidates.json`.

This coordinator-owned runtime artifact is not a worker branch artifact or
ledger replacement. Track only the schema/template in `assets/`; do not commit
the live registry in a worker branch.

Candidate fields: `candidate_id`, `source_issue`, `classification`, `summary`,
`risk`, `estimated_scope`, `decision`, `implementation_issue`.

`classification`: `hardening_candidate`, `safety_escalation`,
`classification_needed`. `decision`: `pending_decision`,
`approved_for_current_pr`, `deferred_follow_up`, `declined`, `risk_accepted`,
`implemented`.

Defaults: each `hardening_candidate.summary` is 80 words or fewer; each source
issue records 5 件 or fewer.

`hardening_candidate` does not block completion, blocker release, or local
`PR_READY`. `safety_escalation` and `classification_needed` require scoped
`human_request_opened`.

## Validation

Validate snapshots with `python3 <skill-dir>/scripts/validate_runtime_state.py <runtime-state.json>`.

For `PR_READY`, `COMPLETE`, or `DONE`, record matching `base_sha`, `head_sha`,
and committed `BASE_SHA..HEAD_SHA` review range; never use `working-tree`.

## Resume Brief Cache

Build a regenerable cache:

```bash
python3 <skill-dir>/scripts/build_resume_brief.py <runtime-root>
```

The brief reads runtime/events plus optional envelope and report/review paths,
enforces 600 words, and writes `<runtime-root>/resume-brief.md` plus meta. Add
`Pending hardening decisions: N` and the candidate registry path when needed; do
not copy candidate full text. If stale, fix runtime/events and rebuild.
