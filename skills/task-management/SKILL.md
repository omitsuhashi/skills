---
name: task-management
description: Use when creating, finding, updating, prioritizing, or completing GitHub Issue-backed tasks collected in one caller-selected GitHub Project through GitHub MCP.
---

# Task Management

Manage task content as GitHub Issues and portfolio state as Project items. Use GitHub MCP directly.

## References

- Read `references/core.md` before resolving the caller's Project or the Issue repository.

## Required boundary

- Accept `project_url` from the invocation, caller default, or established session context.
- Accept optional `inbox_repository` only for repository-independent or unclassified tasks.
- Each caller normally supplies one canonical default Project. An explicit invocation override applies only to that operation.
- Store each task as a GitHub Issue. The Issue repository is the work unit boundary.
- Stop when the target cannot be resolved confidently. Do not invent a destination.
