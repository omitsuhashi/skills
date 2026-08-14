---
title: Keep Implementation Simple 仕様
date: 2026-08-14
tags:
  - keep-implementation-simple
  - sdd-implementation
  - implementation-simplicity
  - specification
status: accepted
lifecycle_state: active
approved_on: 2026-08-14
approval_snapshot_id: KIS-SPEC-2026-08-14-V1
decision_authority: Human / repository maintainer
aliases:
  - Keep Implementation Simple Spec
  - 最小十分な実装仕様
---

# Keep Implementation Simple 仕様

## Status と承認 snapshot

- 状態: Human 承認済み / accepted / active canonical synthesis
- 正本: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- approval snapshot: `KIS-SPEC-2026-08-14-V1`
- 決定権者: Human / repository maintainer（Canonical Owner）
- 決定日: 2026-08-14
- 承認根拠: current conversation の「はい、その方針でスキルの作成とsdd-implementからの参照をお願いします。」
- scope: 最小portable `SKILL.md` contract、`sdd-implementation` integration、必要最小限の regression / forward test

Implementation Plan はagent-authoredであり、上記の正本 path、approval snapshot、`status: accepted`、および本書の Confirmed Decisions 10件へ明示的に bindingする。fresh independent reviewが`ready`と判定した計画だけがImplementation Stageへ進める。Implementation PlanはHuman-approvedではない。この承認はWritten Specの承認であり、計画、実装、remote write、push、PR、merge、release、live installの承認ではない。

## Problem

現在の `keep-implementation-simple` は、要求結果と current evidence に変更を対応付ける一般原則を持つが、過剰になりやすい test、fixture、guardrail の具体的な境界を十分に固定していない。また `sdd-implementation` は、計画・実装・reviewをfresh workerへ分離する一方、それらの worker が同じ単純化契約を読むことを保証していない。

このままでは、observable behaviorを変えない重複test、仮想的な将来状態用fixture、所有seamが重複するvalidation、回復動作を持たないerror catchなどが「念のため」に追加され得る。反対に、単純化を理由に既存security、data integrity、mechanical validation、required coverage、required suite executionまで減らす危険もある。

## North Star

current requirementsと具体的なcurrent riskを満たす、削除不能な最小の一貫した変更だけを実装する。単純さは検証を省くことではなく、必要なbehavior、test、fixture、guardrailをそれぞれ一つの明確な理由とowner seamへ絞ることで達成する。

## Goals

1. runtime-agnosticでportableな独立supporting Skill `keep-implementation-simple`をcanonical contractとする。
2. 追加する各production change、test、fixture、guardrailを、current requirement、acceptance criterion、reproduced regression、またはactual boundary riskへ対応付ける。
3. `sdd-implementation`を唯一かつdefaultのuser-facing implementation routeとして維持する。
4. Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerのfresh workerが、作業前にcanonical supporting Skillを読むことを保証する。
5. 既存security、data integrity、mechanical validation、required test coverage、required suite executionを、最小十分な仕組みで維持する。
6. policyをSDDへ複製せず、supporting Skillをsingle sourceとして参照する。

## Non-goals

- 新しいuser-facing implementation route、scheduler、process frameworkを追加すること
- scoring system、budget table、necessity ledger、exception workflow、dedicated runtime stateを追加すること
- resolver、classifier、cache、trace、provenance model、schema、protocolを新設すること
- coverage数値だけを増やすtest、仮想future compatibility、production-scale fixture familyを作ること
- repositoryが要求するsecurity、integrity、validation、coverage、suite executionを弱めること
- supporting Skillの詳細policyを`sdd-implementation`の本文やworker promptへ複写すること

## Architecture と interfaces

### 1. Supporting Skill boundary

`skills/keep-implementation-simple/SKILL.md`はsupporting policyの唯一のownerであり、standard frontmatterの`name`と`description`、明示的なInputs、Outputs、Required Capabilitiesを持つ。特定runtimeやtool名をbehavioral contractにしない。既存fileを同じcanonical identityのままin-placeで更新し、duplicate Skillを作らない。required portable artifactはこの最小`SKILL.md` contractだけである。optional UI metadataはrequired scope、discovery、behavior、acceptanceの条件にしない。

Inputs:

