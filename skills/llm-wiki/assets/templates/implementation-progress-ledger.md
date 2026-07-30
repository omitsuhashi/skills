# Implementation Progress Ledger Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `implementation-progress-ledger`.
- `purpose`: provide cross-slice discovery of landed scope, remaining scope, evidence, and review conditions without replacing execution records.
- `required_fields`: title; topic identity; area; slice id; slice status; landed scope; remaining scope; evidence; next trigger; owner; review condition.
- `optional_fields`: aliases; tags; dependencies; open scope summary; release identity; related execution records.
- `relation_kinds`: specification; implementation plan; progress record; issue; evidence; release; review.
- `lifecycle_state`: active or archived; slice states are planned, in-progress, implemented-unverified, verified, deferred, blocked, or dropped.
- `discoverability_metadata`: topic; one-line summary; area; status; owner; aliases; tags; remaining-scope terms; review terms.
- `provenance_requirement`: verified slices require evidence; deferred, blocked, and dropped slices require reason and review, unblock, or decision identity.
- `index_log_effect`: maintain one active canonical index record; every material slice or ledger lifecycle update requires a log event.

Semantic constraints:

- Do not call an area complete while required remaining scope is non-empty.
- Keep task order and assignment in execution records; relate them from the ledger.
- Preserve historical evidence or review identity when a slice changes state.
