# Runtime State

Keep all instantiated execution artifacts outside Git and tracked issue branches:

```text
$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/
├── execution-envelope.json
├── runtime-state.json
├── events.jsonl
├── reports/
├── reviews/
├── decisions/
├── locks/
├── recovery/
└── delivery/
```

Do not commit instantiated execution artifacts. Schemas, templates, and test fixtures remain tracked product assets.

Only the coordinator writes state. Worker branches exclude `runtime-state.json`,
`events.jsonl`, and live decisions unless scope owns coordinator tooling.

Event v2 and Runtime State v2 carry one top-level `approved_spec_binding`.
Validate before dedupe and after fold; reject mixed/unknown epochs. Reseal starts
empty state and never copies old events, reviews, requests, or decisions.

`pr_created` sets `pr`/`pr_opened`; `pr_merged` also sets `pr_merged` and
`merge_commit`. Delivery reads runtime state, not local `PR_READY` inference.

## Hardening Candidate Registry

Path: `<runtime-root>/decisions/hardening-candidates.json`.

Registry v2 carries runtime `approved_spec_binding`; missing means empty. Reject
v1 or another epoch before decision reads (`SCHEMA_UNSUPPORTED` /
`AUXILIARY_ARTIFACT_BINDING_MISMATCH`).

This coordinator-owned runtime artifact is not a worker branch artifact or
ledger replacement. Track only the schema/template in `assets/`; do not commit
the live registry in a worker branch.

Do not create registry entries for routine future-only hardening ideas or
classification-only passes. The registry is for human-requested hardening
review, current PR delivery-risk decisions, `safety_escalation`, and
`classification_needed` only when an encountered finding cannot be classified or
the human explicitly requested a classification pass.

Candidate fields: `candidate_id`, `source_issue`, `classification`, `summary`,
`risk`, `estimated_scope`, `decision`, `implementation_issue`.

`classification`: `hardening_candidate`, `safety_escalation`,
`classification_needed`. `decision`: `pending_decision`,
`approved_for_current_pr`, `deferred_follow_up`, `declined`, `risk_accepted`,
`implemented`.

Defaults: each `hardening_candidate.summary` is 80 words or fewer; each source
issue records 5 件 or fewer.

`hardening_candidate` does not block completion, blocker release, or local
`PR_READY`. Future-only suggestions are omitted rather than carried to the
registry. `safety_escalation` and encountered `classification_needed` findings
require scoped `human_request_opened`.

## Validation

Validate snapshots with `python3 <skill-dir>/scripts/validate_runtime_state.py <runtime-state.json>`.

Rebuild only through the binding-aware interface:

```bash
python3 <skill-dir>/scripts/rebuild_runtime_state.py <events.jsonl> \
  --repo-root <trusted-worktree-root> \
  --envelope <execution-envelope.json>
```

The rebuild verifies the closed Envelope and exact packet/spec projection before
and after event folding, then verifies the binding again before returning the
snapshot. The unbound one-argument rebuild form is unsupported.

For `PR_READY`, `COMPLETE`, or `DONE`, record matching `base_sha`, `head_sha`,
and committed `BASE_SHA..HEAD_SHA` review range; never use `working-tree`.

## Resume Brief Cache

Build a regenerable cache:

```bash
python3 <skill-dir>/scripts/build_resume_brief.py <runtime-root> \
  --repo-root <trusted-worktree-root> \
  --envelope <execution-envelope.json>
```

The brief requires the current envelope and reads runtime/events plus
report/review paths,
enforces 600 words, and writes markdown plus required v3 metadata containing
`sources.approved_spec_binding`. Verify current packet/spec before and after the
fold and again immediately before publishing either cache file. Add
`Pending hardening decisions: N` and the candidate registry path when needed; do
not copy candidate full text. Meta-less and v2 caches are unsupported. If stale,
fix runtime/events and rebuild.
