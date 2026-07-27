# SDD Agent-Agnostic Runtime Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `sdd-implementation`とrepositoryのskill authoring contractからagent名によるdependency確認・実行分岐を削除し、active runtimeのcapabilityだけで同じflowを解決する。

**Architecture:** 標準`SKILL.md`を唯一のbehavior contractとし、dependency discoveryはactive runtimeで一度だけ行う。isolated dispatch、model selection、optional effort、wait / resumeはruntime identityではなくcapabilityとして解決する。plugin packaging adapterは今回のscope外とし、historical dual-host planは非実行の証跡として保持する。

**Tech Stack:** Markdown、Python 3 standard library、`unittest`、repository validators、Superpowers skill pressure scenarios。

## 実施状況

spec / plan baseline は `c1f3791` である。Task 1 は `33fe86b240efcd03e8e9c6020f6620e87747da2d`（`Make skill runtime contracts agent agnostic`）で完了し、独立 task review は 0 findings で **Approved** となった。Task 2 は `171d4f1`、fix は `0501c45` であり、scoped re-review は **Approved** となった。

final review は Critical 0 / Important 3 / Minor 0 を返した。bounded final fix `44edcf0` はresult collection、plan provenance、plugin validator guidanceの3件を解消し、final scoped re-review は全3件の解消、新規Critical / Important breakageなし、**APPROVED** を確認した。fresh pressure scenarioでは、synchronous dispatchがcompleted resultを返す場合はwait / resumeなしで継続し、asynchronous dispatchがwaitまたはresumeを欠く場合は`BLOCKED`、optional effortがない場合は`not_supported`として継続する。current planは `LOCAL_COMPLETE`、residual material riskはない。remote writeおよびlive mutationは実施していない。

## Global Constraints

- Skill behavior is defined only by inputs, applicable dependencies, and required capabilities.
- Dependency discovery runs once against the active runtime; it does not inspect another runtime in parallel.
- No active skill instruction selects behavior, fallback, or verification by agent name.
- Optional runtime metadata may not become a behavioral dependency.
- Plugin packaging contracts and historical non-executable plans are out of scope.
- No remote write, live install, release, push, PR creation, merge, issue, comment, or project mutation is authorized.

---

### Task 1: Portable skill runtime contract

**Files:**
- Modify: `AGENTS.md`
- Modify: `skills/AGENTS.md`
- Modify: `skills/sdd-implementation/SKILL.md`
- Modify: `skills/sdd-implementation/tests/test_skill_contract.py`
- Modify: `skills/decide-in-order/tests/test_skill_contract.py`
- Rename: `scripts/test_dual_host_authoring_guidance.py` to `scripts/test_skill_authoring_guidance.py`
- Rename: `scripts/test_dual_host_ci_workflow.py` to `scripts/test_skill_ci_workflow.py`
- Rename: `scripts/validate_dual_host_compatibility.py` to `scripts/validate_repository_compatibility.py`
- Rename: `scripts/test_validate_dual_host_compatibility.py` to `scripts/test_validate_repository_compatibility.py`
- Modify: `.github/workflows/skill-architecture.yml`

**Interfaces:**
- Consumes: Human-approved agent-agnostic revision in `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`.
- Produces: one portable `SKILL.md` contract; active-runtime dependency preflight; capability-based dispatch/model/effort/wait/resume boundary; repository validation entrypoints without dual-host skill semantics.

- [ ] **Step 1: Run the baseline pressure scenario**

Give a fresh worker the current `skills/sdd-implementation/SKILL.md` and this scenario: “Execute an approved plan in an unnamed runtime whose skill discovery, isolated dispatch, explicit model selection, and wait/resume capabilities are available. State the dependency preflight and dispatch mapping.” Record whether it unnecessarily requires named runtimes or parallel per-runtime checks.

- [ ] **Step 2: Write the failing contract tests**

Change `skills/sdd-implementation/tests/test_skill_contract.py` so the required dependency text is:

```text
Before entering a selected route, use the active runtime's skill discovery to verify applicable dependencies and required capabilities.
```

