# ログ

append-only で使います。すべての entry は予測しやすい header で始めます。

## [2026-07-27] spec-gate | Loop Review Simplicity And Phase Skills

- Epic ID `loop-review-simplicity-and-phase-skills` として、reviewを要件達成、material simplicity、material riskに絞り、`Minor` / nit / 好み / 任意改善をfindingとして報告しないSpec Gate候補を追加した。
- 同じ要件をmaterially simplerな構造で満たせる場合は、具体的代案を必須とする`intent_gap` / `Important`として扱い、mechanical validationと既存hardening / safety境界は維持する。
- 両loop skillのcontext contract schema v3に`skills` / `dispatch_skills`を追加し、planning、worker TDD、implementation review、final reviewのsupplemental skill読込をoperation/actor単位で分離する設計を固定した。
- planning branchは`codex/loop-review-simplicity-and-phase-skills/planning`、planning base SHAは`f5d151e34de5089d75be68249e09da8a2d14f282`。remote policyは`per_action`で、local `PR_READY`後のbranch pushとdraft PR作成だけを後続Remote Gateの対象とし、GitHub Issue mirror、issue PR、ready-for-review、merge、release、live installは非承認とした。
- session userは`knowledge/wiki/syntheses/loop-review-simplicity-and-phase-skills/spec.md`、raw-byte SHA-256 `d3ac927b66e348ea39cb71a83cd13ab2139700f022a544872cb41ea708734794`を2026-07-27T07:40:32+09:00にSpec Gateとして再承認した。approval scopeは`accepted_decisions`、`non_goals`、`acceptance_criteria`、`verification`、`remote_policy`、`stop_conditions`の全六項目である。
- Issue分解、Execution Packet、実装、remote writeはまだ行っていない。

## [2026-07-27] issue-gate | Loop Review Simplicity And Phase Skills

- approved specの「1 cohesive issue」判断に従い、`LRSP-001`だけを持つ日本語local-first Issue台帳を追加した。
- blocker graphは単一nodeでcycleなし、`LRSP-001`は`実行可能`。session userは2026-07-27T07:59:52+09:00にIssue scope、write scope、acceptance criteria、実行順序、remote policyをIssue Gateとして承認した。
- worker write scopeは両loop skill、shared context parser / inspector / report / tests、context baselineに限定した。台帳、implementation plan、sealed packet、index、logはplanning coordinator ownershipとしてworker scopeから除外した。
- GitHub Issue mirrorとissue PRは作らず、remote policy `per_action`を維持する。

## [2026-07-27] spec-amendment-gate | Loop Review Simplicity And Phase Skills

- implementation plan scope checkで、operation固定の`dispatch_skills`だけでは、今回のskill edit workerに必須な`writing-skills`のようなtask-triggered skillを表現できない矛盾を検出した。
- session userは、`skills` / `dispatch_skills`をphase-owned workflow skillの宣言に限定し、task-triggered skillは該当phaseでon-demandに読み、future phaseでは先読みしないclarificationを承認した。
- universal allowlist、task-specific worker packet field、generic loader、install inventory validatorは追加しない。
- session userは`knowledge/wiki/syntheses/loop-review-simplicity-and-phase-skills/spec.md`、raw-byte SHA-256 `2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719`を2026-07-27T08:14:23+09:00にSpec Gateとして承認した。approval scopeは`accepted_decisions`、`non_goals`、`acceptance_criteria`、`verification`、`remote_policy`、`stop_conditions`の全六項目である。
- 既存Issue Gate commitは旧spec digestを参照するため、Issue台帳をamended specへreconcileして再承認するまでimplementationへ進まない。

## [2026-07-27] issue-reconciliation-gate | Loop Review Simplicity And Phase Skills

- `LRSP-001`のapproved spec digest / commitを`2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719` / `9f6dba0`へ更新し、review状態を再承認前の`下書き`へ戻した。
- worker scope、単一node blocker graph、material review、remote policyは変更していない。phase-owned workflow skillはcontractで固定し、task-triggered `writing-skills`は本skill-edit taskのimplementation phaseでon-demandに使うclarificationだけを追加した。
- universal allowlist、worker packet field、generic loader、install inventory validatorは非目標のままである。
- session userは2026-07-27T08:17:21+09:00にreconciled `LRSP-001`のIssue scope、write scope、acceptance criteria、実行順序、remote policyをIssue Gateとして再承認した。

## [2026-07-27] execution-plan-candidate | Loop Review Simplicity And Phase Skills

- `LRSP-001`のimplementation planをbaseline pressure RED、schema v3 phase skill contract、material review contract、baseline refresh / full verificationの4 taskとして作成した。execution work itemは1件のままである。
- shared parserとruntime selectorに同じ`skills` / `dispatch_skills` projectionを追加し、task-triggered `writing-skills`はcurrent implementation phaseだけでon-demandに使う。新しいloaderやpacket fieldは作らない。
- approved IssueをInput Packet v2 draftへ正規化した。delivery intentは`per_action`、GitHub Issue mirrorとissue PRはなし、worker write scopeはreconciled ledgerと同一である。
- final packet seal、capability preflight、Execution Plan Gate commit、worker dispatch、remote writeはまだ行っていない。

## [2026-07-27] execution-plan-gate | Loop Review Simplicity And Phase Skills

- session userは2026-07-27T08:23:49+09:00に`LRSP-001` implementation planをExecution Plan Gateとして承認した。
- implementation plan raw-byte SHA-256は`4a4e4041425626bc59d97597b0c2836278575f8987c5900cc4176a7072f2499b`。承認済みspec raw-byte SHA-256 `2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719`へInput Packet v2をsealした。
- sealed Input Packet raw-byte SHA-256は`ea0a34f7f2899a54a691b5d5c21edcc93cb545f06d459b17940b42f2f9e606e8`。packet validator、approved spec binding verify、capability preflightはいずれも成功した。
- executionはfresh coordinatorから`issue-implementation-loop`へ引き渡し、workerはapproved write scope内でTDDとskill pressure testを実行する。remote writeはlocal `PR_READY`後のRemote Gateまで行わない。

## [2026-07-27] execution-plan-amendment-candidate | Loop Review Simplicity And Phase Skills

- fresh baselineではmaterial simplicityとphase loadingのREDを再現した。一方、nit-pressure controlは3 fresh evaluatorsすべてがstyle-only findingを拒否し、現行挙動が既にGREENだった。
- failureを捏造しないため、3件すべてをREDとする計画文を「review policyとphase loadingで各1件以上のRED、既存GREENはregression target」に最小修正した。spec、Issue scope、acceptance criteria、Input Packet bytes、remote policyは変更していない。
- amendment candidateのimplementation plan raw-byte SHA-256は`483f4131e65b953d25ac5da769cfc177f4605e81d14390f998f83edc1b2f4d93`。Execution Plan Gate再承認とcommit前であり、workerはproduction editなしで停止している。

## [2026-07-27] execution-plan-amendment-gate | Loop Review Simplicity And Phase Skills

- session userは2026-07-27T08:40:40+09:00にimplementation plan amendmentをExecution Plan Gateとして承認した。
- approved implementation plan raw-byte SHA-256は`483f4131e65b953d25ac5da769cfc177f4605e81d14390f998f83edc1b2f4d93`。material simplicityとphase loadingのbaseline REDを必須とし、既にGREENのnit抑制はfailureを捏造せずregression targetとして保持する。
- approved spec raw-byte SHA-256 `2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719`、sealed Input Packet raw-byte SHA-256 `ea0a34f7f2899a54a691b5d5c21edcc93cb545f06d459b17940b42f2f9e606e8`、Issue scope、acceptance criteria、remote policyは不変である。

## [2026-07-27] local-pr-ready | Loop Review Simplicity And Phase Skills

- `LRSP-001`はExecution Envelope revision 2で実装・検証・reviewを完了した。実装commitは`10c3cf49d846585cbd5a51ae18e1141ded113572`、review fix commitは`fbaaeeda0e1808d25ab4e029e12eaf0eac19fd1d`。
- schema v3は両loopの全operationに`skills` / `dispatch_skills`を明示し、shared inspector/reportとruntime selectorが同じboundaryを返す。schema v1/v2と`llm-wiki` schema v2は維持した。
- reviewは要件達成、material simplicity、material riskの順とし、`Critical` / `Important`だけをfindingにする。concrete materially simpler alternativeを示せるsimplicity gapは`intent_gap` / `Important`、residual riskはmaterial unresolvedまたはhuman-accepted riskだけに限定した。
- fresh pressure evidenceはnit抑制、material simplicity、phase loadingのbaseline/postを既存worker report schema内に記録した。grill 60、issue loop 292、scripts 59、llm-wiki 6の計417 tests、architecture/context/strict report、dual-host、両quick validator、`git diff --check`がpassした。
- implementation review cycle 1のImportant 2件をfix/report evidenceでcloseし、cycle 2は`Critical` / `Important`なしでapproved。material residual riskなし。
- runtimeはlocal `PR_READY`。GitHub Issue mirror、push、draft PR、ready-for-review、merge、release、live installは未実施であり、pushとdraft PRはexact Remote Gate待ちである。

## [2026-06-08] bootstrap | Initialize skills repo knowledge root

