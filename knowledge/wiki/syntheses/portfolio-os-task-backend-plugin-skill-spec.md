# Portfolio OS タスクバックエンドプラグイン / スキル仕様

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。`issue-implementation-loop` は POTASK-001 から POTASK-009 まで local `PR_READY`。2026-07-15 に追加承認された POTASK-010 の backend-neutral read facade / Hermes read-only tool / export alignment は local 実装・検証済みで、PR delivery 対象とする。2026-07-16 に POTASK-011 として、consumer が backend を意識せず Hermes から実際に `task_query` を呼べる pluggable provider adapter / host-owned route / end-to-end smoke test を追加する方針を承認した。Current companies preflight は `.codex-plugin/plugin.json` だけを読むため、Hermes `plugin.yaml` をauthoritative export evidenceとして受け入れるcross-repo follow-upまでNPLM-006 end-to-end gateはblockedのままとする。GitHub issue mirror、mergeはまだ行わない。

この版では、初期稼働backendをhost-owned local JSONにできる。外部backendはHermes Agentに登録されたMCPまたは別provider pluginのbackend-neutral `task_query` toolへ接続し、direct provider API adapter / `gh` command planner / GraphQL fallbackは作らない。

## 問題

Portfolio OS に task intake / daily review / automation candidate flow を足すには、task state を Portfolio OS runtime に二重管理させず、backend source of truth と skill-level reasoning を分離する必要がある。

task backend は初期稼働時にlocal fileでもよく、後からMCPまたはprovider plugin経由のGitHub Projects等へ差し替えられる必要がある。Portfolio OS coreやreusable task-management skillがfile path、GitHub GraphQL IDs、project field IDs、provider-specific auth、`gh` command、GraphQL fallback実装を直接持つと、backend migrationとplugin swapの設計が壊れる。

また、実運用ではHermes Agentを使う想定である。したがってexternal backend連携はtask-management plugin内にcredential / MCP config / provider clientを抱え込まず、Hermes AgentがMCPまたはprovider pluginの登録・承認・tool enablementを管理する構成に寄せる。Pluginはbackend-neutral `task_query` facade、local read adapter、`TaskSnapshot`正規化だけを所有する。

## 成功条件

- backend-neutral task contract が `TaskDraft`、`TaskRef`、`TaskQuery`、`TaskSnapshot`、`TaskWriteResult`、`TaskBackendRoute`、`TaskBackendDestination` を持つ。
- 初期稼働backendはread-only local JSONでよい。GitHub-specific IDs / field IDs / auth / MCP server config、local source pathはPortfolio OS coreとreusable task-management skillに漏らさない。
- 外部backend連携はhost-provided MCP toolまたは別provider pluginのread-only toolを使う。task-management pluginはdirect GraphQL HTTP client、`gh` command planner、provider credential clientを作らない。
- Portfolio OS は task state の source of truth を持たず、source trail、routing/classification rationale、task draft、backend task refs、decision logs、work report logs だけを保持する。
- task-management skill は capture/chat text を `TaskDraft` に正規化し、human review text と recommendation rationale を出せる。
- adapter invocation envelope は dispatch 前に review できる。実際の create/update/comment の実行方針は MCP などの外部 adapter が所有する。
- MCP server enablement、credential setup、GitHub adapter tool enablement は plugin install では実行しない。
- Hermes native plugin loader 用に `plugins/task-management/plugin.yaml` と `__init__.py` を持ち、`hermes plugins list` / `enable` の入口から同梱 skill を登録できる。
- インストール後は、host-owned local routeまたはHermes Agentに登録済みのMCP / provider plugin toolがあれば、同じ`task_query` contractでtask readを使える。
- normal tests は固定テストデータ / 模擬実装ベースで、live GitHub access、Hermes live profile、credentials、MCP server を要求しない。
- Hermes は `task_query` を `task-management-read` toolset に登録する。model inputからadapter / tool / file path / provider destinationを選ばせず、host-owned routeがlogical `destination_ref`とoptional internal `backend_key`からfixed adapterを解決する。public callでは`backend_key`を省略でき、host defaultを使う。
- `plugin.yaml.exports.toolsets` と runtime registration は正確に `task-management-read` で一致する。`.codex-plugin/plugin.json` は current `plugin-creator` schema に `exports` がないため Codex manifest として有効な field だけを維持する。
- read adapter は `TaskQuery` と opaque `destination_ref` を受け、provider raw IDs、unknown backend metadata、credential-like values を含まない `TaskSnapshotResult` を返す。
- consumerはlocal JSON、MCP、provider plugin backendの違いを意識せず、同じ`task_query` / `TaskSnapshotResult` contractを使う。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## 現在のベースライン

2026-06-29 時点の current checkout で確認した状態は次の通り。

