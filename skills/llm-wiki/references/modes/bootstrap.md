# Bootstrap Mode

Use this mode to establish a new knowledge root or align an existing durable knowledge repository with the LLM Wiki lifecycle.

Read first: `references/core.md`, the chosen topology reference, then this file. That is the structural read-set. Read `references/structure.md` only when resolving layout, page types, durable-document routing, or filename identity.

## Goal

Establish immutable source material, maintained durable knowledge, a discovery index, a change log, and a local authority contract. Keep generic lifecycle rules in `llm-wiki`, and route durable specifications, decisions, plans, and roadmaps into the knowledge root.

## Check First

- Determine whether the repository is dedicated or mixed and whether the topology is single-root or multi-root.
- Resolve the knowledge-root identity, canonical owner, read access, write boundary, draft target, Authoring Profile, and Compatibility Requirement.
- Inventory existing source, maintained knowledge, index, log, and local-contract state.
- Preserve established structural naming or routing unless an explicit local decision changes it.

## Authoring Handoff

After the structural read-set, resolve exactly one readable selected authoring skill through existing skill discovery. Give it the relevant semantic schema from `references/page-authoring.md` and the relation identity for every local contract, repository router, root registry, index, or log record it must serialize. Propagate the selected authoring skill's ordinary check failure. `llm-wiki` must never inspect syntax.

If profile discovery is missing, ambiguous, incompatible, or unreadable, return `BLOCKED` before any durable write.

## Default Procedure

1. Resolve repository shape, topology, target knowledge root, authority, and write boundary.
2. For single-root topology, establish the knowledge-root local contract as authority and do not create a root registry.
3. For multi-root topology, establish a system-specific adapter that resolves root identity, scope, owner, access, write boundary, draft target, authoring profile, and compatibility requirement.
4. For a mixed repository, establish a thin repository router to the knowledge-root contract and durable-document destinations.
5. Resolve the selected authoring skill and hand it the applicable semantic schema and relation identities.
6. Establish only the missing structural directories and durable records.
7. Decide any project-specific durable-document routing and record it as a local override.
8. Seed reader-task discovery and active canonical catalog semantics in the index.
9. Append a `bootstrap` lifecycle event to the log.
10. Apply the selected authoring skill's ordinary check before committing the write set.

## Pause And Align When

- topology, knowledge-root location, owner, or access changes the authority boundary;
- competing layout or routing choices would cause broad relocation later;
- an existing repository contract conflicts with the proposed canonical contract;
- bootstrap requires broad relocation of existing durable pages; or
- existing workflows depend on a durable-document destination whose migration impact is unclear.

## Output Expectations

- The knowledge root has an authoritative local contract, immutable-source boundary, maintained-knowledge boundary, discovery index, and change log.
- A mixed repository has a thin route to the knowledge root.
- Single-root topology has no registry; multi-root topology has an adapter that resolves authority, access, draft routing, and authoring compatibility.
- Later lifecycle modes can reuse the contract without rediscovering serialization policy.
