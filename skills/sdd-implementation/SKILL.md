---
name: sdd-implementation
description: Use when a repository change needs specification, planning, or local implementation through the Superpowers development lifecycle.
---

# SDD Implementation

Superpowers is the authoritative development methodology. Compose its current
skills; do not copy their process into a custom scheduler, worker packet schema,
runtime snapshot, event log, or resume protocol.

## First-Write Worktree Gate

Before any content or artifact write, perform read-only discovery and capture the original checkout canonical path, named `starting_branch`, immutable `starting_head_sha`, distinguishable staged/unstaged/untracked starting status, Git common directory/worktree registration, and Epic branch/path. Detached HEAD, default-branch inference, task-relevant uncommitted original content, branch collision, path collision, allocation failure, or ownership ambiguity is fail closed: return `BLOCKED` with zero content/artifact write and no original checkout fallback.

Create the planning worktree atomically from `starting_head_sha`; only the continuing controller/chat that won atomic allocation may reuse it. If two allocators select the same Epic, the loser must not attach to the existing worktree and returns `BLOCKED`. An independent chat, stale/foreign state, or HEAD/index/tracked/untracked state not attributable to the trusted tuple is `BLOCKED`. Allocation may change shared Git metadata only; never perform original checkout switch/reset/stash/clean/add/commit or content write.

Before the first writable dispatch, prove planning registration/common directory/branch/path, captured-SHA base, original branch/HEAD/status preservation, and that repository root, CWD, every relative or absolute writable artifact path, and the first transient Research Report resolve inside the planning worktree. Reject stale path or escape path. The original checkout must not remain in a writable root, fallback root, CWD, or artifact destination.

## Planning Controller

Before the Implementation Stage, the main session is the Planning Controller.
It owns Human dialogue, the current question, small Decision Record updates,
approval state, stage routing, and evaluation of each Control Return. Do not
inspect source code, broad repository content, full artifacts, diffs, or raw
command output.

Use isolated fresh-context dispatch for every Pre-Implementation Worker. Do not
inherit the parent conversation. Pass canonical paths, applicable constraints,
the current question, and missing task-local facts only. If isolated dispatch
with an explicit model is unavailable, return `BLOCKED`; do not move research
or authoring into the Planning Controller.

For a change request or incomplete specification, read
`references/research-stage.md` before repository investigation. Research,
Spec Synthesis, Spec Review, Plan Authoring, and Plan Review must each use a fresh worker.
Do not require context telemetry, manual compaction, or a strict word-count validator.

Read `references/planning-context.md` only when entering a pre-implementation
decision, synthesis, review, or plan-authoring stage. Keep stage details out of
this entrypoint.

## Dependency Preflight

Before entering a selected route, use the active runtime's skill discovery to verify applicable dependencies and required capabilities.
Check the Superpowers lifecycle skills for every route.
Check `grill-with-docs` when the Spec Stage requires it.
Check `llm-wiki` when a knowledge root exists.

If a required family is missing, return the matching result:

- `BLOCKED: missing Superpowers lifecycle dependency`
- `BLOCKED: missing grill-with-docs dependency`
- `BLOCKED: missing llm-wiki dependency`

## Route By Input Maturity

Do not repeat a completed stage.

- **Change request or incomplete specification:** enter the Planning Controller,
  dispatch the fresh Research Worker defined by `references/research-stage.md`,
  then use `superpowers:brainstorming` and the Spec Stage below. Require Human
  written-spec approval before planning.
  Preserve approved and complete portions of an incomplete specification.
  Use Grill with Docs only for unresolved material decisions.
- **Human-approved current specification:** verify authority, applicability,
  requirements, and acceptance criteria, then use `superpowers:writing-plans`.
  Return to the Spec Stage only for a material conflict.
- **Repository-ready `ready` plan bound to the current specification:** verify
  the approved North Star identity, approved Written Spec identity, baseline
  binding, current-tree compatibility, independent review verdict `ready`, and
  repository validation evidence, then use
  `superpowers:subagent-driven-development`. A plan with `issues_found`, stale
  evidence, absent evidence, or any disposition other than `ready` must not
  enter the Implementation Stage.

