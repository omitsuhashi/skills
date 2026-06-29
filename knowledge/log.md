# ログ

append-only で使います。すべての entry は予測しやすい header で始めます。

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
