# Backend Routing

This reference defines how the task-management skill chooses a backend route
without embedding a concrete project destination in plugin config.

GitHub Projects via the `github_projects_mcp` route is the first backend for the
initial package, not a permanent architecture. The route registry is deliberately
backend-neutral so later MCP, reader, skill, CLI, or URL backed systems can be
selected without making Portfolio OS a task state store.

## Route Registry

The route registry describes connection surfaces only. It answers "which
surface can handle this operation?" and never answers "which concrete project,
repository, board, or workspace should receive this task?"

The committed example config is `plugins/task-management/config/task-backends.example.toml`.
Runtime config may be installed or supplied by a caller/profile/host, but it
must keep the same boundary.

Route entries have this shape:

```toml
default_backend = "github_projects_mcp"

[backends.github_projects_mcp]
kind = "mcp"
connection_ref = "github-projects"
capability = "project_management"

[backends.github_projects_mcp.field_overrides]
work_unit_id = "Work Unit"
work_unit_name = "Work Unit Name"
due_date = "Due Date"
importance = "Priority"
approval_required = "Approval Required"
```

Required route fields:

- `kind`: one of `mcp`, `reader`, `skill`, `cli`, or `url`.
- `connection_ref`: opaque host connection reference, such as a registered MCP
  server/tool surface name.
- `capability`: backend-neutral capability label, such as
  `project_management`.
- `field_overrides`: optional mapping from backend-neutral task fields to
  backend display field names.

The initial default backend key is `github_projects_mcp`. That key means "use
the GitHub Projects MCP route if the host has made it available"; it does not
select a GitHub organization, project number, repository, issue tracker, or
credential.

## Destination Input

A destination is separate caller/profile/host input represented as
`TaskBackendDestination`. It answers "where should this task be written for this
operation?"

Backend routes must not invent a destination. If no destination is supplied, the
skill stops before adapter preview or dispatch and asks for a caller/profile/host
registration.

Destination input has this backend-neutral shape:

```toml
[destinations.default_task_project]
backend = "github_projects_mcp"
destination_ref = "github-projects:portfolio-os-task-board"
destination_label = "Portfolio OS Tasks"

# Optional. Provide only when the adapter operation needs a separate content
# target, such as an issue repository, in addition to the project destination.
content_target_ref = "github-content-target:portfolio-os-issues"
```

`destination_ref` and `content_target_ref` are opaque references. For GitHub
Projects they may resolve outside this plugin to an organization/project and,
when needed, a repository. The task-management plugin must not decompose or
store GitHub owner, project number, repository, token, node ID, field ID, or
option ID in route config.

## Resolution Order

Resolve backend routing in this order:

1. Explicit backend override supplied with the task operation.
2. Caller/profile runtime config.
3. `default_backend` from runtime config.
4. Built-in fallback key `github_projects_mcp`.

After a backend key is selected, require a matching
`TaskBackendDestination` from caller/profile/host registration before preparing
an adapter-facing preview.

Stop before any adapter tool call when:

- the selected backend key is missing from the registry,
- the route kind/capability cannot support the requested operation,
- no destination was supplied for the selected backend,
- the host connection/tool surface is unavailable, or
- the operation would require credentials or concrete GitHub targets from plugin
  config.

## Adapter Preview Contract

Adapter Dispatch Review previews that use a selected route must show:

- backend key and `connection_ref`,
- destination reference and label,
- operation type,
- task title, body, and fields,
- `work_unit_id` and `work_unit_name` when known,
- expected adapter side effects,
- adapter tool name or route surface supplied by the host.

The preview may carry opaque backend references returned by an adapter, such as
a task URL or item reference. It must not expose raw provider implementation
IDs as reusable task-management contract fields.
