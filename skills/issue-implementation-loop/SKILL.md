---
name: issue-implementation-loop
description: Use when implementing approved repository issues after spec, acceptance criteria, and issue decomposition are approved.
---

# Issue Implementation Loop

## Overview

Run approved items to local `PR_READY`. Keep one execution coordinator context; the planning/grill session must not implement issue work. Workers/reviewers own isolated tasks.

Do not create user-owned Codex threads. Without workers, stop; serial fallback uses bounded worker-context jobs.

Use `grill-to-pr-loop` first for design, PRD/spec creation, and issue decomposition.

Read `references/mental-model.md` for the first role-boundary page.

## Applicability

Use this skill only when a normalized approved packet exists, worker context is available, and scope fits.

Do not use this skill for small one-off edits, direct work without a packet, unapproved or changing scope, design, or issue creation.

The coordinator must not implement; it coordinates state, scheduling, waits, review, and blockers.

## Immediate Guard

Before prepare, execute, resume, status, or deliver actions, run:

```bash
python3 <skill-dir>/scripts/check_capabilities.py --input <packet.json> --json
```

Any ok=false blocks state changes. Read-only status/recovery ignores only unsupported approved_spec_seal; other failures block. PLATFORM_UNSUPPORTED: Codex and Hermes stop; no unsafe fallback. Missing tdd/review needs an approved equivalent.

## Mode Router

Always read `references/core.md`; use `scripts/select_operation.py` and `context-contract.toml` for the operation read-set.
At 65% session pressure or phase exit, read `references/context-compaction.md`.

## Required Rules

- Treat the packet as approved scope; do not redesign issues or criteria.
- At prepare, dispatch/fix, review, resume/rebuild, completion, and delivery, freshly verify the same active `approved_spec_binding`; read-only status may diagnose without advancing.
- Use core's three-outcome drift lifecycle: restoration, non-spec reseal, or human Spec Gate reseal.
- Require `execution_policy.worker_context_required=true`, `coordinator_may_implement=false`, and `serial_fallback_mode=worker_context_only`.
- Keep runtime state under `$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/`, outside issue branches.
- Reserve every issue branch/worktree before execution; require `epic_base`, `base_policy`, typed dependencies, and `epic_base.branch_state` for `batch_issue_prs`.
- Recompute runnable work after every event; a wave is not a completion barrier.
- Use `tdd` or an approved equivalent, fresh verification, and a scoped commit before review or success.
- Send bounded paths-first packets. Keep workers in write scope; only the coordinator writes envelope/runtime/events/shared ledger unless assigned.
- Keep ledger and human-facing report updates in Japanese; preserve stable IDs, paths, commands, schema keys, and external issue/PR references.
- Review before completion/blocker release/`PR_READY`; fix in-scope Critical/Important findings within two cycles or seek human risk acceptance.
- Scope human waits narrowly; reserve `epic` for shared corruption/safety/contract failures.
- Remote writes require approved policy; final merge is human-only.

## Completion Report

Report Epic ID, packet/envelope/runtime paths, issue and branch status, verification/reviews, blockers, human requests, remote actions, and residual risks.
