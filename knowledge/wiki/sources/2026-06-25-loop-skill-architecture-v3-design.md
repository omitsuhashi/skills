# 2026-06-25 Loop Skill Architecture V3 Design

## 概要

添付設計は、`grill-to-pr-loop` と `issue-implementation-loop` を 2 つの user-facing loop skill として維持しつつ、context 読み込み量、routing の重複、worker packet の肥大化、resume 時の過剰読込を抑えるための v3 詳細設計である。

設計正本の推奨保存先として `knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md` が指定されている。これはこの repository の durable spec routing と一致する。

## 主要 claim

- ユーザーが直接呼ぶ loop skill は `grill-to-pr-loop` と `issue-implementation-loop` の 2 つに固定する。
- scheduler、execution-envelope、dependency-graph、runtime-state、worktree-lifecycle、review-gate、human-wait、remote-delivery、worker-contract、context-manager は独立 skill にせず、`issue-implementation-loop` の reference、schema、script、internal Python module として保持する。
- `SKILL.md` は `context-contract.toml` を読み、operation を 1 つ選び、base reference と operation-specific reference だけを読む構造に寄せる。
- `grill-to-pr-loop/SKILL.md` は 850 words 以下、`issue-implementation-loop/SKILL.md` は 520 words 以下、default prompt は各 32 words 以下を目標にする。
- worker packet は paths-first とし、full spec / ledger を貼らず、default 450 words、hard limit 800 words を超えた場合は fail-fast にする。
- resume brief は 600 words 以下の派生 cache とし、canonical state は execution envelope、runtime state、events.jsonl に置く。
- `_common.py` は internal lib へ分割し、移行期間中は互換 re-export facade とする。
- context validator と inspection script を追加し、operation ごとの read set と word budget を検証可能にする。

## 現 checkout への反映状況

2026-06-25 時点の current checkout では、既存 `loop-skill-context-optimization` と `issue-implementation-loop-common-lib-split` の実装により、以下はすでに完了済みである。

- `grill-to-pr-loop/references/workflow-contract.md` は router 化され、planning、local issue ledger、execution handoff、remote delivery、common mistakes の one-level references に分割済み。
- repo-local skill root 優先の hardening は実装済み。
- `issue-implementation-loop/scripts/lib/issue_implementation_loop/` は存在し、validation、scheduler、delivery、git、skill discovery が domain module へ分割済み。
- `issue-implementation-loop/tests/` は behavior domain ごとの test file に分割済み。

未実装または未完了の主な領域は次である。

- `context-contract.toml` と operation read-set/budget validator。
- `scripts/validate_loop_skill_context.py` と `scripts/inspect_loop_skill_context.py`。
- `select_operation.py` による構造化 operation selection。
- worker packet schema/template/builder/validator。
- resume brief template/builder。
- `grill-to-pr-loop/SKILL.md` の 850 words 以下への圧縮。
- default prompt から詳細 policy を抜く整理。

## 派生 synthesis

- [Loop Skill Architecture V3 Spec](../syntheses/loop-skill-architecture-v3-spec.md) — 添付設計と current checkout の差分を踏まえた Spec Gate 用の実装契約。

## 出典

- [raw/sources/2026-06-25-loop-skill-architecture-v3-design.md](../../raw/sources/2026-06-25-loop-skill-architecture-v3-design.md)
