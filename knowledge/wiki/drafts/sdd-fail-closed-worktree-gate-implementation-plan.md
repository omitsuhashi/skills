---
title: SDD fail-closed worktree gate 実装計画
page_type: draft-note
date: 2026-08-14
created_date: 2026-08-14
last_updated: 2026-08-14
tags:
  - sdd-implementation
  - worktree
  - fail-closed
  - git-guard
  - implementation-plan
aliases:
  - SDD fail-closed worktree gate implementation plan
status: proposed
lifecycle_state: proposed
artifact_kind: implementation-plan
review_state: awaiting-owner-review
confidence: high
target_root: knowledge
canonical_target: "[[wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan|SDD fail-closed worktree gate 実装計画]]"
source_spec: "[[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|SDD fail-closed worktree gate 仕様]]"
created_actor: fresh SDD Plan Author Worker
requested_owner_action: promote after review
reason_direct_update_unavailable: implementation plan は Human / repository maintainer の review と明示承認前であるため
relations:
  - "[[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|Implements: SDD fail-closed worktree gate 仕様]]"
  - "[[wiki/syntheses/sdd-first-write-worktree-migration-spec|Normative predecessor: SDD first-write worktree migration 仕様]]"
---

# SDD fail-closed worktree gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** repository change の唯一の入口を `sdd-implementation` に固定し、First-Write Worktree Gate の relevant failure を observable な zero-write `BLOCKED` に統一するとともに、primary checkout commit を拒否する repo-managed `prepare-commit-msg` guard の source、read-only preflight、明示 setup 用 transaction/rollback interface を実装する。

**Architecture:** repo-owned router、architecture policy、portable SDD contract が external writable subskill より先の authority と no-fallback precedence を宣言し、deterministic scenario harness が writer/runner を dependency injection して prohibited command の非実行と original fingerprint 不変を観測する。Git guard は tracked executable source とし、activation tool は complete config/hook inventory を mutation 前後で比較するが、この plan の実行では current clone を activate せず、temporary repository fixture 内だけで transaction/rollback を検証する。

**Tech Stack:** Markdown / Obsidian properties、Python standard library（Python 3.9+、`argparse`、`dataclasses`、`hashlib`、`json`、`os`、`pathlib`、`shutil`、`stat`、`subprocess`、`tempfile`、`unittest`）、Git worktree/config/hooks、既存 architecture/context/skill-creator validators、GitHub Actions。

## Status and owner request

- 現在状態: `proposed` / non-canonical draft。verified claim または実行承認として扱わない。
- 承認済み入力: [[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|SDD fail-closed worktree gate 仕様]]（Human-approved、2026-08-14）。
- canonical plan destination: `knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan.md`。
- requested owner action: Human / repository maintainer が本 plan を review し、変更なく妥当なら `promote` を明示承認する。
- approval boundary: Task 0 が完了するまで Implementation Stage、source/test write、current clone activation を開始しない。現 draft 作成時は `knowledge/index.md` / `knowledge/log.md` を変更しない。

## Global Constraints

- 承認済み spec の substantive decisions と Open Decisions `なし` を維持し、plan 内で再決定しない。
- one-time self-hosting bootstrap authority は次の exact tuple にだけ適用する: Epic `sdd-fail-closed-worktree-gate`; branch `codex/sdd-fail-closed-worktree-gate/planning`; registered planning worktree `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/sdd-fail-closed-worktree-gate-planning`; creation base / captured `starting_head_sha` `c370fe14de1641aa5ee30b3fa001f4d857078091`。
- bootstrap は同じ continuing controller の trusted tuple が維持される間、この planning worktree 内の source、tests、spec、plan の author/test/commit だけを許す。activation、original checkout write/commit、external cache edit、fallback、別 task/chat/worktree への reuse は許さない。
- ordinary repository task は guard missing、unconfigured、damaged、identity unknown、allocation/path/ownership/capability/downstream conflict のいずれでも `status: blocked`、`artifact_path: none`、zero content/artifact write、writer/runner invocation `0` とする。
- Git guard は secondary accidental-commit defense であり First-Write Gate の代替ではない。primary checkout と unknown identity を reject し、canonical registration を証明した named linked worktree だけを allow する。hook point は通常の `git commit --no-verify` で suppress されない `prepare-commit-msg` に固定する。
- supported activation model は、全 scope の `core.hooksPath` unset、config-related environment override absent、全 registered worktree の effective/default hooks directory が一意かつ同一、standard non-executable `*.sample` 以外の hook absent、target absent の clone に guard 一件を追加し、Git config を変更しない model だけとする。
- activation は ordinary SDD gate と別の Human-authorized setup operation である。本実装 plan は activation source/interface と temporary-repository tests を作るが、current clone で `activate` を実行する task を含めない。
- activation mutation 後の failure は zero-write と呼ばない。exact prior inventory を byte/type/mode/symlink target/config value+origin まで再証明できた場合だけ `BLOCKED: activation failed; zero net clone-local state proven`、できなければ `BLOCKED: activation incomplete` + exact changed-state evidence とする。
- external Superpowers cache、active installed tree、live install、plugin update、remote issue/PR/push/merge/release は変更しない。repo-owned route から unsafe fallback を unreachable/incompatible にする。
- scheduler、lock、packet/event schema、runtime state/snapshot、compatibility bridge、context telemetry、manual compaction、`CONTEXT.md`、`docs/adr/`、old-loop fallback を作らない。
- implementation write set に spec draft/canonical spec/index/log lifecycle write を混ぜない。Plan Gate sync と implementation closeout は source implementation task から分離する。
- original checkout `/Users/omitsuhashi/repos/omitsuhashi/skills` は開始時の branch `main`、HEAD `c370fe14de1641aa5ee30b3fa001f4d857078091`、clean status のまま保つ。mismatch 時は reset/stash/clean/checkout せず `BLOCKED`。
- final full-range whitespace gate は `git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD` とする。

