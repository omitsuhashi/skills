# GitHub Projects Contract

## Semantic capability check

Check only the semantic capabilities required by the requested operation before mutation:

| operation | required capabilities |
|---|---|
| read / search | Issue read / search; Project read only when requested |
| `task_create` | Issue read / search / create; Project read / item add / initial Status and Priority update; Due date update only when supplied |
| `task_project_register` | Exact Issue read; Project read / item add / initial field update |
| `task_update` with `mutation_kind=issue` | Exact Issue read / requested Issue update |
| `task_update` with `mutation_kind=project_field` | Exact Issue and Project item read / requested Project field update |
| `task_comment` | Exact Issue read / comment create |
| `task_complete` with `resume_state=normal` | Exact Issue and Project item read / Issue close / terminal Project Status update |
| `task_complete` with `resume_state=issue_only` | Exact Issue read / Issue close |
| `task_complete` with `resume_state=project_only` | Exact Project item read / terminal Project Status update |

The GitHub MCP capability inventory is Issue read, search, create, update, and comment; and Project read, item add, and field update. `task_create` requires Issue read, search, and create; Project read, item add, and creation-default field update. Access to the resolved repository and Project is also required. `task_project_register` starts from its exact prior partial receipt and does not require Issue create. A terminal resume requires only the remaining side and does not inherit the other side's mutation capability. For every operation, stop before mutation and report the missing capability or target access.

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
