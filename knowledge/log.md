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

## [2026-07-21] spec | Task-management write / preflight Interface and GitHub Projects Adapter

- current `plugins/task-management` v0.3.0、97 focused tests、manifest / runtime registration、read route v1、Hermes v0.19.0 の public plugin dispatch seamをevidence-firstで監査した
- official GitHub MCP Server main `9d130049e9074772c2afbbd5e904725d240443ad` のProjects実装を確認し、Issue create、Project add、field update、read-backはadapter orchestrationが必要で、Project-native draft item createはcurrent surfaceにないと確定した
- `task-management` public interface v2、unified route v2 clean break、approval preview / digest、`approved | confidence_authorized` receipt、typed preflight / result normalizationをSpec Gate候補として追加した
- 確証がないtaskは外部作成前に人間へpreviewを提示し、十分な確証と機械的eligibilityがある場合だけ`confidence_authorized`を使う運用を固定した
- GitHub固有処理をseparate `plugins/task-adapter-github-projects/` distributionへ隔離し、初期createをlinked Issue onlyとした。draft item / content policyは追加しない
- file-level TDD plan、shared contract/versioning、test strategy、route migration、Companies handoff contract、別Live Activation Gateを文書化した
- Spec Gate前のためlocal issue ledger追加、実装、commit、push、PR、live Hermes / MCP / credential / GitHub Project / Issue変更は実施していない

## [2026-07-21] gate | Task-management write / preflight Spec Gate

- ユーザーがEpic `portfolio-os-task-backend-plugin-skill` のwrite / preflight Interface、separate GitHub Projects Adapter、file-level implementation planをSpec Gateとして承認した
- `codex/portfolio-os-task-backend-plugin-skill/epic-base` branchと`/private/tmp/skills-portfolio-os-task-backend-plugin-skill/epic-base` worktreeを作成し、承認済みplanning artifactsをこのphase branchへ移した
- 初期createはlinked Issue only、確証がないtaskはwrite前にhuman confirmation、十分な確証とeligibilityがある場合だけ`confidence_authorized`とする判断を維持した
- 次phaseは既存canonical ledgerへのPOTASK follow-up issue分解とIssue Gateであり、実装、push、PR、live activation、GitHub / MCP / credential writeは未実施

## [2026-07-21] issue-draft | Task-management write / preflight follow-up issues

- 既存Epic `portfolio-os-task-backend-plugin-skill` のcanonical ledgerへPOTASK-012からPOTASK-019をIssue Gate draftとして追加した
- shared Adapter contract v2を起点に、unified route / approval binding / public facadeと、separate GitHub Adapter scaffold / preflight / applyをdependency-awareに分解し、integration verificationへ収束させた
- POTASK-012だけを`実行可能`、未完了blockerを持つPOTASK-013からPOTASK-019を`ブロック中`とし、blocked issueのphysical worktreeは作らない
- 各issueにWrite Scope、Acceptance Criteria、Non-goals、Verificationを固定した。GitHub issue mirror、実装、push、PR、live activationは未実施

## [2026-07-21] gate | Task-management write / preflight Issue Gate

- ユーザーがPOTASK-012からPOTASK-019の粒度、blocker graph、dependency order、実行状態、Acceptance CriteriaをIssue Gateとして承認した
- POTASK-012からPOTASK-019の`レビュー状態`を`承認済み`へ更新し、POTASK-012だけを`実行可能`、後続7件を`ブロック中`に維持した
- local-first / local-only policyを承認し、GitHub issue mirror、push、PR、merge、live activationをexecution scopeへ追加していない
- 次phaseはnormalized execution packet、capability preflight、Execution Plan Gate commitであり、implementationはfresh `issue-implementation-loop` coordinatorへ委譲する

## [2026-07-21] gate-amendment | Task-management integration work items

- Execution Envelopeのsingle-base policyに合わせ、ユーザーがPOTASK-015 / POTASK-019のintegration ownership amendmentを承認した
- POTASK-015はPOTASK-013 headをbaseにPOTASK-014 headを統合し、POTASK-019はPOTASK-018 headをbaseにPOTASK-015 headを統合する
- Issue ID、機能scope、acceptance behavior、DAG、local-only remote policyは変更せず、integration responsibilityと必要なwrite scopeだけを追加した

