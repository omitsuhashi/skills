# インデックス

wiki の最初の navigation surface として使います。durable page はすべて 1 回だけ載せ、1 行 summary を付けます。現役一覧には canonical page だけを残します。

旧`grill-to-pr-loop` / `issue-implementation-loop` familyのspec、ledger、packet、handoff、baselineは履歴参照用に保持するが、current executable surfaceやrestart entrypointではない。現行のapproved implementation planは`sdd-implementation`を使用し、新しいapprovalとrunを作る。

## ソース

- [[wiki/sources/2026-06-08-llm-wiki-draft-review-and-canonicalize-design.md|2026-06-08 LLM Wiki Draft Review And Canonicalize Design]] — `llm-wiki` skill に `draft-review` と `canonicalize` を first-class mode として追加する添付設計の source summary。
- [[wiki/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md|Grill To PR Loop スキル分割・非停止実行 詳細設計 v2]] — `grill-to-pr-loop` を composition skill と `issue-implementation-loop` execution skill に分割する添付設計の source summary。
- [[wiki/sources/2026-06-25-loop-skill-architecture-v3-design.md|2026-06-25 Loop Skill Architecture V3 Design]] — loop skill の context contract、worker packet、resume brief、operation routing を整理する添付設計の source summary。
- [[wiki/sources/2026-06-26-skill-repository-optimization-v4-design.md|Skill Repository Optimization V4 Design]] — PR #19 後の loop skill / llm-wiki context contract、artifact freshness、CI regression 固定の source summary。

## エンティティ

_現在なし。_

## 概念

_現在なし。_

## シンセシス

- [[wiki/syntheses/sdd-first-write-worktree-migration-spec.md|SDD first-write worktree migration 仕様]] — 最初のrepository write前にEpic planning worktreeをallocate/reuseしてbindingを証明し、original checkoutを保全するHuman承認済み仕様。parallel executionのHuman opt-in / Human-approved issue-plan要件は後継のportable validation仕様にsupersedeされ、agent-owned eligibilityとunknown時のsequential fallbackがcurrentである。
  検索語: sdd-implementation, first write, planning worktree, original checkout, starting_branch, starting_head_sha, binding tuple, integration_branch, parallel issue, superseded opt-in, fail closed, 作業ツリー, 最初の書込み, 保全, 並列実行, 統合

- [[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan.md|SDD first-write worktree migration 実装計画]] — Human承認済みのcurrent implementation plan。captured-SHA Epic planning worktreeへのfirst-write binding、sequential SDD、後続Epicだけのthin opt-in parallel adapter、single-writer integration、final verificationを実行順に定義する。
  検索語: sdd-implementation, implementation plan, Plan Gate, first write, planning worktree, captured SHA, integration branch, sequential SDD, parallel issue adapter, single writer, final review, 実装計画, 作業ツリー, 最初の書込み, 承認

- [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]] — 承認・実装済みの責務分離を維持しつつ、Authoring Profileのsemantic selector、evidence-bearing `BLOCKED`、current-state precedenceを追加するfocused revisionのcurrent Written Spec。reviewed two-file docs-only contractはlandedしたが、Human承認済みのpost-hoc old-contract replay evidence exceptionに合わせ、prior temporal pre-edit RED claimを訂正しscoped final-fix re-reviewを待つ。
  検索語: llm-wiki, authoring responsibility separation, authoring discovery, semantic selector, Authoring Profile, Compatibility Requirement, evidence-bearing BLOCKED, discovery unavailable, unobserved candidates, current-state precedence, historical baseline, post-hoc old-contract replay, evidence exception, corrected chronology, temporal pre-edit RED gate, scoped final-fix re-review pending, docs only, 責務分離, discovery診断, 再発防止, closeout
- [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-implementation-plan|llm-wiki authoring 責務分離実装計画]] — `Implemented / closeout verified`。承認済み仕様を、portable contract、semantic schema、Obsidian移行、durable knowledge closeout、full fresh verificationへ実装したcurrent plan。
  検索語: llm-wiki, authoring responsibility separation, implementation plan, Execution Plan Gate, Obsidian, semantic schema, fail closed, TDD, 実装計画, 実装計画承認, 責務分離, 検証
- [[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|llm-wiki Authoring Discovery Diagnostics 実装計画]] — 2026-08-08のHuman承認計画を、reviewed two-file docs-only production contractとHuman承認済みのpost-hoc old-contract replay evidence exception/correctionを記録するImplementation closeout candidateへ同期した。approved task contractは維持し、scoped final-fix re-reviewを待つ。
  検索語: llm-wiki, authoring discovery diagnostics, semantic selector, evidence-bearing BLOCKED, discovery unavailable, unobserved candidates, current-state precedence, pressure scenario, post-hoc old-contract replay, evidence exception, corrected chronology, temporal pre-edit RED gate, implementation closeout candidate, scoped final-fix re-review pending, reviewed Task 1, docs only, 実装計画, closeout, 再発防止
- [[wiki/syntheses/direct-github-projects-task-management/spec.md|GitHub Projects 直接接続型 Task Management Skill 仕様]] — 1個のcaller-selected Projectへ複数repositoryのIssueを集約し、standalone skillからGitHub MCPへ直接接続するWritten Spec Gate承認済みのcurrent設計。
  検索語: task-management, GitHub Projects, GitHub MCP, Issue, standalone skill, project_url, inbox repository, repository work unit, Status, Priority, Due date, approval policy, fail closed, タスク管理, 直接接続, 承認, セットアップ
