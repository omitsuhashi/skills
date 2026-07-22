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

- [GitHub Projects 直接接続型 Task Management Skill 仕様](wiki/syntheses/direct-github-projects-task-management/spec.md) — 1個のcaller-selected Projectへ複数repositoryのIssueを集約し、standalone skillからGitHub MCPへ直接接続するWritten Spec Gate承認済みのcurrent設計。
  検索語: task-management, GitHub Projects, GitHub MCP, Issue, standalone skill, project_url, inbox repository, repository work unit, Status, Priority, Due date, approval policy, fail closed, タスク管理, 直接接続, 承認, セットアップ
- [GitHub Projects 直接接続型 Task Management Skill Issue 台帳](wiki/syntheses/direct-github-projects-task-management/issues.md) — DGPTM-001からDGPTM-004へstandalone skill、direct MCP contract、旧plugin削除、historical supersessionを依存順に分解したIssue Gate承認済み台帳。
  検索語: task-management, GitHub Projects, GitHub MCP, DGPTM, local issue, Issue Gate, blocker graph, plugin removal, standalone skill, ローカルIssue, ブロッカー, 移行
- [GitHub Projects Direct Task Management Skill Implementation Plan](wiki/syntheses/direct-github-projects-task-management/implementation-plan.md) — DGPTM-001からDGPTM-004をscaffold、RED/GREEN、旧plugin削除、fresh evaluation、local closeoutの順で実装するExecution Plan Gate candidate。
  検索語: task-management, GitHub Projects, implementation plan, writing-plans, TDD, RED GREEN, plugin removal, forward test, 実装計画, テスト駆動, 検証
- [GitHub Projects Direct Task Management Skill Input Packet](wiki/syntheses/direct-github-projects-task-management/input-packet.json) — approved spec bindingとIssue Gate承認済みDGPTM-001〜DGPTM-004を`local_only`で固定したsealed Input Packet v2。
  検索語: task-management, GitHub Projects, Input Packet v2, approved spec binding, execution intent, DGPTM, local_only, 実行契約, 承認済み仕様
- [LLM Wiki Draft Review And Canonicalize Goal Spec](wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md) — Goal command で `skills/llm-wiki` を更新するための詳細実装契約。
- [Grill To PR Loop Issue Implementation Review Gate Plan](wiki/syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md) — `skills/grill-to-pr-loop` に issue 単位の実装レビューゲートを追加するための実装計画。
  検索語: grill-to-pr-loop, requesting-code-review, 実装レビュー, issue review, PR review, review gate, implementation plan
- [Loop Review Governance Spec](wiki/syntheses/loop-review-governance-spec.md) — Issue 意図適合レビューを必須にし、future-only hardening は通常レビュー観点から外し、明示依頼または current PR delivery risk の candidate だけを制御する Spec Gate 承認済み仕様。
  検索語: loop review governance, issue intent, hardening candidate, future-only hardening, safety escalation, final PR, human decision, requesting-code-review, context budget, 実装レビュー, 堅牢化, 人間判断
- [Loop Review Governance Issue 台帳](wiki/syntheses/loop-review-governance-issues.md) — `loop-review-governance` の Issue Gate 承認済み local issue ledger。LRG-001 から LRG-005 の blocker graph、acceptance criteria、remote policy を定義する。
  検索語: loop review governance, local issue, Issue Gate, LRG, blocker graph, hardening candidate, requesting-code-review, context budget, ローカルIssue, 堅牢化
- [Loop Review Governance Input Packet](wiki/syntheses/loop-review-governance-input-packet.json) — historical / non-executable な Input Packet v1。過去の LRG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: loop review governance, input packet, Execution Plan Gate, issue-implementation-loop, LRG, write scope, dependencies, local_only, 実行計画
- [Loop Review Governance Execution Envelope](wiki/syntheses/loop-review-governance-execution-envelope.json) — historical / non-executable な Execution Envelope v2。過去の LRG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: loop review governance, execution envelope, worker_context_required, batch_issue_prs, requesting-code-review, hardening candidate, pending_decision, draft PR, worktree reservation
- [Loop Review Governance Final Delivery Plan](wiki/syntheses/loop-review-governance-final-delivery-plan.json) — `loop-review-governance` の draft final PR 作成用 delivery plan。head は `codex/loop-review-governance/epic-base`、base は `main`、draft only。
  検索語: loop review governance, delivery plan, draft PR, final PR, epic-base, hardening decision