## Spec Stage

**REQUIRED SUB-SKILL: Use superpowers:brainstorming.**

When a knowledge root exists and prior decisions, terminology, architecture, or
implementation can materially affect the specification, query it first.
Do not force a ceremonial query when no relevant knowledge exists.

**REQUIRED SUB-SKILL: Use grill-with-docs** when no Human-approved written specification exists, material ambiguity remains, or repository evidence conflicts with the proposed specification.

Ask one decision question at a time. Investigate repository facts instead of
asking the Human. Confirm shared understanding for each material decision.
Do not silently replace Grill with Docs with ad hoc questioning. If Grill with
Docs is required but unavailable, return `BLOCKED`. For a complete,
Human-approved current specification, record the stage as `not_needed`.

Create and self-review the written specification using the current Superpowers
brainstorming contract. Require Human approval before planning.

## Durable Knowledge

**REQUIRED SUB-SKILL: Use llm-wiki** when a knowledge root exists.

Use the repository topology and write boundary for these checkpoints:

1. Human-approved written specification.
2. Reviewed implementation plan.
3. Implementation closeout.

Keep canonical pages, `knowledge/index.md`, and `knowledge/log.md` synchronized.
Do not create parallel `CONTEXT.md` or `docs/adr/` stores. Keep runtime ledgers,
worker reports, review transcripts, diffs, test logs, agent IDs, and concrete
runtime routing outside the wiki.

No knowledge root is `not_applicable`; do not bootstrap one implicitly. An
existing knowledge root with unresolved authority, target, write boundary,
index/log sync, or validation is `BLOCKED`.

## Plan Stage

**REQUIRED SUB-SKILL: Use superpowers:writing-plans.**

Create an executable plan from the approved specification. Apply any
repository-required fields from `references/plan-contract.md` without copying
the upstream methodology. The Planning Controller dispatches a fresh Plan
Author, then a fresh independent Plan Reviewer. Route `needs_repair` back to a
fresh author/reviewer loop, route only an evidenced material spec conflict as
`needs_decision`, and route a non-decision blocker as `blocked`. Only `ready`
enters the Implementation Stage. Missing remote publication authorization does
not affect local plan readiness. Human North Star and Written Spec authority is
preserved; the implementation plan is agent-authored and independently reviewed.
Persist the reviewed plan through the Durable Knowledge contract.

## Implementation Stage

**REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.**

Main session is the orchestrator. It retains state, paths, routing, waits, and
short verdicts. Never implement production code, perform task review, or author
wiki content in the main session.

Use fresh implementers and independent reviewers. Do not inherit the parent
conversation. Use the runtime's isolated fresh-context dispatch mechanism.
Pass durable paths and missing task-local facts only.

Run SDD sequentially. Review only requirements fit, material simplicity, and
material current risk. A blocking finding needs evidence of a requirement gap,
scope excess, observable regression, or concrete current risk. Do not block on
style, formatting, future-only concerns, scope-external hardening, or equivalent
preferences. Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before closeout.

## Epic Parallel Issue Adapter

Default execution remains sequential canonical SDD. This migration itself runs sequentially in its existing Epic planning worktree. For a later Epic, adapter eligibility is an agent / repository-owned eligibility verdict based on a repository-ready issue plan, proven independent issue units, and current dependency / conflict evidence; it does not require a Human choice. Each issue execution unit has exactly one branch/worktree/session/plan/artifact workspace and exactly one writer. Within an issue, never dispatch concurrent implementers. Do not advance to the next task until its task review and any canonical fix are complete.

