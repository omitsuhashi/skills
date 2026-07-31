# GitHub Projects Contract

## Semantic capability check

Resolve the requested operation first. Before it runs, require its exact read and write semantic capabilities. Require access only to the targets resolved by that operation. This includes relevant private content. Read-only operations have `none` for their write requirement and perform no write. If a required capability or target permission is missing, stop before mutation and report the missing capability.

## Operation capability matrix

| Operation | Required read capabilities | Required write capabilities |
| --- | --- | --- |
| read | `target_issue_or_project_item_read` | none |
| search | `issue_search`, `project_item_read`, `project_item_list` | none |
| status_filtered_list | `project_item_read`, `project_item_list`, `status_field_read` | none |
| create | `duplicate_discovery`, `target_repository_read`, `target_project_read`, `project_schema_read`, `protected_native_metadata_read` | `issue_create`, `project_item_add`, `requested_field_update` |
| register_existing_issue | `issue_read`, `duplicate_membership_discovery`, `target_project_read`, `project_schema_read`, `protected_native_metadata_read` | `project_item_add`, `requested_field_update` |
| title_body_edit | `issue_read`, `protected_native_metadata_read` | `issue_title_body_update` |
| comment | `issue_read`, `protected_native_metadata_read` | `issue_comment_create` |
| status_priority_due_date | `project_item_read`, `requested_field_read`, `protected_native_metadata_read` | `requested_field_update` |
| done_cancelled | `issue_state_reason_read`, `project_status_read`, `protected_native_metadata_read` | `issue_close`, `project_status_update` |
| reopen | `issue_state_reason_read`, `project_status_read`, `protected_native_metadata_read` | `issue_reopen`, `project_status_update` |

## Retry side capability matrix

| Remaining side | Required read capabilities | Required write capabilities |
| --- | --- | --- |
| issue_create | `protected_native_metadata_read` | `issue_create` |
| project_item_add | `protected_native_metadata_read` | `project_item_add` |
| requested_fields | `protected_native_metadata_read` | `requested_field_update` |
| issue_terminal | `protected_native_metadata_read` | `issue_close` |
| project_status | `protected_native_metadata_read` | `project_status_update` |
| issue_reopen | `protected_native_metadata_read` | `issue_reopen` |

For a partial-failure retry, exact-read the current sides first. Then check only
the operation's read set plus the readback and write capabilities for the named
remaining sides; do not require completed-side writes again. The
`protected_native_metadata_read` capability is semantic exact readback, not an
unrelated metadata write. It applies to every supported mutation and retry, but
never to read-only search/list routes.

Tool names may differ by host integration. Match semantic capabilities, but use only GitHub MCP. Do not fall back to a CLI, direct API client, browser automation, or local backend.

## Project item model

- Create or reuse a GitHub Issue before adding it to the Project.
- Do not use a Project-native draft item as the task source of truth.
- Keep completed and cancelled items in the Project for history.
- Do not create a Project, repository, field, option, view, or workflow as a side effect of normal task operations.
- When one canonical task resolves to multiple Project-item memberships, all
  Project field, terminal, and reopen writes stop. Return the canonical task
  identity and every conflicting Project-item identity, and remain blocked until
  exact membership readback proves one write target. A `partial` list result is
  evidence of the conflict, not permission to guess a membership.

### Native metadata preservation

The protected GitHub-native metadata keys are `assignees`, `labels`,
`milestone`, `issue_type`, `parent_issue`, and `sub_issues`. The MVP may read
them, but no supported mutation writes them. This applies to
`register_existing_issue`, `edit_title`, `edit_body`, `comment`, `status`,
`priority`, `due_date`, `done`, `cancelled`, and `reopen`.

For `register_existing_issue`, change only Project membership and explicitly
requested Project fields or applicable creation defaults. Do not modify the
existing Issue's protected native metadata. For every other supported mutation,
change only the operation's requested field or state sides.

