---
title: SDD portable validation と責務単純化 実装計画
date: 2026-08-14
status: active
review_state: independently-reviewed
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

**Goal:** install 済み `sdd-implementation` を source repository 非依存の薄い composition にし、明示 target に対する三つの direct Git gate と package closure を、isolated install と synthetic Git repository で証明する。

**Architecture:** portable package は public contract、required resources、package tests だけを所有し、generic validation は追加 executable を介さず explicit target へ直接 Git probe する。repository 固有の migration/history/canonical-plan/CI policy は既存 root owner に残し、Superpowers は lifecycle/worktree/TDD/review/finishing、SDD はその composition と knowledge/authority seam だけを所有する。

**Tech Stack:** portable Markdown skill contract、Python 3.9+ standard-library `unittest`、Git CLI、GitHub Actions、Obsidian-compatible LLM Wiki、current Superpowers lifecycle skills。

## Approved North Star Identity

- Approved North Star path: knowledge/wiki/syntheses/sdd-portable-validation-simplification.md
- Approved North Star anchor: 目標
- Approved North Star identity: sdd-portable-validation-simplification#目標@2026-08-14
- Approved snapshot SHA-256: 1a8d209ca01e73828043b19c8bfe22d35bd1afa64603add1b7a180a20487285c
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: knowledge/wiki/syntheses/sdd-portable-validation-simplification.md
- Approved spec SHA-256: 1a8d209ca01e73828043b19c8bfe22d35bd1afa64603add1b7a180a20487285c
- Approval state: approved

## Plan Binding

- Repository baseline: 0eb5d97717d644c95ad2e52c9721c6e8c29391ef
- Planning worktree: /private/tmp/skills-sdd-portable-validation-simplification
- Integration branch: codex/sdd-portable-validation-simplification
- Current-tree compatibility: compatible
- Independent review verdict: ready
- Repository checks: passed
- Readiness evidence state: current
- Original checkout path: /Users/omitsuhashi/repos/omitsuhashi/skills
- Starting branch: main
- Starting HEAD SHA: 82dcd32157ff9690ae038f982f3916009e449f80
- Captured starting status: clean
- Binding evidence: baseline は current `HEAD` と一致し、current-tree ancestor check は成功した。baseline package tests 93件、root migration/history regression 22件、CI workflow contract 8件、repository architecture validator が fresh に成功した。

## Independent Plan Review Summary

- Review date: 2026-08-14
- Verdict: ready
- Disposition: ready
- Decision requests: none
- Material risks: none
- Durable finding summary: findingなし。reviewはapproved identityとtrusted Git binding、R-01〜R-13 / AC-01〜AC-12の一意なprimary ownership、SPV-1〜SPV-5のacyclic execution/integration、current-tree buildability、root migration/history ownerの維持、prohibited durable contentと追加validator/adapter/state/protocolの不在を確認した。raw review artifactとtranscriptはdurable planへ複製していない。

## Global Constraints

- Authority A を維持する。Human authority は material Written Spec change と別途 authorization が必要な remote action に限定し、execution method、issue plan、plan 自体の追加 Human approval は要求しない。
- target repository は caller が明示し、canonical absolute path として解決する。CWD、installed skill の source checkout、親 directory、別 worktree から target を推定しない。
- generic mechanical validation は `exceptional-local-scratch-pre-write`、`pre-commit-candidate`、`final-closeout` の三点だけとし、同じ explicit target に対する direct Git probe だけを使う。
- standalone/bundled validator、repository validation adapter、hook registry、scheduler、persistent state、telemetry、追加 protocol、evidence cache、exactly-once machinery を新設しない。
- `scripts/validate_sdd_transient_artifacts.py` とその root regression、one-off migration/history lineage、root CI invocation は repository owner の既存 surface として保持する。portable package からは参照しない。
- canonical-plan parity は package test から root-owned fixture/regression へ移すが、coverage を削除、optional 化、または quick shape check へ縮退させない。
- Superpowers が generic lifecycle、worktree allocation、TDD、dispatch、review/fix、branch finishing を所有する。SDD はそれらの algorithm や fallback を再記述しない。
- fresh worker/model selection、repository-external handoff、target/CWD/write destination binding は public contract の一つの runtime capability interface に集約し、prompts/references は owner と task-local inputs だけを参照する。
- capability/resource/path/state が一意に判定できない場合は、影響する最初の mutation 前に fail closed にする。runtime-specific tool/model/provider 名を durable contract に固定しない。
- parallel eligibility は agent/repository-owned とし、dependency または write-conflict evidence が unknown なら sequential execution に戻す。本実装計画自体は shared file ownership があるため全 task を sequential に実行・統合する。
- package public contract、prompts、references、tests、fixtures に repository 固有 commit/blob hash、canonical wiki path、migration marker、username/absolute path を残さない。
- prospective production/test/script body、patch body、execution command body、concrete runtime routing を durable plan に保存しない。
- remote push、PR、merge、release、live install その他の remote write は本計画の local readiness に含めず、別途明示 authorization がない限り実行しない。
- `knowledge/raw/**` は変更しない。reviewed plan と implementation closeout は `knowledge/index.md` と append-only `knowledge/log.md` を同期する。

