# Task Management Provider Adapters 実装計画

> **For Codex:** `issue-implementation-loop` の worker context で POTASK-011 を実装し、各段階で test-first と verification gate を守ること。

**Goal:** Hermes の公開 `task_query` から、consumer が backend 種別を指定せずに host-owned route を経由し、local snapshot または外部 MCP / provider plugin の task snapshot を取得できるようにする。

**Architecture:** 公開 facade は `TaskQuery` と logical `destination_ref` だけを受け、route loader が default backend と固定 adapter を解決する。adapter は依存を constructor で束縛し、共通の `ResolvedTaskReadRequest -> AdapterTaskSnapshotResult` 境界を実装する。public facade が最終 normalize と安全性検証を所有する。

**Tech Stack:** Python standard library (`dataclasses`, `json`, `tomllib`, `pathlib`), Hermes native plugin context, `unittest`。

---

## Task 1: route contract と RED tests

**Files:**

- Create: `plugins/task-management/task_management/route_config.py`
- Create: `plugins/task-management/tests/test_task_read_routes.py`
- Modify: `plugins/task-management/tests/test_read_adapter.py`

1. public schema で `backend_key` が省略可能であること、default local route、missing/invalid route、host-owned path guard を表す failing tests を追加する。
2. `contract_version = 1` の TOML route loader と typed setup error を最小実装する。
3. 対象 tests を実行し GREEN を確認する。

## Task 2: stable adapter interface と local snapshot backend

**Files:**

- Create: `plugins/task-management/task_management/provider_adapters/__init__.py`
- Create: `plugins/task-management/task_management/provider_adapters/local_json.py`
- Create: `plugins/task-management/tests/fixtures/local_tasks.json`
- Modify: `plugins/task-management/tests/test_task_read_routes.py`

1. adapter dependency が public request に漏れない protocol と request/result type の failing tests を追加する。
2. route が固定した read root 内の regular JSON file のみを読む adapter を実装する。
3. canonical filters と limit を適用し、local file を bootstrap read snapshot として扱う。
4. path escape、invalid JSON、contract mismatch を typed error にする tests を通す。

## Task 3: external MCP / provider plugin adapter

**Files:**

- Create: `plugins/task-management/task_management/provider_adapters/external_tool.py`
- Modify: `plugins/task-management/tests/test_task_read_routes.py`

1. route に固定された `mcp__<server>__task_query` と `task_adapter__<provider>__task_query` だけを dispatch する failing tests を追加する。
2. `adapter_contract_version = 1`、read-only capability、provider error taxonomy を検証する。
3. arbitrary tool、version mismatch、raw provider payload / credential leakage を fail closed にする。
4. POTASK-010 の environment-based MCP compatibility path は維持する。

## Task 4: public facade と Hermes runtime integration

**Files:**

- Modify: `plugins/task-management/task_management/read_adapter.py`
- Modify: `plugins/task-management/__init__.py`
- Create: `plugins/task-management/scripts/smoke_test_hermes_read.py`
- Modify: `plugins/task-management/tests/test_hermes_plugin.py`

1. tool registration が external adapter env なしでも公開される failing test を追加する。
2. per-call route resolution と adapter factory を facade に接続する。
3. local fixture を使って Hermes registry から公開 tool を実呼び出しする smoke test を実装する。
4. plugin test suite と smoke test を通す。

## Task 5: plugin contract、設定例、利用文書を同期

**Files:**

- Modify: `plugins/task-management/.codex-plugin/plugin.json`
- Modify: `plugins/task-management/plugin.yaml`
- Modify: `plugins/task-management/README.md`
- Modify: `plugins/task-management/config/task-backends.example.toml`
- Create: `plugins/task-management/examples/local-task-snapshot.example.json`
- Modify: `plugins/task-management/skills/task-management/SKILL.md`
- Modify: `plugins/task-management/skills/task-management/references/task-read-adapter.md`
- Modify: `plugins/task-management/skills/task-management/references/backend-routing.md`
- Modify: `plugins/task-management/skills/task-management/references/hermes-mcp-governance.md`
- Modify: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-{spec,issues}.md`
- Modify: `knowledge/{index.md,log.md}`

1. version を `0.3.0` に同期する。
2. Codex は workflow skill、Hermes は native runtime tool であることを manifest / README に明記する。実在しない MCP server export は宣言しない。
3. local JSON を mutable source of truth ではなく bootstrap read snapshot と表現する。
4. `gh` / direct provider API fallback がないこと、外部 write backend は MCP / provider plugin 所有であることを同期する。

## Task 6: full verification と delivery

1. plugin tests、Hermes smoke、plugin/skill validators、repository architecture/context validators、`git diff --check` を実行する。
2. independent review を最大 2 cycle 実施し、Critical / Important を修正して再検証する。
3. worker commit を既存 draft PR branch に統合し、branch を push して PR #29 を更新する。`gh` command は使用しない。
