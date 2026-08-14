# Plan Contract Overlay

This repository-local overlay supplements the current
`superpowers:writing-plans` methodology; do not copy, vendor, fork, or replace
the upstream skill. For repository-specific plan fields and readiness,
the Plan Contract Overlay takes precedence.

## Inputs

- approved North Star and Written Spec paths, anchor, SHA-256 approval-snapshot
  identity, and approval state;
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

- `Approved North Star Identity`: contained spec path, stable `North Star`
  anchor, SHA-256 approval-snapshot identity, and approved state;
- `Approved Written Spec Identity`: contained spec path, the same non-empty
  SHA-256 approval-snapshot identity, and approved state;
- `Plan Binding`: full repository baseline commit, planning worktree,
  integration branch, `Current-tree compatibility: compatible`, `Independent
  review verdict: ready`, `Repository checks: passed`, and `Readiness evidence
  state: current`;
- `Global Constraints`: authority, content, portability, local/remote, and
  integration constraints that apply to every task;
- `Requirement And Acceptance Inventory`: every in-scope requirement and
  acceptance ID exactly once;
- `Coverage Matrix`: every inventory ID, exactly one primary task, and any
  contributing tasks;
- `Tasks`, `Dependency Graph`, `Execution Order`, `Serialized Integration`,
  `Post-Integration Combined Verification`, and `Readiness Result`.

The durable approval-snapshot identity must match the identity declared by the
approved spec. The repository baseline must resolve to a current-tree ancestor.
Treat these Plan Binding values as closed semantic states, not non-empty prose.
Reject `incompatible`, `issues_found`, failed or absent repository checks, stale
or absent readiness evidence, and any unknown value. Every identity, binding,
and Readiness Result section and field is a non-empty singleton; collect and
validate every matching section / declaration, and reject empty or duplicate
sections and declarations even
when the first value is valid, including `ready` followed by `issues_found` or
`current` followed by `stale`. Empty, malformed,
mismatched, absent, or stale binding evidence is not `ready`. `Readiness Result`
must likewise declare `Plan readiness disposition: ready`, `Control Return
status: complete`, and `Implementation Stage entry: allowed`.
The canonical ready plan and representative fixture must satisfy the same
executable semantic validator in `tests/test_plan_contract.py`.

## Required Task Fields

Each task declares a deliverable, exact requirement coverage, exact acceptance
coverage, dependencies, an observable `Behavioral interface` with `Consumes`
and `Produces`, verification intent, integration placement, and failure owner.
A task must name every requirement or acceptance criterion for which it is
primary owner.

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

Do not include prospective production or test code, fenced or structurally
unfenced Python / JavaScript bodies, test bodies, script or shell control-flow
bodies, patch bodies, or execution command bodies such as test runners and
shell output commands. Structural bodies include a Python body after a
docstring and intervening blank lines, and one-line JavaScript function or
multi-command shell-if bodies with internal semicolons. Match complete
structural bodies or line-anchored
commands rather than keywords inside prose, so intent-only prose may name these
prohibited classes. Do not include scheduler/runtime machinery, worker packets,
or concrete runtime model, provider, agent, or effort selections. Do not make
the plan a Human approval subject. Human authority remains with the North Star
and Written Spec.

For Python, extract line-anchored `def` / `async def` candidates and use the
language parser to recognize an actual function body after optional docstrings,
comments, and blank lines. Do not maintain an executable-statement whitelist.
A prose interface signature that is not valid Python remains narrative intent.

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
