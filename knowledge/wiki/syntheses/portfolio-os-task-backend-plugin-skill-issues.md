# Portfolio OS タスクバックエンドプラグイン / スキル Issue Ledger

## 状態

Issue Gate / Execution Plan Gate 承認済み。POTASK-001 から POTASK-009 は local `PR_READY`。2026-07-15 に追加承認された POTASK-010 は local 実装・検証済みでPR delivery対象。2026-07-16 に追加承認された POTASK-011 は、backend差をconsumerから隠すpluggable provider adapterとHermes end-to-end call pathを追加する。implementation review 2 cyclesのskills-side Critical / Importantは対応済みで、current companies preflight がHermes `plugin.yaml` exportを読まないcross-repo blockerだけが残る。PR delivery は承認済み。GitHub issue mirror と merge はまだ行わない。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## 前提

- 正本仕様: [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- 初回実装 scope は task taxonomy、`TaskDraft` composition、backend / destination routing、adapter operation envelope、preview / guard、typed result mapping まで。POTASK-010 ではbackend-neutral read facade、POTASK-011ではhost-owned routeとpluggable read-only provider adapterを追加する。
- 外部 adapter の実 write 方針、GitHub Projects mutation、GitHub issue / PR、push、PR creation、merge は adapter / host / delivery workflow の責務であり、この ledger の実装対象外。
- GitHub MCP Server 自体の read/write live smoke test は行わない。通常検証は固定テストデータ / 模擬 tool を使う。
- local issue ledger を canonical とし、GitHub issues は未作成の optional mirror とする。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | 実装結果 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `portfolio-os-task-backend-plugin-skill` | POTASK-001 | `plugins/task-management/` の plugin scaffold と primary skill skeleton を作る | 承認済み | 完了 | `PR_READY` `248d7a4a50e90f9ce05515cae5c05251b769c978` | なし | POTASK-002, POTASK-003, POTASK-004 | 未作成 | approved: `341d776703b837f3bd148965ba8c6ee8e3633bdf..248d7a4a50e90f9ce05515cae5c05251b769c978` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-002 | backend-neutral contract と固定テストデータを定義する | 承認済み | 完了 | `PR_READY` `ed250ca6fe2c1ea38af05bba26a0cd3511413bf8` | POTASK-001 | POTASK-005, POTASK-006, POTASK-007 | 未作成 | approved: `248d7a4a50e90f9ce05515cae5c05251b769c978..ed250ca6fe2c1ea38af05bba26a0cd3511413bf8` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-003 | task taxonomy と `TaskDraft` composition reference / examples を作る | 承認済み | 完了 | `PR_READY` `b2ad95a06c0643c4486d1ef05bc6034d958be1f1` | POTASK-001 | POTASK-005, POTASK-006 | 未作成 | approved: `248d7a4a50e90f9ce05515cae5c05251b769c978..b2ad95a06c0643c4486d1ef05bc6034d958be1f1` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-004 | backend / destination routing config と reference を作る | 承認済み | 完了 | `PR_READY` `c724ee94dd4dae3d74c5e52564f8eded52b69dfb` | POTASK-001 | POTASK-006, POTASK-007, POTASK-008 | 未作成 | approved: `248d7a4a50e90f9ce05515cae5c05251b769c978..c724ee94dd4dae3d74c5e52564f8eded52b69dfb` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-005 | `work_unit_id` / `work_unit_name` の解決と preview contract を実装する | 承認済み | 完了 | `PR_READY` `c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386` | POTASK-002, POTASK-003 | POTASK-006 | 未作成 | approved: `b2ad95a06c0643c4486d1ef05bc6034d958be1f1..c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-006 | adapter operation envelope と Adapter Dispatch Review guard を実装する | 承認済み | 完了 | `PR_READY` `0ce0ffa6eae53b7f085e64af1a453749f82cc3ba` | POTASK-002, POTASK-003, POTASK-004, POTASK-005 | POTASK-007, POTASK-009 | 未作成 | approved: `c46d02023e1b9d8fc58fa9e2a57dde1c51d1a386..0ce0ffa6eae53b7f085e64af1a453749f82cc3ba` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-007 | GitHub MCP route preflight と typed result mapping を実装する | 承認済み | 完了 | `PR_READY` `ed62de954b57ff4c5b32f6efaa6098843d85c1ac` | POTASK-002, POTASK-004, POTASK-006 | POTASK-008, POTASK-009 | 未作成 | approved: `0ce0ffa6eae53b7f085e64af1a453749f82cc3ba..ed62de954b57ff4c5b32f6efaa6098843d85c1ac` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-008 | Hermes adapter availability runbook と governance reference を作る | 承認済み | 完了 | `PR_READY` `06f9b6fc7801271f345a8c2772a6d64e7c64f310` | POTASK-004, POTASK-007 | POTASK-009 | 未作成 | approved: `ed62de954b57ff4c5b32f6efaa6098843d85c1ac..06f9b6fc7801271f345a8c2772a6d64e7c64f310` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-009 | docs / examples / verification / handoff boundary を統合する | 承認済み | 完了 | `PR_READY` `214349fff56bd55ff3e7e68612a499096096803f` | POTASK-006, POTASK-007, POTASK-008 | なし | 未作成 | approved: `06f9b6fc7801271f345a8c2772a6d64e7c64f310..214349fff56bd55ff3e7e68612a499096096803f` | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-010 | backend-neutral task read capability を実装する | 承認済み | 完了 | local verified / PR delivery対象 | POTASK-002, POTASK-007, POTASK-008 | POTASK-011 | 未作成 | PRで追跡 | [#29](https://github.com/omitsuhashi/skills/pull/29) |
| `portfolio-os-task-backend-plugin-skill` | POTASK-011 | pluggable provider adapter と Hermes end-to-end call path を実装する | 承認済み | 実装済み | worker commit / verification 済み | POTASK-004, POTASK-010 | なし | 未作成 | worker verification 済み / integration待ち | [#29](https://github.com/omitsuhashi/skills/pull/29) |

## Blocker Graph

```text
POTASK-001
├── POTASK-002
│   ├── POTASK-005
│   │   └── POTASK-006
│   │       ├── POTASK-007
│   │       │   ├── POTASK-008
│   │       │   │   └── POTASK-009
│   │       │   └── POTASK-009
│   │       └── POTASK-009
│   ├── POTASK-006
│   ├── POTASK-007
│   └── POTASK-010
│       └── POTASK-011
├── POTASK-003
│   ├── POTASK-005
│   └── POTASK-006
└── POTASK-004
    ├── POTASK-006
    ├── POTASK-007
    └── POTASK-008
```

循環依存はない。Issue Gate 承認済みのため、全 issue の `レビュー状態` は `承認済み` とする。
POTASK-010 は POTASK-002 の contract、POTASK-007 の typed adapter boundary、POTASK-008 の Hermes governance を再利用する follow-up であり、既存 issue を再開しない。POTASK-011 はPOTASK-010のpublic facadeを維持したまま、POTASK-004のroutingを実行可能なprovider adapterへ接続する。

## 依存順

1. POTASK-001
2. POTASK-002、POTASK-003、POTASK-004
3. POTASK-005
4. POTASK-006
5. POTASK-007
6. POTASK-008
7. POTASK-009
8. POTASK-010
9. POTASK-011

## Issues

### POTASK-001: `plugins/task-management/` の plugin scaffold と primary skill skeleton を作る

#### 目的

Codex / Hermes にインストール可能な薄い `task-management` plugin package を作り、初回公開 entrypoint を primary `task-management` skill 1 つに限定する。

#### Scope

- `plugins/task-management/.codex-plugin/plugin.json`
- `plugins/task-management/skills/task-management/SKILL.md`
- `plugins/task-management/skills/task-management/agents/openai.yaml`
- `plugins/task-management/config/task-backends.example.toml`
- `plugins/task-management/examples/`
- `plugins/task-management/tests/`

#### Acceptance Criteria

- plugin package は distribution / install-update / config template / examples / references の単位として成立する。
- 初回公開 skill entrypoint は `plugins/task-management/skills/task-management/` だけである。
- GitHub adapter、`gh` command planner、direct GraphQL client、MCP server 実装は存在しない。
- `plugin-creator` validator と `skill-creator` quick validation の対象 path が成立する。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
```

### POTASK-002: backend-neutral contract と固定テストデータを定義する

#### 目的

`TaskDraft`、`TaskRef`、`TaskQuery`、`TaskSnapshot`、`TaskWriteResult`、`TaskBackendRoute`、`TaskBackendDestination` を backend-neutral に定義し、GitHub 固有 ID / auth / field ID を reusable skill へ漏らさない。

#### Scope

- contract reference
- fixture / mock data
- contract-oriented tests

#### Acceptance Criteria

- `TaskDraft` は `work_unit_id`、`work_unit_name`、task type、due date、urgency、importance、automation mode、approval required、source ref を表現できる。
- `TaskBackendRoute` は `kind=mcp|reader|skill|cli|url`、connection ref、capability、field override を表現できる。
- `TaskBackendDestination` は backend key、destination ref / label、必要なら content target ref を表現できる。
- `TaskRef` / `TaskSnapshot` は provider-specific raw IDs を exposed contract にしない。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-003: task taxonomy と `TaskDraft` composition reference / examples を作る

#### 目的

chat / capture text から作る task の title、body、type、importance、urgency、automation mode、approval required、source ref の付け方を定義する。

#### Scope

- `task-draft-contract.md`
- `SKILL.md` から `task-draft-contract.md` への参照導線
- task title / body examples
- task type / importance / urgency examples
- fixture-backed tests

#### Acceptance Criteria

- task title / body の構成規則が skill から参照できる。
- `work_unit_id` と `work_unit_name` の両方が preview に現れる。
- `inbox` fallback の意味が明確である。
- raw platform payload、message id、transport metadata を contract に保存しない。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-004: backend / destination routing config と reference を作る

#### 目的

「どの接続面を使うか」と「実際に task を登録する外部プロジェクト管理先」を分離する。

#### Scope

- `backend-routing.md`
- `task-backends.example.toml`
- route / destination examples
- routing tests

#### Acceptance Criteria

- plugin config は `kind`、`connection_ref`、capability、任意の field override を持つ。
- plugin config は GitHub owner、project number、repository を必須または既定値として持たない。
- destination は caller / profile / host-provided registration から `TaskBackendDestination` として渡す。
- backend keyはprovider detailを内包せず、host-owned `default_backend`で選ぶ。POTASK-011の初期稼働defaultは`local_tasks`でよい。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-005: `work_unit_id` / `work_unit_name` の解決と preview contract を実装する

#### 目的

GitHub Projects などの backend UI を人間が見たときに、ID だけでなく work unit 名でも判断できるようにする。

#### Scope

- work unit fields in `TaskDraft`
- preview rendering contract
- fallback behavior
- tests

#### Acceptance Criteria

- `work_unit_id` は stable routing key として扱われる。
- `work_unit_name` は backend 上の display label として扱われる。
- `work_unit_name` が不明な場合の fallback / human review behavior が明記される。
- preview は `work_unit_id` と `work_unit_name` を両方表示する。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-006: adapter operation envelope と Adapter Dispatch Review guard を実装する

#### 目的

task-management plugin / skill が実 write を所有せず、adapter に渡す operation envelope と dispatch 前 review を所有する構成にする。

#### Scope

- adapter-neutral operation envelope
- preview format
- per-operation explicit review guard
- `SKILL.md` から `adapter-dispatch.md` への参照導線
- fixture / mock adapter tests

#### Acceptance Criteria

- create/update/comment/report に相当する intent を adapter-neutral envelope として表現できる。
- envelope は backend key、connection ref、destination ref / label、operation type、task title/body/fields、`work_unit_id`、`work_unit_name`、adapter tool 名、expected adapter side effects を含む。
- update/comment/report envelope は既存 task を示す opaque `task_ref` を持ち、Adapter Dispatch Review の確認対象に含める。
- 明示 approval check なしに adapter dispatch envelope を渡せない。
- 外部 adapter の実 write 方針、GitHub mutation sequence、retry policy は plugin に存在しない。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-007: GitHub MCP route preflight と typed result mapping を実装する

#### 目的

GitHub MCP Server を external adapter として使う route の availability / capability / typed result を扱う。ただし GitHub MCP Server 自体の read/write は実装・live smoke test しない。

#### Scope

- GitHub MCP route reference
- preflight contract
- typed result mapping
- mock MCP tool result fixtures

#### Acceptance Criteria

- MCP server missing、tool disabled、auth missing、permission failure、project not found、field missing を typed result にできる。
- adapter result から `TaskWriteResult` へ正規化できる。
- GitHub API client、`gh` command planner、GraphQL query は存在しない。
- normal tests は live GitHub access、Hermes live profile、credentials、MCP server を要求しない。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-008: Hermes adapter availability runbook と governance reference を作る

#### 目的

Hermes Agent 側の MCP adapter availability、credential boundary、delegation boundary を plugin install の副作用から分離する。

#### Scope

- `hermes-mcp-governance.md`
- `github-mcp-projects.md`
- `examples/hermes-github-mcp-enable.example.md`
- availability / delegation guidance

#### Acceptance Criteria

- plugin install は MCP server registration、credential setup、Hermes profile edit、GitHub adapter tool enablement を行わない。
- Adapter Availability Gate は host / adapter 側の確認であり、plugin の実装副作用ではない。
- `delegation.inherit_mcp_toolsets: true` による state-changing MCP adapter tools の無条件継承リスクを明記する。
- GitHub MCP adapter tools を子 agent へ無条件継承しない guidance がある。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
```

### POTASK-009: docs / examples / verification / handoff boundary を統合する

#### 目的

仕様、skill references、examples、tests、knowledge entries を整合させ、Portfolio OS handoff boundary と migration boundary を明確にする。

#### Scope

- docs / examples consistency
- knowledge index / log updates
- validation command refresh
- no live external dependency verification

#### Acceptance Criteria

- docsはinitial local JSON backendと、MCP / provider pluginへの差し替え可能性を明記する。GitHub Projectsをimplicit defaultにしない。
- Portfolio OS は task state source of truth を持たない。
- dedicated idempotency key、`task_sha` field、duplicate-prevention store は存在しない。
- GitHub MCP Server read/write live smoke test は normal verification に含めない。
- `git diff --check` と repo-local validators が通る。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
git diff --check
```

### POTASK-010: backend-neutral task read capability を実装する

#### 目的

`TaskQuery` から host-provided read adapter を呼び、Schedule Secretary などの consumer へ provider raw ID、credential、raw payloadを漏らさない normalized `TaskSnapshotResult` を返す。Hermes runtime registration と authoritative exportを正確に `task-management-read` へ揃える。

#### Scope

- `plugins/task-management/task_management/read_adapter.py`
- `plugins/task-management/__init__.py`
- `plugins/task-management/plugin.yaml`
- `plugins/task-management/.codex-plugin/plugin.json` のversion alignment
- task read adapter reference / README / primary skill / task contracts
- behavioral tests

#### Acceptance Criteria

- Hermes は `task_query` を `task-management-read` toolset に `ctx.register_tool` で登録する。
- `plugin.yaml.exports.toolsets` は正確に `["task-management-read"]` であり、runtime registrationと一致する。
- `.codex-plugin/plugin.json` は current `plugin-creator` validatorを通る。未サポートの `exports` fieldは追加しない。
- operator-configured adapter toolは `mcp__<server>__task_query` だけを許可し、model inputから任意toolを選ばせない。
- `TaskQuery` と opaque `destination_ref` をdispatchし、canonical fieldだけを含む `TaskSnapshotResult` を返す。
- provider raw ID / unknown backend metadataはoutputから除外し、credential-like valueを含むsnapshotはgeneric typed errorでfail closedする。
- normal testsはmock dispatchを使い、live Hermes / MCP / GitHub / credentialsを要求しない。

#### Non-goals

- GitHub API / GraphQL / `gh` clientの実装。
- GitHub MCP Server registration、credential setup、profile edit、live install。
- write adapter、task mutation、GitHub issue / PR / push / merge。
- companies repositoryのpreflight変更。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
git diff --check
```

#### Current evidence

- behavioral testsはREDでadapter module、Hermes registration、manifest exportの欠落を確認後、GREENへ進めた。
- plugin test suiteは60 tests成功。
- installed Hermesの実`PluginContext` / registryでplugin moduleをloadし、`task_query`が`task-management-read`へ登録されることを確認した。
- implementation review cycle 1のprovider marker / credential検出、backend一致、canonical taxonomy / ISO date、required `backend_metadata`の指摘を修正した。
- implementation review cycle 2のquoted JSON marker bypassとunsafe link schemeを修正し、query taxonomy / date validationとguard別subtestを追加した。
- delivery branch / commit / PRはGitHub delivery recordで追跡し、live installは実施しない。

### POTASK-011: pluggable provider adapter と Hermes end-to-end call path を実装する

#### 目的

consumerがlocal file、GitHub Projects MCP、将来backendの違いを意識せず、Hermesの同じ`task_query`からnormalized `TaskSnapshotResult`を取得できるようにする。POTASK-010で外部前提だった`mcp__<server>__task_query`の実体不足を解消する。

#### Scope

- host-owned read route config / loader
- provider adapter protocol / router
- read-only local JSON provider adapter
- external MCP / provider plugin `task_query` adapter
- existing external MCP `task_query` compatibility
- Hermes temporary-profile end-to-end smoke test / runbook
- public skill / README / references / behavioral tests

#### Acceptance Criteria

- public toolは`task-management-read:task_query`、inputは`TaskQuery`とopaque logical `destination_ref`、outputは`TaskSnapshotResult`のまま変わらない。public `TaskQuery.backend_key`は省略可能でhost defaultへ解決する。
- consumer / model inputはadapter kind、MCP tool名、GitHub owner / project number / field ID、local path、route file pathを指定しない。
- host-owned routeがoptional internal `backend_key`とlogical `destination_ref`から固定adapterとprovider destinationを解決する。初期稼働defaultはlocal JSONでよい。
- local JSON adapterはrouteで固定されたhost-owned fileだけをread-onlyで読み、canonical query filter / limitを適用する。
- external tool adapterはrouteで固定された`mcp__<server>__task_query`または`task_adapter__<provider>__task_query`だけをHermes dispatchし、direct provider API / GraphQL / `gh` / credential clientを実装しない。
- provider adapter outputはpublic facadeで再normalizeされ、provider raw ID、unknown metadata、credential-like valuesを返さない。
- POTASK-010の`mcp__<server>__task_query` external adapter pathはcompatibility modeとして維持し、別provider plugin toolを同じbackend-neutral result contractで追加できる。
- temporary Hermes profileでpluginをloadし、local JSON backendを通じたpublic `task_query` callがnormalized snapshotを返す。
- external provider auth / networkはnormal testsの必須条件にしない。live connectionが用意された場合だけoptional smoke testを行う。

#### Implementation Evidence

- `route_config.py`がversioned host route、default backend、logical destination、local read-root guardを解決する。
- `provider_adapters/`がconstructor-bound dependencyを持つlocal JSON / exact MCP・plugin read adapterを共通request/result contractへ揃える。
- public `task_query`はroute envなしでもHermesへ登録され、typed setup errorを返せる。POTASK-010 legacy MCP envも維持する。
- installed Hermesの`PluginContext` / registryとtemporary `HERMES_HOME`を使うlocal snapshot smokeを追加した。

#### Non-goals

- direct provider API / GraphQL / `gh` client、credential管理。`gh`はfallbackにも使用しない。
- write adapter、task mutation、GitHub Projects schema repair。
- model-supplied route / tool / file path / provider destination。
- backend detailをSchedule Secretary、Portfolio OS、その他consumer contractへ公開すること。
- companies repositoryのpreflight変更。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_read.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
git diff --check
```

## Issue Gate で承認する事項

- local issue ledger の粒度。
- blocker graph と dependency order。
- `実行可能` / `ブロック中` status。
- 各 issue の acceptance criteria。
- GitHub issue mirror を行わない local-first 方針。