The adapter owns readiness/dependency/conflict verdicts, allocation/wait/result routing, actual-result revalidation, and single-writer serialized integration; it does not schedule issue-internal tasks or alter canonical task/review/fix/ledger/recovery authority. Unknown expected write overlap, dependency, shared mutable resource, pinned-base ancestry, or integration assumption returns to sequential handling. Agent-repairable evidence gaps remain agent-owned. Only an evidenced material North Star / Written Spec conflict returns to Human authority.

Before integration-ready and before every serialized integration, derive actual commit range, actual changed paths, semantic/resource assumptions, and every required issue/task commit from existing Superpowers ledger and Git history; revalidate them against sibling results and current target. A blocked or unreviewed result is not integration-ready. Reject an issue tip that cannot prove every required issue/task commit reachable, including squash or selected cherry-pick loss. Integrate one ready issue at a time; clean textual merge is insufficient and partial integrated state is not completion.

`starting_branch` is PR base and `integration_branch` is PR head and integration target. If target head is unchanged, retain captured ancestry. On descendant advance, revalidate against the same named branch and refresh integration ancestry and combined verification. On non-descendant rewrite, material divergence, or unknown, return `BLOCKED`; never silently retarget. After every required issue/task commit is reachable, run fresh combined verification and exactly one canonical whole-branch review for `starting_branch...integration_branch`. A finding follows one fixer, exactly one scoped re-review, and adjudication/stop; no second fix wave or repeated whole-branch review. Return `LOCAL_COMPLETE` only after original-checkout preservation. Remote publication needs separate explicit authorization and a valid remote PR base.

## Runtime Model And Effort

Follow the current Superpowers SDD Model Selection contract. Every subagent dispatch must state its model. Let Superpowers choose the relative tier for the task and resolve that tier to a concrete model available in the active runtime.
Do not maintain a second role-to-model table.

An explicit user runtime model override takes precedence over upstream model-tier resolution.

Apply reasoning effort as an independent runtime-only overlay when supported:

| Superpowers task class | Reasoning effort |
| --- | --- |
| Mechanical task or small scoped re-review | `low` |
| Multi-file integration, normal debugging, or task review | `medium` |
| Architecture-sensitive or high-risk task, or final review | `high` |

Task complexity and current risk take precedence over role defaults.
A high-risk task review uses `high`, regardless of its role default.
The shared default effort vocabulary is limited to `low`, `medium`, and `high`.

An explicit user runtime effort override takes precedence over the default effort overlay.
For a stuck fix, raise effort one available step before following Superpowers
model escalation.

When the active runtime has no independent effort control, record `not_supported` and continue with Superpowers model selection. Lack of independent effort control does not block the flow. Lack of isolated dispatch with an explicit model is `BLOCKED`.

Persist no concrete model, effort, provider, availability, agent ID, or
run-specific resolution in the specification, plan, wiki, ledger, or schema.

## Runtime Capability Boundary

Map isolated dispatch, explicit model, optional effort, wait, and resume to the
active runtime's capabilities. Detect the fresh worker/reviewer dispatch
mechanism, model selector, optional effort control, and wait/resume mechanisms
before entering SDD. Required isolated dispatch and explicit-model capabilities
are `BLOCKED` when absent; optional effort is `not_supported` when absent.
Synchronous dispatch that returns a completed result is a valid
result-collection mechanism. Asynchronous dispatch requires both wait and
resume capabilities. If neither synchronous result collection nor asynchronous
wait/resume is available, return `BLOCKED`.

Do not hard-code host tool names or model catalogs. Do not silently fall back to
main-session implementation or an old loop skill when required SDD capability
is absent.

## Implementation Closeout

Dispatch a fresh knowledge worker and use the Durable Knowledge contract.
Validate the wiki before final review.

## Final Whole-Branch Review

After closeout, run the Superpowers final whole-branch review over code, tests,
the approved specification, reviewed plan, and knowledge artifacts. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.

Do not perform any remote write without separate explicit authorization.
This includes push, PR, merge, release, live install, issue, comment, and project changes.
Do not push, create a PR, merge, release, or install live without separate
explicit authorization. Report blockers, residual material risk, and unperformed
remote actions briefly.
