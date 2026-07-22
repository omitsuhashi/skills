---
name: task-management
description: Use when creating, finding, updating, prioritizing, commenting on, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use available GitHub MCP capabilities directly.

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

## Default flow

1. Determine the requested outcome and observable acceptance criteria.
2. Resolve the Project and Issue repository using `references/core.md`.
3. Check the semantic GitHub MCP capabilities required for the operation.
4. Search read-only for an obvious existing Issue before creating a task.
5. Create or reuse the Issue according to `references/issue-contract.md`.
6. Add the Issue to the selected Project and set the requested fields; otherwise use `Status=Inbox`, `Priority=P2`, and no due date.
7. Apply `references/safety-and-failures.md` before mutation and after any partial success.
8. Return the Issue URL, repository, Project URL, completed steps, and unfinished steps.

Stop before writing when the Project, repository, task outcome, acceptance criteria, capability, authentication, permission, or schema is not reliable enough to proceed.
