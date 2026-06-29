# Hermes MCP Governance

This reference defines the governance boundary for using host-provided MCP
adapter tools from the task-management skill. Hermes Agent, or another MCP host,
owns MCP server registration, credentials, profile edits, tool enablement, and
adapter availability. The task-management plugin owns only the reviewed task
draft, backend route selection, adapter operation envelope, and normalized
adapter result boundary.

## Install Boundary

Installing or updating the task-management plugin must not:

- register MCP servers
- configure credentials or tokens
- edit live Hermes profiles
- enable GitHub adapter tools
- change permissions or delegation settings
- call live GitHub, Hermes, MCP, browser, credential, or network surfaces

The plugin may ship references, configuration templates, examples, static
fixtures, and tests. It must not turn those artifacts into live host
configuration during install.

## Adapter Availability Gate

The Adapter Availability Gate is host / adapter-side confirmation. It is not a
plugin implementation side effect.

Before a state-changing GitHub MCP adapter tool can receive an approved
operation envelope, the host or adapter must confirm:

- the MCP server for the route is registered outside plugin install
- the required credential or authorization is ready in the host-owned adapter
  flow
- the required adapter tool is explicitly enabled for the task-management flow
- the connection reference and destination reference resolve on the adapter side
- the adapter can report missing server, disabled tool, missing auth,
  permission failure, destination not found, and field missing as availability
  states

The task-management plugin may consume this host-provided availability data and
map it to the typed GitHub MCP route results described in
`github-mcp-projects.md`. If any required condition is absent, the plugin stops
before adapter dispatch and returns setup guidance. It does not self-register,
self-authenticate, self-enable, repair schema, or fall back to a direct GitHub
client.

## Credential Boundary

Credentials belong to the host-owned MCP adapter flow. They must not be stored
in task-management config, examples, task drafts, adapter envelopes, normalized
task refs, logs, or knowledge docs.

Use opaque references such as `connection_ref`, `destination_ref`, and
`task_ref`. Do not expose tokens, authorization headers, GitHub node IDs, field
IDs, project IDs, owner names, repository IDs, or project numbers as reusable
task-management contract values.

## Delegation Boundary

Hermes profiles may set `delegation.inherit_mcp_toolsets: true`. That setting is
risky for state-changing MCP adapter tools because a child agent can inherit the
same create, update, comment, or report capability that was intended only for a
commander or task-management flow.

GitHub MCP adapter tools must not be unconditionally inherited by child agents.
When state-changing tools are enabled for task-management, use a narrow
host-side policy such as:

- enable the tools only for the commander or task-management profile that owns
  Adapter Dispatch Review
- do not expose the tools to review workers, work-unit subagents, or generic
  implementation workers by default
- pass reviewed task drafts, operation previews, or normalized results to child
  agents instead of passing the toolset itself
- require a fresh Adapter Dispatch Review after any destination, tool name,
  operation type, task reference, or expected side effect changes
- keep manual approval and MCP reload confirmation enabled when the host
  supports those controls

If the host cannot prevent unconditional inheritance of state-changing GitHub
MCP tools, treat the Adapter Availability Gate as blocked for write operations.
The skill may still produce previews and setup guidance, but it must not hand an
operation envelope to the adapter.

## Approval Boundary

Adapter availability does not approve a task write. It only proves that the host
can route the approved operation to an external adapter.

Every state-changing operation still needs Adapter Dispatch Review for the
exact envelope values: backend key, connection reference, destination reference,
destination label, operation type, adapter tool name, task content, work unit
fields, task reference when present, and expected adapter side effects.
