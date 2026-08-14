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
approval_snapshot_id: KIS-SPEC-2026-08-14-V2
supersedes: KIS-SPEC-2026-08-14-V1
baseline_sha: 82dcd32157ff9690ae038f982f3916009e449f80
decision_authority: Human / repository maintainer
aliases:
  - Keep Implementation Simple Spec
  - 最小十分な実装仕様
---

# Keep Implementation Simple 仕様

## Status と snapshot binding

- 状態: Human承認済み / accepted / active canonical synthesis
- 正本: `knowledge/wiki/syntheses/keep-implementation-simple-spec.md`
- approval snapshot: `KIS-SPEC-2026-08-14-V2`
- repository baseline: `82dcd32157ff9690ae038f982f3916009e449f80`
- 決定権者: Human / repository maintainer（Canonical Owner）
- 決定日: 2026-08-14
- scope: 既存`keep-implementation-simple`を変更せず、`sdd-implementation`だけへ指定7 roleのcanonical Skill read-before-workを追加する

本V2はV1の有用な履歴を保持しつつ、実装authorityを置き換える。V1のうち`keep-implementation-simple`本文の拡張、behavioral RED/GREENを前提にしたSkill edit、およびtest / fixture / guardrail policyの追加はsupersededであり、実装してはならない。既存V1-bound Implementation Planは本V2へbindingしていないため、再author・fresh independent reviewで`ready`になるまでImplementation Stageへ進めない。

この承認はWritten Specだけを対象とし、Implementation Plan、実装、remote write、push、PR、merge、release、live installを承認しない。

## Problem

baselineでは`skills/keep-implementation-simple/SKILL.md`がすでに、observable outcomeの再記述、最小owner / surfaceの選択、追加concept / artifactのacceptance criteriaまたはcurrent evidenceへのmapping、instruction-only問題でのtest-only runtime回避、単純案が失敗した後だけのarchitecture拡張、material blockerの限定を定義している。

同一scenarioによるfresh isolated evaluationでは、no-guidance controlが5/5 GREEN、変更前の現行Skillも5/5 GREENで、両方ともrequired validationを5/5保持した。現行Skillを編集するために必要なREDは成立していない。一方、`sdd-implementation`は、そのcanonical Skillを指定7 roleへ渡し、作業前の全文readを要求するcontractをまだ持たない。

## North Star

既にGREENなsimplicity policyは変更せず、SDDの既存dependency / dispatch surfaceだけを使って、指定7 roleが同じcanonical Skillを作業前に全文readすることを最小変更で保証する。

## Goals

1. `skills/keep-implementation-simple/SKILL.md`をbaseline byte contentのまま維持する。
2. `sdd-implementation`のDependency Preflightで、active runtimeの既存discovery / global-root fallbackにより一つのcanonical `keep-implementation-simple/SKILL.md` pathをresolveして全文readする。
3. 同じresolved pathと「作業前に全文readする」instructionを、正確に7種類のfresh workerへ既存surfaceから渡す。
4. 一つのfocused regressionとcurrent required validationでcontractを証明する。
5. `sdd-implementation`をsole/default user-facing implementation routeとして維持する。

## Non-goals

- `skills/keep-implementation-simple/SKILL.md`、そのmetadata、またはsupporting policyを変更すること
- Research Workerまたはknowledge closeout workerへ本requirementを追加すること
- 新しいprompt file、fixture、fixture family、corpus、test-only runtime、validatorを作ること
- resolver、classifier、cache、trace、provenance model、schema、protocol、scheduler、retry / fallback、dedicated runtime stateを追加すること
- optional metadata、alias Skill、duplicate route、compatibility layerを追加すること
- `keep-implementation-simple`のpolicy本文を`sdd-implementation`またはworker promptへ複写すること
- current security、data integrity、mechanical validation、required coverage、required suite、transient-artifact rejectionを弱めること

## Requirements

### R-01: Canonical Skillは変更しない

`skills/keep-implementation-simple/SKILL.md`はbaseline `82dcd32157ff9690ae038f982f3916009e449f80`のcontentとbyte-for-byte同一に保つ。supporting policyのownerは同fileのままであり、SDD側はそのpolicyを再定義しない。

### R-02: Dependency Preflightで一つのpathをresolve / readする

