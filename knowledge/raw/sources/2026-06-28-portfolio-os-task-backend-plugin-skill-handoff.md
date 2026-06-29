# Portfolio OS タスクバックエンドプラグイン / スキル実装ハンドオフ

## 目的

この資料は、共有タスクバックエンドプラグインと再利用可能な task-management スキル層を設計・実装するための別セッション向けハンドオフである。明示的に依頼されない限り、そのセッションでは Portfolio OS の profile-specific 設計を続けない。現在の元セッションは Portfolio OS profile 設計と local capture / profile integration を続ける。

## リポジトリと前提

- 主対象 repo: `/Users/omitsuhashi/repos/the3-inc/companies`
- Portfolio OS は core catalog である。repo root を Hermes profile として install しない。
- durable repo documentation は `knowledge/` 配下に置く。
- wiki/bootstrap/ingest/query/lint 作業では、先に `knowledge/AGENTS.md` を読む。
- public user-facing surface は high-level に保つ。通常 UX で low-level script を前面に出さない。
- plugin ecosystem では Claude Code、Anthropic、その他単一 provider を前提にしない。GitHub Projects は最初の task backend implementation であり、恒久的な backend architecture ではない。

## 現在の product decision

最初の task backend は GitHub Projects とする。GitHub Projects が task state の source of truth である。

Portfolio OS は独自の task ledger や task state を持たない。保持してよいものは次に限定する。

- source trail / capture references
- routing and classification rationale
- approved external write 前の task draft
- creation 後の backend task references
- recommendation / automation decision logs
- final response / work report logs

status、due date、priority、assignee、task body、project fields などの task state は task backend が所有する。

Backend migration は、古い backend から新しい backend へ task を移動し、その後 configured plugin / adapter を切り替える形で扱う。Portfolio OS は migration source of truth にならない。

## 必須の backend-agnostic contract

共有 task backend abstraction には少なくとも次の概念を置く。

- `TaskDraft`: external write 前の proposed task
- `TaskRef`: backend task 登録後の stable reference
- `TaskQuery`: retrieval 用の backend-neutral filter
- `TaskSnapshot`: backend から返る read-only view
- `TaskWriteResult`: create/update/comment operation の result
- `TaskBackendAdapter`: GitHub Projects first と将来 backend が実装する interface

core interface は次を support する。

- `TaskDraft` から task を create する
- `TaskRef` で task を read する
- work unit、due date、status、urgency、importance、automation mode、assignee で task を query する。ただし backend で利用可能な場合に限る
- 明示的な adapter call を通じて backend fields を update する
- progress / report comment を追加する
- task に戻れるだけの backend metadata を返す

この abstraction は GitHub GraphQL ID、project field ID、status option ID、repository ID、provider-specific auth を Portfolio OS core に漏らしてはならない。

## 必須 GitHub Projects fields

最初の GitHub Projects adapter では `work_unit_id` を required とする。

推奨 backend fields は次の通り。

- `work_unit_id`: required。Portfolio OS work unit id を値にする。空にせず、`inbox` や `unrouted` のような明示 fallback を使う。
- `task_type`: 例 `capture`, `decision`, `artifact`, `review`, `execution`, `follow_up`
- `due_date`
- `urgency`
- `importance`
- `automation_mode`: `manual`, `draft_only`, `auto_candidate`, `approved_auto`
- `approval_required`: boolean
- `source_ref`: originating source への reference。raw platform payload ではない。

adapter が backend-neutral concepts から GitHub Projects fields への mapping を所有する。

## スキル / プラグイン責務分担

境界は次の通り。

- 共有 task backend plugin:
  - provider-specific API calls
  - create/read/update/comment
  - field mapping
  - auth handling
  - idempotency and duplicate handling
  - rate limit and API error handling
  - 必要なら migration/export helpers

- 再利用可能な task-management skill:
  - chat/capture text を `TaskDraft` に変換する
  - `work_unit_id` を推定または確認する
  - due date、urgency、importance、task type、approval needs を推定する
  - external write 前の human review text を作る
  - recommendation rationale を説明する
  - task が automation candidate かどうかを判断する。ただし high-risk action は実行しない

- Portfolio OS local/profile-specific skills:
  - Portfolio OS profiles にしか存在しない source capture
  - profile-specific routing context
  - local source trail and capture integration
  - shared task-management skill / backend adapter への handoff

profile-specific Portfolio OS capture behavior は、本当に backend-agnostic かつ OS 外でも有用でない限り、reusable task plugin / skill に入れない。

## external write と governance policy

初期挙動は draft-first とする。

1. capture/chat input を `TaskDraft` に normalize する
2. user が review/edit できる
3. approval 後にだけ adapter が GitHub Projects を create/update する

将来的には trusted channels や trusted work units に direct registration を許してもよいが、明示 policy の背後に置く。

External write、customer contact、permission changes、secrets、paid actions、irreversible actions、production actions、publication は human approval または governance decision を必要とする。

Automation は段階化する。

1. `recommend`: 今日の tasks を提案する
2. `draft`: artifact や response を準備する
3. `execute_with_approval`: 明示 approval 後だけ実行する
4. `trusted_automation`: low-risk / reversible / pre-approved rules に限って許可する

## 推奨実装順

1. repo docs を読む。
   - `AGENTS.md`
   - `knowledge/AGENTS.md`
   - `knowledge/wiki/syntheses/portfolio-os-architecture.md`
   - `knowledge/wiki/syntheses/work-unit-core-design.md`
   - `knowledge/wiki/syntheses/command-center-core-design.md`
   - `knowledge/wiki/syntheses/external-plugin-dependency-import-design.md`
   - `knowledge/wiki/syntheses/portfolio-os-operations-command-map.md`
2. backend-neutral task contract を定義する。
3. GitHub Projects adapter mapping と config shape を定義する。
4. live write 前の draft / review path を実装する。
5. adapter 経由で GitHub Projects create/read/query/comment を実装する。
6. 固定テストデータ / 模擬実装を使った tests を追加する。通常 test は live GitHub access を要求しない。
7. migration boundary を document する。GitHub Projects は first backend であり、permanent architecture ではない。

## 推奨 skills

- `superpowers:brainstorming`: implementation 前の design finalization に使う。
- `plugin-creator`: Codex plugin bundle を作る場合に使う。
- `skill-creator`: reusable task-management skill files を作る場合に使う。
- `github:github`: live GitHub repository / project context が明示的に必要な場合だけ使う。
- `github:yeet`: local changes を publish する準備ができた後だけ使う。
- `openai-docs`: implementation が current OpenAI product/API behavior に依存する場合だけ使う。

## 非ゴール

- Portfolio OS task ledger を作らない。
- Portfolio OS runtime を task state source of truth にしない。
- raw Discord platform payloads、message IDs、transport metadata を Portfolio OS knowledge/routing contracts に保存しない。
- GitHub Projects concepts を Portfolio OS core に hard-code しない。
- 明示 approval なしに live credentials、external writes、hooks、MCP servers、production automations を有効化しない。

## 別セッション向け open questions

- shared task backend plugin の exact location / repository。
- task-management skill の exact reusable skill location / repository。
- `inbox` と `unrouted` のどちらを canonical fallback work unit id にするか。
- GitHub Projects field schema と、fields を adapter が作成するか pre-existing validation に限定するか。
- repeated chat messages からの duplicate task creation を避ける idempotency key strategy。
- minimum accepted live-write approval UX。