## File Responsibility Map

| Path | Operation | Exact responsibility |
| --- | --- | --- |
| `skills/sdd-implementation/SKILL.md` | Modify in SPV-1 and SPV-4 | portable public contract、explicit target、三つの normative direct Git gate、failure classification、thin Superpowers/knowledge composition、単一 runtime capability interface の正本 |
| `skills/sdd-implementation/tests/test_portable_git_gates.py` | Create in SPV-1 | synthetic Git repository 上で三 gate の direct probe、positive/negative state、mutation invalidation、failure classification を public behavior として forward-testする owner |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Modify in SPV-1 and SPV-4 | public contract の explicit target/gate uniqueness、portable content、Superpowers ownership、authority A、禁止 surface を固定する contract owner |
| `skills/sdd-implementation/tests/test_transient_artifact_contract.py` | Modify in SPV-1 and SPV-4 | repository-external default、exceptional scratch gate、durable summary route、gate名参照だけが重複しないことを固定する owner |
| `skills/sdd-implementation/tests/test_isolated_install.py` | Create in SPV-2 | skill folder の isolated copy、source/parent 非参照、package-relative resource closure、broken-installation/target-runtime failure 分離を forward-testする owner |
| `skills/sdd-implementation/tests/test_plan_contract.py` | Modify in SPV-2 | portable plan semantic validator と package-relative representative fixture のみを検証し、root canonical plan を読まない owner |
| `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md` | Replace in SPV-2 | repository identity、canonical path、個人 path を含まない package-local representative ready-plan fixture |
| `skills/sdd-implementation/references/plan-contract.md` | Modify in SPV-2 | portable plan schema/prohibition/readiness contract。package fixture と root canonical parity の owner 分離を明示する owner |
| `scripts/fixtures/sdd-plan-contract/ready-plan.md` | Create in SPV-3 | 現行 canonical SDD plan parity の repository-owned expected fixture |
| `scripts/test_sdd_canonical_plan_parity.py` | Create in SPV-3 | canonical SDD plan と root fixture の inventory/coverage/graph/order parity を固定する repository regression owner |
| `scripts/validate_sdd_transient_artifacts.py` | Preserve and verify in SPV-3/SPV-5 | `f07aebc` three-report baseline、marker parent/authorized introduction/cleanup lineage、exact path/mode/blob、cleanup後再導入禁止の root-only validator owner |
| `scripts/test_validate_sdd_transient_artifacts.py` | Preserve and verify in SPV-3/SPV-5 | root validator の one-off migration/history behavior と scratch/candidate/final-tree regression owner |
| `.github/workflows/skill-architecture.yml` | Modify in SPV-3 | root validator/regressions、canonical parity、isolated package closure、package tests を source checkout で fresh 実行する CI owner |
| `scripts/test_skill_ci_workflow.py` | Modify in SPV-3 | 上記 CI invocation set の欠落、履歴非完全性、add-then-delete 見落としを失敗にする contract owner |
| `skills/sdd-implementation/references/planning-context.md` | Modify in SPV-4 | pre-implementation stage routing と worker-specific handoff owner。common runtime/path/model guard は public contract を参照する |
| `skills/sdd-implementation/references/research-stage.md` | Modify in SPV-4 | Research 固有 inputs/results と repository-external report requirement。common binding algorithm は持たない |
| `skills/sdd-implementation/prompts/repository-researcher.md` | Modify in SPV-4 | Research Worker 固有 scope/artifact/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/spec-synthesizer.md` | Modify in SPV-4 | Spec Synthesis 固有 inputs/durable output/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/spec-reviewer.md` | Modify in SPV-4 | Spec Review 固有 lens/raw verdict/return fields。common guard owner を参照する |
| `skills/sdd-implementation/prompts/plan-reviewer.md` | Modify in SPV-4 | Plan Review 固有 lens/readiness routing/return fields。common guard owner を参照する |
| `skills/sdd-implementation/tests/test_preimplementation_context.py` | Modify in SPV-4 | stage references/prompts が common guard を複製せず task-local inputs を追加することを固定する contract owner |
| `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` | Modify in SPV-4 | Superpowers worktree methodology の再実装を拒否し、selected workspace の CWD/write binding と pre-write stop だけを固定する compatibility owner |
| `knowledge/wiki/syntheses/sdd-portable-validation-simplification.md` | Modify in SPV-5 | landed behavior、acceptance evidence、remaining risk、local completion state を approved scope を変えずに記録する current spec owner |
| `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` | Modify in SPV-5 | broader SDD design の current ownership seam と supersession relation を更新する owner |
| `knowledge/wiki/syntheses/sdd-portable-validation-simplification-implementation-plan.md` | Modify in SPV-5 | task/review/integration/verification の durable closeout summary。raw report/transcriptは格納しない |
| `knowledge/index.md` | Modify in SPV-5 | current spec/plan/design の active canonical discoverability owner |
| `knowledge/log.md` | Modify in SPV-5 | reviewed plan と implementation closeout の append-only lifecycle evidence owner |

