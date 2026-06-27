# Backend Contract

## Concepts

- `TaskDraft`: Proposed task before an external write. It may include proposed fields such as due date or urgency, but it is not task state.
- `TaskRef`: Stable public reference returned after backend registration. It must link back to the backend without exposing provider-private IDs.
- `TaskQuery`: Backend-neutral filters for retrieval, including work unit, due date, status, urgency, importance, automation mode, and assignee when available.
- `TaskSnapshot`: Read-only backend view. Treat status, due date, assignee, task body, priority, and project fields as backend-owned state.
- `TaskWriteResult`: Result of create, update, or comment operations.
- `TaskBackendAdapter`: Adapter interface for create, read, query, update, and progress comments.

## Field Rules

Allowed backend-neutral task fields are:

- `title`
- `body`
- `work_unit_id`
- `task_type`
- `due_date`
- `status`
- `urgency`
- `importance`
- `automation_mode`
- `approval_required`
- `source_ref`
- `assignee`

Reject provider-specific field names such as GraphQL IDs, project field IDs, option IDs, repository IDs, auth tokens, raw platform payloads, or transport message IDs at the public contract boundary.

## Local Persistence Rule

Callers may persist source trail, routing rationale, task drafts before approval, backend `TaskRef` values after creation, recommendation logs, and final work reports. They must not persist backend task state as a competing source of truth.

## Fallback Work Unit

Use `inbox` as the default fallback `work_unit_id` when a task is approved before routing is known. Prefer an explicit real work unit when available.
