# Task Management Write / Preflight 実装計画

> **For Codex:** Spec Gate と Issue Gate の承認後、`issue-implementation-loop` の worker context で issue ledger 順に test-first 実装すること。この計画だけを実装承認として扱わない。

## 状態

2026-07-21 Spec Gate 承認済み。file-level plan を承認済み設計に紐づけた。Issue ID、blocker graph、write scope、Execution Envelope は local issue ledger / Execution Plan Gate で追加する。実装は未着手。

## Goal

`plugins/task-management` を executable read / preflight / write Interface に拡張し、GitHub provider knowledge を separate `plugins/task-adapter-github-projects` に隔離する。approval mismatch、uncertain task creation、setup failure、partial provider failure を fail closed な backend-neutral result にする。

## Architecture

task-management は OperationEnvelope を strict validation し、unified route v2 で fixed adapter trio を解決する。adapter preflight が返す safe side effects と route binding を canonical ApprovalPreview / digest に固定し、`task_apply` は current route と re-preflight を照合してから adapter apply を dispatch する。GitHub adapter は official MCP tool chain を所有し、safe adapter result だけを返す。

## Tech stack

Python standard library、Hermes native plugin context、JSON / TOML contracts、`unittest`、repo validators。normal tests では fake dispatcher と static fixtures を使う。

## TDD 順序と file-level scope

### 1. Shared contract v2 と failing fixtures

**task-management files**

- Create: `plugins/task-management/task_management/contracts.py`
- Create: `plugins/task-management/task_management/safety.py`
- Create: `plugins/task-management/tests/fixtures/adapter-v2/`
- Create: `plugins/task-management/tests/test_write_contracts.py`
- Modify: `plugins/task-management/tests/test_task_contracts.py`

**adapter files**

- Create scaffold: `plugins/task-adapter-github-projects/`
- Create: `plugins/task-adapter-github-projects/task_adapter_github_projects/contracts.py`
- Create: `plugins/task-adapter-github-projects/tests/fixtures/adapter-v2/`
- Create: `plugins/task-adapter-github-projects/tests/test_contract_compatibility.py`

1. OperationEnvelope、TaskPreflightResult、ApprovalPreview、ApprovalReceipt、TaskWriteResult v2 の RED tests を追加する。
2. operation-specific requiredness、exact enum、unknown field rejection、opaque ref validation を実装する。
3. 両 plugin が同じ normative fixture を受理・拒否する compatibility tests を GREEN にする。
4. credential-like key / value、raw provider ID、unsafe URL、raw payload を rejection fixtures で固定する。

### 2. Unified route v2 と clean break

**Files**

- Rewrite: `plugins/task-management/task_management/route_config.py`
- Modify: `plugins/task-management/task_management/read_adapter.py`
- Modify: `plugins/task-management/config/task-backends.example.toml`
- Modify: `plugins/task-management/tests/test_task_read_routes.py`
- Modify: `plugins/task-management/tests/test_task_read_adapter.py`
- Modify: `plugins/task-management/scripts/smoke_test_hermes_read.py`

1. `TASK_MANAGEMENT_ROUTES_FILE`、contract v2、exact adapter trio、destination allowlist の RED tests を作る。
2. v1 env / fallback を拒否し、missing route / capability mismatch を typed fail-closed にする。
3. existing `task_query` request / result の regression tests を通す。
4. `local_json` を explicit test / smoke route としてのみ使い、operator default や persistent store にしない。

### 3. Approval preview、digest、confidence policy

**Files**

- Create: `plugins/task-management/task_management/approval.py`
- Create: `plugins/task-management/task_management/preflight.py`
- Create: `plugins/task-management/tests/test_approval_binding.py`
- Create: `plugins/task-management/tests/test_preflight.py`

1. deterministic canonicalization と digest test vectors を先に追加する。
2. operation / destination / task ref / payload / route / side effects の各 1-field mutation で mismatch になる parameterized tests を追加する。
3. human-required / confidence-eligible policy と `approved | confidence_authorized` receipt tests を追加する。
4. preflight pass だけでは apply できないこと、review notes / adapter uncertainty が人間確認を強制することを実装する。

### 4. Public `task_preflight` / `task_apply` facade

**Files**

- Create: `plugins/task-management/task_management/write_adapter.py`
- Modify: `plugins/task-management/__init__.py`
- Modify: `plugins/task-management/task_management/__init__.py`
- Create: `plugins/task-management/tests/test_task_write_adapter.py`
- Modify: `plugins/task-management/tests/test_hermes_plugin_manifest.py`
- Create: `plugins/task-management/scripts/smoke_test_hermes_write.py`

1. adapter unavailable、setup blocker、approval mismatch、success、partial failure の RED tests を追加する。
2. preflight route dispatch、ApprovalPreview 発行、apply 時 re-route / re-preflight / digest check を実装する。
3. adapter apply call count を検証し、全 mismatch / blocker で 0 回にする。
4. fake adapter だけを使う hermetic preflight / apply smoke を追加する。

### 5. Result normalization と leakage guard

**Files**

- Create: `plugins/task-management/task_management/normalization.py`
- Create: `plugins/task-management/tests/test_write_normalization.py`

1. success、setup blocker、provider failure、partial failure、retryable / non-retryable の fixtures と RED tests を追加する。
2. allowlist copy と safe error mapping を実装する。
3. unknown adapter field、raw provider payload、credential、GitHub raw ID、unsafe URL が public result に出ないことを検証する。
4. partial result では safe task ref / URL / title と human action を保持する。