- repo root に thin router `AGENTS.md` を追加
- `knowledge/` を single-root topology の knowledge root として作成
- `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を作成
- Goal command 用の詳細仕様を `knowledge/wiki/syntheses/` に保存する routing を明確化

## [2026-06-08] ingest | LLM Wiki Draft Review And Canonicalize Design

- 添付設計を `knowledge/raw/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md` に保存
- source summary `knowledge/wiki/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md` を追加
- Goal 実装契約 `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` を追加
- `index.md` に source summary と synthesis を登録

## [2026-06-09] canonicalize | LLM Wiki reference read set

- `skills/llm-wiki` の always-read contract を `core.md` に絞り、layout / page authoring detail を conditional reference へ分離
- `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` の stale reference 名を更新
- `knowledge/AGENTS.md` に skill-local base read set と conditional detail reference の方針を追記

## [2026-06-10] query | Portfolio OS install review and procedure

- Portfolio OS 固有 runtime が `skills/llm-wiki` 本体に混入していないことを確認
- `knowledge/wiki/syntheses/Portfolio OS Install Review And Procedure.md` に導入レビューと install procedure を追加
- `index.md` に synthesis を登録

## [2026-06-13] lint | Markdown-first link policy

- `skills/llm-wiki` の link policy と templates を relative Markdown link canonical に更新
- `knowledge/` の active wiki links を Obsidian wikilink から relative Markdown link に更新
- rename / canonicalize は今回行わず、既存 filename を維持

## [2026-06-13] canonicalize | Slug filename policy

- Action: rename
- Actor: repository maintainer-delegated actor
- Owner: repository maintainer or maintainer-delegated actor
- Write Boundary: owned; owner canonical update allowed by local contract
- `knowledge/wiki/**` の active canonical page 3 件を URL と CLI で扱いやすい lower-kebab-case slug へ rename
- `knowledge/index.md`、wiki page 間 link、`skills/llm-wiki` の naming default と templates を slug 優先へ更新
- `knowledge/raw/**` は immutable source material として rename せず維持

## [2026-06-18] query | Implementation progress ledger pattern

- `skills/llm-wiki` の generic docs/templates に implementation progress ledger pattern を追加
- ledger は `wiki/syntheses/` の active canonical durable synthesis とし、`index.md` から発見でき、更新時は `log.md` に lifecycle entry を残す方針を明記
- 個別 spec / plan / progress note を置き換えず、partial implementation state、remaining scope、evidence、next trigger、review-after への横断 discovery surface として扱う
- validator、scheduler、Dataview、Obsidian plugin、issue tracker 連携は必須化しない

## [2026-06-20] query | Grill to PR Loop issue implementation review gate plan

- `skills/grill-to-pr-loop` に issue 単位の実装レビューゲートを追加する実装計画を `knowledge/wiki/syntheses/grill-to-pr-loop-issue-implementation-review-gate-plan.md` に保存
- `superpowers:requesting-code-review` を既定レビュー手段とし、local issue completion / blocker release / PR creation 前に review gate を通す方針を整理
- `knowledge/index.md` に synthesis を登録

## [2026-06-23] ingest | Grill to PR Loop skill split v2

- 添付設計を `knowledge/raw/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md` に保存
- source summary `knowledge/wiki/sources/2026-06-21-grill-to-pr-loop-skill-split-design-v2.md` を追加
- 実装契約 `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-spec.md` とローカルIssue ledger `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-issues.md` を追加
- `knowledge/index.md` に source summary と synthesis を登録

## [2026-06-23] implementation | Grill to PR Loop skill split v2

- `skills/issue-implementation-loop/` を追加し、mode router、reference read set、schemas、templates、validation/scheduler/recovery helper scripts、pressure scenario tests を実装
- `skills/grill-to-pr-loop/` を composition skill に縮小し、execution phase を `issue-implementation-loop` に委譲する契約へ更新
- 独立実装レビューで検出された pending runnable 候補同士の write-scope conflict 漏れを修正し、回帰テストを追加
- `knowledge/wiki/syntheses/grill-to-pr-loop-skill-split-v2-issues.md` に実装レビュー結果、検証結果、local-only PR 未作成理由を記録

## [2026-06-24] query | Grill to PR Loop branch policy spec

- `grill-to-pr-loop` / `issue-implementation-loop` の branch、worktree、commit、integration branch 推奨運用を `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-spec.md` に保存
- local issue ledger `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-issues.md`、input packet、execution envelope を追加
- remote write は未承認のため `local_only` とし、GitHub issue / PR / merge は行わない

## [2026-06-24] implementation | Grill to PR Loop branch policy

- `skills/grill-to-pr-loop` に `epic_base`、issue branch/worktree reservation、scoped local commit review の方針を追加
- `skills/issue-implementation-loop` に `base_policy` validation、integration head validation、`working-tree` review range rejection を追加
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に branch/base/commit policy の回帰テストを追加
- `knowledge/wiki/syntheses/grill-to-pr-loop-branch-policy-issues.md` に実装状態を反映

## [2026-06-24] review-fix | Grill to PR Loop branch policy

- 実装レビュー指摘を受け、`epic_base.ref` / `epic_base.sha` の required / full SHA validation を追加
- `PR_READY` / `COMPLETE` / `DONE` の runtime state に committed `BASE_SHA..HEAD_SHA` review range を必須化
- 複数 `branch_from_integration_head` dependency を拒否し、integration head は単一 base に限定

## [2026-06-24] query | Issue Implementation Loop context policy spec

- `issue-implementation-loop` の context/session policy を `knowledge/wiki/syntheses/issue-implementation-loop-context-policy-spec.md` に保存
- local issue ledger `knowledge/wiki/syntheses/issue-implementation-loop-context-policy-issues.md` と input packet を追加
- remote write は未承認のため `local_only` とし、GitHub issue / PR / merge は行わない

## [2026-06-24] implementation | Issue Implementation Loop context policy

- `skills/issue-implementation-loop/SKILL.md` を trigger-only description と 520 words 以下の entrypoint に圧縮
- `context_policy` を Execution Envelope reference / schema / template / validator に追加
- worker contract に paths-first packet、full source paste 禁止、report budget を追加
- context/session policy の回帰テストを追加し、既存 branch/base/commit policy tests と合わせて検証

## [2026-06-24] query | Grill to PR Loop epic-base delivery policy spec

- issue PR を `codex/<epic-id>/epic-base` へ作成し、guarded agent merge を既定にする方針を `knowledge/wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-spec.md` に保存
- final PR は `epic_base.ref` から `main` へ作成し、final PR merge は human-only とする
- local issue ledger `knowledge/wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-issues.md` を追加

## [2026-06-24] implementation | Grill to PR Loop epic-base delivery policy

- `skills/issue-implementation-loop` の Execution Envelope validation に `batch_issue_prs`、`codex/<epic-id>/epic-base`、issue PR guarded merge、final PR human-only、review cycle 上限 2 回を追加
- `skills/grill-to-pr-loop` / `skills/issue-implementation-loop` の docs、templates、schemas、agent metadata を epic-base delivery policy に更新
- `knowledge/wiki/syntheses/grill-to-pr-loop-epic-base-delivery-policy-issues.md` に実装状態と検証結果を反映

## [2026-06-24] review-fix | Grill to PR Loop epic-base delivery policy

- 実装レビュー指摘を受け、success status に approved review または human risk acceptance を必須化
- `release_on: review_approved` が success status だけで descendant を release しないように修正
- `delivery_intent` validation、`remote_write_policy` type guard、`batch_issue_prs` schema required fields を追加

## [2026-06-24] query | Grill to PR Loop epic-base lifecycle hardening spec

- `epic_base` を名前だけの policy ではなく delivery/integration branch resource として lifecycle 管理に載せる方針を `knowledge/wiki/syntheses/grill-to-pr-loop-epic-base-lifecycle-hardening-spec.md` に保存
- `epic_base.branch_state`、optional `epic_base.worktree_path`、reconcile での branch existence 検証、`pr_created` / `pr_merged` event rebuild を acceptance criteria に追加
- `knowledge/index.md` に synthesis を登録

## [2026-06-25] query | Loop skill context optimization spec

- `grill-to-pr-loop` と `issue-implementation-loop` を 2 user-facing skill のまま維持しつつ、reference 分割、repo-local skill root 優先、後続 `_common.py` lib 分割へ進める方針を `knowledge/wiki/syntheses/loop-skill-context-optimization-spec.md` に保存
- local issue ledger `knowledge/wiki/syntheses/loop-skill-context-optimization-issues.md` と normalized input packet `knowledge/wiki/syntheses/loop-skill-context-optimization-input-packet.json` を追加
- remote write は未承認かつ `gh` auth unavailable のため `local_only` とする

## [2026-06-25] implementation | Loop skill context optimization first slice

- `skills/grill-to-pr-loop/references/workflow-contract.md` を router 化し、planning / local issue ledger / execution handoff / remote delivery / common mistakes の one-level references へ分割
- `skills/grill-to-pr-loop/SKILL.md` に workflow router の読み方を明記
- `skills/grill-to-pr-loop/scripts/check_prereqs.py` と `skills/issue-implementation-loop/scripts/_common.py` の skill root discovery を repo-local `skills/` 優先へ変更
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` を追加し、reference routing と root ordering を回帰テスト化
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` に repo-local skill root 優先の回帰テストを追加

## [2026-06-25] review-fix | Loop skill context optimization first slice

- 実装レビュー指摘を受け、`GitHub Mirror Gate` の具体手順を `remote-delivery.md` へ集約し、router の GitHub mirror read set と一致させた
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` に mirror gate routing regression を追加
- `knowledge/wiki/syntheses/loop-skill-context-optimization-issues.md` に draft PR #15 と実装レビュー状態を反映
- input packet の `spec.approved_hash` を存在しない base commit 参照から `local-draft-reviewed` へ修正

## [2026-06-25] query | Issue Implementation Loop common lib split spec

- `loop-skill-context-optimization` の後続 slice として、`issue-implementation-loop/scripts/_common.py` を internal common lib へ分割する draft spec を `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-spec.md` に保存
- local issue ledger `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md` と normalized input packet `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-input-packet.json` を追加
- user-facing skill は `grill-to-pr-loop` / `issue-implementation-loop` の 2 つに留め、remote write は `local_only` とする

## [2026-06-25] implementation | Issue Implementation Loop common lib split

- `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/` を追加し、validation / scheduler / delivery / git / skill discovery を domain module へ分割
- `skills/issue-implementation-loop/scripts/_common.py` は backward-compatible facade に縮小し、既存 public scripts の import surface を維持
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py` を behavior domain files へ分割し、common-lib split regression を追加
- `knowledge/wiki/syntheses/issue-implementation-loop-common-lib-split-issues.md` に実装状態、manual review fallback、検証結果を反映

## [2026-06-25] ingest | Loop skill architecture v3 design

- 添付設計を `knowledge/raw/sources/2026-06-25-loop-skill-architecture-v3-design.md` に保存
- source summary `knowledge/wiki/sources/2026-06-25-loop-skill-architecture-v3-design.md` を追加
- Spec Gate 用 draft `knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md` を追加
- 既存実装済み範囲と未実装範囲を分離し、Issue ledger / Execution Packet / 実装は Spec Gate 承認後に進める方針を明記
- `knowledge/index.md` に source summary と synthesis を登録

## [2026-06-25] query | Loop skill architecture v3 local issues

- Spec Gate 承認を受け、Issue Gate 用 draft `knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md` を追加
- 6 issue の日本語 local-first ledger と blocker graph を作成し、全 issue を `下書き` とした
- `skill-creator` の skill 更新制約を acceptance criteria に反映し、Execution Packet / GitHub mirror / 実装は Issue Gate 承認後に進める方針を維持
- `knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md` と `knowledge/index.md` から issue ledger を発見できるように更新

## [2026-06-25] decision | Loop skill architecture v3 Issue Gate approved

- Issue Gate 承認を受け、`knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md` の全 issue を `承認済み` に更新
- G2PR-001 を土台にし、G2PR-002 から G2PR-005 を並列化可能、G2PR-006 を統合仕上げにする blocker graph を承認済みとして固定
- GitHub issue mirror、実装、push、PR 作成は Execution Plan Gate 承認後まで行わない方針を維持

## [2026-06-25] query | Loop skill architecture v3 input packet

- コミット `7e6c510c8bc10f171c0c154fe6481b1a69c832ed` 後に normalized input packet `knowledge/wiki/syntheses/loop-skill-architecture-v3-input-packet.json` を追加
- delivery intent は `local_only` とし、GitHub issue mirror、push、PR、merge は未承認のまま維持
- G2PR-006 は複数 blocker head を直接 merge しないよう、dependency `base_effect` を `none` として統合仕上げ issue に留める

## [2026-06-25] decision | Loop skill architecture v3 Execution Plan Gate approved

- Execution Plan Gate 承認を受け、`knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md` に承認事項を記録
- `issue-implementation-loop prepare` へ進める状態とし、remote write は引き続き未承認のため `local_only` を維持

## [2026-06-25] prepare | Loop skill architecture v3 execution envelope

- Execution Envelope `knowledge/wiki/syntheses/loop-skill-architecture-v3-execution-envelope.json` を追加
- `epic_base.ref` を `codex/loop-skill-architecture-v3/epic-base`、`epic_base.sha` を `84a2278e9692a3b592fa3195cb956cf74f075a39` として予約
- 全 issue の branch/worktree path を予約し、物理 worktree 作成は未実行
- G2PR-001 のみ `create_on_run`、G2PR-002 から G2PR-006 は `reserved`
- `validate_execution_envelope.py` は `EXECUTION ENVELOPE OK`、`reconcile_git_state.py --json` は `ok: true` / collisions 0

## [2026-06-25] implementation | Loop skill architecture v3 G2PR-006 integration ledger

- `knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md` に G2PR-001 から G2PR-005 の runtime report / review result と、G2PR-006 の代表 verification evidence を反映
- G2PR-006 は approved dependency `base_effect=none` に従い、G2PR-002 から G2PR-005 の heads を branch へ merge せず、各 issue worktree で代表 CLI / tests を実行した evidence を local ledger に集約
- `quick_validate.py` は `ModuleNotFoundError: No module named 'yaml'` のため未検証理由を記録
- 実装ループ中の remote write は approved execution envelope の `remote_write_policy.mode=local_only` かつ Remote Gate 承認なしのため実行していない

## [2026-06-25] delivery | Loop skill architecture v3 draft PR

- ユーザーの明示依頼を受け、統合 branch `codex/skill-loop-optimization` に G2PR-001 から G2PR-006 の承認済み成果を統合
- 統合 branch を `origin/codex/skill-loop-optimization` へ push
- Draft PR [#19](https://github.com/omitsuhashi/skills/pull/19) を `main` 向けに作成
- GitHub issue mirror と merge は未実行

## [2026-06-25] review-fix | Loop skill architecture v3 phase approval commits

- `grill-to-pr-loop` の Spec Gate / Issue Gate / Execution Plan Gate 承認後に、承認済み local artifacts と ledger/log 更新を commit してから次フェーズへ進む契約を追加

## [2026-06-28] ingest | Portfolio OS task backend plugin / skill handoff

- 添付ハンドオフを `knowledge/raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md` に保存
- source summary `knowledge/wiki/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md` を追加
- Spec Gate 前 draft `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md` を追加
- `grill-to-pr-loop` planning prereq は通過、remote write は未承認のため `local_only` として扱う

## [2026-06-28] decision | Portfolio OS task backend plugin package direction

- shared task backend plugin は repository root の `plugins/` 配下に置く方針に更新
- 推奨 package path を `plugins/task-management/` とし、reusable task-management skill と backend adapter code を同じ Codex plugin package に同梱する方向へ spec draft を更新
- GitHub Projects field schema は adapter が create/repair する方針に更新
- first implementation slice は GitHub Projects に完全に接続する live adapter まで含めるが、normal tests は固定テストデータ / 模擬実装、live mutation は Remote Gate / Live Write Approval Gate 後に限定する

## [2026-06-28] decision | Portfolio OS task backend idempotency and live-write UX

- idempotency は task normalization の早い段階で作る canonical task SHA を単一 duplicate key とし、task name / work unit / body の複数 phase fuzzy matching は行わない方針へ更新
- Portfolio OS local idempotency store は作らない方針へ更新
- dry-run mode は作らず、plugin / skill は承認済み task registration を live adapter で実行する方針へ更新
- 保存なしで cross-run duplicate detection は保証できないため、必要なら backend の検索可能 field に SHA を置く前提を spec に明記

## [2026-06-28] decision | Portfolio OS task backend SHA field duplicate guard

- GitHub Projects adapter が adapter-owned `task_sha` field を create/repair する方針へ更新
- cross-run duplicate detection は `task_sha` field を検索し、同じ SHA が存在する場合は新規 task creation を拒否する方針へ更新
- Portfolio OS local idempotency store は引き続き作らず、duplicate result は可能なら既存 `TaskRef` / linkable metadata を返す

## [2026-06-28] decision | Portfolio OS task backend duplicate prevention simplification

- `task_sha` field / dedicated idempotency key / duplicate-prevention store は初回実装から外す方針へ更新
- 重複 task が作られるリスクは許容し、後から GitHub Projects など backend 側で整理する方針へ更新
- GitHub Projects schema と adapter complexity を増やして事前防止するより、task registration plugin として単純な live write path を優先する

## [2026-06-29] decision | Portfolio OS task backend per-write approval

- live-write approval UX は per-write explicit approval とする方針へ更新
- task create/update/comment と GitHub Projects schema create/repair は、各 operation ごとに preview と明示承認を通ってから実行する
- batch approval、policy-gated approval、trusted automation による task write は初回実装の non-goal とする

## [2026-06-29] query | Portfolio OS task backend GitHub Projects API strategy

- 仕様書を日本語見出しへ整理し、推奨 GitHub Projects GraphQL API strategy を追加
- 公式 GitHub Projects API 記事と public GraphQL schema を確認し、`addProjectV2DraftIssue`、`addProjectV2ItemById`、`createProjectV2Field`、`updateProjectV2Field`、`updateProjectV2ItemFieldValue`、`updateProjectV2DraftIssue`、`convertProjectV2DraftIssueItemToIssue` を実装候補として整理
- `plugin-creator` / `skill-creator` に合わせ、`plugins/task-management/` package、同梱 skill、plugin validation、skill quick validation を acceptance criteria に追加

## [2026-06-29] decision | Portfolio OS task backend GitHub CLI first

- GitHub 操作戦略を direct GraphQL first から GitHub CLI (`gh`) first へ更新
- `gh project item-create`、`gh project item-add`、`gh project item-edit`、`gh project item-list`、`gh project field-list`、`gh project field-create` を標準 path とし、`gh api graphql` は `gh project` で不足する操作の fallback とする
- 理由は、task registration、Issue / PR 操作、auth scope、host handling、JSON output を同じ operational surface に集約できるため

## [2026-06-29] review-fix | Portfolio OS task backend Japanese docs and architecture

- review comment を受け、raw source を日本語化し、テスト種別の英語表現を `固定テストデータ / 模擬実装` に更新
- 仕様書にアプリケーション構成を追加し、`gh` を叩く主体を plugin 内 GitHub Projects adapter script として明記
- routing を input routing、task routing、backend routing、operation routing に分け、Portfolio OS local skill、task-management skill、backend adapter、`gh` runner の責務境界を明記
- commit 延期が明示された場合は ledger/log に例外として記録する方針を追加

## [2026-06-25] review-fix | Loop skill architecture v3 code review findings

- code review の Important 指摘を受け、resume brief の recommended next operation を reviewable / fixable / waiting human / runnable の priority に揃えた
- V3 execution envelope artifact に worker packet schema/template/validator 参照を追加し、execution-envelope reference に新規 envelope では3参照を含める方針を明記
- local issue ledger の完了済み G2PR-001 から G2PR-005 の acceptance checklist を `[x]` に揃えた

## [2026-06-26] ingest | Skill repository optimization v4 design

- 添付設計を `knowledge/raw/sources/2026-06-26-skill-repository-optimization-v4-design.md` に保存
- source summary `knowledge/wiki/sources/2026-06-26-skill-repository-optimization-v4-design.md` を追加
- Spec Gate draft `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` を追加
- Issue Gate draft `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` と draft input packet `knowledge/wiki/syntheses/skill-repository-optimization-v4-input-packet.json` を追加
- 全 issue は `下書き`、remote write は `local_only` とし、実装、GitHub issue mirror、push、PR 作成、merge は未実行
- `knowledge/index.md` に source summary、spec、issue ledger を登録

## [2026-06-26] decision | Skill repository optimization v4 Spec Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` を Spec Gate 承認済みに更新
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` は Issue Gate draft のまま維持し、全 issue の `レビュー状態` は `下書き` とした
- `knowledge/index.md` の V4 spec summary を Spec Gate 承認済み契約として更新
- 次フェーズは Issue Gate。GitHub issue mirror、execution packet 承認、実装、push、PR 作成、merge は未承認

## [2026-06-26] decision | Skill repository optimization v4 context compression amendment

- ユーザーの追補を受け、実装開始前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを行う scope を V4 に追加
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` の success criteria、accepted decisions、SRO4-003 decomposition、acceptance criteria、stop conditions を更新
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` の SRO4-003 に `grill-to-pr-loop/SKILL.md` と `references/execution-handoff.md` へ handoff 前 context 圧縮契約を追加する作業を反映
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-input-packet.json` の SRO4-003 acceptance criteria と verification に同じ requirement を反映
- Issue Gate / Execution Plan Gate / 実装 / remote write は引き続き未承認

## [2026-06-26] decision | Skill repository optimization v4 Issue Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` の SRO4-001 から SRO4-006 までの `レビュー状態` を `承認済み` に更新
- blocker graph は SRO4-001 を初期実行可能、SRO4-002 / SRO4-004 以降を依存順にブロックする形で承認済みとして固定
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` を Spec Gate / Issue Gate 承認済み状態へ更新
- `knowledge/index.md` の V4 issue ledger summary を Issue Gate 承認済みとして更新
- 次フェーズは Execution Plan Gate。GitHub issue mirror、実装、push、PR 作成、merge は未承認

## [2026-06-26] decision | Skill repository optimization v4 Execution Plan Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/skill-repository-optimization-v4-input-packet.json` を承認済み packet として記録
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` と `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` を Spec Gate / Issue Gate / Execution Plan Gate 承認済み状態へ更新
- `check_prereqs.py --phase execution --json` と `check_capabilities.py --input knowledge/wiki/syntheses/skill-repository-optimization-v4-input-packet.json --json` はどちらも `ok: true`
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は未承認
- 次フェーズは approval record commit 後の `issue-implementation-loop prepare`

## [2026-06-26] prepare | Skill repository optimization v4 execution envelope

- `knowledge/wiki/syntheses/skill-repository-optimization-v4-execution-envelope.json` を追加
- Envelope は `remote_write_policy.mode=local_only`、`worker_context_required=true`、`coordinator_may_implement=false`
- `epic_base.sha` は approval record commit `a073a10d38744771c2ed10fe8d9d351e5bf0e588`
- SRO4-005 は複数 blocker head を直接 merge しないよう、SRO4-003 / SRO4-004 依存の `base_effect` を `none` として記録
- `validate_execution_envelope.py` は `EXECUTION ENVELOPE OK`
- `reconcile_git_state.py --json` は `ok: true`, collisions 0

## [2026-06-26] decision | Skill repository optimization v4 SRO4-001 scope revision

- SRO4-001 worker dispatch は、`scripts/validate_skill_architecture.py` と `scripts/report_skill_context.py` が存在せず SRO4-001 write scope 外だったため stop condition で停止
- ユーザー承認を受け、SRO4-001 write scope に `path:scripts/validate_skill_architecture.py` と `path:scripts/report_skill_context.py` を追加
- Execution Envelope を revision 2 に更新し、SRO4-001 physical worktree 作成済み状態を `active` として記録
- SRO4-001 の実装は policy validator と baseline report の最小実装に限定し、Context Contract V2 本体 redesign は SRO4-002 に残す
- remote policy は `local_only` のまま維持

## [2026-06-26] review-fix | Skill repository optimization v4 SRO4-001 forbidden-list source

- SRO4-001 implementation review で、既存 `scripts/validate_loop_skill_context.py` の hard-coded forbidden standalone skill list が acceptance criteria 未達として指摘された
- 指摘は妥当と判断し、Execution Envelope を revision 3 に更新
- SRO4-001 write scope に `path:scripts/validate_loop_skill_context.py` を追加し、`skill-architecture.toml` を forbidden list の正本にする fix を worker に回す
- Context Contract V2 本体 redesign は SRO4-002 に残し、remote policy は `local_only` のまま維持

## [2026-06-26] decision | Skill repository optimization v4 SRO4-005 base revision

- SRO4-005 を revision 3 の `epic_base` から dispatch すると、SRO4-002 / SRO4-003 で承認済みの skill-context validator と loop routing 成果を再実装する必要があると判定
- ユーザー承認を受け、Execution Envelope を revision 4 に更新し、SRO4-005 の base を `blocker_head:SRO4-003` に変更
- SRO4-004 は gating dependency のまま維持し、`base_effect=none` として Worker Packet V2 / Resume Brief V2 との code integration は SRO4-006 に残す
- remote policy は `local_only` のまま維持

## [2026-06-26] implementation | Skill repository optimization v4 SRO4-001 policy baseline

- `skill-architecture.toml` を追加し、repository-change-loop family の user-facing skill 2 件と forbidden standalone skill 名を policy 正本にした
- `scripts/validate_skill_architecture.py` を追加し、forbidden standalone skill list を validator code ではなく policy file から読むようにした
- `scripts/report_skill_context.py` を追加し、schema v1 context contract の operation word-count metrics を JSON 出力できるようにした
- current checkout baseline を `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json` に保存し、`knowledge/index.md` から発見できるようにした
- Context Contract V2 本体 redesign、shared metric library、remote write、push、PR 作成は行っていない

## [2026-06-26] implementation | Skill repository optimization v4 SRO4-006 final integration ledger

- SRO4-006 branch `codex/skill-repository-optimization-v4/SRO4-006-integration-ledger` で、SRO4-005 approved head `e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf` に SRO4-004 approved head `e4f7551b49df4082d1266b04b32249a0770d7481` を競合なしで merge した
- merge commit は `0435b90e5227cf84ef0f6e546463b6f8d3d545df`
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` に SRO4-001 から SRO4-006 の implementation review range、verification、compatibility shim rationale、removal conditions、local_only remote policy、residual risks を反映した
- `knowledge/index.md` の V4 Issues entry を final integration / residual risks の discovery surface として更新した
- full verification は architecture/context/report JSON、grill tests、issue-loop tests、llm-wiki tests、Worker Packet V2 / Resume Brief V2 CLI fixture、stale rejection、`git diff --check` で確認した
- remote policy は execution envelope revision 4 の `local_only` のため、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-26] review-sync | Skill repository optimization v4 SRO4-006 final review approval

- SRO4-006 final implementation review が `e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf..b71514cc40a5b6e825d546eaa15fdf92d29677ce` を approved としたことを `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` に同期
- Critical / Important finding はなし
- 既存 residual risks は維持: `local_only` のため GitHub Actions matrix は未実行、coordinator runtime/events resume mismatch `runtime=4 events=1` は後続 hardening risk
- remote policy は `local_only` のため、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-26] review-fix | Skill repository optimization v4 PR #20 hardening

- Draft PR #20 作成後の code review で、CI の `git diff --check` が clean tree だけを見ている点と、`llm-wiki` operations が baseline comparison 外になっている点を Important として確認
- `.github/workflows/skill-architecture.yml` は checkout `fetch-depth: 0` と event-aware base range を使う whitespace check に変更
- `scripts/report_skill_context.py` に `--require-baseline`、`--fail-on-warning`、`--emit-baseline`、`--output` を追加し、warnings を stderr にも出すようにした
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json` を post-V4 の 3 skills / 28 operations baseline として再生成
- PR #20 の GitHub Actions matrix は Python 3.9 / 3.12 とも成功済み。merge は human-only のまま

## [2026-06-26] review-fix | Skill repository optimization v4 compatibility removal

- ユーザー方針により、loop 専用 wrapper CLI `scripts/validate_loop_skill_context.py` / `scripts/inspect_loop_skill_context.py` を削除し、canonical CLI を `validate_skill_context.py` / `inspect_skill_context.py` / `report_skill_context.py` に一本化した
- `skills/grill-to-pr-loop/references/workflow-contract.md` を削除し、operation routing の正本を `context-contract.toml` だけにした
- `scripts/inspect_skill_context.py` は `llm-wiki` の topology × mode contract も扱える canonical inspector に更新した
- V4 spec / issue ledger / tests は wrapper と workflow shim が残らない前提に更新した

## [2026-06-29] review-fix | Portfolio OS task backend plugin routing and gh boundary

- `portfolio-os-task-backend-plugin-skill-spec.md` の review comment を受け、GitHub Projects adapter を厚い wrapper ではなく `gh` command planner + 最小 executor として定義し直した
- 実行予定の `gh` argv を approval preview と tests で確認できるようにし、executor の責務を `shell=False` 実行、stdout / stderr / exit code / JSON output 捕捉、redaction、typed result 整形に限定した
- backend routing は runtime config の backend key で行い、初回実装の default backend を `github_projects` とする方針を明記した
- target config は `TASK_MANAGEMENT_BACKENDS_CONFIG` または `plugins/task-management/config/task-backends.toml` から読み、repository には `plugins/task-management/config/task-backends.example.toml` を commit する方針を追加した
- 最終的な task state は GitHub Projects に保存し、Portfolio OS は backend task reference と source trail / routing rationale / decision log だけを保持する方針を再確認した

## [2026-06-29] review-fix | Portfolio OS task backend plugin subprocess and field override clarification

- `subprocess.run` を初回実装の必須構成から外し、承認済み `gh` command は Codex agent / plugin runtime が直接実行する方針へ更新した
- `subprocess.run([...], shell=False)` 相当の OS process invocation は、将来 Python / MCP server など非対話 runtime へ移す場合だけの実装詳細として扱う
- `plugins/task-management/` の想定 layout から `gh_executor.py` を外し、`github_projects_commands.py` は許可された `gh` command plan と結果解釈の仕様に限定した
- backend field config は同名 mapping を列挙せず、canonical field name と GitHub Projects field name が違う場合だけ `field_overrides` に書く方針へ変更した

## [2026-06-29] decision | Portfolio OS task backend GitHub MCP Server first

- ユーザー承認を受け、GitHub Projects 連携を独自 GitHub adapter / `gh` command planner / direct GraphQL fallback 実装ではなく GitHub MCP Server first 方針へ変更した
- `portfolio-os-task-backend-plugin-skill-spec.md` を MCP-first 版に差し替え、backend contract を `TaskBackendAdapter` から `TaskBackendRoute` 中心に更新した
- task-management plugin は `TaskDraft` 正規化、backend routing、approval preview、MCP preflight / tool invocation contract だけを持ち、GitHub credential / MCP server registration / tool enablement は Hermes Agent host 側に残す
- GitHub Projects field schema create/repair は初回実装 scope から外し、pre-existing validation と人間向け setup guidance に限定した
- Hermes Agent で `hermes mcp list` が `No MCP servers configured` を返すこと、`approvals.mode: manual`、`mcp_reload_confirm: true`、`delegation.inherit_mcp_toolsets: true` を read-only で確認し、write-capable GitHub MCP tools の無条件 delegation 継承を stop condition に追加した

## [2026-06-29] review-fix | Portfolio OS task backend usable MCP route and work unit display

- GitHub Projects 上で人間が判断できるよう、`TaskDraft` と approval preview に `work_unit_id` だけでなく `work_unit_name` を必須表示として追加した
- `work_unit_id` は stable routing key、`work_unit_name` は backend 上の display label として扱い、work unit rename による表示ずれを既知リスクに追加した
- 将来 backend は MCP / reader / skill graph、CLI、URL interface を routing 先として使い、task-management plugin は原則として backend API client を自作しない方針を追加した
- 初回実装 scope を routing contract だけでなく、インストール可能な plugin / skill、Hermes enablement runbook、review / approval / routing / MCP tool invocation まで実利用できる形に引き上げた
- GitHub MCP Server の read/write 自体は plugin の live smoke test 対象から外し、routing、preview、approval guard、typed error mapping を固定テストデータと模擬 tool で検証する方針に変更した

## [2026-06-29] decision | Portfolio OS task backend plugin and skill packaging boundary

- ユーザー承認を受け、`task-management` は薄い plugin package と、その中に同梱する primary `task-management` skill として実装する方針に確定した
- plugin package は distribution / install-update / config template / examples / references の単位とし、通常の実行 surface は同梱 skill が担う
- 初回実装では公開 entrypoint skill を `task-management` 1 つに保ち、`daily-review` や `backend-admin` などの追加 skill は trigger / permission / context budget が明確に分かれた後続 scope とした
- GitHub read/write adapter や MCP server 実装は plugin package に入れず、GitHub MCP Server など host-provided interface へ routing する方針を維持した

## [2026-06-29] review-fix | Portfolio OS task backend route destination split

- review comment を受け、backend config が GitHub owner / project number / repository などの具体的 target を持つ設計を修正した
- `TaskBackendRoute` は MCP / reader / skill / CLI / URL などの接続面を表し、`TaskBackendDestination` は caller / profile / host-provided registration から渡される実際の外部プロジェクト管理先を表すように分離した
- `plugins/task-management/config/task-backends.example.toml` に置くのは `kind`、`connection_ref`、capability、任意の field override だけとし、owner / project number / repository は必須設定にも既定値にも含めない
- GitHub Projects の project や Issue repository が必要な場合も、plugin package が分解保持せず、`destination_ref` / `content_target_ref` の opaque reference として caller / profile / host 側から渡す方針にした

## [2026-06-29] review-fix | Portfolio OS task backend adapter dispatch scope

- review comment を受け、`task-management` plugin / skill の責務を task taxonomy、TaskDraft composition、routing、adapter operation envelope、preview / guard、typed result mapping に絞り直した
- remote write policy、GitHub Projects mutation、GitHub issue/PR、push、PR creation、merge は adapter / host / delivery workflow の責務であり、この issue の実装対象ではないと明記した
- `Remote Gate` / `Live Write Approval Gate` を削除し、adapter へ渡す envelope を確認する `Adapter Dispatch Review` と、host 側 tool availability を確認する `Adapter Availability Gate` に置き換えた
- GitHub MCP Server の read/write 自体ではなく、task composition、routing、adapter operation envelope、preview、guard、typed result mapping を固定テストデータと模擬 tool で検証する方針に更新した

## [2026-06-29] decision | Portfolio OS task backend adapter dispatch boundary approved

- ユーザー承認を受け、`task-management` plugin / skill の実装 scope は task taxonomy、TaskDraft composition、backend / destination routing、adapter operation envelope、preview / guard、typed result mapping までに確定した
- remote write policy、GitHub Projects mutation、GitHub issue/PR、push、PR creation、merge は adapter / host / delivery workflow の責務であり、この issue の実装対象ではない方針を accepted decision とした
- 実装時は、外部 adapter へ渡す envelope と adapter から返る typed result を中心に検証し、GitHub MCP Server 自体の read/write は plugin の live smoke test 対象にしない

## [2026-06-29] decision | Portfolio OS task backend Spec Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md` を Spec Gate 承認済み仕様として扱う
- 承認済み Epic ID は `portfolio-os-task-backend-plugin-skill`
- 次フェーズは Issue Gate。日本語 local-first issue ledger を作成し、blocker graph、依存順、acceptance criteria、実行可能 / ブロック中 status を提示する
- 実装、Execution Packet、GitHub issue mirror、push、PR 作成、merge はまだ行わない

## [2026-06-29] draft | Portfolio OS task backend Issue Gate ledger

- Spec Gate 承認後の後続作業として、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md` を Issue Gate draft として追加した
- local issue IDs は POTASK-001 から POTASK-009 とし、plugin scaffold、contract、task taxonomy、backend / destination routing、work unit display、adapter operation envelope、GitHub MCP route preflight、Hermes availability runbook、integration docs の順に分解した
- local issue ledger は canonical、GitHub issue mirror は未作成、全 issue の `レビュー状態` は `下書き` とした

## [2026-06-29] decision | Portfolio OS task backend Issue Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md` を Issue Gate 承認済み ledger として扱う
- POTASK-001 から POTASK-009 の粒度、blocker graph、依存順、`実行可能` / `ブロック中` status、acceptance criteria を承認済みとした
- GitHub issue mirror、Execution Packet、実装、push、PR 作成、merge はまだ行っていない

## [2026-06-29] draft | Portfolio OS task backend Execution Plan packet

- Issue Gate 承認後の後続作業として、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-input-packet.json` を Execution Plan Gate draft として追加した
- packet は POTASK-001 から POTASK-009 の acceptance criteria、non-goals、verification、write scope、dependencies を `issue-implementation-loop` 用に正規化する
- `delivery_intent` は `local_only` とし、GitHub issue mirror、push、PR 作成、merge は未実行かつ未承認のままとした

## [2026-06-29] decision | Portfolio OS task backend Execution Plan Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-input-packet.json` を Execution Plan Gate 承認済み packet として扱う
- `delivery_intent` は `local_only`、implementation coordinator は `issue-implementation-loop`、worker-context-required 方針で進める
- 承認後の次作業は `issue-implementation-loop prepare`。GitHub issue mirror、push、PR 作成、merge はまだ行っていない

## [2026-06-29] prepare | Portfolio OS task backend execution envelope

- `issue-implementation-loop prepare` として、`knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-execution-envelope.json` を追加した
- envelope は `worker_context_required=true`、`coordinator_may_implement=false`、`serial_fallback_mode=worker_context_only`、`remote_write_policy.mode=local_only` とする
- POTASK-001 から POTASK-009 の branch / worktree path は予約のみで、物理 worktree 作成や issue implementation はまだ行っていない
- `validate_execution_envelope.py`、`reconcile_git_state.py --json`、`validate_skill_context.py --all`、`git diff --check` は通過した

## [2026-06-29] implementation | POTASK-001 scaffold PR_READY

- POTASK-001 worker が `plugins/task-management/` の thin plugin scaffold と primary `task-management` skill skeleton を実装し、commit `248d7a4a50e90f9ce05515cae5c05251b769c978` を作成した
- `plugin-creator` validator、`skill-creator` quick validation、`git diff --check 341d776703b837f3bd148965ba8c6ee8e3633bdf..248d7a4a50e90f9ce05515cae5c05251b769c978` は通過した
- implementation review は `341d776703b837f3bd148965ba8c6ee8e3633bdf..248d7a4a50e90f9ce05515cae5c05251b769c978` を approved とし、Critical / Important / Minor finding はなし
- 下流 worker が scaffold を見られるよう、execution envelope を revision 2 に更新し、POTASK-002 / POTASK-003 / POTASK-004 の base policy を POTASK-001 head へ向けた

## [2026-06-29] implementation | POTASK-002/003/004 PR_READY

- POTASK-002 worker が backend-neutral contract と fixture tests を実装し、review 指摘後に nested provider raw ID check を harden した commit `ed250ca6fe2c1ea38af05bba26a0cd3511413bf8` を作成した
- POTASK-003 worker が task taxonomy / `TaskDraft` composition reference / preview example を実装し、review 指摘後に `SKILL.md` から `task-draft-contract.md` への参照導線を追加した commit `b2ad95a06c0643c4486d1ef05bc6034d958be1f1` を作成した
- POTASK-004 worker が backend route と destination separation config / reference を実装し、commit `c724ee94dd4dae3d74c5e52564f8eded52b69dfb` を作成した
- POTASK-002、POTASK-003、POTASK-004 の implementation review は approved。`PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` と各 commit range の `git diff --check` は通過した
- POTASK-003 の review fix が `SKILL.md` を触るため、input packet と execution envelope の POTASK-003 write scope に `plugins/task-management/skills/task-management/SKILL.md` を追加し、execution envelope を revision 3 に更新した

## [2026-06-29] plan-fix | POTASK-005 base policy

- POTASK-005 は POTASK-003 の `task-draft-contract.md` と task preview example を継続編集するため、branch base を `epic_base` から POTASK-003 head に変更した
- POTASK-002 は contract 前提として `artifact_ready` dependency のまま維持し、POTASK-005 の code base には混ぜない
- execution envelope を revision 4 に更新し、POTASK-005 の `base_policy` と POTASK-003 dependency の `base_effect` を `branch_from_blocker_head` に揃えた

## [2026-06-29] implementation | POTASK-005 work unit preview PR_READY

- POTASK-005 worker が `work_unit_id` を stable routing key、`work_unit_name` を backend display label として明文化し、unknown display label の human review fallback を追加した
- 実装 commit は `c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386`、review range は `b2ad95a06c0643c4486d1ef05bc6034d958be1f1..c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386`
- implementation review は approved。`PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` は 9 tests OK、`git diff --check b2ad95a06c0643c4486d1ef05bc6034d958be1f1..c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386` は通過した
- POTASK-006 の blocker が解放され、次の runnable issue になった

## [2026-06-29] plan-fix | POTASK-006 base policy

- POTASK-006 は POTASK-005 の `task-create-preview.example.md` を継続編集するため、branch base を `epic_base` から POTASK-005 head に変更した
- POTASK-002、POTASK-003、POTASK-004 は contract / taxonomy / routing 前提として `artifact_ready` dependency のまま維持し、POTASK-006 の code base には混ぜない
- execution envelope を revision 5 に更新し、POTASK-006 の `base_policy` と POTASK-005 dependency の `base_effect` を `branch_from_blocker_head` に揃えた

## [2026-06-29] review-fix | POTASK-006 adapter dispatch contract

- POTASK-006 review で、update/comment/report envelope が既存 task を示す opaque `task_ref` を持たず、create 以外の operation target を完全に表現できない gap を確認した
- 同 review で、`adapter-dispatch.md` が `SKILL.md` から到達できず、Adapter Dispatch Review guard が通常 skill flow に乗らない gap を確認した
- review fix のため、POTASK-006 write scope に `plugins/task-management/skills/task-management/SKILL.md` を追加し、execution envelope を revision 6 に更新した

## [2026-06-29] implementation | POTASK-006 adapter dispatch PR_READY

- POTASK-006 worker が adapter-neutral operation envelope、Adapter Dispatch Review guard、create/update/comment/report intent、expected adapter side effects、`task_ref` guard を定義した
- 実装 commit は `0ce0ffa6eae53b7f085e64af1a453749f82cc3ba`、review range は `c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386..0ce0ffa6eae53b7f085e64af1a453749f82cc3ba`
- 初回 review では `task_ref` 欠落と `SKILL.md` 参照導線欠落が Important として出たが、修正後の re-review は approved になった
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` は 16 tests OK、`git diff --check c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386..0ce0ffa6eae53b7f085e64af1a453749f82cc3ba` は通過した
- POTASK-007 の blocker が解放され、次の runnable issue になった

## [2026-06-29] plan-fix | remaining task backend base policies

- POTASK-007 は POTASK-006 の adapter dispatch contract を前提にするため、branch base を POTASK-006 head に変更した
- POTASK-008 は POTASK-007 の `github-mcp-projects.md` を継続編集するため、branch base を POTASK-007 head に変更した
- POTASK-009 は POTASK-008 後の package / docs を統合確認するため、branch base を POTASK-008 head に変更した
- execution envelope を revision 7 に更新し、残り issue の `base_policy` と対応 dependency の `base_effect` を `branch_from_blocker_head` に揃えた

## [2026-06-29] implementation | POTASK-007 GitHub MCP route PR_READY

- POTASK-007 worker が `github_projects_mcp` route の preflight typed result と `TaskWriteResult` normalization contract を fixture-backed tests で実装した
- 実装 commit は `ed62de954b57ff4c5b32f6efaa6098843d85c1ac`、review range は `0ce0ffa6eae53b7f085e64af1a453749f82cc3ba..ed62de954b57ff4c5b32f6efaa6098843d85c1ac`
- implementation review は approved。Minor として value-level raw ID/auth scan と `SKILL.md` 参照導線が残ったが、POTASK-007 の blocker ではなく POTASK-009 統合確認で扱う
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` は 21 tests OK、`git diff --check 0ce0ffa6eae53b7f085e64af1a453749f82cc3ba..ed62de954b57ff4c5b32f6efaa6098843d85c1ac` は通過した
- POTASK-008 の blocker が解放され、次の runnable issue になった

## [2026-06-29] implementation | POTASK-008 Hermes MCP governance PR_READY

- POTASK-008 worker が host / adapter-side Adapter Availability Gate、credential boundary、Hermes `delegation.inherit_mcp_toolsets: true` の risk、child-agent inheritance guard を文書化した
- 実装 commit は `06f9b6fc7801271f345a8c2772a6d64e7c64f310`、review range は `ed62de954b57ff4c5b32f6efaa6098843d85c1ac..06f9b6fc7801271f345a8c2772a6d64e7c64f310`
- implementation review は approved。Critical / Important / Minor finding はなし
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` は 21 tests OK、`git diff --check ed62de954b57ff4c5b32f6efaa6098843d85c1ac..HEAD` は通過した
- coordinator runtime は POTASK-008 を `PR_READY` とし、scheduler は POTASK-009 のみ runnable と判定した
- resume brief cache の再生成は workspace 外 runtime cache への escalated write として拒否されたため未実施。canonical runtime-state / events / worker report は validation 済み

## [2026-06-29] implementation | POTASK-009 task-management final integration

- POTASK-002 承認済み artifacts から `task-contracts.md`、contract fixtures、`test_task_contracts.py` を個別に取り込み、現行の TaskDraft taxonomy / TaskWriteResult shape に合わせて統合した
- POTASK-004 承認済み artifacts から `backend-routing.md` と `test_backend_routing.py` を個別に取り込み、GitHub Projects は first backend だが permanent architecture ではないことを明記した
- `SKILL.md` から `task-contracts.md`、`backend-routing.md`、`github-mcp-projects.md`、`hermes-mcp-governance.md` へ到達できるようにし、raw ID/auth leakage guard は normalized key だけでなく value marker も検査するようにした
- 通常検証は固定 fixture / local validator のみを対象とし、live GitHub / Hermes / MCP / credential / browser / network 操作は行っていない

## [2026-06-29] review-fix | POTASK-009 TaskRef shape integration

- GitHub MCP route の `TaskWriteResult.task_ref` を POTASK-002 の backend-neutral `TaskRef` shape に統一し、`backend_key`、`task_ref`、`task_url`、`title` の 4 field を canonical とした
- `github-mcp-projects.md`、`github_mcp_route/adapter-results.json`、`test_github_mcp_route.py` を更新し、route fixture が同じ top-level `TaskRef` keys を assert するようにした
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` は 35 tests OK、plugin validator、skill quick validate、`validate_skill_architecture.py --all`、`validate_skill_context.py --all`、`git diff --check 06f9b6fc7801271f345a8c2772a6d64e7c64f310..HEAD` は通過した

## [2026-06-29] review-fix | POTASK-009 coordinator knowledge state sync

- P009 branch の `portfolio-os-task-backend-plugin-skill-spec.md`、`portfolio-os-task-backend-plugin-skill-issues.md`、`knowledge/log.md` を coordinator worktree の current knowledge docs へ同期し、POTASK-001 から POTASK-008 の `PR_READY` progress entries を保持した
- P009 固有の package layout 更新、`validate_skill_architecture.py --all` verification command、POTASK-009 integration log entries を再適用した
- ledger は POTASK-001 から POTASK-008 を `PR_READY`、POTASK-009 を最終統合 issue として `実行中` にしている

## [2026-06-29] delivery-prep | POTASK-009 local PR_READY state

- coordinator runtime / worker report / implementation review で POTASK-009 を `PR_READY` とし、scheduler は runnable / reviewable / fixable / waiting_human なしになった
- PR branch 側の spec / issue ledger を POTASK-001 から POTASK-009 まで local `PR_READY` として最終同期した
- PR delivery はユーザー承認済み。GitHub issue mirror、merge、live GitHub / Hermes / MCP / credential 操作はこの entry 時点ではまだ行っていない
## [2026-06-28] decision | Loop skill operational simplicity Spec Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/loop-skill-operational-simplicity-spec.md` を Spec Gate 承認済み契約として記録
- scope は loop 系 skill の適用基準、1 ページ mental model、workflow complexity advisory report の追加に限定する
- `knowledge/index.md` に synthesis entry を追加
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は未承認
- 次フェーズは local issue ledger 作成と Issue Gate

## [2026-06-28] decision | Loop skill operational simplicity Issue Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` を Issue Gate 承認済み local ledger として記録
- approved issue は LSOS-001 から LSOS-004 の 4 件。LSOS-001 を初期 runnable とし、LSOS-002 / LSOS-003 / LSOS-004 は blocker graph に従う
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-spec.md` の状態を Spec Gate / Issue Gate 承認済みに更新
- `knowledge/index.md` に local issue ledger entry を追加
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は未承認
- 次フェーズは normalized input packet 作成と Execution Plan Gate

## [2026-06-28] decision | Loop skill operational simplicity Execution Plan Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/loop-skill-operational-simplicity-input-packet.json` を承認済み normalized input packet として記録
- packet は LSOS-001 -> LSOS-002 / LSOS-003 -> LSOS-004 の blocker graph と write scope を持つ
- `validate_input_packet.py` と `check_capabilities.py --input` はどちらも `ok: true`
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-spec.md` と `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` の状態を Execution Plan Gate 承認済みに更新
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は未承認
- 次フェーズは approval record commit 後の `issue-implementation-loop prepare`

## [2026-06-28] prepare | Loop skill operational simplicity execution envelope

- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-execution-envelope.json` を追加
- Envelope は `remote_write_policy.mode=local_only`、`worker_context_required=true`、`coordinator_may_implement=false`、`serial_fallback_mode=worker_context_only`
- `epic_base.sha` は Execution Plan Gate approval commit `99f67f2ebe1d026d2b274905abdc61d033fc907f`
- LSOS-001 は `create_on_run`、LSOS-002 / LSOS-003 / LSOS-004 は dependency により `reserved`
- `validate_execution_envelope.py` は `EXECUTION ENVELOPE OK`
- `reconcile_git_state.py --json` は `ok: true`, collisions 0
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は未承認

## [2026-06-28] implementation | Loop skill operational simplicity LSOS-001 applicability

- LSOS-001 worker commit `e7cd6fb695c229ec71d3e84e6fea1999123c97a1` で、`grill-to-pr-loop` と `issue-implementation-loop` の entrypoint に Applicability section を追加
- review range `f61e10dd405d843c5b66ed99395b76e215962f0a..e7cd6fb695c229ec71d3e84e6fea1999123c97a1` は implementation review approved。Critical / Important / Minor finding はなし
- fresh verification は architecture validator、context validator、grill tests、issue-loop tests、`git diff --check` で OK
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に LSOS-001 evidence と blocker release を反映
- LSOS-002 と LSOS-003 を実行可能にした。LSOS-004 は LSOS-002 / LSOS-003 完了待ち
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-28] implementation | Loop skill operational simplicity LSOS-002 mental model

- LSOS-002 worker commits `bd70a8b3a0a8bf07f84ed09f6cb0580e731a19ce` と review-fix `5d48b3f2cffaa2102d9c3b8343fc8351020182a2` で、role-boundary mental model を追加
- `skills/issue-implementation-loop/references/mental-model.md` は coordinator / worker / reviewer / runtime state / local ledger / remote delivery の責務境界を 1 ページで説明する
- mental model は `issue-implementation-loop` と `grill-to-pr-loop` entrypoint から発見できるが、default operation read-set には含めていない
- 1 回目 implementation review は Important 1 件。final PR merge が approval-gated action と読める表現を、review-fix で `Final PR merge is always human-only` に修正
- 2 回目 review range `e798ec03d74280844e09607ebc9f8d97d3b57235..5d48b3f2cffaa2102d9c3b8343fc8351020182a2` は approved。Critical / Important / Minor finding はなし
- fresh verification は context validator、grill tests、issue-loop tests、`git diff --check` で OK
- LSOS-004 は LSOS-003 完了待ち。remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-28] implementation | Loop skill operational simplicity LSOS-003 workflow complexity

- LSOS-003 worker commits `cef44dd07c1102bbc174c63d9fa7653e070a4679` と review-fix `584b34c27fa14adff72c20e8f32c0218042f2be8` で、`scripts/report_skill_context.py --all --json` に top-level `workflow_complexity` を追加
- `workflow_complexity` は operation count、gate count、runtime artifact count、worker-context / review-cycle / human-wait / remote-delivery flags を advisory として返す
- text output は既存 context report の末尾に短い `Workflow complexity:` 行だけを追加し、non-loop `--skill skills/llm-wiki` では workflow advisory を出さない
- `scripts/validate_skill_context.py` は変更せず、read-set budget validator のまま維持
- 1 回目 implementation review は Important 1 件、Minor 1 件。non-loop skill target への誤 advisory と brittle count tests を review-fix で修正
- 2 回目 review range `59ca2a2c7598480191905e5170905d2338897901..584b34c27fa14adff72c20e8f32c0218042f2be8` は approved。Critical / Important / Minor finding はなし
- fresh verification は report JSON/text、non-loop `--skill` report、scripts tests、context validator、grill tests、issue-loop tests、`git diff --check` で OK
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に LSOS-003 evidence と blocker release を反映し、LSOS-004 を実行可能にした
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-28] implementation | Loop skill operational simplicity LSOS-004 regression ledger

- `scripts/test_loop_operational_simplicity_ledger.py` を追加し、`knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` の LSOS-004 final ledger、`knowledge/index.md`、`knowledge/log.md` の discoverability を regression として固定
- 既存 regression により、適用基準は `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` と `skills/issue-implementation-loop/tests/test_entrypoint.py`、mental model discoverability は同 entrypoint tests、workflow complexity JSON shape は `scripts/test_report_skill_context.py` で固定済み
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に LSOS-001 から LSOS-004 の implementation evidence、verification result、review result を集約
- `knowledge/index.md` の Loop Skill Operational Simplicity Issues entry を final ledger / implementation evidence / review result で検索できるように更新
- full verification は architecture validator、context validator、report JSON/text、grill tests、issue-loop tests、scripts tests、`git diff --check` で OK
- LSOS-004 review cycle 1 feedback を反映し、final ledger status と LSOS-002 blocker wording の stale 表現を修正
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-28] review-sync | Loop skill operational simplicity LSOS-004 final review approval

- LSOS-004 final implementation review が `8974dba422a12bcb250a2bb4f80a576dcf4d13b0..8ef5e98d6179bb4f2e28a6a059ebab7a49d3fb09` を approved とした
- Critical / Important / Minor finding はなし
- `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に LSOS-004 review result を同期
- remote policy は `local_only` のまま維持し、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-29] docs | Loop skill 運用単純化 docs 日本語化

- ユーザー指摘を受け、`knowledge/wiki/syntheses/loop-skill-operational-simplicity-spec.md` と `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` を日本語ベースの見出し・本文へ更新
- `skills/grill-to-pr-loop` と `skills/issue-implementation-loop` の生成規約を、仕様、PRD、Issue 台帳、human-facing report、packet の user-facing string は日本語ベースとする方針へ更新
- `knowledge/index.md` の LSOS 関連 entry を、仕様、Issue 台帳、Input Packet、Execution Envelope の日本語ベース表記へ更新
- schema field、CLI option、JSON key、path、commit hash、PR 番号などの機械可読 identifier は互換性のため英語のまま維持
- 2026-06-29 のユーザー承認により branch push と draft PR #22 作成は実施済みとして、仕様と Issue 台帳の remote 状態を同期
- 追加のリモート書き込み、PR の ready 化、merge は未承認。final PR merge は常に human-only

## [2026-06-29] review-fix | Loop skill packet language contract

- code review で、packet template だけでなく packet 生成契約にも日本語ベース方針が必要と確認
- `skills/grill-to-pr-loop/references/execution-handoff.md` と `skills/issue-implementation-loop/references/worker-contract.md` に、packet の user-facing string は日本語ベース、schema key / path / command / ID は維持する方針を追加
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` で packet 生成契約まで regression として固定
- LSOS Issue 台帳と `knowledge/index.md` の human-facing label を `最終台帳` / `全体検証` / `回帰テスト範囲` へ寄せた

## [2026-06-30] draft | Loop skill autonomous gates spec

- ユーザー方針を受け、`knowledge/wiki/syntheses/loop-skill-autonomous-gates-spec.md` を Spec Gate draft として追加した
- `Execution Plan Gate` と `Live Root Gate` / `Adapter Availability Gate` は人間レビュー gate ではなく、agent preflight + commit boundary / readiness gate として扱う方針にした
- 承認済み delivery policy に `final_pr_push_head` と `final_pr_create_draft` が含まれる場合、実装完了後の draft final PR 作成は追加承認なしに自動実行する設計にした
- final PR merge、ready-for-review 化、force push、deploy、credential、permission、billing、production、destructive action は自動化対象外として維持した

## [2026-06-30] decision | Loop skill autonomous gates Spec Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/loop-skill-autonomous-gates-spec.md` を Spec Gate 承認済み仕様として扱う
- 承認済み Epic ID は `loop-skill-autonomous-gates`
- 採用判断は、`Execution Plan Gate` と `Live Root Gate` / `Adapter Availability Gate` を human approval ではなく agent preflight + commit boundary / readiness gate にすること
- 実装完了後の draft final PR 作成は、`final_pr_push_head` と `final_pr_create_draft` が approved action に含まれる場合、追加承認なしに自動実行する方針とした
- 次フェーズは日本語 local-first issue ledger 作成と Issue Gate

## [2026-06-30] decision | Loop skill autonomous gates Issue Gate approved

- ユーザーの明示承認を受け、`knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md` を Issue Gate 承認済み local ledger として追加した
- LSAG-001 から LSAG-005 の粒度、blocker graph、依存順、`実行可能` / `ブロック中` status、acceptance criteria、write scope を承認済みとした
- blocker graph は LSAG-001 を初期実行可能、LSAG-002 / LSAG-003 / LSAG-004 を LSAG-001 完了待ち、LSAG-005 を LSAG-002 / LSAG-003 / LSAG-004 完了待ちとする
- `knowledge/wiki/syntheses/loop-skill-autonomous-gates-spec.md` の状態を Spec Gate / Issue Gate 承認済みに更新した
- 次フェーズは normalized input packet 作成と Execution Plan Gate。Execution Plan Gate は承認済み方針に従い、agent preflight + commit boundary として自動継続できる

## [2026-06-30] auto-continue | Loop skill autonomous gates Execution Plan Gate packet

- 承認済み方針に従い、追加の人間承認を求めず `knowledge/wiki/syntheses/loop-skill-autonomous-gates-input-packet.json` を Execution Plan Gate 用 normalized input packet として追加した
- packet は LSAG-001 -> LSAG-002 / LSAG-003 / LSAG-004 -> LSAG-005 の blocker graph、write scope、verification、`delivery_intent=batch_issue_prs` を持つ
- `delivery_intent=batch_issue_prs` は実装完了後の draft final PR 自動作成方針を表す。final PR merge、ready-for-review、force push、deploy、credential、permission、billing、production、destructive action は自動化対象外のまま維持する
- `validate_input_packet.py knowledge/wiki/syntheses/loop-skill-autonomous-gates-input-packet.json` は `INPUT PACKET OK`
- `check_capabilities.py --input knowledge/wiki/syntheses/loop-skill-autonomous-gates-input-packet.json --json` は `ok: true`
- `knowledge/wiki/syntheses/loop-skill-autonomous-gates-spec.md` と `knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md` の状態を Execution Plan Gate 自動通過済みに更新した

## [2026-06-30] prepare | Loop skill autonomous gates execution envelope

- 承認済み input packet から `knowledge/wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json` を追加した
- Envelope は `execution_policy.worker_context_required=true`、`coordinator_may_implement=false`、`serial_fallback_mode=worker_context_only`
- `epic_base.ref` は `codex/loop-skill-autonomous-gates/epic-base`、`epic_base.sha` は Execution Plan Gate packet commit `c3a68fdb357a747e1c1f429d0e95372c92d795be`
- `remote_write_policy.mode=batch_issue_prs` とし、approved actions は `final_pr_push_head` / `final_pr_create_draft`
- LSAG-001 は `create_on_run`、LSAG-002 / LSAG-003 / LSAG-004 / LSAG-005 は dependency により `reserved`
- `validate_execution_envelope.py knowledge/wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json` は `EXECUTION ENVELOPE OK`
- `codex/loop-skill-autonomous-gates/epic-base` branch を `c3a68fdb357a747e1c1f429d0e95372c92d795be` から作成した
- `reconcile_git_state.py knowledge/wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json --json` は `ok: true`, collisions 0
- `knowledge/wiki/syntheses/loop-skill-autonomous-gates-spec.md` と `knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md` の状態を Execution Envelope prepare 済みに更新した

## [2026-06-30] decision | Loop skill autonomous gates LSAG-005 integration base approved

- LSAG-002 / LSAG-003 / LSAG-004 の reviewed head が互いに sibling branch であり、LSAG-005 を LSAG-004 head から直接分岐すると LSAG-002 / LSAG-003 の変更が base に含まれないことを確認した
- ユーザー承認を受け、Execution Envelope を revision 2 に更新し、LSAG-006 `LSAG-002 / LSAG-003 / LSAG-004 integration base を作成する` を execution-only work item として追加した
- LSAG-006 は LSAG-004 head を base に LSAG-002 / LSAG-003 の reviewed head を統合し、LSAG-005 は LSAG-006 の integration head から分岐する
- この変更は base policy / dependency edge の修正であり、LSAG-002 / LSAG-003 / LSAG-004 の実装内容、Spec / Issue acceptance、remote policy は変更しない
- GitHub issue mirror、push、PR 作成、merge はまだ行っていない

## [2026-06-30] implementation | LSAG-002 Execution Plan Gate auto-continue contract

- `skills/grill-to-pr-loop/references/execution-handoff.md` に、承認済み Spec / Issue scope 内で `validate_input_packet.py` と `check_capabilities.py --input` が通る場合、追加の人間承認なしに自動継続できる契約を追加した
- 自動継続前の durable evidence として normalized packet validation、capability preflight evidence、approved write scope、dependency graph、remote policy summary を残す方針を固定した
- approved artifacts、normalized packet/evidence boundary、local ledger、`knowledge/log.md` を commit してから `issue-implementation-loop prepare` へ進む commit boundary を明記した
- scope change、dirty overlap、capability failure、worker context unavailable、remote policy mismatch は停止条件として維持した
- `skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py` に Execution Plan Gate auto-continue regression を追加し、`knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md` に LSAG-002 worker evidence を同期した

## [2026-06-30] implementation | Loop skill autonomous gates LSAG-003 readiness gates

- `plugins/task-management/skills/task-management/references/github-mcp-projects.md` で `Live Root Gate` / `Adapter Availability Gate` を readiness check として整理し、write approval ではないことを明記した
- readiness pass は承認済み operation が executable であることだけを意味し、未承認 remote write、別 destination、別 tool、別 side effect を許可しない境界を固定した
- root mismatch、auth missing、destination unresolved、unsafe delegation boundary を approval 待ちではなく setup blocker として扱う contract を追加した
- `plugins/task-management/skills/task-management/references/adapter-dispatch.md` で readiness pass と `Adapter Dispatch Review` approval boundary を分離した
- `plugins/task-management/skills/task-management/references/hermes-mcp-governance.md` で plugin install が Hermes profile 編集、MCP server 登録、credential 設定、tool enablement を副作用にしない境界を維持した
- `plugins/task-management/tests/test_github_mcp_route.py` と `plugins/task-management/tests/test_adapter_dispatch.py` に LSAG-003 regression を追加した
- Hermes profile 編集、MCP server 登録、credential 設定、GitHub Projects mutation、task backend write 自動承認、real runtime root 変更は実行していない
- 検証は `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests` が 41 tests OK、`rg -n "Adapter Availability Gate|readiness|approval|credential|delegation" plugins/task-management` が対象 contract を検出、`git diff --check` が OK

## [2026-06-30] implementation | Loop skill autonomous gates LSAG-004 final PR auto-create policy

- `skills/issue-implementation-loop` の Execution Envelope / remote delivery contract に `final_pr_push_head` と `final_pr_create_draft` を固定した
- `validate_execution_envelope.py` は `remote_write_policy.approved_actions` を enum / unique action として検証し、unknown action や force push 相当の action name を拒否する
- `validate_delivery_plan.py` は final PR 作成時に approved action、`epic_base.branch_state: active`、`head == epic_base.ref`、対象 issue の `pr_merged: true`、draft-only policy を検証する
- `assets/templates/execution-envelope.json` は final PR の `draft_default: true`、`assets/templates/delivery-plan.json` は `"draft": true` を示す
- draft final PR 作成後に local ledger、runtime state、completion report へ PR URL、draft state、validation evidence、residual risk を同期する契約を `remote-delivery.md` に追加した
- ready-for-review 化、final PR merge、force push、deploy、credential、permission、billing、production、destructive action、GitHub issue mirror は自動化対象外のまま維持した
- worker 検証として `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` は 110 tests OK
- GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push は実行していない

## [2026-06-30] implementation | Loop skill autonomous gates LSAG-005 regression ledger

- LSAG-005 は regression tests、wiki discoverability、最終台帳集約だけを実装 scope とした
- `scripts/test_loop_autonomous_gates_ledger.py` を追加し、gate taxonomy、Execution Plan Gate auto-continue、Live Root / Adapter Availability readiness semantics、final PR auto-create approved action の regression anchor と、final ledger / index / log discoverability を固定した
- `knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md` に LSAG-001 から LSAG-006 の implementation evidence、review result、verification result、delivery evidence を集約した
- `knowledge/index.md` から仕様、Issue 台帳、Execution Plan Gate input packet、最終台帳、delivery evidence を辿れるようにした
- delivery state は local-only evidence として、GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push を未実行に保った
- coordinator-owned runtime snapshot、event log、input packet、execution envelope、worker packet は編集していない
- full verification は architecture validator、context validator、report JSON、grill tests、issue-loop tests、task-management tests、scripts tests、`git diff --check` で OK。`report_skill_context.py --all --json` は既存 baseline 比の token growth warnings を出したが exit 0

## [2026-06-30] delivery | Loop skill autonomous gates draft final PR

- `codex/loop-skill-autonomous-gates/epic-base` に LSAG-001 から LSAG-006 と Execution Envelope revision 2 を統合した
- `knowledge/wiki/syntheses/loop-skill-autonomous-gates-execution-envelope.json` の `epic_base.branch_state` を `active` にし、delivery plan validation `ok: true` を確認した
- delivery plan は `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-autonomous-gates/decisions/final-pr-delivery-plan.json`
- `final_pr_push_head` と `final_pr_create_draft` の approved action に基づき、branch push と draft final PR 作成を実行した
- Draft final PR は https://github.com/omitsuhashi/skills/pull/26
- ready-for-review、final PR merge、force push、GitHub issue mirror、deploy、credential、permission、billing、production、destructive action は実行していない

## [2026-06-30] review-fix | Loop skill autonomous gates ready-for-review boundary

- Draft PR #26 の code review で、spec 文言が ready-for-review 化を approved action で許可し得る表現になっている点と、Execution Envelope validator が `final_pr.ready_for_review` などの未知 key を拒否しない点を Important として確認した
- `loop-skill-autonomous-gates-spec.md` を、ready-for-review は常に別の human action であり approved remote action では許可しない表現へ修正した
- Execution Envelope validator / schema / tests に、`final_pr.ready_for_review`、`force_push`、`production` などの high-risk final PR fields を拒否する regression を追加した
- 実 Execution Envelope artifact に `final_pr.draft_default: true` を追加し、draft-only intent を self-describing にした

## [2026-06-30] query | Loop skill context compaction spec

- `grill-to-pr-loop` 実行時の context 圧迫を明示的に扱う Spec Gate draft として `knowledge/wiki/syntheses/loop-skill-context-compaction-spec.md` を追加
- session context pressure `65%` を soft trigger、`75%` を hard stop 目安とし、handoff 前は pressure に関係なく圧縮または fresh coordinator を必須にする方針を定義
- 「忘れてはいけないこと」「忘れてもいいこと」「圧縮してはいけないこと」と phase 別 compaction matrix を spec に整理
- read-set budget と session context pressure を分離し、`validate_skill_context.py` は read-set budget validator のまま維持する方針を記録
- `knowledge/index.md` に spec を登録。Issue Gate、Execution Plan Gate、実装、remote write は未承認

## [2026-06-30] review-fix | Loop skill context compaction spec design feedback

- review feedback を受け、`context-compaction` operation は通常 read-set へ常時混ぜず、65% trigger 時だけ current operation の conditional overlay として読む方針を spec に反映
- hard stop policy / acceptance を `75%` 固定へ修正し、「75 以上」と読める条件を排除
- 現行 `skill-architecture.toml` parser の TOML subset に合わせ、mandatory handoff compaction は integer flag `1` を既定とし、boolean 採用時は parser / validator / regression 更新を要求する方針を追加
- keep/drop taxonomy に planning / gate、execution / runtime、shared approval / safety の責務境界を追加
- ユーザー判断により、`現在の前提` の branch / status 記述は変更していない

## [2026-06-30] design | Loop skill phase transition context GC

- ユーザー確認を受け、phase transition 自体を mandatory compaction point として扱う方針を `loop-skill-context-compaction-spec.md` に追加
- 次 phase は carry-forward capsule と canonical artifact path から再開し、前 phase の raw discussion、raw JSON、full command output、diff 全文、実装試行錯誤を前提にしない契約を明記
- carry-forward capsule は default 400 words / hard 600 words、inline JSON / code / diff は合計 80 lines 以下に制限する方針を追加
- host transcript の物理削除ではなく、skill-level の operational context discard として扱う制約を既知リスクに記録

## [2026-06-30] gate | Loop skill context compaction Spec Gate approval

- ユーザーが `loop-skill-context-compaction` の Spec Gate を承認
- `knowledge/wiki/syntheses/loop-skill-context-compaction-spec.md` の状態を Spec Gate 承認済みに更新
- `knowledge/index.md` の entry を Spec Gate 承認済み仕様として同期
- Issue Gate、Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認のまま維持

## [2026-06-30] query | Loop skill context compaction Issue Gate draft

- Spec Gate approval commit `fb731232a37092d8f49f5cd10bdbd7fe28717da9` を source として、`knowledge/wiki/syntheses/loop-skill-context-compaction-issues.md` を追加
- local issue ledger は LSCC-001 から LSCC-005 の 5 件、dependency order は LSCC-001 -> LSCC-002 / LSCC-003 -> LSCC-004 -> LSCC-005
- LSCC-001 は実行可能、LSCC-002 / LSCC-003 / LSCC-004 / LSCC-005 は blocker によりブロック中
- GitHub issue mirror、push、PR 作成、merge は未承認。remote policy は `local_only`

## [2026-06-30] gate | Loop skill context compaction Issue Gate approval

- ユーザーが `loop-skill-context-compaction` の Issue Gate を承認
- `knowledge/wiki/syntheses/loop-skill-context-compaction-issues.md` の状態を Issue Gate 承認済みに更新
- `knowledge/wiki/syntheses/loop-skill-context-compaction-spec.md` の状態を Spec Gate / Issue Gate 承認済みに同期
- LSCC-001 から LSCC-005 の `レビュー状態` を `承認済み` に更新
- `knowledge/index.md` の entry を Issue Gate 承認済み ledger として同期
- Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認のまま維持

## [2026-06-30] implementation | Loop skill context compaction LSCC-003 worker

- `issue-implementation-loop` に execution context compaction reference、entrypoint pointer、`context-compaction` overlay operation を追加
- Execution Envelope の `context_policy.session_compaction` を schema / template / validator で固定し、65% soft trigger、75% hard stop、carry-forward capsule 上限を検証対象にした
- worker packet の strict `context_policy` は維持し、`session_compaction` を unknown field として拒否する regression を追加
- Verification は issue-implementation-loop tests、source-revision Execution Envelope validation、worker packet validation、skill context validation、`git diff --check` が OK
- Packet 記載の relative Execution Envelope validation は、この worker worktree に対象 artifact が存在しないため `FileNotFoundError`。artifact は LSCC-005 write scope 側であり LSCC-003 では編集していない

## [2026-06-30] implementation | Loop skill context compaction LSCC-005 ledger packet verification

- `knowledge/wiki/syntheses/loop-skill-context-compaction-input-packet.json`、`loop-skill-context-compaction-execution-envelope.json`、`loop-skill-context-compaction-handoff-brief.md` を追加し、approved spec / issue ledger / write scope / `local_only` remote policy / session compaction policy を再読込可能にした
- `knowledge/wiki/syntheses/loop-skill-context-compaction-issues.md` に LSCC-001 から LSCC-004 の approved review ranges、worker report paths、review report paths、verification summary を同期した
- LSCC-005 は worker verification passed / coordinator implementation review pending として記録した
- Fresh verification は architecture/context validators、context report JSON、65% advisory JSON、75% hard-stop `--fail-on-warning` expected exit 2、grill tests、issue-loop tests、scripts tests、input packet validator、Execution Envelope validator、`git diff --check` が OK
- Remote policy は `local_only` のため、GitHub issue mirror、push、PR 作成、merge は実行していない

## [2026-06-30] review-fix | Loop skill context compaction CI baseline

- PR #25 の GitHub Actions `Skill Architecture` で、`report_skill_context.py --all --json --require-baseline --fail-on-warning` が context baseline drift を検出した
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json` を `report_skill_context.py --all --json --emit-baseline` で再生成し、意図的に追加した `context-compaction` operation と updated read-set metrics を baseline に同期した
- CI と同じ `--require-baseline --fail-on-warning` context report は warnings なしで通過

## [2026-06-30] review-fix | Loop skill autonomous gates main merge CI baseline

- `origin/main` を `codex/loop-skill-autonomous-gates/epic-base` に merge し、`knowledge/index.md` と `knowledge/log.md` の conflict は `loop-skill-context-compaction` と `loop-skill-autonomous-gates` の entry を両方保持して解消した
- main merge 後の CI 同等 `report_skill_context.py --all --json --require-baseline --fail-on-warning` は `grill-to-pr-loop` の `resume` / `completion-report` / `ambiguity-check` で context growth warning を検出した
- `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json` を current merged tree で再生成し、CI と同じ context report が warnings なしで通過することを確認した
- Post-merge verification は architecture validator、context validator、context report、grill tests、issue-loop tests、llm-wiki tests、task-management tests、scripts tests、input packet validator、Execution Envelope validator、`git diff --check` で OK

## [2026-07-01] query | Loop review governance spec

- Issue 実装レビューで Issue 意図適合と堅牢化候補を分離する方針を `knowledge/wiki/syntheses/loop-review-governance-spec.md` に保存
- `intent_gap` / `implementation_regression` / `hardening_candidate` / `safety_escalation` / `classification_needed` の finding taxonomy を定義
- `hardening_candidate` は Issue completion のために自動修正せず、final PR 前に人間判断 queue として提示する設計にした
- `knowledge/index.md` に Spec Gate draft として登録。Issue Gate、Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認

## [2026-07-01] review-fix | Loop review governance spec feedback

- review feedback を受け、classification / candidate registry が token 消費を増やしすぎないよう context / token budget 方針を追加した
- `superpowers:requesting-code-review` を Issue 実装レビューの第一候補として明記し、未利用時は approved equivalent / manual fallback を要求する方針にした
- finding 分類、candidate 登録、Issue completion、final PR 前 candidate 採否、current PR 取り込み、delivery preflight の判断点と判断主体を表で固定した
- `knowledge/index.md` の summary / 検索語を review governance、context budget、requesting-code-review に同期した

## [2026-07-01] gate | Loop review governance Spec Gate approval

- ユーザーが `loop-review-governance` の Spec Gate を承認
- `knowledge/wiki/syntheses/loop-review-governance-spec.md` の状態を Spec Gate 承認済みに更新
- `knowledge/index.md` の entry を Spec Gate 承認済み仕様として同期
- Issue Gate、Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認のまま維持

## [2026-07-01] query | Loop review governance Issue Gate draft

- Spec Gate approval commit `3a8069b9a0e80e13cda4b547974abba639ddb59e` を source として、`knowledge/wiki/syntheses/loop-review-governance-issues.md` を追加
- local issue ledger は LRG-001 から LRG-005 の 5 件、dependency order は LRG-001 -> LRG-002 -> LRG-003、LRG-001 + LRG-002 -> LRG-004、LRG-001 から LRG-004 -> LRG-005
- LRG-001 は実行可能、LRG-002 / LRG-003 / LRG-004 / LRG-005 は blocker によりブロック中
- `knowledge/index.md` に Issue Gate draft として登録。Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認

## [2026-07-01] gate | Loop review governance Issue Gate approval

- ユーザーが `loop-review-governance` の Issue Gate を承認
- `knowledge/wiki/syntheses/loop-review-governance-issues.md` の状態を Issue Gate 承認済みに更新
- `knowledge/wiki/syntheses/loop-review-governance-spec.md` の状態を Spec Gate / Issue Gate 承認済みに同期
- LRG-001 から LRG-005 の `レビュー状態` を `承認済み` に更新
- `knowledge/index.md` の entry を Issue Gate 承認済み ledger として同期
- Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認のまま維持

## [2026-07-01] query | Loop review governance input packet

- 承認済み spec / issue ledger から `knowledge/wiki/syntheses/loop-review-governance-input-packet.json` を追加
- delivery intent は `local_only` とし、GitHub issue mirror、push、PR 作成、merge は未承認のまま維持
- review governance policy は `superpowers:requesting-code-review` 第一候補、hardening candidate 自動修正禁止、final PR 前 decision 必須、bounded review packet / candidate summary として正規化した
- LRG-005 は複数 blocker head を直接 merge しないよう、dependency `base_effect` を `none` として regression / discoverability issue に留める
- `validate_input_packet.py` は `INPUT PACKET OK` / `{"ok": true, "errors": []}`、`check_capabilities.py --input ... --json` は `ok: true`

## [2026-07-01] gate | Loop review governance Execution Plan Gate approval

- ユーザーが `loop-review-governance` の Execution Plan Gate を承認
- `knowledge/wiki/syntheses/loop-review-governance-execution-envelope.json` を revision 1 として追加し、remote policy は `local_only` / approved remote actions なしに固定
- `knowledge/wiki/syntheses/loop-review-governance-handoff-brief.md` を追加し、planning transcript に依存しない `issue-implementation-loop` 開始 capsule を保存
- `validate_execution_envelope.py` は `EXECUTION ENVELOPE OK`、`reconcile_git_state.py ... --json` は `ok: true`
- 実装、GitHub issue mirror、push、PR 作成、ready-for-review、merge は未実行

## [2026-07-01] implementation | Loop review governance LRG-005 regression discoverability

- `scripts/test_loop_review_governance_ledger.py` を追加し、`intent_gap` / `hardening_candidate` 分離、auto-fix 禁止、final PR 前 decision queue、`requesting-code-review` fallback boundary、wiki artifact discoverability を docs regression として固定した
- `knowledge/index.md` から spec、issue ledger、input packet、execution envelope、handoff brief を辿れるようにした
- `knowledge/wiki/syntheses/loop-review-governance-issues.md` に LRG-001 から LRG-004 は PR_READY / review approved、LRG-005 は regression discoverability branch の evidence として同期した
- HC-LRG-002-001、HC-LRG-003-001、HC-LRG-003-002、HC-LRG-004-001 は pending_decision のまま残し、未判断 hardening candidate は実装していない
- `report_skill_context.py --all --json` は top-level `warnings: []`。`workflow_complexity.warnings` は worker context / review cycle / human wait / remote delivery の advisory として扱い、hard validator 化しない
- GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push、production / credential / permission / billing / destructive action は実施していない

## [2026-07-01] query | Loop review governance hardening decision file

- runtime registry の `hardening-candidates.json` に残る `pending_decision` 4 件を `knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md` に一覧化した
- 各 candidate について source issue、summary、延期 risk、想定 scope、coordinator 推奨、`人間判断` 欄、判断理由欄を追加した
- 当初は `pending_decision` が残る間は final PR 作成に進まないとしたが、後続レビューで draft PR 作成後の一括判断へ修正することになった
- 現時点の coordinator 推奨は 4 件とも `deferred_follow_up`

## [2026-07-01] review-fix | Loop review governance draft PR decision surface

- hardening candidate は JSON runtime registry だけでなく、人間が読める `knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md` と PR body に集約する方針へ修正した
- draft final PR 作成は `pending_decision` で止めず、統合 diff を見たうえで全 candidate を一括判断する流れに変更した
- `pending_decision` は draft PR 作成ではなく、ready-for-review、merge、risk acceptance、または candidate 取り込み実装の前に解消する gate として扱う
- `knowledge/wiki/syntheses/loop-review-governance-execution-envelope.json` を revision 2 に更新し、approved remote action は `final_pr_push_head` と `final_pr_create_draft` のみに限定した
- `knowledge/wiki/syntheses/loop-review-governance-final-delivery-plan.json` を追加し、draft final PR の head / base / issue scope を記録した
- delivery plan validation は temporary integrated runtime で `ok: true`。pending hardening candidate 4 件は `errors` ではなく `decision_gate_blockers` として出力された

## [2026-07-01] delivery | Loop review governance draft PR

- branch `codex/loop-review-governance/epic-base` を GitHub に push し、draft final PR [#27](https://github.com/omitsuhashi/skills/pull/27) を `main` 向けに作成した
- PR body に pending hardening candidate 4 件を一括判断表として掲載した
- GitHub issue mirror、ready-for-review、merge、force push、production / credential / permission / billing / destructive action は実行していない

## [2026-07-01] review-fix | Loop review governance hardening decision visibility

- user feedback を受け、`4 件` の保存場所と出典が人間に分かるよう `knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md` を更新した
- candidate ごとに runtime registry 上の保存位置、出典 review artifact、指している実装箇所を明記した
- `knowledge/wiki/syntheses/loop-review-governance-issues.md` の `Pending Hardening Decisions` から human-readable decision surface へ辿れるようにした
- `knowledge/index.md` の decision artifact summary / 検索語に保存場所、出典、registry path を追加した

## [2026-07-01] review-fix | Loop review governance hardening decision material

- user feedback を受け、`knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md` に判断材料サマリと候補別判断メモを追加した
- 各 candidate について、判断したい問い、現在この PR でできていること、今回取り込む効果、取り込むコスト / 影響、延期時の risk、今回入れる判断条件、coordinator 推奨理由を明記した
- `knowledge/wiki/syntheses/loop-review-governance-issues.md` から判断材料サマリへ辿れるようにした

## [2026-07-01] review-fix | Loop review governance future-only hardening scope

- PR review comment の「後続」を受け、既存 hardening candidate 4 件を `deferred_follow_up` として current PR から除外した
- future-only hardening を routine review から外し、Issue 意図適合、今回変更による regression、current PR delivery risk を中心に review scope を絞った
- `hardening_candidate` は人間が明示的に hardening review を依頼した場合、または current PR delivery risk に結び付く場合だけ registry に記録する方針へ更新した
- `review-gate.md`、runtime / delivery / handoff references、spec、issue ledger、decision artifact、regression tests を同期した

## [2026-07-01] review-fix | Loop review governance code review response

- `superpowers:requesting-code-review` の指摘を受け、active ledger 見出しを `Pending Hardening Decisions` から `Deferred Hardening Follow-ups` に変更した
- human-readable decision artifact の参照先も `Deferred Hardening Follow-ups` に同期し、既存 4 件が未判断ではなく `deferred_follow_up` であることを明確化した
- `review-gate.md` の Scope 冒頭に current PR delivery risk / safety escalation check を明記した

## [2026-07-02] review-fix | Loop review governance automatic review scope

- user feedback を受け、自動レビュー観点を Issue 意図適合、今回変更による regression、current PR delivery risk の 3 つに限定した
- `classification_needed` と `hardening_candidate` は自動探索せず、必要になった場合または人間が明示した場合だけ扱う方針へ更新した
- `review-gate.md`、execution handoff / envelope / runtime / human wait references、spec、input packet、issue ledger、handoff brief、decision artifact、regression tests を同期した

## [2026-07-03] implementation | Task-management Hermes native plugin manifest

- Hermes local docs / loader implementation を確認し、native plugin discovery は `plugin.yaml`、enable/load は `__init__.py` の `register(ctx)` を使うことを反映した
- `plugins/task-management/plugin.yaml` を追加し、current Hermes の valid kind に合わせて `kind: standalone` とした
- `plugins/task-management/__init__.py` を追加し、同梱 `task-management` skill を `ctx.register_skill` で登録するだけの entrypoint にした
- `plugins/task-management/README.md` に subdir install / enable 手順と、`.git` が残らない場合の `hermes plugins update` limitation / `install --force` 更新手順を明記した
- `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md` と task-management plugin tests を同期した

## [2026-07-05] implementation | Loop skill Codex phase branch policy

- `knowledge/wiki/syntheses/loop-skill-codex-optimization-spec.md` を追加し、Codex の planning / execution context、phase approval commit、fresh / compacted coordinator handoff、branch ownership を local-only 仕様として整理した
- `Execution Envelope` 新規 template を schema version `3` に上げ、`phase_branch_policy` を schema / validator / tests で固定した
- `grill-to-pr-loop` execution handoff と `issue-implementation-loop` execution envelope / worktree lifecycle references を、planning branch、`epic_base`、issue branch、integration work item の責務分離に同期した
- schema version `1` / `2` envelope は historical / resume artifact として互換維持する方針にした
- GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push、production / credential / permission / billing / destructive action は実行していない

## [2026-07-15] implementation | Task-management read capability

- companies側 NPLM-006 blockerを確認し、POTASK-010としてbackend-neutral read adapter、Hermes read-only tool registration、`task-management-read` export alignment、normalized `TaskSnapshot` behavioral testを追加した
- `plugins/task-management/task_management/read_adapter.py` は `TaskQuery` とopaque `destination_ref`をoperator-configured `mcp__<server>__task_query`へdispatchし、canonical `TaskSnapshotResult`だけを返す
- model inputによるadapter tool選択、write-capable tool名、provider raw ID / unknown backend metadata / credential-like valueの返却をfail closedにした
- `plugins/task-management/__init__.py` は`task_query`を`task-management-read` toolsetへ登録し、`plugin.yaml.exports.toolsets`とruntime registrationを一致させた
- current `plugin-creator` validatorは`.codex-plugin/plugin.json.exports`を拒否するため、Codex manifestは有効なschemaを維持し、Hermes capability exportのauthoritative sourceを`plugin.yaml`とした
- TDDでadapter module、Hermes registration、manifest export、input/output credential / nested raw ID rejection、invalid query type / adapter exception normalizationの欠落をRED確認し、plugin suite 60 testsをGREEN確認した
- live Hermes / MCP / GitHub / credential、marketplace、cachebuster、install、push、PR作成は実行していない

## [2026-07-15] lint | Task-management POTASK-010 wiki sync

- `knowledge/index.md`、POTASK-010を含むspec / issue ledger、implementation logの相互参照とcanonical配置を確認した
- draft canonicalize、redirect、tombstone、archive、external ingestは不要と判断した
- checkout内にrepo-root wiki validatorは存在しないため、`skills/llm-wiki/tests` 6件の通過と対象Markdownの手動確認をlint evidenceとした

## [2026-07-15] review-fix | Task-management read capability

- implementation review cycle 1で、canonical scalar内のprovider marker / common credential key、queryとsnapshotのbackend不一致、canonical taxonomy / ISO date、required `backend_metadata`のfail-closed不足を確認した
- forbidden-value detectionとnormalization validationを追加し、該当behavioral testsをREDからGREENへ進めた
- `.codex-plugin/plugin.json`だけを読むcompanies preflightと、`exports`を拒否するcurrent `plugin-creator` validatorのcontract mismatchはskills repo単独では解消せず、cross-repo follow-up blockerとして維持する
- implementation review cycle 2で再現したquoted JSON provider / credential marker bypassとunsafe URL schemeをfail closedにし、query側canonical taxonomy / ISO date validationとguard別subtestを追加した

## [2026-07-16] spec | Task-management pluggable provider adapter

- user approvalを受け、POTASK-011としてconsumerがbackend差を意識しない`task_query` contract、host-owned route、pluggable provider adapterを追加した
- read-only local JSON adapterをcredential-free Hermes end-to-end verification backend、GitHub Projects MCP adapterをproduction first backendとして定義した
- GitHub adapterはhost-provided `projects_list` response mappingに限定し、direct API / GraphQL / `gh` / credential clientを持たない境界とした
- public `task_query` / `TaskSnapshotResult`は維持し、model inputからadapter、tool、file path、GitHub destinationを選べないfail-closed方針を固定した
- PR #29の追加scopeとして実装し、GitHub issue mirror、mergeは行わない

## [2026-07-16] spec-review | Task-management initial local backend

- user reviewを受け、`gh` commandをfallbackを含めて使用禁止とした
- external backend接続はread-only MCP `task_query`または別provider pluginの`task_adapter__<provider>__task_query`に限定した
- 初期稼働defaultはhost-owned local JSONでよく、GitHub Projectsをimplicit default / initial requirementにしない方針へ修正した
- public `TaskQuery.backend_key`は省略可能とし、host-owned default routeで解決してconsumerからbackend差を隠す方針を追加した

## [2026-07-16] execution-plan | Task-management POTASK-011

- plugin best-practice reviewを受け、route loader、stable adapter interface、local bootstrap snapshot、external MCP / provider plugin adapter、typed degradation、Hermes end-to-end smokeをPOTASK-011の実装順序として固定した
- local JSONはmutable task management source of truthではなくread-only bootstrap snapshotとし、write backendはMCPまたはprovider pluginが所有する境界を採用した
- Codexは同梱workflow skill、Hermesはnative `task-management-read:task_query` runtime toolであることを明示し、実在しないMCP server exportをmanifestへ追加しない方針を固定した
- POTASK-011専用input packetとExecution Envelope v3を追加し、既存draft PR branchをepic base、専用branch/worktreeをworker所有として予約した
- `gh` commandは使用せず、承認済みremote actionは既存draft PR branchのpush更新だけに限定した

## [2026-07-16] implementation | Task-management POTASK-011 provider adapters

- versioned host-owned route loader、constructor-bound adapter contract、read-only local bootstrap snapshot、exact MCP / provider-plugin read tool adapterを実装した
- public `task_query`の`backend_key`を省略可能にし、Hermes登録をexternal env非依存へ変更した。legacy single-MCP-route envは互換維持した
- provider error taxonomy、contract mismatch、route/source failureをtyped errorにし、raw payload / credentialを返さない既存normalization guardへ接続した
- Codexはworkflow skill、Hermesはnative runtime toolである差をmanifest / READMEへ同期し、実在しないMCP server exportは追加しなかった
- installed Hermesの`PluginContext` / registry、temporary `HERMES_HOME`、local fixtureを使うend-to-end smokeを追加した
- local JSONはmutable source of truthではなくbootstrap read snapshotとし、write backendはMCP / provider plugin所有、direct API / GraphQL / `gh` fallbackなしの境界を同期した

## [2026-07-16] review-fix | Task-management POTASK-011 cycle 1

- route/local `Path.resolve`のsymlink loop / `OSError`を`invalid_read_route`または`task_source_unreadable`へ変換し、public facadeからraw exceptionを漏らさないregression testを追加した
- external responseを5 MiB / 100 itemsへ制限し、JSON string / dictの両方で検証した。public query `limit`はsnapshot normalization前に適用するよう修正した
- `kind=mcp|plugin`とfixed tool namespaceの一致を強制し、重複`public_ref`をfirst-matchせずambiguous routeとして拒否した
- initial implementation commitにあったPython 4 filesのEOF blank-line warningを修正した

## [2026-07-16] implementation-review | Task-management POTASK-011 cycle 2

- independent spec reviewとstandards reviewの両方で、cycle 1のCritical / Importantがすべて解消済みであることを確認した
- coordinator fresh verificationで83 tests、installed Hermes local-route smoke、plugin / skill validators、architecture / context validators、full-range `git diff --check`が成功した
- worker commitsを既存draft PR branchへ統合し、POTASK-011を`PR_READY`とした。external providerのlive auth / network smokeは承認済み仕様どおりoptionalのため未実施とした
- GitHub issue mirror、ready-for-review、merge、live installは実行していない

## [2026-07-16] delivery | Task-management POTASK-011 PR #29

- verified integration branch `codex/task-management-read-capability`を`origin`へpushし、GitHub PR #29のheadを更新した
- GitHub pluginを使ってPR title / bodyをPOTASK-011、plugin v0.3.0、83 tests、Hermes smoke、provider boundary、optional external live smokeへ同期した
- `gh` commandは使用していない。PRはopen、mergeableであり、delivery evidence追記前のimplementation head `a024573`をconnectorで確認した
- GitHub issue mirror、merge、live install、external provider auth / network smokeは実行していない

## [2026-07-16] documentation | Task-management routing diagrams

- consumer、Hermes public tool、facade、host-owned route、local / MCP / provider-plugin adapter、normalized resultの関係をMermaid routing図として追加した
- public callからbackend分岐、external dispatch、normalization、typed error returnまでをsequence diagramで明示した
- backend差し替え時もconsumer contractが不変であるstate transitionと、read pathから分離されたapproval-gated write boundaryを明示した

## [2026-07-17] spec | Decide In Order skill

- ユーザー提供原案を `knowledge/raw/sources/` へ不変 source として取り込み、source summary と承認済み設計を追加した
- `decide-in-order` を task-management から独立した state-free skill とし、判断プロセスは厳密、内部状態は疎、表示は適応的、永続化境界だけ型付きにする方針を固定した
- 初期実装では新規 plugin を作らず、既存 task-management plugin には思想を複製しない動作別 integration policy だけを追加する
- skill-creator の scaffold / validator / forward test と、plugin-creator の既存 plugin validator / update boundary を完成条件へ組み込んだ
- skill 本体、task-management integration policy、marketplace、cachebuster、live install、外部 write は未実施

## [2026-07-17] implementation-plan | Decide In Order skill

- 承認済み設計を4つのreviewable taskへ分解し、standalone skill、forward test、task-management integration、full verificationの順序を固定した
- skill-creatorのinit/generator/validator、plugin-creatorの既存plugin validator、Python contract tests、fresh-agent behavior evaluationを具体的なcommandと期待結果へ落とした
- 新規plugin、marketplace、cachebuster、live install、backend call、外部writeを計画scope外に維持した
- 実装は未着手であり、次のexecution選択を待つ

## [2026-07-17] implementation | Decide In Order skill

- `skills/decide-in-order/` を skill-creator scaffoldから実装し、判断順序、light/deep/review、疎なDecisionFrame、適応的表示、DecisionRecord候補を分離した
- standalone contract tests 6件、fresh-agent forward test 8 scenarios、skill validatorを通過した
- task-managementへ思想を複製せず、動作別decision-support policyとcontract tests 6件を追加した
- integration forward testは、機械的readの除外と判断感度の高いintakeの2 scenariosで最終`2/2 PASS`。no-data readの初回evaluatorは空結果を創作したが、実装無変更の新規evaluatorで再実行して通過し、raw responseをcommitせずevaluator varianceとして記録した
- task-management full suite 89件、skill/plugin validators、llm-wiki tests 6件、skill architecture、3 context contractsを検証した
- Task 3の独立review後、`4475668`でintegration testを強化し、review fixを含めて再検証した
- baselineに既存の`goals/**/*.json`はなく、ignored、untracked、trackedはいずれも0件だったため、追跡確認だけを目的とするgoal JSONは作成しなかった
- 新規plugin、marketplace、cachebuster、live install、backend call、外部writeは実施していない

## [2026-07-17] design | Codex / Hermes dual-host authoring contract

- `decide-in-order` は標準 `SKILL.md` 形式で互換だが live Hermes には未導入、`task-management` は dual-host 構造を持つが live version は repo より古いことを実ファイルと CLI で切り分けた
- 既存作成指示を誤りとはせず、Hermes 必須 target としては discovery / live verification の保証が不足していたと整理した
- repo root の薄い router、`skills/AGENTS.md`、`plugins/AGENTS.md`、共通 validator / CI、既存配布文書の補強を推奨設計として固定した
- `description.md` の新設、standalone skill の plugin 内複製、通常 CI からの live Hermes config 変更は行わない
- 会話上の設計承認後に written spec を作成し、実装前 review 待ちとした

## [2026-07-17] implementation-plan | Codex / Hermes dual-host authoring contract

- written spec 承認を受け、薄い repo / directory guidance、標準ライブラリ共通 validator、既存 `decide-in-order` / `task-management` の導入契約、CI / durable evidence の4 taskへ分解した
- 各 task は failing test、最小実装、targeted verification、scoped commitを持つTDD手順とした
- repository compatibility、distribution / discovery、live loadを分離し、通常CIと本計画からlive Hermes profile変更を除外した
- skill directory内へREADMEや`description.md`を追加せず、standalone companion skillをplugin内へ複製しない制約を維持した

## [2026-07-17] implementation | Codex / Hermes dual-host authoring contract

- landed scopeとして`.github/workflows/skill-architecture.yml`のPython 3.9 / 3.12 CIへguidance test、validator test、repository-wide validationを追加し、durable evidenceとして`knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md`と`knowledge/index.md`を更新した
- 最終local matrixはguidance 3件、validator 15件、llm-wiki 6件、decide-in-order 7件、task-management 89件、context contract 3件、repository / architecture validation、Hermes hermetic smoke、`git diff --check`がすべて成功した
- read-only live確認では`decide-in-order`は引き続き未表示、`task-management`はenabled user version `0.1.0`のままであり、repo version `0.3.0`との差をrepository failureではなくdistribution driftとして記録した
- live Hermes profile、config、credential、skill / plugin installationは変更していない。live install / refreshとexpected version smokeは明示承認を要する別follow-upとして残した

## [2026-07-17] review-fix | Codex / Hermes dual-host final review

- missing / misspelled `skills_root`・`plugins_root` を direct / CLI JSON の両経路で fail closed にし、Codex / Hermes version の独立した非空 string 検証と YAML block marker scalar 拒否を追加した
- bundled `SKILL.md` ごとの validated frontmatter name と exact `ctx.register_skill(<literal-name>, ...)` を照合し、複数 bundled skill の登録漏れと dynamic / wrong receiver を拒否した
- Python 3.9 / 3.12 CI matrix に standalone `decide-in-order`、focused task-management decision-support、Hermes registration / manifest test を追加し、focused manifest test の PyYAML dependency を除去した
- durable page は `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md` と `knowledge/log.md` を更新した。`knowledge/index.md` の既存 summary は正確なため変更していない
- RED は初回 validator 23 tests の 39 subtest failures、workflow contract 2 failures、self-review追加 scalar test の 3 failures、GREEN は validator 24件、workflow contract 2件、guidance 3件、llm-wiki 6件、decide-in-order 7件、task-management 89件、Hermes smoke 1 snapshot、creator validators、architecture / context、diff / Goal audit の成功で確認した

## [2026-07-17] review-fix | Hermes registration and strict manifest contract

- fake Hermes context の bundled skill registration を exactly 1件、name `task-management`、実 bundled `SKILL.md` への resolved path、非空で整合する description として検証し、同名・誤pathを見逃さない contract にした
- PyYAML 非依存を維持しつつ、task-management manifest 専用 parser が全 meaningful line、top-level scalar、`provides_tools`、`exports.toolsets` の indentation / state、duplicate、unexpected content、required field を fail closed で検証するようにした
- RED は Hermes manifest test 10件中6 failures と workflow contract 3件中1 failure、GREEN は Python 3.9.6 / 3.12 の両方で Hermes 10件、workflow 3件、full task-management 93件、validator 24件、decide-in-order 7件、llm-wiki 6件、architecture / context が成功した
- durable page は `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md` と `knowledge/log.md` を更新した。`knowledge/index.md` の既存 summary は正確なため変更していない

## [2026-07-17] review-fix | Exact Hermes manifest version type

- generic dual-host validator の `manifest_version` を `type(value) is int and value == 1` として検証し、Python equality では `1` と等しい YAML boolean `true` と float `1.0` を拒否した
- task-management 専用 strict parser も unquoted integer `1` だけを Python `int` として返し、native manifest contract で exact type / value を固定した
- RED は validator 25件中2 subtest failures と Hermes manifest 11件中3 failures、GREEN は Python 3.9.6 / 3.12 の両方で validator 25件、Hermes 11件、full task-management 94件、workflow 3件、decide-in-order 7件、llm-wiki 6件、architecture / context、repository `--all` が成功した
- durable page は `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md` と `knowledge/log.md` を更新した。`knowledge/index.md` の既存 summary は正確なため変更していない

## [2026-07-21] spec-candidate | Loop Skill Approved Spec Binding Contract

- ユーザーが選択した A 案を `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-spec.md` に書面化し、normalized input packet を machine-readable approval evidence と spec binding の唯一の正本にする設計を固定した
- planning 側が final spec digest を human へ提示して一度だけ seal し、execution 側が prepare、dispatch、fix redispatch、report intake、review、resume、completion、delivery で同じ binding を fail closed に再検証する ownership seam を定義した
- approval circularity、worktree projection、runtime/event/report identity、TOCTOU、explicit delivery/resume bypass を acceptance matrix と停止条件へ反映した
- legacy packet、envelope、worker packet、metadataなしresumeの executable compatibility は維持しない clean break とし、historical wiki evidence は保持する一方で current validator/resume surface から外す方針にした
- CTO / Companies 固有 schema、queue、dispatcher、result store は generic contract に含めず、Codex / Hermes 共通 CLI と repository validators を完成条件にした
- `knowledge/index.md` に summary と検索語を登録した。A案の会話上の方向承認は済んでいるが、written spec review、Issue Gate、implementation plan、実装は未着手

## [2026-07-21] spec-approval | Loop Skill Approved Spec Binding Contract

- actor expression: `session-user`
- approved at: `2026-07-21T17:55:36+09:00`
- exact spec path: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-spec.md`
- raw-byte SHA-256: `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`
- approval scope: `accepted_decisions=true`、`non_goals=true`、`acceptance_criteria=true`、`verification=true`、`remote_policy=true`、`stop_conditions=true`
- ユーザーの「承認」と実装依頼により Written Spec Gate を通過した。spec bytes は変更せず、この entry を bootstrap approval evidence とする
- Issue Gate、Execution Plan Gate、実装、remote write はこの entry だけでは完了扱いにしない。実装は `local_only` で進め、push、PR、merge、live install は別承認とする

