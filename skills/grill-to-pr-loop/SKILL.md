---
name: grill-to-pr-loop
description: Use when a user wants an end-to-end repository change beginning with design interrogation and durable design docs, followed by spec/PRD synthesis, issue decomposition, dependency-aware implementation through issue-implementation-loop, and optional PR delivery.
---

# Grill to PR Loop

## Overview

Use this skill as the operation router and gate entrypoint for a repository change. It coordinates design interrogation, durable docs, spec/PRD synthesis, local issue decomposition, normalized execution handoff, and optional approved delivery. It is not a same-session implementation skill.

Load `references/core.md` first for lifecycle, ownership, gates, local-first rules, and remote approval boundaries. Then load `references/workflow-contract.md`; it is a router to the phase-specific references. Do not load every reference by default.

Treat `grill-with-docs` as the required front door for unresolved design choices. If it is unavailable, stop instead of approximating the workflow.

## Immediate Guard

Before design, issue, execution, or PR actions, run:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase planning
```

Before handing work to execution, run:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase execution
```

If planning lacks `grill-with-docs`, stop. If execution lacks `issue-implementation-loop`, stop before implementation. GitHub authentication is optional until an approved remote-write action requires it.

## Mode Router

After `core.md` and `workflow-contract.md`, load only the references needed for the current operation:

- `intake`, `grill`, `spec`: `planning-contract.md`
- `issue-gate`: `planning-contract.md`, `local-issue-ledger.md`
- `execution-plan`: `planning-contract.md`, `local-issue-ledger.md`, `execution-handoff.md`
- `resume`, `completion-report`: `local-issue-ledger.md`, `execution-handoff.md`; add `remote-delivery.md` only if remote actions were approved or attempted
- `delivery`: `remote-delivery.md`
- `ambiguity-check`: `common-mistakes.md`

## Required Rules

- Keep long specs, ADRs, implementation plans, and Goal contracts in the repo-local durable path defined by the target repository; in this repo that is `knowledge/wiki/syntheses/`.
- Keep the local issue ledger canonical. GitHub issues and PRs are optional mirrors or delivery records after explicit approval.
- Keep planning, spec, issue ledger, and execution packet ownership here. Keep branch/base/commit policy in `execution-handoff.md` and remote policy in `remote-delivery.md`.
- Treat each approved planning gate as a phase approval commit boundary: commit the approved artifacts and ledger/log updates before starting the next phase.
- Delegate approved issue implementation to `issue-implementation-loop`; it owns worktree reservation, scheduling, runtime state, worker dispatch, scoped waits, implementation review, recovery, and `PR_READY`.
- Do not implement issue work in the planning/grill context. If worker contexts are unavailable, stop before implementation.
- Do not publish issues, push, create PRs, merge, force push, deploy, change permissions, touch credentials, perform destructive actions, or incur billing without approved remote policy. Final PR merge is always human-only.

## Gates

- **Spec Gate**: present spec path, `Epic ID`, accepted decisions, non-goals, acceptance criteria, verification, remote policy, and stop conditions.
- **Issue Gate**: present local issues, blocker graph, dependency order, `実行可能/ブロック中` status, and acceptance criteria.
- **Execution Plan Gate**: present the normalized packet, capability preflight, write scopes, dependency graph, fallback policy, and local/remote policy.
- **Remote Gate**: before any external write, load `remote-delivery.md`, verify access, present the exact action set, and wait for explicit approval.

Explicit approval is required at each gate unless the user has already supplied an approved artifact and requested local-only implementation within the same scope.

After Spec Gate, Issue Gate, or Execution Plan Gate approval, commit the approved local artifacts before moving to the next phase. If the user explicitly delays the commit, record that exception in the ledger/log before continuing.

## Stop Conditions

Stop and ask before continuing if an `Epic ID` is ambiguous, dirty changes overlap planned write scope, blockers are cyclic, required skills are missing, execution would change approved scope, or a required external/high-risk action lacks current approval.

## Completion Report

Report spec/docs paths, `Epic ID`, local issue status, packet path, execution result, branch/worktree map from execution, verification, implementation review summary, ledger updates, skipped/performed remote actions, and residual risks.
