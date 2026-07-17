import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugin.yaml"
CODEX_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
ENTRYPOINT = ROOT / "__init__.py"
README = ROOT / "README.md"
SKILL = ROOT / "skills" / "task-management" / "SKILL.md"
SMOKE = ROOT / "scripts" / "smoke_test_hermes_read.py"

TOP_LEVEL_SCALARS = {
    "manifest_version",
    "name",
    "version",
    "description",
    "author",
    "kind",
}
REQUIRED_MANIFEST_FIELDS = TOP_LEVEL_SCALARS | {
    "provides_tools",
    "exports",
    "exports.toolsets",
}

def _manifest_error(line_number, message):
    raise ValueError(f"plugin.yaml line {line_number}: {message}")


def _parse_manifest_value(line_number, value):
    value = value.strip()
    if not value:
        _manifest_error(line_number, "value must be non-empty")
    if value[0] in {'"', "'"}:
        if len(value) < 2 or value[-1] != value[0]:
            _manifest_error(line_number, "quoted value must be closed")
        return value[1:-1]
    return value


def parse_task_management_manifest(path):
    manifest = {}
    provides_tools = []
    toolsets = []
    seen = set()
    state = "top"

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "\t" in raw_line:
            _manifest_error(line_number, "tabs are not allowed")
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if state == "top":
            if indent != 0:
                _manifest_error(line_number, "top-level content must be unindented")
            if stripped == "provides_tools:":
                if "provides_tools" in seen:
                    _manifest_error(line_number, "duplicate provides_tools section")
                seen.add("provides_tools")
                state = "provides_tools"
                continue
            if stripped == "exports:":
                if "exports" in seen:
                    _manifest_error(line_number, "duplicate exports section")
                seen.add("exports")
                state = "exports"
                continue
            if ":" not in stripped:
                _manifest_error(line_number, "unexpected top-level line")
            key, value = stripped.split(":", 1)
            if key not in TOP_LEVEL_SCALARS:
                _manifest_error(line_number, f"unexpected top-level key {key!r}")
            if key in seen:
                _manifest_error(line_number, f"duplicate key {key!r}")
            seen.add(key)
            manifest[key] = _parse_manifest_value(line_number, value)
            continue

        if state == "provides_tools":
            if indent == 2 and stripped.startswith("- "):
                provides_tools.append(
                    _parse_manifest_value(line_number, stripped[2:])
                )
                continue
            if indent == 0 and stripped == "provides_tools:":
                _manifest_error(line_number, "duplicate provides_tools section")
            if indent == 0 and stripped == "exports:":
                if "exports" in seen:
                    _manifest_error(line_number, "duplicate exports section")
                seen.add("exports")
                state = "exports"
                continue
            _manifest_error(line_number, "invalid provides_tools content")

        if state == "exports":
            if indent != 2 or stripped != "toolsets:":
                _manifest_error(line_number, "exports requires indented toolsets")
            if "exports.toolsets" in seen:
                _manifest_error(line_number, "duplicate exports.toolsets section")
            seen.add("exports.toolsets")
            state = "toolsets"
            continue

        if state == "toolsets":
            if indent == 4 and stripped.startswith("- "):
                toolsets.append(_parse_manifest_value(line_number, stripped[2:]))
                continue
            if indent == 0 and stripped == "exports:":
                _manifest_error(line_number, "duplicate exports section")
            _manifest_error(line_number, "invalid exports.toolsets content")

    missing = sorted(REQUIRED_MANIFEST_FIELDS - seen)
    if missing:
        raise ValueError(f"plugin.yaml missing required fields: {', '.join(missing)}")
    if not provides_tools:
        raise ValueError("plugin.yaml provides_tools must be non-empty")
    if not toolsets:
        raise ValueError("plugin.yaml exports.toolsets must be non-empty")
    manifest["provides_tools"] = provides_tools
    manifest["exports"] = {"toolsets": toolsets}
    return manifest


def parse_manifest_text(text):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "plugin.yaml"
        path.write_text(text, encoding="utf-8")
        return parse_task_management_manifest(path)


class HermesPluginManifestTests(unittest.TestCase):
    def test_manifest_parser_rejects_invalid_trailing_content(self):
        valid = MANIFEST.read_text(encoding="utf-8")
        for trailing in ("not yaml\n", "unexpected: value\n"):
            with self.subTest(trailing=trailing):
                with self.assertRaises(ValueError):
                    parse_manifest_text(valid + trailing)

    def test_manifest_parser_rejects_duplicate_key_and_section(self):
        valid = MANIFEST.read_text(encoding="utf-8")
        cases = {
            "key": valid.replace(
                "name: task-management\n",
                "name: task-management\nname: duplicate\n",
            ),
            "section": valid.replace(
                "provides_tools:\n",
                "provides_tools:\n  - task_query\nprovides_tools:\n",
            ),
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(ValueError):
                    parse_manifest_text(text)

    def test_manifest_parser_rejects_invalid_indentation(self):
        text = MANIFEST.read_text(encoding="utf-8").replace(
            "  - task_query\n", "   - task_query\n"
        )

        with self.assertRaises(ValueError):
            parse_manifest_text(text)

    def test_manifest_parser_rejects_missing_required_field(self):
        text = MANIFEST.read_text(encoding="utf-8").replace(
            "author: Omitsuhashi\n", ""
        )

        with self.assertRaises(ValueError):
            parse_manifest_text(text)

    def test_native_hermes_manifest_exists_with_supported_kind(self):
        self.assertTrue(MANIFEST.exists(), "Hermes native plugins require plugin.yaml")

        manifest = parse_task_management_manifest(MANIFEST)

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
        manifest = parse_task_management_manifest(MANIFEST)
        codex_manifest = __import__("json").loads(CODEX_MANIFEST.read_text(encoding="utf-8"))

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

            self.assertEqual(1, len(ctx.skills))
            skill_args, skill_kwargs = ctx.skills[0]
            self.assertEqual(2, len(skill_args))
            self.assertEqual("task-management", skill_args[0])
            self.assertEqual(SKILL.resolve(), Path(skill_args[1]).resolve())
            self.assertEqual(
                "Backend-neutral task intake and task backend routing workflow.",
                skill_kwargs["description"],
            )
            self.assertTrue(skill_kwargs["description"].strip())
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
