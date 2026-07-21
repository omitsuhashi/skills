# Loop Skill Approved Spec Binding Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 人間が一度承認した exact spec bytes を Input Packet v2 に seal し、planning handoff から prepare、worker/reviewer、resume、completion、delivery まで同じ binding だけを fail closed に受理する。

**Architecture:** `issue-implementation-loop` 内の `approved_spec_binding.py` を path/digest/seal/verify の唯一の実装 owner とし、cross-skill seam は sealed JSON と host-neutral CLI に限定する。Input Packet v2 が approval/spec の正本、Envelope v4 が gate commit 付き packet ref、全 execution artifact が同じ ref を伝播する。旧 version は current code から削除し、historical wiki evidence だけを残す。

**Tech Stack:** Python 3 standard library、JSON Schema assets、Python `unittest`、Markdown skill contracts、Git object/tree verification、fresh-agent pressure tests、repository architecture/context/dual-host validators。

## Local Completion Status

2026-07-21 に ASBC-001〜ASBC-006 の TDD 実装、scoped review/fix、fresh-agent forward test、full verification、durable closeout を完了した。全 task は `LOCAL_COMPLETE`。current executable contract は Input Packet v2 / Execution Envelope v4 と downstream current-only artifact familyであり、historical v1〜v3 JSON は non-executable evidence として bytes を変更せず保持する。

- Implementation head before durable closeout: `b3bfa4b5a8cb1dd7788aa61398679ce6c5f995dd`。
- Approved spec / sealed packet / Envelope raw SHA-256: `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc` / `3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7` / `ac7630bf404b1c3607eb504bc18377bc45aef2c3b128be04e38d6737ca351af4`。
- Public acceptance ASB-01〜ASB-30、issue-loop 230 tests、grill 24 tests、llm-wiki 6 tests、architecture/context/strict context report/dual-host/creator validators、Packet/Envelope current validators、`git diff --check` は成功。strict context warnings は空、repository-wide 最小 headroom は 21%、affected issue-loop 最小 headroom は 26%。
- 3 fresh evaluator は planning drift、urgent execution mismatch、terminal後の stale delivery/resume をすべて fail closed に停止し、read-only diagnostic status だけを許可した。
- Scoped review は各 task で完了し、最終時点で open Critical / Important finding はない。
- Remote policy は `local_only` のまま。push、PR、merge、live Codex/Hermes install は意図的に実行していない。

## Global Constraints

- Canonical spec: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-spec.md`。
- Exact approved spec digest: `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`。
- Canonical issue ledger: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-issues.md`。
- Spec Gate commit: `bbf1585e05ad510242af3e4fa59be2447574d6ea`。
- Issue Gate commit: `fd6a3a38d52f1e83f293c133a6658912fbcdef99`。
- Branch: `codex/approved-spec-binding-contract`。
- Remote policy: `local_only`。push、PR、merge、live Codex/Hermes install は行わない。
- Coordinator は planning artifacts、dispatch、review、ledger closeout だけを所有し、issue implementation は fresh worker context が行う。
- 各 issue は RED -> minimal GREEN -> targeted verification -> scoped commit の順に進める。production code を failing test より先に編集しない。
- ASBC-001 だけは bootstrap rule により log evidence で開始する。ASBC-001 commit で Input Packet v2 を seal し、その commit を以後の `gate_commit` とする。
- 以後の worker/reviewer context は sealed packet path/digest と gate commit を必須で受け取る。
- spec bytes を変更しない。変更が必要なら停止し、新 digest の Written Spec Gate へ戻る。
- approval evidence を推測・補完・rehash しない。mismatch は stable code/action を返し、artifact/runtime を変更しない。
- standard library だけを使い、新しい runtime dependency を追加しない。
- persisted artifact に absolute `repo_root` を追加しない。
- path は repo-relative POSIX、raw bytes は非正規化 SHA-256、schema object は closed とする。
- new user-facing skill、`description.md`、consumer固有語彙、compatibility shim を追加しない。
- `SKILL.md` frontmatter description は trigger 条件に限定し、workflow contract は body/reference に置く。
- context operation は増やさず、既存 reference wording を置換・圧縮する。
- historical JSON/spec/ledger は削除しない。current validator の executable input としては拒否する。
- Python command は `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache` を使う。

## Execution Artifact Plan

