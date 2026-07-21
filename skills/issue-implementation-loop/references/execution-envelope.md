# Execution Envelope

The Execution Envelope is the approved execution contract. It is more specific than the input packet and includes reservations, policies, retry budgets, and remote-write boundaries.

## Required Sections

- `schema_version`: `4`; versions 1 through 3 are `SCHEMA_UNSUPPORTED`
- `epic_id`: lower-kebab-case ASCII
- `revision`: positive integer
- `approved_spec_binding`: repo-relative sealed packet path, exact raw-byte SHA-256, and full `gate_commit`
- `epic_base`: per-epic base branch ref, immutable initial full 40- or 64-character hex SHA, and `branch_state` for `batch_issue_prs`
- `execution_policy`: parallel preference, serial fallback, slots, `wave_is_barrier`, and worker-context boundary
- `review_policy`: primary reviewer, fallbacks, manual fallback, `max_review_cycles: 2`, fix-cycle limits, and `hardening_candidates` policy
- `human_policy`: default scope and epic-scope reason requirement
- `context_policy`: paths-first worker packet and report budgets
- `phase_branch_policy`: Codex phase branch ownership and context handoff policy
- `remote_write_policy`: `local_only`, `per_action`, `batch_draft_prs`, or `batch_issue_prs`
- `work_items`: exactly one entry per sealed Input Packet work item, with the same ID, title, source, acceptance criteria, non-goals, verification commands, write scope, and ordered dependency IDs

Envelope v4 is closed at every object level: missing required fields, unknown
fields, and booleans substituted for integer fields are invalid. Its
`epic_id`, complete work-item set, and remote mode must exactly project the
verified Input Packet; a valid packet digest never authorizes caller-supplied
execution intent.

## Execution Context Boundary

Use this required shape:

```json
{
  "worker_context_required": true,
  "coordinator_may_implement": false,
  "serial_fallback_mode": "worker_context_only"
}
```

Serial fallback means worker jobs run one at a time. It does not authorize coordinator-direct implementation. If worker contexts are unavailable, stop before implementation.

## Codex Phase Branch Policy

Envelope v4 always requires `phase_branch_policy`. The fixed policy says: planning artifacts stay on the current planning branch through gate commits; phase transition requires a clean overlapping write scope; execution starts in a fresh or compacted coordinator context; `main_planning_session_may_implement=false`; `branch_prefix=codex`; `epic_base_owner=execution_coordinator`; `issue_branch_owner=worker`; integration branches require an approved integration work item.

Before prepare, verify the current packet/spec projection, require `gate_commit`
to be an ancestor of `epic_base.sha`, and compare the exact packet and referenced
spec blobs both in the gate tree and at the exact `epic_base.sha`. Fail with the
stable binding code; do not convert these failures into general Git
reconciliation advice.

## Review Governance Policy

New envelopes include `review_policy.hardening_candidates` as policy only. Store candidate records and human decision state under runtime `decisions/hardening-candidates.json`, not in the envelope or worker packet. Routine review packets check issue intent, regression, and current PR delivery risk; do not solicit future-only hardening or classification-only passes.

`hardening_candidate` findings do not block issue completion, blocker release, local `PR_READY`, or draft final PR creation by themselves. Existing candidates remain pending for ready-for-review / merge lanes; worker packets may cite the policy path but must not include session-level decision state.

## Reservation Rules

- Reserve branch and worktree path for every approved issue before execution.
- For `batch_issue_prs`, record `epic_base.branch_state` and reconcile the epic base branch before delivery.
- `epic_base.worktree_path` is optional; when present it must be an absolute path and is reconciled like a branch resource, not an issue work item.
- Keep planning artifacts off issue branches; issue branches start only from their declared `base_policy`.
- Do not silently add suffixes to avoid collisions.
- A blocked issue may have a reserved branch/path, but its physical worktree stays absent until release.
- Dependent worktree state should normally be `reserved`.
- Use `scripts/validate_execution_envelope.py` before asking for approval.
- Use `scripts/reconcile_git_state.py` before creating or activating worktrees.

## Base Policy

Every work item declares how its branch is created:

- `{"type": "epic_base"}`: branch from `epic_base.ref` at the recorded base head.
- `{"type": "blocker_head", "issue": "G2PR-001"}`: branch from exactly one prerequisite issue head whose dependency edge uses `base_effect: "branch_from_blocker_head"`.
- `{"type": "integration_head", "integration_issue": "G2PR-010"}`: branch from exactly one approved integration work item whose dependency edge uses `base_effect: "branch_from_integration_head"`.

Dependency objects are not caller-selected expansions of the sealed dependency IDs.
They must equal the canonical typed-edge projection in `dependency-contract.md`.

Do not branch from multiple blocker or integration heads. Add an integration work item or integration branch when downstream code needs more than one prerequisite head.

## Remote Delivery Policy

Use `batch_issue_prs` when the approved delivery path is issue PRs into the epic base branch plus a final PR to `main`.

Required shape: `mode=batch_issue_prs`, `issue_prs.base=epic_base.ref`, issue PR merge `agent_default_with_human_escalation`, `final_pr.head=epic_base.ref`, `final_pr.base=main`, `final_pr.merge=human_only`, and `draft_default=true`. Final PR auto-creation also requires `final_pr_push_head` and `final_pr_create_draft` in `approved_actions`.

`epic_base.branch_state` must be one of `reserved`, `create_on_run`, `active`, or `missing`. Treat a missing `epic_base.ref` branch as a reconciliation failure before final PR delivery.

## Context Policy

The approved envelope must keep worker/reviewer handoffs bounded:

- `paths_first: true`: send durable paths and short summaries before file bodies.
- `max_worker_packet_words`: maximum words in the dispatch packet.
- `max_worker_report_words`: maximum words in normal worker reports.
- `include_full_spec_text: false` and `include_full_ledger_text: false`: workers re-read durable paths instead of receiving pasted source documents.
- `worker_packet_schema`, `worker_packet_template`, and `worker_packet_validator`: repo-root relative paths for the Worker Packet v3 contract.
- `session_compaction`: required. See `references/context-compaction.md`.

Create a new envelope revision before increasing budgets or allowing pasted full source text.

## Revision Required

Create a new envelope revision before changing:

- branch or worktree reservation
- acceptance criteria
- dependency edge
- write scope
- base strategy
- remote action policy
- issue PR merge policy or final PR policy
- retry or review fallback policy
- review governance policy, including `review_policy.hardening_candidates`
- human wait policy
- context policy

Routine state transitions within an approved envelope do not need another approval.
Any change to packet-owned intent first requires the applicable Execution Plan
or Spec Gate and a new sealed packet; the new Envelope revision must then be
projected from that packet rather than independently editing those fields.
