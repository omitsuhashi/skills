# Task Management Write / Preflight Interface 仕様

## 状態

2026-07-21 Spec Gate承認済み。2026-07-22にtask-management `0.4.0`、separate GitHub Projects Adapter `0.1.0`、public fake end-to-endをlocal実装・検証し、POTASK-019の独立implementation review cycle 2も`approved`で完了した。reviewed head `cfcd1ab`はEpic Baseへlocal統合済みである。GitHub Issue mirror、push、PR作成、shared `main`へのmerge、live install / profile / MCP registration / credential setup / real GitHub Project・Issue操作 / live smokeは未実施で、remote deliveryとLive Activation Gateとして別途扱う。

この仕様はCompaniesへ渡すpublic Interface v2の唯一のnormative referenceである。承認済みInterface設計、DAG、plugin責務、remote / live policyは変更していない。current implementation / review状態は[Portfolio OS Task Backend Plugin Skill Issues](portfolio-os-task-backend-plugin-skill-issues.md)で追跡する。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## Spec Gate時点の問題設定

2026-07-21 audit時点の`plugins/task-management` v0.3.0は、Hermes runtimeで`task_query`だけを登録し、`task-management-read`だけをexportしていた。`TaskDraft`、`TaskWriteResult`、Adapter Dispatch Review、GitHub readinessは文書とfixtureに存在したが、`task_preflight`、`task_apply`、approval binding、write adapter dispatchは実行できなかった。

この差を埋める際、task-management を GitHub payload の pass-through や provider client にしてはならない。consumer が理解する Interface は少数に保ち、route selection、preflight、approval identity、adapter dispatch、result normalization、secret / raw provider data の遮断を深い Module の内側へ置く。

## 成功条件

- Hermes runtime と `plugin.yaml` の両方に `task_preflight`、`task_apply`、`task-management-write` が存在する。
- 公開 Interface は `task_query`、`task_preflight`、`task_apply` の 3 つに留める。
- `TaskBackendAdapter` の wire Interface は `query`、`preflight`、`apply` の 3 operation に留め、provider 別 CRUD method を task-management に公開しない。
- `task.create`、`task.update`、`task.comment`、`task.report` を扱い、delete は扱わない。
- 承認後に operation、route、destination、task content、fields、expected side effects のいずれかが変わった場合は dispatch しない。
- 確証がない task は外部 backend に作成せず、人間へ preview を提示して同意を求める。
- 十分な確証があり、機械的な不確実性もない場合だけ `confidence_authorized` を許す。
- preflight pass と write approval を別の状態・別の test として扱う。
- result は backend-neutral で、credential、GitHub raw ID、raw provider payload を含まない。
- route 未設定、version mismatch、capability mismatch は fail closed にする。
- `local_json` は test / smoke fixture のままで、runtime backend、canonical task store、persistent ledger にしない。

## 採用した判断

- task-management を `task_query`、`task_preflight`、`task_apply` の深い Module とする。
- GitHub 固有 Implementation は separate `task-adapter-github-projects` Adapter に隔離する。
- approval binding は canonical ApprovalPreview、SHA-256 digest、minimal receipt を使う。
- 確証がない operation は外部 write 前に人間へ確認し、十分な確証と機械的 eligibility がある場合だけ `confidence_authorized` を許す。
- route v1 は compatibility wrapper を残さず unified route v2 へ clean break する。
- 初期 create は linked Issue only とし、Project-native draft item / `content_policy` を追加しない。
- `task.report` は structured work report とし、Project-wide status update と分離する。

## Spec Gate audit evidence

2026-07-21 の current checkout で次を確認した。

