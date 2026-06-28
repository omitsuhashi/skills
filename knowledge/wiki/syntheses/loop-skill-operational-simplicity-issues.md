# Loop Skill Operational Simplicity Issues

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。実装、push、PR 作成、remote write は未承認。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-operational-simplicity | LSOS-001 | loop 系の適用基準を明文化する | 承認済み | COMPLETE | なし | LSOS-002, LSOS-003 | 未作成 | approved: `f61e10dd405d843c5b66ed99395b76e215962f0a..e7cd6fb695c229ec71d3e84e6fea1999123c97a1` | 未作成 |
| loop-skill-operational-simplicity | LSOS-002 | loop 系 mental model を 1 ページ化する | 承認済み | COMPLETE | LSOS-001 | LSOS-004 | 未作成 | approved: `e798ec03d74280844e09607ebc9f8d97d3b57235..5d48b3f2cffaa2102d9c3b8343fc8351020182a2` | 未作成 |
| loop-skill-operational-simplicity | LSOS-003 | workflow complexity report を追加する | 承認済み | 実行可能 | LSOS-001 | LSOS-004 | 未作成 | 未実施 | 未作成 |
| loop-skill-operational-simplicity | LSOS-004 | regression tests と wiki ledger を更新する | 承認済み | ブロック中 | LSOS-002, LSOS-003 | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- LSOS-001: COMPLETE。ブロック元 なし。LSOS-002 と LSOS-003 を release 済み。
- LSOS-002: COMPLETE。LSOS-001 の適用基準を前提に mental model を作成済み。LSOS-004 は LSOS-003 完了待ち。
- LSOS-003: 実行可能。LSOS-001 の適用基準を前提に operator-facing complexity を定義する。
- LSOS-004: LSOS-002 と LSOS-003 の成果を統合して regression tests と wiki ledger を仕上げる。

## LSOS-001

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

loop 系の適用基準を明文化する

### 作るもの

`grill-to-pr-loop` と `issue-implementation-loop` の入口に、loop 系を使う条件、使わない条件、止まる条件を短く追加する。小さい単発修正は通常の direct implementation / task-specific skill に逃がし、長い repository change だけ loop 系に乗せる。

### 受け入れ条件

- [x] `skills/grill-to-pr-loop/SKILL.md` または operation-owned reference から、loop 系を使うケースと使わないケースが 1 screen 相当で分かる。
- [x] `skills/issue-implementation-loop/SKILL.md` から、approved packet 前提、worker context 必須、coordinator 実装禁止が適用条件として分かる。
- [x] 新しい user-facing skill は追加されない。
- [x] `validate_skill_architecture.py --all` が通る。
- [x] `validate_skill_context.py --all` が通る。

### ブロッカー

- 実行状態: COMPLETE
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

- 仕様: [Loop Skill Operational Simplicity Spec](loop-skill-operational-simplicity-spec.md)
- policy: [skill-architecture.toml](../../../skill-architecture.toml)
- current context contracts: [grill-to-pr-loop/context-contract.toml](../../../skills/grill-to-pr-loop/context-contract.toml), [issue-implementation-loop/context-contract.toml](../../../skills/issue-implementation-loop/context-contract.toml)

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`

### 実装 evidence

- Worker commit: `e7cd6fb695c229ec71d3e84e6fea1999123c97a1`。
- Review range: `f61e10dd405d843c5b66ed99395b76e215962f0a..e7cd6fb695c229ec71d3e84e6fea1999123c97a1`。
- `skills/grill-to-pr-loop/SKILL.md` に Applicability section を追加し、loop 系を使う条件、使わない条件、implementation 前の stop 条件を明示した。
- `skills/issue-implementation-loop/SKILL.md` に Applicability section を追加し、normalized approved packet、worker context、coordinator 実装禁止を入口で明示した。
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` と `skills/issue-implementation-loop/tests/test_entrypoint.py` に entrypoint applicability regression を追加した。
- Implementation review: approved。Critical / Important / Minor finding はなし。
- Remote write は行っていない。

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

loop 系 mental model を 1 ページ化する

### 作るもの

coordinator、worker、reviewer、runtime state、local ledger、remote delivery の関係を 1 ページで説明する operator-facing reference を追加する。default read-set を肥大化させず、入口から必要時に発見できる形にする。

### 受け入れ条件

