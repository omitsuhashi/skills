# Keep Implementation Simple V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to execute this plan sequentially. Each implementation task uses a fresh implementer and an independent reviewer, and checkbox steps are the progress ledger.

**Plan identity:** `KIS-PLAN-2026-08-14-V2`

**Goal:** 既存`keep-implementation-simple`を変更せず、SDDの既存surfaceだけで、正確な7 roleが同じresolved canonical KIS pathを受け取り、作業前に全文readするcontractを実装する。

**Architecture:** `skills/sdd-implementation/SKILL.md`の既存Dependency Preflightが一つのcanonical KIS pathをresolveして全文readし、その同じpathを既存dispatch surfaceへ渡す。既存test moduleの一つのinline-data regressionでdependency、7 role mapping、除外role、single-source policyをまとめて識別し、追加のprompt、fixture、resolver、schema、runtime machineryは作らない。

**Tech Stack:** portable Markdown Skill contracts、Python 3 `unittest`、既存repository validators、LLM Wiki single-root knowledge。

## Approved North Star Identity

- Approved North Star path: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- Approved North Star anchor: `North Star`
- Approved snapshot identity: `KIS-SPEC-2026-08-14-V2`
- Approval-snapshot content SHA-256: `1a99024e9f04791a4194304d01a50c42a29b516c4c2887b144079239f09dcfbd`
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- Approved spec snapshot identity: `KIS-SPEC-2026-08-14-V2`
- Approved-spec content SHA-256: `1a99024e9f04791a4194304d01a50c42a29b516c4c2887b144079239f09dcfbd`
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

Authoring checks established that the baseline is an ancestor of the current planning branch, all named owner surfaces exist, the spec digest matches both approval declarations, and current KIS SHA-256 is `2c2361f04ca6d2dd7433d2dfa80ff173a14f68ef401df0e98e7d4366d1d23b3f`. Initial independent review returned `issues_found` for two execution-order gaps; both are repaired below, and the fresh independent re-review returned `ready`, completing the local Plan Stage gate for Implementation Stage entry.

## Global Constraints

- Human authority remains the approved North Star and Written Spec `KIS-SPEC-2026-08-14-V2`; plan repair, readiness, implementation, review, and local integration are agent / repository-owned.
- Before work, Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewer must receive the same Dependency Preflight-resolved canonical `keep-implementation-simple/SKILL.md` path and read that file fully.
- Research Worker and knowledge closeout worker are excluded from this requirement.
- `skills/keep-implementation-simple/**` is read-only. Preserve `skills/keep-implementation-simple/SKILL.md` byte-for-byte from baseline and keep its policy the single source.
- Production/test writes are limited to the six existing SDD files in the File Map. Do not add or rename a prompt, test file, fixture, validator, optional metadata, alias Skill, or compatibility layer.
- Do not add resolver、classifier、cache、trace、provenance model、schema、protocol、scheduler、retry / fallback、dedicated runtime state、test-only runtime、or duplicated KIS policy.
- Preserve sequential SDD, fresh isolated workers, explicit model selection, independent task review, fresh final whole-branch review, current security/data-integrity/mechanical validation, required coverage, and transient-artifact rejection.
- Source, test, and durable writes stay in the trusted planning worktree. Raw reviews and command output stay in a repository-external task/session temporary path.
- Local readiness never authorizes push、PR、merge、release、live install、Issue/comment/project mutation、or another remote write.

## File Map

- `skills/sdd-implementation/SKILL.md`: require/resolve/read KIS in Dependency Preflight; deliver the same path to Implementer、Task Reviewer、Final Reviewer through the existing Implementation and Final Review sections.
- `skills/sdd-implementation/references/planning-context.md`: carry the resolved path and read-before-work instruction for Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer.
- `skills/sdd-implementation/prompts/spec-synthesizer.md`: existing Spec Synthesizer input/read/failure surface.
- `skills/sdd-implementation/prompts/spec-reviewer.md`: existing Spec Reviewer input/read/failure surface.
- `skills/sdd-implementation/prompts/plan-reviewer.md`: existing Plan Reviewer input/read/failure surface.
- `skills/sdd-implementation/tests/test_preimplementation_context.py`: add exactly one focused regression with minimal inline 7-role/owner-surface data.
- `knowledge/wiki/syntheses/keep-implementation-simple-plan.md`: reviewed execution contract and later closeout summary.
- `knowledge/index.md`: active V2 spec/plan discovery state.
- `knowledge/log.md`: append-only planning and later closeout events.