- [Loop Review Governance Handoff Brief](wiki/syntheses/loop-review-governance-handoff-brief.md) — Execution Plan Gate 後に raw transcript へ依存せず `issue-implementation-loop` を再開するための bounded handoff brief。
  検索語: loop review governance, handoff brief, Execution Plan Gate, runtime root, worker packet, hardening_candidate, local_only
- [Loop Review Governance Hardening Candidate Decisions](wiki/syntheses/loop-review-governance-hardening-decisions.md) — 既存 `hardening_candidate` 4 件を `deferred_follow_up` とし、future-only hardening を通常レビュー観点から外す判断を記録する decision artifact。
  検索語: loop review governance, hardening candidate, future-only hardening, deferred follow-up, review scope, source review, registry path, 保存場所, 出典, 堅牢化, 人間判断
- [Grill To PR Loop Skill Split V2 Spec](wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md) — `issue-implementation-loop` 新設と `grill-to-pr-loop` composition 縮小の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, execution envelope, worktree reservation, scheduler, human wait, runtime state, skill split, implementation plan
- [Grill To PR Loop Skill Split V2 Issues](wiki/syntheses/grill-to-pr-loop-skill-split-v2-issues.md) — skill split 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, ローカルIssue, ブロッカー
- [Grill To PR Loop Skill Split V2 Input Packet](wiki/syntheses/grill-to-pr-loop-skill-split-v2-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Grill To PR Loop Skill Split V2 Execution Envelope](wiki/syntheses/grill-to-pr-loop-skill-split-v2-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Grill To PR Loop Branch Policy Spec](wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md) — `grill-to-pr-loop` / `issue-implementation-loop` の branch、worktree、commit、integration branch 推奨運用を実装契約化する spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, branch policy, worktree reservation, epic_base, scoped commit, integration branch, PR_READY, ブランチ, コミット
- [Grill To PR Loop Branch Policy Issues](wiki/syntheses/grill-to-pr-loop-branch-policy-issues.md) — branch policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, branch policy, local issue, blocker graph, ローカルIssue, ブランチ運用
- [Grill To PR Loop Branch Policy Input Packet](wiki/syntheses/grill-to-pr-loop-branch-policy-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Grill To PR Loop Branch Policy Execution Envelope](wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Issue Implementation Loop Context Policy Spec](wiki/syntheses/issue-implementation-loop-context-policy-spec.md) — `issue-implementation-loop` の context/session policy と entrypoint budget を契約化する spec。
  検索語: issue-implementation-loop, context policy, session semantics, worker packet, Execution Envelope, コンテキスト, セッション
- [Issue Implementation Loop Context Policy Issues](wiki/syntheses/issue-implementation-loop-context-policy-issues.md) — context/session policy 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, context policy, local issue, blocker graph, ローカルIssue, コンテキスト
- [Issue Implementation Loop Context Policy Input Packet](wiki/syntheses/issue-implementation-loop-context-policy-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Loop Skill Context Optimization Spec](wiki/syntheses/loop-skill-context-optimization-spec.md) — `grill-to-pr-loop` と `issue-implementation-loop` の context 最適化、reference 分割、repo-local skill root 優先 hardening の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, context optimization, reference split, skill root, repo-local, コンテキスト最適化
- [Loop Skill Context Optimization Issues](wiki/syntheses/loop-skill-context-optimization-issues.md) — loop skill context optimization 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, reference routing, skill root, ローカルIssue
- [Loop Skill Context Optimization Input Packet](wiki/syntheses/loop-skill-context-optimization-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Loop Skill Codex 最適化仕様](wiki/syntheses/loop-skill-codex-optimization-spec.md) — Codex の planning / execution context と phase branch policy に合わせ、Execution Envelope v3、branch ownership、fresh / compacted coordinator handoff を固定する仕様。
  検索語: Codex, phase_branch_policy, schema version 3, execution envelope, planning branch, epic_base, issue branch, worktree, grill-to-pr-loop, issue-implementation-loop
