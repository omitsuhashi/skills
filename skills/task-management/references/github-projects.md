# GitHub Projects Contract

## Semantic capability check

Resolve the requested operation first. Before it runs, require its exact read and write semantic capabilities. Require access only to the targets resolved by that operation. This includes relevant private content. Read-only operations have `none` for their write requirement and perform no write. If a required capability or target permission is missing, stop before mutation and report the missing capability.

## Operation capability matrix

| Operation | Required read capabilities | Required write capabilities |
| --- | --- | --- |
| read | `target_issue_or_project_item_read` | none |
| search | `issue_search`, `project_item_read`, `project_item_list` | none |
| status_filtered_list | `project_item_read`, `project_item_list`, `status_field_read` | none |
| create | `duplicate_discovery`, `target_repository_read`, `target_project_read`, `project_schema_read` | `issue_create`, `project_item_add`, `requested_field_update` |
| register_existing_issue | `issue_read`, `duplicate_membership_discovery`, `target_project_read`, `project_schema_read` | `project_item_add`, `requested_field_update` |
| title_body_edit | `issue_read` | `issue_title_body_update` |
| comment | `issue_read` | `issue_comment_create` |
| status_priority_due_date | `project_item_read`, `requested_field_read` | `requested_field_update` |
| done_cancelled | `issue_state_reason_read`, `project_status_read` | `issue_close`, `project_status_update` |
| reopen | `issue_state_read`, `project_status_read` | `issue_reopen`, `project_status_update` |

## Retry side capability matrix

| Remaining side | Required write capabilities |
| --- | --- |
| issue_create | `issue_create` |
| project_item_add | `project_item_add` |
| requested_fields | `requested_field_update` |
| issue_terminal | `issue_close` |
| project_status | `project_status_update` |
| issue_reopen | `issue_reopen` |

For a partial-failure retry, exact-read the current sides first. Then check only the operation's read set plus the write capabilities for the named remaining sides; do not require completed-side writes again.

Tool names may differ by host integration. Match semantic capabilities, but use only GitHub MCP. Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Project item model

- Create or reuse a GitHub Issue before adding it to the Project.
- Do not use a Project-native draft item as the task source of truth.
- Keep completed and cancelled items in the Project for history.
- Do not create a Project, repository, field, option, view, or workflow as a side effect of normal task operations.

## Fields

`Status` options:

- `Inbox`: untriaged.
- `Backlog`: accepted but unscheduled.
- `Ready`: actionable.
- `In progress`: active work.
- `Blocked`: waiting on an external condition.
- `Done`: completed.
- `Cancelled`: intentionally not completed.

`Priority` options:

- `P0`: immediate.
- `P1`: high.
- `P2`: normal and the default only for a newly created Project item in a create or register operation when unspecified.
- `P3`: low.

`Due date` is optional. Leave it empty when no reliable deadline exists. Use GitHub-native repository, assignee, label, milestone, Issue type, and parent/sub-issue information instead of duplicate custom fields.

Creation defaults are `Status=Inbox`, `Priority=P2`, and no due date. Apply them only when create or register adds a newly created Project item. Never apply them to read, search, list, edit, comment, field-update, or terminal-update operations, and never reset an existing Project item's fields to these defaults.

## Terminal transitions

- `Done` maps to Issue close reason `completed`.
- `Cancelled` maps to Issue close reason `not planned`.
- Treat the Project Status and Issue close as one logical transition.
- Keep the item in the Project; do not remove or archive it.
- When an externally closed Issue has a reliable close reason, reconcile the Project Status as a safe non-destructive update.
- If only one side succeeds, report the mismatch. Continue only the unfinished steps after applying the safety contract.

## Setup boundary

If fields or options are missing, stop normal task writing and report the exact schema difference. Create or repair schema only in a separately requested setup operation with confirmed GitHub MCP capability and permission. Never silently remap a field by a similar name.
