# Representative Plan Ownership Alignment Plan

## Approved North Star Identity

- Approved North Star path: knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md
- Approved North Star anchor: North Star
- Approved snapshot SHA-256: 1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md
- Approved spec SHA-256: 1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559
- Approval state: approved

## Plan Binding

- Repository baseline: c370fe14de1641aa5ee30b3fa001f4d857078091
- Planning worktree: /Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/sdd-plan-ownership-alignment-planning
- Integration branch: codex/sdd-plan-ownership-alignment-planning
- Current-tree compatibility: compatible
- Independent review verdict: ready
- Repository checks: passed
- Readiness evidence state: current

## Global Constraints

- Human authority is limited to the approved North Star and Written Spec.
- Plan authoring, review, repair, readiness, execution, and integration method are agent / repository-owned.
- Durable plans contain observable intent and no prospective production, test, script, shell-loop, patch, or command body.
- Remote authorization is evaluated separately from local plan readiness and completion.

## Requirement And Acceptance Inventory

- Requirements: R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15
- Acceptance criteria: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14

## Coverage Matrix

| ID | Primary owner | Contributing tasks |
| --- | --- | --- |
| R-01 | POA-2 | POA-3 |
| R-02 | POA-2 | POA-3 |
| R-03 | POA-2 | POA-3 |
| R-04 | POA-2 | POA-3 |
| R-05 | POA-2 | POA-1 |
| R-06 | POA-1 | POA-3 |
| R-07 | POA-1 | POA-3 |
| R-08 | POA-1 | POA-3 |
| R-09 | POA-1 | POA-3 |
| R-10 | POA-1 | POA-3 |
| R-11 | POA-1 | POA-3 |
| R-12 | POA-1 | POA-2, POA-3 |
| R-13 | POA-1 | POA-2, POA-3 |
| R-14 | POA-1 | POA-2, POA-3 |
| R-15 | POA-1 | POA-2, POA-3 |
| AC-01 | POA-2 | POA-3 |
| AC-02 | POA-2 | POA-3 |
| AC-03 | POA-2 | POA-1, POA-3 |
| AC-04 | POA-1 | POA-2, POA-3 |
| AC-05 | POA-1 | POA-2, POA-3 |
| AC-06 | POA-1 | POA-2, POA-3 |
| AC-07 | POA-1 | POA-2, POA-3 |
| AC-08 | POA-1 | POA-2, POA-3 |
| AC-09 | POA-2 | POA-1, POA-3 |
| AC-10 | POA-2 | POA-1, POA-3 |
| AC-11 | POA-1 | POA-2, POA-3 |
| AC-12 | POA-1 | POA-2, POA-3 |
| AC-13 | POA-2 | POA-3 |
| AC-14 | POA-3 | POA-1, POA-2 |

## Tasks

### Task POA-1: Plan contract overlay

- Deliverable: Add the local plan schema and representative validation fixture.
- Requirement coverage: R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15.
- Acceptance coverage: AC-04, AC-05, AC-06, AC-07, AC-08, AC-11, AC-12.
- Dependencies: none.

**Behavioral interface:**

- Consumes: approved spec identity, upstream planning methodology, and repository evidence.
- Produces: plan-level fields, task fields, coverage rules, and readiness vocabulary.

**Verification intent:** Accept the representative plan and reject malformed coverage, dependencies, integration, and prohibited content.

- Integration placement: I-1, before routing or lifecycle changes consume the overlay.
- Failure owner: POA-1 implementer repairs schema, fixture, and validator defects.

### Task POA-2: Agent-owned Plan Stage routing

- Deliverable: Route fresh authoring, independent review, internal repair, and ready entry.
- Requirement coverage: R-01, R-02, R-03, R-04, R-05.
- Acceptance coverage: AC-01, AC-02, AC-03, AC-09, AC-10, AC-13.
- Dependencies: POA-1.

**Behavioral interface:**

- Consumes: approved spec, trusted paths, overlay, author result, and reviewer verdict.
- Produces: author/reviewer dispatch, deterministic repair/decision/blocker dispositions, and ready entry.

**Verification intent:** Cover ready, repairable deficiencies, material conflicts, blockers, and local/remote authorization separation.

- Integration placement: I-2, after POA-1 is reviewed and present.
- Failure owner: POA-2 implementer repairs routing, prompt, and contract defects.

### Task POA-3: Lifecycle alignment and closeout

- Deliverable: Align downstream execution and durable closeout with the reviewed plan.
- Requirement coverage: R-01, R-06, R-12.
- Acceptance coverage: AC-14.
- Dependencies: POA-1 and POA-2.

**Behavioral interface:**

- Consumes: reviewed ready plan and serialized integration state.
- Produces: downstream lifecycle alignment and combined completion evidence.

**Verification intent:** Prove the integrated lifecycle keeps authority and local/remote boundaries intact.

- Integration placement: I-3, after both plan-contract and routing changes.
- Failure owner: POA-3 implementer repairs lifecycle and closeout defects.

## Dependency Graph

| Task | Dependencies |
| --- | --- |
| POA-1 | none |
| POA-2 | POA-1 |
| POA-3 | POA-1, POA-2 |

## Execution Order

1. POA-1
2. POA-2
3. POA-3

## Serialized Integration

- I-1: POA-1. Preconditions: focused contract validation is green. Combined-state expectation: overlay and fixture vocabulary are available.
- I-2: POA-2. Preconditions: I-1 is reviewed and present. Combined-state expectation: only reviewed ready plans enter implementation.
- I-3: POA-3. Preconditions: I-1 and I-2 are reviewed and present. Combined-state expectation: downstream lifecycle and closeout use the same plan contract.

## Post-Integration Combined Verification

**Scope:** Plan ownership alignment across AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, and AC-14.

**Pass criteria:** All focused and repository skill-architecture tests pass with complete coverage, acyclic dependencies, serialized integration, independent review, internal repair, and preserved authority boundaries.

**Required evidence:** Fresh focused outputs, applicable full-suite output, changed-path review, and reachable task commits.

**Failure owner:** The task owning the failing contract repairs it before integration proceeds.

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed

Reviewer vocabulary is ready or issues_found. The latter is classified as needs_repair, needs_decision, or blocked; none permits entry.
