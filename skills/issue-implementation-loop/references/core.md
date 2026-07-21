# Core Contract

Use this skill only after issues and acceptance criteria are approved. The execution coordinator owns:

- input packet and approved Execution Envelope
- append-only event log and mutable runtime snapshot
- blocker release and human request routing
- issue completion and PR-ready decisions
- final report and remote-write approval boundary

The original planning/grill session must not implement issue work. Workers own only their assigned issue worktree, branch, write scope, and verification evidence. Reviewers own only review findings for the issue packet they receive.

## Input Packet

Input Packet v2 is the only executable packet contract:

- `schema_version: 2`, `epic_id`, and repo-relative `artifact_root`
- required `spec_binding` and complete `approval_evidence`
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`: use `batch_issue_prs` for issue PRs into `codex/<epic-id>/epic-base` and a final PR to `main`

Use `assets/templates/input-packet.json` for the concrete shape and `assets/schemas/input-packet.schema.json` for the field contract.

Run validate_input_packet.py. Seal only if check_capabilities.py --json reports approved_spec_seal supported; else PLATFORM_UNSUPPORTED.

## Output Contract

Return a local execution result:

- current-only `schema_version: 2`, active `approved_spec_binding`, `epic_id`,
  `status`, and `envelope_revision`
- epic base branch status when delivery mode uses `batch_issue_prs`
- per-issue status, branch, worktree, base/head SHA, verification, implementation review, and residual risks
- `pending_human_requests`, `delivery_candidates`, and `runtime_state_root`

Use `assets/templates/execution-result.json` for the concrete shape.
Validate it with `scripts/validate_execution_result.py` immediately before reporting
terminal completion. The validator fresh-checks the Envelope v4 packet/spec chain,
Runtime State v2 epoch, committed review ranges, result binding, and any present
hardening candidate registry. Execution Result v1 is unsupported.

Execution Envelope v4 is current-only. It pins the sealed Input Packet v2 through
`approved_spec_binding` and verifies the full gate commit, its ancestry, and its
packet/spec tree blobs before state-changing work.

## Non-Goals

- Do not create or redesign issues.
- Do not let the coordinator become the implementation worker, even in serial fallback.
- Do not create a generic workflow framework.
- Do not route work through a separate LLM node scheduler.
- Do not perform remote writes unless the envelope and the human both approve the exact action.