`skills/sdd-implementation/SKILL.md`の既存Dependency Preflightを使用し、`keep-implementation-simple`をrequired supporting Skillとして扱う。active discoveryと既存global-root fallbackを完了し、使用する一つのcanonical `SKILL.md` pathをresolveして全文readする。

discovery、candidate inspection、path resolution、またはreadを完了できない場合は、affected workの前にfail closedする。結果は`BLOCKED: dependency preflight failed`と、失敗したphase、observedまたはattempted path、underlying errorを含む。complete no-matchとinspection/read failureを混同しない。新しいresolverやfailure protocolは作らない。

### R-03: 同じpathを正確に7 roleへ渡す

Dependency Preflightでresolve / readした同じcanonical pathと、作業前にそのfileを全文readするinstructionを、次のfresh workerだけへ渡す。

| Role | 既存のowner surface |
| --- | --- |
| Spec Synthesizer | `references/planning-context.md`、`prompts/spec-synthesizer.md` |
| Spec Reviewer | `references/planning-context.md`、`prompts/spec-reviewer.md` |
| Plan Author | `references/planning-context.md` |
| Plan Reviewer | `references/planning-context.md`、`prompts/plan-reviewer.md` |
| Implementer | `SKILL.md`のImplementation Stage |
| Task Reviewer | `SKILL.md`のImplementation Stage |
| Final Reviewer | `SKILL.md`のFinal Whole-Branch Review |

各roleはreadを完了できなければ既存のbounded failure / return boundaryで停止し、roleまたはphase、path、underlying errorを報告する。Research Workerとknowledge closeout workerは対象外である。

### R-04: SDDは参照contractだけを所有する

SDD側が所有するのはrequired dependency identity、resolved path、read-fully-before-work instruction、適用する7 role、fail-closed boundaryだけである。KISのInputs、Outputs、Method、review policyや、test / fixture / guardrailに関する新しいpolicy文は複写・追加しない。

### R-05: regressionは一つだけ追加する

`skills/sdd-implementation/tests/test_preimplementation_context.py`へ一つのfocused regressionだけを追加する。expected dataは7 roleと上表の既存owner surfaceをtest内の最小inline dataとして持ち、次を一つのcontractとして識別する。

- required dependencyが宣言され、canonical pathがresolve / readされること
- 同じresolved pathと全文read instructionが7 roleすべてのowner surfaceに存在すること
- Research Workerとknowledge closeout workerがrole setへ入らないこと
- 新しいprompt、fixture、resolver / schema / runtime machinery、policy copyを必要としないこと

role別permutation、coverage-only assertion、fixture file、第二validatorは追加しない。既存testの変更が必要な場合も、本requirementのために新規追加するtest caseはこの一つに限定する。

### R-06: 現行routeとvalidationを維持する

`sdd-implementation`をsole/default user-facing implementation routeとして維持する。既存SDD suite、architecture / context contract、Skill validation、transient-artifact validation、diff hygieneを削除または緩和しない。

## Implementation write boundary

production / regressionの許可surfaceは既存の次のfileだけである。

- `skills/sdd-implementation/SKILL.md`
- `skills/sdd-implementation/references/planning-context.md`
- `skills/sdd-implementation/prompts/spec-synthesizer.md`
- `skills/sdd-implementation/prompts/spec-reviewer.md`
- `skills/sdd-implementation/prompts/plan-reviewer.md`
- `skills/sdd-implementation/tests/test_preimplementation_context.py`

必要なdurable planning / closeout synchronizationは`knowledge/wiki/syntheses/keep-implementation-simple-spec.md`、current V2-bound implementation plan、`knowledge/index.md`、`knowledge/log.md`に限定する。`skills/keep-implementation-simple/**`はwrite boundaryに含めない。

## Acceptance criteria

