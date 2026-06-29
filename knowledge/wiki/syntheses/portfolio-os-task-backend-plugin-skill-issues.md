# Portfolio OS タスクバックエンドプラグイン / スキル Issue Ledger

## 状態

Issue Gate 承認済み。Execution Packet 作成前。実装、GitHub issue mirror、push、PR 作成、merge はまだ行わない。

## Epic ID

`portfolio-os-task-backend-plugin-skill`

## 前提

- 正本仕様: [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)
- 初回実装 scope は task taxonomy、`TaskDraft` composition、backend / destination routing、adapter operation envelope、preview / guard、typed result mapping まで。
- 外部 adapter の実 write 方針、GitHub Projects mutation、GitHub issue / PR、push、PR creation、merge は adapter / host / delivery workflow の責務であり、この ledger の実装対象外。
- GitHub MCP Server 自体の read/write live smoke test は行わない。通常検証は固定テストデータ / 模擬 tool を使う。
- local issue ledger を canonical とし、GitHub issues は未作成の optional mirror とする。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `portfolio-os-task-backend-plugin-skill` | POTASK-001 | `plugins/task-management/` の plugin scaffold と primary skill skeleton を作る | 承認済み | 実行可能 | なし | POTASK-002, POTASK-003, POTASK-004 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-002 | backend-neutral contract と固定テストデータを定義する | 承認済み | ブロック中 | POTASK-001 | POTASK-005, POTASK-006, POTASK-007 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-003 | task taxonomy と `TaskDraft` composition reference / examples を作る | 承認済み | ブロック中 | POTASK-001 | POTASK-005, POTASK-006 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-004 | backend / destination routing config と reference を作る | 承認済み | ブロック中 | POTASK-001 | POTASK-006, POTASK-007, POTASK-008 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-005 | `work_unit_id` / `work_unit_name` の解決と preview contract を実装する | 承認済み | ブロック中 | POTASK-002, POTASK-003 | POTASK-006 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-006 | adapter operation envelope と Adapter Dispatch Review guard を実装する | 承認済み | ブロック中 | POTASK-002, POTASK-003, POTASK-004, POTASK-005 | POTASK-007, POTASK-009 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-007 | GitHub MCP route preflight と typed result mapping を実装する | 承認済み | ブロック中 | POTASK-002, POTASK-004, POTASK-006 | POTASK-008, POTASK-009 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-008 | Hermes adapter availability runbook と governance reference を作る | 承認済み | ブロック中 | POTASK-004, POTASK-007 | POTASK-009 | 未作成 | 未実施 | 未作成 |
| `portfolio-os-task-backend-plugin-skill` | POTASK-009 | docs / examples / verification / handoff boundary を統合する | 承認済み | ブロック中 | POTASK-006, POTASK-007, POTASK-008 | なし | 未作成 | 未実施 | 未作成 |

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
│   └── POTASK-007
├── POTASK-003
│   ├── POTASK-005
│   └── POTASK-006
└── POTASK-004
    ├── POTASK-006
    ├── POTASK-007
    └── POTASK-008
```

循環依存はない。Issue Gate 承認済みのため、全 issue の `レビュー状態` は `承認済み` とする。

## 依存順

1. POTASK-001
2. POTASK-002、POTASK-003、POTASK-004
3. POTASK-005
4. POTASK-006
5. POTASK-007
6. POTASK-008
7. POTASK-009

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
- `github_projects_mcp` は default backend key として表現できるが、具体 project target を内包しない。

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
- fixture / mock adapter tests

#### Acceptance Criteria

- create/update/comment/report に相当する intent を adapter-neutral envelope として表現できる。
- envelope は backend key、connection ref、destination ref / label、operation type、task title/body/fields、`work_unit_id`、`work_unit_name`、adapter tool 名、expected adapter side effects を含む。
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

- docs は GitHub Projects が first backend であり permanent architecture ではないことを明記する。
- Portfolio OS は task state source of truth を持たない。
- dedicated idempotency key、`task_sha` field、duplicate-prevention store は存在しない。
- GitHub MCP Server read/write live smoke test は normal verification に含めない。
- `git diff --check` と repo-local validators が通る。

#### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
git diff --check
```

## Issue Gate で承認する事項

- local issue ledger の粒度。
- blocker graph と dependency order。
- `実行可能` / `ブロック中` status。
- 各 issue の acceptance criteria。
- GitHub issue mirror を行わない local-first 方針。
