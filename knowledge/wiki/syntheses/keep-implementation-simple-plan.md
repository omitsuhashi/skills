# Keep Implementation Simple Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Human承認済みの単純化contractを既存`keep-implementation-simple` Skillへ最小限に実装し、`sdd-implementation`が指定7 roleへcanonical Skillをread-before-workで渡すようにする。

**Architecture:** 既存`skills/keep-implementation-simple/SKILL.md`だけがtest・fixture・guardrail policyを所有し、既存identityのままin-placeで更新する。`sdd-implementation`はDependency Preflight、resolved canonical path、7 roleへのread-before-work、fail-closed境界だけを所有し、policy本文を複製しない。behavioral RED/GREEN evidence、focused SDD contract test、既存repository gateを用い、新しいruntime machineryやfixture infrastructureは作らない。

**Tech Stack:** portable Markdown `SKILL.md` contracts、Python 3.9+ `unittest` contract tests、既存repository validators、Superpowers skill TDD、LLM Wiki single-root durable knowledge。

## Global Constraints

- Human authority is limited to the approved North Star and Written Spec snapshot `KIS-SPEC-2026-08-14-V1`; plan authoring, review, repair, readiness, execution, and integration are agent / repository-owned.
- Preserve `sdd-implementation` as the sole/default user-facing implementation route; `keep-implementation-simple` remains a supporting Skill.
- Update the existing `skills/keep-implementation-simple/SKILL.md` in place. Do not create a duplicate Skill, alias, compatibility layer, or `description.md`.
- The existing Skill directory means the repository's Skill initializer is not applicable. Do not scaffold or reinitialize it.
- Required portable output is the shared `SKILL.md` contract only. Do not add optional `agents/openai.yaml` or other UI metadata without a new evidenced requirement.
- Preserve runtime-agnostic Inputs, Outputs, and Required Capabilities; runtime-specific tool names, model/provider choices, agent identities, and effort selections are not behavioral contract content.
- The supporting Skill owns detailed minimum-change, test, fixture, and guardrail policy. SDD owns only dependency identity, resolved path delivery, applicable roles, read-before-work, and failure handling.
- Preserve existing security, data-integrity, mechanical validation, required coverage, required suite execution, and `.superpowers/**` transient-artifact rejection. Simplicity cannot remove these boundaries.
- Additional tests must name one observable break, use minimal inline data, and distinguish the new contract. Do not add role-by-role equivalent permutations, coverage-only assertions, a fixture family, factory, corpus, property-test framework, or durable test ledger.
- Do not add a resolver, classifier, cache, trace, provenance model, schema, protocol, scoring system, budget table, necessity ledger, exception workflow, dedicated runtime state, retry/fallback, second validator, or recovery-free catch.
- Raw pressure-test prompts, worker answers, rationalizations, review transcripts, and command output remain in a resolved repository-external task/session temporary root. Durable knowledge contains only summarized decisions, verdicts, and evidence identities.
- Source, test, and durable knowledge writes stay inside the trusted planning worktree. The original checkout remains read-only and must finish at its captured starting HEAD/status.
- Every implementation task follows RED, verified RED, minimal GREEN, verified GREEN, and independent task review before serialized integration.
- Local plan readiness and `LOCAL_COMPLETE` do not authorize push, PR, merge, release, live install, issue/comment/project writes, or any other remote mutation.

---

## Approved North Star Identity

- Approved North Star path: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- Approved North Star anchor: `North Star`
- Approved snapshot identity: `KIS-SPEC-2026-08-14-V1`
- Approval-snapshot content SHA-256: `74fb9727f9cc2f9d199b82a54101426b66596057f93b34df02d0866e1f79d23a`
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- Approved spec snapshot identity: `KIS-SPEC-2026-08-14-V1`
- Approved-spec content SHA-256: `74fb9727f9cc2f9d199b82a54101426b66596057f93b34df02d0866e1f79d23a`
- Approval state: approved

## Plan Binding