## Requirement And Acceptance Inventory

- R-01: Keep canonical KIS unchanged and retain policy ownership there.
- R-02: Use existing Dependency Preflight to resolve/read one canonical KIS path and fail closed with the required evidence.
- R-03: Deliver that same path and full-read-before-work instruction to exactly seven approved roles through existing owner surfaces.
- R-04: Let SDD own only dependency identity, resolved path, instruction, role set, and fail-closed boundary.
- R-05: Add exactly one focused inline-data regression in the existing test module.
- R-06: Preserve SDD as the sole/default implementation route and retain current required validation.
- AC-01: Bind every implementation surface to V2 and the approved baseline.
- AC-02: Produce an empty baseline-to-tip KIS diff.
- AC-03: Match the baseline and final KIS SHA-256 to the approved digest.
- AC-04: Prove single-path Dependency Preflight resolution/read and evidence-bearing fail-closed behavior.
- AC-05: Prove same-path full-read delivery to exactly seven approved roles.
- AC-06: Exclude Research/knowledge closeout and preserve KIS as the only policy owner.
- AC-07: Prove the contract with one inline-data regression and no prohibited new surface.
- AC-08: Preserve the sole/default SDD route through architecture validation.
- AC-09: Fresh-run every required validation successfully.
- AC-10: Synchronize the V2 plan, index, and append-only log.

## Coverage Matrix

| ID | Primary owner | Contributing tasks |
| --- | --- | --- |
| R-01 | KIS-2 | none |
| R-02 | KIS-1 | none |
| R-03 | KIS-1 | none |
| R-04 | KIS-1 | none |
| R-05 | KIS-1 | none |
| R-06 | KIS-2 | none |
| AC-01 | KIS-2 | none |
| AC-02 | KIS-2 | none |
| AC-03 | KIS-2 | none |
| AC-04 | KIS-1 | none |
| AC-05 | KIS-1 | none |
| AC-06 | KIS-1 | none |
| AC-07 | KIS-1 | none |
| AC-08 | KIS-2 | none |
| AC-09 | KIS-2 | none |
| AC-10 | KIS-2 | none |

## Tasks

### Task 1: KIS-1 — SDD canonical KIS wiring and focused regression

- Deliverable: TDDで一つのcanonical KIS pathを正確な7 roleへ既存surfaceから渡し、独立Task Reviewerが承認したSDD-only changeを作る。
- Requirement coverage: R-02, R-03, R-04, R-05.
- Acceptance coverage: AC-04, AC-05, AC-06, AC-07.
- Dependencies: none.

**Behavioral interface:**

- Consumes: V2 spec、baseline/current KIS、existing Dependency Preflight、planning context、three existing prompts、Implementation/Final Review sections、existing preimplementation-context test helpers.
- Produces: one resolved/read canonical KIS path; the same path plus full-read-before-work instruction for the exact seven-role set; existing-boundary failure reporting; one focused inline-data regression; no KIS diff or new artifact family.

**Verification intent:** The focused test must RED only because the baseline lacks the required dependency/path/read wiring, then GREEN only when all seven role-to-owner mappings share the same path, both excluded roles remain absent, and no KIS policy copy or new supporting surface is introduced.

- Integration placement: I-1, as the only implementation/review task before knowledge closeout.
- Failure owner: KIS-1 implementer owns production/test defects; its independent Task Reviewer owns requirement-fit, material simplicity, and current-risk verdicts.

