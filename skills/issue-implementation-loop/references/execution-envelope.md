# Execution Envelope

The Execution Envelope is the approved execution contract. It is more specific than the input packet and includes reservations, policies, retry budgets, and remote-write boundaries.

## Required Sections

- `schema_version`: `2` for new envelopes. Legacy `1` envelopes remain valid when they predate the session-compaction policy.
- `epic_id`: lower-kebab-case ASCII
- `revision`: positive integer
- `epic_base`: per-epic base branch ref, immutable initial full 40- or 64-character hex SHA, and `branch_state` for `batch_issue_prs`
- `execution_policy`: parallel preference, serial fallback, slots, `wave_is_barrier`, and worker-context boundary
- `review_policy`: primary reviewer, fallbacks, manual fallback, `max_review_cycles: 2`, and fix-cycle limits
- `human_policy`: default scope and epic-scope reason requirement
- `context_policy`: paths-first worker packet and report budgets
- `remote_write_policy`: `local_only`, `per_action`, `batch_draft_prs`, or `batch_issue_prs`
- `work_items`: one entry per approved issue

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

## Reservation Rules

- Reserve branch and worktree path for every approved issue before execution.
- For `batch_issue_prs`, record `epic_base.branch_state` and reconcile the epic base branch before delivery.
- `epic_base.worktree_path` is optional; when present it must be an absolute path and is reconciled like a branch resource, not an issue work item.
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

Do not branch from multiple blocker or integration heads. Add an integration work item or integration branch when downstream code needs more than one prerequisite head.

## Remote Delivery Policy

Use `batch_issue_prs` when the approved delivery path is issue PRs into the epic base branch plus a final PR to `main`.

Required shape:

```json
{
  "mode": "batch_issue_prs",
  "approved_actions": [],
  "issue_prs": {
    "base": "epic_base.ref",
    "merge": "agent_default_with_human_escalation"
  },
  "final_pr": {
    "head": "epic_base.ref",
    "base": "main",
    "merge": "human_only"
  }
}
```

For this mode, `epic_base.ref` must be `codex/<epic-id>/epic-base`. Issue PR merges may be agent-run only while checks, review, permissions, and mergeability are unambiguous. Final PR merge is always human-only.

`epic_base.branch_state` must be one of `reserved`, `create_on_run`, `active`, or `missing`. Treat a missing `epic_base.ref` branch as a reconciliation failure before final PR delivery.

## Context Policy

The approved envelope must keep worker/reviewer handoffs bounded:

- `paths_first: true`: send durable paths and short summaries before file bodies.
- `max_worker_packet_words`: maximum words in the dispatch packet.
- `max_worker_report_words`: maximum words in normal worker reports.
- `include_full_spec_text: false` and `include_full_ledger_text: false`: workers re-read durable paths instead of receiving pasted source documents.
- `worker_packet_schema`, `worker_packet_template`, and `worker_packet_validator`: repo-root relative paths for the worker packet contract. Legacy envelopes may omit all three, but new envelopes should include all three.
- `session_compaction`: session-level execution compaction policy; required for schema version `2`, optional only for legacy schema version `1` envelopes. See `references/context-compaction.md`.

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
- human wait policy
- context policy

Routine state transitions within an approved envelope do not need another approval.
