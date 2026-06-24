# Loop Skill Context Optimization Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-context-optimization | G2PR-001 | context optimization spec と local ledger を正本化する | 承認済み | 実行可能 | 実装済み | なし | G2PR-002, G2PR-003 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-optimization | G2PR-002 | `grill-to-pr-loop` の workflow reference を分割する | 承認済み | 実行可能 | 実装済み | G2PR-001 | G2PR-003 | 未作成 | 未実施 | 未作成 |
| loop-skill-context-optimization | G2PR-003 | repo-local skill root 優先と回帰テストを追加する | 承認済み | 実行可能 | 実装済み | G2PR-001, G2PR-002 | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; 実装済み; ブロック元 なし; ブロック先 G2PR-002, G2PR-003
- G2PR-002: 実行可能; 実装済み; ブロック元 G2PR-001; ブロック先 G2PR-003
- G2PR-003: 実行可能; 実装済み; ブロック元 G2PR-001, G2PR-002

## G2PR-001

### Epic ID

`loop-skill-context-optimization`

### タイトル

context optimization spec と local ledger を正本化する

### 作るもの

現在の状況からベストな状態へ進めるための実装契約、local issue ledger、normalized input packet を `knowledge/wiki/syntheses/` に保存し、`knowledge/index.md` と `knowledge/log.md` から発見できるようにする。

### 受け入れ条件

- [x] `loop-skill-context-optimization-spec.md` が目的、現状、ベストな状態、今回の範囲、非目標、acceptance criteria、verification、stop conditions を持つ。
- [x] `loop-skill-context-optimization-issues.md` が日本語 local-first ledger と blocker graph を持つ。
- [x] `loop-skill-context-optimization-input-packet.json` が `validate_input_packet.py` を通る。
- [x] `knowledge/index.md` と `knowledge/log.md` が更新されている。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: G2PR-002, G2PR-003

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md`
- 既存 context policy: `knowledge/wiki/syntheses/issue-implementation-loop-context-policy-spec.md`
- 既存 split spec: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/loop-skill-context-optimization-input-packet.json`
- `rg -n "Loop Skill Context Optimization|loop-skill-context-optimization" knowledge/index.md knowledge/log.md knowledge/wiki/syntheses`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成
- 理由: 今回はユーザーが subagent / delegation を明示しておらず、remote write も未承認のため、local verification で完了状態を記録する。
- 検証結果: `validate_input_packet.py` は `INPUT PACKET OK`。`rg` で `knowledge/index.md`, `knowledge/log.md`, `knowledge/wiki/syntheses` から新規成果物を確認。

## G2PR-002

### Epic ID

`loop-skill-context-optimization`

### タイトル

`grill-to-pr-loop` の workflow reference を分割する

### 作るもの

`workflow-contract.md` を router 化し、planning / local issue ledger / execution handoff / remote delivery / common mistakes の one-level references へ分ける。`SKILL.md` は新しい reference routing を案内する。

### 受け入れ条件

- [x] `workflow-contract.md` が分割 reference を直接 link している。
- [x] `planning-contract.md`, `local-issue-ledger.md`, `execution-handoff.md`, `remote-delivery.md`, `common-mistakes.md` が存在する。
- [x] 既存の gates, local-first rules, branch/base/commit policy, PR delivery policy, common mistakes が失われていない。
- [x] `SKILL.md` が `workflow-contract.md` と mode-specific references の読み分けを説明している。
- [x] `skills/grill-to-pr-loop/tests/` が reference routing を検証している。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001
- ブロック先: G2PR-003

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md`
- 対象: `skills/grill-to-pr-loop/SKILL.md`, `skills/grill-to-pr-loop/references/`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `wc -w skills/grill-to-pr-loop/references/*.md`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成
- 理由: 今回はユーザーが subagent / delegation を明示しておらず、local verification で完了状態を記録する。
- 検証結果: `python3 -m unittest discover -s skills/grill-to-pr-loop/tests` は 4 tests OK。`wc -w` で `workflow-contract.md` は 368 words、分割後 reference 合計は bounded。

## G2PR-003

### Epic ID

`loop-skill-context-optimization`

### タイトル

repo-local skill root 優先と回帰テストを追加する

### 作るもの

`check_prereqs.py` と `issue-implementation-loop/scripts/_common.py` の skill root discovery を repo-local 優先へ変更し、global installed skill が repo-local implementation を隠さないようにする。

### 受け入れ条件

- [x] explicit `--skills-root` が最優先のまま維持されている。
- [x] `Path.cwd()/skills` が home-level `.agents/skills` と `.codex/skills` より先に探索される。
- [x] plugin cache roots は引き続き optional skill detection に使われる。
- [x] `grill-to-pr-loop` と `issue-implementation-loop` の tests が root ordering を検証している。
- [x] planning / execution preflight が repo-local `skills/issue-implementation-loop` を選ぶ。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001, G2PR-002
- ブロック先: なし

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md`
- 対象: `skills/grill-to-pr-loop/scripts/check_prereqs.py`, `skills/issue-implementation-loop/scripts/_common.py`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --json`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成
- 理由: 今回はユーザーが subagent / delegation を明示しておらず、local verification で完了状態を記録する。
- 検証結果: `python3 -m unittest discover -s skills/grill-to-pr-loop/tests` は 4 tests OK。`python3 -m unittest discover -s skills/issue-implementation-loop/tests` は 47 tests OK。`check_prereqs.py --phase execution --json` は repo-local `skills/issue-implementation-loop/SKILL.md` を選択。
