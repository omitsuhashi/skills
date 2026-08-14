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

- Requirements: R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15, R-16, R-17, R-18, R-19, R-20, R-21
- Acceptance criteria: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20

## Coverage Matrix

| ID | Primary owner | Contributing tasks |
| --- | --- | --- |
| R-01 | POA-2 | POA-3 |
| R-02 | POA-2 | POA-1, POA-3 |
| R-03 | POA-2 | POA-3 |
| R-04 | POA-2 | POA-3, POA-8 |
| R-05 | POA-2 | POA-1, POA-3 |
| R-06 | POA-2 | POA-1, POA-3 |
| R-07 | POA-2 | POA-1, POA-3 |
| R-08 | POA-2 | POA-1, POA-3 |
| R-09 | POA-2 | POA-1, POA-3 |
| R-10 | POA-2 | POA-1, POA-3 |
| R-11 | POA-2 | POA-1, POA-3 |
| R-12 | POA-2 | POA-1, POA-3 |
| R-13 | POA-2 | POA-1, POA-3 |
| R-14 | POA-2 | POA-1, POA-3 |
| R-15 | POA-2 | POA-1, POA-3 |
| R-16 | POA-5 | POA-4, POA-7 |
| R-17 | POA-5 | POA-4, POA-6 |
| R-18 | POA-5 | POA-4, POA-6, POA-8 |
| R-19 | POA-7 | POA-4, POA-5, POA-6 |
| R-20 | POA-5 | POA-4, POA-6, POA-8 |
| R-21 | POA-6 | POA-4, POA-7, POA-8 |
| AC-01 | POA-2 | POA-3 |
| AC-02 | POA-2 | POA-1, POA-3 |
| AC-03 | POA-2 | POA-1, POA-3 |
| AC-04 | POA-2 | POA-1, POA-3 |
| AC-05 | POA-2 | POA-1, POA-3 |
| AC-06 | POA-2 | POA-1, POA-3 |
| AC-07 | POA-2 | POA-1, POA-3 |
| AC-08 | POA-2 | POA-1, POA-3 |
| AC-09 | POA-2 | POA-1, POA-3 |
| AC-10 | POA-2 | POA-1, POA-3 |
| AC-11 | POA-2 | POA-1, POA-3 |
| AC-12 | POA-2 | POA-1, POA-3 |
| AC-13 | POA-2 | POA-3, POA-8 |
| AC-14 | POA-3 | POA-1, POA-2 |
| AC-15 | POA-5 | POA-4, POA-7 |
| AC-16 | POA-5 | POA-4, POA-6 |
| AC-17 | POA-5 | POA-4, POA-6, POA-8 |
| AC-18 | POA-7 | POA-4, POA-5, POA-6 |
| AC-19 | POA-6 | POA-4, POA-7, POA-8 |
| AC-20 | POA-8 | POA-4, POA-5, POA-6, POA-7 |

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
- Requirement coverage: R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15.
- Acceptance coverage: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13.
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

### Task POA-4: Transient artifact executable RED contract

- Deliverable: Add executable expectations for repository-external handoff, scratch gating, Git-tree invariants, and durable-summary routing.
- Requirement coverage: R-16, R-17, R-18, R-19, R-20, R-21.
- Acceptance coverage: AC-15, AC-16, AC-17, AC-18, AC-19, AC-20.
- Dependencies: POA-1, POA-2, and POA-3.

**Behavioral interface:**

- Consumes: approved amendment, consumed migration entry, current destinations, ignore coverage, and tracked-report baseline.
- Produces: reviewed intentional RED tests and an expanded representative fixture.

**Verification intent:** Prove only current destination, missing validator, and missing CI invocation gaps remain.

- Integration placement: I-4, after the original closeout and single-use entry consumption.
- Failure owner: POA-4 implementer repairs test semantics and expected-failure provenance.

### Task POA-5: Repository-external handoff and validator

- Deliverable: Migrate normal-stage transient destinations and implement the fail-closed repository validator and CI invocation.
- Requirement coverage: R-16, R-17, R-18, R-20.
- Acceptance coverage: AC-15, AC-16, AC-17.
- Dependencies: POA-4.

**Behavioral interface:**

- Consumes: reviewed POA-4 RED, current stage destinations, ignore coverage, and Git tree state.
- Produces: repository-external handoff, scratch gate, validator, and CI integration.

**Verification intent:** Turn the amended focused contract GREEN while preserving the exact inherited report baseline.

- Integration placement: I-5, after the reviewed amended RED contract.
- Failure owner: POA-5 implementer repairs migration and validator defects.

### Task POA-6: Tracked report final-tree cleanup

