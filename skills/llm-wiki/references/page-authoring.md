# Semantic Page Schema Inventory

Read this inventory only after the structural read-set resolves one readable selected authoring skill. This inventory is the authoritative semantic contract. Each asset mirrors exactly one inventory entry without adding or omitting semantics. `llm-wiki` supplies the applicable semantic schema and relation identity; the selected authoring skill owns serialization and its ordinary checks.

## Common Contract

Every page schema declares:

- `page_type`: stable semantic identity.
- `purpose`: durable reader value.
- `required_fields`: information that must survive authoring.
- `optional_fields`: information included only when supported by evidence or the operation.
- `relation_kinds`: typed outbound and inbound target identities.
- `lifecycle_state`: allowed state and transition meaning.
- `discoverability_metadata`: reader tasks, summary, aliases, and search terms needed to find the page.
- `provenance_requirement`: evidence needed for claims or decisions.
- `index_log_effect`: required discovery-index and change-log synchronization.

Keep one durable topic per page. When two pages strongly overlap, select one canonical target by stable name, clear scope, and continued reference value. Preserve relation identities and discoverability through `rename`, `merge`, `archive`, `split`, or `rehome`. A direct canonicalization updates the affected pages, their inbound and outbound relations, the discovery index, and the change log. An actor without direct authority routes the proposed change to the resolved draft target.

## Schema Inventory

### Knowledge-root local contract

- `page_type`: `knowledge-root-local-contract`.
- `purpose`: declare the root's authority, access, lifecycle routing, and authoring compatibility.
- `required_fields`: knowledge-root identity; topology; root-registry policy; canonical owner; read access; write boundary; draft target policy; Authoring Profile; Compatibility Requirement; immutable-source boundary; maintained-knowledge boundary; index purpose; log purpose; default durable-document routing; conflict rule.
- `optional_fields`: local naming, page-type, language, routing, and governance overrides; multi-root adapter identity and resolution rules.
- `relation_kinds`: repository router; selected authoring profile; registry adapter; immutable-source destination; maintained-knowledge destination; index; log; draft destination; durable-document destination.
- `lifecycle_state`: active; superseded only by an identified successor local contract.
- `discoverability_metadata`: root scope; entrypoint identity; owner; topology; supported lifecycle operations.
- `provenance_requirement`: identify local governance or owner authority for each override and profile selection.
- `index_log_effect`: do not catalog this contract as an active knowledge page; append a lifecycle log event when authority, routing, access, or authoring compatibility changes.

### Repository router

- `page_type`: `repository-router`.
- `purpose`: route repository lifecycle work and durable planning or decision outputs to the authoritative knowledge root.
- `required_fields`: repository identity; knowledge-root identity; local-contract identity; topology route; durable-document route; blocked-write conditions; thin-router boundary.
- `optional_fields`: multi-root adapter identity; repository-specific routing notes.
- `relation_kinds`: knowledge-root contract; registry adapter; durable-document destination.
- `lifecycle_state`: active; superseded only by an identified successor router.
- `discoverability_metadata`: repository scope; knowledge-root entrypoint; supported lifecycle operations.
- `provenance_requirement`: identify repository governance for the chosen knowledge-root route.
- `index_log_effect`: do not catalog this router as an active knowledge page; append a lifecycle log event in the affected root when routing changes.

### Root registry

- `page_type`: `root-registry`.
- `purpose`: resolve durable root identity, scope, authority, access, proposal routing, and authoring compatibility.
- `required_fields`: registry identity; for each root, Root ID, Root URI or Path identity, Scope, Canonical Owner, Read, Write, Draft Target, Authoring Profile, Compatibility Requirement.
- `optional_fields`: root alias; governance note; deprecation reason; successor root identity.
- `relation_kinds`: root local contract; selected authoring profile; draft destination; predecessor root; successor root.
- `lifecycle_state`: active, deprecated, or superseded.
- `discoverability_metadata`: registry identity; root ids; scopes; owners; lifecycle states.
- `provenance_requirement`: identify adapter or governance authority for every root record and lifecycle change.
- `index_log_effect`: keep registry identity discoverable from each multi-root contract; append affected-root log events for material registry changes.