---

## File Structure

| Path | Change | Responsibility |
| --- | --- | --- |
| `AGENTS.md` | Modify | repository change の first entry、direct pre-gate rejection、downstream conflict precedence を最上位 router に固定する。 |
| `skill-architecture.toml` | Modify | `first_entry_skill`、pre-gate writable subskill policy、downstream conflict action、guard activation ownershipを machine-readable に固定する。 |
| `scripts/validate_skill_architecture.py` | Modify | architecture policy の exact values と router contract を fail closed で検証する。 |
| `scripts/test_validate_skill_architecture.py` | Modify | policy/router drift を red/green で検証する。 |
| `skills/sdd-implementation/SKILL.md` | Modify | entry/gate ordering、guard preflight、bootstrap、zero-write failure、downstream no-fallback、source/install/cache/activation lifecycle を portable contract として宣言する。 |
| `skills/sdd-implementation/references/planning-context.md` | Modify | Plan Author を含む controller preflight、guard status、four-field result、bootstrap lifetime、result path revalidation を固定する。 |
| `skills/sdd-implementation/references/research-stage.md` | Modify | guard/gate failure 後の report absent と no-fallback を research handoff に固定する。 |
| `skills/sdd-implementation/prompts/repository-researcher.md` | Modify | bound writer が allocation/activation/fallback を所有しないことを明示する。 |
| `skills/sdd-implementation/prompts/spec-synthesizer.md` | Modify | 同じ downstream composition boundary を spec writer に明示する。 |
| `skills/sdd-implementation/prompts/spec-reviewer.md` | Modify | 同じ downstream composition boundary を review writer に明示する。 |
| `skills/sdd-implementation/scripts/prepare-commit-msg` | Create | tracked executable canonical guard source。primary/unknown reject、registered linked worktree allow、read-only `--self-check` を提供する。 |
| `skills/sdd-implementation/scripts/activate_commit_guard.py` | Create | JSON-producing `preflight` / `self-check` CLI と、明示 setup 時だけ使える transactional `activate` library/CLI を提供する。 |
| `skills/sdd-implementation/tests/harnesses/__init__.py` | Create | harness package marker。 |
| `skills/sdd-implementation/tests/harnesses/fail_closed_scenario.py` | Create | injected allocator/writer/runner、command recorder、bootstrap verdict、complete repository fingerprint を持つ deterministic behavior harness。 |
| `skills/sdd-implementation/tests/harnesses/git_config_hook_inventory.py` | Create | isolated repo/worktree、include/worktree config、hook collision fixture と exact inventory assertion helper。 |
| `skills/sdd-implementation/tests/fixtures/unsafe_downstream.py` | Create | 実行された場合だけ supplied marker を作る prohibited-command fixture。 |
| `skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py` | Create | SDD-first route、direct pre-gate rejection、downstream conflict、bootstrap non-reuse、lifecycle separation。 |
| `skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py` | Create | injected `EACCES` / sandbox denial、zero-write、prohibited command absent、original preservation。 |
| `skills/sdd-implementation/tests/test_commit_guard_behavior.py` | Create | guard identity、complete inventory、preflight、temporary-repo activation/rollback、primary/linked commit subprocess behavior。 |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Modify | new `scripts` resource shape、portable input/output/capability/failure/lifecycle prose contract。 |
| `.github/workflows/skill-architecture.yml` | Modify | three focused behavioral modulesを明示実行してから既存 full discovery を実行する。 |
| `scripts/test_skill_ci_workflow.py` | Modify | focused CI commands と full regression の両方が残ることを検証する。 |
| `knowledge/wiki/drafts/sdd-fail-closed-worktree-gate-implementation-plan.md` | Modify in Task 0 only | owner decisionを記録した promoted lifecycle evidence。 |
| `knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan.md` | Create in Task 0 only | Human-approved canonical implementation plan。 |
| `knowledge/index.md`, `knowledge/log.md` | Modify in Task 0 / closeout only | Plan Gate promotion sync と後日の implementation closeout。source tasksでは変更しない。 |

`skills/sdd-implementation/agents/openai.yaml`、external Superpowers cache、`.agents` installed tree、canonical spec は変更しない。既存 `.github/workflows/skill-architecture.yml` の Python 3.9 / 3.12 matrix と standard-library-only policy を維持する。

## Public interfaces and exact types

### Scenario harness

```python
@dataclass(frozen=True)
class BootstrapContext:
    epic: str
    branch: str
    worktree: Path
    starting_head_sha: str
    same_controller: bool
    tuple_trusted: bool
    lifecycle: str       # "bootstrap" or "later_task"
    requested_scope: str # "source", "test", "spec", "plan", or "activation"

@dataclass(frozen=True)
class ControlReturn:
    status: str
    artifact_path: str
    decision_requests: str
    material_risks: str

@dataclass(frozen=True)
class RepositoryFingerprint:
    branch: str
    head: str
    index: bytes
    cached_diff: bytes
    worktree_diff: bytes
    status: bytes
    tracked_and_untracked: tuple[tuple[str, bytes], ...]
    commit_count: int

@dataclass(frozen=True)
class ScenarioResult:
    control_return: ControlReturn
    writer_invocations: int
    runner_invocations: int
    attempted_commands: tuple[tuple[str, ...], ...]
    executed_commands: tuple[tuple[str, ...], ...]
    before: RepositoryFingerprint
    after: RepositoryFingerprint
```