- Repository baseline: `82dcd32157ff9690ae038f982f3916009e449f80`
- Starting branch: `main`
- Planning worktree: `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/keep-implementation-simple-planning`
- Integration branch: `codex/keep-implementation-simple/planning`
- Current-tree compatibility: compatible
- Independent review verdict: ready
- Repository checks: passed
- Readiness evidence state: current

Current-tree evidence at the latest authoring check consists of a clean baseline ancestry check, 93 passing SDD tests including 24 passing plan-contract tests, passing architecture and context validators, successful active-runtime Skill validation for both affected Skills, a passing current-index transient-artifact candidate-tree check, and passing working/cached diff whitespace checks. The spec digest also matches both plan identity declarations, and manual semantic inspection confirms the required singleton sections, inventory/coverage/dependency mappings, and prohibited-content boundary remain intact. Detailed command output remains outside durable knowledge. A fresh independent re-review confirmed that the repaired KIS-1 sample-sufficiency contract is complete and that no material spec, scope, dependency, acceptance, or execution defect remains; it returned `ready` with no decision request or material risk.

## File Map

- `skills/keep-implementation-simple/SKILL.md`: canonical supporting policy and portable Inputs, Outputs, Required Capabilities, deletion test, and explicit test / fixture / guardrail contracts.
- `skills/sdd-implementation/SKILL.md`: required dependency resolution, fail-closed boundary, and delivery/read contract for the implementation-stage and final-review roles.
- `skills/sdd-implementation/references/planning-context.md`: resolved supporting-Skill path delivery for Spec Synthesis, Spec Review, Plan Authoring, and Plan Review dispatches.
- `skills/sdd-implementation/prompts/spec-synthesizer.md`: Spec Synthesizer read-before-work input and boundary.
- `skills/sdd-implementation/prompts/spec-reviewer.md`: Spec Reviewer read-before-work input and boundary.
- `skills/sdd-implementation/prompts/plan-reviewer.md`: Plan Reviewer read-before-work input and boundary.
- `skills/sdd-implementation/tests/test_preimplementation_context.py`: one focused, data-driven regression over dependency resolution and all seven required roles, using inline expected data.
- `knowledge/wiki/syntheses/keep-implementation-simple-plan.md`: reviewed executable plan and implementation closeout summary.
- `knowledge/index.md`: active canonical discovery records for the approved spec and reviewed plan.
- `knowledge/log.md`: append-only Plan Stage and implementation-closeout lifecycle events.

## Requirement And Acceptance Inventory