## Requirement And Acceptance Inventory

### Requirements

- R-01: installed skill folder と required package resources だけで explicit target repository に対する SDD validation を完結する。
- R-02: canonical absolute explicit target と同一の `git -C TARGET` binding を使う direct Git contract を public `SKILL.md` に一度だけ定義し、standalone/bundled validator を追加しない。
- R-03: package resource 欠落を `broken skill installation`、target/Git/capability failure を target/runtime-side failure として mutation 前に区別する。
- R-04: portable public contract、prompts、references、tests、fixtures から repository 固有 hash/path/marker/canonical plan/個人 path を除去する。
- R-05: root validator、migration/history regression、canonical-plan parity、CI invocation contract を repository-owned surface に保持する。
- R-06: mechanical validation point を三 gate に限定し、各 gate の inputs、Git surface、pass/block boundary、state invalidation、re-run freshness を一意にする。
- R-07: mandatory resource の存在/readability/skill-relative resolution と package 外参照/source topology dependency の不在を isolated closure test で固定する。
- R-08: generic lifecycle/worktree/TDD/review/finishing を Superpowers owner に戻し、SDD を薄い repository-independent composition にする。
- R-09: target/CWD/write binding、external handoff、fresh dispatch/result collection、Git operations 等の required capability と pre-mutation stop を contract test で固定する。
- R-10: parallel eligibility を agent/repository-owned、unknown dependency/conflict を sequential fallback、Human authority を material Written Spec change/remote action に限定する。
- R-11: installed-folder と synthetic Git repository の positive/negative forward tests を source checkout 非依存で実行する。
- R-12: source package tests、isolated install tests、root validators/regressions、CI contract、architecture/skill validators、diff hygiene、final Git gate を fresh combined verification で成功させる。
- R-13: diff を既存 owner と最小 test/fixture surface に限定し、新しい adapter/scheduler/state/telemetry/protocol を追加せず durable knowledge を close out する。

### Acceptance criteria

- AC-01: isolated install が source repository access なしで resource resolution、direct Git validation、package tests を完了する。
- AC-02: portable package に generic validator executable がなく、public contract が explicit canonical target と同一 Git binding だけを使う。
- AC-03: missing resource と Git capability failure が別 owner/failure category として mutation 前に観測できる。
- AC-04: portable files/fixtures に repository 固有 hash/path/marker/canonical plan/個人 absolute path がない。
- AC-05: root history/migration/canonical parity coverage と CI invocation contract が保持される。
- AC-06: 三 gate だけが normative で、mandatory input、positive/negative state、mutation invalidation、re-run が isolated test で観測できる。
- AC-07: closure test が mandatory resource 欠落、package 外参照、source topology dependency を検出する。
- AC-08: SDD public contract が Superpowers 所有の generic methodology を再定義しない。
- AC-09: required capabilities と unavailable 時の pre-mutation stop が contract test で固定される。
- AC-10: parallel eligibility、sequential fallback、Human authority boundary が contract test で固定される。
- AC-11: all relevant source、isolated-copy、repository validator、CI contract checks が fresh に成功する。
- AC-12: implementation diff が既存 owner/minimum surface に限定され、禁止された新規 mechanism がない。

## Coverage Matrix