`run_repository_change` の exact signature は `run_repository_change(*, original: Path, entry_skill: str, guard_status: str, bootstrap: Optional[BootstrapContext], allocator: Callable[[], Path], writer: Callable[[Path], None], downstream_command: Optional[tuple[str, ...]], command_runner: Callable[[tuple[str, ...]], int]) -> ScenarioResult` とする。`entry_skill == "sdd-implementation"`、guard verdict、allocation result、ownership/containment、bootstrap exact tuple、downstream compatibility をこの順に評価する。fail branch は callback を呼ばず four-field `blocked` を返す。attempted command は policy input として記録できるが、runner に渡した command だけを executed list に入れる。

### Guard and activation

```python
@dataclass(frozen=True)
class CommandRecord:
    argv: tuple[str, ...]
    cwd: str
    returncode: int
    stdout: bytes
    stderr: bytes

@dataclass(frozen=True)
class FileIdentity:
    path: str
    kind: str
    mode: int
    sha256: Optional[str]
    symlink_target: Optional[str]

@dataclass(frozen=True)
class WorktreeRecord:
    path: str
    head: str
    branch: Optional[str]
    detached: bool
    locked: bool
    prunable: bool
    git_dir: str
    common_dir: str
    config_worktree: Optional[FileIdentity]
    effective_hooks_dir: str

@dataclass(frozen=True)
class HookConfigInventory:
    repository: str
    common_dir: str
    worktrees: tuple[WorktreeRecord, ...]
    command_records: tuple[CommandRecord, ...]
    config_records: tuple[tuple[str, str, str, str], ...]
    config_files: tuple[FileIdentity, ...]
    config_environment: tuple[tuple[str, str], ...]
    hook_directories: tuple[tuple[str, tuple[FileIdentity, ...]], ...]
    source: FileIdentity

@dataclass(frozen=True)
class OperationResult:
    status: str  # "ok", "activated", or "blocked"
    reason: str
    before: HookConfigInventory
    after: Optional[HookConfigInventory]
    changed_state: tuple[FileIdentity, ...]
```

Production signatures are fixed as follows.

- `collect_inventory(repository: Path) -> HookConfigInventory`
- `preflight_repository(repository: Path) -> OperationResult`
- `self_check(repository: Path, checkout: Path) -> OperationResult`
- `activate_repository(repository: Path, *, explicit_setup: bool, fault_injector: Optional[Callable[[str, Path], None]] = None) -> OperationResult`

`fault_injector` は in-process temporary-repository test 専用で CLI から指定できない。CLI は `preflight --repository PATH`、`self-check --repository PATH --checkout PATH`、`activate --repository PATH --confirm-explicit-setup` のみを公開し、stdout に stable JSON、diagnostic を stderr、success/allow は exit `0`、blocked/reject は nonzero で返す。current clone に対する `activate` command は本 plan のどの task でも実行しない。

## Acceptance coverage matrix

| Approved scenario | Exact executable coverage |
| --- | --- |
| SDD-first route / direct pre-gate rejection | `FailClosedEntryBehaviorTests.test_sdd_is_the_only_allowed_first_entry`, `test_direct_writable_subskill_is_blocked_before_callback` |
| allocation `EACCES` / sandbox failure zero-write | `FailClosedAllocationBehaviorTests.test_eacces_is_zero_write_blocked`, `test_sandbox_denial_is_zero_write_blocked` |
| prohibited downstream commands not executed | `FailClosedEntryBehaviorTests.test_conflicting_downstream_command_is_recorded_but_not_executed` |
| primary normal and `--no-verify` commit rejected | `CommitGuardBehaviorTests.test_primary_commit_and_no_verify_are_rejected` |
| registered linked worktree commit allowed | `CommitGuardBehaviorTests.test_registered_linked_worktree_commit_is_allowed` |
| unknown/unregistered/detached identity blocked | `CommitGuardBehaviorTests.test_unknown_checkout_identity_fails_closed` |
| external fallback conflict blocked | `test_conflicting_downstream_command_is_recorded_but_not_executed` plus architecture/router contract tests |
| complete config/worktree/hook inventory | `CommitGuardBehaviorTests.test_inventory_records_every_required_command_and_candidate`, `test_include_and_worktree_config_are_inventoried` |
| activation collision pre-mutation blocked | `CommitGuardBehaviorTests.test_all_config_and_hook_collisions_block_before_mutation` |
| transactional activation / exact rollback / incomplete result | `test_clean_fixture_activation_adds_only_guard`, `test_post_probe_failure_proves_zero_net_rollback`, `test_rollback_drift_reports_activation_incomplete` |
| missing/damaged/unconfigured guard blocked without repair | `CommitGuardBehaviorTests.test_preflight_missing_damaged_and_unconfigured_are_read_only_blocked`, `FailClosedEntryBehaviorTests.test_guard_failure_blocks_ordinary_task_without_writer` |
| bootstrap exception exact tuple and non-reuse | `FailClosedEntryBehaviorTests.test_exact_bootstrap_tuple_allows_only_source_test_spec_plan`, `test_bootstrap_cannot_be_reused_or_reconstructed` |
| original checkout preservation | every scenario compares `RepositoryFingerprint`; linked commit test also compares primary fingerprint |
| source/install/cache/activation separation | `SddImplementationSkillContractTests.test_fail_closed_lifecycle_states_are_separate` and router/validator policy |

### Task 0: Promote the reviewed plan and synchronize Plan Gate

**Files:** Modify `knowledge/wiki/drafts/sdd-fail-closed-worktree-gate-implementation-plan.md`; create `knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan.md`; modify `knowledge/index.md`, `knowledge/log.md`.

**Interfaces:** Consumes Human `promote` decision for this exact draft and accepted spec; produces one active canonical plan relation and one append-only Plan Gate event. Produces no source/test/guard change.

- [ ] **Step 1: Gate on explicit Human approval**

  Require the Human / repository maintainer to approve this exact draft and request `promote`. If decision is absent, `defer`、`reject`、or requests substantive edits, stop before canonical/index/log write and return the four-field result with `status: needs_decision` or `blocked` as applicable.

