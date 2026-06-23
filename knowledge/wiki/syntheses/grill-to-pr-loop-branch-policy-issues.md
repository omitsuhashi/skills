# Grill To PR Loop Branch Policy Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grill-to-pr-branch-policy | G2PR-001 | branch / worktree / commit policy を契約化する | 承認済み | 実行可能 | 実装済み | なし | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; ブロック元 なし; ブロック先 なし

## G2PR-001

### Epic ID

`grill-to-pr-branch-policy`

### タイトル

branch / worktree / commit policy を契約化する

### 作るもの

`grill-to-pr-loop` と `issue-implementation-loop` に、推奨 branch 運用、`epic_base`、issue branch naming、integration branch、scoped local commit、`PR_READY` までの契約を追加する。

### 受け入れ条件

- [x] `grill-to-pr-loop` が「開発メインブランチ」ではなく `epic_base` を実行契約の中心として説明している。
- [x] issue branch naming、worktree reservation、blocked issue の physical worktree delay が明示されている。
- [x] scoped local commit の順序が `fresh verification -> scoped local commit -> issue review -> fixes/re-review -> PR_READY` として明示されている。
- [x] envelope validation が `base_policy` type を検証する。
- [x] `branch_from_blocker_head` を複数 blocker へ同時に使う envelope を拒否する。
- [x] `branch_from_integration_head` を使う dependency が integration base policy と一致しない envelope を拒否する。
- [x] `PR_READY` issue の review range に `working-tree` が明示された runtime state を拒否する。
- [x] 既存の `issue-implementation-loop` テストと skill validation が通る。

### 非目標

- GitHub issue、push、PR、merge は実行しない。
- `main` へ merge しない。
- standalone worktree manager skill は作らない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: なし

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md`
- 既存責務分割: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`
- 既存 review gate: `knowledge/wiki/syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md`

### 検証

- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop`
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-input-packet.json`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_execution_envelope.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/reconcile_git_state.py knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json --json`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成。subagent review はユーザーの明示承認が必要なため未実行。
- レビュー結果: 未作成。local verification は通過済みだが、Issue Implementation Review Gate は未完了。
- PR: 未作成。remote write 未承認かつ今回の delivery intent は local-only。
