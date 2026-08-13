from __future__ import annotations

from pathlib import Path
import re
import shutil
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
PLAN_CONTRACT = SKILL_DIR / "references" / "plan-contract.md"
READY_PLAN = SKILL_DIR / "tests" / "fixtures" / "plan-contract" / "ready-plan.md"

REQUIREMENT_IDS = {f"R-{number:02d}" for number in range(1, 16)}
ACCEPTANCE_IDS = {f"AC-{number:02d}" for number in range(1, 15)}
TASK_IDS = ("POA-1", "POA-2", "POA-3")


def load_plan(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def table_rows(text: str) -> list[list[str]]:
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith("|") and not re.fullmatch(r"[| :\-]+", line)
    ]


def coverage_rows(text: str) -> list[list[str]]:
    return [row for row in table_rows(section(text, "Coverage Matrix")) if row[0] != "ID"]


def task_sections(text: str) -> dict[str, str]:
    matches = re.finditer(
        r"^### Task (POA-\d+):.*?$(.*?)(?=^### Task |^## |\Z)",
        section(text, "Tasks"),
        flags=re.MULTILINE | re.DOTALL,
    )
    return {match.group(1): match.group(2) for match in matches}


def plan_errors(text: str) -> list[str]:
    errors: list[str] = []
    spec_identity = section(text, "Approved Written Spec Identity")
    for field in (
        "- Approved spec path:",
        "- Approved spec SHA-256:",
        "- Approval state: approved",
    ):
        if field not in spec_identity:
            errors.append(f"missing approved-spec identity field: {field[2:]}")

    inventory = section(text, "Requirement And Acceptance Inventory")
    inventory_ids = set(re.findall(r"\b(?:R|AC)-\d{2}\b", inventory))
    for item_id in sorted(REQUIREMENT_IDS | ACCEPTANCE_IDS):
        if item_id not in inventory_ids:
            errors.append(f"inventory missing ID: {item_id}")
    for item_id in sorted(inventory_ids - (REQUIREMENT_IDS | ACCEPTANCE_IDS)):
        errors.append(f"inventory has unknown ID: {item_id}")

    coverage = coverage_rows(text)
    seen_coverage: set[str] = set()
    primary_owner: dict[str, str] = {}

    for row in coverage:
        if len(row) != 3:
            errors.append("coverage rows must contain ID, primary owner, and contributing tasks")
            continue
        item_id, primary, contributing = row
        if item_id not in REQUIREMENT_IDS | ACCEPTANCE_IDS:
            errors.append(f"unknown coverage ID: {item_id}")
        if item_id in seen_coverage:
            errors.append(f"duplicate coverage ID: {item_id}")
        seen_coverage.add(item_id)
        if primary not in TASK_IDS:
            errors.append(f"invalid primary owner for {item_id}: {primary}")
        else:
            primary_owner[item_id] = primary
        for task_id in filter(None, (value.strip() for value in contributing.split(","))):
            if task_id not in TASK_IDS:
                errors.append(f"unknown contributing task: {task_id}")

    for item_id in sorted(REQUIREMENT_IDS | ACCEPTANCE_IDS):
        if item_id not in primary_owner:
            errors.append(f"unassigned coverage ID: {item_id}")

    tasks = task_sections(text)
    for task_id in TASK_IDS:
        task = tasks.get(task_id)
        if task is None:
            errors.append(f"orphan task: {task_id}")
            continue
        for label in (
            "Deliverable",
            "Requirement coverage",
            "Acceptance coverage",
            "Dependencies",
            "Consumes",
            "Produces",
            "Verification intent",
            "Integration placement",
            "Failure owner",
        ):
            if not re.search(rf"^- {re.escape(label)}: .+", task, flags=re.MULTILINE):
                errors.append(f"missing {label} for {task_id}")
        for item_id, owner in primary_owner.items():
            if owner == task_id and item_id not in task:
                errors.append(f"primary owner {task_id} does not declare {item_id}")

    graph = {
        row[0]: row[1]
        for row in table_rows(section(text, "Dependency Graph"))
        if len(row) == 2 and row[0] != "Task"
    }
    if set(graph) != set(TASK_IDS):
        errors.append("dependency graph must define every task")
    dependencies: dict[str, list[str]] = {}
    for task_id, declared in graph.items():
        dependencies[task_id] = [] if declared == "none" else [value.strip() for value in declared.split(",")]
        for dependency in dependencies[task_id]:
            if dependency not in TASK_IDS:
                errors.append(f"undefined dependency: {task_id} -> {dependency}")

    execution = re.findall(r"^\d+\. (POA-\d+)$", section(text, "Execution Order"), flags=re.MULTILINE)
    if set(execution) != set(TASK_IDS) or len(execution) != len(TASK_IDS):
        errors.append("execution order must list every task exactly once")
    else:
        positions = {task_id: index for index, task_id in enumerate(execution)}
        for task_id, task_dependencies in dependencies.items():
            for dependency in task_dependencies:
                if dependency in positions and positions[dependency] >= positions[task_id]:
                    errors.append(f"execution-order violation: {dependency} must precede {task_id}")

    pending = dict(dependencies)
    resolved: set[str] = set()
    while pending:
        ready = [task_id for task_id, values in pending.items() if set(values) <= resolved]
        if not ready:
            errors.append("dependency cycle")
            break
        for task_id in ready:
            resolved.add(task_id)
            pending.pop(task_id)

    integration = section(text, "Serialized Integration")
    if not all(value in integration for value in ("I-1: POA-1", "I-2: POA-2", "I-3: POA-3")):
        errors.append("missing serialized integration order")
    if not all(value in integration for value in ("Preconditions", "Combined-state expectation")):
        errors.append("serialized integration lacks preconditions or combined-state expectation")

    verification = section(text, "Post-Integration Combined Verification")
    for label in ("Scope", "Pass criteria", "Required evidence", "Failure owner"):
        if not re.search(rf"^\*\*{re.escape(label)}:\*\* .+", verification, flags=re.MULTILINE):
            errors.append(f"combined verification missing {label}")
    for acceptance_id in sorted(ACCEPTANCE_IDS):
        if acceptance_id not in verification:
            errors.append(f"combined verification missing {acceptance_id}")

    readiness = section(text, "Readiness Result")
    for value in ("ready", "needs_repair", "needs_decision", "blocked", "issues_found"):
        if value not in readiness:
            errors.append(f"missing readiness vocabulary: {value}")
    if "status: complete" not in readiness or "Implementation Stage entry" not in readiness:
        errors.append("readiness mapping is incomplete")

    if "```" in text:
        errors.append("prospective body: fenced code block")
    if re.search(r"^\s*(?:\$ |git (?:add|commit)|python\d* |npm |uv )", text, flags=re.MULTILINE):
        errors.append("prospective body: command body")
    if re.search(r"Human (?:plan )?approval (?:is )?required", text, flags=re.IGNORECASE):
        errors.append("Human plan-approval language")

    return errors


