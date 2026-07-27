---
name: task-management
description: Use when creating, finding, updating, prioritizing, commenting on, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use available GitHub MCP capabilities directly.

## Availability

If Hermes is the host, make this distribution discoverable through its configured
skill root or `skills.external_dirs`, then verify it appears in `hermes skills list`.
Repository compatibility does not prove live availability. This skill describes the
conditional discovery route only; do not install automatically or change a live host
while following the task workflow.

## References

- Read `references/core.md` before resolving the caller's Project or Issue repository.
- Read `references/github-projects.md` before adding an Issue to the Project, changing fields, completing a task, or checking capabilities.
- Read `references/issue-contract.md` before creating an Issue or deciding whether an existing Issue is the same task.
- Read `references/safety-and-failures.md` before any write, destructive operation, bulk change, or recovery from a partial failure.
- Read `references/target-authorization.md` before every write route.

## Boundaries

- Accept `project_url` from the invocation, caller default, or established session context. Do not store a user-specific default in this skill.
- Accept optional `inbox_repository` only for repository-independent or unclassified tasks.
- Keep one canonical default Project per caller. An explicit invocation override applies only to that operation.
- Store every task as a GitHub Issue. The Issue repository is the work unit boundary.
- Use GitHub MCP directly. Do not route GitHub reads or writes through a facade, adapter, provider-neutral schema, CLI, direct API client, browser automation, or local backend. The read-only `portfolio-os task-preflight` command is only the local authority gate; it does not call or wrap GitHub MCP.
- Do not own credentials, MCP registration, Project creation, repository creation, or normal-operation schema repair.

## Operation routing

1. Classify the requested operation before resolving targets or checking capabilities.
2. Resolve only the scope and targets required by that operation through `references/core.md`.
3. For read, search, and list, require only the read capabilities because these routes perform no write.
4. For every bounded write operation, run `portfolio-os task-preflight` for the exact typed target immediately before its first write. A blocked gate means zero writes.
5. After an allowed local gate, perform a separate direct GitHub MCP capability and access check for only that operation, then invoke official GitHub MCP directly.
6. Follow exactly one operation flow below. Combine flows only when the user explicitly requests each operation.

### Read, search, and list

- Resolve only the query scope needed to answer.
- Check only the read and search operation capabilities, then use available GitHub MCP tools directly. Do not require write capabilities for a zero-write request.
- Perform no mutation: never create or edit an Issue, add a comment, close an Issue, add an Issue to a Project, or update a Project field.
- Return only read results, resolved scope, and any ambiguity that prevented an answer. Do not claim completed writes.

### Create and register

Only this operation uses the new-task flow:

1. Determine the requested outcome and observable acceptance criteria.
2. Resolve the Project and Issue repository.
3. Search read-only for an obvious existing Issue and Project item.
4. Reuse a high-confidence match according to `references/issue-contract.md`.
5. If no Issue matches, immediately before Issue creation run `portfolio-os task-preflight --operation task_create` with the exact Work Unit, repository, Project, source profile, and deterministic idempotency identity. A blocked decision returns `confirmation-needed` or `blocked` with zero writes.
6. After an allowed local gate, check only the create operation capabilities through a separate direct GitHub MCP capability and access check for `task_create`. That one gate authorizes the bounded Issue-create plus initial-Project-registration plan for this invocation.
7. Invoke official GitHub MCP directly to create the Issue, read back its exact identity, then continue the initial Project registration under the same `task_create` invocation. Do not run `task_project_register` during this normal successful create flow. Apply `Status=Inbox`, `Priority=P2`, and no due date only to that newly created Project item when the user supplied no value.
8. Reserve `task_project_register` for retry or resume after a previous partial or unknown result. In that recovery path, immediately before the remaining Project write run `portfolio-os task-preflight --operation task_project_register` with the exact existing Issue identity, Project, and explicit partial-resume state; then perform its separate direct GitHub MCP capability and access check and invoke official GitHub MCP directly.
9. For an existing Project item, preserve every Issue and Project item field except an explicitly requested change or documented unfinished write.
10. Return the Issue URL, repository, Project URL, completed steps, preserved state, and unfinished steps.

### Edit

- Immediately before the mutation, run `portfolio-os task-preflight --operation task_update --mutation-kind issue` with the exact Issue identity and one exact `--requested-issue-property title` or `body`. A blocked decision returns `confirmation-needed` or `blocked` with zero writes.
- After an allowed local gate, perform the separate direct GitHub MCP capability and access check for `task_update`, then invoke official GitHub MCP directly.
- Update only the explicitly requested Issue properties, such as title or body.
- Do not add Project membership. Do not apply creation defaults unless the user separately requests a create or register operation.
- Return the edited Issue properties and Issue URL; do not claim unrelated Project writes.

### Comment

- Immediately before the mutation, run `portfolio-os task-preflight --operation task_comment` with the exact Issue identity. A blocked decision returns `confirmation-needed` or `blocked` with zero writes.
- After an allowed local gate, perform the separate direct GitHub MCP capability and access check for `task_comment`, then invoke official GitHub MCP directly.
- Add only the requested comment to the resolved Issue.
- Do not add Project membership. Do not apply creation defaults unless the user separately requests a create or register operation.
- Return the comment result and Issue URL; do not claim unrelated Issue or Project writes.

### Non-terminal field update

- Immediately before the mutation, run `portfolio-os task-preflight --operation task_update --mutation-kind project_field` with the exact Issue identity, Project URL, Project item ID, and allowed field. A blocked decision returns `confirmation-needed` or `blocked` with zero writes.
- After an allowed local gate, perform the separate direct GitHub MCP capability and access check for `task_update`, then invoke official GitHub MCP directly.
- Update only the explicitly requested field values for Status, Priority, or Due date.
- Do not change any unrequested field, add Project membership, or apply creation defaults.
- Return only the requested field results, target item, and any unfinished requested write.

### Terminal update

- Immediately before each remaining terminal-side mutation, run `portfolio-os task-preflight --operation task_complete` with the exact Issue and/or Project item identity, `requested_field=Status` for any Project side, and the matching `normal`, `issue_only`, or `project_only` resume state. A blocked decision returns `confirmation-needed` or `blocked` with zero writes for that side.
- After each allowed local gate, perform the separate direct GitHub MCP capability and access check for the remaining `task_complete` side, then invoke official GitHub MCP directly for only that side.
- Treat an explicit terminal instruction as approval for the Issue close and matching Project Status transition. Do not ask twice.
- Obtain confirmation before an inferred terminal transition.
- Apply the terminal and partial-failure contracts in `references/github-projects.md` and `references/safety-and-failures.md`, then return the result of each side and any unfinished step.

Stop before writing when the Project, repository, task outcome, acceptance criteria, capability, authentication, permission, or schema is not reliable enough to proceed.