- branch は `main`、HEAD と current `origin/main` は `cab8bd88351727f3495b657df447f7f64aa881d1` で一致した。
- user-owned untracked file `skills/llm-wiki/DESCRIPTION.md` が存在する。本作業では変更しない。
- task-management focused tests は 97 件成功した。
- plugin-creator validator、skill-creator quick validation、dual-host validator、Hermes read smoke、`git diff --check` は成功した。
- `plugin.yaml`、Codex manifest、runtime `register(ctx)` は read-only である。
- current route は `TASK_MANAGEMENT_READ_ROUTES_FILE`、`contract_version = 1`、capability `task_read` だけを扱う。
- Hermes Agent v0.19.0 の公開 `PluginContext.dispatch_tool(name, args)` は、登録済みの built-in / MCP / other-plugin tool を呼び出せる。
- 同じ公開 `PluginContext` Interface には、model-facing tool enablement や registry inventory を検証する operation がない。adapter は Hermes 内部 registry へ依存しない。
- official GitHub MCP Server current main `9d130049e9074772c2afbbd5e904725d240443ad` の Projects surface は、Issue / Pull Request の Project 追加、field update、read-back、Project status update を提供するが、Project-native draft item create は提供しない。

## 責任分界

| 所有者 | 所有するもの | 所有しないもの |
| --- | --- | --- |
| task-management | backend-neutral contracts、route selection、approval preview / digest、apply 前の identity check、adapter wire validation、result / error normalization、public data leakage guard | canonical task state、persistent task store、provider IDs、credentials、GitHub field mapping、MCP registration、provider retry implementation |
| TaskBackendAdapter | opaque destination 解決、backend operation、backend-specific preflight、idempotency、partial failure、safe adapter result | task-management public approval policy、public raw payload、host profile mutation |
| caller / host | task content の意味上の確証、人間への preview 表示、approval actor の認証、route / adapter config、live activation | approval 後の内容変更、provider-specific public contract の要求 |
| external backend | mutable task state の source of truth | Portfolio OS local ledger への同期要求 |

## Deep Module review

consumer が学ぶ Interface は `task_query`、`task_preflight`、`task_apply` と backend-neutral contracts に限定される。routing、canonicalization、approval binding、re-preflight、adapter dispatch、error / result normalization、leakage guard は task-management Module の Implementation に隠す。

deletion test では、task-management Module を削除すると、各 caller が route resolution、approval identity、provider result safety を重複実装しなければならない。したがって単なる pass-through ではなく、複雑性を一か所へ集めて caller に leverage を与える。Adapter seam は test / smoke fake と GitHub Projects Adapter の少なくとも 2 implementations を持つため、仮想的な拡張点ではない。内部 `approval.py` や `normalization.py` は testable な internal seam であり、caller の Interface には追加しない。

## 用語

- **OperationEnvelope**: backend-neutral な write intent。provider tool 名や provider ID を含まない。
- **ApprovalPreview**: preflight 後に task-management が canonicalize した review 対象。operation と route binding と expected side effects を固定する。
- **ApprovalDigest**: ApprovalPreview の同一性を検証する SHA-256 digest。署名や user identity proof ではない。
- **ApprovalReceipt**: caller / host が approval decision と対象 digest を task-management へ渡す最小 receipt。
- **Readiness**: adapter と destination が operation を実行できる状態。approval ではない。
- **RouteBinding**: host route の exact adapter tool set を task-management 内部で固定した binding。public preview には safe adapter key と opaque binding digest だけを出す。

## 公開 Interface

### `task_query`

既存の model-facing request と `TaskSnapshotResult` を維持する。内部 route contract だけを v2 に切り替える。consumer は tool name、provider ref、file path、GitHub owner / project numberを入力しない。

### `task_preflight`

`task_preflight` は `interface_version: 2` と `operation` を受ける。request の概念形は次の通り。

```yaml
interface_version: 2
operation:
  operation_type: task.create
  backend_key: remote_tasks
  destination_ref: tasks:default
  task_ref: null
  payload:
    task:
      title: Implement write facade
      body: Add approval-bound task apply.
      work_unit_id: portfolio-os
      work_unit_name: Portfolio OS
      task_type: implementation
      due_date: null
      urgency: normal
      importance: high
      automation_mode: assistive
      approval_required: true
      source_ref:
        kind: conversation
        ref: source:opaque
        label: Approved planning discussion
      fields:
        review_notes: []
```

operation-specific payload は次に固定する。

| operation_type | task_ref | payload |
| --- | --- | --- |
| `task.create` | 禁止 | full `TaskDraft` を `payload.task` に持つ |
| `task.update` | 必須 | backend-neutral patch を `payload.changes` に持つ |
| `task.comment` | 必須 | non-empty `payload.comment.body` を持つ |
| `task.report` | 必須 | `summary`、`work_performed`、`verification`、`residuals` を `payload.report` に持つ |

