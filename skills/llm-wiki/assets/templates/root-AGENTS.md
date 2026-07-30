# Repository Router Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `repository-router`.
- `purpose`: route repository lifecycle work and durable planning or decision outputs to the authoritative knowledge root.
- `required_fields`: repository identity; knowledge-root identity; local-contract identity; topology route; durable-document route; blocked-write conditions; thin-router boundary.
- `optional_fields`: multi-root adapter identity; repository-specific routing notes.
- `relation_kinds`: knowledge-root contract; registry adapter; durable-document destination.
- `lifecycle_state`: active; superseded only by an identified successor router.
- `discoverability_metadata`: repository scope; knowledge-root entrypoint; supported lifecycle operations.
- `provenance_requirement`: identify repository governance for the chosen knowledge-root route.
- `index_log_effect`: do not catalog this router as an active knowledge page; append a lifecycle log event in the affected root when routing changes.

Semantic constraints:

- Keep repository guidance limited to routing and repository-local scope.
- Route single-root authority to the local contract and multi-root authority to the resolved adapter.
- Return `BLOCKED` before durable write when access, write authority, draft routing, or authoring compatibility cannot be resolved.
