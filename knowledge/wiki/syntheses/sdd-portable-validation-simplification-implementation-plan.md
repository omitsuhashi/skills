---
title: SDD portable validation と責務単純化 実装計画
date: 2026-08-15
status: amendment-plan-ready-pending-implementation
review_state: independent-plan-review-ready
plan_readiness: ready
tags:
  - sdd-implementation
  - skill-portability
  - validation
  - implementation-plan
aliases:
  - SDD Portable Validation Simplification Implementation Plan
---

# SDD portable validation と責務単純化 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. 各 task は checkbox で進捗を追跡し、task review を通過してから次へ進む。

**Goal:** SPV-1〜SPV-5で完了したportable validationを維持したまま、root copied plan snapshotと重複parity runnerを既存ownerへ吸収し、canonical plan direct validationとexecution-time resource boundaryを最小差分で成立させる。

**Architecture:** portable packageのsingle semantic parserはpackage-relative fixtureを引き続き所有し、rootの既存CI contract testだけがcanonical durable planのrepository-bound identityを直接読む。実行時inventoryはprompt/referenceだけ、test/harness/fixtureはisolated release/CI copy-setだけに分離し、direct Git、First-Write、KISの既存behaviorは変更しない。

**Tech Stack:** portable Markdown skill contract、Python 3.9+ standard-library `unittest`、Git CLI、GitHub Actions、Obsidian-compatible LLM Wiki、current Superpowers lifecycle skills。

## Approved North Star Identity

- Approved North Star path: knowledge/wiki/syntheses/sdd-portable-validation-simplification.md
- Approved North Star anchor: 目標
- Approved North Star identity: sdd-portable-validation-simplification#目標@2026-08-14
- Approved snapshot SHA-256: d701b2087983cbe5ef715d866f923c0f8da39ec23ed11c713b28f8d9c33993db
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: knowledge/wiki/syntheses/sdd-portable-validation-simplification.md
- Approved spec SHA-256: d701b2087983cbe5ef715d866f923c0f8da39ec23ed11c713b28f8d9c33993db
- Approval state: approved

## Plan Binding

- Repository baseline: 4d67bed6d297ba4e9a0f44559d3ca45c9a035976
- Planning worktree: verified task-linked worktree; runtime path is not durable evidence
- Integration branch: codex/sdd-portable-validation-simplification
- Current-tree compatibility: compatible
- Independent review verdict: ready
- Repository checks: passed
- Readiness evidence state: current
- Binding evidence: planning/spec commitは`8b433806af6835bbf859bea7a7e30a0752d6d294`である。pre-amendment feature tip `e5b6b77e790d8d89952b84cfbb04886546e8e8e5`とcurrent main `5e68f5c466b7efcd6e8b3ebb1daf1e6f76682684`はtree `8f995222eef73ab5d56a9fb227f367bf8b44c634`が完全一致し、merge baseは`15152126fe0785bcf789a9ecbfe752b9e368fc4e`である。current HEADのtree差分はapproved spec/plan amendmentだけである。ordinary mergeは二つのcanonical planning documentsだけのadded-in-both conflictでblockedとなった歴史的evidenceであり、raw transcriptは保存しない。content edit前にこの全identity、non-planning content divergence不在、original checkout fingerprint、target branchを再検証し、feature branch treeを明示的に保持するcurrent main second-parentのnon-force no-ff `ours` mergeを作成する。merge後は両parent/lineageのreachabilityとmerge treeがpre-merge feature treeに等しいことを確認する。any drift、unknown ancestry、branch/original fingerprint mismatch、non-planning divergence、content conflict、rebase、rewrite、force、またはfallbackでは停止する。

## Current Independent Plan Review Summary

- Review verdict: ready
- Disposition: ready
- Decision requests: none
- Material risks: none
- Durable finding summary: exact-identity `ours` no-ff merge predicate、feature-tree retention proof、current amendment task ownership、dependency/order、combined verification、and pending AM-1/AM-2 status are buildable and sufficient. The reviewed plan does not authorize the merge or implementation before its declared predicates are reverified.

## Historical Independent Plan Review Summary

- Prior review date: 2026-08-14; historical only
- Current review date: 2026-08-14
- Prior verdict: ready before the current serialized-integration repair; historical only
- Current verdict: ready
- Disposition: ready
- Decision requests: none
- Material risks: none
- Durable finding summary: prior post-origin `ready` verdict はpre-repair bytesのhistorical evidenceである。fresh independent reviewは、root-owned parity replacementを先にGREENにしてからpackage dependencyを除去し、root parity/package semantic/isolated closureを同じSPV-2 commit/review boundaryでGREENにするatomic cutover repairを`ready`と判定した。当該verdictはTask 1完了時点のhistorical plan-readiness evidenceに限定し、current landed statusは下記Implementation Progressを正本とする。five-task chain、R-01〜R-15 / AC-01〜AC-14のunique primary ownership、strict-zero/First-Write/KIS preservation、decision request `none`、material risk `none`は不変である。raw review artifact、path、transcriptはdurable planへ複製していない。

## Historical Final Whole-Branch Review Summary

- Canonical review head `9f4787f` returned Critical 0 / Important 4 / Minor 0.
- One bounded final fix `e9d1bcb` addressed all four original findings. Its scoped re-review confirmed all four addressed and identified one new Important KIS spec/plan SHA binding drift.
- Human explicitly approved one bounded binding repair. Commit `3ef7564` preserved historical KIS snapshot `1a99024e9f04791a4194304d01a50c42a29b516c4c2887b144079239f09dcfbd` and bound current Human-approved KIS spec `0c9570f9d3d54821d3ce6302c0a46824192b0d5c05c3b2e03e6923a0565d4aa4`.
- Final scoped re-review returned residual finding `ADDRESSED`, new Critical 0 / Important 0, and ready for the dependent local-completion status transition. No raw review transcript or runtime artifact identity is stored here.

## Implementation Progress

| Task | Reviewed result | Current durable state |
| --- | --- | --- |
| SPV-1 | `9a4e155..481d424`; scoped re-review clean | explicit target、three direct-Git gates、fresh recomputation、failure taxonomy landed |
| SPV-2 | `f1f5d96..42ce4df`; scoped re-review clean | root parity GREEN後のpackage cutover、portable fixture、isolated closure landed |
| SPV-3 | `07a1e8d`; independent review clean | root parity / isolated closure CI wiring landed; strict-zero owner preserved |
| SPV-4 | `84e3940..f29c0fd`; scoped re-review clean | thin composition、Authority A、First-Write / exact-seven KIS preservation landed |
| SPV-5 | `41c2a63..3ef7564`; closeout, canonical final review, bounded fixes, and scoped re-reviews complete | knowledge synchronization、fresh combined verification、final direct-Git / root strict-zero gates、final review、Human-approved KIS binding repair、dependent `LOCAL_COMPLETE` transition completed |

## Historical SPV-1〜SPV-5 Global Constraints

- Authority A を維持する。Human authority は material Written Spec change と別途 authorization が必要な remote action に限定し、execution method、issue plan、plan 自体の追加 Human approval は要求しない。
- target repository は caller が明示し、canonical absolute path として解決する。CWD、installed skill の source checkout、親 directory、別 worktree から target を推定しない。
- generic mechanical validation は `exceptional-local-scratch-pre-write`、`pre-commit-candidate`、`final-closeout` の三点だけとし、同じ explicit target に対する direct Git probe だけを使う。
- standalone/bundled validator、repository validation adapter、hook registry、scheduler、persistent state、telemetry、追加 protocol、evidence cache、exactly-once machinery を新設しない。
- `scripts/validate_sdd_transient_artifacts.py` とその root regression、`--post-policy-history` CI invocation は repository owner の既存 surface として保持する。current authority は index、nominated candidate tree、repository policy boundary 以後の reachable new commits、final tree の strict-zero contract であり、completed marker や過去の exact path/mode/blob/lineage ではない。policy-root identity と actual-parent relationship は root owner にだけ保持し、portable package から参照しない。
- canonical-plan parity は package test から root-owned fixture/regression へ移すが、root replacementを先にGREENにしてからpackage dependencyを除去し、同じSPV-2 commit/review boundaryでcutoverする。coverage を削除、optional 化、または quick shape check へ縮退させない。
- Superpowers が generic lifecycle、worktree allocation、TDD、dispatch、review/fix、branch finishing を所有する。SDD はそれらの algorithm や fallback を再記述しない。
- SDD-owned First-Write Worktree Gate の repository-change first entry、task-owner identity、Git worktree registration、bound CWD/path、single writer、exactly one absent artifactの atomic publish、separate commit plan、zero-write/no-fallback、original-checkout preservation を削除・緩和しない。
- `keep-implementation-simple` は dependency preflight で同じ canonical path を一度 resolve し、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewer の exact seven roles が作業前に全文 read する。discovery/read failure は affected role の work 前に bounded failure とし、fallback protocol を作らない。
- fresh worker/model selection、repository-external handoff、target/CWD/write destination binding は public contract の一つの runtime capability interface に集約し、prompts/references は owner と task-local inputs だけを参照する。
- capability/resource/path/state が一意に判定できない場合は、影響する最初の mutation 前に fail closed にする。runtime-specific tool/model/provider 名を durable contract に固定しない。
- parallel eligibility は agent/repository-owned とし、dependency または write-conflict evidence が unknown なら sequential execution に戻す。本実装計画自体は shared file ownership があるため全 task を sequential に実行・統合する。
- package public contract、prompts、references、tests、fixtures に repository 固有 commit/blob hash、canonical wiki path、migration marker、username/absolute path を残さない。
- prospective production/test/script body、patch body、execution command body、concrete runtime routing を durable plan に保存しない。
- remote push、PR、merge、release、live install その他の remote write は本計画の local readiness に含めず、別途明示 authorization がない限り実行しない。
- `knowledge/raw/**` は変更しない。reviewed plan と implementation closeout は `knowledge/index.md` と append-only `knowledge/log.md` を同期する。