- [x] Step 1: The fresh Implementer reads the resolved canonical KIS file fully before work, then reads the V2 spec and only the six production/test owner files in the File Map. Confirm the baseline-to-worktree KIS diff is empty before any source edit.
- [x] Step 2: Add exactly one test case to `test_preimplementation_context.py`. Keep the seven role names and their owner-file mapping as minimal inline data; use the module's existing loaded text/helpers and include the two excluded roles in the same contract rather than another test.
- [x] Step 3: Run only the new test and record verified RED caused by missing KIS dependency/path/full-read wiring. Stop if it fails because of syntax, missing fixture, or an unrelated contract.
- [x] Step 4: Extend the existing Dependency Preflight prose in `skills/sdd-implementation/SKILL.md` to require one readable canonical KIS path and read it fully. Preserve active discovery/global-root fallback; distinguish complete no-match through the existing missing-dependency result from discovery/candidate/path/read failure through `BLOCKED: dependency preflight failed` with phase, observed or attempted path, and underlying error before affected work.
- [x] Step 5: Extend `planning-context.md` and the three existing prompts so Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer receive that same resolved path, read it fully before work, and use their existing bounded return when role/phase, path, or underlying read error prevents completion.
- [x] Step 6: Extend only the existing Implementation Stage and Final Whole-Branch Review sections so Implementer、Task Reviewer、Final Reviewer receive that same path and full-read instruction before work. Do not route it to Research Worker or knowledge closeout.
- [x] Step 7: Run the focused test to verified GREEN, then run the full existing SDD unittest suite. Inspect the six-file implementation/test diff to confirm exact role membership, one inline-data test, single-source KIS policy, and absence of new prompt/fixture/resolver/schema/runtime machinery.
- [x] Step 8: After the focused GREEN, full SDD suite, six-file diff inspection, and empty KIS diff pass, run the existing `scripts/validate_sdd_transient_artifacts.py` against the current Git index, then materialize the exact staged candidate tree and run the same validator with `--candidate-tree <candidate-tree>`. Any failure stops before commit creation or I-1 transition.
- [x] Step 9: Create one scoped KIS-1 implementation commit containing only the approved six-file production/test change after Step 8 passes, and verify that the commit is reachable from the integration branch.
- [x] Step 10: Run `scripts/validate_sdd_transient_artifacts.py --new-commit <KIS-1-commit>` against the new scoped commit. Any failure stops before Task Review or I-1 transition.
- [x] Step 11: Dispatch a fresh independent Task Reviewer after it reads the same KIS path fully. Give it the exact committed range `82dcd32157ff9690ae038f982f3916009e449f80..<KIS-1-commit>` and integrate only a verdict with no requirement gap, scope excess, observable regression, or concrete current risk; any repair returns to the owning implementer, repeats the applicable index/candidate/commit validation, and receives one scoped re-review before I-1.

### Task 2: KIS-2 — Durable closeout and combined verification

- Deliverable: Synchronize durable V2 state, prove the unchanged-KIS and repository gates on the combined branch, and obtain the canonical final whole-branch verdict.
- Requirement coverage: R-01, R-06.
- Acceptance coverage: AC-01, AC-02, AC-03, AC-08, AC-09, AC-10.
- Dependencies: KIS-1.

**Behavioral interface:**

- Consumes: reviewed KIS-1 result and commit, V2 spec/plan, index/log, current Git index and integrated tip, existing validators, original-checkout snapshot.
- Produces: synchronized plan/index/log; exact unchanged-KIS evidence; fresh combined gate results; reachable reviewed commits; final review verdict; local-only completion state.

**Verification intent:** Closeout succeeds only when the KIS baseline-to-tip diff is empty, both KIS digests match, the complete SDD/architecture/context/Skill/transient/diff gates pass fresh, changed paths remain within the approved SDD and durable surfaces, and final review finds no material defect.

- Integration placement: I-2, after reviewed KIS-1 is reachable from the integration branch.
- Failure owner: the knowledge worker owns plan/index/log synchronization; KIS-1 owns SDD/test regressions; the orchestrator owns candidate/new-commit/final-tree, reachability, original-checkout, and final-review gates.

