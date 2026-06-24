# Grill To PR Loop Epic Base Delivery Policy Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grill-to-pr-epic-base-delivery | G2PR-001 | epic-base delivery と issue PR merge policy を契約化する | 承認済み | 実行可能 | 実装済み | なし | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; ブロック元 なし; ブロック先 なし

## G2PR-001

### Epic ID

`grill-to-pr-epic-base-delivery`

### タイトル

epic-base delivery と issue PR merge policy を契約化する

### 作るもの

`grill-to-pr-loop` と `issue-implementation-loop` に、`codex/<epic-id>/epic-base`、issue PR の agent merge 既定、final PR human-only、review cycle 上限 2 回の契約と validation を追加する。

### 受け入れ条件

- [x] Execution Envelope が `batch_issue_prs` remote mode を受け入れる。
- [x] `batch_issue_prs` では `epic_base.ref` が `codex/<epic-id>/epic-base` でなければ validation が失敗する。
- [x] issue PR base / merge policy と final PR head / base / merge policy が validation される。
- [x] `review_policy.max_review_cycles` は 1 以上 2 以下でなければ validation が失敗する。
- [x] docs / templates / agent metadata が新しい delivery policy を説明している。
- [x] 既存の `issue-implementation-loop` tests と skill validation が通る。

### 非目標

- GitHub issue、push、PR、merge は実行しない。
- final PR merge を agent に許可しない。
- global `dev` branch を導入しない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: なし

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-spec.md`
- 既存 branch policy: `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md`
- 既存 context policy: `knowledge/wiki/syntheses/issue-implementation-loop-context-policy-spec.md`

### 検証

- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest skills.issue-implementation-loop.tests.test_issue_implementation_loop`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop`
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成
- PR: 未作成。remote write 未実行。

### 検証結果

- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest skills.issue-implementation-loop.tests.test_issue_implementation_loop` -> OK, 25 tests.
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> OK, 25 tests.
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop` -> OK, Skill is valid.
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop` -> OK, Skill is valid.
- `git diff --check` -> OK.
