# Knowledge-root Local Contract Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `knowledge-root-local-contract`.
- `purpose`: declare the root's authority, access, lifecycle routing, and authoring compatibility.
- `required_fields`: knowledge-root identity; topology; root-registry policy; canonical owner; read access; write boundary; draft target policy; Authoring Profile; Compatibility Requirement; immutable-source boundary; maintained-knowledge boundary; index purpose; log purpose; default durable-document routing; conflict rule.
- `optional_fields`: local naming, page-type, language, routing, and governance overrides; multi-root adapter identity and resolution rules.
- `relation_kinds`: repository router; selected authoring profile; registry adapter; immutable-source destination; maintained-knowledge destination; index; log; draft destination; durable-document destination.
- `lifecycle_state`: active; superseded only by an identified successor local contract.
- `discoverability_metadata`: root scope; entrypoint identity; owner; topology; supported lifecycle operations.
- `provenance_requirement`: identify local governance or owner authority for each override and profile selection.
- `index_log_effect`: do not catalog this contract as an active knowledge page; append a lifecycle log event when authority, routing, access, or authoring compatibility changes.

Semantic constraints:

- Single-root topology has no root registry.
- Direct canonical update requires allowed read access, owned write, canonical-owner authority, and a successful authoring gate.
- A non-owner proposal requires allowed read access, a write boundary that permits proposals, and a resolved in-root draft target.
- Local overrides may specialize the root but cannot weaken the structural authoring gate.
