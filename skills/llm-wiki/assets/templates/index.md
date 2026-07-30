# Discovery Index Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `discovery-index`.
- `purpose`: provide reader-task entrypoints and one catalog record for every active canonical durable page.
- `required_fields`: root identity; representative reader-task shortcuts; active canonical page identities; page types; one-line summaries; primary search terms; lifecycle inclusion rule.
- `optional_fields`: aliases; audience-specific entrypoints; recent-change shortcuts; domain categories.
- `relation_kinds`: reader-task shortcut target; active canonical page target.
- `lifecycle_state`: active and synchronized with canonical page lifecycle.
- `discoverability_metadata`: reader task; page type; canonical title; summary; aliases; primary search terms.
- `provenance_requirement`: every record resolves to an allowed active canonical target and reflects its current lifecycle state.
- `index_log_effect`: this schema is the index; each material change is represented by the operation's change-log event.

Semantic constraints:

- Catalog each active canonical durable page exactly once.
- Do not catalog proposed, rejected, deferred, merged, superseded, or archived duplicates as active targets.
- Keep reader-task shortcuts selective; they are not a duplicate full catalog.
