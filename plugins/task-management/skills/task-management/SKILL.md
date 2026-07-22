---
name: task-management
description: Use for backend-neutral task intake, normalized task reads, reviewable task preflight, and approval-bound create/update/comment/report through a host-configured adapter. Keep provider tools, GitHub coordinates, credentials, raw payloads, and live activation outside the reusable workflow.
---

# Task Management

Use this shared Codex/Hermes skill to turn intent into neutral task contracts and
to use the public task interface without selecting provider tools. Hermes exposes
`task-management-read:task_query` and
`task-management-write:{task_preflight,task_apply}`. Codex follows the same
workflow through this skill.

## References

- Read `references/task-draft-contract.md` before composing a TaskDraft.
- Read `references/decision-support-policy.md` when intent, priority, routing,
  or continue/stop/defer/delegate meaning is uncertain. Ask the human when the
  uncertainty affects the task outcome or authorization; do not invent intent.
  Before composing a new TaskDraft, use that policy for decision-sensitive
  intake. Do not use it for task reads, backend routing, or adapter previews;
  skip decision support for current-state reads, routing, and adapter previews.
- Read `references/task-contracts.md` for the v2 neutral wire shapes and safety
  boundary.
- Read `references/task-read-adapter.md` before calling `task_query` or
  interpreting read errors.
- Read `references/backend-routing.md` for the unified host route.
- Read `references/adapter-dispatch.md` before `task_preflight` or `task_apply`.
- Read `references/routing-flow.md` for the full read/write sequence and
  ownership at each hop.
- Read `references/github-mcp-projects.md` for the separate GitHub Projects
  adapter contract and partial/retry semantics.
- Read `references/hermes-mcp-governance.md` before host setup or live
  activation guidance.

## Operating boundaries

- The public request may carry only a neutral query/operation and opaque
  `destination_ref`. Never accept a route path, adapter tool, MCP tool, GitHub
  owner/repository/project/field identifier, credential, or raw provider payload
  from the model.
- The host-owned route fixes one adapter `query`, `preflight`, and `apply` trio.
  Task-management owns resolution, normalization, re-preflight, and approval
  identity. The provider adapter owns provider mapping and mutations.
- `local_json` is a plugin-owned test/read-smoke fixture only. There is no local
  write adapter or Portfolio OS task ledger.
- Portfolio OS must not own task route, task data, task result, or task-specific
  evidence. It may keep only generic plugin selection, native install, manifest
  identity / required-export verification, and generic profile enablement
  evidence.
- Plugin install and repository tests do not configure a route, install an
  adapter, register MCP, authenticate, edit a profile, or perform a live write.

## Default flow

1. Normalize the requested outcome. If material intent or routing is uncertain,
   ask the human before drafting or authorizing a task.
2. For current state, call `task_query(destination_ref, query)` and stop on any
   typed error.
3. Build a backend-neutral TaskDraft and operation envelope. Use `task_ref` only
   for update/comment/report; create requires `task_ref: null`.
4. Call `task_preflight(interface_version=2, operation=...)`. Treat readiness as
   evidence only, never as write approval.
5. Present the exact `ApprovalPreview`, including destination, task content,
   route binding, and ordered expected side effects.
6. Use `decision: approved` only after explicit human approval of that exact
   digest. Use `decision: confidence_authorized` only when preflight is all
   three: ready, confidence-eligible, and certain. Any explicit approval flag,
   review note, adapter uncertainty, blocked readiness, or changed preview
   requires human approval or a new preflight.
7. Call `task_apply` with the exact preview and receipt. It reloads the route,
   re-preflights, rejects drift, and dispatches the fixed adapter apply tool.
8. Read `TaskWriteResult`. Inspect partial or unknown outcomes before retrying.
   Retry automatically only when the typed result explicitly says no write
   occurred and `retryable: true`.
9. Use `task_query` when a post-write public readback is needed.

## Review surface

Show the human: operation type; backend and opaque destination; task title/body
and neutral fields; `work_unit_id` and `work_unit_name`; existing opaque
`task_ref` when required; ordered expected side effects; approval mode; and the
approval digest. If any value changes, discard the prior receipt and preflight
again.
