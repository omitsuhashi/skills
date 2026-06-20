---
name: grill-to-pr-loop
description: Use when a user requests a repeatable development operating mode for large designs involving Grill with Docs, PRD/spec synthesis, issue decomposition, git worktrees, TDD, goal loops, issue implementation review, or PR review.
---

# Grill to PR Loop

## Overview

Coordinate a repo change from design interrogation to PR review without skipping human gates. Keep issue management local-first; use GitHub issues only as an optional remote mirror/tracking layer after approval. Treat `grill-with-docs` as the required front door: if it is unavailable, stop instead of approximating the workflow.

This skill is an orchestrator. Do not duplicate the detailed behavior of the existing sub-skills:

- **Required front door:** use `grill-with-docs` for design interrogation and durable design docs.
- **PRD/spec synthesis:** use `to-prd` when turning the approved conversation and docs into product requirements or a spec packet.
- **Issue decomposition:** use `to-issues` for vertical-slice draft breakdown and user quiz/review.
- **Implementation discipline:** use `tdd` when a Goal loop changes behavior or fixes bugs.
- **Issue implementation review:** use `superpowers:requesting-code-review` when available to review each issue implementation against its local issue, spec, acceptance criteria, write scope, and verification evidence before completion.

## Immediate Guard

Run the prerequisite check before design, issue, worktree, or PR actions:

```bash
python3 <skill-dir>/scripts/check_prereqs.py
```

If it reports missing `grill-with-docs`, stop and tell the user the skill must be installed first. Do not fall back to plain `grill-me` for this workflow because the required docs are part of the contract.

If it reports missing `requesting-code-review`, do not fail during intake. Before implementation completion, either use an available equivalent code-review subagent with the same review packet or stop and ask whether to install the skill or approve a manual review fallback.

Read `references/workflow-contract.md` when executing the workflow, resuming from a middle state, creating multiple worktrees, or preparing a Goal prompt.

## Required Operating Rules

- Load and follow repo instructions first: `AGENTS.md`, local skill routers, specs, tests, and CI docs.
- Preserve user work. Inspect `git status --short`, `git worktree list`, existing branch names, and proposed worktree paths before changing branches or creating worktrees.
- Assign a stable `Epic ID` before local issue decomposition or worktree planning. Derive it from the approved spec topic when the user did not provide one, present it for approval, and use it in every branch/worktree name so multiple epics can run in parallel without issue ID collisions.
- Keep design decisions in durable docs, not only chat. Prefer repo-local conventions; otherwise write a spec under `docs/grill-to-pr-loop/`.
- Use `to-prd` for PRD/spec synthesis when it is installed. Keep output local-first until this skill's remote-write gate has passed.
- Split work into independently reviewable vertical slices in a local issue ledger. Write issue titles, headings, labels, status values, and prose in Japanese; keep IDs, paths, commands, code symbols, and external error text unchanged.
- Build an explicit blocker graph for local issues. Track `ブロック元`, `ブロック先`, and `実行可能/ブロック中` status before any worktree or Goal loop starts.
- Use `to-issues` only for draft breakdown and quiz/review if installed; do not run its publish phase unless this skill's GitHub mirror gate has passed.
- Mirror approved local issues to GitHub only when GitHub access is available, the repo has a GitHub remote, and the user explicitly approves remote issue creation.
- Whenever a GitHub issue is created, a PR is opened, or an issue is completed, update the local issue ledger in the same step so local tracking reflects the remote reality.
- Create one epic-scoped branch and one epic-scoped worktree per approved `実行可能` issue. Do not create worktrees for `ブロック中` issues until their blockers are complete or the user explicitly overrides the dependency.
- Before the Worktree Map Gate, check proposed branch names and worktree paths for collisions. If a collision exists, revise the `Epic ID` or issue slug with user approval; do not silently add numeric suffixes.
- Before starting implementation, compute parallel waves from approved `実行可能` issues. Dispatch every issue in the same wave in parallel when the platform supports parallel agents or background threads.
- Before dispatching a wave, display every issue's worktree path in the parent session so the user can see where each task is running.
- If parallel execution is requested but the platform cannot start independent agents/threads, stop and ask whether to run the wave serially or move to a platform that can run it in parallel.
- Pause for human approval after spec, issue breakdown, proposed worktree map, and initial verification are ready.
- After approval, run Goal loops by parallel wave with short prompts and links to durable docs.
- Use `tdd` in each Goal loop when implementation changes behavior, fixes bugs, or refactors behavior-bearing code.
- Before marking a local issue complete, releasing its blockers, or creating a PR for it, run the Issue Implementation Review Gate from `references/workflow-contract.md`. PR review, CI checks, or later review monitoring do not replace this issue-level review.
- Fix Critical and Important issue implementation review findings before proceeding, unless the human explicitly accepts the risk and the local ledger records that decision.
- Before GitHub issue creation, push, PR creation, or any external write, get explicit user approval, then use the relevant GitHub/PR skill or repo convention. Never hide remote writes, permission, billing, or credential actions inside this workflow.

## State Machine

