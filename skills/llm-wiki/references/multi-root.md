# Multi Root Topology

Use this topology when durable knowledge spans multiple roots. Each root has its own immutable source material, maintained knowledge, discovery index, change log, and local contract.

## Adapter Contract

A system-specific adapter resolves the target root's relation identity, scope, Canonical Owner, Read access, Write Boundary, Draft Target, Authoring Profile, and Compatibility Requirement. The generic skill does not prescribe the adapter's representation or approval workflow.

The Authoring Profile must resolve through existing skill discovery to exactly one readable authoring `SKILL.md`. Its Compatibility Requirement must be supported by that selected skill's documented procedure. Missing, ambiguous, incompatible, or unreadable selection returns `BLOCKED` before a page, index, or log write.

## Access and Routing

- `Read` is `allowed`, `restricted`, or `no-access`.
- `Write` is `owned`, `propose`, or `closed`.
- Only an owner acting on an allowed root with `Write: owned` may directly update a verified claim, and only after the authoring gate succeeds.
- An allowed actor may create a proposal only when an in-root Draft Target is resolved and the write boundary permits proposals.
- Restricted, no-access, closed, unresolved, or out-of-root targets return `BLOCKED` before any durable write.

## Cross-Root Target Identity

Choose one canonical target identity for a claim or source that spans roots. Other roots preserve a pointer or citation to that target instead of duplicating canonical knowledge. Do not move restricted source detail into a root that lacks authority to read it.

## Draft Review and Canonicalization

The owner closes each draft as `promote`, `merge`, `reject`, or `defer`. The owner may update the canonical target and its index/log only when the root remains allowed, owned, and authoring-gate valid. Record every decision and canonicalization action in the applicable change log.

## Common Mistakes

- Resolving a target without its authoring profile and compatibility requirement.
- Writing a verified claim outside the selected root's authority boundary.
- Duplicating a cross-root canonical claim instead of preserving one target identity.
