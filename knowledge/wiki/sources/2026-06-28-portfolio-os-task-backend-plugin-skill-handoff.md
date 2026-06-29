# 2026-06-28 Portfolio OS Task Backend Plugin / Skill Handoff

## 概要

添付ハンドオフは、Portfolio OS profile-specific 設計から切り離して、再利用可能な task-management skill layer と task backend routing を設計・実装するための入力である。

主要方針は、最初の backend を GitHub Projects としつつ、Portfolio OS core には GitHub 固有 ID、project field ID、provider-specific auth、task state を漏らさないことにある。Portfolio OS は source trail、routing/classification rationale、task draft、backend task references、recommendation / automation decision logs、final response logs だけを保持し、status、due date、priority、assignee、task body、project fields は backend source of truth とする。

## 主要 claim

- GitHub Projects は first backend であり、永久固定の backend architecture ではない。
- `TaskDraft`、`TaskRef`、`TaskQuery`、`TaskSnapshot`、`TaskWriteResult`、`TaskBackendRoute`、`TaskBackendDestination` を backend-neutral contract として定義する。
- GitHub 連携は GitHub MCP Server first とし、独自 GitHub adapter、`gh` command planner、direct GraphQL HTTP client は作らない。
- GitHub MCP Server の registration、credential、tool enablement は Hermes Agent host 側の明示操作として扱い、task-management plugin install では有効化しない。
- task-management skill は capture/chat text から `TaskDraft` を作り、`work_unit_id`、`work_unit_name`、due date、urgency、importance、task type、approval needs を推定または確認し、人間レビュー用 text を用意する。
- Portfolio OS local/profile-specific skills は profile-specific source capture、routing context、source trail integration、shared task-management skill への handoff に限定する。
- initial behavior は draft-first とし、task draft、routing decision、adapter invocation envelope を dispatch 前に review できるようにする。

## 現時点で採用する前提

- この repository では、Spec Gate 前の durable planning artifact を `knowledge/wiki/syntheses/` に置く。
- `grill-to-pr-loop` の planning prereq は通過しており、`grill-with-docs` と `issue-implementation-loop` は利用可能である。
- 現時点の planning scope は task composition / routing / adapter dispatch envelope までとし、外部 adapter が行う実 write policy はこの issue の責務にしない。
- memory 上の既存決定と照合し、fallback work unit は `inbox` を既定案として扱う。ただし Spec Gate では明示的に accepted decision として提示する。

## Grill で確認済みの判断

- task-management plugin は repository root の `plugins/` 配下に置く。
- reusable task-management skill は同じ Codex plugin package に同梱する案を推奨する。top-level `skills/task-management/` へ分離せず、plugin の install/update/config lifecycle と一緒に扱う。
- plugin は distribution / install-update / config template / examples / references の単位とし、通常の実行 surface は同梱された primary `task-management` skill が担う。
- 初回実装では公開 entrypoint skill を `task-management` 1 つに保つ。追加 skill は trigger、permission、context budget が明確に分かれた後続 scope とする。
- GitHub Projects field schema は初回実装では create/repair せず、pre-existing validation と人間向け setup guidance に限定する。
- 推奨 package path は `plugins/task-management/` とする。plugin root に `.codex-plugin/plugin.json`、同梱 skill に `skills/task-management/`、backend routing config template に `config/task-backends.example.toml`、skill references に GitHub MCP / Hermes governance docs を置く。
- 同梱を推す理由は、skill が生成する `TaskDraft` と backend routing / approval contract を同じ version / install lifecycle で管理できるためである。
- first implementation slice は、インストール可能な plugin / skill、review / approval path、routing / preview / guard tests、GitHub MCP Server route preflight、guarded adapter dispatch envelope、Hermes Agent での adapter availability runbook まで含める。ただし normal tests は live GitHub / Hermes MCP access を要求しない。
- 初回実装では dedicated idempotency key / `task_sha` field / duplicate-prevention store を作らない。
- 重複 task が作られるリスクは許容し、後から backend 側で整理する。これは GitHub Projects schema と adapter complexity を増やしてまで事前防止するより単純である。
- dry-run mode は作らない。plugin / skill は task 登録の routing と adapter operation envelope を作るためのものであり、未承認 adapter dispatch の代替として dry-run 実行を持たせない。必要なのは dispatch 前の review / approval gate である。
- adapter dispatch UX は per-operation explicit review とする。task create/update/comment/report に相当する adapter operation envelope は、それぞれ preview と明示承認を通ってから adapter へ渡す。
- ユーザー承認を受け、task-management plugin / skill は remote write policy、GitHub Projects mutation、GitHub issue/PR、push、PR creation、merge を所有しない方針に確定した。これらは adapter / host / delivery workflow の責務とする。
- GitHub Projects strategy は GitHub MCP Server first とする。独自 `gh` / GraphQL 実装は作らず、Hermes Agent に登録された MCP tools を routing 先にする。
- Backend routing は runtime config に登録した backend key で行う。初回実装の default backend は `github_projects_mcp` とし、repository には `plugins/task-management/config/task-backends.example.toml` だけを commit する。plugin config は `kind`、`connection_ref`、capability、任意の field override だけを持ち、GitHub owner、project number、repository などの具体的 target は持たない。
- 実際に task を登録する外部プロジェクト管理先は、caller / profile / host-provided registration から `TaskBackendDestination` として渡す。GitHub Projects の場合も `destination_ref` は外部接続登録や Project URL などの opaque reference として扱い、plugin が owner / project number / repository を分解保持しない。
- task には `work_unit_id` と `work_unit_name` の両方を持たせる。`work_unit_id` は stable routing key、`work_unit_name` は GitHub Projects 上で人間が判断できる display label とする。
- 最終的な task state は選択された backend に保存する。初回実装では GitHub Projects が保存先であり、Portfolio OS は backend key、task URL / item reference、source trail、routing rationale、decision log などの参照情報だけを保持する。
- MCP server registration、credential setup、GitHub adapter tool enablement、Hermes live profile edit は plugin install では行わず、adapter / host 側の availability boundary として扱う。
- Hermes config では `delegation.inherit_mcp_toolsets: true` が確認されているため、GitHub MCP adapter tools を子 agent へ無条件継承しないことを stop condition にする。
- 将来の project-management backend も、MCP / reader / skill graph、CLI、URL interface を routing 先として使う。task-management plugin は原則として backend API client を自作しない。
- GitHub MCP Server の read/write 自体は live smoke test しない。plugin 側は task composition、routing、adapter operation envelope、preview、guard、typed result mapping を固定テストデータと模擬 tool で検証する。

## 残る未決定点

- Hermes Agent のどの profile / platform / delegation boundary に GitHub MCP adapter tools を expose するか。

## 派生 synthesis

- [Portfolio OS Task Backend Plugin Skill Spec](../syntheses/portfolio-os-task-backend-plugin-skill-spec.md) — Spec Gate 承認済み仕様。

## 出典

- [raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md](../../raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [GitHub MCP Server: Codex install guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md)
- [GitHub MCP Server: Remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [Codex MCP docs](https://developers.openai.com/codex/mcp)
