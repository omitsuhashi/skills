# Core Contract

## Caller input

- `project_url`: URL of the one canonical default Project selected by the caller, or an explicit invocation override.
- `inbox_repository`: optional `OWNER/REPOSITORY` used only when the task is genuinely repository-independent or unclassified.

The skill stores neither value. Caller-owned configuration, invocation context, and established session context supply them. An invocation override never changes the caller default and never enables automatic routing across multiple Projects.

## Project resolution order

1. Invocation `project_url`.
2. Caller default `project_url`.
3. Session-established Project.
4. Unique open Project discovery through a read-only GitHub MCP capability, only when no owner, visibility, closed-state, or template conflict exists.
5. Ask the user when more than one candidate remains or the authenticated owner is unclear.

Accept personal `/users/<owner>/projects/<number>` and organization `/orgs/<owner>/projects/<number>` URLs. Interpret the owner-scoped number only when an MCP operation requires it. Never select a state-changing target from title or recency alone, and never substitute another Project after an invalid URL or permission failure.

## Repository resolution order

1. Explicit repository from the user.
2. Current repository when the task directly concerns that repository.
3. Unique referenced repository derived from one Issue, PR, durable specification, or code target.
4. Configured inbox when the task is repository-independent or deliberately unclassified.
5. Ask the user when repositories conflict or attribution remains uncertain.

Never use inbox as an ambiguity fallback. The repository is the work unit boundary. GitHub's repository metadata is the grouping key; do not duplicate it in a custom Project field.

## Read and write identity

- A task is a GitHub Issue added to the selected Project through GitHub MCP.
- Issue title and body are the source of task content.
- Project membership, Status, Priority, and Due date are the source of portfolio workflow state.
- One operation targets one resolved Project and one resolved Issue repository.
