# Entity Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `entity`.
- `purpose`: maintain the durable identity, facts, importance, and history of a named thing.
- `required_fields`: title; creation identity; last-update identity; identity boundary; summary; key facts; importance; provenance.
- `optional_fields`: aliases; tags; entity kind; timeline; open questions; contradictions; status.
- `relation_kinds`: source summary; concept; synthesis; related entity; query note.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: canonical name; aliases; one-line summary; entity kind; tags; primary search terms.
- `provenance_requirement`: provide evidence identity for each material fact and each disputed interpretation.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

Semantic constraints:

- Preserve one canonical identity for strongly overlapping entity pages.
- Keep disagreements explicit and evidence-linked.