- R-01: Preserve one independent, runtime-agnostic, portable `keep-implementation-simple` supporting Skill and update its existing canonical identity in place.
- R-02: Map each added production change, test, fixture, and guardrail to a current requirement, acceptance criterion, reproduced regression, or actual boundary risk; remove additions that fail the deletion test.
- R-03: Add only the minimum discriminating tests for requested observable behavior, reproduced regression, or necessary current boundary behavior, while distinguishing test-code additions from required suite execution.
- R-04: Prefer inline data and existing fixtures; add a fixture only for behavior-intrinsic files/artifacts or actual reuse of non-trivial setup.
- R-05: Require current evidence for a guardrail, keep one owning seam, preserve existing security/data-integrity boundaries, and reject duplicate/speculative validation or recovery-free catches.
- R-06: Preserve `sdd-implementation` as the sole/default user-facing route and avoid architecture-policy or optional UI changes.
- R-07: Resolve/read `keep-implementation-simple` in SDD Dependency Preflight and fail closed with phase/path and underlying error before affected work when resolution/read fails.
- R-08: Deliver the canonical Skill path and require read-before-work for Spec Synthesizer, Spec Reviewer, Plan Author, Plan Reviewer, Implementer, Task Reviewer, and Final Reviewer without copying policy.
- R-09: Add no scoring, budget, ledger, exception workflow, runtime state, duplicate route, resolver/classifier/cache/trace/schema/protocol, speculative fallback, or dedicated validation machinery.
- R-10: Keep explicit portable Inputs, Outputs, Required Capabilities, current evidence categories, required validation preservation, durable knowledge synchronization, and local/remote boundaries.
- AC-01: The supporting Skill satisfies the standard portable `SKILL.md` contract, with runtime-agnostic Inputs, Outputs, and Required Capabilities, and no required artifact beyond `SKILL.md`.
- AC-02: The supporting Skill explicitly defines minimum coherent change, deletion test, test / fixture / guardrail contracts, and preservation of required validation.
- AC-03: Architecture validation confirms `sdd-implementation` remains the sole/default user-facing implementation route.
- AC-04: SDD Dependency Preflight requires the supporting Skill and fails closed on unresolved or unreadable dependency state.
- AC-05: All seven required fresh roles read the canonical Skill before work and no SDD surface duplicates its detailed policy.
- AC-06: One focused SDD regression distinguishes dependency plus seven-role wiring, and the exact combined pressure scenario produces verified pre-change RED followed by post-change GREEN.
- AC-07: No equivalent-permutation or coverage-only test expansion is introduced.
- AC-08: Fresh SDD suite, architecture, context, both Skill validations, transient-artifact Git-surface validation, and diff checks all exit successfully.
- AC-09: `knowledge/index.md` and append-only `knowledge/log.md` are synchronized with the accepted spec and reviewed plan lifecycle.
- AC-10: The final diff contains no scoring, budget, ledger, exception workflow, runtime state, duplicate route, or other prohibited machinery.

## Coverage Matrix

| ID | Primary owner | Contributing tasks |
| --- | --- | --- |
| R-01 | KIS-1 | KIS-3 |
| R-02 | KIS-1 | KIS-2, KIS-3 |
| R-03 | KIS-1 | KIS-2, KIS-3 |
| R-04 | KIS-1 | KIS-2 |
| R-05 | KIS-1 | KIS-2, KIS-3 |
| R-06 | KIS-2 | KIS-3 |
| R-07 | KIS-2 | KIS-3 |
| R-08 | KIS-2 | KIS-3 |
| R-09 | KIS-1 | KIS-2, KIS-3 |
| R-10 | KIS-1 | KIS-2, KIS-3 |
| AC-01 | KIS-1 | KIS-3 |
| AC-02 | KIS-1 | KIS-3 |
| AC-03 | KIS-2 | KIS-3 |
| AC-04 | KIS-2 | KIS-3 |
| AC-05 | KIS-2 | KIS-3 |
| AC-06 | KIS-1 | KIS-2, KIS-3 |
| AC-07 | KIS-2 | KIS-1, KIS-3 |
| AC-08 | KIS-3 | KIS-1, KIS-2 |
| AC-09 | KIS-3 | KIS-1, KIS-2 |
| AC-10 | KIS-3 | KIS-1, KIS-2 |

## Tasks

### Task 1: KIS-1 — Skill TDD and minimum supporting contract

- Deliverable: Produce verified RED/GREEN behavioral evidence and update the existing canonical supporting Skill with the minimum explicit policy contract.
- Requirement coverage: R-01, R-02, R-03, R-04, R-05, R-09, R-10.
- Acceptance coverage: AC-01, AC-02, AC-06.
- Dependencies: none.

**Behavioral interface:**

- Consumes: accepted spec `KIS-SPEC-2026-08-14-V1`, the current 38-line Skill, current repository rules and required validation, `/private/tmp/keep-implementation-simple.uY2W4Z/research.md`, `/private/tmp/keep-implementation-simple.uY2W4Z/baseline-score.md`, and the exact combined pressure scenario in the spec.
- Produces: one in-place portable `SKILL.md`, a repository-external RED/GREEN evidence identity, minimum discriminating test/fixture/guardrail decisions, and concrete `BLOCKED` output when a current requirement cannot be satisfied.

