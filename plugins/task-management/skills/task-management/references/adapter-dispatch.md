# Adapter Dispatch Contract

This reference defines the adapter-neutral operation envelope that the
task-management skill may prepare after TaskDraft review. The envelope is a
review and dispatch boundary only; the selected external adapter owns actual
backend writes and backend-specific result details.

## Operation Envelope

An adapter-neutral operation envelope can represent these intent types:

| Operation type | Intent |
| --- | --- |
| `task.create` | Create a task from a reviewed TaskDraft. |
| `task.update` | Update fields or body content for an existing backend task reference identified by `task_ref`. |
| `task.comment` | Add a comment or human-readable progress note to an existing backend task reference identified by `task_ref`. |
| `task.report` | Attach or publish a work report summary to an existing backend task reference identified by `task_ref`. |

The envelope surface uses these fields before it is eligible for Adapter
Dispatch Review. Operation-specific requiredness is part of each field contract:

| Field | Contract |
| --- | --- |
| `backend_key` | Backend route key, for example `github_projects_mcp`. |
| `connection_ref` | Opaque host or profile connection reference. It is not a credential. |
| `destination_ref` | Opaque backend destination reference supplied by caller, profile, or host registration. |
| `destination_label` | Human-readable destination label shown in preview. |
| `operation_type` | One of `task.create`, `task.update`, `task.comment`, or `task.report`. |
| `task.title` | Reviewed task title, when the operation creates or updates task content. |
| `task.body` | Reviewed task body or operation body. |
| `task.fields` | Backend-neutral fields such as task type, urgency, importance, approval requirement, source ref, and work unit values. |
| `work_unit_id` | Stable routing key copied into task fields. |
| `work_unit_name` | Backend display label copied into task fields for human scanning. |
| `task_ref` | opaque backend-owned task reference; required for `task.update`, `task.comment`, and `task.report`. |
| `adapter_tool_name` | Host-provided adapter tool or route surface name. |
| `expected_adapter_side_effects` | Human-readable list of side effects expected after explicit approval. |

`task.fields` must stay backend-neutral. Do not place GitHub node IDs, field IDs,
repository IDs, auth material, raw platform payloads, or transport metadata in
the envelope. If a target-specific identifier is required, pass an opaque
backend-owned reference such as `destination_ref` or an existing `task_ref`.
`task_ref` is required for `task.update`, `task.comment`, and `task.report`
because those operations mutate or annotate an existing backend task. It is
omitted from `task.create` unless an external adapter explicitly supplied a
backend-owned reference for a prior object.

## Adapter Dispatch Review Guard

Do not pass an envelope to an adapter until Adapter Dispatch Review is complete.

The review check must confirm:

- `review_status: approved`
- `approved_operation_type` matches `operation_type`
- `approved_adapter_tool_name` matches `adapter_tool_name`
- `approved_destination_ref` matches `destination_ref`
- `approved_task_ref` matches `task_ref` for update, comment, and report
  envelopes
- the reviewer has seen `backend_key`, `connection_ref`, `destination_ref`,
  `destination_label`, `operation_type`, task title/body/fields,
  `work_unit_id`, `work_unit_name`, `task_ref` when present, and
  `expected_adapter_side_effects`

If any value is missing or changed after review, stop and present a new Adapter
Dispatch Review preview. Approval for one envelope does not approve a later
create, update, comment, report, batch, or policy-gated operation.

## Non-Ownership Boundary

The task-management plugin does not define external adapter write policy,
GitHub mutation sequence, backend retry semantics, backend API clients, `gh`
planners, GraphQL clients, schema repair, duplicate-prevention stores,
`task_sha`, or local task ledgers.

The adapter may decide how to create a GitHub issue, create a project-native
draft item, update fields, attach a comment, publish a report, retry a backend
call, or return typed errors. The task-management skill only prepares the
reviewed envelope and normalizes the adapter result boundary described by the
surrounding task contract.
