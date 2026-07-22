# GitHub Projects Task Backend Adapter 仕様

## 状態

2026-07-21 Spec Gate承認済み。2026-07-22にseparate plugin `task-adapter-github-projects` `0.1.0`とpublic fake-MCP end-to-endをlocal実装・検証し、POTASK-019の独立implementation review cycle 2も`approved`で完了した。reviewed head `cfcd1ab`はEpic Baseへlocal統合済みである。GitHub Issue mirror、push、PR作成、shared `main`へのmerge、MCP registration、credential setup、Hermes live profile、real GitHub Project / Issue操作、live smokeは未実施で、remote deliveryとLive Activation Gateとして別途扱う。

承認済みAdapter設計、DAG、plugin責務、remote / live policyは変更していない。current implementation / review状態は[Portfolio OS Task Backend Plugin Skill Issues](portfolio-os-task-backend-plugin-skill-issues.md)で追跡する。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## 結論

GitHub 固有処理は `plugins/task-management` の条件分岐に埋め込まず、`plugins/task-adapter-github-projects/` という別 distribution に置く。adapter は Hermes の公開 `ctx.dispatch_tool()` seam を使い、official GitHub MCP Server の登録済み tool を呼び出す。

```text
Task Manager / Schedule Secretary
  -> task-management:{task_preflight,task_query,task_apply}
  -> task-adapter-github-projects:{preflight,query,apply}
  -> ctx.dispatch_tool(exact configured MCP tool)
  -> official GitHub MCP Server
  -> GitHub Issue + GitHub Project item
```

task-management と adapter は Python package import で結合しない。JSON-compatible `adapter_contract_version: 2` と normative fixtures が seam である。

## Spec Gate時点のofficial capability

2026-07-21 に official repository main `9d130049e9074772c2afbbd5e904725d240443ad` を監査した。

| Official MCP tool | relevant methods | adapter use |
| --- | --- | --- |
| `projects_list` | `list_projects`, `list_project_fields`, `list_project_items`, `list_project_status_updates` | destination / fields / items read and pagination |
| `projects_get` | `get_project`, `get_project_field`, `get_project_item`, `get_project_status_update` | destination / item read-back |
| `projects_write` | `add_project_item`, `update_project_item`, `delete_project_item`, `create_project_status_update`, `create_project`, `create_iteration_field` | Issue を Project へ追加し、field を更新する |
| `issue_write` | `create`, `update` など | linked Issue の create / update |
| `add_issue_comment` | Issue comment create | `task.comment` / `task.report` |

`projects_write.add_project_item` は Issue または Pull Request を追加する。Project-native draft item create method は current official surface にない。そのため初期 `task.create` は常に linked Issue creation とし、`backend_item` や `content_policy` は public contract に追加しない。

## 責任分界

adapter が所有する。

- opaque `destination_ref` から GitHub organization/user project を解決すること
- opaque `content_target_ref` から Issue repository を解決すること
- canonical task field から Project field / option への mapping
- official GitHub MCP tool 名と method / arguments
- GitHub auth、permission、pagination、rate limit の結果解釈
- Issue create / update、Project add、field update、comment、report、read-back
- backend-specific idempotency / duplicate prevention
- partial success と retry guidance
- provider result から safe adapter result への変換

adapter が所有しない。

- task-management public approval receipt / caller identity
- canonical task state や local task ledger
- MCP server registration、credential setup、Hermes profile edit
- GitHub schema auto-create / repair
- direct GraphQL / REST / `gh` fallback
- raw provider payload の public export

## Plugin package

推奨 layout:

```text
plugins/task-adapter-github-projects/
├── .codex-plugin/plugin.json
├── plugin.yaml
├── __init__.py
├── README.md
├── config/github-projects.example.toml
├── task_adapter_github_projects/
│   ├── __init__.py
│   ├── adapter.py
│   ├── config.py
│   ├── contracts.py
│   ├── normalization.py
│   └── safety.py
├── scripts/smoke_test_hermes_adapter.py
└── tests/
    ├── fixtures/
    ├── test_adapter.py
    ├── test_config.py
    ├── test_hermes_plugin.py
    ├── test_normalization.py
    └── test_safety.py
```

初期 version は `0.1.0` とする。Hermes runtime tools は次の exact names / toolsets とする。

| tool | toolset |
| --- | --- |
| `task_adapter__github_projects__task_query` | `task-adapter-github-projects-read` |
| `task_adapter__github_projects__task_preflight` | `task-adapter-github-projects-write` |
| `task_adapter__github_projects__task_apply` | `task-adapter-github-projects-write` |

`.codex-plugin/plugin.json` は valid Codex manifest とし、`plugin.yaml` と `register(ctx)` の tool registration を exact alignment test で固定する。adapter は model が直接 provider arguments を作る primary workflow ではなく、task-management から固定 route で呼ばれる runtime seam である。

