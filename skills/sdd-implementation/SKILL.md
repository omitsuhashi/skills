---
name: sdd-implementation
description: Use when a human-approved implementation plan is ready for local execution in the current repository.
---

# SDD Implementation

Execute only a human-approved implementation plan.

**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development for its
task briefs, reports, task and fix loops, reviews, ledger, and worktree.

Main session is the orchestrator. It retains state, paths, routing, waits, and
short verdicts. Never implement production code, perform task review, or author wiki content in the main session.
Build no custom scheduler, worker packet schema, runtime snapshot, event log, or
resume protocol.

## Preflight And Isolation

- Require `PLAN_FILE`; read repository instructions, Git/worktree state, and the
  plan once.
- Require fresh implementers, independent reviewers, and per-dispatch model and
  reasoning selection. Missing plan or capability means `BLOCKED`.
  Do not fall back to another implementation workflow.
- Use only the SDD workspace and ledger.

Do not inherit the parent conversation. On Codex, dispatch implementation and
review agents with `fork_turns="none"`; on Hermes, use the equivalent fresh
context. Pass artifact paths and missing task-local facts only.

Skip Scout when the plan binds the current tree exactly. When file, interface,
test, or call-site binding is unclear, dispatch one bounded read-only Scout and
return only its status, SDD artifact path, and blocking concern.
A material plan/tree or reviewer/plan conflict goes to a high-capability
adjudicator for evidence; Human makes the authority-bearing decision.

## Runtime Routing

| Role | Work class | Capability |
| --- | --- | --- |
| orchestrator | state, routing, path handoff | balanced |
| Scout | bounded investigation | balanced-to-high; high for broad risk |
| mechanical implementer | exact one- or two-file change | economical balanced |
| integration implementer | multi-file coordination | balanced-to-high |
| high-risk implementer | debugging, architecture, security, concurrency | high |
| task reviewer | task-scoped judgment | risk-appropriate, not below implementer |
| adjudicator | plan conflict or review disagreement | high |
| knowledge closeout worker | Japanese knowledge synchronization | balanced-to-high |
| final reviewer | whole-branch judgment | highest available |

Resolve this table only in host dispatch calls. Honor user overrides. On a stuck
fix, raise reasoning first, then capability.
Persist no concrete model name, reasoning effort value, provider, agent ID, or run-specific routing result.

## Task Loop And Review

Run SDD sequentially. Give reviewers the approved task, binding constraints,
committed diff package, and verification report. Review only requirements fit,
material simplicity, and material current risk.

A blocking finding needs evidence of a requirement gap, scope excess, observable
regression, or concrete current risk. Material simplicity also needs a concrete simpler alternative,
removed mechanism, and material impact. Style, formatting, future-only concerns,
scope-external hardening, and equivalent preferences are non-blocking.
Non-blocking observations never enter the fix loop or block completion.
Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before dispatching
the Knowledge Closeout Worker.

## Closeout

When a knowledge root exists, dispatch a fresh Knowledge Closeout Worker. It
reads root instructions and uses `llm-wiki` to synchronize relevant canonical
pages in Japanese, `knowledge/index.md`, and `knowledge/log.md`, then validates
the wiki. Preserve stable identifiers and technical literals verbatim.

No knowledge root is `not_applicable`; an existing but unresolved closeout is
`BLOCKED`.

After closeout, run the highest-available final whole-branch review over code,
tests, and knowledge artifacts with the same material threshold. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.

## Platform Boundary

Codex must use isolated dispatch with explicit runtime model and reasoning
selection. Hermes must discover this shared skill through `skills.external_dirs`
and provide equivalent SDD and routing. Repository compatibility is not live
availability; fail closed when required capability is absent.

Do not push, create a PR, merge, release, or install live. Report blockers,
residual material risk, and unperformed remote actions briefly.