- [ ] **Step 2: Write the promotion sync set only**

  Change draft `status` / `lifecycle_state` to `promoted` and record `decision`, `decision_actor`, `decision_date`, `decision_reason`, `destination`. Create the canonical synthesis with `status: accepted`, `lifecycle_state: active`, source draft relation, accepted spec relation, and the approved plan body unchanged. Add exactly one active canonical catalog entry to `knowledge/index.md`; append one Japanese `draft-review / promote / Plan Gate` event to `knowledge/log.md`.

- [ ] **Step 3: Verify promotion semantics**

Run: `rg -n "sdd-fail-closed-worktree-gate-implementation-plan" knowledge/index.md knowledge/log.md knowledge/wiki/drafts/sdd-fail-closed-worktree-gate-implementation-plan.md knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan.md`

Expected: draft, canonical, one active index relation, one appended promote event are discoverable; the canonical relation is not duplicated.

Run: `git diff --check`

Expected: no output, exit `0`.

- [ ] **Step 4: Commit the Plan Gate separately**

```bash
git add knowledge/wiki/drafts/sdd-fail-closed-worktree-gate-implementation-plan.md knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-implementation-plan.md knowledge/index.md knowledge/log.md
git commit -m "docs: approve fail-closed SDD implementation plan"
```

Expected: one Plan Gate commit; no `AGENTS.md`、skill、script、test、workflow path in this commit.

### Task 1: Enforce SDD-first routing and fail-closed scenario behavior

**Files:** Create `skills/sdd-implementation/tests/harnesses/__init__.py`, `skills/sdd-implementation/tests/harnesses/fail_closed_scenario.py`, `skills/sdd-implementation/tests/fixtures/unsafe_downstream.py`, `skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py`, `skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py`; modify `AGENTS.md`, `skill-architecture.toml`, `skills/sdd-implementation/SKILL.md`, both `references/*.md`, all three `prompts/*.md`.

**Interfaces:** Consumes the exact bootstrap tuple and existing four-field Control Return; produces the scenario types/signature above and a portable no-fallback contract used by later validator/CI tasks. Does not consume or invoke activation.

- [ ] **Step 1: Write the entry and allocation behavior tests first**

  Create `FailClosedEntryBehaviorTests` with exact methods `test_sdd_is_the_only_allowed_first_entry`, `test_direct_writable_subskill_is_blocked_before_callback`, `test_conflicting_downstream_command_is_recorded_but_not_executed`, `test_guard_failure_blocks_ordinary_task_without_writer`, `test_exact_bootstrap_tuple_allows_only_source_test_spec_plan`, `test_bootstrap_cannot_be_reused_or_reconstructed`。Create `FailClosedAllocationBehaviorTests` with exact methods `test_eacces_is_zero_write_blocked`, `test_sandbox_denial_is_zero_write_blocked`。

  Each blocked assertion must require `ControlReturn("blocked", "none", "none", reason)`, `writer_invocations == 0`, `runner_invocations == 0`, `executed_commands == ()`, before/after fingerprint equality, report/spec/plan absence, and commit count unchanged. Exact reasons are `SDD First-Write Worktree Gate required`, `downstream incompatible with SDD containment`, `guard_missing`, `guard_unconfigured`, `guard_damaged`, `worktree allocation denied: EACCES`, and `worktree allocation denied: sandbox`。The downstream conflict case additionally requires one attempted tuple for `unsafe_downstream.py`, marker absence, and no runner invocation. Bootstrap allow requires all four exact identity fields, same controller, trusted tuple, lifecycle `bootstrap`, and scope in `{source,test,spec,plan}`; every single-field mismatch、`activation` scope、`later_task`、tuple loss、別 controller を table-driven blocked casesにする。

- [ ] **Step 2: Run focused tests to prove red**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py -v`

Expected: FAIL/ERROR naming missing `tests.harnesses.fail_closed_scenario` or missing `run_repository_change`; no repository artifact is created by the failed test.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py -v`

Expected: FAIL/ERROR for the same missing harness interface; no report/spec/plan is created.

- [ ] **Step 3: Implement the deterministic harness and prohibited fixture minimally**

  Implement the dataclasses and `fingerprint_repository(root: Path) -> RepositoryFingerprint` using `git branch --show-current`, `rev-parse HEAD`, `ls-files --stage -z`, cached/worktree binary diffs, porcelain status, all tracked/untracked file bytes, and `rev-list --count HEAD`. Implement `run_repository_change` as an ordered pure policy gate: entry → guard/bootstrap → allocation → registration/ownership/containment → downstream compatibility → writer. Catch injected `PermissionError(errno.EACCES, ...)` and `SandboxDenied` as blocked without invoking writer/runner. `unsafe_downstream.py` accepts exactly one marker path argument and writes it; the harness never executes it on a conflicting policy branch.

- [ ] **Step 4: Update repo-owned routing and portable contract**

  In `AGENTS.md`, expand `## Default implementation route` with these normative sentences:

```markdown
- `sdd-implementation` is the first repository-change entry, before brainstorming, writing-plans, using-git-worktrees, domain modeling, implementation, or any other writable supporting skill.
- A direct writable supporting-skill entry returns `BLOCKED: SDD First-Write Worktree Gate required`; it does not silently switch routes and continue.
- Repository entry, containment, zero-write, and no-fallback rules override conflicting downstream instructions. Allocation, permission, sandbox, capability, dependency, guard, identity, or path failure never continues in the current/original checkout.
```

  Add these exact policy keys under `[families.repository-change-loop]`:

