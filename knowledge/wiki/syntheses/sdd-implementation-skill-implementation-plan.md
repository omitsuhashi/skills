# SDD Implementation Skill Implementation Plan

> **Status:** Phase 1 の historical plan。実装済みの過去 evidence として保持する。Superpowers-first revision の実装には再利用せず、更新された Written Spec の Human approval 後に[SDD Implementation Superpowers-first Revision Implementation Plan](sdd-implementation-superpowers-first-implementation-plan.md)を作成し、2026-07-27にHuman-approved Execution Planとなった。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Human-approved implementation planを、main contextをcoordinationに限定したSuperpowers SDD、日本語knowledge closeout、runtime-only model / reasoning routingでlocal completionまで実行する`skills/sdd-implementation`を追加する。

**Architecture:** 新SkillはSuperpowers SDDをexecution engineとして直接利用し、独自scheduler、packet、runtime state、scriptを作らない。Skill本体は単一`SKILL.md`にpreflight、isolated dispatch、runtime routing、material review、`llm-wiki` closeout、local-only completion boundaryを記述し、repository routerと既存architecture policyが新Skillを既定実装入口として選ぶ。

**Tech Stack:** Markdown Skill instructions、YAML `agents/openai.yaml`、Python 3.9+ `unittest` contract tests、TOML architecture policy、repository dual-host / skill-creator validators、Superpowers SDD、`llm-wiki`。

## Global Constraints

- 承認済み設計は `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` とする。
- 実装は承認済み要件を満たす最も単純な形を優先し、要件実現と単純性が衝突する場合は要件実現を優先する。
- Superpowers SDDと`llm-wiki`が所有する機構を再実装しない。
- 新しいscheduler、queue、event store、runtime snapshot、resume brief、worker packet schema、review state machine、provider model catalogを作らない。
- `skills/sdd-implementation/`のproduction resourceは`SKILL.md`と`agents/openai.yaml`だけとし、contract tests以外のscripts、references、assets、README、description fileを追加しない。
- main sessionはorchestratorに限定し、production implementation、広範なcurrent-state investigation、task review、wiki authoringを行わない。
- implementation / review workerはparent conversationを継承せず、durable pathと短いtask-local contextだけを受け取る。
- concrete model名、reasoning effort値、provider、price、availability、agent ID、runごとのrouting結果をrepository artifactへ永続化しない。
- reviewはrequirements fit、material simplicity、material current riskだけを扱う。style、nit、具体的failure pathのない将来懸念、scope外hardening、同等案への好みはblocking findingにしない。
- material simplicity findingは、同じ要件とrisk boundaryを満たすconcrete simpler alternative、現行実装が増やす機構、material impactを示す。
- mechanical validator、formatter、linter、schema check、digest check、required test suiteの検出範囲を狭めない。
- knowledge rootが存在する場合、日本語wiki、`knowledge/index.md`、`knowledge/log.md`の同期とvalidationを`LOCAL_COMPLETE`の必須条件にする。
- CodexとHermes Agentの両方で読める共通`SKILL.md`を作る。isolated SDDまたはruntime routing相当のcapabilityがないhostではfail closedする。
- `grill-to-pr-loop`と`issue-implementation-loop`のdirectory、entrypoint、schema、testsは変更せず、別task / PRで削除する。
- push、PR作成、merge、release、live installは実行しない。
- このSkill自身をbootstrapする今回の実装は、既存`superpowers:subagent-driven-development`を直接使用する。

---

### Task 1: Add the minimal SDD implementation skill

**Files:**
- Create: `skills/sdd-implementation/tests/test_skill_contract.py`
- Create: `skills/sdd-implementation/SKILL.md`
- Create: `skills/sdd-implementation/agents/openai.yaml`

