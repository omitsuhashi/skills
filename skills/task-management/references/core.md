# Core Contract

## Caller input

- `project_url`: URL of the one canonical default Project selected by the caller, or an explicit invocation override.
- `inbox_repository`: optional `OWNER/REPOSITORY` used only when the task is genuinely repository-independent or unclassified.

The skill stores neither value. Caller-owned configuration, invocation context, and established session context supply them.

## Task identity

- A task is a GitHub Issue added to the selected Project through GitHub MCP.
- The repository is the work unit boundary and remains the source of repository ownership.
- Project membership and Project fields remain the source of portfolio workflow state.
- Do not create Project-native draft tasks or duplicate repository identity in a custom field.
