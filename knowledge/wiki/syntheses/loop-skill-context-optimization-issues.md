# Loop Skill Context Optimization Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-context-optimization | G2PR-001 | context optimization spec と local ledger を正本化する | 承認済み | 実行可能 | 実装済み | なし | G2PR-002, G2PR-003 | 未作成 | 実施済み | draft PR #15 |
| loop-skill-context-optimization | G2PR-002 | `grill-to-pr-loop` の workflow reference を分割する | 承認済み | 実行可能 | 実装済み | G2PR-001 | G2PR-003 | 未作成 | 実施済み | draft PR #15 |
| loop-skill-context-optimization | G2PR-003 | repo-local skill root 優先と回帰テストを追加する | 承認済み | 実行可能 | 実装済み | G2PR-001, G2PR-002 | なし | 未作成 | 実施済み | draft PR #15 |

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

- 状態: 実施済み
- レビュー範囲: `9430e1b3d085832cda76075218c89cb02b0b7388..73d4f1b57075e11d5540b8c2b8c648ea49789626`
- 理由: ユーザーが `$superpowers:requesting-code-review` を明示したため、read-only reviewer で PR 差分を確認した。
- 検証結果: Critical 0。Important 1 件は `GitHub Mirror Gate` の routing 不整合で、review-fix で `remote-delivery.md` へ gate 手順を集約した。`validate_input_packet.py` は `INPUT PACKET OK`。

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

- 実行状態: 実行可能
- ブロック元: G2PR-001
- ブロック先: G2PR-003

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md`
- 対象: `skills/grill-to-pr-loop/SKILL.md`, `skills/grill-to-pr-loop/references/`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `wc -w skills/grill-to-pr-loop/references/*.md`

### 実装レビュー

- 状態: 実施済み
- レビュー範囲: `9430e1b3d085832cda76075218c89cb02b0b7388..73d4f1b57075e11d5540b8c2b8c648ea49789626`
- 理由: ユーザーが `$superpowers:requesting-code-review` を明示したため、read-only reviewer で PR 差分を確認した。
- 検証結果: Critical 0。Important 1 件は `GitHub Mirror Gate` の routing 不整合で、review-fix で修正し、`skills/grill-to-pr-loop/tests` に mirror gate routing regression を追加した。

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

- 実行状態: 実行可能
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

- 状態: 実施済み
- レビュー範囲: `9430e1b3d085832cda76075218c89cb02b0b7388..73d4f1b57075e11d5540b8c2b8c648ea49789626`
- 理由: ユーザーが `$superpowers:requesting-code-review` を明示したため、read-only reviewer で PR 差分を確認した。
- 検証結果: Critical 0。repo-local root precedence は reviewer 再実行でも問題なし。`python3 -m unittest discover -s skills/issue-implementation-loop/tests` は 47 tests OK。`check_prereqs.py --phase execution --json` は repo-local `skills/issue-implementation-loop/SKILL.md` を選択。
