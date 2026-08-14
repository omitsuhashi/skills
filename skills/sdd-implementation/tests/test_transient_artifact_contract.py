from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
PLANNING_CONTEXT = SKILL_DIR / "references" / "planning-context.md"
RESEARCH_STAGE = SKILL_DIR / "references" / "research-stage.md"
RESEARCHER_PROMPT = SKILL_DIR / "prompts" / "repository-researcher.md"
SYNTHESIZER_PROMPT = SKILL_DIR / "prompts" / "spec-synthesizer.md"
SPEC_REVIEWER_PROMPT = SKILL_DIR / "prompts" / "spec-reviewer.md"
PLAN_REVIEWER_PROMPT = SKILL_DIR / "prompts" / "plan-reviewer.md"

RAW_HANDOFF_DEFAULT = "repository-external task/session temporary"
STAGE_DURABLE_ROUTES = {
    "Research": "canonical specification",
    "Spec": "canonical specification",
    "Plan": "reviewed implementation plan",
    "Implementation": "reviewed implementation plan",
    "Task review": "reviewed implementation plan",
    "Repair": "reviewed implementation plan",
    "Integration": "reviewed implementation plan",
    "Final review": "reviewed implementation plan",
    "Knowledge closeout": "knowledge/log.md",
}
RAW_ARTIFACTS = (
    "research report",
    "worker report",
    "fix report",
    "raw review output",
    "transcript",
    "duplicate task content",
)
EXPECTED_FIELDS = {
    "Default raw handoff route": RAW_HANDOFF_DEFAULT,
    "Repository-local scratch prerequisite": (
        "concrete operational reason and mechanical pre-write .gitignore coverage"
    ),
    "Allowed scratch state": "ignored, untracked, unstaged, uncommitted",
    "Missing prerequisite route": "fail closed to repository-external default",
    "Raw artifacts excluded from durable outputs": ", ".join(RAW_ARTIFACTS),
    "Durable summary fields": "decision, finding, repair, verdict, evidence identity",
    "Durable summary surfaces": (
        "canonical specification, reviewed implementation plan, knowledge/log.md"
    ),
}
COMPLIANT_BOUNDARY = """## Transient Artifact Boundary

- Default raw handoff route: repository-external task/session temporary
- Repository-local scratch prerequisite: concrete operational reason and mechanical pre-write .gitignore coverage
- Allowed scratch state: ignored, untracked, unstaged, uncommitted
- Missing prerequisite route: fail closed to repository-external default
- Raw artifacts excluded from durable outputs: research report, worker report, fix report, raw review output, transcript, duplicate task content
- Durable summary fields: decision, finding, repair, verdict, evidence identity
- Durable summary surfaces: canonical specification, reviewed implementation plan, knowledge/log.md

| Stage | Raw handoff default | Durable summary route |
| --- | --- | --- |
| Research | repository-external task/session temporary | canonical specification |
| Spec | repository-external task/session temporary | canonical specification |
| Plan | repository-external task/session temporary | reviewed implementation plan |
| Implementation | repository-external task/session temporary | reviewed implementation plan |
| Task review | repository-external task/session temporary | reviewed implementation plan |
| Repair | repository-external task/session temporary | reviewed implementation plan |
| Integration | repository-external task/session temporary | reviewed implementation plan |
| Final review | repository-external task/session temporary | reviewed implementation plan |
| Knowledge closeout | repository-external task/session temporary | knowledge/log.md |
"""