1. **Intake**: Confirm repo root, active branch, dirty state, target outcome, `Epic ID`, and whether existing spec/issues/PRs already exist.
2. **Grill**: Use `grill-with-docs` to resolve design choices and produce docs. If the user already has docs, review them for unresolved decisions before continuing.
3. **Spec / PRD**: Use `to-prd` when available to synthesize the approved conversation and Grill with Docs artifacts into a concise PRD/spec packet with accepted decisions, non-goals, acceptance criteria, verification commands, and rollback/stop conditions.
4. **Spec Gate**: Present the spec and wait for explicit approval before issue decomposition.
5. **Local Issues**: Use `to-issues` when available to draft Japanese vertical-slice issues with acceptance criteria and a blocker graph. Write them to a local issue ledger and ask for approval of granularity, blocker edges, and dependency order.
6. **Optional GitHub Mirror**: If GitHub access is available and the user approves, create GitHub issues from the approved local issues and immediately record the remote issue URLs in the local ledger. If GitHub is unavailable or not approved, continue local-only.
7. **Proposed Worktree Map**: Propose epic-scoped branch/worktree paths for approved `実行可能` local issues before running `git worktree add`. Verify the proposed names against existing branches, `git worktree list`, and filesystem paths.
8. **Worktree Gate**: Wait for explicit approval of the proposed worktree map, then create isolated worktrees. Record Epic ID, local issue, optional remote issue, branch, worktree path, base commit, owner/agent, and status.
9. **Initial Verification Gate**: Run available lightweight verification, summarize the spec/issues/worktree map, and ask the user to approve starting implementation loops.
10. **Parallel Goal Loop Scheduler**: Build the first runnable wave from approved `実行可能` issues with no dependency or write-scope conflicts. Display the wave's issue IDs, branches, and worktree paths in the parent session, then dispatch all wave members in parallel. When a worker reports implementation complete, run the Issue Implementation Review Gate before ledger completion, blocker release, or PR readiness.
11. **Issue Implementation Review Gate**: Review each completed issue implementation with `superpowers:requesting-code-review` when available, using the local issue, spec, acceptance criteria, write scope, verification results, and base/head SHA range. Fix or explicitly accept Critical and Important findings, then update the local ledger with `実装レビュー`, `レビュー範囲`, and `レビュー結果`.
12. **PR Review**: After issue implementation review passes and after explicit approval for remote writes, open draft or ready PRs according to repo convention and immediately record the PR URL/status in the local ledger. If a remote issue exists, link the PR to it with the repo's preferred `Closes` or `Refs` syntax. Monitor checks/review comments, address actionable feedback, and report remaining risks.

## Goal Prompt Contract

For each issue, keep the prompt short and point at source artifacts:

- Local issue identifier and title.
- Epic ID used for branch and worktree naming.
- GitHub issue URL or number if a remote mirror was created.
- Wave ID and whether the issue is running in parallel or serial override mode.
- ブロッカー状態: `実行可能` または `ブロック中`、および `ブロック元` のIssue ID.
- Spec path and any ADR/glossary paths from Grill with Docs / `to-prd`.
- Worktree path and branch.
- Exclusive write scope for this worker/agent, and any coordinator-owned files it must not edit directly.
- Required behavior and acceptance criteria.
- Verification commands to run fresh after docs/progress updates.
- Issue implementation review packet: reviewer skill or approved fallback, exact review prompt, base/head SHA range, local issue/spec paths, acceptance criteria, write scope, and verification evidence.
- Local ledger path and the exact ledger fields that must be updated after GitHub issue creation, issue implementation review, PR creation, and issue completion.
- Stop conditions requiring the human.

Do not paste the full spec into the Goal prompt when a durable path exists.

## Stop Conditions

Stop and ask the user before continuing if:

- `grill-with-docs` is missing.
- The repo has dirty changes that overlap with the planned branches.
- The Epic ID is missing, ambiguous, not approved, or collides with another active epic's branch/worktree namespace.
- A proposed branch name or worktree path collides with an existing branch, existing worktree, or filesystem path, and the user has not approved a revised Epic ID or issue slug.
- The blocker graph is cyclic, ambiguous, or makes parallel work unsafe.
- A Goal loop is requested for a `ブロック中` issue without explicit override.
- Issue implementation review is required but `requesting-code-review` or an equivalent review subagent is unavailable and the user has not approved a manual fallback.
- Issue implementation review returns Critical or Important findings that are not fixed or explicitly accepted by the human.
- The user requested GitHub issue/PR linkage but GitHub access, repo remote, or permission is unavailable; ask whether to continue local-only.
- Tests fail in a way unrelated to the issue and no local contract explains it.
- A GitHub issue, PR, push, credential, permission, production, billing, or external-write action is required and has not been approved.
- Human review rejects the spec, issue split, worktree map, or implementation result.

## Completion Report

End with:

- Spec/docs paths.
- Epic ID.
- Local issue list and status.
- GitHub issue links when created, or explicit local-only reason.
- Worktree/branch map.
- Parallel wave execution summary, including every issue's worktree path shown in the parent session.
- Issue implementation review summary, including reviewer used or manual fallback, review range, verdict, fixed findings, and accepted residual risks.
- Local ledger updates made for GitHub issue creation, issue implementation review, PR creation, and issue completion.
- Verification commands and results.
- PR URLs or explicit reason PR creation was not done.
- Residual risks and unresolved human decisions.
