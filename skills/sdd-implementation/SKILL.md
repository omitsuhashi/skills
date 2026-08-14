---
name: sdd-implementation
description: Use when a repository change needs specification, planning, or local implementation through the Superpowers development lifecycle.
---

# SDD Implementation

Superpowers is the authoritative development methodology. Compose its current
skills; do not copy their process into a custom scheduler, worker packet schema,
runtime snapshot, event log, or resume protocol.

## Repository Change Entry

Enter every repository change through `sdd-implementation` before
brainstorming, writing-plans, using-git-worktrees, domain modeling,
implementation, or another writable supporting skill. A direct writable
supporting-skill entry returns exactly:

- `status`: `blocked`
- `artifact_path`: `none`
- `decision_requests`: `none`
- `material_risks`: `SDD First-Write Worktree Gate required`

Return without invoking the supporting skill, allocating a worktree, or writing
an artifact. Repository entry, containment, zero-write, and no-fallback rules
override conflicting downstream instructions.

## First-Write Worktree Gate

The primary/default checkout and its `main` branch are read-only for task work.
Capture its canonical path, `starting_branch`, `starting_head_sha`, and status
using read-only discovery. It receives no task content/artifact write and no task
commit.

Before the first content/artifact write, create or verify a task-linked worktree.
Prove its Git registration, common directory, branch, canonical path, and
separation from the original checkout. The controller mints one opaque task-owner
capability and requires the allocator to return that same object by identity;
path equality and branch naming are not ownership evidence. Bind the repository
root, CWD, and every writable path to that owned worktree. Revalidate returned
paths before accepting worker output or committing task changes.

Source and canonical durable repository writes remain inside the owned
task-linked worktree. Raw Research, review, worker, fix, and transcript handoff
uses a separate bounded capability whose destination resolves to a
repository-external task/session temporary path outside the repository root,
original checkout, owned worktree, and sibling worktrees. Do not pass an
external transient handoff path to the repository writer. Reject stale paths,
aliases, and escape paths before either kind of write.

One writable gate invocation materializes exactly one new artifact. Validate the
complete data-only plan, existing parent, absent target, and containment before
mutation; stage inside the verified worktree and atomically publish the artifact.
A multi-output plan or pre-existing target is `BLOCKED` before the writer because
this minimal evidence model does not claim rollback for replacements. Commit in a
separate invocation through the gate-owned data-only `git commit` plan and native
runner, with CWD equal to the verified worktree. Reject original or stale CWD
before runner invocation; do not accept an arbitrary callback.

A capability, dependency, path, ownership, permission, allocation, binding, or
expected runtime failure returns the four-field Control Return with `status: blocked`,
`artifact_path: none`, `decision_requests: none`, and the material blocker. Make
zero content/artifact writes, invoke no writer or downstream runner, and create
no report, spec, plan, or commit. Allocation may change shared Git metadata
only; it must preserve the original checkout fingerprint.

Never continue in the current or original checkout, select another workflow's
worktree, choose a fallback root, or fall back to an old loop. This is a
repository-owned SDD workflow boundary; it does not prohibit arbitrary manual
Git use outside that workflow.

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
If active discovery has no readable match, check the globally installed skill roots exposed by the runtime, including the cross-runtime alias `~/.agents/skills` when that alias is accessible. When `<root>/<required-skill>/SKILL.md` is readable, read it, use it, and continue the selected route.

Report a required family as missing only after active discovery and every accessible global-root check complete with no readable match. If discovery or a root/candidate read cannot be completed, report `BLOCKED: dependency preflight failed` together with the observed phase or path and underlying error. Do not report that failure as missing.
Check `keep-implementation-simple` as a required supporting Skill. Resolve one readable canonical `keep-implementation-simple/SKILL.md` path through that discovery and fallback, then read it fully before work. If its discovery, candidate inspection, path resolution, or read fails, return `BLOCKED: dependency preflight failed` with the failed phase, observed or attempted path, and underlying error before affected work.
Check the Superpowers lifecycle skills for every route.
Check `grill-with-docs` when the Spec Stage requires it.
Check `llm-wiki` when a knowledge root exists.

If a required family is missing, return the matching result:

- `BLOCKED: missing Superpowers lifecycle dependency`
- `BLOCKED: missing grill-with-docs dependency`
- `BLOCKED: missing llm-wiki dependency`
- `BLOCKED: missing keep-implementation-simple dependency`

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

## Transient Artifact Boundary

- Default raw handoff route: repository-external task/session temporary
- Repository-local scratch prerequisite: concrete operational reason and mechanical pre-write .gitignore coverage
- Allowed scratch state: ignored, untracked, unstaged, uncommitted
- Missing prerequisite route: fail closed to repository-external default
- Raw artifacts excluded from durable outputs: research report, worker report, fix report, raw review output, transcript, duplicate task content
- Durable summary fields: decision, finding, repair, verdict, evidence identity
- Durable summary surfaces: canonical specification, reviewed implementation plan, knowledge/log.md