- `grill-to-pr-loop` planning prereq: passed。
- `grill-with-docs` と `issue-implementation-loop` は利用可能。
- 添付ハンドオフは [source summary](../sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md) と [raw source](../../raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md) に保存済み。
- GitHub MCP Server と Codex / Hermes MCP host 方針を調査済み。
- Hermes Agent には `hermes mcp` と `hermes tools` があり、MCP server 管理と `server:tool` notation による tool enable / disable が可能である。
- 現在の live Hermes config では `hermes mcp list` は `No MCP servers configured` を返した。GitHub MCP Server は未登録である。
- Hermes config は `approvals.mode: manual`、`mcp_reload_confirm: true` であり、`delegation.inherit_mcp_toolsets: true` が設定されている。

## 採用済み判断

- 初期稼働backendはread-only local JSONでよく、GitHub ProjectsはMCPまたは別provider plugin経由で後から差し替え可能にする。
- 選択されたbackendをtask stateのsource of truthとする。初期稼働ではhost-owned local JSONでよい。
- Portfolio OS は task ledger / task state を独自に保持しない。
- Backend migration は、旧 backend から新 backend へ task を移したうえで configured backend route を切り替える。Portfolio OS は migration source of truth にならない。
- backend-neutral contract は `TaskDraft`、`TaskRef`、`TaskQuery`、`TaskSnapshot`、`TaskWriteResult`、`TaskBackendRoute`、`TaskBackendDestination` を中心に置く。
- shared task backend plugin ではなく、薄い `task-management` plugin package と、その中に同梱する primary `task-management` skill として実装する。
- plugin は distribution / install-update / config template / examples / references の単位であり、通常の実行 surface は同梱 skill が担う。
- 初回実装では公開 entrypoint skill を `task-management` 1 つに保つ。`daily-review`、`backend-admin`、`task-router` などの追加 skill は、trigger と責務が明確に分かれた後続 scope とする。
- GitHub Projectsへ接続する場合はGitHub MCP Serverまたは別provider pluginを使う。
- direct GitHub API adapter / provider client、`gh` command planner、direct GraphQL HTTP client、GitHub Projects schema repair codeは作らない。GitHub固有response mappingが必要な場合はMCP serverまたは別provider plugin側が所有する。
- 実装は repository root の `plugins/` 配下に置く。
- 推奨 package path は `plugins/task-management/` とする。
- top-level `skills/task-management/` は作らない。skill は `plugins/task-management/skills/task-management/` に置く。
- plugin scaffold は `plugin-creator` の helper を使い、`.codex-plugin/plugin.json` を必須にする。
- Hermes native plugin manifest として `plugin.yaml` を package root に置く。current Hermes の valid kind は `standalone` / `backend` / `exclusive` / `platform` / `model-provider` なので、workflow package であっても `kind: standalone` とする。
- Hermes enable/load entrypoint として package root の `__init__.py` から同梱 skill を `ctx.register_skill("task-management", ...)` で登録し、`task_query` を `ctx.register_tool(..., toolset="task-management-read")` で登録する。Provider access は host-provided adapter に残す。
- current Hermes は subdir plugin install 時に対象 subdir だけを installed plugin directory へ移すため、`.git` が残らず `hermes plugins update task-management` が失敗する場合がある。standalone repository 化または Hermes installer の source metadata 対応までは、README で `hermes plugins install --force ...#plugins/task-management` による更新手順を明記する。
- skill scaffold は `skill-creator` の helper を使い、`SKILL.md` と `agents/openai.yaml` を検証対象にする。
- Portfolio OS local/profile-specific skills は profile-specific capture / routing / source trail integration / shared layer handoff に限定する。
- initial behavior は review / approval gate first とし、task draft、routing decision、adapter invocation envelope を人間が確認できるようにする。
- fallback work unit id は `inbox` を既定案とする。
- task には `work_unit_id` に加えて `work_unit_name` を持たせる。`work_unit_id` は stable routing key、`work_unit_name` は GitHub Projects 上で人間が判断できる display label とする。
- GitHub Projects field schema は初回実装では create/repair しない。pre-existing validation と人間向け setup guidance に限定する。
- first implementation slice は、インストール可能な plugin / skill、review / approval path、routing / preview / guard tests、GitHub MCP Server route preflight、guarded adapter dispatch envelope、Hermes Agent での adapter availability runbook まで含める。
- dry-run mode は作らない。未承認 adapter dispatch の代替は dry-run ではなく review / approval gate である。
- 初回実装では dedicated idempotency key、`task_sha` field、duplicate-prevention store を作らない。
- 重複 task が作られるリスクは許容し、後から backend 側で整理する。Portfolio OS local duplicate ledger も作らない。
- adapter dispatch UX は per-operation explicit review とする。task create/update/comment/report に相当する adapter operation envelope は、それぞれ preview と明示承認を通ってから adapter へ渡す。
- batch approval と policy-gated approval は初回実装では扱わない。
- 現 planning scope は task composition / routing / adapter dispatch envelope までとし、外部 adapter が行う実 write policy はこの issue の責務にしない。
- task-management plugin / skill は remote write policy、GitHub Projects mutation、GitHub issue/PR、push、PR creation、merge を所有しない。これらは adapter / host / delivery workflow の責務とする。
- POTASK-010 の external adapter compatibility として `TASK_MANAGEMENT_READ_ADAPTER_TOOL=mcp__<server>__task_query` を維持する。
- POTASK-011ではhost-owned route fileからlogical `destination_ref`とoptional internal `backend_key`に対応するadapter kindとfixed tool / sourceを解決する。route file path、adapter kind、MCP / plugin tool名、local source path、GitHub owner / project number / field mappingはmodel inputに含めない。
- 初期provider adapterはread-only local JSONとexternal read toolとする。external read toolはMCP `mcp__<server>__task_query`または別pluginの`task_adapter__<provider>__task_query`に限定する。どのbackendでもpublic contractは同じである。
- Hermes capability export の authoritative source は `plugin.yaml.exports.toolsets` とする。Current `plugin-creator` が `.codex-plugin/plugin.json.exports` を拒否するため、Codex manifest は current schema のまま有効性を保つ。

