# インデックス

wiki の最初の navigation surface として使います。durable page はすべて 1 回だけ載せ、1 行 summary を付けます。現役一覧には canonical page だけを残します。

## ソース

- [2026-06-08 LLM Wiki Draft Review And Canonicalize Design](wiki/sources/2026-06-08-llm-wiki-draft-review-and-canonicalize-design.md) — `llm-wiki` skill に `draft-review` と `canonicalize` を first-class mode として追加する添付設計の source summary。
- [Grill To PR Loop スキル分割・非停止実行 詳細設計 v2](wiki/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md) — `grill-to-pr-loop` を composition skill と `issue-implementation-loop` execution skill に分割する添付設計の source summary。
- [2026-06-25 Loop Skill Architecture V3 Design](wiki/sources/2026-06-25-loop-skill-architecture-v3-design.md) — loop skill の context contract、worker packet、resume brief、operation routing を整理する添付設計の source summary。
- [Skill Repository Optimization V4 Design](wiki/sources/2026-06-26-skill-repository-optimization-v4-design.md) — PR #19 後の loop skill / llm-wiki context contract、artifact freshness、CI regression 固定の source summary。
- [2026-06-28 Portfolio OS Task Backend Plugin / Skill Handoff](wiki/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md) — Portfolio OS の task state-free 方針を保った task-management skill と GitHub MCP Server first routing の handoff source summary。

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
- [Grill To PR Loop Branch Policy Spec](wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md) — `grill-to-pr-loop` / `issue-implementation-loop` の branch、worktree、commit、integration branch 推奨運用を実装契約化する spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, branch policy, worktree reservation, epic_base, scoped commit, integration branch, PR_READY, ブランチ, コミット
- [Grill To PR Loop Branch Policy Issues](wiki/syntheses/grill-to-pr-loop-branch-policy-issues.md) — branch policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, branch policy, local issue, blocker graph, ローカルIssue, ブランチ運用
- [Issue Implementation Loop Context Policy Spec](wiki/syntheses/issue-implementation-loop-context-policy-spec.md) — `issue-implementation-loop` の context/session policy と entrypoint budget を契約化する spec。
  検索語: issue-implementation-loop, context policy, session semantics, worker packet, Execution Envelope, コンテキスト, セッション
- [Issue Implementation Loop Context Policy Issues](wiki/syntheses/issue-implementation-loop-context-policy-issues.md) — context/session policy 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, context policy, local issue, blocker graph, ローカルIssue, コンテキスト
- [Loop Skill Context Optimization Spec](wiki/syntheses/loop-skill-context-optimization-spec.md) — `grill-to-pr-loop` と `issue-implementation-loop` の context 最適化、reference 分割、repo-local skill root 優先 hardening の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, context optimization, reference split, skill root, repo-local, コンテキスト最適化
- [Loop Skill Context Optimization Issues](wiki/syntheses/loop-skill-context-optimization-issues.md) — loop skill context optimization 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, reference routing, skill root, ローカルIssue
- [Issue Implementation Loop Common Lib Split Spec](wiki/syntheses/issue-implementation-loop-common-lib-split-spec.md) — `issue-implementation-loop` の `_common.py` と単一巨大 test file を internal common lib / behavior-domain tests へ分割する後続実装契約。
  検索語: issue-implementation-loop, common lib, _common.py, scripts/lib, test split, context optimization, skill split, コンテキスト最適化
- [Issue Implementation Loop Common Lib Split Issues](wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md) — common lib split 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, local issue, blocker graph, common lib, _common.py, tests, ローカルIssue
- [Loop Skill Architecture V3 Spec](wiki/syntheses/loop-skill-architecture-v3-spec.md) — `grill-to-pr-loop` / `issue-implementation-loop` の context contract、operation selection、worker packet、resume brief を実装契約化する Spec Gate draft。
  検索語: grill-to-pr-loop, issue-implementation-loop, context-contract, worker packet, resume brief, operation routing, コンテキスト最適化
- [Loop Skill Architecture V3 Issues](wiki/syntheses/loop-skill-architecture-v3-issues.md) — loop skill architecture v3 実装の日本語 local-first issue ledger と統合 verification evidence。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, context-contract, worker packet, resume brief, ローカルIssue
- [Skill Repository Optimization V4 Spec](wiki/syntheses/skill-repository-optimization-v4-spec.md) — PR #19 後の read-set 正本化、推定 token budget、Worker Packet V2、Resume Brief V2、`llm-wiki` contract、CI 固定の Spec / Issue / Execution Plan Gate 承認済み契約。
  検索語: skill repository optimization, grill-to-pr-loop, issue-implementation-loop, llm-wiki, context-contract, token budget, worker packet v2, resume brief v2, CI, コンテキスト最適化
- [Skill Repository Optimization V4 Issues](wiki/syntheses/skill-repository-optimization-v4-issues.md) — Skill Repository Optimization V4 の local-first integration ledger。SRO4-001 から SRO4-006 の実装状態、review range、full verification、canonical context CLI、wrapper / workflow shim 削除、remote policy、residual risks を集約する。
  検索語: skill repository optimization, local issue, blocker graph, SRO4, context-contract, Worker Packet V2, Resume Brief V2, llm-wiki, final integration, canonical CLI, wrapper removal, residual risks, local_only, ローカルIssue, 統合検証, 残リスク