`task_ref` は existing backend-neutral `TaskRef` shape とし、create 以外では `backend_key`、opaque `task_ref`、safe URL / title を持つ。`payload.changes` は non-empty object で、`title`、`body`、`work_unit_id`、`work_unit_name`、`task_type`、`due_date`、`urgency`、`importance`、`automation_mode`、`approval_required`、`source_ref`、`fields` だけを許す。`payload.report.summary` は non-empty string、`work_performed` と `verification` は non-empty string list、`residuals` は string list とする。

`task.comment` は短い会話的な補足、`task.report` は作業内容・結果・検証・残件を持つ structured work report とする。GitHub adapter が両方を Issue comment へ変換しても、operation type と success status は `commented` / `reported` として区別する。Project 全体の status update は `project.report` などの将来契約であり、本 scope には含めない。

成功した preflight は `TaskPreflightResult` を返す。

```yaml
result_type: TaskPreflightResult
ok: true
status: ready
operation_type: task.create
backend_key: remote_tasks
destination_ref: tasks:default
approval_mode: human_required
approval_preview:
  preview_version: 1
  operation: {}
  destination:
    backend_key: remote_tasks
    destination_ref: tasks:default
    destination_label: Default tasks
    content_target_ref: task-content:default
  route_binding:
    adapter_key: github_projects
    binding_digest: sha256:...
  expected_side_effects:
    - effect_type: content.create
      description: Create a linked GitHub Issue.
    - effect_type: destination.attach
      description: Add the linked task to the configured GitHub Project.
    - effect_type: fields.update
      description: Update the reviewed task fields.
    - effect_type: task.read_back
      description: Read the resulting task state.
approval_digest: sha256:...
readiness:
  ok: true
  checks: []
error: null
```

preflight failure は `approval_preview` と `approval_digest` を発行せず、typed blocker を返す。preflight pass は write approval ではない。

### `task_apply`

`task_apply` は caller が編集し直した operation ではなく、`task_preflight` が返した exact `approval_preview` と minimal receipt を受ける。

```yaml
interface_version: 2
approval_preview: {}
approval_receipt:
  receipt_version: 1
  decision: approved
  operation_digest: sha256:...
```

`decision` は次の 2 値だけを許す。

- `approved`: 人間が preview を確認し、同じ digest を明示承認した。
- `confidence_authorized`: caller が task intent に十分な確証を持ち、下記の機械的条件をすべて満たしたため、人間確認を省略した。

receipt は署名済み user identity proof ではない。approval actor の認証、会話 UI、audit trail は caller / host が所有する。task-management は receipt の digest binding と policy compliance だけを検証する。

## 確証と human confirmation policy

task-management は task の意味上の正しさを完全には判定できない。このため caller / host は次の運用を守る。

1. task の必要性、内容、work unit、destination、side effect に確証がなければ、外部 write を行わない。
2. `task_preflight` で preview を作り、「この内容で作成・更新してよいですか」と人間へ確認する。
3. 修正があれば新しい operation で preflight をやり直し、新しい digest を承認対象にする。
4. 十分な evidence があり、下記の eligibility も満たす場合だけ `confidence_authorized` を使う。

task-management は次のいずれかで `approval_mode: human_required` を強制する。

- `TaskDraft.approval_required` が true。
- `fields.review_notes` に未解決事項が 1 件以上ある。
- adapter preflight が `requires_human_confirmation` を返す。
- destination、task reference、required task content、field mapping、expected side effect が一意に解決できない。
- prior preview から route または side effect が変わった。

missing required field や unresolved destination は human approval で上書きせず、setup / validation blocker にする。`confidence_authorized` は `approval_mode: confidence_eligible` で、preflight が pass し、上記の未解決条件がない場合だけ許す。`automation_mode` は作成後の task execution policy であり、task creation approval の代替ではない。

## Approval binding

