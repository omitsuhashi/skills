from __future__ import annotations

import ast
from pathlib import Path
import re
import shutil
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
PLAN_CONTRACT = SKILL_DIR / "references" / "plan-contract.md"
READY_PLAN = SKILL_DIR / "tests" / "fixtures" / "plan-contract" / "ready-plan.md"

REQUIREMENT_IDS = {f"R-{number:02d}" for number in range(1, 22)}
ACCEPTANCE_IDS = {f"AC-{number:02d}" for number in range(1, 21)}
TASK_IDS = tuple(f"POA-{number}" for number in range(1, 9))


def load_plan(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def sections(text: str, heading: str) -> list[str]:
    return [
        match.group(1)
        for match in re.finditer(
            rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    ]


def singleton_section(errors: list[str], text: str, heading: str) -> str:
    matches = sections(text, heading)
    if len(matches) != 1:
        errors.append(f"duplicate section: {heading}")
    return "\n".join(matches)


def table_rows(text: str) -> list[list[str]]:
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith("|") and not re.fullmatch(r"[| :\-]+", line)
    ]


def coverage_rows(text: str) -> list[list[str]]:
    return [row for row in table_rows(section(text, "Coverage Matrix")) if row[0] != "ID"]


def task_sections(text: str, task_ids: tuple[str, ...] = TASK_IDS) -> dict[str, str]:
    task_id_pattern = "|".join(re.escape(task_id) for task_id in task_ids)
    matches = re.finditer(
        rf"^### Task (?:\d+: )?({task_id_pattern})(?::|\s+—).*?$(.*?)(?=^### Task |^## |\Z)",
        section(text, "Tasks"),
        flags=re.MULTILINE | re.DOTALL,
    )
    return {match.group(1): match.group(2) for match in matches}


def field_value(text: str, label: str) -> str:
    match = re.search(
        rf"^[ \t]*(?:- (?:\[[ xX]\] )?)?(?:\*\*)?{re.escape(label)}(?:\*\*)?:[ \t]*([^\r\n]+)$",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def field_values(text: str, label: str) -> list[str]:
    return [
        value.strip()
        for value in re.findall(
            rf"^[ \t]*(?:- (?:\[[ xX]\] )?)?(?:\*\*)?{re.escape(label)}(?:\*\*)?:[ \t]*([^\r\n]+)$",
            text,
            flags=re.MULTILINE,
        )
    ]


def contains_parsed_python_function(text: str) -> bool:
    lines = text.splitlines()
    function_start = re.compile(
        r"^(?P<indent>[ \t]*)(?:async[ \t]+)?def\b"
    )
    for index, line in enumerate(lines):
        start = function_start.match(line)
        if start is None:
            continue
        base_indent = start.group("indent")
        for end in range(index + 1, len(lines) + 1):
            candidate = [
                candidate_line[len(base_indent) :]
                if candidate_line.startswith(base_indent)
                else candidate_line
                for candidate_line in lines[index:end]
            ]
            try:
                parsed = ast.parse("\n".join(candidate))
            except SyntaxError:
                continue
            if parsed.body and isinstance(
                parsed.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                return True
    return False


def contains_unfenced_production_body(text: str) -> bool:
    if contains_parsed_python_function(text):
        return True
    javascript_body = re.search(
        r"^(?P<indent>[ \t]*)(?:(?:export|async)[ \t]+)*"
        r"(?:function[ \t]+[A-Za-z_$][\w$]*[ \t]*\([^\n]*\)|"
        r"(?:const|let|var)[ \t]+[A-Za-z_$][\w$]*[ \t]*=[ \t]*"
        r"(?:async[ \t]+)?(?:\([^\n]*\)|[A-Za-z_$][\w$]*))[ \t]*"
        r"(?:=>[ \t]*)?\{[ \t]*\n(?P=indent)[ \t]+"
        r"(?:return|throw|const|let|var|if|for|while|switch|await|"
        r"[A-Za-z_$][\w.$]*[ \t]*\()",
        text,
        flags=re.MULTILINE,
    )
    javascript_inline_body = re.search(
        r"^[ \t]*(?:(?:export|async)[ \t]+)*(?:const|let|var)[ \t]+"
        r"[A-Za-z_$][\w$]*[ \t]*=[ \t]*(?:async[ \t]+)?"
        r"(?:\([^\n]*\)|[A-Za-z_$][\w$]*)[ \t]*=>[ \t]*"
        r"(?:await[ \t]+|new[ \t]+|[A-Za-z_$][\w.$]*[ \t]*\()",
        text,
        flags=re.MULTILINE,
    )
    javascript_function_inline_body = re.search(
        r"^[ \t]*(?:(?:export|async)[ \t]+)*function[ \t]+"
        r"[A-Za-z_$][\w$]*[ \t]*\([^\n]*\)[ \t]*\{[ \t]*"
        r"(?:return\b|throw\b|const\b|let\b|var\b|if\b|for\b|while\b|"
        r"switch\b|await\b|[A-Za-z_$][\w.$]*[ \t]*\()[^\n]*\}[ \t]*;?[ \t]*$",
        text,
        flags=re.MULTILINE,
    )
    return any(
        match is not None
        for match in (
            javascript_body,
            javascript_inline_body,
            javascript_function_inline_body,
        )
    )


def reject_duplicate_fields(
    errors: list[str], text: str, labels: tuple[str, ...], scope: str
) -> None:
    for label in labels:
        if len(field_values(text, label)) != 1:
            errors.append(f"duplicate {scope} field: {label}")


def plan_errors(
    text: str,
    *,
    requirement_ids: tuple[str, ...] = tuple(sorted(REQUIREMENT_IDS)),
    acceptance_ids: tuple[str, ...] = tuple(sorted(ACCEPTANCE_IDS)),
    task_ids: tuple[str, ...] = TASK_IDS,
    integration_ids: tuple[str, ...] | None = None,
    north_star_anchor: str = "North Star",
    external_dependencies: tuple[str, ...] = (),
) -> list[str]:
    errors: list[str] = []
    expected_requirement_ids = set(requirement_ids)
    expected_acceptance_ids = set(acceptance_ids)
    expected_ids = expected_requirement_ids | expected_acceptance_ids
    expected_integration_ids = (
        integration_ids
        if integration_ids is not None
        else tuple(str(number) for number in range(1, len(task_ids) + 1))
    )
    north_star_identity = singleton_section(
        errors, text, "Approved North Star Identity"
    )
    spec_identity = singleton_section(errors, text, "Approved Written Spec Identity")
    binding = singleton_section(errors, text, "Plan Binding")

    reject_duplicate_fields(
        errors,
        north_star_identity,
        (
            "Approved North Star path",
            "Approved North Star anchor",
            "Approved snapshot SHA-256",
            "Approval state",
        ),
        "North Star identity",
    )
    reject_duplicate_fields(
        errors,
        spec_identity,
        ("Approved spec path", "Approved spec SHA-256", "Approval state"),
        "approved-spec identity",
    )

    for field in (
        "Approved North Star path",
        "Approved North Star anchor",
        "Approved snapshot SHA-256",
        "Approval state",
    ):
        if not field_value(north_star_identity, field):
            errors.append(f"missing North Star identity field: {field}")

    north_star_sha = field_value(north_star_identity, "Approved snapshot SHA-256")
    if north_star_sha and not re.fullmatch(r"[0-9a-f]{64}", north_star_sha):
        errors.append("invalid North Star approval snapshot SHA-256")

    for field in ("Approved spec path", "Approved spec SHA-256", "Approval state"):
        if not field_value(spec_identity, field):
            errors.append(f"missing approved-spec identity field: {field}")

    spec_sha = field_value(spec_identity, "Approved spec SHA-256")
    if spec_sha and not re.fullmatch(r"[0-9a-f]{64}", spec_sha):
        errors.append("invalid approved spec SHA-256")

    if field_value(spec_identity, "Approval state") != "approved":
        errors.append("approved spec is not in approved state")
    if field_value(north_star_identity, "Approval state") != "approved":
        errors.append("North Star is not in approved state")

    spec_path_value = field_value(spec_identity, "Approved spec path")
    north_star_path_value = field_value(north_star_identity, "Approved North Star path")
    spec_path = Path(spec_path_value.strip().strip("`"))
    north_star_path = Path(north_star_path_value.strip().strip("`"))
    for label, candidate in (
        ("approved spec", spec_path),
        ("approved North Star", north_star_path),
    ):
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"{label} path is not repository-relative and portable")

    if north_star_path != spec_path or field_value(north_star_identity, "Approved North Star anchor") != north_star_anchor:
        errors.append("North Star identity does not resolve to the approved spec North Star")
    if north_star_sha != spec_sha:
        errors.append("North Star and Written Spec approval snapshots differ")

    baseline_sha = field_value(binding, "Repository baseline")
    binding_fields = (
        "Repository baseline",
        "Planning worktree",
        "Integration branch",
        "Current-tree compatibility",
        "Independent review verdict",
        "Repository checks",
        "Readiness evidence state",
    )
    reject_duplicate_fields(errors, binding, binding_fields, "plan binding")
    for field in binding_fields:
        if not field_value(binding, field):
            errors.append(f"missing plan binding field: {field}")
    if baseline_sha and not re.fullmatch(r"[0-9a-f]{40}", baseline_sha):
        errors.append("repository baseline is not a full commit identity")
    if field_value(binding, "Current-tree compatibility") != "compatible":
        errors.append("current-tree compatibility is not compatible")
    if field_value(binding, "Independent review verdict") != "ready":
        errors.append("independent review verdict is not ready")
    if field_value(binding, "Repository checks") != "passed":
        errors.append("repository checks did not pass")
    if field_value(binding, "Readiness evidence state") != "current":
        errors.append("readiness evidence is not current")

    global_constraints = section(text, "Global Constraints")
    if len(re.findall(r"^- ", global_constraints, flags=re.MULTILINE)) < 3:
        errors.append("global constraints are incomplete")

    inventory = section(text, "Requirement And Acceptance Inventory")
    inventory_ids = set(re.findall(r"\b(?:R|AC)-\d{2}\b", inventory))
    for item_id in sorted(expected_ids):
        if item_id not in inventory_ids:
            errors.append(f"inventory missing ID: {item_id}")
    for item_id in sorted(inventory_ids - expected_ids):
        errors.append(f"inventory has unknown ID: {item_id}")

    coverage = coverage_rows(text)
    seen_coverage: set[str] = set()
    primary_owner: dict[str, str] = {}

    for row in coverage:
        if len(row) < 3:
            errors.append("coverage rows must contain ID, primary owner, and contributing tasks")
            continue
        item_id, primary, contributing = row[:3]
        if item_id not in expected_ids:
            errors.append(f"unknown coverage ID: {item_id}")
        if item_id in seen_coverage:
            errors.append(f"duplicate coverage ID: {item_id}")
        seen_coverage.add(item_id)
        if primary not in task_ids:
            errors.append(f"invalid primary owner for {item_id}: {primary}")
        else:
            primary_owner[item_id] = primary
        for task_id in filter(None, (value.strip() for value in contributing.split(","))):
            if task_id not in task_ids:
                errors.append(f"unknown contributing task: {task_id}")

    for item_id in sorted(expected_ids):
        if item_id not in primary_owner:
            errors.append(f"unassigned coverage ID: {item_id}")

    tasks = task_sections(text, task_ids)
    if set(tasks) != set(task_ids):
        errors.append("task inventory must define the expected tasks exactly once")
    for task_id in task_ids:
        task = tasks.get(task_id)
        if task is None:
            errors.append(f"orphan task: {task_id}")
            continue
        for label in ("Deliverable", "Requirement coverage", "Acceptance coverage", "Dependencies", "Integration placement", "Failure owner"):
            if not field_value(task, label):
                errors.append(f"missing {label} for {task_id}")
        behavioral_interface = re.search(
            r"^(?:- (?:\[[ xX]\] )?)?\*\*Behavioral interface:\*\*\s*$(.*?)(?=^(?:- (?:\[[ xX]\] )?)?\*\*|^#### |\Z)",
            task,
            flags=re.MULTILINE | re.DOTALL,
        )
        if not behavioral_interface or not all(field_value(behavioral_interface.group(1), label) for label in ("Consumes", "Produces")):
            errors.append(f"missing observable Behavioral interface for {task_id}")
        if not re.search(
            r"^(?:- (?:\[[ xX]\] )?)?(?:\*\*|#### )Verification intent",
            task,
            flags=re.MULTILINE,
        ):
            errors.append(f"missing Verification intent for {task_id}")
        for item_id, owner in primary_owner.items():
            if owner == task_id and item_id not in task:
                errors.append(f"primary owner {task_id} does not declare {item_id}")

    graph = {
        row[0]: row[1]
        for row in table_rows(section(text, "Dependency Graph"))
        if len(row) >= 2 and row[0] != "Task"
    }
    if set(graph) != set(task_ids):
        errors.append("dependency graph must define every task")
    dependencies: dict[str, list[str]] = {}
    for task_id, declared in graph.items():
        dependencies[task_id] = [] if declared == "none" else [value.strip() for value in declared.split(",")]
        for dependency in dependencies[task_id]:
            if dependency not in task_ids and dependency not in external_dependencies:
                errors.append(f"undefined dependency: {task_id} -> {dependency}")

    execution = re.findall(
        rf"^\d+\. (?:Execute )?({'|'.join(re.escape(task_id) for task_id in task_ids)})(?!\d)",
        section(text, "Execution Order"),
        flags=re.MULTILINE,
    )
    if set(execution) != set(task_ids) or len(execution) != len(task_ids):
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
        ready = [
            task_id
            for task_id, values in pending.items()
            if set(values) - set(external_dependencies) <= resolved
        ]
        if not ready:
            errors.append("dependency cycle")
            break
        for task_id in ready:
            resolved.add(task_id)
            pending.pop(task_id)

    integration = section(text, "Serialized Integration")
    if len(expected_integration_ids) != len(task_ids) or not all(
        re.search(
            rf"(?:I-{re.escape(integration_id)}:\s*{re.escape(task_id)}|"
            rf"\|\s*I-{re.escape(integration_id)}\s*\|\s*{re.escape(task_id)}\s*\|)",
            integration,
        )
        for integration_id, task_id in zip(expected_integration_ids, task_ids)
    ):
        errors.append("missing serialized integration order")
    if not all(value in integration for value in ("Preconditions", "Combined-state expectation")):
        errors.append("serialized integration lacks preconditions or combined-state expectation")

    verification = section(text, "Post-Integration Combined Verification")
    for label in ("Scope", "Pass criteria", "Required evidence", "Failure owner"):
        if not re.search(rf"^\*\*{re.escape(label)}:\*\* .+", verification, flags=re.MULTILINE):
            errors.append(f"combined verification missing {label}")
    verification_acceptance_ids = set(re.findall(r"\bAC-\d{2}\b", verification))
    for start, end in re.findall(
        r"\b(AC-\d{2})\s+through\s+(AC-\d{2})\b", verification
    ):
        start_number = int(start.removeprefix("AC-"))
        end_number = int(end.removeprefix("AC-"))
        if start_number <= end_number:
            verification_acceptance_ids.update(
                f"AC-{number:02d}" for number in range(start_number, end_number + 1)
            )
    for acceptance_id in sorted(expected_acceptance_ids):
        if acceptance_id not in verification_acceptance_ids:
            errors.append(f"combined verification missing {acceptance_id}")

    readiness = singleton_section(errors, text, "Readiness Result")
    reject_duplicate_fields(
        errors,
        readiness,
        (
            "Plan readiness disposition",
            "Control Return status",
            "Implementation Stage entry",
        ),
        "readiness",
    )
    for value in ("ready", "needs_repair", "needs_decision", "blocked", "issues_found"):
        if value not in readiness:
            errors.append(f"missing readiness vocabulary: {value}")
    if "status: complete" not in readiness or "Implementation Stage entry" not in readiness:
        errors.append("readiness mapping is incomplete")
    if field_value(readiness, "Plan readiness disposition") != "ready":
        errors.append("plan readiness disposition is not ready")
    if field_value(readiness, "Control Return status") != "complete":
        errors.append("Control Return status is not complete")
    if field_value(readiness, "Implementation Stage entry") != "allowed":
        errors.append("Implementation Stage entry is not allowed")

    if "```" in text:
        errors.append("prospective body: fenced code block")
    if contains_unfenced_production_body(text):
        errors.append("prospective body: production code")
    if re.search(r"^\s*(?:def test_|async def test_|assert\s+|(?:describe|it|test)\s*\(|class Test\w+)", text, flags=re.MULTILINE):
        errors.append("prospective body: test body")
    if re.search(r"^\s*(?:for\s+\w+\s+in\s+.+;\s*do\b|while\s+.+;\s*do\b)", text, flags=re.MULTILINE):
        errors.append("prospective body: shell loop")
    if re.search(
        r"^[ \t]*if\b[^\n]*;[ \t]*then[ \t]*\n"
        r"(?:(?![ \t]*fi[ \t]*$)[^\n]+\n)+[ \t]*fi[ \t]*$",
        text,
        flags=re.MULTILINE,
    ):
        errors.append("prospective body: shell body")
    if re.search(
        r"^[ \t]*if\b[^\n]*;[ \t]*then\b[ \t]+\S[^\n]*;[ \t]*fi[ \t]*$",
        text,
        flags=re.MULTILINE,
    ):
        errors.append("prospective body: shell body")
    if re.search(r"^\s*(?:\*\*\* Begin Patch|\*\*\* Update File:|diff --git\s|@@\s+-\d|--- a/|\+\+\+ b/)", text, flags=re.MULTILINE):
        errors.append("prospective body: patch body")
    if re.search(
        r"^\s*(?:\$ |git (?:add|commit)\b|python\d*\s+-m\s+unittest\b|"
        r"(?:python\d*\s+-m\s+)?pytest\b|uv\s+run\s+pytest\b|"
        r"npm\s+(?:test|run)\b|echo[ \t]+(?!(?:is|was|means)\b)\S+)",
        text,
        flags=re.MULTILINE,
    ):
        errors.append("prospective body: command body")
    if re.search(r"Human (?:plan )?approval (?:is )?required", text, flags=re.IGNORECASE):
        errors.append("Human plan-approval language")

    return errors


def fixture_plan_errors(text: str) -> list[str]:
    return plan_errors(text)


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
        self.assertEqual([], fixture_plan_errors(load_plan(READY_PLAN)))

    def test_package_plan_validator_is_semantic_only(self) -> None:
        self.assertEqual([], plan_errors(load_plan(READY_PLAN)))

    def test_representative_fixture_covers_the_complete_semantic_inventory(self) -> None:
        fixture = load_plan(READY_PLAN)
        self.assertEqual(REQUIREMENT_IDS | ACCEPTANCE_IDS, set(re.findall(r"\b(?:R|AC)-\d{2}\b", section(fixture, "Requirement And Acceptance Inventory"))))
        self.assertEqual(set(TASK_IDS), set(task_sections(fixture)))

    def test_rejects_missing_approved_spec_identity(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(
                load_plan(copy).replace(
                    "- Approval state: approved",
                    "- Approval state: pending",
                    1,
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "North Star is not in approved state",
                fixture_plan_errors(load_plan(copy)),
            )

    def test_rejects_nonportable_approved_identity_paths(self) -> None:
        ready_plan = load_plan(READY_PLAN)
        absolute_probe = Path("/").joinpath(
            "Users", "example", "private-spec.md"
        ).as_posix()
        for replacement in (
            absolute_probe,
            "../outside/private-spec.md",
        ):
            with self.subTest(replacement=replacement):
                mutated = ready_plan.replace(
                    "specifications/representative-sdd.md",
                    replacement,
                )
                errors = fixture_plan_errors(mutated)
                self.assertIn(
                    "approved spec path is not repository-relative and portable",
                    errors,
                )
                self.assertIn(
                    "approved North Star path is not repository-relative and portable",
                    errors,
                )

    def test_rejects_empty_wrong_or_malformed_binding_hashes(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(
                load_plan(copy)
                .replace(
                    "- Approved spec SHA-256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "- Approved spec SHA-256:",
                )
                .replace(
                    "- Approved snapshot SHA-256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "- Approved snapshot SHA-256: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
                )
                .replace(
                    "- Repository baseline: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                    "- Repository baseline: 111111111111111111111111111111111111111",
                ),
                encoding="utf-8",
            )
            errors = fixture_plan_errors(load_plan(copy))
            self.assertIn("missing approved-spec identity field: Approved spec SHA-256", errors)
            self.assertIn("North Star and Written Spec approval snapshots differ", errors)
            self.assertIn("repository baseline is not a full commit identity", errors)

    def test_rejects_an_incomplete_requirement_acceptance_inventory(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            inventory = section(load_plan(copy), "Requirement And Acceptance Inventory")
            self.assertIn("AC-14", inventory)
            copy.write_text(load_plan(copy).replace("AC-14", "omitted acceptance", 1), encoding="utf-8")
            self.assertIn("inventory missing ID: AC-14", fixture_plan_errors(load_plan(copy)))

    def test_rejects_an_unassigned_acceptance(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| AC-14 | POA-3 | POA-1, POA-2 |", ""), encoding="utf-8")
            self.assertIn("unassigned coverage ID: AC-14", fixture_plan_errors(load_plan(copy)))

    def test_rejects_an_unknown_coverage_id(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| AC-14 | POA-3 | POA-1, POA-2 |", "| AC-99 | POA-3 | POA-1, POA-2 |"), encoding="utf-8")
            self.assertIn("unknown coverage ID: AC-99", fixture_plan_errors(load_plan(copy)))

    def test_rejects_an_orphan_task(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("### Task POA-3:", "### Removed Task POA-3:"), encoding="utf-8")
            self.assertIn("orphan task: POA-3", fixture_plan_errors(load_plan(copy)))

    def test_rejects_an_undefined_dependency(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| POA-3 | POA-1, POA-2 |", "| POA-3 | POA-1, POA-9 |"), encoding="utf-8")
            self.assertIn("undefined dependency: POA-3 -> POA-9", fixture_plan_errors(load_plan(copy)))

    def test_rejects_a_dependency_cycle(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("| POA-1 | none |", "| POA-1 | POA-3 |"), encoding="utf-8")
            self.assertIn("dependency cycle", fixture_plan_errors(load_plan(copy)))

    def test_rejects_an_execution_order_violation(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("1. POA-1\n2. POA-2\n3. POA-3", "1. POA-2\n2. POA-1\n3. POA-3"), encoding="utf-8")
            self.assertIn("execution-order violation: POA-1 must precede POA-2", fixture_plan_errors(load_plan(copy)))

    def test_rejects_missing_serialized_integration_or_combined_verification(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy).replace("I-3: POA-3", "I-3 omitted").replace("**Failure owner:**", "Failure owner:"), encoding="utf-8")
            errors = fixture_plan_errors(load_plan(copy))
            self.assertIn("missing serialized integration order", errors)
            self.assertIn("combined verification missing Failure owner", errors)

    def test_rejects_nonready_semantic_readiness_states_even_when_nonempty(self) -> None:
        probes = {
            "- Current-tree compatibility: compatible": (
                "- Current-tree compatibility: incompatible",
                "current-tree compatibility is not compatible",
            ),
            "- Independent review verdict: ready": (
                "- Independent review verdict: issues_found",
                "independent review verdict is not ready",
            ),
            "- Repository checks: passed": (
                "- Repository checks: absent",
                "repository checks did not pass",
            ),
            "- Readiness evidence state: current": (
                "- Readiness evidence state: stale",
                "readiness evidence is not current",
            ),
            "- Plan readiness disposition: ready": (
                "- Plan readiness disposition: needs_repair",
                "plan readiness disposition is not ready",
            ),
        }
        ready_plan = load_plan(READY_PLAN)
        for original, (replacement, expected_error) in probes.items():
            with self.subTest(replacement=replacement):
                self.assertIn(original, ready_plan)
                mutated = ready_plan.replace(original, replacement, 1)
                self.assertIn(expected_error, fixture_plan_errors(mutated))

    def test_rejects_duplicate_contradictory_singleton_states(self) -> None:
        ready_plan = load_plan(READY_PLAN)
        probes = {
            "- Independent review verdict: ready": (
                "- Independent review verdict: ready\n- Independent review verdict: issues_found",
                "duplicate plan binding field: Independent review verdict",
            ),
            "- Readiness evidence state: current": (
                "- Readiness evidence state: current\n- Readiness evidence state: stale",
                "duplicate plan binding field: Readiness evidence state",
            ),
            "- Plan readiness disposition: ready": (
                "- Plan readiness disposition: ready\n- Plan readiness disposition: issues_found",
                "duplicate readiness field: Plan readiness disposition",
            ),
        }
        for original, (replacement, expected_error) in probes.items():
            with self.subTest(replacement=replacement):
                mutated = ready_plan.replace(original, replacement, 1)
                self.assertIn(expected_error, fixture_plan_errors(mutated))

    def test_rejects_empty_singletons_and_duplicate_matching_sections(self) -> None:
        ready_plan = load_plan(READY_PLAN)
        probes = {
            ready_plan.replace(
                "- Repository checks: passed", "- Repository checks:", 1
            ): "missing plan binding field: Repository checks",
            ready_plan
            + "\n## Plan Binding\n\n"
            + "- Repository baseline: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
            + "- Planning worktree: worktrees/other\n"
            + "- Integration branch: other\n"
            + "- Current-tree compatibility: incompatible\n"
            + "- Independent review verdict: issues_found\n"
            + "- Repository checks: failed\n"
            + "- Readiness evidence state: stale\n": "duplicate section: Plan Binding",
            ready_plan
            + "\n## Readiness Result\n\n"
            + "- Plan readiness disposition: issues_found\n"
            + "- Control Return status: blocked\n"
            + "- Implementation Stage entry: forbidden\n": "duplicate section: Readiness Result",
        }
        for mutated, expected_error in probes.items():
            with self.subTest(expected_error=expected_error):
                self.assertIn(expected_error, fixture_plan_errors(mutated))

    def test_rejects_prospective_body_and_human_plan_approval_language(self) -> None:
        temporary_directory, copy = self.copy_ready_plan()
        with temporary_directory:
            copy.write_text(load_plan(copy) + "\n```python\npass\n```\nHuman plan approval is required.\n", encoding="utf-8")
            errors = fixture_plan_errors(load_plan(copy))
            self.assertIn("prospective body: fenced code block", errors)
            self.assertIn("Human plan-approval language", errors)

    def test_rejects_unfenced_test_shell_loop_patch_and_pytest_bodies(self) -> None:
        probes = {
            "\ndef test_ready_plan():\n    assert plan.ready\n": "prospective body: test body",
            "\nfor path in files; do\n  validate $path\ndone\n": "prospective body: shell loop",
            "\n*** Begin Patch\n*** Update File: plan.md\n": "prospective body: patch body",
            "\npytest -q tests/test_plan.py\n": "prospective body: command body",
        }
        for body, expected_error in probes.items():
            with self.subTest(expected_error=expected_error):
                self.assertIn(expected_error, fixture_plan_errors(load_plan(READY_PLAN) + body))

    def test_rejects_unfenced_production_shell_and_execution_bodies(self) -> None:
        probes = {
            "\ndef build_plan(spec):\n    return normalize(spec)\n": "prospective body: production code",
            "\ndef build_plan(spec): return normalize(spec)\n": "prospective body: production code",
            "\nfunction buildPlan(spec) {\n  return normalize(spec);\n}\n": "prospective body: production code",
            "\nconst buildPlan = (spec) => normalize(spec);\n": "prospective body: production code",
            "\nif [ -f \"$plan\" ]; then\nvalidate \"$plan\"\nfi\n": "prospective body: shell body",
            "\npython3 -m unittest discover -s tests\n": "prospective body: command body",
            "\necho \"ready\"\n": "prospective body: command body",
        }
        for body, expected_error in probes.items():
            with self.subTest(expected_error=expected_error, body=body):
                self.assertIn(expected_error, fixture_plan_errors(load_plan(READY_PLAN) + body))

    def test_rejects_remaining_structural_body_and_plain_echo_forms(self) -> None:
        probes = {
            (
                '\ndef build_plan(spec):\n    """Build a normalized plan."""\n'
                "    return normalize(spec)\n"
            ): "prospective body: production code",
            "\nfunction buildPlan(spec) { return normalize(spec); }\n": "prospective body: production code",
            "\nif [ -f \"$plan\" ]; then validate \"$plan\"; fi\n": "prospective body: shell body",
            "\necho ready\n": "prospective body: command body",
        }
        for body, expected_error in probes.items():
            with self.subTest(body=body):
                self.assertIn(expected_error, fixture_plan_errors(load_plan(READY_PLAN) + body))

    def test_rejects_blank_line_docstring_body_and_multi_command_inline_shell_if(self) -> None:
        probes = {
            (
                '\ndef build_plan(spec):\n    """Build a normalized plan."""\n\n'
                "    return normalize(spec)\n"
            ): "prospective body: production code",
            (
                '\nif [ -f "$plan" ]; then validate "$plan"; '
                'echo ready; record "$plan"; fi\n'
            ): "prospective body: shell body",
        }
        for body, expected_error in probes.items():
            with self.subTest(body=body):
                self.assertIn(expected_error, fixture_plan_errors(load_plan(READY_PLAN) + body))

    def test_rejects_any_parsed_python_statement_after_optional_preamble(self) -> None:
        probes = (
            (
                "\ndef build_plan(spec):\n"
                "# optional comment\n"
                "    import json\n"
            ),
            (
                "\ndef build_plan(\n"
                "    spec,\n"
                "):\n"
                "    import json\n"
            ),
            '\ndef build_plan(spec):\n    """Build the plan."""\n\n    import json\n',
            (
                '\nasync def build_plan(spec):\n    """Build the plan."""\n\n'
                "    await normalize(spec)\n"
            ),
            (
                '\ndef build_plan(spec):\n    """Build the plan."""\n'
                "    # implementation follows\n\n    self.normalize(spec)\n"
            ),
            (
                '\ndef build_plan(spec):\n    """Build the plan."""\n\n'
                "    self.plan = spec\n"
            ),
        )
        for body in probes:
            with self.subTest(body=body):
                self.assertIn(
                    "prospective body: production code",
                    fixture_plan_errors(load_plan(READY_PLAN) + body),
                )

    def test_prohibition_scan_allows_intent_only_narrative(self) -> None:
        narrative = (
            "\nThe reviewer rejects an unfenced test body, shell loop, patch body, "
            "or pytest command body and records only observable intent. "
            "A plan may name Python `def build_plan(spec):`, JavaScript "
            "`function buildPlan(spec) { ... }`, shell if bodies, "
            "`python3 -m unittest`, and `echo` as prohibited classes without "
            "supplying their bodies or execution commands.\n"
            "echo is also the name of a prohibited shell output command, not "
            "an execution instruction in this sentence.\n"
            "The proposed interface `def build_plan(spec): returns a normalized "
            "plan in the proposed interface.` describes intent without a body.\n"
        )
        self.assertNotIn("prospective body", " ".join(fixture_plan_errors(load_plan(READY_PLAN) + narrative)))


if __name__ == "__main__":
    unittest.main()