```toml
first_entry_skill = "sdd-implementation"
pre_gate_writable_subskill_action = "blocked"
downstream_conflict_action = "blocked"
guard_activation_owner = "separate_human_authorized_setup"
```

  In `SKILL.md`, place repository-entry rejection and read-only guard preflight before allocation and Planning Controller; define `Gate Pass` as non-durable; state the exact bootstrap tuple and expiration; map every relevant failure to zero-write four-field `BLOCKED`; prohibit fallback/current-directory/ignore repair/automatic activation. In planning/research references and all three prompts, require bound root/CWD/path、guard verdict、writer ownership、original preservation; writers must return `blocked` and must not allocate, activate, select a fallback root, or write outside binding. Preserve existing fresh-dispatch/model and Control Return contracts.

- [ ] **Step 5: Run the same tests green and the existing contract suite**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py -v`

Expected: all six named tests PASS.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py -v`

Expected: both denial tests PASS and each proves complete fingerprint equality.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_first_write_worktree_contract.py -v`

Expected: existing first-write tests PASS; do not change test discovery topology.

- [ ] **Step 6: Review Task 1 write set and commit**

Run: `git diff --name-only -- AGENTS.md skill-architecture.toml skills/sdd-implementation`

Expected: only Task 1 listed paths; no external cache、installed tree、index/log、activation script。

```bash
git add AGENTS.md skill-architecture.toml skills/sdd-implementation/SKILL.md skills/sdd-implementation/references/planning-context.md skills/sdd-implementation/references/research-stage.md skills/sdd-implementation/prompts/repository-researcher.md skills/sdd-implementation/prompts/spec-synthesizer.md skills/sdd-implementation/prompts/spec-reviewer.md skills/sdd-implementation/tests/harnesses/__init__.py skills/sdd-implementation/tests/harnesses/fail_closed_scenario.py skills/sdd-implementation/tests/fixtures/unsafe_downstream.py skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py
git commit -m "feat: fail closed before SDD repository writes"
```

### Task 2: Implement the checkout-identity commit guard source

**Files:** Create `skills/sdd-implementation/scripts/prepare-commit-msg`; create the commit behavior portion of `skills/sdd-implementation/tests/test_commit_guard_behavior.py`; modify `skills/sdd-implementation/tests/test_skill_contract.py`.

**Interfaces:** Consumes current toplevel、absolute git dir/common dir、symbolic branch、HEAD、`git worktree list --porcelain -z`; produces exit `0` only for one matching registered linked worktree and nonzero bounded diagnostic otherwise. Later activation copies these exact bytes/mode.

- [ ] **Step 1: Write guard subprocess tests first**

  In `CommitGuardBehaviorTests`, create exact methods `test_primary_commit_and_no_verify_are_rejected`, `test_registered_linked_worktree_commit_is_allowed`, and `test_unknown_checkout_identity_fails_closed`。

  Temporary fixtures initialize `main`, configure test user, commit one base file, install the repository source bytes as `.git/hooks/prepare-commit-msg` mode `0o755`, and record commit count/fingerprint. Primary normal and `--no-verify` both must return nonzero with `SDD commit guard: primary checkout rejected`, and commit count remains unchanged. Linked fixture uses `git worktree add -b topic/allowed`, installs once in common hooks, commits exactly once from linked checkout, and proves primary fingerprint unchanged. Unknown cases cover detached linked HEAD、registration mismatch simulated by a copied checkout path、missing/ambiguous git-dir evidence; all reject without content mutation by guard.

- [ ] **Step 2: Prove red**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py CommitGuardBehaviorTests.test_primary_commit_and_no_verify_are_rejected -v`

Expected: FAIL because `skills/sdd-implementation/scripts/prepare-commit-msg` is absent or primary commit succeeds.

- [ ] **Step 3: Implement the executable guard**

  Create a mode-`100755` Python executable with a shebang. `checkout_verdict(cwd: Path) -> tuple[bool, str]` runs only read-only Git commands. Reject if any command fails; current branch is detached; `git_dir == common_dir`; current git dir is not a direct `common_dir/worktrees/<id>` registration; its `gitdir` backlink does not identify `<canonical-toplevel>/.git`; or no single porcelain record matches canonical toplevel、HEAD、`refs/heads/<branch>`。Do not allow by branch name、path prefix、`.worktrees` directory name、record order alone. Normal hook invocation ignores commit-message content and exits by verdict; `--self-check` prints stable JSON and creates no commit/content/config.

- [ ] **Step 4: Update resource-shape and portable contract tests**

  Change `test_skill_has_only_the_internal_stage_resource_shape` expected children to include `scripts` and assert `prepare-commit-msg` is present and executable. Add `test_fail_closed_lifecycle_states_are_separate` requiring repo source completion、active installed copy、external dependency/cache、guard activation/operational verification to remain distinct and forbidding absolute cache/version/provider literals in portable documents. Task 3 strengthens the script inventory to exact equality after both approved scripts exist.

- [ ] **Step 5: Run guard behavior green**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v`

Expected at this intermediate task: the three guard identity tests PASS; activation/inventory tests are not added until Tasks 3–4.

- [ ] **Step 6: Commit the guard source and its identity tests**

```bash
git add skills/sdd-implementation/scripts/prepare-commit-msg skills/sdd-implementation/tests/test_commit_guard_behavior.py skills/sdd-implementation/tests/test_skill_contract.py
git commit -m "feat: reject commits from primary checkouts"
```

### Task 3: Build complete read-only hook/config inventory and ordinary preflight

**Files:** Create `skills/sdd-implementation/scripts/activate_commit_guard.py`, `skills/sdd-implementation/tests/harnesses/git_config_hook_inventory.py`; extend `skills/sdd-implementation/tests/test_commit_guard_behavior.py`.

**Interfaces:** Consumes the guard source from Task 2 and every registered worktree/config/hook candidate; produces immutable `HookConfigInventory`, ordinary `preflight_repository`, and `self_check`. `preflight` never installs or repairs.

- [ ] **Step 1: Add inventory/preflight tests before implementation**

  Add exact methods `test_inventory_records_every_required_command_and_candidate`, `test_include_and_worktree_config_are_inventoried`, `test_all_config_and_hook_collisions_block_before_mutation`, and `test_preflight_missing_damaged_and_unconfigured_are_read_only_blocked`。

  Fixture builder must create primary + two linked worktrees and independently exercise: common config include、conditional include evaluated per worktree、`extensions.worktreeConfig=true` with applicable `config.worktree`、unset key exit `1` semantics、relative and absolute `core.hooksPath` records、default/common/worktree-specific hook candidates、custom non-target hook、existing target、executable sample、symlink hook、config environment override。Every collision case captures full before inventory, runs preflight, requires `status == "blocked"`, exact reason, after inventory equality, and no target/staging path.

  In `test_skill_contract.py`, strengthen the script inventory assertion to exact equality `{"activate_commit_guard.py", "prepare-commit-msg"}` now that both approved production files exist.

- [ ] **Step 2: Prove focused red state**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py CommitGuardBehaviorTests.test_inventory_records_every_required_command_and_candidate -v`