- [[wiki/syntheses/direct-github-projects-task-management/issues.md|GitHub Projects 直接接続型 Task Management Skill Issue 台帳]] — DGPTM-001からDGPTM-004へstandalone skill、direct MCP contract、旧plugin削除、historical supersessionを依存順に分解したIssue Gate承認済み台帳。
  検索語: task-management, GitHub Projects, GitHub MCP, DGPTM, local issue, Issue Gate, blocker graph, plugin removal, standalone skill, ローカルIssue, ブロッカー, 移行
- [[wiki/syntheses/direct-github-projects-task-management/implementation-plan.md|GitHub Projects Direct Task Management Skill Implementation Plan]] — DGPTM-001からDGPTM-004のstandalone migrationに使ったExecution Plan Gate承認済み・実行完了のhistorical plan。final reviewで判明したoperation routing等の欠落はcurrent Issue台帳とlogで補正済み。
  検索語: task-management, GitHub Projects, implementation plan, writing-plans, TDD, RED GREEN, plugin removal, forward test, 実装計画, テスト駆動, 検証
- [[wiki/syntheses/direct-github-projects-task-management/input-packet.json|GitHub Projects Direct Task Management Skill Input Packet]] — approved spec bindingとIssue Gate承認済みDGPTM-001〜DGPTM-004を`local_only`で固定したsealed Input Packet v2。
  検索語: task-management, GitHub Projects, Input Packet v2, approved spec binding, execution intent, DGPTM, local_only, 実行契約, 承認済み仕様
- [[wiki/syntheses/portfolio-os-task-backend-plugin-skill-input-packet.json|Portfolio OS Task Backend Plugin Skill Input Packet]] — historical / non-executable な Input Packet v1。旧POTASK実行証跡としてbytesを保持し、current validatorでは再利用しない。
  検索語: historical POTASK, Input Packet v1, non-executable, 旧タスク管理, 履歴証跡
- [[wiki/syntheses/portfolio-os-task-backend-plugin-skill-potask-011-input-packet.json|Portfolio OS Task Backend Plugin Skill POTASK-011 Input Packet]] — historical / non-executable な Input Packet v1。旧provider adapter実行証跡としてbytesを保持し、current validatorでは再利用しない。
  検索語: historical POTASK-011, Input Packet v1, provider adapter, non-executable, 履歴証跡
- [[wiki/syntheses/portfolio-os-task-backend-plugin-skill-potask-011-execution-envelope.json|Portfolio OS Task Backend Plugin Skill POTASK-011 Execution Envelope]] — historical / non-executable な Execution Envelope v3。旧runの証跡としてbytesを保持し、resumeせずnew approval / new runを作る。
  検索語: historical POTASK-011, Execution Envelope v3, non-executable, resume不可, 履歴証跡
- [[wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md|LLM Wiki Draft Review And Canonicalize Goal Spec]] — Goal command で `skills/llm-wiki` を更新するための詳細実装契約。
- [[wiki/syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md|Grill To PR Loop Issue Implementation Review Gate Plan]] — 削除済み`skills/grill-to-pr-loop`への過去の実装計画。historical / non-executableとして保持する。
  検索語: grill-to-pr-loop, requesting-code-review, 実装レビュー, issue review, PR review, review gate, implementation plan
- [[wiki/syntheses/loop-review-governance-spec.md|Loop Review Governance Spec]] — Issue 意図適合レビューを必須にし、future-only hardening は通常レビュー観点から外し、明示依頼または current PR delivery risk の candidate だけを制御する Spec Gate 承認済み仕様。
  検索語: loop review governance, issue intent, hardening candidate, future-only hardening, safety escalation, final PR, human decision, requesting-code-review, context budget, 実装レビュー, 堅牢化, 人間判断
- [[wiki/syntheses/loop-review-simplicity-and-phase-skills/spec.md|Loop Review Simplicity And Phase Skills 仕様]] — material findingだけを報告するreview基準と、phase-owned workflow skillをoperation/dispatch別に分離しtask-triggered skillをcurrent phaseだけでon-demand読込するcontext contract schema v3のSpec Gate承認済み仕様。
  検索語: grill-to-pr-loop, issue-implementation-loop, material review, simplicity, phase skills, context contract schema v3, skills, dispatch_skills, Critical, Important, review, シンプルさ, フェーズ別読込, 実装レビュー
- [[wiki/syntheses/loop-review-simplicity-and-phase-skills/issues.md|Loop Review Simplicity And Phase Skills Issue 台帳]] — `LRSP-001`のschema v3、phase-scoped skill、material review、TDD、417 tests、cycle 2 review承認、local `PR_READY` evidenceを持つ完了台帳。
  検索語: LRSP-001, local issue, Issue Gate, context contract schema v3, phase mapping, material review, TDD, blocker graph, ローカルIssue, フェーズ別読込, 実装レビュー
- [[wiki/syntheses/loop-review-simplicity-and-phase-skills/implementation-plan.md|Loop Review Simplicity And Phase Skills Implementation Plan]] — baseline pressure、schema v3、material review、full verification、2-cycle reviewまで完了したExecution Plan Gate承認済み計画。
  検索語: LRSP-001, Execution Plan Gate, implementation plan, TDD, pressure scenario, schema v3, skills, dispatch_skills, material review, RED GREEN, 実装計画, テスト駆動, フェーズ別読込
- [[wiki/syntheses/loop-review-simplicity-and-phase-skills/input-packet.json|Loop Review Simplicity And Phase Skills Input Packet]] — 旧loop familyの過去runを固定したhistorical / non-executable Input Packet v2。current validatorで再利用せず、新しいapproval/new runを作る。
  検索語: LRSP-001, Input Packet v2, approved spec binding, per_action, phase-scoped skill, material review
