from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "task-management"
SKILL = SKILL_ROOT / "SKILL.md"
CORE = SKILL_ROOT / "references" / "core.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TaskManagementContractTests(unittest.TestCase):
    def test_standalone_structure_and_frontmatter(self) -> None:
        self.assertTrue(SKILL.is_file())
        self.assertTrue(CORE.is_file())
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


if __name__ == "__main__":
    unittest.main()
