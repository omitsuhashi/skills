# インデックス

wiki の最初の navigation surface として使います。durable page はすべて 1 回だけ載せ、1 行 summary を付けます。現役一覧には canonical page だけを残します。

## ソース

- [2026-06-08 LLM Wiki Draft Review And Canonicalize Design](wiki/sources/2026-06-08-llm-wiki-draft-review-and-canonicalize-design.md) — `llm-wiki` skill に `draft-review` と `canonicalize` を first-class mode として追加する添付設計の source summary。
- [Grill To PR Loop スキル分割・非停止実行 詳細設計 v2](wiki/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md) — `grill-to-pr-loop` を composition skill と `issue-implementation-loop` execution skill に分割する添付設計の source summary。

## エンティティ

_現在なし。_

## 概念

_現在なし。_

## シンセシス

- [LLM Wiki Draft Review And Canonicalize Goal Spec](wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md) — Goal command で `skills/llm-wiki` を更新するための詳細実装契約。
- [Grill To PR Loop Issue Implementation Review Gate Plan](wiki/syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md) — `skills/grill-to-pr-loop` に issue 単位の実装レビューゲートを追加するための実装計画。
  検索語: grill-to-pr-loop, requesting-code-review, 実装レビュー, issue review, PR review, review gate, implementation plan
- [Grill To PR Loop Skill Split V2 Spec](wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md) — `issue-implementation-loop` 新設と `grill-to-pr-loop` composition 縮小の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, execution envelope, worktree reservation, scheduler, human wait, runtime state, skill split, implementation plan
- [Grill To PR Loop Skill Split V2 Issues](wiki/syntheses/grill-to-pr-loop-skill-split-v2-issues.md) — skill split 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, ローカルIssue, ブロッカー
- [Portfolio OS Install Review And Procedure](wiki/syntheses/portfolio-os-install-review-and-procedure.md) — `skills` repo に Portfolio OS 固有 runtime を混ぜないためのレビュー結果と導入手順。

## クエリ起点成果物

_現在なし。_