## アプリケーション構成

今回作るものは、ユーザーが直接使う CLI app ではなく、Codex / Hermes にインストール可能な薄い task-management plugin package である。GitHub provider client は含めない。plugin package は配布・更新・設定テンプレート・参照資料、backend-neutral read facade、pluggable provider adapter のまとまりであり、agent-facing workflow は同梱された primary `task-management` skill、read-only runtime surface は `task-management-read:task_query` が担う。

想定 layout は次の通り。

```text
plugins/task-management/
├── .codex-plugin/plugin.json
├── plugin.yaml
├── __init__.py
├── task_management/
│   ├── __init__.py
│   ├── read_adapter.py
│   ├── route_config.py
│   └── provider_adapters/
│       ├── __init__.py
│       ├── local_json.py
│       └── external_tool.py
├── README.md
├── config/
│   └── task-backends.example.toml
├── skills/task-management/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── task-contracts.md
│       ├── task-read-adapter.md
│       ├── task-draft-contract.md
│       ├── backend-routing.md
│       ├── adapter-dispatch.md
│       ├── github-mcp-projects.md
│       └── hermes-mcp-governance.md
├── examples/
│   ├── task-create-preview.example.md
│   └── hermes-github-mcp-enable.example.md
└── tests/
```

`scripts/task_management/github_projects_commands.py`、`gh_executor.py`、GitHub GraphQL client、GitHub固有response mapperは作らない。GitHub Projectsへ接続する場合は、backend-neutral `task_query` contractを提供するMCP serverまたは別provider pluginをhost-owned routeから呼ぶ。

## Read Provider Adapter 設計

public `task_query` はbackend-neutral `TaskQuery`とopaque logical `destination_ref`を受ける。public `TaskQuery.backend_key`は省略可能で、host default routeへ解決する。consumerはbackend kind、MCP / plugin tool名、GitHub owner / project number、local file path、field mappingを指定しない。

host-owned route file は次を解決する。

1. optional internal `backend_key`とlogical `destination_ref`に対応するadapter kind。`backend_key`未指定時はhost defaultを使う。
2. adapterが使うfixed read surface。external backendの場合はread-only MCP / plugin `task_query` tool、local JSONの場合はhost-owned source file。
3. provider destinationとcanonical fieldのmapping。これらはadapter内部入力であり、`TaskSnapshotResult`へ返さない。

provider adapter は同じ内部protocolを実装する。

```text
query(route, destination, task_query, dispatch) -> AdapterTaskSnapshotItems
```

- `local_json` はhost-owned JSON documentをread-onlyで読み、query filterとlimitを適用する。path traversalやmodel-supplied pathは許可しない。
- `external_tool`はhost-owned routeから固定されたread-only `mcp__<server>__task_query`または`task_adapter__<provider>__task_query`だけをHermes `ctx.dispatch_tool`で呼ぶ。direct HTTP、GraphQL、`gh`、credential lookupは行わない。
- POTASK-010の`TASK_MANAGEMENT_READ_ADAPTER_TOOL=mcp__<server>__task_query`はlegacy single-route compatibilityとして維持する。
- facadeはadapter出力を再度allowlist normalizeし、provider raw ID、route secrets、unknown metadata、credential-like valuesをfail closedする。

route configを差し替えてもconsumer、Schedule Secretary、Portfolio OS、Hermes prompt側のtool名とresult contractは変えない。将来backendを追加するときはprovider adapterとhost routeだけを追加し、public schemaへprovider-specific fieldを足さない。

