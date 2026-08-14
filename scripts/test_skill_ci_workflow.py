from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-architecture.yml"
LEGACY_GRILL_SKILL = "-".join(("grill", "to", "pr", "loop"))
LEGACY_ISSUE_SKILL = "-".join(("issue", "implementation", "loop"))
TASK_MANAGEMENT_TEST = (
    REPO_ROOT
    / "skills"
    / "task-management"
    / "tests"
    / "test_task_management_contract.py"
)
CANONICAL_PLAN = (
    REPO_ROOT
    / "knowledge"
    / "wiki"
    / "syntheses"
    / "sdd-portable-validation-simplification-implementation-plan.md"
)
APPROVED_SPEC = (
    REPO_ROOT
    / "knowledge"
    / "wiki"
    / "syntheses"
    / "sdd-portable-validation-simplification.md"
)
ROOT_FIXTURE = REPO_ROOT / "scripts" / "fixtures" / "sdd-plan-contract" / "ready-plan.md"
ROOT_PARITY_RUNNER = REPO_ROOT / "scripts" / "test_sdd_canonical_plan_parity.py"

sys.path.insert(0, str(REPO_ROOT / "skills" / "sdd-implementation" / "tests"))
from test_plan_contract import plan_errors  # noqa: E402


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


def canonical_plan_identity_errors(text: str) -> list[str]:
    errors: list[str] = []
    north_star_identity = section(text, "Approved North Star Identity")
    spec_identity = section(text, "Approved Written Spec Identity")
    binding = section(text, "Plan Binding")
    expected_path = "knowledge/wiki/syntheses/sdd-portable-validation-simplification.md"
    expected_digest = sha256(APPROVED_SPEC.read_bytes()).hexdigest()

    if field_value(north_star_identity, "Approved North Star path") != expected_path:
        errors.append("approved North Star path does not identify the approved spec")
    if field_value(spec_identity, "Approved spec path") != expected_path:
        errors.append("approved spec path does not identify the approved spec")
    if field_value(north_star_identity, "Approved North Star anchor") != "目標":
        errors.append("approved North Star anchor is absent")
    if field_value(north_star_identity, "Approved snapshot SHA-256") != expected_digest:
        errors.append("approved North Star digest does not match current approved spec bytes")
    if field_value(spec_identity, "Approved spec SHA-256") != expected_digest:
        errors.append("approved spec digest does not match current approved spec bytes")
    if field_value(north_star_identity, "Approval state") != "approved":
        errors.append("North Star is not in approved state")
    if field_value(spec_identity, "Approval state") != "approved":
        errors.append("approved spec is not in approved state")
    if not re.search(r"^status:\s*(?:accepted|approved)\s*$", APPROVED_SPEC.read_text(encoding="utf-8"), re.MULTILINE):
        errors.append("approved spec durable status is not accepted")
    if not re.search(r"^review_state:\s*approved\s*$", APPROVED_SPEC.read_text(encoding="utf-8"), re.MULTILINE):
        errors.append("approved spec durable review state is not approved")
    if not section(APPROVED_SPEC.read_text(encoding="utf-8"), "目標").strip():
        errors.append("approved North Star anchor is absent")

    baseline_sha = field_value(binding, "Repository baseline")
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline_sha, "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        errors.append("repository baseline is not a current-tree ancestor commit")
    return errors