- [[wiki/syntheses/loop-review-governance-issues.md|Loop Review Governance Issue 台帳]] — `loop-review-governance` の Issue Gate 承認済み local issue ledger。LRG-001 から LRG-005 の blocker graph、acceptance criteria、remote policy を定義する。
  検索語: loop review governance, local issue, Issue Gate, LRG, blocker graph, hardening candidate, requesting-code-review, context budget, ローカルIssue, 堅牢化
- [[wiki/syntheses/loop-review-governance-input-packet.json|Loop Review Governance Input Packet]] — historical / non-executable な Input Packet v1。過去の LRG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: loop review governance, input packet, Execution Plan Gate, issue-implementation-loop, LRG, write scope, dependencies, local_only, 実行計画
- [[wiki/syntheses/loop-review-governance-execution-envelope.json|Loop Review Governance Execution Envelope]] — historical / non-executable な Execution Envelope v2。過去の LRG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: loop review governance, execution envelope, worker_context_required, batch_issue_prs, requesting-code-review, hardening candidate, pending_decision, draft PR, worktree reservation
- [[wiki/syntheses/loop-review-governance-final-delivery-plan.json|Loop Review Governance Final Delivery Plan]] — `loop-review-governance` の draft final PR 作成用 delivery plan。head は `codex/loop-review-governance/epic-base`、base は `main`、draft only。
  検索語: loop review governance, delivery plan, draft PR, final PR, epic-base, hardening decision
- [[wiki/syntheses/loop-review-governance-handoff-brief.md|Loop Review Governance Handoff Brief]] — 削除済み`issue-implementation-loop`の過去runに関するbounded handoff brief。historical / non-executableであり、再開には使わない。
  検索語: loop review governance, handoff brief, Execution Plan Gate, runtime root, worker packet, hardening_candidate, local_only
- [[wiki/syntheses/loop-review-governance-hardening-decisions.md|Loop Review Governance Hardening Candidate Decisions]] — 既存 `hardening_candidate` 4 件を `deferred_follow_up` とし、future-only hardening を通常レビュー観点から外す判断を記録する decision artifact。
  検索語: loop review governance, hardening candidate, future-only hardening, deferred follow-up, review scope, source review, registry path, 保存場所, 出典, 堅牢化, 人間判断
- [[wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md|Grill To PR Loop Skill Split V2 Spec]] — `issue-implementation-loop` 新設と `grill-to-pr-loop` composition 縮小の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, execution envelope, worktree reservation, scheduler, human wait, runtime state, skill split, implementation plan
- [[wiki/syntheses/grill-to-pr-loop-skill-split-v2-issues.md|Grill To PR Loop Skill Split V2 Issues]] — skill split 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, ローカルIssue, ブロッカー
- [[wiki/syntheses/grill-to-pr-loop-skill-split-v2-input-packet.json|Grill To PR Loop Skill Split V2 Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/grill-to-pr-loop-skill-split-v2-execution-envelope.json|Grill To PR Loop Skill Split V2 Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md|Grill To PR Loop Branch Policy Spec]] — `grill-to-pr-loop` / `issue-implementation-loop` の branch、worktree、commit、integration branch 推奨運用を実装契約化する spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, branch policy, worktree reservation, epic_base, scoped commit, integration branch, PR_READY, ブランチ, コミット
- [[wiki/syntheses/planning-worktree-gate/spec.md|Planning Worktree Gate 仕様]] — 最初のrepository write前のEpic単位planning worktree、default checkout保全、prepare / PR_READY / deliveryのphysical commit reachability guardを定義し、実装完了した承認済み仕様。
  検索語: Planning Worktree Gate, planning branch, worktree reuse, default checkout, pre-existing dirt, prepare, PR_READY, delivery, physical commit reachability, 作業ツリー, main保全, 実行準備, 配送
- [[wiki/syntheses/planning-worktree-gate/issues.md|Planning Worktree Gate Issue 台帳]] — PWTG-001〜PWTG-004の完了状態、全commit、Acceptance 1〜8、fresh verification、review、local_only境界を集約したcanonical closeout台帳。
  検索語: Planning Worktree Gate, PWTG, Issue Gate, implementation closeout, worktree reuse, repository guard, runtime identity, delivery integrity, Acceptance 1-8, local_only, ローカルIssue, 完了, 配送検証
- [[wiki/syntheses/planning-worktree-gate/implementation-plan.md|Planning Worktree Gate Implementation Plan]] — PWTG-001〜PWTG-004をTDDで実装完了し、planning identity、default checkout snapshot、physical final head reachabilityの実測evidenceを記録したExecution Plan。
  検索語: Planning Worktree Gate, implementation plan, TDD, RED GREEN, repository guard, final head, physical commit reachability, fresh verification, 実装計画, テスト駆動, 配送検証, 完了
- [[wiki/syntheses/planning-worktree-gate/input-packet.json|Planning Worktree Gate Input Packet]] — Planning Worktree Gate実装前の現行v2 validatorでsealしたself-hosting execution lock。target実装後の新規packet contractとは区別する。
  検索語: Planning Worktree Gate, Input Packet v2, self-hosting, approved spec binding, PWTG, local_only, 実行契約, 承認済み仕様
- [[wiki/syntheses/grill-to-pr-loop-branch-policy-issues.md|Grill To PR Loop Branch Policy Issues]] — branch policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, branch policy, local issue, blocker graph, ローカルIssue, ブランチ運用
- [[wiki/syntheses/grill-to-pr-loop-branch-policy-input-packet.json|Grill To PR Loop Branch Policy Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/grill-to-pr-loop-branch-policy-execution-envelope.json|Grill To PR Loop Branch Policy Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/issue-implementation-loop-context-policy-spec.md|Issue Implementation Loop Context Policy Spec]] — `issue-implementation-loop` の context/session policy と entrypoint budget を契約化する spec。
  検索語: issue-implementation-loop, context policy, session semantics, worker packet, Execution Envelope, コンテキスト, セッション