### Discovery index

- `page_type`: `discovery-index`.
- `purpose`: provide reader-task entrypoints and one catalog record for every active canonical durable page.
- `required_fields`: root identity; representative reader-task shortcuts; active canonical page identities; page types; one-line summaries; primary search terms; lifecycle inclusion rule.
- `optional_fields`: aliases; audience-specific entrypoints; recent-change shortcuts; domain categories.
- `relation_kinds`: reader-task shortcut target; active canonical page target.
- `lifecycle_state`: active and synchronized with canonical page lifecycle.
- `discoverability_metadata`: reader task; page type; canonical title; summary; aliases; primary search terms.
- `provenance_requirement`: every record resolves to an allowed active canonical target and reflects its current lifecycle state.
- `index_log_effect`: this schema is the index; each material change is represented by the operation's change-log event.

### Change log

- `page_type`: `change-log`.
- `purpose`: preserve an append-only audit trail for durable lifecycle effects.
- `required_fields`: event date; operation; actor; target identity; authority result; lifecycle effect; affected page identities; affected index identity; evidence.
- `optional_fields`: owner decision; canonicalization action; reason; follow-up condition; predecessor identity; successor identity.
- `relation_kinds`: changed page; affected index; proposal; decision source; evidence; predecessor; successor.
- `lifecycle_state`: append-only active history.
- `discoverability_metadata`: date; operation; actor; target identities; affected page types; decision or action.
- `provenance_requirement`: identify evidence or decision authority sufficient to audit every recorded effect.
- `index_log_effect`: this schema is the log; append one event for every required durable effect without deleting or rewriting prior history.

### Source summary

- `page_type`: `source-summary`.
- `purpose`: preserve what a source establishes, why it matters, and which maintained knowledge it affects.
- `required_fields`: title; creation identity; last-update identity; source identity; source position; key claims; affected knowledge; open questions; provenance.
- `optional_fields`: aliases; tags; chronology; contradictions; source limitations; confidence.
- `relation_kinds`: raw source; entity; concept; synthesis; query note; competing source.
- `lifecycle_state`: active, superseded, or archived.
- `discoverability_metadata`: title; one-line summary; source identity; aliases; tags; primary search terms.
- `provenance_requirement`: provide a resolvable immutable-source identity for each durable claim.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

### Entity

- `page_type`: `entity`.
- `purpose`: maintain the durable identity, facts, importance, and history of a named thing.
- `required_fields`: title; creation identity; last-update identity; identity boundary; summary; key facts; importance; provenance.
- `optional_fields`: aliases; tags; entity kind; timeline; open questions; contradictions; status.
- `relation_kinds`: source summary; concept; synthesis; related entity; query note.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: canonical name; aliases; one-line summary; entity kind; tags; primary search terms.
- `provenance_requirement`: provide evidence identity for each material fact and each disputed interpretation.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

### Concept

- `page_type`: `concept`.
- `purpose`: maintain a working definition and evidence-backed boundary for a recurring idea.
- `required_fields`: title; creation identity; last-update identity; working definition; importance; supporting claims; tensions; provenance.
- `optional_fields`: aliases; tags; counterevidence; open questions; scope exclusions; confidence.
- `relation_kinds`: source summary; entity; synthesis; related concept; query note.
- `lifecycle_state`: active, superseded, merged, split, or archived.
- `discoverability_metadata`: canonical term; aliases; one-line summary; tags; primary search terms.
- `provenance_requirement`: provide evidence identities for support, contradiction, and disputed interpretation.
- `index_log_effect`: maintain one active canonical index record; creation and lifecycle changes require log events.

### Synthesis

