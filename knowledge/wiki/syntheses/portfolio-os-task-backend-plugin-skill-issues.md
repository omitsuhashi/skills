# Portfolio OS タスクバックエンドプラグイン / スキル Issue Ledger

## 状態

POTASK-001 から POTASK-011 は既存 Issue Gate / Execution Plan Gate 承認済みで実装完了。2026-07-21 に、task-management write / preflight Interfaceとseparate GitHub Projects AdapterをPOTASK-012からPOTASK-019へ分解し、Issue Gate承認を得た。2026-07-22時点でPOTASK-012からPOTASK-018はすべて独立review approvedのlocal `PR_READY`。POTASK-019はreviewed headsのintegrationとpublic fake end-to-endを進め、human request `hr-potask-019-normative-status-scope-001`の承認により2つのnormative specをstatus/current-boundary更新だけのwrite scopeへ追加し、保存済み差分から実装を再開した。GitHub issue mirror、push、PR、merge、live activationは行わない。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## 前提

- 正本仕様: [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- write / preflight正本仕様: [Task Management Write / Preflight Interface 仕様](task-management-write-preflight-interface-spec.md)
- GitHub Adapter正本仕様: [GitHub Projects Task Backend Adapter 仕様](task-adapter-github-projects-spec.md)
- file-level plan: [Task Management Write / Preflight 実装計画](2026-07-21-task-management-write-preflight-implementation-plan.md)
- normalized packet: [Task Management Write / Preflight Input Packet](portfolio-os-task-backend-plugin-skill-write-preflight-input-packet.json)
- execution contract: [Task Management Write / Preflight Execution Envelope](portfolio-os-task-backend-plugin-skill-write-preflight-execution-envelope.json)
- execution preflight: [Task Management Write / Preflight Execution Preflight](portfolio-os-task-backend-plugin-skill-write-preflight-execution-preflight.json)
- POTASK-001からPOTASK-011のhistorical scopeはtask taxonomy、`TaskDraft` composition、read-only routing / facade / provider adapter、docs-only write contractまでである。
- POTASK-012からPOTASK-019はwrite / preflightを実行可能にし、GitHub Projects mutation Implementationをseparate Adapterへ追加するfollow-upである。route v2 clean break、executable approval binding、linked Issue onlyの新仕様が、旧route v1 compatibilityとdocs-only write記述を置き換える。
- GitHub issue / PRによるdelivery、push、PR creation、mergeはadapter Implementationではなくremote delivery workflowの責務であり、今回のlocal issue実装scope外である。real GitHub Project / Issue mutationはLive Activation Gateまで行わない。
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
| `portfolio-os-task-backend-plugin-skill` | POTASK-011 | pluggable provider adapter と Hermes end-to-end call path を実装する | 承認済み | 完了 | `PR_READY` `458f712` | POTASK-004, POTASK-010 | POTASK-012 | 未作成 | approved: `feb8908..458f712` / 2 cycles | [#29](https://github.com/omitsuhashi/skills/pull/29) |
| `portfolio-os-task-backend-plugin-skill` | POTASK-012 | shared Adapter contract v2 と安全なwrite契約を実装する | 承認済み | 完了 | `PR_READY` `d539ebd` | POTASK-011 | POTASK-013, POTASK-014, POTASK-016 | 未作成 | approved: `cc1d428..d539ebd` / 通常2 cycles + 例外1 cycle + 最終micro-review | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-013 | unified route v2へ移行しread Interfaceを回帰維持する | 承認済み | 完了 | `PR_READY` `badc466` | POTASK-012 | POTASK-015 | 未作成 | approved: `d539ebd..badc466` / 1 cycle | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-014 | approval digestとconfidence-aware approval policyを実装する | 承認済み | 完了 | `PR_READY` `a5bcf11` | POTASK-012 | POTASK-015 | 未作成 | approved: `d539ebd..a5bcf11` / 1 cycle | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-015 | executable `task_preflight` / `task_apply` facadeを実装する | 承認済み | 完了 | `PR_READY` `f5fc50e` | POTASK-013, POTASK-014 | POTASK-019 | 未作成 | approved: `badc466..f5fc50e` / 1 cycle | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-016 | separate GitHub Projects Adapter pluginとhost configを作る | 承認済み | 完了 | `PR_READY` `bc73c99` | POTASK-012 | POTASK-017 | 未作成 | approved: `d539ebd..bc73c99` / 1 cycle | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-017 | GitHub Adapterのexecutable preflight / queryを実装する | 承認済み | 完了 | `PR_READY` `b2494e5` | POTASK-016 | POTASK-018 | 未作成 | approved: `bc73c99..b2494e5` / 2 cycles | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-018 | GitHub Adapterのcreate/update/comment/report applyを実装する | 承認済み | 完了 | `PR_READY` `cc61018` | POTASK-017 | POTASK-019 | 未作成 | approved: `b2494e5..cc61018` / 2 cycles | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-019 | dual-host契約・文書・smoke・full verificationを統合する | 承認済み | 実装再開 | integration `3c8ba06` + e2e 6 / 6 / normative status scope承認済み | POTASK-015, POTASK-018 | なし | 未作成 | 未実施 | 未作成 |

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
│           └── POTASK-012
│               ├── POTASK-013
│               │   └── POTASK-015
│               │       └── POTASK-019
│               ├── POTASK-014
│               │   └── POTASK-015
│               └── POTASK-016
│                   └── POTASK-017
│                       └── POTASK-018
│                           └── POTASK-019
├── POTASK-003
│   ├── POTASK-005
│   └── POTASK-006
└── POTASK-004
    ├── POTASK-006
    ├── POTASK-007
    └── POTASK-008
```

循環依存はない。POTASK-001からPOTASK-011の`レビュー状態`は既存Issue Gate承認済み。POTASK-012からPOTASK-019も2026-07-21のIssue Gateで承認済みである。
POTASK-010 は POTASK-002 の contract、POTASK-007 の typed adapter boundary、POTASK-008 の Hermes governance を再利用する follow-up であり、既存 issue を再開しない。POTASK-011 はPOTASK-010のpublic facadeを維持したまま、POTASK-004のroutingを実行可能なprovider adapterへ接続する。
POTASK-012からPOTASK-018はlocal `PR_READY`。POTASK-019のdependency blockerは解消済みで、human-approved revision 5 amendmentにより2 normative specのstatus/current-boundary editだけを追加し、保存済みworker差分から実装を再開した。
2026-07-21のIssue Gate amendmentにより、POTASK-015はPOTASK-013 headをbaseにreview approvedなPOTASK-014 headを統合するintegration work item、POTASK-019はPOTASK-018 headをbaseにreview approvedなPOTASK-015 headを統合するintegration work itemとする。複数blocker headを通常workerがad-hoc mergeしない。

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
10. POTASK-012
11. POTASK-013、POTASK-014、POTASK-016
12. POTASK-015、POTASK-017
13. POTASK-018
14. POTASK-019

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
- review cycle 1でpath resolve例外のtyped mapping、response byte/item上限、normalization前limit、route kind/tool namespace一致、duplicate destination拒否を追加した。

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

### POTASK-012: shared Adapter contract v2 と安全なwrite契約を実装する

#### 目的

task-managementとseparate Adapterが共有するbackend-neutral wire contract v2を実行可能な型・validator・normative fixturesとして固定し、後続issueが同じseamを独立に実装できるようにする。

#### Write Scope

- `plugins/task-management/task_management/contracts.py`
- `plugins/task-management/task_management/safety.py`
- `plugins/task-management/task_management/provider_adapters/`
- `plugins/task-management/tests/fixtures/adapter-v2/`
- `plugins/task-management/tests/test_write_contracts.py`
- `plugins/task-management/tests/test_task_contracts.py`
- `plugins/task-management/tests/test_adapter_dispatch.py`
- `plugins/task-management/tests/test_github_mcp_route.py`

#### Acceptance Criteria

- `OperationEnvelope`、`TaskPreflightResult`、`ApprovalPreview`、`ApprovalReceipt`、`TaskWriteResult` v2をstrict validationできる。
- `task.create`、`task.update`、`task.comment`、`task.report`のrequired payloadと`task_ref`条件が仕様どおりである。deleteは拒否する。
- `TaskDraft`と`TaskBackendDestination`は承認済みbackend-neutral fieldsを維持する。
- adapter Interfaceは`query`、`preflight`、`apply`の3 operationだけを公開する。
- unexpected field、float / invalid canonical value、credential-like data、raw provider ID、unsafe URL、raw payloadをfail closedにする。
- normative accept/reject fixturesが後続GitHub Adapter contract testsから再利用できる。

#### Non-goals

- route v2、approval digest、Hermes tool registration、GitHub Adapter pluginの実装。
- provider client、canonical task store、persistent ledger。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_write_contracts.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
git diff --check
```

#### Implementation Evidence

- worker branch: `codex/portfolio-os-task-backend-plugin-skill/POTASK-012-contract-v2`
- base / current head: `cc1d42856ea46296fb1575c4533f913cbe675ba0..d539ebdec2660f99d87dd68d6a36eef0b5637d2c`
- implementation commits: `bb66affd71a4c35b33210b37d10482bbbf1ab7df`、`5f4c0dcb59cd5356867acb2caa486bf0df95ec7a`、`c47a9c794f09d037655def5f4edc879903f5106f`、`d539ebdec2660f99d87dd68d6a36eef0b5637d2c`
- fresh verification: write contracts 26 / 26、task-management full suite 127 / 127、read adapter 18 / 18、read routes 18 / 18、`git diff --check` PASS
- implementation review cycle 1 / 2は、brittle exact-file guardとHTTP destination URL受理をImportant `intent_gap`として検出し、`5f4c0dc`で修正した。
- cycle 2 / 2は、scheme-relative / colon-form URL bypassと、root plugin entrypoint / direct provider SDK / separate-adapter importのscan漏れをImportant `intent_gap`として検出した。blockerはreleaseしていない。
- human request `hr-potask-012-review-exception-001` により、上記残存2件だけをTDD修正し独立reviewする例外cycle 1回を2026-07-22に承認し、`c47a9c7`でURL-shaped bypassとroot / provider import scan漏れを修正した。
- exception reviewは、両guardの`r"\b(?:api\.github\.com|/graphql)\b"`がquote後またはstring先頭の`/graphql`をword-boundary条件で見逃すImportant `intent_gap`を1件検出した。他のscope内findingはない。
- human request `hr-potask-012-post-exception-decision-001` に対し、ユーザーは両guard testの無効な先頭word-boundary修正と代表的`endpoint = "/graphql"` probe追加だけを対象にする最終micro-fix + independent review 1回を承認した。既存のclient / API / GraphQL / `gh` / provider禁止は維持し、他scopeへ広げない。
- final micro-fix `d539ebd`は2 test fileだけを4 insertions / 2 deletionsで変更し、TDD RED 23 tests / 2 expected failuresからGREEN 23 / 23、write contracts 26 / 26、full 127 / 127、read regression各18 / 18、diff-checkを通過した。
- final independent reviewは`cc1d428..d539ebd`と`c47a9c7..d539ebd`を`approved`とし、Critical / Important findingは0件。POTASK-013、POTASK-014、POTASK-016をreleaseした。
- next trigger: runnable 3 issueのworker dispatch。POTASK-015、POTASK-017からPOTASK-019は各typed dependencyのreview approval待ち。
- remote / live evidence: GitHub Issue、push、PR、merge、Hermes profile / MCP registration、credential、GitHub Project / Issue mutationは未実施。

### POTASK-013: unified route v2へ移行しread Interfaceを回帰維持する

#### 目的

read-only route v1を、query / preflight / applyのfixed Adapter trioを解決するhost-owned route v2へclean breakし、existing `task_query` consumer contractを維持する。

#### Write Scope

- `plugins/task-management/task_management/route_config.py`
- `plugins/task-management/task_management/read_adapter.py`
- `plugins/task-management/task_management/provider_adapters/`
- `plugins/task-management/config/task-backends.example.toml`
- `plugins/task-management/tests/test_task_read_routes.py`
- `plugins/task-management/tests/test_task_read_adapter.py`
- `plugins/task-management/tests/test_backend_routing.py`
- `plugins/task-management/scripts/smoke_test_hermes_read.py`

#### Acceptance Criteria

- `TASK_MANAGEMENT_ROUTES_FILE`と`contract_version = 2`を使い、`adapter_key`、`query_tool`、`preflight_tool`、`apply_tool`をhost configから解決する。
- tool name、provider ref、file path、GitHub mappingをmodel inputにしない。
- `TASK_MANAGEMENT_READ_ROUTES_FILE`、`TASK_MANAGEMENT_READ_ADAPTER_TOOL`、route v1 compatibility wrapperをproduction codeから除去する。
- missing / duplicate / version mismatch / namespace mismatch / capability mismatchをdispatch前にtyped failureにする。
- existing `task_query` request / `TaskSnapshotResult`とlocal_json fixture-only smokeが回帰しない。
- implicit GitHub、direct GraphQL、`gh` fallbackを持たない。

#### Non-goals

- live route file配置、Hermes profile edit、MCP registration。
- approval / write facade、GitHub field mapping。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_task_read_routes.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_task_read_adapter.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_backend_routing.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_read.py
git diff --check
```

#### Execution Evidence

- worker branch / base: `codex/portfolio-os-task-backend-plugin-skill/POTASK-013-route-v2` / `d539ebdec2660f99d87dd68d6a36eef0b5637d2c`
- approved scope内のroute/read変更は未commit。targeted route 21 / 21、read adapter 18 / 18、`git diff --check`はPASSした。
- approved configをroute v2へ更新すると、既存`plugins/task-management/tests/test_backend_routing.py`がroute v1 shapeをexact assertして回帰する。しかし同testはPOTASK-013 Write Scope外である。
- human request `hr-potask-013-regression-guard-scope-001` は、機能scope / DAG / remote policyを変えず、上記1 test fileだけをWrite Scope / read pathsへ追加する承認を求める。承認または別判断までworkerとdescendantを停止する。
- 2026-07-22にユーザーが推奨amendmentを承認した。input packetとschema v3 Execution Envelope revision 3へ上記1 fileとtargeted verificationだけを追加し、保存済み7-file diffを破棄せず元workerで再開する。
- commit `badc466`は保存済み7-file diffを維持したままconfig / smoke / approved regression guardをroute v2へ同期した。route 21 / 21、read 18 / 18、backend 8 / 8、full 130 / 130、smoke / validatorsを通過し、independent review cycle 1は`approved`。local `PR_READY` / `artifact_ready`。
- remote / live evidence: GitHub Issue、push、PR、merge、Hermes profile / MCP registration、credential変更は未実施。

### POTASK-014: approval digestとconfidence-aware approval policyを実装する

#### 目的

review時とapply時のoperation identityをcanonical digestで固定し、確証がないtaskをwrite前にhuman confirmationへ戻すfail-closed approval policyを実装する。

#### Write Scope

- `plugins/task-management/task_management/approval.py`
- `plugins/task-management/task_management/preflight.py`
- `plugins/task-management/tests/test_approval_binding.py`
- `plugins/task-management/tests/test_preflight.py`
- approval test vectors under `plugins/task-management/tests/fixtures/adapter-v2/`

#### Acceptance Criteria

- canonical JSONは`null`、boolean、integer、NFC string、array、objectだけを受理し、deterministic SHA-256 digestを作る。
- digestはoperation type、backend / destination、task ref、task content / fields、content target、route binding、ordered expected side effectsをすべてbindingする。
- 各binding fieldの1-field mutation、route変更、side-effect変更で`approval_mismatch`になり、adapter apply callは0回である。
- `approval_required: true`、non-empty `fields.review_notes`、adapter uncertaintyは`human_required`を強制する。
- `confidence_authorized`はpreflight pass、`confidence_eligible`、unresolved uncertaintyなしの場合だけ許す。
- preflight passとwrite approvalを別状態・別testsにする。approval digestはactor identity proofと表現しない。

#### Non-goals

- signing key、approval database、queue、dispatcher、result store。
- task intentの意味上の確証をtask-managementが自動推論すること。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_approval_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_preflight.py'
git diff --check
```

#### Implementation Evidence

- worker branch / range: `codex/portfolio-os-task-backend-plugin-skill/POTASK-014-approval-binding` / `d539ebdec2660f99d87dd68d6a36eef0b5637d2c..a5bcf118ae263cc3db33c56eb24401a5bfdcc9d4`
- fresh verification: approval binding 5 / 5、preflight 5 / 5、task-management full suite 137 / 137、`git diff --check` PASS。
- independent review cycle 1は`approved`。canonical digest、confidence / human-required policy、adapter dispatch 0回のfail-closed boundaryにCritical / Important findingはない。
- separate Adapter側のfrozen fixture copy同期はPOTASK-019 integration scopeが所有する。POTASK-014のfindingではない。
- local `PR_READY` / `artifact_ready`。remote / live writeは未実施。

### POTASK-015: executable `task_preflight` / `task_apply` facadeを実装する

#### 目的

task-management public Interfaceとしてexecutable preflight / applyを公開し、route resolution、re-preflight、approval identity、Adapter dispatch、result normalizationを深いModuleの内側へ隠す。

このissueはPOTASK-013 / POTASK-014のapproved integration work itemでもある。POTASK-013 headをbaseにし、POTASK-014がimplementation review approvedになった後、そのheadをintegration scopeとして取り込み、両方のcontract上でpublic facadeを実装する。

#### Write Scope

- `plugins/task-management/task_management/write_adapter.py`
- `plugins/task-management/task_management/normalization.py`
- `plugins/task-management/task_management/__init__.py`
- `plugins/task-management/__init__.py`
- `plugins/task-management/plugin.yaml`
- `plugins/task-management/.codex-plugin/plugin.json`
- `plugins/task-management/tests/test_task_write_adapter.py`
- `plugins/task-management/tests/test_write_normalization.py`
- `plugins/task-management/tests/test_hermes_plugin_manifest.py`
- `plugins/task-management/scripts/smoke_test_hermes_write.py`
- POTASK-013 Write Scopeに含まれるroute / read filesとtests
- POTASK-014 Write Scopeに含まれるapproval / preflight files、tests、fixtures

#### Acceptance Criteria

- `task_preflight`と`task_apply`をruntime登録し、`plugin.yaml.exports.toolsets`に`task-management-write`を追加する。
- `task_apply`はexact ApprovalPreviewとReceiptを受け、current route reloadとadapter re-preflight後に一致したoperationだけをdispatchする。
- success、setup blocker、provider failure、partial failure、retryable / non-retryableをbackend-neutral `TaskWriteResult`へ正規化する。
- resultはsafe task ref / HTTPS URL / title / human actionを許し、raw provider data、credential、GitHub raw IDを遮断する。
- fake Adapter smokeでcreate success、human-required stop、approval mismatch dispatch 0回を実証する。
- task-management versionを`0.4.0`へ同期し、Companies handoff Interface v2をmanifest / runtime / docsから検証できる。
- POTASK-013 / POTASK-014のreview approved headsをこのissueだけが統合し、統合後rangeでtargeted regressionとimplementation reviewを通す。

#### Non-goals

- GitHub MCP method / field mapping、provider retry implementation。
- live install / enable、Companies repo変更。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_write.py
python3 scripts/validate_dual_host_compatibility.py --plugin plugins/task-management
git diff --check
```

#### Implementation Evidence

- worker branch / range: `codex/portfolio-os-task-backend-plugin-skill/POTASK-015-write-facade-integration` / `badc466320ca6ab59a0a6a03e9a50426428ad089..f5fc50ecdb87345b7e9e434b59e22d07c5a6f82a`
- integration commit `82b3246`はparentsをreviewed POTASK-013 `badc466`とreviewed POTASK-014 `a5bcf11`に固定し、conflict 0件、両head ancestryを実証した。
- implementation `f5fc50e`は`task_preflight` / `task_apply`、route reload → re-preflight → approval binding → fixed apply dispatch、backend-neutral bounded normalization、v0.4.0 read/write toolsets、fake write smokeを実装した。
- fresh verification: facade 7 / 7、normalization 9 / 9、manifest 11 / 11、approval 5 / 5、preflight 5 / 5、full 156 / 156、read / write smokes、plugin / dual-host validators、diff / cache scan PASS。
- independent review cycle 1は`approved`、finding 0件。local `PR_READY` / `artifact_ready`、remote / live writeは未実施。

### POTASK-016: separate GitHub Projects Adapter pluginとhost configを作る

#### 目的

GitHub provider knowledgeをtask-managementから隔離するdual-host plugin distributionを作り、fixed MCP tools、opaque destination mapping、field mapping、delegation attestationをfail-closed configとして定義する。

#### Write Scope

- `plugins/task-adapter-github-projects/.codex-plugin/plugin.json`
- `plugins/task-adapter-github-projects/plugin.yaml`
- `plugins/task-adapter-github-projects/__init__.py`
- `plugins/task-adapter-github-projects/README.md`
- `plugins/task-adapter-github-projects/config/github-projects.example.toml`
- `plugins/task-adapter-github-projects/task_adapter_github_projects/{__init__,contracts,config,safety}.py`
- `plugins/task-adapter-github-projects/tests/fixtures/`
- `plugins/task-adapter-github-projects/tests/test_contract_compatibility.py`
- `plugins/task-adapter-github-projects/tests/test_config.py`
- `plugins/task-adapter-github-projects/tests/test_hermes_plugin.py`
- `plugins/task-adapter-github-projects/tests/test_safety.py`

#### Acceptance Criteria

- `plugin-creator` scaffoldを基にCodex / Hermes manifests、importable `register(ctx)`、adapter runtime tool trioを持つversion `0.1.0` pluginが成立する。
- configはexact MCP tool allowlist、opaque destination / content target、GitHub owner / project / repository、canonical field mapping、host attestationを持つ。
- credential、caller-supplied tool name、arbitrary dispatch、unknown destination、unsafe `raw_mcp_exposure` / `adapter_write_exposure`を拒否する。
- adapter write toolsetはhost policy上`task_management_only`であり、model / child agentへ直接公開しない。
- task-management normative adapter-v2 fixturesとのcompatibility testsが通る。

#### Non-goals

- MCP registration、credential / permission setup、live Project / Issue access。
- preflight provider call、query、write orchestration。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests
python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-adapter-github-projects
python3 scripts/validate_dual_host_compatibility.py --plugin plugins/task-adapter-github-projects
git diff --check
```

#### Implementation Evidence

- worker branch / range: `codex/portfolio-os-task-backend-plugin-skill/POTASK-016-github-adapter-scaffold` / `d539ebdec2660f99d87dd68d6a36eef0b5637d2c..bc73c99920afab392d5e20aa22a6a1859686f05e`
- fixed MCP allowlist、opaque destination / content target、host attestation、dual-host manifests、local contract / frozen fixturesを43 approved pathsで実装した。
- fresh verification: adapter tests 15 / 15、plugin validator、dual-host compatibility、`git diff --check` PASS。
- independent review cycle 1は`approved`。task-managementからPython importせず、contract v2とexact fixture equalityでseparate distribution boundaryを維持した。
- local `PR_READY` / `artifact_ready`。remote / live writeは未実施。

### POTASK-017: GitHub Adapterのexecutable preflight / queryを実装する

#### 目的

official GitHub MCP Serverのread surfaceをfake dispatcher経由で呼び、auth / permission / Project / field / capability / delegation readinessとnormalized queryを実行可能にする。

#### Write Scope

- `plugins/task-adapter-github-projects/task_adapter_github_projects/adapter.py`
- `plugins/task-adapter-github-projects/task_adapter_github_projects/normalization.py`
- `plugins/task-adapter-github-projects/tests/test_preflight.py`
- `plugins/task-adapter-github-projects/tests/test_query.py`
- provider-shape fixtures under `plugins/task-adapter-github-projects/tests/fixtures/`

#### Acceptance Criteria

- `projects_get` / `projects_list`のread-only probeでdestination、field、item、paginationを検証する。
- preflightはwrite toolを呼ばず、successをwrite approvalとして返さない。
- adapter unavailable、tool disabled、auth missing、permission failure、destination unresolved、required field missing、field type mismatch、unsafe delegation exposure、capability mismatchをstable codeへ正規化する。
- queryはcanonical filters / limitをprovider queryまたはbounded post-filterへ変換し、raw GraphQL payloadを返さない。
- Hermes private registryを参照せず、host attestationとpublic `ctx.dispatch_tool()` seamだけを使う。

#### Non-goals

- Issue / Project mutation、schema repair、direct GraphQL / REST / `gh` fallback。
- live GitHub smoke。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests -p 'test_preflight.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests -p 'test_query.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests
git diff --check
```

#### Implementation Evidence

- worker branch / range: `codex/portfolio-os-task-backend-plugin-skill/POTASK-017-github-preflight-query` / `bc73c99920afab392d5e20aa22a6a1859686f05e..b2494e59d729f0f98031c3abab3b77642bf1d51f`
- initial implementation `eb570e4`に対し、cycle 1 reviewはofficial compact field `data_type`のlowercase mismatchと、public Hermes `ctx.dispatch_tool()` JSON envelopeをtestsが迂回している2件をCritical `intent_gap`として検出した。
- fix `b2494e5`はofficial pinned GitHub MCP source `9d130049e9074772c2afbbd5e904725d240443ad`とlive installed Hermes public dispatch seamを根拠に、lowercase typesとouter result / error envelopeのstrict safe decodeをTDD修正した。
- fresh verification: preflight 7 / 7、query 5 / 5、adapter full suite 27 / 27、plugin validator、dual-host compatibility、`git diff --check` PASS。
- independent review cycle 2は`approved`、残存finding 0件。local `PR_READY` / `artifact_ready`、remote / live writeは未実施。

### POTASK-018: GitHub Adapterのcreate/update/comment/report applyを実装する

#### 目的

official MCP toolsをAdapter内でorchestrationし、linked Issue create、Project add、field update、comment / structured report、read-back、partial failureをsafe adapter resultにする。

#### Write Scope

- `plugins/task-adapter-github-projects/task_adapter_github_projects/adapter.py`
- `plugins/task-adapter-github-projects/task_adapter_github_projects/normalization.py`
- `plugins/task-adapter-github-projects/tests/test_apply_create.py`
- `plugins/task-adapter-github-projects/tests/test_apply_update.py`
- `plugins/task-adapter-github-projects/tests/test_apply_comment_report.py`
- `plugins/task-adapter-github-projects/tests/test_partial_failures.py`
- `plugins/task-adapter-github-projects/scripts/smoke_test_hermes_adapter.py`
- provider-shape fixtures under `plugins/task-adapter-github-projects/tests/fixtures/`

#### Acceptance Criteria

- createは`issue_write(create)`、`projects_write(add_project_item)`、fieldごとの`update_project_item`、read-backの順に実行する。
- Project-native draft itemと`content_policy`を実装しない。createにはopaque `content_target_ref`を必須にする。
- updateはIssue content / Project fields、commentは短いIssue comment、reportはstructured Markdown Issue commentとしてdistinct statusを返す。
- Project-wide status updateを`task.report`に使わない。
- Issue create後 / Project add後 / field update中の失敗をstage付きpartial failureにし、safe task ref / URL / title / human actionを保持する。
- unknown write outcomeをblind retryableにせず、write未実行が確実なrate limit等だけretryableにできる。
- backend-specific duplicate preventionをadapter内に置き、persistent local storeを追加しない。

#### Non-goals

- delete、Project schema repair、canonical task state、direct API fallback。
- live GitHub mutation。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-adapter-github-projects/scripts/smoke_test_hermes_adapter.py
git diff --check
```

#### Implementation Evidence

- worker branch / range: `codex/portfolio-os-task-backend-plugin-skill/POTASK-018-github-apply` / `b2494e59d729f0f98031c3abab3b77642bf1d51f..cc61018cb55172fcbd15e6ffa1b01f91e58b4357`
- implementation `d780f8c`はofficial MCP shapesでIssue create → Project add → ordered 9 field updates → read-back、distinct update / comment / report、safe partial resultを実装した。public Interfaceは`preflight` / `query` / `apply`だけを維持した。
- cycle 1 reviewは、field-only update / comment / reportのfirst writeでexplicit no-write rate limitの`retryable`が失われ、stable `rate_limited` spellingをno-write detectorが認識しないImportant `intent_gap`を1件検出した。
- fix `cc61018`はoperation-local prior-write invariantを追加し、Issue-content update、field-only update、comment、report、underscore spellingの5 probesだけをsafe retryableにした。later-write / unknown outcomeはpartial / nonretryableを維持する。
- fresh verification: partial failure 6 / 6、adapter full suite 39 / 39、Hermes `PluginContext` fake-MCP smoke、plugin validator、dual-host compatibility、full / fix rangeの`git diff --check` PASS。
- independent review cycle 2は`approved`、Critical / Important / nonblocking finding 0件。local `PR_READY` / `artifact_ready`、remote / live writeは未実施。

### POTASK-019: dual-host契約・文書・smoke・full verificationを統合する

#### 目的

task-management public Interface v2とGitHub Adapter v0.1をend-to-end fixtureで接続し、manifests、runtime registration、skill references、examples、knowledge、verification evidenceを同期する。

このissueはPOTASK-015 / POTASK-018のapproved final integration work itemでもある。POTASK-018 headをbaseにし、POTASK-015がimplementation review approvedになった後、そのheadをintegration scopeとして取り込み、両Moduleのend-to-end contractを検証する。

#### Write Scope

- `plugins/task-management/{plugin.yaml,.codex-plugin/plugin.json,README.md}`
- `plugins/task-management/skills/task-management/SKILL.md`
- `plugins/task-management/skills/task-management/references/`
- `plugins/task-management/examples/`
- `plugins/task-management/tests/fixtures/`
- `plugins/task-adapter-github-projects/{plugin.yaml,.codex-plugin/plugin.json,README.md}`
- `plugins/task-adapter-github-projects/config/`
- `plugins/task-adapter-github-projects/tests/`
- `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-spec.md`
- `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md`
- `knowledge/wiki/syntheses/task-management-write-preflight-interface-spec.md`（status/current-boundaryのみ）
- `knowledge/wiki/syntheses/task-adapter-github-projects-spec.md`（status/current-boundaryのみ）
- `knowledge/index.md`
- `knowledge/log.md`

2026-07-22のExecution Envelope revision 5 amendmentにより、final integrationのdocs / completion evidenceに加え、上記2 normative specのstatus/current-boundary更新だけもworker contextが所有する。coordinatorは実装せず、独立reviewとruntime遷移だけを行う。

#### Execution Evidence

- integration commit `3c8ba06`はreviewed POTASK-018 `cc61018`とreviewed POTASK-015 `f5fc50e`をexact parentsに持ち、conflict 0件、両head ancestryを実証した。
- inherited baselineはtask-management 156 / 156、adapter fixture-copy RED 1件 / 他38件PASS、3 smokes PASS。fixture exact-copy同期後、public facade→Adapter fake end-to-end 6 / 6、task-management 156 / 156、adapter 45 / 45、3 smokesまでGREENになった。
- human request `hr-potask-019-normative-status-scope-001`は承認済み。revision 5はnormative canonical `task-management-write-preflight-interface-spec.md`とAdapter specの2 filesだけをstatus/current-boundary更新scopeへ追加した。design / DAG / remote / live policyは変更しない。
- 保存済みworker差分からfinal commit、worker report、implementation reviewへ再開する。remote / live writeは未実施。

#### Acceptance Criteria

- task-management `0.4.0`とGitHub Adapter `0.1.0`のmanifest / runtime registration / docsがexact alignmentする。
- `task-management-read`に`task_query`、`task-management-write`に`task_preflight` / `task_apply`が存在する。
- task-managementからGitHub field mapping / MCP method / credential処理が検出されない。
- adapterとtask-managementのcontract compatibility、preflight、approval、apply、read-backをfake MCP end-to-end testで実証する。
- secret / raw ID / provider payload leakage scan、existing read regression、local_json fixture-only assertionが通る。
- Companiesへ渡すpublic Interface v2がdurable docsで一意に参照できる。
- live activation未実施と別GateをREADME / knowledge / completion evidenceに明記する。
- POTASK-015 / POTASK-018のreview approved headsをこのissueだけが統合し、統合後rangeでfull verificationとimplementation reviewを通す。

#### Non-goals

- Companies repo変更、GitHub Issue mirror、push / PR / merge。
- MCP registration、credential / permission、live Hermes profile / Project / Issue変更。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-adapter-github-projects/tests -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_read.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-management/scripts/smoke_test_hermes_write.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 plugins/task-adapter-github-projects/scripts/smoke_test_hermes_adapter.py
python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-adapter-github-projects
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
python3 scripts/validate_dual_host_compatibility.py --plugin plugins/task-management
python3 scripts/validate_dual_host_compatibility.py --plugin plugins/task-adapter-github-projects
python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests -v
git diff --check
```

## Issue Gate で承認する事項

- local issue ledger の粒度。
- blocker graph と dependency order。
- `実行可能` / `ブロック中` status。
- 各 issue の acceptance criteria。
- GitHub issue mirror を行わない local-first 方針。
- POTASK-012からPOTASK-019を既存Epicのfollow-upとして扱い、新しいEpicを作らない方針。
- remote policyはlocal-onlyとし、GitHub Issue作成、push、PR作成、merge、live activationをIssue Gate承認に含めない方針。
- amendmentとしてPOTASK-015をPOTASK-013 / 014、POTASK-019をPOTASK-015 / 018のapproved integration work itemにする方針。
- execution amendmentとして、必須の新規Moduleを列挙する既存regression guardを同期するため`test_adapter_dispatch.py`と`test_github_mcp_route.py`をPOTASK-012 Write Scopeへ追加する方針。機能scopeとDAGは変更しない。