**Verification intent:** Before any Skill write, use exactly five fresh-context outputs for a no-guidance control and exactly five for the unchanged current Skill under the same combined authority/time/sunk-cost scenario and identical repository evidence, manually score every output, and assess variance rather than trusting a single sample. After the minimal edit, use a matched five fresh-context outputs with the updated Skill and manually score every output. Score removal of unsupported duplicate/equivalent/coverage-only tests, fixture infrastructure, second validation, speculative retry/fallback, and recovery-free catches separately from retention of the genuine existing SDD suite and transient boundary; the retention check is a second manual dimension of the same scenario, not another scenario or fixture.

- Integration placement: I-1, before any SDD surface begins to depend on the expanded contract.
- Failure owner: KIS-1 implementer owns baseline-evidence validity, minimal Skill wording, Skill validation, and GREEN behavioral compliance.

- [ ] Step 1: Read `superpowers:writing-skills`, `superpowers:test-driven-development`, their required skill-testing/test-quality references, the approved spec, repository rules, and the current supporting Skill before any write.
- [ ] Step 2: Resolve a bounded repository-external task/session temporary evidence path and preserve the exact accepted scenario prompt plus repository evidence inputs there; do not create a repository fixture or durable transcript.
- [ ] Step 3: Inspect the existing raw no-guidance baseline artifacts under `/private/tmp/keep-implementation-simple.uY2W4Z/` before dispatch. Count an artifact only when it is a fresh isolated output produced with no `keep-implementation-simple` guidance, the exact accepted combined scenario, and identical repository evidence; `baseline-score.md` is a summary and never counts as a sample. Reuse each qualifying raw output once and dispatch only enough missing no-guidance samples to reach exactly five. Different parse-mode or fixture scenarios remain advisory and do not count toward this matched control.
- [ ] Step 4: Complete the no-guidance control before any Skill write. For each of its five outputs, manually record in the repository-external evidence root the chosen change/test/fixture/guardrail set, required validation retained or dropped, exact rationalizations, the spec-defined RED/GREEN outcome, and the separate genuine-boundary-retention outcome. Automated counts may assist navigation but never replace reading and scoring an output.
- [ ] Step 5: Before any Skill write, dispatch exactly five fresh isolated workers against the unchanged current Skill with the identical accepted scenario and repository evidence. Manually score every output using the same two outcome dimensions and record exact rationalizations outside the repository. Compare the five no-guidance and five current-Skill outcomes to identify variance and the recurring failure form; do not create a durable score, test ledger, fixture corpus, or scoring framework.
- [ ] Step 6: Verify RED before editing `skills/keep-implementation-simple/SKILL.md`: the no-guidance control must exhibit the target failure, and the current-Skill samples must establish the spec-defined failure as an observed pattern rather than a lone unexamined outlier by retaining an unsupported duplicate test, speculative fixture, duplicate/speculative guardrail, or dropping the existing transient boundary/required suite. If the control does not fail, the current Skill has no observed failure, or variance prevents identifying a concrete recurring failure and rationalization, stop without a Skill write.
- [ ] Step 7: Update the existing Skill in place with explicit Inputs, Outputs, Required Capabilities, minimum coherent change and deletion test, the three artifact contracts, required-validation preservation, concrete evidence/blocker categories, and counters only for observed scope rationalizations. A smaller diff alone never authorizes changing an observable error payload or other existing behavior; do not freeze whitespace/Unicode or another unrequested input policy.
- [ ] Step 8: Keep the Skill concise and self-contained. Add no secondary file, initializer output, UI metadata, fixture, script, workflow, state, score, ledger, or exception path.
- [ ] Step 9: Dispatch exactly five new fresh isolated workers with the updated Skill and the identical scenario prompt/evidence, matching the two pre-write variants' sample count. Manually read and score every output against both the exact accepted GREEN result and genuine-boundary retention; all five must converge on one focused discriminating test with minimal inline data, reject every named unsupported surface, and retain the existing SDD suite and transient boundary.
- [ ] Step 10: If any updated-Skill output fails or exposes a new rationalization, add only the minimum counter matching that observed failure and rerun a complete five-sample updated-Skill variant against the identical scenario; prior outputs from superseded wording do not count toward the final five. Do not add a scenario permutation or hypothetical policy.
- [ ] Step 11: Run the active-runtime `quick_validate.py` against `skills/keep-implementation-simple` and re-read the final Skill for portable frontmatter, Inputs, Outputs, Required Capabilities, and absence of optional files.
- [ ] Step 12: Request independent task review of the Skill diff and summarized RED/GREEN evidence. Integrate only after the reviewer confirms the qualifying five/five pre-write samples, matched five final samples, manual score for every output, retained genuine boundary, and no requirement gap, policy duplication, observable regression, or concrete current risk.