## [2026-07-21] issue-gate | Loop Skill Approved Spec Binding Contract

- ユーザーの明示的な「承認」「skill 作成のベストプラクティスに則った実装」依頼を受け、承認済み spec の scope を変更せず ASBC-001 から ASBC-006 へ分解した
- dependency は core/input packet -> envelope/worker と runtime/auxiliary と docs -> state-changing guards -> bootstrap seal/full verification とし、first runnable issue を ASBC-001 に固定した
- production change 前の fresh-agent baseline で、保存 spec digest と current bytes が不一致でも validator / Required Immediate Guard が exit 0 / ok=true になる RED を確認した
- Issue Gate は承認済み。Execution Plan Gate、worker 実装、implementation review は未完了であり、remote policy は `local_only` のまま維持する

## [2026-07-21] execution-plan | Loop Skill Approved Spec Binding Contract

- ASBC-001 から ASBC-006 を、各 issue の RED -> minimal GREEN -> targeted verification -> scoped commit として実行する詳細計画を固定した
- bootstrap exception は ASBC-001 の core/Input Packet v2 実装だけに限定し、その commit で approved spec を v2 packet へ seal して以後の gate commit とする
- Envelope/worker、runtime/auxiliary/resume、routing/review/completion/delivery、skill contract、fresh-agent forward test/full verification の依存順序と exact command set を記録した
- scope は approved spec/issue ledger と同一、remote policy は `local_only`。worker 実装、review、push、PR、merge、live install はまだ実行していない

