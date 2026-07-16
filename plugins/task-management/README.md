# Task Management Plugin

`task-management` keeps task consumers independent of the storage provider.
Codex receives the bundled workflow skill. Hermes additionally loads the native
read-only `task-management-read:task_query` runtime tool from `plugin.yaml` and
`__init__.py`. This package does not bundle an MCP server, so the Codex manifest
does not declare `mcpServers`.

## Hermes Install

```bash
hermes plugins install git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```

The Hermes entrypoint registers `task-management:task-management` through
`ctx.register_skill` and `task_query` through `ctx.register_tool`. The
authoritative Hermes export is `plugin.yaml.exports.toolsets`, which exactly
matches `task-management-read` at runtime.

## Read Routes

The public tool accepts an opaque logical `destination_ref` and a neutral query.
`query.backend_key` is optional; when omitted, the host route's
`default_backend` is used. Callers never supply an adapter kind, tool name,
provider destination, route path, or local file path.

Set the host-owned route file:

```bash
export TASK_MANAGEMENT_READ_ROUTES_FILE=/host-owned/task-read-routes.toml
```

Start from `config/task-backends.example.toml`. Its `local_tasks` route reads the
versioned `examples/local-task-snapshot.example.json` file as a bootstrap read
snapshot. It is not a mutable task-management source of truth and the plugin
does not provide a local write tool. A mutable backend remains owned by an MCP
server or another provider plugin.

External routes fix exactly one read-only tool in host config:

- `mcp__<server>__task_query`
- `task_adapter__<provider>__task_query`

The adapter contract is version 1 and capability `task_read`. External adapters
own provider authorization, pagination, destination mapping, and provider-side
errors. They must page internally up to the requested `limit`; provider cursors
are not exposed by the public result. Responses are limited to 5 MiB and 100
items, and the public `limit` is applied before snapshot normalization. Route
kind and tool namespace must match (`mcp` to `mcp__...`, `plugin` to
`task_adapter__...`), and duplicate logical destination refs invalidate the
route. The facade allowlist-normalizes every item
and rejects raw provider IDs, unknown metadata, unsafe links, and credential-like
values.

See
[`routing-flow.md`](skills/task-management/references/routing-flow.md) for the
read routing overview, end-to-end sequence, backend switch, ownership table, and
the separate state-changing boundary.

`TASK_MANAGEMENT_READ_ADAPTER_TOOL=mcp__<server>__task_query` remains supported
only as the POTASK-010 single-route compatibility mode. It requires
`query.backend_key` because no host route is available to resolve a default.
There is no implicit GitHub route and no direct provider API, GraphQL, or `gh`
fallback.

## Verification

The isolated smoke test uses the installed Hermes `PluginContext` and registry,
a temporary `HERMES_HOME`, and the local snapshot fixture. It does not edit a
live profile or contact a provider:

```bash
python3 scripts/smoke_test_hermes_read.py
```

## Update Caveat

A subdirectory install usually does not retain `.git`, so
`hermes plugins update task-management` may report that it is not a git
checkout. Refresh with:

```bash
hermes plugins install --force git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```