## [2026-07-21] gate | Task-management write / preflight Execution Plan Gate

- POTASK-012からPOTASK-019のnormalized input packetとExecution Envelope v3を作成し、packet / envelope validatorをerror 0で通過した
- capability preflightでgit repository、TDD skill、independent review skillを確認した。parallel availabilityはplatform依存とし、serial fallbackもworker context内だけに限定した
- Git reconciliationでEpic Baseのactive registrationと8 issue branch/worktree予約を確認し、collision 0件、初期実行可能issueをPOTASK-012と確定した
- `worker_context_required=true`、`coordinator_may_implement=false`、最大2 review cycle、POTASK-015 / 019だけがmulti-head integrationを所有するExecution Planを固定した
- remote policyは`local_only`。GitHub Issue、push、PR、merge、live Hermes / MCP / credential / Project / Issue変更は未承認・未実施のままfresh execution coordinatorへ引き継ぐ

## [2026-07-21] gate-amendment | POTASK-012 regression guard scope

- 初回worker dispatchは、承認済み`contracts.py` / `safety.py`追加と、既存exact implementation-file guard 2件のPOTASK-012 Write Scope外編集が両立しないことを編集前に検知してfail closedした
- ユーザー承認により`plugins/task-management/tests/test_adapter_dispatch.py`と`plugins/task-management/tests/test_github_mcp_route.py`だけをPOTASK-012 Write Scopeへ追加した
- input packetとExecution Envelope revision 2を同期した。機能scope、acceptance behavior、DAG、remote / live policyは変更していない

## [2026-07-22] human-decision | POTASK-012 exceptional review cycle

- POTASK-012 workerは`bb66aff`とreview fix `5f4c0dc`を作成し、write contracts 26 / 26、task-management full suite 123 / 123、read regression各18 / 18、`git diff --check`を通過した
- 独立review cycle 2 / 2で、scheme-relative / colon-form URL-shaped `destination_ref` bypassと、root plugin entrypoint / direct provider SDK / separate-adapter importのguard scan漏れがImportant `intent_gap`として残った
- max review cycle到達後、runtime human request `hr-potask-012-review-exception-001`でPOTASK-012と全descendantを停止し、blockerをreleaseしなかった
- ユーザーは残存2件だけをTDD修正して独立reviewする例外cycle 1回を承認した。新規または残存Critical / Important findingがあれば再停止し、risk acceptanceを自動推論しない
- remote policyは`local_only`のまま。GitHub Issue、push、PR、merge、live Hermes / MCP / credential / Project / Issue変更は未実施

## [2026-07-22] review-stop | POTASK-012 exceptional review

- 人間承認済み例外fix `c47a9c7`はURL-shaped destination bypassとroot / provider import scan漏れをTDD修正し、write contracts 26 / 26、task-management full suite 127 / 127、read regression各18 / 18、`git diff --check`を通過した
- 独立exception reviewは、両guardの`r"\b(?:api\.github\.com|/graphql)\b"`がquoted / string-start `/graphql`を検出できないImportant `intent_gap`を1件再現した。他のscope内findingは検出されなかった
- 承認済みexception後にImportantが残ったためPOTASK-012を`WAITING_HUMAN`へ戻し、POTASK-013、POTASK-014、POTASK-016をreleaseしなかった
- human request `hr-potask-012-post-exception-decision-001` は、regex boundaryと代表probeだけのmicro-fix + independent review 1回、既知riskの明示accept、実行停止のいずれかを要求する
- remote policyは`local_only`のまま。追加fix、GitHub Issue、push、PR、merge、live Hermes / MCP / credential / Project / Issue変更は未実施

## [2026-07-22] human-decision | POTASK-012 final micro-fix review

