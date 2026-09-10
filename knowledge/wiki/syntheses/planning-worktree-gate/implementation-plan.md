---
summary: planning identity、main 保全と physical commit reachability の実装・検証証跡を確認できる。
knowledge_status: historical
---
# Planning Worktree Gate Implementation Plan

## 適用範囲と履歴

旧 grill-to-pr-loop / issue-implementation-loop の設計・実行証跡。[[wiki/syntheses/sdd-implementation-phase2-removal-plan|旧 loop skill の除去記録]] により executable surface / restart entrypoint ではない。本文の current 表現や packet / envelope / baseline は当時の範囲に限り、再実行には新しい承認と run を必要とする。現行の作業境界は repository root の `AGENTS.md` を参照する。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:test-driven-development` and implement each task with RED → GREEN → REFACTOR. The execution coordinator does not implement worker scope.

**Goal:** `grill-to-pr-loop` の最初のwriteをEpic planning worktreeへ固定し、`issue-implementation-loop` が default checkout drift と欠落commitを prepare / PR_READY / delivery で拒否できるようにする。

**Architecture:** planning側は小さな `planning_worktree.py` CLI が branch/worktree作成・再利用と開始snapshotを担当する。execution側は packetのdurable planning identityとuntracked Execution Envelopeのhost identityを `repository_integrity.py` で結合し、existing binding validation、completion、deliveryから同じread-only guardを呼ぶ。

**Tech Stack:** Python 3 standard library、Git CLI、JSON Schema、`unittest`、Markdown skill contract。

## Global Constraints

- discovery、read-only調査、grillingまではdefault checkoutでよい。
- Written Specを含む最初のrepository write前にEpic単位planning worktreeを作成または再利用する。
- Spec Gate、Issue Gate、Execution Plan Gate、index/log同期まで同じplanning worktreeを使う。
- default checkoutでtask由来のwrite、stage、commitを行わない。
- worktree作成失敗時はdefault checkoutへフォールバックしない。
- `planning_branch` / `planning_base_sha`はdurable packet、host固有pathはruntime artifactにだけ置く。
- pre-existing dirtを移動、削除、stash、reset、PR混入しない。
- remote policyは`local_only`。

---

### Task 1: PWTG-001 Planning Worktree Gate CLI

**Files:**

- Create: `skills/grill-to-pr-loop/scripts/planning_worktree.py`
- Create: `skills/grill-to-pr-loop/tests/test_planning_worktree_gate.py`
- Modify: `skills/grill-to-pr-loop/SKILL.md`
- Modify: `skills/grill-to-pr-loop/references/core.md`
- Modify: `skills/grill-to-pr-loop/references/planning-contract.md`
- Modify: `skills/grill-to-pr-loop/references/execution-handoff.md`
- Modify: `skills/grill-to-pr-loop/references/common-mistakes.md`
- Modify: `skills/grill-to-pr-loop/context-contract.toml`

**Interfaces:**

- Produces CLI:
  - `planning_worktree.py prepare --repo-root <abs> --epic-id <lower-kebab> [--default-branch <name>] [--worktree-root <abs>] [--json]`
  - JSON fields: `ok`, `epic_id`, `planning_branch`, `planning_base_sha`, `reused`, `runtime_state_path`, `default_checkout`.
- Produces runtime artifact under Git common directory:
  - `agent-runs/grill-to-pr-loop/<epic-id>/planning-worktree.json`
  - contains host paths and exact starting HEAD/status; it is never tracked.

- [x] **Step 1: Write failing CLI tests**

Create temp Git repositories and assert:

```python
def test_prepare_creates_planning_worktree_before_first_write(): ...
def test_prepare_reuses_existing_epic_worktree(): ...
def test_repeated_gate_entry_returns_same_worktree(): ...
def test_worktree_creation_failure_does_not_write_default_checkout(): ...
def test_prepare_preserves_preexisting_dirt(): ...
```

- [x] **Step 2: Run RED**

Run:

```bash
python3 -m unittest skills.grill-to-pr-loop.tests.test_planning_worktree_gate
```

Expected: FAIL because `planning_worktree.py` does not exist or required behavior is absent.

- [x] **Step 3: Implement minimal CLI**

Implementation requirements:

- canonicalize the repository root with `git rev-parse --show-toplevel`;
- parse `git worktree list --porcelain`;
- select registered default branch checkout without editing it;
- set `planning_branch = codex/<epic-id>/planning`;
- reuse a registered worktree for that exact branch;
- otherwise require the project-local worktree root to be ignored and run one `git worktree add`;
- on any failure, return non-zero before file write/stage/commit in default checkout;
- capture `head` and exact porcelain status before creation;
- atomically write only the untracked runtime artifact after successful create/reuse;
- never run reset, clean, stash, checkout, add, commit, move, or delete.

- [x] **Step 4: Run GREEN and refactor**

Run the focused test and keep all five scenarios green.

- [x] **Step 5: Update skill contract**

Add `Planning Worktree Gate` before Written Spec, one-worktree reuse across all planning gates, no repeated consent when preference exists, fail-closed sandbox behavior, and tracked/runtime identity boundary. Route `intake`, `spec`, `issue-gate`, and `execution-plan` read sets through the planning contract that owns the Gate.

- [x] **Step 6: Run Task 1 suite**

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
```