- [[wiki/syntheses/issue-implementation-loop-context-policy-issues.md|Issue Implementation Loop Context Policy Issues]] — context/session policy 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, context policy, local issue, blocker graph, ローカルIssue, コンテキスト
- [[wiki/syntheses/issue-implementation-loop-context-policy-input-packet.json|Issue Implementation Loop Context Policy Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/loop-skill-context-optimization-spec.md|Loop Skill Context Optimization Spec]] — `grill-to-pr-loop` と `issue-implementation-loop` の context 最適化、reference 分割、repo-local skill root 優先 hardening の実装契約。
  検索語: grill-to-pr-loop, issue-implementation-loop, context optimization, reference split, skill root, repo-local, コンテキスト最適化
- [[wiki/syntheses/loop-skill-context-optimization-issues.md|Loop Skill Context Optimization Issues]] — loop skill context optimization 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, reference routing, skill root, ローカルIssue
- [[wiki/syntheses/loop-skill-context-optimization-input-packet.json|Loop Skill Context Optimization Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/loop-skill-codex-optimization-spec.md|Loop Skill Codex 最適化仕様]] — Codex の planning / execution context と phase branch policy に合わせ、Execution Envelope v3、branch ownership、fresh / compacted coordinator handoff を固定する仕様。
  検索語: Codex, phase_branch_policy, schema version 3, execution envelope, planning branch, epic_base, issue branch, worktree, grill-to-pr-loop, issue-implementation-loop
- [[wiki/syntheses/planning-authority-policy/spec.md|Planning Authority Policy 仕様]] — planning integrationをactive-runtime-selected main context、人間をdecision authority、supporting agentをadvisory/read-onlyとし、model / reasoningをdurable artifactへ保存しないcurrent canonical仕様。
  検索語: planning authority, main planning context, supporting agent, advisory only, read only, human decision authority, active runtime, runtime capability, model selection, reasoning, 計画統合, 人間承認
- [[wiki/syntheses/planning-authority-policy/issues.md|Planning Authority Policy Issue 台帳]] — PAP-001の5-field spec fixとcycle 2承認、PAP-004へのfix統合、未実施のPAP-004 cycle 2 reviewsをserial release順、commit、evidenceとともに追跡するcurrent台帳。
  検索語: planning authority, PAP, Issue Gate, local issue, blocker graph, family policy, advisory only, model persistence, ローカルIssue, ブロッカー
- [[wiki/syntheses/planning-authority-policy/implementation-plan.md|Planning Authority Policy 実装計画]] / [[wiki/syntheses/planning-authority-policy/input-packet.json|sealed Input Packet v2]] — Execution Plan Gate、5-field coverage fix、final branch integration、worker-only境界と未実施のPAP-004 cycle 2 reviewsを区別するlocal-only handoff。
  検索語: planning authority, implementation plan, Input Packet v2, Execution Plan Gate, sealed packet, TDD, worker-only, local-only, 実装計画
- [[wiki/syntheses/sdd-portable-validation-simplification|SDD portable validation と責務単純化仕様]] — 2026-08-14 Human-approved active Written Spec。standalone validatorを追加せず、explicit targetに対する三つのdirect Git gateでtransient artifactを検査し、repository固有migration/history validatorをroot ownerへ隔離する。Superpowers ownership、agent-owned parallel eligibility、unknown時のsequential fallback、isolated package closureをcurrent contractとして定義する。
  検索語: sdd-implementation, portable skill, direct Git probe, write-tree, BASELINE..HEAD, transient artifact, .superpowers, staged deletion, ignored scratch, package closure, migration history validator, Superpowers ownership, sequential fallback, Written Spec, 責務単純化, 検証
- [[wiki/syntheses/sdd-portable-validation-simplification-implementation-plan|SDD portable validation と責務単純化 実装計画]] — independent review `ready`、Plan readiness `ready`。direct Git gate、isolated installed-folder closure、root-owned migration/history/canonical parity、Superpowers ownership deduplication、knowledge closeoutを5 taskのserialized implementationへ割り当てたcurrent repository-ready plan。
  検索語: sdd-implementation, portable validation, implementation plan, Plan Gate, direct Git gate, isolated install, package closure, synthetic Git repository, canonical plan parity, Superpowers ownership, serialized integration, ready, 実装計画, 責務単純化, 検証
- [[wiki/syntheses/sdd-implementation-skill-design.md|SDD Implementation Skill 設計]] — Superpowersを開発方法論の正本とし、Planning Controller、Control Return、fresh pre-implementation worker、agent-owned Plan Readinessを含むcurrent lifecycleを、入力・依存skill・active runtime capabilityだけで解決するcanonical design。raw stage handoffはrepository外temporary locationへ置き、`.superpowers/**`のcurrent direct Git gateとportable/repository ownershipは後継のportable validation仕様へ委譲する。
  検索語: sdd-implementation, Superpowers, brainstorming, writing-plans, Subagent-Driven Development, SDD, Planning Controller, Control Return, fresh pre-implementation worker, Plan Contract Overlay, Plan Reviewer, Plan Readiness Gate, repository-external handoff, .superpowers, ignored scratch, Grill with Docs, active runtime, capability boundary, agent-agnostic, portable skill, compatibility-free, reasoning effort, llm-wiki, knowledge lifecycle, Written Spec, 仕様作成, 仕様精緻化
