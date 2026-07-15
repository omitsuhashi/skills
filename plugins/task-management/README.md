# Task Management Plugin

`task-management` is a thin Hermes / Codex workflow package for reviewed task
intake, backend-neutral task routing, and normalized task reads. The package
ships one primary skill at `skills/task-management/SKILL.md`. It does not
register MCP servers, configure credentials, edit Hermes profiles, or perform
GitHub writes during install.

## Hermes Install

Install the plugin subdirectory from this repository:

```bash
hermes plugins install git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```

Hermes will discover `plugin.yaml` and load `__init__.py` when the plugin is
enabled. The entrypoint registers the bundled skill as
`task-management:task-management` through `ctx.register_skill` and the
read-only `task_query` tool in the `task-management-read` toolset through
`ctx.register_tool`.

`plugin.yaml` is the authoritative Hermes manifest. Its `exports.toolsets`
value is exactly `task-management-read`, matching the runtime registration.
The Codex `.codex-plugin/plugin.json` remains within the current
`plugin-creator` schema, which does not accept an `exports` field.

## Read Adapter

The public `task_query` tool accepts an opaque `destination_ref` and a
backend-neutral `TaskQuery`. It dispatches only to the host-configured MCP tool
named by `TASK_MANAGEMENT_READ_ADAPTER_TOOL`. The configured name must match
`mcp__<server>__task_query`; arbitrary MCP tool names and write tools are
rejected before dispatch.

The host-provided adapter owns provider access, credentials, pagination, and
destination resolution. It returns an `items` array, and this plugin projects
each item into the canonical `TaskSnapshot` allowlist. Provider raw IDs,
unknown backend metadata, and credential-like values are never returned to the
caller. Query/snapshot taxonomy and ISO dates are validated, and linkable URLs
must use `http` or `https` without embedded credentials. Missing configuration,
invalid adapter output, and unsafe snapshots fail closed with typed errors.

Example host configuration:

```bash
export TASK_MANAGEMENT_READ_ADAPTER_TOOL=mcp__task_backend__task_query
```

This variable contains only a registered Hermes tool name. It is not a token,
credential, GitHub owner, project number, or destination mapping.

## Update Caveat

Current Hermes installs a subdirectory plugin by cloning the repository to a
temporary directory and moving only the selected subdirectory into
`~/.hermes/plugins/task-management`. That installed directory usually does not
retain `.git`, so:

```bash
hermes plugins update task-management
```

may fail with "not a git checkout". Until Hermes records source metadata for
subdirectory plugins or this plugin is published as a standalone repository,
refresh it with a forced reinstall:

```bash
hermes plugins install --force git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```
