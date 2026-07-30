# Change Log Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `change-log`.
- `purpose`: preserve an append-only audit trail for durable lifecycle effects.
- `required_fields`: event date; operation; actor; target identity; authority result; lifecycle effect; affected page identities; affected index identity; evidence.
- `optional_fields`: owner decision; canonicalization action; reason; follow-up condition; predecessor identity; successor identity.
- `relation_kinds`: changed page; affected index; proposal; decision source; evidence; predecessor; successor.
- `lifecycle_state`: append-only active history.
- `discoverability_metadata`: date; operation; actor; target identities; affected page types; decision or action.
- `provenance_requirement`: identify evidence or decision authority sufficient to audit every recorded effect.
- `index_log_effect`: this schema is the log; append one event for every required durable effect without deleting or rewriting prior history.

Semantic constraints:

- Record bootstrap, ingest, durable query filing, every draft-review decision, every canonicalization action, and every lint write.
- Preserve rejected and deferred decision reasons and future review conditions.