- ユーザーはhuman request `hr-potask-012-post-exception-decision-001`に対し、残存したquoted / string-start `/graphql` guard漏れだけを対象にする最終micro-fixと独立review 1回を承認した
- write scopeは`plugins/task-management/tests/test_adapter_dispatch.py`と`plugins/task-management/tests/test_github_mcp_route.py`の2ファイルに限定し、無効な先頭word-boundaryの修正と代表的`endpoint = "/graphql"` failing probe追加だけを許可する
- 既存のclient / API / GraphQL / `gh` / provider禁止を維持し、最終review後もCritical / Important findingが残る場合は自動fixやrisk acceptanceを行わず再停止する
- POTASK-012のblockerは最終review approvalまで維持する。remote policyは`local_only`のままで、GitHub Issue、push、PR、merge、live Hermes / MCP / credential / Project / Issue変更は未実施

## [2026-07-22] implementation-review | POTASK-012 local PR_READY

- 最終micro-fix `d539ebd`は2つのguard testだけを変更し、`endpoint = "/graphql"` probeを各helperへ追加してTDD RED 23 tests / 2 expected failuresからGREEN 23 / 23へ進めた
- write contracts 26 / 26、task-management full suite 127 / 127、read adapter / routes各18 / 18、full / micro rangeの`git diff --check`を通過した
- 独立reviewはfull range `cc1d428..d539ebd`とmicro range `c47a9c7..d539ebd`を`approved`とし、Critical / Important findingは0件だった
- POTASK-012をlocal `PR_READY`へ移し、`artifact_ready`でPOTASK-013、POTASK-014、POTASK-016をreleaseした。remote / live writeは未実施

## [2026-07-22] implementation-review | POTASK-014 and POTASK-016 local PR_READY

- POTASK-014 `a5bcf11`はcanonical approval digest、confidence-aware approval policy、preflightとの状態分離を実装し、approval / preflight各5 / 5、task-management full 137 / 137を通過した。independent review cycle 1は`approved`
- POTASK-016 `bc73c99`はseparate GitHub Projects Adapter scaffold、fixed MCP allowlist、opaque mapping、host attestation、dual-host manifestsを実装し、adapter tests 15 / 15、plugin / dual-host validatorsを通過した。independent review cycle 1は`approved`
- 両issueをlocal `PR_READY` / `artifact_ready`へ移した。POTASK-014 fixtureのseparate Adapter copy同期はPOTASK-019 integration scopeが所有する
- GitHub Issue、push、PR、merge、live install / MCP / credential / GitHub mutationは未実施

## [2026-07-22] human-wait | POTASK-013 regression guard scope

- POTASK-013 workerはapproved scope内でroute 21 / 21、read adapter 18 / 18、diff-checkを通過したが、route v2 config更新がscope外の既存`plugins/task-management/tests/test_backend_routing.py` route v1 exact assertionsを回帰させることを検出した
- human request `hr-potask-013-regression-guard-scope-001`を開き、上記1 test fileだけをWrite Scope / read pathsへ追加する承認を求めた。機能scope、DAG、remote / live policyは変更しない
- workerの未commit変更を保持し、POTASK-013を`WAITING_HUMAN`、POTASK-015をblockedに維持した

## [2026-07-22] gate-amendment | POTASK-013 regression guard scope approved

- ユーザーがhuman request `hr-potask-013-regression-guard-scope-001`の推奨案を承認し、`plugins/task-management/tests/test_backend_routing.py`だけをPOTASK-013 Write Scope / read pathsへ追加した
- assertionsをlegacy route v1からapproved route v2 exampleへ同期する。機能scope、Acceptance Criteria、DAG、remote / live policyは変更しない
- normalized input packetとschema v3 Execution Envelope revision 3を同期し、POTASK-015 integration scopeはPOTASK-013のapproved scopeを継承する
- 保存済み7-file uncommitted diffを破棄せず、source hashesを更新したbounded worker packetから元workerを再開する

## [2026-07-22] implementation-review | POTASK-017 local PR_READY

- initial `eb570e4`のcycle 1 reviewは、official compact field typeのlowercase mismatchと、public Hermes dispatch JSON envelopeをtestsが迂回する2件をCritical `intent_gap`として検出した
- fix `b2494e5`はpinned official GitHub MCP sourceとlive installed Hermes public seamを根拠にTDD修正し、preflight 7 / 7、query 5 / 5、full 27 / 27、plugin / dual-host validatorsを通過した
- cycle 2 reviewは`approved`、finding 0件。POTASK-017をlocal `PR_READY` / `artifact_ready`へ移し、POTASK-018をreleaseした