| ID | Primary task | Contributing tasks |
| --- | --- | --- |
| R-01 | SPV-2 | SPV-1, SPV-5 |
| R-02 | SPV-1 | SPV-2, SPV-4 |
| R-03 | SPV-1 | SPV-2 |
| R-04 | SPV-2 | SPV-1, SPV-4 |
| R-05 | SPV-3 | SPV-5 |
| R-06 | SPV-1 | SPV-2 |
| R-07 | SPV-2 | SPV-5 |
| R-08 | SPV-4 | SPV-1 |
| R-09 | SPV-4 | SPV-1, SPV-2 |
| R-10 | SPV-4 | SPV-5 |
| R-11 | SPV-2 | SPV-1, SPV-5 |
| R-12 | SPV-5 | SPV-1, SPV-2, SPV-3, SPV-4 |
| R-13 | SPV-4 | SPV-1, SPV-2, SPV-3, SPV-5 |
| AC-01 | SPV-2 | SPV-1, SPV-5 |
| AC-02 | SPV-1 | SPV-2, SPV-4 |
| AC-03 | SPV-1 | SPV-2 |
| AC-04 | SPV-2 | SPV-1, SPV-4 |
| AC-05 | SPV-3 | SPV-5 |
| AC-06 | SPV-1 | SPV-2 |
| AC-07 | SPV-2 | SPV-5 |
| AC-08 | SPV-4 | SPV-1 |
| AC-09 | SPV-4 | SPV-1, SPV-2 |
| AC-10 | SPV-4 | SPV-5 |
| AC-11 | SPV-5 | SPV-1, SPV-2, SPV-3, SPV-4 |
| AC-12 | SPV-4 | SPV-1, SPV-2, SPV-3, SPV-5 |

## Tasks

### Task 1: SPV-1 — Explicit target と三つの direct Git gate

- [ ] **Deliverable:** public `SKILL.md` が explicit target identity と三つの normative gate を一度だけ所有し、synthetic Git forward tests が各 gate の observable behavior と fail-closed boundary を RED→GREEN で固定する。
- [ ] **Requirement coverage:** R-02, R-03, R-06。
- [ ] **Acceptance coverage:** AC-02, AC-03, AC-06。
- [ ] **Dependencies:** なし。
- [ ] **Files:** modify `skills/sdd-implementation/SKILL.md`, `skills/sdd-implementation/tests/test_skill_contract.py`, `skills/sdd-implementation/tests/test_transient_artifact_contract.py`; create `skills/sdd-implementation/tests/test_portable_git_gates.py`。
- [ ] **Behavioral interface — Consumes:** caller-supplied canonical absolute target、installed skill directory、target-relative scratch path/non-empty exceptional reason、trusted immutable `starting_head_sha`、current index/HEAD/ignore/working-tree state。
- [ ] **Behavioral interface — Produces:** `exceptional-local-scratch-pre-write` の ignored/untracked/uncommitted leaf verdict、`pre-commit-candidate` の candidate/index cleanliness verdict、`final-closeout` の candidate/HEAD/全 `BASELINE..HEAD` commit-tree verdict、および skill/package・target/runtime・gate-specific failure classification。
- [ ] **Behavioral interface — Invariants:** target identity は `rev-parse` の top-level/inside-work-tree 結果で完全一致を確認し、全 probe は同じ canonical target binding を使用する。scratch gate は normalize/symlink ownership、`check-ignore --no-index`、index/HEAD absenceを判定し、target/path/ownership/ignore/HEAD/index mutationで失効する。pre-commit gate は `write-tree` candidate、candidate/index/unignored working pathを判定し、index/working-tree/ignore mutationで失効する。final gate はcandidate、`HEAD^{tree}`、baseline commit/ancestry、object graphからfreshに導出した全 `BASELINE..HEAD` commit treeを`ls-tree`/`cat-file`相当で判定し、HEAD/index/working-tree/ignore/baseline binding mutationで失効する。exactly-once/cache/state は作らない。
- [ ] **RED intent:** public contract の root validator invocation、repository-specific migration prose、曖昧な全-stage gate を拒否する contract assertions と、ignored scratch/force-add/unmerged index/staged deletion/add-then-delete/stale evidence を区別する synthetic cases を先に追加する。期待する失敗は新しい三 gate contract の欠落または旧 owner leakage に限定し、test discovery/syntax/Git fixture failure は許容しない。
- [ ] **GREEN intent:** `SKILL.md` の repository validation section を approved normative table と explicit target/failure behavior に最小置換する。test file 内の helper は synthetic repository の観測専用とし、installed package が呼ぶ validator module/executable として公開しない。
- [ ] **Focused verification:** 新規 gate forward tests と既存 skill/transient contract tests が、positive/negative/invalidation case を含めて成功し、root validator file 自体に差分がないことを確認する。
- [ ] **Integration placement:** I-1。shared `SKILL.md` owner を先に確定し、後続 task はこの public interface を変更せず closure/ownership/duplication を追加検証する。
- [ ] **Failure owner:** SPV-1 implementer が direct Git fixture、gate contract、failure classification の defect を修復し、独立 task reviewer が spec table との一致と bundled validator 不在を判定する。
- [ ] **Commit boundary:** direct Git gate contract、synthetic forward tests、focused GREEN だけを一つの reviewed task commit に含める。