def run_git(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def transient_validation_step() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"^      - name: Validate SDD transient artifacts\n"
        r"(?P<body>.*?)(?=^      - name: |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError("transient validation workflow step is missing")
    lines = match.group("body").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("        run: "):
            value = line.removeprefix("        run: ")
            if value != "|":
                return value
            command_lines = []
            for command_line in lines[index + 1 :]:
                if not command_line:
                    command_lines.append("")
                    continue
                if not command_line.startswith("          "):
                    break
                command_lines.append(command_line[10:])
            return "\n".join(command_lines)
    raise AssertionError("transient validation workflow command is missing")


def clone_reachable_repository(destination: Path, *, depth: int | None = None) -> None:
    command = ["git", "clone", "--quiet", "--no-local"]
    if depth is not None:
        command.extend(("--depth", str(depth)))
    command.extend((REPO_ROOT.as_uri(), str(destination)))
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_ci_validation(repository: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", transient_validation_step()],
        cwd=repository,
        check=False,
        capture_output=True,
        text=True,
    )


class SkillCiWorkflowTests(unittest.TestCase):
    def test_python_matrix_runs_standalone_skill_contracts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('python-version:\n          - "3.9"\n          - "3.12"', text)
        self.assertIn("Run decide-in-order tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/decide-in-order/tests", text
        )
        self.assertIn("Run task-management tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/task-management/tests", text
        )
        self.assertIn("Run sdd-implementation tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/sdd-implementation/tests",
            text,
        )
        self.assertNotIn(f"Run {LEGACY_GRILL_SKILL} tests", text)
        self.assertNotIn(f"Run {LEGACY_ISSUE_SKILL} tests", text)
        self.assertNotIn("plugins/task-management", text)

    def test_task_management_contract_is_host_neutral(self) -> None:
        text = TASK_MANAGEMENT_TEST.read_text(encoding="utf-8")
        self.assertIn("test_skill_has_no_host_specific_or_runtime_surface", text)
        self.assertIn("test_capability_and_partial_failures_are_fail_closed", text)

    def test_workflow_omits_repository_compatibility_entrypoints(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test skill authoring guidance", text)
        self.assertIn("scripts/test_skill_authoring_guidance.py", text)
        self.assertIn("Test skill CI workflow contract", text)
        self.assertIn("scripts/test_skill_ci_workflow.py", text)
        self.assertNotIn("Test repository compatibility validator", text)
        self.assertNotIn("scripts/test_validate_repository_compatibility.py", text)
        self.assertNotIn("Validate repository compatibility", text)
        self.assertNotIn("scripts/validate_repository_compatibility.py", text)

    def test_workflow_runs_transient_artifact_regression_and_validation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Test SDD transient artifact validator", text)
        self.assertIn("python3 scripts/test_validate_sdd_transient_artifacts.py", text)
        self.assertIn("Validate SDD transient artifacts", text)
        self.assertIn("python3 scripts/validate_sdd_transient_artifacts.py", text)
        self.assertIn("--post-policy-history", text)
        self.assertNotIn("--post-cleanup-history", text)
        self.assertNotIn("--migration-baseline", text)

    def test_workflow_omits_root_parity_runner_and_keeps_isolated_package_closure(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("Test SDD canonical plan parity", text)
        self.assertNotIn("scripts/test_sdd_canonical_plan_parity.py", text)
        self.assertFalse(ROOT_FIXTURE.exists())
        self.assertFalse(ROOT_PARITY_RUNNER.exists())
        self.assertIn(
            "      - name: Test isolated SDD package closure\n"
            "        run: PYTHONPYCACHEPREFIX=/tmp/skills-pycache "
            "python3 skills/sdd-implementation/tests/test_isolated_install.py",
            text,
        )

    def test_canonical_plan_directly_passes_root_identity_and_current_amendment_semantics(self) -> None:
        canonical = CANONICAL_PLAN.read_text(encoding="utf-8")
        self.assertEqual([], canonical_plan_identity_errors(canonical))
        current_amendment = canonical.split(
            "## Current Fixture-Minimization Amendment\n", 1
        )[1]
        semantic_text = "\n".join(
            (
                "## Approved North Star Identity\n" + section(canonical, "Approved North Star Identity"),
                "## Approved Written Spec Identity\n" + section(canonical, "Approved Written Spec Identity"),
                "## Plan Binding\n" + section(canonical, "Plan Binding"),
                "## Current Fixture-Minimization Amendment\n" + current_amendment,
            )
        )
        self.assertEqual(
            [],
            plan_errors(
                semantic_text,
                requirement_ids=tuple(f"R-{number:02d}" for number in range(1, 16)),
                acceptance_ids=tuple(f"AC-{number:02d}" for number in range(1, 18)),
                task_ids=("AM-1", "AM-2"),
                integration_ids=("AM-1", "AM-2"),
                north_star_anchor="目標",
                external_dependencies=(
                    "content edit前のexact-identity `ours` no-ff merge prerequisite",
                ),
            ),
        )

    def test_canonical_plan_direct_check_rejects_path_digest_and_baseline_mutations(self) -> None:
        canonical = CANONICAL_PLAN.read_text(encoding="utf-8")
        wrong_path = canonical.replace(
            "- Approved spec path: knowledge/wiki/syntheses/sdd-portable-validation-simplification.md",
            "- Approved spec path: knowledge/wiki/syntheses/missing-approved-spec.md",
            1,
        )
        wrong_digest = canonical.replace(
            sha256(APPROVED_SPEC.read_bytes()).hexdigest(),
            "f" * 64,
            1,
        )
        wrong_baseline = canonical.replace(
            "- Repository baseline: 4d67bed6d297ba4e9a0f44559d3ca45c9a035976",
            "- Repository baseline: " + "0" * 40,
            1,
        )
        self.assertIn(
            "approved spec path does not identify the approved spec",
            canonical_plan_identity_errors(wrong_path),
        )
        self.assertIn(
            "approved North Star digest does not match current approved spec bytes",
            canonical_plan_identity_errors(wrong_digest),
        )
        self.assertIn(
            "repository baseline is not a current-tree ancestor commit",
            canonical_plan_identity_errors(wrong_baseline),
        )

    def test_historical_plan_block_cannot_satisfy_current_amendment_semantics(self) -> None:
        historical = CANONICAL_PLAN.read_text(encoding="utf-8").split(
            "## Current Fixture-Minimization Amendment\n", 1
        )[0]
        errors = plan_errors(
            historical,
            requirement_ids=tuple(f"R-{number:02d}" for number in range(1, 16)),
            acceptance_ids=tuple(f"AC-{number:02d}" for number in range(1, 18)),
            task_ids=("AM-1", "AM-2"),
            integration_ids=("AM-1", "AM-2"),
            north_star_anchor="目標",
            external_dependencies=(
                "content edit前のexact-identity `ours` no-ff merge prerequisite",
            ),
        )
        self.assertIn("inventory missing ID: R-01", errors)

    def test_transient_validation_step_accepts_reachable_only_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)

            result = run_ci_validation(repository)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_transient_validation_does_not_require_origin_main(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)
            run_git(repository, "update-ref", "-d", "refs/remotes/origin/main")
            with self.assertRaises(subprocess.CalledProcessError):
                run_git(repository, "rev-parse", "--verify", "refs/remotes/origin/main")

            result = run_ci_validation(repository)

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_transient_validation_rejects_post_policy_add_then_delete(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository)
            run_git(repository, "config", "user.name", "Test User")
            run_git(repository, "config", "user.email", "test@example.invalid")
            transient = repository / ".superpowers" / "smuggled.md"
            transient.parent.mkdir(parents=True, exist_ok=True)
            transient.write_text("must be rejected\n", encoding="utf-8")
            run_git(repository, "add", "-f", ".superpowers/smuggled.md")
            run_git(repository, "commit", "-m", "add forbidden transient artifact")
            added = run_git(repository, "rev-parse", "HEAD").strip()
            run_git(repository, "rm", ".superpowers/smuggled.md")
            run_git(repository, "commit", "-m", "delete forbidden transient artifact")
            self.assertTrue(
                run_git(repository, "ls-tree", "-r", added, "--", ".superpowers").strip()
            )

            result = run_ci_validation(repository)

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("category=new_commit_entry", result.stdout + result.stderr)

    def test_transient_validation_rejects_shallow_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory) / "repository"
            clone_reachable_repository(repository, depth=1)
            self.assertEqual(
                "true",
                run_git(repository, "rev-parse", "--is-shallow-repository").strip(),
            )

            result = run_ci_validation(repository)

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("category=history_unavailable", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
