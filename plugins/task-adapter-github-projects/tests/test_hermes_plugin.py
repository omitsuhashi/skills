import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
HERMES_MANIFEST = PLUGIN_ROOT / "plugin.yaml"
ENTRYPOINT = PLUGIN_ROOT / "__init__.py"
README = PLUGIN_ROOT / "README.md"

TOOLSETS = {
    "task_adapter__github_projects__task_query": "task-adapter-github-projects-read",
    "task_adapter__github_projects__task_preflight": "task-adapter-github-projects-write",
    "task_adapter__github_projects__task_apply": "task-adapter-github-projects-write",
}


def _load_entrypoint():
    spec = importlib.util.spec_from_file_location(
        "task_adapter_github_projects_plugin",
        ENTRYPOINT,
        submodule_search_locations=[str(PLUGIN_ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return spec.name, module


class FakeContext:
    def __init__(self):
        self.tools = []
        self.dispatch_count = 0

    def register_tool(self, **kwargs):
        self.tools.append(kwargs)

    def dispatch_tool(self, *_args, **_kwargs):
        self.dispatch_count += 1
        raise AssertionError("POTASK-016 registration and placeholders must not dispatch")


class HermesPluginTests(unittest.TestCase):
    def test_codex_and_hermes_manifests_are_coherent(self):
        codex = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))
        hermes = yaml.safe_load(HERMES_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual("task-adapter-github-projects", codex["name"])
        self.assertEqual(codex["name"], hermes["name"])
        self.assertEqual("0.1.0", codex["version"])
        self.assertEqual(codex["version"], hermes["version"])
        self.assertTrue(codex["description"].strip())
        self.assertTrue(hermes["description"].strip())
        self.assertEqual(list(TOOLSETS), hermes["provides_tools"])
        self.assertEqual(
            list(dict.fromkeys(TOOLSETS.values())), hermes["exports"]["toolsets"]
        )

    def test_register_exposes_exact_tool_trio_without_dispatch(self):
        module_name, module = _load_entrypoint()
        try:
            context = FakeContext()
            module.register(context)

            self.assertEqual(0, context.dispatch_count)
            self.assertEqual(TOOLSETS, {
                tool["name"]: tool["toolset"] for tool in context.tools
            })
            for tool in context.tools:
                with self.subTest(tool=tool["name"]):
                    self.assertEqual(tool["name"], tool["schema"]["name"])
                    self.assertTrue(callable(tool["handler"]))
                    self.assertEqual(
                        ["TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE"],
                        tool["requires_env"],
                    )
                    self.assertTrue(tool["description"].strip())
        finally:
            sys.modules.pop(module_name, None)

    def test_placeholder_handlers_fail_closed_and_reject_tool_selection(self):
        module_name, module = _load_entrypoint()
        try:
            context = FakeContext()
            module.register(context)

            for tool in context.tools:
                with self.subTest(tool=tool["name"], case="not_implemented"):
                    result = json.loads(tool["handler"]({}))
                    self.assertFalse(result["ok"])
                    self.assertEqual("blocked", result["status"])
                    self.assertEqual("adapter_not_implemented", result["error"]["code"])
                with self.subTest(tool=tool["name"], case="caller_tool"):
                    result = json.loads(
                        tool["handler"](
                            {"tool_name": "mcp__github__projects_write"}
                        )
                    )
                    self.assertFalse(result["ok"])
                    self.assertEqual("caller_tool_selection", result["error"]["code"])
            self.assertEqual(0, context.dispatch_count)
        finally:
            sys.modules.pop(module_name, None)

    def test_readme_documents_host_policy_and_non_live_boundary(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn("TASK_ADAPTER_GITHUB_PROJECTS_CONFIG_FILE", text)
        self.assertIn("task_management_only", text)
        self.assertIn("adapter_only", text)
        self.assertIn("no credentials", text.lower())
        self.assertIn("does not install", text.lower())


if __name__ == "__main__":
    unittest.main()
