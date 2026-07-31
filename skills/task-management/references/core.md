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

## Canonical identity

Determine `canonical_task_identity` by the first available value in this order:

1. The provider's stable Issue ID.
2. The canonical Issue URL.
3. The normalized `owner/repository#number` key.

Normalize an Issue URL to
`https://github.com/<casefold(owner)>/<casefold(repository)>/issues/<decimal-number>`
after resolving provider-declared canonical redirects. Require the `github.com`
host and exact Issue path shape; remove query, fragment, and trailing slash.
Owner and repository comparison is case-insensitive and the stored identity uses
their casefold form. Normalize the Issue number as its decimal integer
representation, so `0007` and `7` identify the same Issue. Apply the same
casefold and decimal rules to the `owner/repository#number` fallback key.
Display casing is not identity.

Determine `canonical_project_item_identity` from the provider's stable item ID. Only when that ID is unavailable, use the tuple `(canonical_project_url, canonical_task_identity)`. Normalize the Project URL to its canonical `/users/<owner>/projects/<number>` or `/orgs/<owner>/projects/<number>` form after removing query, fragment, and trailing slash. Never use a title, mutable field, page position, or fetch order as identity.

If required components are missing, malformed, or contradictory and no unique
canonical identity can be proven, isolate the observation as `partial`. Do not
deduplicate by title or mutable display fields, and do not write by title,
mutable display fields, page position, or fetch order. Exact identity readback
is required before the observation can enter a unique match or mutation target.