1. canonical spec identityが`KIS-SPEC-2026-08-14-V2`で、全箇所がbaseline `82dcd32157ff9690ae038f982f3916009e449f80`へbindingしている。
2. `git diff 82dcd32157ff9690ae038f982f3916009e449f80 -- skills/keep-implementation-simple/SKILL.md`がemptyである。
3. baseline blobとfinal worktreeの`skills/keep-implementation-simple/SKILL.md`のSHA-256がともに`2c2361f04ca6d2dd7433d2dfa80ff173a14f68ef401df0e98e7d4366d1d23b3f`である。
4. SDD Dependency Preflightが一つのcanonical KIS pathをresolve / 全文readし、discovery / resolution / read failureをphase、path、underlying error付きでaffected work前にfail closedする。
5. 同じresolved pathと全文read-before-work instructionが、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerの正確な7 roleへ既存surfaceから渡される。
6. Research Workerとknowledge closeout workerは対象外で、SDD内にKIS policy本文のduplicateがない。
7. `test_preimplementation_context.py`へ追加された一つのfocused regressionが、7 role / owner surface mappingをinline dataで検証する。新しいtest file、prompt、fixture、resolver、schema、runtime machinery、optional metadata、第二validatorは存在しない。
8. `scripts/validate_skill_architecture.py --all`がpassし、`sdd-implementation`だけがsole/default user-facing implementation routeである。
9. 次のcurrent required validationをfresh runし、すべてpassする。

   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests`
   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
   - `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
   - active runtimeのskill-creator `quick_validate.py`を`skills/keep-implementation-simple`と`skills/sdd-implementation`へそれぞれ実行
   - current Git indexのnominated candidate treeに対する`python3 scripts/validate_sdd_transient_artifacts.py --candidate-tree <candidate-tree>`。new commit / final treeが存在するstageでは対応する`--new-commit` / `--final-tree`も実行
   - `git diff --check`

10. `knowledge/index.md`とappend-only `knowledge/log.md`がV2 snapshotと、V1-bound planがcurrent implementation entryではないことへ同期している。

## Stop conditions

- `skills/keep-implementation-simple/**`へ差分が生じた場合は停止する。
- 7 roleの一部だけへread requirementが置かれた場合、またはResearch / knowledge closeoutが追加された場合は停止する。
- roleごとに異なるpathをresolveする案、または同一pathを証明できない案は停止する。
- KIS policy本文のduplicate、新規prompt / fixture / resolver / schema / runtime machinery / optional metadataが必要になった場合はscope conflictとして停止する。
- required validationまたはsole/default SDD routeを弱める場合は停止する。
- V2へbindingしていないImplementation PlanでImplementation Stageへ進もうとする場合は停止する。

## Confirmed Decisions

1. `keep-implementation-simple` Skillは変更しない。
2. no-guidance 5/5 GREEN、unchanged Skill 5/5 GREENでREDが成立しなかったため、V1のSkill拡張proposalはsupersededである。
3. 実装対象は`sdd-implementation`だけである。
4. required roleはSpec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerの正確な7種類である。
5. Research Workerとknowledge closeout workerは対象外である。
6. Dependency Preflightは一つのcanonical KIS pathをresolve / 全文readし、同じpathを7 roleへ渡す。
7. discovery / resolution / read failureはphase、path、underlying error付きでfail closedする。
8. regressionは既存test module内の一つだけで、role / owner surface mappingはinline dataにする。
9. 新しいprompt、fixture、resolver / schema / runtime machinery、optional metadata、policy duplicationを追加しない。
10. `sdd-implementation`をsole/default routeとし、current required validationを維持する。

## Open Decisions

なし。

## Provenance

- Human authority: current conversation、2026-08-14。既存KISを変更せず、`sdd-implementation`だけで正確な7 roleへcanonical Skill read-before-workを要求するscope correction。
- baseline: `82dcd32157ff9690ae038f982f3916009e449f80`。
- matched behavioral evidence: 2026-08-14のcontroller-collected prewrite evaluation summary。repository-external raw artifactのruntime pathはdurable provenanceとして保持せず、no-guidance 5/5 scope GREEN・5/5 retention PASS、unchanged current Skill 5/5 scope GREEN・5/5 retention PASS、varianceなし、RED未成立。
- repository evidence: baselineとcurrentの`skills/keep-implementation-simple/SKILL.md`は同一SHA-256 `2c2361f04ca6d2dd7433d2dfa80ff173a14f68ef401df0e98e7d4366d1d23b3f`。baseline SDD suiteは93 tests、architecture / context / KIS Skill validationはpass済み。
- current repository authority: `AGENTS.md`、`knowledge/AGENTS.md`、`skills/AGENTS.md`。
- V1 history: `KIS-SPEC-2026-08-14-V1`はinitial expansion proposalとそのreview historyを保持するが、current implementation authorityではない。