- Input Packet v2: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-input-packet.json`
- Execution Envelope v4: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-execution-envelope.json`
- packet approval: `decision=approved`、`subject=spec_binding`、`actor_expression=session-user`、`approved_at=2026-07-21T17:55:36+09:00`、6 scope fields は exactly `true`。
- packet work items: ASBC-001〜ASBC-006、ledger と同じ acceptance/non-goal/write-scope/dependency、`delivery_intent=local_only`。
- ASBC-001 commit は final spec と sealed packet の exact blobs を含む最初の commit とし、Envelope v4 の `approved_spec_binding.gate_commit` に使う。
- Packet 自身に gate commit を書かない。Envelope v4 以降だけが packet path/raw-byte digest/full gate commit を持つ。

## File Map

### Create

- `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/approved_spec_binding.py`
- `skills/issue-implementation-loop/scripts/approved_spec_binding.py`
- `skills/issue-implementation-loop/tests/test_approved_spec_binding.py`
- `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-input-packet.json`
- `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-execution-envelope.json`

### Delete

- `skills/issue-implementation-loop/assets/schemas/worker-packet-v1.schema.json`

### Modify: Core and Schemas

- Input Packet schema/template/public validator and `validation/input_packet.py`。
- Execution Envelope schema/template/validator。
- Worker Packet schema/template/builder/validator and Worker Report schema/validator。

### Modify: Runtime and Gates

- Event/Runtime State/Human Request/Hardening Registry schemas and templates。
- `runtime_state.py`、`resume_brief.py`、`operation_selection.py`、`scheduler.py`、`review.py`、`delivery.py`、`delivery_plan.py`。
- runtime rebuild/resume/delivery public CLIs and relevant tests/helpers。

### Modify: Skill Contracts and Evidence

- both skill `SKILL.md` entrypoints and existing planning/handoff/envelope/worker/runtime/review/recovery/delivery references。
- both skill test suites and context contracts only if budgets require wording replacement。
- `knowledge/index.md`、`knowledge/log.md`、issue ledger、this plan closeout sections。

### Explicitly Unchanged

- family ownership/worker-only policy、context schema/version/operation names。
- scheduler algorithm、branch policy、review cycle count、merge authority。
- historical input packet/envelope/spec/ledger files other than index annotation。
- plugins、marketplace、installed Codex/Hermes state。

---

## Task 1 / ASBC-001: Implement binding core, Input Packet v2, and bootstrap seal

**Files:** canonical core/CLI, Input Packet schema/template/validator/tests, normalized packet artifact。

**Interfaces:**

- `identify_spec(repo_root, spec_path) -> SpecRevision`
- `seal_input_packet(repo_root, draft_packet_path, output_packet_path, expected_spec_revision, approval) -> InputPacketRef`
- `verify_chain(repo_root, artifact_refs) -> VerifiedBinding`
- CLI: `approved_spec_binding.py identify|seal|verify --repo-root ...`
- Stable failures use approved spec codes/actions and never mutate state on failure。

- [x] **Step 1: Add failing public-interface tests**

Create `test_approved_spec_binding.py` with temporary Git repository fixtures and tests for ASB-01, ASB-02, ASB-03, ASB-05〜ASB-09, ASB-20, ASB-21, ASB-24, ASB-25。Call public Python operations and CLI, not private hash helpers。Replace input packet tests so v2 closed shape succeeds and v1/missing approval/incomplete scope/malformed hash/unknown field/empty work items/unsafe paths fail with exact codes。

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_approved_spec_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_validation.py'
```

Expected: missing module/CLI errors and failures because Input Packet v1 still validates。

- [x] **Step 3: Implement safe file identity and stable results**

Implement trusted repo-root canonicalization, POSIX path parsing, component `lstat`, no-follow open, `fstat`, streaming SHA-256, before/after identity comparison, and stable result/error mappings。Translate OS/Git exceptions without raw payload/credential leakage。

- [x] **Step 4: Implement identify/seal/verify and CLI**

Implement the three operations and subcommands。Seal re-reads expected spec revision, injects exact approval evidence, serializes deterministic UTF-8/unescaped Unicode/LF/2-space/sorted-key/trailing-newline JSON, atomically replaces only output packet, and proves spec bytes unchanged。

- [x] **Step 5: Replace Input Packet v1 with v2**

Use exactly seven top-level fields, closed objects, exact six-field approval scope, and one-or-more strict work items。Remove optional `approved_revision`/`approved_hash` and persisted `repo_root`。Make public validation derive or accept a trusted Git root, then verify file/digest/approval。

- [x] **Step 6: Run GREEN**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_approved_spec_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_validation.py'
```

Expected: focused tests pass; v1 positives are deleted or inverted to `SCHEMA_UNSUPPORTED`。

