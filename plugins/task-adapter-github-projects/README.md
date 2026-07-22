# GitHub Projects Task Adapter

`task-adapter-github-projects` version `0.1.0` is the provider-specific runtime
behind `task-management` interface v2. It owns GitHub Projects/Issue mapping and
registers this exact adapter contract v2 trio for Hermes:

- `task-adapter-github-projects-read:task_adapter__github_projects__task_query`
- `task-adapter-github-projects-write:task_adapter__github_projects__task_preflight`
- `task-adapter-github-projects-write:task_adapter__github_projects__task_apply`

The adapter and task-management packages do not import one another. Their wire
contract is pinned by the exact frozen `tests/fixtures/adapter-v2` copy and the
public fake end-to-end suite.

## Host configuration

Set `TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE` to a host-owned file based on
`config/github-projects.example.toml`. It contains:

- the exact allowlisted GitHub MCP public tool names;
- opaque destination and content-target references;
- adapter-private owner, project number, repository, and canonical field
  mappings;
- a fail-closed host exposure attestation.

It contains no credentials. Authentication remains in the separately managed
GitHub MCP server. The paired task-management route and this config must use the
same opaque `destination_ref` and `content_target_ref` values.

Required exposure policy:

```toml
raw_mcp_exposure = "adapter_only"
adapter_write_exposure = "task_management_only"
```

Raw MCP tools are never model input, and adapter write tools must not be exposed
directly to a model or child agent. Task-management alone resolves and invokes
the fixed adapter tools after approval binding.

## Runtime behavior

- `query` resolves the configured Project, paginates fields/items, and emits
  backend-neutral task snapshots without provider raw IDs.
- `preflight` uses read probes only. It validates host attestation,
  destination, fields, and item-read capability; readiness is not approval.
- `apply` supports linked-Issue create, update, comment, and report. Create
  writes the Issue, attaches it to the Project, writes reviewed fields, and
  reads the result back.
- Approval is not accepted by this plugin as caller input. The adapter write
  tool is host-policy restricted to task-management, which supplies the exact
  operation digest after its own re-preflight and approval check.
- Partial writes are never blindly retryable. An explicit first-write
  rate-limit response that states no write occurred may be retryable; unknown
  write outcomes require human inspection.

The adapter fails closed on missing config, credentials in arguments/config,
caller-selected tools, unsafe delegation, destination mismatch, invalid public
envelopes, ambiguous MCP responses, and raw provider leakage.

## Verification and live boundary

```bash
python3 -m unittest discover -s plugins/task-adapter-github-projects/tests
python3 plugins/task-adapter-github-projects/scripts/smoke_test_hermes_adapter.py
```

Tests use fake public GitHub MCP dispatch. The smoke uses an installed Hermes
`PluginContext` with hermetic fake MCP tools. Neither path edits a live profile,
uses credentials, contacts GitHub, or mutates a real Project/Issue.

Repository completion does not install or activate this adapter. Plugin install,
route/config placement, MCP registration, authentication, permission setup,
toolset exposure, and real GitHub mutation require a separate live activation
gate.
