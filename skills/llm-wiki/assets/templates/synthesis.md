# Synthesis Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `synthesis`.
- `purpose`: preserve a durable decision, comparison, specification, plan, briefing, or cross-source conclusion.
- `required_fields`: title; creation identity; last-update identity; status; decision; problem; goal; non-goal; acceptance; provenance.
- `optional_fields`: aliases; tags; relations; alternatives; implications; risks; open questions; operating guidance.
- `relation_kinds`: source summary; entity; concept; predecessor decision; successor decision; evidence; implementation progress ledger.
- `lifecycle_state`: proposed, active, accepted, superseded, or archived.
- `discoverability_metadata`: title; one-line summary; artifact kind; status; aliases; tags; reader tasks; primary search terms.
- `provenance_requirement`: provide evidence and decision authority for claims, acceptance, and lifecycle state.
- `index_log_effect`: maintain one active canonical index record; creation, decision, status, and successor changes require log events.

Semantic constraints:

- Distinguish a decision from alternatives and unresolved risks.
- Keep acceptance evidence and successor identity discoverable.
