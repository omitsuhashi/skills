# Lint Mode

Use this mode for a whole-root health review rather than single-source processing. Lint detects structural weaknesses, applies bounded low-risk corrections, and routes owner decisions to `draft-review` or `canonicalize`.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set.

## Goal

Detect discovery gaps, orphan targets, stale claims, contradictions, unnamed recurring concepts, unresolved proposals, and incomplete implementation-state evidence without mechanically scoring presentation.

## Check First

- Determine whether the index provides useful reader-task entrypoints and exactly one record per active canonical target.
- Identify active catalog entries missing summary, aliases, search terms, or valid target identity.
- Review unresolved proposals, recent lifecycle events, orphan pages, stale claims, recurring unnamed concepts, and implementation ledgers lacking evidence or review conditions.
- Resolve authority before applying any correction.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill before any correction or lint log event. Give it the relevant semantic schema from `references/page-authoring.md` and each affected canonical, proposed, provenance, and discovery relation identity. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

Read-only detection may proceed before authoring discovery. Missing, ambiguous, incompatible, or unreadable discovery returns `BLOCKED` before a page, index, or log write.

## Default Procedure

1. Review the discovery index and change log.
2. For roots owned by the actor, identify unresolved proposals for `draft-review`.
3. Confirm orphan targets, stale claims, contradiction candidates, recurring unnamed concepts, and discovery gaps against affected pages.
4. Resolve authority, selected authoring skill, semantic schemas, and relation identities before any write.
5. Apply only bounded corrections to semantic discoverability, relation identity, or clearly superseded lifecycle state.
6. Route proposal decisions to `draft-review` and boundary changes to `canonicalize`.
7. Propose targeted source acquisition only for confirmed evidence gaps.
8. Synchronize any corrected active index records and append one `lint` log event describing findings, routing, and bounded corrections.
9. Apply the selected authoring skill's ordinary check before committing the write set.

## Common Lint Findings

- an active canonical target without inbound discovery;
- an active catalog record missing summary or search metadata;
- a reader-task shortcut that merely duplicates the full catalog;
- duplicate concept identities;
- a source summary whose supported entity or concept effects were never integrated;
- a claim without resolvable provenance;
- a synthesis not updated for newer evidence; or
- an implementation slice marked verified without evidence, or deferred or blocked without reason and review or unblock conditions.
