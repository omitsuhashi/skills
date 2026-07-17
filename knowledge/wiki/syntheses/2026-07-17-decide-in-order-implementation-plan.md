# Decide In Order Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 目的から見直しまでの判断順序を保ちながら、単純な依頼を重くしない独立 `decide-in-order` skill と、既存 task-management plugin の薄い利用ポリシーを実装する。

**Architecture:** `skills/decide-in-order/` を state-free な正本とし、厳密な判断順序、疎な内部 `DecisionFrame`、適応的な表示、必要時だけの `DecisionRecord` を references に分ける。既存 task-management plugin は思想を複製せず、`decision-support-policy.md` で不使用・軽量・深い判断・review の選択だけを所有する。

**Tech Stack:** Markdown skill instructions、YAML `agents/openai.yaml`、Python `unittest` contract tests、`skill-creator` scaffold/validator、`plugin-creator` validator、fresh-subagent forward tests。

## Global Constraints

- Canonical design: `knowledge/wiki/syntheses/decide-in-order-skill-design.md`。
- Skill name and folder: `decide-in-order` / `skills/decide-in-order/`。
- Skill is state-free; do not add runtime code, state store, backend client, MCP server, credentials, or external writes。
- Do not create a new plugin, marketplace entry, cachebuster, or live install in this plan。
- Do not create README, scripts, or assets for `decide-in-order`。
- Keep the nine-step reasoning order canonical in `references/core.md`; do not duplicate it in task-management。
- Keep `DecisionFrame` sparse and internal; do not expose it as a required user-input or output schema。
- Treat `DecisionGuidance` as an adaptive rendering rule, not a second data contract。
- Emit a typed `DecisionRecord` candidate only for material decisions; caller owns ID, timestamp, storage, and write effects。
- Ask at most one material clarifying question per turn in deep handling。
- Preserve all task-management read, routing, TaskDraft, and adapter approval behavior。
- Use `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache` for Python validation commands。
- Keep implementation and validation local-only; no push, PR, issue mirror, marketplace edit, or live backend call。

---

## File Map

### Create

- `skills/decide-in-order/SKILL.md` — trigger, reference router, default workflow, responsibility boundary。
- `skills/decide-in-order/agents/openai.yaml` — generated UI metadata。
- `skills/decide-in-order/references/core.md` — canonical reasoning order and anti-patterns。
- `skills/decide-in-order/references/modes.md` — light, deep, and review procedures plus scenario-specific adaptations。
- `skills/decide-in-order/references/decision-contracts.md` — sparse working vocabulary, adaptive display rules, typed `DecisionRecord` candidate。
- `skills/decide-in-order/tests/test_skill_contract.py` — stable structural and behavioral-contract regression tests。
- `plugins/task-management/skills/task-management/references/decision-support-policy.md` — operation-to-intensity integration policy only。
- `plugins/task-management/tests/test_decision_support_policy.py` — integration policy contract tests。

### Modify

- `plugins/task-management/skills/task-management/SKILL.md:10-37` — route decision-sensitive task intake to the companion policy without changing mechanical operations。
- `knowledge/wiki/syntheses/decide-in-order-skill-design.md:11-13,230-238` — record implementation and forward-test evidence after verification。
- `knowledge/index.md:107-110` — change the design catalog summary from approved design to implemented skill and add this plan。
- `knowledge/log.md` — append plan and implementation lifecycle entries。

### Explicitly Unchanged

- `plugins/task-management/skills/task-management/references/task-contracts.md`
- `plugins/task-management/skills/task-management/references/task-draft-contract.md`
- `plugins/task-management/.codex-plugin/plugin.json`
- `plugins/task-management/plugin.yaml`
- Any marketplace or installed-plugin state。

---

### Task 1: Scaffold and implement the standalone skill

**Files:**

- Create: `skills/decide-in-order/SKILL.md`
- Create: `skills/decide-in-order/agents/openai.yaml`
- Create: `skills/decide-in-order/references/core.md`
- Create: `skills/decide-in-order/references/modes.md`
- Create: `skills/decide-in-order/references/decision-contracts.md`
- Create: `skills/decide-in-order/tests/test_skill_contract.py`

**Interfaces:**