canonical digest は project-local の deterministic JSON rules をリポジトリ内で明文化・実装し、UTF-8 bytes に SHA-256 を適用して `sha256:<lowercase hex>` とする。digest 対象値は `null`、boolean、integer、string、array、object に限定し、float、duplicate key、NaN / Infinity、unknown runtime type を拒否する。string は NFC に正規化し、object key sort と compact separators を使う。同じ canonicalized value を preview と adapter dispatch の両方に使うため、表示対象と実行対象が別表現にならない。

digest input は次をすべて含む。

- interface / preview version
- `operation_type`
- `backend_key`
- `destination_ref`
- `task_ref`
- operation-specific payload の task content / fields
- safe destination label と `content_target_ref`
- exact query / preflight / apply tool route から task-management が作る route binding digest
- ordered canonical expected side effects

`task_apply` は dispatch 直前に route file を再読込し、adapter preflight を再実行し、ApprovalPreview を canonicalize し直す。receipt digest、preview digest、current route binding、current expected side effects のいずれかが一致しなければ `approval_mismatch` とし、adapter apply を呼ばず、新しい preview を要求する。

digest は tamper-evident identity binding であって secret ではない。task-management は signing key、approval database、queue、dispatcher、result store を持たない。

## Routing contract v2

read-only route v1 は clean break で廃止する。repo 内利用監査では plugin 外 consumer がなく、write / preflight を追加する前に単一 contract へ揃える方が安全である。

- environment: `TASK_MANAGEMENT_ROUTES_FILE`
- top-level: `contract_version = 2`
- backend fields: `adapter_key`、`query_tool`、`preflight_tool`、`apply_tool`
- destination fields: `public_ref`、`destination_label`、optional `content_target_ref`
- tool name は host-owned config から解決し、public model input にしない。
- `provider_ref` は廃止する。provider mapping は adapter-owned config に置く。
- credential、token、GitHub raw ID は保存しない。
- file missing、route missing、unknown key、duplicate public ref、tool pattern mismatch、capability mismatch は fail closed にする。
- implicit GitHub fallback や direct GraphQL / `gh` fallback は作らない。

概念例:

```toml
contract_version = 2
default_backend = "remote_tasks"

[backends.remote_tasks]
adapter_key = "github_projects"
query_tool = "task_adapter__github_projects__task_query"
preflight_tool = "task_adapter__github_projects__task_preflight"
apply_tool = "task_adapter__github_projects__task_apply"

[backends.remote_tasks.destinations.default]
public_ref = "tasks:default"
destination_label = "Default tasks"
content_target_ref = "task-content:default"
```

task-management は exact adapter tool trio が同じ adapter namespace に属することを検証する。GitHub 固有 mapping はここに置かない。

## Adapter wire contract

別 distribution 間で Python module を import しない。共有 seam は JSON-compatible な `adapter_contract_version: 2` の wire contract とし、normative fixtures と双方の contract tests で同期する。

- adapter query: normalized query と opaque destination を受け、normalized snapshots を返す。
- adapter preflight: operation intent、opaque destination / content target、required capability を受け、safe readiness、expected side effects、approval hints を返す。
- adapter apply: preflight 済み operation と task-management が固定した operation digest を受け、safe adapter result を返す。

adapter は task-management の receipt を検証したことを信用せず、少なくとも operation type、destination、required field を自分の seam でも検証する。adapter は provider raw result を wire result に含めない。

`expected_side_effects` は backend-neutral `effect_type` と safe human-readable `description` の ordered list とする。task-management は effect type、件数、文字列長、credential / raw ID absence を検証するが、GitHub 固有の method 名を hard-code しない。adapter が返した side effect list は preview / digest に入り、apply 時の re-preflight で exact match を要求する。

## Executable preflight taxonomy

task-management は adapter response を次の stable code に正規化する。

| code | class | retryable | dispatch |
| --- | --- | --- | --- |
| `adapter_unavailable` | setup blocker | false | stop |
| `tool_disabled` | setup blocker | false | stop |
| `auth_missing` | setup blocker | false | stop |
| `permission_failure` | setup blocker | false | stop |
| `destination_unresolved` | setup blocker | false | stop |
| `required_field_missing` | setup blocker | false | stop |
| `field_type_mismatch` | setup blocker | false | stop |
| `unsafe_delegation_exposure` | safety blocker | false | stop |
| `capability_mismatch` | setup blocker | false | stop |
| `approval_required` | approval blocker | false | stop |
| `approval_mismatch` | approval blocker | false | stop and re-preview |

