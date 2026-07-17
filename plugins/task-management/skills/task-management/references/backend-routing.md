# Backend Routing

The read route registry is host-owned. It lets every consumer use the same
`task_query` contract while the host chooses an MCP tool or provider-plugin
tool. There is no implicit GitHub fallback.

## Route Registry

```toml
contract_version = 1
default_backend = "remote_tasks"

[backends.remote_tasks]
kind = "mcp"
capability = "task_read"
tool_name = "mcp__task_backend__task_query"

[backends.remote_tasks.destinations.default]
public_ref = "tasks:default"
provider_ref = "tasks:default"
```

The host can replace this with `kind = "plugin"` and a fixed
`task_adapter__<provider>__task_query` name. The config stores no credentials.
The model cannot set `tool_name` or `provider_ref`.

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
consumers keep the same public query/result contract.

## Test and Smoke Fixture

The read-only `local_json` adapter is retained only as a plugin-owned test and
smoke fixture seam. Tests use files under `tests/fixtures/`; the Hermes smoke
copies that data into a temporary directory together with a temporary route and
`HERMES_HOME`. These artifacts are discarded after the process exits.

`local_json` is not a normal runtime backend, operator bootstrap route, or
persistent task source of truth. Operator-facing route config uses an external
MCP or provider-plugin tool.

## Read and Write Ownership

The plugin exposes no local write adapter. Mutable task state and all provider
writes belong to an MCP server or another provider plugin and still require the
existing Adapter Dispatch Review. The task-management plugin has no direct API,
GraphQL, `gh`, or credential fallback.