Expected: all tests pass.

---

### Task 2: PWTG-002 Durable planning identity and repository guard

**Files:**

- Create: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/repository_integrity.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/approved_spec_binding.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/validation/execution_envelope.py`
- Modify: `skills/issue-implementation-loop/assets/schemas/input-packet.schema.json`
- Modify: `skills/issue-implementation-loop/assets/templates/input-packet.json`
- Modify: `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json`
- Modify: `skills/issue-implementation-loop/assets/templates/execution-envelope.json`
- Modify: `skills/issue-implementation-loop/references/execution-envelope.md`
- Modify: `skills/issue-implementation-loop/references/worktree-lifecycle.md`
- Modify: `skills/issue-implementation-loop/tests/test_approved_spec_binding.py`
- Modify: `skills/issue-implementation-loop/tests/test_validation.py`

**Interfaces:**

- New packet fields:
  - `planning_branch: "codex/<epic-id>/planning"`
  - `planning_base_sha: <full 40/64-character SHA>`
- New optional-for-legacy Envelope field, required when the packet has planning fields:

```json
{
  "repository_guard": {
    "planning_worktree_path": "/host/path",
    "planning_branch": "codex/<epic-id>/planning",
    "planning_base_sha": "<full-sha>",
    "default_checkout": {
      "path": "/host/default-checkout",
      "branch": "main",
      "head": "<full-sha>",
      "status_porcelain_v1": ""
    }
  }
}
```

- `validate_repository_guard(envelope, packet, repo_root) -> list[str]` performs read-only validation.

- [x] **Step 1: Write failing packet/schema tests**

Add tests for:

- both planning fields accepted together;
- either field alone rejected;
- noncanonical planning branch rejected;
- short/nonhex base rejected;
- current tracked sealed v2 packet remains valid without byte edits.

- [x] **Step 2: Run packet RED**

Run focused `test_approved_spec_binding` cases; expect unknown-field/schema failures.

- [x] **Step 3: Add backward-compatible packet shape**

Allow the pair in Input Packet v2, require pair completeness and canonical values when either appears, and update the new-packet template. Do not rewrite existing sealed packets.

- [x] **Step 4: Write failing repository guard tests**

Create real temp Git worktrees and assert:

- packet/Envelope branch or base mismatch fails;
- unregistered planning path fails;
- default checkout HEAD/status drift fails;
- unchanged pre-existing dirt passes;
- Gate commit on `main` but not reachable from `epic_base.sha` returns `GATE_COMMIT_NOT_ANCESTOR`.

- [x] **Step 5: Run repository guard RED**

Expected: missing `repository_integrity.py` or validator accepts invalid fixtures.

- [x] **Step 6: Implement repository guard**

Validate all absolute host paths as registered worktrees sharing the trusted Git common directory. Compare exact branch/base/snapshot values without mutating Git or files. Call the guard from `validate_execution_envelope` after loading the active packet.

- [x] **Step 7: Run Task 2 GREEN**

```bash
python3 -m unittest skills.issue-implementation-loop.tests.test_approved_spec_binding
python3 -m unittest skills.issue-implementation-loop.tests.test_validation
```

---

### Task 3: PWTG-003 PR_READY and final delivery integrity

**Files:**

- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/repository_integrity.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/validation/execution_result.py`
- Modify: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/delivery.py`
- Modify: `skills/issue-implementation-loop/references/core.md`
- Modify: `skills/issue-implementation-loop/references/remote-delivery.md`
- Modify: `skills/issue-implementation-loop/references/recovery.md`
- Modify: `skills/issue-implementation-loop/SKILL.md`
- Modify: `skills/issue-implementation-loop/tests/test_delivery.py`
- Modify: `skills/issue-implementation-loop/tests/test_validation.py`

**Interfaces:**

- `validate_success_repository_integrity(envelope, runtime, repo_root) -> list[str]`
- `validate_final_head_integrity(envelope, runtime, execution_result, head_ref, repo_root) -> list[str]`

- [x] **Step 1: Write failing PR_READY tests**

Use real temp Git repositories. A runtime state with `PR_READY` must fail when default checkout HEAD or status differs from the guard snapshot and pass with unchanged pre-existing dirt.

- [x] **Step 2: Run PR_READY RED**

Expected: completion validation currently ignores default checkout state.

- [x] **Step 3: Implement success-status guard**

When any issue is in `PR_READY`, `COMPLETE`, or `DONE`, execution-result validation must re-run repository guard. Do not attempt recovery mutations.

- [x] **Step 4: Write failing final-head tests**

Create real commits for Gate, implementation A, implementation B, and final branch. Assert delivery fails separately when:

- actual final head omits Gate commit;
- actual final head omits one delivery candidate `head_sha`;
- runtime says `pr_merged: true` but the commit is unreachable;
- actual final head includes every required commit.

- [x] **Step 5: Run delivery RED**

Expected: omitted implementation commit is currently accepted.

- [x] **Step 6: Implement final-head guard**

Resolve the local final head ref and require ancestry for:

- `planning_base_sha`;
- `approved_spec_binding.gate_commit`;
- every delivery candidate’s full `head_sha`.

Return validation errors before remote mutation. Preserve existing draft-only/hardening checks.

- [x] **Step 7: Run Task 3 GREEN**

```bash
python3 -m unittest skills.issue-implementation-loop.tests.test_delivery
python3 -m unittest discover -s skills/issue-implementation-loop/tests
```

---

### Task 4: PWTG-004 Documentation, cross-contract verification, and review

**Files:**

- Modify: `knowledge/wiki/syntheses/planning-worktree-gate/issues.md`
- Modify: `knowledge/wiki/syntheses/planning-worktree-gate/implementation-plan.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`
- Modify only if required by validators: `skill-architecture.toml`, `context-contract.toml`

- [x] **Step 1: Synchronize durable evidence**

Record actual test counts, commits, review results, remaining risks, and `local_only` boundary. Do not track host-specific worktree paths.

- [x] **Step 2: Run full verification**

```bash
python3 -m unittest discover -s skills/grill-to-pr-loop/tests
python3 -m unittest discover -s skills/issue-implementation-loop/tests
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 scripts/validate_dual_host_compatibility.py --skill skills/issue-implementation-loop
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
python3 -m unittest discover -s scripts
git diff --check
```

- [x] **Step 3: Verify repository delivery invariants**

```bash
git merge-base --is-ancestor <execution-plan-gate-commit> HEAD
git status --short --branch
git -C <default-checkout-runtime-path> rev-parse HEAD
git -C <default-checkout-runtime-path> status --porcelain=v1 --untracked-files=all
```

The default checkout HEAD/status must equal the runtime start snapshot. Report pre-existing unrelated dirt unchanged; do not move or delete it.

- [x] **Step 4: Independent review**

Review the committed implementation range against `spec.md` and `issues.md`. Fix Critical/Important findings with test-first cycles, up to two review cycles.

## Execution Evidence

### Landed commits

- PWTG-001: `5770a69`, `89cb0e3`, `0b5fe8c`, `94eaf0f`, `dfc04b5`, `971b178`, `22ebb42`
- PWTG-002: `59c6a31`, `747227b`, `9253c6b`, `724bc31`, `a2dcd18`, `9f8eca6`, `bc557be`
- PWTG-003: `c355b08`
- phase artifacts: `6511899`, `e87a7e3`, `863711a`
- planning base `b3b869b` を含む pre-closeout 19-commit chain はすべて current planning HEAD の ancestor である。
- PWTG-004: 本 plan / Issue台帳 / index / log の同期commit。

### Fresh results

- `grill-to-pr-loop`: `58/58` pass。
- `issue-implementation-loop`: `284/284` pass。
- repository scripts: `58/58` pass。
- `llm-wiki`: `6/6` pass。
- Acceptance 1〜8 focused regressions: `18/18` pass。
- skill architecture / 3 context contracts: pass。
- changed-skill scoped dual-host compatibility: 2 skillsともpass。
- skill-creator quick validation: 2 skillsとも`Skill is valid!`。
- default checkoutのHEAD/statusはstart snapshotと一致し、approved spec / sealed Input Packet hashesは不変。
- cumulative production reviewと最終fix reviewはCritical 0 / Important 0。

approved specに残る`validate_dual_host_authoring.py`はhistorical plan defectである。sealed specとInput Packetは編集せず、実行可能な本plan / Issue台帳だけを実在する`validate_dual_host_compatibility.py`のchanged-skill scoped commandsへ訂正した。repository-wide `--all` は未変更の`llm-wiki` DESCRIPTION discovery findingだけを返し、passとは扱わない。

### Acceptance coverage

- Acceptance 1〜5: first-create、pre-existing exact worktree adoption/reuse、same planning chain、creation/post-add failure、pre-existing dirt/index preservationでcoverage。
- Acceptance 6: new guarded packetとlegacy guardless packetのphysical Gate ancestryでcoverage。
- Acceptance 7: physical planning base / Gate / all candidate final-head ancestryでcoverage。
- Acceptance 8: runtime-bound actual default checkoutのHEAD/status、substitute worktree rejection、unchanged pre-existing dirtでcoverage。
- Non-goals: generic manager、destructive recovery、default checkout自動復元、remote writeは導入していない。

### Remaining Minor risks

- Git environment policyのskill間重複。
- runtime artifact load / validateのstabilization sequence反復。
- planning/default identity parameter data clump。

いずれも最終reviewでnon-blocking Minorとして分類し、Acceptance 1〜8またはdelivery safetyを阻害しない。remote policyは`local_only`で、push、PR、merge、GitHub mutationは実施していない。

## Execution Plan Gate

- `planning_branch`: `codex/planning-worktree-gate/planning`
- `planning_base_sha`: `b3b869b60dfb785b325f754292dccf675e47313b`
- `worker_context_required`: `true`
- `coordinator_may_implement`: `false`
- `serial_fallback_mode`: `worker_context_only`
- `delivery_intent`: `local_only`
- `remote actions`: なし
- `final merge`: human-only

今回の bootstrap packet は Planning Worktree Gate 実装前の現行 Input Packet v2 validatorで seal する。これは移行作業のexecution lockであり、新規packet templateの完成形ではない。target implementation後に作る新規packetは `planning_branch` / `planning_base_sha` を必須とし、既存 sealed packetのbytesは変更しない。

## Self-review

- Spec coverage: Acceptance Tests 1〜8 は Task 1〜4 のいずれかに対応している。
- Placeholder scan: code symbol、field name、command、expected failureを明示し、`TBD` / `TODO` はない。
- Type consistency: `planning_branch`、`planning_base_sha`、`repository_guard`、`status_porcelain_v1` を全taskで同じ名称にした。
- Scope: generic manager、default checkout recovery、remote writeを含めていない。

## 関連ページ

- [Planning Worktree Gate 仕様](spec.md)
- [Planning Worktree Gate Issue 台帳](issues.md)

## 出典

- [Planning Worktree Gate 仕様](spec.md)
- [Planning Worktree Gate Issue 台帳](issues.md)

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

PWTG-001〜PWTG-004をTDDで実装完了し、planning identity、default checkout snapshot、physical final head reachabilityの実測evidenceを記録したExecution Plan。