Expected: ERROR naming missing `activate_commit_guard.collect_inventory`.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py CommitGuardBehaviorTests.test_preflight_missing_damaged_and_unconfigured_are_read_only_blocked -v`

Expected: ERROR naming missing `preflight_repository`; fixture inventory remains unchanged.

- [ ] **Step 3: Implement exact command capture**

  `collect_inventory` must execute and preserve argv/cwd/exit/stdout/stderr for the complete approved list:

```text
git worktree list --porcelain -z
git rev-parse --path-format=absolute --git-common-dir
git config --file <common>/config --includes --null --list
git config --show-origin --show-scope --includes --null --list
git config --show-origin --show-scope --includes --null --get-all extensions.worktreeConfig
git config --show-origin --show-scope --includes --null --get-all core.hooksPath
git -C <worktree> rev-parse --path-format=absolute --git-dir
git -C <worktree> rev-parse --path-format=absolute --git-common-dir
git -C <worktree> rev-parse --path-format=absolute --git-path config.worktree
git -C <worktree> rev-parse --path-format=absolute --git-path hooks
git config --file <applicable-config.worktree> --includes --null --list
git -C <worktree> config --show-origin --show-scope --includes --null --list
git -C <worktree> config --show-origin --show-scope --includes --null --get-all extensions.worktreeConfig
git -C <worktree> config --show-origin --show-scope --includes --null --get-all core.hooksPath
git -C <worktree> config --path --includes --get-all core.hooksPath
```

  Record `--get-all` exit `1` + empty output as unset; any other nonzero or nonempty exit-1 is inventory failure. Run `--file config.worktree` only when worktreeConfig makes it applicable; applicable missing/unreadable and unexpected file while disabled are ambiguous blocked states. Record every config origin file identity、common/config.worktree bytes/mode/owner、all `GIT_CONFIG_*` override keys、all candidate directory entries with type/mode/hash/symlink target/sample bit。Do not normalize away origins or infer missing records.

- [ ] **Step 4: Implement ordinary preflight and self-check**

  `preflight_repository` requires target `prepare-commit-msg` to exist in the one effective default/common hooks directory, mode executable, regular non-symlink, and byte-identical to tracked executable source; config environment and every `core.hooksPath` record must be absent; complete inventory must be unambiguous. Missing is `blocked: guard_missing`; absent correct active location is `guard_unconfigured`; content/mode/source mismatch is `guard_damaged`; any config/custom hook ambiguity is its exact collision reason. It returns without calling `activate_repository` or mutating any file/config. `self_check` combines preflight with guard `--self-check` for the specified checkout.

- [ ] **Step 5: Run all inventory/preflight cases green**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v`

Expected: all guard identity and inventory/preflight tests present so far PASS; every blocked fixture has exact before/after inventory equality.

- [ ] **Step 6: Commit read-only tooling**

```bash
git add skills/sdd-implementation/scripts/activate_commit_guard.py skills/sdd-implementation/tests/harnesses/git_config_hook_inventory.py skills/sdd-implementation/tests/test_commit_guard_behavior.py
git commit -m "feat: inventory SDD commit guard state"
```

### Task 4: Implement temporary-repository activation transaction and rollback semantics

**Files:** Extend `skills/sdd-implementation/scripts/activate_commit_guard.py`, `skills/sdd-implementation/tests/test_commit_guard_behavior.py`.

**Interfaces:** Consumes two exact equal inventories around the mutation boundary and `explicit_setup=True`; produces `activated`, pre-mutation blocked, exact zero-net blocked, or `activation incomplete`. No caller in ordinary SDD invokes it.

- [ ] **Step 1: Add activation tests first**

  Add exact methods `test_clean_fixture_activation_adds_only_guard`, `test_post_probe_failure_proves_zero_net_rollback`, `test_rollback_drift_reports_activation_incomplete`, and `test_activation_requires_explicit_setup_and_rechecks_inventory`。

  Clean fixture must have committed tracked source, all scopes hooksPath unset, no config overrides, no custom/non-sample/executable hooks, common default hooks candidate shared by every worktree, target absent. Success asserts config bytes and sample identities unchanged, one added target identical to source, no staging residue, primary self-check reject, linked self-check allow. Fault `after_rename` forces post-probe failure; rollback removes only transaction-owned path and exact prior inventory equality yields the zero-net reason. Drift injector modifies a separate config/hook identity before rollback comparison; tool must stop, retain exact before/after/remaining path/failed step evidence, and return `activation incomplete` without further repair.

- [ ] **Step 2: Prove activation tests red**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py CommitGuardBehaviorTests.test_clean_fixture_activation_adds_only_guard -v`

Expected: FAIL because `activate_repository` returns unimplemented/blocked and target is absent.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py CommitGuardBehaviorTests.test_post_probe_failure_proves_zero_net_rollback -v`