- [x] Step 1: Verify spec identity `KIS-SPEC-2026-08-14-V2` and baseline `82dcd32157ff9690ae038f982f3916009e449f80` across the reviewed plan and current durable discovery state.
- [x] Step 2: Require `git diff 82dcd32157ff9690ae038f982f3916009e449f80 -- skills/keep-implementation-simple/SKILL.md` to produce no output. Compute SHA-256 for the baseline blob and current KIS file and require both to equal `2c2361f04ca6d2dd7433d2dfa80ff173a14f68ef401df0e98e7d4366d1d23b3f`.
- [x] Step 3: Fresh-run `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests`, `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`, and `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`; require success and confirm architecture reports only `sdd-implementation` as the sole/default user-facing implementation route.
- [x] Step 4: Fresh-run the active runtime skill-creator `quick_validate.py` separately for `skills/keep-implementation-simple` and `skills/sdd-implementation`; require both to pass.
- [x] Step 5: Validate the already-created KIS-1 commit with `scripts/validate_sdd_transient_artifacts.py --new-commit <KIS-1-commit>`. Run `git diff --check` for the working state and `82dcd32157ff9690ae038f982f3916009e449f80..<KIS-1-commit>`, inspect the exact changed-path set, and fail on any KIS edit, new test/prompt/fixture/validator/metadata, policy duplicate, resolver/schema/runtime machinery, weakened validation, or out-of-bound write.
- [x] Step 6: Only after Steps 1-5 produce actual fresh results, dispatch a fresh knowledge closeout worker under the `llm-wiki` single-root contract. Update only this plan, its existing `knowledge/index.md` entry, and one append-only `knowledge/log.md` closeout event with those actual result identities, landed scope, review verdict, remaining remote actions, and material residual risk; do not copy raw outputs or transcripts.
- [x] Step 7: Validate the synchronized wiki before Final Review by running the existing `skills/llm-wiki/tests` suite and inspecting the plan/index/log relation identities, append-only log effect, and allowed write set; any failure returns to the knowledge worker.
- [ ] Step 8: Run `scripts/validate_sdd_transient_artifacts.py` against the current closeout index, materialize the exact staged closeout candidate tree, and validate it with `--candidate-tree <closeout-candidate-tree>`. Any failure stops before closeout commit creation or Final Review dispatch.
- [ ] Step 9: Create one scoped closeout commit containing only the synchronized plan/index/log changes, validate it with `--new-commit <closeout-commit>`, and validate the integrated tip with `--final-tree <integration-tip>`. Verify the KIS-1 and closeout commits are reachable from that tip and the original checkout still matches its captured branch, HEAD, staged, unstaged, and untracked state; any failure stops before Final Review dispatch.
- [ ] Step 10: Only after Steps 1-9 pass, dispatch one fresh Final Reviewer after it reads the same canonical KIS path fully. Review `82dcd32157ff9690ae038f982f3916009e449f80..<integration-tip>` across code, test, V2 spec, reviewed plan, and committed knowledge closeout; a material finding returns to its failure owner for one repair and one scoped re-review before the canonical verdict.
- [ ] Step 11: Record `LOCAL_COMPLETE` only after every gate passes and final review is clean. Keep push、PR、merge、release、live install、and other remote writes unperformed absent separate authorization.

## Implementation closeout candidate

- KIS-1 is implemented and reviewed: `099c1df3cd35a75d838e7c66279293723f4dbbc0` landed the approved six existing SDD owner/test files, and `e3815157b8af151d6fc5683e851eec3108dd69c3` repaired the complete-no-match dependency result and role-to-owner-surface regression binding. The initial independent Task Review reported two Important findings; the scoped re-review found both addressed and no new Critical or Important breakage.
- KIS-2 Steps 1–5 passed before this durable update: SDD unittest `94/94`; skill architecture and one skill-context contract; separate skill-creator quick validation for KIS and SDD; transient-artifact validation for the KIS-1 commit; and working/range `git diff --check`. Architecture keeps `sdd-implementation` as the sole/default route.
- The baseline and current KIS SHA-256 are both `2c2361f04ca6d2dd7433d2dfa80ff173a14f68ef401df0e98e7d4366d1d23b3f`, and the baseline-to-tip KIS diff is empty. Before this closeout, the baseline-to-tip scope was the four existing durable files (V2 spec, this plan, index, log) plus exactly the approved six existing SDD owner/test files; no new file, fixture, prompt, validator, metadata, machinery, or policy copy landed.
- Planning lifecycle evidence is `9cdf6c51185382f5ce62eec88ce3a8c925aa5704` with readiness correction `ade270462404ea0d8aa073f83c267c951e0e3a7c`. This update completes KIS-2 Steps 6–7 only. Steps 8–10 remain controller-owned and pending, so `LOCAL_COMPLETE` is not claimed. Remote actions remain unperformed and unauthorized.