通常検証はfixture / fake dispatchを使う。Hermes実呼出し検証は隔離したtemporary profileとread-only local JSON adapterで `plugin load → task_query dispatch → normalized TaskSnapshotResult` を確認する。external tool adapterはMCP toolとplugin toolのexact dispatchをfixture-backed testで検証し、live provider auth / networkをnormal testの必須条件にしない。operatorがlive provider connectionを用意した場合のみ、同じpublic queryによるoptional live smoke testを行う。

初回実装では `skills/task-management/` を唯一の公開 skill entrypoint とする。複数 skill へ分割するのは、入力 task 化、daily review、backend administration などが独立した trigger / permission / context budget を持つと確認できた場合に限る。

## Backend Routing

Routing は 3 層に分ける。

1. **入力 routing**: Portfolio OS local/profile-specific skill または user chat が task-management skill に依頼する。profile-specific capture や source trail は Portfolio OS 側に残し、backend dispatch は task-management skill に渡す。
2. **task routing**: task-management skill が入力を `TaskDraft` に normalize し、`work_unit_id` を決める。迷う場合の fallback は `inbox` とする。ここでは backend state を作らない。
3. **backend routing**: host-owned routeがprofile configのdefault backendを決める。public read callの`backend_key`は省略可能で、consumer / modelによるprovider選択を通常flowにしない。初期稼働defaultは`local_json`でよい。
4. **destination routing**: caller / profile / host-provided registration から、実際に task を登録する外部プロジェクト管理先を `TaskBackendDestination` として受け取る。plugin package 自体は owner、project number、repository などの具体的な target を持たない。

backendが未指定の場合はhost-owned `default_backend`を使う。defaultが未設定、routeが存在しない、またはlogical destinationが解決できない場合はprovider tool / local fileを読む前にtyped errorで停止する。GitHubへの暗黙fallbackは行わない。

Adapter Dispatch Review の preview には、選択された backend key、connection ref、destination ref / label、operation type、task title/body/fields、`work_unit_id`、`work_unit_name`、expected adapter side effects、呼び出す adapter tool 名を含める。

将来の project-management backend も同じ routing model で扱う。優先する integration surface は次の順序とする。

1. **local read adapter**: host-owned local JSONをinitial source of truthとして使える。
2. **MCP**: hostが提供するread-only `task_query` toolへ接続する。
3. **provider plugin**: 別pluginが提供するread-only `task_adapter__<provider>__task_query`へ接続する。
4. **URL surface**: backend URLはlinkable metadataとして扱えるが、task read execution surfaceにはしない。

task-management pluginはbackend API clientやCLI plannerを自作しない。local read adapter、MCP、別provider pluginをrouting先として使い、Portfolio OS coreは`TaskBackendRoute`と`TaskBackendDestination`だけを見る。`gh` commandはfallbackを含めて使用しない。

## Backend 登録と保存先

Backend routing の registry は task-management plugin の runtime config として扱う。ただしここに登録するのは「どの接続面を使うか」であり、「どの GitHub organization / project / repository に書くか」ではない。

- repository に commit するのは template である `plugins/task-management/config/task-backends.example.toml` とする。
- 実際の connection config は install / profile / caller が渡す local config に保存する。
- config には backend key、kind、connection ref、必要なら field name override を置く。token や secret は保存しない。
- default backendはhost-owned configの`default_backend`で明示する。未指定時のGitHub fallbackは持たない。初期稼働例は`local_tasks`とする。
- field name override は任意である。同名の場合は config に書かず、backend-neutral field name をそのまま backend field name として使う。
- read provider kindは`local_json`、`mcp`、`plugin`に限定する。既存write routing contractのkindを変更する場合は別issueとし、POTASK-011ではread pathにCLIを実装しない。
- GitHub Projects の owner、project number、repository はこの config に置かない。必要な場合は caller / profile / host-provided registration が `TaskBackendDestination` として渡す。

例:

```toml
default_backend = "local_tasks"

[backends.local_tasks]
kind = "local_json"
connection_ref = "local-task-file"
capability = "task_read"

# 任意。接続先 backend 側の表示名が canonical field name と違う場合だけ書く。
[backends.local_tasks.field_overrides]
work_unit_id = "Work Unit"
work_unit_name = "Work Unit Name"
due_date = "Due Date"
importance = "Priority"
approval_required = "Approval Required"
```

`TaskBackendDestination` は backend route の外側から渡す。例えば GitHub Projects の場合でも、task-management plugin は `owner`、`project_number`、`repository` を分解して保持せず、`destination_ref` を外部接続登録や Project URL などの opaque reference として扱う。

例:

```toml
[destinations.default_tasks]
backend = "local_tasks"
destination_ref = "tasks:default"
destination_label = "Default Tasks"
```