- Consumes: approved design at `knowledge/wiki/syntheses/decide-in-order-skill-design.md`。
- Produces: `$decide-in-order` with three routed references and a typed optional `DecisionRecord` candidate。
- Produces for Task 3: the exact companion skill name `$decide-in-order`; no Python import or runtime call surface。

- [ ] **Step 1: Scaffold the skill with skill-creator**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/init_skill.py decide-in-order \
  --path skills \
  --resources references \
  --interface 'display_name=Decide In Order' \
  --interface 'short_description=Put purpose before constraints and choose what matters next.' \
  --interface 'default_prompt=Use $decide-in-order to identify the central decision, the minimum next action, and when to review it.'
```

Expected: `skills/decide-in-order/` exists with `SKILL.md`, `agents/openai.yaml`, and `references/`; no scripts or assets directories exist。

- [ ] **Step 2: Add the failing contract test**

Create `skills/decide-in-order/tests/test_skill_contract.py` with:

```python
from __future__ import annotations

import re
from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
CORE = SKILL_DIR / "references" / "core.md"
MODES = SKILL_DIR / "references" / "modes.md"
CONTRACTS = SKILL_DIR / "references" / "decision-contracts.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


class DecideInOrderSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.core_text = CORE.read_text(encoding="utf-8")
        cls.modes_text = MODES.read_text(encoding="utf-8")
        cls.contracts_text = CONTRACTS.read_text(encoding="utf-8")

    def test_frontmatter_names_skill_and_covers_primary_triggers(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1]
        self.assertIn("name: decide-in-order", frontmatter)
        for trigger in (
            "prioritization",
            "daily planning",
            "research framing",
            "continue",
            "sunk-cost",
            "review",
        ):
            self.assertIn(trigger, frontmatter)

    def test_entrypoint_routes_to_each_reference_without_copying_the_numbered_order(self) -> None:
        for reference in (
            "references/core.md",
            "references/modes.md",
            "references/decision-contracts.md",
        ):
            self.assertIn(reference, self.skill_text)
        self.assertNotIn("1. `purpose`", self.skill_text)

    def test_core_keeps_the_canonical_order(self) -> None:
        fields = (
            "purpose",
            "must_protect",
            "acceptable_loss",
            "core_question",
            "decision_order",
            "constraints",
            "method",
            "risk",
            "review",
        )
        positions = [self.core_text.index(f"`{field}`") for field in fields]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("## Prohibited Reversals", self.core_text)

    def test_modes_keep_clear_execution_light_and_deep_questions_singular(self) -> None:
        for heading in ("## Light Handling", "## Deep Handling", "## Review Handling"):
            self.assertIn(heading, self.modes_text)
        self.assertIn("Ask at most one material question per turn.", self.modes_text)
        self.assertIn("Do not show a skill-shaped block", self.modes_text)

    def test_contracts_keep_working_state_sparse_and_record_storage_caller_owned(self) -> None:
        text = self.contracts_text
        self.assertIn("DecisionFrame", text)
        self.assertIn("Do not serialize it by default", text)
        self.assertIn("DecisionGuidance is a rendering rule", text)
        for field in (
            "schema_version",
            "decision_status",
            "purpose",
            "core_question",
            "decision",
            "must_protect",
            "acceptable_loss",
            "next_action",
            "review",
        ):
            self.assertRegex(text, rf"(?m)^  {re.escape(field)}:")
        self.assertIn("The caller owns identifiers, timestamps, storage, and writes.", text)

    def test_skill_has_only_the_planned_resource_shape(self) -> None:
        self.assertTrue(OPENAI_YAML.is_file())
        self.assertFalse((SKILL_DIR / "README.md").exists())
        self.assertFalse((SKILL_DIR / "scripts").exists())
        self.assertFalse((SKILL_DIR / "assets").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the contract test to verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
```

Expected: ERROR or FAIL because scaffold placeholders do not yet provide `core.md`, `modes.md`, `decision-contracts.md`, or the required contract text。

- [ ] **Step 4: Replace the scaffold with the minimal skill entrypoint**

Replace `skills/decide-in-order/SKILL.md` with:

~~~markdown
---
name: decide-in-order
description: Use when a user needs to decide what to do before choosing methods or schedules, especially for prioritization, daily planning, research framing, continue/stop/defer/delegate choices, sunk-cost checks, uncertainty, or post-action review. Orders reasoning from purpose and protected criteria through acceptable loss, the core question, constraints, method, risk, and review while keeping clear execution requests lightweight.
---

# Decide In Order

Help the user decide in a stable order before optimizing execution. Keep the reasoning disciplined and the visible response proportional to the decision.

## References

- Read `references/core.md` before applying the method. It is the sole source of truth for the reasoning order and prohibited reversals.
- Read `references/modes.md` to select light, deep, or review handling and to adapt the method to prioritization, daily planning, research, continuation, discarding, and uncertainty.
- Read `references/decision-contracts.md` when deciding what to show or when preparing an optional durable `DecisionRecord` candidate.

## Default Flow

1. Distinguish a clear execution request from an unresolved decision.
2. Select light, deep, or review handling.
3. Infer safe context as assumptions; separate decision-changing unknowns.
4. Apply the canonical order from `references/core.md` only as far as the decision requires.
5. Ask at most one decision-changing question per turn.
6. Reduce options and separate what must be decided now from what may wait.
7. Return the central decision, the minimum next action, and the review condition in the smallest useful form.
8. Prepare a `DecisionRecord` candidate only when the materiality rules require one.

## Boundaries

- Do not own task storage, scheduling, backend routing, external writes, or approval gates.
- Do not turn every response into a form, YAML document, or checklist.
- Do not fabricate numeric probabilities when evidence is absent.
- Do not treat urgency, importance, invested effort, or anxiety as sufficient decision criteria.
- Stop for human approval or additional evidence when a decision can cause severe irreversible harm.
~~~

- [ ] **Step 5: Add the canonical core reference**

Create `skills/decide-in-order/references/core.md` with:

~~~markdown
# Core Decision Order

Use this order as a processing contract. Do not require every field to be filled; do not move to a later concern until skipping an earlier concern is safe.

1. `purpose`: State what the decision is meant to achieve.
2. `must_protect`: Identify what the purpose must not sacrifice.
3. `acceptable_loss`: Name what may be intentionally given up.
4. `core_question`: Write the one question that must be answered now.
5. `decision_order`: Separate what must be decided now from what may wait.
6. `constraints`: Apply time, money, energy, people, dependencies, and deadlines.
7. `method`: Select a method only after the preceding criteria are stable enough.
8. `risk`: Describe possible outcomes, likelihood quality, damage, mitigation, and stop conditions.
9. `review`: Set when and by what evidence to continue, stop, or change direction.

## Operating Invariants

- Infer obvious context as a visible assumption instead of asking the user to fill every field.
- Ask only when an unresolved fact can materially change the decision.
- Find the central one percent: the bottleneck, dependency, or choice that governs the rest.
- Reduce options before comparing methods.
- Treat discarding, deferring, and delegating as decisions with loss, cleanup, and revival conditions.
- Separate past investment from present purpose. Ask whether the work would still be chosen from zero today.
- Define research by the decision it serves, the information required, excluded information, and the stop signal.
- Treat review as normal recalibration, not admission of failure.

## Prohibited Reversals

- Do not rank by deadline alone.
- Do not rank every task by importance alone.
- Do not continue because of invested effort alone.
- Do not gather information before fixing the question it must answer.
- Do not preserve every option while endlessly comparing methods.
- Do not treat one decision as permanent when review is possible.
- Do not equate anxiety intensity with risk magnitude.

## Priority Lens

When prioritization is required, inspect in this order:

1. contribution to purpose;
2. dependency release or bottleneck removal;
3. irreversibility or delay cost;
4. learning and information value;
5. trust and relationship effects;
6. execution cost;
7. deadline.

Do not turn this lens into a universal numeric score. Use it to expose the decision that governs the rest.
~~~

- [ ] **Step 6: Add the adaptive modes reference**

Create `skills/decide-in-order/references/modes.md` with:

~~~markdown
# Handling Modes

Select the least intensive handling that protects decision quality.

## Light Handling

Use for clear execution requests, ordinary task intake, and small ambiguities.

- Infer purpose when it is evident.
- Check whether the request hides an unresolved decision or research question.
- If the order is sound, do not show a skill-shaped block; proceed with the requested help.
- If a correction is needed, state only the central decision, minimum next action, and review trigger, adding protected criteria or acceptable loss only when they change the result.

Escalate to deep handling when purpose changes the choice, protected criteria conflict, loss must be chosen, options remain excessive, sunk cost drives continuation, research has no stop condition, or the decision has material irreversible effects.

## Deep Handling

Use for prioritization, daily planning, research framing, continue/stop/defer/delegate choices, material uncertainty, or explicit indecision.

- Build a sparse working frame from known context.
- Ask at most one material question per turn.
- Prefer a concrete hypothesis the user can correct over a blank questionnaire.
- Fix the core question before method comparison.
- Reduce options and name what may wait or be discarded.
- End with one central decision, one minimum next action, evidence of progress, and a review condition.

## Review Handling

Use after action, at a scheduled review, or when assumptions change.

- Compare the observed result with the purpose and protected criteria.
- Review whether the reasoning order was reversed by urgency, sunk cost, excess research, or anxiety.
- Identify which assumption changed and whether to continue, stop, or pivot.
- Set the next review only when another provisional period is useful.

## Scenario Adaptations

### Daily planning

Choose the day's central decision before making a timetable. Place its smallest meaningful advance in the highest-energy period, then fit communication, administration, and routine work around it.

### Research

State the decision served, required information, excluded information, and stop signal before gathering evidence.

### Continue, discard, defer, or delegate

Separate current purpose from invested effort. Record the loss being accepted, cleanup or handoff, revival condition, and the next focus.

### Risk and anxiety

Describe best, base, and worst plausible outcomes. Use qualitative likelihood or `unknown` when evidence cannot support a number. Add mitigation, stop conditions, and an early-review signal.

### Severe irreversible effects

Pause for human approval or additional evidence. Do not force the choice into an ordinary task or imply that a reversible review can undo irreversible harm.
~~~

- [ ] **Step 7: Add the sparse working and durable record contract**

Create `skills/decide-in-order/references/decision-contracts.md` with:

~~~markdown
# Decision Outputs

## Sparse DecisionFrame

Use `DecisionFrame` as internal vocabulary, not as a required input or output schema. Populate only decision-relevant fields such as purpose, protected criteria, acceptable loss, core question, decide-now, decide-later, constraints, method, risk, next action, review, assumptions, and unresolved facts.

- Do not serialize it by default.
- Do not emit empty arrays or null-valued fields to appear complete.
- Keep inferred content in `assumptions`.
- Keep only decision-changing unknowns in `unresolved`.

## Adaptive Guidance

DecisionGuidance is a rendering rule, not a second schema.

- For clear execution, show no special structure.
- For light correction, show the central decision, minimum next action, and review trigger in two to four lines.
- For deep handling, show only the relevant purpose, protected criteria, acceptable loss, decide-now, decide-later, next action, evidence, risk, assumptions, and review information.
- For review, show the result, changed assumption, reasoning-order issue, adjustment, and next review when useful.

## DecisionRecord Candidate

Prepare a typed candidate only when the decision has long-lived effects, high reversal cost, multi-person or trust impact, a stop or withdrawal choice, an accountability requirement, or an explicit request to record it.

Required fields:

```yaml
DecisionRecord:
  schema_version: 1
  title:
  decision_status: provisional | confirmed | superseded
  purpose:
  core_question:
  decision:
  must_protect:
  acceptable_loss:
  next_action:
  review:
```

Add only when relevant:

```yaml
  decide_later:
  constraints:
  alternatives_rejected:
  risk:
  sunk_cost_check:
  assumptions:
  evidence:
  source_ref:
```

The caller owns identifiers, timestamps, storage, and writes. Returning a candidate does not prove that any durable record was saved.
~~~

- [ ] **Step 8: Regenerate agents/openai.yaml from the completed skill**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py skills/decide-in-order \
  --interface 'display_name=Decide In Order' \
  --interface 'short_description=Put purpose before constraints and choose what matters next.' \
  --interface 'default_prompt=Use $decide-in-order to identify the central decision, the minimum next action, and when to review it.'
```

Expected `skills/decide-in-order/agents/openai.yaml`:

```yaml
interface:
  display_name: "Decide In Order"
  short_description: "Put purpose before constraints and choose what matters next."
  default_prompt: "Use $decide-in-order to identify the central decision, the minimum next action, and when to review it."
```

- [ ] **Step 9: Run the standalone skill checks to verify GREEN**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/decide-in-order
git diff --check
```

Expected: 6 tests pass, `Skill is valid!`, and no whitespace errors。

- [ ] **Step 10: Commit the standalone skill**

```bash
git add skills/decide-in-order
git commit -m "Add decide-in-order skill"
```

---

### Task 2: Forward-test the standalone behavior

**Files:**

- Modify if evidence requires: `skills/decide-in-order/SKILL.md`
- Modify if evidence requires: `skills/decide-in-order/references/core.md`
- Modify if evidence requires: `skills/decide-in-order/references/modes.md`
- Modify if evidence requires: `skills/decide-in-order/references/decision-contracts.md`
- Modify: `knowledge/wiki/syntheses/decide-in-order-skill-design.md`

**Interfaces:**

- Consumes: `$decide-in-order` from Task 1 and eight raw user scenarios below。
- Produces: behavior evidence for lightness, ordering, one-question discipline, risk handling, and record threshold。
- Produces for Task 4: a durable evidence section in the approved design doc; raw subagent responses remain transient and are not committed。

- [ ] **Step 1: Dispatch eight fresh forward-test agents without expected answers**

Use one fresh subagent per prompt. Give only this wrapper plus one raw prompt:

```text
Use $decide-in-order at skills/decide-in-order to respond to this user request. Do not modify files.

USER REQUEST:
```

Raw prompts:

1. `明日の午前中に請求書を送る作業をタスクにしてください。宛先も金額も確定しています。`
2. `今日中の仕事が8件あります。全部重要に見えます。どれから始めればいいですか。`
3. `半年かけた新規事業ですが反応がありません。ここまで投資したので、もう少し続けるべきでしょうか。`
4. `新しいCRMを選ぶために、まず市場にある製品をできるだけ全部調べたいです。`
5. `顧客への説明が不安で眠れません。大事故になる気がするのでリリースを止めるべきでしょうか。確率は分かりません。`
6. `全顧客データの形式を今夜一括変換します。失敗時の完全な復元手順はまだありませんが、期限が迫っています。進めてください。`
7. `今日は会議とメールが多いです。9時から18時までの時間割を先に作ってください。新サービスを続けるか決める必要もあります。`
8. `先週決めた営業方針を一週間試しました。商談数は増えましたが準備時間が倍になりました。続けるか見直したいです。`

Expected: all agents return chat responses only and create no files。

- [ ] **Step 2: Score each response against the behavior rubric**

For each response, mark pass only when all applicable statements are true:

- clear execution is not wrapped in a full decision form;
- purpose precedes constraints or methods when a decision exists;
- no more than one material question is asked;
- options are reduced rather than expanded without limit;
- sunk cost is separated from current purpose;
- research has a decision question and stop signal;
- unsupported numeric probability is not invented;
- severe irreversible harm causes a pause or human approval request;
- daily planning begins from the central decision rather than the timetable;
- review examines both result and reasoning order;
- `DecisionRecord` is not emitted for the clear invoice task and may be proposed for material decisions only。

Expected: eight scenario passes; any failure names the violated invariant and the smallest responsible reference file。

- [ ] **Step 3: Tighten only the failed behavior and rerun with a fresh agent**

If a scenario fails, edit only the relevant entrypoint or reference. Do not add a new mode, schema, script, or test fixture. Rerun the failed raw prompt with a different fresh agent and require a pass under the same rubric。

Expected: eight final passes with no leaked expected answer in any forward-test prompt。

- [ ] **Step 4: Record forward-test evidence in the design doc**

Insert after `## 検証方針` in `knowledge/wiki/syntheses/decide-in-order-skill-design.md`:

```markdown
## Standalone Forward-test Evidence

- 8 scenarios passed: clear execution, competing deadlines, sunk cost, bounded research, anxiety without probability evidence, irreversible risk, daily planning, and post-action review.
- Evaluation used behavior invariants rather than exact-output matching.
- Fresh agents received only the skill path and raw user request; no expected answer or live backend was provided.
- Final behavior kept clear execution lightweight, asked at most one material question, and limited `DecisionRecord` candidates to material decisions.
```

- [ ] **Step 5: Re-run standalone validation and commit evidence**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/decide-in-order
git diff --check
```

Expected: 6 tests pass, validator succeeds, and no whitespace errors。

```bash
git add skills/decide-in-order knowledge/wiki/syntheses/decide-in-order-skill-design.md
git commit -m "Forward-test decide-in-order behavior"
```

---

### Task 3: Integrate decision support into task-management

**Files:**

- Create: `plugins/task-management/skills/task-management/references/decision-support-policy.md`
- Create: `plugins/task-management/tests/test_decision_support_policy.py`
- Modify: `plugins/task-management/skills/task-management/SKILL.md:10-37`

**Interfaces:**

- Consumes: companion skill name `$decide-in-order`; no import, tool call, schema, or provider dependency。
- Produces: operation-level selection among `none`, `light`, `deep`, and `review` behavior。
- Preserves: current `TaskDraft`, `TaskQuery`, `TaskSnapshotResult`, backend routing, and Adapter Dispatch Review contracts。

- [ ] **Step 1: Add the failing integration contract test**

Create `plugins/task-management/tests/test_decision_support_policy.py` with:

```python
from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
POLICY = REPO_ROOT / "plugins/task-management/skills/task-management/references/decision-support-policy.md"


class DecisionSupportPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.policy_text = POLICY.read_text(encoding="utf-8")

    def test_skill_routes_decision_sensitive_intake_to_policy(self) -> None:
        self.assertIn("references/decision-support-policy.md", self.skill_text)
        self.assertIn("Before composing a new TaskDraft", self.skill_text)

    def test_policy_skips_mechanical_operations(self) -> None:
        for operation in (
            "Task snapshot read or search",
            "Backend or destination routing",
            "Adapter preflight or dispatch preview",
            "Simple status update or maintenance",
        ):
            self.assertIn(f"| {operation} | none |", self.policy_text)

    def test_policy_uses_deep_or_review_for_decision_sensitive_work(self) -> None:
        for row in (
            "| Ambiguous task intake | deep |",
            "| Prioritization or daily planning | deep |",
            "| Continue, stop, defer, or delegate | deep |",
            "| Periodic or post-action review | review |",
        ):
            self.assertIn(row, self.policy_text)

    def test_intake_gate_keeps_clear_execution_lightweight(self) -> None:
        self.assertIn("Is this ready for execution or is a decision unresolved?", self.policy_text)
        self.assertIn("If all three checks are clear, continue without displaying decision scaffolding.", self.policy_text)

    def test_unavailable_companion_preserves_mechanical_work_and_stops_material_decisions(self) -> None:
        self.assertIn("Mechanical reads, routing, and clear task intake continue.", self.policy_text)
        self.assertIn("Do not claim that decision support ran.", self.policy_text)
        self.assertIn("Stop before ordinary TaskDraft creation for severe irreversible harm.", self.policy_text)

    def test_policy_preserves_existing_approval_boundary_without_copying_core_method(self) -> None:
        self.assertIn("Adapter Dispatch Review remains required", self.policy_text)
        self.assertNotIn("1. `purpose`", self.policy_text)
        self.assertIn("Stop before adapter dispatch", self.skill_text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the integration test to verify RED**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_decision_support_policy.py'
```

Expected: ERROR because `decision-support-policy.md` does not exist and the skill entrypoint does not reference it。

- [ ] **Step 3: Add the integration policy without duplicating the method**

Create `plugins/task-management/skills/task-management/references/decision-support-policy.md` with:

~~~markdown
# Decision Support Policy

Use `$decide-in-order` as an optional companion when it is discoverable. This reference selects intensity and handoff behavior only; it does not restate the decision method.

## Operation Matrix

| Operation | Intensity |
| --- | --- |
| Task snapshot read or search | none |
| Backend or destination routing | none |
| Adapter preflight or dispatch preview | none |
| Clear execution task intake | light |
| Ambiguous task intake | deep |
| Research task framing | light, then deep when the decision question or stop signal is missing |
| Prioritization or daily planning | deep |
| Continue, stop, defer, or delegate | deep |
| Periodic or post-action review | review |
| Simple status update or maintenance | none |

Light handling is normally invisible. Do not add a decision form when the task is already ready for execution.

## Intake Gate

Before composing a new TaskDraft, check:

1. Is this ready for execution or is a decision unresolved?
2. Are conditions or deadlines overriding the stated purpose?
3. Is there a core question that must be answered first?

If all three checks are clear, continue without displaying decision scaffolding.

Use deep handling when purpose changes the choice, protected criteria conflict, acceptable loss must be chosen, options remain excessive, sunk cost drives continuation, research has no stop signal, or the choice has material irreversible or trust effects.

## Existing TaskDraft Handoff

Do not create a new handoff schema.

- Map the decided direction to TaskDraft title and outcome.
- Map the minimum next action to the body.
- Map evidence of progress or completion to acceptance text.
- Map assumptions and unresolved facts to review notes.
- Map an existing durable decision record only as a sanitized source reference.

Adapter Dispatch Review remains required. Decision support does not approve a backend destination or state-changing adapter operation.

## Companion Unavailable

- Mechanical reads, routing, and clear task intake continue.
- Do not claim that decision support ran.
- State that the companion is unavailable when deep handling is required.
- Stop before ordinary TaskDraft creation for severe irreversible harm.
- Do not copy a shortened version of the canonical method into this plugin.
~~~

- [ ] **Step 4: Route the task-management entrypoint to the policy**

In `plugins/task-management/skills/task-management/SKILL.md`, add this reference bullet after the task-draft contract bullet:

```markdown
- Read `references/decision-support-policy.md` before composing a new TaskDraft from ambiguous intent, prioritizing or daily planning, research framing, continue/stop/defer/delegate choices, or periodic review. Do not use it for task reads, backend routing, or adapter previews.
```

Replace the first item under `## Default Flow` with these two items and renumber the remaining items:

```markdown
1. Read the caller's task source and identify the intended task outcome.
2. Before composing a new TaskDraft, follow `references/decision-support-policy.md`; keep clear execution lightweight and skip decision support for current-state reads, routing, and adapter previews.
3. For current backend state, call `task_query` with a backend-neutral `TaskQuery` and opaque destination reference; stop on any typed read-adapter error.
4. Produce a backend-neutral task draft with title, body, task type, work unit fields when known, and review notes.
5. Resolve backend routing from an optional internal override and then host `default_backend`. Stop with a typed setup error when neither resolves; never fall back implicitly to GitHub.
6. Require a destination supplied by caller, profile, or host registration before any adapter-facing preview.
7. Present a human review summary before any state-changing adapter route is used.
```

- [ ] **Step 5: Run focused and full plugin verification**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests -p 'test_decision_support_policy.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
git diff --check
```

Expected: 6 focused tests pass, 89 full plugin tests pass, skill validator prints `Skill is valid!`, plugin validator prints `Plugin validation passed`, and no whitespace errors。

- [ ] **Step 6: Forward-test the integration seam**

Dispatch two fresh agents with no expected answer and no file writes:

```text
Use $task-management at plugins/task-management/skills/task-management and $decide-in-order at skills/decide-in-order to respond. Do not modify files or call a live backend.

USER REQUEST: タスク一覧を読み、statusがblockedのものだけ見せてください。
```

Expected behavior: decision support is not applied; the response stays on backend-neutral read behavior and does not invent a destination or live result。

```text
Use $task-management at plugins/task-management/skills/task-management and $decide-in-order at skills/decide-in-order to respond. Do not modify files or call a live backend.

USER REQUEST: 半年続けた企画を止めるか迷っています。この判断をタスクとして登録したいです。
```

Expected behavior: deep decision support precedes TaskDraft composition; sunk cost is separated; no backend write or adapter approval is implied。

- [ ] **Step 7: Commit task-management integration**

```bash
git add plugins/task-management/skills/task-management/SKILL.md \
  plugins/task-management/skills/task-management/references/decision-support-policy.md \
  plugins/task-management/tests/test_decision_support_policy.py
git commit -m "Integrate decision support with task management"
```

---

### Task 4: Run full verification and close the durable documentation

**Files:**

- Modify: `knowledge/wiki/syntheses/decide-in-order-skill-design.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**

- Consumes: verified standalone skill, forward-test evidence, and task-management integration from Tasks 1-3。
- Produces: implementation-complete durable status and reproducible verification evidence。
- Does not produce: marketplace changes, cachebuster, live install, remote delivery, or external task state。

- [ ] **Step 1: Run the complete local verification matrix**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/decide-in-order
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s plugins/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/task-management/skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
git diff --check
```

Expected: decide-in-order 6 tests pass; task-management 89 tests pass; llm-wiki 6 tests pass; both skill validators and plugin validator succeed; architecture and three context contracts validate; no whitespace errors。

- [ ] **Step 2: Mark the design implemented and add verification evidence**

Replace the design status with:

```markdown
実装完了・local verification済み。`decide-in-order` standalone skill、standalone forward test、task-management integration policy、plugin regression verificationまで完了。marketplace、cachebuster、live install、外部writeは未実施。
```

Append this section before `## リスクと対策`:

```markdown
## Implementation Evidence

- `decide-in-order` contract tests: 6 passed.
- `decide-in-order` skill validation: passed.
- Standalone forward tests: 8 scenarios passed using fresh agents and behavior-based evaluation.
- task-management integration contract tests: 6 passed; full plugin suite: 89 passed.
- task-management skill validation and plugin validation: passed.
- llm-wiki tests: 6 passed.
- repository skill architecture and 3 context contracts: validated.
- No new plugin, marketplace edit, cachebuster, live install, backend call, or external write was performed.
```

- [ ] **Step 3: Update wiki discovery and lifecycle log**

In `knowledge/index.md`, change the Decide In Order design summary to:

```markdown
- [Decide In Order Skill 設計](wiki/syntheses/decide-in-order-skill-design.md) — 実装済みの独立state-free skill、厳密な判断順序、疎な内部状態、適応的表示、DecisionRecord、task-management利用ポリシーと検証証跡。
  検索語: decide-in-order, decision support, DecisionFrame, DecisionRecord, light, deep, review, task-management integration, skill-creator, plugin-creator, 決める順番, 意思決定支援, 日次計画, 継続判断, 調査方針, 許容損失
```

Append to `knowledge/log.md`:

```markdown
## [2026-07-17] implementation | Decide In Order skill

- `skills/decide-in-order/` を skill-creator scaffoldから実装し、判断順序、light/deep/review、疎なDecisionFrame、適応的表示、DecisionRecord候補を分離した
- standalone contract tests 6件、fresh-agent forward test 8 scenarios、skill validatorを通過した
- task-managementへ思想を複製せず、動作別decision-support policyとcontract tests 6件を追加した
- task-management full suite 89件、skill/plugin validators、llm-wiki tests 6件、skill architecture、3 context contractsを検証した
- 新規plugin、marketplace、cachebuster、live install、backend call、外部writeは実施していない
```

- [ ] **Step 4: Re-run documentation checks**

Run:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
rg -n "T[B]D|\[T]ODO|PLACEHOLD[E]R" skills/decide-in-order plugins/task-management/skills/task-management knowledge/wiki/syntheses/decide-in-order-skill-design.md knowledge/index.md knowledge/log.md
git diff --check
git status --short
```

Expected: llm-wiki 6 tests pass; `rg` returns no placeholder matches; no whitespace errors; status lists only the intended documentation files before commit。

- [ ] **Step 5: Commit final documentation evidence**

```bash
git add knowledge/wiki/syntheses/decide-in-order-skill-design.md knowledge/index.md knowledge/log.md
git commit -m "Record decide-in-order implementation evidence"
```

- [ ] **Step 6: Verify the final checkout**

Run:

```bash
git status --short --branch
git log -6 --oneline
```

Expected: clean checkout; six commits are visible for design, implementation plan, standalone skill, forward test, integration, and final evidence。

## Related Documents

- [Decide In Order Skill 設計](decide-in-order-skill-design.md)
- [Decide In Order Skill 原案](../sources/2026-07-17-decide-in-order-source-brief.md)
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md)

## Sources

- [Decide In Order 原案](../../raw/sources/2026-07-17-decide-in-order-source-brief.md)
- `skill-creator:/Users/omitsuhashi/.codex/skills/.system/skill-creator/SKILL.md`
- `plugin-creator:/Users/omitsuhashi/.codex/skills/.system/plugin-creator/SKILL.md`
- `superpowers:writing-plans:/Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.1.1/skills/writing-plans/SKILL.md`
