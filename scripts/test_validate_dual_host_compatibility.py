import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_dual_host_compatibility import (
    validate_plugin,
    validate_repository,
    validate_skill,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_dual_host_compatibility.py"


def write_skill(root, name, description="Shared workflow."):
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n# Skill\n",
        encoding="utf-8",
    )
    return skill_dir


def write_plugin(root, name="sample-plugin"):
    plugin_dir = root / name
    (plugin_dir / ".codex-plugin").mkdir(parents=True)
    (plugin_dir / "skills" / name).mkdir(parents=True)
    (plugin_dir / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(
            {"name": name, "version": "1.0.0", "description": "Codex package."}
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.yaml").write_text(
        "manifest_version: 1\n"
        f"name: {name}\n"
        "version: 1.0.0\n"
        "description: Hermes package.\n"
        "kind: standalone\n",
        encoding="utf-8",
    )
    (plugin_dir / "skills" / name / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Bundled workflow.\n---\n",
        encoding="utf-8",
    )
    (plugin_dir / "__init__.py").write_text(
        "def register(ctx):\n"
        f"    ctx.register_skill({name!r}, 'skills/{name}/SKILL.md')\n",
        encoding="utf-8",
    )
    return plugin_dir


class DualHostCompatibilityTests(unittest.TestCase):
    def test_valid_repository_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skills_root = root / "skills"
            plugins_root = root / "plugins"
            write_skill(skills_root, "sample-skill")
            write_plugin(plugins_root)
            self.assertEqual([], validate_repository(skills_root, plugins_root))

    def test_skill_contract_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing = root / "missing"
            missing.mkdir()
            self.assertIn("missing/SKILL.md is required", validate_skill(missing))
            mismatch = write_skill(root, "folder-name", description="")
            path = mismatch / "SKILL.md"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "name: folder-name", "name: another-name"
                ),
                encoding="utf-8",
            )
            errors = validate_skill(mismatch)
            self.assertIn(
                "folder-name: frontmatter name must equal directory name", errors
            )
            self.assertIn(
                "folder-name: frontmatter description must be non-empty", errors
            )

    def test_separate_description_md_discovery_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = write_skill(Path(tmpdir), "sample-skill")
            (skill_dir / "description.md").write_text(
                "Wrong entrypoint.", encoding="utf-8"
            )
            self.assertIn(
                "sample-skill: SKILL.md must not depend on description.md for discovery",
                validate_skill(skill_dir),
            )

    def test_plugin_identity_and_registration_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex = json.loads(codex_path.read_text(encoding="utf-8"))
            codex["version"] = "2.0.0"
            codex_path.write_text(json.dumps(codex), encoding="utf-8")
            (plugin_dir / "__init__.py").write_text(
                "def register(ctx):\n    pass\n", encoding="utf-8"
            )
            errors = validate_plugin(plugin_dir)
            self.assertIn(
                "sample-plugin: Codex and Hermes versions must match", errors
            )
            self.assertIn(
                "sample-plugin: bundled skills require ctx.register_skill(...)", errors
            )

    def test_cli_json_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skills_root = root / "skills"
            plugins_root = root / "plugins"
            (skills_root / "bad-skill").mkdir(parents=True)
            plugins_root.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--all",
                    "--skills-root",
                    str(skills_root),
                    "--plugins-root",
                    str(plugins_root),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(1, result.returncode)
            self.assertFalse(payload["ok"])
            self.assertIn("bad-skill/SKILL.md is required", payload["errors"])


if __name__ == "__main__":
    unittest.main()
