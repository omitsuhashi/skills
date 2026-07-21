import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = PLUGIN_ROOT / "config" / "github-projects.example.toml"
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.config import (  # noqa: E402
    CANONICAL_FIELD_KEYS,
    CONFIG_CONTRACT_VERSION,
    MCP_TOOL_ALLOWLIST,
    ConfigError,
    load_config,
)


class GithubProjectsConfigTests(unittest.TestCase):
    def setUp(self):
        self.example_text = EXAMPLE.read_text(encoding="utf-8")

    def load_text(self, text):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.toml"
            path.write_text(text, encoding="utf-8")
            return load_config(path)

    def assert_config_error(self, text, code):
        with self.assertRaises(ConfigError) as raised:
            self.load_text(text)
        self.assertEqual(code, raised.exception.code)

    def test_example_has_exact_tools_attestation_and_canonical_mappings(self):
        config = load_config(EXAMPLE)

        self.assertEqual(1, CONFIG_CONTRACT_VERSION)
        self.assertEqual(MCP_TOOL_ALLOWLIST, config.mcp_tools)
        self.assertEqual(
            "adapter_only", config.host_attestation["raw_mcp_exposure"]
        )
        self.assertEqual(
            "task_management_only",
            config.host_attestation["adapter_write_exposure"],
        )
        self.assertEqual(CANONICAL_FIELD_KEYS, set(config.field_mappings))

    def test_resolves_only_configured_opaque_refs(self):
        config = load_config(EXAMPLE)

        destination = config.resolve_destination("tasks:portfolio-os")
        self.assertEqual("example-owner", destination.owner)
        self.assertEqual(7, destination.project_number)
        content_target = config.resolve_content_target("task-content:portfolio-os")
        self.assertEqual("example-owner", content_target.owner)
        self.assertEqual("example-repository", content_target.repository)

        for lookup, value in (
            (config.resolve_destination, "tasks:unknown"),
            (config.resolve_content_target, "task-content:unknown"),
        ):
            with self.subTest(value=value):
                with self.assertRaises(ConfigError) as raised:
                    lookup(value)
                self.assertEqual("destination_unresolved", raised.exception.code)

    def test_rejects_credentials_and_non_allowlisted_mcp_tools(self):
        credential = self.example_text.replace(
            '[mcp_tools]\n', '[mcp_tools]\ntoken = "redacted"\n', 1
        )
        self.assert_config_error(credential, "unsafe_data")

        arbitrary_tool = self.example_text.replace(
            'projects_write = "mcp__github__projects_write"',
            'projects_write = "mcp__github__delete_everything"',
            1,
        )
        self.assert_config_error(arbitrary_tool, "invalid_mcp_tool_allowlist")

    def test_rejects_unknown_config_shape_and_unsafe_delegation(self):
        unknown = self.example_text.replace(
            "contract_version = 1\n",
            "contract_version = 1\ncaller_tool_name = \"mcp__github__projects_write\"\n",
            1,
        )
        self.assert_config_error(unknown, "invalid_config")

        unsafe_exposure = self.example_text.replace(
            'adapter_write_exposure = "task_management_only"',
            'adapter_write_exposure = "model_visible"',
            1,
        )
        self.assert_config_error(
            unsafe_exposure, "unsafe_delegation_exposure"
        )


if __name__ == "__main__":
    unittest.main()