## [2026-07-21] implementation-closeout | Loop Skill Approved Spec Binding Contract

- ASBC-001〜ASBC-006 を dependency 順に TDD 実装し、全 issue を `LOCAL_COMPLETE` とした。implementation head は `b3bfa4b5a8cb1dd7788aa61398679ce6c5f995dd`、binding gate commit は `ad9adeab69bcafd761d8457e9c33d1b4c26096d5`
- current executable contract は Input Packet v2 / Execution Envelope v4 / Event・Runtime・Human Request・Hardening Registry・Report・Result・Delivery v2 / Worker・Reviewer Packet v3 / Resume metadata v3。historical Input Packet v1 と Envelope v1〜v3 JSON は non-executable evidence として bytes を変更せず保持した
- planning の exact identify/present/approve/seal と、prepare、dispatch、worker/reviewer start・report intake、resume/rebuild、review/completion、delivery の fresh fail-closed verificationをCodex/Hermes共通 skill contractへ同期した。invalid binding で許可するのは read-only diagnostic status だけとした
- ASB-01〜ASB-30 を public operation / real entrypoint hookへ一意に mappingし、issue-implementation-loop 230 tests、grill-to-pr-loop 24 tests、llm-wiki 6 tests、architecture/context/strict context report/dual-host/creator validators、Packet v2 / Envelope v4 validators、`git diff --check` が成功した。strict context warnings は空、repository-wide 最小 headroom は 21%、affected issue-loop 最小 headroom は 26%
- fresh-agent forward test 3件は planning one-byte drift、urgency下の execution mismatch、terminal後の stale delivery/resume をすべて停止し、read-only statusだけを許可した。scoped implementation reviewは全taskで完了し、open Critical / Important finding はない
- immutable raw-byte SHA-256 は spec `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`、sealed packet `3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7`、Envelope `ac7630bf404b1c3607eb504bc18377bc45aef2c3b128be04e38d6737ca351af4` のまま一致した
- residual risk は raw-byte contract の保守性、validation後mutationの理論的可能性、actor expressionが暗号学的本人性を証明しないこと、clean breakで旧runをresumeできないこと、live host installを検証していないこと。各state-changing boundaryのfresh verification、new approval/new run、separate live authorizationを維持する
- approved remote policy は `local_only`。push、GitHub Issue、PR、merge、live Codex/Hermes install/runtime changeは意図的に実行せず、別の明示承認が必要な境界として残した

## [2026-07-22] implementation-recloseout | Loop Skill Approved Spec Binding Contract

- 2026-07-21 の `implementation-closeout` entry と commit `6f0158c66710ee0dcce1f868d0fbe6c85bc72602` は当時の証跡として保持するが、その completion claim は後続whole-branch reviewで再オープンされた。本entryが最終状態をcorrectiveにsupersedeする
- whole-branch review `cab8bd88351727f3495b657df447f7f64aa881d1..6f0158c66710ee0dcce1f868d0fbe6c85bc72602` は2 Critical / 6 Importantを検出した。Envelopeのsealed intent非対応、Worker/Reviewer caller semantics、closed/strict validation、runtime/resume fresh verification、remote-delivery signature、9番目のcontext operation、status exception、exact Epic-base blobsがblockerだった
- `f8f69bb3b9396ee5daa49f0fb710a28e1086ee94` (`fix: bind approved intent end to end`) で上記を修正した後、hardening review `6f0158c66710ee0dcce1f868d0fbe6c85bc72602..f8f69bb3b9396ee5daa49f0fb710a28e1086ee94` が2 Critical / 1 Important / 1 Minorを検出した。dependency edge semantics、worker trust roots/active runtime、exact boolean types、schema-required fieldsが残blockerだった
- `7e9515a7e74f632c3202ae2ab81dd65e7102b4ac` (`fix: verify worker trust boundaries`) でcanonical dependency edges、trusted repo/assigned worktree/active Envelope・Runtime boundary、exact primitive types、closed Worker Packet fieldsを修正した。final focused closure `f8f69bb3b9396ee5daa49f0fb710a28e1086ee94..7e9515a7e74f632c3202ae2ab81dd65e7102b4ac` はCritical / Important / Minorすべて0
- final local verificationはissue-implementation-loop 244 tests、grill-to-pr-loop 25 tests、llm-wiki 6 tests、architecture/context/strict context/dual-host/両creator validators、current Envelope validator、`git diff --check`が成功した。strict contextは`warnings=[]`、issue-loop operation countはapproved contractどおり8
- immutable raw-byte SHA-256はspec `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`、sealed Input Packet `3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7`のまま。corrected Envelope v4は`c15a7e9f4dc18acf8899f8e660f8f6eff8753f39b9f72a5772e44daf22d89497`
- 全ASBC issueは最終的に`LOCAL_COMPLETE`、remote policyは`local_only`。push、GitHub Issue、PR、merge、live Codex/Hermes install/runtime changeは実行していない

## [2026-07-22] final-verification | Loop Skill Approved Spec Binding Contract

- commit `18a7fc4e8439421b28499f9105bf7653888b22de` (`fix: close binding metadata parity`) で Worker Packet の Envelope / Runtime / binding metadata exact parityと、strict context baselineのoperation-count self-consistencyを固定した
- final focused review `7e9515a7e74f632c3202ae2ab81dd65e7102b4ac..18a7fc4e8439421b28499f9105bf7653888b22de` は Approved。Critical / Important / Minorすべて0で、open findingはない
- final local verificationはissue-implementation-loop 245 tests、grill-to-pr-loop 25 tests、llm-wiki 6 tests、scripts 59 testsが成功した。strict contextはcurrent / baseline operation count `8 == 8`、`warnings=[]`
- immutable raw-byte SHA-256はspec `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`、sealed Input Packet `3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7`、corrected Envelope v4 `c15a7e9f4dc18acf8899f8e660f8f6eff8753f39b9f72a5772e44daf22d89497`のまま変更していない
- 全ASBC issueは`LOCAL_COMPLETE`、remote policyは`local_only`。push、GitHub Issue、PR、merge、live Codex/Hermes install/runtime changeは実行していない

## [2026-07-22] spec-candidate | Approved Spec Binding Artifact Lifecycle

- user feedbackを受け、同一Epicのdurable spec/ledger/plan/packetを`knowledge/wiki/syntheses/<epic-id>/`へ集約し、Envelope以後のinstantiated execution JSON/JSONLをGit common runtime rootへ分離するconsolidated revision candidateを作成した
- current skillだけを使うfresh read-only baseline 3件では、planning artifactsは`syntheses/`直下へflat配置され、execution artifactsはGit common runtime rootへ非追跡配置された。planning layoutとruntime contractの不一致をproduction change前に再現した
- Input Packet v2はexact approval/execution-intent lockかつgate commit blobなのでtrackedのまま維持し、Execution Envelope、runtime/events、worker/reviewer packets/reports、decisions、recovery、deliveryはGit非追跡とする。schema/template/test fixture JSONはproduct contractとしてtrackedを維持する
- consolidated spec、follow-up ledger、initial plan archive、TDD implementation planを`knowledge/wiki/syntheses/approved-spec-binding-contract/`へ配置した。ASBC-007〜ASBC-009はexact spec path/raw-byte digestのWritten Spec Gate待ちで、production skill/code、sealed packet、remote PR stateは未変更
- Written Spec Gate提示値はpath `knowledge/wiki/syntheses/approved-spec-binding-contract/spec.md`、raw-byte SHA-256 `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`。approval subjectは`spec_binding`、scopeはaccepted decisions / non-goals / acceptance criteria / verification / remote policy / stop conditionsの6項目で、decisionは未承認

## [2026-07-22] spec-approval | Approved Spec Binding Artifact Lifecycle

- actor expression: `session-user`
- approved at: `2026-07-22T07:36:04+09:00`
- exact spec path: `knowledge/wiki/syntheses/approved-spec-binding-contract/spec.md`
- raw-byte SHA-256: `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`
- approval subject: `spec_binding`
- decision: `approved`
- approval scope: `accepted_decisions=true`、`non_goals=true`、`acceptance_criteria=true`、`verification=true`、`remote_policy=true`、`stop_conditions=true`
- ユーザーの「承認」により exact Written Spec Gate を通過した。承認後の `spec.md` bytes は変更せず、ASBC-007をfirst runnable issueとする
- remote scopeはbranch `codex/approved-spec-binding-contract`へのpushと既存Draft PR #32の更新のみ。PR ready化、merge、release、live installは非承認

## [2026-07-22] canonicalize-rehome | Approved Spec Binding Artifact Lifecycle

- Written Spec Gateのexact path/raw-byte SHA-256、`session-user`、`approved`、`spec_binding`、six-part scopeをpublic `identify`で再確認し、ASBC-007のreviewed implementation commit `ce70e6c`をmigration前提として固定した
- current durable spec、ledger、initial implementation plan、follow-up implementation plan、sealed Input Packet v2を`knowledge/wiki/syntheses/approved-spec-binding-contract/`へ集約し、current index linksをnested rootへ切り替えた
- Input Packet v2をapproved spec SHA-256 `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`へresealした。packet SHA-256は`e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`、public packet validatorとbinding verifyはいずれも成功した
- superseded flat current spec、issues、implementation plan、Input Packet、Execution Envelopeの5 filesだけをcurrent treeから削除した。historical artifactは追加削除せず、current instantiated EnvelopeはGit indexから除外した
- 本entryを含むartifact lifecycle gate commitのfull SHAは、commit作成後のappend-only follow-up entryに記録する。specとsealed packet bytesは以後変更しない

## [2026-07-22] artifact-lifecycle-gate | Approved Spec Binding Artifact Lifecycle

- gate commit: `bc1f32dd7a4ac01dd8651744ae7929402dfa9356` (`docs: group approved spec binding artifacts`)
- gate commit内のspec raw-byte SHA-256は`2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed Input Packet raw-byte SHA-256は`e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`
- `knowledge/wiki/syntheses/approved-spec-binding-contract/input-packet.json`はtracked、superseded current instantiated Envelope pathはGit indexに存在しない。spec/packet bytesはgate commit後に変更していない

## [2026-07-22] local-pr-ready | Approved Spec Binding Artifact Lifecycle

- ASBC-007 review range `10c0d0cffc5960c1a841b7fdacb0cd7a7b592e32..ce70e6cf8ddacc07948c72320443f306c32585b2`とASBC-008 review range `ce70e6cf8ddacc07948c72320443f306c32585b2..a15e7dc04a7c830ac09773268a820479ff25cea2`はApproved、open findingなし。ASBC-007/ASBC-008を`COMPLETE`、ASBC-009をlocal `PR_READY`とした
- current loop skill entrypointだけを読むfresh read-only evaluator 3件は、hypothetical Epicごとに`knowledge/wiki/syntheses/<epic-id>/{spec.md,issues.md,implementation-plan.md,input-packet.json}`をtracked durable tree、`$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/`配下のExecution Envelope/runtime artifactsをuntrackedと判断した。3/3 pass、raw transcriptはcommitしていない
- final local verificationはissue-implementation-loop 247 tests、grill-to-pr-loop 26 tests、llm-wiki 6 tests、scripts 59 tests、skill architecture/context、strict context report、dual-host、両skill-creator validator、`git diff --check`が成功した。strict contextはissue-loop operation count `8 == 8`、top-level `warnings=[]`
- initial briefの`report_skill_context.py --all --json --strict`はcurrent CLIに`--strict`がなくexit 2だった。CLI `--help`、CI workflow、strict report testsが定義するcanonical equivalent `--require-baseline --fail-on-warning`へimplementation planを訂正し、同commandのexit 0 / top-level `warnings=[]`を確認した。CLI/specは変更していない
- `origin/main...HEAD` local risk reviewはspec/implementation alignment、host-specific tracked paths、stale flat current links、accidental historical migration、schema/version drift、remote-scope expansionを確認し、Critical / Important finding 0。historical initial planのflat pathとtest-only legacy drift fixture shimはcurrent runtime guidanceではない
- immutable raw-byte SHA-256はspec `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed packet `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`。両bytesはgate commit後も不変
- mandatory controller task review / broad whole-branch review、branch push、Draft PR #32 summary/check更新はnonblocking pending delivery。push/PR mutationは本taskで実行せず、PR ready化、merge、release、live installは引き続き非承認

## [2026-07-22] final-review-corrective-wave | Approved Spec Binding Artifact Lifecycle