## Historical SPV-1〜SPV-5 File Responsibility Map

| Path | Operation | Exact responsibility |
| --- | --- | --- |
| `skills/sdd-implementation/SKILL.md` | Implemented in SPV-1; modify in SPV-4 | portable public contract、explicit target、三つの normative direct Git gate、First-Write Worktree Gate、KIS preflight/seven-role wiring、failure classification、thin Superpowers/knowledge composition、単一 runtime capability interface の正本 |
| `skills/sdd-implementation/tests/test_portable_git_gates.py` | Implemented and fixed in SPV-1 | synthetic Git repository 上で三 gate の direct probe、positive/negative state、mutation invalidation、failure classification を public behavior として forward-testする owner |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Implemented in SPV-1; modify in SPV-4 | public contract の explicit target/gate uniqueness、portable content、Superpowers ownership、authority A、First-Write/KIS preservation、禁止 surface を固定する contract owner |
| `skills/sdd-implementation/tests/test_transient_artifact_contract.py` | Implemented in SPV-1; modify in SPV-4 | repository-external default、exceptional scratch gate、durable summary route、gate名参照だけが重複しないことを固定する owner |
| `skills/sdd-implementation/tests/test_isolated_install.py` | Create in SPV-2 | skill folder の isolated copy、source/parent 非参照、package-relative resource closure、broken-installation/target-runtime failure 分離を forward-testする owner |
| `skills/sdd-implementation/tests/test_plan_contract.py` | Modify in SPV-2 | portable plan semantic validator と package-relative representative fixture のみを検証し、root canonical plan を読まない owner |
| `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md` | Replace in SPV-2 | repository identity、canonical path、個人 path を含まない package-local representative ready-plan fixture |
| `skills/sdd-implementation/references/plan-contract.md` | Modify in SPV-2 | portable plan schema/prohibition/readiness contract。package fixture と root canonical parity の owner 分離を明示する owner |
| `scripts/fixtures/sdd-plan-contract/ready-plan.md` | Create in SPV-2; consume and preserve in SPV-3/SPV-5 | package dependency removal前に現行 canonical SDD plan parity を引き継ぐ repository-owned expected fixture |
| `scripts/test_sdd_canonical_plan_parity.py` | Create and GREEN in SPV-2; consume and preserve in SPV-3/SPV-5 | package dependency removal前に canonical SDD plan と root fixture の inventory/coverage/graph/order parity を固定する repository regression owner |
| `scripts/validate_sdd_transient_artifacts.py` | Preserve and verify in SPV-3/SPV-5 | explicit repository root の current index、nominated candidate tree、repository policy boundary 以後の reachable new commits、final tree を strict-zero で fail closed にする root-only owner。policy-root identity と actual parent の解釈はここから portable package へ漏らさない |
| `scripts/test_validate_sdd_transient_artifacts.py` | Preserve and verify in SPV-3/SPV-5 | one exact diagnostic category、marker非 authorization、index/candidate/new-commit/final-tree strict-zero、staged deletion、pre-policy historical ancestor blob の current root regression owner |
| `.github/workflows/skill-architecture.yml` | Modify in SPV-3 | `--post-policy-history` root validation、root regressions、canonical parity、isolated package closure、package tests を full-history source checkout で fresh 実行する CI owner |
| `scripts/test_skill_ci_workflow.py` | Modify in SPV-3 | `--post-policy-history` invocation、reachable clean clone、`origin/main` 非依存、shallow-history rejection、post-policy add-then-delete rejection、parity/isolated invocation を固定する contract owner |
| `skills/sdd-implementation/references/planning-context.md` | Modify in SPV-4 | pre-implementation stage routing と worker-specific handoff owner。common runtime/path/model guard は public contract を参照する |
| `skills/sdd-implementation/references/research-stage.md` | Modify in SPV-4 | Research 固有 inputs/results と repository-external report requirement。common binding algorithm は持たない |
| `skills/sdd-implementation/prompts/repository-researcher.md` | Modify in SPV-4 | Research Worker 固有 scope/artifact/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/spec-synthesizer.md` | Modify in SPV-4 | Spec Synthesis 固有 inputs/durable output/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/spec-reviewer.md` | Modify in SPV-4 | Spec Review 固有 lens/raw verdict/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/plan-reviewer.md` | Modify in SPV-4 | Plan Review 固有 lens/readiness routing/return fields。common guard owner を参照する |
| `skills/sdd-implementation/tests/test_preimplementation_context.py` | Modify in SPV-4 | stage resources/prompts が common guard を複製せず task-local inputs を追加すること、KIS canonical path/full-read が exact seven roles にだけ配線されることを固定する contract owner |
| `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` | Modify only if deduplication requires; otherwise preserve and verify in SPV-4 | generic allocation methodology を Superpowers に委譲しつつ、SDD first entry、owner/worktree/path/CWD binding、single writer、one atomic artifact、separate commit plan、zero-write/no-fallback、original-checkout preservation を固定する owner |
| `skills/sdd-implementation/tests/harnesses/fail_closed_scenario.py` and `skills/sdd-implementation/tests/harnesses/__init__.py` | Preserve and include in SPV-2 closure; verify in SPV-4/SPV-5 | origin/main から取り込んだ First-Write Worktree Gate の current deterministic behavioral harness。production runtime ではなく、新 harness system を追加しない |
| `skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py` and `skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py` | Preserve and include in SPV-2 closure; verify in SPV-4/SPV-5 | direct supporting-skill entry、allocation/binding/path/owner/preservation failure、atomic publish、original-checkout commit attempt の zero-write/no-fallback behavior owner |
| `skills/sdd-implementation/tests/fixtures/unsafe_downstream.py` | Preserve and include in SPV-2 closure; verify in SPV-4/SPV-5 | unsafe downstream mutation が gate を迂回できないことを観測する current test-only fixture。追加 fixture system は作らない |
| `knowledge/wiki/syntheses/sdd-portable-validation-simplification.md` | Modify in SPV-5 | landed behavior、acceptance evidence、remaining risk、local completion state を approved scope を変えずに記録する current spec owner |
| `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` | Modify in SPV-5 | broader SDD design の current ownership seam と supersession relation を更新する owner |
| `knowledge/wiki/syntheses/sdd-portable-validation-simplification-implementation-plan.md` | Modify in SPV-5 | task/review/integration/verification の durable closeout summary。raw report/transcriptは格納しない |
| `knowledge/index.md` | Modify in SPV-5 | current spec/plan/design の active canonical discoverability owner |
| `knowledge/log.md` | Modify in SPV-5 | reviewed plan と implementation closeout の append-only lifecycle evidence owner |

## Historical SPV-1〜SPV-5 Requirement And Acceptance Inventory

### Requirements

- R-01: installed skill folder と required package resources だけで explicit target repository に対する SDD validation を完結する。
- R-02: canonical absolute explicit target と同一の `git -C TARGET` binding を使う direct Git contract を public `SKILL.md` に一度だけ定義し、standalone/bundled validator を追加しない。
- R-03: package resource 欠落を `broken skill installation`、target/Git/capability failure を target/runtime-side failure として mutation 前に区別する。
- R-04: portable public contract、prompts、references、tests、fixtures から repository 固有 hash/path/marker/canonical plan/個人 path を除去する。
- R-05: root validator/regression は current index、nominated candidate tree、repository policy boundary 以後の reachable new commits、final tree の strict-zero contract を所有し、policy-root identity/actual parent、canonical-plan parity、`--post-policy-history` CI invocation を repository-only surface に保持する。
- R-06: mechanical validation point を三 gate に限定し、各 gate の inputs、Git surface、pass/block boundary、state invalidation、re-run freshness を一意にする。
- R-07: mandatory resource の存在/readability/skill-relative resolution と package 外参照/source topology dependency の不在を isolated closure test で固定する。
- R-08: generic lifecycle/worktree/TDD/review/finishing を Superpowers owner に戻し、SDD を薄い repository-independent composition にする。
- R-09: target/CWD/write binding、external handoff、fresh dispatch/result collection、Git operations 等の required capability と pre-mutation stop を contract test で固定する。
- R-10: parallel eligibility を agent/repository-owned、unknown dependency/conflict を sequential fallback、Human authority を material Written Spec change/remote action に限定する。
- R-11: installed-folder と synthetic Git repository の positive/negative forward tests を source checkout 非依存で実行する。
- R-12: source package tests、isolated install tests、root validators/regressions、CI contract、architecture/skill validators、diff hygiene、final Git gate を fresh combined verification で成功させる。
- R-13: diff を既存 owner と最小 test/fixture surface に限定し、新しい adapter/scheduler/state/telemetry/protocol を追加せず durable knowledge を close out する。
- R-14: current SDD First-Write Worktree Gate の repository-change entry、task-owner/worktree/path/CWD binding、single-writer containment、exactly one artifact atomic write、separate commit plan、zero-write/no-fallback、original-checkout preservation を generic lifecycle proseの重複整理後も削除・緩和しない。
- R-15: `keep-implementation-simple` dependency preflight と、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewer の exact seven-role canonical-path/full-read wiring を保持し、affected work 前の bounded failure を固定する。

### Acceptance criteria

- AC-01: isolated install が source repository access なしで resource resolution、direct Git validation、package tests を完了する。
- AC-02: portable package に generic validator executable がなく、public contract が explicit canonical target と同一 Git binding だけを使う。
- AC-03: missing resource と Git capability failure が別 owner/failure category として mutation 前に観測できる。
- AC-04: portable files/fixtures に repository 固有 hash/path/marker/canonical plan/個人 absolute path がない。
- AC-05: current root validator/regression/CI が index、candidate、post-policy new commit、final tree を strict-zero で検査し、marker や過去の exact lineage を current authority にせず、policy-root identity/actual parent と canonical-plan parity を root-only に保つ。workflow は `--post-policy-history` を fresh 実行し、clean clone と `origin/main` 不在でも動作する。
- AC-06: 三 gate だけが normative で、mandatory input、positive/negative state、mutation invalidation、re-run が isolated test で観測できる。
- AC-07: closure test が mandatory resource 欠落、package 外参照、source topology dependency を検出する。
- AC-08: SDD public contract が Superpowers 所有の generic methodology を再定義しない。
- AC-09: required capabilities と unavailable 時の pre-mutation stop が contract test で固定される。
- AC-10: parallel eligibility、sequential fallback、Human authority boundary が contract test で固定される。
- AC-11: all relevant source、isolated-copy、repository validator、CI contract checks が fresh に成功する。
- AC-12: implementation diff が既存 owner/minimum surface に限定され、禁止された新規 mechanism がない。
- AC-13: current fail-closed scenario tests が direct supporting-skill entry、allocation/binding/path/owner/preservation failure、original-checkout commit attempt を mutation 前に block し、exactly one new artifact と別 commit plan だけを許可する。
- AC-14: KIS dependency preflight と exact seven-role wiring が current tree と一致し、各 role の full-read failure が affected work 前に bounded failure となり、SPV-4 がこの wiring または First-Write Worktree Gate を弱めない。

## Historical SPV-1〜SPV-5 Coverage Matrix

| ID | Primary task | Contributing tasks |
| --- | --- | --- |
| R-01 | SPV-2 | SPV-1, SPV-5 |
| R-02 | SPV-1 | SPV-2, SPV-4 |
| R-03 | SPV-1 | SPV-2 |
| R-04 | SPV-2 | SPV-1, SPV-4 |
| R-05 | SPV-3 | SPV-2, SPV-5 |
| R-06 | SPV-1 | SPV-2 |
| R-07 | SPV-2 | SPV-5 |
| R-08 | SPV-4 | SPV-1 |
| R-09 | SPV-4 | SPV-1, SPV-2 |
| R-10 | SPV-4 | SPV-5 |
| R-11 | SPV-2 | SPV-1, SPV-5 |
| R-12 | SPV-5 | SPV-1, SPV-2, SPV-3, SPV-4 |
| R-13 | SPV-4 | SPV-1, SPV-2, SPV-3, SPV-5 |
| R-14 | SPV-4 | SPV-2, SPV-5 |
| R-15 | SPV-4 | SPV-2, SPV-5 |
| AC-01 | SPV-2 | SPV-1, SPV-5 |
| AC-02 | SPV-1 | SPV-2, SPV-4 |
| AC-03 | SPV-1 | SPV-2 |
| AC-04 | SPV-2 | SPV-1, SPV-4 |
| AC-05 | SPV-3 | SPV-2, SPV-5 |
| AC-06 | SPV-1 | SPV-2 |
| AC-07 | SPV-2 | SPV-5 |
| AC-08 | SPV-4 | SPV-1 |
| AC-09 | SPV-4 | SPV-1, SPV-2 |
| AC-10 | SPV-4 | SPV-5 |
| AC-11 | SPV-5 | SPV-1, SPV-2, SPV-3, SPV-4 |
| AC-12 | SPV-4 | SPV-1, SPV-2, SPV-3, SPV-5 |
| AC-13 | SPV-4 | SPV-2, SPV-5 |
| AC-14 | SPV-4 | SPV-2, SPV-5 |

## Historical SPV-1〜SPV-5 Tasks

### Task 1: SPV-1 — Explicit target と三つの direct Git gate

- [x] **Implementation status:** implemented in `9a4e155`; independent task review found one test-evidence defect, fixed in `481d424`; focused rereview was clean after that single fix round. Both commits are reachable from current baseline `0ed5f358979ae9281fb7dde8fe47647175720ca8`.
- [x] **Deliverable:** public `SKILL.md` が explicit target identity と三つの normative gate を一度だけ所有し、synthetic Git forward tests が各 gate の observable behavior と fail-closed boundary を固定する。
- [x] **Requirement coverage:** R-02, R-03, R-06。
- [x] **Acceptance coverage:** AC-02, AC-03, AC-06。
- [x] **Dependencies:** なし。
- [x] **Files:** modified `skills/sdd-implementation/SKILL.md`, `skills/sdd-implementation/tests/test_skill_contract.py`, `skills/sdd-implementation/tests/test_transient_artifact_contract.py`; created `skills/sdd-implementation/tests/test_portable_git_gates.py`。
- [x] **Behavioral interface — Consumes:** caller-supplied canonical absolute target、installed skill directory、target-relative scratch path/non-empty exceptional reason、trusted immutable `starting_head_sha`、current index/HEAD/ignore/working-tree state。
- [x] **Behavioral interface — Produces:** `exceptional-local-scratch-pre-write` の ignored/untracked/uncommitted leaf verdict、`pre-commit-candidate` の candidate/index cleanliness verdict、`final-closeout` の candidate/HEAD/全 `BASELINE..HEAD` commit-tree verdict、および skill/package・target/runtime・gate-specific failure classification。
- [x] **Behavioral interface — Invariants:** target identity は `rev-parse` の top-level/inside-work-tree 結果で完全一致を確認し、全 probe は同じ canonical target binding を使用する。scratch gate は normalize/symlink ownership、`check-ignore --no-index`、index/HEAD absenceを判定し、target/path/ownership/ignore/HEAD/index mutationで失効する。pre-commit gate は `write-tree` candidate、candidate/index/unignored working pathを判定し、index/working-tree/ignore mutationで失効する。final gate はcandidate、`HEAD^{tree}`、baseline commit/ancestry、object graphからfreshに導出した全 `BASELINE..HEAD` commit treeを判定し、HEAD/index/working-tree/ignore/baseline binding mutationで失効する。exactly-once/cache/state は作らない。
- [x] **RED evidence:** public contract の root validator invocation、repository-specific migration prose、曖昧な全-stage gate を拒否する contract assertions と、ignored scratch/force-add/unmerged index/staged deletion/add-then-delete/stale evidence を区別する synthetic cases が intended pre-implementation failures を観測した。
- [x] **GREEN evidence:** `SKILL.md` の repository validation section を approved normative table と explicit target/failure behavior に最小置換し、test helper を synthetic repository の観測専用に留め、installed package が呼ぶ validator module/executable を追加しなかった。
- [x] **Focused verification:** gate forward tests と existing skill/transient contract tests は positive/negative/invalidation cases を含めて GREEN。review finding は `481d424` の後の one scoped rereview で clean となった。
- [x] **Integration placement:** I-1。Task 1 public interface と fix は current baseline へ到達済みで、後続 task はこれを consume し、closure/ownership/deduplication を追加検証する。
- [x] **Failure owner:** SPV-1 implementer が one review finding を修復し、independent task reviewer が spec table との一致と bundled validator 不在を clean と判定した。
- [x] **Commit boundary:** implementation commit `9a4e155` と one scoped review-fix commit `481d424`。

### Task 2: SPV-2 — Isolated installed-folder closure と portable fixture

- [x] **Implementation status:** implemented in `f1f5d96`; independent task review findings were fixed in `42ce4df`; scoped rereview was clean. Root canonical parity became GREEN before package dependency removal, and both commits are reachable from the current branch.
- [x] **Deliverable:** package dependency removal前に root-owned canonical parity fixture/regression を作成して GREEN にし、その replacement coverage を保持したまま skill folder の isolated copy が source repository/parent を read path に持たず package tests と direct Git validation を完結し、package resources/fixture/plan validator から root canonical dependency と個人/repository identity が消える。この順序全体を一つの commit/review boundaryで扱う。
- [x] **Requirement coverage:** R-01, R-04, R-07, R-11。
- [x] **Acceptance coverage:** AC-01, AC-04, AC-07。
- [x] **Dependencies:** SPV-1 reviewed and integrated。
- [x] **Contributing coverage:** R-05, AC-05 の canonical parity replacement surfaceを package-side removal前に root ownerへ確立する。R-05 / AC-05 の primary owner は SPV-3 のままとする。
- [x] **Files:** create `scripts/fixtures/sdd-plan-contract/ready-plan.md`, `scripts/test_sdd_canonical_plan_parity.py`, `skills/sdd-implementation/tests/test_isolated_install.py`; modify `skills/sdd-implementation/tests/test_plan_contract.py`, `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md`, `skills/sdd-implementation/references/plan-contract.md`; include current `SKILL.md`, prompts, references, tests, existing fixtures, and existing harnesses in closure discovery without planning content changes to those resources in this task。
- [x] **Behavioral interface — Consumes:** copied installed skill directory、mandatory resource inventory derived from the current public contract and actual package tree without a new manifest executable、source/parent outside the allowed read closure、one synthetic explicit target。
- [x] **Behavioral interface — Produces:** root canonical parity replacement の GREEN verdict、isolated package test result、mandatory resource closure verdict、package-outside reference/leakage verdict、`broken skill installation` versus target/runtime failure evidence、portable representative plan semantic result。
- [x] **Behavioral interface — Invariants:** root-owned parity fixture/regression が current canonical coverageを引き継いで GREEN になるまで package test の canonical-plan dependencyを除去しない。replacement GREEN後の package removal、portable fixture transition、isolated closure GREENまでを同じ reviewed task commitに含め、coverageのない intermediate integration stateを作らない。installed copy は original checkout path、parent topology、root canonical plan、root scripts を利用しない。package fixture は semantic plan contract の representative であり repository canonical parity の source ではない。
- [x] **RED intent:** 最初に root-owned fixture/regression が absentまたはcanonical inventory/coverage/graph/orderと不一致なら失敗する replacement expectationを置き、existing package canonical parity coverageを残した状態で intended REDを観測する。root replacementをGREENにした後にだけ、existing package test の canonical plan read、source-relative topology dependency、missing mandatory resource、outside-package reference、forbidden repository identity を個別 failure として観測する isolated-copy expectationsへ進む。
- [x] **GREEN intent:** root-owned fixture/regressionを先に current canonical plan parityへ一致させてGREENにする。そのGREENを保持したまま package plan validator を package-relative semantic validation に限定し、representative fixture を portable identity に置換し、overlay の parity statement を package fixture validation と reviewed root-owned canonical parity に分離する。最後にisolated closureをGREENにする。origin/main で追加された prompts/references/First-Write tests/harnesses/fixture は actual package closure として検査するだけとし、新しい manifest executable、loader、validator、adapter、fixture system を追加しない。
- [x] **Focused verification:** package dependency removal前に root canonical parity regressionがGREENであることを確認し、removal後もそのroot parityとpackage semantic suiteをGREENに保つ。続いて isolated copy で package test discovery と synthetic target cases が成功し、mandatory resource を一件欠かした copy と package 外参照を混入した copy がそれぞれ intended category で失敗する。
- [x] **Integration placement:** I-2。SPV-1 public interface を consumeし、root-owned parity replacement GREEN、package-side canonical dependency removal、isolated closure GREENをこの順で一つの atomic cutoverとして統合する。replacementだけまたはremovalだけのpartial stateはintegration-readyとしない。
- [x] **Failure owner:** SPV-2 implementer が root parity replacement、closure harness/resource identity、fixture portability defectを修復し、独立 task reviewerが replacement GREENがremovalに先行すること、canonical parity coverage、hidden source dependencyとstandalone validatorの不在を判定する。
- [x] **Commit boundary:** root parity fixture/regression、isolated closure test、portable fixture/validator、overlay owner separationを一つの reviewed task commitに含める。root replacement GREEN前の package dependency removal、または片側だけのcommit/reviewは許可しない。

### Task 3: SPV-3 — Repository-owned strict-zero/canonical parity と CI

- [x] **Implementation status:** implemented in `07a1e8d`; independent task review was clean. The commit is reachable and preserves the reviewed SPV-2 parity owner while adding only CI/invocation wiring.
- [x] **Deliverable:** SPV-2で作成・review済みの root canonical parity fixture/regressionをconsumeして再検証し、current root validator/regression の strict-zero index/candidate/post-policy-history/final-tree authority を保持し、CI とその contract test が `--post-policy-history`、root regression/parity、isolated closure、package tests を fresh に呼ぶ。root parity surfaceはこのtaskで再作成しない。
- [x] **Requirement coverage:** R-05。
- [x] **Acceptance coverage:** AC-05。
- [x] **Dependencies:** SPV-2 reviewed and integrated。
- [x] **Files:** modify `.github/workflows/skill-architecture.yml`, `scripts/test_skill_ci_workflow.py`; consume and preserve `scripts/fixtures/sdd-plan-contract/ready-plan.md`, `scripts/test_sdd_canonical_plan_parity.py`; preserve and verify `scripts/validate_sdd_transient_artifacts.py`, `scripts/test_validate_sdd_transient_artifacts.py`。
- [x] **Behavioral interface — Consumes:** SPV-2 reviewed commitに含まれるGREENのroot canonical parity fixture/regression、root canonical SDD plan、explicit repository root、current index、nominated candidate tree、full reachable Git history、repository-only policy-root identity and actual-parent relationship、final tree、CI workflow text。
- [x] **Behavioral interface — Produces:** root canonical parity verdict、strict-zero index/candidate/post-policy-new-commit/final-tree verdict、one exact diagnostic category on rejection、CI invocation-set verdict、clean-clone/no-`origin/main` behavior、isolated closure/package suite invocation evidence。
- [x] **Behavioral interface — Invariants:** package tests は root fixture/canonical page、policy-root identity、actual parent、root validator を読まない。completed marker と pre-amendment exact path/mode/blob/lineage は historical evidence であり current executable authority ではない。root validator は current strict-zero surfaces だけを検査し、staged deletion と pre-policy historical ancestor blob を current violation としない。CI path は reachable clean clone から実行でき、`origin/main` ref を必須にしない。
- [x] **RED intent:** SPV-2 reviewed root parity regression、current root strict-zero regression、`--post-policy-history` workflow behaviorをpre-change GREEN preservation baselineとし、CI contract に canonical parity regression と isolated closure invocation の欠落だけを失敗させる expectations を先に追加する。root fixture/regressionの欠落をこのtaskのintended REDにせず、current validator、clean-clone/no-`origin/main`、shallow-history rejection、add-then-delete rejection の回帰は受理しない。
- [x] **GREEN intent:** reviewed root parity regressionとisolated closureのCI invocation、および対応するworkflow contract expectationだけを追加する。SPV-2のroot fixture/regressionを再作成・再移管せず、origin/main から landed した current root validator/regression と `--post-policy-history` workflow behavior は preserve-and-verify とし、marker/lineage authority へ戻さない。
- [x] **Focused verification:** root canonical parity、strict-zero root regression、root validator の current-tree invocation、CI workflow contract、isolated closure/package suite invocation が成功する。workflow contract は full reachable clone、`origin/main` ref 不在、post-policy add-then-delete、shallow history をそれぞれ期待通り判定する。
- [x] **Integration placement:** I-3。SPV-2のatomic cutoverで既に成立した package/root owner separationをconsumeし、reviewed root parityとisolated closureをcurrent strict-zero checksとともにCIへ接続する。
- [x] **Failure owner:** SPV-3 implementer が current strict-zero preservationまたはCI/invocation wiring defectを修復する。SPV-2 reviewed root fixture/regression自体のdefectはcontributing owner SPV-2へ戻す。independent task reviewer は current strict-zero authority、root-only policy identities、canonical parity、clean-clone/no-`origin/main` coverage の削除・optional化・quick-check化がないことを判定する。
- [x] **Commit boundary:** parity/isolated CI invocationとCI contract expectationだけを一つの reviewed task commitに含める。SPV-2 reviewed root parity fixture/regressionとcurrent root validator/regressionのpreserve-only surfaceは差分に含めない。

### Task 4: SPV-4 — Superpowers ownership deduplication と authority A

- [x] **Implementation status:** implemented in `84e3940`; independent task review findings were fixed in `f29c0fd`; scoped rereview was clean. Both commits are reachable and retain First-Write fail-closed behavior plus exact seven-role KIS wiring.
- [x] **Deliverable:** SDD entrypoint を thin composition にし、common runtime capability/path guard を一箇所に集約し、stage references/prompts は owner reference と worker-specific inputs/results だけを保持する。Authority A、parallel eligibility、sequential fallback に加え、current SDD First-Write Worktree Gate と exact seven-role KIS full-read wiring を deduplication 後も弱めず contract/behavior tests で固定する。
- [x] **Requirement coverage:** R-08, R-09, R-10, R-13, R-14, R-15。
- [x] **Acceptance coverage:** AC-08, AC-09, AC-10, AC-12, AC-13, AC-14。
- [x] **Dependencies:** SPV-3 reviewed and integrated。
- [x] **Files:** modify `skills/sdd-implementation/SKILL.md`, `skills/sdd-implementation/references/planning-context.md`, `skills/sdd-implementation/references/research-stage.md`, `skills/sdd-implementation/prompts/repository-researcher.md`, `skills/sdd-implementation/prompts/spec-synthesizer.md`, `skills/sdd-implementation/prompts/spec-reviewer.md`, `skills/sdd-implementation/prompts/plan-reviewer.md`, `skills/sdd-implementation/tests/test_skill_contract.py`, `skills/sdd-implementation/tests/test_preimplementation_context.py`, `skills/sdd-implementation/tests/test_transient_artifact_contract.py`; modify `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` only if its assertions must follow a prose-owner move; preserve and verify `skills/sdd-implementation/tests/harnesses/__init__.py`, `skills/sdd-implementation/tests/harnesses/fail_closed_scenario.py`, `skills/sdd-implementation/tests/fixtures/unsafe_downstream.py`, `skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py`, `skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py`。
- [x] **Behavioral interface — Consumes:** selected Superpowers lifecycle contracts、applicable repository instructions、installed resource paths、explicit target/workspace/CWD/write destinations、minted task-owner identity、Git worktree registration、original-checkout fingerprint/preservation evidence、fresh dispatch/result-collection capabilities、resolved canonical KIS path、approved Written Spec and remote-action policy。
- [x] **Behavioral interface — Produces:** thin ordered composition、single common capability guard、worker-specific stage inputs/outputs、four-field pre-mutation blocked diagnosis、preserved First-Write entry/containment/one-artifact publish/separate-commit/zero-write/no-fallback/original-preservation behavior、exact seven-role KIS full-read verdict、agent/repository-owned parallel eligibility or sequential fallback、Human decision/remote-action stop reason。
- [x] **Behavioral interface — Invariants:** SDD は generic worktree allocation algorithm/fallback、TDD loop、review/fix algorithm、branch finishing、model-tier table を再記述しない。一方で SDD repository-change first entry、task-owner/worktree/path/CWD binding、single writer、exactly one absent artifactのatomic publish、separate native Git commit plan、zero-write/no-fallback、original-checkout preservation は削除・optional化・generic fallback化しない。prompts/references は common path rejection/model selection procedureを複製しない。KIS canonical path は preflight で一度 resolve し、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewer のみが affected work 前に全文 read する。material spec change 以外の agent-repairable evidence gap は Human decision にしない。
- [x] **RED intent:** generic lifecycle/path-guard 重複の forbidden ownership leakage と required capability absence/unknown dependency classification を固定すると同時に、origin/main で landed した First-Write positive/fail-closed scenarios と exact seven-role KIS test を pre-change GREEN preservation baseline とする。deduplication 後に entry、containment、zero-write、no-fallback、original preservation、一 artifact/別 commit plan、七 role のいずれかが欠けることを regression として失敗させる。
- [x] **GREEN intent:** public contract に一つの required-capability interface と composition order を残し、stage resources/prompts を task-local差分へ縮める。First-Write Worktree Gate と seven-role KIS wiring は existing owner に保持し、Authority A と unknown→sequential を短い observable contract にする。新しい manifest、validator、adapter、state、telemetry、protocol、cache、harness、fixture system を導入しない。
- [x] **Focused verification:** skill/preimplementation/workspace/transient contract suites が generic ownership leakage、duplicate guard、authority regression、missing capability continuation を拒否する。First-Write contract と fail-closed entry/allocation behavioral suites が direct entry、binding/path/owner/preservation failures、atomic publish、original-checkout commit attempt を current 通り判定し、preimplementation suite が exact seven-role KIS path/full-read/failure boundary を固定する。
- [x] **Integration placement:** I-4。SPV-1 の normative gate interface と SPV-2/3 の owner separationを保持したまま shared prose/tests を最終形へ収束する。
- [x] **Failure owner:** SPV-4 implementer が deduplication/guard/authority/First-Write/KIS compatibility defect を修復し、independent task reviewer が「required SDD behavior の削除・弱体化」と「generic methodology 再実装」の両方を判定する。
- [x] **Commit boundary:** thin composition、common guard、authority/parallel contract、First-Write/KIS preservation に必要な existing owner/test の最小差分だけを一つの reviewed task commit に含める。preserve-only harness/fixture に差分を加えない。

### Task 5: SPV-5 — Knowledge closeout と fresh combined verification

- [x] **Completed deliverable scope:** 全 task commit と review の integration branch reachabilityを確認し、approved spec、current design、reviewed plan、index/logをlanded evidenceへ同期した。portable/root/CI/full repository checks、final direct-Git gate、root strict-zero gateは`41c2a63..458a52e`のcloseout / review-correction cycleでfresh GREENである。
- [x] **Independent whole-branch review:** canonical review at `9f4787f` returned Critical 0 / Important 4 / Minor 0; `e9d1bcb` addressed all four original findings; the Human-approved `3ef7564` KIS binding repair addressed the one new scoped-re-review finding; final scoped re-review returned residual `ADDRESSED`, new Critical 0 / Important 0.
- [x] **Final status transition:** final scoped re-review found the branch ready, and the Human-approved dependent transition records `LOCAL_COMPLETE`.
- [x] **Requirement coverage:** R-12。closeout / verification / final-gate / final-review evidenceはlanded済みである。
- [x] **Acceptance coverage:** AC-11。knowledge synchronization、fresh combined verification、commit、post-commit gate、final review / bounded fix / scoped re-reviewは成功済みである。
- [x] **Dependencies:** SPV-4 reviewed and integrated。`f29c0fd`はTask 5 closeout/review chain `41c2a63..3ef7564`のancestorとしてreachableである。
- [x] **Files:** `knowledge/wiki/syntheses/sdd-portable-validation-simplification.md`, `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`, this implementation plan, `knowledge/index.md`, `knowledge/log.md`のみにcloseoutを同期した。Source/test filesは変更していない。
- [x] **Behavioral interface — Consumes:** reviewed task commits、task review verdicts、current integration branch Git facts、approved spec identity、all acceptance mappings、package/root/CI validation surfacesをcloseout evidenceとして消費した。
- [x] **Behavioral interface — Produces:** acceptance-by-acceptance result、remaining risk、unperformed remote action、canonical discoverability、append-only log event、knowledge closeout / gate evidence、final review verdict、`LOCAL_COMPLETE`を生成した。
- [x] **Behavioral interface — Invariants:** raw worker/review/test transcripts と runtime path は wiki に複製していない。approved scope/authority は変更せず、ignored untracked local scratchをdestructive cleanupしていない。remote authorization absenceはlocal verificationと分離した。
- [x] **RED intent:** closeout前に complete R-01〜R-15 / AC-01〜AC-14 coverage、required task commit reachability、current root strict-zero/post-policy-history/parity、isolated closure、First-Write fail-closed behavior、exact seven-role KIS wiring、knowledge index/log effect、final gate evidence の欠落を checklist failure として列挙した。source behaviorの欠落はなかった。
- [x] **GREEN intent:** landed behaviorとfresh evidence identitiesだけをdurable surfacesへ反映し、全verification surfaceをfreshに実行した。final review、one bounded final-fix wave、Human-approved one bounded KIS binding repair、scoped re-reviewsを完了した。
- [x] **Focused verification:** package source suite 143/143、root scripts 39/39、llm-wiki 22/22、root canonical parity 4/4、repository architecture validator、one context contract / warning-free context report、`sdd-implementation` Skill validatorはstatus transition前のfresh runで成功した。isolated installed-copy / synthetic gate / First-Write / exact-seven KIS、current strict-zero / `--post-policy-history` / clean-clone / no-`origin/main`は当該suiteに含まれる。
- [x] **Integration placement:** I-5。closeout / review-correction commits `41c2a63..9f4787f`、bounded final fix `e9d1bcb`、Human-approved KIS binding repair `3ef7564`、各required gate / reviewを完了した。
- [x] **Failure owner:** behavior/test failure は coverage matrix の primary task owner、root strict-zero/parity/CI failure は SPV-3、thin contract/authority/First-Write/KIS failure は SPV-4、knowledge/index/log failure は SPV-5、baseline/commit-range/final gate failure は integration ownerとする分類を保持した。
- [x] **Commit boundary:** initial canonical closeout / index-log sync / fresh verification identityは`41c2a63`、review-driven knowledge correctionsは`458a52e..9f4787f`、four final-review fixesは`e9d1bcb`、Human-approved KIS binding repairは`3ef7564`に分離した。本dependent status transitionは五つのapproved SDD knowledge filesだけのatomic closeout commitとする。

## Historical SPV-1〜SPV-5 Dependency Graph

| Task | Dependencies | Reason |
| --- | --- | --- |
| SPV-1 | none | normative public Git gate interface は `9a4e155` + `481d424` で implemented/reviewed/integrated 済み |
| SPV-2 | SPV-1 | 確定した public gate interfaceをisolation対象にし、root parity replacement GREENからpackage dependency removal/isolated closure GREENまでをatomic cutoverする |
| SPV-3 | SPV-2 | SPV-2 reviewed root parity/isolated closure surfacesをconsumeし、current root strict-zero checksとともにCIへ接続する |
| SPV-4 | SPV-3 | shared `SKILL.md`/tests を最終形へ収束し、owner cutover後のcontractをdeduplicateする |
| SPV-5 | SPV-4 | 全 reviewed implementation とserialized integration後にcloseout/combined verificationを行う |

Cycle check: chain は `SPV-1 -> SPV-2 -> SPV-3 -> SPV-4 -> SPV-5` の単方向であり、undefined dependency と cycle はない。

## Historical SPV-1〜SPV-5 Execution Order

1. SPV-1 complete: direct Git gate contract と synthetic forward tests を `9a4e155` で実装し、one review fix `481d424` 後の scoped rereview は clean。
2. SPV-2 complete: root-owned parity replacementを先にGREENにし、その後にpackage dependency removal / portable fixture transitionを行い、root parityとisolated package closureを同じreviewed boundaryでGREENにした。
3. SPV-3 complete: reviewed root parity / isolated closureをcurrent strict-zero / post-policy-history / clean-clone / no-`origin/main` ownerとともにCIへ接続し、independent reviewを完了した。
4. SPV-4 complete: generic prose / common guard / authorityをdeduplicateし、First-Write Worktree Gateとexact seven-role KIS wiringを保持した上でscoped re-reviewを完了した。
5. SPV-5 complete: durable closeout、fresh combined verification、knowledge commits、post-commit final direct-Git/root strict-zero gates、canonical whole-branch review、bounded final fix、Human-approved KIS binding repair、scoped re-reviews、dependent `LOCAL_COMPLETE` transitionを完了した。

全 task は shared owners と migration cutover orderを持つため sequential execution とする。task内でも一つの public seam、一つの failing behavior、一つの最小修正を順に進め、同一 issue 内の concurrent implementer は使用しない。

## Historical SPV-1〜SPV-5 Serialized Integration

| Step | Task | Status / reviewed evidence | Landed combined state |
| --- | --- | --- | --- |
| I-1 | SPV-1 | **completed** — `9a4e155..481d424` reachable; scoped rereview clean | public contract owns the explicit target and three direct-Git gates; synthetic suite GREEN and current root checks preserved |
| I-2 | SPV-2 | **completed** — `f1f5d96..42ce4df` reachable; scoped rereview clean | root canonical parity became GREEN before package dependency removal; portable fixture, package semantics, and isolated closure remained GREEN in the reviewed atomic cutover |
| I-3 | SPV-3 | **completed** — `07a1e8d` reachable; independent review clean | reviewed root parity and isolated closure run in CI with current strict-zero / `--post-policy-history` / clean-clone / no-`origin/main` behavior preserved |
| I-4 | SPV-4 | **completed** — `84e3940..f29c0fd` reachable; scoped rereview clean | thin composition, one common guard, Authority A, unknown-to-sequential, First-Write preservation, and exact-seven KIS wiring landed |
| I-5 | SPV-5 | **completed** — `41c2a63..3ef7564` reachable; canonical whole-branch review, `e9d1bcb` final fix, Human-approved `3ef7564` KIS binding repair, and scoped re-reviews completed | canonical knowledge/index/log are synchronized; residual finding `ADDRESSED`, new Critical 0 / Important 0, local disposition `LOCAL_COMPLETE` |

Integration owner は各 step 前に actual commit range、changed paths、semantic/resource assumptions、required task commit reachability を Git facts から再導出する。partial integration、unreviewed result、unknown ancestry、non-descendant target rewrite は integration-ready としない。textual clean merge だけでは成功としない。

## Historical SPV-1〜SPV-5 Post-Integration Combined Verification

### Scope

- `skills/sdd-implementation/` の public contract、全 prompts/references、package tests/fixtures。
- root canonical parity fixture/regression、current strict-zero index/candidate/post-policy-history/final-tree validator/regression、CI workflow/invocation contract。
- current First-Write Worktree Gate contract/behavior harnesses と exact seven-role KIS wiring。
- approved spec、current design、reviewed implementation plan、`knowledge/index.md`、`knowledge/log.md`。
- rebound baseline `0ed5f358979ae9281fb7dde8fe47647175720ca8` から integration branch までの全 commit tree、current HEAD/index/working-tree/ignore state、original checkout starting fingerprint。

### Pass criteria

1. AC-01〜AC-14 の各 primary owner evidence が一件ずつあり、contributing evidence と矛盾しない。
2. SPV-2 evidenceがroot-owned canonical parity replacementのGREENをpackage dependency removalより先に示し、そのremoval後もroot parityとpackage semantic testsがGREENである。package source tests と isolated installed-copy tests が成功し、isolated copy は source checkout/parent/root scriptsを読まない。
3. synthetic Git tests が ignored scratch、force-add、unmerged index、staged deletion、add-then-delete、baseline non-ancestor、state mutationによるevidence失効とre-runを期待通り判定する。
4. root canonical parity、root strict-zero regression、root validator、CI invocation contract が成功する。workflow は `--post-policy-history` を含み、full reachable clean clone と `origin/main` ref 不在で成功、post-policy add-then-delete と shallow history で fail closed となる。marker/legacy exact lineage は current authority に戻らない。
5. First-Write contract/entry/allocation suites が repository-change entry、owner/worktree/path/CWD binding、single writer、one atomic artifact、separate commit plan、zero-write/no-fallback、original-checkout preservation を成功させ、exact seven-role KIS test が同じ canonical path/full-read と affected-work-before failure を固定する。
6. repository architecture validator、skill-creator validator、knowledge lint、diff whitespace check が成功する。
7. final `final-closeout` gate が current candidate、HEAD tree、immutable rebound `starting_head_sha..HEAD` の全 commit treeで `.superpowers/**` entry zero を確認する。ignored/untracked/unstaged/uncommitted scratch は failure にしない。original checkout は captured starting branch/HEAD/status を保持する。
8. final whole-branch review が approved amended spec fit、material simplicity、current material risk、knowledge consistencyを ready とし、禁止された portable manifest executable、standalone/bundled validator、adapter、state、telemetry、protocol、cache、new fixture/harness system が存在しない。existing root validator は preserve-only authority として残る。

### Required evidence

- focused task RED/GREEN result と independent task review verdict。SPV-2はroot parity replacement GREEN、続くpackage dependency removal、final root parity/package semantic/isolated closure GREENが同じcommit/review boundaryにある順序 evidenceを含む。
- task commit IDs と integration branch reachability。
- isolated-copy root identity/read-closure evidence と synthetic target case summary。
- root strict-zero validator/regression/parity、`--post-policy-history` CI contract、clean-clone/no-`origin/main` の fresh result summary。
- First-Write entry/containment/zero-write/no-fallback/original-preservation と exact seven-role KIS full-read の fresh result summary。
- architecture/skill/knowledge/diff checks の fresh result summary。
- final direct Git gate と whole-branch review の durable verdict summary。

### Implementation closeout evidence — `LOCAL_COMPLETE`

| Coverage | Landed / fresh result |
| --- | --- |
| R-01, R-04, R-07, R-11 / AC-01, AC-04, AC-07 | reviewed SPV-2 tip `42ce4df`; root parity-first atomic cutover、portable package identity、source-independent installed-folder and synthetic-repository forward tests、isolated closure |
| R-02, R-03, R-06 / AC-02, AC-03, AC-06 | reviewed SPV-1 tip `481d424`; explicit canonical target、three direct-Git gates、synthetic state / invalidation / taxonomy cases |
| R-05 / AC-05 | reviewed SPV-3 tip `07a1e8d`; root-only parity and strict-zero ownership、`--post-policy-history`、clean-clone / no-`origin/main`、add-then-delete / shallow-history behavior |
| R-08, R-09, R-10, R-13, R-14, R-15 / AC-08, AC-09, AC-10, AC-12, AC-13, AC-14 | reviewed SPV-4 tip `f29c0fd`; thin composition、one common guard、Authority A、unknown-to-sequential、First-Write fail-closed containment、exact seven-role KIS |
| R-12 / AC-11 | `41c2a63..3ef7564` reachable; fresh package 143、root scripts 39、llm-wiki 22、canonical parity 4 tests; architecture / context / warning-free context report / Skill validators GREEN; knowledge/diff/candidate/final gates completed; `9f4787f` whole-branch review findings addressed by `e9d1bcb` and Human-approved `3ef7564`; final scoped re-review residual `ADDRESSED`, new Critical 0 / Important 0 |

Task 1〜4のreviewed implementation、Task 5のcloseout、fresh checks、canonical
whole-branch review、bounded fixes、scoped re-reviewsは完了した。residual findingは
`ADDRESSED`、new Critical 0 / Important 0で、新規material riskはない。よって
local dispositionは`LOCAL_COMPLETE`である。push、PR、remote merge、release、live
installは未実施かつ未承認である。

### Failure owners by acceptance criterion

| Acceptance | Failure owner |
| --- | --- |
| AC-01 | SPV-2 |
| AC-02 | SPV-1 |
| AC-03 | SPV-1 |
| AC-04 | SPV-2 |
| AC-05 | SPV-3; SPV-2 atomic root parity replacement defect returns to SPV-2 as contributing owner |
| AC-06 | SPV-1 |
| AC-07 | SPV-2 |
| AC-08 | SPV-4 |
| AC-09 | SPV-4 |
| AC-10 | SPV-4 |
| AC-11 | SPV-5; underlying behavior failure returns to its primary task owner |
| AC-12 | SPV-4; forbidden surface introduced by another task returns to that task owner |
| AC-13 | SPV-4 |
| AC-14 | SPV-4 |

## Historical SPV-1〜SPV-5 Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed
- Repository-ready disposition: SPV-1〜SPV-5 reviewed, fixed, re-reviewed, and integrated; local disposition is `LOCAL_COMPLETE`.
- Controller transition: dependent local-completion status transition complete. Any remote publication, merge, release, or live installation remains a separate explicitly authorized action.
- Material decision request: none
- Material risk: none
- Remote publication state: not authorized and not required for local readiness

## Current Fixture-Minimization Amendment

SPV-1〜SPV-5 の完了記録は上記の歴史的証跡として保持する。以下だけが、`human-directed-fixture-minimization-amendment-20260815` に対する実行前のcurrent planである。実装は pending であり、SPV-5 の `LOCAL_COMPLETE` を本追補の完了根拠にしてはならない。

## Global Constraints

- Human-approved Written Spec の追補だけを実装し、root fixture、新規 runner、new entrypoint、validator、adapter、manifest、loader、state、cache、protocol は追加しない。
- `scripts/fixtures/sdd-plan-contract/ready-plan.md` と `scripts/test_sdd_canonical_plan_parity.py` は削除する。package-relative representative fixture、single semantic parser、isolated package suite、root strict-zero ownerは保存する。
- canonical durable planは既存root CI contract test `scripts/test_skill_ci_workflow.py`が直接読み、approval path、current bytes digest、accepted-or-approved status、approved review state、North Star anchor、baseline ancestryと三negative mutationを検証する。semantic inventory、coverage、task、dependency graph、execution order、serialized integrationはexisting package parser一つだけを直接利用する。
- execution-time runtime inventoryはnormal direct-Git gateで必要なprompt/referenceだけとする。test、harness、fixtureはisolated release/CI copy-setに残してよいが、その欠落だけを`broken skill installation`にしてはならない。
- portable direct Git三gate、root strict-zero post-policy behavior、First-Write Worktree Gate、exact seven-role KIS wiring、Human authority、remote-action boundaryを削除、optional化、または弱体化しない。
- ordinary mergeのblocked evidenceはcanonical planning documentsだけのadded-in-both conflictに限る。content edit前にintegration ownerはplanning/spec commit `8b433806af6835bbf859bea7a7e30a0752d6d294`、pre-amendment feature tip `e5b6b77e790d8d89952b84cfbb04886546e8e8e5`、current main `5e68f5c466b7efcd6e8b3ebb1daf1e6f76682684`、shared tree `8f995222eef73ab5d56a9fb227f367bf8b44c634`、merge base `15152126fe0785bcf789a9ecbfe752b9e368fc4e`、target branch、original checkout fingerprint、non-planning content divergence不在を再検証する。全条件が一致する時だけ、feature branch treeを保つGit `ours` strategyのnon-force no-ff mergeを作りcurrent mainをsecond parentにする。`.gitattributes`、merge driver、manual conflict resolution、rebase、rewrite、force、generic fallbackは使わない。merge後に両parent/lineageのreachabilityとmerge treeがpre-merge feature treeに等しいことを確認するまでTask 6 content editへ進まない。
- raw review、test transcript、temporary report、runtime pathはdurable planへ複製しない。remote writeは本追補のlocal readinessに含めない。

## File Responsibility Map

| Path | Operation | Exact responsibility |
| --- | --- | --- |
| `scripts/fixtures/sdd-plan-contract/ready-plan.md` | Delete | canonical durable planのtest-only copied snapshotを除去する。後継fixtureを作らない。 |
| `scripts/test_sdd_canonical_plan_parity.py` | Delete | copied snapshot comparisonとroot-specific checkの重複ownerを除去する。後継runnerを作らない。 |
| `scripts/test_skill_ci_workflow.py` | Modify | existing root CI contract ownerとしてcanonical planをdirect readし、repository-bound identity、three negative mutations、removed path/entrypointの不在、single semantic parserのdirect resultを固定する。 |
| `.github/workflows/skill-architecture.yml` | Modify | deleted parity runner stepを除き、existing CI contract、root strict-zero regression/validation、isolated closure、package suiteを維持する。 |
| `skills/sdd-implementation/tests/test_plan_contract.py` | Modify | package-relative fixtureのsemantic suiteを維持しつつ、root callerがcanonical plan textへ適用できるsingle semantic parserを所有する。root pathを定数、inventory、read dependencyとして持たない。 |
| `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md` | Preserve | portable representative semantic fixtureとしてpackage suiteだけが読む。root canonical snapshotまたはruntime resourceにしない。 |
| `skills/sdd-implementation/references/plan-contract.md` | Modify | package fixture、root direct check、single parser、fixture default-denyのowner boundaryをcurrent approved specへ整合する。 |
| `skills/sdd-implementation/tests/test_portable_git_gates.py` | Modify | normal direct-Git gateのexecution-time resource inventoryと`broken skill installation` boundaryだけを所有し、test evidenceをruntime inventoryから外す。 |
| `skills/sdd-implementation/tests/test_isolated_install.py` | Modify | isolated copy-set、missing runtime resource failure、missing test-only evidence非failure、root/canonical read dependency不在を検証する。 |
| `knowledge/wiki/syntheses/sdd-portable-validation-simplification-implementation-plan.md`, `knowledge/index.md`, `knowledge/log.md` | Modify in AM-2 | reviewed result、fresh verification、remaining riskを同期し、historical SPV closeoutとこのamendment closeoutを混同しない。 |

## Requirement And Acceptance Inventory

#### Requirements

- R-01: isolated installed skillがsource repositoryに依存せず、explicit targetとexecution-time resourcesでdirect Git validationを完結する。
- R-02: standalone/bundled generic validatorを追加せず、explicit targetと三つのdirect Git gateを維持する。
- R-03: missing execution-time resource、target/Git capability failure、test-only evidence absenceのfailure ownershipを区別する。
- R-04: portable packageからrepository-specific canonical plan、root path、hash、history identityを排除する。
- R-05: root ownerがstrict-zero policyとcanonical planのdirect repository-bound validationを保持する。
- R-06: normative mechanical gateを三つに保ち、fresh direct-Git behaviorを退行させない。
- R-07: runtime inventoryとisolated release/CI copy-setを分離し、package-external read dependencyを排除する。
- R-08: Superpowers ownershipとthin SDD compositionを維持する。
- R-09: current capability/binding fail-closed behaviorを維持する。
- R-10: agent/repository-owned sequential fallbackとHuman authority boundaryを維持する。
- R-11: isolated copyとsynthetic Git forward testsをsource checkout非依存で維持する。
- R-12: fresh combined verification、knowledge closeout、final reviewを本追補に対して完了する。
- R-13: existing ownerだけを変更し、新しいmechanismを増やさない。
- R-14: First-Write Worktree Gateの全direct behaviorを維持する。
- R-15: exact seven-role KIS wiringを維持する。

#### Acceptance criteria

- AC-01: isolated installがsource repositoryなしでresource resolution、direct Git validation、package testsを完了する。
- AC-02: portable packageにgeneric validator executableはなく、explicit target bindingだけを用いる。
- AC-03: missing execution-time resourceは`broken skill installation`、Git capability failureはgate-specific failure、test-only evidence absenceはnormal gate failureではない。
- AC-04: portable contract、prompt、reference、fixtureにrepository-specific identityがない。
- AC-05: root strict-zero/CI behaviorとcanonical direct repository-bound validationがroot-onlyである。
- AC-06: three direct Git gatesだけがnormativeである。
- AC-07: closureがruntime resource、outside reference、source topologyを検知し、test evidenceをruntime inventoryへ入れない。
- AC-08: Superpowers ownershipとSDD First-Write boundaryが維持される。
- AC-09: capability failureがpre-mutationでfail closedになる。
- AC-10: parallel/sequential/Human authority boundaryが維持される。
- AC-11: source、isolated-copy、root、CI、knowledge validatorsがfreshに成功する。
- AC-12: changed surfaceはexisting ownersだけで、新しいmechanismがない。
- AC-13: First-Write fail-closed scenariosが退行しない。
- AC-14: KIS seven-role full-read/failure boundaryが退行しない。
- AC-15: copied root fixture、parity runner、root snapshot、second semantic parserが存在しない。
- AC-16: existing root CI contract testがcanonical planをdirect validateし、three negative mutationsとsingle semantic parserを保持する。
- AC-17: runtime inventoryはexecution-time resourceだけで、isolated copyはroot script、root fixture、canonical durable documentをruntime/read dependencyにしない。

## Coverage Matrix

| ID | Primary task | Contributing tasks |
| --- | --- | --- |
| R-01 | AM-1 | AM-2 |
| R-02 | AM-1 | AM-2 |
| R-03 | AM-1 | AM-2 |
| R-04 | AM-1 | AM-2 |
| R-05 | AM-1 | AM-2 |
| R-06 | AM-1 | AM-2 |
| R-07 | AM-1 | AM-2 |
| R-08 | AM-1 | AM-2 |
| R-09 | AM-1 | AM-2 |
| R-10 | AM-1 | AM-2 |
| R-11 | AM-1 | AM-2 |
| R-12 | AM-2 | AM-1 |
| R-13 | AM-1 | AM-2 |
| R-14 | AM-1 | AM-2 |
| R-15 | AM-1 | AM-2 |
| AC-01 | AM-1 | AM-2 |
| AC-02 | AM-1 | AM-2 |
| AC-03 | AM-1 | AM-2 |
| AC-04 | AM-1 | AM-2 |
| AC-05 | AM-1 | AM-2 |
| AC-06 | AM-1 | AM-2 |
| AC-07 | AM-1 | AM-2 |
| AC-08 | AM-1 | AM-2 |
| AC-09 | AM-1 | AM-2 |
| AC-10 | AM-1 | AM-2 |
| AC-11 | AM-2 | AM-1 |
| AC-12 | AM-1 | AM-2 |
| AC-13 | AM-1 | AM-2 |
| AC-14 | AM-1 | AM-2 |
| AC-15 | AM-1 | AM-2 |
| AC-16 | AM-1 | AM-2 |
| AC-17 | AM-1 | AM-2 |

## Tasks

### Task 6: AM-1 — Existing-owner canonical direct validation and resource split

- [ ] **Implementation status:** pending; implementation begins only after the exact preconditioned current-main-second-parent `ours` no-ff merge and its tree/reachability proof succeed.
- [ ] **Deliverable:** delete the copied root fixture and parity runner; make the existing root CI contract test direct-validate the canonical plan and consume the existing package semantic parser; split runtime inventory from isolated test evidence without changing direct Git, strict-zero, First-Write, or KIS behavior.
- [ ] **Requirement coverage:** R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-13, R-14, R-15.
- [ ] **Acceptance coverage:** AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17.
- [ ] **Dependencies:** content edit前のexact-identity `ours` no-ff merge prerequisite; no prior amendment task.
- [ ] **Behavioral interface:**
  - **Consumes:** exact precondition evidence: planning/spec commit `8b433806af6835bbf859bea7a7e30a0752d6d294`、feature tip `e5b6b77e790d8d89952b84cfbb04886546e8e8e5`、current main `5e68f5c466b7efcd6e8b3ebb1daf1e6f76682684`、shared pre-amendment tree `8f995222eef73ab5d56a9fb227f367bf8b44c634`、merge base `15152126fe0785bcf789a9ecbfe752b9e368fc4e`、original checkout/target-branch fingerprints、non-planning divergence absence、and the post-merge parent/lineage/tree proof. It also consumes `scripts/test_skill_ci_workflow.py` のcurrent amendment block text、current approved spec bytes、workflow text、existing `plan_errors` semantic-parser interface、portable fixture、isolated skill copy、synthetic explicit Git target、First-Write/KIS/root strict-zero contracts。
  - **Produces:** feature treeを保持しcurrent mainをsecond parentとするnon-force no-ff `ours` merge verdict、両parent/lineage reachability、merge-tree/pre-merge-feature-tree equality、then root CI contract testだけがownerとなるcanonical direct repository-bound verdictと`plan_errors`だけがownerとなるcurrent amendment semantic verdict。root copied snapshot/runner/workflow stepはなく、execution-time-only runtime inventory、isolated test copy-set、classified missing-resource behaviorを残す。
- [ ] **Verification intent:** RED first proves that current-amendment selectorを外してhistorical SPV blockを渡す場合、またはcurrent expected inventory/task schemaと三repository-bound negative mutationのいずれかを変える場合に、既存ownerのCI contractがfailureとなることを示す。各removed root artifact、duplicate parser、missing execution-time resource、source/root/canonical read dependencyもowner contract違反として観測する。GREENはcurrent-amendment blockを同一 `plan_errors` interfaceでsemantic passさせ、package fixture mutation coverageとsource-independent package suiteを維持し、CI regression failure、isolated package independence、approved specが要求するdirect Git / strict-zero / First-Write / KIS preservation suitesを保持する。
- [ ] **Integration placement:** I-AM-1; content edit前にexact-condition `ours` no-ff mergeでcurrent mainをsecond parentにし、両parent/lineage reachabilityとmerge tree equalityを確認してから、deletionとreplacement coverageがgreenの一reviewed changeだけをintegrateする。
- [ ] **Failure owner:** AM-1 implementer; root identity/CI failures remain in `scripts/test_skill_ci_workflow.py`, package semantic/resource failures remain in the existing package tests, and strict-zero/First-Write/KIS regressions return to their existing owners.

### Task 7: AM-2 — Amendment closeout and fresh combined verification

- [ ] **Implementation status:** pending.
- [ ] **Deliverable:** after AM-1 is independently reviewed and serially integrated, record only the reviewed amendment outcome and run the complete current verification set; do not reclassify SPV-1〜SPV-5 history as this amendment's completion.
- [ ] **Requirement coverage:** R-12.
- [ ] **Acceptance coverage:** AC-11.
- [ ] **Dependencies:** AM-1 reviewed and integrated after the recorded exact-condition `ours` no-ff current-main-second-parent merge.
- [ ] **Behavioral interface:**
  - **Consumes:** accepted AM-1 commit range, recorded exact-identity `ours` no-ff merge evidence including both parents/lineages and tree equality, current approved spec identity, all current acceptance mappings, existing package/root/CI/knowledge validation surfaces, and original-checkout preservation evidence.
  - **Produces:** fresh combined result, amendment-specific knowledge closeout, final review disposition, residual-risk statement, and explicit separation of unperformed remote actions.
- [ ] **Verification intent:** RED treats absent deletion evidence, direct-validation negatives, runtime/test separation, isolated independence, strict-zero, First-Write, KIS, plan binding, or knowledge synchronization as incomplete. GREEN requires every current acceptance criterion to have fresh evidence after the final durable edit.
- [ ] **Integration placement:** I-AM-2; serially integrate closeout only after AM-1, then revalidate both merge parents/lineages, retained feature-tree equality, target compatibility, original-checkout preservation, and final Git/root conditions before final review.
- [ ] **Failure owner:** AM-2 closeout owner for freshness and knowledge evidence; any behavior failure returns to AM-1 or its named existing owner.

## Dependency Graph

| Task | Dependencies | Reason |
| --- | --- | --- |
| AM-1 | content edit前のexact-identity `ours` no-ff merge prerequisite | all source/test deletions and replacements share owners and must begin only after the specified equal-tree pair, merge base, target/original fingerprints, and non-planning divergence condition are reverified; the resulting merge retains the feature tree and reaches both parents. |
| AM-2 | AM-1 | closeout can only describe the reviewed, serially integrated implementation. |

## Execution Order

1. AM-1: content edit前にexact factsを再検証し、feature treeを明示的に保つcurrent-main-second-parent Git `ours` no-ff mergeを作る。両parent/lineage reachabilityとmerge-tree equalityを確認してから、single TDD implementationとindependent task reviewを行う。rebase、history rewrite、force、manual conflict resolution、generic fallbackは行わない。
2. AM-2: serially integrate AM-1, perform fresh combined verification, synchronize durable knowledge, and request the canonical final review.

## Serialized Integration

| Step | Task | Preconditions | Combined-state expectation |
| --- | --- | --- | --- |
| I-AM-1 | AM-1 | content edit前にspecified SHA/tree/merge-base、target/original fingerprints、non-planning divergence absenceを再検証し、feature treeを保持するcurrent-main-second-parent Git `ours` no-ff mergeが完了している。両parent/lineage reachability、merge-tree equality、changed paths、RED evidenceが記録済みである。unknown ancestry、identity/tree drift、non-planning divergence、branch/original mismatch、content conflict、rebase、rewrite、force、manual resolution、fallbackはnot eligible。 | deleted root snapshot/runner are absent; root direct check, package single parser, runtime/test split, CI regression, isolated copy, and all preserved boundaries are green together. |
| I-AM-2 | AM-2 | AM-1 review is accepted and reachable from the verified current-compatible target. | current canonical plan, knowledge discovery/log, fresh verification, final Git/root results, and final review all describe this amendment rather than historical SPV completion. |

## Post-Integration Combined Verification

**Scope:** canonical plan/spec binding, exact-identity `ours` merge precondition and retained-tree proof, existing root CI contract and workflow, deleted root paths, package semantic parser/fixture, runtime inventory, isolated copy, three direct Git gates, strict-zero, First-Write, KIS, and knowledge artifacts.

**Pass criteria:** AC-01 through AC-17 each have one primary-owner result; deleted paths and workflow entrypoint remain absent; canonical direct validation rejects wrong approved path, digest, and baseline ancestry; no second parser/snapshot remains; direct Git normal execution ignores absent test-only evidence but rejects missing execution-time resource; source-independent isolated suite and all preserved fail-closed/root/knowledge checks are current and green.

**Required evidence:** reviewed AM-1 change range and task-review result; the specified SHA/tree/merge-base recheck, target/original fingerprints, non-planning divergence absence, `ours` no-ff merge parents/lineages, and retained-feature-tree equality; root direct positive and three negative results; selected current-amendment semantic positive and historical-block/schema-negative results; isolated-copy results; workflow/strict-zero/First-Write/KIS preservation results; final plan/spec digest and baseline ancestry; knowledge synchronization; final review disposition.

**Failure owner:** AM-2 owns stale or missing combined evidence. A source behavior failure returns to AM-1; root strict-zero, First-Write, and KIS behavior retain their existing named owners.

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed
- Review vocabulary: ready, issues_found, needs_repair, needs_decision, blocked.
- Current disposition: repaired amendment plan independently reviewed and ready; exact-condition `ours` merge prerequisite, AM-1 implementation, and fresh combined verification remain pending.
- Material decision request: none
- Material risk: none. The exact `ours` merge predicates remain execution-time stop conditions, not a current plan-readiness risk.
- Remote publication state: not authorized and not required for plan authoring.
