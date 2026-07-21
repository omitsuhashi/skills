# GitHub Projects Task Adapter

This dual-host plugin isolates GitHub Projects provider knowledge from
`task-management`. Codex receives valid distribution metadata; Hermes receives
the exact query, preflight, and apply runtime registrations declared by
`plugin.yaml`.

POTASK-016 establishes contracts and a fail-closed registration seam only. The
placeholder handlers do not dispatch provider tools. This package does not install
or register an MCP server, edit a marketplace or live profile, set up
permissions, or create/update a GitHub Project or Issue. Executable preflight,
query, and apply orchestration belong to subsequent approved issues.

## Host configuration

Set `TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE` to a host-owned file based on
`config/github-projects.example.toml`. The file contains exact MCP tool names,
opaque destination/content-target mappings, GitHub coordinates, canonical field
mapping, and host attestation. It contains no credentials; authentication stays
with the separately managed GitHub MCP server.

The required exposure policy is deliberately narrow:

- `raw_mcp_exposure = "adapter_only"`
- `adapter_write_exposure = "task_management_only"`

The write toolset must not be exposed directly to a model or child agent.
Task-management owns fixed internal routing into the adapter.

## Runtime tools

- `task_adapter__github_projects__task_query` in
  `task-adapter-github-projects-read`
- `task_adapter__github_projects__task_preflight` and
  `task_adapter__github_projects__task_apply` in
  `task-adapter-github-projects-write`

The adapter and task-management packages do not import one another. Their seam
is `adapter_contract_version: 2`, pinned by the frozen normative fixtures under
`tests/fixtures/adapter-v2` and the compatibility suite.
