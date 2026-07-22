# Task Read Adapter

Hermes exposes `task-management-read:task_query`. Its caller supplies one opaque
logical destination and neutral filters:

```yaml
destination_ref: tasks:portfolio-os
query:
  backend_key: remote_tasks # optional; otherwise use host default
  work_unit_id: planning
  status: ready
  due_before: 2026-07-31
  limit: 20
```

The caller never provides a route/config path, adapter/MCP tool, provider
destination, GitHub coordinate, credential, raw payload, or cursor.

## Unified host contract v2

`TASK_MANAGEMENT_ROUTES_FILE` points to a host-owned TOML route with
`contract_version = 2`. Each external backend fixes an `adapter_key`, exact
`query_tool`, `preflight_tool`, and `apply_tool`, then maps opaque public
destinations to labels and optional opaque content targets. Duplicate public
references, namespace/capability mismatch, missing routes, and legacy route v1
fail before dispatch.

The read facade sends adapter contract v2 to the fixed query tool. External
responses are capped at 5 MiB and 100 items. The public limit is applied before
snapshot normalization; provider cursors and raw payloads never escape.

## Test and smoke fixture

The read-only `local_json` adapter is a plugin-owned test and smoke fixture. It
is not a normal runtime backend, not an operator-facing runtime backend, a bootstrap
route, or mutable task state. There is no local write adapter.

## Typed result

Success is `TaskSnapshotResult` containing only allowlisted `TaskSnapshot`
values. Missing/invalid route, unavailable adapter, contract mismatch, invalid
query/snapshot, unsafe URL, provider identifier, credential-like data, response
size, and item-count failures return safe typed errors without raw detail.

See [`routing-flow.md`](routing-flow.md) for the full read/write sequence.