- [Issue Implementation Loop Common Lib Split Spec](wiki/syntheses/issue-implementation-loop-common-lib-split-spec.md) — `issue-implementation-loop` の `_common.py` と単一巨大 test file を internal common lib / behavior-domain tests へ分割する後続実装契約。
  検索語: issue-implementation-loop, common lib, _common.py, scripts/lib, test split, context optimization, skill split, コンテキスト最適化
- [Issue Implementation Loop Common Lib Split Issues](wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md) — common lib split 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, local issue, blocker graph, common lib, _common.py, tests, ローカルIssue
- [Issue Implementation Loop Common Lib Split Input Packet](wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Loop Skill Architecture V3 Spec](wiki/syntheses/loop-skill-architecture-v3-spec.md) — `grill-to-pr-loop` / `issue-implementation-loop` の context contract、operation selection、worker packet、resume brief を実装契約化する Spec Gate draft。
  検索語: grill-to-pr-loop, issue-implementation-loop, context-contract, worker packet, resume brief, operation routing, コンテキスト最適化
- [Loop Skill Architecture V3 Issues](wiki/syntheses/loop-skill-architecture-v3-issues.md) — loop skill architecture v3 実装の日本語 local-first issue ledger と統合 verification evidence。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, context-contract, worker packet, resume brief, ローカルIssue
- [Loop Skill Architecture V3 Input Packet](wiki/syntheses/loop-skill-architecture-v3-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Loop Skill Architecture V3 Execution Envelope](wiki/syntheses/loop-skill-architecture-v3-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Skill Repository Optimization V4 Spec](wiki/syntheses/skill-repository-optimization-v4-spec.md) — PR #19 後の read-set 正本化、推定 token budget、Worker Packet V2、Resume Brief V2、`llm-wiki` contract、CI 固定の Spec / Issue / Execution Plan Gate 承認済み契約。
  検索語: skill repository optimization, grill-to-pr-loop, issue-implementation-loop, llm-wiki, context-contract, token budget, worker packet v2, resume brief v2, CI, コンテキスト最適化
- [Skill Repository Optimization V4 Issues](wiki/syntheses/skill-repository-optimization-v4-issues.md) — Skill Repository Optimization V4 の local-first integration ledger。SRO4-001 から SRO4-006 の実装状態、review range、full verification、canonical context CLI、wrapper / workflow shim 削除、remote policy、residual risks を集約する。
  検索語: skill repository optimization, local issue, blocker graph, SRO4, context-contract, Worker Packet V2, Resume Brief V2, llm-wiki, final integration, canonical CLI, wrapper removal, residual risks, local_only, ローカルIssue, 統合検証, 残リスク
