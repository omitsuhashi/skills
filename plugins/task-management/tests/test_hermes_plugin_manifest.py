import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugin.yaml"
ENTRYPOINT = ROOT / "__init__.py"
README = ROOT / "README.md"
SKILL = ROOT / "skills" / "task-management" / "SKILL.md"


def parse_simple_yaml(path):
    parsed = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith("- "):
            continue
        if ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        parsed[key] = value
    return parsed


class HermesPluginManifestTests(unittest.TestCase):
    def test_native_hermes_manifest_exists_with_supported_kind(self):
        self.assertTrue(MANIFEST.exists(), "Hermes native plugins require plugin.yaml")

        manifest = parse_simple_yaml(MANIFEST)

        self.assertEqual("task-management", manifest.get("name"))
        self.assertEqual("0.1.0", manifest.get("version"))
        self.assertEqual("Omitsuhashi", manifest.get("author"))
        self.assertEqual(
            "standalone",
            manifest.get("kind"),
            "Current Hermes PluginManager supports standalone/backend/exclusive/platform/model-provider; workflow would be coerced with a warning.",
        )
        self.assertIn("workflow package", manifest.get("description", ""))

    def test_native_hermes_entrypoint_registers_bundled_skill(self):
        self.assertTrue(
            ENTRYPOINT.exists(),
            "Hermes enable/load requires __init__.py with register(ctx)",
        )

        text = ENTRYPOINT.read_text(encoding="utf-8")

        self.assertIn("def register(ctx):", text)
        self.assertIn("ctx.register_skill", text)
        self.assertIn('"task-management"', text)
        self.assertIn("skills", text)
        self.assertIn("SKILL.md", text)
        self.assertTrue(SKILL.exists(), "registered skill target must exist")

    def test_hermes_install_docs_describe_subdir_update_limitation(self):
        self.assertTrue(README.exists(), "Hermes plugin package needs install/update notes")

        text = README.read_text(encoding="utf-8")

        self.assertIn("hermes plugins install", text)
        self.assertIn("git@github.com:omitsuhashi/skills.git#plugins/task-management", text)
        self.assertIn("hermes plugins enable task-management", text)
        self.assertIn("hermes plugins update task-management", text)
        self.assertIn(".git", text)
        self.assertIn("hermes plugins install --force", text)


if __name__ == "__main__":
    unittest.main()