- `page_type`: `synthesis`.
- `purpose`: preserve a durable decision, comparison, specification, plan, briefing, or cross-source conclusion.
- `required_fields`: title; creation identity; last-update identity; status; decision; problem; goal; non-goal; acceptance; provenance.
- `optional_fields`: aliases; tags; relations; alternatives; implications; risks; open questions; operating guidance.
- `relation_kinds`: source summary; entity; concept; predecessor decision; successor decision; evidence; implementation progress ledger.
- `lifecycle_state`: proposed, active, accepted, superseded, or archived.
- `discoverability_metadata`: title; one-line summary; artifact kind; status; aliases; tags; reader tasks; primary search terms.
- `provenance_requirement`: provide evidence and decision authority for claims, acceptance, and lifecycle state.
- `index_log_effect`: maintain one active canonical index record; creation, decision, status, and successor changes require log events.

### Query note

- `page_type`: `query-note`.
- `purpose`: preserve a reusable answer, comparison, briefing, or decision input originating from a question.
- `required_fields`: title; creation identity; last-update identity; originating question; durable answer; decision material; provenance; follow-up disposition.
- `optional_fields`: aliases; tags; alternatives; uncertainties; missing sources; candidate page updates.
- `relation_kinds`: source summary; entity; concept; synthesis; follow-up target.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: question; one-line summary; answer kind; aliases; tags; reader tasks; primary search terms.
- `provenance_requirement`: provide resolvable evidence identity for the answer and every disputed claim.
- `index_log_effect`: reusable active notes have one canonical index record; durable filing and lifecycle changes require log events.

### Draft note

- `page_type`: `draft-note`.
- `purpose`: preserve a non-owner proposal and the owner's eventual decision without presenting it as verified.
- `required_fields`: title; current status; review state; confidence; target root; canonical target identity; proposal; evidence; created actor; created date; reason direct update was unavailable; requested owner action.
- `optional_fields`: related targets; destination identity; open questions; follow-up condition; owner decision; decision reason; decision actor; decision date.
- `relation_kinds`: target root; canonical target; related page; source evidence; decision log event; destination.
- `lifecycle_state`: proposed, promoted, merged, rejected, or deferred.
- `discoverability_metadata`: proposal title; target identity; current status; owner; review condition; never active-canonical discovery while unverified.
- `provenance_requirement`: provide evidence for the proposal and owner authority for the final decision.
- `index_log_effect`: proposed and deferred drafts stay out of the active catalog; every owner decision requires a log event; promoted or merged canonical targets are synchronized in the index.

### Implementation progress ledger

- `page_type`: `implementation-progress-ledger`.
- `purpose`: provide cross-slice discovery of landed scope, remaining scope, evidence, and review conditions without replacing execution records.
- `required_fields`: title; topic identity; area; slice id; slice status; landed scope; remaining scope; evidence; next trigger; owner; review condition.
- `optional_fields`: aliases; tags; dependencies; open scope summary; release identity; related execution records.
- `relation_kinds`: specification; implementation plan; progress record; issue; evidence; release; review.
- `lifecycle_state`: active or archived; slice states are planned, in-progress, implemented-unverified, verified, deferred, blocked, or dropped.
- `discoverability_metadata`: topic; one-line summary; area; status; owner; aliases; tags; remaining-scope terms; review terms.
- `provenance_requirement`: verified slices require evidence; deferred, blocked, and dropped slices require reason and review, unblock, or decision identity.
- `index_log_effect`: maintain one active canonical index record; every material slice or ledger lifecycle update requires a log event.

## Preservation And Discoverability

For every authored result:

- preserve the selected schema's required fields, optional supported fields, relation kinds, lifecycle state, discoverability metadata, provenance, and index/log effect;
- keep one canonical target identity for strongly overlapping pages;
- maintain meaningful outbound relations and at least one inbound discovery path for each new active canonical page;
- retain disagreement instead of flattening a disputed claim; and
- apply the selected authoring skill's ordinary check exactly as documented, propagating failure without inspecting syntax in `llm-wiki`.
