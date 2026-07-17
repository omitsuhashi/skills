# Task Read Adapter

Hermes exposes one public read-only tool: `task-management-read:task_query`.
Codex uses the workflow skill and does not receive a runtime tool from the Codex
manifest because this package bundles no MCP server.

## Public Input

```yaml
destination_ref: tasks:default
query:
  work_unit_id: planning
  status: ready
  due_before: 2026-07-16
  limit: 20
```

`query.backend_key` is optional. The host-owned route resolves its default.
Callers never provide a route file, adapter kind, tool name, provider
destination, local path, GitHub target, credential, raw payload, or cursor.

## Versioned Host Contract

`TASK_MANAGEMENT_READ_ROUTES_FILE` points to a host-owned TOML document with
`contract_version = 1`. A route fixes capability `task_read`, a logical
destination mapping, and exactly one external adapter:

- `mcp`: dispatches one exact `mcp__<server>__task_query` tool.
- `plugin`: dispatches one exact `task_adapter__<provider>__task_query` tool.

All adapters implement the internal
`ResolvedTaskReadRequest -> AdapterTaskSnapshotResult` boundary. File access or
Hermes dispatch is bound when the adapter is constructed; the public request
cannot replace it. Adapter contract version is 1. External adapters must handle
pagination internally up to `query.limit`; the public contract exposes no
provider cursor. External responses are capped at 5 MiB and 100 items, and the
public `limit` is applied before normalization. Route kind/tool namespaces must
match, and duplicate `public_ref` mappings fail as `invalid_read_route`.

`TASK_MANAGEMENT_READ_ADAPTER_TOOL` remains a legacy single-MCP-route mode. It
requires `query.backend_key` and never acts as a GitHub fallback.

## Test and Smoke Fixture

The read-only `local_json` adapter is retained only for plugin-owned tests and
the isolated Hermes smoke. It is not an operator-facing runtime backend,
bootstrap route, or persistent task source of truth. The smoke copies a test
fixture and route into a temporary directory and cleans them up when the process
exits. The adapter still validates the JSON envelope, file boundary,
regular-file/size constraints, filters, and limit. There is no local write
adapter; mutable task state stays MCP/provider-owned.

## Typed Errors

- `read_route_missing`, `read_route_not_found`, `invalid_read_route`,
  `read_route_contract_mismatch`
- `read_adapter_unavailable`, `invalid_read_adapter_tool`,
  `adapter_contract_mismatch`, `task_source_unreadable`
- allowlisted provider states such as `read_adapter_auth_missing`,
  `read_adapter_permission_denied`, `read_destination_not_found`,
  `read_adapter_rate_limited`, and `read_adapter_timeout`
- `invalid_task_query`, `invalid_adapter_result`, `invalid_task_snapshot`,
  `unsafe_task_snapshot`

All failures omit raw adapter payloads and credentials. Successful items are
re-normalized through the canonical `TaskSnapshot` allowlist, so provider IDs,
unknown metadata, unsafe URLs, and credential-like values fail closed.

For the actor-by-actor routing overview and sequence diagram, see
[`routing-flow.md`](routing-flow.md).
