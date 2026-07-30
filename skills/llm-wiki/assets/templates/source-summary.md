# Source Summary Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `source-summary`.
- `purpose`: preserve what a source establishes, why it matters, and which maintained knowledge it affects.
- `required_fields`: title; source identity; source position; key claims; affected knowledge; open questions; provenance.
- `optional_fields`: aliases; tags; chronology; contradictions; source limitations; confidence.
- `relation_kinds`: raw source; entity; concept; synthesis; query note; competing source.
- `lifecycle_state`: active, superseded, or archived.
- `discoverability_metadata`: title; one-line summary; source identity; aliases; tags; primary search terms.
- `provenance_requirement`: provide a resolvable immutable-source identity for each durable claim.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

Semantic constraints:

- Preserve source disagreement and limitations.
- Keep the raw source immutable.
- Give each affected durable target a stable relation identity.