### Task 2: SPV-2 — Isolated installed-folder closure と portable fixture

- [ ] **Deliverable:** skill folder の isolated copy が source repository/parent を read path に持たず package tests と direct Git validation を完結し、package resources/fixture/plan validator から root canonical dependency と個人/repository identity が消える。
- [ ] **Requirement coverage:** R-01, R-04, R-07, R-11。
- [ ] **Acceptance coverage:** AC-01, AC-04, AC-07。
- [ ] **Dependencies:** SPV-1 reviewed and integrated。
- [ ] **Files:** create `skills/sdd-implementation/tests/test_isolated_install.py`; modify `skills/sdd-implementation/tests/test_plan_contract.py`, `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md`, `skills/sdd-implementation/references/plan-contract.md`。
- [ ] **Behavioral interface — Consumes:** copied installed skill directory、package-relative mandatory resource manifest derived from the public contract、source/parent outside the allowed read closure、one synthetic explicit target。
- [ ] **Behavioral interface — Produces:** isolated package test result、mandatory resource closure verdict、package-outside reference/leakage verdict、`broken skill installation` versus target/runtime failure evidence、portable representative plan semantic result。
- [ ] **Behavioral interface — Invariants:** installed copy は original checkout path、parent topology、root canonical plan、root scripts を利用しない。package fixture は semantic plan contract の representative であり repository canonical parity の source ではない。
- [ ] **RED intent:** existing package test の canonical plan read、source-relative topology dependency、missing mandatory resource、outside-package reference、forbidden repository identity を個別 failure として観測する isolated-copy tests を先に追加する。
- [ ] **GREEN intent:** package plan validator を package-relative semantic validation に限定し、representative fixture を portable identity に置換し、overlay の parity statement を package fixture validation と root-owned canonical parity に分離する。新しい manifest executable や loader module は追加しない。
- [ ] **Focused verification:** isolated copy で package test discovery と synthetic target cases が成功し、mandatory resource を一件欠かした copy と package 外参照を混入した copy がそれぞれ intended category で失敗する。
- [ ] **Integration placement:** I-2。SPV-1 public interface を consume し、SPV-3 が移管する repository-specific canonical parity の package-side removalを完了する。
- [ ] **Failure owner:** SPV-2 implementer が closure harness/resource identity/fixture portability defect を修復し、独立 task reviewer が hidden source dependency と standalone validator の不在を判定する。
- [ ] **Commit boundary:** isolated closure test、portable fixture/validator、overlay owner separation だけを一つの reviewed task commit に含める。

### Task 3: SPV-3 — Repository-owned migration/history/canonical parity と CI