### 6. GitHub adapter scaffold と config

**Files**

- Create: `plugins/task-adapter-github-projects/.codex-plugin/plugin.json`
- Create: `plugins/task-adapter-github-projects/plugin.yaml`
- Create: `plugins/task-adapter-github-projects/__init__.py`
- Create: `plugins/task-adapter-github-projects/README.md`
- Create: `plugins/task-adapter-github-projects/config/github-projects.example.toml`
- Create: `plugins/task-adapter-github-projects/task_adapter_github_projects/{__init__,config,safety}.py`
- Create: `plugins/task-adapter-github-projects/tests/test_config.py`
- Create: `plugins/task-adapter-github-projects/tests/test_hermes_plugin.py`
- Create: `plugins/task-adapter-github-projects/tests/test_safety.py`

1. plugin-creator scaffold / validator contract を test で固定する。
2. exact MCP tool allowlist、destination / content target mapping、field mapping、host attestation の RED tests を作る。
3. credential-in-config、arbitrary MCP tool、unsafe delegation、unknown destination を fail closed にする。
4. manifest と runtime tool registration の exact alignment を検証する。

### 7. GitHub adapter executable preflight / query

**Files**

- Create: `plugins/task-adapter-github-projects/task_adapter_github_projects/adapter.py`
- Create: `plugins/task-adapter-github-projects/task_adapter_github_projects/normalization.py`
- Create: `plugins/task-adapter-github-projects/tests/test_preflight.py`
- Create: `plugins/task-adapter-github-projects/tests/test_query.py`

1. fake dispatcher を注入し、projects get/list の method、pagination、field type validation の RED tests を作る。
2. auth、permission、destination、field、tool / capability、unsafe exposure の provider responses を stable code にする。
3. raw response を破棄し、adapter v2 safe result だけを返す。
4. preflight が write tool を呼ばず、approval を返さないことを検証する。

### 8. GitHub adapter apply orchestration

**Files**

- Modify: `plugins/task-adapter-github-projects/task_adapter_github_projects/adapter.py`
- Create: `plugins/task-adapter-github-projects/tests/test_apply_create.py`
- Create: `plugins/task-adapter-github-projects/tests/test_apply_update.py`
- Create: `plugins/task-adapter-github-projects/tests/test_apply_comment_report.py`
- Create: `plugins/task-adapter-github-projects/tests/test_partial_failures.py`
- Create: `plugins/task-adapter-github-projects/scripts/smoke_test_hermes_adapter.py`

1. create の Issue -> Project add -> field update -> read-back call order を RED test にする。
2. update の Issue / Project field mapping、comment / report の distinct render / status を実装する。
3. draft item method が存在しないこと、project status update を report に使わないことを test で固定する。
4. 各 stage の partial failure、unknown outcome、rate limit、idempotency guidance を実装する。
5. fake MCP tools を Hermes context へ登録する hermetic smoke を通す。

### 9. Docs / manifests / version sync

**Files**

- Modify: `plugins/task-management/plugin.yaml`
- Modify: `plugins/task-management/.codex-plugin/plugin.json`
- Modify: `plugins/task-management/README.md`
- Modify: `plugins/task-management/skills/task-management/SKILL.md`
- Modify: `plugins/task-management/skills/task-management/references/{task-contracts,task-read-adapter,backend-routing,adapter-dispatch,github-mcp-projects,hermes-mcp-governance,routing-flow}.md`
- Modify: `plugins/task-management/examples/task-create-preview.example.md`
- Create: write / preflight JSON fixtures and examples under `plugins/task-management/tests/fixtures/` and `examples/`
- Modify after Issue Gate: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-{spec,issues}.md`
- Modify: `knowledge/index.md`, `knowledge/log.md`

1. task-management version を `0.4.0`、GitHub adapter を `0.1.0` に揃える。
2. `task-management-read` / `task-management-write` export と runtime registration を同期する。
3. old route v1 / docs-only write language を executable v2 contract へ置き換える。
4. confidence-aware human confirmation、linked Issue only、separate live gate を全 consumer docs に同期する。

## Verification matrix

current repo で実装後に次を実行する。実際の test count と結果は issue ledger / log に記録する。

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

追加 leakage check は tracked diff と plugin trees に対して、token / authorization / GraphQL node ID / field ID / option ID / raw provider payload の fixture 外出現を監査する。existing read Interface regression、manifest exact alignment、local_json fixture-only assertion も full suite に含める。

## Delivery / remote policy

- implementation は Issue Gate 後に `issue-implementation-loop` へ委譲する。
- current user authorization は skills repo の local file edits と local verification までである。
- commit、push、PR creation は本 Spec Gate の暗黙 scope に含めない。必要なら別途明示確認する。
- GitHub Project / Issue、MCP registration、credential、permission、live Hermes install / apply は行わない。
- repo implementation complete と live activation complete を混同しない。

## 関連ページ

- [Task Management Write / Preflight Interface 仕様](task-management-write-preflight-interface-spec.md)
- [GitHub Projects Task Backend Adapter 仕様](task-adapter-github-projects-spec.md)
- [Portfolio OS Task Backend Plugin Skill Issues](portfolio-os-task-backend-plugin-skill-issues.md)

## 出典

- [Task Management Write / Preflight Interface 仕様](task-management-write-preflight-interface-spec.md)
- [GitHub Projects Task Backend Adapter 仕様](task-adapter-github-projects-spec.md)
- [plugin authoring rules](../../../plugins/AGENTS.md)
- [knowledge authoring rules](../../AGENTS.md)