## [2026-07-22] implementation-review | POTASK-018 local PR_READY

- implementation `d780f8c`はofficial MCP operation shapes/orderでlinked Issue create、Project add、ordered 9 field update、read-back、update / comment / report、safe partial resultを実装した
- cycle 1 reviewはfirst-write explicit-no-write retryabilityがfield-only update / comment / reportで失われ、stable `rate_limited` spellingがno-write detectorから漏れるImportant `intent_gap`を1件検出した
- fix `cc61018`は5 first-write probesだけをfailed / provider failure / retryableにし、later-write / unknown outcomeはpartial / nonretryableを維持した。partial 6 / 6、full 39 / 39、Hermes fake-MCP smoke、plugin / dual-host validatorsを通過した
- cycle 2 reviewはfull range `b2494e5..cc61018`とfix delta `d780f8c..cc61018`を`approved`とし、finding 0件。POTASK-018をlocal `PR_READY` / `artifact_ready`へ移した
- runtime next actionsはrunnable / reviewable / fixableなし。POTASK-013だけがhuman wait、POTASK-015はPOTASK-013、POTASK-019はPOTASK-015を待つ。remote / live writeは未実施

## [2026-07-22] implementation-review | POTASK-013 and POTASK-015 local PR_READY

- POTASK-013 `badc466`はhuman-approved regression guard scopeを含むroute v2 clean breakを完了し、focused 21 / 18 / 8、full 130、smoke / validatorsを通過した。independent review cycle 1は`approved`
- POTASK-015 integration commit `82b3246`はreviewed `badc466`と`a5bcf11`をexact parentsに持ち、implementation `f5fc50e`はapproval-bound preflight/apply facade、bounded normalization、v0.4.0 read/write toolsets、fake write smokeを実装した
- facade 7、normalization 9、manifest 11、full 156、read / write smokes、plugin / dual-host validatorsを通過し、independent review cycle 1は`approved`、finding 0件
- POTASK-013 / 015をlocal `PR_READY` / `artifact_ready`へ移し、POTASK-019の全blockerを解消した。remote / live writeは未実施

## [2026-07-22] gate-amendment | POTASK-019 worker-owned completion evidence

- ユーザー指示により、POTASK-019 final integration workerがplugin docs / manifests / SKILL / references / examples / testsに加え、canonical spec / ledger / index / logのcompletion evidenceも所有する
- normalized input packetとschema v3 Execution Envelope revision 4へ4つのknowledge pathsを追加した。機能scope、DAG、base policy、local-only remote / live policyは変更しない
- POTASK-019はreviewed POTASK-018 `cc61018`をbaseにし、reviewed POTASK-015 `f5fc50e`をexplicit integration commitで取り込んでからfinal TDD / docs / full verificationへ進む。coordinatorは実装しない

## [2026-07-22] human-wait | POTASK-019 normative status scope

- POTASK-019 integration commit `3c8ba06`はexact parents `cc61018` + `f5fc50e`、conflict 0件、両head ancestry PASS。fixture exact-copyとpublic fake end-to-end 6 / 6をTDDで進め、task-management 156 / 156、adapter 45 / 45、3 smokesをGREENにした
- unique Companies Interface v2 canonical `task-management-write-preflight-interface-spec.md`とGitHub Adapter specのstatus/current boundaryが2026-07-21時点の未実装記述を残すが、Execution Envelope revision 4では両fileはread-onlyである
- human request `hr-potask-019-normative-status-scope-001`は上記2 filesだけをwrite scopeへ追加し、実装完了 / local fake verification完了 / remote・live未実施のstatusへ同期する承認を求める。normative design、DAG、plugin scope、remote / live policyは変更しない
- POTASK-019を`WAITING_HUMAN`へ移し、既許可scopeのworking changesを保持した。final commit / report / reviewはdecisionまで実施しない