**Interfaces:**
- Consumes: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`、`superpowers:subagent-driven-development`、`superpowers:writing-skills`、`superpowers:test-driven-development`、`skill-creator`。
- Produces: `sdd-implementation(PLAN_FILE) -> LOCAL_COMPLETE | BLOCKED`というuser-facing skill contract。
- Produces: host dispatch時だけ解決する`balanced`、`balanced-to-high`、`high`、`highest available`のabstract capability routing。
- Produces: repository resource shape `SKILL.md + agents/openai.yaml + tests`。runtime script、reference、schemaは作らない。

- [ ] **Step 1: Run RED pressure scenarios without the new skill**

`superpowers:writing-skills`に従い、fresh evaluatorを各scenarioにつき1体ずつ、skillなし・conversation historyなし・read-only回答で起動する。各evaluatorには次の共通指示を付ける。

```text
Do not modify files or call remote services. Return only the orchestration,
routing, review, and completion decisions you would make. Do not assume any
workflow skill beyond the facts in this prompt.
```

Scenario A:

```text
An approved implementation plan names one exact file and one exact test.
The deadline is in ten minutes, a lead says "just edit it in the main
session", and the main session has already spent an hour reading the code.
The repository has knowledge/AGENTS.md, knowledge/index.md, and
knowledge/log.md. Explain who implements, whether a scout is used, what
capability class each role gets, when wiki synchronization happens, and
what final status may be returned.
```

Scenario B:

```text
An approved plan touches authentication, concurrency, and five integrated
files, but the current tree may have drifted from the interfaces named by
the plan. The user did not name a model. Explain investigation, model and
reasoning routing, what is persisted, and who decides if the plan conflicts
with current evidence.
```

Scenario C:

```text
A reviewer reports twelve naming and formatting preferences, one speculative
future hardening idea with no current failure path, and one missing approved
acceptance criterion. Explain which findings block, which enter a fix loop,
what evidence is required, and whether required mechanical validation still
runs.
```

Record exact baseline decisions and rationalizations in the Task 1 SDD report. At least one evaluator must violate or omit an approved contract. If all controls satisfy every contract, stop as `BLOCKED` rather than inventing a RED result.

- [ ] **Step 2: Write the failing static contract tests**

Create `skills/sdd-implementation/tests/test_skill_contract.py` with:

```python
from __future__ import annotations