Expected: FAIL because zero-net rollback reason/inventory proof is missing.

- [ ] **Step 3: Implement supported-candidate decision and transaction**

  Internally separate `activation_candidate(inventory)` from ordinary preflight: activation candidate requires target absent, while ordinary preflight requires target present and correct. `activate_repository` first rejects `explicit_setup=False`; collects candidate inventory; runs primary/linked source self-check simulation; recollects inventory immediately before mutation and requires exact equality. Create a unique `.<target>.stage-<pid>-<random>` in the target directory with `O_CREAT|O_EXCL`, copy exact bytes/mode, fsync file and directory, verify stage identity/self-check, recollect and compare inventory, then `os.replace(stage, target)` only if target is still absent. Do not modify Git config.

- [ ] **Step 4: Implement post-probe and bounded rollback**

  After rename, verify installed/source identity、complete hook inventory delta exactly one target、config unchanged、primary reject、every registered named linked worktree allow. On failure, remove only the transaction-owned stage/target after confirming its identity; recollect complete inventory. Exact equality with initial inventory returns `blocked` reason `activation failed; zero net clone-local state proven`. Any remove failure、owner ambiguity、concurrent drift、identity mismatch returns `blocked` reason `activation incomplete` with `changed_state` and failed stage; do not attempt config repair、hook chaining、second rollback wave。

- [ ] **Step 5: Exercise activation only in temporary fixtures**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v`

Expected: all named tests PASS. Command output must show only temporary directory paths; there is no invocation of `activate --repository /Users/omitsuhashi/repos/omitsuhashi/skills` or the planning worktree.

- [ ] **Step 6: Commit transaction behavior**

```bash
git add skills/sdd-implementation/scripts/activate_commit_guard.py skills/sdd-implementation/tests/test_commit_guard_behavior.py
git commit -m "feat: add transactional commit guard setup"
```

### Task 5: Enforce architecture drift and CI discovery

**Files:** Modify `scripts/validate_skill_architecture.py`, `scripts/test_validate_skill_architecture.py`, `.github/workflows/skill-architecture.yml`, `scripts/test_skill_ci_workflow.py`.

**Interfaces:** Consumes policy keys from Task 1 and three focused test module paths; produces fail-closed architecture validation and CI commands without hard-coding external cache/provider/version.

- [ ] **Step 1: Write validator and CI contract tests first**

  Add table-driven tests that mutate each new policy key and expect one exact error:

```python
EXPECTED_FIRST_WRITE_POLICY = {
    "first_entry_skill": "sdd-implementation",
    "pre_gate_writable_subskill_action": "blocked",
    "downstream_conflict_action": "blocked",
    "guard_activation_owner": "separate_human_authorized_setup",
}
```

  Add router tests for exact direct-entry `BLOCKED` diagnostic and no current/original continuation. In `test_skill_ci_workflow.py`, require a step named `Run fail-closed SDD behavior tests` containing each exact focused command and retain `python3 -m unittest discover -s skills/sdd-implementation/tests`.

- [ ] **Step 2: Prove red**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest scripts.test_validate_skill_architecture scripts.test_skill_ci_workflow -v`

Expected: FAIL on missing first-write policy validation and missing focused CI step; existing unrelated tests remain PASS.

- [ ] **Step 3: Implement minimal validator and workflow changes**

  Extend validator allowed/required fields under the existing repository-change family; compare exact values and reject missing/unknown/drift. Do not inspect external filesystem or installed cache. Add one CI step with the three spec-fixed commands, then leave existing full SDD discovery step intact:

```yaml
      - name: Run fail-closed SDD behavior tests
        run: |
          PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py -v
          PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py -v
          PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v
```

- [ ] **Step 4: Run focused validator/CI tests green**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest scripts.test_validate_skill_architecture scripts.test_skill_ci_workflow -v`

Expected: all tests PASS.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`

Expected: `OK: validated skill architecture policy (repository-change-loop)`.

- [ ] **Step 5: Commit validator/CI enforcement**

```bash
git add scripts/validate_skill_architecture.py scripts/test_validate_skill_architecture.py .github/workflows/skill-architecture.yml scripts/test_skill_ci_workflow.py
git commit -m "test: enforce fail-closed SDD routing"
```

### Task 6: Run complete source verification without activation

**Files:** Test/review only; no planned content modification.

**Interfaces:** Consumes committed Tasks 1–5; produces source-complete evidence only. It does not produce active install、plugin/cache update、guard activation、operational safety。

- [ ] **Step 1: Run the three exact focused behavioral modules**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py -v`

Expected: PASS; direct entry/downstream/bootstrap cases verify callbacks and writes are absent.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py -v`

Expected: PASS; EACCES/sandbox cases verify exact original fingerprint and zero artifacts/commits.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v`

Expected: PASS; all Git/activation operations occur only under test-owned temporary directories.

- [ ] **Step 2: Run full SDD and repository script regressions**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -v`

Expected: all SDD tests PASS.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest scripts.test_validate_skill_architecture scripts.test_skill_ci_workflow scripts.test_skill_authoring_guidance -v`

Expected: all selected repository script tests PASS.

- [ ] **Step 3: Run required validators**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`

Expected: `OK: validated skill architecture policy (repository-change-loop)`.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

Expected: stdout matches `OK: validated [0-9]+ skill context contract\(s\)` and exit `0`; bind to exit/result semantics because the valid count may change independently.

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation`

Expected: `Skill is valid!`. If the runtime-discovered validator path has legitimately moved, resolve the current `skill-creator` validator through active skill discovery and run its equivalent; do not skip or substitute an unrelated validator.

- [ ] **Step 4: Verify scope/lifecycle separation and branch range**

Run: `git diff --name-only c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`

Expected: only Plan Gate files plus the exact repo-owned source/test/validator/CI files in this plan; no path under `/Users/omitsuhashi/.codex/plugins/cache`、`/Users/omitsuhashi/.agents`、live hooks directory。

Run: `git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`

Expected: no output, exit `0`.

- [ ] **Step 5: Read-only verify guard status; do not activate**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/scripts/activate_commit_guard.py preflight --repository /Users/omitsuhashi/repos/omitsuhashi/skills`

