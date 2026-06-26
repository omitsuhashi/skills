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

## Resume Brief Cache

Generate a short resume cache from a runtime root with:

```bash
python3 <skill-dir>/scripts/build_resume_brief.py <runtime-root>
```

The builder reads `runtime-state.json`, `events.jsonl`, optional `execution-envelope.json`, and latest files under `reports/` and `reviews/`. It writes `<runtime-root>/resume-brief.md` and enforces a 600 word limit. The brief must include Epic ID, overall status, runnable, active, reviewable, fixable, waiting human, pending remote action, verified commit ranges, latest report paths, and the recommended next operation.

The builder also writes `<runtime-root>/resume-brief.meta.json` with source
digests and revisions for the execution envelope, runtime state, and event log.
Validate the cache before trusting it with:

```bash
python3 <skill-dir>/scripts/validate_resume_brief.py <runtime-root>
```

Treat `resume-brief.md` as a regenerable cache only. It is not canonical state and must not be edited to fix scheduler/runtime data. If it disagrees with runtime or events, investigate the canonical sources and rebuild the brief.
