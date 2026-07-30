# Concept Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `concept`.
- `purpose`: maintain a working definition and evidence-backed boundary for a recurring idea.
- `required_fields`: title; creation identity; last-update identity; working definition; importance; supporting claims; tensions; provenance.
- `optional_fields`: aliases; tags; counterevidence; open questions; scope exclusions; confidence.
- `relation_kinds`: source summary; entity; synthesis; related concept; query note.
- `lifecycle_state`: active, superseded, merged, split, or archived.
- `discoverability_metadata`: canonical term; aliases; one-line summary; tags; primary search terms.
- `provenance_requirement`: provide evidence identities for support, contradiction, and disputed interpretation.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

Semantic constraints:

- Preserve one durable topic and one canonical target identity.
- Retain competing interpretations instead of flattening them.