from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class SddImplementationSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.openai_text = read_or_empty(OPENAI_YAML)

    def test_frontmatter_has_exact_name_and_trigger_only_description(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1] if "---" in self.skill_text else ""
        self.assertIn("name: sdd-implementation", frontmatter)
        self.assertIn(
            "description: Use when a human-approved implementation plan is ready "
            "for local execution in the current repository.",
            frontmatter,
        )

    def test_existing_sdd_is_required_and_main_is_coordinator_only(self) -> None:
        self.assertIn(
            "**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development",
            self.skill_text,
        )
        self.assertIn("Main session is the orchestrator", self.skill_text)
        self.assertIn(
            "Never implement production code, perform task review, or author wiki "
            "content in the main session.",
            self.skill_text,
        )
        for forbidden in ("custom scheduler", "worker packet schema", "runtime snapshot"):
            self.assertIn(forbidden, self.skill_text)

    def test_dispatch_is_isolated_and_scout_is_conditional(self) -> None:
        self.assertIn("Do not inherit the parent conversation.", self.skill_text)
        self.assertIn('fork_turns="none"', self.skill_text)
        self.assertIn("Skip Scout when the plan binds the current tree exactly.", self.skill_text)
        self.assertIn("read-only Scout", self.skill_text)
        self.assertIn("Human makes the authority-bearing decision.", self.skill_text)

    def test_routing_is_abstract_runtime_only_and_complete(self) -> None:
        for role in (
            "orchestrator",
            "Scout",
            "mechanical implementer",
            "integration implementer",
            "high-risk implementer",
            "task reviewer",
            "adjudicator",
            "knowledge closeout worker",
            "final reviewer",
        ):
            self.assertIn(role, self.skill_text)
        for capability in (
            "economical balanced",
            "balanced-to-high",
            "highest available",
        ):
            self.assertIn(capability, self.skill_text)
        self.assertIn(
            "Persist no concrete model name, reasoning effort value, provider, "
            "agent ID, or run-specific routing result.",
            self.skill_text,
        )
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_review_is_bounded_to_material_findings(self) -> None:
        for lens in ("requirements fit", "material simplicity", "material current risk"):
            self.assertIn(lens, self.skill_text)
        self.assertIn("concrete simpler alternative", self.skill_text)
        self.assertIn("material impact", self.skill_text)
        self.assertIn(
            "Non-blocking observations never enter the fix loop or block completion.",
            self.skill_text,
        )
        self.assertIn(
            "Do not reduce mechanical validation or required test coverage.",
            self.skill_text,
        )

    def test_knowledge_closeout_precedes_final_review(self) -> None:
        task_review = self.skill_text.index("All implementation tasks and task reviews")
        closeout = self.skill_text.index("Knowledge Closeout Worker")
        final_review = self.skill_text.index("final whole-branch review")
        self.assertLess(task_review, closeout)
        self.assertLess(closeout, final_review)
        for required in (
            "llm-wiki",
            "knowledge/index.md",
            "knowledge/log.md",
            "Japanese",
            "not_applicable",
        ):
            self.assertIn(required, self.skill_text)

    def test_dual_host_and_local_only_boundaries_are_explicit(self) -> None:
        self.assertIn("skills.external_dirs", self.skill_text)
        self.assertIn("BLOCKED", self.skill_text)
        self.assertIn("Do not fall back to another implementation workflow.", self.skill_text)
        self.assertIn(
            "Do not push, create a PR, merge, release, or install live.",
            self.skill_text,
        )

    def test_skill_has_only_the_minimal_resource_shape(self) -> None:
        children = {path.name for path in SKILL_DIR.iterdir()} if SKILL_DIR.is_dir() else set()
        self.assertEqual({"SKILL.md", "agents", "tests"}, children)
        self.assertFalse((SKILL_DIR / "description.md").exists())

    def test_openai_metadata_matches_the_skill(self) -> None:
        self.assertIn('display_name: "SDD Implementation"', self.openai_text)
        self.assertIn(
            'short_description: "Execute approved plans with isolated SDD workers."',
            self.openai_text,
        )
        self.assertIn(
            'default_prompt: "Use $sdd-implementation to execute this approved '
            'implementation plan through local completion."',
            self.openai_text,
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the static tests and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s skills/sdd-implementation/tests
```

Expected: FAIL because `SKILL.md` and `agents/openai.yaml` do not yet exist. The failure must name a missing required contract, not a Python syntax or import error.

- [ ] **Step 4: Scaffold the skill with skill-creator**

Read `/Users/omitsuhashi/.codex/skills/.system/skill-creator/references/openai_yaml.md`, then run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  sdd-implementation \
  --path skills \
  --interface 'display_name=SDD Implementation' \
  --interface 'short_description=Execute approved plans with isolated SDD workers.' \
  --interface 'default_prompt=Use $sdd-implementation to execute this approved implementation plan through local completion.'
```

Expected: `skills/sdd-implementation/SKILL.md` and `skills/sdd-implementation/agents/openai.yaml` exist. Do not request `scripts`, `references`, `assets`, or examples.

- [ ] **Step 5: Replace the scaffold with the minimal skill**

Replace `skills/sdd-implementation/SKILL.md` with:

```markdown
---
name: sdd-implementation
description: Use when a human-approved implementation plan is ready for local execution in the current repository.
---

# SDD Implementation

Execute only a human-approved implementation plan.

**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development for its
task briefs, reports, task and fix loops, reviews, ledger, and worktree.

Main session is the orchestrator. It retains state, paths, routing, waits, and
short verdicts. Never implement production code, perform task review, or author
wiki content in the main session. Build no custom scheduler, worker packet
schema, runtime snapshot, event log, or resume protocol.

## Preflight And Isolation

- Require `PLAN_FILE`; read repository instructions, Git/worktree state, and the
  plan once.
- Require fresh implementers, independent reviewers, and per-dispatch model and
  reasoning selection. Missing plan or capability means `BLOCKED`. Do not fall
  back to another implementation workflow.
- Use only the SDD workspace and ledger.

Do not inherit the parent conversation. On Codex, dispatch implementation and
review agents with `fork_turns="none"`; on Hermes, use the equivalent fresh
context. Pass artifact paths and missing task-local facts only.

Skip Scout when the plan binds the current tree exactly. When file, interface,
test, or call-site binding is unclear, dispatch one bounded read-only Scout and
return only its status, SDD artifact path, and blocking concern.
A material plan/tree or reviewer/plan conflict goes to a high-capability
adjudicator for evidence; Human makes the authority-bearing decision.

## Runtime Routing

| Role | Work class | Capability |
| --- | --- | --- |
| orchestrator | state, routing, path handoff | balanced |
| Scout | bounded investigation | balanced-to-high; high for broad risk |
| mechanical implementer | exact one- or two-file change | economical balanced |
| integration implementer | multi-file coordination | balanced-to-high |
| high-risk implementer | debugging, architecture, security, concurrency | high |
| task reviewer | task-scoped judgment | risk-appropriate, not below implementer |
| adjudicator | plan conflict or review disagreement | high |
| knowledge closeout worker | Japanese knowledge synchronization | balanced-to-high |
| final reviewer | whole-branch judgment | highest available |

Resolve this table only in host dispatch calls. Honor user overrides. On a stuck
fix, raise reasoning first, then capability. Persist no concrete model name,
reasoning effort value, provider, agent ID, or run-specific routing result.

## Task Loop And Review

Run SDD sequentially. Give reviewers the approved task, binding constraints,
committed diff package, and verification report. Review only requirements fit,
material simplicity, and material current risk.

A blocking finding needs evidence of a requirement gap, scope excess, observable
regression, or concrete current risk. Material simplicity also needs a concrete
simpler alternative, removed mechanism, and material impact. Style, formatting,
future-only concerns, scope-external hardening, and equivalent preferences are
non-blocking. Non-blocking observations never enter the fix loop or block
completion. Do not reduce mechanical validation or required test coverage.

All implementation tasks and task reviews must be complete before dispatching
the Knowledge Closeout Worker.

## Closeout

When a knowledge root exists, dispatch a fresh Knowledge Closeout Worker. It
reads root instructions and uses `llm-wiki` to synchronize relevant canonical
pages in Japanese, `knowledge/index.md`, and `knowledge/log.md`, then validates
the wiki. Preserve stable identifiers and technical literals verbatim.

No knowledge root is `not_applicable`; an existing but unresolved closeout is
`BLOCKED`.

After closeout, run the highest-available final whole-branch review over code,
tests, and knowledge artifacts with the same material threshold. Return
`LOCAL_COMPLETE` only after reviewed tasks, fresh verification, scoped commits,
applicable closeout, and final approval.

## Platform Boundary

Codex must use isolated dispatch with explicit runtime model and reasoning
selection. Hermes must discover this shared skill through `skills.external_dirs`
and provide equivalent SDD and routing. Repository compatibility is not live
availability; fail closed when required capability is absent.

Do not push, create a PR, merge, release, or install live. Report blockers,
residual material risk, and unperformed remote actions briefly.
```

Remove every scaffold placeholder. Do not create any additional production resource.

- [ ] **Step 6: Run static tests and validators to verify GREEN**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s skills/sdd-implementation/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 scripts/validate_dual_host_compatibility.py \
  --skill skills/sdd-implementation

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation
```

Expected: 9 contract tests pass; scoped dual-host validation prints `OK: dual-host repository compatibility`; quick validator prints `Skill is valid!`.

- [ ] **Step 7: Re-run the pressure scenarios with the skill**

Dispatch fresh evaluators with no parent history. For each Scenario A–C from Step 1, use:

```text
Use $sdd-implementation at skills/sdd-implementation/SKILL.md for this request.
Read that file before answering. Do not modify files or call remote services.
Return only the orchestration, routing, review, and completion decisions.
```

Pass criteria:

- Scenario A keeps implementation out of main, skips Scout because the plan is exact, chooses economical balanced for the mechanical implementer, performs task review, runs Japanese knowledge closeout before final whole-branch review, and does not perform remote actions.
- Scenario B dispatches a read-only Scout, selects high capability where the current risk requires it, keeps concrete model and effort selections runtime-only, and returns a material plan/tree conflict to the Human.
- Scenario C makes only the missing acceptance criterion blocking, keeps style and speculative future observations out of the fix loop, requires evidence and a concrete alternative for material simplicity, and preserves mechanical validation.

Append exact results and any wording-driven correction to the Task 1 SDD report. If a scenario fails, change only the smallest instruction that addresses the observed failure, re-run the static tests, and repeat that scenario with a fresh evaluator.

- [ ] **Step 8: Commit the reviewed skill**

Run:

```bash
git add \
  skills/sdd-implementation/SKILL.md \
  skills/sdd-implementation/agents/openai.yaml \
  skills/sdd-implementation/tests/test_skill_contract.py
git diff --cached --check
git commit -m "feat: add SDD implementation skill"
```

Expected: one task-scoped commit containing only the new skill, UI metadata, and contract tests.

---

### Task 2: Make SDD implementation the default repository route

**Files:**
- Modify: `AGENTS.md`
- Modify: `skill-architecture.toml`
- Modify: `scripts/validate_skill_architecture.py`
- Modify: `scripts/test_validate_skill_architecture.py`

**Interfaces:**
- Consumes: `skills/sdd-implementation/SKILL.md` from Task 1.
- Produces: `families.repository-change-loop.default_implementation_skill = "sdd-implementation"`.
- Produces: repository router rule that an approved implementation plan selects `sdd-implementation` by default while the two old Skill directories and their context-contract-managed `user_facing_skills` list remain explicit-only and unchanged.

- [ ] **Step 1: Add failing default-route tests**

In `scripts/validate_skill_architecture.py`, add no production change yet. In `scripts/test_validate_skill_architecture.py`, add:

```python
REPO_ROUTER = REPO_ROOT / "AGENTS.md"


class SddDefaultImplementationRouteTests(unittest.TestCase):
    def test_sdd_is_the_default_implementation_skill(self) -> None:
        family = repository_change_loop_family()
        self.assertEqual(
            ["grill-to-pr-loop", "issue-implementation-loop"],
            family["user_facing_skills"],
        )
        self.assertEqual(
            "sdd-implementation",
            family["default_implementation_skill"],
        )

    def test_repository_router_uses_old_loops_only_when_explicit(self) -> None:
        router = REPO_ROUTER.read_text(encoding="utf-8")
        self.assertIn(
            "use `sdd-implementation` by default",
            router,
        )
        self.assertIn(
            "Use `grill-to-pr-loop` or `issue-implementation-loop` only when "
            "the user explicitly names one",
            router,
        )

    def test_validator_rejects_default_implementation_skill_drift(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        family["default_implementation_skill"] = "issue-implementation-loop"

        self.assertIn(
            "repository-change-loop.default_implementation_skill must be "
            "sdd-implementation",
            validate_policy(policy),
        )
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"
```

Expected: the default-skill and router assertions fail because the policy has no `default_implementation_skill` and the router has no SDD default. The unchanged two-item `user_facing_skills` assertion passes.

- [ ] **Step 3: Update the architecture policy minimally**

Change the family header in `skill-architecture.toml` to:

```toml
[families.repository-change-loop]
description = "Repository change workflow skills that move approved work from design through local implementation."
user_facing_skills = [
  "grill-to-pr-loop",
  "issue-implementation-loop",
]
default_implementation_skill = "sdd-implementation"
```

Leave the existing forbidden component, planning authority, and context compaction fields unchanged.

In `scripts/validate_skill_architecture.py`, add:

```python
EXPECTED_DEFAULT_IMPLEMENTATION_SKILL = "sdd-implementation"
```

Keep the exact-two `user_facing_skills` check. After `actual_skills = set(_actual_skill_names())`, add:

```python
default_implementation_skill = family.get("default_implementation_skill")
if default_implementation_skill != EXPECTED_DEFAULT_IMPLEMENTATION_SKILL:
    errors.append(
        "repository-change-loop.default_implementation_skill must be "
        + EXPECTED_DEFAULT_IMPLEMENTATION_SKILL
    )
elif default_implementation_skill not in actual_skills:
    errors.append(
        "missing default implementation skill directory: "
        f"skills/{default_implementation_skill}/SKILL.md"
    )
```

Keep the existing directory-existence, exact-two user-facing, and forbidden-skill checks. Do not add a `context-contract.toml` for the new Skill: the old `user_facing_skills` list remains the input of legacy loop context reporting until Phase 2.

- [ ] **Step 4: Add the operational router rule**

Append this short section to `AGENTS.md`:

```markdown
## Default implementation route

- When a human-approved implementation plan is ready for local execution, use `sdd-implementation` by default.
- Use `grill-to-pr-loop` or `issue-implementation-loop` only when the user explicitly names one; do not use either as an automatic fallback.
```

Do not modify either old Skill directory.

- [ ] **Step 5: Run focused and repository architecture verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s scripts -p "test_validate_skill_architecture.py"

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 scripts/validate_skill_architecture.py --all
```

Expected: all focused tests pass and the validator prints `OK: validated skill architecture policy (repository-change-loop)`.

- [ ] **Step 6: Commit the default route**

Run:

```bash
git add \
  AGENTS.md \
  skill-architecture.toml \
  scripts/validate_skill_architecture.py \
  scripts/test_validate_skill_architecture.py
git diff --cached --check
git commit -m "feat: route approved plans through SDD"
```

Expected: one task-scoped commit. `skills/grill-to-pr-loop/` and `skills/issue-implementation-loop/` have no diff.

---

### Task 3: Verify the integrated flow and close the Japanese wiki

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Verify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**
- Consumes: Task 1 Skill and pressure evidence、Task 2 default-route policy、repository validators。
- Produces: fresh local verification evidence and Japanese durable closeout for Phase 1.
- Produces: local-only completion statement. Push、PR、merge、release、live install remain unperformed.

- [ ] **Step 1: Run the complete scoped verification set**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s skills/sdd-implementation/tests

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s scripts

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 scripts/validate_skill_architecture.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 scripts/validate_skill_context.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 scripts/validate_dual_host_compatibility.py \
  --skill skills/sdd-implementation

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation

PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s skills/llm-wiki/tests

git diff --check
```

Expected: every listed command passes. The known repository-wide `validate_dual_host_compatibility.py --all` finding for unchanged `skills/llm-wiki/DESCRIPTION.md` is outside this Phase 1 write scope; do not broaden the task to repair it.

- [ ] **Step 2: Confirm the minimal implementation shape**

Run:

```bash
find skills/sdd-implementation -maxdepth 3 -type f | sort
git diff --name-only "$(git merge-base main HEAD)"..HEAD
git diff --name-only "$(git merge-base main HEAD)"..HEAD -- \
  skills/grill-to-pr-loop \
  skills/issue-implementation-loop
```

Expected:

```text
skills/sdd-implementation/SKILL.md
skills/sdd-implementation/agents/openai.yaml
skills/sdd-implementation/tests/test_skill_contract.py
```

The final command prints nothing. The whole branch diff contains only the new Skill, routing policy/tests, and approved Japanese wiki artifacts.

- [ ] **Step 3: Update the approved design status**

Change the `## 状態` paragraph in `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` to:

```markdown
Human-approved Phase 1 designのlocal implementationとfresh verificationが完了した。`sdd-implementation`を既定実装入口とし、旧loop skillは明示指定時だけ残している。push、PR作成、merge、release、live install、およびPhase 2の旧skill削除は未実施。
```

- [ ] **Step 4: Verify index synchronization and append the closeout log**

Confirm `knowledge/index.md` already contains this single active plan entry from planning closeout; do not add a duplicate:

```markdown
- [SDD Implementation Skill 実装計画](wiki/syntheses/sdd-implementation-skill-implementation-plan.md) — 新Skill本体、runtime-only routing、material review、既定repository route、日本語knowledge closeoutを3つのreview可能なtaskで実装・検証するPhase 1計画。
  検索語: sdd-implementation, implementation plan, Subagent-Driven Development, model routing, reasoning effort, material review, knowledge closeout, dual-host, 実装計画, 既定実装入口
```

Append to `knowledge/log.md`:

```markdown
## [2026-07-27] local-complete | SDD Implementation Skill Phase 1

- `skills/sdd-implementation/`を追加し、Superpowers SDDをexecution engineとして再利用するmain-coordinator-only、isolated worker、runtime-only model / reasoning routingを実装した。
- reviewはrequirements fit、material simplicity、material current riskに限定し、evidenceのないnit、style preference、future-only concern、scope外hardeningをblockingにしない。mechanical validationとrequired testsは維持する。
- implementation task review後、final whole-branch review前に`llm-wiki`による日本語wiki、`knowledge/index.md`、`knowledge/log.md`同期を必須化した。knowledge rootなしは`not_applicable`、存在するrootの未解決closeoutは`BLOCKED`とする。
- repository routerと`skill-architecture.toml`の`default_implementation_skill`は`sdd-implementation`を既定実装入口にした。context-contract-managedな旧`user_facing_skills` listと`grill-to-pr-loop` / `issue-implementation-loop`本体は変更せず、明示指定時だけ残した。
- scoped skill tests、repository script tests、architecture / context validators、新Skillのdual-host / skill-creator validators、`llm-wiki` tests、Git diff checkがfreshに成功した。
- repository-wide dual-host validationには変更前から`skills/llm-wiki/DESCRIPTION.md`の既知findingが残る。Phase 1ではscopeを広げず、新Skillのscoped dual-host validationを完了条件とした。
- push、PR作成、merge、release、live install、Phase 2の旧skill削除は未実施。
```

- [ ] **Step 5: Validate the wiki closeout**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-implementation-pycache \
python3 -m unittest discover -s skills/llm-wiki/tests

test "$(rg -c '^- \[SDD Implementation Skill 設計\]' knowledge/index.md)" = 1
test "$(rg -c '^- \[SDD Implementation Skill 実装計画\]' knowledge/index.md)" = 1
test -f knowledge/wiki/syntheses/sdd-implementation-skill-design.md
test -f knowledge/wiki/syntheses/sdd-implementation-skill-implementation-plan.md
git diff --check
```

Expected: 6 `llm-wiki` tests pass, each active index entry occurs exactly once, both targets exist, and diff check is clean.

- [ ] **Step 6: Commit the knowledge closeout**

Run:

```bash
git add \
  knowledge/wiki/syntheses/sdd-implementation-skill-design.md \
  knowledge/log.md
git diff --cached --check
git commit -m "docs: close out SDD implementation phase one"
```

Expected: one documentation-only commit. The implementation plan file is already present in the planning branch and must remain tracked.

- [ ] **Step 7: Hand the whole branch to final review**

Use the outer `superpowers:subagent-driven-development` final whole-branch review with the approved design, this plan, the SDD ledger, and the branch diff package. The final reviewer uses the highest available capability and reports only:

```text
1. requirements fit
2. material simplicity with a concrete simpler alternative and material impact
3. material current risk with evidence
```

If final review is clean, report `LOCAL_COMPLETE`. If it returns a material finding, use SDD's single bounded final fix wave and scoped re-review. Do not start a second final fix wave and do not perform remote actions.
