from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "task-management"
SKILL = SKILL_ROOT / "SKILL.md"
CORE = SKILL_ROOT / "references" / "core.md"
PROJECTS = SKILL_ROOT / "references" / "github-projects.md"
ISSUES = SKILL_ROOT / "references" / "issue-contract.md"
SAFETY = SKILL_ROOT / "references" / "safety-and-failures.md"

EXPECTED_FILES = {
    "SKILL.md",
    "references/core.md",
    "references/github-projects.md",
    "references/issue-contract.md",
    "references/safety-and-failures.md",
    "tests/test_task_management_contract.py",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    """Return one Markdown section, excluding peer and parent headings."""
    match = re.search(
        rf"(?ms)^{re.escape(heading)}\n(.*?)(?=^#{{1,{heading.count('#')}}} |\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"missing section: {heading}")
    return match.group(1)


def field_options(text: str, field: str) -> list[str]:
    """Parse the backtick option names in one Project field subsection."""
    next_field = {
        "Status": r"^`Priority` options:",
        "Priority": r"^`Due date`",
    }[field]
    match = re.search(
        rf"(?ms)^`{re.escape(field)}` options:\n(.*?)(?={next_field})",
        text,
    )
    if match is None:
        raise AssertionError(f"missing field option block: {field}")
    field_text = match.group(1)
    return re.findall(r"(?m)^- `([^`]+)`: ", field_text)


class TaskManagementContractTests(unittest.TestCase):
    def test_standalone_structure_and_frontmatter(self) -> None:
        actual_files = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual(EXPECTED_FILES, actual_files)
        self.assertFalse((REPO_ROOT / "plugins" / "task-management").exists())
        text = read(SKILL)
        self.assertTrue(text.startswith("---\nname: task-management\n"))
        self.assertIn("description:", text.split("---", 2)[1])

    def test_core_is_caller_owned_and_issue_backed(self) -> None:
        text = read(SKILL) + "\n" + read(CORE)
        for required in (
            "project_url",
            "inbox_repository",
            "one canonical default Project",
            "GitHub Issue",
            "repository is the work unit boundary",
            "GitHub MCP",
        ):
            self.assertIn(required, text)

    def test_skill_has_no_host_specific_or_runtime_surface(self) -> None:
        production = [
            SKILL,
            *sorted((SKILL_ROOT / "references").glob("*.md")),
        ]
        text = "\n".join(read(path) for path in production)
        for prohibited in (
            "Hermes",
            "Codex",
            "task-management-read",
            "task_adapter__",
            "work_unit_id",
        ):
            self.assertNotIn(prohibited, text)
        self.assertFalse((SKILL_ROOT / "agents").exists())
        self.assertFalse((SKILL_ROOT / "plugin.yaml").exists())
        self.assertFalse((SKILL_ROOT / ".codex-plugin").exists())
        production_python = [
            path
            for path in SKILL_ROOT.rglob("*.py")
            if "tests" not in path.parts
        ]
        self.assertEqual([], production_python)

    def test_reference_router_is_complete(self) -> None:
        skill_text = read(SKILL)
        for name in (
            "core.md",
            "github-projects.md",
            "issue-contract.md",
            "safety-and-failures.md",
        ):
            self.assertIn(f"references/{name}", skill_text)
            self.assertTrue((SKILL_ROOT / "references" / name).is_file())

    def test_target_resolution_is_ordered_and_ambiguity_stops(self) -> None:
        text = read(CORE)
        project_section = text.split("## Project resolution order", 1)[1].split(
            "## Repository resolution order", 1
        )[0]
        repository_section = text.split("## Repository resolution order", 1)[1].split(
            "## Read and write identity", 1
        )[0]
        project_steps = (
            "Invocation `project_url`",
            "Caller default `project_url`",
            "Session-established Project",
            "Unique open Project discovery",
            "Ask the user",
        )
        repository_steps = (
            "Explicit repository",
            "Current repository",
            "Unique referenced repository",
            "Configured inbox",
            "Ask the user",
        )
        for section, steps in (
            (project_section, project_steps),
            (repository_section, repository_steps),
        ):
            positions = [section.index(step) for step in steps]
            self.assertEqual(sorted(positions), positions)
        self.assertIn("Never use inbox as an ambiguity fallback", text)

    def test_issue_and_project_fields_are_exact(self) -> None:
        project_text = read(PROJECTS)
        issue_text = read(ISSUES)
        self.assertEqual(
            [
                "Inbox",
                "Backlog",
                "Ready",
                "In progress",
                "Blocked",
                "Done",
                "Cancelled",
            ],
            field_options(project_text, "Status"),
        )
        self.assertEqual(
            ["P0", "P1", "P2", "P3"],
            field_options(project_text, "Priority"),
        )
        self.assertIn("`Due date` is optional.", project_text)
        due_date = project_text.split("`Due date` is optional.", 1)[1].split(
            "## Terminal transitions", 1
        )[0]
        self.assertIn("Leave it empty", due_date)
        self.assertIn("close reason `completed`", project_text)
        self.assertIn("close reason `not planned`", project_text)
        for heading in (
            "## Outcome",
            "## Context",
            "## Acceptance criteria",
            "## References",
        ):
            self.assertIn(heading, issue_text)

    def test_operation_routing_is_classified_before_capabilities(self) -> None:
        text = read(SKILL)
        routing = section(text, "## Operation routing")
        self.assertIn("For every write route", routing)
        self.assertLess(
            routing.index("Classify the requested operation"),
            routing.index("For every write route"),
        )

        read_flow = section(text, "### Read, search, and list")
        for prohibited_write in (
            "create or edit an Issue",
            "add a comment",
            "close an Issue",
            "add an Issue to a Project",
            "update a Project field",
        ):
            self.assertIn(prohibited_write, read_flow)
        self.assertIn("Resolve only the query scope needed to answer", read_flow)
        self.assertIn("Return only read results", read_flow)

        create_flow = section(text, "### Create and register")
        self.assertIn("Only this operation uses the new-task flow", create_flow)
        self.assertIn("newly created Project item", create_flow)
        self.assertIn("Status=Inbox", create_flow)
        self.assertIn("Priority=P2", create_flow)
        self.assertIn("no due date", create_flow)

        edit_flow = section(text, "### Edit")
        self.assertIn("only the explicitly requested Issue properties", edit_flow)
        self.assertIn("Do not add Project membership", edit_flow)
        self.assertIn("Do not apply creation defaults", edit_flow)

        comment_flow = section(text, "### Comment")
        self.assertIn("only the requested comment", comment_flow)
        self.assertIn("Do not add Project membership", comment_flow)
        self.assertIn("Do not apply creation defaults", comment_flow)

        field_flow = section(text, "### Non-terminal field update")
        self.assertIn("only the explicitly requested field values", field_flow)
        self.assertIn("Do not change any unrequested field", field_flow)

        terminal_flow = section(text, "### Terminal update")
        self.assertIn("explicit terminal instruction", terminal_flow)
        self.assertIn("Do not ask twice", terminal_flow)
        self.assertIn("inferred terminal transition", terminal_flow)
        self.assertIn("confirmation", terminal_flow)

    def test_create_preflight_requires_only_create_and_registration_capabilities(self) -> None:
        skill_text = read(SKILL)
        project_text = section(read(PROJECTS), "## Semantic capability check")
        create_flow = section(skill_text, "### Create and register")

        for required in (
            "Issue read, search, and create",
            "Project read, item add, and creation-default field update",
            "Access to the resolved repository and Project",
        ):
            self.assertIn(required, project_text)
        for unrelated in (
            "Issue update and comment",
            "Issue close",
            "terminal Project Status update",
        ):
            self.assertNotIn(unrelated, create_flow)
        self.assertIn("check only the create operation capabilities", create_flow)

    def test_skill_uses_direct_mcp_and_has_structural_inferred_create_gate(self) -> None:
        text = "\n".join(
            read(path)
            for path in [SKILL, CORE, PROJECTS, ISSUES, SAFETY]
        )
        for required in (
            "Use available GitHub MCP capabilities directly",
            "explicit",
            "inferred",
            "one task",
            "idempotency key",
            "observable acceptance criteria",
            "Do not ask twice",
        ):
            self.assertIn(required, text)
        for prohibited in (
            "GitHub MCP facade",
            "execution wrapper",
            "transport adapter",
            "numeric confidence",
        ):
            self.assertNotIn(prohibited, text)

    def test_reuse_and_partial_failure_preserve_existing_state(self) -> None:
        issue_text = section(read(ISSUES), "## Duplicate handling")
        self.assertIn("never create a second Issue", issue_text)
        self.assertIn("Preserve its current fields", issue_text)
        self.assertIn("requested operation", issue_text)
        self.assertIn("documented unfinished partial-failure step", issue_text)

        partial_failure = section(read(SAFETY), "## Partial success")
        self.assertIn("continue only the unfinished steps", partial_failure.lower())
        self.assertIn("Do not reset completed or current fields", partial_failure)
        self.assertIn("Do not create a duplicate Issue", partial_failure)

    def test_approval_policy_distinguishes_safe_uncertain_and_destructive(self) -> None:
        text = read(SAFETY)
        for required in (
            "High-confidence safe single-item writes run automatically",
            "Uncertain target or content requires confirmation",
            "Destructive or bulk mutation requires confirmation",
            "An explicit user instruction is the approval for that exact operation",
            "Do not ask twice",
        ):
            self.assertIn(required, text)

    def test_capability_and_partial_failures_are_fail_closed(self) -> None:
        text = read(PROJECTS) + "\n" + read(SAFETY)
        for required in (
            "Issue read, search, create, update, and comment",
            "Project read, item add, and field update",
            "Do not fall back to a CLI, direct API client, browser automation, or local backend",
            "Do not delete the created Issue",
            "Continue only the unfinished steps",
            "Do not create a duplicate Issue",
        ):
            self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
