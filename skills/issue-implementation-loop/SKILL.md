---
name: issue-implementation-loop
description: Use when implementing approved repository issues after spec, acceptance criteria, and issue decomposition are approved.
---

# Issue Implementation Loop

## Overview

Run approved repository work items from a normalized input packet to local `PR_READY`. Keep one execution coordinator context responsible for global state, blocker release, human requests, review decisions, and final reporting. The planning/grill session must not implement issue work. Dispatch workers or reviewers only for isolated implementation and review tasks.

Do not create user-owned Codex threads. If worker contexts are unavailable, stop before implementation. If parallel workers are unavailable, continue through approved serial fallback only as bounded worker-context jobs.

Use `grill-to-pr-loop` before this skill for design interrogation, PRD/spec creation, and issue decomposition.

Read `references/mental-model.md` when you need the first role-boundary page for coordinator, worker, reviewer, runtime state, local ledger, and remote delivery responsibilities.

## Applicability

Use this skill only when a normalized approved packet exists, the Execution Envelope requires worker-only execution, worker context is available, and the issue can stay inside its assigned write scope.

Do not use this skill for small one-off edits, direct implementation without a packet, unapproved or changing scope, design interrogation, issue creation, or cases where the coordinator must implement to make progress.

The coordinator must not implement issue work. It owns global state, scheduling, waits, review decisions, blocker release, and final reporting; workers own bounded issue changes and verification evidence.

## Immediate Guard

Before prepare, execute, resume, status, or deliver actions, run:

```bash
python3 <skill-dir>/scripts/check_capabilities.py --input <packet.json> --json
```

If no packet exists, omit `--input` only for status/recovery inspection. Stop before execution when git, repo, or packet validation fails. Missing `tdd` or `requesting-code-review` requires an approved equivalent or manual fallback in the Execution Envelope.

## Mode Router

Always read `references/core.md`. For operation-specific context, use `scripts/select_operation.py` and `context-contract.toml`; the contract file is the single read-set source. Do not list or load every reference by default.

## Required Rules

- Treat the input packet as approved scope; do not redesign issues or acceptance criteria here.
- Require `execution_policy.worker_context_required=true`, `coordinator_may_implement=false`, and `serial_fallback_mode=worker_context_only`.
- Keep coordinator runtime state out of tracked issue branches; default to `$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/`.
- Reserve branch/worktree paths for every approved issue before execution; create physical worktrees only when runnable.
- Require `epic_base`, `base_policy`, and typed dependency edges; require `epic_base.branch_state` for `batch_issue_prs`.
- Recompute runnable work after every event. A wave is a launch cohort, not a completion barrier.
- Use `tdd` or an approved equivalent for behavior changes, bug fixes, behavior-bearing refactors, and tests.
- Send workers bounded paths-first packets; do not paste full specs or ledgers when durable paths suffice.
- Keep workers inside write scope; only the coordinator writes envelope, runtime snapshot, event log, and shared ledger unless explicitly assigned.
- Require a local scoped commit before review, blocker release, issue completion, or any success status.
- Run issue-scoped implementation review before issue completion, blocker release, or PR readiness.
- Run at most two issue implementation review cycles. Fix Critical and Important in-scope findings, or stop for explicit human risk acceptance after the second review still finds in-scope issues.
- Scope human waits to the smallest affected set; use `epic` only for envelope/DAG/runtime corruption, shared-base safety, credential/security incidents, or external contract changes affecting every issue.
- Never perform GitHub issue creation, push, PR creation, issue PR merge, force push, deployment, destructive action, billing, credential, or permission changes without approved remote policy. Never merge the final PR; final merge is human-only.

## Completion Report

Report Epic ID, packet/envelope paths, runtime root, issue status table, blocker releases, branch/worktree map, verification, review ranges and verdicts, PR-ready branches, human requests, skipped/performed remote actions, and residual risks.
