# Grill To PR Loop Skill Split V2 Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| issue-implementation-loop | G2PR-001 | v2仕様をrepo wikiへ正本化する | 承認済み | 実行可能 | 完了 | なし | G2PR-002, G2PR-003 | 未作成 | 承認済み | 未作成 |
| issue-implementation-loop | G2PR-002 | `issue-implementation-loop` を追加する | 承認済み | 実行可能 | 完了 | G2PR-001 | G2PR-003 | 未作成 | 承認済み | 未作成 |
| issue-implementation-loop | G2PR-003 | `grill-to-pr-loop` をcompositionへ縮小する | 承認済み | 実行可能 | 完了 | G2PR-002 | なし | 未作成 | 承認済み | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; 完了; ブロック先 G2PR-002, G2PR-003
- G2PR-002: 実行可能; 完了; ブロック元 G2PR-001; ブロック先 G2PR-003
- G2PR-003: 実行可能; 完了; ブロック元 G2PR-002

## G2PR-001

### Epic ID

`issue-implementation-loop`

### タイトル

v2仕様をrepo wikiへ正本化する

### 作るもの

添付設計を raw source / source summary / implementation spec / local issue ledger として `knowledge/` に保存し、`knowledge/index.md` と `knowledge/log.md` から発見できるようにする。

### 受け入れ条件

- [x] 添付 v2 が `knowledge/raw/sources/` に保存されている。
- [x] source summary と implementation spec が relative Markdown link で接続されている。
- [x] `knowledge/index.md` に active synthesis と source summary が登録されている。
- [x] `knowledge/log.md` に今回の ingest / implementation entry が残っている。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: G2PR-002, G2PR-003

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`
- 元設計: `knowledge/raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md`

### 検証

- `rg -n "grill-to-pr-loop-skill-split-v2|issue-implementation-loop" knowledge/index.md knowledge/log.md knowledge/wiki`

### 実装レビュー

- 状態: 承認済み
- レビュー範囲: `dd22cd8b7cb518d3838c612c24e0164c31dfd986..working-tree`
- レビュー結果: 独立レビューで G2PR-002 の write-scope conflict 指摘があり、修正後の再レビューで findings なし。
- PR: 未作成。remote write 未承認かつ `gh` auth unavailable のため local-only。

## G2PR-002

### Epic ID

`issue-implementation-loop`

### タイトル

`issue-implementation-loop` を追加する

### 作るもの

承認済み Issue 群を dependency-aware worktree / verification / issue-scoped review / runtime-state / recovery で実装する新 skill を追加する。

### 受け入れ条件

- [x] `skills/issue-implementation-loop/SKILL.md` が direct invocation と mode router を説明している。
- [x] references が selective read set で分割されている。
- [x] schemas / templates / scripts が存在し、stdlib だけで動く。
- [x] helper scripts が cycle、write-scope conflict、human wait scope、runtime rebuild、git reconciliation を検証または報告できる。
- [x] pressure scenario を unittest で確認できる。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-001
- ブロック先: G2PR-003

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`

### 検証

- `python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop`

### 実装レビュー

- 状態: 承認済み
- レビュー範囲: `dd22cd8b7cb518d3838c612c24e0164c31dfd986..working-tree`
- レビュー結果: 初回レビューで pending runnable 候補同士の write-scope conflict が同時 runnable になる Important finding。`test_pending_runnable_candidates_with_overlapping_scope_are_serialized` を追加し、`compute_next_actions()` が選択済み runnable 候補を `reserved_dispatch_scopes` として扱うよう修正。再レビュー findings なし。
- PR: 未作成。remote write 未承認かつ `gh` auth unavailable のため local-only。

## G2PR-003

### Epic ID

`issue-implementation-loop`

### タイトル

`grill-to-pr-loop` をcompositionへ縮小する

### 作るもの

既存 `grill-to-pr-loop` を上流 composition skill として更新し、execution phase は `issue-implementation-loop` に normalized packet を渡す契約へ変更する。

### 受け入れ条件

- [x] `grill-to-pr-loop` が worktree lifecycle / scheduler / runtime state を直接所有しない。
- [x] execution phase で `issue-implementation-loop` を required として扱う。
- [x] `check_prereqs.py --phase execution --json` が execution skill availability を報告する。
- [x] optional GitHub writes は明示承認 gate のまま残る。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: G2PR-002
- ブロック先: なし

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`
- 新 skill: `skills/issue-implementation-loop/SKILL.md`

### 検証

- `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop`
- `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json`

### 実装レビュー

- 状態: 承認済み
- レビュー範囲: `dd22cd8b7cb518d3838c612c24e0164c31dfd986..working-tree`
- レビュー結果: 独立レビューで G2PR-002 以外の in-scope gap はなし。G2PR-002 修正後の再レビューで findings なし。
- PR: 未作成。remote write 未承認かつ `gh` auth unavailable のため local-only。
