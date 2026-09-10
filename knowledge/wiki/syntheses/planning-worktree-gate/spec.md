---
summary: 最初の repository write 前の作業ツリー確保と、commit reachability による配送確認の当時の設計を確認できる。
knowledge_status: historical
---
# Planning Worktree Gate 仕様

## 適用範囲と履歴

旧 grill-to-pr-loop / issue-implementation-loop の設計・実行証跡。[[wiki/syntheses/sdd-implementation-phase2-removal-plan|旧 loop skill の除去記録]] により executable surface / restart entrypoint ではない。本文の current 表現や packet / envelope / baseline は当時の範囲に限り、再実行には新しい承認と run を必要とする。現行の作業境界は repository root の `AGENTS.md` を参照する。

## 問題設定 / 成功条件

`grill-to-pr-loop` は planning artifact を current planning branch に commit することを要求しているが、最初の repository write より前に Epic 単位の planning worktree を確保する規則、同じ worktree の再利用、作成失敗時の fail-closed 停止を skill-local contract と実行可能な guard として持っていない。

`issue-implementation-loop` は approved Gate commit と `epic_base.sha` の ancestry を検証する一方、実際の final PR branch が全 planning / implementation commit を含むこと、default branch checkout の HEAD / status が開始時 snapshot と一致することを delivery 前に検証していない。

成功条件は、default branch checkout を task work に対して read-only に保ち、planning と execution の branch ownership を machine-verifiable にし、main への一時書き込み、欠落 commit を含む delivery、pre-existing dirt の破壊を fail closed で拒否できることである。

## Epic ID

`planning-worktree-gate`

## 採用した判断

### Planning Worktree Gate

- discovery、read-only 調査、grilling は通常 checkout で実行してよい。
- Written Spec を含む最初の repository write より前に、`codex/<epic-id>/planning` branch と Epic 単位の planning worktree を作成または再利用する。
- Written Spec、Spec Gate、Issue Gate、Execution Plan Gate、`knowledge/index.md` / `knowledge/log.md` 同期は同じ planning worktree で行う。
- Gate ごとに planning worktree を作り直さない。
- default branch checkout では task 由来の file write、stage、commit を行わない。
- worktree 作成または再利用に失敗した場合、default checkout へフォールバックせず repository write 前に停止する。
- repo / user instruction が worktree preference を既に宣言している場合、毎回の作成確認は行わない。
- `skills/grill-to-pr-loop/scripts/planning_worktree.py prepare` を executable guard とし、既存 worktree の再利用、ignored project-local worktree root、default checkout snapshot、fail-closed error を一つの contract にする。

### Durable / runtime artifact 境界

- 新規 Input Packet v2 は top-level `planning_branch` と `planning_base_sha` を持つ。`planning_base_sha` は full 40/64-character Git object ID とする。
- 既存の sealed Input Packet v2 は raw-byte approval lock を壊さないため読み取り互換を保つ。Planning Worktree Gate 導入後に新しく作る packet は両 field を必須とする。
- host 固有の planning worktree path、default checkout path、開始時 HEAD / porcelain status は tracked packet に入れず、Git common directory 配下の untracked runtime artifact と Execution Envelope v4 `repository_guard` に記録する。
- `repository_guard` は packet の `planning_branch` / `planning_base_sha` と一致し、registered worktree と default checkout snapshot を参照する。

### Prepare / PR_READY / delivery guard

- prepare は approved Gate commit が `epic_base.sha` から到達可能でなければ `GATE_COMMIT_NOT_ANCESTOR` で拒否する。Gate commit を default branch にだけ置いて `epic_base` に含めない運用は許可しない。
- prepare と completion validation は、registered planning worktree、packet と runtime guard の branch/base 一致、default checkout の開始時 HEAD / status 一致を検証する。
- default checkout に task 由来の commit または status drift があれば `PR_READY` / completion / delivery を拒否する。
- final PR delivery は actual final head ref を解決し、approved Gate commit、`planning_base_sha`、全 delivery candidate の committed `head_sha` が final head の ancestor であることを検証する。
- `pr_merged: true` の runtime record だけを implementation commit integration の証拠にしない。
- validation failure 時に default checkout の reset、clean、変更移動、削除を行わない。
- 開始前から存在した無関係な dirt は snapshot として保持し、同じ HEAD / status のままなら許可する。自動で planning worktree または PR branch へ移さない。

## 検討した選択肢

1. skill prose だけを更新する方法は既存 agent の rationalization を抑えられても Acceptance Tests 1、2、4、6、7、8 を executable に証明できないため採用しない。
2. generic worktree manager を新設する方法は責務が広すぎ、`grill-to-pr-loop` の Epic lifecycle から ownership が離れるため採用しない。
3. Epic-scoped CLI と `issue-implementation-loop` の repository integrity guard を組み合わせる方法を採用する。planning worktree lifecycle と delivery integrity を別 module に保ち、tracked durable state と host-specific runtime state を分離できる。