Every supported mutation requires exact readback of the requested fields and all
protected native metadata. Compare all protected keys with their pre-write
values. If protected native metadata readback is unavailable, return `partial`;
never report the mutation as `complete`.

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
- Merge `Status`, `Priority`, and `Due date` independently. Each field owns its
  own authoritative freshness timestamp. A field that is missing or ordinary
  `null` preserves the last known value. Clear a value only when the provider
  explicitly declares that field in an explicit-clear signal.
- Persist an explicit-clear tombstone with that field's freshness. A later
  non-null observation may replace the clear only when its timestamp is at
  least as fresh; an older or unorderable observation must not resurrect the
  cleared value.
- Tombstone presence is distinct from its timestamp value. Accept and retain a
  timestamp-less tombstone when the provider explicitly clears a field with no
  timestamp. A later non-null value cannot be ordered against that tombstone:
  keep the field cleared and isolate the item as a reconciliation conflict
  until exact readback establishes an authoritative order.
- When both the old and new non-null values have timestamps, the newest timestamp wins; equal timestamps use the later provider observation.
- A same-value observation advances only that field's freshness, including Due
  date; it cannot make another field stale. Due date update, missing/null
  preservation, and provider explicit clear follow the same rules.
- When conflicting non-null values cannot be ordered because a timestamp is missing, isolate that item as a reconciliation conflict instead of guessing.
- Track reconciliation conflict fields independently. A provider-declared
  `authoritative_readback` for an exact Status, Priority, or Due date may replace
  that field's unresolved value/tombstone and clear only that field's conflict.
  Remove the item-level reconciliation conflict only when no field conflict
  remains. Authoritative field recovery never clears an identity conflict.

Normalize and retain the requested Status filter for the entire traversal and
apply that filter only after reconciliation; never substitute a fixed Status.
Exclude isolated item conflicts. If an updated observation ceases matching, remove
the earlier match; if it starts matching, add the canonical task once in its
first-valid order. First-valid means the provider-order position at which the
reconciled item first satisfies the normalized filter, not the position of an
earlier non-matching observation. If multiple valid Project items resolve to the same task,
return the canonical task once in its first-valid order, count an identity
conflict, and mark the result partial. Other unambiguous results remain usable.
A same-item/different-task conflict or reconciliation conflict likewise marks
the result partial without discarding unrelated results.

Build the complete canonical-task-to-Project-membership map before suppressing
tasks delivered by an earlier call. This preserves same-task/multiple-membership
conflicts discovered after resume. Delivery suppression must never hide that
conflict or permit a Project write.

The result envelope reports `raw_observation_count`, `deduplicated_observation_count`, `identity_conflict_count`, `reconciliation_conflict_count`, `unique_task_count`, `returned_count`, `task_order`, `completeness`, `truncated`, `continuation`, and `stop_reason`. `raw_observation_count` counts all raw observations fetched and inspected during the call, including observations in an overshoot page that is deferred rather than committed.

## Lossless unique-50 continuation

For a standard display call, the maximum is 50 unique matching tasks per call.
Reconcile each whole page atomically against a candidate copy of the prior
state:

- If accepting the whole page yields fewer than 50 unique matches, commit it and continue when the provider has another page.
- If accepting it yields exactly 50, commit it and stop with `unique_limit_reached`.
- If accepting it would exceed 50, do not consume or commit any part of that page. Return the page's unchanged provider-supplied incoming cursor, the reconciliation state from before that page, and `unique_limit_page_deferred`, even though this can return fewer than 50 tasks.
- Validate every page boundary before consuming the next page. When a page says
  another page exists, its provider-supplied outgoing cursor must exactly equal
  the next page's incoming cursor. A mismatch returns a structured `blocked`
  envelope from the last committed page, with `create_allowed=false` and
  restart-from-source guidance; do not consume the mismatched page.
