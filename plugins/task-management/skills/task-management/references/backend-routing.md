# Backend Routing

The Route Registry is host-owned and credential-free. It binds the public
task-management interface to a fixed adapter trio; there is no implicit GitHub
fallback.

## Route Registry

```toml
contract_version = 2
default_backend = "remote_tasks"

[backends.remote_tasks]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"

[backends.remote_tasks.destinations.portfolio_os]
public_ref = "tasks:portfolio-os"
destination_label = "Portfolio OS Tasks"
content_target_ref = "task-content:portfolio-os"
```

Tool names and `adapter_key` must be a coherent fixed trio. A public request
cannot replace them. Route v1, duplicate destination refs, wrong namespaces, a
missing capability, and unknown destinations fail closed.

## Destination Input

`TaskBackendDestination` contains backend key, opaque `destination_ref`, human
label, and optional opaque `content_target_ref`. They are opaque references;
task-management must not decompose or store GitHub owner, project number,
repository, token, field ID, option ID, item identifier, or credential from
them. The separate adapter config
owns those mappings.

## Resolution order

1. An optional trusted internal `backend_key`.
2. Host `default_backend`.
3. Typed route failure.

The same resolved route is used for read, preflight, re-preflight, and apply.
Any route-binding drift invalidates the prior approval.

## Test and smoke fixture

`local_json` is a test and smoke fixture only and not a normal runtime backend.
Tests create temporary files and `HERMES_HOME`; they do not publish a local task
store. Mutable state and provider writes remain external-adapter-owned.