- Deliverable: Remove exactly the migration-baseline reports from the index and final tree without destroying needed local bytes.
- Requirement coverage: R-17, R-18, R-20, R-21.
- Acceptance coverage: AC-16, AC-17, AC-19.
- Dependencies: POA-5.

**Behavioral interface:**

- Consumes: exact report set, ignore coverage, validator GREEN, and durable-summary sufficiency.
- Produces: zero candidate-tree entries and optional ignored local copies.

**Verification intent:** Accept staged deletion and historical blobs while rejecting extra or reintroduced entries.

- Integration placement: I-6, after validator enforcement is reviewed.
- Failure owner: POA-6 implementer owns exact non-destructive index cleanup.

### Task POA-7: Durable amendment closeout

- Deliverable: Synchronize reviewed migration and cleanup evidence into canonical knowledge without raw report duplication.
- Requirement coverage: R-16, R-19, R-21.
- Acceptance coverage: AC-15, AC-18, AC-19.
- Dependencies: POA-5 and POA-6.

**Behavioral interface:**

- Consumes: reviewed migration, cleanup evidence, canonical paths, and append-only log.
- Produces: canonical durable summary and synchronized discovery.

**Verification intent:** Keep decisions, verdicts, and evidence identities durable while raw handoffs remain transient.

- Integration placement: I-7, after migration and cleanup are reviewed.
- Failure owner: POA-7 knowledge worker repairs canonical synchronization defects.

### Task POA-8: Combined verification and publication gate

- Deliverable: Run fresh combined verification and final review before any separately authorized publication.
- Requirement coverage: R-18, R-20, R-21.
- Acceptance coverage: AC-17, AC-19, AC-20.
- Dependencies: POA-4, POA-5, POA-6, and POA-7.

**Behavioral interface:**

- Consumes: complete reviewed commit range, fresh validation, tree inspection, and separate publication authorization.
- Produces: final review verdict and an authorized non-force branch update when permitted.

**Verification intent:** Prove every required commit is reachable and every current candidate and final tree has zero transient entries.

- Integration placement: I-8, after all content tasks are reviewed and reachable.
- Failure owner: POA-8 owns combined verification and publication-boundary failures.

## Dependency Graph

| Task | Dependencies |
| --- | --- |
| POA-1 | none |
| POA-2 | POA-1 |
| POA-3 | POA-1, POA-2 |
| POA-4 | POA-1, POA-2, POA-3 |
| POA-5 | POA-4 |
| POA-6 | POA-5 |
| POA-7 | POA-5, POA-6 |
| POA-8 | POA-4, POA-5, POA-6, POA-7 |

## Execution Order

1. POA-1
2. POA-2
3. POA-3
4. POA-4
5. POA-5
6. POA-6
7. POA-7
8. POA-8

## Serialized Integration

- I-1: POA-1. Preconditions: focused contract validation is green. Combined-state expectation: overlay and fixture vocabulary are available.
- I-2: POA-2. Preconditions: I-1 is reviewed and present. Combined-state expectation: only reviewed ready plans enter implementation.
- I-3: POA-3. Preconditions: I-1 and I-2 are reviewed and present. Combined-state expectation: downstream lifecycle and closeout use the same plan contract.
- I-4: POA-4. Preconditions: I-1 through I-3 are reviewed and the single-use entry is consumed. Combined-state expectation: the amended test contract is intentionally RED only for declared implementation gaps.
- I-5: POA-5. Preconditions: I-4 is reviewed and reachable. Combined-state expectation: migration and validator behavior are GREEN while the exact baseline reports remain pending cleanup.
- I-6: POA-6. Preconditions: I-5 is reviewed and ignore coverage is proven. Combined-state expectation: the candidate tree has zero transient entries and optional local copies remain ignored.
- I-7: POA-7. Preconditions: I-5 and I-6 are reviewed. Combined-state expectation: durable knowledge summarizes the reviewed result without raw report duplication.
- I-8: POA-8. Preconditions: I-4 through I-7 are reviewed and reachable. Combined-state expectation: final verification and any authorized publication preserve the zero-entry invariant.

## Post-Integration Combined Verification

**Scope:** Plan ownership alignment across AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, and AC-20.

**Pass criteria:** All focused and repository skill-architecture tests pass with complete coverage, acyclic dependencies, serialized integration, independent review, internal repair, and preserved authority boundaries.

**Required evidence:** Fresh focused outputs, applicable full-suite output, changed-path review, and reachable task commits.

**Failure owner:** The task owning the failing contract repairs it before integration proceeds.

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed

Reviewer vocabulary is ready or issues_found. The latter is classified as needs_repair, needs_decision, or blocked; none permits entry.
