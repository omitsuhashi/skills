# Task Create Preview Example

This example is review text for a proposed task create operation. It is not an adapter response and it does not prove that a backend write occurred.

## Input Summary

A planning note asks for task-management to define task draft composition rules and show the work unit in review previews.

## Proposed TaskDraft

```yaml
title: "Implement task draft composition guidance"
task_type: "implementation"
work_unit_id: "portfolio-os-task-backend-plugin-skill"
work_unit_name: "Portfolio OS Task Backend Plugin Skill"
due_date: null
urgency: "normal"
importance: "high"
automation_mode: "assistive"
approval_required: true
source_ref:
  kind: "source_trail"
  ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003"
  label: "POTASK-003 source trail"
body: |
  Outcome:
  Define backend-neutral TaskDraft composition guidance for title, body,
  taxonomy fields, work unit display, and review preview expectations.

  Context:
  Task state remains in the selected backend. The task-management skill prepares
  a reviewable draft and does not store raw platform payloads or transport
  metadata in the draft contract.

  Acceptance:
  - Title and body composition rules are referenceable from the skill.
  - Preview shows both work_unit_id and work_unit_name.
  - The inbox fallback is explicit for uncertain routing.
  - Raw platform payloads, platform message ids, and transport metadata are not
    stored in TaskDraft.

  Review:
  Confirm the work unit before adapter dispatch.
fields:
  review_notes:
    - "Routing is inferred from the approved POTASK-003 worker packet."
    - "State-changing adapter dispatch still requires explicit approval."
```

## Human Review Preview

Backend: `github_projects_mcp`
Connection: `github-projects`
Destination: `github-projects:portfolio-os-task-board`
Destination label: `Portfolio OS Tasks`
Operation: `task.create`

Task:

- Title: `Implement task draft composition guidance`
- Type: `implementation`
- Work unit id: `portfolio-os-task-backend-plugin-skill`
- Work unit name: `Portfolio OS Task Backend Plugin Skill`
- Routing key: `work_unit_id`
- Backend display label: `work_unit_name`
- Urgency: `normal`
- Importance: `high`
- Automation mode: `assistive`
- Approval required: `true`
- Source ref: `source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003` (`POTASK-003 source trail`)

Expected adapter side effects after explicit approval:

- Create one task in the selected backend destination.
- Store the task title, body, neutral fields, `work_unit_id`, and `work_unit_name`.
- Return an opaque backend task reference or typed error.

## Adapter Operation Envelope Preview

This envelope is adapter-neutral review input. It is not a backend write and it
must not be passed to an adapter until Adapter Dispatch Review approves the same
operation, tool, and destination.

```yaml
operation_type: "task.create"
backend_key: "github_projects_mcp"
connection_ref: "github-projects"
destination_ref: "github-projects:portfolio-os-task-board"
destination_label: "Portfolio OS Tasks"
adapter_tool_name: "github-projects:task-create"
task:
  title: "Implement task draft composition guidance"
  body: |
    Outcome:
    Define backend-neutral TaskDraft composition guidance for title, body,
    taxonomy fields, work unit display, and review preview expectations.
  fields:
    task_type: "implementation"
    urgency: "normal"
    importance: "high"
    automation_mode: "assistive"
    approval_required: true
    source_ref:
      kind: "source_trail"
      ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003"
      label: "POTASK-003 source trail"
    work_unit_id: "portfolio-os-task-backend-plugin-skill"
    work_unit_name: "Portfolio OS Task Backend Plugin Skill"
    review_notes:
      - "Routing is inferred from the approved POTASK-003 worker packet."
      - "State-changing adapter dispatch still requires explicit approval."
work_unit_id: "portfolio-os-task-backend-plugin-skill"
work_unit_name: "Portfolio OS Task Backend Plugin Skill"
expected_adapter_side_effects:
  - "Create one task in the selected backend destination."
  - "Store the task title, body, neutral fields, work_unit_id, and work_unit_name."
  - "Return an opaque backend task reference or typed error."
adapter_dispatch_review:
  status: "required"
  required_match:
    approved_operation_type: "task.create"
    approved_adapter_tool_name: "github-projects:task-create"
    approved_destination_ref: "github-projects:portfolio-os-task-board"
  instruction: "Do not dispatch until review_status is approved."
```

Adapter Dispatch Review: required. Do not dispatch until review_status is approved.

## Unknown Work Unit Name Preview

Use this fallback when the stable work unit id is known but the backend display label is not.

```yaml
title: "Implement task create preview contract"
task_type: "implementation"
work_unit_id: "portfolio-os-task-backend-plugin-skill"
work_unit_name: "Unknown work unit: portfolio-os-task-backend-plugin-skill"
due_date: null
urgency: "normal"
importance: "high"
automation_mode: "assistive"
approval_required: true
source_ref:
  kind: "source_trail"
  ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-005"
  label: "POTASK-005 source trail"
fields:
  review_notes:
    - "work_unit_id is retained as the stable routing key."
    - "Human review must confirm the backend display label before adapter dispatch."
```

## Inbox Fallback Preview

Use this fallback only when the source is actionable but routing is unclear.

```yaml
title: "Triage task-management follow-up"
task_type: "inbox_triage"
work_unit_id: "inbox"
work_unit_name: "Inbox"
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
    - "work_unit_id uses inbox because caller context did not identify a work unit."
    - "Human review should replace inbox with the correct stable work unit before dispatch when possible."
```
