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
- Read `references/operation-readback-state-machine.toml` before every write or partial retry. Treat its semantic `read_before -> write -> read_after -> observed` transitions as the required direct-tool call order.

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
4. Before a write route, classify its guard outcome. Only the declared `eligible`, `explicit`, or `inferred` outcomes may continue. `blocked`, `ambiguous`, `duplicate`, `bulk`, `destructive`, `confirmation-needed`, a missing outcome, or any unknown guard outcome means zero writes.
5. For every bounded write operation, run `portfolio-os task-preflight` for the exact typed target immediately before its first write. A blocked gate means zero writes.
6. After an allowed local gate, perform a separate direct GitHub MCP capability and access check for only that operation and, for a partial terminal retry, only the remaining side. Then invoke official GitHub MCP directly.
7. For each mutation, call the named official GitHub MCP write directly, then perform its named `read_after` through official GitHub MCP and evaluate the named `observed` condition. A write acknowledgment or search match alone is never success.
8. On an unknown Issue-create result, search the exact idempotency marker. Continue only when one match resolves its Issue number or node ID, then read that exact Issue and validate repository, marker, and identity. Zero or multiple matches fail closed without a retry. For other unknown writes, read back the exact target before retrying and never repeat an observed write.
9. Return success only from the operation's final observed remote state. On partial success, resume only unfinished transitions and preserve every already-observed Issue, Project item, and field.
10. Follow exactly one operation flow below. Combine flows only when the user explicitly requests each operation.

### Read, search, and list

- Resolve only the query scope needed to answer.
- Check only the read and search operation capabilities, then use available GitHub MCP tools directly. Do not require write capabilities for a zero-write request.
- Perform no mutation: never create or edit an Issue, add a comment, close an Issue, add an Issue to a Project, or update a Project field.
- Return only read results, resolved scope, and any ambiguity that prevented an answer. Do not claim completed writes.

### Create and register

Only this operation uses the new-task flow:

1. Determine the requested outcome and observable acceptance criteria.
2. Resolve the Project and Issue repository.
3. Search the exact idempotency marker read-only before title similarity. Zero matches may continue; multiple matches are `ambiguous`.
4. For normal `task_create`, one matching existing Issue is `duplicate` and returns that Issue with zero writes, whether or not it already belongs to the selected Project. Do not use normal create as an implicit registration route.
5. When no Issue matches, immediately before Issue creation run `portfolio-os task-preflight --operation task_create` with the exact Work Unit, repository, Project, deterministic idempotency identity, and guard outcome. The command derives profile and instance authority from the Hermes host context; do not pass identity or root overrides. A blocked decision returns `confirmation-needed` or `blocked` with zero writes.
6. After an allowed local gate, check only the create operation capabilities through a separate direct GitHub MCP capability and access check for `task_create`. That one gate authorizes the bounded Issue-create plus initial-Project-registration plan for this invocation.
7. Invoke official GitHub MCP directly to create the Issue, establish its exact number or node ID, and validate an exact Issue read before continuing. Then add it to the Project under the same `task_create` invocation. Do not run `task_project_register` during this normal successful create flow.
8. Apply initial Project fields only to a newly created Project item that was added in this invocation. Honor an explicit `Status`, `Priority`, or `Due date`; otherwise use `Status=Inbox`, `Priority=P2`, and no due date. If the item already exists, preserve all its fields.
9. Reserve `task_project_register` for retry or resume backed by an exact prior partial receipt from `task_create`. The receipt must bind repository, Project URL, idempotency marker, existing Issue number or node ID, and unfinished state. A boolean resume flag is insufficient. Immediately before the remaining Project write, run its local gate and a separate direct GitHub MCP capability/access check that does not require Issue-create capability.
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