最終的なtask stateは選択されたbackendに保存される。初期稼働ではhost-owned local JSONをsource of truthにできる。MCPまたは別provider pluginへrouteを差し替えた後は、そのbackendをsource of truthとする。Portfolio OS側に残せるのはsource trail、routing rationale、承認済みadapter dispatchのdecision log、backend key、backend task URL / item referenceなどの参照情報だけである。

## Hermes / MCP Integration

GitHub MCP Server は task-management plugin が自動登録しない。Hermes Agent 側の明示操作で登録・認証・tool enablement する。

設計上の前提:

- GitHub MCP Server は Hermes Agent の MCP server として登録される。
- task-management skill は MCP server の存在と必要 tool の enablement を preflight する。
- MCP server 未登録、必要 tool 無効、credential 不足、scope 不足の場合は adapter dispatch を行わず、人間向け setup guidance を返す。
- MCP tool call は外部 adapter への dispatch なので、task-management skill 内の Adapter Dispatch Review を必ず通す。
- task-management plugin install は MCP server registration、credential setup、tool enablement、Hermes live profile edit を行わない。

Hermes Agent での懸念:

- 現状 `hermes mcp list` は GitHub MCP Server 未登録であるため、live 実行には別途 enablement が必要である。
- Hermes config では `delegation.inherit_mcp_toolsets: true` が確認されている。state-changing GitHub MCP adapter tools を commander へ持たせる場合、子 agent へ継承されないよう Execution Plan Gate で扱う。
- `approvals.mode: manual` と `mcp_reload_confirm: true` は維持する。
- GitHub MCP adapter tools は commander / task-management flow 専用にし、work unit subagent や review worker へ無条件継承しない。

## GitHub MCP Adapter Route Strategy

この節は Spec Gate 承認対象の推奨案である。

### 基本方針

- GitHub Projects backend は GitHub MCP Server first とする。
- GitHub API access は host-provided MCP tools へ委譲する。
- task-management plugin は GitHub API client、`gh` command、GraphQL query、field id repair logic を持たない。
- Portfolio OS core と reusable task-management skill は GraphQL node ID、field ID、option ID、repository ID、auth token を直接扱わない。
- GitHub MCP Server の toolset は必要最小限にする。`all` 相当の広い toolset は初回実装では使わない。
- GitHub Projects の read/write 自体は GitHub MCP Server の責務である。task-management plugin が検証するのは、backend routing、approval preview、必要 tool 名の選択、permission guard、typed error mapping である。

### Adapter operation envelope

- task-management plugin は、create/update/report などの意図を adapter-neutral operation envelope として作る。
- envelope は task title、body、backend-neutral fields、`work_unit_id`、`work_unit_name`、destination ref / label、必要なら content target ref、呼び出す adapter tool 名、想定 adapter side effect を含む。
- GitHub Issue を作るか、Project-native draft issue を作るか、既存 item を更新するかは GitHub MCP Server adapter の capability と実装に委ねる。
- task-management plugin は GitHub 側の実作成手順、mutation sequence、retry policy、schema repair を所有しない。
- adapter から返る result を `TaskWriteResult` として正規化し、backend task URL / item reference / typed error を consumer へ返す。

### Schema validation

- 初回実装では GitHub Projects field schema の create/repair を行わない。
- required / recommended fields が存在するかを preflight で確認し、不足している場合は human setup guidance として返す。
- schema create/repair を自動化する場合は後続 scope とし、MCP tool support と separate approval policy を確認してから扱う。

### Error / permission

- MCP server missing、tool disabled、auth missing、permission failure、project not found、field missing、field type mismatch、tool capability mismatch、rate limit、partial update failure を typed result として扱う。
- network timeout 後の再実行で duplicate task が作られる可能性は許容する。duplicate cleanup は backend 側の task hygiene として扱う。
- credential や token はログ、knowledge docs、Portfolio OS state、task-management config に保存しない。

## Spec Gate で承認済みの判断

- 初期稼働はlocal JSONでよく、外部backendはMCPまたは別provider pluginへ接続すること。direct GitHub API adapter / `gh` / GraphQL fallback実装は作らないこと。
- 初回実装では GitHub Projects schema create/repair を scope 外にし、pre-existing validation に限定すること。
- 初回実装を、routing contract だけでなくインストール後に実利用できる task-management skill package として完成させること。
- Hermes Agent で GitHub MCP adapter tools をどの profile / platform / delegation boundary に expose するかを、Issue Gate / Execution Plan Gate で確認すること。
- live smoke test は通常検証に含めないこと。GitHub MCP Server の read/write 自体は外部 MCP server の責務であり、この plugin は routing / preview / guard を固定テストデータと模擬 tool で検証する。

## 非ゴール

