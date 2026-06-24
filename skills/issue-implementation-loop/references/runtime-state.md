# Runtime State

Keep mutable state outside tracked issue branches.

Default root:

```text
$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/
├── runtime-state.json
├── events.jsonl
├── reports/
├── reviews/
├── decisions/
├── locks/
└── recovery/
```

## Update Rule

Only the coordinator writes central state:

```text
worker/reviewer report
  -> coordinator validates attempt/report ID
  -> append event
  -> atomic snapshot update
  -> render human summary when needed
```

Worker branches must not include `runtime-state.json` or `events.jsonl` unless the approved issue explicitly owns coordinator-state tooling.

`pr_created` events set `pr` and `pr_opened` on the issue record. `pr_merged` events set `pr`, `pr_opened`, `pr_merged`, and `merge_commit` when provided. Delivery decisions must read this state rather than inferring epic-base integration from local `PR_READY`.

Validate snapshots with:

```bash
python3 <skill-dir>/scripts/validate_runtime_state.py <runtime-state.json>
```

For `PR_READY`, `COMPLETE`, or `DONE` issues, record matching `base_sha`, `head_sha`, and committed `BASE_SHA..HEAD_SHA` review range. Do not omit them or record `working-tree` as the review head for new success states.