class PlanContractTests(unittest.TestCase):
    def copy_ready_plan(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        self.assertTrue(
            READY_PLAN.is_file(),
            f"representative ready-plan fixture is missing: {READY_PLAN}",
        )
        temporary_directory = tempfile.TemporaryDirectory()
        copy = Path(temporary_directory.name) / "ready-plan.md"
        shutil.copyfile(READY_PLAN, copy)
        return temporary_directory, copy

    def test_overlay_declares_the_local_plan_contract_without_copying_upstream(self) -> None:
        self.assertTrue(
            PLAN_CONTRACT.is_file(),
            f"local plan-contract overlay is missing: {PLAN_CONTRACT}",
        )
        text = load_plan(PLAN_CONTRACT)
        for heading in (
            "## Inputs",
            "## Outputs",
            "## Required Capabilities",
            "## Required Plan-Level Fields",
            "## Required Task Fields",
            "## Coverage And Dependency Invariants",
            "## Execution, Integration, And Combined Verification",
            "## Prohibited Durable Plan Content",
            "## Review And Readiness Vocabulary",
        ):
            self.assertIn(heading, text)
        self.assertIn("superpowers:writing-plans", text)
        self.assertIn("do not copy, vendor, fork, or replace", text)
        self.assertIn("Plan Contract Overlay takes precedence", text)

    def test_representative_ready_plan_satisfies_the_complete_contract(self) -> None:
        self.assertTrue(
            READY_PLAN.is_file(),
            f"representative ready-plan fixture is missing: {READY_PLAN}",
        )
        self.assertEqual([], plan_errors(load_plan(READY_PLAN)))

    def test_rejects_missing_approved_spec_identity(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(
                load_plan(copy).replace(
                    "- Approval state: approved",
                    "- Approval state: pending",
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "missing approved-spec identity field: Approval state: approved",
                plan_errors(load_plan(copy)),
            )

    def test_rejects_an_incomplete_requirement_acceptance_inventory(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            inventory = section(load_plan(copy), "Requirement And Acceptance Inventory")
            self.assertIn("AC-14", inventory)
            copy.write_text(load_plan(copy).replace("AC-14", "omitted acceptance", 1), encoding="utf-8")
            self.assertIn("inventory missing ID: AC-14", plan_errors(load_plan(copy)))

    def test_rejects_an_unassigned_acceptance(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| AC-14 | POA-3 | POA-1, POA-2 |", ""), encoding="utf-8")
            self.assertIn("unassigned coverage ID: AC-14", plan_errors(load_plan(copy)))

    def test_rejects_an_unknown_coverage_id(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| AC-14 | POA-3 | POA-1, POA-2 |", "| AC-99 | POA-3 | POA-1, POA-2 |"), encoding="utf-8")
            self.assertIn("unknown coverage ID: AC-99", plan_errors(load_plan(copy)))

    def test_rejects_an_orphan_task(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("### Task POA-3:", "### Removed Task POA-3:"), encoding="utf-8")
            self.assertIn("orphan task: POA-3", plan_errors(load_plan(copy)))

    def test_rejects_an_undefined_dependency(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| POA-3 | POA-1, POA-2 |", "| POA-3 | POA-1, POA-9 |"), encoding="utf-8")
            self.assertIn("undefined dependency: POA-3 -> POA-9", plan_errors(load_plan(copy)))

    def test_rejects_a_dependency_cycle(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| POA-1 | none |", "| POA-1 | POA-3 |"), encoding="utf-8")
            self.assertIn("dependency cycle", plan_errors(load_plan(copy)))

    def test_rejects_an_execution_order_violation(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("1. POA-1\n2. POA-2\n3. POA-3", "1. POA-2\n2. POA-1\n3. POA-3"), encoding="utf-8")
            self.assertIn("execution-order violation: POA-1 must precede POA-2", plan_errors(load_plan(copy)))

    def test_rejects_missing_serialized_integration_or_combined_verification(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("I-3: POA-3", "I-3 omitted").replace("**Failure owner:**", "Failure owner:"), encoding="utf-8")
            errors = plan_errors(load_plan(copy))
            self.assertIn("missing serialized integration order", errors)
            self.assertIn("combined verification missing Failure owner", errors)

    def test_rejects_prospective_body_and_human_plan_approval_language(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy) + "\n```python\npass\n```\nHuman plan approval is required.\n", encoding="utf-8")
            errors = plan_errors(load_plan(copy))
            self.assertIn("prospective body: fenced code block", errors)
            self.assertIn("Human plan-approval language", errors)


if __name__ == "__main__":
    unittest.main()
