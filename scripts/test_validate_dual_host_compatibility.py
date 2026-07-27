import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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

    def test_missing_repository_roots_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            missing_skills = root / "sklls"
            missing_plugins = root / "plugnis"

            self.assertEqual(
                [
                    f"skills root is not a directory: {missing_skills}",
                    f"plugins root is not a directory: {missing_plugins}",
                ],
                validate_repository(missing_skills, missing_plugins),
            )

    def test_missing_skill_entrypoint_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing"
            missing.mkdir()
            self.assertIn("missing/SKILL.md is required", validate_skill(missing))

    def test_skill_frontmatter_name_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mismatch = write_skill(Path(tmpdir), "folder-name")
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

    def test_empty_skill_frontmatter_description_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = write_skill(Path(tmpdir), "sample-skill", description="")
            errors = validate_skill(skill_dir)
            self.assertIn(
                "sample-skill: frontmatter description must be non-empty", errors
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

    def test_uppercase_description_md_is_not_the_lowercase_discovery_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = write_skill(Path(tmpdir), "sample-skill")
            (skill_dir / "DESCRIPTION.md").write_text(
                "Hermes distribution description.", encoding="utf-8"
            )
            with mock.patch.object(Path, "exists", return_value=True):
                self.assertEqual([], validate_skill(skill_dir))

    def test_plugin_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex = json.loads(codex_path.read_text(encoding="utf-8"))
            codex["version"] = "2.0.0"
            codex_path.write_text(json.dumps(codex), encoding="utf-8")
            errors = validate_plugin(plugin_dir)
            self.assertIn(
                "sample-plugin: Codex and Hermes versions must match", errors
            )

    def test_codex_plugin_version_must_be_a_non_empty_string(self):
        cases = {
            "missing": object(),
            "empty": "",
            "null": None,
            "non-string": 1,
        }
        for label, value in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmpdir:
                plugin_dir = write_plugin(Path(tmpdir))
                codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
                codex = json.loads(codex_path.read_text(encoding="utf-8"))
                if label == "missing":
                    codex.pop("version")
                else:
                    codex["version"] = value
                codex_path.write_text(json.dumps(codex), encoding="utf-8")

                self.assertIn(
                    "sample-plugin: Codex version must be a non-empty string",
                    validate_plugin(plugin_dir),
                )

    def test_hermes_plugin_version_must_be_a_non_empty_string(self):
        replacements = {
            "missing": "",
            "empty": "version:\n",
            "null": "version: null\n",
            "non-string": "version: 1\n",
            "sequence": "version: []\n",
            "mapping": "version: {}\n",
        }
        for label, replacement in replacements.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmpdir:
                plugin_dir = write_plugin(Path(tmpdir))
                manifest = plugin_dir / "plugin.yaml"
                text = manifest.read_text(encoding="utf-8")
                text = text.replace("version: 1.0.0\n", replacement)
                manifest.write_text(text, encoding="utf-8")

                self.assertIn(
                    "sample-plugin: Hermes version must be a non-empty string",
                    validate_plugin(plugin_dir),
                )

    def test_hermes_manifest_version_requires_exact_integer_one(self):
        for scalar in ("true", "1.0"):
            with self.subTest(scalar=scalar), tempfile.TemporaryDirectory() as tmpdir:
                plugin_dir = write_plugin(Path(tmpdir))
                manifest = plugin_dir / "plugin.yaml"
                text = manifest.read_text(encoding="utf-8").replace(
                    "manifest_version: 1\n", f"manifest_version: {scalar}\n"
                )
                manifest.write_text(text, encoding="utf-8")

                self.assertIn(
                    "sample-plugin: Hermes manifest_version must be integer 1",
                    validate_plugin(plugin_dir),
                )

    def test_missing_plugin_skill_registration_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            (plugin_dir / "__init__.py").write_text(
                "def register(ctx):\n    pass\n", encoding="utf-8"
            )
            errors = validate_plugin(plugin_dir)
            self.assertIn(
                "sample-plugin: bundled skill 'sample-plugin' requires matching "
                "ctx.register_skill(...)",
                errors,
            )

    def test_each_bundled_skill_requires_matching_literal_registration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            write_skill(plugin_dir / "skills", "second-skill")

            errors = validate_plugin(plugin_dir)

            self.assertNotIn(
                "sample-plugin: bundled skill 'sample-plugin' requires matching "
                "ctx.register_skill(...)",
                errors,
            )
            self.assertIn(
                "sample-plugin: bundled skill 'second-skill' requires matching "
                "ctx.register_skill(...)",
                errors,
            )

    def test_dynamic_registered_skill_name_does_not_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            (plugin_dir / "__init__.py").write_text(
                "def register(ctx):\n"
                "    skill_name = 'sample-plugin'\n"
                "    ctx.register_skill(skill_name, "
                "'skills/sample-plugin/SKILL.md')\n",
                encoding="utf-8",
            )

            self.assertIn(
                "sample-plugin: bundled skill 'sample-plugin' requires matching "
                "ctx.register_skill(...)",
                validate_plugin(plugin_dir),
            )

    def test_register_without_ctx_parameter_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            (plugin_dir / "__init__.py").write_text(
                "def register():\n"
                "    ctx.register_skill('sample-plugin', "
                "'skills/sample-plugin/SKILL.md')\n",
                encoding="utf-8",
            )
            self.assertIn(
                "sample-plugin: __init__.py must define register(ctx)",
                validate_plugin(plugin_dir),
            )

    def test_register_with_wrong_parameter_name_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            (plugin_dir / "__init__.py").write_text(
                "def register(context):\n"
                "    context.register_skill('sample-plugin', "
                "'skills/sample-plugin/SKILL.md')\n",
                encoding="utf-8",
            )
            self.assertIn(
                "sample-plugin: __init__.py must define register(ctx)",
                validate_plugin(plugin_dir),
            )

    def test_register_skill_call_with_wrong_receiver_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            (plugin_dir / "__init__.py").write_text(
                "def register(ctx):\n"
                "    other.register_skill('sample-plugin', "
                "'skills/sample-plugin/SKILL.md')\n",
                encoding="utf-8",
            )
            self.assertIn(
                "sample-plugin: bundled skill 'sample-plugin' requires matching "
                "ctx.register_skill(...)",
                validate_plugin(plugin_dir),
            )

    def test_skill_required_scalar_rejects_yaml_block_markers(self):
        for marker in ("|", "|-", "|+", ">", ">-", ">+"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as tmpdir:
                skill_dir = write_skill(
                    Path(tmpdir), "sample-skill", description=marker
                )
                self.assertIn(
                    "sample-skill: frontmatter description must be non-empty",
                    validate_skill(skill_dir),
                )

    def test_quoted_block_marker_is_a_non_empty_yaml_string(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = write_skill(
                Path(tmpdir), "sample-skill", description='"|"'
            )

            self.assertEqual([], validate_skill(skill_dir))

    def test_hermes_required_scalars_reject_yaml_block_markers(self):
        field_errors = {
            "version": "sample-plugin: Hermes version must be a non-empty string",
            "description": "sample-plugin: Hermes description must be non-empty",
            "kind": "sample-plugin: Hermes kind must be non-empty",
        }
        for field, expected_error in field_errors.items():
            for marker in ("|", "|-", "|+", ">", ">-", ">+"):
                with self.subTest(field=field, marker=marker):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        plugin_dir = write_plugin(Path(tmpdir))
                        manifest = plugin_dir / "plugin.yaml"
                        lines = manifest.read_text(encoding="utf-8").splitlines()
                        lines = [
                            f"{field}: {marker}"
                            if line.startswith(f"{field}:")
                            else line
                            for line in lines
                        ]
                        manifest.write_text(
                            "\n".join(lines) + "\n", encoding="utf-8"
                        )

                        self.assertIn(expected_error, validate_plugin(plugin_dir))

    def test_invalid_bundled_skill_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            skill_path = plugin_dir / "skills" / "sample-plugin" / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace(
                    "description: Bundled workflow.", "description:"
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "sample-plugin: frontmatter description must be non-empty",
                validate_plugin(plugin_dir),
            )

    def test_null_codex_description_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex = json.loads(codex_path.read_text(encoding="utf-8"))
            codex["description"] = None
            codex_path.write_text(json.dumps(codex), encoding="utf-8")
            self.assertIn(
                "sample-plugin: Codex description must be non-empty",
                validate_plugin(plugin_dir),
            )

    def test_non_object_codex_manifest_fails_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex_path.write_text("[]", encoding="utf-8")
            self.assertIn(
                "sample-plugin: Codex manifest must be a JSON object",
                validate_plugin(plugin_dir),
            )

    def test_cli_json_non_object_manifest_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_dir = write_plugin(Path(tmpdir))
            codex_path = plugin_dir / ".codex-plugin" / "plugin.json"
            codex_path.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--plugin",
                    str(plugin_dir),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(1, result.returncode)
            self.assertFalse(payload["ok"])
            self.assertIn(
                "sample-plugin: Codex manifest must be a JSON object",
                payload["errors"],
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

    def test_cli_json_missing_repository_root_failure(self):
        for missing_target in ("skills", "plugins"):
            with self.subTest(missing_target=missing_target):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    skills_root = root / "skills"
                    plugins_root = root / "plugins"
                    skills_root.mkdir()
                    plugins_root.mkdir()
                    missing_root = root / f"misspelled-{missing_target}"
                    if missing_target == "skills":
                        skills_root = missing_root
                    else:
                        plugins_root = missing_root

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
                    self.assertIn(
                        f"{missing_target} root is not a directory: {missing_root}",
                        payload["errors"],
                    )


if __name__ == "__main__":
    unittest.main()