### Task 2: KIS-2 — SDD dependency and seven-role read wiring

- Deliverable: Make SDD resolve one canonical supporting-Skill path and pass it with read-before-work to exactly the seven approved fresh roles, backed by one focused regression.
- Requirement coverage: R-06, R-07, R-08.
- Acceptance coverage: AC-03, AC-04, AC-05, AC-07.
- Dependencies: KIS-1.

**Behavioral interface:**

- Consumes: the reviewed KIS-1 canonical Skill, active-runtime dependency discovery/global-root fallback, existing SDD fresh-worker dispatch surfaces, and the approved exact seven-role set.
- Produces: one resolved/readable canonical Skill path, fail-closed dependency result, read-before-work delivery for the seven roles, and no duplicated supporting policy.

**Verification intent:** A single inline-data regression must fail when the dependency is absent, unreadable, not delivered, or omitted from any approved role and must pass only when the complete seven-role contract is present; Research Worker and knowledge closeout remain outside the role set.

- Integration placement: I-2, after KIS-1 is reviewed so SDD never points workers at an incomplete contract.
- Failure owner: KIS-2 implementer owns the dependency boundary, dispatch/path wiring, focused regression, and SDD suite compatibility.

- [ ] Step 1: Re-read the reviewed KIS-1 Skill, the approved role list, current SDD entrypoint, planning-context reference, three affected prompts, and current SDD tests before modifying a Skill surface.
- [ ] Step 2: Add one focused contract regression in `test_preimplementation_context.py` with the exact seven role names and their existing owning surfaces as minimal inline expected data. Name the concrete break: a required dependency/path/read instruction missing from any approved role or appearing as a duplicated policy body.
- [ ] Step 3: Run only that focused regression and verify RED for the current missing dependency/read wiring, not for a typo, missing fixture, or unrelated assertion.
- [ ] Step 4: Extend SDD Dependency Preflight to require and resolve/read `keep-implementation-simple`, preserve existing active/global discovery behavior, and return a concrete phase/path/underlying-error `BLOCKED` before affected work when resolution or reading cannot complete.
- [ ] Step 5: Pass the resolved canonical Skill path through existing dispatch inputs for Spec Synthesizer, Spec Reviewer, Plan Author, and Plan Reviewer. Each affected prompt/reference requires reading that path completely before work and reports inability through its existing bounded return; do not copy test/fixture/guardrail policy.
- [ ] Step 6: In the existing Implementation Stage and Final Whole-Branch Review surfaces, require the orchestrator to pass the same resolved path and read-before-work instruction to Implementer, Task Reviewer, and Final Reviewer. Do not create new prompts, worker packet schema, runtime state, or compatibility bridge.
- [ ] Step 7: Keep the approved role set exact. Do not add Research Worker or knowledge closeout, and do not duplicate role-by-role tests when the one focused regression already distinguishes omission.
- [ ] Step 8: Run the focused regression and full existing SDD unittest suite; verify GREEN with no change to existing required coverage or transient-artifact behavior.
- [ ] Step 9: Run the active-runtime `quick_validate.py` against `skills/sdd-implementation`, then review the affected SDD prose for dependency identity/read/failure wiring only and the supporting Skill for exclusive policy ownership.
- [ ] Step 10: Request independent task review across KIS-1 and KIS-2 combined state. Integrate only after all seven roles, sole/default route, fail-closed behavior, and policy single-source ownership are confirmed.

