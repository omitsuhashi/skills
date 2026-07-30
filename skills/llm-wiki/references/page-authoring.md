# Semantic Page Schema Inventory

Read this inventory only after the structural read-set resolves one readable selected authoring skill. `llm-wiki` supplies the applicable semantic schema and relation identity; the selected authoring skill owns serialization and its ordinary checks.

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
- `purpose`: declare root identity, authority, routing, and authoring compatibility.
- `required_fields`: root identity, topology, canonical owner, read access, write boundary, draft target policy, authoring profile, compatibility requirement, immutable-source boundary, maintained-knowledge boundary, durable-document routing, conflict rule.
- `optional_fields`: local naming, page-type, language, routing, and governance overrides; multi-root adapter identity.
- `relation_kinds`: repository router, selected authoring profile, registry adapter, durable destination.
- `lifecycle_state`: active; superseded only by an identified successor contract.
- `discoverability_metadata`: root scope, entrypoint identity, owner, and supported operations.
- `provenance_requirement`: local governance or owner authority for every override.
- `index_log_effect`: authority, routing, or profile changes require a lifecycle log event; the contract is not an active knowledge-page catalog entry.

### Repository router

- `page_type`: `repository-router`.
- `purpose`: route repository work to the authoritative knowledge-root contract.
- `required_fields`: knowledge-root identity, local-contract identity, topology route, durable-document route, and blocked-write conditions.
- `optional_fields`: multi-root adapter identity and repository-specific routing notes.
- `relation_kinds`: knowledge-root contract, registry adapter, durable destination.
- `lifecycle_state`: active; superseded only with a replacement route.
- `discoverability_metadata`: repository scope and knowledge-root entrypoint.
- `provenance_requirement`: repository governance for the chosen route.
- `index_log_effect`: routing changes require a lifecycle log event in the affected root; no active catalog entry.

### Root registry

- `page_type`: `root-registry`.
- `purpose`: resolve root identity, authority, access, draft routing, and authoring compatibility.
- `required_fields`: root id, root URI or path identity, scope, canonical owner, read access, write boundary, draft target, authoring profile, compatibility requirement.
- `optional_fields`: local governance note, alias, and deprecation successor.
- `relation_kinds`: root contract, selected authoring profile, draft destination, successor root.
- `lifecycle_state`: active, deprecated, or superseded.
- `discoverability_metadata`: registry identity, root ids, scopes, and owners.
- `provenance_requirement`: adapter or governance authority for each root record.
- `index_log_effect`: registry changes require affected-root log events; registry identity is discoverable from each multi-root contract.

### Discovery index

- `page_type`: `discovery-index`.
- `purpose`: provide reader-task entrypoints and one catalog record for each active canonical durable page.
- `required_fields`: root identity, reader-task shortcuts, active-page identities, one-line summaries, search terms, lifecycle filters.
- `optional_fields`: aliases, recent-change shortcuts, and audience-specific entrypoints.
- `relation_kinds`: shortcut target and active canonical page target.
- `lifecycle_state`: active and synchronized with canonical lifecycle changes.
- `discoverability_metadata`: reader task, page type, summary, aliases, and search terms.
- `provenance_requirement`: each entry must resolve to an allowed active canonical target.
- `index_log_effect`: this schema is the index; every material index change is represented by the operation's log event.

### Change log

- `page_type`: `change-log`.
- `purpose`: preserve an append-only audit trail of durable lifecycle changes.
- `required_fields`: event date, operation, actor, target identity, authority result, lifecycle effect, affected identities, evidence.
- `optional_fields`: owner decision, reason, follow-up condition, and successor identity.
- `relation_kinds`: changed page, decision source, evidence, predecessor, successor.
- `lifecycle_state`: append-only active history.
- `discoverability_metadata`: operation, date, actor, affected page types, and target identities.
- `provenance_requirement`: evidence or decision identity sufficient to audit every recorded effect.
- `index_log_effect`: this schema is the log; append one event for each required lifecycle effect without rewriting prior events.

### Source summary

- `page_type`: `source-summary`.
- `purpose`: preserve what a source establishes, why it matters, and which durable knowledge it affects.
- `required_fields`: title, source identity, source position, key claims, affected knowledge, open questions, provenance.
- `optional_fields`: aliases, tags, chronology, contradictions, and source limitations.
- `relation_kinds`: raw source, entity, concept, synthesis, query note, competing source.
- `lifecycle_state`: active, superseded, or archived.
- `discoverability_metadata`: title, summary, source identity, aliases, tags, and search terms.
- `provenance_requirement`: resolvable source identity for each durable claim.
- `index_log_effect`: active canonical summaries have one index record; creation and lifecycle changes require log events.

### Entity

- `page_type`: `entity`.
- `purpose`: maintain the durable identity, facts, importance, and history of a named thing.
- `required_fields`: title, identity boundary, summary, key facts, importance, provenance.
- `optional_fields`: aliases, tags, timeline, open questions, contradictions, and status.
- `relation_kinds`: source summary, concept, synthesis, related entity, query note.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: canonical name, aliases, summary, entity kind, tags, and search terms.
- `provenance_requirement`: evidence identity for every material fact or disputed interpretation.
- `index_log_effect`: one active canonical index record; creation and lifecycle changes require log events.

