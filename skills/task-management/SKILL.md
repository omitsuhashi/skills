---
name: task-management
description: Use when turning chat or capture text into backend-neutral task drafts, reviewing tasks before external writes, or working with task backends such as GitHub Projects without leaking provider-specific IDs or task state into application core.
---

# Task Management

## Overview

Use this skill to prepare, review, and register tasks through a backend-neutral contract. The first backend target is GitHub Projects, but the skill must keep task state in the backend and keep provider-specific details inside the adapter layer.

## Workflow

1. Normalize the user's chat, capture, or source note into a `TaskDraft`.
2. Resolve or infer `work_unit_id`. If there is no better value, use `inbox`.
3. Infer `task_type`, `due_date`, `urgency`, `importance`, `automation_mode`, and `approval_required` when the source supports it.
4. Present human-review text before any external create, update, or comment.
5. After approval, call the configured backend adapter and store only the returned `TaskRef` plus source trail or rationale in the caller's local system.
6. Read or query backend tasks through `TaskQuery` and treat returned task fields as a read-only `TaskSnapshot` unless the user approved an explicit adapter update.

## Hard Boundaries

- Do not create a local task ledger or treat local files as the source of truth for task status.
- Do not persist GitHub GraphQL IDs, project field IDs, status option IDs, repository IDs, raw message IDs, or provider auth in the caller's core system.
- Do not perform live external writes without explicit user approval or an already-approved governance policy.
- Do not add Portfolio OS profile-specific capture behavior here. Profile-local skills may hand off a normalized source trail to this skill.
- Do not make GitHub Projects the permanent architecture. Treat it as the first adapter.

## Router

- For task concepts and Python contract objects, read `references/backend-contract.md`.
- For GitHub Projects mapping, fixture adapter behavior, and future live adapter boundaries, read `references/github-projects.md`.
- For approval and automation policy, read `references/governance.md`.
- For backend migration or export discussion, read `references/migration.md`.

## Bundled Helpers

- `scripts/task_backend.py` defines `TaskDraft`, `TaskRef`, `TaskQuery`, `TaskSnapshot`, `TaskWriteResult`, and `TaskBackendAdapter`.
- `scripts/task_draft.py` provides deterministic draft normalization helpers for simple capture text.
- `scripts/github_projects_adapter.py` provides a GitHub Projects config shape and an in-memory fixture adapter for tests and dry runs. It intentionally does not perform live GitHub API calls.

Use the scripts as contract examples or fixture utilities. A live GitHub adapter may be added later behind explicit auth and approval handling.
