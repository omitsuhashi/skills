# Core Contract

Use this skill only after issues and acceptance criteria are approved. The execution coordinator owns:

- input packet and approved Execution Envelope
- append-only event log and mutable runtime snapshot
- blocker release and human request routing
- issue completion and PR-ready decisions
- final report and remote-write approval boundary

The original planning/grill session must not implement issue work. Workers own only their assigned issue worktree, branch, write scope, and verification evidence. Reviewers own only review findings for the issue packet they receive.

## Input Packet

Normalize local or remote issues before execution:

- `schema_version`, `repo_root`, `epic_id`, optional `artifact_root`
- `spec.path`, plus approved revision/hash when available
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`: use `batch_issue_prs` for issue PRs into `codex/<epic-id>/epic-base` and a final PR to `main`

Use `assets/templates/input-packet.json` for the concrete shape and `assets/schemas/input-packet.schema.json` for the field contract.

Validate with:

```bash
python3 <skill-dir>/scripts/validate_input_packet.py <packet.json>
```

## Output Contract

Return a local execution result:

- `schema_version`, `epic_id`, `status`, and `envelope_revision`
- epic base branch status when delivery mode uses `batch_issue_prs`
- per-issue status, branch, worktree, base/head SHA, verification, implementation review, and residual risks
- `pending_human_requests`, `delivery_candidates`, and `runtime_state_root`

Use `assets/templates/execution-result.json` for the concrete shape.

## Non-Goals

- Do not create or redesign issues.
- Do not let the coordinator become the implementation worker, even in serial fallback.
- Do not create a generic workflow framework.
- Do not route work through a separate LLM node scheduler.
- Do not perform remote writes unless the envelope and the human both approve the exact action.
