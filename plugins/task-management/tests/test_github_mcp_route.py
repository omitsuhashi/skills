import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins/task-management"
REFERENCE = PLUGIN_ROOT / "skills/task-management/references/github-mcp-projects.md"
FIXTURES = PLUGIN_ROOT / "tests/fixtures/github_mcp_route"
PREFLIGHT_FIXTURE = FIXTURES / "preflight-results.json"
ADAPTER_FIXTURE = FIXTURES / "adapter-results.json"


REQUIRED_TYPED_CODES = {
    "mcp_server_missing",
    "tool_disabled",
    "auth_missing",
    "permission_failure",
    "project_not_found",
    "field_missing",
}
CANONICAL_TASK_REF_KEYS = {"backend_key", "task_ref", "task_url", "title"}

FORBIDDEN_NORMALIZED_KEYS = {
    "node_id",
    "field_id",
    "project_id",
    "repository_id",
    "owner",
    "project_number",
    "token",
    "authorization",
}
FORBIDDEN_NORMALIZED_VALUE_PATTERNS = (
    r"\bnode_id\b",
    r"\bfield_id\b",
    r"\bproject_id\b",
    r"\bproject_number\b",
    r"\brepository_id\b",
    r"\boption_id\b",
    r"\braw_id\b",
    r"\bauthorization\b",
    r"\bbearer\s+",
    r"\bghp_[A-Za-z0-9_]+",
    r"\bgithub_pat_[A-Za-z0-9_]+",
    r"\btoken\s*[:=]",
)


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def _forbidden_value_paths(value, patterns, path="$"):
    if isinstance(value, dict):
        matches = []
        for key, child in value.items():
            matches.extend(_forbidden_value_paths(child, patterns, f"{path}.{key}"))
        return matches

    if isinstance(value, list):
        matches = []
        for index, child in enumerate(value):
            matches.extend(_forbidden_value_paths(child, patterns, f"{path}[{index}]"))
        return matches

    if isinstance(value, str):
        for pattern in patterns:
            if re.search(pattern, value, flags=re.IGNORECASE):
                return [path]

    return []


class GitHubMcpRouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference_text = REFERENCE.read_text(encoding="utf-8")
        cls.preflight = _load_json(PREFLIGHT_FIXTURE)
        cls.adapter = _load_json(ADAPTER_FIXTURE)

    def test_reference_defines_external_mcp_route_without_owning_github_writes(self):
        text = self.reference_text

        self.assertIn("# GitHub MCP Projects Route", text)
        self.assertIn("external adapter route", text)
        self.assertIn("GitHub MCP Server owns GitHub Projects read/write", text)
        self.assertIn("normalizes route availability", text)
        self.assertIn("adapter results into the backend-neutral `TaskWriteResult` boundary", text)
        self.assertIn("plugin install must not register MCP servers", text)
        self.assertIn("No live smoke test is required", text)

    def test_reference_uses_canonical_backend_neutral_task_ref_shape(self):
        text = self.reference_text

        for field_name in CANONICAL_TASK_REF_KEYS:
            self.assertIn(field_name, text)

        self.assertIn("`task_ref.task_ref` value is an opaque backend-owned reference", text)
        self.assertIn("`task_ref.task_url`", text)
        self.assertNotIn("`task_ref.ref`", text)
        self.assertNotIn("`task_ref.url`", text)

    def test_preflight_can_represent_required_typed_results(self):
        results = self.preflight["preflight_results"]
        codes = {result["task_write_result"]["error"]["code"] for result in results}

        self.assertEqual(REQUIRED_TYPED_CODES, codes)

        for result in results:
            task_write_result = result["task_write_result"]
            self.assertEqual("TaskWriteResult", task_write_result["result_type"])
            self.assertFalse(task_write_result["ok"])
            self.assertEqual("blocked", task_write_result["status"])
            self.assertEqual("github_projects_mcp", task_write_result["backend_key"])
            self.assertIsNone(task_write_result["task_ref"])
            self.assertEqual(result["case"], task_write_result["error"]["code"])
            self.assertIsInstance(task_write_result["error"]["human_action"], str)
            self.assertTrue(task_write_result["error"]["human_action"])

    def test_adapter_result_fixture_normalizes_to_task_write_result_shape(self):
        cases = self.adapter["adapter_results"]
        self.assertGreaterEqual(len(cases), 1)

        for case in cases:
            adapter_result = case["adapter_result"]
            task_write_result = case["task_write_result"]

            self.assertTrue(adapter_result["ok"])
            self.assertEqual("TaskWriteResult", task_write_result["result_type"])
            self.assertTrue(task_write_result["ok"])
            self.assertEqual(adapter_result["operation_type"], task_write_result["operation_type"])
            self.assertEqual(adapter_result["backend_key"], task_write_result["backend_key"])
            self.assertEqual(adapter_result["destination_ref"], task_write_result["destination_ref"])
            self.assertEqual(CANONICAL_TASK_REF_KEYS, set(task_write_result["task_ref"]))
            self.assertEqual(adapter_result["backend_key"], task_write_result["task_ref"]["backend_key"])
            self.assertEqual(adapter_result["adapter_ref"], task_write_result["task_ref"]["task_ref"])
            self.assertEqual(adapter_result["url"], task_write_result["task_ref"]["task_url"])
            self.assertIsNone(task_write_result["error"])

    def test_normalized_task_write_result_does_not_expose_provider_raw_ids_or_auth(self):
        normalized_results = [
            *(result["task_write_result"] for result in self.preflight["preflight_results"]),
            *(result["task_write_result"] for result in self.adapter["adapter_results"]),
        ]

        for normalized in normalized_results:
            for item in _walk_dicts(normalized):
                self.assertTrue(FORBIDDEN_NORMALIZED_KEYS.isdisjoint(item.keys()))
            self.assertEqual(
                [],
                _forbidden_value_paths(normalized, FORBIDDEN_NORMALIZED_VALUE_PATTERNS),
            )

    def test_forbidden_value_scan_covers_normalized_raw_id_and_auth_leaks(self):
        normalized = {
            "result_type": "TaskWriteResult",
            "ok": True,
            "task_ref": {
                "backend_key": "github_projects_mcp",
                "task_ref": "external_ref",
                "task_url": "https://example.invalid/tasks/1",
                "title": "Task",
            },
            "error": {
                "code": "blocked",
                "message": "field_id: must-not-leak",
            },
        }

        self.assertEqual(
            ["$.error.message"],
            _forbidden_value_paths(normalized, FORBIDDEN_NORMALIZED_VALUE_PATTERNS),
        )

    def test_plugin_contains_no_live_github_client_command_planner_or_graphql_query(self):
        scanned_paths = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file() and ".codex-plugin" not in path.relative_to(PLUGIN_ROOT).parts
        ]

        implementation_suffixes = {".py", ".js", ".ts", ".sh"}
        implementation_files = [
            path.relative_to(PLUGIN_ROOT).as_posix()
            for path in scanned_paths
            if path.suffix in implementation_suffixes and "tests" not in path.relative_to(PLUGIN_ROOT).parts
        ]
        self.assertEqual([], implementation_files)

        combined_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in scanned_paths
            if path.suffix in {".md", ".json", ".toml", ".yaml", ".yml"}
        )
        forbidden_live_patterns = (
            r"\bgh\s+api\b",
            r"\bgh\s+project\b",
            r"\bmutation\s+[A-Za-z_]*\s*\{",
            r"\bquery\s+[A-Za-z_]*\s*\{",
        )
        for pattern in forbidden_live_patterns:
            self.assertIsNone(re.search(pattern, combined_text))


if __name__ == "__main__":
    unittest.main()