- [[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|Global Skill Fallback And Simple Implementation Plan]] — local implementationとtask reviewを完了し、final whole-branch review待ちのone-task計画。SDD dependency preflightのactive/global readable fallbackと、独立`keep-implementation-simple` Skillを2つのfresh-agent behavior checkとfocused validatorで検証済み。
  検索語: sdd-implementation, dependency preflight, global skill root, readable SKILL.md, ~/.agents/skills, keep-implementation-simple, writing-skills, pressure scenario, TDD, YAGNI, implementation plan, skill discovery, 単純実装, 実装計画
- [[wiki/syntheses/sdd-preimplementation-context-isolation-spec.md|SDD 実装前コンテキスト分離仕様]] — Planning ControllerをHuman対話・判断・approval・routingへ限定し、repository調査、Spec Synthesis、Plan Authoring / Reviewをfresh workerへ委譲するcurrent仕様。Plan Stage semanticsとrepository-contained Research / review handoff destinationはPlan Ownership Alignmentがsupersedeし、raw pathはrepository外temporary locationへ移行済みである。
  検索語: sdd-implementation, Planning Controller, Research Worker, Spec Synthesis Worker, Plan Author Worker, Plan Reviewer, Plan Readiness Gate, fresh context, Control Return, Stage Capsule, Decision Record, context isolation, repository-external temporary, .superpowers, duplicate question, 実装前調査, コンテキスト分離, 重複質問, 仕様作成, 実装計画
- [[wiki/syntheses/sdd-preimplementation-context-isolation-implementation-plan.md|SDD 実装前コンテキスト分離実装計画]] — baseline `66d93ae`の承認済み仕様を、Planning Controller contract、fresh Research / Spec Synthesis / Spec Review / Plan Author seam、TDD、knowledge closeout、final reviewへ落とした実行可能計画。
  検索語: sdd-implementation, Planning Controller, Control Return, Stage Capsule, Decision Record, fresh worker, research-stage, planning-context, Spec Reviewer, Plan Author, baseline 66d93ae, TDD, 実装計画, コンテキスト分離
- [[wiki/syntheses/sdd-plan-ownership-alignment.md|SDD Plan Ownership Alignment 仕様]] — 2026-08-14 Human-approved active canonical Written Spec。Human approvalをNorth Star / Written Specへ限定するcurrent Plan Stage authorityに加え、全SDD stageのtransient handoffをrepository外へ置き、`.superpowers/**`をignore確認済みの例外的local scratchだけに限定し、cleanup後のGit index / new commit / PR final treeをentry zeroにする境界を定義する。broader二仕様の競合するPlan semanticsとrepository-contained research / report / brief destinationを該当範囲でsupersedeする。
  検索語: sdd-implementation, plan ownership, Plan Contract Overlay, Plan Reviewer, Plan Readiness Gate, complete coverage, integration order, combined verification, Human approval, transient artifact, repository-external handoff, .superpowers, Git index, staging area, candidate tree, commit tree, PR final tree, history rewrite prohibition, research report, review report, brief, 実装計画, 計画所有, 準備判定
- [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan.md|SDD Plan Ownership Alignment 実装計画]] — approved specをbaseline `c370fe1`へbindingしたagent-authored canonical plan。POA-1〜POA-8のlocal work、fresh combined verification、canonical whole-branch review、bounded fix `bbfd06e`、Spec / Standards scoped re-reviewは完了し`LOCAL_COMPLETE`である。current Git index / final treeは`.superpowers/**` entry zero、3 local copiesはignored / untracked、`f07aebc`を含むancestor historyはrewriteせず保持する。authorized non-force remote branch updateはpending / unpublishedで、merge、release、live installは未承認である。
  検索語: sdd-implementation, implementation plan, agent-owned plan, plan-contract, Plan Author, Plan Reviewer, independently-reviewed, ready, LOCAL_COMPLETE, POA-8, bbfd06e, e180888, whole-branch review, Spec READY, Standards READY, repository-external handoff, zero final tree, ignored local copy, no history rewrite, pending push, coverage matrix, dependency graph, serialized integration, post-integration verification, 実装計画, エージェント所有
- [[wiki/syntheses/sdd-agent-agnostic-runtime-implementation-plan.md|SDD Agent-Agnostic Runtime Contract Implementation Plan]] — active runtimeのcapability解決へ置き換えたportable skill contractのhistorical / non-executable実装証跡。本文のcompatibility validator commandとunchecked checklistはobsoleteであり実行しない。
  検索語: sdd-implementation, agent-agnostic, portable skill, active runtime, dependency discovery, capability boundary, historical, non-executable, obsolete validator, implementation evidence, エージェント非依存
- [[wiki/syntheses/sdd-compatibility-removal-follow-up-plan.md|SDD Compatibility Removal Follow-up Plan]] — agent-agnostic behaviorを維持し、非要件となったcross-runtime compatibility policy、validator、CI gateを削除した`LOCAL_COMPLETE` / PR-ready plan。bounded fixのscoped re-reviewはfindingなしで承認済み。
  検索語: sdd-implementation, compatibility removal, cross-runtime, validator removal, CI gate removal, plugin target, historical dual-host, final review fix, scoped re-review approved, LOCAL_COMPLETE, PR-ready, follow-up plan, 互換性削除, 実装計画
- [[wiki/syntheses/sdd-effort-risk-precedence-implementation-plan.md|SDD Reasoning Effort Risk Precedence Implementation Plan]] — high-risk task reviewをhighとして扱い、共有default effort vocabularyを増やさない変更は、Task 1、final review、bounded fix、scoped re-reviewを完了した`LOCAL_COMPLETE` plan。
  検索語: reasoning effort, risk precedence, task complexity, high-risk task review, low, medium, high, runtime override, final review, リスク優先, 実装計画
