# Hermes GitHub MCP Enablement Example

This is an operator-facing example for making a GitHub MCP adapter available to
the task-management skill. It is not executed by plugin install, tests, or
normal task preview. It contains no credentials, owner names, repositories,
project numbers, field IDs, node IDs, or tokens.

## Boundary

The task-management plugin install does not perform MCP server registration,
credential setup, Hermes profile edits, GitHub adapter tool enablement, schema
repair, or live GitHub checks.

Hermes Agent, or another MCP host, owns those steps. The task-management skill
only consumes host-provided availability evidence and stops before adapter
dispatch when the evidence is missing.

## Host-Side Runbook Shape

Use this as a shape for a host operator runbook. Replace placeholders in the
host-owned environment and do not embed the resolved values in the plugin repo.

```text
# Illustrative host-side steps only. Do not run from plugin install.
1. Confirm the GitHub MCP server is registered for the connection reference.
2. Complete the host-owned authentication or authorization flow.
3. Enable only the GitHub MCP adapter tools required by task-management.
4. Confirm the destination reference resolves to the intended task project.
5. Confirm required backend fields exist before any write operation.
6. Record availability evidence for the Adapter Availability Gate.
```

Example availability evidence passed to task-management:

```yaml
adapter_availability:
  backend_key: "github_projects_mcp"
  connection_ref: "github-projects"
  server_registered: true
  credentials_ready: true
  required_tools_enabled:
    - "github-projects:task-create"
  destination_ref: "github-projects:portfolio-os-task-board"
  destination_resolved: true
  required_fields_ready: true
  child_agent_inheritance: "not_unconditional"
```

If any value is false or unknown, the skill should return setup guidance instead
of dispatching an adapter envelope.

## Delegation Guard

If a Hermes profile has `delegation.inherit_mcp_toolsets: true`, state-changing
MCP adapter tools can accidentally flow to child agents. GitHub MCP adapter
tools must not be unconditionally inherited by child agents.

Recommended host policy:

- expose GitHub task write tools only to the commander or task-management flow
  that performs Adapter Dispatch Review
- do not expose those tools by default to review workers, work-unit subagents,
  or generic implementation workers
- pass previews and normalized results to child agents instead of the MCP
  write-capable toolset
- block write availability when the host cannot restrict child-agent
  inheritance for state-changing tools

## Dispatch Reminder

Adapter availability is not approval. A state-changing operation still requires
Adapter Dispatch Review for the exact operation type, adapter tool name,
destination reference, task content, work unit fields, task reference when
present, and expected adapter side effects.
