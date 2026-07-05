# Loop Skill Codex 最適化仕様

## 問題設定 / 成功条件

loop 系 skill は planning と implementation の責務分離、context contract、worker packet をすでに持つ。一方で Codex の実行モデルでは、同一会話の肥大化、フェーズ承認後の commit 境界、planning branch と issue branch の混同が起きやすい。

成功条件は、次を機械検証可能な契約と reference に落とすこと。

- 新規 Execution Envelope が Codex 向け phase branch policy を持つ。
- planning docs / ledger / packet / approval evidence は issue branch に入れない。
- execution は fresh または compacted coordinator context から始まり、main planning session が worker にならない。
- `epic_base`、issue branch、integration branch の owner と作成タイミングが明確である。
- 既存 schema version `1` / `2` envelope は resume 互換を保つ。

## Epic ID

`loop-skill-codex-optimization`

## 採用した判断

- 新規 envelope は schema version `3` とし、`phase_branch_policy` を必須にする。
- schema version `1` / `2` は historical / resume artifact として引き続き受け入れる。
- `phase_branch_policy` は自由入力ではなく、validator / schema / template で固定値として扱う。
- planning branch、`epic_base`、issue branch、worker worktree、integration work item を別 resource として扱う。
- branch/worktree の詳細は `issue-implementation-loop` が所有し、`grill-to-pr-loop` は handoff で v3 envelope 作成を要求する。

## 非目標

- loop skill を単一 same-session implementation skill に戻さない。
- 既存 historical envelope を v3 へ一括書き換えない。
- GitHub issue 作成、push、PR 作成、merge、force push、destructive action は実行しない。
- 新しい standalone skill は追加しない。

## Issue 分解方針

今回の変更は小さな横断更新として同一作業で扱う。

- docs: `grill-to-pr-loop` handoff と `issue-implementation-loop` references を Codex phase branch policy に同期する。
- implementation: execution envelope schema/template/validator に v3 `phase_branch_policy` を追加する。
- regression: validation tests と grill-to-pr-loop docs tests で v3 policy、legacy v2 compatibility、planning/execution handoff wording を固定する。
- wiki: この仕様、`knowledge/index.md`、`knowledge/log.md` を更新する。

## 受け入れ条件

- `skills/issue-implementation-loop/assets/templates/execution-envelope.json` が `schema_version: 3` と `phase_branch_policy` を含む。
- `validate_execution_envelope.py` が schema version `3` で `phase_branch_policy` 欠落や不正値を拒否する。
- schema version `2` envelope は `phase_branch_policy` がなくても validation を通る。
- `skills/grill-to-pr-loop/references/execution-handoff.md` が Codex phase branch policy と fresh / compacted coordinator context を説明する。
- `skills/issue-implementation-loop/references/execution-envelope.md` と `worktree-lifecycle.md` が同じ branch ownership 語彙を使う。
- regression tests と context validators が通る。

## 検証方針 / コマンド

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 -m unittest discover -s scripts
python3 scripts/validate_skill_context.py --all
python3 scripts/validate_skill_architecture.py --all
python3 scripts/report_skill_context.py --all --json
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

## リモート書き込み方針

`local_only`。GitHub issue mirror、push、PR 作成、ready-for-review、merge はこの作業に含めない。

## 人間レビューゲート

この作業は既存 scope 内の Codex 最適化であり、remote write や destructive action は行わない。`phase_branch_policy` の値を変更する、schema version `1` / `2` の互換性を切る、または loop skill の role boundary を変える場合は人間判断を要求する。

## 停止条件 / 既知のリスク

- context budget が baseline から 10% 超過する。
- historical envelope validation が壊れる。
- worker-only policy を弱める変更が必要になる。
- dirty changes が planned write scope と競合する。

