# Query Mode

Use this mode to answer a question from maintained durable knowledge and decide whether the answer should be filed back.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set. Read `references/structure.md` only when resolving a new durable destination.

## Goal

Reuse compiled knowledge for a grounded answer, consult raw provenance only when needed, and preserve reusable output within the target root when authority permits.

## Check First

- Identify relevant reader-task shortcuts or active canonical targets in the index.
- Resolve authority and proposal routing before any durable filing.
- Determine whether maintained knowledge is sufficient or raw provenance is needed.
- Decide whether the answer is transient or has reusable durable value.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill before durable filing. Give it the relevant semantic schema from `references/page-authoring.md`, supporting provenance, and the canonical or proposed relation identity. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

A read-only answer may be assembled before authoring discovery. Missing, ambiguous, incompatible, or unreadable discovery returns `BLOCKED` before a page, index, or log write.

## Default Procedure

1. Start from the index and read the minimum relevant durable pages.
2. Consult raw provenance only when maintained knowledge is thin, stale, or disputed.
3. Answer with resolvable evidence identities.
4. Decide whether the answer has durable reuse value.
5. If filing is warranted, resolve authority, the selected authoring skill, the applicable semantic schema, and target relation identity.
6. Directly create or update a query note or synthesis only when read is allowed, write is owned, and the actor is canonical owner.
7. Otherwise create only a proposal in the resolved in-root draft target when the write boundary permits it.
8. For a direct update, synchronize one active canonical index record, any warranted reader-task shortcut, and a `query` log event.
9. Propagate an ordinary authoring check failure and leave durable state unchanged.

## File-Back Rule

File the answer when authority permits and it creates reusable comparison, synthesis, taxonomy, decision material, implementation-state discovery, a durable gap closure, or a user-requested durable artifact.

## Pause And Align When

- the durable target is ambiguous and would require broad reorganization;
- the answer spans several materially different artifact candidates; or
- filing requires a rename, merge, split, archive, or rehome decision.