- [Skill Repository Optimization V4 Execution Envelope](wiki/syntheses/skill-repository-optimization-v4-execution-envelope.json) — V4 実装ループの local-only Execution Envelope、worker-only policy、branch/worktree reservation、prepare 検証済み実行契約。
  検索語: skill repository optimization, execution envelope, worker_context_required, local_only, SRO4, worktree reservation, 実行計画
- [Skill Repository Optimization V4 Context Baseline](wiki/syntheses/skill-repository-optimization-v4-context-baseline.json) — SRO4-001 で固定した loop skill operation context metrics baseline。
  検索語: skill repository optimization, SRO4-001, context baseline, operation metrics, word count, grill-to-pr-loop, issue-implementation-loop
- [Loop Skill 運用単純化仕様](wiki/syntheses/loop-skill-operational-simplicity-spec.md) — loop 系 skill の適用基準、役割境界モデル、workflow complexity レポートを追加する Spec Gate 承認済み契約。
  検索語: 適用基準, 役割境界モデル, 複雑性, grill-to-pr-loop, issue-implementation-loop, operational simplicity, workflow complexity, mental model, コンテキスト最適化
- [Loop Skill 運用単純化 Issue 台帳](wiki/syntheses/loop-skill-operational-simplicity-issues.md) — loop 系 skill 運用単純化の日本語 local-first 最終台帳。LSOS-001 から LSOS-004 の実装証跡、レビュー結果、全体検証、remote boundary、draft PR #22 を集約する。
  検索語: ローカルIssue, 実装証跡, レビュー結果, 最終台帳, 運用単純化, draft PR #22, grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, workflow complexity, role boundary
- [Loop Skill 運用単純化 Input Packet](wiki/syntheses/loop-skill-operational-simplicity-input-packet.json) — LSOS-001 から LSOS-004 を local-only で実行する承認済み normalized input packet。
  検索語: 実行計画, 承認済み packet, loop skill operational simplicity, execution packet, input packet, LSOS, local_only
- [Loop Skill 運用単純化 Execution Envelope](wiki/syntheses/loop-skill-operational-simplicity-execution-envelope.json) — LSOS 実装ループの local-only Execution Envelope、worker-only policy、branch/worktree reservation、prepare 検証済み実行契約。
  検索語: 実行計画, 実行 envelope, worker_context_required, local_only, LSOS, worktree reservation, loop skill operational simplicity
- [Grill To PR Loop Epic Base Delivery Policy Spec](wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-spec.md) — issue PR を `codex/<epic-id>/epic-base` に集約し、issue PR は guarded agent merge、final PR merge は human-only とする delivery policy。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, batch_issue_prs, issue PR, final PR, merge policy, review cycles, PR配送
- [Grill To PR Loop Epic Base Delivery Policy Issues](wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-issues.md) — epic-base delivery policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, epic-base, delivery policy, local issue, blocker graph, ローカルIssue, PR配送
- [Grill To PR Loop Epic Base Lifecycle Hardening Spec](wiki/syntheses/grill-to-pr-loop-epic-base-lifecycle-hardening-spec.md) — `epic_base` を検証可能な delivery/integration branch resource として lifecycle 管理に載せる hardening spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, branch lifecycle, reconcile, pr_merged, final PR, ブランチ統制
- [Portfolio OS Install Review And Procedure](wiki/syntheses/portfolio-os-install-review-and-procedure.md) — `skills` repo に Portfolio OS 固有 runtime を混ぜないためのレビュー結果と導入手順。
- [Portfolio OS Task Backend Plugin Skill Spec](wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md) — Portfolio OS task state-free 方針を保つ薄い task-management plugin package / primary skill / GitHub MCP Server first routing の Spec Gate 承認済み仕様。
  検索語: Portfolio OS, task backend, task-management, plugin package, primary skill, GitHub Projects, GitHub MCP Server, Hermes Agent, TaskDraft, TaskRef, TaskQuery, TaskSnapshot, TaskBackendRoute, TaskBackendDestination, adapter dispatch, operation envelope, connection_ref, destination_ref, work_unit_id, work_unit_name, inbox, routing, preview, approval gate
- [Portfolio OS Task Backend Plugin Skill Issues](wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md) — `portfolio-os-task-backend-plugin-skill` の Issue Gate 承認済み local-first ledger。POTASK-001 から POTASK-009、blocker graph、acceptance criteria を定義する。
  検索語: Portfolio OS, task backend, task-management, local issue, Issue Gate, POTASK, blocker graph, adapter dispatch, TaskDraft, TaskBackendRoute, TaskBackendDestination
- [Portfolio OS Task Backend Plugin Skill Input Packet](wiki/syntheses/portfolio-os-task-backend-plugin-skill-input-packet.json) — `portfolio-os-task-backend-plugin-skill` の Execution Plan Gate 承認済み input packet。承認済み POTASK-001 から POTASK-009 の source、acceptance criteria、write scope、dependencies、local-only delivery intent を正規化する。
  検索語: Portfolio OS, task backend, task-management, input packet, Execution Plan Gate, issue-implementation-loop, POTASK, write scope, dependencies, local_only

## クエリ起点成果物

_現在なし。_
