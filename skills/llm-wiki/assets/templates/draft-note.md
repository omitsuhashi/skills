# Draft Note Schema

This asset is a syntax-neutral field contract. Supply these semantic fields to the selected authoring skill.

- `page_type`: `draft-note`.
- `purpose`: preserve a non-owner proposal and the owner's eventual decision without presenting it as verified.
- `required_fields`: title; current status; review state; confidence; target root; canonical target identity; proposal; evidence; created actor; created date; reason direct update was unavailable; requested owner action.
- `optional_fields`: related targets; destination identity; open questions; follow-up condition; owner decision; decision reason; decision actor; decision date.
- `relation_kinds`: target root; canonical target; related page; source evidence; decision log event; destination.
- `lifecycle_state`: proposed, promoted, merged, rejected, or deferred.
- `discoverability_metadata`: proposal title; target identity; current status; owner; review condition; never active-canonical discovery while unverified.
- `provenance_requirement`: provide evidence for the proposal and owner authority for the final decision.
- `index_log_effect`: proposed and deferred drafts stay out of the active catalog; every owner decision requires a log event; promoted or merged canonical targets are synchronized in the index.

Semantic constraints:

- A draft is not a verified claim.
- Preserve the final decision and reason; never delete a draft without decision history.
