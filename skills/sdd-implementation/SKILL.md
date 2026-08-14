---
name: sdd-implementation
description: Use when a repository change needs specification, planning, or local implementation through the Superpowers development lifecycle.
---

# SDD Implementation

Superpowers is the authoritative development methodology. Compose its current
skills; do not copy their process into a custom scheduler, worker packet schema,
runtime snapshot, event log, or resume protocol.
Superpowers owns generic worktree allocation, planning methodology, TDD, worker
dispatch, review and repair, and branch finishing. SDD owns only repository
entry and containment, stage composition, knowledge routing, the portable Git
gates, and the authority boundary below.

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
Check the Superpowers lifecycle skills for every route.
Check `grill-with-docs` when the Spec Stage requires it.
Check `llm-wiki` when a knowledge root exists.

If a required family is missing, return the matching result:

- `BLOCKED: missing Superpowers lifecycle dependency`
- `BLOCKED: missing grill-with-docs dependency`
- `BLOCKED: missing llm-wiki dependency`
- `BLOCKED: missing keep-implementation-simple dependency`

## Common Runtime Capability Guard

Apply this guard once before dispatching a stage, and reapply it before the
first affected mutation when any bound input changes. Consume the installed resource paths,
explicit target repository, original checkout fingerprint,
owned worktree, bound CWD, all durable and transient write destinations,
task-owner capability identity, original-checkout preservation evidence, fresh isolated dispatch,
explicit model, and result collection capabilities.

Resolve every path canonically. Apply the First-Write Worktree Gate to durable
repository writes and bind raw handoff to a bounded repository-external
task/session temporary destination. Verify each required package resource is
readable, each destination has the required ownership and containment, and the
target, CWD, and write destinations remain the supplied identities. Do not
infer an unverified substitute, move the work into the controller, or use an
old loop.

Follow the current Superpowers SDD Model Selection contract. Every worker dispatch states the resolved explicit model.
A user model override takes precedence. Independent effort control is optional and its absence does not
block. Synchronous dispatch that returns a completed result is a valid
result-collection mechanism. Asynchronous dispatch requires both wait and
resume capabilities. If neither synchronous result collection nor asynchronous
wait/resume is available, block before the first affected mutation.

Any missing, unreadable, mismatched, or unknown required capability or binding
returns the four-field Control Return: `status: blocked`, `artifact_path: none`,
`decision_requests: none`, and `material_risks` containing the role or phase,
failed capability or path, and underlying error. Make zero content or artifact
writes and invoke no downstream worker, writer, runner, or fallback.

## Keep Implementation Simple Wiring

Check `keep-implementation-simple` as a required supporting Skill during
Dependency Preflight. Resolve one readable canonical
`keep-implementation-simple/SKILL.md` path, then pass that same path to
exactly these seven roles and no others:

- Spec Synthesizer
- Spec Reviewer
- Plan Author
- Plan Reviewer
- Implementer
- Task Reviewer
- Final Reviewer

Each listed role must read it fully before work. If discovery proves no readable
match, return `BLOCKED: missing keep-implementation-simple dependency`. If
discovery, candidate inspection, path resolution, or reading fails, use the
Common Runtime Capability Guard before the affected work; do not invent an ad
hoc simplicity protocol or test-only runtime.

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

Resolve every normal-stage raw handoff through the Common Runtime Capability
Guard, which preserves the repository-external containment and pre-mutation
failure boundary. Keep only the durable summary fields above on canonical
surfaces; never copy a raw artifact or transcript into durable knowledge.

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
Apply the Common Runtime Capability Guard and Keep Implementation Simple Wiring
before either role begins affected work.

Within one selected execution unit, run SDD tasks sequentially. Review only
requirements fit, material simplicity, and material current risk. A blocking finding needs evidence of a requirement gap,
scope excess, observable regression, or concrete current risk. Do not block on
style, formatting, future-only concerns, scope-external hardening, or equivalent
preferences. Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before closeout.

## Execution Shape And Authority

Superpowers owns the allocation, dispatch, review, repair, integration, and
branch-completion methods. Parallel eligibility is agent / repository-owned and
requires current dependency evidence, write-conflict evidence, shared-resource
evidence, and ancestry evidence. If any required fact is unknown, use
sequential execution; no Human execution-method or issue-plan approval is required.

The observable SDD outcomes remain fail closed: one writer owns each unit and
integration (one unit per issue/task), and no unit contains concurrent
implementers; blocked or unreviewed results are ineligible. Before serialized integration, the applicable
Superpowers contract revalidates actual commit ranges, changed paths,
dependencies, conflicts, the captured target or a verified compatible advance,
and reachability of every required task commit. The accepted tip retains those
commits despite any history transformation. Integrate ready units serially;
never treat a clean textual merge or partial integrated state as completion.

The integration target must remain the captured target. Divergence, rewrite, or
uncertainty blocks without retargeting. Completion requires fresh combined
verification and original-checkout preservation.
`starting_branch` is PR base and `integration_branch` is PR head and integration target.

Agent-repairable evidence gaps remain agent-owned. Return to Human authority
only for an evidenced material Written Spec change. A remote action always
requires its own separate explicit authorization and a valid remote base.

## Implementation Closeout

Dispatch a fresh knowledge worker and use the Durable Knowledge contract.
Validate the wiki before final review.

## Final Whole-Branch Review

After Implementation Closeout, run exactly one canonical whole-branch review
through the Superpowers review contract. Cover code, tests, the approved
specification, reviewed plan, and knowledge artifacts. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.
Apply the Common Runtime Capability Guard and Keep Implementation Simple Wiring
before the Final Reviewer begins affected work.

Do not perform any remote write without separate explicit authorization.
This includes push, PR, merge, release, live install, issue, comment, and project changes.
Do not push, create a PR, merge, release, or install live without separate
explicit authorization. Report blockers, residual material risk, and unperformed
remote actions briefly.
