---
name: sdd-implementation
description: Use when a repository change needs specification, planning, or local implementation through the Superpowers development lifecycle.
---

# SDD Implementation

Superpowers is the authoritative development methodology. Compose its current
skills; do not copy their process into a custom scheduler, worker packet schema,
runtime snapshot, event log, or resume protocol.

## Route By Input Maturity

Do not repeat a completed stage.

- **Change request or incomplete specification:** use
  `superpowers:brainstorming`, the Spec Stage below, and Human written-spec
  approval before planning.
- **Human-approved current specification:** verify authority, applicability,
  requirements, and acceptance criteria, then use `superpowers:writing-plans`.
  Return to the Spec Stage only for a material conflict.
- **Approved plan bound to the current specification:** verify its binding,
  current-tree compatibility, and verification scope, then use
  `superpowers:subagent-driven-development`.

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
2. Repository-approved implementation plan.
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
repository-required plan review or Human approval. Persist the approved plan
through the Durable Knowledge contract. Do not dispatch implementation from an
unapproved plan.

## Implementation Stage

**REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.**

Main session is the orchestrator. It retains state, paths, routing, waits, and
short verdicts. Never implement production code, perform task review, or author
wiki content in the main session.

Use fresh implementers and independent reviewers. Do not inherit the parent
conversation. On Codex, use `fork_turns="none"`; on Hermes Agent, use the
equivalent fresh context. Pass durable paths and missing task-local facts only.

Run SDD sequentially. Review only requirements fit, material simplicity, and
material current risk. A blocking finding needs evidence of a requirement gap,
scope excess, observable regression, or concrete current risk. Do not block on
style, formatting, future-only concerns, scope-external hardening, or equivalent
preferences. Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before closeout.

## Runtime Model And Effort

Follow the current Superpowers SDD Model Selection contract. Every subagent dispatch must state its model. Let Superpowers choose the relative tier for the task and resolve that tier to a concrete model available in the current host.
Do not maintain a second role-to-model table.

Apply reasoning effort as an independent runtime-only overlay when supported:

| Superpowers task class | Reasoning effort |
| --- | --- |
| Mechanical task or small scoped re-review | `low` |
| Multi-file integration, normal debugging, or task review | `medium` |
| Architecture-sensitive or high-risk task, or final review | `high` |

Honor an explicit user runtime override. For a stuck fix, raise effort one
available step before following Superpowers model escalation.

When a host has no independent effort control, record `not_supported` and continue with Superpowers model selection. Lack of independent effort control does not block the flow. Lack of isolated dispatch with an explicit model is `BLOCKED`.

Persist no concrete model, effort, provider, availability, agent ID, or
run-specific resolution in the specification, plan, wiki, ledger, or schema.

## Host Boundary

Codex maps isolated dispatch, explicit model, optional effort, wait, and resume
to current host capabilities. Hermes Agent is not assumed to have an upstream
adapter; detect and map fresh worker/reviewer, model selector, optional effort,
and resume capabilities. Keep `skills.external_dirs` as the documented Hermes
discovery route.

Do not hard-code host tool names or model catalogs. Do not silently fall back to
main-session implementation or an old loop skill when required SDD capability
is absent.

## Implementation Closeout

Dispatch a fresh knowledge worker and use the Durable Knowledge contract.
Validate the wiki before final review.

## Final Whole-Branch Review

After closeout, run the Superpowers final whole-branch review over code, tests,
the approved specification and plan, and knowledge artifacts. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.

Do not push, create a PR, merge, release, or install live without separate
explicit authorization. Report blockers, residual material risk, and
unperformed remote actions briefly.