adapter / MCP の transport timeout や rate limit は provider failure として retryable にできるが、preflight pass や approval pass に変換しない。

## TaskWriteResult v2

public result は次の allowlist だけを持つ。

```yaml
result_type: TaskWriteResult
ok: false
status: partial
operation_type: task.create
backend_key: remote_tasks
destination_ref: tasks:default
task_ref:
  backend_key: remote_tasks
  task_ref: task:opaque
  task_url: https://github.com/example/example/issues/42
  title: Implement write facade
retryable: false
human_action: Inspect the linked task before retrying field updates.
error:
  error_type: partial_failure
  code: partial_update_failure
  message: Task content was created but one or more project fields were not updated.
  stage: project_fields_update
```

`status` は success で `created`、`updated`、`commented`、`reported`、failure で `blocked`、`failed`、`partial` を許す。`error.error_type` は `setup_blocker`、`provider_failure`、`partial_failure`、`approval_failure`、`contract_failure` のいずれかとする。

`task_ref` の opaque ref、HTTPS URL、title は公開可とする。GraphQL node ID、repository ID、project field ID、option ID、token、auth header、raw provider response、trace dump は公開しない。unknown adapter field は捨てるのではなく contract violation として fail closed にし、safe error へ置き換える。

## Security / safety seam

- public input と public result の両方に credential-like key / value detector と raw provider ID denylist を適用する。
- safe URL は `https` のみを許し、userinfo、query credential、fragment credential を拒否する。
- raw adapter exception text をそのまま返さない。
- task-management は Hermes internal registry、private manager field、GitHub credential storeを参照しない。
- state-changing raw MCP tool は model-facing Interface として task-management から export しない。
- host attestation が unsafe delegation exposure を否定できない場合、preflight は fail closed にする。

## Migration

- repo contract は route v2 へ clean break する。
- `TASK_MANAGEMENT_READ_ROUTES_FILE` と `TASK_MANAGEMENT_READ_ADAPTER_TOOL` の compatibility wrapper は残さない。
- `task_query` の public request / result は回帰維持する。
- route v1 example、tests、docs は v2 に同時更新する。
- live Hermes profile に旧 environment が存在するかの確認、new route file の配置、plugin install / enable、MCP registration / tool enablement は別の Live Activation Gate で行う。

## Companies へ渡す versioned contract

Companies repo は変更しない。handoff contract は `task-management public interface version 2` とし、consumer が依存してよい surface を次に限定する。

- read toolset `task-management-read`: `task_query`
- write toolset `task-management-write`: `task_preflight`、`task_apply`
- operation: `task.create`、`task.update`、`task.comment`、`task.report`
- approval receipt version 1: `approved | confidence_authorized` と `operation_digest`
- result: `TaskSnapshotResult`、`TaskPreflightResult`、`TaskWriteResult`
- consumer input: backend-neutral operation、opaque `destination_ref`、opaque `task_ref`
- consumer が依存しないもの: adapter tool name、MCP tool name、provider ref、GitHub mapping、credential、route file path

Companies integration は、uncertain task では `task_preflight` の preview を人間へ提示し、approved digest を `task_apply` へ渡す。confidence-authorized path は caller が意味上の確証を持つ場合だけ使う。

## Non-goals

- Project-native draft item と `content_policy` enum
- task delete
- canonical task state、persistent local store、custom queue / dispatcher / result store
- approval signing service、approval actor database
- GitHub schema create / repair
- direct GitHub GraphQL、REST、`gh` fallback
- credential / permission provisioning
- MCP server registration、Hermes profile edit、live plugin install
- batch approval、policy engine、Project-wide status report

## Acceptance criteria

