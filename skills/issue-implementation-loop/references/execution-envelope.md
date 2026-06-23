# Execution Envelope

The Execution Envelope is the approved execution contract. It is more specific than the input packet and includes reservations, policies, retry budgets, and remote-write boundaries.

## Required Sections

- `schema_version`: `1`
- `epic_id`: lower-kebab-case ASCII
- `revision`: positive integer
- `epic_base`: immutable base ref and full 40- or 64-character hex SHA
- `execution_policy`: parallel preference, serial fallback, slots, and `wave_is_barrier`
- `review_policy`: primary reviewer, fallbacks, manual fallback, and fix-cycle limits
- `human_policy`: default scope and epic-scope reason requirement
- `context_policy`: paths-first worker packet and report budgets
- `remote_write_policy`: `local_only`, `per_action`, or `batch_draft_prs`
- `work_items`: one entry per approved issue

## Reservation Rules

- Reserve branch and worktree path for every approved issue before execution.
- Do not silently add suffixes to avoid collisions.
- A blocked issue may have a reserved branch/path, but its physical worktree stays absent until release.
- Dependent worktree state should normally be `reserved`.
- Use `scripts/validate_execution_envelope.py` before asking for approval.
- Use `scripts/reconcile_git_state.py` before creating or activating worktrees.

## Base Policy

Every work item declares how its branch is created:

- `{"type": "epic_base"}`: branch from immutable `epic_base.ref` / `epic_base.sha`.
- `{"type": "blocker_head", "issue": "G2PR-001"}`: branch from exactly one prerequisite issue head whose dependency edge uses `base_effect: "branch_from_blocker_head"`.
- `{"type": "integration_head", "integration_issue": "G2PR-010"}`: branch from exactly one approved integration work item whose dependency edge uses `base_effect: "branch_from_integration_head"`.

Do not branch from multiple blocker or integration heads. Add an integration work item or integration branch when downstream code needs more than one prerequisite head.

## Context Policy

The approved envelope must keep worker/reviewer handoffs bounded:

- `paths_first: true`: send durable paths and short summaries before file bodies.
- `max_worker_packet_words`: maximum words in the dispatch packet.
- `max_worker_report_words`: maximum words in normal worker reports.
- `include_full_spec_text: false` and `include_full_ledger_text: false`: workers re-read durable paths instead of receiving pasted source documents.

Create a new envelope revision before increasing budgets or allowing pasted full source text.

## Revision Required

Create a new envelope revision before changing:

- branch or worktree reservation
- acceptance criteria
- dependency edge
- write scope
- base strategy
- remote action policy
- retry or review fallback policy
- human wait policy
- context policy

Routine state transitions within an approved envelope do not need another approval.
