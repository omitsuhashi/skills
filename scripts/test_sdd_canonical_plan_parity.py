from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PLAN = (
    REPOSITORY_ROOT
    / "knowledge"
    / "wiki"
    / "syntheses"
    / "sdd-plan-ownership-alignment-implementation-plan.md"
)
ROOT_FIXTURE = (
    REPOSITORY_ROOT
    / "scripts"
    / "fixtures"
    / "sdd-plan-contract"
    / "ready-plan.md"
)
PACKAGE_TESTS = REPOSITORY_ROOT / "skills" / "sdd-implementation" / "tests"
sys.path.insert(0, str(PACKAGE_TESTS))

from test_plan_contract import plan_errors as package_plan_errors  # noqa: E402


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def table_rows(text: str) -> list[tuple[str, ...]]:
    return [
        tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        for line in text.splitlines()
        if line.startswith("|") and not re.fullmatch(r"[| :\-]+", line)
    ]


def inventory_ids(text: str) -> tuple[str, ...]:
    return tuple(
        re.findall(
            r"\b(?:R|AC)-\d{2}\b",
            section(text, "Requirement And Acceptance Inventory"),
        )
    )


def coverage_rows(text: str) -> tuple[tuple[str, ...], ...]:
    return tuple(
        row[:3]
        for row in table_rows(section(text, "Coverage Matrix"))
        if row[0] != "ID" and len(row) >= 3
    )


def task_ids(text: str) -> tuple[str, ...]:
    return tuple(
        re.findall(
            r"^### Task (?:\d+: )?(POA-\d+)(?::|\s+—)",
            section(text, "Tasks"),
            flags=re.MULTILINE,
        )
    )


def dependency_rows(text: str) -> tuple[tuple[str, ...], ...]:
    return tuple(
        row[:2]
        for row in table_rows(section(text, "Dependency Graph"))
        if row[0] != "Task" and len(row) >= 2
    )


def execution_order(text: str) -> tuple[str, ...]:
    return tuple(
        re.findall(
            r"^\d+\. (?:Execute )?(POA-\d+)(?!\d)",
            section(text, "Execution Order"),
            flags=re.MULTILINE,
        )
    )


def integration_order(text: str) -> tuple[tuple[str, str], ...]:
    return tuple(
        re.findall(
            r"I-(\d+): (POA-\d+)",
            section(text, "Serialized Integration"),
        )
    )


class CanonicalPlanParityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(CANONICAL_PLAN.is_file(), f"canonical plan is missing: {CANONICAL_PLAN}")
        self.assertTrue(ROOT_FIXTURE.is_file(), f"root parity fixture is missing: {ROOT_FIXTURE}")
        self.canonical = load(CANONICAL_PLAN)
        self.fixture = load(ROOT_FIXTURE)

    def test_canonical_plan_satisfies_the_repository_bound_contract(self) -> None:
        self.assertEqual(
            [],
            package_plan_errors(
                self.canonical,
                validation_scope="repository",
                repository_root=REPOSITORY_ROOT,
            ),
        )

    def test_inventory_and_complete_coverage_are_identical(self) -> None:
        canonical_inventory = inventory_ids(self.canonical)
        fixture_inventory = inventory_ids(self.fixture)
        self.assertEqual(canonical_inventory, fixture_inventory)
        self.assertEqual(len(canonical_inventory), len(set(canonical_inventory)))

        canonical_coverage = coverage_rows(self.canonical)
        fixture_coverage = coverage_rows(self.fixture)
        self.assertEqual(canonical_coverage, fixture_coverage)
        self.assertEqual(
            set(canonical_inventory),
            {row[0] for row in fixture_coverage},
        )
        self.assertEqual(len(fixture_coverage), len({row[0] for row in fixture_coverage}))

    def test_task_graph_execution_and_integration_order_are_identical_and_valid(self) -> None:
        canonical_tasks = task_ids(self.canonical)
        fixture_tasks = task_ids(self.fixture)
        self.assertEqual(canonical_tasks, fixture_tasks)
        self.assertEqual(len(fixture_tasks), len(set(fixture_tasks)))

        canonical_graph = dependency_rows(self.canonical)
        fixture_graph = dependency_rows(self.fixture)
        self.assertEqual(canonical_graph, fixture_graph)
        self.assertEqual(set(fixture_tasks), {row[0] for row in fixture_graph})

        canonical_execution = execution_order(self.canonical)
        fixture_execution = execution_order(self.fixture)
        self.assertEqual(canonical_execution, fixture_execution)
        self.assertEqual(set(fixture_tasks), set(fixture_execution))
        positions = {task_id: index for index, task_id in enumerate(fixture_execution)}
        for task_id, declared in fixture_graph:
            dependencies = () if declared == "none" else tuple(
                value.strip() for value in declared.split(",")
            )
            for dependency in dependencies:
                self.assertIn(dependency, positions)
                self.assertLess(positions[dependency], positions[task_id])

        canonical_integration = integration_order(self.canonical)
        fixture_integration = integration_order(self.fixture)
        self.assertEqual(canonical_integration, fixture_integration)
        self.assertEqual(
            fixture_tasks,
            tuple(task_id for _, task_id in fixture_integration),
        )


if __name__ == "__main__":
    unittest.main()