- [[wiki/syntheses/sdd-superpowers-model-and-reasoning-research.md|Superpowers SDD のモデル選択・Reasoning・Host 境界調査]] — Superpowers v6.2.0のdispatch model選択、reasoning effort不在、Codex/Hermes adapter境界、brainstorming・planning・SDDの責任分割を一次情報で確認した調査。
  検索語: Superpowers, v6.2.0, SDD, model selection, MODEL REQUIRED, reasoning_effort, Thinking Effort, Codex, Hermes Agent, host adapter, brainstorming, writing-plans, upstream research, モデル選択, 思考強度
- [[wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md|SDD Implementation Superpowers-first Revision 実装計画]] — 実装済みbaselineを保持するhistorical / non-executable plan。runtime固有部分はagent-agnostic revisionにsupersedeされ、current runtime behaviorの実行入口には使わない。
  検索語: sdd-implementation, Superpowers-first, implemented baseline, historical, non-executable, superseded runtime adapter, implementation plan, Execution Plan Gate, Grill with Docs, llm-wiki, reasoning effort, TDD, 履歴実装計画
- [[wiki/syntheses/sdd-implementation-skill-implementation-plan.md|SDD Implementation Skill 実装計画]] — 現行Skill本体、runtime-only routing、material review、既定repository route、日本語knowledge closeoutを実装・検証したPhase 1のhistorical plan。後継revisionには再利用しない。
  検索語: sdd-implementation, historical implementation plan, Phase 1, Subagent-Driven Development, model routing, reasoning effort, material review, knowledge closeout, dual-host, 実装計画, 既定実装入口
- [[wiki/syntheses/sdd-implementation-phase2-removal-plan.md|SDD Implementation Phase 2 旧実装スキル削除計画]] — SDD実run、fresh coordinator verification、final whole-branch reviewを完了し、旧loop skill本体と専用runtime/context surfaceをlocal treeから除去した`LOCAL_COMPLETE` Phase 2計画。
  検索語: sdd-implementation, Phase 2, grill-to-pr-loop, issue-implementation-loop, removal, legacy implementation skill, historical evidence, context report, SDD実run, 旧実装スキル削除
- [[wiki/syntheses/issue-implementation-loop-common-lib-split-spec.md|Issue Implementation Loop Common Lib Split Spec]] — `issue-implementation-loop` の `_common.py` と単一巨大 test file を internal common lib / behavior-domain tests へ分割する後続実装契約。
  検索語: issue-implementation-loop, common lib, _common.py, scripts/lib, test split, context optimization, skill split, コンテキスト最適化
- [[wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md|Issue Implementation Loop Common Lib Split Issues]] — common lib split 実装のローカルIssue ledger。
  検索語: issue-implementation-loop, local issue, blocker graph, common lib, _common.py, tests, ローカルIssue
- [[wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json|Issue Implementation Loop Common Lib Split Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/loop-skill-architecture-v3-spec.md|Loop Skill Architecture V3 Spec]] — `grill-to-pr-loop` / `issue-implementation-loop` の context contract、operation selection、worker packet、resume brief を実装契約化する Spec Gate draft。
  検索語: grill-to-pr-loop, issue-implementation-loop, context-contract, worker packet, resume brief, operation routing, コンテキスト最適化
- [[wiki/syntheses/loop-skill-architecture-v3-issues.md|Loop Skill Architecture V3 Issues]] — loop skill architecture v3 実装の日本語 local-first issue ledger と統合 verification evidence。
  検索語: grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, context-contract, worker packet, resume brief, ローカルIssue
- [[wiki/syntheses/loop-skill-architecture-v3-input-packet.json|Loop Skill Architecture V3 Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/loop-skill-architecture-v3-execution-envelope.json|Loop Skill Architecture V3 Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/skill-repository-optimization-v4-spec.md|Skill Repository Optimization V4 Spec]] — PR #19 後の read-set 正本化、推定 token budget、Worker Packet V2、Resume Brief V2、`llm-wiki` contract、CI 固定の Spec / Issue / Execution Plan Gate 承認済み契約。
  検索語: skill repository optimization, grill-to-pr-loop, issue-implementation-loop, llm-wiki, context-contract, token budget, worker packet v2, resume brief v2, CI, コンテキスト最適化
- [[wiki/syntheses/skill-repository-optimization-v4-issues.md|Skill Repository Optimization V4 Issues]] — Skill Repository Optimization V4 の local-first integration ledger。SRO4-001 から SRO4-006 の実装状態、review range、full verification、canonical context CLI、wrapper / workflow shim 削除、remote policy、residual risks を集約する。
  検索語: skill repository optimization, local issue, blocker graph, SRO4, context-contract, Worker Packet V2, Resume Brief V2, llm-wiki, final integration, canonical CLI, wrapper removal, residual risks, local_only, ローカルIssue, 統合検証, 残リスク