### Task 3: KIS-3 — Durable closeout and combined repository verification

- Deliverable: Synchronize the reviewed result into durable knowledge and prove the integrated branch preserves every required repository gate and prohibited-surface boundary.
- Requirement coverage: none primary; contributes to R-01 through R-10 as declared in the Coverage Matrix.
- Acceptance coverage: AC-08, AC-09, AC-10.
- Dependencies: KIS-1 and KIS-2.

**Behavioral interface:**

- Consumes: reviewed KIS-1 and KIS-2 combined state, repository index and append-only log, current Git index/candidate tree, task commits, final tree, and repository-external evidence summaries.
- Produces: synchronized plan/index/log lifecycle state, fresh combined verification evidence, a final whole-branch verdict, and a local-only completion result.

**Verification intent:** Confirm architecture, context, Skill validity, all SDD tests, transient-artifact Git surfaces, diff hygiene, exact changed-path scope, and the absence of prohibited machinery without copying raw outputs into the wiki.

- Integration placement: I-3, after both implementation tasks are reviewed and serialized into the integration branch.
- Failure owner: KIS-3 knowledge worker owns index/log/plan synchronization; the task that owns a failing contract repairs it before closeout and receives exactly one scoped re-review.

- [ ] Step 1: Use `llm-wiki` single-root ingest semantics and the selected Obsidian-compatible authoring procedure to update the reviewed plan, add or refresh its active index record, and append one closeout event without rewriting prior log entries.
- [ ] Step 2: Summarize only landed scope, review verdicts, verification identities, remaining remote actions, and material residual risk. Do not copy pressure-test responses, rationalizations, command logs, raw reviews, agent identities, or runtime routing into durable knowledge.
- [ ] Step 3: Run the complete `skills/sdd-implementation/tests` unittest suite fresh and require successful exit with the focused regression included.
- [ ] Step 4: Run `scripts/validate_skill_architecture.py --all` and require the exact sole/default user-facing route to remain `sdd-implementation`.
- [ ] Step 5: Run `scripts/validate_skill_context.py --all` and require all current context contracts to remain valid.
- [ ] Step 6: Run the active-runtime `quick_validate.py` separately for `skills/keep-implementation-simple` and `skills/sdd-implementation`.
- [ ] Step 7: Materialize the current Git index candidate tree and run `scripts/validate_sdd_transient_artifacts.py` for that candidate. Validate each new task/integration commit as a new commit and the integrated tip as the final tree when those surfaces exist; any `.superpowers/**` violation aborts closeout.
- [ ] Step 8: Run `git diff --check` over the final working diff and the baseline-to-integration commit range, and inspect the exact changed-path set for optional metadata, extra fixtures/tests, duplicated policy, new runtime machinery, or removed required validation.
- [ ] Step 9: Verify the original checkout still matches captured branch, HEAD, and staged/unstaged/untracked status; do not repair unrelated original-checkout state.
- [ ] Step 10: Dispatch one fresh final whole-branch reviewer over baseline through the integration branch, including code, tests, approved spec, reviewed plan, and knowledge closeout. A material finding goes to its owning task for one repair and one scoped re-review before the canonical final verdict.
- [ ] Step 11: Record `LOCAL_COMPLETE` only after all fresh gates pass, every reviewed task commit is reachable, knowledge is synchronized, and the final verdict has no material finding. Record push/PR/merge/release/live-install as unperformed absent separate authorization.

## Dependency Graph

| Task | Dependencies |
| --- | --- |
| KIS-1 | none |
| KIS-2 | KIS-1 |
| KIS-3 | KIS-1, KIS-2 |

## Execution Order

1. KIS-1
2. KIS-2
3. KIS-3

## Serialized Integration

