# Issue Implementation Loop Context Policy Issues

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| issue-implementation-loop-context-policy | G2PR-001 | context / session policy を契約化する | 承認済み | 実行可能 | 実装済み | なし | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- G2PR-001: 実行可能; ブロック元 なし; ブロック先 なし

## G2PR-001

### Epic ID

`issue-implementation-loop-context-policy`

### タイトル

context / session policy を契約化する

### 作るもの

`issue-implementation-loop` の入口説明、Execution Envelope、worker contract、tests に context/session contract を追加し、skill entrypoint の肥大化と別セッション誤解を防ぐ。

### 受け入れ条件

- [x] `SKILL.md` の description が trigger-only で、workflow 要約語を含まない。
- [x] `SKILL.md` 本体が 520 words 以下である。
- [x] `SKILL.md` が「親 coordinator は同じセッションに残る」「ユーザー-owned Codex thread を自動作成しない」「parallel worker 不在時は承認済み serial fallback で続行できる」を明記している。
- [x] `execution-envelope` reference / schema / template が `context_policy` を持つ。
- [x] `validate_execution_envelope.py` が `context_policy` 欠落と不正 budget を拒否する。
- [x] `worker-contract` が durable paths-first packet と全文貼り付け禁止を説明している。
- [x] 既存の branch/base/commit policy tests が引き続き通る。
- [x] skill validation が `issue-implementation-loop` を通す。

### 非目標

- scheduler / runtime recovery の挙動変更はしない。
- GitHub issue、push、PR、merge は実行しない。
- worker を必ず parallel / subagent 実行する契約にはしない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: なし

### 必要な文脈

- 仕様: `knowledge/wiki/syntheses/issue-implementation-loop-context-policy-spec.md`
- 既存 skill split: `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md`
- 既存 branch policy: `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md`

### 検証

- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json`
- `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/issue-implementation-loop-context-policy-input-packet.json`

### 実装レビュー

- 状態: 未実施
- レビュー範囲: 未作成
- 理由: 現在の Codex multi-agent tool は、ユーザーが明示的に subagent / delegation を依頼した場合のみ reviewer subagent を起動できるため。
- PR: 未作成。remote write 未承認かつ今回の delivery intent は local-only。