- For every successfully fetched page, `has_next` must be an exact boolean;
  missing values, strings, and integer `0`/`1` are pagination schema ambiguity.
  When `has_next=true`, require a non-null, non-empty, resumable opaque outgoing
  cursor. If it is unavailable, preserve the fetched/reconciled results, return
  `partial` with `continuation_unavailable`, `create_allowed=false`, no trusted
  continuation state, and resume-unsupported guidance. When `has_next=false`,
  the outgoing cursor must be absent or null; a non-null value is
  `pagination_terminal_cursor_mismatch` and likewise returns an unresumable
  partial result. Only exact `has_next=false` with an absent or null outgoing cursor
  proves source exhaustion. Validate this terminal schema before declaring
  completeness or permitting duplicate creation.

`ContinuationState` is one indivisible runtime-held value containing the opaque
provider continuation unchanged, a lossless reconciliation checkpoint, and a
non-secret public association over those exact two components.
The provider continuation is never embedded in the checkpoint. The checkpoint
uses an explicit allowlist only: canonical item/task identities; reconciled
Status, Priority, and Due date values; per-field freshness and explicit-clear
tombstones; stable first-valid order; item-identity, reconciliation, and
membership conflicts; `already_emitted_task_identities`; cumulative raw and
deduplicated counts; normalized filter and query mode; and the aggregate
matching, display, and invalidated identity sets. The resumed call supplies the
exact prior `ContinuationState`, suppresses already emitted canonical tasks only
after membership conflict detection, and may then reconcile the formerly
deferred whole page.

This checkpoint is portable state, not a credential. It must not contain a
credential, secret, authentication-token value, raw provider session, arbitrary
provider key, or arbitrary provider payload. Checkpoint serialization copies
only the allowlisted fields and recursively excludes everything else. It must
also recursively type-check every allowlisted value before serialization and
resume: identities and timestamps are normalized strings, Status/Priority/Due
date are permitted scalar forms, counts are non-negative integers, collections
contain normalized strings, and maps use their exact declared schemas.
Malformed provider values are never stringified or copied; isolate their item
as `partial`. The provider continuation remains opaque and unchanged; the skill must not synthesize an
intra-page offset, replacement cursor, item identity, or task identity.
Provider intra-page resume is outside this contract because a later observation
in the same page may revise an earlier one. Preserving only a cursor and emitted
identity set is insufficient because a resumed observation may change task
identity, field value, explicit-clear state, freshness, or Project membership.

An opaque provider continuation token is permitted only as pagination state and
must be returned unchanged.

### MVP continuation trust boundary

Retain `ContinuationState` only inside the same trusted caller/runtime execution
context that received the prior result. Its public SHA-256 association detects
accidental mix or corruption only; it does not authenticate state and must not
be described as protection against malicious recombination.

The caller must not decompose `ContinuationState`, pair its checkpoint with a
separately supplied cursor, or recombine components from different results.
User-supplied, transcript- or artifact-loaded, independently serialized,
reconstructed, copied across an execution boundary, or otherwise untrusted
state is unsupported even when its public digest was recomputed correctly.
Resume accepts only the exact runtime-retained `resume_continuation_state`.
Before any provider fetch, verify trusted provenance, exact schema, checkpoint
types, public association, normalized filter/query mode, and the unchanged
provider continuation.

Invalid provenance, association, schema, filter, query mode, or legacy separate
input returns a structured `blocked` envelope with
`create_allowed=false`, a precise `stop_reason`, and restart-from-source
guidance. It is a portable caller result, not an assertion or exception, and
cannot reach duplicate creation. The result envelope may expose the unchanged
opaque continuation for diagnostics, but that value is not a standalone resume
input.

A malicious trusted caller is outside the MVP threat model because it can also
falsify provider observations. If cross-boundary persisted resume is later
required, it needs a runtime-owned MAC or signature, or a server-side opaque handle.
That is a separate Companies/live design and permission review; this
portable skill must not implement or hard-code a signing key.

