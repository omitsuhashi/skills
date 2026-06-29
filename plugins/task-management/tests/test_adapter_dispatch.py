import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins/task-management"
REFERENCE = PLUGIN_ROOT / "skills/task-management/references/adapter-dispatch.md"
EXAMPLE = PLUGIN_ROOT / "examples/task-create-preview.example.md"


class AdapterDispatchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference_text = REFERENCE.read_text(encoding="utf-8") if REFERENCE.exists() else ""
        cls.example_text = EXAMPLE.read_text(encoding="utf-8")

    def test_reference_defines_adapter_neutral_operation_envelope(self):
        text = self.reference_text

        self.assertTrue(REFERENCE.exists(), "adapter dispatch reference must exist")
        self.assertIn("# Adapter Dispatch Contract", text)
        self.assertIn("adapter-neutral operation envelope", text)

        for operation_type in ("task.create", "task.update", "task.comment", "task.report"):
            self.assertIn(operation_type, text)

    def test_envelope_includes_required_dispatch_fields(self):
        text = self.reference_text

        for field_name in (
            "backend_key",
            "connection_ref",
            "destination_ref",
            "destination_label",
            "operation_type",
            "task.title",
            "task.body",
            "task.fields",
            "work_unit_id",
            "work_unit_name",
            "adapter_tool_name",
            "expected_adapter_side_effects",
        ):
            self.assertIn(f"`{field_name}`", text)

    def test_adapter_dispatch_review_is_required_before_dispatch(self):
        text = self.reference_text

        self.assertIn("## Adapter Dispatch Review Guard", text)
        self.assertIn("Do not pass an envelope to an adapter until Adapter Dispatch Review is complete.", text)
        self.assertIn("review_status: approved", text)
        self.assertIn("approved_operation_type", text)
        self.assertIn("approved_adapter_tool_name", text)
        self.assertIn("approved_destination_ref", text)

    def test_preview_example_contains_reviewable_envelope_and_guard(self):
        text = self.example_text

        self.assertIn("## Adapter Operation Envelope Preview", text)
        self.assertIn('operation_type: "task.create"', text)
        self.assertIn('backend_key: "github_projects_mcp"', text)
        self.assertIn('connection_ref: "github-projects"', text)
        self.assertIn('destination_ref: "github-projects:portfolio-os-task-board"', text)
        self.assertIn('destination_label: "Portfolio OS Tasks"', text)
        self.assertIn('adapter_tool_name: "github-projects:task-create"', text)
        self.assertIn("expected_adapter_side_effects:", text)
        self.assertIn("Adapter Dispatch Review: required", text)
        self.assertIn("Do not dispatch until review_status is approved.", text)

    def test_plugin_does_not_add_adapter_implementation_or_backend_clients(self):
        forbidden_name_parts = (
            "graphql",
            "gh_planner",
            "github_adapter",
            "github_projects_commands",
            "backend_client",
            "retry_policy",
            "task_sha",
        )

        scanned_paths = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
            and "tests" not in path.relative_to(PLUGIN_ROOT).parts
            and ".codex-plugin" not in path.relative_to(PLUGIN_ROOT).parts
        ]

        for path in scanned_paths:
            relative_name = path.relative_to(PLUGIN_ROOT).as_posix().lower()
            for forbidden in forbidden_name_parts:
                self.assertNotIn(forbidden, relative_name)

        implementation_suffixes = {".py", ".js", ".ts", ".sh"}
        implementation_files = [
            path.relative_to(PLUGIN_ROOT).as_posix()
            for path in scanned_paths
            if path.suffix in implementation_suffixes
        ]

        self.assertEqual([], implementation_files)


if __name__ == "__main__":
    unittest.main()