- [[wiki/syntheses/skill-repository-optimization-v4-input-packet.json|Skill Repository Optimization V4 Input Packet]] — historical / non-executable な Input Packet v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
- [[wiki/syntheses/skill-repository-optimization-v4-execution-envelope.json|Skill Repository Optimization V4 Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: skill repository optimization, execution envelope, worker_context_required, local_only, SRO4, worktree reservation, 実行計画
- [[wiki/syntheses/skill-repository-optimization-v4-context-baseline.json|Skill Repository Optimization V4 Context Baseline]] — 削除済みloop familyのSRO4-001 context metricsを残すhistorical / non-executable baseline。current reporter / validatorのbaseline比較には使わない。
  検索語: skill repository optimization, SRO4-001, context baseline, operation metrics, word count, grill-to-pr-loop, issue-implementation-loop
- [[wiki/syntheses/loop-skill-operational-simplicity-spec.md|Loop Skill 運用単純化仕様]] — loop 系 skill の適用基準、役割境界モデル、workflow complexity レポートを追加する Spec Gate 承認済み契約。
  検索語: 適用基準, 役割境界モデル, 複雑性, grill-to-pr-loop, issue-implementation-loop, operational simplicity, workflow complexity, mental model, コンテキスト最適化
- [[wiki/syntheses/loop-skill-operational-simplicity-issues.md|Loop Skill 運用単純化 Issue 台帳]] — loop 系 skill 運用単純化の日本語 local-first 最終台帳。LSOS-001 から LSOS-004 の実装証跡、レビュー結果、全体検証、remote boundary、draft PR #22 を集約する。
  検索語: ローカルIssue, 実装証跡, レビュー結果, 最終台帳, 運用単純化, draft PR #22, grill-to-pr-loop, issue-implementation-loop, local issue, blocker graph, workflow complexity, role boundary
- [[wiki/syntheses/loop-skill-operational-simplicity-input-packet.json|Loop Skill 運用単純化 Input Packet]] — historical / non-executable な Input Packet v1。過去の LSOS 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: 実行計画, 承認済み packet, loop skill operational simplicity, execution packet, input packet, LSOS, local_only
- [[wiki/syntheses/loop-skill-operational-simplicity-execution-envelope.json|Loop Skill 運用単純化 Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の LSOS 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: 実行計画, 実行 envelope, worker_context_required, local_only, LSOS, worktree reservation, loop skill operational simplicity
- [[wiki/syntheses/loop-skill-context-compaction-spec.md|Loop Skill Context Compaction Spec]] — loop 系 skill の session context pressure 65% 圧縮 trigger、保持/圧縮分類、phase 別 compaction policy を定義する Spec Gate 承認済み仕様。
  検索語: grill-to-pr-loop, issue-implementation-loop, context compaction, session pressure, 65%, 圧縮, 忘れてはいけないこと, handoff brief, resume brief, worker packet
- [[wiki/syntheses/loop-skill-context-compaction-issues.md|Loop Skill Context Compaction Issues]] — context compaction 実装の日本語 local-first ledger。LSCC-001 から LSCC-005 の implementation evidence、review result、verification result、remote policy を集約する。
  検索語: LSCC, Issue Gate, local issue ledger, context compaction, carry-forward capsule, phase transition GC, conditional overlay, local_only, implementation evidence, review result, verification result
- [[wiki/syntheses/loop-skill-context-compaction-input-packet.json|Loop Skill Context Compaction Input Packet]] — historical / non-executable な Input Packet v1。過去の LSCC 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSCC, input packet, Execution Plan Gate, issue-implementation-loop, worker-only, local_only, write scope, dependency graph
- [[wiki/syntheses/loop-skill-context-compaction-execution-envelope.json|Loop Skill Context Compaction Execution Envelope]] — historical / non-executable な Execution Envelope v2。過去の LSCC 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSCC, execution envelope, worker_context_required, coordinator_may_implement, local_only, session_compaction, hard_stop_percent, worktree reservation
- [[wiki/syntheses/loop-skill-context-compaction-handoff-brief.md|Loop Skill Context Compaction Handoff Brief]] — 旧loop familyの過去runに関するbounded handoff brief。historical / non-executableであり、再開には使わない。
  検索語: LSCC, handoff brief, carry-forward capsule, resume, runtime root, worker packet, context compaction
- [[wiki/syntheses/loop-skill-autonomous-gates-spec.md|Loop Skill 自動継続 Gate 仕様]] — `Execution Plan Gate` と `Live Root Gate` を agent preflight + commit boundary として自動継続し、承認済み delivery policy 内の draft final PR 作成を追加承認なしに行う Spec Gate 承認済み仕様。
  検索語: Execution Plan Gate, Live Root Gate, Adapter Availability Gate, final PR, draft PR, approved_actions, auto-continue, grill-to-pr-loop, issue-implementation-loop, remote policy, human-only merge
- [[wiki/syntheses/loop-skill-autonomous-gates-issues.md|Loop Skill 自動継続 Gate Issue 台帳]] — `loop-skill-autonomous-gates` の Issue Gate 承認済み日本語 local-first 最終台帳。LSAG-001 から LSAG-006 の implementation evidence、review result、verification result、delivery evidence、remote 未実行境界を集約する。
  検索語: LSAG, Loop Skill 自動継続, local issue, Issue Gate, final ledger, 最終台帳, implementation evidence, review result, verification result, delivery evidence, blocker graph, Execution Plan Gate, Live Root Gate, Adapter Availability Gate, final PR, approved_actions
- [[wiki/syntheses/loop-skill-autonomous-gates-input-packet.json|Loop Skill 自動継続 Gate Input Packet]] — historical / non-executable な Input Packet v1。過去の LSAG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSAG, input packet, execution packet, Execution Plan Gate, auto-continue, issue-implementation-loop, batch_issue_prs, final PR, approved_actions, delivery evidence
- [[wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json|Loop Skill 自動継続 Gate Execution Envelope]] — historical / non-executable な Execution Envelope v1。過去の LSAG 実行証跡として保持し、current validator では再利用せず new approval/new run を作る。
  検索語: LSAG, execution envelope, worker_context_required, batch_issue_prs, final_pr_push_head, final_pr_create_draft, worktree reservation, auto-continue
- [[wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-spec.md|Grill To PR Loop Epic Base Delivery Policy Spec]] — issue PR を `codex/<epic-id>/epic-base` に集約し、issue PR は guarded agent merge、final PR merge は human-only とする delivery policy。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, batch_issue_prs, issue PR, final PR, merge policy, review cycles, PR配送
- [[wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-issues.md|Grill To PR Loop Epic Base Delivery Policy Issues]] — epic-base delivery policy 実装のローカルIssue ledger。
  検索語: grill-to-pr-loop, epic-base, delivery policy, local issue, blocker graph, ローカルIssue, PR配送
- [[wiki/syntheses/grill-to-pr-loop-epic-base-lifecycle-hardening-spec.md|Grill To PR Loop Epic Base Lifecycle Hardening Spec]] — `epic_base` を検証可能な delivery/integration branch resource として lifecycle 管理に載せる hardening spec。
  検索語: grill-to-pr-loop, issue-implementation-loop, epic_base, epic-base, branch lifecycle, reconcile, pr_merged, final PR, ブランチ統制
- [[wiki/syntheses/approved-spec-binding-contract/spec.md|Loop Skill Approved Spec Binding Artifact Lifecycle Revision]] — Epic単位のtracked durable rootとGit common directory配下のuntracked runtime rootを分離し、Input Packetだけをapproval lockとしてGitに残すWritten Spec Gate承認済みrevision。
  検索語: approved spec binding, artifact lifecycle, epic directory, artifact root, input packet lock, untracked execution envelope, runtime root, Git common dir, ASBC-007, ASBC-008, ASBC-009
- [[wiki/syntheses/approved-spec-binding-contract/issues.md|Loop Skill Approved Spec Binding Artifact Lifecycle Issues]] — initial ASBC-001〜ASBC-006 evidenceを保持し、ASBC-007/ASBC-008 `COMPLETE`、ASBC-009 local `PR_READY`、controller review後のDraft PR #32更新pendingまでを集約する最終local ledger。
  検索語: ASBC-007, ASBC-008, ASBC-009, COMPLETE, PR_READY, artifact layout, runtime boundary, issue ledger, full verification, pending remote delivery, Draft PR 32
- [[wiki/syntheses/approved-spec-binding-contract/implementation-plan.md|Loop Skill Approved Spec Binding Artifact Lifecycle Implementation Plan]] — layout validation、current artifact migration/reseal、fresh-agent 3/3、full verification、local risk reviewとcontroller delivery境界を記録した実行plan。
  検索語: artifact lifecycle implementation plan, TDD, reseal, input packet, execution envelope, fresh evaluator, full verification, PR_READY, controller review, Draft PR 32
- [[wiki/syntheses/approved-spec-binding-contract/input-packet.json|Loop Skill Approved Spec Binding Artifact Lifecycle Input Packet]] — 旧loop familyのASBC-007〜ASBC-009 execution intentを残すhistorical / non-executable Input Packet v2。current validatorで再利用せず、新しいapproval/new runを作る。
  検索語: ASBC-007, ASBC-008, ASBC-009, current Input Packet v2, approved spec binding, spec digest, approval evidence, per_action, executable artifact, seal
- [[wiki/syntheses/portfolio-os-install-review-and-procedure.md|Portfolio OS Install Review And Procedure]] — `skills` repo に Portfolio OS 固有 runtime を混ぜないためのレビュー結果と導入手順。
- [[wiki/sources/2026-07-17-decide-in-order-source-brief.md|Decide In Order Skill 原案]] — 目的、守るもの、許容損失、核心の問いから始める実行支援型 skill の一次資料と設計時の解釈。
  検索語: decide in order, decision ordering, task management, purpose, must protect, acceptable loss, core question, sunk cost, risk, review, 決める順番, 意思決定, 優先順位, サンクコスト, 見直し
- [[wiki/syntheses/decide-in-order-skill-design.md|Decide In Order Skill 設計]] — 独立state-free skillの判断順序、適応的表示、DecisionRecordを記録する設計。旧task-management plugin integrationはhistoricalであり、current skillはtask storageを所有しない。
  検索語: decide-in-order, decision support, DecisionFrame, DecisionRecord, light, deep, review, standalone skill, 決める順番, 意思決定支援, 日次計画, 継続判断, 調査方針, 許容損失
- [[wiki/syntheses/2026-07-17-decide-in-order-implementation-plan.md|Decide In Order Skill 実装計画]] — standalone decision skillのtest-first実装とforward testを記録するhistorical plan。旧task-management plugin integrationはcurrent task contractではない。
  検索語: decide-in-order, implementation plan, skill-creator, forward test, contract test, TDD, standalone skill, 実装計画, 意思決定支援, 回帰検証
- [[wiki/syntheses/hermes-dual-host-authoring-contract-design.md|Codex / Hermes Dual-host Authoring Contract 設計]] — skill behaviorとplugin packaging compatibilityの双方でhistorical / non-executableな旧設計。過去のdiscovery / live load evidenceを参照する場合だけ使う。
  検索語: Hermes Agent, Codex, dual-host, historical, non-executable, SKILL.md, description.md, plugin.yaml, register(ctx), external_dirs, install, discovery, live load, skill creator, plugin creator, compatibility validator, CI gate, 作成指示, 互換性, インストール, 検証
- [[wiki/syntheses/2026-07-17-hermes-dual-host-authoring-contract-implementation-plan.md|Codex / Hermes Dual-host Authoring Contract 実装計画]] — historical / non-executableな旧dual-host plan。原文は過去の実装証跡として保持し、current skill behaviorの実行指示には使わない。
  検索語: Hermes Agent, Codex, dual-host, historical, non-executable, superseded, implementation plan, AGENTS.md, validator, unittest, CI, TDD, SKILL.md, plugin.yaml, register(ctx), 履歴実装計画, 作成ルール, 検証

## クエリ起点成果物

_現在なし。_
