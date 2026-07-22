# Task Create Preflight Example

This is a review and public-interface example. It does not prove a backend write.

## Proposed TaskDraft

```yaml
title: "Implement task draft composition guidance"
body: |
  Outcome: define backend-neutral TaskDraft composition guidance.
  Acceptance: public preview shows stable and display work-unit values.
work_unit_id: "portfolio-os-task-backend-plugin-skill"
work_unit_name: "Portfolio OS Task Backend Plugin Skill"
task_type: "implementation"
due_date: null
urgency: "normal"
importance: "high"
automation_mode: "assistive"
approval_required: true
source_ref:
  kind: "source_trail"
  ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003"
  label: "POTASK-003 source trail"
fields:
  review_notes:
    - "Human approval is required before apply."
```

Human review summary:

- Backend: `remote_tasks`
- Destination: `tasks:portfolio-os` (`Portfolio OS Tasks`)
- Operation: `task.create`
- Work unit id: `portfolio-os-task-backend-plugin-skill`
- Work unit name: `Portfolio OS Task Backend Plugin Skill`
- Routing key: `work_unit_id`
- Backend display label: `work_unit_name`
- Approval required: `true`

## Public operation

The caller does not include a route path, adapter/MCP tool, GitHub coordinate,
credential, or expected side effect. Those are resolved/returned by the host
route and adapter.

```yaml
interface_version: 2
operation:
  adapter_contract_version: 2
  operation_type: "task.create"
  backend_key: "remote_tasks"
  destination_ref: "tasks:portfolio-os"
  task_ref: null
  payload:
    task:
      title: "Implement task draft composition guidance"
      body: "Define backend-neutral TaskDraft composition guidance."
      work_unit_id: "portfolio-os-task-backend-plugin-skill"
      work_unit_name: "Portfolio OS Task Backend Plugin Skill"
      task_type: "implementation"
      due_date: null
      urgency: "normal"
      importance: "high"
      automation_mode: "assistive"
      approval_required: true
      source_ref:
        kind: "source_trail"
        ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003"
        label: "POTASK-003 source trail"
      fields:
        review_notes:
          - "Human approval is required before apply."
```

Call `task_preflight` first. It returns the exact destination label/content
target, route binding, ordered expected side effects, approval mode, preview,
and digest. Because this task has `approval_required: true`, its approval mode
is `human_required`; a `confidence_authorized` receipt must complete no write.

After a human approves the exact preview, `task_apply` receives:

```yaml
interface_version: 2
approval_preview: "<exact object returned by task_preflight>"
approval_receipt:
  receipt_version: 1
  decision: "approved"
  operation_digest: "<exact approval_digest returned by task_preflight>"
```

`task_apply` reloads the route and re-preflights. Any preview, route, destination,
side-effect, or digest drift returns `approval_mismatch` without adapter apply.

## Result handling

- `created` with a safe opaque task ref: optionally confirm with `task_query`.
- `partial`: inspect the linked task; do not blindly retry.
- `failed` with unknown outcome: determine whether the task exists first.
- `failed` with `retryable: true`: retry only because the provider explicitly
  confirmed no write occurred.

## Unknown work-unit display label

```yaml
work_unit_id: "portfolio-os-task-backend-plugin-skill"
work_unit_name: "Unknown work unit: portfolio-os-task-backend-plugin-skill"
fields:
  review_notes:
    - "Human review must confirm the backend display label before adapter dispatch."
```

## Inbox fallback

Use only when the source is actionable but the stable work unit is unknown:

```yaml
title: "Triage task-management follow-up"
work_unit_id: "inbox"
work_unit_name: "Inbox"
task_type: "inbox_triage"
due_date: null
urgency: "normal"
importance: "normal"
automation_mode: "assistive"
approval_required: true
source_ref:
  kind: "source_summary"
  ref: "source-summary:unrouted-task-management-note"
  label: "Unrouted task-management note"
fields:
  review_notes:
    - "Human review should replace inbox with the correct stable work unit before dispatch when possible."
```