Expected: either read-only `ok` for an already verified activated guard or nonzero JSON `blocked` with exact missing/unconfigured/damaged/collision reason. Both outcomes must leave config/hooks unchanged. A blocked result is an operational activation blocker, not a source implementation failure; do not run `activate` in this plan.

### Task 7: Commit implementation closeout separately, then perform final review

**Files:** Modify `knowledge/log.md` only for closeout; no source/test changes unless the bounded review flow returns one material finding.

**Interfaces:** Consumes source-complete verification and original-checkout preservation evidence; produces one append-only implementation-closeout event and final `LOCAL_COMPLETE` source verdict. Operational activation remains pending separate Human authorization.

- [ ] **Step 1: Append one Japanese implementation-closeout event**

  Record accepted spec、canonical approved plan、source/test commit range、three focused module results、architecture/context/skill-creator/CI validation classes、original checkout comparison、external cache/installed tree unchanged、activation not performed、remote actions not performed。Do not add raw logs、agent IDs、runtime state、activation evidence not actually observed。

- [ ] **Step 2: Commit closeout before final whole-branch review**

```bash
git add knowledge/log.md
git commit -m "docs: close out fail-closed SDD source work"
```

- [ ] **Step 3: Re-run final committed verification**

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py -v`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_fail_closed_allocation_behavior.py -v`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/sdd-implementation/tests/test_commit_guard_behavior.py -v`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -v`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`

Run: `PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation`

Run: `git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`

Expected: every command exits `0`; final diff check has no output. Do not rerun current-clone activation.

- [ ] **Step 4: Run one canonical whole-branch review**

  Review `c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD` against the accepted spec and canonical plan exactly once. A material finding gets one scoped fixer, exactly one scoped re-review, and adjudication/stop; do not start a repeated whole-branch review wave. After any permitted fix, rerun the complete Step 3 bundle and commit the fix before its scoped re-review.

- [ ] **Step 5: Verify bootstrap expiry and original checkout preservation**

  Verify all Plan Gate、task、closeout commits are reachable from `codex/sdd-fail-closed-worktree-gate/planning`; verify the original checkout path、branch `main`、HEAD `c370fe14de1641aa5ee30b3fa001f4d857078091`、clean status match the trusted starting tuple. On mismatch return `BLOCKED` without repair. Mark the one-time bootstrap authority expired at implementation/integration closeout; future repository tasks require verified active guard. Report `LOCAL_COMPLETE` only for repo source and explicitly state activation、active install/plugin update、push/PR/merge/release remain unperformed.

## Later separately authorized activation boundary

本 plan は current clone activation を実行しない。source merge 後、Human が別 turn / operation で明示承認した場合だけ、approved commit を checkout した clone に対し次の順で進める: read-only `preflight` / complete collision report、explicit `activate --confirm-explicit-setup` transaction、primary normal + `--no-verify` reject、registered linked allow、damaged guard preflight BLOCKED、active installed SDD/source identity と external dependency semantics の read-only verification。collision または rollback-incomplete 時は Human resolution まで全 repository task を停止する。この段落は authorization ではなく future gate の定義である。

## Self-Review

- **Spec coverage:** acceptance matrix と Tasks 1–7 が SDD-first、pre-gate rejection、allocation/sandbox zero-write、prohibited command nonexecution、primary reject、linked allow、unknown BLOCKED、external conflict BLOCKED、complete config/hook inventory、collision pre-mutation BLOCKED、activation/rollback semantics、missing/damaged/unconfigured BLOCKED、bootstrap exact tuple/non-reuse、original preservation、source/install/cache/activation separationをすべて named testへ traceする。
- **Decision preservation:** approved exact bootstrap tuple、`prepare-commit-msg` hook point、config非変更の最小 activation model、no fallback、no automatic activation、external owner separationを変更していない。Open Decisionsを新設していない。
- **Placeholder scan:** placeholder directive や generic “add tests/error handling” はない。各 task に exact file、named tests、red signal、minimal green implementation、passing command、scoped commit がある。型注釈内の ellipsis は可変長 tuple 型を表す Python syntax であり、未定義実装ではない。
- **Type/interface consistency:** scenario dataclasses、inventory dataclasses、production signatures、CLI subcommands、stable status/reason valuesは Tasks 1–4 で同じ名前を使う。ordinary `preflight_repository` は active guardを要求し、internal activation candidateは target absentを要求するため semanticsを混同しない。
- **Command executability:** focused testsは repository rootから直接実行でき、full unittest discovery、architecture/context validators、skill-creator validator、CI contract、full-range `git diff --check` を含む。hyphenated directoryの dotted-import ambiguityには executable-path equivalentを明記した。
- **Write-set exactness:** Plan Gate sync、source/test/validator/CI tasks、implementation closeoutを別 commit/taskに分けた。canonical spec、external cache、installed tree、live hooks、remote stateは write set外。
- **No unauthorized activation:** production activation interfaceとtemp-repo testsは作るが、current cloneでは read-only `preflight` だけを実行し、`activate` は実行しない。later activation paragraphも separate Human authorizationを必須とする。

## Execution Handoff

Human / repository maintainer が本 draft を review して `promote` を明示した後、Task 0 の Plan Gate syncから開始する。実装は exact bootstrap tuple の planning worktree内で sequential SDDとして実行し、各 taskをfresh review gateへ渡す。current clone activation とremote publicationは別 authorizationである。
