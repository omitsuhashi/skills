# Core Invariants

This is the minimum shared contract for every mode and topology. Read detail references only when the operation needs them.

## Layers

- `knowledge root`: the unit of durable knowledge operation.
- `raw/`: immutable source material; read but do not edit it.
- `wiki/`: maintained durable knowledge.
- `AGENTS.md`: router to this skill and local contract; do not duplicate generic lifecycle rules there.
- `index.md`: reader-facing discovery surface for active canonical durable knowledge.
- `log.md`: append-only audit trail for durable changes.

## Local Contract Fields

The local contract must declare:

- knowledge-root identity;
- Canonical Owner;
- Write Boundary;
- Draft Target for non-owner proposals when applicable;
- Authoring Profile; and
- Compatibility Requirement.

The selected Authoring Profile identifies exactly one applicable authoring skill through existing skill discovery. The Compatibility Requirement defines the semantic preservation the selected skill must support. Missing, ambiguous, incompatible, or unreadable selection returns `BLOCKED` before a page, index, or log write.

## Draft Contract

A draft is not a verified claim. Until an owner promotes or merges it, do not reflect it in canonical knowledge or list it as active in the discovery index.

A draft records the target root, target canonical claim or page, proposal, supporting source, creating actor, requested owner action, and creation date. Its status is one of `proposed`, `promoted`, `merged`, `rejected`, or `deferred`.

## Write Boundary

Direct canonical update is allowed only when the actor is the canonical owner, the target permits reading and owned writing, and the local contract or adapter allows the action. A non-owner may route a durable proposal only to an allowed in-root draft target. If root, access, draft target, or authority cannot be resolved, return `BLOCKED` before any durable write.

Owner `draft-review` and `canonicalize` remain authority-bound actions. They may directly update canonical knowledge only when the same target and local permission requirements are satisfied.

## Index Invariant

The discovery index must make every active canonical durable page discoverable. Keep purpose-oriented entry points and a catalog whose entries preserve the page's relation identity, summary, and useful search terms. Do not list drafts, rejected or deferred notes, archived duplicates, or merged source pages as active canonical knowledge.

After rename, merge, archive, split, or rehome, preserve only the current canonical relation identity in the active catalog. Validate discovery as a semantic effect, not as a dependency on a renderer or tool.

## Log Invariant

The change log must make durable effects traceable. Record bootstrap, ingest, durable query filing, lint passes, draft-review decisions, and canonicalization actions, including what changed and the affected relation identity.