- Portfolio OS task ledger の作成。
- Portfolio OS runtime を task state source of truth にすること。
- raw Discord platform payloads、message ids、transport metadata を Portfolio OS knowledge/routing contracts に保存すること。
- GitHub Projects concepts を Portfolio OS core に hard-code すること。
- GitHub API client、`gh` command planner、direct GraphQL HTTP client の作成。
- plugin install 時の live credentials、MCP server registration、tool enablement、hooks、production automations の有効化。
- GitHub Projects field schema create/repair。
- GitHub issue / PR 作成、push、merge、deployment。
- GitHub MCP Server 自体の read/write 実装テスト。
- plugin 自身による GitHub API / GraphQL / `gh` read client、credential 管理。provider destination 解決はhost-owned routeを入力とするprovider adapterだけが行い、consumer / public contractへ漏らさない。
- model input で任意の adapter tool 名を選ばせること。
- model input でlocal file path、GitHub owner、project number、field ID、route file pathを選ばせること。
- batch approval、policy-gated approval、trusted automation による adapter dispatch。
- dedicated duplicate prevention のための `task_sha` field、local store、raw source payload 保存。

## Issue 分解方針

Spec Gate 承認後に、日本語 local-first ledger として issue 化する。現時点の想定順序は次の通り。

1. `plugins/task-management/` の Codex plugin scaffold と primary `task-management` skill skeleton を作る。
2. backend-neutral `TaskDraft` / `TaskRef` / `TaskQuery` / `TaskSnapshot` / `TaskWriteResult` / `TaskBackendRoute` / `TaskBackendDestination` contract と固定テストデータを定義する。
3. review / per-operation approval gate を持つ task-management skill contract / prompt / examples を作る。
4. provider-neutral backend routing config、destination input contract、Hermes MCP governance referenceを作る。初期稼働defaultはPOTASK-011で`local_tasks`へ更新する。
5. `work_unit_id` と `work_unit_name` の解決 / preview / backend field contract を実装する。
6. GitHub MCP Server preflight contract を実装する。live Hermes / live GitHub を要求せず、固定テストデータ / 模擬実装で検証する。
7. Adapter operation envelope preview と typed result mapping を実装する。実 write policy は adapter 側の責務であり、この plugin は envelope dispatch までを扱う。
8. Hermes Agent への GitHub MCP Server availability runbook と task-management skill の利用例を作る。
9. Portfolio OS handoff boundary、migration boundary、duplicate cleanup stance、MCP enablement boundary を docs / examples に反映する。
10. backend-neutral read adapter、Hermes `task-management-read:task_query` registration、authoritative export alignment、normalized `TaskSnapshot` behavioral test を追加する。
11. pluggable provider adapter、host-owned route、local JSON / external MCP・plugin tool adapter、Hermes end-to-end smoke testを追加する。

## 受け入れ基準

