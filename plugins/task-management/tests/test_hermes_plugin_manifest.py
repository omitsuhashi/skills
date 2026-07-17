import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugin.yaml"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
ENTRYPOINT = ROOT / "__init__.py"
README = ROOT / "README.md"
SKILL = ROOT / "skills" / "task-management" / "SKILL.md"
SMOKE = ROOT / "scripts" / "smoke_test_hermes_read.py"


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
        self.assertEqual("0.3.0", manifest.get("version"))
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

    def test_native_manifest_exports_exact_read_toolset(self):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        codex_manifest = __import__("json").loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

        self.assertIn("provides_tools", manifest)
        self.assertIn("exports", manifest)
        self.assertEqual("0.3.0", codex_manifest["version"])
        self.assertEqual(codex_manifest["version"], manifest["version"])
        self.assertEqual(["task_query"], manifest["provides_tools"])
        self.assertEqual(
            {"toolsets": ["task-management-read"]},
            manifest["exports"],
        )

    def test_native_entrypoint_registers_read_only_task_query_tool(self):
        spec = importlib.util.spec_from_file_location(
            "task_management_plugin",
            ENTRYPOINT,
            submodule_search_locations=[str(ROOT)],
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)

            class FakeContext:
                def __init__(self):
                    self.skills = []
                    self.tools = []

                def register_skill(self, *args, **kwargs):
                    self.skills.append((args, kwargs))

                def register_tool(self, **kwargs):
                    self.tools.append(kwargs)

                def dispatch_tool(self, *_args, **_kwargs):
                    raise AssertionError("registration must not dispatch")

            ctx = FakeContext()
            with patch.dict(os.environ, {}, clear=True):
                module.register(ctx)

            self.assertEqual(1, len(ctx.tools))
            registration = ctx.tools[0]
            self.assertEqual("task_query", registration["name"])
            self.assertEqual("task-management-read", registration["toolset"])
            self.assertEqual("task_query", registration["schema"]["name"])
            self.assertTrue(callable(registration["handler"]))
            self.assertEqual([], registration["requires_env"])
        finally:
            sys.modules.pop(spec.name, None)

    def test_hermes_install_docs_describe_subdir_update_limitation(self):
        self.assertTrue(README.exists(), "Hermes plugin package needs install/update notes")

        text = README.read_text(encoding="utf-8")

        self.assertIn("hermes plugins install", text)
        self.assertIn("git@github.com:omitsuhashi/skills.git#plugins/task-management", text)
        self.assertIn("hermes plugins enable task-management", text)
        self.assertIn("hermes plugins update task-management", text)
        self.assertIn(".git", text)
        self.assertIn("hermes plugins install --force", text)
        self.assertIn(
            "hermes skills install omitsuhashi/skills/skills/decide-in-order",
            text,
        )
        self.assertIn("hermes skills list", text)
        self.assertIn("hermes plugins list --plain --no-bundled", text)
        self.assertIn("must match `plugin.yaml`", text)
        self.assertIn("Mechanical task operations continue", text)

    def test_smoke_uses_real_hermes_context_and_registry_dispatch(self):
        self.assertTrue(SMOKE.is_file())
        text = SMOKE.read_text(encoding="utf-8")
        self.assertIn("PluginContext", text)
        self.assertIn("registry.dispatch", text)


if __name__ == "__main__":
    unittest.main()
