---
name: task-management
description: Use for backend-neutral task intake and task backend routing workflows, especially when converting capture/chat text into a reviewed task draft, preparing human approval text, checking task backend boundaries, or preparing adapter dispatch previews without implementing GitHub adapters, gh command planners, direct GraphQL clients, MCP servers, credentials, or external writes.
---

# Task Management

Use this skill to normalize task intent, prepare reviewable task drafts, and keep task backend routing separate from Portfolio OS state. Treat the selected backend as the source of truth for task state.

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
- task title, body, and fields
- `work_unit_id` and `work_unit_name` when known
- expected adapter side effects
- adapter tool name or route surface, if supplied by the host

If destination, capability, or tool availability is missing, stop with setup guidance instead of inventing a backend target.
