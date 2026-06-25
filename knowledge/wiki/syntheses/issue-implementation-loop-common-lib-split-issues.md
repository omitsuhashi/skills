# Issue Implementation Loop Common Lib Split Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| issue-implementation-loop-common-lib-split | G2PR-001 | lib package と `_common.py` facade を確立する | 承認済み | 実行可能 | 実装済み | なし | G2PR-002 | 未作成 | 実施済み | 未作成 |
| issue-implementation-loop-common-lib-split | G2PR-002 | validation logic を domain module へ分割する | 承認済み | 実行可能 | 実装済み | G2PR-001 | G2PR-003 | 未作成 | 実施済み | 未作成 |
| issue-implementation-loop-common-lib-split | G2PR-003 | scheduler / dependency graph を domain module へ分割する | 承認済み | 実行可能 | 実装済み | G2PR-002 | G2PR-004 | 未作成 | 実施済み | 未作成 |
| issue-implementation-loop-common-lib-split | G2PR-004 | delivery / runtime-facing helper と CLI compatibility を仕上げる | 承認済み | 実行可能 | 実装済み | G2PR-003 | G2PR-005 | 未作成 | 実施済み | 未作成 |
| issue-implementation-loop-common-lib-split | G2PR-005 | tests を behavior domain ごとに分割し ledger を更新する | 承認済み | 実行可能 | 実装済み | G2PR-004 | なし | 未作成 | 実施済み | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; 実装済み; ブロック元 なし; ブロック先 G2PR-002
- G2PR-002: 実行可能; 実装済み; ブロック元 G2PR-001; ブロック先 G2PR-003
- G2PR-003: 実行可能; 実装済み; ブロック元 G2PR-002; ブロック先 G2PR-004
- G2PR-004: 実行可能; 実装済み; ブロック元 G2PR-003; ブロック先 G2PR-005
- G2PR-005: 実行可能; 実装済み; ブロック元 G2PR-004; ブロック先 なし

2026-06-25 に spec / issue / packet は user approval 済み。remote write は未承認のため `local_only` とし、GitHub issue / PR / push / merge は行わない。

## G2PR-001

### Epic ID

`issue-implementation-loop-common-lib-split`

### タイトル

lib package と `_common.py` facade を確立する

### 作るもの

`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/` を作り、package import と `_common.py` backward-compatible facade の土台を置く。まず JSON I/O、ID / SHA / branch utility、review 判定、git helper、skill discovery のような低依存 helper を移し、既存 CLI が `from _common import ...` のまま動くことを固定する。

### 受け入れ条件

- [x] `scripts/lib/issue_implementation_loop/` が package として import できる。
- [x] `_common.py` が既存 public symbol を re-export する facade として動く。
- [x] `check_capabilities.py --json` が repo-local skill root 優先を維持する。
- [x] `validate_input_packet.py` など既存 public scripts が import error なく動く。
- [x] import compatibility と skill discovery の regression test が先に追加されている。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: G2PR-002

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-spec.md`
- 既存 follow-up: `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md`
- 対象: `skills/issue-implementation-loop/scripts/_common.py`, `skills/issue-implementation-loop/scripts/check_capabilities.py`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json --json`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: commit 前 working tree diff
- 理由: subagent tool は明示的な subagent 依頼がない場合に使用できないため、manual review fallback として approved spec / issue / acceptance criteria / diff を照合した。
- 検証結果: Critical 0、Important 0。`_common.py` は facade 化され、public scripts は既存 CLI のまま通る。

## G2PR-002

### Epic ID

`issue-implementation-loop-common-lib-split`

### タイトル

validation logic を domain module へ分割する

### 作るもの

input packet、execution envelope、runtime state、worker report、delivery plan の validation を `validation/` package へ移す。既存 validator scripts の CLI output / exit code / error message contract は変えない。

### 受け入れ条件

- [x] `validation/input_packet.py`, `validation/execution_envelope.py`, `validation/runtime_state.py`, `validation/worker_report.py`, `validation/delivery_plan.py` が存在する。
- [x] `_common.py` は validation functions を re-export するだけで、validation 実装本体を持たない。
- [x] validator scripts の CLI output と exit code が既存 contract と一致する。
- [x] validation tests が behavior domain file へ分離されている。
- [x] schema files の意味変更を含まない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-001
- ブロック先: G2PR-003

### 必要な文脈

- 対象: `skills/issue-implementation-loop/scripts/_common.py`, `skills/issue-implementation-loop/scripts/validate_*.py`, `skills/issue-implementation-loop/assets/schemas/`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: commit 前 working tree diff
- 理由: manual review fallback で approved acceptance criteria と validator script behavior を照合した。
- 検証結果: Critical 0、Important 0。validation schema の意味変更はなし。