- `plugins/task-management/.codex-plugin/plugin.json` が存在し、`plugin-creator` validator を通る。
- `plugins/task-management/plugin.yaml` が存在し、Hermes native plugin manifest として `name: task-management`、`version: 0.2.0`、`kind: standalone`、`exports.toolsets = ["task-management-read"]` 相当を持つ。
- `plugins/task-management/__init__.py` は同梱 skill と read-only `task_query` tool を登録するが、live Hermes profile、credentials、MCP registration、GitHub、network には触れない。
- `plugins/task-management/README.md` は Hermes subdir install / enable 手順と、subdir install では `.git` が残らず `hermes plugins update task-management` が使えない場合の `install --force` 更新手順を明記する。
- `plugins/task-management/skills/task-management/SKILL.md` が存在し、`skill-creator` quick validation を通る。
- 初回実装の公開 skill entrypoint は `plugins/task-management/skills/task-management/` の 1 つだけである。
- plugin package は distribution / install-update / config template / examples / references、backend-neutral read facade、read-only provider adaptersを所有し、GitHub provider client、write adapter、MCP server 実装を所有しない。
- `TaskDraft` は `work_unit_id`、`work_unit_name`、task type、due date、urgency、importance、automation mode、approval required、source ref を backend-neutral に表現できる。
- `TaskBackendRoute` は `kind=mcp|reader|skill|cli|url`、connection ref、capability、field override を表現できる。
- `TaskBackendDestination` は backend key、destination ref / label、必要なら content target ref を表現できる。
- plugin package の backend config は owner、project number、repository を必須または既定値として持たない。
- `TaskRef` と `TaskSnapshot` は provider-specific raw IDs を Portfolio OS core consumer に漏らさず、linkable metadata は backend-owned metadata として扱う。
- `task_query` は backend-neutral `TaskQuery` と opaque `destination_ref` を固定 host adapter へ渡し、allowlist された `TaskSnapshotResult` だけを返す。
- `task_query` は missing configuration、write-capable tool name、invalid adapter result、invalid/unsafe snapshot を typed error として fail closed する。
- `task_query` のpublic schemaはbackend追加で変わらない。`TaskQuery.backend_key`は省略可能で、host-owned default routeがadapterを選ぶ。consumerはlocal JSON / MCP / provider pluginの違いを指定しない。
- local JSON adapterはhost-owned pathだけをread-onlyで扱い、model-supplied pathやroute外pathを読まない。
- external tool adapterはfixed read-only `mcp__<server>__task_query`または`task_adapter__<provider>__task_query`だけをdispatchし、direct API / GraphQL / `gh`を使わない。
- `plugin.yaml.exports.toolsets` と Hermes `ctx.register_tool(..., toolset=...)` は正確に `task-management-read` で一致する。
- GitHub MCP Server route は MCP server missing、tool disabled、auth missing、permission failure、project not found、field missing を typed result にできる。
- 固定テストデータ / 模擬実装 tests で create/update/report/query preview と typed result mapping を検証できる。
- standalone dry-run mode は存在しない。
- review / approval gate は、人間が task registration 内容を確認できる `TaskDraft` / adapter operation envelope preview を提示できる。
- adapter dispatch path は明示 approval check を通らない限り adapter へ envelope を渡せない。
- per-operation explicit approval は create、update、comment/report に相当する adapter operation envelope に適用される。
- approval preview は backend key / connection ref / destination ref / destination label、operation type、task title/body/fields、`work_unit_id`、`work_unit_name`、呼び出す adapter tool 名、expected adapter side effects を含む。
- batch approval と policy-gated approval は実装されない。
- plugin install は live MCP server registration、credential setup、Hermes profile edit、GitHub adapter tool enablement を行わない。
- direct GitHub API client / `gh` command planner / direct GraphQL HTTP clientは存在しない。task read execution surfaceはlocal JSON、MCP、別provider pluginに限定する。
- GitHub Projects schema create/repair は初回実装では行わない。
- GitHub MCP Server の read/write 自体を live smoke test しない。routing / preview / guard / typed error mapping を固定テストデータと模擬 tool で検証する。
- インストール後に、Hermes Agent に GitHub MCP Server が登録済みであれば、task 登録の review / approval / routing / adapter dispatch まで実利用できる。
- dedicated idempotency key、`task_sha` field、duplicate-prevention store は存在しない。
- task duplication が起きた場合は backend 側で整理する。Portfolio OS は duplicate state / cleanup ledger を持たない。
- docsはinitial local JSON backendと、MCP / provider pluginへの差し替え可能性を明記する。GitHub Projectsをimplicit defaultにしない。
- temporary Hermes profileでpublic `task_query`を呼び、local JSON providerからnormalized `TaskSnapshotResult`が返るend-to-end smoke testが通る。

## 検証コマンド

