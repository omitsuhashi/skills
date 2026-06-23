---
name: issue-implementation-loop
description: Use when implementing one or more approved local or remote repository issues with dependency-aware scheduling, isolated git worktree reservations, verification, issue-scoped implementation review, resumable runtime state, and scoped human escalation that must not block unrelated work. Do not use for initial design interrogation, PRD/spec creation, or issue decomposition.
---

# Issue Implementation Loop

## Overview

Run approved repository work items from an input packet to `PR_READY` without turning every human wait into an epic-wide stop. Keep one parent coordinator responsible for global state; dispatch workers or reviewers only for isolated implementation and review tasks.

This skill starts after design, PRD/spec, acceptance criteria, and local issue decomposition are approved. Use `grill-to-pr-loop` for the upstream design-to-issue workflow.

## Immediate Guard

Before prepare, execute, resume, status, or deliver actions, run:

```bash
python3 <skill-dir>/scripts/check_capabilities.py --input <packet.json> --json
```

If no packet exists yet, omit `--input` only for status/recovery inspection. Stop before execution when git is unavailable, the repo is invalid, or the normalized input packet is invalid. Missing `tdd` or `requesting-code-review` does not automatically fail preflight, but the Execution Envelope must approve an equivalent or manual fallback before implementation can complete.

## Mode Router

Always read `references/core.md` first. Then load only the references for the current mode:

- `prepare`: read `references/execution-envelope.md`, `references/dependency-contract.md`, and `references/worktree-lifecycle.md`.
- `execute`: read `references/scheduler.md`, `references/worker-contract.md`, `references/review-gate.md`, `references/human-wait.md`, and `references/runtime-state.md`.
- `resume`: read `references/runtime-state.md` and `references/recovery.md`.
- `status`: read `references/runtime-state.md` and `references/scheduler.md`.
- `deliver`: read `references/remote-delivery.md`.

Do not load every reference by default.

## State Machine

1. **Prepare**: Validate the normalized input packet, check capabilities, build an Execution Envelope, reserve all issue branch/worktree names, and ask for approval of the envelope.
2. **Execute**: Reconcile runtime/git state, compute runnable work after every event, dispatch available implementation/review/fix work, persist coordinator-owned events and snapshots, and continue unrelated work during scoped human waits.
3. **Review**: Before any issue becomes complete, releases blockers, or becomes PR-ready, run the Issue Implementation Review Gate.
4. **Resume**: Rebuild state from event log when needed, compare snapshot, git worktrees, branch heads, reports, and leases, then continue from the first safe action.
5. **Status**: Report runnable, running, reviewable, fixable, waiting-human, blocked, and PR-ready sets.
6. **Deliver**: After explicit remote-write approval, hand exact PR-ready branches and issue links to the repo's GitHub/PR workflow. The default end state is local `PR_READY`.

## Required Rules

- Treat the normalized input packet as approved scope. Do not redesign issues or acceptance criteria inside this skill.
- Use the same parent coordinator for global state, blocker release, human requests, and final reporting.
- Keep central runtime state out of tracked issue branches. Default to `$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/`.
- Reserve branch and worktree paths for every approved issue before execution. Create physical worktrees only when the issue is runnable.
- Require every work item to declare `base_policy`; use an integration work item/branch instead of merging multiple blocker heads ad hoc.
- Recompute runnable work after every event. A wave is a launch cohort, not a completion barrier.
- Use `tdd` or an approved equivalent when implementation changes behavior, fixes bugs, refactors behavior-bearing code, or adds tests.
- Keep workers inside their issue write scope. Workers and reviewers must not edit coordinator-owned runtime state, ledger, or envelope files unless the issue explicitly owns those files.
- Run issue-scoped implementation review before issue completion, blocker release, or PR readiness.
- Fix Critical and Important in-scope review findings, or stop for explicit human risk acceptance recorded by the coordinator.
- Default human wait scope is `issue`; use `epic` only for envelope corruption, DAG corruption, shared-base safety, credential/security incidents, or external contract changes affecting every issue.
- Remote failures must not stop local implementation/review lanes unless the approved envelope makes that remote action a dependency.
- Never perform GitHub issue creation, push, PR creation, merge, force push, deployment, destructive action, billing, credential, or permission changes without explicit current approval.

## Scripts

- `scripts/check_capabilities.py`: repo/git/packet/skill capability preflight.
- `scripts/validate_input_packet.py`: validate normalized work-item packet.
- `scripts/validate_execution_envelope.py`: validate envelope schema, dependency references, cycles, and reservation uniqueness.
- `scripts/compute_next_actions.py`: compute runnable/reviewable/fixable/waiting sets without a wave barrier.
- `scripts/validate_runtime_state.py`: validate runtime snapshot shape and human request scopes.
- `scripts/rebuild_runtime_state.py`: rebuild snapshot from append-only events and ignore duplicate event IDs.
- `scripts/reconcile_git_state.py`: compare envelope reservations with local branches and worktrees without mutating git state.

## Stop Conditions

Stop and ask the human only for the smallest affected scope when:

- The input packet or approved envelope is invalid.
- A branch/worktree reservation collides and no approved revised reservation exists.
- The blocker graph is cyclic or ambiguous.
- Execution needs to change acceptance criteria, dependency edges, base strategy, write scope, retry policy, review fallback, or remote policy.
- A worker needs out-of-scope edits.
- Runtime snapshot, event log, or git state cannot be reconciled.
- Required reviewer capability or approved fallback is unavailable at review time.
- Critical or Important in-scope review findings remain unresolved without explicit risk acceptance.
- Any external write or high-risk action lacks explicit approval.

## Completion Report

End with the Epic ID, input packet path, envelope path/revision, runtime state root, issue status table, blocker releases, worktree/branch map, verification results, implementation review ranges and verdicts, PR-ready branches, human requests, remote actions performed or skipped, and residual risks.
