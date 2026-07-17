---
name: task-management
description: Use for backend-neutral task intake, normalized task reads, and task backend routing workflows, especially when converting capture/chat text into a reviewed task draft, querying current task snapshots, preparing human approval text, checking task backend boundaries, or preparing adapter dispatch previews without implementing GitHub clients, gh command planners, direct GraphQL clients, MCP servers, credentials, or external writes.
---

# Task Management

Use this skill to normalize task intent, prepare reviewable task drafts, and keep task backend routing separate from Portfolio OS state. Codex uses this workflow skill; Hermes additionally exposes the native read-only `task-management-read:task_query` runtime tool.

## References

- Read `references/task-draft-contract.md` before composing TaskDraft title, body, taxonomy, inbox fallback, source-boundary content, or create/update preview text.
- Read `references/task-contracts.md` when checking backend-neutral contract fields, normalized task refs, query/snapshot/write-result shapes, or raw provider ID/auth boundaries.
- Read `references/task-read-adapter.md` before using the read-only `task_query` tool, configuring its host adapter route, or interpreting `TaskSnapshotResult` errors.
- Read `references/routing-flow.md` when explaining the end-to-end actor sequence, backend switching, route ownership, or the boundary between read routing and approved state-changing dispatch.
- Read `references/backend-routing.md` before selecting a backend key, resolving route registry entries, or requiring caller/profile/host destination input.
- Read `references/adapter-dispatch.md` before preparing adapter operation envelopes or applying the Adapter Dispatch Review guard.
- Read `references/github-mcp-projects.md` before representing GitHub Projects MCP route availability, typed route blocks, or adapter result normalization.
- Read `references/hermes-mcp-governance.md` before giving setup guidance for MCP registration, credential/tool enablement boundaries, or Hermes delegation risk.

## Operating Boundaries

- Portfolio OS must not own task route, task data, task result, or task-specific evidence. It may keep only generic plugin selection, native install, manifest identity / required-export verification, and generic profile enablement evidence.
- Use only `task-management-read:task_query` for task reads. Its normal host-owned route selects `mcp__<server>__task_query` or `task_adapter__<provider>__task_query`, and it returns only normalized `TaskSnapshot` values. `local_json` is reserved for plugin-owned test and smoke fixtures and is not an operator-facing runtime backend.
- Do not implement or call direct GitHub clients, `gh` command planners, direct GraphQL clients, MCP servers, credential setup, MCP registration, remote writes, issue/PR creation, push, or merge.
- External read/write task state belongs to an MCP server or provider plugin. The task-management plugin owns no provider API client, CLI fallback, credential client, or local write surface.
- Stop before adapter dispatch unless the caller has provided a reviewable operation envelope and explicit approval path.
- Keep GitHub Projects details such as raw node IDs, field IDs, tokens, owner, project number, and repository out of reusable skill contracts unless an external adapter result has already returned an opaque reference.

## Default Flow

1. Read the caller's task source and identify the intended task outcome.
2. For current backend state, call `task_query` with a backend-neutral `TaskQuery` and opaque destination reference; stop on any typed read-adapter error.
3. Produce a backend-neutral task draft with title, body, task type, work unit fields when known, and review notes.
4. Resolve backend routing from an optional internal override and then host `default_backend`. Stop with a typed setup error when neither resolves; never fall back implicitly to GitHub.
5. Require a destination supplied by caller, profile, or host registration before any adapter-facing preview.
6. Present a human review summary before any state-changing adapter route is used.

## Required Review Surface

When preparing a task create/update/comment/report preview, include:

- backend key and connection reference
- destination reference and label
- operation type
- opaque task reference for update/comment/report operations
- task title, body, and fields
- `work_unit_id` and `work_unit_name` when known
- expected adapter side effects
- adapter tool name or route surface, if supplied by the host

If destination, capability, or tool availability is missing, stop with setup guidance instead of inventing a backend target.