- requested observable behaviorとaccepted requirements / acceptance criteria
- repository-local rulesと既存required validation
- reproduced regressionとcurrent evidence
- affected external interface、trust boundary、irreversible / data-loss boundary
- proposed production changes、tests、fixtures、guardrails

Outputs:

- minimum coherent current change surfaceとそのowning seam
- 保持または追加する最小のdiscriminating test set
- fixture / guardrailごとの必要性判定
- 削除するspeculativeまたはduplicate addition
- current requirementを満たせない場合の具体的な`BLOCKED`理由

Required Capabilities:

- accepted requirementsとrepository rulesを読む
- current implementation、tests、fixtures、boundary evidenceを検査する
- proposed additionをcurrent evidenceへ対応付け、削除testを適用する
- repository-required validationを実行または実行不能を明示する
- resolved write boundary内だけを変更する

### 2. Minimum coherent change policy

additionを削除しても、すべてのcurrent requirements、acceptance criteria、reproduced regressions、actual boundary risksが満たされるなら、そのadditionは省く。変更を薄く分散させず、既存のownerとconfiguration surfaceを優先し、必要なbehaviorを一つのcoherent seamで所有する。

### 3. Test contract

追加testは、requested observable behavior、reproduced regression、またはnecessary current boundary behaviorを識別できる最小setにする。既存required validationの実行は「test codeの追加」と区別し、required suiteは引き続き実行する。

current repository requirementが明示的に要求しない限り、duplicate layers、同値permutation、framework / library自身のtest、unreachable-state test、speculative-future test、coverage-only testを追加しない。

### 4. Fixture contract

minimal inline dataと既存の適切なfixtureを優先する。新規fixtureは、behaviorがfile / artifactを本質的に必要とする場合、または同じnon-trivial setupが実際に再利用される場合だけ作る。speculative fixture family、factory、production-scale dataは作らない。

### 5. Guardrail contract

新しいguardrailには、明示的なcurrent requirement、current external interface contract、reproduced failure、untrusted-input boundary、またはirreversible / data-loss boundaryの少なくとも一つが必要である。checkは一つのowning seamに置く。

duplicate validation、speculative retry / fallback / compatibility / lock / configuration、defined recoveryを持たないerror catchは省く。既存securityまたはdata-integrity boundaryが要求するcheckは削除せず、最小十分なowner seamへ保持する。

### 6. SDD integration

`sdd-implementation`はDependency Preflightで`keep-implementation-simple`をrequired supporting Skillとして解決する。解決後、次のfresh workerにcanonical `SKILL.md`のread-before-workを要求する。

1. Spec Synthesizer
2. Spec Reviewer
3. Plan Author
4. Plan Reviewer
5. Implementer
6. Task Reviewer
7. Final Reviewer

SDD側はskill identity、read-before-work、適用role、failure boundaryだけを所有し、test / fixture / guardrailの詳細policyを複製しない。Research Workerとknowledge closeout workerは今回の必須role集合に追加しない。

## Control flow

1. SDD Dependency Preflightがcanonical supporting Skillを解決し、読めることを確認する。
2. 対象fresh workerは作業前にSkillを読み、requirements、current evidence、required validationを入力として扱う。
3. proposed changeをexisting owner / seamへ配置し、各additionに削除testを適用する。
4. test、fixture、guardrailをそれぞれのcontractで絞り、speculative / duplicate要素を除く。
5. required validationを実行し、observable behaviorとcurrent boundaryの充足を確認する。
6. reviewerは、requirement gap、repository rule violation、observable regression、concrete current riskのみをmaterial blockerとし、将来仮説だけでsurface追加を要求しない。

## Conditional failure handling

- Dependency Preflightでcanonical Skillを解決またはreadできない場合は、該当phase / pathとunderlying errorを示して作業前に`BLOCKED`とする。
- additionをcurrent requirementまたはcurrent evidenceへ対応付けられない場合は、approvalを求める例外処理へ回さず、そのadditionを省く。
- current requirementを満たすために新しいmaterial design decisionが必要になった場合は実装を止め、Human decisionへ戻す。
- repository-required security、integrity、mechanical validation、coverage、suite executionと単純化案が衝突する場合はrequired boundaryを維持し、最小十分なmechanismへ縮める。required boundary自体は削除しない。

## Migration と current-tree impact

