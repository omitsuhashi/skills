---
name: grill-to-pr-loop
description: Use when a repository change requires approved durable design, issue decomposition, and worker-only implementation.
---

# Grill to PR Loop

## Overview

Use this operation router for durable design, gated issue decomposition, worker-only execution handoff, and optional approved delivery. It is not a same-session implementation skill.

Load `references/core.md`, then use `context-contract.toml` as the operation router; do not load every reference.

Treat `grill-with-docs` as the required front door for unresolved design choices. If it is unavailable, stop instead of approximating the workflow.

For role orientation, read `../issue-implementation-loop/references/mental-model.md` only when needed; it is outside default read-sets.

## Applicability

Use loop skills when a change needs durable design decisions, local issue decomposition, dependency ordering, approved packet handoff, review, or remote delivery.

Do not use loop skills for small one-off edits, one clear file change, or direct implementation that needs no new gate.

Stop before implementation when design/scope is unresolved, no normalized approved packet exists, worker context is unavailable, or the coordinator would implement.

## Immediate Guard

Before design, issue, execution, or PR actions, run:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase planning
```

Before handing work to execution, run:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase execution
```

Stop if planning lacks `grill-with-docs` or execution lacks `issue-implementation-loop`. GitHub auth is optional until an approved remote write.

## Planning Worktree Gate

Before Written Spec, prepare/reuse one Epic worktree with the current planning read set. Existing preference needs no repeated consent; sandbox failure stops before writes/default-checkout use.

## Mode Router

Load only the current operation files in `context-contract.toml`, the single read-set source.

Read only the current operation's `skills`. Only a bounded dispatch actor reads that operation's `dispatch_skills`; do not preload a future operation's phase-owned skill. Read task-triggered skills on demand only in the current phase, without adding them to the generic contract.

At `65%` context pressure, keep the current operation read-set loaded and add `references/context-compaction.md` only as a conditional overlay.

## Required Rules

- Store each Epic's durable artifacts under repo-local `<durable-planning-root>/<epic-id>/` using the current planning/execution read-set lifecycle. Specs/PRDs/ledgers use Japanese; preserve IDs, paths, commands, schema keys, branches, errors, and external refs.
- The local issue ledger is canonical; GitHub is an optional mirror/delivery record.
- Authority: main planning context integrates canonical spec/issue ledger/execution plan/sealed packet and finalizes the Human Gate approval candidate as integration owner; supporting agents are advisory-only/read-only; Human decides the Gate.
- Host runtime selects model/reasoning; durable artifacts omit concrete values.
- Planning owns final spec identification, exact-path/digest six-part approval, and Input Packet v2 sealing; changes to spec bytes, `spec_binding`, or `approval_evidence` return to the human Spec Gate for new approval/seal.
- Other packet drift uses the handoff's Execution Plan Gate restore/reseal lifecycle.
- Each gate is a phase approval commit boundary: commit artifacts/ledger/log. Before handoff, context 圧縮 or use a fresh coordinator with the packet and bounded brief.
- Execution Envelope v4 carries `approved_spec_binding` and `phase_branch_policy`; it and later instantiated artifacts are untracked runtime state. Planning commits, `epic_base`, issue branches, and worktrees remain separate.
- `issue-implementation-loop` owns reservations, scheduling, runtime, workers, review, recovery, and `PR_READY`; planning never implements.
- Route spec self-review and `final-review` through requirements, material simplicity, then material risk. Report only `Critical` / `Important` findings.
- Remote writes/high-risk actions require approved remote policy. Final PR merge is always human-only.

## Gates

- **Spec Gate**: human decision gate for exact spec revision and six-part scope.
- **Issue Gate**: human decision gate for issues, blockers, order, status, and criteria.
- **Execution Plan Gate**: agent preflight + commit boundary for packet/capabilities/scope/DAG/policy; it is not a human approval gate when approved scope is unchanged.
- **Remote Gate**: before an external write outside approved remote policy, present exact actions and wait.

Human gates need explicit approval unless the exact artifact/scope is already approved. Commit each approved boundary; record any approved delay in the ledger/log.

## Stop Conditions

Stop for ambiguous `Epic ID`, overlapping dirt, cyclic blockers, missing skills/workers, scope drift, or unapproved external/high-risk action.

## Completion Report

Report paths/`Epic ID`, issues, packet/result, branch map, verification, implementation review summary, spec alignment review summary, ledger/remote actions, and risks.