- whole-branch final review range `cab8bd88351727f3495b657df447f7f64aa881d1..e2db6bfc6e9690f0b3e4bac9e791853ca04b6431`のCritical 1、Important 3、Minor 1をlocalでcloseした。actual Git common directoryを基準にしたlinked-worktree runtime trust root、descriptor-relative/no-follow load、post-install spec revalidationとrollback、nested tracked templates、ASB-34〜ASB-36のbehavior mappingを実装した
- test-only hard-link compatibility shimとflat fixture aliasesを削除した。以前のresidual risk記録は本entryでsupersedeされ、current fixtureはexplicit nested durable pathsを使用する
- fresh local verificationはissue-implementation-loop 249 tests、grill-to-pr-loop 28 tests、llm-wiki 6 tests、scripts 59 testsと全repository validatorが成功し、strict context reportは`warnings=[]`、minimum headroom 20%以上だった。spec/packet SHA-256は`2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193` / `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`のまま不変
- ASBC-007/ASBC-008は`COMPLETE`、ASBC-009はlocal `PR_READY`を維持する。mandatory controller whole-branch re-review/final review後のpushとDraft PR #32更新がpendingであり、本waveではremote/live actionを行っていない

## [2026-07-22] asb-34-repository-wide-envelope-guard | Approved Spec Binding Artifact Lifecycle

- follow-up re-reviewのImportant 1を受け、ASB-34をcurrent nested Epic rootのbasename checkから`knowledge/wiki/syntheses`全域のGit-index JSON scanへ拡張した。former flat pathを含む任意layoutのtracked `schema_version == 4` instantiated Execution Envelopeを拒否する
- TDD fixtureはflat v4、historical v3、malformed syntheses JSON、skill-assets v4 templateを同時にtrackし、RED 1 errorからGREEN 2 focused testsへ進めた。historical v1〜v3 evidenceとtracked product templateは保持し、public ASB-34 mappingはcurrent ownershipとdeterministic flat-v4 detectionの2 behaviorを解決する
- local suitesはissue-implementation-loop 249 tests、grill-to-pr-loop 29 tests、llm-wiki 6 tests、scripts 59 testsが成功した。spec/Input Packet bytesとschema versionsは不変
- ASBC-009はlocal `PR_READY`、mandatory controller whole-branch re-review/final reviewはpendingを維持する。push、Draft PR #32 mutation、ready、merge、release、live installは実行していない

## [2026-07-22] remote-delivery | Approved Spec Binding Artifact Lifecycle

