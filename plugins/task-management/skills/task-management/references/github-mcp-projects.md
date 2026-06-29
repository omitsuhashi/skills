# GitHub MCP Projects Route

This reference defines the `github_projects_mcp` backend route. It is an
external adapter route: GitHub MCP Server owns GitHub Projects read/write
behavior, while the task-management plugin normalizes route availability and
adapter results into the backend-neutral `TaskWriteResult` boundary.

## Scope

The route may be used only after the normal TaskDraft preview and Adapter
Dispatch Review guard have approved the same operation, destination, and adapter
tool name.

The task-management plugin may:

- identify the configured backend key, connection reference, destination
  reference, destination label, operation type, and adapter tool name
- check route availability from host-provided capability data
- represent unavailable route states as typed results
- normalize an external adapter result into `TaskWriteResult`

The task-management plugin must not:

- register MCP servers, edit Hermes profiles, enable adapter tools, configure
  credentials, or modify permissions during plugin install
- implement GitHub API clients, GitHub adapters, `gh` command planners, direct
  GraphQL clients, schema repair, retry policy, duplicate-prevention stores,
  `task_sha`, or local task ledgers
- call GitHub, Hermes, MCP, browser, credential, or network surfaces during
  normal tests

The plugin install must not register MCP servers or enable GitHub adapter tools.
More completely, plugin install must not register MCP servers, configure
credentials, edit Hermes profiles, or enable GitHub adapter tools. Those actions
belong to the host / adapter-side setup path described in
`hermes-mcp-governance.md`.

No live smoke test is required for this route in the repository test suite.
Fixture-backed tests cover the plugin-owned contract. Live GitHub MCP Server
behavior belongs to the host and adapter availability gate.

## Route Inputs

The route needs these values before an adapter-facing preview can be prepared:

| Field | Contract |
| --- | --- |
| `backend_key` | Must be `github_projects_mcp` for the default GitHub Projects route. |
| `kind` | Must be `mcp`; other backend kinds use different route contracts. |
| `connection_ref` | Opaque host or profile reference, for example `github-projects`. It is not a credential. |
| `capability` | Host-declared capability such as `project_management`. |
| `destination_ref` | Opaque destination reference supplied by caller, profile, or host registration. |
| `destination_label` | Human-readable destination label shown in review previews. |
| `adapter_tool_name` | Host-provided MCP adapter tool route for the approved operation. |

GitHub owner, project number, repository, node IDs, field IDs, option IDs, and
tokens are not route inputs for the reusable task-management contract. If the
external adapter requires target details, it must resolve them from the opaque
host-owned connection and destination references.

## Adapter Availability Gate

The Adapter Availability Gate is host / adapter-side confirmation, not a plugin
implementation side effect. The host or adapter supplies availability evidence
for the configured MCP server, credentials, enabled adapter tool, destination,
and project field readiness. The task-management plugin maps that evidence to
typed route results and stops before dispatch when setup is incomplete.

Passing this gate must not be implemented by plugin install, self-registration,
Hermes profile editing, credential setup, automatic tool enablement, schema
repair, or direct GitHub fallback code. The gate confirms that an external MCP
adapter is ready to receive an operation that has already passed TaskDraft
review and Adapter Dispatch Review.

When a Hermes profile uses `delegation.inherit_mcp_toolsets: true`, the host
must ensure state-changing GitHub MCP adapter tools are not unconditionally
inherited by child agents. If that delegation boundary is not enforced, write
availability is blocked even if the MCP server and credentials exist.

## Preflight Result Codes

Preflight is a representation step, not a live GitHub check. The host or caller
may supply availability data. The task-management plugin maps that data to a
typed `TaskWriteResult` and stops before dispatch when any required condition is
missing.

| Code | Meaning | Dispatch behavior |
| --- | --- | --- |
| `mcp_server_missing` | The host has no available GitHub MCP Server connection for `connection_ref`. | Stop and ask the human or host to configure the adapter outside plugin install. |
| `tool_disabled` | The server exists but the required adapter tool is not enabled for this flow. | Stop and request explicit tool enablement outside the plugin. |
| `auth_missing` | The adapter reports missing authentication or expired authorization. | Stop and ask the human to authenticate through the host-owned adapter flow. |
| `permission_failure` | Authentication exists, but the adapter lacks required project permission. | Stop and request access review; do not retry through a fallback client. |
| `project_not_found` | The opaque `destination_ref` cannot be resolved by the adapter. | Stop and ask the human to correct the destination registration. |
| `field_missing` | Required backend fields for the approved TaskDraft cannot be resolved. | Stop and provide setup guidance; do not create or repair schema here. |

These codes are stable contract values for normalizing GitHub MCP route
availability. Adapters may expose more detailed backend-specific errors, but the
reusable skill should return the stable code plus human action text.

## TaskWriteResult Shape

Every preflight block or adapter response normalizes to this shape:

```yaml
result_type: "TaskWriteResult"
ok: true | false
status: "created" | "updated" | "commented" | "reported" | "blocked" | "failed"
backend_key: "github_projects_mcp"
operation_type: "task.create"
destination_ref: "github-projects:portfolio-os-task-board"
task_ref:
  ref: "github-projects:portfolio-os-task-board/task/opaque-1024"
  url: "https://github.com/orgs/example-org/projects/portfolio-os-task-board?pane=task&item=opaque-1024"
  title: "Implement task draft composition guidance"
error: null
```

For blocked or failed operations, `task_ref` is `null` and `error` is populated:

```yaml
result_type: "TaskWriteResult"
ok: false
status: "blocked"
backend_key: "github_projects_mcp"
operation_type: "task.create"
destination_ref: "github-projects:portfolio-os-task-board"
task_ref: null
error:
  code: "field_missing"
  message: "Required backend field Work Unit is unavailable."
  retryable: false
  setup_required: true
  human_action: "Add the missing field in the GitHub Projects setup, then rerun preflight."
```

`task_ref.ref` is an opaque backend-owned reference. Consumers must not parse it
for GitHub IDs. Linkable URLs are allowed as backend-owned metadata, but
credentials, tokens, raw node IDs, field IDs, repository IDs, and project numbers
must not appear in `TaskWriteResult`.

## Adapter Result Normalization

An external GitHub MCP adapter may return its own result shape. The
task-management boundary keeps only these normalized values:

| Adapter result value | TaskWriteResult value |
| --- | --- |
| adapter success flag | `ok` |
| approved operation type | `operation_type` |
| approved backend key | `backend_key` |
| approved destination reference | `destination_ref` |
| adapter-owned task/item reference | `task_ref.ref` |
| adapter-owned task/project URL | `task_ref.url` |
| adapter-owned title or display label | `task_ref.title` |
| typed adapter error | `error.code`, `error.message`, `error.retryable`, `error.setup_required`, `error.human_action` |

The adapter owns write details such as whether it created a GitHub issue, a
project-native draft item, a project field update, or a comment. The reusable
task-management skill owns only the reviewed envelope and normalized result
boundary.

## Test Boundary

Normal tests must use static fixtures or mock result data. They must not require:

- live GitHub access
- Hermes live profile access
- credentials or tokens
- MCP server registration
- GitHub MCP Server read/write behavior

Repository tests should assert the typed result codes, `TaskWriteResult`
normalization, absence of implementation clients or command planners, and
absence of live dependency setup.
