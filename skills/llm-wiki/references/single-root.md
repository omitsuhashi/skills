# Single Root Topology

Use this topology for one knowledge root. Do not create a root registry. The knowledge-root local contract is the authority source.

## Local Contract

The local contract declares the root identity, Canonical Owner, Read access, Write Boundary, Draft Target, Authoring Profile, Compatibility Requirement, durable-document routing overrides, and local overrides that do not weaken this skill's structural gate.

The Authoring Profile must resolve through existing skill discovery to exactly one readable authoring `SKILL.md`. Its Compatibility Requirement must be supported by that selected skill's documented procedure. Otherwise return `BLOCKED` before page, index, or log write.

## Write Boundary

- `Read`: `allowed`, `restricted`, or `no-access`.
- `owned`: only the owner actor directly updates verified claims; an allowed non-owner may create a proposal in the resolved draft target.
- `propose`: routine actors do not directly update verified claims; an allowed actor may create a proposal in the resolved draft target.
- `closed`: do not create verified claims or proposals.

Direct canonical update requires `Read: allowed`, `Write: owned`, owner authority, and the selected authoring gate to succeed. Proposal routing requires `Read: allowed`, a write boundary that permits proposals, and an in-root resolved Draft Target. A missing, restricted, no-access, or out-of-root target returns `BLOCKED` before a durable write.

## Bootstrap Notes

1. Establish the knowledge-root identity and confirm that no root registry is needed.
2. Declare owner, Read access, write boundary, non-owner draft target, Authoring Profile, and Compatibility Requirement in the local contract.
3. Establish immutable source material, maintained knowledge, discovery index, change log, and local contract inside the root.

## Common Mistakes

- Creating a root registry for a single root.
- Omitting authoring profile or compatibility requirement from the local contract.
- Writing a verified claim without owner authority, an allowed boundary, and a successful authoring gate.
