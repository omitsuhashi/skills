# Hermes MCP Governance

Hermes/the MCP host owns plugin installation, route/config placement, MCP server
registration, credentials, permissions, profile edits, tool enablement, and
delegation. Repository validation owns none of those live changes.

## Exposure boundary

For the GitHub adapter, host attestation must state:

- raw GitHub MCP tools are `adapter_only`;
- adapter write tools are `task_management_only`;
- required Project, Issue-write, and comment-write toolsets are enabled.

The model/child agent receives only task-management public tools. It must never
receive raw MCP tool names or adapter apply directly. If the host cannot prevent
state-changing tool inheritance, write readiness is blocked.

## Approval boundary

Tool availability and successful preflight are readiness evidence, not write
approval. The exact preview/digest still requires human approval unless
preflight is simultaneously ready, confidence-eligible, and certain. Any
uncertainty, explicit approval policy, review note, route drift, destination
drift, or side-effect drift returns to the human.

## Credential boundary

Credentials stay in the host-managed MCP connection. Do not put them in plugin
config, route files, task drafts, operation envelopes, examples, results, logs,
or knowledge docs. Use only opaque public destination/content/task references.

## Live activation gate

An approved live activation workflow must separately verify:

1. both plugin versions and enabled state;
2. host route/config location and matching opaque refs;
3. GitHub MCP registration, auth, permission, and exact tool availability;
4. delegation exposure policy;
5. preflight against the intended destination;
6. explicit approval before any real mutation;
7. post-write public readback and audit evidence.

Installing or testing this repository does not perform any of these actions.
