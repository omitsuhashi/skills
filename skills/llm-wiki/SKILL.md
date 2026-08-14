---
name: llm-wiki
description: Use when building or maintaining a persistent knowledge base whose durable lifecycle includes bootstrap, ingest, query filing, draft review, canonicalization, or lint.
---

# LLM Wiki

## Overview

This skill routes durable knowledge lifecycle work through a local contract. `raw/` remains immutable source material; the maintained knowledge base, its discovery index, and its change log remain synchronized durable state.

## Inputs

- `operation`: `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, or `lint`.
- resolved `knowledge_root`, topology, actor / authority context, operation payload, existing document state, target relation identity, and syntax-neutral semantic schema.
- the local contract's selected authoring profile and compatibility requirement.

## Outputs

- `operation success` with the authored or changed document identity, required index/log sync set, and its completion state;
- `BLOCKED` before a durable write when a precondition is unresolved, including evidence-bearing authoring-discovery diagnostics; or
- an incomplete result after an in-progress failure, with the exact changed-file set and failed check needed for recovery.

## Required Capabilities

- read the declared structural read-set and local contract;
- apply durable file edits only within resolved authority;
- use existing skill discovery to compare the local Authoring Profile, Compatibility Requirement, and requested operation with each readable candidate's documented scope and procedure, then resolve one applicable authoring skill and read its `SKILL.md`;
- serialize the semantic schema by that skill's documented procedure; and
- validate only semantic preservation, authority, path, bounded write set, and index/log effect.

## Router

Before work, choose one mode and resolve the topology. Read only the operation's structural read-set from `context-contract.toml`; do not read every reference initially.

1. Resolve topology and authority.
2. Extract the local contract's Authoring Profile and Compatibility Requirement. Treat the profile as a semantic selector unless the local contract explicitly declares exact ID semantics; name mismatch alone is neither missing nor incompatible.
3. Through existing skill discovery, compare those fields and the requested operation with each discovered readable candidate's documented scope and procedure. Continue the existing handoff only when exactly one applicable readable `SKILL.md` resolves.
4. Hand off serialization of the syntax-neutral semantic schema to that skill.
5. Validate the resulting structural effect before writing.

When executed discovery cannot resolve uniquely, return `BLOCKED` before any page, index, or log write with the extracted profile, Compatibility Requirement, observed candidate identities, exactly one of `missing`, `ambiguous`, `incompatible`, or `unreadable`, and a candidate-specific reason. When discovery is unavailable, return `BLOCKED` with the extracted profile, Compatibility Requirement, diagnostic condition `discovery unavailable`, candidate set `unobserved`, and the concrete execution failure as the exact cause; do not infer one of the four candidate outcomes. A read-only query may collect material until it would file back; it must return `BLOCKED` before that durable write if the gate is not satisfied.

Before proposing a local-contract mutation, compare the same current checkout's current local contract, current approved spec when present, and current target file state. Historical evidence cannot override those current sources.

If a declared reference disagrees with `context-contract.toml`, treat the contract as the source of truth and fix the mismatch before relying on the read-set.

## Quick Rules

- Inspect the discovery index before changing durable pages unless the task is pure bootstrap.
- Direct canonical update is allowed only when the actor is canonical owner, the target allows read and owned write, and the local contract or adapter permits the action.
- Non-owner durable proposals route to a draft only when the write boundary permits it; a draft is not a verified claim.
- If target resolution or required authority is unavailable, do not write a verified claim or proposal; return `BLOCKED` before a durable write.
- Owner `draft-review` decisions are exactly `promote`, `merge`, `reject`, `defer`.
- `canonicalize` actions are exactly `rename`, `merge`, `archive`, `split`, `rehome`.
- Synchronize the discovery index and change log for direct durable changes, draft-review decisions, canonicalize actions, ingest, durable query filing, and lint passes.
- Pause only for ambiguous, high-impact, or multi-page changes. Routine low-risk updates proceed autonomously.

## Reference Map

- `references/core.md`: shared layers, authority, routing, and semantic index/log invariants.
- `references/single-root.md`: local-contract topology without a root registry.
- `references/multi-root.md`: adapter-resolved root identity, authority, and cross-root routing.
- `references/structure.md`: layout and durable-document routing detail; read only when needed.
- `references/page-authoring.md`: page-boundary and semantic-preservation detail; read only when needed after the authoring gate succeeds.
- `references/modes/*.md`: mode-specific checks, default procedure, and pause rules.
- `references/optional-tooling.md`: optional local workflow support; never a gate requirement.
- `assets/templates/`: optional initial local-contract and durable-record templates.

## Common Mistakes

- Editing immutable source material.
- Updating a durable page without synchronizing its discovery index or change log.
- Writing a canonical page without required authority or an allowed write boundary.
- Continuing to a page, index, or log write when authoring discovery does not resolve uniquely or is unavailable instead of returning the required evidence-bearing `BLOCKED`.
- Treating an Authoring Profile / skill-ID name mismatch as missing or incompatible, or proposing a local-contract mutation without the required current-state comparison.
- Treating a proposed draft as a verified claim or deleting it without a recorded decision.
- Filing scope-specific claims into a broader or unrelated root.
- Duplicating a canonical claim across roots instead of preserving one canonical target identity.
- Loading every reference before resolving the operation's structural read-set.