- whole-branch final review `cab8bd88351727f3495b657df447f7f64aa881d1..c844a3085a53878352f42b8d87eaa6d8e888a49b` はCritical / Important / Minorすべて0、既存Draft PR #32へのpublish Approvedとなった
- branch `codex/approved-spec-binding-contract`をhead `c844a3085a53878352f42b8d87eaa6d8e888a49b`へpushし、[Draft PR #32](https://github.com/omitsuhashi/skills/pull/32)のtitle/body/check summaryをper-Epic durable root、untracked Git-common runtime root、tracked Input Packet exception、final validation evidenceへ更新した
- PR #32はOPEN / Draftを維持し、Skill Architecture Python 3.9 / 3.12の4 jobsはすべてPASSした
- final controller verificationはissue-implementation-loop 249 tests、grill-to-pr-loop 29 tests、llm-wiki 6 tests、scripts 59 tests、全repository validator、strict `warnings=[]`、packet `ok=true`、binding `valid=true`、`git diff --check`に成功した
- immutable raw-byte SHA-256はspec `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed Input Packet `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`のまま不変
- ASBC-007〜ASBC-009を`COMPLETE`とする。PR ready化、merge、release、live Codex/Hermes installは非承認かつ未実行

## [2026-07-23] spec-candidate | GitHub Projects Direct Task Management Skill

- userとのone-decision-at-a-time設計で、1個のcaller-selected GitHub Project、Issue-backed task、repository-as-work-unit、Status / Priority / Due date、Issue template、high-confidence safe auto-execution、caller-owned target configを確定した
- `plugins/task-management/` のbackend-neutral facade / adapter / host-specific registrationを廃止し、`skills/task-management/`のstandalone skillからGitHub MCPへ直接接続するcandidate specを`knowledge/wiki/syntheses/direct-github-projects-task-management/spec.md`に作成した
- skill内へ特定owner / Project / repository / agent hostを埋め込まず、caller-supplied `project_url`とoptional `inbox_repository`を解決する。`work_unit_id` custom field、CLI / API fallback、Project draft item、通常操作中のschema作成は採用しない
- current stateはexact path / raw-byte SHA-256のWritten Spec Gate待ち。Issue分解、implementation plan、production skill/plugin変更、live GitHub write、push、PR、installは未実施
- unrelated untracked `skills/llm-wiki/DESCRIPTION.md`は変更していない

## [2026-07-23] spec-approval | GitHub Projects Direct Task Management Skill

- actor expression: `session-user`
- approved at: `2026-07-23T08:10:21+09:00`
- exact spec path: `knowledge/wiki/syntheses/direct-github-projects-task-management/spec.md`
- raw-byte SHA-256: `9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94`
- approval subject: `spec_binding`
- decision: `approved`
- approval scope: `accepted_decisions=true`、`non_goals=true`、`acceptance_criteria=true`、`verification=true`、`remote_policy=true`、`stop_conditions=true`
- userの「Written Spec Gateを承認」によりexact revisionを承認した。承認後の`spec.md` bytesは変更せず、Issue分解を次のgateとする
- remote policyは`local_only`。push、GitHub Issue / Project mutation、PR、merge、release、live installは非承認

## [2026-07-23] issue-candidate | GitHub Projects Direct Task Management Skill

- approved spec `knowledge/wiki/syntheses/direct-github-projects-task-management/spec.md`をbinding sourceとし、DGPTM-001〜DGPTM-004のlocal Issue ledgerを`knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`に作成した
- dependency orderはstandalone contract、direct GitHub MCP workflow、旧plugin / CI migration、historical supersession / integration verificationの直列4段階とした
- 全Issueは`未承認 / ブロック中`であり、Issue Gate承認前にimplementation plan、Input Packet seal、production change、GitHub mirrorを開始しない
- remote policyは`local_only`。unrelated untracked `skills/llm-wiki/DESCRIPTION.md`は変更していない

## [2026-07-23] issue-approval | GitHub Projects Direct Task Management Skill

- actor expression: `session-user`
- approved at: `2026-07-23T08:16:12+09:00`
- approved ledger path: `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`
- pre-approval raw-byte SHA-256: `78c163ace72ec29f108fbf7e221454c1bed53c7556d4d5dceb731bb306fe3fc2`
- decision: `approved`
- approval scope: Issue ID、Outcome、blocker graph、dependency order、write scope、acceptance criteria、verification、non-goals
- userの「Issue Gateを承認」によりDGPTM-001〜DGPTM-004を承認した。status-only更新後、DGPTM-001をfirst runnable candidate、DGPTM-002〜DGPTM-004をdependency blockedとする
- Execution Plan Gateまではproduction implementationを開始せず、remote policyは`local_only`を維持する

## [2026-07-23] execution-plan-candidate | GitHub Projects Direct Task Management Skill

- `superpowers:writing-plans`を使い、DGPTM-001〜DGPTM-004のexact file responsibility、test-first step、RED/GREEN command、scoped commit、fresh evaluation、local closeoutを`knowledge/wiki/syntheses/direct-github-projects-task-management/implementation-plan.md`に作成した
- approved spec `9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94`と2026-07-23T08:10:21+09:00のsix-part approval evidenceを使い、Input Packet v2を`knowledge/wiki/syntheses/direct-github-projects-task-management/input-packet.json`へsealした
- sealed packet raw-byte SHA-256は`14b011499e4113ea2c496592228e5f2e7d37962592bec92073b8dd699f68266f`、delivery intentは`local_only`、Issue dependencyはDGPTM-001→002→003→004の直列とした
- current stateはExecution Plan Gate validation / capability preflight待ち。production implementation、live GitHub write、push、PR、installは未実施

## [2026-07-23] execution-plan-validation | GitHub Projects Direct Task Management Skill

- implementation plan raw-byte SHA-256は`a912f624a44102df663408c9a6334a0791cbe6f41dd6fa98d6378398502dbac5`、sealed Input Packet raw-byte SHA-256は`14b011499e4113ea2c496592228e5f2e7d37962592bec92073b8dd699f68266f`
- Input Packet validatorは`ok=true / errors=[]`、approved spec seal capabilityは`blocking=false / supported=true`、Git repository preflightとrequired review / TDD skill discoveryは成功した
- executionはDGPTM-001→002→003→004のserial worker-context job、`max_parallel=1`、`coordinator_may_implement=false`、review cycle上限2、remote policy`local_only`とした
- writing-plans self-reviewでspec coverage、placeholder、test名 / field名 / dependency整合を確認し、open gapはない。実行方式のuser選択とExecution Plan Gate commitまではproduction implementationを開始しない

## [2026-07-23] execution-plan-approval | GitHub Projects Direct Task Management Skill

- actor expression: `session-user`
- approved at: `2026-07-23T08:28:19+09:00`
- exact plan path: `knowledge/wiki/syntheses/direct-github-projects-task-management/implementation-plan.md`
- plan raw-byte SHA-256: `a912f624a44102df663408c9a6334a0791cbe6f41dd6fa98d6378398502dbac5`
- exact packet path: `knowledge/wiki/syntheses/direct-github-projects-task-management/input-packet.json`
- packet raw-byte SHA-256: `14b011499e4113ea2c496592228e5f2e7d37962592bec92073b8dd699f68266f`
- decision: `approved`
- approval scope: DGPTM-001→DGPTM-004のdependency chain、各Issueのwrite scope、serial worker context、task単位review、review cycle上限2、remote policy `local_only`
- userの「はい」によりExecution Plan GateとSubagent-Driven executionを承認した。production implementationはgate commit後に開始し、live GitHub write、push、PR、install、release、mergeは引き続き非承認とする

## [2026-07-23] implementation-closeout | GitHub Projects Direct Task Management Skill

- DGPTM-001〜DGPTM-003のreviewed local commitsは`6e48aadf117d7d433460f07bc4f98a68546f108d`（clean）、`edb600fb3578319f17b5e2f931b847882397559a`（1 fix cycle後clean、focused tests 8件）、`91a4dcdf39ea37a874d728d9c2059fb184f3581d`（clean、旧plugin 47 files削除 / CI migration）である。DGPTM-004は本local closeout commitであり、commit SHAとexternal task review resultは未来の値のため独立review後のfollow-up commitで追記する。
- stale active discovery REDでは旧Portfolio OS task backend source summary、plugin spec / ledger / Input Packet、provider-adapter plan、POTASK-011 Input Packet / Execution Envelopeが`knowledge/index.md`に残っていた。historical artifactのbytesを変更せずactive catalog entriesだけを除去し、`decide-in-order`はstandalone / state-freeかつtask storage非所有のcurrent skillとして再記述した。
- current `skills/task-management/SKILL.md`と直接参照Markdownだけを読むfresh read-only evaluator A/Bの8 scenarioをcontrollerが評価し、8/8 pass、named failureなしとした。target resolution、safe write、ambiguity / inferred terminal confirmation、explicit terminal no-double-confirm、repository-independent inbox、partial failure resume、no invented live result / non-MCP fallbackを確認した。raw transcriptはcommitしていない。
- local verificationはtask-management、decide-in-order、llm-wiki、scripts unittest、`validate_skill_architecture.py --all`、scoped `validate_dual_host_compatibility.py --skill skills/task-management`、skill-creator quick validator、旧plugin absence、static negative checks、`git diff --check`がすべてpassした。repository-wide compatibility validatorのunrelated `skills/llm-wiki/DESCRIPTION.md` findingは既存のまま変更していない。
- historical preservation auditはsource summary SHA-256 `5e5f87fdaf395813d3da7edfe54b49cabfe2c448c8ebe5661de8e2bdffc9bbd0`、plugin spec `9dc32a052e45bad2f3f2905837ebad8db56fce75c850ef6752a1d256e3fb923d`、ledger `c0db33d4c69f2177a7ea633dc60da6e7c6ad3281912f3a294b7d491124b5937d`、Input Packet `91b07cd047cc5dd7515dfde569c825cea751ff1f72a4b39ef40d8c7f47f1ee1d`、provider-adapter plan `9ed2090945938c4c5e7fc3e1239003006e4b5ea859950883c6f8d9ade33d7dd8`、POTASK-011 Input Packet `b7734592723b370d282f041301eec95d31608bf4e41431ca72b325d049216605`、Execution Envelope `85030ab103f99c50a3f5bb8afa1bafd759692b91989e93613d6fe59155eda02a`の不変を確認した。
- delivery stateは`local_only`。push、PR、GitHub Issue / Project mutation、live MCP、install、release、mergeは実行していない。remaining riskはDGPTM-004のindependent external task review pendingのみである。

## [2026-07-23] implementation-review-closeout | GitHub Projects Direct Task Management Skill

- DGPTM-001〜DGPTM-004のlocal implementationとtask reviewをcloseした。DGPTM-004 reviewed commitは`60314a31ec609f1ac702792a23e488f15a9645b3`（`docs: close direct GitHub task management migration`）であり、approved spec compliance / task qualityともにApproved、Critical・Important・Minor findingはすべて0件のclean verdictである。
- prior `implementation-closeout`のfresh read-only evaluator A/Bによる8 scenario 8/8 passと、task-management、decide-in-order、llm-wiki、scripts unittest、architecture / scoped dual-host / skill validator、negative checks、`git diff --check`のlocal verification passを本review evidenceへ継承する。historical artifact preservation auditも同entryのとおり維持する。
- 先行entryがcommit自身のSHAと独立reviewをfollow-upへdeferした記録は、reviewerが正確なinterim recordとして受理した。approved spec SHA-256 `9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94`とsealed Input Packet SHA-256 `14b011499e4113ea2c496592228e5f2e7d37962592bec92073b8dd699f68266f`は不変である。
- remote stateは引き続き`local_only`。push、PR、GitHub Issue / Project mutation、live MCP、install、release、mergeは実行していない。

## [2026-07-23] final-review-fix-pending-evaluation | GitHub Projects Direct Task Management Skill

- whole-branch final reviewが、先行task review後にCritical 1件（read-only requestがgeneric create flowへ入り得る）とImportant 3件（permissive static tests、standalone discovery route欠落、active knowledge / completion evidence不整合）を検出した。userはcurrent skill / tests、2つのcurrent synthesis、index、ledger、logへのwrite scope expansionを明示承認した。
- approved `implementation-plan.md`にもgeneric default flowとoperation-specific behavior test欠落があり、plan defectとして記録した。plan、approved `spec.md`、sealed `input-packet.json`は編集せず、historical artifact bytesも変更していない。
- TDDではtest-firstでexact allowed tree、plugin absence、Status / Priority exact parse、read / search / list zero mutation、edit / comment / non-terminal scope、reuse / partial-failure preservationを固定した。test helperのformat前提を訂正後、untouched `de0b995` production Markdownで10 tests中2 expected failuresを観測し、operation routingとpreservation contract実装後は10/10 GREENとなった。
- current `skills/task-management/`はread / search / listをzero-write、create / registerだけをnew-task flow、edit / comment / non-terminal updateをrequested propertiesだけ、terminal updateをexplicit no-double-confirm / inferred confirmationへrouteする。creation defaultsはnewly created Project itemだけに適用し、reuse / retryはexisting fieldとcompleted stepをresetしない。
- dual-host synthesisはcurrent surfaceをstandalone `skills/task-management/SKILL.md`とし、`~/.hermes/config.yaml`の`skills.external_dirs: [${SKILLS_REPO}/skills]`をrepository-level discovery routeに選んだ。external dirsはwrite protectionではないこと、filesystem permissionまたは別profile / toolsetが必要なこと、repository compatibilityのみverifiedでlive config / `hermes skills list`は未実施であることを記録した。
- decide-in-order synthesisはstandalone / state-free / task-storage非所有をcurrent境界とし、旧plugin integration、TaskDraft、adapter、validator、deleted pathをhistorical / supersededへ移した。indexはimplementation planをExecution Plan Gate承認済み・実行完了のhistorical planへ更新し、DGPTM-001〜004の満たしたacceptance criteriaをすべてcheckedにした。ledgerには旧source summary、plugin spec / ledger / packet、adapter plan、POTASK-011 packet / envelopeからcurrent standalone contractへのhistorical supersession mapを追加した。
- local verificationはtask-management 10、decide-in-order 7、llm-wiki 6、scripts 58 tests、skill architecture、scoped dual-host、skill quick validator、plugin absence、host-neutral negative search、`git diff --check`がすべてpass。spec / packet SHA-256は`9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94` / `14b011499e4113ea2c496592228e5f2e7d37962592bec92073b8dd699f68266f`のまま不変である。
- fresh evaluator A/Bの起動はplatformの`agent thread limit reached`でpending。過去outputやcontaminated agent contextは再利用せず、6/6 behavior評価前にはcommitしない。remote stateは`local_only`で、push、PR、GitHub mutation、live config、install、release、mergeを実行していない。

## [2026-07-23] evaluator-capacity-waiver-and-delivery-approval | GitHub Projects Direct Task Management Skill

- platformがcompleted agentを保持した状態でfresh evaluator spawnを3回試行したが、すべてevaluator作成前に`agent thread limit reached`となった。session userはこのplatform capacity blockerに対するfresh-evaluation waiverを明示承認した。これはbehavioral test failureではなく、過去evaluator outputやcontaminated agent contextは再利用していない。
- substitute acceptance gateはstrengthened task-management contract suite 10 tests、full repository verification、final independent reviewer re-reviewとする。fix implementerは前2条件の成功後にexact subjectでlocal commitを作成し、controllerがindependent re-reviewとfresh full verificationを完了してからpublication可否を判断する。
- session userはdelivery authorizationを従来の`local_only`から、completed feature branchのpushとdraft PR作成に限って拡張した。merge、release、live install、live GitHub Project / Issue mutation、その他のlive changeは非承認のままである。本implementerはpush / PR作成を行わずcontrollerへ引き渡す。

## [2026-07-23] final-re-review-capability-and-delivery-correction | GitHub Projects Direct Task Management Skill

- independent final re-reviewはImportant 2件を検出した。write routeがoperation別のselective capability checkへ狭まってapproved specのcomplete Issue / Project capability and permission preflightと矛盾した点、およびIssue ledgerのactive Gate policyが後続delivery authorizationを反映せず`local_only`だけをcurrent表示していた点である。
- TDDではfull write preflightとselective phrase禁止をtest-firstで追加し、current head `c45d45926a67d23fc49d198d19cdcb630701071a`に対して11 tests中2 expected failuresを確認した。`SKILL.md`と`references/github-projects.md`を揃えた後は11/11 GREENとなった。
- read / search / listはzero-writeのため必要なIssue / Project read capabilityだけを要求する。create / register、edit、comment、non-terminal update、terminal updateは、mutation前にIssue read / search / create / update / comment、Project read / item add / field update、resolved target permissionのcomplete setをすべて確認し、operation別にpreflightを狭めない。
- Gate policyはoriginal approved spec / sealed executionの`local_only`と、後続session-user authorizationによるfeature-branch push + draft PR作成だけのdelivery exceptionを区別した。merge、release、live install、live GitHub Issue / Project mutation、その他のlive changeは非承認のままである。本fix commitではpush / PR作成を行わない。

## [2026-07-23] lint | Historical POTASK artifact index repair

- GitHub Actions run `29970825450` のPython 3.9 / 3.12双方で、`grill-to-pr-loop`のhistorical artifact index invariantが失敗した。旧POTASK active catalog削除時に、保持対象のInput Packet v1 2件とExecution Envelope v3 1件まで`knowledge/index.md`から外したことが原因だった。
- `knowledge/index.md`へ3件だけをhistorical / non-executable evidenceとして再登録した。旧plugin spec、Issue ledger、provider-adapter planはactive catalogへ戻さず、current task-management contractはGitHub Projects直接接続型standalone skillのままとした。
- historical JSONのbytes、approved spec、sealed current Input Packetは変更していない。focused regression、grill-to-pr-loop 29 tests、issue-implementation-loop 249 tests、llm-wiki 6 tests、decide-in-order 7 tests、task-management 11 tests、architecture / context / dual-host checks、context report、`git diff --check`はすべてpassした。

## [2026-07-24] spec | Planning Worktree Gate

- Epic ID `planning-worktree-gate` として、Written Specを含む最初のrepository write前に`codex/<epic-id>/planning` branch/worktreeを作成または再利用し、Spec Gate、Issue Gate、Execution Plan Gate、index/log同期まで同じplanning worktreeを使う仕様を追加した。
- durable packetは`planning_branch` / `planning_base_sha`を持ち、host固有pathとdefault checkout開始snapshotはGit common directory配下のuntracked runtime artifact / Execution Envelopeに分離する。
- prepareはGate commit ancestry、PR_READY / deliveryはdefault checkout HEAD/status、final deliveryはplanning / implementation commitのactual final head reachabilityをfail closedで検証する。unrelated pre-existing dirtの移動、削除、stash、reset、PR混入は行わない。
- planning branchは`codex/planning-worktree-gate/planning`、base SHAは`b3b869b60dfb785b325f754292dccf675e47313b`。host固有worktree pathはtracked wikiへ記録せず、runtime artifactにのみ保持した。
- session userの依頼をSpec Gate approval evidenceとし、exact spec pathは`knowledge/wiki/syntheses/planning-worktree-gate/spec.md`、raw-byte SHA-256は`f4b8cebd19a832963aa5e4d022759b21ef73dc417ff6d2f1555b87419b578ec3`、six-part scopeは採用判断、非目標、受け入れ条件、検証、remote policy、停止条件をすべて承認済みとした。
- remote policyは`local_only`。push、PR、merge、GitHub mutationは非承認である。

## [2026-07-24] issue-gate | Planning Worktree Gate

- PWTG-001からPWTG-004へPlanning Worktree Gate CLI、packet/runtime repository guard、PR_READY / delivery integrity、wiki / full verificationをserial dependencyで分解した。
- user提示のAcceptance Tests 1〜8とNon-goalsをIssue Gate approval evidenceとし、各issueのwrite scope、criteria、non-goals、verificationを`knowledge/wiki/syntheses/planning-worktree-gate/issues.md`に固定した。
- local ledgerはcanonical、GitHub Issueは`未作成`、remote policyは`local_only`。Gateごとのworktreeは作成せず、Spec Gateと同じplanning worktreeを継続利用する。

## [2026-07-24] execution-plan | Planning Worktree Gate

- PWTG-001からPWTG-004のfile ownership、RED/GREEN command、interface、stop conditionを`knowledge/wiki/syntheses/planning-worktree-gate/implementation-plan.md`へ固定した。
- planning CLI、packet/runtime repository guard、PR_READY / final delivery integrity、wiki / full verificationをserial worker-context executionとし、`coordinator_may_implement=false`、remote policy `local_only`、final merge human-onlyを維持する。
- self-hosting bootstrap packetはPlanning Worktree Gate実装前の現行Input Packet v2 validatorでsealし、target implementation後の新規packet contractと区別する。既存sealed packetのbytesは変更しない。
- Spec Gate、Issue Gate、Execution Plan Gate、index/log同期は同じ`codex/planning-worktree-gate/planning` branchで行い、Gateごとのworktree再作成はしていない。
- exact packet pathは`knowledge/wiki/syntheses/planning-worktree-gate/input-packet.json`、raw-byte SHA-256は`7b7ecc562d1ff2aa2066438099741dad9e70ccb889c9dada4620eebb2224e219`。`validate_input_packet.py --json`と`check_capabilities.py --json`はいずれも`ok: true`で、approved spec seal、`tdd`、`requesting-code-review`、worker-context execution prerequisitesを確認した。
- Execution Plan Gateはapproved scope内、remote actionなし、dependency cycleなし、write scope明示済みとしてauto-continueする。packet / plan / index / logをphase approval commitに固定してからworker contextへ渡す。

## [2026-07-24] implementation-closeout | Planning Worktree Gate

- PWTG-001〜PWTG-004を完了へ同期した。pre-closeout chainはplanning base `b3b869b`、phase artifacts `6511899` / `e87a7e3` / `863711a`、PWTG-001の7 commits、PWTG-002の7 commits、PWTG-003 `c355b08`から成る19 commitsで、すべてpre-closeout production head `bc557bef95cabea39a2ac5220ce4ec09d59f980e`のancestorである。PWTG-004のcloseout documentationは`4d96bfd71b63c86727ad36b2d3d8fd0beb710a78`で完了し、post-commit独立reviewのstale status findingは後続のdocs-only review-fixで訂正した。
- fresh verificationは`grill-to-pr-loop` 58件、`issue-implementation-loop` 284件、repository scripts 58件、`llm-wiki` 6件、Acceptance 1〜8 focused regressions 18件がすべてpassした。skill architecture、3 context contracts、変更対象2 skillのscoped dual-host compatibility、両skillのskill-creator quick validator、`git diff --check`もpassした。
- approved specに残る`validate_dual_host_authoring.py`はhistorical plan defectであり、sealed specとInput Packetは編集していない。実行可能なIssue台帳 / Implementation Planは実在する`validate_dual_host_compatibility.py`のchanged-skill scoped commandsと、両skillのskill-creator quick-validator commandsへ訂正した。
- repository-wide `validate_dual_host_compatibility.py --all`は未変更の`llm-wiki` DESCRIPTION discovery findingだけを返した。変更対象2 skillのscoped validationはpassしたが、repository-wide passとは記録しない。
- Acceptance 1〜8はfirst-create、pre-existing exact worktree adoption/reuse、single planning chain、failure/default preservation、physical Gate ancestry、physical final-head containment、runtime-bound actual default checkout drift rejectionの実repo regressionsへ対応する。new packetはplanning identity pairをseal時に必須化し、historical sealed v2のread/verify compatibilityを維持した。
- approved spec SHA-256 `f4b8cebd19a832963aa5e4d022759b21ef73dc417ff6d2f1555b87419b578ec3`とsealed Input Packet SHA-256 `7b7ecc562d1ff2aa2066438099741dad9e70ccb889c9dada4620eebb2224e219`は不変である。default checkoutのHEADとexact porcelain statusはruntime start snapshotと一致した。
- prior production Important findingsはTDD fixと再reviewを経てすべてclosedし、最終fix reviewはCritical 0 / Important 0である。non-blocking MinorとしてGit environment policyのskill間重複、runtime load/validate stabilization sequenceの反復、planning/default identity parameter data clumpを残す。
- delivery stateは`local_only`。push、PR作成、merge、GitHub mutation、default checkoutのreset / clean / stash、destructive recoveryは実行していない。

## [2026-07-27] spec-candidate | Planning Authority Policy

- Epic ID `planning-authority-policy` として、planning integrationを`main_planning_context`、supporting agentを`advisory_only` / `read_only`、Spec Gate / Issue Gateのdecision authorityをHumanへ固定する仕様候補を追加した。
- model / reasoningはCodexの選択画面などhost runtimeが所有し、spec、Input Packet、Execution Envelope、Worker Packet、runtime stateへ永続化しない。supporting agent、execution coordinator、worker、reviewerのmodel routingはhostに委譲する。
- `skill-architecture.toml`のclosed family policy、architecture validator、`grill-to-pr-loop` entrypoint / planning contract、focused testsだけを変更対象とし、`issue-implementation-loop`のschema、scheduler、worker lifecycleは変更しない。
- planning branchは`codex/planning-authority-policy/planning`、planning baseは`f5d151e34de5089d75be68249e09da8a2d14f282`。remote policyは`local_only`であり、GitHub issue、push、PR、merge、release、live installは非承認である。
- exact spec path / raw-byte SHA-256を確認し、Human Spec Gate approvalを得るまでIssue分解とproduction implementationへ進まない。

## [2026-07-27] spec-gate-approval | Planning Authority Policy

- actor expression: `session-user`
- approved at: `2026-07-27T09:32:17+09:00`
- decision: `approved`
- Epic ID: `planning-authority-policy`
- exact spec path: `knowledge/wiki/syntheses/planning-authority-policy/spec.md`
- spec raw-byte SHA-256: `6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68`
- approval scope: `accepted_decisions`, `non_goals`, `acceptance_criteria`, `verification`, `remote_policy`, `stop_conditions`
- accepted decisions: planning integration ownerは`main_planning_context`、supporting agentは`advisory_only` / `read_only`、decision authorityはHuman、model selectionは`host_runtime`、具体的model / reasoning値のpersistenceは禁止する。
- non-goals: model router、Codex設定、agent file、execution schema、scheduler、`issue-implementation-loop` production implementationは変更しない。
- verification: architecture / loop / wiki tests、context validator、dual-host validator、skill validator、`git diff --check`を要求する。
- remote policy: `local_only`。GitHub issue、push、PR、merge、release、live installは非承認である。
- stop conditions: authorityを分離できない、具体的model値の保存が必要、execution側変更が必要、Human gateまたはworker-only契約が弱まる、context budget超過、planned scope競合、relevant validation失敗。

## [2026-07-27] issue-gate-candidate | Planning Authority Policy

- approved specをPAP-001からPAP-004のserial dependencyへ分解した。PAP-001はfamily policy / validator、PAP-002はmain planning / supporting agent運用契約、PAP-003はmodel非永続化 / execution non-regression、PAP-004はwiki / full verification closeoutを所有する。
- Issue Gate候補では`PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`をcycleなしのblocker graphとし、実行可能はPAP-001だけ、PAP-002〜004はblocker releaseまで`ブロック中`とした。
- productionのInput Packet、Execution Envelope、Worker Packet、`issue-implementation-loop` scheduler / runtime / worker lifecycleはwrite scope外とした。
- local Issue台帳をcanonicalとし、GitHub Issue / PRは`未作成`、remote policyは`local_only`を維持する。Human Issue Gate approval前にImplementation Plan / Input Packet作成やproduction implementationへ進まない。

## [2026-07-27] issue-gate-approval | Planning Authority Policy

- actor expression: `session-user`
- approved at: `2026-07-27T09:43:11+09:00`
- decision: `approved`
- approved dependency: `PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`
- approved scope: 各Issueのwrite scope、acceptance criteria、non-goals、verification。
- PAP-001だけを`実行可能`、PAP-002〜PAP-004をblocker releaseまで`ブロック中`とする。
- local Issue台帳はcanonical、GitHub Issue / PRは`未作成`、remote policyは`local_only`。push、PR、merge、release、live installは非承認である。
- Issue Gate commitを固定してからImplementation Plan、Input Packet、Execution Plan Gate evidenceを作成する。production implementationはExecution Plan Gate commit前に開始しない。

## [2026-07-27] execution-plan-gate | Planning Authority Policy

- decided at: `2026-07-27T09:50:50+09:00`
- decision: `auto-continue`
- implementation plan: `knowledge/wiki/syntheses/planning-authority-policy/implementation-plan.md`
- normalized packet: `knowledge/wiki/syntheses/planning-authority-policy/input-packet.json`
- packet SHA-256: `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`
- `validate_input_packet.py`: `ok: true`、errorsなし。
- capability preflight: `ok: true`。approved-spec seal、issue-implementation-loop、TDD、independent reviewが利用可能。parallel availabilityはplatform-dependentで、serial fallbackはworker contextに限定する。
- fresh planning verification: grill-to-pr-loop 58 tests、llm-wiki 6 tests、`git diff --check`がpass。
- default checkout: `HEAD=f5d151e34de5089d75be68249e09da8a2d14f282`、`## main...origin/main`でplanning開始時snapshotから不変。
- approved write scopeと`PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`はIssue Gateから不変。runnableはPAP-001だけ、後続worktreeはblocker releaseまで作らない。
- phase policy: planning artifactをcurrent planning branchのGate commitで固定し、executionはfresh / compacted coordinatorへhandoffする。planning/grill sessionは実装しない。
- remote policy: `local_only`。unapproved external / high-risk actionがないため、追加Human approvalなしでExecution Plan Gateをauto-continueした。

## [2026-07-27] implementation-verification-handoff | Planning Authority Policy

- serial releaseは `PAP-001 -> PAP-002 -> PAP-003 -> PAP-004`。PAP-001は`5dfe3ff38d7c46f46c61714e5ab154613517babc`でfamily policy / validatorを実装し、reviewはCritical 0 / Important 0 / Minor 0でapproved。PAP-002はinitial `9d79aa6ddf5f4344641d755b64d96a32d4dd8389`に対するcycle 1 Important `intent_gap` 1件を`bf04888b41a37d2dd6488a2258f8fda400e6dd33`で修正し、cycle 2はfindings 0でapproved。PAP-003は`681dfb723be171b81502540ded0458c186f6f036`でmodel非永続化 / execution non-regressionを固定し、findings 0でapprovedとなった。
- PAP-004はIssue台帳、Implementation Plan、index、logをcurrent implementation evidenceへ同期した。specとsealed Input Packetはverify-onlyで、SHA-256は`6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68` / `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`のまま不変である。
- fresh full verificationはgrill-to-pr-loop 63件、issue-implementation-loop 284件、llm-wiki 6件、scripts 63件がpassした。skill architecture、3 context contracts、scoped dual-host compatibility、grill-to-pr-loop quick validator、`git diff --check`もpassし、context reportはwarningsなし、execution-plan headroom 20%である。
- approved PAP-004 write scope外のdiffはなく、execution schemas / validator / scheduler / runtimeのproduction diffはゼロ。default checkoutは`HEAD=f5d151e34de5089d75be68249e09da8a2d14f282`、`## main...origin/main`でplanning開始時snapshotと一致する。remote actionは0である。
- PAP-004のcommitted rangeに対するimplementation reviewとspec alignment reviewは未実施であり、local `PR_READY`にはしていない。このentryはreview handoffまでを記録し、review approvalを先取りしない。

## [2026-07-27] spec-alignment-fix-handoff | Planning Authority Policy

- PAP-004 initial closeout range `681dfb723be171b81502540ded0458c186f6f036..4bc6fe52e4bdd062a10766b96446b325a57c540a`のimplementation review cycle 1はCritical 0 / Important 0 / Minor 0でapprovedとなった。
- spec alignment review cycle 1はCritical 0 / Important 1 / Minor 0でchanges requestedとなった。production validatorはapproved 5 fieldすべての不正値を正しく拒否していたが、恒久的なinvalid-value regression coverageが`supporting_agent_authority` 1 fieldに限られていた。
- PAP-001 fix `40a4459a8a5ab9b6f6afff0bd3e6505821d049bf`は`integration_owner`、`supporting_agent_authority`、`decision_authority`、`model_selection`、`model_persistence`の5 subcasesをparameterized regressionへ固定した。focused architecture suite 8件、scripts 63件、architecture validator、committed-range `git diff --check`がpassし、PAP-001 fix review cycle 2はfindings 0でapprovedとなった。
- review-approved fixはmerge commit `11477585f1d0c77c842a1b654d3aaf0f182bda63`でPAP-004 final branchへ統合済みである。本docs fix workerはmerge、runtime mutation、remote actionを行わず、統合済みHEADをdurable docsへ同期した。
- fix統合後のfresh full verificationはgrill-to-pr-loop 63件、issue-implementation-loop 284件、llm-wiki 6件、scripts 63件、skill architecture、3 context contracts、context report、scoped dual-host compatibility、grill-to-pr-loop quick validator、`git diff --check`がpassした。context reportはwarningsなし、execution-plan headroom 20%を維持した。
- approved spec / sealed packetのSHA-256は`6f4a952f35dd44fb930af98403ddfe5f0760af1d398722b338a18ef4493f8c68` / `90b22e13c1a91abcee126fd05345941d91d0671c60cb6ec03774005c5c90b9d5`で不変。execution production diffはゼロ、default checkoutは開始時snapshotと一致、remote actionは0である。
- PAP-004のfix同期commitを含むfinal rangeに対するimplementation review cycle 2とspec alignment review cycle 2は未実施であり、local `PR_READY`にはしていない。cycle 2 approvalを先取りしない。

## [2026-07-27] query | SDD Implementation Skill 設計

- 承認済みimplementation planからSuperpowers SDDを実行し、repository固有責務をruntime-only model / reasoning routingと`llm-wiki`による日本語wiki・`knowledge/index.md`・`knowledge/log.md` closeoutへ限定する設計を`knowledge/wiki/syntheses/sdd-implementation-skill-design.md`へ追加した。
- main sessionはbalanced capabilityのorchestratorとしてstate、routing、path handoffだけを所有し、current-state investigation、implementation、task review、wiki authoring、final reviewをisolated subagentへ委譲する。run-specific model名、reasoning値、provider、agent IDはdurable artifactへ保存しない。
- wiki closeoutをwhole-branch final reviewの前に置き、knowledge rootがあるrepositoryでは日本語wiki、index、log同期とvalidationを`LOCAL_COMPLETE`の必須条件にした。
- Phase 1は新`sdd-implementation` skillを既定入口として追加し、旧`grill-to-pr-loop` / `issue-implementation-loop`を明示指定時だけ残す。Phase 2の別PRで旧loop skill production filesを削除し、historical wikiはsuperseded evidenceとして保持する。
- production implementation、旧skill変更・削除、push、PR作成、merge、release、live installは未実施。written design review後にimplementation planへ進む。

## [2026-07-27] design-review-update | SDD Implementation Skill

- Human feedbackにより、実装の第一優先を「承認済み要件の実現」と「その要件を満たす最も単純なimplementation」に固定した。将来仮説や互換性だけを理由にschema、state、adapter、fallback、設定を増やさない。
- task review / final reviewをrequirements fit、material simplicity、material current riskの3観点へ限定した。style preference、具体的failure pathのない将来懸念、scope外refactor / hardening、軽微なformatting、同等案への好みはblocking findingにしない。
- blocking findingはrequirement gap、scope excess、observable regression、material current riskのいずれかとevidenceを必要とする。material simplicity findingには同じ要件を満たすconcrete simpler alternativeとmaterial impactも要求し、それ以外のobservationはfix loopやcompletionを妨げない。
- このreview thresholdはmechanical validator、schema check、required test suiteを弱めず、機械的に検出できるblocking failureは従来どおり修正対象とする。
- production implementation、旧skill変更・削除、remote actionは引き続き未実施。更新後のwritten design reviewを経てからimplementation planへ進む。

## [2026-07-27] execution-plan-candidate | SDD Implementation Skill

- Humanがwritten designを承認したため、`sdd-implementation-skill-implementation-plan.md`を作成した。
- planは新Skill本体、既定repository route、integrated verificationと日本語wiki closeoutの3 taskに限定した。独自script、reference群、runtime state、packet schemaは追加しない。
- Skill authoringはpressure scenarioのRED、static contract RED、最小SkillのGREEN、fresh evaluatorによるforward verificationの順で行う。
- 旧`grill-to-pr-loop` / `issue-implementation-loop` directoryはPhase 1で変更せず、repository routerとarchitecture policyだけで新Skillを既定入口にする。
- repository-wide dual-host validatorには変更前から`skills/llm-wiki/DESCRIPTION.md`の既知findingがある。scopeを広げず、新Skillのscoped dual-host validatorを完了条件にする。
- production implementation、push、PR作成、merge、release、live installは未実施。

## [2026-07-27] local-complete | SDD Implementation Skill Phase 1

- `skills/sdd-implementation/`を追加し、Superpowers SDDをexecution engineとして再利用するmain-coordinator-only、isolated worker、runtime-only model / reasoning routingを実装した。
- reviewはrequirements fit、material simplicity、material current riskに限定し、evidenceのないnit、style preference、future-only concern、scope外hardeningをblockingにしない。mechanical validationとrequired testsは維持する。
- implementation task review後、final whole-branch review前に`llm-wiki`による日本語wiki、`knowledge/index.md`、`knowledge/log.md`同期を必須化した。knowledge rootなしは`not_applicable`、存在するrootの未解決closeoutは`BLOCKED`とする。
- repository routerと`skill-architecture.toml`の`default_implementation_skill`は`sdd-implementation`を既定実装入口にした。context-contract-managedな旧`user_facing_skills` listと`grill-to-pr-loop` / `issue-implementation-loop`本体は変更せず、明示指定時だけ残した。
- scoped skill tests、repository script tests、architecture / context validators、新Skillのdual-host / skill-creator validators、`llm-wiki` tests、Git diff checkがfreshに成功した。
- repository-wide dual-host validationには変更前から`skills/llm-wiki/DESCRIPTION.md`の既知findingが残る。Phase 1ではscopeを広げず、新Skillのscoped dual-host validationを完了条件とした。
- push、PR作成、merge、release、live install、Phase 2の旧skill削除は未実施。

## [2026-07-27] execution-plan-gate | SDD Implementation Skill Phase 2

- session userが`sdd-implementation`を既定実装入口とした後の旧実装系skill削除を依頼し、既存designのPhase 2 scopeを実行承認した。
- `knowledge/wiki/syntheses/sdd-implementation-phase2-removal-plan.md`を作成し、Task 1をSDD単独route化と削除前の実run / forward evidence、Task 2を`skills/grill-to-pr-loop/`、`skills/issue-implementation-loop/`、専用runtime/context surfaceの削除に限定した。
- historical wiki、`knowledge/raw/**`、`skill-repository-optimization-v4-context-baseline.json`は削除せず、current executable surfaceからだけ切り離す。`planning_authority`とSDDのforbidden standalone component policyは保持する。
- worktreeは`codex/sdd-implementation-phase2-removal`、開始HEADは`8ff2bdcb5e8e74e2de17ca742ff0e2ff6488c8bd`、default checkoutは同HEAD・差分なし。push、PR、merge、release、live installは非対象である。

## [2026-07-27] implementation-closeout | SDD Implementation Skill Phase 2

- Task 1は`ce87b65`とfix `4e4f532`でSDD-only route、architecture policy、CIを成立させ、fix round 1後のtask reviewはcleanとなった。reported GREEN evidenceはfocused architecture/CI 11 tests、`skills/sdd-implementation/tests` 9 tests、architecture validatorのpassである。
- Task 2は`1def312405a1c1046366be749d85d3a493e5f887`で`skills/grill-to-pr-loop/`、`skills/issue-implementation-loop/`、3件の旧loop ledger test、専用runtime/context report surfaceをcurrent treeから削除し、task reviewはfindings 0でcleanとなった。reported GREEN evidenceはfocused architecture/context 12 tests、scripts 42 tests、`skills/llm-wiki/tests` 5 tests、context validator/report、architecture validator、dual-host CI workflowのpass、およびproduction surface grepのmatchなしである。
- `knowledge/raw/**`、historical wiki、`skill-repository-optimization-v4-context-baseline.json`は削除せず、historical / non-executable evidenceとして保持した。indexの旧packet、handoff、baselineのcurrent / executable / restart表現を更新し、削除済みproduction filesへのMarkdown linkをhistorical inline codeへ置換した。
- Phase 2のfresh final verificationとknowledge closeout後のwhole-branch final reviewは未実施であり、`LOCAL_COMPLETE`を先取りしない。push、PR作成、merge、release、live installも未実施で、remote stateは変更していない。

## [2026-07-27] local-complete | SDD Implementation Skill Phase 2

- fresh coordinator verificationはSDD 9 tests、llm-wiki 5 tests、scripts 42 tests、architecture validator、1 context contract、warnings空かつexit 0のgeneric context report、scoped dual-host validator、skill-creator `quick_validate`でpassした。両旧directoryはabsent、non-knowledge legacy literal grepとdeleted-production Markdown link grepはmatchなし、branch diff checkはcleanである。
- `8ff2bdc..804c2c7`のfinal whole-branch reviewはCritical 0、Important 0、Minor 0、Ready to merge Yesである。Task 1/Task 2 review、knowledge closeout、fresh verification、final reviewが揃ったため、Phase 2を`LOCAL_COMPLETE`とする。
- push、PR作成、merge、release、live installは未実施であり、remote stateは変更していない。

## [2026-07-27] written-spec-candidate | SDD Implementation Superpowers-first Revision

- Superpowers v6.2.0の一次情報を調査し、SDDにはdispatchごとのmodel選択が既にある一方、modelと独立したreasoning effort contractとHermes Agent公式adapterはないことを`knowledge/wiki/syntheses/sdd-superpowers-model-and-reasoning-research.md`へ保存した。
- `sdd-implementation`の後継設計を、Superpowers `brainstorming -> writing-plans -> subagent-driven-development`を主系とする構成へ更新した。repo-local skillはupstream lifecycle、TDD、review、model tierを再実装しない。
- specが存在しない、未承認、またはmaterialに未確定な場合は`Grill with Docs`を必須とし、一問一答で仕様を詰める。Human-approved current specがある場合は再grillingせず、完了済みstageをskipする。
- `llm-wiki`はrelevant knowledge queryと、Human-approved spec、repository-approved plan、implementation closeoutのdurable syncを所有する。Grill / Domain Modelingの既定出力を使った`CONTEXT.md`やrepo-root `docs/adr/`という並行正本は作らない。
- dispatch model tierはSuperpowersを正本とし、repo-local責務をhostのconcrete model resolutionとoptionalなlow / medium / high reasoning effort overlayへ限定した。effort非対応hostは`not_supported`としてmodel selectionだけで継続し、isolated model dispatch自体が不可能な場合だけ`BLOCKED`とする。
- 既存implementation planはPhase 1のhistorical evidenceへ状態変更した。production skill変更、successor implementation plan、remote actionは未実施であり、本Written SpecのHuman review待ちである。

## [2026-07-27] spec-gate | SDD Implementation Superpowers-first Revision

- Humanは`knowledge/wiki/syntheses/sdd-implementation-skill-design.md`のSuperpowers-first revisionをWritten Specとして承認した。
- Superpowersがbrainstorming、writing-plans、SDD、review、model tierを所有し、repo-local責務をGrill with Docs、LLM Wiki、host model resolution、optional reasoning effortへ限定するownershipは確定した。
- spec未作成またはmaterial ambiguityありではGrill with Docsを必須とし、approved current spec / planがある場合は完了済みstageをskipする。
- production skill変更、implementation plan、worker dispatch、remote actionはこのSpec Gate時点では未実施である。

## [2026-07-27] execution-plan-candidate | SDD Implementation Superpowers-first Revision

- Humanは`knowledge/wiki/syntheses/sdd-implementation-skill-design.md`をSuperpowers-first revisionのWritten Specとして承認した。
- `superpowers:writing-plans`を使い、後継implementation planを`knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md`へ作成した。
- planはSkill lifecycle contract、repository router / architecture / Codex metadata、LLM Wiki closeoutとfull verificationの3 taskに限定した。新しいscript、schema、scheduler、runtime state、old loop fallbackは追加しない。
- Task 1は`superpowers:writing-skills`と`superpowers:test-driven-development`を必須とし、contract testのREDから開始する。Task 2はdefault routeとUI copyを揃え、Task 3はsingle-root ingestとfinal whole-branch reviewを行う。
- production skill変更、Execution Plan Gate、worker dispatch、remote actionは未実施である。

## [2026-07-27] execution-plan-gate | SDD Implementation Superpowers-first Revision

- Humanは`knowledge/wiki/syntheses/sdd-implementation-superpowers-first-implementation-plan.md`をExecution Plan Gateとして承認し、`superpowers:subagent-driven-development`による実行を選択した。
- 実行順はTask 1のshared Skill lifecycle contract、Task 2のrepository router / architecture / Codex metadata、Task 3のLLM Wiki closeout / full verification / final reviewである。
- fresh implementer、task-scoped independent reviewer、fix loop、final whole-branch reviewはSuperpowers SDDに従い、main sessionはcoordinationとartifact handoffだけを所有する。
- remote policyはlocal-onlyであり、push、PR作成、merge、release、live installは未承認のままである。

## [2026-07-27] final-review-candidate | SDD Implementation Superpowers-first Revision

- Task 1は`65abafa` `feat: make SDD implementation Superpowers-first`とreview fix `6fa0f4f` `test: cover SDD review and remote boundaries`で完了し、Task 1 review fix round 1はapproved（open material findingなし）である。Task 2は`693e1aa` `docs: route repository changes through Superpowers`で完了し、task reviewはmaterial findingなしでapprovedである。SHAとsubjectは`git log --oneline --reverse 8c18ef0..HEAD`で確認した。
- fresh verificationはLLM Wiki 6 tests、`sdd-implementation` 12 tests、repository scripts 68 testsがすべて`OK`である。skill architecture、3 skill context contracts、`sdd-implementation` scoped dual-host compatibility、skill-creator quick validator、Step 3 / Step 4の`git diff --check`も成功した。
- design、current successor plan、indexをfinal whole-branch review待ちへ同期した。`LOCAL_COMPLETE`、final review approval、`local-complete` entryは記録していない。push、PR作成、merge、release、live installも未実施である。

## [2026-07-27] local-complete | SDD Implementation Superpowers-first Revision

- Task 1は`65abafa` `feat: make SDD implementation Superpowers-first`とreview fix `6fa0f4f` `test: cover SDD review and remote boundaries`、Task 2は`693e1aa` `docs: route repository changes through Superpowers`で完了し、各task reviewはapprovedである。Task 3 closeout candidateは`ec12012` `docs: prepare Superpowers-first SDD final review`で記録した。
- `ec12012`に対するfinal whole-branch reviewはCritical 0、Important 5、Minor 1を検出した。`8b35113` `fix: address Superpowers-first SDD review findings`が6件すべてをbounded waveで解消し、scoped re-reviewはall findings addressed・new Critical/Important breakageなしでapprovedとなった。
- fresh post-fix verificationはSDD 17/17、LLM Wiki 6/6、scoped dual-host compatibility、skill-creator quick validator、`git diff --check HEAD^ HEAD`のすべてが成功した。Task 2 full bundleとしてscripts 68/68、skill architecture validator、3 skill context contracts、scoped dual-host compatibility、skill-creator quick validator、`git diff --check`もcandidate closeoutで成功済みである。
- knowledgeのdesign、current / implemented successor plan、index、append-only logをcloseoutへ同期した。residual material riskはない。push、PR作成、merge、release、live install、issue / comment / project変更を含むremote writeは実施していない。

## [2026-07-28] main-integration | SDD Implementation Skill Phase 2

- GitHub上の最新`main`である`dec5647`（PR #39、Superpowers-first revision）を`codex/sdd-implementation-phase2-removal`へ統合した。`AGENTS.md`、architecture policy / tests、SDD design、knowledge index / logの競合は、Superpowers-first lifecycleとSDD-only route / legacy removalの両方を保持して解消した。
- fresh verificationはSDD 17 tests、LLM Wiki 5 tests、repository scripts 43 tests、skill architecture validator、1 skill context contract、warningsなしのcontext report、scoped dual-host validator、skill-creator quick validator、legacy directory absence、`git diff --check`のすべてが成功した。
- branchはDraft PR #41として公開済みである。PR merge、release、live installは未実施である。

## [2026-07-28] spec-and-plan-gate | SDD Reasoning Effort Risk Precedence

- Humanは既存のlow / medium / high mappingを維持し、task complexity / riskをrole defaultより優先する方針を承認した。通常のtask reviewはmedium、architecture-sensitive / high-risk task reviewはhighとする。
- 共有default contractへ`xhigh`、`max`、`ultra`その他host-specific levelを追加せず、明示的runtime overrideとしてのみ扱う。user override、stuck-fix one-step escalation、effort `not_supported`時の継続条件は変更しない。
- canonical designを更新し、実装計画を`knowledge/wiki/syntheses/sdd-effort-risk-precedence-implementation-plan.md`へ作成した。Execution Plan Gateは承認済みであり、fresh implementer、independent task review、knowledge closeout、final whole-branch reviewへ進む。
- push、PR、merge、release、live installその他のremote writeはscope外である。

## [2026-07-28] final-review-candidate | SDD Reasoning Effort Risk Precedence

- spec / planは`c49fa714c917d4a0e7948ab92dfb828f2748b555`（`docs: define SDD effort risk precedence`）、Task 1 implementationは`2549892c07dc3f65c22094ca27b9208c831e65b0`（`Clarify SDD effort risk precedence`）である。Task 1の独立reviewは`APPROVED`、material findingなしである。
- fresh verificationはSDD contract 18 tests、repository scripts 43 tests、LLM Wiki 5 testsが各`OK`であり、skill architecture validator、1 skill context contract validator、scoped dual-host compatibility、skill quick validation、`git diff --check`も成功した。
- canonical design、focused plan、indexをTask 1実装済み・independent approval済みの状態へ同期した。spec、plan、Skill、tests、knowledge artifactsを同じbranch rangeで確認するfinal whole-branch reviewはpendingである。
- `LOCAL_COMPLETE`と`local-complete` entryは記録していない。push、PR、merge、release、live installその他のremote writeは未実施である。

## [2026-07-28] final-review-fix-candidate | SDD Reasoning Effort Risk Precedence

- closeout candidate `ffa8339df00a5a8dfec90f572e843509516f49fe`へのfinal whole-branch reviewはImportant 2件を返した。designとfocused planのindex entryが1つの検索語行を共有していたdiscoverability gap、およびfocused planにrelated-page linksとprovenance sectionがないcitation gapである。
- bounded fixで各index entryへ直後の専用`検索語:`行を置き、focused planへcanonical designと既存Superpowers model / reasoning researchを辿る`関連ページ`と`出典`を追加した。
- fresh LLM Wiki 5 testsと`git diff --check`は成功した。scoped re-reviewとfinal approvalはpendingであり、`LOCAL_COMPLETE`と`local-complete` entryは記録していない。
- push、PR、merge、release、live installその他のremote writeは未実施である。

## [2026-07-28] local-complete | SDD Reasoning Effort Risk Precedence

- spec / plan commitは`c49fa714c917d4a0e7948ab92dfb828f2748b555`、Task 1 implementationは`2549892c07dc3f65c22094ca27b9208c831e65b0`、closeout candidateは`ffa8339df00a5a8dfec90f572e843509516f49fe`、final-review bounded fixは`a7d0d294a6ccdbeec84f44c0cd6f3060967de5d1`である。
- final whole-branch reviewが返したImportant 2件は、index entryごとの検索語associationとfocused planのrelated-page / provenance不足であった。bounded fixは両方を解消し、scoped re-reviewはresolved 2/2、新規Critical / Importantなしで`APPROVED`となった。
- fresh verificationはLLM Wiki 5 testsが`OK`、`git diff --check`が出力なしで成功した。先行closeout candidateのSDD contract 18 tests、repository scripts 43 tests、skill architecture / context validator、scoped dual-host compatibility、skill quick validationも成功済みである。
- Task 1 implementation、independent task review、knowledge closeout、final whole-branch review、bounded fix、scoped re-review、fresh verificationが揃ったため`LOCAL_COMPLETE`とする。
- push、PR作成、merge、release、live installその他のremote writeは実施していない。

## [2026-07-28] spec-and-plan-gate | SDD Agent-Agnostic Runtime Contract

- Humanは、skillを特定agentに依存させず、どの対応runtimeでも同じ`SKILL.md`、入力、依存skill、必要capabilityからbehaviorを決める方針を明示承認した。
- agentごとのdependency確認、agent名によるdispatch / fallback / verification分岐はcurrent contractから削除する。dependency discoveryはactive runtimeで一度だけ行い、isolated dispatch、explicit model、optional effort、wait / resumeはcapabilityとして解決する。
- canonical designを`knowledge/wiki/syntheses/sdd-implementation-skill-design.md`へ同期し、実装計画を`knowledge/wiki/syntheses/sdd-agent-agnostic-runtime-implementation-plan.md`へ作成した。実装はportable skill contractとdurable knowledge closeoutの2 taskで行う。
- plugin packaging adapterとhistorical non-executable planはscope外である。push、PR、merge、release、live installその他のremote writeは未承認である。

## [2026-07-28] implementation-closeout-candidate | SDD Agent-Agnostic Runtime Contract

- Task 1 は `33fe86b240efcd03e8e9c6020f6620e87747da2d`（`Make skill runtime contracts agent agnostic`）で完了し、独立 task review は Critical / Important / Minor なしの `Approved` である。baseline pressure scenario の named dual-runtime preflight は、post-change scenario で active runtime の一回だけの dependency / capability discovery、capability-only dispatch mapping、optional effort `not_supported` 時の継続へ置換された。
- fresh local verification は `skills/sdd-implementation/tests` 18 tests、`skills/llm-wiki/tests` 5 tests、`scripts` 44 tests が各 `OK`、`validate_skill_architecture.py --all`、`validate_skill_context.py --all`（1 contract）、`validate_repository_compatibility.py --skill skills/sdd-implementation`、`git diff --check` がすべて exit 0 である。
- repository-wide compatibility は pre-existing な case-insensitive `skills/llm-wiki/DESCRIPTION.md` collision が本変更の範囲外のため未実行である。push、PR作成、merge、release、live install、issue / comment / project mutationその他のremote writeは実施していない。whole-branch final reviewと`LOCAL_COMPLETE`もこのcandidateでは未実施である。

## [2026-07-28] final-review-fix-candidate | SDD Agent-Agnostic Runtime Contract

- `0501c4522f6d20775a88537b3cd7787a0b9d7eaf`までのwhole-branch final reviewはImportant 3件を返した。result collectionのfail-closed条件不足、current catalogからsuperseded planへ戻れるprovenance gap、plugin guidanceに残った旧validator名である。
- bounded fixは、completed resultを返すsynchronous dispatchを有効なresult collectionとし、asynchronous dispatchにwait / resumeを要求し、どちらも利用できない場合を`BLOCKED`とした。dual-host planはhistorical / non-executable、Superpowers-first planはruntime固有部分がsupersedeされた実装済みbaseline、本agent-agnostic planはcurrent delta / closeout candidateとしてcatalogとcanonical designを同期した。plugin handoffは`scripts/validate_repository_compatibility.py`へ更新し、paired plugin manifest / version / registration validationは変更していない。
- TDDのexpected REDは、SDD contractが19 tests中1 failure（result-collection semantics欠落）、authoring guidanceが3 tests中1 failure（現行validator path欠落）であった。production変更後はSDD contract 19 tests、authoring guidance 3 tests、LLM Wiki 5 tests、repository scripts 44 testsが各`OK`、skill architecture validator、1 skill context contract validator、scoped repository compatibility、skill-creator quick validation、`git diff --check`がすべて成功した。
- pressure scenarioでは、synchronous dispatchがcompleted resultを返す場合はwait / resumeなしでも有効、asynchronous dispatchでwait / resumeを満たせない場合は`BLOCKED`、independent effort controlだけがない場合は`not_supported`としてSuperpowers model selectionで継続となる。
- scoped re-review、final approval、`LOCAL_COMPLETE`はpendingである。push、PR作成、merge、release、live install、issue、comment、project mutationその他のremote writeとlive mutationは実施していない。

## [2026-07-28] local-complete | SDD Agent-Agnostic Runtime Contract

- spec / plan baselineは`c1f3791`、Task 1は`33fe86b`（review 0 findingsでApproved）、Task 2は`171d4f1`、Task 2 fixは`0501c45`（scoped re-review Approved）である。final reviewはCritical 0 / Important 3 / Minor 0を返した。
- bounded final fix `44edcf0`が3件を解消し、final scoped re-reviewは全3件の解消、新規Critical / Important breakageなし、`APPROVED`を確認した。fresh pressure scenarioではsynchronous completed resultはwait / resumeなしで継続、asynchronous dispatchでwaitまたはresumeがなければ`BLOCKED`、optional effortがなければ`not_supported`として継続する。
- canonical design、current plan、index、append-only logを同期し、fresh `skills/llm-wiki/tests` 5 testsと`git diff --check`が成功した。residual material riskはない。remote writeおよびlive mutationは実施していない。

## [2026-07-28] spec-and-plan-gate | SDD Compatibility Removal Follow-up

- HumanはPR作成を選択し、publish前条件としてcross-runtime compatibilityは不要と明示した。標準`SKILL.md`とactive-runtime capabilityによるagent-agnostic behaviorは維持する。
- paired runtime packages、manifest整合、repository compatibility validator、compatibility CI gateはcurrent requirementから削除する。pluginは必要なruntimeを個別targetでき、互換性だけのために別runtime packageを追加しない。
- focused planを`knowledge/wiki/syntheses/sdd-compatibility-removal-follow-up-plan.md`へ作成した。local completion後のbranch pushとPull Request作成は承認済みであり、merge、release、live mutationは未承認である。

## [2026-07-28] local-complete | SDD Compatibility Removal Follow-up

- Task 1は`a1a177b877ebb07258bb69aa6d1f6f3429e9bc6e`（`Remove cross-runtime compatibility requirements`）で完了した。独立reviewは`APPROVED`で、Critical / Important / Minorのfindingはない。standard `SKILL.md`、agent-agnostic skill behavior、active-runtime capability boundaryは維持し、paired runtime packages、manifest compatibility、repository compatibility validator、compatibility CI gateはcurrent requirementから削除した。
- current repositoryにはcompatibility validatorとcompatibility CI gateは存在しない。旧Codex / Hermes dual-host designはskill behaviorとplugin packaging compatibilityの双方でhistorical / non-executableであり、旧implementation plan本文と先行log entryはappend-only evidenceとして保持した。
- fresh verificationは`PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests`が5 tests `OK`、`PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s scripts`が19 tests `OK`、`git diff --check`が出力なし・exit 0で成功した。
- residual material riskはない。local branchはPR-readyである。pushとPull Request作成は承認済みだが本taskでは未実施であり、merge、release、live mutationは未承認かつ未実施である。

## [2026-07-28] final-review-correction | SDD Compatibility Removal Follow-up

- 直前の`local-complete` entryは、complete branchに対するfinal whole-follow-up reviewより先に`LOCAL_COMPLETE` / PR-readyを記録したため、current completion stateとしてsupersedeする。append-only evidenceとして旧entryは保持するが、本follow-upはfinal-review-fix candidateへ戻し、scoped re-review承認まではfinal review pendingとする。
- `f0b8efd...bc46e60`のfinal reviewはCritical 0 / Important 2 / Minor 1で`NOT READY TO MERGE`を返した。bounded fixは、follow-up planへfinal review、fix、scoped re-review、completion restoreの順序を追加し、Task 2を完了済みのcloseout candidateとして記述した。preceding agent-agnostic planはhistorical / non-executableとし、削除済みcompatibility validator commandとunchecked checklistをobsoleteと明示した。
- current Planning Authority specからdual-host requirement、runtime名ごとのmodel設定例、削除済みcompatibility validator command、scoped dual-host acceptance / stop conditionを除き、標準`SKILL.md`とactive-runtime capabilityによるportable contractへ置換した。catalogとtransient ledgerも同じcurrent / historical boundaryへ同期した。production codeとCIは変更していない。
- fresh verificationはLLM Wiki 5 tests、repository scripts 19 testsが各`OK`、skill architecture validator、1 skill context contract validator、warning-free context report、`git diff --check`がすべて成功した。scoped re-reviewとcompletion restoreはpendingであり、現時点で`LOCAL_COMPLETE` / PR-readyではない。push、Pull Request作成、merge、release、live mutationは実施していない。

## [2026-07-28] local-complete | SDD Compatibility Removal Follow-up

- bounded final fix `ae151b979e20b656b5a7173eb841228256c90632`はfinal whole-follow-up reviewのCritical 0 / Important 2 / Minor 1を対象とした。`bc46e60..ae151b9`のscoped re-reviewは全3 findingの解消と新規findingなしを確認し、Critical 0 / Important 0 / Minor 0で`APPROVED`となった。
- current follow-up planはfinal review、bounded fix、scoped re-review、completion restoreをすべて完了し、catalogとtransient ledgerも同じ状態へ同期した。これにより本follow-upを`LOCAL_COMPLETE`かつPR-readyとする。
- closeout後のfresh verificationは`PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests`が5 tests `OK`、`git diff --check`が出力なし・exit 0で成功した。pushとPull Request作成は承認済みだが未実施であり、merge、release、live mutationは未承認かつ未実施である。

## [2026-07-29] written-spec-review-candidate | SDD Pre-Implementation Context Isolation

- Humanは、`sdd-implementation`を唯一のuser-facing entrypointとして維持し、Research、Spec Synthesis、Plan Authoringを内部seamとfresh workerへ分離するGrand Designのshared understandingを承認した。
- Planning ControllerはHuman対話、Decision Record、approval、routingだけを所有する。source code、broad wiki / docs、full spec / plan、diff、test output、複数file探索はworkerだけが読み、worker detailsはartifact pathへ置く。
- Research Reportはplanning worktree内のgitignoredな`.superpowers/research/<epic-id>/`へ置く。spec draftのConfirmed Decisions / Open Decisionsを唯一のDecision Recordとし、別ledger、`CONTEXT.md`、custom scheduler、runtime / packet schemaを追加しない。
- Control Return 200 words、Stage Capsule 400 wordsは運用目安に限定し、context telemetry、manual compaction、strict word validator、main-session fallbackは非目標とした。
- focused revision spec、index、append-only logを文書レビュー候補として同期した。HumanのWritten Spec review、implementation plan、implementation、remote writeは未実施である。

## [2026-07-29] spec-gate-approved | SDD Pre-Implementation Context Isolation

- Humanは`knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md`をWritten Specとして承認した。
- approved scopeは、`sdd-implementation`を唯一のuser-facing entrypointとして維持し、Research、Spec Synthesis、Plan Authoringをfresh workerへ分離し、Planning ControllerをHuman対話、Decision Record、approval、routingへ限定する。
- context telemetry、manual compaction、strict word validator、main-session exploration fallback、new user-facing skill、custom scheduler / runtime schemaは非目標のまま維持する。
- Spec Gateは承認済みである。Implementation planの作成・review・approval、implementation、remote writeは未実施である。

## [2026-07-29] plan-gate-approved | SDD Pre-Implementation Context Isolation

- Humanは`knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-implementation-plan.md`をrepository-required Plan Gateとして承認した。これはcurrentな実行計画であり、承認済みWritten Spec `knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md`およびbaseline `66d93ae4a233fc8f9750b6bc6d824cc54bb0838d`（`66d93ae`）にbindingされる。
- 計画、`knowledge/index.md`、append-only `knowledge/log.md`をDurable Knowledge checkpointとして同期した。implementation、task review、knowledge closeout、final whole-branch reviewは未実施である。
- push、PR、merge、release、live install、issue、comment、project変更その他のremote writeは未承認かつ未実施である。

## [2026-07-29] implementation-closeout-candidate | SDD Pre-Implementation Context Isolation

- Task 1は`1f5906fdb185cdf436eda31ccefedf3d0e3f1220 Add SDD planning controller contract`、Task 2は`44c52cdb3426363a32203cbcb3d486eeb0ac56d5 Route SDD planning work to fresh workers`である。`git log --format='%H %s' 66d93ae..HEAD`でfull SHAとsubjectを確認した。
- Task 1の独立task reviewは`APPROVED`、material findingなしである。Task 2の独立task reviewも`APPROVED`、material findingなしである。
- fresh-context forward scenarioは7件すべて`PASS`である。(1) rough change requestではResearch Workerだけがrepository evidenceを読み、Controllerはsourceを読まなかった。(2) 325行・2,365語のlong reportはartifactへ置き、direct returnを4 fieldに限定した。(3) confirmed decisionを再質問せず次のopen decisionへrouteした。(4) material conflictがあるdecisionだけを再openした。(5) fresh Spec Synthesis / Spec Reviewを分離し、Human Written Spec approvalを保持した。(6) fresh Plan Authorがbaseline `66d93ae`、approved spec、repository rules、`writing-plans`にbindingしたTDD planを作成・self-reviewした。(7) isolated dispatch欠如時は`BLOCKED`を返し、Controller explorationへfallbackしなかった。別のfresh verifierも7件にmaterial gapがないことを確認した。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 -m unittest discover -s skills/sdd-implementation/tests -v`は32 tests、`OK`である。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 -m unittest discover -s skills/llm-wiki/tests -v`は5 tests、`OK`である。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 -m unittest discover -s scripts -v`は19 tests、`OK`である。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 scripts/validate_skill_architecture.py --all`は`OK: validated skill architecture policy (repository-change-loop)`である。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 scripts/validate_skill_context.py --all`は`OK: validated 1 skill context contract(s)`であり、SDD context contractは追加されていない。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 scripts/report_skill_context.py --all --json --fail-on-warning`はexit 0、1 skill・12 operations、warnings 0である。
- `PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation`は`Skill is valid!`である。
- `test ! -e skills/grill-to-pr-loop`、`test ! -e skills/issue-implementation-loop`、`test ! -e skills/sdd-implementation/context-contract.toml`、`test ! -e skills/sdd-implementation/runtime-state.json`、`test ! -e skills/sdd-implementation/worker-packet.json`はすべてexit 0である。
- `git diff --check 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..HEAD`はexit 0、出力なしである。residual material riskは`none`である。
- canonical design、index、append-only logをimplementation closeout candidateへ同期した。whole-branch final reviewはcontrollerが別のfresh reviewerへdispatchするためpendingであり、`LOCAL_COMPLETE`を先取りしない。
- push、PR作成、merge、release、live install、issue作成・更新、comment、project変更、その他のremote writeはすべて未実施であり、remote stateは変更していない。

## [2026-07-29] final-review-approved-local-complete | SDD Pre-Implementation Context Isolation

- fresh whole-branch reviewは`66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..c7a69927cf74f9316b2b1122283ca0b0e47d8e6b`を対象に、Critical 0 / Important 0 / Minor 0、`Ready to merge: Yes`で承認した。Task 1 / 2 / 3 reviewもcleanであり、residual material riskはない。
- full fresh verification（SDD 32/32、LLM Wiki 5/5、repository scripts 19/19、全validator・absence・diff・branch-integrity check）は成功したため、本変更を`LOCAL_COMPLETE`とする。
- local-only completionである。push、PR作成、merge、release、live install、issue、comment、project変更を含むremote writeはすべて未実施かつ未承認である。

## [2026-07-30] spec-gate-approved | llm-wiki Authoring Responsibility Separation

- Human は [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]] を Written Spec として承認した。仕様の `status` を `approved` とし、承認日を `2026-07-30` と記録した。
- durable catalog を同じ承認状態へ同期した。implementation plan、implementation、remote write は未実施である。

