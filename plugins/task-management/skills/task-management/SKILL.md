---
name: task-management
description: Use for backend-neutral task intake and task backend routing workflows, especially when converting capture/chat text into a reviewed task draft, preparing human approval text, checking task backend boundaries, or preparing adapter dispatch previews without implementing GitHub adapters, gh command planners, direct GraphQL clients, MCP servers, credentials, or external writes.
---

# Task Management

Use this skill to normalize task intent, prepare reviewable task drafts, and keep task backend routing separate from Portfolio OS state. Treat the selected backend as the source of truth for task state.

## References

- Read `references/task-draft-contract.md` before composing TaskDraft title, body, taxonomy, inbox fallback, source-boundary content, or create/update preview text.
- Read `references/task-contracts.md` when checking backend-neutral contract fields, normalized task refs, query/snapshot/write-result shapes, or raw provider ID/auth boundaries.
- Read `references/backend-routing.md` before selecting a backend key, resolving route registry entries, or requiring caller/profile/host destination input.
- Read `references/adapter-dispatch.md` before preparing adapter operation envelopes or applying the Adapter Dispatch Review guard.
- Read `references/github-mcp-projects.md` before representing GitHub Projects MCP route availability, typed route blocks, or adapter result normalization.
- Read `references/hermes-mcp-governance.md` before giving setup guidance for MCP registration, credential/tool enablement boundaries, or Hermes delegation risk.

## Operating Boundaries

- Keep Portfolio OS out of task state ownership. It may keep source trail, routing rationale, draft previews, backend references, and decision logs.
- Do not implement or call GitHub adapters, `gh` command planners, direct GraphQL clients, MCP servers, credential setup, MCP registration, remote writes, issue/PR creation, push, or merge.
- Prefer host-provided MCP, reader, skill, CLI, or URL surfaces as external adapter routes. The plugin does not own backend API clients.
- Stop before adapter dispatch unless the caller has provided a reviewable operation envelope and explicit approval path.
- Keep GitHub Projects details such as raw node IDs, field IDs, tokens, owner, project number, and repository out of reusable skill contracts unless an external adapter result has already returned an opaque reference.

## Default Flow

1. Read the caller's task source and identify the intended task outcome.
2. Produce a backend-neutral task draft with title, body, task type, work unit fields when known, and review notes.
3. Resolve backend routing from explicit override, caller/profile config, then `default_backend`; if none is available, use `github_projects_mcp`.
4. Require a destination supplied by caller, profile, or host registration before any adapter-facing preview.
5. Present a human review summary before any state-changing adapter route is used.

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
