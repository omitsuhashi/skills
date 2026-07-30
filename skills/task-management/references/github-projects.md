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

## Status normalization

| Canonical Status | Accepted user wording |
| --- | --- |
| `Inbox` | `Inbox`, `受信箱`, `未整理` |
| `Backlog` | `Backlog`, `バックログ`, `実施候補` |
| `Ready` | `Ready`, `着手可能`, `準備完了` |
| `In progress` | `In progress`, `進行中`, `着手中`, `対応中` |
| `Blocked` | `Blocked`, `ブロック中`, `停止中` |
| `Done` | `Done`, `完了`, `終了` |
| `Cancelled` | `Cancelled`, `Canceled`, `中止`, `キャンセル` |

Normalize user wording to one canonical Status before comparing it with the
Project schema. Do not guess between multiple Status values. A missing option,
duplicate option, or other schema ambiguity must stop the operation as a schema
mismatch before any write or filtered result claim.

## Page reconciliation and unique matching

Reconcile observations by `canonical_project_item_identity`, then match and return each `canonical_task_identity` once. Process pages and observations in provider order, and retain the stable first-valid observation order for returned tasks.

For a repeated Project item:

- Count every observation after the first as deduplicated.
- If its task identity changes, isolate that item as an identity conflict. Do not choose either task identity or return the item.
- Merge `Status` and `Priority` independently. A field that is missing or ordinary `null` preserves the last known value. Clear a value only when the provider explicitly declares that field in an explicit-clear signal.
- When both the old and new non-null values have timestamps, the newest timestamp wins; equal timestamps use the later provider observation.
- When conflicting non-null values cannot be ordered because a timestamp is missing, isolate that item as a reconciliation conflict instead of guessing.

Apply the requested filter only after reconciliation. Exclude isolated item conflicts. If multiple valid Project items resolve to the same task, return the canonical task once in its first-valid order, count an identity conflict, and mark the result partial. Other unambiguous results remain usable. A same-item/different-task conflict or reconciliation conflict likewise marks the result partial without discarding unrelated results.

The result envelope reports `raw_observation_count`, `deduplicated_observation_count`, `identity_conflict_count`, `reconciliation_conflict_count`, `unique_task_count`, `returned_count`, `task_order`, `completeness`, `truncated`, `continuation`, and `stop_reason`. `raw_observation_count` counts all raw observations fetched and inspected during the call, including observations in an overshoot page that is deferred rather than committed.

## Lossless unique-50 continuation

For a standard display call, the maximum is 50 unique matching tasks per call.
Reconcile each whole page atomically against a candidate copy of the prior
state:

- If accepting the whole page yields fewer than 50 unique matches, commit it and continue when the provider has another page.
- If accepting it yields exactly 50, commit it and stop with `unique_limit_reached`.
- If accepting it would exceed 50, do not consume or commit any part of that page. Return the page's unchanged provider-supplied incoming cursor, the reconciliation state from before that page, and `unique_limit_page_deferred`, even though this can return fewer than 50 tasks.

`ContinuationState` contains the opaque `provider_cursor` unchanged plus the exact `already_emitted_task_identities`. The resumed call supplies that incoming cursor and identity set, suppresses already emitted canonical tasks, and may then reconcile the formerly deferred whole page. It must not synthesize an intra-page offset, replacement cursor, item identity, or task identity. Provider intra-page resume is outside this contract because a later observation in the same page may revise an earlier one.

When the source is exhausted, return `source_exhausted`; when a later page fails, preserve previously reconciled results, return that page's incoming cursor, and use the failure as `stop_reason`. Any continuation is partial; exhaustion is complete only when no conflict prevents completeness.

Completeness-required mode overrides the standard display call's
`unique_limit_reached` stop. Keep a display/return buffer containing at most the
first 50 unique canonical tasks, but continue the investigation and
reconciliation state across every provider page. Follow each provider-supplied
opaque continuation without changing it. The aggregate result's counts,
conflicts, and stop reason cover the full investigated extent even when
`returned_count` stays at 50. Duplicate discovery must not set
`create_allowed=true` until this aggregate loop confirms raw source exhaustion.
If the loop hits a hard stop, preserve its current buffer and aggregate state,
return `partial`, and expose the unchanged provider continuation when one is
available.

## Completeness envelope

Use the reconciled result envelope for unfiltered lists, Status-filtered lists,
searches, duplicate discovery, and other completeness-required investigations.
It reports `raw_observation_count`, `deduplicated_observation_count`,
`identity_conflict_count`, `reconciliation_conflict_count`,
`unique_task_count`, `returned_count`, `task_order`, `completeness`,
`truncated`, `continuation`, and `stop_reason`.

Set `complete` only after raw source exhaustion is confirmed and no identity,
reconciliation, or schema ambiguity prevents a complete result. Reaching the
unique-result limit, deferring a page, or stopping for a permission failure,
page retrieval failure, schema ambiguity, or tool hard limit is `partial`.
Preserve all already fetched, reconciled results and report the precise
`stop_reason`, `truncated` state, provider-supplied continuation when available,
and whether resumption is possible. Never synthesize a provider cursor,
continuation value, or intra-page position.

The 50-item display/return limit is distinct from investigation extent. A
completeness-required investigation, including duplicate discovery, continues
to raw source exhaustion even if only 50 items can be displayed or returned. If
that investigation cannot exhaust the source, return `partial`; never treat 50
returned results as evidence of completeness.

### Query mode decision matrix

| Query mode | Condition | Investigation action | Completeness | Returned items |
| --- | --- | --- | --- | --- |
| standard display | 50 unique matches before exhaustion | stop the call | `partial` | at most 50 |
| completeness-required | 50 unique matches before exhaustion | continue investigation | `partial` | at most 50 |
| completeness-required | provider continuation available | follow the opaque continuation | `partial` | at most 50 |
| any | raw source exhausted without conflicts | stop | `complete` | at most 50 |
| any | hard stop or conflict | stop and preserve results | `partial` | at most 50 |

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
