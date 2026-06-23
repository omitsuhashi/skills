# Grill To PR Loop スキル分割・非停止実行 詳細設計 v2

## 概要

`skills/grill-to-pr-loop` を、設計から PR delivery までの composition skill と、承認済み Issue 群を非停止で実装する reusable execution skill に分割する設計資料。

## 主要 claim

- 新設するユーザー向け skill は `issue-implementation-loop` だけにする。
- `execution-envelope`、worktree reservation、typed dependency edge、event-driven scheduler、scoped human wait、durable resume、issue implementation review gate は独立 skill ではなく、`issue-implementation-loop` の references / deterministic helper として持つ。
- `grill-to-pr-loop` は `grill-with-docs`、`to-prd`、`to-issues` を使う上流 composition として、spec / issue decomposition / execution packet / optional PR delivery を所有する。
- `issue-implementation-loop` は approved work-item packet から Execution Envelope を作り、依存関係対応の scheduling、worktree lifecycle、runtime state、issue-scoped review、PR-ready 判定を所有する。
- runtime state は issue branch の tracked file へ置かず、既定では `$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/` に置く。
- 人間待ちは既定で issue scope に局所化し、無関係な runnable work は継続する。

## open question

- 実行 worker / reviewer をどのプラットフォームで並列起動できるかは実行環境依存。skill は capability preflight と serial fallback policy を持つが、外部 LLM router は作らない。
- 将来 `non-blocking-workflow-core` を抽出するかは、Git/worktree/SHA を除いた共通 state machine の第2利用者が現れてから判断する。

## 関連ページ

- [Grill To PR Loop Skill Split V2 Spec](../syntheses/grill-to-pr-loop-skill-split-v2-spec.md) は、この source を実装契約へ圧縮した spec。
- [Grill To PR Loop Issue Implementation Review Gate Plan](../syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md) は、前段で追加済みの issue implementation review gate 設計。

## 出典

- [raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md](../../raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md)