## Issue 分解方針

- `PWTG-001`: Planning Worktree Gate CLI と `grill-to-pr-loop` contract / tests。
- `PWTG-002`: packet / Execution Envelope repository guard contract と prepare / completion validation。
- `PWTG-003`: final PR commit reachability、default checkout snapshot、delivery tests。
- `PWTG-004`: dual-host validation、wiki index/log、全体 verification と review。

`PWTG-002` は `PWTG-001`、`PWTG-003` は `PWTG-002`、`PWTG-004` は `PWTG-001` から `PWTG-003` に依存する。

## 受け入れ条件

1. clean な `main` から最初の spec write 前に planning worktree が作られる。
2. 同じ Epic の planning worktree が既に存在すれば再利用される。
3. Spec Gate から Execution Plan Gate と index/log 同期まで同じ planning worktree を使う。
4. worktree 作成不能時に `main` へ file write、stage、commit を行わない。
5. default checkout の pre-existing dirt を変更、移動、削除、PR 混入しない。
6. approved Gate commit が `epic_base` から到達不能なら prepare が失敗する。Gate commit が `main` のみにある場合も同じである。
7. final PR branch が approved Gate commit または全 implementation `head_sha` を含まなければ delivery が失敗する。
8. `PR_READY` / delivery 時に default checkout の HEAD / status が開始時 snapshot と一致する。pre-existing dirt が同一なら成功し、task 由来の差分があれば失敗する。

## 検証方針 / コマンド

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/validate_dual_host_authoring.py --all
python3 -m unittest discover -s scripts
git diff --check
```

RED では各 acceptance behavior の test を実装前に失敗させる。GREEN 後は focused test、両 skill suite、repository validator の順で fresh verification を行う。

## リモート書き込み方針

`local_only`。push、PR 作成、merge、GitHub issue mutation は行わない。

## 人間レビューゲート

- ユーザーが提示した方針、Acceptance Tests、Non-goals を本 spec の承認済み scope とする。
- scope、durable/runtime boundary、remote policy、stop condition を変更する場合は再確認する。
- final merge は常に human-only。

## 非目標

- Gate ごとの worktree 作成。
- `llm-wiki` による Git lifecycle 管理。
- unrelated dirt の自動移動、削除、stash、commit、PR 混入。
- default branch の自動 hard reset、clean、checkout による復元。
- generic scheduler、generic worktree manager、Git hosting abstraction の新設。
- 既存 sealed packet の bytes を migration のために書き換えること。

## 停止条件 / 既知のリスク

- planning worktree の作成 / 再利用が失敗する。
- planning branch/path が別 Epic または別 branch と衝突する。
- default checkout の開始時 snapshot を取得できない。
- approved Gate commit が `epic_base.sha` から到達不能である。
- packet、Execution Envelope、runtime の planning identity が一致しない。
- final PR head が planning / implementation commit を含まない。
- default checkout の HEAD / status が開始時 snapshot から変化している。
- pre-existing dirt と task write scope が重なり、安全に分離できない。
- remote write または destructive recovery が必要になる。

## 関連ページ

- [Grill To PR Loop Branch Policy Spec](../grill-to-pr-loop-branch-policy-spec.md) は issue branch / worktree と `epic_base` の既存 ownership を定義する。本仕様はその前段の planning worktree と最終 delivery integrity を追加する。
- [Loop Skill Approved Spec Binding Artifact Lifecycle Revision](../approved-spec-binding-contract/spec.md) は tracked durable artifact と Git common directory 配下の untracked runtime artifact の境界を定義する。

## 出典

- `../../../../AGENTS.md`
- `../../../../skills/grill-to-pr-loop/SKILL.md`
- `../../../../skills/grill-to-pr-loop/references/planning-contract.md`
- `../../../../skills/grill-to-pr-loop/references/execution-handoff.md`
- `../../../../skills/issue-implementation-loop/SKILL.md`
- `../../../../skills/issue-implementation-loop/references/execution-envelope.md`
- `../../../../skills/issue-implementation-loop/references/worktree-lifecycle.md`
- `../../../../skills/issue-implementation-loop/references/remote-delivery.md`

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

最初のrepository write前のEpic単位planning worktree、default checkout保全、prepare / PR_READY / deliveryのphysical commit reachability guardを定義し、実装完了した承認済み仕様。

## 関連する実行証跡

以下は旧 run の記録であり、現在の実行契約として再利用しない。承認済み bytes / seal / digest は当時の Git revision に対するものであり、探索 metadata を追加した現在のページの digest ではない。

- [[wiki/syntheses/planning-worktree-gate/input-packet.json|Planning Worktree Gate Input Packet]] — Planning Worktree Gate実装前の現行v2 validatorでsealしたself-hosting execution lock。target実装後の新規packet contractとは区別する。