## [2026-07-30] plan-gate-approved | llm-wiki Authoring Responsibility Separation

- Human は [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-implementation-plan|llm-wiki authoring 責務分離実装計画]] を実装計画として承認し、`Human-approved / current` として記録した。[[index|durable catalog]] を同じ承認状態へ同期した。

## [2026-07-30] implementation | llm-wiki authoring responsibility separation

- [[llm-wiki-authoring-responsibility-separation-spec]] と [[llm-wiki-authoring-responsibility-separation-implementation-plan]] に従い、[[AGENTS.md|local contract]] と [[index|durable catalog]] を `obsidian` authoring profile と maintained internal-note migration へ同期した。
- `raw/**` は untouched のまま保持し、historical spec の evidence と raw citation を変更していない。

## [2026-07-30] implementation-closeout | llm-wiki authoring responsibility separation

- current [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]] と [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-implementation-plan|llm-wiki authoring 責務分離実装計画]] を`Implemented / closeout verified`へ同期した。authoring responsibility boundaryと各taskのacceptance criteriaは変更していない。
- prerequisiteとなるreviewed commitsは、Task 1 `ee46afd4cb26be2b25b0376670b8d3e6c8e1e4ac` / `eb46b685eb256276f7c56419f71fa86d32eec7f8`、Task 2 `9c76d0253995b375009867d5181ff7ba06cc6f54` / `dd73e3bb23ae4749ccacf53dc837b003d517278e` / `0d9928c5e717cc6f66d8cd1c6c4994b8111a71b3`、Task 3 `10cccfe18afa6c430b1541dee76963bfc92dd098` / `5ff7520777828d67bac6aa4e4c2fd9cc7655b882`であり、各独立task reviewはopen findingなしである。
- full fresh verificationとして、`python3 -m unittest discover -s skills/llm-wiki/tests -v`、`python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json`、`python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning`、`python3 scripts/validate_skill_architecture.py --all`、skill-creator `quick_validate.py`、focused `test_authoring_boundary.py`、`git diff --check f23bde7..HEAD`、`git diff --check`をすべてexit `0`で完了した。repository checkはObsidian reading-view renderingの証拠として扱っていない。
- `knowledge/raw/**`はuntouchedである。installed-skill-directed authoring reviewはstatic skill-directed reviewとして`PASS`し、Critical / Important findingはない。active runtimeにactual Obsidian reading-view controlはなく、`Obsidian reading-view rendering: unavailable`であり、rendered proofは主張しない。pendingなのはcontroller-owned Step 7 whole-branch reviewだけであり、その承認前に`LOCAL_COMPLETE`を宣言しない。

## [2026-07-30] final-review-fix | llm-wiki authoring responsibility separation

- final whole-branch reviewの3件のImportant findingに対し、一回のscoped fix waveで、portable Outputs / recovery stateとauthority-scoped durable edit capability、5つのlegacy templateのcreation / last-update semantic identityとrepresentation-neutral baseline mapping、adapter-resolved cross-root target identityのselected authoring skillへのserialization委譲を補完した。
- `test_public_contract_reports_completion_and_recovery_state`、`test_every_legacy_semantic_field_maps_to_exactly_one_current_identity`、`test_local_contract_selects_obsidian_without_copying_authoring_syntax`は、それぞれ欠落していたcontract、creation identity、cross-root semantic ruleを理由にREDとなり、最小実装後にGREENとなった。
- full fresh verificationはLLM Wiki 21 tests、12 topology × modeのcontext validation / warning-free report、repository skill architecture validation、skill-creator quick validation、focused boundary suite、literal 37-path assertion、baseline / working-tree diff check、raw / external-skill scope checkをすべてexit `0`で完了した。`knowledge/raw/**`とexternal installed authoring skillは変更していない。
- [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|current spec]] と [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-implementation-plan|current plan]] のproduct boundaryは変更していない。Step 7のfresh whole-branch re-reviewはcontroller-owned gateとしてpendingであり、`LOCAL_COMPLETE`は宣言しない。

## [2026-07-30] draft-review | SDD first-write worktree migration 仕様

- Actor: repository maintainer-delegated actor。Canonical OwnerであるHuman / repository maintainerの明示承認に基づく。
- Decision: `promote`。proposal [[wiki/drafts/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様（昇格済み draft）]] を、active canonical synthesis [[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]] へ昇格した。
- Authority result: `Read: allowed`、`Write Boundary: owned`、Canonical OwnerのHuman承認、およびselected authoring profile `obsidian` の手順を満たし、direct canonical updateを許可した。
- Lifecycle effect: draftを`promoted`として保持し、canonical targetを`accepted` / `active`として作成した。active catalogにはcanonical targetを1件だけ登録し、draftは登録していない。
- Evidence: HumanのWritten Spec明示承認、draft内の`Confirmed Decisions`、`Open Decisions: なし`、および`knowledge/AGENTS.md`のsingle-root owner/write-boundary contract。

## [2026-07-30] draft-review | SDD first-write worktree migration 実装計画

- Actor: repository maintainer-delegated actor。Canonical OwnerであるHuman / repository maintainerの明示承認に基づく。
- Decision: `promote`。proposal [[wiki/drafts/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration Implementation Plan（昇格済み draft）]] を、active canonical synthesis [[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]] へ昇格した。
- Authority result: `Read: allowed`、`Write Boundary: owned`、Canonical OwnerのHuman承認、およびselected authoring profile `obsidian` の手順を満たし、direct canonical updateを許可した。
- Lifecycle effect: draftを`promoted`として保持し、canonical targetを`accepted` / `active` implementation planとして作成した。active catalogにはcanonical targetを1件だけ登録し、draftは登録していない。
- Evidence: Humanのimplementation plan明示承認、承認済みdraft本文、および`knowledge/AGENTS.md`のsingle-root owner/write-boundary contract。remote publicationは承認・実施していない。

## [2026-07-30] plan-gate-approved | SDD first-write worktree migration

- Human承認済みの[[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]]をaccepted specとして、[[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]]をrepository-approved canonical implementation planとしてPlan Gateへ記録した。
- Canonical OwnerであるHuman / repository maintainerの明示承認に基づく。remote publicationは承認・実施していない。

## [2026-07-30] canonical-correction | SDD first-write worktree migration 実装計画

- [[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]]に、昇格元draftの`## Draft Review Decision`本文を決定内容を変えずに復元した。canonical metadata、active catalog、accepted specとのrelation identityは維持した。
- Canonical OwnerであるHuman / repository maintainerの承認済み昇格内容の完全性を是正するscoped correctionであり、remote publicationは承認・実施していない。

## [2026-07-30] implementation-closeout | SDD first-write worktree migration

- accepted [[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]] と canonical [[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|SDD first-write worktree migration 実装計画]] に従い、first-write planning worktree gate、bound planning paths、後続Epic限定のopt-in parallel adapter、single-writer integration/final gateから成るportable contractを完了した。仕様・計画の承認済みproduct boundaryは変更していない。
- 実装・task review済みcommitは Plan Gate `d463ce3`、Task 0 `62f9184`、Task 1 `17545a3` / `4942640`、Task 2 `cf30396` / `7477705` / `4551e06`であり、各task reviewはopen findingなしで完了した。promoted implementation-plan draftの先頭frontmatterを有効な`---`へ是正し、lifecycle / provenance / canonical target identityは維持した。
- local validationはSDD implementation unittest、skill architecture validation、skill context validation、architecture / CI validator unittest、skill-creator authoring validation、`git diff --check`を通過した。captured tupleとのoriginal checkout比較は開始時の`main`、`282fa44a9fe97d9d0feb2e8d6733a6ae47f00f78`、clean statusと一致した。remote publicationは承認・実施していない。

## [2026-07-30] human-ruling-correction | SDD first-write worktree migration

- Human rulingにより、final whitespace gateの正本はclean working treeだけを見る`git diff --check`ではなく、complete planning-branch rangeを検査する`git diff --check 282fa44a9fe97d9d0feb2e8d6733a6ae47f00f78..HEAD`とした。[[wiki/syntheses/sdd-first-write-worktree-migration-implementation-plan|canonical implementation plan]]のTask 3/Task 4 closeout instructionsとglobal final-gate ruleをこの判断へ同期した。
- [[wiki/syntheses/sdd-first-write-worktree-migration-spec|canonical specification]]末尾のsemanticsを持たないtrailing blank recordを除去した。accepted lifecycle、provenance、acceptance criteria、active catalog identityは変更していない。index summaryにgate表現は含まれないため変更不要である。
- このscoped correctionは明示されたHuman rulingに基づく。fresh validation、original-checkout preservation確認、canonical final reviewはこの訂正commit後にあらためて行い、remote publicationは承認・実施していない。

## [2026-07-30] correction | SDD first-write worktree migration final-review sequencing

- append-only recordとして、直前の`human-ruling-correction` eventにある「canonical final reviewはこの訂正commit後にあらためて行い」という wording を supersede する。このcorrection commitはTask 4のscoped re-reviewを受け、その完了後にcontrollerがTask 4 closeout後のsingle canonical final whole-branch reviewを初回として一度だけ実行する。
- canonical final whole-branch reviewはまだ実行しておらず、full reviewのrepeatは発生していない。remote publicationは承認・実施していない。

## [2026-08-14] ingest | SDD Plan Ownership Alignment 実装計画

- Planning ControllerからHuman-approved current Written Specとして渡された[[wiki/syntheses/sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]を、baseline `c370fe14de1641aa5ee30b3fa001f4d857078091`とspec SHA-256 `d3e7915fc5e69778140f549016e4fe8ba4308612df439d137f60cbc6b2520be9`へbindingし、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|agent-owned implementation plan]]としてingestした。
- Plan Author self-reviewはrequirements `15/15`、acceptance criteria `14/14`にprimary ownerがあり、unassigned item、orphan task、unknown ID、undefined dependency、dependency cycle、prospective production / test body、script / patch body、shell commit command、Human plan-approval / execution-choice promptがないことを確認した。
- active catalogをspec / planのcanonical relation identityへ同期した。Plan Author verdictは`ready_for_independent_review`であり、独立Plan Reviewerとrepository readiness gateは未実施であるため、Plan Readiness `ready`、Implementation Stage entry、local completionを先取りしない。
- implementation、push、PR creation、merge、release、live install / deployment、その他のremote / privileged / destructive actionは未実施である。Human plan approvalは要求せず、action-specific authorization boundaryは変更していない。

## [2026-08-14] review-fix | SDD Plan Ownership Alignment 承認記録と実装計画

- Human-approved current Written Specとして渡された[[wiki/syntheses/sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]のfrontmatterと状態説明を`accepted` / `approved` / `approved_on: 2026-08-14`へ同期した。North Star、requirements、acceptance criteria、non-goals、stop conditionsを含む承認済みproduct boundaryは変更していない。状態記録同期後のapproved spec SHA-256は`1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559`であり、先行ingest entryの`d3e7915...` bindingをsupersedeする。
- 独立Plan Reviewのblocking findingを受け、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|agent-owned implementation plan]]では、`plan-contract.md`追加で影響を受ける二つのstrict reference-set expectationをPOA-1へ割り当てた。POA-1のREDはtask内TDD checkpointであり、overlay実装とcompatibility repair後のGREENだけをtask review / I-1 gateとする。POA-2はそのreviewed GREEN stateをconsumeしてrouting contractを追加する。
- active catalogを承認状態とrevised plan semanticsへ同期した。Plan Readiness `ready`、Implementation Stage entry、implementation、remote actionはまだ完了・実施していない。

## [2026-08-14] review-fix | SDD Plan Ownership Alignment task boundary

- 実行履歴 `fa2b26c..6f1ca9f` が RED contract testsのみ、`6d8222d` が Plan Contract Overlay、representative fixture、compatibility repair、Plan Stage routing / reviewer prompt、focused GREENを所有することに合わせ、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|agent-owned implementation plan]]のtask boundaryを修復した。
- 直前の`review-fix` entryにある「POA-1内でREDからGREENまで完結する」というplan semanticsをsupersedeする。POA-1 completion / I-1はreviewed intentional RED、POA-2 completion / I-2が初めてのcombined GREENであり、POA-2はPOA-1 GREENやoverlay outputをpreconditionとしない。
- requirements `15/15`とacceptance criteria `14/14`のprimary ownership、3 task、execution / serialized integration order、prohibition、agent-owned readiness、remote authorization boundaryは維持した。このentryはplan readiness、Task 2 review、Implementation Stage entry、remote actionの完了を宣言しない。

## [2026-08-14] implementation-closeout-candidate | SDD Plan Ownership Alignment

- Actorはrepository maintainer-delegated Task POA-3 knowledge workerである。`knowledge/AGENTS.md`の`Read: allowed`、`Write Boundary: owned`、selected authoring profile `obsidian`を確認し、[[wiki/syntheses/sdd-plan-ownership-alignment|current Plan Stage authority]]、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|agent-authored plan]]、[[wiki/syntheses/sdd-implementation-skill-design|broader current design]]、[[wiki/syntheses/sdd-preimplementation-context-isolation-spec|fresh-worker boundary]]、[[index|active catalog]]をdirect canonical closeout candidateへ同期した。
- POA-1 reviewed intentional RED commitsは`fa2b26c9003a5c525040cbd28bb224b004c0fdbb` / `6f1ca9fb39340c417d5afcb8784244bb69d258a7`、POA-2 reviewed combined-GREEN commitsは`6d8222d64c4a50328e3dd873abdcabb43fdf4be7` / `71889d21343efdcaafe0152ce3eb763d0857b8e5`であり、Task 1 / 2 review後のopen material findingはない。actual integrated rangeのchanged pathは15件で、required task commitsはcurrent branchからreachableである。
- current designとfocused context specificationはPlan StageのHuman / repository approval semanticsを[[wiki/syntheses/sdd-plan-ownership-alignment|Plan Ownership Alignment]]へsupersedeし、Plan Contract Overlay、fresh Plan Author / independent Plan Reviewer、agent-owned Plan Readiness Gate、`ready`-only Implementation entryをcurrent contractとして指す。historical plans、approval logs、implementation evidenceは削除・再解釈していない。
- agent-authored planのapproved spec SHA-256 `1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559`は承認時snapshot identityとして維持した。landed state / provenanceだけを追記したcurrent spec bytesはSHA-256 `a7d09abfda0a9c981c0f9f0150fce8e1209099f8b8b83993ae72aed12a918284`であり、承認済みNorth Star、requirements、acceptance criteria、non-goals、stop conditionsは変更していない。plan本文はruntime result ledgerへ変換していない。
- fresh combined verificationはSDD implementation tests `69/69`、repository script tests `19/19`、LLM Wiki tests `21/21`、skill architecture validation、skill context validation、1 skill / 12 operations / warnings `0`のcontext report、`sdd-implementation` skill-creator quick validationをすべてexit `0`で完了した。durable plan inspectionはrequirements `15/15`、acceptance criteria `14/14`、unique primary owner、3 tasks、acyclic / topological order、I-1〜I-3、combined verification fields、prohibited-body absenceを確認し、knowledge inspectionはspec / plan各1件のcanonical index identity、resolved relations、append-only log prefix、`knowledge/raw/**` unchangedを確認した。`agents/openai.yaml`はpublic contract testとauthoring validationに一致したため変更不要である。
- original checkoutは開始時tupleの`main`、`c370fe14de1641aa5ee30b3fa001f4d857078091`、clean porcelain statusと一致した。Task POA-3 task-scoped reviewと、その後一度だけ行うcanonical final whole-branch reviewはpendingであり、`LOCAL_COMPLETE`を宣言しない。push、PR creation、merge、release、live install / deployment、issue、comment、project変更、その他のremote / privileged / destructive actionは未実施である。

## [2026-08-14] review-correction | SDD Plan Ownership Alignment plan readiness

- Task POA-3 task reviewのImportant findingにより、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical agent-authored plan]]のstaleな`ready-for-agent-review` / review pending表現をcurrent lifecycleへ修正した。fresh independent plan review、blocking finding修復、re-reviewは`.superpowers/reviews/sdd-plan-ownership-alignment/plan-review.md`と`plan-rereview.md`に記録され、最終re-review dispositionはrepository readiness `ready`、decision request `none`、material risk `none`である。
- Planning Controllerがapproved spec bindingとplan pathを確認し、Plan Readiness Gate `ready`をControl Return `status: complete`へmapしてImplementation Stageへentryした事実をdurable planと[[index|active catalog]]へ同期した。これはHuman plan approvalではなく、canonical final whole-branch review、`LOCAL_COMPLETE`、remote action authorizationも宣言しない。
- 同reviewのMinor findingに対し、[[wiki/syntheses/sdd-preimplementation-context-isolation-spec|fresh-worker boundary]]のSkill Structure treeへlanded `references/plan-contract.md`と`prompts/plan-reviewer.md`を追加した。treeは再びcurrent internal resource topologyを表し、新しいuser-facing skillまたはruntime surfaceは追加していない。

## [2026-08-14] provenance-correction | SDD Plan Ownership Alignment plan review

- 直前の`review-correction` entryがplan review / re-reviewのtransient `.superpowers/reviews/...` pathだけをprovenanceとして示した表現をsupersedeする。raw review transcriptsはwikiまたはGitへcommitせず、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]内の`Durable Plan Review Evidence`へ、2026-08-14のreview stage、approved spec path / SHA-256、canonical plan path / baseline binding、initial `issues_found` / `needs_repair`の2 finding、agent repair、final `ready` / decision request `none` / material risk `none`、Control Return `status: complete`、Implementation Stage entry、landed POA-1 / POA-2 commit identitiesを自己完結して記録した。
- transient initial review SHA-256 `0d5ff88616ec9c8cd4496b7e5d8912a4f636f8a6b419b1937867c18069548e34`とre-review SHA-256 `52b6345da5321e220fc47f8aeafd307e75a8d1ae50d057d5763fed349a631822`はintegrity fingerprintとしてのみ保持する。future cloneからtransient fileを読める、またはreview時plan byte digest / review commitが存在するとは主張しない。durable evidenceはcanonical plan内のverdict summaryと本append-only correctionである。
- canonical final whole-branch review、`LOCAL_COMPLETE`、Human plan approval、remote action authorizationは引き続き未宣言である。active catalogのreadiness summaryは既に正しく、index変更は不要である。

## [2026-08-14] final-review-correction | SDD Plan Ownership Alignment semantic contract

- Actor: repository maintainer-delegated final-review fix worker。Target identityは
  [[wiki/syntheses/sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical implementation plan]]、および
  `skills/sdd-implementation` Plan Stage contractである。
- Authority result: `knowledge/AGENTS.md`の`Read: allowed`、`Write Boundary: owned`、Canonical Ownerから委譲された
  correction authority、selected authoring profile `obsidian`を確認し、direct canonical correctionを許可した。
  Human authorityはapproved North Star / Written Specのproduct boundaryに限定したままである。
- Lifecycle effect: 先行eventは削除・変更せず、本eventが不足していたactor / authority / affected-index /
  evidence fieldsを補う。maturity routeはcurrent spec-bound repository readiness `ready`の証拠を必須化し、parallel
  eligibilityはagent / repository-ownedへ是正した。canonical plan、representative fixture、Plan Contract Overlay、
  executable validatorをNorth Star identity、approval-snapshot identity、baseline binding、global constraints、
  observable behavioral interfaceを持つ一つのsemantic schemaへ同期した。
- Affected page identities: 上記spec / plan、`skills/sdd-implementation/SKILL.md`、
  `skills/sdd-implementation/references/plan-contract.md`、representative fixture、focused contract tests。
  Specのtransient research / review pathはclone-stableなdurable evidence summaryとcommitted identitiesへ置換し、raw
  transcriptはcommitしていない。
- Affected index identity: [[index|knowledge/index.md]]のactive canonical spec / plan records。target identity、summary、
  lifecycle stateはcurrent correction後も正しいためindex bytesの変更は不要であり、catalog effectは`unchanged`である。
- Evidence: REDではcanonical plan / fixture schema、current binding、maturity `ready` evidence、parallel ownershipが
  exact contract failureとなった。GREEN後のfocused plan/public contract suitesは46 tests、failure 0、error 0である。
  full combined verification、scoped commit、final-fix reportはこのcorrection後のfresh gateで確定する。remote write、
  live mutation、Human execution-choiceは実施していない。

## [2026-08-14] authority-evidence-correction | SDD Plan Ownership Alignment

- `implementation-closeout-candidate` と直前の `final-review-correction` にある
  `knowledge/AGENTS.md` の `Read: allowed` を確認したという記録をsupersedeする。同fileはread stateを宣言して
  いないため、その表現はauthority evidenceとしてunsupportedであり、本event以降は撤回済みとして扱う。
- `knowledge/AGENTS.md` が実際に宣言するevidenceは、knowledge rootが`knowledge/`であること、Canonical Ownerが
  repository maintainerまたはmaintainer-delegated actorであること、Write Boundaryが`owned`でowner actorだけが
  verified claimを直接更新できること、authoring profileが`obsidian`であることである。今回のHuman-approved
  residual fixはこの明示されたowner/write boundary内のappend-only correctionだけを行い、未宣言のread stateを
  推論しない。
- 先行eventはappend-only historyとして削除・変更しない。本correctionはauthority evidenceだけを修正し、approved
  North Star / Written Spec、agent-owned plan readiness / execution、separate remote authorization、canonical page identity、
  `knowledge/index.md`のactive catalog effectを変更しない。

## [2026-08-14] review-fix | SDD Plan Ownership Alignment residual round 1

- 独立re-reviewのImportant 2件に対し、Plan Binding / Readiness Resultのsingleton fieldをcardinality込みで検証し、
  valid valueの後に`issues_found`または`stale`を重ねるcontradictory duplicateをrejectするcontractへ補強した。
- prospective-body validationはPython docstring後のbody、one-line JavaScript function、one-line shell-if、plain
  `echo ready`をrejectし、`def build_plan(spec): returns a normalized plan in the proposed interface.`のような
  interface proseは`return` token / executable structureを持たないため許可する。
- authority-evidence-correctionは変更していない。Human authorityはapproved North Star / Written Spec、plan readiness /
  executionはagent ownership、remote authorizationはaction-specificな別gateのまま維持した。

## [2026-08-14] review-fix | SDD Plan Ownership Alignment residual round 2

- 独立re-reviewの残るImportant 2件を修正した。singleton section parserは同名sectionを全件収集し、identity、
  `Plan Binding`、`Readiness Result`のsection / fieldがexactly oneかつnon-emptyでないplanをrejectする。second
  `Plan Binding` / `Readiness Result`に`issues_found`、`stale`、`failed`を隠すfirst-section bypassを許さない。
- prospective-body validationはPython docstring後のblank linesを越えたexecutable bodyと、internal semicolonを持つ
  multi-command one-line shell-ifをstructural formでrejectする。既存のinterface prose controlは引き続き許可する。
- approved North Star / Written Spec、agent-owned plan readiness / execution、separate remote authorization、および
  先行authority-evidence-correctionは変更していない。

## [2026-08-14] review-fix | SDD Plan Ownership Alignment residual round 3

- 残るImportant 1件に対し、Python prospective-body detectionのexecutable-statement whitelistを廃止した。
  line-anchored `def` / `async def` candidateとそのindented suiteを抽出し、Python parserが実function bodyとして
  受理するstructureを一律rejectする。
- optional docstring / comment / blank line後の`import json`、`await normalize(spec)`、`self.normalize(spec)`、
  `self.plan = spec`をadversarial regressionへ追加した。`def build_plan(spec): returns ...`はvalid Python bodyでは
  ないためintent-only proseとして引き続き許可する。shell validationは変更していない。
- Human-only Written Spec authority、agent-owned plan readiness / execution、separate remote authorization、既存の
  authority correctionとround 1 / 2 evidenceは変更していない。

## [2026-08-14] ingest | SDD transient artifact boundary amendment

