# Backend Routing

The read route registry is host-owned. It lets every consumer use the same
`task_query` contract while the host chooses a local bootstrap read snapshot,
MCP tool, or provider-plugin tool. There is no implicit GitHub fallback.

## Route Registry

```toml
contract_version = 1
default_backend = "local_tasks"

[backends.local_tasks]
kind = "local_json"
capability = "task_read"
read_root = "../examples"
source_path = "local-task-snapshot.example.json"

[backends.local_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
```

The host can replace this with `kind = "mcp"` or `kind = "plugin"` and a fixed
read-only `tool_name`. The config stores no credentials. The model cannot set
`read_root`, `source_path`, `tool_name`, or `provider_ref`.

## Destination Input

The public `destination_ref` is an opaque logical reference. The route maps it
to a provider-owned opaque reference without exposing that value in the public
result. For state-changing workflows, `TaskBackendDestination` remains the
review surface and may also carry a `destination_label` or
`content_target_ref`.

These are opaque references. The task-management plugin must not decompose or
store GitHub owner, project number, repository, token, node ID, field ID, or
option ID in route config.

## Resolution Order

1. Optional internal `query.backend_key` when a trusted caller supplies it.
2. Host `default_backend`.
3. Typed `read_route_not_found` error.

The plugin never invents a backend, destination, local path, or provider tool.
Changing providers changes only host config and the adapter implementation;
Schedule Secretary, Portfolio OS, and other consumers keep the same public
query/result contract.

## Read and Write Ownership

`local_json` is a bootstrap read snapshot, not a mutable management system.
The plugin exposes no local write adapter. Mutable task state and all provider
writes belong to an MCP server or another provider plugin and still require the
existing Adapter Dispatch Review. The task-management plugin has no direct API,
GraphQL, `gh`, or credential fallback.
