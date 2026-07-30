# Ingest Mode

Use this mode when new immutable source material must be integrated into maintained durable knowledge.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set. Read `references/structure.md` only when resolving a new page type or filename identity.

## Goal

Compile new source knowledge once, preserve its provenance, and distribute its durable effect across the relevant source summary, entity, concept, synthesis, discovery, and lifecycle records.

## Check First

- Identify the new source and the existing canonical targets it affects.
- Resolve target-root read access, write boundary, owner, and draft target.
- Determine whether a source summary or implementation progress ledger already exists for the topic.
- Preserve the canonical target and relation identity for every affected claim.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill. Give it each relevant semantic schema from `references/page-authoring.md`, the source provenance, and the canonical or proposed relation identity. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

If discovery is missing, ambiguous, incompatible, or unreadable, return `BLOCKED` before a page, index, or log write.

## Default Procedure

1. Read the immutable source.
2. Use the index to identify likely canonical targets, then read only directly affected durable pages.
3. Resolve authority and select direct canonical update, proposal routing, or blocked outcome.
4. Resolve the selected authoring skill and hand it the applicable semantic schema, provenance, and relation identities.
5. Directly update the source summary, related canonical pages, index, and log only when read access is allowed, write is owned, and the actor is the canonical owner.
6. Otherwise create only a proposal in the resolved in-root draft target when read is allowed and the write boundary permits proposals.
7. Return `BLOCKED` without durable write when access, authority, target identity, or draft routing is insufficient.
8. For a direct update, synchronize one active canonical index record, reader-task shortcuts when warranted, and an `ingest` log event.
9. Apply the selected authoring skill's ordinary check before committing the write set.

## Semantic Preservation

- Do not modify raw source material.
- Preserve contradictions instead of silently replacing an earlier claim.
- Retain provenance while moving a source-supported fact into entity, concept, or synthesis knowledge.
- When implementation evidence changes a tracked area, update an existing ledger candidate so landed scope, remaining scope, evidence, next trigger, and review condition stay visible.

## Pause And Align When

- one source would redefine multiple page boundaries;
- canonical identity or topic scope must change; or
- competing interpretations would materially change downstream durable knowledge.

Routine source summaries, provenance strengthening, and low-impact relation additions proceed within the resolved authority boundary.
