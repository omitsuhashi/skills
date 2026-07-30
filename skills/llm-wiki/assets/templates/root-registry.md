# Knowledge Root Registry Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `root-registry`.
- `purpose`: resolve durable root identity, scope, authority, access, proposal routing, and authoring compatibility.
- `required_fields`: registry identity; for each root, Root ID, Root URI or Path identity, Scope, Canonical Owner, Read, Write, Draft Target, Authoring Profile, Compatibility Requirement.
- `optional_fields`: root alias; governance note; deprecation reason; successor root identity.
- `relation_kinds`: root local contract; selected authoring profile; draft destination; predecessor root; successor root.
- `lifecycle_state`: active, deprecated, or superseded.
- `discoverability_metadata`: registry identity; root ids; scopes; owners; lifecycle states.
- `provenance_requirement`: identify adapter or governance authority for every root record and lifecycle change.
- `index_log_effect`: keep registry identity discoverable from each multi-root contract; append affected-root log events for material registry changes.

Semantic constraints:

- `Read` is `allowed`, `restricted`, or `no-access`.
- `Write` is `owned`, `propose`, or `closed`.
- Direct canonical update requires the canonical owner, allowed read, owned write, local permission, and a successful authoring gate.
- Proposal routing requires allowed read, a write boundary that permits proposals, and a resolved in-root draft target.
- Return `BLOCKED` when required identity, authority, access, routing, profile, or compatibility cannot be resolved.
