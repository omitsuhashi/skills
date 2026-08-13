# Plan Contract Overlay

This repository-local overlay supplements the current
`superpowers:writing-plans` methodology; do not copy, vendor, fork, or replace
the upstream skill. For repository-specific plan fields and readiness,
the Plan Contract Overlay takes precedence.

## Inputs

- approved Written Spec path, SHA-256 identity, and approval state;
- complete requirement and acceptance-criteria inventory;
- current upstream `superpowers:writing-plans` skill path;
- current-tree file responsibility and verification evidence;
- trusted planning worktree, baseline, and writable artifact paths.

## Outputs

- one executable implementation plan containing the plan-level and task-level
  fields below;
- complete primary and contributing coverage, dependency, execution,
  integration, and combined-verification mappings;
- one review result using the readiness vocabulary below.

## Required Capabilities

- isolated fresh-context Plan Author and independent Plan Reviewer dispatch;
- bounded reads of the approved spec, upstream skill, repository rules, and
  current-tree evidence;
- writes confined to the trusted planning worktree;
- synchronous result collection or asynchronous wait and resume.

## Required Plan-Level Fields

Include these sections:

- `Approved Written Spec Identity`: approved spec path, SHA-256, and approved
  state;
- `Requirement And Acceptance Inventory`: every in-scope requirement and
  acceptance ID exactly once;
- `Coverage Matrix`: every inventory ID, exactly one primary task, and any
  contributing tasks;
- `Tasks`, `Dependency Graph`, `Execution Order`, `Serialized Integration`,
  `Post-Integration Combined Verification`, and `Readiness Result`.

## Required Task Fields

Each task declares a deliverable, requirement coverage, acceptance coverage,
dependencies, consumed artifacts, produced artifacts, verification intent,
integration placement, and failure owner. A task must name every requirement or
acceptance criterion for which it is primary owner.

## Coverage And Dependency Invariants

- Assign every inventory ID to exactly one primary task; contributing tasks do
  not replace primary ownership.
- Reject unknown IDs, duplicate coverage, unassigned IDs, and orphan tasks.
- Define every task in the dependency graph and reject undefined dependencies
  or cycles.
- Order execution topologically after all declared dependencies.

## Execution, Integration, And Combined Verification

Define execution order separately from serialized integration. For each
integration step, state preconditions and the expected combined state. After
the final integration, define scope, pass criteria, required evidence, and a
failure owner covering every acceptance criterion.

## Prohibited Durable Plan Content

Do not include prospective implementation code, scripts, command bodies,
patches, scheduler/runtime machinery, worker packets, or concrete runtime
model, provider, agent, or effort selections. Do not make the plan a Human
approval subject. Human authority remains with the North Star and Written Spec.

## Review And Readiness Vocabulary

The independent Plan Reviewer returns `ready` or `issues_found`. The Planning
Controller classifies `issues_found` as `needs_repair`, `needs_decision`, or
`blocked`:

- `needs_repair`: an agent-repairable plan deficiency, including missing
  coverage, prohibited durable content, dependency errors, or a method that is
  not buildable on the current tree;
- `needs_decision`: only an evidenced material conflict with the approved
  Written Spec;
- `blocked`: a non-decision capability, path, trust, or evidence blocker.

Keep `needs_repair` inside the agent-owned Plan Stage. Only `ready` maps to the
existing Control Return `status: complete` and Implementation Stage entry.
Missing authorization for a later remote publication does not change local
plan readiness.