- [ ] **Deliverable:** canonical-plan parity を root fixture/regression へ移し、既存 migration/history validator と回帰を変更せず保持し、CI とその contract test が root checks、isolated closure、package tests を fresh に呼ぶ。
- [ ] **Requirement coverage:** R-05。
- [ ] **Acceptance coverage:** AC-05。
- [ ] **Dependencies:** SPV-2 reviewed and integrated。
- [ ] **Files:** create `scripts/fixtures/sdd-plan-contract/ready-plan.md`, `scripts/test_sdd_canonical_plan_parity.py`; modify `.github/workflows/skill-architecture.yml`, `scripts/test_skill_ci_workflow.py`; preserve and verify `scripts/validate_sdd_transient_artifacts.py`, `scripts/test_validate_sdd_transient_artifacts.py`。
- [ ] **Behavioral interface — Consumes:** root canonical SDD plan、repository-owned expected parity fixture、full Git history、one-off migration identities already owned by root validator、CI workflow text。
- [ ] **Behavioral interface — Produces:** root canonical parity verdict、root history/migration verdict、CI invocation-set verdict、isolated closure/package suite invocation evidence。
- [ ] **Behavioral interface — Invariants:** package tests は root fixture/canonical page を読まない。root validator は three-report baseline、marker lineage、exact mode/blob/path、cleanup transition、post-cleanup reintroduction prohibition の唯一の owner のまま残る。
- [ ] **RED intent:** CI contract に canonical parity regression と isolated closure invocation の欠落を失敗させる expectations を追加し、root parity test を fixture/CI wiring より先に作成する。既存 root validator/regression failure は intended RED として受理しない。
- [ ] **GREEN intent:** repository-specific former package fixture を root fixture として保持し、root parity regression と workflow invocationを最小追加する。現行 root validator と migration regression の implementation/expectations は編集しない。
- [ ] **Focused verification:** root parity test、root migration/history regression、CI workflow contract、package suite invocation が成功し、add-then-delete commit と incomplete history の negative coverage が残る。
- [ ] **Integration placement:** I-3。package-side separation後に repository coverage を接続し、coverage gap のない cutover を成立させる。
- [ ] **Failure owner:** SPV-3 implementer が root fixture/parity/CI wiring defect を修復し、独立 task reviewer が migration/history coverage の削除・optional化・quick-check化がないことを判定する。
- [ ] **Commit boundary:** root parity fixture/regression と CI invocation contract だけを一つの reviewed task commit に含める。

### Task 4: SPV-4 — Superpowers ownership deduplication と authority A

- [ ] **Deliverable:** SDD entrypoint を thin composition にし、common runtime capability/path guard を一箇所に集約し、stage references/prompts は owner reference と worker-specific inputs/results だけを保持する。Authority A、parallel eligibility、sequential fallback を contract tests で固定する。
- [ ] **Requirement coverage:** R-08, R-09, R-10, R-13。
- [ ] **Acceptance coverage:** AC-08, AC-09, AC-10, AC-12。
- [ ] **Dependencies:** SPV-3 reviewed and integrated。
- [ ] **Files:** modify `skills/sdd-implementation/SKILL.md`, `skills/sdd-implementation/references/planning-context.md`, `skills/sdd-implementation/references/research-stage.md`, all four files under `skills/sdd-implementation/prompts/`, `skills/sdd-implementation/tests/test_skill_contract.py`, `skills/sdd-implementation/tests/test_preimplementation_context.py`, `skills/sdd-implementation/tests/test_first_write_worktree_contract.py`, `skills/sdd-implementation/tests/test_transient_artifact_contract.py`。
- [ ] **Behavioral interface — Consumes:** selected Superpowers lifecycle contracts、applicable repository instructions、installed resource paths、explicit target/workspace/CWD/write destinations、fresh dispatch/model/result-collection capabilities、approved Written Spec and remote-action policy。
- [ ] **Behavioral interface — Produces:** thin ordered composition、single common capability guard、worker-specific stage inputs/outputs、pre-mutation blocked diagnosis、agent/repository-owned parallel eligibility or sequential fallback、Human decision/remote-action stop reason。
- [ ] **Behavioral interface — Invariants:** SDD は worktree allocation/fallback、TDD loop、review/fix algorithm、branch finishing、model-tier table を再記述しない。prompts/references は common path rejection/model selection procedureを複製しない。material spec change 以外の agent-repairable evidence gap は Human decision にしない。
- [ ] **RED intent:** detailed First-Write allocation algorithm、duplicated path guards、runtime model/effort table、issue adapter scheduling/integration prose、Human execution-method/issue-plan approval languageを forbidden ownership leakage として先に contract-testする。required capability absence と unknown dependency/conflict の期待分類も先に固定する。
- [ ] **GREEN intent:** public contract に一つの required-capability interface と composition orderを残し、stage resources/prompts を task-local差分へ縮める。Authority A と unknown→sequential は短い observable contract として保持し、新しい adapter/state/protocol を導入しない。
- [ ] **Focused verification:** skill/preimplementation/workspace/transient contract suites が generic ownership leakage、duplicate guard、authority regression、missing capability continuation を拒否し、既存 fresh-worker/Control Return/read-write separation behavior は維持する。
- [ ] **Integration placement:** I-4。SPV-1 の normative gate interface と SPV-2/3 の owner separationを保持したまま shared prose/tests を最終形へ収束する。
- [ ] **Failure owner:** SPV-4 implementer が deduplication/guard/authority compatibility defect を修復し、独立 task reviewer が「削除しすぎによる required SDD behavior 欠落」と「generic methodology 再実装」の両方を判定する。
- [ ] **Commit boundary:** thin composition、common guard、authority/parallel contract、対応 focused tests だけを一つの reviewed task commit に含める。

