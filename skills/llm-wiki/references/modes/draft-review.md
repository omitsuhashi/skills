# Draft Review Mode

Use this mode when the canonical owner closes a proposed note as `promote`, `merge`, `reject`, or `defer`.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set.

## Goal

Record an explicit owner decision, apply only accepted content to canonical knowledge, preserve rejected or deferred reasoning, and never delete a proposal without decision history.

## Check First

- Confirm canonical-owner authority, allowed read access, owned write boundary, and any local restriction on direct owner update.
- Resolve the proposal's canonical target identity, evidence, requested action, and current lifecycle state.
- Identify the index and log effects of each possible decision.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill. Give it the draft-note semantic schema, any affected canonical semantic schema from `references/page-authoring.md`, and the proposal, target, provenance, and decision relation identities. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

If discovery is missing, ambiguous, incompatible, or unreadable, return `BLOCKED` before changing the draft, canonical page, index, or log.

## Decision Set

- `promote`: establish the proposal as a verified canonical target.
- `merge`: incorporate only unique supported content into an existing canonical target.
- `reject`: close the proposal with a reason and no canonical claim change.
- `defer`: retain the proposal with the missing evidence, owner action, or review condition.

## Default Procedure

1. Read the proposal, canonical target, index, and log.
2. Confirm evidence, open questions, requested action, owner authority, and direct-update boundary.
3. Choose exactly one decision.
4. Resolve the selected authoring skill and give it the applicable semantic schemas and relation identities.
5. Apply `promote` or `merge` to canonical knowledge only when owner authority, allowed read, owned write, and local permission all hold.
6. Record `reject` or `defer` with reason and follow-up identity without changing verified claims.
7. Update the draft lifecycle state for every decision.
8. When canonical knowledge changes, synchronize its one active index record and any warranted reader-task shortcut.
9. Append a `draft-review` log event for every decision.
10. Apply the selected authoring skill's ordinary check before committing the write set.

## Pause And Align When

- owner authority is unclear;
- evidence is too weak for a high-impact decision;
- promotion or merge requires rename, split, or rehome; or
- rejection could erase a material competing interpretation.