## Host-owned adapter config

adapter config は `TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE` から読む `contract_version = 1` の host-owned file とする。credential は保存しない。

```toml
contract_version = 1

[mcp_tools]
projects_list = "mcp__github__projects_list"
projects_get = "mcp__github__projects_get"
projects_write = "mcp__github__projects_write"
issue_write = "mcp__github__issue_write"
add_issue_comment = "mcp__github__add_issue_comment"

[host_attestation]
projects_toolset_enabled = true
issue_write_enabled = true
comment_write_enabled = true
raw_mcp_exposure = "adapter_only"
adapter_write_exposure = "task_management_only"

[destinations.portfolio_tasks]
destination_ref = "tasks:portfolio-os"
owner = "example-owner"
project_number = 7

[content_targets.portfolio_issues]
content_target_ref = "task-content:portfolio-os"
owner = "example-owner"
repository = "example-repository"
```

GitHub owner、project number、repository、field / option mapping は adapter-private config であり、task-management route や public operation に出さない。token、authorization header、environment credential value はこの file に保存しない。

MCP tool 名は exact `mcp__<server>__<tool>` pattern と、operation ごとの allowlist に一致する必要がある。arbitrary tool dispatch、caller-supplied tool name、dynamic fallback は拒否する。

## Field mapping

canonical field mapping は adapter config が field display name、expected GitHub type、canonical enum から option label への変換を所有する。raw field / option node ID を public contract に出さない。

初期 required mapping は少なくとも次を対象にする。

- `work_unit_id` / `work_unit_name`
- `task_type`
- `due_date`
- `urgency`
- `importance`
- `automation_mode`
- `approval_required`
- safe source label / URL when configured

destination field が存在しない場合は `required_field_missing`、type が合わない場合は `field_type_mismatch` とする。adapter は schema を作成・修復しない。

## Preflight

adapter preflight は write side effect を起こさない。次を実行する。

1. adapter contract version、operation、opaque refs、config version を strict validation する。
2. exact MCP tool allowlist と host attestation を検証する。
3. `projects_get` / `projects_list` の read-only call で Project、fields、既存 item の read capability を確認する。
4. create の場合は `content_target_ref` と repository mapping を検証する。
5. operation に必要な configured write capability attestation を確認する。
6. canonical field mapping と expected GitHub field type を検証する。
7. safe expected side effects を deterministic order で返す。

Hermes の公開 plugin Interface は他 tool の dispatch を提供するが、model-facing enablement inventory は提供しない。このため adapter は private registry introspection を行わない。preflight v1 では host attestation と read-only probe を組み合わせ、attestation がない、`raw_mcp_exposure != "adapter_only"`、または `adapter_write_exposure != "task_management_only"` の場合は fail closed にする。apply 時の unknown tool / disabled tool responseも `tool_disabled` へ正規化する。

adapter runtime tools は global registry に必要だが、write toolset を model / child agent が直接選べる状態にはしない。task-management の fixed internal dispatch だけを許す host policy とする。receipt は cryptographic capability ではないため、direct adapter invocation の防止はこの host exposure seam が所有する。

preflight code mapping:

| condition | code |
| --- | --- |
| MCP call が unknown / unavailable | `adapter_unavailable` または `tool_disabled` |
| auth がない | `auth_missing` |
| Project / repository 権限不足 | `permission_failure` |
| opaque ref を config で解決できない | `destination_unresolved` |
| field 不在 | `required_field_missing` |
| field type 不一致 | `field_type_mismatch` |
| write tool attestation 不足 | `capability_mismatch` |
| raw MCP tool が child / model に無制限露出 | `unsafe_delegation_exposure` |

preflight success は task-management approval ではなく、adapter apply を単独で許可しない。

## Provider operations

### `task.create`

1. `issue_write(method=create)` で Issue を作る。
2. returned Issue URL / number を adapter 内部で保持し、safe opaque task ref を作る。
3. `projects_write(method=add_project_item)` で Issue を Project に追加する。
4. `projects_write(method=update_project_item)` を field ごとに呼ぶ。
5. `projects_get` または `projects_list` で item / field を read-back する。
6. `created` success または typed partial failure を返す。

expected side effects は generic `content.create`、`destination.attach`、`fields.update`、`task.read_back` の順に固定し、それぞれの safe description で linked GitHub Issue と GitHub Project mutation を人間に示す。Project-native item は作らない。

### `task.update`

task_ref から Issue と Project item を adapter 内部で解決する。title / body の変更は `issue_write(method=update)`、canonical fields は `projects_write(method=update_project_item)`、最後に read-back を行う。変更対象が空、task_ref が解決不能、field mapping が不完全なら write 前に止める。