- I-1: KIS-1. Preconditions: before the first supporting-Skill write, exactly five qualifying no-guidance outputs and five unchanged-current-Skill outputs use the identical accepted scenario/evidence, every output is manually scored, variance is assessed, and the current Skill has verified RED; after the minimal edit, a matched final set of five updated-Skill outputs is manually scored GREEN with the genuine boundary retained. Active-runtime Skill validation passes and independent task review is clean. Combined-state expectation: one portable supporting Skill owns the complete simplicity policy with no new infrastructure.
- I-2: KIS-2. Preconditions: I-1 is reviewed and reachable, the focused SDD regression is verified RED before SDD edits and GREEN afterward, the full SDD suite passes, and independent task review is clean. Combined-state expectation: SDD resolves and delivers the canonical Skill to exactly seven approved roles while remaining the sole/default route and without policy duplication.
- I-3: KIS-3. Preconditions: I-1 and I-2 are reviewed and reachable, durable targets and authority remain resolved, and all combined gates are runnable. Combined-state expectation: index/log/plan are synchronized, required validation and transient boundaries are preserved, prohibited machinery is absent, and final review supports local completion.

## Post-Integration Combined Verification

**Scope:** R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10 and AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 across the integrated `82dcd32157ff9690ae038f982f3916009e449f80..codex/keep-implementation-simple/planning` change.

**Pass criteria:** The exact combined pressure scenario has five manually scored no-guidance controls and five manually scored unchanged-current-Skill samples before the first Skill write, plus five manually scored updated-Skill samples after the final wording; the pre-write variants establish trustworthy RED and observable variance, the matched updated variant is uniformly GREEN, and the separately scored retention dimension confirms the genuine SDD/transient boundary is preserved without adding a second scenario. One focused SDD regression covers dependency plus all seven roles; the complete SDD suite, architecture, context, both Skill validations, transient candidate/new-commit/final-tree surfaces, and diff checks pass; the changed-path review finds no optional metadata, duplicate policy, speculative test/fixture/guardrail, prohibited machinery, or weakened required boundary; knowledge is synchronized and final review has no material finding.

**Required evidence:** Repository-external RED/GREEN summary identity, fresh gate exit results, exact changed-path list, reachable reviewed task commits, synchronized index/log/plan identities, original-checkout preservation, and final whole-branch verdict. Raw outputs and transcripts remain outside durable knowledge.

**Failure owner:** KIS-1 owns supporting-policy and behavioral-evaluation failures; KIS-2 owns dependency/role-wiring and SDD-regression failures; KIS-3 owns knowledge, combined-gate, reachability, original-checkout, and final-review closeout failures.

## Author Self-Review

- Spec coverage: all 10 Confirmed Decisions and all 10 numbered acceptance criteria have exactly one primary owner in the Coverage Matrix; no in-scope requirement is unassigned.
- File compatibility: every planned file exists in the current tree except this new plan; no new implementation prompt, fixture family, validator, schema, runtime state, or UI metadata is required.
- TDD order: five no-guidance and five unchanged-current-Skill outputs are manually scored before any supporting-Skill write; the unchanged Skill has verified RED before the matched five-output updated-Skill GREEN; genuine-boundary retention is scored separately without another scenario. The focused SDD regression is RED before SDD Skill edits; both tasks finish GREEN and independently reviewed.
- Type and identity consistency: `KIS-1` through `KIS-3`, I-1 through I-3, `KIS-SPEC-2026-08-14-V1`, the baseline SHA, worktree, branch, canonical Skill path, and seven role names are consistent across tasks, dependencies, integration, and combined verification.
- Placeholder and prohibited-body scan: no placeholder, prospective production/test body, script body, shell control-flow body, patch body, execution command body, scheduler/runtime machinery, or concrete runtime selection is present.

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed

Reviewer vocabulary is `ready` or `issues_found`. Fresh independent re-review returned `ready` after verifying the prior KIS-1 repair and the unchanged substantive plan contract. It found no decision request or material risk. Missing remote publication authorization does not change local plan readiness.