### Task 5: SPV-5 — Knowledge closeout と fresh combined verification

- [ ] **Deliverable:** 全 task commit と review が integration branch に到達した後、approved spec、current design、reviewed plan、index/log を landed evidence へ同期し、portable/root/CI/full repository checks と final direct Git gate、whole-branch review を fresh に成功させる。
- [ ] **Requirement coverage:** R-12。
- [ ] **Acceptance coverage:** AC-11。
- [ ] **Dependencies:** SPV-4 reviewed and integrated。
- [ ] **Files:** modify `knowledge/wiki/syntheses/sdd-portable-validation-simplification.md`, `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`, this implementation plan, `knowledge/index.md`, `knowledge/log.md`。Source/test filesはfinding修復が必要な場合だけ、そのprimary task ownerへ一回戻す。
- [ ] **Behavioral interface — Consumes:** reviewed task commits、task review verdicts、current integration branch Git facts、approved spec identity、all acceptance mappings、package/root/CI validation surfaces。
- [ ] **Behavioral interface — Produces:** local completion evidence、acceptance-by-acceptance result、remaining risk、unperformed remote action、canonical discoverability、append-only log event、final whole-branch verdict。
- [ ] **Behavioral interface — Invariants:** raw worker/review/test transcripts と runtime path は wiki に複製しない。approved scope/authority は変更しない。ignored untracked local scratch の destructive cleanup は要求しない。remote authorization absence は local completion を失敗にしない。
- [ ] **RED intent:** closeout前に coverage matrix、required task commit reachability、root validator preservation、isolated closure、knowledge index/log effect、final gate evidence の欠落を checklist failure として列挙する。欠落した source behavior はcloseout proseで隠さずprimary taskへ戻す。
- [ ] **GREEN intent:** knowledge worker が landed behavior と fresh evidence identities だけを durable surfacesへ反映し、全 verification surfaceを fresh に実行する。final reviewer は approved spec、reviewed plan、combined diff、tests、knowledge artifacts を一回の whole-branch reviewで判定する。
- [ ] **Focused verification:** package source suite、isolated installed-copy suite、synthetic gate cases、root canonical parity、root migration/history regression、CI invocation contract、repository architecture validator、skill-creator validator、knowledge lint、diff whitespace check が成功する。
- [ ] **Integration placement:** I-5。最後の code/test task review後に knowledge commit を一件だけ統合し、その後に final combined verification と whole-branch reviewを行う。
- [ ] **Failure owner:** behavior/test failure は coverage matrix の primary task owner、root history/parity/CI failure は SPV-3、thin contract/authority failure は SPV-4、knowledge/index/log failure は SPV-5、baseline/commit-range/final gate failure は integration owner が修復する。
- [ ] **Commit boundary:** canonical closeout summary、index/log sync、fresh verification identity だけを一つの reviewed knowledge commit に含める。

## Dependency Graph

| Task | Dependencies | Reason |
| --- | --- | --- |
| SPV-1 | none | normative public Git gate interface を最初に確定する |
| SPV-2 | SPV-1 | installed closure は確定した public gate interface を isolation対象にする |
| SPV-3 | SPV-2 | packageからcanonical parityを外した直後にroot ownerへcoverageを接続する |
| SPV-4 | SPV-3 | shared `SKILL.md`/tests を最終形へ収束し、owner cutover後のcontractをdeduplicateする |
| SPV-5 | SPV-4 | 全 reviewed implementation とserialized integration後にcloseout/combined verificationを行う |

Cycle check: chain は `SPV-1 -> SPV-2 -> SPV-3 -> SPV-4 -> SPV-5` の単方向であり、undefined dependency と cycle はない。

## Execution Order

1. Execute SPV-1: direct Git gate contract と synthetic forward tests を RED→GREEN にし、独立 task reviewを完了する。
2. Execute SPV-2: isolated package closure と portable fixture/validator separation を RED→GREEN にし、独立 task reviewを完了する。
3. Execute SPV-3: root canonical parity と CI owner retention を RED→GREEN にし、独立 task reviewを完了する。
4. Execute SPV-4: Superpowers/common-guard/authority deduplication を RED→GREEN にし、独立 task reviewを完了する。
5. Execute SPV-5: durable closeout、fresh combined verification、final whole-branch reviewを完了する。

