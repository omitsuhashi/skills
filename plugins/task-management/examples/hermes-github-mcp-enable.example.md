# Hermes GitHub Adapter Activation Example

This is a host-operator checklist, not an install script. Repository tests do not
execute it.

## Required artifacts

1. Install/enable `task-management` version `0.4.0`.
2. Install/enable `task-adapter-github-projects` version `0.1.0`.
3. Place a host-owned task route based on
   `task-management/config/task-backends.example.toml` and set
   `TASK_MANAGEMENT_ROUTES_FILE`.
4. Place a host-owned adapter config based on
   `task-adapter-github-projects/config/github-projects.example.toml` and set
   `TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE`.
5. Ensure both configs use the same opaque `destination_ref` and
   `content_target_ref`.

## MCP and exposure checks

- Register/authenticate the GitHub MCP connection outside plugin install.
- Enable only the exact adapter-config allowlist.
- Keep raw MCP exposure `adapter_only`.
- Keep adapter write exposure `task_management_only`.
- Block write readiness if child agents can inherit raw or adapter write tools.
- Keep credentials out of both TOML files and all task values.

## Approval and live check

Run `task_preflight` against the intended opaque destination. Readiness does not
approve a write. Ask the human when the task intent or result is uncertain.
`confidence_authorized` is valid only when the result is ready,
confidence-eligible, and certain; otherwise require an exact human-approved
preview/digest.

Only an independently approved live activation gate may call `task_apply` on a
real destination. Record the exact preflight, receipt, normalized write result,
and public `task_query` readback. A partial or unknown result stops for human
inspection; retry only when the result explicitly confirms no write occurred.
