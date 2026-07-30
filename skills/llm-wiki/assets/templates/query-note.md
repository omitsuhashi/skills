# Query Note Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `query-note`.
- `purpose`: preserve a reusable answer, comparison, briefing, or decision input originating from a question.
- `required_fields`: title; originating question; durable answer; decision material; provenance; follow-up disposition.
- `optional_fields`: aliases; tags; alternatives; uncertainties; missing sources; candidate page updates.
- `relation_kinds`: source summary; entity; concept; synthesis; follow-up target.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: question; one-line summary; answer kind; aliases; tags; reader tasks; primary search terms.
- `provenance_requirement`: provide resolvable evidence identity for the answer and every disputed claim.
- `index_log_effect`: reusable active notes have one canonical index record; durable filing and lifecycle changes require log events.

Semantic constraints:

- File back only when the answer has durable reuse value and authority permits it.
- Preserve uncertainty and the identity of any knowledge target that should be updated next.
