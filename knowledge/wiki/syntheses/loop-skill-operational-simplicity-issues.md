# Loop Skill 運用単純化 Issue 台帳

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。LSOS-001 から LSOS-004 のローカル実装は commit 済み。ユーザー承認により branch push と draft PR #22 作成は実施済み。追加のリモート書き込み、PR の ready 化、merge は未承認。

## 台帳

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-operational-simplicity | LSOS-001 | loop 系の適用基準を明文化する | 承認済み | 完了 | なし | LSOS-002, LSOS-003 | 未作成 | 承認済み: `f61e10dd405d843c5b66ed99395b76e215962f0a..e7cd6fb695c229ec71d3e84e6fea1999123c97a1` | [draft PR #22](https://github.com/omitsuhashi/skills/pull/22) |
| loop-skill-operational-simplicity | LSOS-002 | loop 系の役割境界モデルを 1 ページ化する | 承認済み | 完了 | LSOS-001 | LSOS-004 | 未作成 | 承認済み: `e798ec03d74280844e09607ebc9f8d97d3b57235..5d48b3f2cffaa2102d9c3b8343fc8351020182a2` | [draft PR #22](https://github.com/omitsuhashi/skills/pull/22) |
| loop-skill-operational-simplicity | LSOS-003 | workflow complexity レポートを追加する | 承認済み | 完了 | LSOS-001 | LSOS-004 | 未作成 | 承認済み: `59ca2a2c7598480191905e5170905d2338897901..584b34c27fa14adff72c20e8f32c0218042f2be8` | [draft PR #22](https://github.com/omitsuhashi/skills/pull/22) |
| loop-skill-operational-simplicity | LSOS-004 | regression tests と wiki 台帳を更新する | 承認済み | 完了 | LSOS-002, LSOS-003 | なし | 未作成 | 承認済み: `8974dba422a12bcb250a2bb4f80a576dcf4d13b0..8ef5e98d6179bb4f2e28a6a059ebab7a49d3fb09` | [draft PR #22](https://github.com/omitsuhashi/skills/pull/22) |

## ブロッカーグラフ

- LSOS-001: 完了。ブロック元 なし。LSOS-002 と LSOS-003 を release 済み。
- LSOS-002: 完了。LSOS-001 の適用基準を前提に役割境界モデルを作成済み。LSOS-004 へ release 済み。
- LSOS-003: 完了。LSOS-001 の適用基準を前提に実行者向け complexity を定義済み。LSOS-004 へ release 済み。
- LSOS-004: 完了。LSOS-002 と LSOS-003 の成果を統合し、regression tests と wiki 最終台帳を固定済み。

## LSOS-001

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

loop 系の適用基準を明文化する

### 作るもの

`grill-to-pr-loop` と `issue-implementation-loop` の入口に、loop 系を使う条件、使わない条件、止まる条件を短く追加する。小さい単発修正は通常の直接実装または task-specific skill に逃がし、長いリポジトリ変更だけ loop 系に乗せる。

### 受け入れ条件

- [x] `skills/grill-to-pr-loop/SKILL.md` または operation-owned reference から、loop 系を使うケースと使わないケースが 1 screen 相当で分かる。
- [x] `skills/issue-implementation-loop/SKILL.md` から、承認済み packet 前提、worker context 必須、coordinator 実装禁止が適用条件として分かる。
- [x] 新しいユーザー向け skill は追加されない。
- [x] `validate_skill_architecture.py --all` が通る。
- [x] `validate_skill_context.py --all` が通る。

### ブロッカー

- 実行状態: 完了
- ブロック元: なし
- ブロック先: LSOS-002, LSOS-003 release 済み

### 想定 write scope

- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/references`
- `path:skills/issue-implementation-loop/SKILL.md`
- `path:skills/issue-implementation-loop/references`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- policy: [skill-architecture.toml](../../../skill-architecture.toml)
- current context contracts: [grill-to-pr-loop/context-contract.toml](../../../skills/grill-to-pr-loop/context-contract.toml), [issue-implementation-loop/context-contract.toml](../../../skills/issue-implementation-loop/context-contract.toml)

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`

### 実装証跡

- Worker commit: `e7cd6fb695c229ec71d3e84e6fea1999123c97a1`。
- Review range: `f61e10dd405d843c5b66ed99395b76e215962f0a..e7cd6fb695c229ec71d3e84e6fea1999123c97a1`。
- `skills/grill-to-pr-loop/SKILL.md` に Applicability section を追加し、loop 系を使う条件、使わない条件、実装前の停止条件を明示した。
- `skills/issue-implementation-loop/SKILL.md` に Applicability section を追加し、normalized approved packet、worker context、coordinator 実装禁止を入口で明示した。
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` と `skills/issue-implementation-loop/tests/test_entrypoint.py` に entrypoint applicability regression を追加した。
- 実装レビュー: 承認済み。Critical / Important / Minor finding はなし。
- 実装ループ中の remote write は行っていない。

### 実装検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> OK, 12 tests。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK, 101 tests。
- `git diff --check` -> OK。

## LSOS-002

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

loop 系の役割境界モデルを 1 ページ化する

### 作るもの

coordinator、worker、reviewer、runtime state、local ledger、remote delivery の関係を 1 ページで説明する実行者向け reference を追加する。default read-set を肥大化させず、入口から必要時に発見できる形にする。

### 受け入れ条件

- [x] 役割境界モデルは coordinator / worker / reviewer / runtime state / local ledger / remote delivery の責務境界を説明している。
- [x] 役割境界モデルは `issue-implementation-loop` の実行者が最初に読む役割境界として使える。
- [x] 役割境界モデルの追加後も `validate_skill_context.py --all` が通る。
- [x] default read-set に不要な重い reference を追加しない。

### ブロッカー

- 実行状態: 完了
- ブロック元: LSOS-001
- ブロック先: LSOS-004 release 済み

### 想定 write scope

- `path:skills/grill-to-pr-loop/references`
- `path:skills/issue-implementation-loop/references`
- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/issue-implementation-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- `skills/grill-to-pr-loop/references/core.md`
- `skills/issue-implementation-loop/references/core.md`
- `skills/issue-implementation-loop/references/runtime-state.md`
- `skills/issue-implementation-loop/references/worker-contract.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `rg -n "coordinator|worker|reviewer|runtime state|remote delivery" skills/grill-to-pr-loop skills/issue-implementation-loop`

### 実装証跡

- Worker commits: `bd70a8b3a0a8bf07f84ed09f6cb0580e731a19ce`, review-fix `5d48b3f2cffaa2102d9c3b8343fc8351020182a2`。
- Review range: `e798ec03d74280844e09607ebc9f8d97d3b57235..5d48b3f2cffaa2102d9c3b8343fc8351020182a2`。
- `skills/issue-implementation-loop/references/mental-model.md` を追加し、coordinator / worker / reviewer / runtime state / local ledger / remote delivery の責務境界を 1 ページで整理した。
- `skills/issue-implementation-loop/SKILL.md` と `skills/grill-to-pr-loop/SKILL.md` から必要時に役割境界モデルを発見できるようにした。
- `mental-model.md` は `context-contract.toml` の default operation read-set には追加していない。
- 1 回目の実装レビューは Important 1 件。`final PR merge` が approval-gated action と読める境界表現だったため、review-fix で `Final PR merge is always human-only` を明記した。
- 2 回目の実装レビュー: 承認済み。Critical / Important / Minor finding はなし。
- 実装ループ中の remote write は行っていない。

### 実装検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> OK, 13 tests。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK, 103 tests。
- `git diff --check` -> OK。

## LSOS-003

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

workflow complexity レポートを追加する

### 作るもの

`scripts/report_skill_context.py --all --json` に、read-set context metrics とは別の `workflow_complexity` summary を追加する。gate 数、operation 数、runtime artifact 数、worker-context 必須、review cycle、human wait、remote delivery の有無を advisory として返す。

### 受け入れ条件

- [x] JSON output に top-level `workflow_complexity` がある。
- [x] `workflow_complexity` は operation count、gate count、runtime artifact count、worker-context flag、review-cycle flag、remote-delivery flag を含む。
- [x] text output は既存 context report を読みづらくしない。complexity は必要な warning だけ短く出す。
- [x] `validate_skill_context.py` は read-set budget validator のままで、complexity を hard failure にしない。
- [x] workflow complexity の tests が JSON shape と advisory behavior を固定する。

### ブロッカー

- 実行状態: 完了
- ブロック元: LSOS-001
- ブロック先: LSOS-004 release 済み

### 想定 write scope

- `path:scripts/report_skill_context.py`
- `path:scripts/skill_context`
- `path:scripts`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- `scripts/report_skill_context.py`
- `scripts/skill_context/contract.py`
- `scripts/skill_context/metrics.py`
- `skill-architecture.toml`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

### 実装証跡

- Worker commits: `cef44dd07c1102bbc174c63d9fa7653e070a4679`, review-fix `584b34c27fa14adff72c20e8f32c0218042f2be8`。
- Review range: `59ca2a2c7598480191905e5170905d2338897901..584b34c27fa14adff72c20e8f32c0218042f2be8`。
- `scripts/report_skill_context.py --all --json` に top-level `workflow_complexity` を追加した。
- `workflow_complexity` は operation count、gate count、runtime artifact count、worker-context flag、review-cycle flag、human-wait flag、remote-delivery flag を advisory として返す。
- text output は既存 context report の末尾に短い `Workflow complexity:` 行だけを追加し、non-loop `--skill skills/llm-wiki` では workflow advisory を出さない。
- `scripts/validate_skill_context.py` は変更せず、read-set budget validator のまま維持した。
- 1 回目の実装レビューは Important 1 件、Minor 1 件。non-loop skill target への誤 advisory と brittle count tests を review-fix で修正した。
- 2 回目の実装レビュー: 承認済み。Critical / Important / Minor finding はなし。
- 実装ループ中の remote write は行っていない。

### 実装検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --skill skills/llm-wiki` -> OK, `Workflow complexity:` line なし。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --skill skills/llm-wiki --json` -> OK, `worker_context_required: false`, `warnings: []`。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts` -> OK, 4 tests。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> OK, 13 tests。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK, 103 tests。
- `git diff --check` -> OK。

## LSOS-004

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

regression tests と wiki 台帳を更新する

### 作るもの

LSOS-001 から LSOS-003 の成果を統合し、regression tests、wiki index/log、issue 台帳の実装証跡を仕上げる。

### 受け入れ条件

- [x] 適用基準、役割境界モデルの discoverability、workflow complexity JSON shape が tests で固定されている。
- [x] `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に各 issue の実装証跡、検証結果、レビュー結果が反映されている。
- [x] `knowledge/index.md` と `knowledge/log.md` が最終台帳を発見できる。
- [x] 全体検証が通る。
- [x] remote write は行われていない。
- [x] 仕様書 / PRD / Issue 台帳 / human-facing report / packet の生成・更新規約は日本語ベースを明示し、機械可読 identifier は維持されている。

### ブロッカー

- 実行状態: 完了
- ブロック元: LSOS-002, LSOS-003
- ブロック先: なし

### 想定 write scope

- `path:skills/grill-to-pr-loop`
- `path:skills/issue-implementation-loop`
- `path:scripts`
- `path:knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md`
- `path:knowledge/index.md`
- `path:knowledge/log.md`

### 必要な文脈

- 仕様: [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- この local issue ledger
- `knowledge/AGENTS.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts`
- `git diff --check`

### 実装証跡

- 回帰テスト範囲: `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` が loop applicability と役割境界モデルの discoverability を固定し、`skills/issue-implementation-loop/tests/test_entrypoint.py` が execution applicability と role-boundary mental model discoverability を固定している。
- 回帰テスト範囲: `scripts/test_report_skill_context.py` が `workflow_complexity` JSON shape、text advisory、non-loop target behavior、`validate_skill_context.py` が complexity hard failure にならないことを固定している。
- 回帰テスト範囲: `scripts/test_loop_operational_simplicity_ledger.py` を追加し、LSOS-004 最終台帳、`knowledge/index.md`、`knowledge/log.md` から実装証跡と remote boundary を発見できることを固定した。
- 回帰テスト範囲: `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` が生成 spec/PRD と packet の日本語ベース規約を固定している。
- `knowledge/index.md` の Loop Skill 運用単純化 Issue 台帳 entry を最終台帳 / 実装証跡検索語付きに更新した。
- `skills/grill-to-pr-loop/references/planning-contract.md` に、生成 spec/PRD の title、見出し、label、本文を日本語ベースにし、schema key や path などの identifier を維持する方針を追加した。
- `skills/issue-implementation-loop/SKILL.md` に、ledger と human-facing report 更新を日本語ベースにする方針を追加した。
- `skills/grill-to-pr-loop/references/execution-handoff.md` と `skills/issue-implementation-loop/references/worker-contract.md` に、packet の user-facing string を日本語ベースにする方針を追加した。
- `skills/issue-implementation-loop/assets/templates/input-packet.json` と `skills/issue-implementation-loop/assets/templates/worker-packet.json` の user-facing string 例を日本語へ更新した。
- `knowledge/log.md` に LSOS-004 regression ledger closeout を追記した。
- レビュー結果: final independent review 承認済み。Critical / Important / Minor finding はなし。
- 実装ループ中の remote write は行っていない。

### 実装検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts` -> OK。
- `git diff --check` -> OK。

## リモート方針

実装ループ中は `local_only`。

GitHub issue mirror と merge は未承認。2026-06-29 のユーザー承認により、branch push と [draft PR #22](https://github.com/omitsuhashi/skills/pull/22) 作成は実施済み。final PR merge は常に human-only。
