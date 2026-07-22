# GitHub Projects Adapter Route

`task-adapter-github-projects` is the separate external adapter route for GitHub
Projects. The GitHub MCP Server owns authenticated provider operations; the
adapter owns provider mapping; task-management owns the backend-neutral public
interface and approval binding.

## Fixed tools

The host route binds exactly:

- `task_adapter__github_projects__task_query`
- `task_adapter__github_projects__task_preflight`
- `task_adapter__github_projects__task_apply`

The adapter config then binds exact allowlisted GitHub MCP public tools and maps
opaque `destination_ref`/`content_target_ref` values to adapter-private GitHub
coordinates and canonical fields. Those details never enter task-management
model input or output.

## Adapter Availability Gate

This is a readiness check (also called a Live Root Gate in some workflows), not
write approval. It confirms host config, tool availability, auth/permission,
destination, field mapping, read capability, and safe delegation. A pass means
only that an already approved operation is executable; it does not permit
unapproved remote writes.

Root mismatch, `tool_disabled`, `auth_missing`, `permission_failure`,
`destination_unresolved`, `required_field_missing`, `field_type_mismatch`,
`capability_mismatch`, or unsafe delegation is a setup blocker. No fallback
client is attempted.

## Linked-Issue behavior

- Create writes one GitHub Issue through the configured opaque content target,
  attaches it to the Project, updates canonical fields, then reads back the
  Project item.
- Update changes linked Issue content and/or reviewed Project fields.
- Comment and report add content to the linked Issue and read back safe task
  identity.
- Project-native draft items and caller-selected content policy are not part of
  this adapter.

Public `task_ref` has exactly `backend_key`, opaque `task_ref.task_ref`, optional
safe `task_ref.task_url`, and title. Consumers never parse it for provider IDs.

## Partial and retry safety

- Failure after a confirmed write returns nonretryable `partial` with a safe
  task reference and inspection action.
- An unconfirmed first-write outcome is nonretryable and requires the human to
  determine whether the linked task exists.
- A rate-limit failure is retryable only when the provider explicitly states
  that no write occurred.
- Raw provider errors, IDs, payloads, credentials, and ambiguous public MCP
  envelopes fail closed.

## Test and live boundary

Repository tests connect both plugin public entrypoints to a fake GitHub MCP
boundary and prove query, preflight, approval, apply, readback, zero-write
guards, partial safety, and explicit no-write retry. They do not contact GitHub.

Plugin install must not register MCP servers, configure credentials, edit live
profiles, enable tools, or mutate GitHub. Repository completion is not live
activation; a separate gate is required.
