---
name: grill-to-pr-loop
description: Use when a user wants an end-to-end repository change beginning with design interrogation and durable design docs, followed by spec/PRD synthesis, issue decomposition, dependency-aware implementation through issue-implementation-loop, and optional PR delivery.
---

# Grill to PR Loop

## Overview

Coordinate a repo change from design interrogation to PR delivery without skipping durable docs or approval gates. This is now a composition skill: it owns design, spec, issue decomposition, normalized execution input, and optional remote delivery coordination. It delegates approved issue implementation, worktree lifecycle, scheduling, runtime state, scoped human wait, and issue-scoped implementation review to `issue-implementation-loop`.

Treat `grill-with-docs` as the required front door. If it is unavailable, stop instead of approximating the workflow.

## Immediate Guard

Run the prerequisite check before design, issue, execution, or PR actions:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase planning
```

Before handing work to execution, run:

```bash
python3 <skill-dir>/scripts/check_prereqs.py --phase execution
```

If planning reports missing `grill-with-docs`, stop. If execution reports missing `issue-implementation-loop`, stop before implementation and install or add the execution skill. GitHub authentication is optional and required only for approved remote writes.

Read `references/workflow-contract.md` when executing the workflow, resuming from a middle state, preparing an execution packet, or coordinating PR delivery.

## Responsibilities

This skill owns:

- `grill-with-docs` design interrogation and durable docs.
- PRD/spec synthesis with `to-prd` when installed.
- Japanese local issue decomposition with `to-issues` when installed, local-first and without remote publication unless approved.
- Stable `Epic ID` selection.
- Local issue ledger as the planning source of truth.
- Optional GitHub issue mirror proposal and explicit remote-write gate.
- Normalized input packet for `issue-implementation-loop`.
- Final composition report and optional PR delivery coordination after execution returns `PR_READY` candidates, including issue PRs to the approved epic base branch and final PR creation.

This skill does not own:

- worktree lifecycle
- runtime state / event log / leases
- runnable calculation
- worker dispatch policy
- scoped human wait mechanics
- issue implementation review/fix loop
- recovery/reconciliation of execution state

Load `issue-implementation-loop` for those execution responsibilities.

## State Machine

1. **Intake**: Confirm repo root, active branch, dirty state, target outcome, candidate `Epic ID`, existing specs/issues/PRs, and local-only vs possible remote delivery.
2. **Grill**: Use `grill-with-docs` to resolve design choices and produce durable ADR/glossary/design docs. If the user already provided docs, review them for unresolved decisions before continuing.
3. **Spec / PRD**: Use `to-prd` when available to synthesize accepted decisions, non-goals, acceptance criteria, verification commands, rollback/stop conditions, and issue strategy.
4. **Spec Gate**: Present spec path, `Epic ID`, accepted decisions, non-goals, acceptance criteria, verification, and stop conditions. Wait for explicit approval before issue decomposition unless the user has already provided an approved spec and requested direct implementation.
5. **Local Issues**: Use `to-issues` when available for draft vertical slices and quiz/review. Keep local issue titles, headings, labels, status values, and prose in Japanese.
6. **Issue Gate**: Present issue list, blocker graph, `実行可能/ブロック中` status, dependency order, and acceptance criteria. Wait for approval before GitHub mirroring or execution planning.
7. **Execution Plan Packet**: Build a normalized input packet for `issue-implementation-loop`, including spec path, approved revision/hash when available, work items, acceptance criteria, non-goals, verification, write scopes, dependency edges, and delivery intent.
8. **Execution Plan Gate**: Run planning/execution prerequisites. Present the packet, capability preflight summary, remote policy, and whether serial fallback or manual review fallback is approved. Wait for explicit approval before execution unless the user has already authorized implementation and all actions remain local.
9. **Issue Implementation Loop**: Load and follow `issue-implementation-loop` for envelope creation, worktree reservation, scheduling, verification, issue implementation review, scoped human waits, recovery, and `PR_READY` result.
10. **Optional PR Delivery**: After execution returns `PR_READY` candidates, use the approved remote policy. Issue PRs target `codex/<epic-id>/epic-base`; issue PR merge may be agent-run when guardrails pass. Final PRs target `main`, and final PR merge is always human-only.
11. **Completion Report**: Reconcile local ledger with execution output and any approved remote actions.

## Local-First Rules

- Preserve user work. Inspect `git status --short`, `git worktree list`, branch names, and proposed execution reservations before changing branches or creating worktrees.
- Keep design decisions in durable docs. In this repo, use `knowledge/wiki/syntheses/` for long specs and keep Goal prompts short.
- Use a stable lower-kebab-case ASCII `Epic ID` for ledger, packet, branch, worktree, and runtime namespace.
- Local issues are canonical; GitHub issues are optional mirrors after explicit approval.
- Update the local ledger whenever a GitHub issue, PR, issue implementation review, PR-ready state, or completion state changes.
- Do not let `to-prd` or `to-issues` publish remotely before this skill's remote-write gate.
- Do not create GitHub issues for `下書き`, `差し戻し`, or `未解決` local issues.

## Branch / Base / Commit Policy

- Treat planning branches as optional workspace isolation, not as the execution source of truth.
- Treat Execution Envelope `epic_base.ref` as the per-epic base branch `codex/<epic-id>/epic-base` and `epic_base.sha` as its immutable initial SHA.
- Prefer issue branches named `codex/<epic-id>/<local-id>-<slug>`.
- Reserve one branch/worktree path per approved issue before execution; create physical worktrees only for runnable issues.
- Express downstream code dependencies through typed dependency edges and work item `base_policy`, not ad hoc merges into a shared mutable development branch.
- Use an approved integration work item/branch when a downstream issue needs multiple blocker heads.
- Before issue completion, blocker release, or `PR_READY`, run fresh verification, create/update a scoped local commit, and review the committed `BASE_SHA..HEAD_SHA` range.

## Normalized Execution Packet

Build a normalized input packet file for `issue-implementation-loop`; do not paste the packet body into the prompt when a file can hold it. Include:

- `schema_version`, `repo_root`, `epic_id`, optional `artifact_root`
- `spec.path`, plus approved revision/hash when available
- `work_items[]` with ID, title, source, acceptance criteria, non-goals, verification, write scope, and dependencies
- `delivery_intent`

Use `issue-implementation-loop/assets/templates/input-packet.json` for the concrete shape and `issue-implementation-loop/assets/schemas/input-packet.schema.json` for the field contract. Validate it through `issue-implementation-loop/scripts/validate_input_packet.py` before execution.

## Stop Conditions

Stop and ask the user before continuing if:

- `grill-with-docs` is missing.
- `issue-implementation-loop` is missing before execution.
- Dirty repo changes overlap with the planned issue write scopes.
- The `Epic ID` is missing, ambiguous, unapproved, or collides with another active epic namespace.
- Local issue blocker graph is cyclic or ambiguous.
- Issue granularity or dependency order is rejected.
- GitHub issue/PR linkage is requested but access, remote, auth, or permission is unavailable; ask whether to continue local-only.
- Execution requires changing approved spec, acceptance criteria, issue scope, or write scope.
- Execution reports unresolved Critical/Important in-scope findings without human risk acceptance.
- Tests fail in a way unrelated to the issue and no local contract explains it.
- Any external write, credential, permission, billing, production, destructive, push, PR, or merge action is required without approved remote policy. Final PR merge always requires current human action.

## Completion Report

End with:

- Spec/docs paths.
- Epic ID.
- Local issue list and status.
- GitHub issue links when created, or local-only reason.
- Execution packet path and `issue-implementation-loop` result.
- Worktree/branch map from execution output.
- Verification commands and results.
- Issue implementation review summary from execution output.
- Local ledger updates made for GitHub issue creation, issue implementation review, PR creation, and completion.
- PR URLs when created, or explicit reason PR creation was not done.
- Residual risks and unresolved human decisions.