- [x] mental model は coordinator / worker / reviewer / runtime state / local ledger / remote delivery の責務境界を説明している。
- [x] mental model は `issue-implementation-loop` の実行者が最初に読む役割境界として使える。
- [x] mental model の追加後も `validate_skill_context.py --all` が通る。
- [x] default read-set に不要な重い reference を追加しない。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: LSOS-001
- ブロック先: LSOS-004 は LSOS-003 完了待ち

### 想定 write scope

- `path:skills/grill-to-pr-loop/references`
- `path:skills/issue-implementation-loop/references`
- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/issue-implementation-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Operational Simplicity Spec](loop-skill-operational-simplicity-spec.md)
- `skills/grill-to-pr-loop/references/core.md`
- `skills/issue-implementation-loop/references/core.md`
- `skills/issue-implementation-loop/references/runtime-state.md`
- `skills/issue-implementation-loop/references/worker-contract.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `rg -n "coordinator|worker|reviewer|runtime state|remote delivery" skills/grill-to-pr-loop skills/issue-implementation-loop`

### 実装 evidence

- Worker commits: `bd70a8b3a0a8bf07f84ed09f6cb0580e731a19ce`, review-fix `5d48b3f2cffaa2102d9c3b8343fc8351020182a2`。
- Review range: `e798ec03d74280844e09607ebc9f8d97d3b57235..5d48b3f2cffaa2102d9c3b8343fc8351020182a2`。
- `skills/issue-implementation-loop/references/mental-model.md` を追加し、coordinator / worker / reviewer / runtime state / local ledger / remote delivery の責務境界を 1 ページで整理した。
- `skills/issue-implementation-loop/SKILL.md` と `skills/grill-to-pr-loop/SKILL.md` から必要時に mental model を発見できるようにした。
- `mental-model.md` は `context-contract.toml` の default operation read-set には追加していない。
- 1 回目 implementation review は Important 1 件。`final PR merge` が approval-gated action と読める境界表現だったため、review-fix で `Final PR merge is always human-only` を明記した。
- 2 回目 implementation review: approved。Critical / Important / Minor finding はなし。
- Remote write は行っていない。

### 実装検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> OK。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> OK, 13 tests。
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK, 103 tests。
- `git diff --check` -> OK。

## LSOS-003

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

workflow complexity report を追加する

### 作るもの

`scripts/report_skill_context.py --all --json` に、read-set context metrics とは別の `workflow_complexity` summary を追加する。gate 数、operation 数、runtime artifact 数、worker-context 必須、review cycle、human wait、remote delivery の有無を advisory として返す。

### 受け入れ条件

- [ ] JSON output に top-level `workflow_complexity` がある。
- [ ] `workflow_complexity` は operation count、gate count、runtime artifact count、worker-context flag、review-cycle flag、remote-delivery flag を含む。
- [ ] text output は既存 context report を読みづらくしない。complexity は必要な warning だけ短く出す。
- [ ] `validate_skill_context.py` は read-set budget validator のままで、complexity を hard failure にしない。
- [ ] workflow complexity の tests が JSON shape と advisory behavior を固定する。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: LSOS-001
- ブロック先: LSOS-004

### 想定 write scope

- `path:scripts/report_skill_context.py`
- `path:scripts/skill_context`
- `path:scripts`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Operational Simplicity Spec](loop-skill-operational-simplicity-spec.md)
- `scripts/report_skill_context.py`
- `scripts/skill_context/contract.py`
- `scripts/skill_context/metrics.py`
- `skill-architecture.toml`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

## LSOS-004

### Epic ID

`loop-skill-operational-simplicity`

### タイトル

regression tests と wiki ledger を更新する

### 作るもの

LSOS-001 から LSOS-003 の成果を統合し、regression tests、wiki index/log、issue ledger の implementation evidence を仕上げる。

### 受け入れ条件

- [ ] 適用基準、mental model discoverability、workflow complexity JSON shape が tests で固定されている。
- [ ] `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に各 issue の実装 evidence、検証結果、review 結果が反映されている。
- [ ] `knowledge/index.md` と `knowledge/log.md` が final ledger を発見できる。
- [ ] full verification が通る。
- [ ] remote write は行われていない。

### ブロッカー

- 実行状態: ブロック中
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

- 仕様: [Loop Skill Operational Simplicity Spec](loop-skill-operational-simplicity-spec.md)
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

## Remote Policy

`local_only`。

GitHub issue mirror、push、PR 作成、merge は未承認。final PR merge は常に human-only。