VALIDATION_GATE_ROWS = {
    "exceptional-local-scratch-pre-write": (
        "before each exceptional repository-local scratch leaf's first write"
    ),
    "pre-commit-candidate": "immediately before each commit creation",
    "final-closeout": "after cleanup and immediately before local completion",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def field_values(text: str, label: str) -> list[str]:
    return [
        value.strip()
        for value in re.findall(
            rf"^- {re.escape(label)}:\s*([^\r\n]+)$",
            text,
            flags=re.MULTILINE,
        )
    ]


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        indent = len(line) - len(line.lstrip(" "))
        candidate = line.strip()
        if indent > 3 or "|" not in candidate:
            continue
        if re.fullmatch(r"[| :\-]+", candidate):
            continue
        if candidate.startswith("|"):
            candidate = candidate[1:]
        if candidate.endswith("|"):
            candidate = candidate[:-1]
        rows.append([cell.strip() for cell in candidate.split("|")])
    return rows


def transient_boundary_errors(text: str) -> list[str]:
    errors: list[str] = []
    boundary = section(text, "Transient Artifact Boundary")
    if not boundary:
        return ["missing Transient Artifact Boundary section"]

    for label, expected in EXPECTED_FIELDS.items():
        values = field_values(boundary, label)
        if values != [expected]:
            errors.append(f"invalid boundary field: {label}")

    rows = [row for row in table_rows(boundary) if row and row[0] != "Stage"]
    for row in rows:
        if len(row) != 3:
            errors.append(f"malformed stage row: {row[0] or '<empty>'}")
    stage_counts = Counter(row[0] for row in rows)
    for stage, durable_route in STAGE_DURABLE_ROUTES.items():
        if stage_counts[stage] != 1:
            errors.append(f"stage row count must be one: {stage}")
            continue
        row = next(row for row in rows if row[0] == stage)
        if len(row) != 3:
            continue
        if row[1] != RAW_HANDOFF_DEFAULT:
            errors.append(f"repository-external default mismatch: {stage}")
        if row[2] != durable_route:
            errors.append(f"durable summary route mismatch: {stage}")
        if any(raw_artifact in row[2].lower() for raw_artifact in RAW_ARTIFACTS):
            errors.append(f"raw artifact routed to durable output: {stage}")

    unknown_stages = set(stage_counts) - set(STAGE_DURABLE_ROUTES)
    for stage in sorted(unknown_stages):
        errors.append(f"unknown stage row: {stage}")
    return errors


def validation_gate_errors(text: str) -> list[str]:
    validation = section(text, "Repository Validation Gate")
    if not validation:
        return ["missing Repository Validation Gate section"]
    rows = [row for row in table_rows(validation) if row and row[0] != "Gate"]
    counts = Counter(row[0].strip("`") for row in rows)
    errors: list[str] = []
    for gate, moment in VALIDATION_GATE_ROWS.items():
        if counts[gate] != 1:
            errors.append(f"gate row count must be one: {gate}")
            continue
        row = next(row for row in rows if row[0].strip("`") == gate)
        if len(row) != 3:
            errors.append(f"malformed validation gate row: {gate}")
            continue
        if row[1] != moment:
            errors.append(f"gate moment mismatch: {gate}")
        if not row[2]:
            errors.append(f"missing direct Git verdict: {gate}")
    unknown = set(counts) - set(VALIDATION_GATE_ROWS)
    for gate in sorted(unknown):
        errors.append(f"unknown validation gate row: {gate}")
    return errors


class TransientArtifactContractTests(unittest.TestCase):
    def test_skill_defines_each_stage_route_with_no_contradictory_destination(self) -> None:
        self.assertEqual([], transient_boundary_errors(read(SKILL)))

    def test_stage_contract_rejects_repo_contained_missing_or_duplicate_routes(self) -> None:
        for stage, durable_route in STAGE_DURABLE_ROUTES.items():
            with self.subTest(stage=stage):
                external_row = (
                    f"| {stage} | {RAW_HANDOFF_DEFAULT} | {durable_route} |"
                )
                repository_contained_row = (
                    f"| {stage} | .superpowers/sdd/{stage.lower().replace(' ', '-')} | "
                    f"{durable_route} |"
                )
                mutated = COMPLIANT_BOUNDARY.replace(
                    external_row, repository_contained_row
                )
                self.assertIn(
                    f"repository-external default mismatch: {stage}",
                    transient_boundary_errors(mutated),
                )

        missing = COMPLIANT_BOUNDARY.replace(
            "| Spec | repository-external task/session temporary | canonical specification |\n",
            "",
        )
        self.assertIn(
            "stage row count must be one: Spec", transient_boundary_errors(missing)
        )
        duplicate = COMPLIANT_BOUNDARY.replace(
            "| Research | repository-external task/session temporary | canonical specification |",
            "| Research | repository-external task/session temporary | canonical specification |\n"
            "| Research | .superpowers/research/<epic-id>/ | canonical specification |",
        )
        self.assertIn(
            "stage row count must be one: Research",
            transient_boundary_errors(duplicate),
        )

        valid_plus_four_cell = COMPLIANT_BOUNDARY.replace(
            "| Research | repository-external task/session temporary | canonical specification |",
            "| Research | repository-external task/session temporary | canonical specification |\n"
            "| Research | repository-external task/session temporary | canonical specification | "
            ".superpowers/research/<epic-id>/ |",
        )
        errors = transient_boundary_errors(valid_plus_four_cell)
        self.assertIn("malformed stage row: Research", errors)
        self.assertIn("stage row count must be one: Research", errors)

    def test_stage_contract_rejects_gfm_rows_with_optional_outer_pipes_and_indent(self) -> None:
        canonical = (
            "| Research | repository-external task/session temporary | "
            "canonical specification |"
        )
        contradictory_rows = (
            "Research | .superpowers/research/<epic-id>/ | canonical specification",
            "  | Research | .superpowers/research/<epic-id>/ | canonical specification |",
        )
        for contradictory in contradictory_rows:
            with self.subTest(row=contradictory):
                mutated = COMPLIANT_BOUNDARY.replace(canonical, contradictory)
                self.assertIn(
                    "repository-external default mismatch: Research",
                    transient_boundary_errors(mutated),
                )

    def test_stage_contract_rejects_raw_artifacts_in_durable_spec_plan_or_log(self) -> None:
        mutations = {
            "canonical specification": "raw research report in canonical specification",
            "reviewed implementation plan": "raw review output in reviewed implementation plan",
            "knowledge/log.md": "fix report transcript in knowledge/log.md",
        }
        for durable_route, contaminated_route in mutations.items():
            with self.subTest(durable_route=durable_route):
                mutated = COMPLIANT_BOUNDARY.replace(
                    f"| Research | {RAW_HANDOFF_DEFAULT} | {durable_route} |"
                    if durable_route == "canonical specification"
                    else (
                        f"| Plan | {RAW_HANDOFF_DEFAULT} | {durable_route} |"
                        if durable_route == "reviewed implementation plan"
                        else f"| Knowledge closeout | {RAW_HANDOFF_DEFAULT} | {durable_route} |"
                    ),
                    f"| Research | {RAW_HANDOFF_DEFAULT} | {contaminated_route} |"
                    if durable_route == "canonical specification"
                    else (
                        f"| Plan | {RAW_HANDOFF_DEFAULT} | {contaminated_route} |"
                        if durable_route == "reviewed implementation plan"
                        else f"| Knowledge closeout | {RAW_HANDOFF_DEFAULT} | {contaminated_route} |"
                    ),
                )
                errors = transient_boundary_errors(mutated)
                expected_stage = {
                    "canonical specification": "Research",
                    "reviewed implementation plan": "Plan",
                    "knowledge/log.md": "Knowledge closeout",
                }[durable_route]
                self.assertIn(
                    f"raw artifact routed to durable output: {expected_stage}", errors
                )

    def test_research_raw_report_binding_is_external_while_spec_remains_durable(self) -> None:
        research_stage = read(RESEARCH_STAGE)
        researcher = read(RESEARCHER_PROMPT)
        synthesizer = read(SYNTHESIZER_PROMPT)
        for text in (research_stage, researcher):
            self.assertIn(RAW_HANDOFF_DEFAULT, text)
            self.assertNotIn(".superpowers/research/<epic-id>/", text)
            self.assertNotIn("resolve inside the planning worktree", text)
        self.assertIn("repository-external Research Report paths", synthesizer)
        self.assertIn("durable spec draft in the planning worktree", synthesizer)

    def test_spec_and_plan_raw_review_bindings_are_external_and_summary_only(self) -> None:
        stage_prompts = {
            "Spec": read(SPEC_REVIEWER_PROMPT),
            "Plan": read(PLAN_REVIEWER_PROMPT),
        }
        for stage, text in stage_prompts.items():
            with self.subTest(stage=stage):
                self.assertIn(RAW_HANDOFF_DEFAULT, text)
                self.assertIn("durable verdict summary", text)
                self.assertNotIn("contained by that worktree", text)
                self.assertNotIn("raw review artifact under `.superpowers/", text)

    def test_compliant_fixture_has_no_contract_errors(self) -> None:
        self.assertEqual([], transient_boundary_errors(COMPLIANT_BOUNDARY))

    def test_repository_validation_has_exactly_three_unambiguous_gate_moments(self) -> None:
        self.assertEqual([], validation_gate_errors(read(SKILL)))

    def test_stage_resources_reference_one_common_guard_without_copying_path_algorithms(self) -> None:
        stage_resources = (
            PLANNING_CONTEXT,
            RESEARCH_STAGE,
            RESEARCHER_PROMPT,
            SYNTHESIZER_PROMPT,
            SPEC_REVIEWER_PROMPT,
            PLAN_REVIEWER_PROMPT,
        )
        for path in stage_resources:
            text = read(path)
            with self.subTest(path=path.name):
                self.assertIn("Common Runtime Capability Guard", text)
                for duplicated_guard in (
                    "git worktree registration",
                    "task-owner capability identity",
                    "relative, unresolved, unbounded, stale",
                    "Do not allocate, select a fallback root",
                    "Synchronous dispatch that returns a completed result",
                    "Asynchronous dispatch requires both wait and resume",
                ):
                    self.assertNotIn(duplicated_guard, text)

    def test_direct_git_gate_algorithms_remain_owned_only_by_the_public_contract(self) -> None:
        stage_resources = (
            PLANNING_CONTEXT,
            RESEARCH_STAGE,
            RESEARCHER_PROMPT,
            SYNTHESIZER_PROMPT,
            SPEC_REVIEWER_PROMPT,
            PLAN_REVIEWER_PROMPT,
        )
        for path in stage_resources:
            text = read(path)
            with self.subTest(path=path.name):
                for command in ("git check-ignore --no-index", "git write-tree", "git ls-tree", "git cat-file"):
                    self.assertNotIn(command, text)


if __name__ == "__main__":
    unittest.main()
