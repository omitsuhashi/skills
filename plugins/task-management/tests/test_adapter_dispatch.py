import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins/task-management"
SKILL = PLUGIN_ROOT / "skills/task-management/SKILL.md"
REFERENCE = PLUGIN_ROOT / "skills/task-management/references/adapter-dispatch.md"
EXAMPLE = PLUGIN_ROOT / "examples/task-create-preview.example.md"
IMPLEMENTATION_SUFFIXES = {".py", ".js", ".ts", ".sh"}
FORBIDDEN_IMPLEMENTATION_PATTERNS = (
    r"\b(?:import|from)\s+(?:requests|httpx|aiohttp|urllib3|urllib\.request|http\.client)\b",
    r"\b(?:import|from)\s+(?:github(?:\.[A-Za-z_][A-Za-z0-9_]*)*|githubkit(?:\.[A-Za-z_][A-Za-z0-9_]*)*|task_adapter_github_projects(?:\.[A-Za-z_][A-Za-z0-9_]*)*)\b",
    r"\bfrom\s+urllib\s+import\s+request\b",
    r"\bfrom\s+http\s+import\s+client\b",
    r"(?:api\.github\.com|/graphql)\b",
    r"\b(?:mutation|query)\s+[A-Za-z_]*\s*\{",
    r"[\"']gh[\"']",
)


def _implementation_paths():
    return [
        path
        for path in PLUGIN_ROOT.rglob("*")
        if path.is_file()
        and "tests" not in path.relative_to(PLUGIN_ROOT).parts
        and ".codex-plugin" not in path.relative_to(PLUGIN_ROOT).parts
        and path.suffix in IMPLEMENTATION_SUFFIXES
    ]


def _forbidden_implementation_matches(text):
    return tuple(
        pattern
        for pattern in FORBIDDEN_IMPLEMENTATION_PATTERNS
        if re.search(pattern, text)
    )


class AdapterDispatchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.reference_text = REFERENCE.read_text(encoding="utf-8") if REFERENCE.exists() else ""
        cls.example_text = EXAMPLE.read_text(encoding="utf-8")

    def test_skill_entrypoint_references_adapter_dispatch_contract(self):
        self.assertIn("references/adapter-dispatch.md", self.skill_text)

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
            "adapter_contract_version: 2",
            "operation_type",
            "backend_key",
            "destination_ref",
            "task_ref",
            "payload",
        ):
            self.assertIn(f"`{field_name}`", text)
        for caller_forbidden in ("route/config paths", "adapter/MCP", "tool names"):
            self.assertIn(caller_forbidden, text)

    def test_existing_task_operations_require_task_ref_and_review_match(self):
        text = self.reference_text

        for operation_type in ("task.update", "task.comment", "task.report"):
            self.assertRegex(
                text,
                rf"\| `{operation_type}` \| required opaque backend-owned task reference",
            )

        self.assertIn("opaque backend-owned task reference", text)
        self.assertIn("Any operation, destination", text)

    def test_adapter_dispatch_review_is_required_before_dispatch(self):
        text = self.reference_text

        self.assertIn("## Preflight and review guard", text)
        self.assertIn("decision: approved", text)
        self.assertIn("decision: confidence_authorized", text)
        self.assertIn("ready,", text)
        self.assertIn("confidence-eligible", text)
        self.assertIn("certain", text)

    def test_dispatch_approval_is_separate_from_readiness_gate(self):
        text = self.reference_text

        self.assertIn("readiness", text)
        self.assertIn("not\napproval", text)
        self.assertIn("must not replace human review", text)

    def test_preview_example_contains_reviewable_envelope_and_guard(self):
        text = self.example_text

        self.assertIn("## Public operation", text)
        self.assertIn("interface_version: 2", text)
        self.assertIn("adapter_contract_version: 2", text)
        self.assertIn('operation_type: "task.create"', text)
        self.assertIn('backend_key: "remote_tasks"', text)
        self.assertIn('destination_ref: "tasks:portfolio-os"', text)
        self.assertIn("approval_preview:", text)
        self.assertIn('decision: "approved"', text)
        self.assertIn("operation_digest:", text)

    def test_implementation_guard_scans_root_runtime_entrypoint(self):
        relative_paths = {
            path.relative_to(PLUGIN_ROOT).as_posix()
            for path in _implementation_paths()
        }

        self.assertIn("__init__.py", relative_paths)

    def test_implementation_guard_rejects_provider_and_separate_adapter_imports(self):
        forbidden_snippets = (
            "from github import Github",
            "import githubkit",
            "from task_adapter_github_projects import GithubProjectsAdapter",
            'endpoint = "/graphql"',
        )

        for snippet in forbidden_snippets:
            with self.subTest(snippet=snippet):
                self.assertTrue(_forbidden_implementation_matches(snippet))

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

        implementation_paths = _implementation_paths()
        implementation_files = [
            path.relative_to(PLUGIN_ROOT).as_posix()
            for path in implementation_paths
        ]
        required_implementation_files = {
            "task_management/__init__.py",
            "task_management/contracts.py",
            "task_management/read_adapter.py",
            "task_management/route_config.py",
            "task_management/safety.py",
            "task_management/provider_adapters/__init__.py",
            "task_management/provider_adapters/local_json.py",
            "task_management/provider_adapters/external_tool.py",
            "scripts/smoke_test_hermes_read.py",
        }
        self.assertTrue(
            required_implementation_files.issubset(set(implementation_files)),
            "required backend-neutral implementation files must remain present",
        )

        combined_implementation = "\n".join(
            path.read_text(encoding="utf-8") for path in implementation_paths
        )
        for pattern in FORBIDDEN_IMPLEMENTATION_PATTERNS:
            self.assertIsNone(re.search(pattern, combined_implementation))


if __name__ == "__main__":
    unittest.main()
