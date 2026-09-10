---
summary: Planning Controller、Research / Spec / Plan worker の分離を当時の baseline に実装する計画を確認できる。
knowledge_status: historical
---
# SDD Pre-Implementation Context Isolation Implementation Plan

## 適用範囲と履歴

当時の SDD 設計・実装証跡であり、本文の current / active / 実行可能は当時の範囲を指す。SDD 既定ルートは [PR #58](https://github.com/omitsuhashi/skills/pull/58)、KIS / decide-in-order 本体は commit `99fdaf2` で削除されている。現行の作業ツリー保全規約は repository root の `AGENTS.md` を参照する。部分的な仕様置換と当時の承認・未承認の区別は本文に保持する。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## 状態

2026-07-29にHumanが本計画をrepository-required Plan Gateとして承認した。これは
currentな実行計画であり、承認済みWritten Spec
`knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md`と、baseline
commit `66d93ae4a233fc8f9750b6bc6d824cc54bb0838d`（`66d93ae`）にbindingされる。
implementation、remote writeは未実施である。

**Goal:** `sdd-implementation`を唯一のuser-facing repository-change skillとして維持しながら、実装前のrepository調査、Spec Synthesis / Review、Plan Authoringをisolated fresh-context workerへ移し、main sessionをPlanning Controllerへ限定する。

**Architecture:** portableな`SKILL.md`にはinput maturity routing、Planning Controller invariant、lazy-loaded stage reference、fresh worker dispatch requirementだけを置く。詳細なread boundary、Decision Record、Control Return、Stage Capsuleは2つのinternal referenceへ分け、Research / Spec Synthesis / Spec Reviewは3つのinternal promptで実行する。Plan Authorは新しいpromptやskillを作らず、`planning-context.md`からfresh workerへcurrent Superpowers `writing-plans`をrouteする。

**Tech Stack:** Markdown Skill instructions、Python 3.9+ standard-library `unittest` contract tests、TOML architecture policy、Superpowers v6.2.0、`grill-with-docs`、`llm-wiki`。

## Global Constraints

- 承認済みWritten Specは`knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md`であり、実装とreviewのbinding sourceとする。
- current branch baselineはcommit `66d93ae4a233fc8f9750b6bc6d824cc54bb0838d`（short SHA `66d93ae`）であり、全diff、review、verificationをこのcommitへbindingする。
- `sdd-implementation`を唯一のuser-facing repository-change skillおよびdefault implementation routeとして維持する。
- `skills/sdd-implementation/`内のreferenceとpromptをinternal seamとして追加し、新しいuser-facing skillは作らない。
- Planning ControllerはHuman対話、current decision、Decision Recordの小さな更新、approval、stage routing、Control Return評価だけを所有する。
- Planning Controllerはsource code、broad wiki / docs、full spec / plan、git diff、test / command output、複数file探索結果を直接読まない。
- Research、Spec Synthesis、Spec Review、Plan Authorはparent conversationを継承しないisolated fresh-context workerとする。
- Humanがmaterial decision、risk acceptance、Written Spec approval、repository-required Plan approvalの最終authorityを持つ。supporting workerは`advisory_only`のままとする。
- Decision Recordはplanning worktree上のspec draft内にある`Confirmed Decisions`と`Open Decisions`だけとし、別ledger、`CONTEXT.md`、repo-root `docs/adr/`を作らない。
- worker detailはartifactへ書き、直接returnするControl Returnは`status`、`artifact_path`、`decision_requests`、`material_risks`に限定する。
- Control Returnの約200 wordsとStage Capsuleの約400 wordsは運用目安であり、word-count schema、validator、script、超過時のstate machineを作らない。
- Research Reportはplanning worktree内のgitignoredな`.superpowers/research/<epic-id>/`へ置き、wiki、Git、canonical specへ登録しない。
- physical context compaction、manual compaction、session-pressure telemetry、numerical triggerをrequired機能にしない。
- custom scheduler、retry / fallback matrix、runtime state、context contract、Execution Envelope、packet schema、event log、resume protocolを作らない。
- required fresh worker capabilityがない場合は既存dependency / capability boundaryで`BLOCKED`とし、main-session explorationへfallbackしない。
- current Superpowers lifecycle、`grill-with-docs`の一問一答、`llm-wiki`の3 durable checkpoints、knowledge closeout、final whole-branch reviewを維持する。
- concrete model、effort、provider、availability、agent ID、run-specific routingをspec、plan、wiki、ledger、schemaへ保存しない。
- `skill-architecture.toml`の`user_facing_skills = ["sdd-implementation"]`、`default_implementation_skill = "sdd-implementation"`、`decision_authority = "human"`を変更しない。
- `knowledge/index.md`と`knowledge/log.md`はPlan Author作業では変更せず、approved planを実行する際のknowledge closeout taskで同期する。
- push、PR、merge、release、live install、issue、comment、project変更を実行しない。remote writeには別の明示承認が必要である。

## File Map

- `skills/sdd-implementation/SKILL.md`: input maturity routing、Planning Controller invariant、required internal reference、fresh-context dispatch、fail-closed boundaryを保持する唯一のuser-facing entrypoint。
- `skills/sdd-implementation/references/planning-context.md`: Planning Controllerのownership、allowed / forbidden read rules、Decision Record、Control Return、Stage Capsule、Spec / Plan routingを定義する。
- `skills/sdd-implementation/references/research-stage.md`: Research Workerのinput、evidence scope、gitignored report、decision handoffを定義する。
- `skills/sdd-implementation/prompts/repository-researcher.md`: repository evidenceをpath / line付きでfact、conflict、unknownへ分離するfresh Research Worker prompt。
- `skills/sdd-implementation/prompts/spec-synthesizer.md`: research pathsとDecision RecordからWritten Specを統合するfresh Spec Synthesis Worker prompt。
- `skills/sdd-implementation/prompts/spec-reviewer.md`: accepted decision、evidence、unknown、acceptance criteria、non-goal、stop conditionを独立検証するfresh Spec Reviewer prompt。
- `skills/sdd-implementation/tests/test_skill_contract.py`: final internal resource shapeと既存public lifecycle contractを検証する。
- `skills/sdd-implementation/tests/test_preimplementation_context.py`: Planning Controller read rules、Decision Record、Control Return、fresh worker routing、negative simplicity、forward-flow contractsを検証する。
- `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`: implementation closeout時にlanded behaviorとcurrent / historical境界を統合するcurrent canonical design。
- `knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-implementation-plan.md`: baseline bindingと実行手順を保持するrepository-approved plan。review-state同期はPlanning Controllerが所有する。
- `knowledge/index.md`: repository-approved planとlanded canonical designのdiscoverabilityをcloseout時に同期する。
- `knowledge/log.md`: plan approval、implementation closeout、final review結果をappend-onlyでcloseout時に記録する。

---

### Task 1: Planning Controller, Decision Record, and bounded handoff contract

**Files:**
- Create: `skills/sdd-implementation/references/planning-context.md`
- Create: `skills/sdd-implementation/tests/test_preimplementation_context.py`
- Modify: `skills/sdd-implementation/SKILL.md:6-40`

**Interfaces:**
- Consumes: input maturity classification、Human dialogue、canonical spec / plan paths、approval state、short worker verdict。
- Produces: `Planning Controller` invariant、`Confirmed Decisions` / `Open Decisions`、`Control Return(status, artifact_path, decision_requests, material_risks)`、bounded `Stage Capsule`、fresh Plan Author dispatch。
- Preserves: Superpowers ownership、Human decision authority、`llm-wiki` durable checkpoints、existing Implementation Stage。

- [ ] **Step 1: Read the required implementation skills and verify the baseline binding**

Read completely before editing:

```text
/Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/writing-skills/SKILL.md
/Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/test-driven-development/SKILL.md
```

Run:

```bash
git rev-parse HEAD
git diff --exit-code 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d -- knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md
```

Expected: the first command prints the execution branch HEAD; the second exits 0 with no output, proving the approved spec is unchanged from baseline `66d93ae`.

- [ ] **Step 2: Write the failing Planning Controller contract tests**

Create `skills/sdd-implementation/tests/test_preimplementation_context.py` with:

```python
from __future__ import annotations

from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
PLANNING_CONTEXT = SKILL_DIR / "references" / "planning-context.md"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


class PreImplementationContextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.planning_text = read_or_empty(PLANNING_CONTEXT)

    def test_entrypoint_limits_main_session_to_planning_controller(self) -> None:
        self.assertIn("## Planning Controller", self.skill_text)
        for ownership in (
            "Human dialogue",
            "Decision Record",
            "approval state",
            "stage routing",
            "Control Return",
        ):
            self.assertIn(ownership, self.skill_text)
        self.assertIn(
            "Do not inspect source code, broad repository content, full artifacts, "
            "diffs, or raw command output.",
            " ".join(self.skill_text.split()),
        )

    def test_planning_controller_allowed_and_forbidden_reads_are_explicit(self) -> None:
        for allowed in (
            "applicable skill instructions and repository `AGENTS.md`",
            "repository root, branch, worktree, and status metadata",
            "Control Return and Stage Capsule",
            "short excerpt for the current decision",
            "approval state and canonical artifact paths",
        ):
            self.assertIn(allowed, self.planning_text)
        for forbidden in (
            "source code",
            "broad wiki or documentation pages",
            "full specification or full implementation plan",
            "git diff, test output, or raw command output",
            "multi-file repository exploration",
        ):
            self.assertIn(forbidden, self.planning_text)

    def test_spec_draft_is_the_only_decision_record(self) -> None:
        self.assertIn("## Decision Record", self.planning_text)
        self.assertIn("`Confirmed Decisions`", self.planning_text)
        self.assertIn("`Open Decisions`", self.planning_text)
        self.assertIn(
            "Do not create a separate ledger, `CONTEXT.md`, or repo-root `docs/adr/`.",
            self.planning_text,
        )
        self.assertIn(
            "Reopen a confirmed decision only when new repository evidence creates "
            "a material conflict.",
            " ".join(self.planning_text.split()),
        )

    def test_control_return_has_only_bounded_semantic_fields(self) -> None:
        self.assertIn("## Control Return", self.planning_text)
        for field in (
            "`status`",
            "`artifact_path`",
            "`decision_requests`",
            "`material_risks`",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn("Keep detailed findings in the artifact.", self.planning_text)
        self.assertIn(
            "Aim for about 200 words; do not add a word-count validator.",
            self.planning_text,
        )

    def test_stage_capsule_carries_only_current_control_state(self) -> None:
        self.assertIn("## Stage Capsule", self.planning_text)
        for field in (
            "current result",
            "canonical paths",
            "open decisions",
            "approval state",
            "material risks",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn(
            "Aim for about 400 words; do not copy raw discussion or tool output.",
            self.planning_text,
        )

    def test_plan_author_is_fresh_and_uses_upstream_writing_plans(self) -> None:
        normalized = " ".join(self.planning_text.split())
        self.assertIn("Plan Author Worker", self.planning_text)
        self.assertIn("superpowers:writing-plans", self.planning_text)
        self.assertIn("Do not inherit the parent conversation.", self.planning_text)
        self.assertIn(
            "The Planning Controller evaluates only the Control Return, plan path, "
            "spec binding, and repository-required approval.",
            normalized,
        )

    def test_missing_fresh_dispatch_never_falls_back_to_controller_exploration(self) -> None:
        self.assertIn(
            "If isolated fresh-context dispatch is unavailable, return `BLOCKED`.",
            self.planning_text,
        )
        self.assertIn(
            "Do not fall back to Planning Controller exploration or artifact authoring.",
            self.planning_text,
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the focused test and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t1-red \
python3 -m unittest discover -s skills/sdd-implementation/tests \
  -p "test_preimplementation_context.py" -v
```

Expected: FAIL because `references/planning-context.md` and the `Planning Controller` section do not exist at baseline.

- [ ] **Step 4: Add the minimal Planning Controller entrypoint seam**

In `skills/sdd-implementation/SKILL.md`, insert this section immediately before `## Dependency Preflight`:

```markdown
## Planning Controller

Before the Implementation Stage, the main session is the Planning Controller.
It owns Human dialogue, the current question, small Decision Record updates,
approval state, stage routing, and evaluation of each Control Return. Do not
inspect source code, broad repository content, full artifacts, diffs, or raw
command output.

Use isolated fresh-context dispatch for every Pre-Implementation Worker. Do not
inherit the parent conversation. Pass canonical paths, applicable constraints,
the current question, and missing task-local facts only. If isolated dispatch
with an explicit model is unavailable, return `BLOCKED`; do not move research
or authoring into the Planning Controller.

Read `references/planning-context.md` only when entering a pre-implementation
decision, synthesis, review, or plan-authoring stage. Keep stage details out of
this entrypoint.
```

Do not change the existing input maturity route, Implementation Stage, model / effort boundary, closeout, or remote-write sections.

- [ ] **Step 5: Create the exact planning context reference**

Create `skills/sdd-implementation/references/planning-context.md` with:

```markdown
# Planning Context

Load this reference only after input maturity selects a pre-implementation
decision, synthesis, review, or plan-authoring stage.

## Controller Ownership

The Planning Controller owns Human dialogue, the current material decision,
small updates to the Decision Record, approval state, stage routing, Control
Return evaluation, and the next Stage Capsule. It does not own repository
exploration, full artifact synthesis, review, or implementation.

## Read Boundary

Allowed direct reads:

- applicable skill instructions and repository `AGENTS.md`;
- repository root, branch, worktree, and status metadata;
- Control Return and Stage Capsule;
- a worker-provided short excerpt for the current decision;
- approval state and canonical artifact paths.

Forbidden direct reads:

- source code;
- broad wiki or documentation pages;
- full specification or full implementation plan;
- git diff, test output, or raw command output;
- multi-file repository exploration.

Pass paths to the responsible fresh worker instead of integrating these sources
inside the Planning Controller.

## Decision Record

Use the planning-worktree specification draft sections `Confirmed Decisions`
and `Open Decisions` as the only Decision Record. Do not create a separate
ledger, `CONTEXT.md`, or repo-root `docs/adr/`.

Before asking the Human, read only the worker-provided Decision Record excerpt
for the current question. Do not ask a confirmed question again. Reopen a
confirmed decision only when new repository evidence creates a material
conflict. Present the previous decision, conflicting evidence, and decision
impact together. Ask one material decision at a time through `grill-with-docs`;
workers remain advisory and never approve scope or risk.

## Control Return

Every Pre-Implementation Worker returns exactly these semantic fields:

- `status`: `complete`, `needs_decision`, or `blocked`;
- `artifact_path`: canonical or transient detail path, or `none`;
- `decision_requests`: one material Human decision or `none`;
- `material_risks`: current material conflict, blocker, or `none`.

Keep detailed findings in the artifact. Aim for about 200 words; do not add a
word-count validator.

## Stage Capsule

At each stage transition carry only:

- current result;
- canonical paths;
- open decisions;
- approval state;
- material risks.

Aim for about 400 words; do not copy raw discussion or tool output.

## Spec Synthesis And Review

After all material decisions are confirmed, dispatch a fresh Spec Synthesis
Worker with research report paths, the `Confirmed Decisions` and `Open
Decisions` excerpts, the current spec draft path, and applicable authoring
rules. Do not inherit the parent conversation.

Then dispatch a separate fresh Spec Reviewer with the spec path, research paths,
Decision Record excerpts, and review artifact path. The reviewer is
advisory-only. The Human must approve the Written Spec before Plan Stage.

## Plan Authoring

For a Human-approved current specification, dispatch a fresh Plan Author Worker.
Do not inherit the parent conversation. Pass the repository root, baseline
commit, approved spec path, required plan path, applicable repository rules, and
the current `superpowers:writing-plans` skill path. The worker maps current files
and tests, writes an executable TDD plan, performs the upstream plan
self-review, and returns only a Control Return.

The Planning Controller evaluates only the Control Return, plan path, spec
binding, and repository-required approval. It does not repeat repository file
mapping or code exploration. Do not begin Implementation Stage until the plan
is repository-approved.

## Failure Boundary

If isolated fresh-context dispatch is unavailable, return `BLOCKED`. Do not fall
back to Planning Controller exploration or artifact authoring. Do not add a
fallback matrix, retry scheduler, runtime state, packet schema, context
telemetry, manual compaction, or strict word-count enforcement.
```

- [ ] **Step 6: Run Task 1 GREEN verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t1-green \
python3 -m unittest discover -s skills/sdd-implementation/tests \
  -p "test_preimplementation_context.py" -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t1-green \
python3 -m unittest discover -s skills/sdd-implementation/tests \
  -p "test_skill_contract.py" -v

git diff --check
```

Expected: 7 new Planning Controller tests PASS, the existing 19 skill contract tests PASS, and `git diff --check` exits 0 with no output.

- [ ] **Step 7: Commit Task 1**

```bash
git add \
  skills/sdd-implementation/SKILL.md \
  skills/sdd-implementation/references/planning-context.md \
  skills/sdd-implementation/tests/test_preimplementation_context.py
git commit -m "Add SDD planning controller contract"
```

Expected: one scoped commit containing only the three Task 1 paths.

---

### Task 2: Fresh Research, Spec Synthesis, Spec Review, and Plan Author routing

**Files:**
- Create: `skills/sdd-implementation/references/research-stage.md`
- Create: `skills/sdd-implementation/prompts/repository-researcher.md`
- Create: `skills/sdd-implementation/prompts/spec-synthesizer.md`
- Create: `skills/sdd-implementation/prompts/spec-reviewer.md`
- Modify: `skills/sdd-implementation/SKILL.md:25-57`
- Modify: `skills/sdd-implementation/tests/test_preimplementation_context.py`
- Modify: `skills/sdd-implementation/tests/test_skill_contract.py:224-228`

**Interfaces:**
- Consumes: `repository_root: Path`、`baseline_commit: str`、`epic_id: str`、`current_question: str`、`constraints: list[str]`、canonical artifact paths、Decision Record excerpts。
- Produces: transient Research Report、review artifact、updated Written Spec、Control Return、repository-approved executable plan。
- Preserves: Human authority、Superpowers `brainstorming` / `writing-plans` ownership、`llm-wiki` write boundary、no parent-conversation inheritance。

- [ ] **Step 1: Add failing worker-resource and simplicity tests**

At module level in `skills/sdd-implementation/tests/test_preimplementation_context.py`, add:

```python
RESEARCH_STAGE = SKILL_DIR / "references" / "research-stage.md"
RESEARCHER_PROMPT = SKILL_DIR / "prompts" / "repository-researcher.md"
SYNTHESIZER_PROMPT = SKILL_DIR / "prompts" / "spec-synthesizer.md"
REVIEWER_PROMPT = SKILL_DIR / "prompts" / "spec-reviewer.md"
```

At the end of `setUpClass`, add:

```python
        cls.research_text = read_or_empty(RESEARCH_STAGE)
        cls.researcher_text = read_or_empty(RESEARCHER_PROMPT)
        cls.synthesizer_text = read_or_empty(SYNTHESIZER_PROMPT)
        cls.reviewer_text = read_or_empty(REVIEWER_PROMPT)
```

Add these test methods before the module’s `if __name__` block:

```python
    def test_research_stage_routes_only_fresh_repository_exploration(self) -> None:
        normalized = " ".join(self.research_text.split())
        self.assertIn("`.superpowers/research/<epic-id>/`", self.research_text)
        self.assertIn("`prompts/repository-researcher.md`", self.research_text)
        self.assertIn("Do not inherit the parent conversation.", self.research_text)
        self.assertIn(
            "The Planning Controller reads the Control Return, not the report body.",
            normalized,
        )
        for category in ("confirmed facts", "material conflicts", "unknowns"):
            self.assertIn(category, self.research_text)

    def test_every_worker_prompt_is_advisory_and_returns_control_fields(self) -> None:
        for prompt_text in (
            self.researcher_text,
            self.synthesizer_text,
            self.reviewer_text,
        ):
            self.assertIn("Do not inherit the parent conversation.", prompt_text)
            self.assertIn("advisory-only", prompt_text)
            for field in (
                "`status`",
                "`artifact_path`",
                "`decision_requests`",
                "`material_risks`",
            ):
                self.assertIn(field, prompt_text)

    def test_research_prompt_requires_path_and_line_evidence(self) -> None:
        for category in (
            "Confirmed Facts",
            "Material Conflicts",
            "Unknowns",
        ):
            self.assertIn(category, self.researcher_text)
        self.assertIn("repository-relative path and line range", self.researcher_text)
        self.assertIn("git history", self.researcher_text)
        self.assertIn("llm-wiki", self.researcher_text)

    def test_spec_synthesis_and_review_are_separate_fresh_workers(self) -> None:
        self.assertIn("Spec Synthesis Worker", self.synthesizer_text)
        self.assertIn("Spec Reviewer", self.reviewer_text)
        self.assertIn("`Confirmed Decisions`", self.synthesizer_text)
        self.assertIn("`Open Decisions`", self.synthesizer_text)
        self.assertIn("Do not fill an unresolved decision with an assumption.", self.synthesizer_text)
        for review_lens in (
            "accepted decisions",
            "resolved questions",
            "repository evidence",
            "unknowns",
            "acceptance criteria",
            "non-goals",
            "stop conditions",
        ):
            self.assertIn(review_lens, self.reviewer_text)

    def test_internal_resource_shape_has_no_new_user_facing_or_runtime_surface(self) -> None:
        references = {
            path.name for path in (SKILL_DIR / "references").iterdir()
        }
        prompts = {
            path.name for path in (SKILL_DIR / "prompts").iterdir()
        }
        self.assertEqual(
            {"planning-context.md", "research-stage.md"},
            references,
        )
        self.assertEqual(
            {
                "repository-researcher.md",
                "spec-synthesizer.md",
                "spec-reviewer.md",
            },
            prompts,
        )
        for forbidden in (
            "context-contract.toml",
            "runtime-state.json",
            "worker-packet.json",
            "fallback-matrix.md",
            "scheduler.py",
        ):
            self.assertFalse((SKILL_DIR / forbidden).exists())

    def test_contract_rejects_numerical_context_control_and_controller_fallback(self) -> None:
        combined = "\n".join(
            (
                self.skill_text,
                self.planning_text,
                self.research_text,
                self.researcher_text,
                self.synthesizer_text,
                self.reviewer_text,
            )
        )
        self.assertIn(
            "Do not require context telemetry, manual compaction, or a strict "
            "word-count validator.",
            combined,
        )
        self.assertIn(
            "Do not fall back to Planning Controller exploration or artifact authoring.",
            combined,
        )
```

In `skills/sdd-implementation/tests/test_skill_contract.py`, replace
`test_skill_has_only_the_minimal_resource_shape` with:

```python
    def test_skill_has_only_the_internal_stage_resource_shape(self) -> None:
        children = {path.name for path in SKILL_DIR.iterdir()} if SKILL_DIR.is_dir() else set()
        self.assertEqual(
            {"SKILL.md", "agents", "prompts", "references", "tests"},
            children,
        )
        self.assertEqual(
            {"planning-context.md", "research-stage.md"},
            {path.name for path in (SKILL_DIR / "references").iterdir()},
        )
        self.assertEqual(
            {
                "repository-researcher.md",
                "spec-synthesizer.md",
                "spec-reviewer.md",
            },
            {path.name for path in (SKILL_DIR / "prompts").iterdir()},
        )
        self.assertFalse((SKILL_DIR / "description.md").exists())
        self.assertFalse((SKILL_DIR / "context-contract.toml").exists())
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t2-red \
python3 -m unittest discover -s skills/sdd-implementation/tests -v
```

Expected: FAIL because `research-stage.md`, all three prompt files, and the final resource shape do not exist.

- [ ] **Step 3: Route the Research Stage lazily from the entrypoint**

In `skills/sdd-implementation/SKILL.md`, add this paragraph immediately before the final paragraph of `## Planning Controller`:

```markdown
For a change request or incomplete specification, read
`references/research-stage.md` before repository investigation. Research,
Spec Synthesis, Spec Review, and Plan Authoring must each use a fresh worker.
Do not require context telemetry, manual compaction, or a strict word-count
validator.
```

In the `Change request or incomplete specification` route, replace the current first sentence with:

```markdown
- **Change request or incomplete specification:** enter the Planning Controller,
  dispatch the fresh Research Worker defined by `references/research-stage.md`,
  then use `superpowers:brainstorming` and the Spec Stage below. Require Human
  written-spec approval before planning. Preserve approved and complete portions
  of an incomplete specification. Use Grill with Docs only for unresolved
  material decisions.
```

Keep the approved-spec and approved-plan routes unchanged so completed stages are still skipped.

- [ ] **Step 4: Create the Research Stage reference**

Create `skills/sdd-implementation/references/research-stage.md` with:

```markdown
# Research Stage

Load this reference only for a change request, incomplete specification, or a
material conflict that requires repository evidence.

## Dispatch

Create an isolated fresh-context Research Worker using
`prompts/repository-researcher.md`. Do not inherit the parent conversation. Pass
only:

- repository root and current baseline commit;
- epic ID and current research question;
- applicable repository and knowledge constraints;
- current spec path when one exists;
- report path under `.superpowers/research/<epic-id>/`.

Required isolated dispatch and explicit-model capability are fail-closed. If
they are unavailable, return `BLOCKED`. Do not fall back to Planning Controller
exploration or artifact authoring.

## Worker Scope

The Research Worker may inspect the minimum relevant repository structure,
source code, documentation, tests, validators, git history, and existing
knowledge. When a relevant knowledge root exists, it follows the `llm-wiki`
query contract. It separates confirmed facts, material conflicts, and unknowns,
and cites repository-relative paths and line ranges.

The worker does not make design decisions, approve scope, accept risk, or decide
the final Human question.

## Research Report

Write detailed evidence to the supplied path under
`.superpowers/research/<epic-id>/`. This directory is gitignored transient
evidence. Do not add the report to the wiki, Git, `knowledge/index.md`, or
`knowledge/log.md`.

Return only the Control Return defined in `planning-context.md`. The Planning
Controller reads the Control Return, not the report body. For a current material
decision, the worker may provide a short evidence excerpt or a dedicated excerpt
path.

## Decision Handoff

The Planning Controller compares the current Decision Record excerpt with the
Control Return. It asks the Human one unresolved material decision through
`grill-with-docs`. A confirmed decision remains closed unless new repository
evidence creates a material conflict.
```

- [ ] **Step 5: Create the fresh Research Worker prompt**

Create `skills/sdd-implementation/prompts/repository-researcher.md` with:

```markdown
# Repository Researcher

You are the fresh Research Worker for one pre-implementation research question.
Do not inherit the parent conversation. Your authority is advisory-only.

## Inputs

- repository root;
- baseline commit;
- epic ID;
- one research question;
- applicable constraints;
- current spec path, or `none`;
- report path under `.superpowers/research/<epic-id>/`.

Read the applicable repository `AGENTS.md` and knowledge router before scoped
exploration. Inspect only the source, tests, validators, documentation, git
history, and current runtime contract needed to answer the research question.
When relevant knowledge exists, use the `llm-wiki` query contract.

## Artifact

Write the report to the supplied report path with these sections:

1. `Question And Scope`
2. `Confirmed Facts`
3. `Material Conflicts`
4. `Unknowns`
5. `Decision Impact`
6. `Evidence`

Every confirmed fact and material conflict includes a repository-relative path
and line range. Distinguish an unavailable fact from a verified absence.

Do not decide architecture, scope, risk acceptance, approval, or the final Human
question. Do not modify canonical artifacts.

## Direct Return

Aim for about 200 words and return exactly:

- `status`
- `artifact_path`
- `decision_requests`
- `material_risks`

Keep all detailed evidence in the report. Do not add a word-count validator,
packet schema, runtime state, or retry protocol.
```

- [ ] **Step 6: Create the fresh Spec Synthesis and Spec Review prompts**

Create `skills/sdd-implementation/prompts/spec-synthesizer.md` with:

```markdown
# Spec Synthesizer

You are the fresh Spec Synthesis Worker. Do not inherit the parent conversation.
Your authority is advisory-only; the Human owns material decisions and Written
Spec approval.

## Inputs

- repository root;
- current spec draft path;
- Research Report paths;
- short `Confirmed Decisions` and `Open Decisions` excerpts;
- applicable repository and knowledge authoring rules.

Read only these paths and the minimum applicable authoring instructions. Update
the spec draft with problem, goals, non-goals, architecture, interfaces, control
flow, failure handling, testing, acceptance criteria, migration, and stop
conditions. Preserve every accepted decision. Do not reopen a resolved question.
Do not fill an unresolved decision with an assumption.

Keep `Confirmed Decisions` and `Open Decisions` in the spec draft as the only
Decision Record. Do not create another ledger, `CONTEXT.md`, or `docs/adr/`.

## Direct Return

Aim for about 200 words and return exactly:

- `status`
- `artifact_path`
- `decision_requests`
- `material_risks`

Keep the complete synthesis in the spec draft.
```

Create `skills/sdd-implementation/prompts/spec-reviewer.md` with:

```markdown
# Spec Reviewer

You are the independent fresh Spec Reviewer. Do not inherit the parent
conversation. Your authority is advisory-only; you cannot approve the Written
Spec or make a material Human decision.

## Inputs

- repository root;
- spec draft path;
- Research Report paths;
- short `Confirmed Decisions` and `Open Decisions` excerpts;
- review artifact path;
- applicable review constraints.

Review the spec against:

- accepted decisions are completely reflected;
- resolved questions are not reopened;
- repository evidence is not contradicted;
- unknowns are not stated as confirmed facts;
- acceptance criteria are executable;
- non-goals prevent scope expansion;
- stop conditions preserve Human authority and fail-closed boundaries.

Write evidence-backed findings and a `ready_for_human_review` or `needs_revision`
verdict to the supplied review artifact path. Do not edit the spec.

## Direct Return

Aim for about 200 words and return exactly:

- `status`
- `artifact_path`
- `decision_requests`
- `material_risks`

Keep detailed findings in the review artifact.
```

- [ ] **Step 7: Run Task 2 GREEN verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t2-green \
python3 -m unittest discover -s skills/sdd-implementation/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t2-green \
python3 -m unittest discover -s scripts \
  -p "test_validate_skill_architecture.py" -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t2-green \
python3 scripts/validate_skill_architecture.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-t2-green \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation

git diff --check
```

Expected: 32 SDD tests PASS (19 existing, Task 1’s 7, and Task 2’s 6
worker/simplicity tests), 11 architecture tests PASS, architecture validation
prints `OK: validated skill architecture policy (repository-change-loop)`,
quick validation prints `Skill is valid!`, and the diff check exits 0.

- [ ] **Step 8: Run the seven fresh-context forward scenarios**

Use isolated fresh-context dispatch for each scenario. Give each worker only the
listed paths and inputs; do not pass the parent conversation. Save detailed
scenario evidence under `.superpowers/research/sdd-preimplementation-context-isolation/forward-scenarios/` and do not commit it.

1. **Rough change request:** pass repository root, baseline, a rough change request, constraints, and a report path to the Research Worker. Expected: it reads source/evidence, writes a cited report, and returns one `decision_requests` item; the Planning Controller does not read source files.
2. **Long report:** provide enough scoped evidence to produce a multi-page report. Expected: the report holds the detail while the direct return contains only the four Control Return fields and stays concise.
3. **Confirmed decision:** give a fresh Planning Controller a short excerpt showing the current question in `Confirmed Decisions`. Expected: it does not ask the question again and routes to the next unresolved decision or stage.
4. **Material conflict:** give a fresh Planning Controller the previous confirmed decision plus a Research Worker excerpt with contradictory current evidence. Expected: it reopens only that decision and presents the old decision, conflict, and impact together.
5. **Spec synthesis and review:** give a fresh Spec Synthesis Worker only research paths, Decision Record excerpts, spec path, and authoring rules; then give a different fresh Spec Reviewer the resulting paths. Expected: synthesis preserves decisions, review remains advisory, and Human approval is still required.
6. **Plan author:** give a fresh Plan Author Worker repository root, baseline `66d93ae`, approved spec path, required plan path, repository rules, and the `writing-plans` skill path. Expected: it writes an executable plan, self-reviews spec coverage / placeholders / interface consistency, and returns only Control Return; the Planning Controller performs no code exploration.
7. **Missing dispatch capability:** remove isolated fresh-context dispatch from the declared runtime capability set. Expected: the route returns `BLOCKED` and does not move exploration or authoring into the Planning Controller.

Reject a scenario if read ownership, decision authority, artifact handoff,
duplicate-question prevention, or scope simplicity differs from the expected
behavior. Do not compare exact prose.

- [ ] **Step 9: Commit Task 2**

```bash
git add \
  skills/sdd-implementation/SKILL.md \
  skills/sdd-implementation/references/research-stage.md \
  skills/sdd-implementation/prompts/repository-researcher.md \
  skills/sdd-implementation/prompts/spec-synthesizer.md \
  skills/sdd-implementation/prompts/spec-reviewer.md \
  skills/sdd-implementation/tests/test_preimplementation_context.py \
  skills/sdd-implementation/tests/test_skill_contract.py
git commit -m "Route SDD planning work to fresh workers"
```

Expected: one scoped commit containing only the seven Task 2 paths.

---

### Task 3: Knowledge closeout, fresh verification, and final review

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`
- Verify: `skill-architecture.toml`
- Verify: `.github/workflows/skill-architecture.yml`

**Interfaces:**
- Consumes: Task 1 and Task 2 commits、independent task-review verdicts、seven forward-scenario results、fresh verification output。
- Produces: current canonical landed design、discoverable approved plan、append-only closeout evidence、whole-branch final verdict、`LOCAL_COMPLETE | BLOCKED`。
- Preserves: approved spec unchanged、three `llm-wiki` durable checkpoints、baseline `66d93ae` review range、local-only remote boundary。

- [ ] **Step 1: Complete independent task review before closeout**

For each Task 1 and Task 2 commit, dispatch a fresh reviewer with only:

```text
baseline commit
task commit
approved spec path
this implementation plan path
changed file paths
focused test results
```

Review only requirements fit, material simplicity, and material current risk.
Expected: each task is `APPROVED`, or an evidence-backed blocking finding is
returned to a fresh implementer for a bounded TDD fix and scoped re-review.
Style, formatting preference, future-only concern, and scope-external hardening
are non-blocking.

- [ ] **Step 2: Use the `llm-wiki` single-root ingest contract**

Read completely:

```text
skills/llm-wiki/SKILL.md
skills/llm-wiki/references/core.md
skills/llm-wiki/references/single-root.md
skills/llm-wiki/references/modes/ingest.md
```

Treat `knowledge/` as an owned single-root knowledge root. Do not modify the
approved focused spec. Keep Research Reports, forward-scenario evidence, worker
returns, test output, and review transcripts outside the wiki.

- [ ] **Step 3: Integrate landed behavior into the current canonical design**

In `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`, insert the
following section immediately before `## Entry Classification`:

```markdown
## 実装前 Planning Controller

実装前のmain sessionはPlanning Controllerであり、Human対話、current decision、
spec draft内の`Confirmed Decisions` / `Open Decisions`、approval、stage routing、
短いControl Returnだけを所有する。source code、broad wiki / docs、full spec /
plan、diff、test output、複数file探索は直接読まない。

Change requestまたはincomplete specではfresh Research Workerがgitignoredな
`.superpowers/research/<epic-id>/`へpath / line evidence付きreportを書く。
accepted decisionが揃った後はfresh Spec Synthesis Worker、別のfresh Spec
Reviewer、fresh Plan Author Workerへ順にrouteする。workerはparent conversationを
継承せずadvisory-onlyであり、Humanがmaterial decision、Written Spec approval、
repository-required Plan approvalを保持する。

workerの直接returnは`status`、`artifact_path`、`decision_requests`、
`material_risks`へ限定し、詳細はartifact pathへ置く。stage transitionはcurrent
result、canonical paths、open decisions、approval state、material riskだけを
Stage Capsuleへcarryする。Control ReturnとStage Capsuleの長さは運用目安であり、
context telemetry、manual compaction、word-count validatorをcorrectness gateにしない。

このseamは`skills/sdd-implementation/references/`と`prompts/`に閉じる。新しい
user-facing skill、custom scheduler、context contract、runtime state、packet schema、
fallback matrix、main-session exploration fallbackは追加しない。Superpowers、
`grill-with-docs`、`llm-wiki`の既存ownershipを変更しない。
```

In the same page’s `Testing Strategy` section, add the seven forward scenarios
from Task 2 as current landed verification coverage. In `Migration`, state that
the focused spec and this plan supersede only the pre-implementation context
ownership portion; historical loop context documents remain non-executable
evidence and their runtime machinery is not restored.

- [ ] **Step 4: Synchronize the knowledge index and append-only log**

In `knowledge/index.md`, update the existing SDD design summary so it includes
`Planning Controller`, `Control Return`, and `fresh pre-implementation worker`
search terms. Immediately after the existing focused spec entry, add exactly
one entry for this plan:

```markdown
- [SDD 実装前コンテキスト分離実装計画](wiki/syntheses/sdd-preimplementation-context-isolation-implementation-plan.md) — baseline `66d93ae`の承認済み仕様を、Planning Controller contract、fresh Research / Spec Synthesis / Spec Review / Plan Author seam、TDD、knowledge closeout、final reviewへ落とした実行可能計画。
  検索語: sdd-implementation, Planning Controller, Control Return, Stage Capsule, Decision Record, fresh worker, research-stage, planning-context, Spec Reviewer, Plan Author, baseline 66d93ae, TDD, 実装計画, コンテキスト分離
```

Append an `implementation-closeout-candidate` entry to `knowledge/log.md`.
Record:

- Task 1 and Task 2 full commit SHAs and subjects from
  `git log --format='%H %s' 66d93ae..HEAD`;
- both independent task-review verdicts;
- all seven forward-scenario verdicts;
- each verification command from Step 5 with its actual test count or success
  message;
- residual material risk or `none`;
- every unperformed remote action.

Do not add a `local-complete` claim before whole-branch final review approval.

- [ ] **Step 5: Run the complete fresh local verification bundle**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 -m unittest discover -s skills/sdd-implementation/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 -m unittest discover -s skills/llm-wiki/tests -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 -m unittest discover -s scripts -v

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 scripts/validate_skill_architecture.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 scripts/validate_skill_context.py --all

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 scripts/report_skill_context.py --all --json --fail-on-warning

PYTHONPYCACHEPREFIX=/private/tmp/sdd-preimplementation-final \
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/sdd-implementation

test ! -e skills/grill-to-pr-loop
test ! -e skills/issue-implementation-loop
test ! -e skills/sdd-implementation/context-contract.toml
test ! -e skills/sdd-implementation/runtime-state.json
test ! -e skills/sdd-implementation/worker-packet.json

git diff --check 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..HEAD
```

Expected:

- all SDD contract tests PASS;
- all `llm-wiki` tests PASS;
- all repository script tests PASS;
- architecture validator prints `OK: validated skill architecture policy (repository-change-loop)`;
- context validator and warning-free context report exit 0 without adding an SDD context contract;
- skill quick validation prints `Skill is valid!`;
- every absence check exits 0;
- `git diff --check` exits 0 with no output.

- [ ] **Step 6: Commit the closeout candidate**

```bash
git add \
  knowledge/wiki/syntheses/sdd-implementation-skill-design.md \
  knowledge/index.md \
  knowledge/log.md
git commit -m "Document SDD preimplementation context isolation"
```

Expected: one documentation-only closeout-candidate commit. The approved focused
spec remains byte-for-byte unchanged.

- [ ] **Step 7: Run final whole-branch review**

Dispatch a fresh final reviewer with:

```text
review range: 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..HEAD
approved spec: knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md
approved plan: knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-implementation-plan.md
production paths: skills/sdd-implementation/SKILL.md, references/, prompts/
test paths: skills/sdd-implementation/tests/
knowledge paths: knowledge/wiki/syntheses/sdd-implementation-skill-design.md, knowledge/index.md, knowledge/log.md
verification: Step 5 command results
```

Review code, tests, spec binding, plan execution, knowledge closeout, current /
historical boundary, and remote-write scope. Expected verdict: Critical 0,
Important 0, no unresolved material risk, `APPROVED`.

If a Critical or Important finding is returned, dispatch a fresh implementer for
the smallest bounded fix, rerun the affected RED/GREEN cycle and full Step 5
bundle, commit the fix, and dispatch a fresh scoped re-review. Do not broaden
scope or suppress required mechanical validation.

- [ ] **Step 8: Verify branch integrity and return control**

Run:

```bash
git status --short --branch
git log --oneline --decorate 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..HEAD
git diff --name-status 66d93ae4a233fc8f9750b6bc6d824cc54bb0838d..HEAD
git -C /Users/omitsuhashi/repos/omitsuhashi/skills status --short --branch
```

Expected: the planning/implementation worktree is clean; the log contains every
Task 1, Task 2, bounded fix if any, and closeout commit; changed
paths are restricted to this plan’s File Map; the default checkout matches the
execution preflight HEAD/status and contains no task-created change.

Return `LOCAL_COMPLETE` only after all task reviews, forward scenarios, fresh
verification, knowledge closeout, final whole-branch approval, completion
and branch integrity checks succeed. Return the final verdict to the Planning
Controller, which owns review-state synchronization. Report remote writes as
unperformed.

## Execution Handoff

After Human Execution Plan Gate approval, use
`superpowers:subagent-driven-development` and dispatch a fresh implementer plus
independent reviewer for each task. Do not execute this plan from an unapproved
state. No remote action is included in either execution mode.

## 関連ページ

- [SDD 実装前コンテキスト分離仕様](sdd-preimplementation-context-isolation-spec.md) — Human-approved Written Spec and binding source。
- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — current lifecycle、ownership、runtime capability、knowledge checkpointのcanonical baseline。
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md) — Human decision authorityとsupporting worker advisory boundary。
- [Loop Skill Context Compaction Spec](loop-skill-context-compaction-spec.md) — historical / non-executable evidence。artifact handoff原則だけを参照し、runtime machineryは再利用しない。

## 出典

- [SDD 実装前コンテキスト分離仕様](sdd-preimplementation-context-isolation-spec.md)
- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md)
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md)
- [sdd-implementation SKILL.md](../../../skills/sdd-implementation/SKILL.md)
- [skill-architecture.toml](../../../skill-architecture.toml)
- `codex-plugin-cache:openai-curated-remote/superpowers/6.2.0/skills/writing-plans/SKILL.md`

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

baseline `66d93ae`の承認済み仕様を、Planning Controller contract、fresh Research / Spec Synthesis / Spec Review / Plan Author seam、TDD、knowledge closeout、final reviewへ落とした実行可能計画。