### `task.comment`

task_ref を linked Issue に解決し、`add_issue_comment` を 1 回呼び、必要な safe read-back 後に `commented` を返す。

### `task.report`

structured report を deterministic Markdown に render し、`add_issue_comment` を 1 回呼ぶ。見出しは summary、work performed、verification、residuals の順に固定し、`reported` を返す。Project status update は呼ばない。

### `task.query`

`projects_list` / `projects_get` の pagination を adapter 内に閉じ込め、canonical filters を provider query または post-filter へ変換する。result は `adapter_contract_version: 2` の normalized snapshot で、raw GraphQL result を含めない。

## Idempotency と partial failure

adapter は backend-specific duplicate prevention を所有する。初期実装では persistent local store を追加しない。

- create 前に source_ref、title、destination、content target から safe idempotency fingerprint を算出し、configured search/read で既存 Issue / item を確認する。
- official MCP surface で確実な duplicate check ができない場合、preflight / result に human action を出し、blind retry を retryable にしない。
- Issue create 後に Project add が失敗した場合、`partial_update_failure`、stage `project_item_add`、created Issue の safe task_ref / URL を返す。
- Project add 後に field update が失敗した場合、stage `project_fields_update` とし、blind create retry を禁止する。
- comment / report の timeout で write outcome が不明な場合、`provider_failure`、retryable false、human action で Issue を確認するよう返す。
- rate limit など write 未実行が確実な failure だけ retryable true にできる。

## Adapter result

adapter は task-management が allowlist normalization できる次の safe fields だけを返す。

- `adapter_contract_version`
- `ok`
- `status`
- `operation_type`
- `backend_key`
- `destination_ref`
- safe `task_ref`、HTTPS URL、title
- `retryable`
- `human_action`
- typed `error_type`、`code`、safe message、stage
- deterministic `expected_side_effects` for preflight

raw provider payload、GraphQL node ID、repository ID、project field ID、option ID、token、authorization、request / response headers、stack trace は返さない。adapter safety validator は unexpected fields と credential-like data を contract violation にする。

## Test strategy

normal tests は fake dispatcher と static official-shape fixtures を使う。

- config version / exact tool allowlist / opaque ref resolution
- preflight blocker taxonomy と readiness-not-approval
- create orchestration order、linked Issue only、field update、read-back
- update / comment / report method mapping
- pagination と normalized query
- partial failure 各 stage、retryability、safe human action
- idempotency / duplicate handling
- raw ID / secret / raw payload leakage rejection
- Hermes manifest / runtime registration alignment
- task-management shared adapter fixture compatibility
- hermetic smoke。live GitHub、live MCP、credential は不要

## Live Activation Gate

repo 実装完了は live activation 完了ではない。次は別の明示承認を必要とする。

- GitHub MCP server registration / update
- projects toolset / issue write / comment tool enablement
- credential / auth / permission changes
- Hermes profile / plugin install / enable / environment changes
- real destination mapping の配置
- live preflight / live write smoke
- GitHub Project / Issue の作成・更新

live smoke を承認する場合も、最初は read-only preflight、次に人間が確認した専用 test operation の順に gate を分ける。

## Acceptance criteria

- separate plugin の public code に task-management import または direct GitHub client がない。
- task-management 本体に GitHub 固有 branch、field mapping、MCP method name がない。
- `task.create` は linked Issue create だけを実装し、draft item 概念を持たない。
- preflight / query / apply が executable で、normal tests は fake dispatcher で完結する。
- auth / permission / destination / field / capability / unsafe delegation が typed result になる。
- create / update の部分成功が safe task ref を保持した partial failure になる。
- raw provider data と credential が task-management public result に到達しない。
- manifest、runtime registration、dual-host validator、plugin-creator validator が通る。

## 関連ページ

- [Task Management Write / Preflight Interface 仕様](task-management-write-preflight-interface-spec.md)
- [Task Management Write / Preflight 実装計画](2026-07-21-task-management-write-preflight-implementation-plan.md)
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md)

## 出典

- [GitHub MCP Server repository](https://github.com/github/github-mcp-server)
- [GitHub MCP Server Projects source at audited revision](https://github.com/github/github-mcp-server/blob/9d130049e9074772c2afbbd5e904725d240443ad/pkg/github/projects.go)
- [GitHub Docs: configure MCP toolsets](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp-in-your-ide/configure-toolsets)
- [GitHub MCP Projects Route reference](../../../plugins/task-management/skills/task-management/references/github-mcp-projects.md)
- current runtime audit: `/Users/omitsuhashi/.hermes/hermes-agent/hermes_cli/plugins.py` の `PluginContext.register_tool` / `dispatch_tool`（repo 外の live source は変更していない）