## Dependency Graph

| Task | Dependencies |
| --- | --- |
| KIS-1 | none |
| KIS-2 | KIS-1 |

## Execution Order

1. KIS-1
2. KIS-2

## Serialized Integration

- I-1 — KIS-1: Preconditions are verified RED, minimal GREEN, full SDD suite success, empty KIS diff, successful current-index and nominated-candidate validation, one reachable scoped KIS-1 commit, successful new-commit validation, and independent Task Reviewer approval over the exact committed baseline-to-task range. Any repository-gate failure stops before commit creation or transition. Expected combined state is the six existing SDD production/test files implementing one-path seven-role wiring with one focused regression and no prohibited surface.
- I-2 — KIS-2: Preconditions are reviewed KIS-1 reachability, resolved wiki authority, fresh combined results produced before durable recording, synchronized plan/index/log with successful wiki validation, successful closeout index/candidate validation, and one reachable scoped closeout commit whose new-commit and integrated final tree validations pass before Final Review. Expected combined state is committed V2 durable knowledge, fresh full verification, original-checkout preservation, and a clean final whole-branch verdict.

## Post-Integration Combined Verification

**Scope:** All inventory IDs across `82dcd32157ff9690ae038f982f3916009e449f80..codex/keep-implementation-simple/planning`, including the exact six production/test owner files and three durable synchronization files.

**Pass criteria:** KIS remains byte-identical with the approved SHA-256 and an empty baseline-to-tip diff; the single regression proves one resolved/read path, exact seven-role delivery, and both exclusions; every fresh repository gate in KIS-2 passes; the changed-path set contains no prohibited surface or policy copy; every reviewed commit is reachable; durable state and original checkout are preserved; final review has no material finding.

**Required evidence:** Focused RED/GREEN result, full-suite and validator exit results, KIS diff/digests, KIS-1 index/candidate/new-commit identities, exact Task Review range and verdict, closeout index/candidate/new-commit/final-tree identities, exact changed paths, reachable commits, validated plan/index/log identities, original-checkout preservation, and final verdict. Record fresh verification identities only after the corresponding runs complete, and keep raw outputs outside durable knowledge.

**Failure owner:** KIS-1 owns SDD wiring/test failures; KIS-2 owns unchanged-KIS, repository gate, durable synchronization, reachability, original-checkout, and final-review closeout failures.

## Author Self-Review

- Observable outcome and smallest owner: unchanged KIS plus existing SDD dependency/dispatch surfaces are sufficient; the abandoned KIS edit and behavioral evaluation are absent.
- Coverage: R-01 through R-06 and AC-01 through AC-10 each appear once in the inventory and once as one primary task assignment; no contributing assignment duplicates ownership.
- Buildability: every named production/test/durable file exists, and the existing test module already loads all affected SDD surfaces.
- TDD and review order: KIS-1 requires focused RED before production edits, minimal GREEN, full suite, index/candidate gates, scoped commit/new-commit validation, then independent Task Review over the committed range before I-1. KIS-2 produces fresh combined evidence before durable recording, validates wiki and the scoped closeout commit/final tree, then dispatches Final Review.
- Scope scan: no prospective code/test body, placeholder implementation, KIS edit, new prompt/test file/fixture/resolver/schema/runtime machinery/metadata, duplicated policy, parallel issue adapter, or remote mutation is planned.
- Identity and dependency consistency: `KIS-PLAN-2026-08-14-V2`, `KIS-SPEC-2026-08-14-V2`, baseline SHA, KIS digest, task IDs KIS-1/KIS-2, and I-1/I-2 are consistent.

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed

Author self-review is complete with no gap or material risk. Fresh independent Plan Reviewer verdict `ready` and durable verdict integration are complete; remote publication authorization is not a local readiness blocker.
