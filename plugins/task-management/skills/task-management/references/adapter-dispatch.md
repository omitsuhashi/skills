# Adapter Dispatch Contract

The adapter-neutral operation envelope is the only write intent accepted by
`task_preflight`. Callers do not select an adapter or provider tool.

## Operation envelope

| Operation | `task_ref` rule | Payload |
| --- | --- | --- |
| `task.create` | must be `null` | one reviewed `task` |
| `task.update` | required opaque backend-owned task reference | non-empty neutral `changes` |
| `task.comment` | required opaque backend-owned task reference | non-empty comment body |
| `task.report` | required opaque backend-owned task reference | structured report + verification |

Every envelope has exact fields:

- `adapter_contract_version: 2`
- `operation_type`
- `backend_key`
- opaque `destination_ref`
- `task_ref`
- operation-specific `payload`

The payload may contain only backend-neutral task fields. Provider coordinates,
raw identifiers, credentials, raw payloads, route/config paths, and adapter/MCP
tool names are rejected.

## Preflight and review guard

`task_preflight(interface_version=2, operation=...)` resolves the host route and
returns a `TaskPreflightResult` with readiness, approval mode, exact
`ApprovalPreview`, and digest. The preview binds:

- the full operation;
- resolved destination label/content target;
- adapter key and route-binding digest;
- ordered expected side effects.

Adapter preflight performs read-only readiness checks. A readiness pass is not
approval and must not replace human review.

Use `decision: approved` only after a human approves the exact preview. Use
`decision: confidence_authorized` only when preflight is ready,
confidence-eligible, and certain. Explicit approval policy, review notes,
adapter uncertainty, or blocked readiness requires the human.

## Apply guard

`task_apply` accepts only interface version 2, the exact preview, and a receipt
containing receipt version 1, decision, and matching operation digest. It reloads
the route and re-preflights before dispatch. Any operation, destination,
route-binding, side-effect, digest, or approval-mode change returns
`approval_mismatch`/`approval_required` with zero adapter apply calls.

After authorization, task-management sends the fixed adapter apply tool the
operation, resolved destination, ordered side effects, and operation digest.
The provider adapter never receives the human receipt and cannot choose its own
approval.

## Result boundary

The adapter result is normalized to `TaskWriteResult`. Partial writes preserve a
safe task reference and are nonretryable. Unknown write outcomes require
inspection. Only an explicit no-write provider failure may be retryable.

Task-management owns no provider client, GraphQL/`gh` fallback, credentials,
schema repair, duplicate store, task ledger, or provider retry loop.
