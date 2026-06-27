# GitHub Projects Adapter

## Scope

GitHub Projects is the first adapter, not the permanent task architecture. Keep GitHub-specific API calls, auth, rate-limit handling, duplicate detection, field mapping, and error translation inside the adapter.

The bundled `InMemoryGitHubProjectsAdapter` is a dry-run and test fixture. It does not call GitHub and should be safe for normal tests.

## Config Shape

The config should identify:

- GitHub owner or organization
- Project number
- Optional repository for task URLs or issue-backed tasks
- Default work unit fallback, normally `inbox`
- Backend-neutral field mapping by field name, not by GitHub IDs

Do not expose GraphQL IDs, project field IDs, status option IDs, repository IDs, or auth details to callers.

## Recommended Fields

- `work_unit_id` is required. Use `inbox` when routing is unknown.
- `task_type`
- `due_date`
- `urgency`
- `importance`
- `automation_mode`
- `approval_required`
- `source_ref`

The adapter owns the mapping from these names to GitHub Projects fields.

## Live Adapter Boundary

A future live adapter may validate that required fields exist or create them only when a governance policy explicitly allows schema mutation. Live create, update, and comment operations require explicit approval unless the caller has a pre-approved trusted automation policy.