全 task は shared owners と migration cutover orderを持つため sequential execution とする。task内でも一つの public seam、一つの failing behavior、一つの最小修正を順に進め、同一 issue 内の concurrent implementer は使用しない。

## Serialized Integration

| Step | Task | Preconditions | Expected combined state |
| --- | --- | --- | --- |
| I-1 | SPV-1 | baseline binding current、focused RED provenance確認、task review ready | public contract は三 direct Git gateだけを所有し、synthetic gate suite GREEN。root validator/testsは未変更 |
| I-2 | SPV-2 | I-1 reachable、SPV-2 isolated REDがsource dependency/resource leakに限定、task review ready | installed copy self-contained、package fixture portable、package plan validatorはroot canonical page非依存 |
| I-3 | SPV-3 | I-2 reachable、root parity/CI RED確認、root migration/history baseline GREEN、task review ready | canonical parityはroot regression owner、root validator/history/CI invocation coverage保持、package isolation維持 |
| I-4 | SPV-4 | I-1〜I-3 reachable、shared file overlap再評価、task review ready | thin SDD composition、single common guard、Authority A、unknown→sequential、全focused suites GREEN |
| I-5 | SPV-5 | I-1〜I-4の全required task commit reachable、全task review complete、target HEAD ancestry current | canonical knowledge/index/log同期、all acceptance evidence current、final combined verification/whole-branch review ready |

Integration owner は各 step 前に actual commit range、changed paths、semantic/resource assumptions、required task commit reachability を Git facts から再導出する。partial integration、unreviewed result、unknown ancestry、non-descendant target rewrite は integration-ready としない。textual clean merge だけでは成功としない。

## Post-Integration Combined Verification

### Scope

- `skills/sdd-implementation/` の public contract、全 prompts/references、package tests/fixtures。
- root canonical parity fixture/regression、root migration/history validator/regression、CI workflow/invocation contract。
- approved spec、current design、reviewed implementation plan、`knowledge/index.md`、`knowledge/log.md`。
- baselineからintegration branchまでの全 commit tree、current HEAD/index/working-tree/ignore state。

### Pass criteria

1. AC-01〜AC-12 の各 primary owner evidence が一件ずつあり、contributing evidence と矛盾しない。
2. package source tests と isolated installed-copy tests が成功し、isolated copy は source checkout/parent/root scriptsを読まない。
3. synthetic Git tests が ignored scratch、force-add、unmerged index、staged deletion、add-then-delete、baseline non-ancestor、state mutationによるevidence失効とre-runを期待通り判定する。
4. root canonical parity、root migration/history regression、root validator、CI invocation contract が成功し、one-off history owner surfaceに機能差分がない。
5. repository architecture validator、skill-creator validator、knowledge lint、diff whitespace check が成功する。
6. final `final-closeout` gate が current candidate、HEAD tree、immutable `starting_head_sha..HEAD` の全commit treeで `.superpowers/**` entry zeroを確認する。ignored/untracked/unstaged/uncommitted scratchはfailureにしない。
7. final whole-branch review が approved spec fit、material simplicity、current material risk、knowledge consistencyをreadyとし、禁止された validator/adapter/state/protocol が存在しない。

### Required evidence

- focused task RED/GREEN result と independent task review verdict。
- task commit IDs と integration branch reachability。
- isolated-copy root identity/read-closure evidence と synthetic target case summary。
- root validator/history/parity/CI contract の fresh result summary。
- architecture/skill/knowledge/diff checks の fresh result summary。
- final direct Git gate と whole-branch review の durable verdict summary。

### Failure owners by acceptance criterion

| Acceptance | Failure owner |
| --- | --- |
| AC-01 | SPV-2 |
| AC-02 | SPV-1 |
| AC-03 | SPV-1 |
| AC-04 | SPV-2 |
| AC-05 | SPV-3 |
| AC-06 | SPV-1 |
| AC-07 | SPV-2 |
| AC-08 | SPV-4 |
| AC-09 | SPV-4 |
| AC-10 | SPV-4 |
| AC-11 | SPV-5; underlying behavior failure returns to its primary task owner |
| AC-12 | SPV-4; forbidden surface introduced by another task returns to that task owner |

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed
- Repository-ready disposition: sequential five-task execution through `superpowers:subagent-driven-development`, serialized integration I-1〜I-5, then one fresh combined verification and whole-branch review。
- Material decision request: none
- Material risk: none
- Remote publication state: not authorized and not required for local readiness
