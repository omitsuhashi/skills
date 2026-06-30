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
