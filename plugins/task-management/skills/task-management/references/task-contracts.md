# Task Contracts

This reference defines the backend-neutral contracts used by the
`task-management` skill. These contracts are the consumer-facing surface for
task intake, routing, previews, and adapter results.

The mutable external backend remains the source of truth for task state.
Operator-facing read routes use MCP or provider-plugin tools and expose no
local write tool.

The read-only `local_json` adapter is a temporary plugin-owned test and smoke
fixture only. It is not an initial reference read route, runtime persistent
source of truth, or normal bootstrap route. MCP and provider-plugin routes reuse
the same contracts without making GitHub or any other provider an implicit
fallback.

## Non-Goals

- Do not implement a backend API client.
- Do not implement a direct GraphQL client.
- Do not implement a gh command planner.
- Do not store credentials, tokens, or provider auth material.
- Do not expose provider-specific raw IDs as reusable skill contracts.
- Do not create or repair GitHub Projects schema in this skill.
- Do not create `task_sha`, a duplicate-prevention store, or a local task
  ledger in Portfolio OS.

## TaskDraft

`TaskDraft` is the reviewable task content before adapter dispatch.

Required fields:

- `title`: human-readable task title.
- `body`: reviewable task body.
- `work_unit_id`: stable routing key, for example `inbox`.
- `work_unit_name`: human display label for backend UIs.
- `task_type`: one of `implementation`, `review`, `research`, `decision`,
  `coordination`, `maintenance`, or `inbox_triage`.
- `due_date`: ISO date string or `null`.
- `urgency`: one of `low`, `normal`, `high`, or `blocked`.
- `importance`: one of `low`, `normal`, `high`, or `critical`.
- `automation_mode`: one of `manual_only`, `assistive`, or
  `trusted_after_approval`.
- `approval_required`: boolean. State-changing adapter dispatch still requires
  an explicit review gate; this field records task-level policy.
- `source_ref`: sanitized source summary or opaque source trail with `kind`,
  `ref`, and `label`.
- `fields`: backend-neutral field bag for future extension.

`TaskDraft` must not contain raw platform payloads, message ids, transport
metadata, GitHub node IDs, project field IDs, repository IDs, or credentials.

## TaskBackendRoute

`TaskBackendRoute` describes which integration surface to use. It does not
describe a concrete project, repository, or board target.

Required fields:

- `kind`: one of `mcp`, `reader`, `skill`, `cli`, or `url`.
- `connection_ref`: opaque host or profile connection reference.
- `capability`: requested adapter capability, such as `project_management`.
- `field_overrides`: optional map from canonical contract field names to
  backend display field names.

The route can name `github_projects_mcp` in surrounding config, but it must not
carry GitHub owner, project number, repository, field IDs, or tokens.

## TaskBackendDestination

`TaskBackendDestination` describes the concrete external destination supplied
by the caller, profile, or host registration.

Required fields:

- `backend_key`: selected backend key, for example `github_projects_mcp`.
- `destination_ref`: opaque external destination reference or URL.
- `destination_label`: human-readable label for review.
- `content_target_ref`: optional opaque target used by an adapter when it must
  create linked content such as an issue before attaching it to a project.

Destination refs are opaque. The reusable skill should not split them into
provider-specific raw IDs.

## TaskRef

`TaskRef` is the consumer-facing reference returned after a backend accepts or
locates a task.

Required fields:

- `backend_key`: selected backend key.
- `task_ref`: opaque adapter-owned task reference.
- `task_url`: linkable URL when available, otherwise `null`.
- `title`: last known title for human review.

`task_ref` may be adapter-owned and stable within that adapter, but provider
raw IDs remain backend-owned metadata and are not part of the exposed contract.

## TaskQuery

`TaskQuery` is a backend-neutral read request. It filters by consumer concepts,
not provider IDs.

Common fields:

- `backend_key`: optional; the host route resolves `default_backend` when absent.
- `work_unit_id`
- `task_type`
- `status`
- `due_before`
- `limit`

Adapters may translate this into provider-specific reads outside the reusable
skill. Query fixtures must not require live GitHub, Hermes profiles, MCP
servers, or credentials.

The executable Hermes surface wraps these fields in an object containing
`query` and opaque `destination_ref`. Route path, local path, provider
destination, adapter kind, and adapter tool name are host-owned configuration
and must not be accepted as model input.

## TaskSnapshot

`TaskSnapshot` is a normalized read model returned from a backend.

Required fields:

- `task_ref`: `TaskRef`.
- `title`
- `body`
- `work_unit_id`
- `work_unit_name`
- `task_type`
- `status`
- `due_date`
- `urgency`
- `importance`
- `automation_mode`
- `approval_required`
- `source_ref`
- `backend_metadata`

`backend_metadata` may include display-only, backend-owned metadata such as a
link label and HTTP(S) URL without embedded credentials. It must not expose
provider-specific raw IDs, field IDs, or auth details to task-management
consumers. Snapshot task type, due date, urgency, importance, and automation
mode use the same canonical values as `TaskDraft`.

## TaskSnapshotResult

`TaskSnapshotResult` is the executable read envelope returned by
`task-management-read:task_query`.

Required fields:

- `result_type`: `TaskSnapshotResult`.
- `ok`: boolean.
- `backend_key`: the selected backend key on success.
- `destination_ref`: the opaque destination used for the read on success.
- `task_snapshots`: zero or more normalized `TaskSnapshot` values.
- `error`: `null` on success, otherwise a typed backend-neutral error.

The result must fail closed instead of returning a partial snapshot when a
required field is missing or a normalized value contains credential-like data.
Raw adapter results and provider payloads are never included in errors.

## TaskWriteResult

`TaskWriteResult` normalizes an adapter create, update, comment, or report
result.

Required fields:

- `result_type`: `TaskWriteResult`.
- `ok`: boolean.
- `status`: `created`, `updated`, `commented`, `reported`, `blocked`, or
  `failed`.
- `operation_type`: adapter-neutral operation name such as `task.create`.
- `backend_key`: selected backend key.
- `destination_ref`: opaque destination reference used for the reviewed
  operation.
- `task_ref`: `TaskRef` when available.
- `error`: `null` on success, otherwise a typed error object.

Typed errors are defined by later preflight and adapter-result work. This
contract only requires that error information be structured and
backend-neutral, not that this skill implement GitHub API behavior.

## Fixture Contract

The fixtures under `plugins/task-management/tests/fixtures/` are normative test
data for this reference. They intentionally use opaque refs such as
`external_ref`, `github-projects:portfolio-os-task-board`, and
`source:commander-chat:2026-06-29T09-00-00Z` instead of GitHub node IDs,
project numbers, repository IDs, field IDs, tokens, or live MCP tool payloads.
The Hermes smoke copies its local JSON fixture into a temporary directory; no
versioned operator-facing task snapshot or persistent local task store is part
of this contract.