## G2PR-003

### Epic ID

`issue-implementation-loop-common-lib-split`

### タイトル

scheduler / dependency graph を domain module へ分割する

### 作るもの

dependency cycle、dependency satisfaction、descendants、write-scope conflict、human wait、`compute_next_actions` を `graph.py` と `scheduler.py` へ移す。scheduler の「wave は completion barrier ではない」「review_approved dependency は success status だけで release しない」「pending runnable の overlapping scope は serialize する」契約を維持する。

### 受け入れ条件

- [x] `graph.py` と `scheduler.py` が存在する。
- [x] `_common.py` は graph / scheduler functions を re-export するだけで、実装本体を持たない。
- [x] `compute_next_actions.py` の CLI output が変わらない。
- [x] scheduler / dependency tests が behavior domain file へ分離されている。
- [x] human wait scope と write-scope conflict の regression が維持される。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-002
- ブロック先: G2PR-004

### 必要な文脈

- 対象: `skills/issue-implementation-loop/scripts/_common.py`, `skills/issue-implementation-loop/scripts/compute_next_actions.py`, `skills/issue-implementation-loop/references/scheduler.md`, `skills/issue-implementation-loop/references/human-wait.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/compute_next_actions.py <fixture-envelope> <fixture-runtime>`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: commit 前 working tree diff
- 理由: manual review fallback で scheduler / dependency graph contract と regression coverage を照合した。
- 検証結果: Critical 0、Important 0。scheduler semantics の変更はなし。

## G2PR-004

### Epic ID

`issue-implementation-loop-common-lib-split`

### タイトル

delivery / runtime-facing helper と CLI compatibility を仕上げる

### 作るもの

delivery plan validation helper、issue branch ownership、delivery issue scope、runtime rebuild / reconcile 周辺の shared import surface を module 化し、public scripts の CLI compatibility を再確認する。`rebuild_runtime_state.py` と `reconcile_git_state.py` は behavior を変えず、必要な shared helper だけを lib から参照できる状態にする。

### 受け入れ条件

- [x] `delivery.py`, `git_state.py`, `skill_discovery.py` が存在し、責務が分かれている。
- [x] `validate_delivery_plan.py`, `reconcile_git_state.py`, `rebuild_runtime_state.py`, `check_capabilities.py` が import error なく動く。
- [x] delivery policy、epic_base lifecycle、runtime rebuild、git reconcile の regression が維持される。
- [x] GitHub remote write は実行しない。
- [x] `_common.py` は delivery / git / skill discovery の実装本体を持たない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-003
- ブロック先: G2PR-005

### 必要な文脈

- 対象: `skills/issue-implementation-loop/scripts/validate_delivery_plan.py`, `skills/issue-implementation-loop/scripts/reconcile_git_state.py`, `skills/issue-implementation-loop/scripts/rebuild_runtime_state.py`, `skills/issue-implementation-loop/scripts/check_capabilities.py`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json --json`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: commit 前 working tree diff
- 理由: manual review fallback で delivery / runtime-facing CLI compatibility と local-only policy を照合した。
- 検証結果: Critical 0、Important 0。remote write は未実行。

## G2PR-005

### Epic ID

`issue-implementation-loop-common-lib-split`

### タイトル

tests を behavior domain ごとに分割し ledger を更新する

### 作るもの

旧 `test_issue_implementation_loop.py` に集中していた tests を behavior domain ごとの files へ分割し、全体 verification と wiki ledger 更新を行う。必要なら旧 file は compatibility / smoke tests だけに縮小する。

### 受け入れ条件

- [x] tests が `test_entrypoint.py`, `test_skill_discovery.py`, `test_validation.py`, `test_runtime_state.py`, `test_delivery.py`, `test_scheduler.py`, `test_git_reconcile.py` 相当へ分かれている。
- [x] 単一 test file が全契約を保持していない。
- [x] `issue-implementation-loop/SKILL.md` の entrypoint budget / trigger-only description tests が維持される。
- [x] local issue ledger に実装状態、verification、implementation review 結果が反映されている。
- [x] `knowledge/index.md` と `knowledge/log.md` が必要な更新を持つ。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-004
- ブロック先: なし

### 必要な文脈

- 対象: `skills/issue-implementation-loop/tests/`, `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md`, `knowledge/index.md`, `knowledge/log.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json`
- `git diff --check`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: commit 前 working tree diff
- 理由: manual review fallback で test split と ledger/index/log update を照合した。
- 検証結果: Critical 0、Important 0。monolithic `test_issue_implementation_loop.py` は削除され、behavior domain files へ分割済み。