- [x] **Step 7: Seal this implementation packet**

Create a temporary untracked draft containing ASBC-001〜ASBC-006 and run the new CLI with exact spec path/digest and log approval fields。Output only the planned Input Packet v2 path。Validate it, confirm spec digest remains `6ced...d359a3dcc`, and delete the temporary draft with `apply_patch`。

- [x] **Step 8: Commit core and sealed packet**

```bash
git add skills/issue-implementation-loop knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-input-packet.json
git commit -m "feat: bind approved spec to input packet"
git rev-parse HEAD
```

Expected: one scoped ASBC-001 commit; record its full object ID as the later gate commit。

---

## Task 2 / ASBC-002: Make Envelope and worker/reviewer artifacts current-only

**Files:** Envelope/Worker Packet/Worker Report schemas, templates, builders, validators, references, helpers, tests; delete V1 schema。

- [x] **Step 1: Add failing chain/gate tests**

Add tests for ASB-04, ASB-10〜ASB-13, ASB-22, ASB-26〜ASB-28。Build temporary Git histories where the ASBC-001 gate commit is/is not an ancestor and tree packet/spec blobs match/differ。Assert Envelope v1〜v3 and Worker v1/v2 return `SCHEMA_UNSUPPORTED`。

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_validation.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_worker_packet.py'
```

Expected: missing binding/gate checks fail and legacy-positive assertions expose old branches。

- [x] **Step 3: Replace Envelope with v4**

Require top-level binding。Validate packet path/raw digest/full current Git object ID, gate ancestor, gate-tree packet blob, and packet-referenced spec blob。Remove v1/v2/v3 conditions and compatibility wording/tests。

- [x] **Step 4: Replace worker/reviewer packet/report contracts**

Delete V1 schema and `--schema-version`/V1/V2 branches。Require Packet v3 `source_revision.approved_spec_binding`; distinguish executor/reviewer by `task_kind`/access policy only。Require Report v2 binding plus dispatch identity and compare report/dispatch/runtime bindings at intake。

- [x] **Step 5: Create and validate Envelope v4**

Create the planned Envelope path using the ASBC-001 full commit as `gate_commit` and sealed packet raw digest。Use the current isolated branch, maximum two review cycles, worker-only policy, and `local_only` remote policy。Validate through the public CLI。

- [x] **Step 6: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_validation.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_worker_packet.py'
git diff --check
git add skills/issue-implementation-loop knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-execution-envelope.json
git commit -m "feat: propagate spec binding through workers"
```

Expected: current-only chain tests pass and no legacy worker schema remains。

---

## Task 3 / ASBC-003: Bind runtime, events, auxiliary artifacts, and resume

**Files:** Event/Runtime/Human Request/Hardening Registry schemas/templates; rebuild, scheduler, registry, resume code/tests/references。

- [x] **Step 1: Add failing epoch tests**

Add public-entrypoint tests for ASB-13, ASB-17〜ASB-19, ASB-23, ASB-29〜ASB-30 with same-binding, mixed-binding, resealed epoch, v1/v2/meta-less inputs。

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_runtime_state.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_resume_brief.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_candidate_registry.py'
```

Expected: mixed events fold, old registry/request is accepted, meta-less resume succeeds with warning。

- [x] **Step 3: Replace runtime/event and auxiliary contracts**

Require Event v2 and Runtime State v2 binding; reject mixed/unknown bindings before and after fold。Require Human Request v2 and Hardening Registry v2 binding and compare to active runtime before routing/delivery reads。Reseal starts an empty new auxiliary epoch unless human re-records decisions。

- [x] **Step 4: Replace resume metadata with v3**

Require `sources.approved_spec_binding`, validate it before cache use and event fold, and delete meta-less/v2 success branches。Stale spec/packet rejects resume independently of envelope/runtime/event freshness。

- [x] **Step 5: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_runtime_state.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_resume_brief.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_candidate_registry.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_scheduler.py'
git diff --check
git add skills/issue-implementation-loop
git commit -m "feat: bind runtime epoch to approved spec"
```

---

## Task 4 / ASBC-004: Guard operation selection, review, completion, and delivery

**Files:** operation selection, scheduler/report intake, review, result/delivery contracts, public CLI, tests/references。

- [x] **Step 1: Add failing state-changing gate tests**

