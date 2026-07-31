---
name: task-management
description: Use when creating, finding, updating, prioritizing, commenting on, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use available GitHub MCP capabilities directly.

## Inputs

- `operation`: one MVP operation: read, search, list, create, register, title/body
  edit, comment, Status/Priority/Due date update, Done/Cancelled, or reopen.
- `project_url`: optional caller-selected Project URL. When omitted, resolve the
  caller default or established session Project through `references/core.md`.
- `inbox_repository`: optional caller-owned repository for genuinely
  repository-independent or unclassified create operations. It has no skill-owned
  default.
- Operation payload: the target Issue or query, requested mutation values, and
  optional Status filter. A bare reopen defaults only its target Status to
  `Backlog`.
- `resume_continuation_state`: optional single runtime-held value returned by a
  prior operation in the same trusted caller/runtime execution context, as
  defined in `references/github-projects.md`. It contains the opaque provider
  continuation, non-secret reconciliation checkpoint, and their accidental-mix
  association. A new traversal omits it. Never accept a separately supplied
  cursor/checkpoint or user-/artifact-reconstructed state.

## Outputs

- A result envelope with the resolved target and one of `complete`, `partial`,
  or `blocked`.
- Read/list results include counts, conflicts, display truncation, stop reason,
  opaque continuation, and one lossless caller-held `ContinuationState`.
- Mutation results include requested-field and protected-native-metadata exact
  readback, completed sides, remaining sides, and recovery instructions.
- A `partial` or `blocked` result identifies missing semantic capability,
  permission, schema, identity, or readback evidence. Recovery resumes only
  unfinished work and never guesses a target or silently changes transport.
- An invalid or untrusted continuation returns `blocked`,
  `create_allowed=false`, and restart-from-source guidance; it is never raised
  as a portable caller exception.

## Required Capabilities

- Resolve semantic GitHub Issue, Project-item, field, search/list, and write
  capabilities operation-scoped through the matrices in
  `references/github-projects.md`.
- Exact readback of every requested mutation and protected native metadata;
  retries require readback plus only the remaining-side write capabilities.
- Preserve opaque provider continuation and runtime-held reconciliation state
  as one `ContinuationState` inside the same trusted execution context, without
  storing credentials, secrets, or authentication-token values.
- Fail closed when identity, target membership, capability, permission, schema,
  or exact readback is ambiguous. Exact live tool names are runtime-resolved and
  are not part of this portable contract.

## References

- Read `references/core.md` before resolving the caller's Project or Issue repository.
- Read `references/github-projects.md` before adding an Issue to the Project, changing fields, completing a task, or checking capabilities.
- Read `references/issue-contract.md` before creating an Issue or deciding whether an existing Issue is the same task.
- Read `references/safety-and-failures.md` before any write, destructive operation, bulk change, or recovery from a partial failure.

## Boundaries

- Accept `project_url` from the invocation, caller default, or established session context. Do not store a user-specific default in this skill.
- Accept optional `inbox_repository` only for repository-independent or unclassified tasks.
- Keep one canonical default Project per caller. An explicit invocation override applies only to that operation.
- Store every task as a GitHub Issue. The Issue repository is the work unit boundary.
- Use GitHub MCP directly. Do not route through a facade, adapter, provider-neutral schema, CLI, direct API client, browser automation, or local backend.
- Do not own credentials, MCP registration, Project creation, repository creation, or normal-operation schema repair.
- Native metadata may be read, but the MVP never writes assignees, labels, milestone, Issue type, or parent/sub-issue relationships. Preserve it across every supported mutation and exact-read it back with the requested result.

## Operation routing

1. Classify the requested operation before resolving targets or checking capabilities.
2. Resolve only the scope and targets required by that operation through `references/core.md`.
3. For read, search, and list, require only the read capabilities because these routes perform no write.
4. For every operation, complete the operation-scoped capability and target-permission preflight in `references/github-projects.md` before mutation.
5. Follow exactly one operation flow below. Combine flows only when the user explicitly requests each operation.
6. If one canonical task has multiple Project-item memberships, all Project
   field, terminal, and reopen writes stop until exact readback proves one
   canonical Project-item identity. Return every conflicting membership; never
   choose by order, title, or mutable display fields.