- Actorはrepository maintainer-delegated Spec Synthesis workerであり、Humanが2026-08-14に明示承認した
  `sdd-transient-artifact-boundary-2026-08-14`を、owned write boundary内で
  [[wiki/syntheses/sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]へdirect canonical ingestした。
  original `approval_snapshot_sha256`はamendment前snapshotのidentityとして維持し、新しいbytesをcoverすると
  再解釈していない。approved North Starは変更していない。
- Lifecycle effectは`Confirmed Decisions` 9、`R-16`〜`R-21`、`AC-15`〜`AC-20`、transient handoff boundary、
  failure handling、testing、migration、stop conditionsの追加である。normal SDD handoffはruntime temporary /
  repository外を優先し、repository-local `.superpowers/**`はpre-write ignore coverageを持つconcrete local
  scratchだけに限定する。durable summaryはcanonical spec、reviewed plan、append-only logだけが所有する。
- Git invariantは`.superpowers/**`のGit index / staged-tree / commit / PR final-tree entry zeroである。ignored /
  untracked local scratchとfinal-treeからentryを除くstaged deletionは許可し、tracked / staged-tree entryは
  mechanical repository validationとfocused testsでfailさせる。current evidenceでは`.gitignore`が
  `.superpowers/`をcoverする一方、`approved-residual-fix-report.md`、`final-fix-report.md`、`task-2-report.md`の
  3件がtrackedであり、implementation migrationでlocal copyを必要に応じて保持したままfinal treeから除く。
- Affected page identityはcanonical specと本append-only logである。[[index|knowledge/index.md]]のactive canonical
  identity、status、current Plan Stage authority summaryは引き続き正しく、index effectは`unchanged`である。
  canonical implementation planはこのSpec Synthesisでは更新しておらず、amendmentをconsumeするPlan Stageは
  後続作業である。

## [2026-08-14] policy-clarification | SDD transient artifact boundary review repair

- Actorはrepository maintainer-delegated Spec Revision / knowledge workerである。Human / Canonical Ownerの今回の
  明示承認に基づき、`knowledge/AGENTS.md`のLocal Contractへ`Read: allowed`を追加した。既存のCanonical Owner、
  `Write Boundary: owned`、non-owner draft routing、`raw/` immutable boundaryは変更していない。これにより
  [[wiki/syntheses/sdd-plan-ownership-alignment|canonical spec]]、[[index|active catalog]]、本logへのdirect canonical
  updateはread allowed / owned write / delegated owner authorityを満たす。
- Lifecycle effectはfresh spec reviewのF1 / F2修復である。Human-approved amendmentがResearch、Spec、Plan、
  Implementation、review、repair、integration、final review、knowledge closeoutを含むすべてのSDD stageの
  transient destination / write bindingを統治し、競合するrepository-contained research / report / brief pathを
  supersedeすることを明記した。normal scratch / handoffはtask / session用のboundedなrepository-external temporary
  pathへ置き、repository-local `.superpowers/**`はconcrete operational needとpre-write ignore verificationがある
  場合だけ、ignored / untracked / unstaged / uncommittedで使用できる。
- Git history semanticsを分離した。tracked-report cleanup後のGit index / staging area、candidate commit tree、
  以後のすべてのnew commit tree、PR final treeは`.superpowers/**` entry zeroであり、new commitは再導入できない。
  pre-amendment historical ancestor commitはblobをaudit historyとして保持でき、別途の明示的なdestructive
  authorizationなしにrewriteしない。final-tree removalのstaged deletionと必要なignored local copyは引き続き許可する。
- 直前のingest eventがcatalog effectを`unchanged`とした記録をsupersedeする。canonical identityとstatusは不変だが、
  amendmentが追加した全SDD stageのtransient artifact / Git boundaryはmaterial discovery scopeであるため、
  [[index|knowledge/index.md]]のsummaryとsearch termsへrepository-external handoff、`.superpowers/**`、Git index /
  candidate / new commit / PR final tree、history rewrite prohibition、research / review report / briefを同期した。
  approved North Star、raw source、canonical page identityは変更していない。

## [2026-08-14] plan-authoring | SDD transient artifact amendment follow-up

- Actorはrepository maintainer-delegated fresh Plan Author Workerである。Human-approved
  `sdd-transient-artifact-boundary-2026-08-14`、current upstream `superpowers:writing-plans`、repository
  `Plan Contract Overlay`、current tree / test / Git evidenceをconsumeし、
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|existing canonical implementation plan]]を
  duplicate作成なしでdirect canonical updateした。
- Follow-up sequenceはPOA-4 test-first RED contract、POA-5全SDD-stageのrepository-external transient migrationと
  Git index / candidate / new-tree validator、POA-6のR-21 tracked report 3件のnon-destructive final-tree cleanup、
  POA-7 spec / plan / design / index / append-only log closeout、POA-8 fresh combined verification / canonical
  whole-branch review / separately authorized push updateである。R-16〜R-21とAC-15〜AC-20はexactly one primary
  ownerへ割り当て、dependency、execution、serialized integration、combined verificationを明示した。
- Current evidenceとして`.gitignore`は`.superpowers/`をcoverし、Git indexの`.superpowers/**` entryはR-21の
  3件だけである。cleanupはworking-tree bytesを破壊せずignored / untracked local scratchとして保持でき、
  candidate / cleanup後new commit / PR final treeはentry zeroにする。pre-amendment ancestor commitとblobはaudit
  historyとして保持し、history rewriteを計画・実行しない。
- Durable effectはcanonical plan、[[index|active catalog]]、本append-only eventの同期である。raw worker / review /
  fix report、transcript、duplicate task contentは追加していない。Plan Author self-reviewはamended task graphを
  `ready_for_independent_review`とし、fresh independent Plan Review、implementation、fresh verification、remote
  publicationはこのeventでは未実施である。
- Current executable plan validatorはR-01〜R-15、AC-01〜AC-14、POA-1〜POA-3を固定inventoryとしているため、
  expanded canonical plan checkはamended IDs / tasksに対してintentional REDである。POA-4がtest-first contractを
  更新し、POA-5がrepresentative fixture / validatorをGREENにするまでfollow-up Implementation Stage entryはpending
  とした。このknown agent-repairable gapはHuman decision requestまたはmaterial Written Spec conflictではない。

## [2026-08-14] plan-repair | SDD transient artifact amendment follow-up

- Actorはrepository maintainer-delegated fresh Plan Repair Workerである。fresh independent Plan Reviewの
  `issues_found` / `needs_repair` 2件を、Human-approved Written Specを変更せず
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]内でrepairした。decision requestは
  `none`であり、raw review artifactはrepository外temporary pathに留めた。
- POA-4がshared executable semantic validatorのR-01〜R-21 / AC-01〜AC-20 / POA-1〜POA-8 expansionと
  representative ready-plan fixtureの同時transitionを所有するようfile responsibility、task interface、RED gate、
  I-4 preconditionを同期した。これによりstale fixtureやinventory / coverage / graph / order mismatchは許可された
  RED reasonではなく、I-4はrepository-contained destination、missing validator、missing CI invocationだけを
  declared RED reasonにできる。POA-5からfixture / test変更権限を除き、GREEN contract / runtime / CI
  implementationだけを所有させた。
- current amendmentのformal fieldsを`issues_found`、repository checks `failed`、readiness evidence `stale`、
  `needs_repair`、Control Return `not_returned`、Implementation Stage entry `forbidden`へ修正した。original
  POA-1〜POA-3の`ready` / `complete` / `allowed`はHistorical Durable Plan Review Evidenceだけに隔離し、current
  amendment gateへ流用しない。
- [[index|knowledge/index.md]]はPOA-4 / POA-5 ownership splitとcurrent lifecycle stateを同期した。fresh independent
  re-reviewとsuccessful current repository checksは未実施であり、canonical semantic checkがREDの間はPOA-4を
  dispatchしない。no-history-rewrite、exact coverage / dependency / execution / serialized integration order、
  tracked / staged / candidate / final-tree zero contract、repository-external transient default、prospective-body禁止、
  Human plan approval禁止は変更していない。

## [2026-08-14] plan-repair | SDD transient artifact amendment bootstrap transition

- Actorはrepository maintainer-delegated fresh Plan Repair Workerである。fresh independent Plan Re-reviewの
  circular pre-entry findingを、Human-approved Written Specを変更せず
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]内でround-2 repairした。
  decision requestは`none`であり、repository `.superpowers/**`へ新しいartifactを書いていない。
- governing transitionはamendment前HEAD `f07aebce7bbf854cd64184311d204cf04055fd28`、そのtree / current indexで
  mode / blob / pathまで一致するR-21の3 tracked reports、root `.gitignore` coverage、zero staged delta、POA-4 / POA-5 /
  POA-6 ownershipへsingle-useでbindした。additional / changed / renamed / staged path、baseline drift、ignore欠落、
  owner欠落、retry / reuseはImplementation entry前にfail closedとする。
- pre-entryではcurrent validator / representative fixtureに未実装のR-16〜R-21、AC-15〜AC-20、POA-4〜POA-8
  schema transitionだけをexpected REDとして受理できる。POA-4がexpanded semantic parityとintentional REDを所有し、
  POA-5がmigration / validator / CI GREENを所有する。POA-6 cleanupをpre-entry conditionにせず、I-6 candidate tree、
  I-6以後のnew commit tree、PR final treeの`.superpowers/**` entry zero invariantは維持した。
- [[index|knowledge/index.md]]をsingle-use baselineとround-2 lifecycleへ同期した。fresh independent Plan Re-reviewは
  pendingであり、formal stateは`needs_repair`、Control Return `not_returned`、Implementation Stage entry
  `forbidden`のままである。pre-amendment commit / blobはaudit historyとして保持し、history rewriteを行わない。

## [2026-08-14] plan-readiness | SDD transient artifact amendment follow-up

- Actorはrepository maintainer-delegated fresh Plan Readiness / knowledge finalizerである。round-2 repair後のfresh
  independent Plan Re-reviewは[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]を
  `ready`、repository readiness `ready`、decision request `none`、material risk `none`と判定した。raw review transcriptは
  repository外`/private/tmp`に留めてcommitせず、SHA-256
  `f4fcb520361c7aaf191aa7c547980e3b9c72983f7575b1b90218e841d9a219f6`をintegrity fingerprintとしてだけplanへ
  synthesisした。
- single-use entry baselineは`f07aebce7bbf854cd64184311d204cf04055fd28`である。baseline treeとcurrent indexの
  `.superpowers/**` tracked setは`approved-residual-fix-report.md` blob
  `b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1`、`final-fix-report.md` blob
  `c884197bf566cc93f319f3c2a1b6d2ad1563d10e`、`task-2-report.md` blob
  `da22b7580961fb9a2087ab1eb034fb34000711f8`のexact 3 entryだけで、すべてmode `100644`、pathも一致する。
  global staged deltaと`.superpowers/**` worktree deltaはzero、additional tracked / staged / changed / renamed /
  intent-to-add / unignored pathはなく、root `.gitignore` line 1の`.superpowers/`が3 pathとoptional local scratchを
  `--no-index`でcoverする。既存のignored / untracked local scratchはbaseline setに含めず保持する。
- ownershipはPOA-4のshared validator / representative fixture / amended RED、POA-5のall-stage migration /
  repository validator / CI GREEN、POA-6のexact three-report non-destructive cleanupに分離し、I-4〜I-6で直列化する。
  exceptionが許すのはPOA-4 / POA-5 pre-cleanup treeでexact 3 entryをunchanged継承する一回だけである。POA-6の
  I-6 candidate tree、I-6以後のnew commit tree、PR final treeは`.superpowers/**` entry zeroを維持し、additional /
  changed / renamed / staged / reintroduced entry、baseline drift、retry / reuseはfail closedとする。
- current suiteの81件中80件はpassし、1件の88 findingはformal pending field 6件とapproved amendment schema
  transition 82件に限定された。fresh-ready field substitutionとR-01〜R-21 / AC-01〜AC-20 / POA-1〜POA-8への
  validator inventory expansionではerror zeroになり、他のfailureはなかった。このbounded REDをPOA-4 inputとして
  受理し、canonical formal stateを`independently-reviewed` / `ready`、repository checks `passed`、Control Return
  `complete`へ同期した。single-use exceptionはまだ`available_unconsumed_ready`であり、Controllerのatomic recheck /
  consumption前にImplementation Stageへentryしない。formal finalization後のfresh rerunは81件中80 pass / 1 intentional
  failureで、findingはamended schema transition 82件だけとなった。implementation、POA-6 cleanup、final zero-tree
  verification、`LOCAL_COMPLETE`、remote publicationは未完了である。
- [[index|knowledge/index.md]]のactive plan summaryを同じformal readiness、conditional entry、final-zero boundaryへ
  同期した。Human-approved Written Spec、original approval snapshot identity、historical POA-1〜POA-3 evidence、
  pre-amendment historyは変更していない。

## [2026-08-14] implementation-closeout | SDD transient artifact amendment POA-7

- Actorはrepository maintainer-delegated POA-7 knowledge workerであり、single-root `owned` / `Read: allowed`の
  authorityとObsidian authoring profileを確認した。対象は既存の
  [[wiki/syntheses/sdd-implementation-skill-design|broader SDD design]]、
  [[wiki/syntheses/sdd-preimplementation-context-isolation-spec|focused context-isolation spec]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment|Human-approved alignment spec]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|reviewed canonical plan]]、
  [[index|active catalog]]だけであり、新しいspec、plan、report、ledgerを作成していない。
- POA-5は`c7aced8d7b3975f081ec8bfcd065dcaa57bb2eec`、`91cbd5aec3d062f534937953ee8241f415d8db33`、
  `29dc0de8f5f721d5004e5dac253ae04a36899aad`でall-stage repository-external handoff、local scratch
  reason / ignore gate、Git surface validator、CI integrationをGREENにし、independent scoped re-reviewは`ready`だった。
  POA-6 `7b4a8e6e0951e2ddd3c6020a10e00a6afe604b60`はR-21 exact three reportsとmigration markerを
  cleanup treeから除き、`74eb79a3fbb0da2d6521129cf83976a366877af4`はhistorical migration fixtureをcleanup前
  introduction commitへanchorした。cleanup / correctionのscoped re-reviewも`ready`だった。
- Actual Git evidenceではcurrent index / HEAD treeの`.superpowers/**` entryはzeroである。R-21の3 local copiesは
  root `.gitignore` line 1のcoverage下でignored / untrackedのまま存在し、contentをdestructive deleteしていない。
  migration baseline `f07aebce7bbf854cd64184311d204cf04055fd28`はcurrent ancestryに残り、ancestor commit / blobの
  history rewrite、replacement、force publicationを行っていない。
- Fresh closeout validationはSDD focused suite `93/93`、transient validator regression `22/22`、actual candidate
  tree、post-cleanup commits `7b4a8e6` / `74eb79a`、HEAD final treeに対するrepository validator passである。
  Raw worker / reviewer report、transcript、test outputはrepository外temporary evidenceのまま、wikiまたは
  `.superpowers/**`のtracked surfaceへcopyしていない。
- Durable lifecycle effectとしてbroader二仕様の競合するrepository-contained handoff destinationをalignment specへ
  supersedeし、planをPOA-1〜POA-6 reviewed / landed、POA-7 closeout task-review candidate、POA-8 pendingへ更新し、
  active catalogを同期した。POA-7 independent task reviewとPOA-8のfresh combined verification、canonical
  whole-branch review、authorized remote branch updateは未実施であり、`LOCAL_COMPLETE`、publication、merge、
  release、live installを宣言しない。

## [2026-08-14] review-fix | SDD transient artifact POA-7 lifecycle

- POA-7 independent reviewのImportant 2件を受け、[[wiki/syntheses/sdd-implementation-skill-design|broader SDD design]]の
  Migration / Related Pagesを修正した。alignment specがPlan Stageのauthority semanticsに加え、Researchから
  knowledge closeoutまでのすべてのnormal SDD stageで競合するrepository-contained transient handoff destination /
  write bindingをsupersedeすることを明記し、Superpowers-firstのbroader lifecycle、fresh worker isolation、trusted
  planning worktree内のsource code / durable knowledge write boundaryはcurrentのまま維持した。
- [[wiki/syntheses/sdd-plan-ownership-alignment|canonical spec]]のRemaining lifecycleと
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]のPlan Binding / Readiness Resultを、
  POA-7 independent task review pending、Implementation Stage active、そのreview完了後にだけPOA-8へ進む順序へ同期した。
  `Implementation Stage execution: completed`と`Remaining lifecycleはPOA-8だけ`という先行closeout wordingを
  本eventがsupersedeする。
- [[index|active catalog]]は既にPOA-7 independent task review pendingとPOA-8後続順序を正しく示すため変更していない。
  このfixはまだ独立re-review前であり、POA-7 review completion、POA-8 entry、`LOCAL_COMPLETE`、publicationを
  宣言しない。raw review artifactまたは`.superpowers/**`へのwriteは追加していない。

## [2026-08-14] review-disposition | SDD transient artifact POA-7 ready

- Actorはrepository maintainer-delegated POA-7 review-disposition knowledge workerであり、single-root `owned` /
  `Read: allowed` authorityとObsidian authoring profileの下で、fresh scoped re-reviewのdurable verdictだけを既存
  canonical identitiesへ同期した。対象は[[wiki/syntheses/sdd-implementation-skill-design|broader SDD design]]、
  [[wiki/syntheses/sdd-preimplementation-context-isolation-spec|focused context-isolation spec]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment|alignment spec]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]、[[index|active catalog]]である。
- Fresh scoped re-reviewはPOA-7 lifecycle correction commit
  `664dbd15923d7cf395095d810038125a10b727f8`を`ready`とし、prior Important 2件の解消と新規Critical /
  Importantなしを確認した。fresh supporting evidenceはSDD `93/93`、llm-wiki `21/21`、transient repository
  validator passである。raw review report、transcript、test outputはdurable surfaceへcopyしていない。
- Lifecycle dispositionをPOA-1〜POA-7 reviewed / landed、remaining POA-8へ更新した。POA-8 fresh combined
  verification、canonical whole-branch review、authorized remote branch updateはpendingであり、`LOCAL_COMPLETE`、
  publication、merge、release、live installを宣言しない。新しいartifactや`.superpowers/**` writeは追加していない。

## [2026-08-14] evidence-correction | SDD POA-8 responsibility map and CI history gate

- Actorはrepository maintainer-delegated durable-evidence correction workerであり、single-root `owned` /
  `Read: allowed` authorityの下で、[[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]の
  correction timelineだけを追記した。commit `bbfd06eecf2fec0e45697257b3edf545fecdb4b6`は重複していた
  `prompts/plan-reviewer.md` responsibility-map rowを一件へ統合し、surviving rowにPOA-2 `Create`とPOA-5
  `modify`のownershipをともに保持した。
- 同commitはCIがcleanup boundary以後の全commit treeをtransient-artifact validatorへ渡すhistory gateと、その
  regressionを実装した。scoped Spec-axis re-reviewはcanonical plan correctionを`READY`とした。
- canonical identityとcatalog summaryは変わらないため[[index|knowledge/index.md]]へのeffectはnoneである。final
  Standards dispositionとauthorized pushはpendingであり、`LOCAL_COMPLETE`またはpublicationを宣言しない。

## [2026-08-14] local-closeout | SDD plan ownership alignment POA-8

- Actorはrepository maintainer-delegated final local-closeout knowledge workerであり、single-root `owned` /
  `Read: allowed` authorityとObsidian authoring profileの下で、既存のbroader design、focused context spec、
  [[wiki/syntheses/sdd-plan-ownership-alignment|alignment spec]]、
  [[wiki/syntheses/sdd-plan-ownership-alignment-implementation-plan|canonical plan]]、[[index|active catalog]]だけを
  `LOCAL_COMPLETE` stateへ同期した。新しいspec、plan、report、ledgerは作成していない。
- evidence tip `e18088893737099d45e446e06a476c68c79ea25f`のfresh combined resultsはSDD `93/93`、
  scripts `46/46`、llm-wiki `21/21`、decide-in-order `7/7`、task-management `11/11`である。skill architecture /
  context / warning-free report (`warnings: []`) / skill-creator / transient-artifact / diff checksもpassした。candidate /
  final treeの`.superpowers/**` entryはzero、3 local copiesはignored / untracked、ancestor historyはrewriteしていない。
- fixed point `c370fe14de1641aa5ee30b3fa001f4d857078091`からのcanonical whole-branch reviewは、Spec Importantの
  CI intermediate-commit detection gapとStandards Minorのduplicate responsibility rowを検出した。bounded fix
  `bbfd06eecf2fec0e45697257b3edf545fecdb4b6`が両方を修正してSpec scoped re-reviewは`READY`となり、
  append-only evidence correction `e18088893737099d45e446e06a476c68c79ea25f`が残るStandards log findingを
  解消してfinal Standards verdictも`READY`となった。
- POA-1〜POA-8 local workはcompleteで、current dispositionは`LOCAL_COMPLETE`である。authorized non-force remote
  branch updateはpending / unpublishedであり、push、merge、release、live installを実施または承認済みと扱わない。

## [2026-08-08] written-spec-review-candidate | llm-wiki Authoring Discovery Diagnostics

- Humanは、Authoring Profileをsemantic selectorとしskill IDとのname mismatchだけをfailureにしないこと、discovery起因の`BLOCKED`にprofile、Compatibility Requirement、candidateまたはdiscovery unavailable、exact causeと具体的理由を要求するshared understandingを承認した。
- local-contract mutationの提案前にcurrent local contract、current approved spec、current checkoutを比較し、historical spec、old memory、append-only history、siblingまたはolder worktreeをcurrent ruleのoverride根拠にしない。
- current repository evidenceである`obsidian`からdiscovered `obsidian-markdown`へのmappingとwikilink behaviorはrepository-specificに保ち、generic portable selectorへhardcodeしない。
- [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|canonical Written Spec]]、[[index|durable catalog]]、append-only logを文書レビュー候補へ同期した。scopeはdocs-onlyで、validator、test、runtime resolver、code、新runtime metadata、visual artifactを含まない。Humanの更新Written Spec review、Plan Stage、production contract変更、remote writeは未実施である。

## [2026-08-08] correction | llm-wiki Authoring Discovery Diagnostics Written Spec Candidate

- fresh independent spec reviewの指摘に従い、`discovery unavailable`を`missing`、`ambiguous`、`incompatible`、`unreadable`のcandidate outcomeとは別のdiagnostic conditionとして明確化した。result statusは`BLOCKED`のまま維持し、candidate setを`unobserved`、exact causeをdiscovery実行不能の具体的理由として報告し、candidate outcomeを推論しない。
- canonical specにRetained baselineの時間的scopeを追加し、2026-07-30のpre-migration problem、decision、migration contract、implementation historyがhistorical baselineであり、2026-08-08のcurrent contract interpretationをoverrideしないことを明記した。
- [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|Written Spec candidate]]と[[index|durable catalog]]を同じcorrectionへ同期した。docs-only scope、Open Decisionsなし、Human Written Spec review pending、production contractとremote stateの未変更は維持する。

## [2026-08-08] spec-gate-approved | llm-wiki Authoring Discovery Diagnostics

- Humanは、commit `fc398b54492ccfc3f4ec14161d84bd7a2546f058`に記録されたrecurrence-prevention deltaを、[[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]]のfocused revisionとしてWritten Spec承認した。focused revisionはHuman-approved / currentである。
- [[index|durable catalog]]を同じ承認状態へ同期した。既承認のauthoring責務分離decisionとhistorical baselineは維持する。
- Plan Stage、production contract変更、remote writeはこのWritten Spec承認に含まれず未実施である。

## [2026-08-08] implementation-plan-review-candidate | llm-wiki Authoring Discovery Diagnostics

- [[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|llm-wiki Authoring Discovery Diagnostics 実装計画]]を、approval commit `f3126d8ec2f740be228640d22215f9d1f1a52175`のHuman-approved focused Written Specにbindingしたrepository review candidateとして作成した。
- 計画は`skills/llm-wiki/SKILL.md`と`skills/llm-wiki/references/core.md`だけをproduction contract write setとし、focused semantic selector、evidence-bearing `BLOCKED`、current-state precedenceを実装する。durable closeoutはcurrent spec、本plan、[[index|durable catalog]]、append-only logだけに限定する。
- tests、validators、runtime resolver、code、sidecar、runtime metadata、context-contract operation read-sets、repository-specific mappingのportable hardcodeはscope外である。HumanのPlan Gate承認、implementation、remote writeは未実施である。

## [2026-08-08] implementation-plan-review-correction | llm-wiki Authoring Discovery Diagnostics

- independent plan reviewのImportant findingに従い、[[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|implementation plan candidate]]のTask 1へ`writing-skills` / TDDのexplicit RED-GREEN contractを追加した。
- pre-editは同一pressure scenarioをno-guidance controlとcurrent unmodified llm-wiki contractで各fresh contextに適用し、post-editはchanged `SKILL.md` / `core.md`を明示的に渡した別fresh contextで再実行する。semantic `obsidian` profile、differently named `obsidian-markdown`、current wikilink contract、2 fields missingとrelative Markdown link復元へのpressure、discovery unavailable branchを同じmanual scorecardで比較する。
- prompt、verbatim result、manual scorecardはplan-owned gitignored SDD workspaceだけに置く。repository test / validator、runtime resolver、code、sidecar、runtime metadata、context-contract operation read-set、production contractはこのplan correctionで変更していない。HumanのPlan Gate承認、implementation、remote writeは引き続き未実施である。

## [2026-08-08] plan-gate-approved | llm-wiki Authoring Discovery Diagnostics

- Humanは明示message `承認`により、[[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|llm-wiki Authoring Discovery Diagnostics 実装計画]]をrepository-required Plan Gateとして承認した。本計画はHuman-approved / currentである。
- approved plan candidate commit `0b99c98872661c84a789580d6bae78dad5691ba3`を、approved focused Written Spec commit `f3126d8ec2f740be228640d22215f9d1f1a52175`へbindingし、[[index|durable catalog]]を同じ承認状態へ同期した。
- この承認checkpointはplan、catalog、append-only logだけを更新する。production contract、test、validator、runtime resolver、code、runtime metadataは変更せず、implementation、task review、durable implementation closeout、final whole-branch review、remote writeは未実施である。

## [2026-08-08] implementation-closeout-candidate | llm-wiki Authoring Discovery Diagnostics

- reviewed production commit `f40a164e4c4fac1988b1ff98929fc829713fc572`により、`skills/llm-wiki/SKILL.md`と`skills/llm-wiki/references/core.md`だけのdocs-only contractがlandedした。semantic selector、evidence-bearing `BLOCKED`、current-state precedenceを確認し、pre-edit REDを観測してpost-edit GREENを満たした。prompt / result本文は記録せず、ignored execution evidenceのままとする。
- focused current [[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|Written Spec]]、[[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|implementation plan]]、[[index|durable catalog]]をimplementation closeout candidateへ同期した。fresh verification resultsはcommit前に利用可能であり、final whole-branch reviewはpendingである。`knowledge/raw/**`はuntouchedで、remote writeは行っていない。

## [2026-08-08] final-review-evidence-exception | llm-wiki Authoring Discovery Diagnostics

- このeventは、直前の`implementation-closeout-candidate` eventにあるtemporalな「pre-edit RED」evidence claimだけをcorrect / supersedeし、その他のhistoryをrewriteしない。original before-edit current-control evidenceはprompt embedding defectによりinvalidatedされた。production commit `f40a164e4c4fac1988b1ff98929fc829713fc572`後、byte-exactな`ac67fde` sourceを使う5回のfresh runがREDを再現したが、これはpost-hoc old-contract replay evidenceである。5回のpost-edit runはGREENである。
- Humanは2026-08-08に、このchronologyを一回限りのevidence exceptionとして明示承認した。このexceptionは一般のtemporal pre-edit RED gateを満たすものでも弱めるものでもなく、future skill workのoriginal gateを変更しない。two-file production contract（`skills/llm-wiki/SKILL.md`、`skills/llm-wiki/references/core.md`）とfour durable closeout filesからなるsix-file total scopeは不変であり、[[wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec|Written Spec]]、[[wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan|implementation plan]]、[[index|durable catalog]]を訂正へ同期した。
- scoped final-fix re-reviewはpendingである。`knowledge/raw/**`はuntouchedで、remote writeは行っていない。

## [2026-08-14] plan-authoring | global skill fallback and simple implementation

- Actor: repository maintainer-delegated Plan Author Worker。Human-approved requirementsとbaseline `c370fe14de1641aa5ee30b3fa001f4d857078091`に基づき、[[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|Global Skill Fallback And Simple Implementation Plan]]をactive canonical proposed implementation planとして作成した。
- Lifecycle effect: active runtime discoveryの後にruntime-exposed global rootsとaccess可能な`~/.agents/skills`を確認するSDD fallback、および独立`keep-implementation-simple` Skillを、2 implementation taskのTDD planへ固定した。plan自体のHuman approvalとImplementation Stageは未実施である。
- Scope boundary: resolver、classifier、provenance/evidence model、dependency closure、trace、cache、dedup、cycle model、test-only runtime、schema、protocol、live install、remote write、push、PRはplan対象外とした。
- Index effect: proposed planをreader-facing discovery entryとして1件追加した。raw sourceは変更していない。

## [2026-08-14] plan-review-correction | global skill fallback and simple implementation

- Independent reviewに従い、[[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|plan]]を2 task / persistent prose assertion / 14-run pressure ritualから、2つの`SKILL.md`だけを変更するone-task planへ縮小した。
- current conversationとrejected branchをobserved REDとして扱い、GREENは単純化とglobal fallbackのfresh-agent scenario各1件、既存focused SDD tests、architecture validator、changed Skillsのskill-creator validator、diff checkだけとした。
- 新しいdecision gate、test-only runtime/helper/resolver/classifier/schema/protocol、追加review gate、別closeout artifactは作成しない。plan approval、implementation、live install、remote writeは未実施である。

## [2026-08-14] plan-gate-approved | global skill fallback and simple implementation

- Humanはcorrected minimal scopeのlocal implementationを明示承認し、independent repository plan reviewはmaterial requirement/scope defectなしと判定した。残るobservationはmandatory repository closeoutに関するもので、追加review gateではないとadjudicateされた。
- [[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|plan]]を`accepted` / `approved-for-local-implementation`へ更新し、既存index entryを同じlifecycle stateへ同期した。plan contentとone-task scopeは変更していない。
- live install、remote write、push、PR、merge、releaseは承認・実施していない。

## [2026-08-14] implementation-closeout-candidate | global skill fallback and simple implementation

- [[wiki/syntheses/global-skill-fallback-and-simple-implementation-plan|canonical plan]]のlocal implementationは`e40fa348db056be005a254c1e5a84b51d7447629`（`feat: keep skill discovery fallback simple`）で完了し、approved task reviewはopen material findingなしである。planと[[index|durable catalog]]を`implemented-task-reviewed-pending-final-review`へ同期した。
- fresh-agent behavior GREENは2件ともPASSである。`keep-implementation-simple`はexisting configuration owner/surfaceを選び、unmapped resolver/classifier/cache/provenance traceを除外し、review blockerをrequirement gap・repository rule violation・observable regression・concrete current riskに限定した。SDD Dependency Preflightはreadableな`~/.agents/skills/llm-wiki/SKILL.md`をread/useして継続し、complete no-matchだけをmissing、incomplete discovery/candidate readをconcreteな`BLOCKED: dependency preflight failed`として扱った。
- focused validationはSDD unittest 49件、`scripts/validate_skill_architecture.py --all`、両Skillの`quick_validate.py`、`git diff --check`がすべてGREENである。`c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`のfinal diff checkとfresh final whole-branch reviewは未実施のままであり、`LOCAL_COMPLETE`は宣言しない。push、PR、merge、release、remote write、live installは未実施である。
