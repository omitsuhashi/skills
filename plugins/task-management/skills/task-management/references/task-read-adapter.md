# Task Read Adapter

The `task-management-read` toolset exposes one Hermes tool: `task_query`. It
accepts a backend-neutral `TaskQuery`, calls a fixed host-provided read adapter,
and returns `TaskSnapshotResult` with zero or more normalized `TaskSnapshot`
values.

## Public Input

```yaml
destination_ref: github-projects:portfolio-os-task-board
query:
  backend_key: github_projects_mcp
  work_unit_id: planning
  task_type: coordination
  status: ready
  due_before: 2026-07-16
  limit: 20
```

`destination_ref` remains opaque. `TaskQuery` must not contain GitHub owner,
project number, repository, node ID, field ID, credential, raw payload, or
adapter tool name.

## Host Adapter Contract

The operator configures `TASK_MANAGEMENT_READ_ADAPTER_TOOL` with a registered
Hermes MCP tool name matching `mcp__<server>__task_query`. The public tool does
not accept an adapter tool name from the model, so it cannot be redirected to a
write-capable MCP tool at call time.

The host adapter owns provider API access, authorization, credentials,
pagination, rate limiting, destination resolution, and provider field mapping.
It accepts the same `destination_ref` and `query` envelope and returns an
`items` array. Normal repository tests use a mock dispatch function and never
require live Hermes, MCP, GitHub, or credentials.

## Normalized Output

Successful reads return:

```yaml
result_type: TaskSnapshotResult
ok: true
backend_key: github_projects_mcp
destination_ref: github-projects:portfolio-os-task-board
task_snapshots:
  - result_type: TaskSnapshot
    task_ref:
      backend_key: github_projects_mcp
      task_ref: external_ref
      task_url: https://example.invalid/tasks/1
      title: Prepare quarterly plan
    title: Prepare quarterly plan
    body: Draft and review the quarterly plan.
    work_unit_id: planning
    work_unit_name: Planning
    task_type: coordination
    status: ready
    due_date: 2026-07-16
    urgency: high
    importance: high
    automation_mode: assistive
    approval_required: false
    source_ref:
      kind: task_backend
      ref: external_ref
      label: Portfolio OS Tasks
    backend_metadata:
      display_link:
        name: Open task
        url: https://example.invalid/tasks/1
error: null
```

Only canonical `TaskRef`, `TaskSnapshot`, `source_ref`, and display-link fields
survive normalization. Unknown backend metadata is dropped. Credential-like
values and provider ID markers cause the whole result to fail closed rather
than returning a partial or redacted snapshot. Query/snapshot taxonomy and ISO
dates are validated. `task_url` and `backend_metadata.display_link.url` must be
HTTP(S) URLs without embedded credentials.

## Typed Errors

- `read_adapter_unavailable`: `TASK_MANAGEMENT_READ_ADAPTER_TOOL` is absent.
- `invalid_read_adapter_tool`: the configured name is not an MCP `task_query` tool.
- `invalid_task_query`: the public query shape is invalid.
- `read_adapter_failed`: the host adapter returned an error.
- `invalid_adapter_result`: the adapter result is not the required JSON object and items array.
- `invalid_task_snapshot`: an item cannot satisfy the canonical `TaskSnapshot` shape.
- `unsafe_task_snapshot`: a normalized value still contains provider credential material.

All errors omit raw adapter payloads and credential values.