Add public tests for ASB-04, ASB-14〜ASB-16, ASB-22, ASB-29。Mutate spec/packet after runtime is terminal and prove explicit `deliver`, review, completion, and normal delivery are blocked while `status` is diagnostic only。

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_operation_selection.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_review_gate.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_delivery.py'
```

Expected: explicit deliver bypass and spec-unaware delivery tests fail new expectations。

- [x] **Step 3: Move binding verification before routing**

Evaluate binding before explicit-mode short-circuits。Return `status` with `binding_valid=false`/state advance blocked; every other invalid-binding operation returns stable reapproval blocker without mutation。

- [x] **Step 4: Bind review/result/delivery**

Require review dispatch/report/approval to match active binding and `BASE_SHA..HEAD_SHA`。Replace Execution Result v1 and Delivery Plan v1 with v2。Verify envelope→packet→spec and runtime/report/review/result/plan/registry immediately before terminal transition/delivery。

- [x] **Step 5: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_operation_selection.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_review_gate.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_delivery.py'
git diff --check
git add skills/issue-implementation-loop
git commit -m "feat: guard execution with spec binding"
```

---

## Task 5 / ASBC-005: Update skill contracts and remove active legacy guidance

**Files:** both entrypoints, existing references/context tests, historical index annotations。

- [x] **Step 1: Add failing skill-contract tests**

In grill tests require exact spec path/digest, six-field approval, seal, packet validation, and reapproval on any byte change。In issue-loop tests require prepare/dispatch/review/resume/completion/delivery guards and absence of legacy wording/options/files。Keep descriptions trigger-only and dual-host neutral。

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_entrypoint.py'
```

Expected: “when available”, old envelope/worker/resume clauses, and missing hooks fail。

- [x] **Step 3: Replace/compact current guidance**

Planning owns identify/present/approve/seal; execution owns verify/reapproval。Document one user approval, automatic checks, status-only exception, clean break, separate remote authorization。Replace existing references instead of adding an unconditional read-set。

- [x] **Step 4: Mark historical artifacts non-executable**

Update `knowledge/index.md` summaries for historical Input Packet v1/Envelope v1-v3 pages; retain the files and do not rewrite them as current v2 artifacts。

- [x] **Step 5: Run GREEN and commit**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_entrypoint.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
git add skills/grill-to-pr-loop skills/issue-implementation-loop knowledge/index.md
git commit -m "docs: require approved spec binding"
```

---

## Task 6 / ASBC-006: Forward-test, full verification, review, and closeout

**Files:** acceptance tests/fixtures as required, packet/envelope, issue ledger, plan, index, log。

- [x] **Step 1: Cover ASB-01〜ASB-30 through public surfaces**

Add a matrix in `test_approved_spec_binding.py` mapping each ASB ID to test method(s)。No row may be represented only by a private helper test。

- [x] **Step 2: Fresh-agent forward tests**

Launch three fresh evaluators with current skills only and no intended answer/spec text: planning one-byte drift; execution stored/current mismatch under urgency; terminal runtime then stale binding before explicit delivery/resume。All must mechanically stop/reapprove; only status may remain diagnostic。Keep raw responses outside the repo and record concise evidence。

- [x] **Step 3: Run full verification**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

Expected: all exit 0; context report warnings empty; no legacy schema/file/option or generic-vocabulary violation remains。

- [x] **Step 4: Independent implementation review**

Review each scoped range against issue criteria, then final-align immutable spec and sealed packet。Maximum two review/fix cycles。Critical/Important findings block completion and go to a fresh bounded RED/GREEN worker。

- [x] **Step 5: Sync durable evidence and commit closeout**

Update ledger with ranges/evidence/review/verification/forward tests/residual risks; append log entries; update index summaries without changing spec bytes。

```bash
git add knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-issues.md knowledge/wiki/syntheses/2026-07-21-loop-skill-approved-spec-binding-contract-implementation-plan.md knowledge/index.md knowledge/log.md
git commit -m "docs: close approved spec binding implementation"
git status --short --branch
```

Expected: clean local branch; all issues `PR_READY` or `LOCAL_COMPLETE`; remote actions unexecuted。

## Stop Conditions

- spec digest differs from the exact approved digest -> Written Spec Gate。
- packet scope/dependency/write scope/delivery intent must change -> Execution Plan Gate。
- worker needs unplanned files/dependency -> coordinator re-dispatch; do not broaden silently。
- legacy success branch is needed for bootstrap -> stop; fallback is prohibited。
- binding cannot reach any executor/reviewer/report/runtime/resume/completion/delivery boundary -> stop; do not downgrade to warning。
- context headroom drops below policy -> compress/replace wording without hiding approval/reapproval/stop/delivery guards。
- push、PR、merge、live install、credential、remote service、destructive action becomes necessary -> stop for explicit authorization。