実装 scope 確定後に更新する。現時点の初期候補は次の通り。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
git diff --check
```

external providerのlive smoke testはnormal verificationに含めない。normal verificationはtask composition、routing、adapter operation envelope、preview、guard、typed result mappingに加え、`task_query`のhost default route resolution、local JSON read、MCP / plugin tool exact read-only dispatch、`TaskSnapshotResult` allowlist、credential leak rejection、Hermes toolset/export alignmentを固定テストデータ / 模擬toolで検証する。Hermesの実呼出し経路はtemporary profileとlocal JSON fixtureで検証する。

## Adapter Dispatch 方針

この plugin / skill は remote write policy を所有しない。

実装 scope には、インストール可能な task-management plugin、task taxonomy、TaskDraft composition、backend / destination routing、adapter operation envelope、preview / guard tests、Hermes availability runbook を含める。

GitHub MCP Server registration、credential setup、tool enablement、GitHub Projects mutation、GitHub issue/PR、push、PR creation、merge は adapter / host / delivery workflow の責務であり、この issue の実装対象ではない。

normal tests は固定テストデータ / 模擬実装を使い、GitHub MCP Server 自体の read/write live smoke test は行わない。`task_query` は mock dispatch を通じて exact adapter tool 名、`TaskQuery` envelope、`TaskSnapshotResult` allowlist、typed fail-closed behavior を検証する。

dry-run mode は作らない。`local_only` は planning / repository delivery policy であり、task-management plugin の user-facing runtime mode ではない。

## 人間レビューゲート

- **Spec Gate**: この spec の Epic ID、accepted decisions、non-goals、acceptance criteria、verification、stop conditions、GitHub MCP Server first 方針を承認する。
- **Issue Gate**: 承認後に作る日本語 local-first issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: normalized input packet、adapter operation envelope、dependency graph、fallback policy、Hermes MCP adapter boundary を承認する。
- **Adapter Availability Gate**: Hermes Agent に登録済みまたは登録予定の MCP server、toolset、available tools、credential boundary、allowed / denied work units、audit log destination、rollback / revocation path を確認する。これは adapter / host 側の enablement であり、plugin install の副作用ではない。
- **Adapter Dispatch Review**: task create/update/comment/report に相当する envelope ごとに preview を表示し、backend key / connection ref / destination ref / destination label、operation type、task title/body/fields、呼び出す adapter tool 名、expected adapter side effects を確認してから adapter へ渡す。batch approval と policy-gated approval は初回実装では使わない。

各 gate 承認後は、承認済み local artifacts と ledger/log 更新を commit してから次フェーズへ進む。ユーザーが明示的に commit 延期を指示した場合は、その例外を ledger/log に記録する。

## 停止条件

- shared task-management plugin / reusable skill / Portfolio OS local skill の責務境界が混ざる。
- `Epic ID` または設置場所が曖昧なまま issue decomposition に進む。
- plugin package path が `plugins/task-management/` 以外に変更され、approved write scope と合わなくなる。
- plugin package の backend config に GitHub owner、project number、repository などの具体的 target を必須設定として戻す。
- Portfolio OS に task state source of truth が戻る。
- GitHub-specific IDs / field IDs / auth が Portfolio OS core または reusable task-management skill に漏れる。
- live GitHub access、credential、external adapter access が normal tests または planning phase に必要になる。
- normal tests が live GitHub access、Hermes live profile、MCP server、credentials を要求する。
- plugin install が MCP server registration、credential setup、Hermes live profile edit、GitHub adapter tool enablement を行う。
- `inbox` fallback の意味が Portfolio OS work unit と backend sentinel の間で曖昧になる。
- duplicate prevention のために `task_sha` field、local store、raw source payload 保存が scope に戻る。
- 重複作成を完全に防ぐと主張する。
- batch approval または policy-gated approval を初回実装 scope に戻す。
- preview なし、または operation ごとの明示承認なしで adapter dispatch envelope を渡す。
- task-management pluginがdirect API、`gh`、GraphQL client、provider credential managementを持つ。
- `task-management-read:task_query` がhost-owned routeを迂回してmodel-supplied任意tool / file path / provider destinationへdispatchできる。
- normalized `TaskSnapshot` が provider raw ID、unknown backend metadata、credential-like value を返す。
- `plugin.yaml.exports.toolsets` と Hermes runtime registration の toolset 名が一致しない。
- GitHub Projects schema create/repair を初回実装 scope に戻す。
- `work_unit_name` なしで GitHub Projects 上の work unit 表示を `work_unit_id` だけに戻す。
- Hermes `delegation.inherit_mcp_toolsets` によって state-changing GitHub MCP adapter tools が子 agent へ無条件継承される。

## 既知のリスク

- GitHub MCP Server の Projects tool coverage が不足する場合、Project-native draft issue や一部 field update は初回実装で扱えない可能性がある。
- GitHub Projects schema create/repair を初回 scope から外すため、project setup は人間の前準備に依存する。
- Hermes Agent の MCP server registration / credential / tool enablement は live operation であり、repo-only verification では検証できない。
- Hermes config の `delegation.inherit_mcp_toolsets: true` により、state-changing MCP adapter tools が子 agent に継承されるリスクがある。
- MCP remote server / OAuth / token scope の扱いを誤ると credential exposure や過剰権限につながる。
- `TASK_MANAGEMENT_READ_ADAPTER_TOOL` は tool 名だけを保持するが、host-provided `task_query` adapter 自体の read-only 性、credential、destination mapping、pagination は live Adapter Availability Gate で別途検証が必要である。
- host-owned route fileのpermission、destination mapping、GitHub field mappingが誤るとwrong destinationまたはinvalid snapshotになる。routeはmodel inputから変更できず、adapter resultはfacadeで再検証する必要がある。
- current `plugin-creator` schema は `.codex-plugin/plugin.json.exports` を受け付けないため、Hermes capability export の authoritative source は `plugin.yaml` とする。companies 側 preflight が Codex manifest だけを読む場合は、Hermes manifest も検証対象にする follow-up が必要である。
- `work_unit_name` は display label なので、work unit rename 後に backend 上の古い task と表示名がずれる可能性がある。安定識別は `work_unit_id`、人間向け表示は `work_unit_name` として扱う。
- dedicated duplicate prevention を持たないため、通信 timeout 後の再実行や人間の二重承認で duplicate task が作られる可能性がある。
- duplicate cleanup は backend 側の通常 task hygiene として扱うため、backend 上での整理手順や検出 view が後続で必要になる可能性がある。

## 関連ページ

- [Portfolio OS Task Backend Plugin / Skill Handoff](../sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md)

## 公式情報

- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [GitHub MCP Server: Codex install guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md)
- [GitHub MCP Server: Remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [Codex MCP docs](https://developers.openai.com/codex/mcp)

## 出典

- [Portfolio OS Task Backend Plugin / Skill Handoff](../sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md)
- [raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md](../../raw/sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md)
- `hermes mcp --help`
- `hermes tools --summary list`
- `hermes mcp list`
- `~/.hermes/config.yaml` の read-only inspection