Require the skill to contain a `Runtime Capability Boundary`, require isolated dispatch/model/optional effort/wait/resume capability mapping, and reject named-agent instructions. Update authoring guidance tests to require standard `SKILL.md`, portable inputs/outputs/capabilities, active-runtime discovery, and optional metadata isolation. Rename the scripts and update imports/workflow references.

- [ ] **Step 3: Run tests to verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_authoring_guidance.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_ci_workflow.py
```

Expected: at least one assertion fails because current production guidance still requires named runtimes or the renamed entrypoints are not yet wired.

- [ ] **Step 4: Implement the minimal portable contract**

In `skills/sdd-implementation/SKILL.md`:

- replace the two-runtime dependency preflight with one active-runtime discovery check;
- replace named dispatch examples with the runtime’s isolated fresh-context mechanism;
- replace `Host Boundary` with `Runtime Capability Boundary`;
- map isolated dispatch, explicit model, optional effort, wait, and resume by capability only;
- keep `BLOCKED` behavior for missing required capabilities and `not_supported` for optional effort.

In `AGENTS.md` and `skills/AGENTS.md`, define skill portability through the shared `SKILL.md`, inputs, outputs, and capabilities. Keep plugin packaging routed separately to `plugins/AGENTS.md`. Rename the repository validation scripts and CI labels so active skill validation is not described as dual-host verification. Preserve the plugin-package checks inside the repository validator.

- [ ] **Step 5: Run focused GREEN verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_authoring_guidance.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_ci_workflow.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_validate_repository_compatibility.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_repository_compatibility.py --skill skills/sdd-implementation
```

Expected: all commands exit 0.

- [ ] **Step 6: Run the post-change pressure scenario**

Repeat Step 1 with a fresh worker and the revised skill. Expected: the worker checks active-runtime discovery once, maps only the stated capabilities, and does not add named-runtime checks or behavior branches.

- [ ] **Step 7: Commit Task 1**

```bash
git add AGENTS.md skills/AGENTS.md skills/sdd-implementation skills/decide-in-order/tests/test_skill_contract.py scripts .github/workflows/skill-architecture.yml
git commit -m "Make skill runtime contracts agent agnostic"
```

### Task 2: Durable knowledge closeout

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Modify: `knowledge/wiki/syntheses/sdd-agent-agnostic-runtime-implementation-plan.md`
- Modify: `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**
- Consumes: Task 1 commit, task review verdict, pressure-scenario evidence, and fresh verification output.
- Produces: current agent-agnostic SDD design, superseded historical dual-host skill guidance, discoverable implementation plan, and append-only closeout evidence.

- [ ] **Step 1: Update current and historical boundaries**

Record Task 1 implementation and review evidence in the current SDD design. Mark the old dual-host authoring design as historical for skill behavior while preserving any still-current plugin packaging evidence. Do not rewrite the historical implementation plan.

- [ ] **Step 2: Synchronize discovery and audit surfaces**

Update the existing SDD design catalog entry to use `agent-agnostic`, `active runtime`, `capability boundary`, and `portable skill` search terms. Add this plan once to the Active Page Catalog. Append an `implementation-closeout-candidate` entry to `knowledge/log.md` with exact verification evidence and unperformed remote actions.

- [ ] **Step 3: Run full local verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_repository_compatibility.py --skill skills/sdd-implementation
git diff --check
```

Expected: all commands exit 0. The repository-wide compatibility command is not required because the pre-existing case-insensitive `skills/llm-wiki/DESCRIPTION.md` collision is outside this change.

- [ ] **Step 4: Commit Task 2**

```bash
git add knowledge/wiki/syntheses/sdd-implementation-skill-design.md knowledge/wiki/syntheses/sdd-agent-agnostic-runtime-implementation-plan.md knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md knowledge/index.md knowledge/log.md
git commit -m "Document agent-agnostic skill runtime contract"
```

## 関連ページ

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — Human-approved agent-agnostic revisionとcurrent lifecycle contract。
- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md) — skill behaviorについては本計画でhistoricalへ移す旧契約。plugin packaging evidenceは別境界として残す。

## 出典

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md)
- repository instruction: `AGENTS.md`
- skill authoring instruction: `skills/AGENTS.md`
