---
title: SDD Plan Ownership Alignment 実装計画
date: 2026-08-14
tags:
  - sdd-implementation
  - planning
  - implementation-plan
  - skill-architecture
status: active
review_state: independently-reviewed
plan_readiness: ready
implementation_state: local-complete-remote-update-pending
aliases:
  - SDD agent-owned execution plan
  - SDD plan readiness implementation plan
---

# SDD Plan Ownership Alignment 実装計画

## Plan Binding

本計画は、Planning Controller から Human-approved current Written Spec として渡された
[[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]を、agent-owned execution
contract へ変換した Plan Author 成果物である。Human に plan approval、file choice、command choice、
prospective code、commit granularity の判断を求めない。

- Repository baseline: c370fe14de1641aa5ee30b3fa001f4d857078091
- Planning worktree: /Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/sdd-plan-ownership-alignment-planning
- Integration branch: codex/sdd-plan-ownership-alignment-planning
- Current-tree compatibility: compatible
- Independent review verdict: ready
- Repository checks: passed
- Readiness evidence state: current
- upstream methodology: active discovery で解決した `superpowers:writing-plans` v6.2.0
- local precedence: approved spec の Plan Contract Overlay が、upstream の保存先、prospective body、
  Human execution-choice prompt、plan approval semantics と衝突する output / routing contract を上書きする
- amendment transition precedence: 下記Single-use Amendment Migration Entryが、このamendmentの最初のPOA-4 entryに
  限り、Plan Contract Overlayの「canonical ready planとrepresentative fixtureがcurrent executable validatorを同時に
  passする」preconditionをexact missing-schema REDへ狭く置換する。他のbinding / review / repository checkは維持する
- Amendment follow-up author state: independently_reviewed
- Amendment implementation state: POA-4 through POA-8 local work reviewed and complete
- Amendment follow-up repository check state: passed
- Amendment follow-up Implementation Stage entry: allowed_and_consumed
- Amendment migration baseline commit: f07aebce7bbf854cd64184311d204cf04055fd28
- Amendment migration exception state: consumed_and_retired
- Current final-tree state: `.superpowers/**` entry zero
- Local completion state: LOCAL_COMPLETE
- Remaining remote action: authorized non-force integration-branch update; pending / unpublished

## Approved North Star Identity

- Approved North Star path: knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md
- Approved North Star anchor: North Star
- Approved snapshot SHA-256: 1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559
- Approval state: approved

## Approved Written Spec Identity

- Approved spec path: knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md
- Approved spec SHA-256: 1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559
- Approval state: approved

## Historical Durable Plan Review Evidence

- lifecycle scope: amendment前のoriginal POA-1〜POA-3 plan review、readiness、Implementation Stage entryだけを
  記録するhistorical evidenceであり、current amendmentのreview / readiness fieldではない。
- review date / stage: 2026-08-14、original planのfresh independent Plan Review後にagent repairとfresh re-reviewを実施。
- reviewed spec identity: `knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md`、approval-state
  SHA-256 `1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559`、`accepted` / `approved`。
- reviewed plan identity: 本canonical path
  `knowledge/wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan.md`、repository baseline
  `c370fe14de1641aa5ee30b3fa001f4d857078091`、上記approved spec binding。review時のplanはplanning
  worktree内の未commit artifactだったため、reviewed byte digestまたはreview commitが存在するとは主張しない。
- initial review disposition: `issues_found` / `needs_repair`。blocking findingは2件で、(1) Written Specの
  durable approval stateとplan bindingの矛盾、(2) `plan-contract.md`追加で影響する二つ目のstrict
  reference-set expectationがPOA-1 file ownershipから漏れていたこと。decision requestは`none`。
- repair / re-review result: approval metadata、spec digest、index / append-only log、POA-1 / POA-2 task boundaryを
  agent repairし、fresh re-reviewは両findingをresolved、repository readiness `ready`、decision request
  `none`、material risk `none`とした。
- transient review integrity fingerprints: initial review SHA-256
  `0d5ff88616ec9c8cd4496b7e5d8912a4f636f8a6b419b1937867c18069548e34`、re-review SHA-256
  `52b6345da5321e220fc47f8aeafd307e75a8d1ae50d057d5763fed349a631822`。これらはtask-local
  `.superpowers/reviews/...` artifactsの同一性確認用fingerprintであり、transient files自体をdurable sourceまたは
  future cloneから読めるcommitted evidenceとは扱わない。本sectionがdurable reviewer verdict summaryである。
- historical readiness / entry: Planning Controllerはoriginal approved spec bindingとcanonical plan pathを確認し、Plan Readiness
  Gateを`ready`、Control Returnを`status: complete`としてImplementation Stageへentryした。landed implementation
  provenanceはPOA-1 `fa2b26c9003a5c525040cbd28bb224b004c0fdbb` / `6f1ca9fb39340c417d5afcb8784244bb69d258a7`、
  POA-2 `6d8222d64c4a50328e3dd873abdcabb43fdf4be7` / `71889d21343efdcaafe0152ce3eb763d0857b8e5`である。
- approved amendment binding: Human-approved `sdd-transient-artifact-boundary-2026-08-14`を同じNorth Starと
  original approval-snapshot identityへ追加bindingした。POA-1〜POA-3のlanded historyは書き換えず、POA-4〜POA-8を
  follow-up sequenceとして追加する。amendment前commitの`.superpowers/**` blobはaudit historyに保持し、history
  rewriteを行わない。

このhistorical readinessはcurrent amendmentの`ready`、Human plan approval、canonical final whole-branch review、
`LOCAL_COMPLETE`、remote action authorizationを意味しない。current amendmentは下記のformal Readiness Resultと
single-use migration entry contractだけで評価する。fresh independent re-reviewと、そのentry contractが要求する
bounded repository precheckより前にImplementation Stageへentryしない。POA-4が所有するamended schema / fixtureの
test-first transitionやPOA-6が所有するfinal-tree cleanupを、pre-entryのall-GREEN条件として先取りしない。

## Goal

Human approval を North Star と Written Spec に限定し、承認済み scope 内の plan creation、repair、
review、readiness、task ordering、serialized integration、combined verification を agent / repository
ownership に移す。

## Architecture

current `sdd-implementation` の Superpowers-first lifecycle と Planning Controller / fresh worker 分離は
維持する。新しい local Plan Contract Overlay が durable plan schema、禁止内容、coverage invariant、
ordering / integration contract、readiness vocabulary を所有し、`planning-context.md` が fresh Plan
Author と独立 Plan Reviewer の routing と repair loop を接続する。production runtime、scheduler、
packet、event log、resume protocol、upstream fork は追加しない。amendment follow-upは全SDD stageのraw handoffを
task / session用のboundedなrepository外 temporary pathへ移し、repository-level validatorがGit index、candidate
tree、cleanup後のnew commit treeをfail closedに検査する。`.superpowers/**`はignore coverage確認済みの例外的な
local scratchだけに残し、durable summaryはcanonical spec、reviewed plan、append-only logへ統合する。
amendment Implementation entryだけは、pre-amendment commitに固定したexact three-report migration baselineを
single-useで受理する。これはPOA-4のschema / fixture RED-to-RED transitionとPOA-6 cleanupを実行可能にする
bootstrap seamであり、candidate / final-tree readiness、post-cleanup commit invariant、または通常のPlan Readinessを
緩和しない。

## Tech Stack

Markdown Skill instructions、Python 3.9+ standard-library `unittest` contract tests、Obsidian-compatible
LLM Wiki、current Superpowers lifecycle skills。

## Global Constraints

- Human-owned product boundary は approved North Star / Written Spec だけである。plan はその scope を
  拡張、縮小、再解釈しない。
- plan creation、review、repair、readiness は agent / repository ownership とし、Human plan approval
  または execution-choice promptを追加しない。
- Human へ戻すのは material North Star / Written Spec change または repository evidence だけでは
  解消できない material decision の一件だけである。
- remote、privileged、destructive action の separate authorization boundary を維持する。その未承認は
  対象 action だけを止め、plan readiness や local completion を遡って block しない。
- `superpowers:writing-plans` を required methodology として維持し、fork、vendor、copy、replacementを
  作らない。
- upstream の task sizing、file responsibility、TDD sequence、interface reasoning、self-review を使うが、
  durable plan に prospective production / test code、script body、patch body、擬似 patch、commit command
  body を保存しない。
- exact path は current-tree責務の識別に必要な範囲だけ記録する。line range、shell command、snippet、
  commit boundary は durable plan の required content や Human checkpoint にしない。
- portable contract は inputs、outputs、required capabilities で記述し、concrete runtime、tool name、
  model、provider、agent ID、run-specific routing を固定しない。
- task implementation と task review は canonical SDD に従って一件ずつ完了させる。並列 issue adapter は
  本変更へ適用しない。
- plan 本体を runtime ledger にしない。実行時のtuple、task result、review evidence、recovery state は
  ordinary plan-owned transient progress ledger に保持する。
- historical plan / approval / execution evidence は書き換えず、current design page には supersession
  relation と landed behavior だけを同期する。
- normal SDD stageのresearch / worker / fix / review report、brief、raw review output、transcript、duplicate
  spec / plan / task contentはrepository `.superpowers/**`へ書かず、task / session用のboundedなrepository外
  temporary pathへrouteする。
- repository-local `.superpowers/**` scratchはconcrete operational reasonとpre-write `.gitignore` coverageを
  mechanically証明できる場合だけ許し、ignored / untracked / unstaged / uncommittedに限定する。coverageがなければ
  local writeをfailさせ、repository外 temporary routeを使う。
- cleanup後のGit index、candidate commit tree、以後のnew commit tree、PR final treeに`.superpowers/**`
  entryを許さない。ignored local scratchとfinal-tree removalのstaged deletionは許し、tracked / staged / candidate
  entryはvalidatorでfailさせる。
- current tracked report 3件はcontentを破壊せずGit indexとPR final treeから除く。必要なlocal copyは既存の
  `.gitignore` coverage下でignored / untracked scratchとして保持できる。
- amendment前のcommitやblobを除くためのhistory rewriteは行わない。cleanup後のnew commitへの再導入だけを拒否する。
- amendment Implementation entryは、`f07aebce7bbf854cd64184311d204cf04055fd28`のtreeとbyte-for-byte一致する
  下記3 tracked reportだけをpre-amendment migration baselineとして一度だけ受理できる。追加 / 変更 / staged
  `.superpowers/**` delta、ignore coverage欠落、baseline不一致、cleanup owner欠落、または例外の再利用はfail closedとする。
  この例外はPOA-4開始だけを解放し、candidate / final-tree readinessを与えない。
- `knowledge/raw/**` は変更しない。

## File Responsibility Map

| Path | Operation | Responsibility |
|---|---|---|
| `skills/sdd-implementation/references/plan-contract.md` | Create in POA-2; modify in POA-5 | repo-local Plan Contract Overlay、plan semantic fields、coverage / order / integration invariants、禁止内容、review / readiness taxonomy、plan-stage raw review destination boundaryの正本 |
| `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md` | Create in POA-2; modify test-first in POA-4 | implementation bodyを持たず、POA-4がcanonical planと同時にR-01〜R-21 / AC-01〜AC-20、POA-1〜POA-8へ拡張し、同じexecutable semantic validatorでinventory / coverage / graph / orderを一致させるrepresentative fixture |
| `skills/sdd-implementation/tests/test_plan_contract.py` | Create in POA-1; modify test-first in POA-4 | original Plan Contract RED / GREENを保持し、amended inventory、task graph、transient destination / tree invariant、prohibited durable contentへ同じexecutable validatorを拡張する |
| `skills/sdd-implementation/SKILL.md` | Modify in POA-2 and POA-5 | Plan Stage ownershipに加え、全normal stageのrepository-external transient route、local scratch gate、durable summary、Git tree failure boundaryを持つportable contract |
| `skills/sdd-implementation/references/planning-context.md` | Modify in POA-2 and POA-5 | fresh Plan Author / independent Plan Reviewer routingと、Spec / Plan review raw handoffのrepository-external destination separation |
| `skills/sdd-implementation/prompts/plan-reviewer.md` | Create in POA-2; modify in POA-5 | independent reviewer contractと、raw review artifactのrepository-external temporary binding / durable verdict summary separation |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Modify in POA-1, POA-2, and POA-4 | original public lifecycle contractを保持し、all-stage transient boundaryとrepository validator fail-closed behaviorをtest-firstで追加する |
| `skills/sdd-implementation/tests/test_preimplementation_context.py` | Modify in POA-1, POA-2, and POA-4 | original Plan Author / Reviewer isolationを保持し、Research / Spec / Planのrepository-external raw handoff expectationsをtest-firstで固定する |
| `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` | Modify in POA-4 | source / durable writeのplanning-worktree containmentと、first transient Research Reportのrepository-external bounded-path contractを別々にfixture化する |
| `skills/sdd-implementation/tests/test_transient_artifact_contract.py` | Create in POA-4 | 全SDD stageのrepository外handoff、local scratch ignore gate、durable-summary routing、tracked / staged / candidate-tree拒否をtemporary repository fixtureで固定するtest-first contract |
| `scripts/validate_sdd_transient_artifacts.py` | Create in POA-5 | cleanup後のGit index、candidate tree、new commit / final treeに`.superpowers/**` entryがないことを検査し、working-tree scratchやpre-amendment historyだけでは失敗しないrepository validator |
| `scripts/test_validate_sdd_transient_artifacts.py` | Create in POA-4 | validatorのmissing-ignore、tracked、staged-tree、candidate / new commit再導入、ignored scratch、staged deletion、historical ancestorをtest-firstに固定するroot-level regression |
| `scripts/test_skill_ci_workflow.py` | Modify in POA-4 | CIがrepository transient-artifact validatorとfocused regressionをfreshに実行する契約をREDで追加し、POA-5のworkflow実装を検証する |
| `.github/workflows/skill-architecture.yml` | Modify in POA-5 | architecture / context / focused suitesと同じPython matrixでrepository transient-artifact validationを実行する |
| `.gitignore` | Verify before POA-6; modify only if current coverage is missing or too narrow | repository-local `.superpowers/**` scratchを最初のwrite前からcoverするignore boundary。現在は`.superpowers/`でroot全体をcoverする |
| `skills/sdd-implementation/references/research-stage.md` | Modify in POA-5 | Research Reportをplanning worktree内ではなくtask / session boundedなrepository外 temporary pathへbindする |
| `skills/sdd-implementation/prompts/repository-researcher.md` | Modify in POA-5 | research report write bindingとblocked returnをrepository外 transient boundaryへ移す |
| `skills/sdd-implementation/prompts/spec-synthesizer.md` | Modify in POA-5 | research inputとspec draftのdurable / transient destinationを分離し、raw handoffをrepository外へ限定する |
| `skills/sdd-implementation/prompts/spec-reviewer.md` | Modify in POA-5 | raw review artifactをrepository外 temporaryへ置き、durable verdict summaryだけをcanonical surfaceへ返す |
| `.superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/approved-residual-fix-report.md` | Remove from Git index / final tree in POA-6 | tracked reportをnon-destructively追跡解除し、必要ならignored / untracked local scratchとして保持する |
| `.superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/final-fix-report.md` | Remove from Git index / final tree in POA-6 | tracked reportをnon-destructively追跡解除し、必要ならignored / untracked local scratchとして保持する |
| `.superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/task-2-report.md` | Remove from Git index / final tree in POA-6 | tracked reportをnon-destructively追跡解除し、必要ならignored / untracked local scratchとして保持する |
| `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` | Modify at closeout | broader current design に landed Plan Stage ownership と supersession relation を統合 |
| `knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md` | Modify at closeout | current context-isolation design の Plan Author seam に successor relation を明記し、historical evidence は保持 |
| `knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md` | Modify at closeout | implementation result、acceptance evidence、current lifecycle state を product boundary を変えずに同期 |
| `knowledge/index.md` | Modify | current spec / plan / landed design の canonical discoverability を一意に維持 |
| `knowledge/log.md` | Modify | plan authoring、implementation closeout、review / verification effect を append-only で追跡 |

## Requirement And Acceptance Inventory

- Requirements: R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15, R-16, R-17, R-18, R-19, R-20, R-21
- Acceptance criteria: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20

## Single-use Amendment Migration Entry

このsectionはcurrent amendmentのPlan Readinessを支配するplan-specific bootstrap transitionである。Plan Contract
Overlayの「canonical ready planとrepresentative fixtureが同じcurrent executable semantic validatorをpassする」条件を、
この一回のentryに限って下記5のexact missing-schema REDへ置換する。それ以外のapproved identity、binding、independent
review、prohibited content、coverage / graph completeness、repository evidence requirementは変更しない。通常のPlan
Contract Overlay、別plan、再entry、candidate / final-tree readinessへ一般化しない。fresh independent Plan Reviewerが
本planを`ready`とした後、agent-owned readiness finalizationがformal bindingを`ready` / `passed` / `current`へ同期し、
Planning Controllerは次のpreconditionsを一回のatomic evaluationとして確認する。すべて成立した場合だけPOA-4
Implementation Stage entryを許可する。

1. **Immutable baseline binding:** amendment migration baselineは
   `f07aebce7bbf854cd64184311d204cf04055fd28`であり、entry時の`HEAD`はこのcommitと一致する。commitの
   `.superpowers/**` treeは次のmode / blob / path 3件だけである。
   - `100644 b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1 .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/approved-residual-fix-report.md`
   - `100644 c884197bf566cc93f319f3c2a1b6d2ad1563d10e .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/final-fix-report.md`
   - `100644 da22b7580961fb9a2087ab1eb034fb34000711f8 .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/task-2-report.md`
2. **Exact current index equality:** current indexの`.superpowers/**` setは上記3 entryとmode / blob / pathまで一致し、
   baselineとの差分はzeroである。追加tracked path、intent-to-add、staged content、report modification / deletion、
   rename、または他のindex deltaを一件でも検出したらentryを拒否する。ignored working-tree scratchはこのsetへ
   数えないが、tracked / staged stateへ昇格してはならない。
3. **Ignore and write boundary:** root `.gitignore`が上記3 pathとoptional repository-local `.superpowers/**`
   scratchをcoverする。normal raw handoffは引き続きrepository外 temporaryへ置き、新しいrepository-local scratchは
   concrete operational reasonとmechanical pre-write ignore checkなしに作らない。
4. **Owned migration:** POA-4がamended semantic validator / representative fixtureのtest-first transitionを所有し、
   POA-5がmigration / validator / CI GREENを所有し、POA-6が上記3 entryだけのnon-destructive final-tree removalを
   所有する。owner、dependency、またはserialized integration slotが欠けた場合はentryを拒否する。
5. **Precisely bounded expected RED:** pre-entryのcurrent semantic validator / representative fixtureは、未実装の
   R-16〜R-21、AC-15〜AC-20、POA-4〜POA-8 schema / inventory / coverage / graph / order transitionに由来する
   canonical-plan incompatibilityだけをREDとして許容する。test discovery、syntax、approved identity / baseline、
   prohibited content、R-01〜R-15 / AC-01〜AC-14 regression、または上記以外のfailureは例外対象外である。
   Fresh reviewerの`ready`後はformal review / binding fields自体をRED reasonに残さない。
6. **Single consumption:** Controllerはentry時にbaseline SHA、exact path / blob set、ignore result、review verdict、
   expected-RED classificationをordinary plan-owned progress ledgerへtransferし、同じatomic transitionで例外を
   `consumed`にする。resume、retry、別session、別worktree、別HEAD、または後続taskがこの例外を再利用してはならない。

この例外で許されるのは、POA-4 / POA-5のpre-cleanup commit treeがbaselineのexact 3 entriesを継承することだけで
ある。POA-6はI-6でcandidate treeをzeroにし、I-6以後のすべてのnew commit treeとPR final treeは
`.superpowers/**` entry zeroでなければならない。baselineとancestor blobはaudit historyとして保持し、reset、
filter、rebase rewrite、replacement commit、force publicationで消さない。追加path、baseline drift、staged delta、
exception reuseは`needs_repair`へ丸めずentry前にfail closedとし、Human decision requestを作らない。

## Tasks

### Task 1: POA-1 — Plan Contract の executable RED regression

**Deliverable:** approved spec の plan-level / task-level fields、coverage、dependency、execution / integration、
combined verification、prohibition、readiness vocabulary を executable tests と strict resource-shape expectations
として固定し、未実装の overlay / representative fixture の欠落だけを原因に意図した RED になる。

**Requirement coverage:** R-02, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15.

**Acceptance coverage:** AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12.

POA-1 はこれらの
RED evidence contract を所有し、最終 behavior の primary owner は GREEN 化を所有する POA-2 とする。

**Dependencies:** なし。approved spec と current upstream `writing-plans` を直接 consume する。

**Behavioral interface:**

- Consumes: approved spec identity、requirement / acceptance inventory、current upstream plan methodology、
  repository file responsibility evidence。
- Produces: executable RED tests、complete requirement / acceptance inventory assertions、strict reference-set
  expectations、期待する failure reason と GREEN pass condition。
- Does not produce: `plan-contract.md`、representative ready-plan fixture、Plan Stage routing / prompt、GREEN
  implementation、scheduler、runtime validator service、worker packet、prospective implementation body、upstream skill copy。

**Files:** create `tests/test_plan_contract.py`; modify only the strict reference-set expectations in
`tests/test_skill_contract.py` and `tests/test_preimplementation_context.py`。POA-1 は overlay / fixture / routing /
prompt を作成しない。

**Verification intent:**

1. RED contract authoring: define the representative-plan validator and mutations for approved-spec identity、
   complete inventory / coverage、unknown ID、orphan task、undefined dependency、cycle、execution order、
   serialized integration / combined verification、prospective body、Human plan-approval language。
2. Expected RED evidence: contract tests fail because `plan-contract.md` and ready-plan fixture are absent、and both
   strict resource-shape suites fail because `plan-contract.md` is absent。Import、syntax、test discovery、or
   unrelated assertion failure does not satisfy this gate。
3. Review gate: the POA-1 reviewer confirms the tests express approved-spec behavior、the exact expected failures
   are recorded、the changed paths contain tests only、and no overlay / fixture / production routing was introduced。
4. Transition: reviewed intentional RED is POA-1's completion condition and I-1 precondition。It is not Plan
   Readiness `ready`、not product GREEN、and not permission to skip POA-2。

**Integration placement:** first as a reviewed intentional-RED checkpoint。Task POA-2 consumes the executable
failure contract and is solely responsible for turning the combined state GREEN。

**Failure owner:** Task POA-1 implementer repairs RED test semantics / harness defects; independent task reviewer
verifies spec fit、expected-failure provenance、and absence of premature implementation。

### Task 2: POA-2 — Agent-owned Plan Stage routing と independent review loop

**Deliverable:** POA-1 の reviewed RED contract を local Plan Contract Overlay、representative fixture、
compatibility repair、Plan Stage routing / reviewer prompt で GREEN にする。Planning Controller は approved spec と
bounded paths を fresh Plan Author へ渡し、author self-review 後に独立 Plan Reviewer を dispatchし、
plan deficiency を Human へ返さず修復し、`ready` だけを Implementation Stage entry へ接続する。

**Requirement coverage:** R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15.

**Acceptance coverage:** AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13.

POA-2 が
overlay / fixture / routing / prompt と、POA-1 の executable contract を GREEN にする全 compatibility / route
test changes を所有する。

**Dependencies:** reviewed intentional-RED Task POA-1 integrated at I-1。POA-2 は POA-1 が作成した
executable failure contract と strict reference-set expectations を consume する。POA-1 GREEN、overlay、fixture、
reviewer prompt、or routing implementation を predecessor output として要求しない。

**Behavioral interface:**

- Consumes: approved spec path / approval state、trusted worktree and baseline binding、upstream skill path、
  POA-1 executable RED contract / strict resource expectations、Plan Author result、independent reviewer verdict。
- Produces: local Plan Contract Overlay、representative ready-plan fixture、focused / compatibility GREEN、fresh
  author dispatch、fresh independent review、internal `needs_repair` loop、material conflict onlyの`needs_decision`、
  non-decision blockerの`blocked`、`ready`から既存Control Return `complete`への一意 mapping。
- Preserves: Planning Controller の bounded read set、Superpowers lifecycle ownership、Human Written Spec authority、
  implementation task review、knowledge closeout、remote authorization boundary。

**Files:** create `references/plan-contract.md`、`tests/fixtures/plan-contract/ready-plan.md`、
`prompts/plan-reviewer.md`; modify `SKILL.md`、`references/planning-context.md`、
`tests/test_plan_contract.py`、`tests/test_preimplementation_context.py`、`tests/test_skill_contract.py`。The test
files are shared sequentially: POA-2 preserves POA-1's reviewed RED intent、repairs any contract-test defect needed
to exercise that intent、provides the missing resources、and adds only the Plan Stage routing / prompt assertions it owns。

**Verification intent:**

1. Pre-implementation observation: I-1 is intentionally RED for the exact missing overlay / fixture reasons。Before
   changing the implementation、routing-focused tests also expose current literals requiring an approved /
   repository-approved plan、missing independent reviewer seam、missing repair disposition、and the existing
   prompt-set expectation。
2. GREEN implementation: create the overlay and fixture、repair strict resource compatibility、then change routing /
   prompt / focused tests so Human approval subjects are only North Star / Written Spec、Plan Author and
   Reviewer are isolated、`issues_found` is deterministically classified、`needs_repair` never leaves the agent loop、
   only material spec conflict yields one decision request、and remote-action authorization is not a plan blocker。
3. GREEN gate: the plan-contract、public-contract、and pre-implementation-context suites all pass together。
   No expected RED remains at POA-2 completion。
4. Forward evidence: representative plan flows cover ready、unassigned acceptance repair、prospective-body repair、
   dependency-cycle repair、current-tree method correction、material spec conflict、serialized integration、and
   unauthorized remote publication without changing local readiness。

**Integration placement:** second, after the reviewed POA-1 intentional-RED commit is reachable on the integration
target。I-2 is the first GREEN combined state。POA-2 must not duplicate the overlay schema inside `SKILL.md` or
`planning-context.md`。

**Failure owner:** Task POA-2 implementer owns overlay / fixture / compatibility / route / prompt / test defects;
independent task reviewer verifies authority boundaries and current-tree buildability。Only an evidenced material
spec conflict returns to Human authority。

### Task 3: POA-3 — Durable closeout と combined repository verification

**Deliverable:** landed Plan Stage semantics、supersession relations、canonical discovery、append-only lifecycle
recordが一致し、full integrated branch が全 acceptance と repository authoring / architecture checks を満たす。

**Requirement coverage:** R-01, R-02, R-03, R-04, R-05, R-06, R-07, R-08, R-09, R-10, R-11, R-12, R-13, R-14, R-15.

**Acceptance coverage:** AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14.

**Dependencies:** POA-1 の reviewed RED result、POA-2 の reviewed combined-GREEN result、integrated
changed-path revalidation がすべて完了していること。

**Behavioral interface:**

- Consumes: reviewed POA-1 / POA-2 results、actual changed paths、fresh focused validation evidence、approved spec
  identity、current / historical design identities。
- Produces: current designのlanded contract、supersession relation、canonical index entry、append-only closeout、
  final whole-branch review candidate。
- Preserves: historical plan / approval / execution evidence、raw sources、planのnon-ledger boundary、separate
  remote authorization。

**Files:** modify `sdd-implementation-skill-design.md`、`sdd-preimplementation-context-isolation-spec.md`、
`sdd-plan-ownership-alignment.md`、`knowledge/index.md`、`knowledge/log.md`。本plan本文はruntime result ledgerへ
変換しない。

**Verification intent:**

1. Baseline observation: current catalog and current design do not yet expose the Plan Contract Overlay or its
   supersession relation; append-only log has no implementation-closeout event for this change。
2. GREEN behavior: one canonical relation for spec and plan is discoverable、broader SDD design points to the local
   Plan Stage authority、historical records remain historical、and closeout records exact fresh evidence without
   claiming remote action or final review before it occurs。
3. Final evidence: focused SDD tests、repository script tests、LLM Wiki tests、skill architecture validation、skill
   context validation / warning-free report、skill authoring validation、knowledge link / index / log inspection、
   complete branch whitespace check、original-checkout preservation、fresh whole-branch review all succeed。

**Integration placement:** third and last。Knowledge closeout is integrated only after POA-1 and POA-2 are reachable
and reviewed。Final whole-branch review happens once after this closeout candidate。

**Failure owner:** Task POA-3 knowledge worker repairs authoring / discoverability / provenance defects; implementation
or integration failures return to the owning POA task; one bounded final fixer and one scoped re-review handle a material
final-review finding under the existing SDD contract。

### Task 4: POA-4 — Transient artifact boundary の executable RED contract

**Deliverable:** amended specの全SDD-stage handoff、pre-write ignore gate、Git index / candidate-tree invariant、
non-destructive tracked-report migration、durable-summary routingをtest-firstに固定し、現行repository-contained
destinationとmissing repository validatorだけを理由に意図したREDとなる。

**Requirement coverage:** R-16, R-17, R-18, R-19, R-20, R-21.

**Acceptance coverage:** AC-15, AC-16, AC-17, AC-18, AC-19, AC-20.

POA-4はRED evidence contractを所有する。final behaviorのprimary ownerはPOA-5〜POA-8に分かれ、POA-4は
それらのcontributing taskである。

**Dependencies:** reviewed and landed POA-1、POA-2、POA-3 state、Human-approved amendment、fresh Plan Reviewer
`ready`、上記Single-use Amendment Migration Entryのatomic precheck / consumption。amendment前のtask commit、review
evidence、historical `.superpowers/**` blobは入力として参照できるが変更しない。

**Behavioral interface:**

- Consumes: R-16〜R-21、AC-15〜AC-20、current `.gitignore` coverage、tracked report inventory、現行skill /
  reference / prompt destinations、current CI and test surfaces、consumed migration-baseline evidence。
- Produces: repository-external handoff expectations、ignore-coverage precondition、temporary Git repository
  fixtureによるtracked / staged / candidate / historical boundary、durable-summary-only output、R-01〜R-21 /
  AC-01〜AC-20 / POA-1〜POA-8へ同期したrepresentative ready-plan fixture、exact RED reasons。
- Does not produce: validator implementation、skill / reference / prompt migration、tracked-report index cleanup、
  canonical closeout、raw report copy、history rewrite。

**Files:** create `skills/sdd-implementation/tests/test_transient_artifact_contract.py` and
`scripts/test_validate_sdd_transient_artifacts.py`; modify test expectations in
`skills/sdd-implementation/tests/test_first_write_worktree_contract.py`、
`skills/sdd-implementation/tests/test_preimplementation_context.py`、
`skills/sdd-implementation/tests/test_plan_contract.py`、
`skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md`、
`skills/sdd-implementation/tests/test_skill_contract.py`、
`scripts/test_skill_ci_workflow.py`。production skill、references、prompts、workflow、validator、tracked reportsは
POA-4で変更しない。

**Verification intent:**

1. RED contract authoring: every normal SDD stage rejects repository-contained raw handoff destinations and resolves
   a task / session bounded repository-external temporary location while canonical source / knowledge writes remain in
   the trusted planning worktree。
2. Git fixture contract: missing ignore coverage blocks repository-local scratch before write; ignored / untracked /
   unstaged / uncommitted scratch and final-tree removalのstaged deletionはaccepted; tracked index entry、staged-tree
   content、candidate / cleanup後new commitへの再導入はrejected; pre-amendment ancestor blobだけではrejectedにしない。
3. Shared semantic fixture: canonical planとrepresentative ready-plan fixtureは同じexpanded inventory、coverage、
   task graph、execution / integration orderを同じvalidatorへ渡す。stale fixture、missing amended ID、coverage / graph /
   order mismatchはI-4の許可されたRED reasonではない。
4. Expected RED evidence: current `.superpowers/research/**` destination literals、worktree-contained raw review
   binding、missing validator、missing CI invocationだけがfailure reasonである。test discovery、syntax、temporary
   repository setup、stale representative fixture、unrelated architecture assertionのfailureはこのgateを満たさない。
5. Review gate: independent task reviewがamended spec coverage、canonical / representative fixture semantic parity、
   fixture isolation、working-tree scratch preservation、
   no-history-rewrite boundary、test-only changed pathsを確認する。
6. Entry provenance: the task consumes the already-marked-consumed migration exception and cannot re-evaluate、broaden、
   or reuse it。Any pre-entry path / baseline drift would have blocked dispatch rather than becoming an allowed POA-4 RED。

**Integration placement:** single-use migration entry後、I-4でreviewed intentional REDとしてlocal integration
targetへ直列統合する。POA-5がこのcontractをGREENにするまでmigration behaviorをrepository-ready、final-tree-ready、
push-readyとは扱わない。Plan Stage entry readinessとamendment implementation GREENを混同しない。

**Failure owner:** POA-4 implementerがtest semantics、fixture isolation、expected-failure provenanceを修正し、
independent task reviewerがpremature implementationやdestructive cleanupがないことを検査する。

### Task 5: POA-5 — Repository-external handoff migration と fail-closed validator

**Deliverable:** POA-4のreviewed REDを、Research、Spec、Plan、Implementation、task review、repair、integration、
final review、knowledge closeoutの全SDD stageに共通するrepository-external transient write binding、local scratch
pre-write ignore gate、Git index / candidate / new-tree validator、CI integrationでGREENにする。

**Requirement coverage:** R-16, R-17, R-18, R-19, R-20.

**Acceptance coverage:** AC-15, AC-16, AC-17.

**Dependencies:** I-4のreviewed intentional REDがreachableであること。POA-4が記録したfailure contract、expanded
canonical / representative fixture parity、current stage destinations、current Git / CI evidenceをconsumeする。

**Behavioral interface:**

- Consumes: trusted planning-worktree source / durable write boundary、task / session identity、runtime / OSが解決した
  repository外 temporary root、`.gitignore` coverage、Git index and commit-tree evidence、POA-4 regressions。
- Produces: every-stage repository-external raw handoff contract、bounded-path / alias / escape rejection、optional local
  scratchのreason-and-ignore gate、index / staged-tree / candidate-tree / cleanup後new-tree fail-closed validator、fresh
  CI invocation。
- Preserves: canonical spec / plan / source writes in the trusted planning worktree、Planning Controller read boundary、
  fresh worker isolation、Human authority、local scratch bytes、pre-amendment history、remote authorization boundary。

**Files:** create `scripts/validate_sdd_transient_artifacts.py`; modify
`skills/sdd-implementation/SKILL.md`、`skills/sdd-implementation/references/research-stage.md`、
`skills/sdd-implementation/references/planning-context.md`、`skills/sdd-implementation/references/plan-contract.md`、
`skills/sdd-implementation/prompts/repository-researcher.md`、
`skills/sdd-implementation/prompts/spec-synthesizer.md`、
`skills/sdd-implementation/prompts/spec-reviewer.md`、
`skills/sdd-implementation/prompts/plan-reviewer.md`、`.github/workflows/skill-architecture.yml`。POA-5はPOA-4が
所有するrepresentative fixture、test contract、test fixtureを変更せず、GREEN contract / runtime / CI implementationだけを所有する。

**Verification intent:**

1. Migration observation: the current contract requires the first Research Report inside the planning worktree and lets
   review artifacts inherit that repository-contained write binding; these exact literals satisfy POA-4 RED evidence。
2. GREEN behavior: source / canonical destination and transient handoff destination become distinct capabilities。Normal
   raw reports use a task / session bounded repository-external temporary path; unresolved, broad, repository-aliased,
   original-checkout, worktree, or sibling paths fail before write。
3. Local exception: repository-local `.superpowers/**` write is available only for a concrete operational reason after
   mechanical ignore coverage succeeds, and its allowed state remains ignored / untracked / unstaged / uncommitted。
4. Repository enforcement: validator recognizes the already-consumed, exact baseline-bound three-report migration state
   only until POA-6、evaluates the Git index and its candidate tree、rejects any additional / changed / newly staged path and
   cleanup後new commit or final-tree reintroduction、permits ignored working-tree scratch and allowed staged deletion、and
   does not require deletion or rewrite of a pre-amendment ancestor blob。
5. GREEN gate: focused stage contracts、validator regressions、CI workflow contract、existing worktree safety tests pass
   together before independent task review。

**Integration placement:** I-5 follows I-4 and creates the first GREEN migration / validator state。It does not remove the
three baseline reports; therefore the single-use entry exception is already consumed and cannot authorize any second entry、
while POA-6 remains required before candidate-tree and final-tree readiness。

**Failure owner:** POA-5 implementer owns path binding、ignore gate、validator semantics、CI / contract compatibility;
independent task reviewer verifies fail-closed scope and that scratch preservation is not confused with tracked-tree acceptance。

### Task 6: POA-6 — Tracked report final-tree cleanup without local content destruction

**Deliverable:** R-21の3 tracked report entryをGit index、candidate commit tree、PR final treeから除き、必要な
local bytesは`.gitignore` coverage下のignored / untracked scratchとして保持できる状態にする。

**Requirement coverage:** R-18, R-20, R-21.

**Acceptance coverage:** AC-17, AC-19.

**Dependencies:** I-5のvalidator GREEN、current `.gitignore` coverageのmechanical confirmation、raw reportだけに
required durable decisionが残っていないことの確認。required summaryが不足する場合はPOA-7のcanonical targetを
先に特定してsynthesisし、cleanupを停止する。

**Behavioral interface:**

- Consumes: exact R-21 tracked path set、current Git index、candidate-tree projection、ignore coverage、canonical plan /
  spec / logに既に統合されたdurable evidence summary。
- Produces: three index deletions、`.superpowers/**` entry zeroのcandidate tree、optional ignored / untracked local
  copies、validator pass evidence。
- Preserves: report bytes needed as local scratch、pre-amendment ancestor commits and blobs、other untracked / ignored
  state、unrelated user changes、canonical durable summary。

**Files:** remove the three R-21 `.superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/*.md` entries from
the Git index and final tree; verify `.gitignore` and modify it only if coverage is absent before any local scratch write。
Do not add a replacement report path or copy raw content into the wiki。

**Verification intent:**

1. Pre-cleanup evidence: exact tracked path inventory equals the three R-21 reports and `.gitignore` covers the retained
   scratch location before index mutation。
2. Cleanup behavior: candidate tree has zero `.superpowers/**` entry while a needed local copy may remain ignored /
   untracked / unstaged / uncommitted; final-tree deletion is represented as an allowed staged deletion rather than
   destructive byte removal。
3. History boundary: amendment前ancestor commit is left reachable and unchanged。No reset、filtering、rebase rewrite、
   force publication、or replacement commit is used to erase historical blobs。
4. Review gate: validator and focused migration tests pass against the actual index / candidate tree, and independent task
   review confirms exact path scope and preservation of unrelated state。

**Integration placement:** I-6 follows I-5。Only after the reviewed cleanup commit is reachable may later commits be
accepted; every subsequent integration slot re-runs the validator to prevent reintroduction。

**Failure owner:** POA-6 implementer owns exact index cleanup and local-copy preservation。Missing ignore coverage、extra
tracked paths、or durable-summary uncertainty stops cleanup and returns to POA-5 or POA-7 rather than deleting content。

### Task 7: POA-7 — Durable amendment closeout and canonical synchronization

**Deliverable:** amended transient-artifact behavior、cleanup effect、no-history-rewrite boundary、canonical discovery、
append-only lifecycle evidenceがspec、reviewed plan、broader current design、index、logで一意に一致する。

**Requirement coverage:** R-16, R-19, R-21.

**Acceptance coverage:** AC-18, AC-19.

**Dependencies:** reviewed POA-5 migration / validator GREEN、reviewed POA-6 cleanup、actual changed-path and candidate-tree
revalidation。All durable facts must be based on current files / Git evidence rather than raw report claims。

**Behavioral interface:**

- Consumes: approved amendment identity、reviewed task verdict summaries、actual index / candidate-tree result、focused
  validator evidence、existing canonical page identities and append-only log。
- Produces: landed transient boundary and supersession relation、updated canonical plan status、one active index record、
  append-only closeout event with evidence identities and remaining remote action state。
- Preserves: approved North Star、original approval-snapshot identity、historical POA-1〜POA-3 evidence、raw source、
  review transcripts outside durable knowledge、separate remote authorization。

**Files:** modify `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`、
`knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md`、
`knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md`、this canonical plan、`knowledge/index.md`、
`knowledge/log.md`。Do not create a duplicate plan、review report、worker report、task packet、or new durable ledger。

**Verification intent:**

1. Canonical effect: broader lifecycle pages point to this spec for conflicting transient destination / write-binding
   semantics while preserving their unaffected worktree、controller、implementation-review、closeout boundaries。
2. Durable summary: required decisions、findings、repairs、verdicts、test / validator evidence identities are synthesized
   without raw report / transcript duplication; index has one active spec / plan relation and log receives an append-only event。
3. Tree effect: canonical pages describe three report final-tree removals and optional ignored local scratch without claiming
   ancestor deletion or history rewrite。
4. Knowledge gate: applicable Obsidian / llm-wiki validation、link / index / log inspection、repository validator pass before
   independent task review。

**Integration placement:** I-7 follows reviewed I-6 and is the final content integration slot before combined verification。
No remote publication occurs in POA-7。

**Failure owner:** POA-7 knowledge worker owns canonical inconsistency、index / log synchronization、unsupported evidence
claims。Implementation or Git invariant failures return to POA-5 or POA-6; material spec conflict alone returns to Human。

### Task 8: POA-8 — Fresh combined verification, final review, and authorized push update

**Deliverable:** full baseline-to-integration result passes fresh focused and repository checks、one canonical whole-branch
review has no unresolved material finding、every required commit remains reachable、and the authorized integration branch
update is pushed without rewriting remote history。

**Requirement coverage:** R-04, R-18, R-20.

**Acceptance coverage:** AC-13, AC-17, AC-20.

**Dependencies:** I-4〜I-7のrequired task / review commits reachable、candidate tree `.superpowers/**` entry zero、durable
closeout synchronized、original checkout preserved。Remote push remains last and is performed only under the separate
authorization carried by the execution request; absent authorization stops only publication and does not revoke local readiness。

**Behavioral interface:**

- Consumes: complete commit range、actual changed paths、fresh test / validator / knowledge results、task review verdicts、
  candidate / final-tree inspection、original-checkout fingerprint、remote branch ancestry and publication authorization。
- Produces: fresh combined verification record、one canonical whole-branch review verdict、at most one bounded final fix and
  one scoped re-review if needed、non-force push update of the integration branch、published commit identity。
- Preserves: all required task commits、default checkout starting HEAD / status、remote history、pre-amendment audit history、
  no-PR / no-merge / no-live-install boundary unless separately authorized。

**Files:** no planned production path ownership。A material review finding may change only its owning POA scope through one
bounded fixer; durable evidence corrections follow POA-7。Publication changes remote branch state only after local gates pass。

**Verification intent:**

1. Fresh local gate: focused SDD and transient-artifact suites、root script tests、repository validator against actual index /
   candidate tree、skill architecture / context / authoring checks、LLM Wiki checks、whitespace and changed-path inspection pass。
2. Reachability gate: every POA-4〜POA-7 task / review / fix commit is reachable from the integration tip, the default checkout
   matches its captured start, and `.superpowers/**` is absent from candidate and final tree while ancestor history remains intact。
3. Review gate: one fresh whole-branch reviewer evaluates baseline through integration tip against the amended spec and this
   plan。A material finding gets one bounded fixer and one scoped re-review; no second whole-branch review loop is created。
4. Publication gate: after fresh results are still current and remote ancestry is compatible, update the authorized integration
   branch without force or history rewrite。A push rejection or ancestry divergence stops publication with exact evidence。

**Integration placement:** I-8 is the final verification / publication gate after I-7。Any bounded final-fix commit is
serialized and revalidated before push; otherwise POA-8 adds no content commit。

**Failure owner:** focused failures return to their owning POA task、cross-task failures to the single integration fixer、
knowledge failures to POA-7、publication ancestry / authorization failures to the controller with local completion preserved。

## Dependency Graph

| Task | Direct predecessors | Dependency reason |
|---|---|---|
| POA-1 | none | Defines the executable RED contract and exact expected failures consumed by GREEN implementation |
| POA-2 | POA-1 | Must implement overlay / routing against the reviewed RED contract; does not depend on predecessor GREEN or overlay output |
| POA-3 | POA-1, POA-2 | Can close out only reviewed landed behavior and actual integrated paths |
| POA-4 | POA-1, POA-2, POA-3 | Adds the amended test-first contract only after original closeout is stable and the fresh-ready, exact-baseline, single-use migration entry has been consumed |
| POA-5 | POA-4 | Implements all-stage migration and repository validator against the reviewed amended RED contract |
| POA-6 | POA-5 | Removes tracked reports only after ignore and candidate-tree semantics are mechanically enforced |
| POA-7 | POA-5, POA-6 | Synchronizes only reviewed landed migration and exact cleanup evidence into durable knowledge |
| POA-8 | POA-4, POA-5, POA-6, POA-7 | Runs final combined verification and publication only after every content task and review result is reachable |

The graph is acyclic。The selected serialized topological execution order is
`POA-1 → POA-2 → POA-3 → POA-4 → POA-5 → POA-6 → POA-7 → POA-8`。

## Execution Order

1. POA-1 — execute as the test-first contract task。Record the exact overlay / fixture absence failures、prove the
   harness and test syntax are sound、obtain independent task review of that intentional RED deliverable、then
   integrate it at I-1。Do not create the overlay / fixture or claim product GREEN in POA-1。
2. POA-2 — execute from reviewed I-1 RED。Create the overlay / fixture、apply routing / prompt / compatibility-test
   changes、and require the complete focused group to turn GREEN before independent task review and I-2。
3. POA-3 — revalidate actual result paths and spec binding, then execute durable closeout and integrated checks。
4. POA-4 — after atomic verification and consumption of the single-use amendment migration entry, add the amended
   test-first contract and integrate only the reviewed intentional RED with exact current-contract / missing-validator
   failure provenance。Do not re-evaluate or reuse the entry exception inside the task。
5. POA-5 — migrate all normal SDD transient destinations and make the repository validator / CI contract GREEN。
6. POA-6 — verify ignore and durable-summary preconditions, then remove only the three R-21 entries from the index / final
   tree while preserving any needed ignored local scratch and all ancestor history。
7. POA-7 — synchronize the landed amendment into canonical design、spec、plan、index、append-only log and validate knowledge。
8. POA-8 — run fresh combined verification, one canonical whole-branch review, any single bounded fix / scoped re-review,
   then update the authorized remote branch only if ancestry and all evidence remain current。

## POA-1 → POA-2 Gate Transition

POA-1 は「実装済み behavior」ではなく「実行可能な期待 failure contract」を deliver する特別な
test-first task である。そのため task completion / dependency satisfaction と product GREEN を次のように
分離する。

1. POA-1 completion: test syntax / discovery が正常で、recorded failures が missing overlay / fixture と
   それに紐づく strict resource expectation に限定され、independent review が test contract を承認する。
2. Dependency release: その reviewed RED commit が I-1 で reachable になった時点で POA-2 を開始できる。
   POA-1 GREEN、overlay、fixture、routing output はこの precondition ではない。
3. POA-2 completion: POA-2 が overlay / fixture / compatibility / routing / prompt を実装し、POA-1 の RED
   contract と POA-2 route tests が全て GREEN になり、independent review が承認する。
4. GREEN release: I-2 後にだけ POA-3、Plan Readiness evaluation、その他の GREEN state consumer
   は進行できる。I-1 の intentional RED を repository-ready または implementation-ready とみなさない。

## POA-4 → POA-5 Gate Transition

pre-entryでは、現行semantic validator / representative fixtureがまだR-01〜R-15、AC-01〜AC-14、POA-1〜POA-3
schemaだけを実装しているため、amended canonical planとの差分はSingle-use Amendment Migration Entryで列挙したexact
schema-transition REDとして受理できる。このREDはfinal cleanupのfailureでもcurrent Plan Readinessのfailureでもなく、
POA-4がtest-firstに所有する入力である。他のfailure、baseline / path / ignore drift、またはformal reviewer / binding
fieldのnon-ready stateは受理しない。

POA-4はamendment behavior implementationではなくschema / fixture transitionを含むtest-first expectationをdeliverする。
POA-5へのrelease条件は、test syntax / discoveryとtemporary Git fixtureが正常で、canonical planとrepresentative fixtureが
expanded inventory / coverage / graph / orderについて同じexpanded semantic validatorを通り、残るfailureがcurrent
repository-contained destinations、missing validator、missing CI invocationに限定され、independent reviewがR-16〜R-21 /
AC-15〜AC-20とのfitを確認することである。I-4は意図したREDであり、report cleanup、candidate-tree readiness、remote
publicationを許可しない。POA-5がmigration / validatorを実装してfocused groupをGREENにし、reviewed I-5がreachableに
なった後だけPOA-6へ進む。entry exceptionはPOA-4 dispatch時点ですでにconsumedであり、このtransitionでは再利用しない。

## Serialized Integration

Execution order describes when work is performed; this section describes when reviewed results become part of the
integration target。

| Integration slot | Preconditions | Integrated result | Combined-state expectation |
|---|---|---|---|
| I-1: POA-1 | contract test syntax / discovery is valid、failures are exactly the declared missing overlay / fixture and strict resource expectations、independent task review ready、actual paths are test-only | executable RED contract tests and strict resource-shape expectations | integration target is intentionally RED for the recorded reasons; no overlay / fixture / routing implementation is present and no Plan Readiness claim is made |
| I-2: POA-2 | I-1 reachable、overlay / fixture and routing changes make plan-contract / public-contract / pre-implementation-context suites GREEN together、independent task review ready、no undefined overlay reference | local overlay、representative fixture、compatibility repair、agent-owned route、review prompt、repair / readiness mapping | the reviewed RED contract is satisfied; authoring、review、repair、Control Return mapping form the first coherent GREEN Plan Stage and Human plan approval is absent |
| I-3: POA-3 | I-1 and I-2 reachable and reviewed、all required task results present、current spec binding valid | canonical knowledge closeout and final-review candidate | code / tests / current design / spec relation / index / log describe the same integrated behavior |
| I-4: POA-4 | I-1〜I-3 reachable、amendment approved、fresh plan review ready、exact `f07aebce7bbf854cd64184311d204cf04055fd28` three-report migration entry precheck passed and exception consumed、expanded canonical / representative fixture semantic parity、test discovery and temporary Git fixtures valid、failures exactly match current destination / validator / CI gaps、independent task review ready | amended transient-artifact RED contract、expanded representative fixture、CI expectation | integration target is intentionally RED only for declared amendment behavior gaps; exact baseline reports may be inherited unchanged, existing plan-ownership GREEN remains distinguishable, and no cleanup or exception reuse is claimed |
| I-5: POA-5 | I-4 reachable、all-stage destination migration and validator / CI implementation satisfy the focused RED contract、independent task review ready、baseline report set has no additional / changed / staged entry | repository-external handoff contract、ignore gate、repository validator、CI integration | focused amended suite is GREEN; exactly the inherited baseline reports still exist unchanged and therefore candidate / final-tree readiness remains pending POA-6; the consumed entry exception cannot be reused |
| I-6: POA-6 | I-5 reachable、ignore coverage proven、durable summary sufficient、exact tracked set equals R-21、independent task review ready | three non-destructive index / final-tree deletions with optional ignored local copies | candidate tree has zero `.superpowers/**` entries; ancestor history and unrelated state remain intact; every later integration rejects reintroduction |
| I-7: POA-7 | I-5 and I-6 reachable and reviewed、actual paths and evidence revalidated、canonical authority / authoring gate satisfied | durable design / spec / plan / index / log closeout | implementation、Git boundary、canonical discovery、append-only evidence describe one coherent amendment outcome without raw report duplication |
| I-8: POA-8 | I-4〜I-7 reachable、fresh combined verification and whole-branch review ready、candidate / final-tree invariant and original-checkout preservation proven、remote ancestry and authorization valid | optional single bounded final fix plus non-force integration-branch update | local and published integration tip contain every required commit、zero final-tree `.superpowers/**` entries、no history rewrite、no unauthorized PR / merge / live action |

Integration is single-writer and serialized。A clean textual merge、partial task presence、unreviewed result、or missing
required task result is not integration completion。

## Post-Integration Combined Verification

**Scope:** the complete baseline-to-integration-branch range、all `skills/sdd-implementation` instructions / prompts /
references / tests、the approved spec and this plan、current SDD design pages、`knowledge/index.md`、`knowledge/log.md`、
repository validator / CI contract、Git index / candidate and final trees、repository skill architecture and knowledge
contracts、authorized remote branch update boundary。

Acceptance scope: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20.

**Pass criteria:** Every integrated outcome below must pass with fresh evidence.

- SDD focused suite passes, including the original plan-ownership families and amended all-stage transient-artifact /
  Git-boundary families; root validator regressions and CI workflow contract pass in the supported Python matrix。
- all `R-01`〜`R-21` and `AC-01`〜`AC-20` retain exactly one primary owner and integrated evidence; POA-1 / POA-4
  RED evidence remains distinguishable from POA-2 / POA-5 GREEN behavior、and unknown or orphan IDs are absent。
- dependency graph is acyclic; declared execution order is topological; serialized integration and combined verification
  fields are present and internally consistent。
- no durable plan or routing instruction contains prospective production / test body、script / patch body、commit
  command body、Human plan-approval prompt、or Human execution-choice prompt。
- existing first-write worktree、Planning Controller、implementation review、final review、portable capability、remote
  authorization tests remain green。
- all normal SDD stages bind raw research / worker / fix / review output to task / session bounded repository-external
  temporary paths; canonical source / knowledge writes remain in the trusted planning worktree; repository-local scratch
  fails before write without concrete reason and ignore coverage。
- actual Git index、candidate tree、every post-cleanup commit tree、PR final tree contain zero `.superpowers/**` entries。
  Ignored / untracked / unstaged / uncommitted scratch and allowed staged deletion pass; pre-amendment ancestor history
  remains reachable and unchanged; any new-tree reintroduction fails。
- the pre-cleanup migration exception was consumed exactly once against commit
  `f07aebce7bbf854cd64184311d204cf04055fd28` and only the three declared mode / blob / path entries were inherited through
  I-4 / I-5。No additional、changed、renamed、or newly staged `.superpowers/**` path crossed that boundary。
- the three R-21 reports are absent from the final tree without destructive local scratch deletion, and no raw replacement
  report、duplicate task content、review transcript、or worker packet is added to durable surfaces。
- repository script tests、skill architecture validation、skill context validation and warning-free report、
  `sdd-implementation` skill authoring validation、LLM Wiki tests、index / log semantic inspection all pass freshly。
- complete branch whitespace validation is clean and the original checkout matches its captured starting state。
- one fresh whole-branch reviewer reports no material requirement gap、scope excess、observable regression、or current risk。
- after local evidence and review remain current, the separately authorized integration branch update succeeds without
  force、history rewrite、PR creation、merge、release、or live install。

**Required evidence:** fresh test / validator summaries with counts and exit state、coverage inventory result、actual changed
path set、task-review verdicts、index / candidate / final-tree inspection、ancestor / required-commit reachability、whole-branch
review verdict、original-checkout preservation、remote ancestry and pushed tip identity。Raw evidence belongs in bounded
repository-external transient state; durable decisions、verdict、evidence identities belong in the canonical plan / spec and
append-only closeout log, not in this plan as a runtime event stream or a tracked report。

**Failure owner:** a focused failure returns to the POA task that owns the affected contract。A cross-task integration
failure is owned by the integration fixer。A knowledge-only failure is owned by POA-7。A Git index / tree invariant failure
returns to POA-5 or POA-6。A publication failure stops at POA-8 while preserving local readiness。A material spec conflict alone
returns one decision request to Human; capability / authority / binding failure returns `blocked` with no decision request。

## Coverage Matrix

### Requirements

| ID | Primary task | Contributing task | Planned evidence |
|---|---|---|---|
| R-01 | POA-2 | POA-3 | approval-boundary contract and route tests |
| R-02 | POA-2 | POA-1, POA-3 | no-plan-approval contract and prohibited-language regression |
| R-03 | POA-2 | POA-3 | material-conflict-only decision routing |
| R-04 | POA-2 | POA-3, POA-8 | action-specific authorization isolation regression and authorized-push last gate |
| R-05 | POA-2 | POA-1, POA-3 | author / reviewer / repair ownership and isolation tests |
| R-06 | POA-2 | POA-1, POA-3 | required task-field fixture and contract checks |
| R-07 | POA-2 | POA-1, POA-3 | full coverage matrix validation with primary / contributing ownership |
| R-08 | POA-2 | POA-1, POA-3 | acyclic graph and topological-order validation |
| R-09 | POA-2 | POA-1, POA-3 | distinct execution / serialized integration schema and flow |
| R-10 | POA-2 | POA-1, POA-3 | combined-verification scope / criteria / evidence / owner checks |
| R-11 | POA-2 | POA-1, POA-3 | prohibited-body regression and artifact inspection |
| R-12 | POA-2 | POA-1, POA-3 | method metadata remains agent-owned and non-Human checkpoint |
| R-13 | POA-2 | POA-1, POA-3 | external upstream dependency and methodology preservation |
| R-14 | POA-2 | POA-1, POA-3 | explicit local precedence without upstream copy |
| R-15 | POA-2 | POA-1, POA-3 | portable Inputs / Outputs / Capabilities and fail-closed tests |
| R-16 | POA-5 | POA-4, POA-7 | all-stage repository-external handoff migration and canonical supersession sync |
| R-17 | POA-5 | POA-4, POA-6 | concrete-reason and pre-write ignore gate with retained local scratch evidence |
| R-18 | POA-5 | POA-4, POA-6, POA-8 | index / candidate / new-tree validator and final reachability inspection |
| R-19 | POA-7 | POA-4, POA-5, POA-6 | canonical-only durable summary and append-only closeout without raw artifacts |
| R-20 | POA-5 | POA-4, POA-6, POA-8 | focused repository validation semantics and actual-tree enforcement |
| R-21 | POA-6 | POA-4, POA-7, POA-8 | exact three-report final-tree removal with optional ignored local copies |

### Acceptance Criteria

| ID | Primary task | Contributing task | Planned evidence |
|---|---|---|---|
| AC-01 | POA-2 | POA-3 | only North Star / Written Spec approval checkpoints remain |
| AC-02 | POA-2 | POA-1, POA-3 | no Human method-choice or prospective-code judgement route |
| AC-03 | POA-2 | POA-1, POA-3 | independent review and `ready`-only stage entry |
| AC-04 | POA-2 | POA-1, POA-3 | exact task-to-requirement / acceptance trace with primary owners |
| AC-05 | POA-2 | POA-1, POA-3 | unassigned / orphan / undefined dependency rejection |
| AC-06 | POA-2 | POA-1, POA-3 | graph、execution order、serialized integration consistency |
| AC-07 | POA-2 | POA-1, POA-3 | integrated-state verification covers every acceptance |
| AC-08 | POA-2 | POA-1, POA-3 | prohibited prospective body checks |
| AC-09 | POA-2 | POA-1, POA-3 | agent repair loop never becomes a Human plan question |
| AC-10 | POA-2 | POA-1, POA-3 | deterministic `needs_decision` / `blocked` distinction |
| AC-11 | POA-2 | POA-1, POA-3 | upstream required, local output / routing precedence |
| AC-12 | POA-2 | POA-1, POA-3 | portable contract、binding、knowledge sync、fail closed |
| AC-13 | POA-2 | POA-3, POA-8 | remote / privileged / destructive isolation and authorized-push last gate |
| AC-14 | POA-3 | POA-1, POA-2 | fresh focused、architecture、authoring、knowledge validation |
| AC-15 | POA-5 | POA-4, POA-7 | all normal stages use bounded repository-external transient handoff |
| AC-16 | POA-5 | POA-4, POA-6 | repository-local scratch requires reason and mechanical ignore coverage |
| AC-17 | POA-5 | POA-4, POA-6, POA-8 | zero index / candidate / new / final-tree entries with allowed scratch and staged deletion |
| AC-18 | POA-7 | POA-4, POA-5, POA-6 | canonical spec / plan / log synthesis without tracked raw duplicate |
| AC-19 | POA-6 | POA-4, POA-7, POA-8 | exact R-21 report removal without destructive local-copy deletion |
| AC-20 | POA-8 | POA-4, POA-5, POA-6, POA-7 | fresh focused / repository / tree / knowledge verification and final review |

Coverage result: requirements `21/21` primary-owned、acceptance criteria `20/20` primary-owned、unassigned `0`、
orphan task `0`、unknown ID `0`。

## Historical Amendment Follow-up Readiness

このsectionはPOA-4 entry前のreadiness / single-use bootstrap stateをhistorical evidenceとして保持する。
current implementation stateは下記Implementation Closeoutを正本とし、exceptionはconsume済みで再利用できない。

- Plan repair disposition: independently_reviewed_ready
- Prior Independent Plan Review: issues_found / needs_repair
- Fresh Independent Plan Re-review: ready
- Current executable plan-check state: passed_with_bounded_schema_transition_red
- Single-use migration precheck: passed_at_f07aebce7bbf854cd64184311d204cf04055fd28
- Single-use migration exception: available_unconsumed_ready
- Follow-up Implementation Stage entry: allowed_after_atomic_single_use_entry_consumption
- Decision requests: none

The prior fresh independent Plan Re-review found one remaining agent-repairable circularity: current semantic GREEN required
POA-4's schema / fixture transition while POA-4 entry required current semantic GREEN。This round repairs that transition with
the Single-use Amendment Migration Entry。The pre-entry check is bound to exact commit
`f07aebce7bbf854cd64184311d204cf04055fd28`、the three named mode / blob / path entries、existing ignore coverage、zero
index delta、and explicit POA-4 / POA-5 / POA-6 ownership。Any additional or changed path、staged delta、baseline drift、or
reuse fails closed。

The current executable validator remains intentionally RED because its implemented inventory and fixture stop at
R-01〜R-15、AC-01〜AC-14、POA-1〜POA-3 while the amended canonical plan truthfully declares the approved new schema。
Fresh independent re-review classified that exact schema-transition RED as the allowed pre-entry input owned by POA-4 and
returned `ready`; it does not require POA-6 final cleanup before Implementation entry。Agent-owned readiness finalization has
therefore marked the formal binding `ready` / `passed` / `current`。The Controller may now atomically reverify and consume the
exception at POA-4 entry。Successful repository checks mean the bounded migration precheck plus no unexpected failures, not
premature POA-4 schema GREEN or POA-6 final-tree cleanup。No Human decision request is created。

## Durable Amendment Plan Review Evidence

- review date / stage: 2026-08-14、round-2 repair後のfresh independent Plan Re-review。
- reviewed identities: Human-approved amendmentを含む
  `knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md`と、本canonical plan。raw reviewer transcriptは
  repository外の`/private/tmp`に留め、durable artifactまたはfuture cloneから読めるprovenanceとは扱わない。
  transcript integrity fingerprintはSHA-256
  `f4fcb520361c7aaf191aa7c547980e3b9c72983f7575b1b90218e841d9a219f6`である。
- verdict: `ready`。repository readiness classificationは`ready`、decision requestは`none`、material riskは
  `none`。このverdictとformal finalizationはsingle-use exceptionをまだconsumeせず、candidate / final-tree acceptance、
  implementation完了、`LOCAL_COMPLETE`、publicationを宣言しない。
- exact migration baseline: `HEAD` / immutable migration baselineは
  `f07aebce7bbf854cd64184311d204cf04055fd28`で、repository baseline
  `c370fe14de1641aa5ee30b3fa001f4d857078091`はancestorである。baseline treeとcurrent indexの
  `.superpowers/**` tracked setは次の3 entryだけでmode / blob / pathが一致する。
  - `100644 b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1 .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/approved-residual-fix-report.md`
  - `100644 c884197bf566cc93f319f3c2a1b6d2ad1563d10e .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/final-fix-report.md`
  - `100644 da22b7580961fb9a2087ab1eb034fb34000711f8 .superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/task-2-report.md`
- path / ignore evidence: global staged deltaと`.superpowers/**` worktree deltaはzeroであり、additional tracked、
  newly staged、changed、renamed、intent-to-add、またはadditional unignored pathはない。root `.gitignore` line 1の
  `.superpowers/`は`git check-ignore --no-index`で上記3 pathとoptional local scratchをcoverする。既存のadditional
  ignored / untracked / unstaged / uncommitted local scratchはmigration baseline setに含めず、許容状態のまま保持する。
- ownership / order: POA-4がshared semantic validator、R-01〜R-21 / AC-01〜AC-20 / POA-1〜POA-8
  representative fixture parity、amended RED contractを所有する。POA-5がall-stage destination migration、repository
  validator、CI GREENを所有し、POA-6が上記3 entryだけのnon-destructive cleanupを所有する。I-4、I-5、I-6が
  この順に直列化し、ownerを跨ぐ変更を許さない。
- executable review evidence: current `skills/sdd-implementation/tests` 81件は80件passし、1件だけがformal pending
  fields 6件とapproved amended inventory / coverage / graph / order schema transition 82件、計88 findingで意図どおり
  failした。formal fieldsをfresh-readyへ置換し、validator inventoryをR-01〜R-21 / AC-01〜AC-20 / POA-1〜POA-8へ
  in-memory expansionした同じcanonical planはvalidator error zeroとなり、他のdiscovery、syntax、baseline、approved
  identity、prohibited content、original schema、fixture、unrelated regression failureはなかった。formal finalization後の
  fresh 81-test rerunも80 pass / 1 intentional failureで、findingはamended schema transition 82件だけに縮退した。
- final-zero invariant: exceptionが許すのはPOA-4 / POA-5 pre-cleanup commit treeによるexact 3 entryのunchanged
  inheritanceだけである。POA-6のI-6 candidate treeは`.superpowers/**` entry zeroにし、I-6以後のすべてのnew commit
  treeとPR final treeもzeroを維持する。ignored local scratchとcandidate treeがzeroのstaged deletionは許可するが、
  additional、changed、renamed、newly staged、reintroduced entry、baseline drift、retry / reuseはfail closedとする。

## Amendment Implementation Closeout

- **POA-5 reviewed GREEN:** `c7aced8d7b3975f081ec8bfcd065dcaa57bb2eec`、
  `91cbd5aec3d062f534937953ee8241f415d8db33`、
  `29dc0de8f5f721d5004e5dac253ae04a36899aad`がall-stage repository-external handoff、local scratch
  reason / ignore gate、fail-closed Git surface validator、CI integrationをlandさせた。independent scoped re-reviewは
  `ready`で、POA-4 RED contractをGREENにした。
- **POA-6 reviewed cleanup:** `7b4a8e6e0951e2ddd3c6020a10e00a6afe604b60`がR-21 exact three-report
  entriesとsingle-use migration markerを同じcleanup treeから除いた。`74eb79a3fbb0da2d6521129cf83976a366877af4`
  はauthorized migration repository fixtureをcleanup前のintroduction commitへanchorし、cleanup後HEADからの
  historical fixture executionを修復した。scoped re-reviewはcleanup / correctionを`ready`とした。
- **Actual Git state:** POA-7 entry時のcurrent indexとHEAD treeは`.superpowers/**` entry zeroである。R-21の
  3 working-tree copiesはroot `.gitignore`によりignored / untrackedであり、destructive deletionしていない。
  baseline `f07aebce7bbf854cd64184311d204cf04055fd28`はancestorとしてreachableで、historical blobsを
  rewriteしていない。
- **Fresh evidence:** SDD focused suite `93/93`、transient validator regression `22/22`、actual candidate tree、
  post-cleanup commit trees `7b4a8e6` / `74eb79a`、HEAD final treeのrepository validatorがpassした。raw reports、
  review transcripts、test logsはdurable surfaceへcopyしていない。
- **Lifecycle status:** POA-1〜POA-8のlocal workはreviewed / completeで、本planは`LOCAL_COMPLETE`である。
  authorized non-force remote branch updateはpending / unpublishedで、merge、release、live installは未承認である。

## Final Local Closeout

- **Fresh combined verification:** evidence tip `e18088893737099d45e446e06a476c68c79ea25f`でSDD `93/93`、
  scripts `46/46`、llm-wiki `21/21`、decide-in-order `7/7`、task-management `11/11`がpassした。skill architecture、
  skill context、warning-free context report (`warnings: []`)、skill-creator、transient-artifact、complete diff checksもpassした。
- **Git boundary:** current candidate / final treeの`.superpowers/**` entryはzeroで、cleanup後の全commit historyをCIが
  validatorへ渡す。R-21の3 local copiesはignored / untrackedのまま保持し、baseline
  `f07aebce7bbf854cd64184311d204cf04055fd28`とpre-amendment ancestor historyをrewriteしていない。
- **Whole-branch review:** fixed point `c370fe14de1641aa5ee30b3fa001f4d857078091`からのcanonical reviewは、Spec
  ImportantのCI intermediate-commit detection gapとStandards Minorのduplicate responsibility rowを検出した。bounded
  fix `bbfd06eecf2fec0e45697257b3edf545fecdb4b6`が両方を修正し、Spec scoped re-reviewは`READY`となった。
  append-only evidence correction `e18088893737099d45e446e06a476c68c79ea25f`が残るStandards log findingを解消し、
  final Standards verdictも`READY`となった。
- **Disposition:** POA-1〜POA-8のlocal execution / review / durable evidenceはcompleteで、`LOCAL_COMPLETE`である。
  authorized non-force integration-branch updateはまだ実行していない。publication、merge、release、live installを
  このlocal dispositionから推論しない。

## Readiness Result

- Plan readiness disposition: ready
- Control Return status: complete
- Implementation Stage entry: allowed
- Implementation Stage execution: completed through POA-8 local gates
- Content integration and final review: complete
- Local disposition: LOCAL_COMPLETE
- Remaining remote action: authorized non-force branch update; pending / unpublished

| Internal disposition | External Control Return | Implementation entry | Owner / next route |
|---|---|---|---|
| `ready` | `status: complete`; plan path; no decision request; no material risk | allowed after Controller verifies current spec binding and readiness evidence | Planning Controller passes the reviewed plan to Implementation Stage |
| `needs_repair` | no external return | forbidden | agent repairs exact deficiency and obtains independent re-review |
| `needs_decision` | `status: needs_decision`; one material decision; conflict and impact | forbidden | Spec Stage / Human authority resolves North Star or Written Spec conflict |
| `blocked` | `status: blocked`; no decision request; exact blocker | forbidden | capability、trusted binding、authority、write-boundary failure must be cleared |

Reviewer `issues_found` is not an external status。It must be classified into `needs_repair`、`needs_decision`、or
`blocked`。Remote authorization absence is none of these for Plan Readiness; it is evaluated only at the affected action。

The pre-entry reviewer verdict and agent-owned formal disposition remain `ready`; the Controller consumed the exact
baseline-bound exception once and entered POA-4 without creating a Human decision request。POA-4〜POA-8 local gates are
reviewed and complete。The POA-6 cleanup tree and every later commit tree remain `.superpowers/**` entry zero, and the
exception cannot be reused。`LOCAL_COMPLETE` does not authorize publication; the non-force remote branch update remains a
separate pending action。

## Plan Author Self-Review

- Spec coverage: pass。Every `R-01`〜`R-21` and `AC-01`〜`AC-20` has exactly one primary task and at least one planned evidence class。
- Task boundaries: pass。Each task has an independently reviewable deliverable and its own failure owner。
- Placeholder scan: pass。No deferred implementation placeholder or instruction to infer unspecified behavior remains。
- Interface consistency: pass。POA-2 consumes POA-1's original reviewed RED; POA-4 owns the amended shared-validator /
  representative-fixture transition and creates only the declared amendment RED; POA-5 owns only migration / validator /
  CI GREEN implementation; POA-6 consumes that enforcement for exact cleanup; POA-7 consumes actual landed
  evidence; POA-8 consumes every reviewed local result。No task requires an undefined predecessor output。
- Dependency / order consistency: pass。The graph is acyclic and execution / integration orders both respect it while remaining separately specified。
- Prohibited-body scan: pass。This plan contains no prospective production code、test code、script body、patch body、pseudo-patch、shell commit command、or Human execution-choice prompt。
- Scope check: pass。The plan adds only the amended SDD transient destination contract、repository validator / CI
  integration、exact tracked-report cleanup、required durable synchronization、fresh review / authorized branch update。It
  does not create a scheduler、runtime state、packet、event log、resume protocol、upstream fork、replacement raw-report store、
  PR、merge、release、or live install。
- Current-tree applicability: pass。At authoring / POA-4 entry, the migration baseline
  `f07aebce7bbf854cd64184311d204cf04055fd28` contained exactly the three declared path / blob entries with zero staged
  delta and root `.gitignore` coverage。That single-use precheck was consumed。Current POA-7 closeout evidence instead shows
  zero `.superpowers/**` entries in the Git index / HEAD tree、the three optional local copies ignored / untracked、and
  repository baseline `c370fe14de1641aa5ee30b3fa001f4d857078091` plus migration baseline still reachable as ancestors。
- History safety: pass。No task rewrites pre-amendment commits or removes ancestor blobs。Only cleanup後index / candidate /
  new / final-tree entries are prohibited, and publication is non-force after ancestry verification。
- Repair / re-review verdict: `independently_reviewed_ready`。The original POA-1〜POA-3 plan review / execution
  evidence remains historical and unchanged。The amended POA-4 entry used the independently reviewed non-circular、single-use、
  exact baseline-bound route; POA-5 GREENとPOA-6 zero-tree cleanup / fixture correctionはscoped reviewをpassしてlandedした。
  POA-7 closeout / lifecycle correctionもfresh scoped re-reviewでprior Important 2件の解消と新規Critical / Important
  なしを確認し、reviewed / landedとなった。POA-8 combined verification / whole-branch review / bounded fix / scoped
  re-reviewsも完了し、local dispositionは`LOCAL_COMPLETE`である。remote publicationはdistinct pending actionである。

## Related Pages

- [[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]] — requirement、acceptance、authority boundary の binding source。
- [[sdd-implementation-skill-design|SDD Implementation Skill 設計]] — broader current lifecycle contract。
- [[sdd-preimplementation-context-isolation-spec|SDD 実装前コンテキスト分離仕様]] — Planning Controller / fresh worker boundary の current source。