| Stage | Raw handoff default | Durable summary route |
| --- | --- | --- |
| Research | repository-external task/session temporary | canonical specification |
| Spec | repository-external task/session temporary | canonical specification |
| Plan | repository-external task/session temporary | reviewed implementation plan |
| Implementation | repository-external task/session temporary | reviewed implementation plan |
| Task review | repository-external task/session temporary | reviewed implementation plan |
| Repair | repository-external task/session temporary | reviewed implementation plan |
| Integration | repository-external task/session temporary | reviewed implementation plan |
| Final review | repository-external task/session temporary | reviewed implementation plan |
| Knowledge closeout | repository-external task/session temporary | knowledge/log.md |

Resolve every normal-stage raw handoff to an OS/runtime-provided, task/session-bounded
temporary path outside the repository root, planning worktree, original checkout,
and sibling worktrees. Reject an unresolved or broad root, relative destination,
repository alias, stale binding, sibling path, or escape before write. Keep only
the durable summary fields above on canonical surfaces; never copy a raw artifact
or transcript into durable knowledge.

Repository-local `.superpowers/**` scratch is exceptional. Before its first
write, record a concrete operational reason and mechanically verify that the
exact path is covered by `.gitignore`. If either prerequisite is missing, do
not write locally and use the repository-external default. Never stage or
commit the scratch.

## Repository Validation Gate

Consume a caller-supplied canonical absolute target and the installed skill
directory as distinct identities. Require readable package content. Run
`git -C <target> rev-parse --show-toplevel` and
`git -C <target> rev-parse --is-inside-work-tree`; require `true` and require
that the returned top level exactly equals the canonical target. Every probe in
all three gates uses that same target binding. Never infer the target from the
skill package, process CWD, or ambient checkout.

| Gate | Required moment | Fresh direct Git verdict |
| --- | --- | --- |
| `exceptional-local-scratch-pre-write` | before each exceptional repository-local scratch leaf's first write | Require a non-empty exceptional reason and a normalized target-relative path whose resolved path and symlink ownership remain inside the target; use `git check-ignore --no-index` for the exact path and require it to be ignored, absent from the index, and absent from HEAD, so the leaf is ignored, untracked, unstaged, and uncommitted. |
| `pre-commit-candidate` | immediately before each commit creation | Derive the candidate with `git write-tree`; require the candidate tree, current index, and every unignored working-tree path to contain zero `.superpowers/**` entries. An unmerged index or unreadable candidate fails. A staged deletion passes only when the fresh candidate and index are clean; a force-add fails, while an add-then-delete is judged by its fresh final index and candidate. |
| `final-closeout` | after cleanup and immediately before local completion | Re-run the candidate/index/unignored-working-tree checks; require `HEAD^{tree}` to contain zero `.superpowers/**` entries; prove trusted immutable `starting_head_sha` is a commit and ancestor of HEAD; derive every commit in `starting_head_sha..HEAD` from the current object graph and use `git cat-file` and `git ls-tree` to require each commit tree to contain zero `.superpowers/**` entries. |

Evidence is single-use: recompute the selected gate from current Git objects and
state at its required moment. Scratch evidence is invalid after any target,
path, resolved ownership, ignore, HEAD, or index mutation. Pre-commit evidence
is invalid after any index, working-tree, or ignore mutation. Final evidence is
invalid after any HEAD, index, working-tree, ignore, or baseline-binding
mutation. Do not create an exactly-once mechanism, cache, state file, bundled
validator, adapter, scheduler, telemetry, or protocol.

Fail closed and stop the affected write, commit, transition, or closeout. A
missing or unreadable installed skill is
`BLOCKED: skill/package unavailable`; a target identity, Git capability, or
object-read failure is `BLOCKED: target/runtime unavailable`; a dirty or stale
gate verdict is respectively `FAIL: exceptional-local-scratch-pre-write`,
`FAIL: pre-commit-candidate`, or `FAIL: final-closeout`.

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
Pass Implementer and Task Reviewer the resolved canonical
`keep-implementation-simple/SKILL.md` path; each must read it fully before work.
If that read prevents completion, use the existing bounded return with the role
or phase, path, and underlying error.

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
Pass Final Reviewer the resolved canonical `keep-implementation-simple/SKILL.md`
path; the reviewer must read it fully before work. If that read prevents
completion, use the existing bounded return with the role or phase, path, and
underlying error.

Do not perform any remote write without separate explicit authorization.
This includes push, PR, merge, release, live install, issue, comment, and project changes.
Do not push, create a PR, merge, release, or install live without separate
explicit authorization. Report blockers, residual material risk, and unperformed
remote actions briefly.