Before resume, compare the checkpoint's normalized Status filter and query mode
with the new request. Reject a mismatch before reading another page. After
reconciliation, report any previously emitted task that no longer matches as an
invalidated task, remove it from aggregate matching/display identities, and
update aggregate counts. Do not silently retain stale filter results.

When the source is exhausted, return `source_exhausted`; when a later page
fails, preserve previously reconciled results, return that page's unchanged
incoming cursor and the checkpoint from immediately before the failed fetch,
and use the failure as `stop_reason`. Any continuation is partial; exhaustion
is complete only when no conflict prevents completeness.

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

The completeness-required executor, rather than a caller-supplied boolean,
drives every page fetch until exhaustion or a hard stop. It commits whole pages
to one aggregate reconciliation checkpoint even after 50 matches, retains at
most the first 50 tasks in the display buffer, and derives duplicate decisions
only from the final aggregate envelope. On exhaustion it may be `complete` with
display `truncated=true`; on permission, page, or tool failure it returns
`partial`, preserves the current display and aggregate checkpoint, and exposes
the failed page's unchanged incoming continuation. It never sets
`create_allowed=true` before conflict-free source exhaustion.

On a later resume, cumulative raw/deduplicated counts, all unique matching
identities, first-50 display identities, conflicts, and invalidations continue
from the checkpoint rather than restarting at zero. The final envelope and
checkpoint therefore describe the full investigation across calls.

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
- `Done` targets Issue state `closed`, close reason `completed`, and Project Status `Done`.
- `Cancelled` targets Issue state `closed`, close reason `not planned`, and Project Status `Cancelled`.
- Treat the Project Status and Issue close as two sides of one logical transition.
- Read the current Issue state, close reason, and Project Status first. The Issue
  side is already complete only when both state and close reason equal their
  target. A closed Issue with the wrong close reason still leaves `issue` in
  `first_remaining_sides`.
- An explicit terminal instruction needs no second confirmation. An inferred terminal transition still requires confirmation before mutation.
- Keep the item in the Project; do not remove or archive it.
- When an externally closed Issue has a reliable close reason, reconcile the Project Status as a safe non-destructive update.
- If only one side succeeds, return `partial`. Per-side result and exact readback identify completed work; `first_remaining_sides` contains unfinished sides only. Do not report a two-side partial success as `complete`.
- Retry after another exact readback. Put only the still-missing side in `retry_attempted_sides`; do not write an already-correct side again.

## Reopen

Issue state and Project Status are two sides of one logical operation; the Issue
side includes close reason. Reopen targets Issue state `open`, an exactly
cleared close reason, and a non-terminal Project Status.

- Normalize an explicit target and allow only `Inbox`, `Backlog`, `Ready`, `In progress`, and `Blocked`. A bare reopen defaults to `Backlog`.
- Block `Done`, `Cancelled`, every unknown or non-normalizable value, and a schema-ambiguous target before either side is attempted.
- Read current Issue state, close reason, and Project Status first. The Issue
  side remains unfinished when state is not `open` or provider readback has not
  cleared close reason to its exact open-state representation.
- If both sides read back at their targets, return `complete`. If one side succeeds and the other does not, return `partial`, name the completed side and `first_remaining_sides`, and include the current Issue state, close reason, and Status as exact readback.
- When the other side fails, do not roll back a successful side. Keep its exact readback as the resume basis.
- On retry, read both sides again and put the remaining side only in `retry_attempted_sides`. Never reopen an Issue already confirmed open, rewrite a Status already confirmed correct, or reset a successful explicit Status to the bare-reopen default.

## Setup boundary

If fields or options are missing, stop normal task writing and report the exact schema difference. Create or repair schema only in a separately requested setup operation with confirmed GitHub MCP capability and permission. Never silently remap a field by a similar name.