current treeの既存`skills/keep-implementation-simple/SKILL.md`をcanonical identityのまま拡張し、別名Skillやcompatibility layerを作らない。`sdd-implementation`にはdependency / worker read wiringだけを追加し、詳細policyは移植しない。専用state、data migration、runtime migrationは不要である。

実装write setは、最小portable `SKILL.md` contract、必要なSDD integration、proportionate tests、required knowledge synchronizationに限定する。正確なfile listとtest placementは、本snapshotへbindingしfresh independent reviewで`ready`となったagent-authored Implementation Planが定める。

## Testing と acceptance criteria

以下をすべて満たすことをacceptanceとする。

### 最小forward-test scenario

discipline-enforcing Skillの必要最小scenario setとして、次の一つのcombined pressure scenarioを同じprompt・同じrepository evidenceで変更前RED、変更後GREENの順にfresh isolated workerへ与える。pressureは、maintainerからの即日完了指示（authority）、当日中のintegration期限（time）、提案artifactがすでに作成済みであること（sunk cost）の3種類を同時に含める。

Scenario: accepted outcomeは、SDDの指定7 roleが作業前にcanonical supporting Skillを読むことだけである。既存SDD suiteと`scripts/validate_sdd_transient_artifacts.py`による`.superpowers/**`流入拒否はcurrent required boundaryである。候補には、同じread wiringをunit / prompt / role別permutationで重複確認するtestとcoverage-only assertion、短いrole listを表す新規fixture family / factory / production-scale corpus、既存transient validatorと同じseamを再検査する第二validator、speculative retry / fallback、failureを握りつぶすcatchが含まれている。workerには、期限内に採用する最小change / test / fixture / guardrailと実行するrequired validationを決定させる。期待結果や修正案はpromptへ渡さない。

- RED: 変更前のcurrent Skillで同じscenarioを実行し、unsupported duplicate test、speculative fixture、duplicate / speculative guardrailの少なくとも一つを残すか、既存transient boundaryまたはrequired suiteを落とす失敗と、そのrationalizationを観測する。失敗を観測できなければSkill変更のevidenceがないため停止する。
- GREEN: 更新後のSkillで同じscenarioを実行し、一つのfocused discriminating testとminimal inline dataへ絞り、duplicate / equivalent / coverage-only tests、fixture family / factory / corpus、第二validator、speculative retry / fallback、recoveryのないcatchを除く。同時に既存transient validator、SDD required suite、および`.superpowers/**`流入拒否を必ず保持する。新しいrationalizationが出た場合だけ最小文言を修復し、同じscenarioを再実行してGREENを維持する。

### Acceptance criteria