### Read, search, and list

- Resolve only the query scope needed to answer.
- Require only Issue read/search and Project read capabilities. Do not require write capabilities for a zero-write request.
- Normalize a requested Status and apply the completeness envelope in `references/github-projects.md`. A result is complete only when raw source exhaustion is confirmed; otherwise preserve fetched results and report the partial stop.
- Treat duplicate discovery and any request that depends on all matching tasks as completeness-required. Keep its display/return buffer at 50 items while continuing the investigation across opaque provider continuations until source exhaustion or an explicit partial stop.
- Perform no mutation: never create or edit an Issue, add a comment, close an Issue, add an Issue to a Project, or update a Project field.
- Return only read results, resolved scope, and any ambiguity that prevented an answer. Do not claim completed writes.

### Create and register

Only this operation uses the new-task flow:

1. Determine the requested outcome and observable acceptance criteria.
2. Resolve the Project and Issue repository.
3. Search read-only for an obvious existing Issue and Project item through a completeness-required duplicate discovery. Stop creation unless aggregate discovery reaches source exhaustion with outcome `none`.
4. Reuse only an exhausted discovery's `unique_high_confidence` match according to `references/issue-contract.md`; stop on `ambiguous_or_multiple`.
5. Before mutation, use the `create` preflight when creating an Issue or the `register_existing_issue` preflight when registering an existing Issue.
6. If no Issue matches, create it. If the Issue is not yet in the selected Project, add it and apply `Status=Inbox`, `Priority=P2`, and no due date only to that newly created Project item when the user supplied no value.
7. For an existing Project item, preserve every Issue and Project item field except an explicitly requested change or documented unfinished write.
8. When registering an existing Issue, change only Project membership and explicitly requested Project fields or applicable defaults; preserve and exact-read back the Issue's native metadata.
9. Return the Issue URL, repository, Project URL, completed steps, preserved state, and unfinished steps.

### Edit

- Complete the `title_body_edit` operation-scoped preflight in `references/github-projects.md` before mutation.
- Update only the explicitly requested Issue properties, such as title or body.
- Do not add Project membership. Do not apply creation defaults unless the user separately requests a create or register operation.
- Return the edited Issue properties and Issue URL; do not claim unrelated Project writes.

### Comment

- Complete the `comment` operation-scoped preflight in `references/github-projects.md` before mutation.
- Add only the requested comment to the resolved Issue.
- Do not add Project membership. Do not apply creation defaults unless the user separately requests a create or register operation.
- Return the comment result and Issue URL; do not claim unrelated Issue or Project writes.

### Non-terminal field update

- Complete the `status_priority_due_date` operation-scoped preflight in `references/github-projects.md` before mutation.
- Update only the explicitly requested field values for Status, Priority, or Due date.
- Do not change any unrequested field, add Project membership, or apply creation defaults.
- Return only the requested field results, target item, and any unfinished requested write.

### Terminal update

- Complete the `done_cancelled` operation-scoped preflight in `references/github-projects.md` before mutation.
- Treat an explicit terminal instruction as approval for the Issue close and matching Project Status transition. Do not ask twice.
- Obtain confirmation before an inferred terminal transition.
- Apply the terminal and partial-failure contracts in `references/github-projects.md` and `references/safety-and-failures.md`, then return the result of each side and any unfinished step.

### Reopen

- Complete the `reopen` operation-scoped preflight in `references/github-projects.md` before mutation.
- Use the user's explicit non-terminal Status target. For a bare reopen, use `Backlog`.
- Read both current sides first, apply the reopen state machine, and return each side's exact readback, result, and remaining work.

Stop before writing when the Project, repository, task outcome, acceptance criteria, capability, authentication, permission, or schema is not reliable enough to proceed.