- manifest / runtime registration alignment tests が read と write toolset の exact set を検証する。
- approval digest の同値・差分・canonicalization tests が、全 binding field の変更で dispatch 0 回になることを検証する。
- `confidence_authorized` は eligibility を満たす場合だけ dispatch できる。
- human-required operation は `approved` receipt なしに dispatch できない。
- preflight success と apply approval が別 tests で証明される。
- route v1 env / wrapper が production code と docs から除去される。
- adapter result に raw provider field が 1 つでも含まれれば public success にしない。
- existing `task_query` consumer contract と local fixture smoke が回帰しない。
- normal tests は network、credential、live Hermes / GitHub state を要求しない。

## Issue 分解方針

Spec Gate commit 後、既存 canonical ledger [Portfolio OS Task Backend Plugin Skill Issues](portfolio-os-task-backend-plugin-skill-issues.md) に POTASK follow-up issues を追加する。分解順は shared contract / route v2、approval / public facade、normalization、GitHub Adapter scaffold / config、GitHub preflight / query、GitHub apply orchestration、docs / manifests / full verification とし、各 issue は日本語 acceptance criteria、write scope、verification、blocker edge を持つ。詳細な file-level 順序は [実装計画](2026-07-21-task-management-write-preflight-implementation-plan.md) を正本とする。

## 検証方針

通常検証は fake Adapter / fake MCP dispatcher / static fixtures で完結させる。task-management focused tests、GitHub Adapter focused tests、read / write smoke、manifest/runtime alignment、plugin / skill validators、dual-host validator、repository architecture / context tests、leakage checks、`git diff --check` を実行する。具体的な command matrix は [実装計画](2026-07-21-task-management-write-preflight-implementation-plan.md#verification-matrix) に固定する。

## 既知のリスク

- approval digest は operation identity を固定するが、approval actor の暗号学的 identity proof ではない。
- current Hermes public plugin Interface には model-facing tool inventory がないため、unsafe delegation check は host attestation と read-only probe に依存する。
- GitHub create / Project add / field update は複数 call なので部分成功し得る。blind retry を避ける typed partial result が必要である。
- official GitHub MCP Interface drift により method / schema が変わる可能性があるため、実装時に pinned fixture と current official source を再照合する。
- route v2 clean break は repo 内 compatibility wrapper を持たない。live route migration は別 Live Activation Gate が必要である。

## Gate と停止条件

- **Spec Gate**: 本仕様と GitHub Projects Adapter 仕様、file-level implementation plan を承認する。
- **Issue Gate**: 承認後に既存 local ledgerへ follow-up issues を追加し、blocker graph、acceptance、write scope を承認する。
- **Execution Plan Gate**: `issue-implementation-loop` の input packet / execution envelope を準備し、local-only delivery policy を確認する。
- **Live Activation Gate**: repo 実装・通常検証完了後、live Hermes / MCP / credential / GitHub destination を変更する前に別途明示承認を得る。

Spec / Issue Gate 前の実装、unknown provider capability の推測、approval mismatch 後の dispatch、credential / project / issue / MCP / profile の live 変更で停止する。

## 関連ページ

- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- [Portfolio OS Task Backend Plugin Skill Issues](portfolio-os-task-backend-plugin-skill-issues.md)
- [GitHub Projects Adapter 仕様](task-adapter-github-projects-spec.md)
- [Task Management Write / Preflight 実装計画](2026-07-21-task-management-write-preflight-implementation-plan.md)
- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md)

## 出典

- [plugins/task-management/plugin.yaml](../../../plugins/task-management/plugin.yaml)
- [plugins/task-management/__init__.py](../../../plugins/task-management/__init__.py)
- [plugins/task-management/task_management/read_adapter.py](../../../plugins/task-management/task_management/read_adapter.py)
- [plugins/task-management/task_management/route_config.py](../../../plugins/task-management/task_management/route_config.py)
- [Task Contracts](../../../plugins/task-management/skills/task-management/references/task-contracts.md)
- [Adapter Dispatch Contract](../../../plugins/task-management/skills/task-management/references/adapter-dispatch.md)
- [GitHub MCP Server repository](https://github.com/github/github-mcp-server)
- [GitHub MCP Server Projects source at audited revision](https://github.com/github/github-mcp-server/blob/9d130049e9074772c2afbbd5e904725d240443ad/pkg/github/projects.go)
- [GitHub Docs: configure MCP toolsets](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp-in-your-ide/configure-toolsets)