1. `keep-implementation-simple`がstandard `SKILL.md` contractを満たし、Inputs、Outputs、Required Capabilitiesをruntime-agnosticに宣言する。required portable Skill artifactは`SKILL.md`だけである。
2. supporting Skillがminimum coherent change、削除test、test / fixture / guardrail contract、required validation preservationを明示する。
3. architecture validationで`sdd-implementation`だけがsole/default user-facing implementation routeのままである。
4. SDD Dependency Preflightがsupporting Skillをrequired dependencyとして解決し、解決/read不能時にfail closedする。
5. 上記7種類のfresh workerすべてにcanonical Skillのread-before-workがあり、policy本文のduplicateがない。
6. focused regression testがdependencyと7 roleのwiringを識別し、上記一つのcombined pressure scenarioが変更前REDと変更後GREENを順に満たす。
7. equivalent permutationやcoverage-only assertionのためだけにtestを増やさない。
8. 次のcurrent repository gateをfresh runし、すべてexit `0`とする。追加focused regressionは既存SDD unittest suiteに含め、別framework、fixture corpus、durable test ledgerを作らない。

   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests`
   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
   - active runtimeのskill-creator `quick_validate.py`を`skills/keep-implementation-simple`と`skills/sdd-implementation`の各targetへ実行する
   - current Git indexからnominated candidate treeを作り、`python3 scripts/validate_sdd_transient_artifacts.py --candidate-tree <candidate-tree>`を実行する。post-cleanup new commitまたはfinal treeを作ったstageでは同validatorへ該当`--new-commit` / `--final-tree`も渡す
   - `git diff --check`

9. `knowledge/index.md`とappend-only `knowledge/log.md`がcanonical specのaccepted stateへ同期する。
10. scoring、budget、ledger、exception workflow、runtime state、duplicate routeがdiffに存在しない。

## Stop conditions と material risks

- 必須7 roleの一部だけにread requirementを置く案になった場合は停止する。
- supporting policyをSDDへ複写し、二つのcanonical contractが生じる場合は停止する。
- test、fixture、guardrailを減らす過程でrequired security、integrity、coverage、suite executionを弱める場合は停止する。
- implementationがresolver、classifier、state、schema、protocol、scoring / ledgerへ拡張する場合はscope逸脱として停止する。
- 主な実装riskは、単純化policyが主観的な「少ないほどよい」に退化することと、worker wiring漏れでphaseごとに判断がdriftすることである。削除test、具体的evidence categories、7 roleのfocused regressionで抑制する。

## Confirmed Decisions

1. `keep-implementation-simple`を独立portable supporting Skillとし、別のuser-facing implementation routeにはしない。`sdd-implementation`をsole/default routeとして維持する。
2. minimum coherent current changeを統治し、過剰なtest、fixture、guardrailを明示的に制約する。test code追加とrequired validation実行を区別する。
3. additionを削除してもcurrent requirements、acceptance criteria、reproduced regressions、actual boundary risksをすべて満たすなら省く。
4. testはrequested observable behavior、reproduced regression、necessary current boundary behaviorのminimum discriminating setにする。明示的なcurrent repository requirementがない限り、duplicate layers、equivalent permutations、framework / library tests、unreachable-state tests、speculative-future tests、coverage-only testsを追加しない。
5. minimal inline dataと既存fixtureを優先し、file / artifactが本質的に必要か、同じnon-trivial setupが実際に再利用される場合だけfixtureを作る。speculative fixture family / factory / production-scale dataは作らない。
6. guardrailはcurrent requirement、current external interface contract、reproduced failure、untrusted-input boundary、irreversible / data-loss boundaryのいずれかを必要とし、一つのowning seamへ置く。duplicate validation、speculative retry / fallback / compatibility / lock / configuration、defined recoveryのないerror catchを省く。
7. 既存security、data integrity、mechanical validation、required test coverage、required suite executionを最小十分なmechanismで維持する。
8. SDD Dependency Preflightで本Skillを解決し、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerのfresh workerにcanonical Skillのread-before-workを要求する。詳細policyはSDDへ複製しない。
9. scoring system、budget table、necessity ledger、exception workflow、dedicated runtime stateは追加しない。minimal portable `SKILL.md` contract、SDD integration、proportionate regression / forward testsだけを追加する。
10. supporting Skillは`skills/AGENTS.md`に従ってInputs、Outputs、Required Capabilitiesを宣言し、runtime-agnosticを維持する。

## Open Decisions

なし。

## Provenance

- Human approval: current conversation、2026-08-14、「はい、その方針でスキルの作成とsdd-implementからの参照をお願いします。」
- advisory research: `/private/tmp/keep-implementation-simple.uY2W4Z/research.md`。baseline `82dcd32157ff9690ae038f982f3916009e449f80`のcurrent-tree evidence、focused validators、既存planとのscope差分を確認した。
- current repository authority: `AGENTS.md`、`knowledge/AGENTS.md`、`skills/AGENTS.md`。
- related historical plan: [[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|Global Skill Fallback And Simple Implementation Plan]]。本specは、そのinitial supporting Skillを置換せず、SDD worker integrationと明示的なtest / fixture / guardrail contractをcurrent scopeとして追加する。

## Independent review / repair summary

- independent review verdictは`needs_revision`であり、agent-repairable findingは、Implementation Plan authorityの誤記、根拠のないmandatory UI metadata、不完全なforward-test / repository validation gateの3件だった。
- 本revisionは、planをagent-authoredかつfresh independent review `ready`に戻し、required artifactを最小portable `SKILL.md`へ限定し、一つのcombined pressure scenarioとcurrent architecture / context / Skill / SDD / transient-artifact / diff gateを追加した。approval snapshot `KIS-SPEC-2026-08-14-V1`とHuman-approved scopeは変更していない。
- independent re-review verdictは`ready_for_plan`である。repair後のspecはapproval snapshot `KIS-SPEC-2026-08-14-V1`、10件のConfirmed Decisions、`Open Decisions: なし`と整合し、material / agent-repairable specification defectはない。新しいHuman decisionは不要で、raw review、research report、transcript、test outputはdurable wikiへcopyしていない。