- [Skill Repository Optimization V4 Input Packet](wiki/syntheses/skill-repository-optimization-v4-input-packet.json) — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [Skill Repository Optimization V4 Execution Envelope](wiki/syntheses/skill-repository-optimization-v4-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: skill repository optimization, execution envelope, worker_context_required, local_only, SRO4, worktree reservation, 実行計画
- [Skill Repository Optimization V4 Context Baseline](wiki/syntheses/skill-repository-optimization-v4-context-baseline.json) — SRO4-001 で固定した loop skill operation context metrics baseline。
  検索語: skill repository optimization, SRO4-001, context baseline, operation metrics, word count, grill-to-pr-loop, issue-implementation-loop
- [Loop Skill 運用単純化仕様](wiki/syntheses/loop-skill-operational-simplicity-spec.md) — loop 系 skill の適用基準、役割境界モデル、workflow complexity レポートを追加する Spec Gate 承認済み契約。
  検索語: 適用基準, 役割境界モデル, 複雑性, grill-to-pr-loop, issue-implementation-loop, operational simplicity, workflow complexity, mental model, コンテキスト最適化
- [Loop Skill 運用単純化 Issue 台帳](wiki/syntheses/loop-skill-operational-simplicity-issues.md) — loop 系 skill 運用単純化の日本語 local-first 最終台帳。LSOS-001 から LSOS-004 の実装証跡、レビュー結果、全体検証、remote boundary、draft PR #22 を集約する。
  検索語: ローカルIssue, 実装証跡, レビュー結果, 最終台帳, 運用単純化, draft PR #22, grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, workflow complexity, role boundary
- [Loop Skill 運用単純化 Input Packet](wiki/syntheses/loop-skill-operational-simplicity-input-packet.json) — historical / non-executable な Input Packet v1。過去の LSOS 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: 実行計画, 承認済み packet, loop skill operational simplicity, execution packet, input packet, LSOS, local_only
- [Loop Skill 運用単純化 Execution Envelope](wiki/syntheses/loop-skill-operational-simplicity-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の LSOS 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: 実行計画, 実行 envelope, worker_context_required, local_only, LSOS, worktree reservation, loop skill operational simplicity
- [Loop Skill Context Compaction Spec](wiki/syntheses/loop-skill-context-compaction-spec.md) — loop 系 skill の session context pressure 65% 圧縮 trigger、保持/圧縮分類、phase 別 compaction policy を定義する Spec Gate 承認済み仕様。
  検索語: grill-to-pr-loop, issue-implementation-loop, context compaction, session pressure, 65%, 圧縮, 忘れてはいけないこと, handoff brief, resume brief, worker packet
- [Loop Skill Context Compaction Issues](wiki/syntheses/loop-skill-context-compaction-issues.md) — context compaction 実装の日本語 local-first ledger。LSCC-001 から LSCC-005 の implementation evidence、review result、verification result、remote policy を集約する。
  検索語: LSCC, Issue Gate, local issue ledger, context compaction, carry-forward capsule, phase transition GC, conditional overlay, local_only, implementation evidence, review result, verification result
- [Loop Skill Context Compaction Input Packet](wiki/syntheses/loop-skill-context-compaction-input-packet.json) — historical / non-executable な Input Packet v1。過去の LSCC 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSCC, input packet, Execution Plan Gate, issue-implementation-loop, worker-only, local_only, write scope, dependency graph
- [Loop Skill Context Compaction Execution Envelope](wiki/syntheses/loop-skill-context-compaction-execution-envelope.json) — historical / non-executable な Execution Envelope v2。過去の LSCC 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSCC, execution envelope, worker_context_required, coordinator_may_implement, local_only, session_compaction, hard_stop_percent, worktree reservation
- [Loop Skill Context Compaction Handoff Brief](wiki/syntheses/loop-skill-context-compaction-handoff-brief.md) — Execution Plan Gate 後に raw transcript へ依存せず再開するための bounded handoff brief。
  検索語: LSCC, handoff brief, carry-forward capsule, resume, runtime root, worker packet, context compaction
- [Loop Skill 自動継続 Gate 仕様](wiki/syntheses/loop-skill-autonomous-gates-spec.md) — `Execution Plan Gate` と `Live Root Gate` を agent preflight + commit boundary として自動継続し、承認済み delivery policy 内の draft final PR 作成を追加承認なしに行う Spec Gate 承認済み仕様。
  検索語: Execution Plan Gate, Live Root Gate, Adapter Availability Gate, final PR, draft PR, approved_actions, auto-continue, grill-to-pr-loop, issue-implementation-loop, remote policy, human-only merge
- [Loop Skill 自動継続 Gate Issue 台帳](wiki/syntheses/loop-skill-autonomous-gates-issues.md) — `loop-skill-autonomous-gates` の Issue Gate 承認済み日本語 local-first 最終台帳。LSAG-001 から LSAG-006 の implementation evidence、review result、verification result、delivery evidence、remote 未実行境界を集約する。
  検索語: LSAG, Loop Skill 自動継続, local issue, Issue Gate, final ledger, 最終台帳, implementation evidence, review result, verification result, delivery evidence, blocker graph, Execution Plan Gate, Live Root Gate, Adapter Availability Gate, final PR, approved_actions
- [Loop Skill 自動継続 Gate Input Packet](wiki/syntheses/loop-skill-autonomous-gates-input-packet.json) — historical / non-executable な Input Packet v1。過去の LSAG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSAG, input packet, execution packet, Execution Plan Gate, auto-continue, issue-implementation-loop, batch_issue_prs, final PR, approved_actions, delivery evidence
- [Loop Skill 自動継続 Gate Execution Envelope](wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json) — historical / non-executable な Execution Envelope v1。過去の LSAG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSAG, execution envelope, worker_context_required, batch_issue_prs, final_pr_push_head, final_pr_create_draft, worktree reservation, auto-continue
- [Grill To PR Loop Epic Base Delivery Policy Spec](wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-spec.md) — issue PR を `codex/<epic-id>/epic-base` に集約し、issue PR は guarded agent merge、final PR merge は human-only とする delivery policy。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, batch_issue_prs, issue PR, final PR, merge policy, review cycles, PR配送
- [Grill To PR Loop Epic Base Delivery Policy Issues](wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-issues.md) — epic-base delivery policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, epic-base, delivery policy, local issue, blocker graph, ローカルIssue, PR配送
- [Grill To PR Loop Epic Base Lifecycle Hardening Spec](wiki/syntheses/grill-to-pr-loop-epic-base-lifecycle-hardening-spec.md) — `epic_base` を検証可能な delivery/integration branch resource として lifecycle 管理に載せる hardening spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, branch lifecycle, reconcile, pr_merged, final PR, ブランチ統制
- [Loop Skill Approved Spec Binding Artifact Lifecycle Revision](wiki/syntheses/approved-spec-binding-contract/spec.md) — Epic単位のtracked durable rootとGit common directory配下のuntracked runtime rootを分離し、Input Packetだけをapproval lockとしてGitに残すWritten Spec Gate承認済みrevision。
  検索語: approved spec binding, artifact lifecycle, epic directory, artifact root, input packet lock, untracked execution envelope, runtime root, Git common dir, ASBC-007, ASBC-008, ASBC-009
- [Loop Skill Approved Spec Binding Artifact Lifecycle Issues](wiki/syntheses/approved-spec-binding-contract/issues.md) — initial ASBC-001〜ASBC-006 evidenceを保持し、ASBC-007/ASBC-008 `COMPLETE`、ASBC-009 local `PR_READY`、controller review後のDraft PR #32更新pendingまでを集約する最終local ledger。
  検索語: ASBC-007, ASBC-008, ASBC-009, COMPLETE, PR_READY, artifact layout, runtime boundary, issue ledger, full verification, pending remote delivery, Draft PR 32
- [Loop Skill Approved Spec Binding Artifact Lifecycle Implementation Plan](wiki/syntheses/approved-spec-binding-contract/implementation-plan.md) — layout validation、current artifact migration/reseal、fresh-agent 3/3、full verification、local risk reviewとcontroller delivery境界を記録した実行plan。
  検索語: artifact lifecycle implementation plan, TDD, reseal, input packet, execution envelope, fresh evaluator, full verification, PR_READY, controller review, Draft PR 32
- [Loop Skill Approved Spec Binding Artifact Lifecycle Input Packet](wiki/syntheses/approved-spec-binding-contract/input-packet.json) — current executable Input Packet v2。承認済みconsolidated spec、six-part approval evidence、ASBC-007〜ASBC-009のexecution intentを同一Epic rootでsealする唯一のtracked machine-readable lock。
  検索語: ASBC-007, ASBC-008, ASBC-009, current Input Packet v2, approved spec binding, spec digest, approval evidence, per_action, executable artifact, seal
- [Portfolio OS Install Review And Procedure](wiki/syntheses/portfolio-os-install-review-and-procedure.md) — `skills` repo に Portfolio OS 固有 runtime を混ぜないためのレビュー結果と導入手順。
- [Decide In Order Skill 原案](wiki/sources/2026-07-17-decide-in-order-source-brief.md) — 目的、守るもの、許容損失、核心の問いから始める実行支援型 skill の一次資料と設計時の解釈。
  検索語: decide in order, decision ordering, task management, purpose, must protect, acceptable loss, core question, sunk cost, risk, review, 決める順番, 意思決定, 優先順位, サンクコスト, 見直し
- [Decide In Order Skill 設計](wiki/syntheses/decide-in-order-skill-design.md) — 実装済みの独立state-free skill、厳密な判断順序、疎な内部状態、適応的表示、DecisionRecord、task-management利用ポリシーと検証証跡。
  検索語: decide-in-order, decision support, DecisionFrame, DecisionRecord, light, deep, review, task-management integration, skill-creator, plugin-creator, 決める順番, 意思決定支援, 日次計画, 継続判断, 調査方針, 許容損失
- [Decide In Order Skill 実装計画](wiki/syntheses/2026-07-17-decide-in-order-implementation-plan.md) — skill-creator scaffold、contract tests、fresh-agent forward test、task-management integration、plugin回帰、wiki証跡同期を固定するtest-first実装計画。
  検索語: decide-in-order, implementation plan, skill-creator, plugin-creator, forward test, task-management integration, contract test, TDD, 実装計画, 意思決定支援, 回帰検証
- [Codex / Hermes Dual-host Authoring Contract 設計](wiki/syntheses/hermes-dual-host-authoring-contract-design.md) — skill / plugin のリポジトリ互換、Hermes discovery、live load を分離し、薄い作成指示、共通検証、Python 3.9 / 3.12 CI enforcementを実装・ローカル検証済みの設計。
  検索語: Hermes Agent, Codex, dual-host, SKILL.md, description.md, plugin.yaml, register(ctx), external_dirs, install, discovery, live load, skill creator, plugin creator, 作成指示, 互換性, インストール, 検証
- [Codex / Hermes Dual-host Authoring Contract 実装計画](wiki/syntheses/2026-07-17-hermes-dual-host-authoring-contract-implementation-plan.md) — 薄いauthoring guidance、標準ライブラリvalidator、既存skill/plugin導入契約、CIを4つのTDD単位で実装する計画。
  検索語: Hermes Agent, Codex, dual-host, implementation plan, AGENTS.md, validator, unittest, CI, TDD, SKILL.md, plugin.yaml, register(ctx), 実装計画, 作成ルール, 検証
- [Portfolio OS Task Backend Plugin Skill Spec](wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md) — Portfolio OS task state-free 方針を保つtask-management pluginの承認済み仕様。POTASK-010のbackend-neutral read facadeに加え、POTASK-011でconsumerからbackend差を隠すhost-owned route、initial local JSON backend、external MCP / provider plugin adapter、Hermes end-to-end call pathを定義する。
  検索語: Portfolio OS, task backend, task-management, plugin package, primary skill, local JSON, MCP, provider plugin, no gh, Hermes Agent, TaskDraft, TaskRef, TaskQuery, TaskSnapshot, TaskSnapshotResult, task_query, task-management-read, TaskBackendRoute, TaskBackendDestination, adapter dispatch, operation envelope, connection_ref, destination_ref, work_unit_id, work_unit_name, inbox, routing, preview, approval gate
- [Portfolio OS Task Backend Plugin Skill Issues](wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md) — `portfolio-os-task-backend-plugin-skill` の Issue Gate 承認済み local-first ledger。POTASK-001からPOTASK-011、blocker graph、acceptance criteria、POTASK-010/POTASK-011 local verified、PR #29を定義する。
  検索語: Portfolio OS, task backend, task-management, local issue, Issue Gate, POTASK-010, POTASK-011, provider adapter, local JSON, MCP, provider plugin, no gh, Hermes end-to-end, blocker graph, task-management-read, task_query, TaskSnapshotResult, adapter dispatch, TaskDraft, TaskBackendRoute, TaskBackendDestination
- [Portfolio OS Task Backend Plugin Skill Input Packet](wiki/syntheses/portfolio-os-task-backend-plugin-skill-input-packet.json) — historical / non-executable な Input Packet v1。過去の POTASK 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: Portfolio OS, task backend, task-management, input packet, Execution Plan Gate, issue-implementation-loop, POTASK, write scope, dependencies, local_only
- [Task Management Provider Adapters 実装計画](wiki/syntheses/2026-07-16-task-management-provider-adapters-implementation-plan.md) — POTASK-011 の test-first 実装順序、adapter 境界、Hermes smoke、文書同期、PR delivery を固定する計画。
  検索語: POTASK-011, implementation plan, route config, local snapshot, provider adapter, Hermes smoke, TDD, PR #29
- [Portfolio OS Task Backend Plugin Skill POTASK-011 Input Packet](wiki/syntheses/portfolio-os-task-backend-plugin-skill-potask-011-input-packet.json) — historical / non-executable な Input Packet v1。過去の POTASK-011 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: POTASK-011, input packet, provider adapter, local JSON, MCP, provider plugin, per_action
- [Portfolio OS Task Backend Plugin Skill POTASK-011 Execution Envelope](wiki/syntheses/portfolio-os-task-backend-plugin-skill-potask-011-execution-envelope.json) — historical / non-executable な Execution Envelope v3。過去の POTASK-011 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: POTASK-011, execution envelope, worker context, issue branch, worktree, review cycle, draft PR #29

## クエリ起点成果物

_現在なし。_