### Concept

- `page_type`: `concept`.
- `purpose`: maintain a working definition and evidence-backed boundary for a recurring idea.
- `required_fields`: title, working definition, importance, supporting claims, tensions, provenance.
- `optional_fields`: aliases, tags, counterevidence, open questions, and scope exclusions.
- `relation_kinds`: source summary, entity, synthesis, related concept, query note.
- `lifecycle_state`: active, superseded, merged, split, or archived.
- `discoverability_metadata`: canonical term, aliases, summary, tags, and search terms.
- `provenance_requirement`: evidence identities for support, contradiction, and disputed interpretation.
- `index_log_effect`: one active canonical index record; creation and lifecycle changes require log events.

### Synthesis

- `page_type`: `synthesis`.
- `purpose`: preserve a durable decision, comparison, specification, plan, briefing, or cross-source conclusion.
- `required_fields`: title, status, decision, problem, goal, non-goal, acceptance, provenance.
- `optional_fields`: aliases, tags, relations, alternatives, implications, risks, open questions, and operating guidance.
- `relation_kinds`: source summary, entity, concept, predecessor decision, successor decision, evidence, implementation ledger.
- `lifecycle_state`: proposed, active, accepted, superseded, or archived.
- `discoverability_metadata`: title, summary, artifact kind, status, aliases, tags, reader tasks, and search terms.
- `provenance_requirement`: evidence and decision authority for claims, acceptance, and lifecycle state.
- `index_log_effect`: one active canonical index record; creation, decision, status, and successor changes require log events.

### Query note

- `page_type`: `query-note`.
- `purpose`: preserve a reusable answer, comparison, briefing, or decision input originating from a question.
- `required_fields`: title, originating question, durable answer, decision material, provenance, follow-up disposition.
- `optional_fields`: aliases, tags, alternatives, uncertainties, missing sources, and candidate page updates.
- `relation_kinds`: source summary, entity, concept, synthesis, follow-up target.
- `lifecycle_state`: active, superseded, merged, or archived.
- `discoverability_metadata`: question, summary, answer kind, aliases, tags, reader tasks, and search terms.
- `provenance_requirement`: resolvable evidence identity for the answer and every disputed claim.
- `index_log_effect`: reusable active notes have one index record; durable filing and lifecycle changes require log events.

### Draft note

- `page_type`: `draft-note`.
- `purpose`: preserve a non-owner proposal and the owner's eventual decision without presenting it as verified.
- `required_fields`: title, current status, review state, confidence, target root, canonical target identity, proposal, evidence, created actor, created date, reason direct update was unavailable, requested owner action.
- `optional_fields`: related targets, destination identity, open questions, follow-up condition, owner decision, decision reason, decision actor, decision date.
- `relation_kinds`: target root, canonical target, related page, source evidence, decision log event, destination.
- `lifecycle_state`: proposed, promoted, merged, rejected, or deferred.
- `discoverability_metadata`: proposal title, target identity, status, owner, and review condition; never active-canonical discovery while unverified.
- `provenance_requirement`: evidence for the proposal and owner authority for the final decision.
- `index_log_effect`: proposed and deferred drafts stay out of the active catalog; every owner decision requires a log event and any promoted or merged target is synchronized in the index.

### Implementation progress ledger

- `page_type`: `implementation-progress-ledger`.
- `purpose`: provide a cross-slice discovery surface for landed scope, remaining scope, evidence, and review conditions without replacing execution records.
- `required_fields`: title, topic identity, area, slice id, slice status, landed scope, remaining scope, evidence, next trigger, owner, review condition.
- `optional_fields`: aliases, tags, dependencies, open scope summary, release identity, and related execution records.
- `relation_kinds`: specification, implementation plan, progress record, issue, evidence, release, review.
- `lifecycle_state`: active or archived; slice states are planned, in-progress, implemented-unverified, verified, deferred, blocked, or dropped.
- `discoverability_metadata`: topic, summary, area, status, owner, aliases, tags, remaining-scope terms, and review terms.
- `provenance_requirement`: verified slices require evidence; deferred, blocked, and dropped slices require reason and review, unblock, or decision identity.
- `index_log_effect`: an active ledger has one index record; every material slice or lifecycle update requires a log event.

## Preservation And Discoverability

For every authored result:

- preserve the selected schema's required fields, optional supported fields, relation kinds, lifecycle state, discoverability metadata, provenance, and index/log effect;
- keep one canonical target identity for strongly overlapping pages;
- maintain meaningful outbound relations and at least one inbound discovery path for each new active canonical page;
- retain disagreement instead of flattening a disputed claim; and
- apply the selected authoring skill's ordinary check exactly as documented, propagating failure without inspecting syntax in `llm-wiki`.
