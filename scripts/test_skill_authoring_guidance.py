from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "AGENTS.md"
SKILLS = REPO_ROOT / "skills" / "AGENTS.md"
PLUGINS = REPO_ROOT / "plugins" / "AGENTS.md"


class SkillAuthoringGuidanceTests(unittest.TestCase):
    def test_root_routes_to_directory_contracts(self):
        text = ROOT.read_text(encoding="utf-8")
        for value in ("portable", "skills/AGENTS.md", "plugins/AGENTS.md"):
            self.assertIn(value, text)

    def test_skill_contract_names_portable_entrypoint_and_runtime_boundary(self):
        text = SKILLS.read_text(encoding="utf-8")
        for value in (
            "SKILL.md", "name", "description", "inputs", "outputs",
            "capabilities", "active runtime", "optional metadata",
        ):
            self.assertIn(value, text)
        self.assertIn("must not create `description.md`", text)

    def test_plugin_contract_allows_runtime_selected_packaging(self):
        text = PLUGINS.read_text(encoding="utf-8")
        for value in (
            "Plugins may target one runtime.",
            "Do not add another runtime package solely for compatibility.",
            "standalone companion skill",
        ):
            self.assertIn(value, text)
        self.assertNotIn("scripts/validate_repository_compatibility.py", text)


if __name__ == "__main__":
    unittest.main()
