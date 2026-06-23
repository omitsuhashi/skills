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

Validate snapshots with:

```bash
python3 <skill-dir>/scripts/validate_runtime_state.py <runtime-state.json>
```
