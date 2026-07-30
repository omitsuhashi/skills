# Canonicalize Mode

Use this mode when an owner resolves duplication, strong overlap, or a broken durable topic boundary through `rename`, `merge`, `archive`, `split`, or `rehome`.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set.

## Goal

Maintain one canonical target identity, reader discoverability, relation integrity, provenance, and an audit trail while changing page boundaries.

## Check First

- Confirm canonical-owner authority, allowed read access, owned write boundary, and local permission.
- Resolve the current index entry, inbound and outbound relation identities, and affected provenance.
- Choose exactly one canonicalization action and one canonical target.
- For cross-root work, resolve the canonical owner and draft target for every affected root.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill. Give it each affected semantic schema from `references/page-authoring.md` and all predecessor, successor, inbound, outbound, and provenance relation identities. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

If discovery is missing, ambiguous, incompatible, or unreadable, return `BLOCKED` before changing a page, index, or log.

## Action Set

- `rename`: preserve the previous identity as discoverability metadata or a successor relation when needed.
- `merge`: choose one destination, preserve unique supported content, and mark predecessor identity.
- `archive`: remove obsolete or superseded knowledge from active discovery while preserving its successor or reason.
- `split`: create independent durable topic identities and preserve their boundary and relations.
- `rehome`: move knowledge to the correct root, page type, or directory while preserving ownership and successor identity.

## Default Procedure

1. Use the index to resolve the affected targets and overlap candidates.
2. Read the affected pages and prior lifecycle events.
3. Select the canonical target and action.
4. Resolve authority, the selected authoring skill, applicable semantic schemas, and all affected relation identities.
5. Apply the canonical change only when owner authority, allowed read, owned write, and local permission hold.
6. Otherwise create only a proposal in a resolved in-root draft target when the write boundary permits it.
7. Return `BLOCKED` without durable write when authority, access, identity, or draft routing is insufficient.
8. For a direct update, synchronize affected pages and relations, keep exactly one active canonical index record, retain only valid reader-task shortcuts, and append a `canonicalize` log event.
9. Apply the selected authoring skill's ordinary check before committing the write set.

## Pause And Align When

- canonical ownership is unclear;
- split or rehome crosses authority boundaries;
- archive would lose historical or provenance value; or
- the action requires broad relation changes.
