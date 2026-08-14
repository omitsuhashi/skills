from __future__ import annotations

from pathlib import Path
import re
import subprocess
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
def load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def field_value(text: str, label: str) -> str:
    match = re.search(
        rf"^(?:- |\*\*){re.escape(label)}(?:\*\*)?:[ \t]*([^\r\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def resolve_repository_path(repository_root: Path, value: str) -> Path | None:
    candidate = (repository_root / value.strip().strip("`")).resolve()
    try:
        candidate.relative_to(repository_root.resolve())
    except ValueError:
        return None
    return candidate


def git_commit_is_current_ancestor(repository_root: Path, commit_sha: str) -> bool:
    if not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit_sha, "HEAD"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def repository_bound_plan_errors(text: str, repository_root: Path) -> list[str]:
    errors: list[str] = []
    north_star_identity = section(text, "Approved North Star Identity")
    spec_identity = section(text, "Approved Written Spec Identity")
    binding = section(text, "Plan Binding")

    north_star_sha = field_value(
        north_star_identity, "Approved snapshot SHA-256"
    )
    spec_sha = field_value(spec_identity, "Approved spec SHA-256")
    if not re.fullmatch(r"[0-9a-f]{64}", north_star_sha):
        errors.append("invalid North Star approval snapshot SHA-256")
    if not re.fullmatch(r"[0-9a-f]{64}", spec_sha):
        errors.append("invalid approved spec SHA-256")
    if field_value(north_star_identity, "Approval state") != "approved":
        errors.append("North Star is not in approved state")
    if field_value(spec_identity, "Approval state") != "approved":
        errors.append("approved spec is not in approved state")
    if north_star_sha != spec_sha:
        errors.append("North Star and Written Spec approval snapshots differ")

    north_star_path_value = field_value(
        north_star_identity, "Approved North Star path"
    )
    spec_path_value = field_value(spec_identity, "Approved spec path")
    north_star_path = resolve_repository_path(
        repository_root, north_star_path_value
    )
    spec_path = resolve_repository_path(repository_root, spec_path_value)
    if spec_path is None or not spec_path.is_file():
        errors.append("approved spec path is not a contained repository file")
        spec_text = ""
    else:
        spec_text = load(spec_path)
        if spec_sha != frontmatter_value(spec_text, "approval_snapshot_sha256"):
            errors.append(
                "approved spec SHA-256 does not match durable approval snapshot identity"
            )
        if frontmatter_value(spec_text, "status") not in {"accepted", "approved"}:
            errors.append("approved spec durable status is not accepted")
        if frontmatter_value(spec_text, "review_state") != "approved":
            errors.append("approved spec durable review state is not approved")

    if (
        north_star_path != spec_path
        or field_value(north_star_identity, "Approved North Star anchor")
        != "North Star"
    ):
        errors.append(
            "North Star identity does not resolve to the approved spec North Star"
        )
    if spec_text and not section(spec_text, "North Star").strip():
        errors.append("approved North Star anchor is absent")

    baseline_sha = field_value(binding, "Repository baseline")
    if not git_commit_is_current_ancestor(repository_root, baseline_sha):
        errors.append("repository baseline is not a current-tree ancestor commit")
    return errors


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
            repository_bound_plan_errors(
                self.canonical,
                repository_root=REPOSITORY_ROOT,
            ),
        )

    def test_repository_bound_contract_rejects_approval_and_git_drift(self) -> None:
        wrong_spec = self.canonical.replace(
            "- Approved spec path: knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md",
            "- Approved spec path: knowledge/wiki/syntheses/missing-approved-spec.md",
            1,
        )
        wrong_snapshot = self.canonical.replace(
            "- Approved spec SHA-256: 1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559",
            "- Approved spec SHA-256: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            1,
        )
        wrong_baseline = self.canonical.replace(
            "- Repository baseline: c370fe14de1641aa5ee30b3fa001f4d857078091",
            "- Repository baseline: 0000000000000000000000000000000000000000",
            1,
        )

        self.assertIn(
            "approved spec path is not a contained repository file",
            repository_bound_plan_errors(wrong_spec, REPOSITORY_ROOT),
        )
        self.assertIn(
            "approved spec SHA-256 does not match durable approval snapshot identity",
            repository_bound_plan_errors(wrong_snapshot, REPOSITORY_ROOT),
        )
        self.assertIn(
            "repository baseline is not a current-tree ancestor commit",
            repository_bound_plan_errors(wrong_baseline, REPOSITORY_ROOT),
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
