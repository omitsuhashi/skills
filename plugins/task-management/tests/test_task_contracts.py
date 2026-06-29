import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
CONTRACT_DOC = ROOT / "skills" / "task-management" / "references" / "task-contracts.md"
PROVIDER_RAW_ID_OR_AUTH_KEYS = {
    "node_id",
    "project_id",
    "project_number",
    "repository_id",
    "field_id",
    "option_id",
    "raw_id",
    "token",
}
PROVIDER_RAW_ID_OR_AUTH_VALUE_PATTERNS = (
    r"\bnode_id\b",
    r"\bproject_id\b",
    r"\bproject_number\b",
    r"\brepository_id\b",
    r"\bfield_id\b",
    r"\boption_id\b",
    r"\braw_id\b",
    r"\bauthorization\b",
    r"\bbearer\s+",
    r"\bghp_[A-Za-z0-9_]+",
    r"\bgithub_pat_[A-Za-z0-9_]+",
    r"\btoken\s*[:=]",
)


def forbidden_key_paths(payload, forbidden_keys, path="$"):
    if isinstance(payload, dict):
        matches = []
        for key, value in payload.items():
            child_path = f"{path}.{key}"
            if key in forbidden_keys:
                matches.append(child_path)
            matches.extend(forbidden_key_paths(value, forbidden_keys, child_path))
        return matches

    if isinstance(payload, list):
        matches = []
        for index, value in enumerate(payload):
            matches.extend(forbidden_key_paths(value, forbidden_keys, f"{path}[{index}]"))
        return matches

    return []


def forbidden_value_paths(payload, forbidden_patterns, path="$"):
    if isinstance(payload, dict):
        matches = []
        for key, value in payload.items():
            matches.extend(forbidden_value_paths(value, forbidden_patterns, f"{path}.{key}"))
        return matches

    if isinstance(payload, list):
        matches = []
        for index, value in enumerate(payload):
            matches.extend(forbidden_value_paths(value, forbidden_patterns, f"{path}[{index}]"))
        return matches

    if isinstance(payload, str):
        for pattern in forbidden_patterns:
            if re.search(pattern, payload, flags=re.IGNORECASE):
                return [path]

    return []


class TaskContractFixtureTests(unittest.TestCase):
    def load_fixture(self, name):
        with (FIXTURES / name).open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_task_draft_exposes_required_backend_neutral_fields(self):
        draft = self.load_fixture("task-draft.example.json")

        self.assertEqual(
            {
                "title",
                "body",
                "work_unit_id",
                "work_unit_name",
                "task_type",
                "due_date",
                "urgency",
                "importance",
                "automation_mode",
                "approval_required",
                "source_ref",
                "fields",
            },
            set(draft),
        )
        self.assertEqual("implementation", draft["task_type"])
        self.assertIn(draft["urgency"], {"low", "normal", "high", "blocked"})
        self.assertIn(draft["importance"], {"low", "normal", "high", "critical"})
        self.assertIn(
            draft["automation_mode"],
            {"manual_only", "assistive", "trusted_after_approval"},
        )
        self.assertIsInstance(draft["approval_required"], bool)
        self.assertEqual({"kind", "ref", "label"}, set(draft["source_ref"]))

    def test_route_and_destination_keep_backend_target_separate(self):
        route = self.load_fixture("backend-route.example.json")
        destination = self.load_fixture("backend-destination.example.json")

        self.assertEqual("github_projects_mcp", destination["backend_key"])
        self.assertEqual(
            {"backend_key", "destination_ref", "destination_label", "content_target_ref"},
            set(destination),
        )
        self.assertEqual({"kind", "connection_ref", "capability", "field_overrides"}, set(route))
        self.assertIn(route["kind"], {"mcp", "reader", "skill", "cli", "url"})
        self.assertNotIn("owner", route)
        self.assertNotIn("project_number", route)
        self.assertNotIn("repository", route)
        self.assertNotIn("token", route)

    def test_task_refs_do_not_expose_provider_raw_ids(self):
        task_ref = self.load_fixture("task-ref.example.json")
        snapshot = self.load_fixture("task-snapshot.example.json")

        for name, payload in {"TaskRef": task_ref, "TaskSnapshot": snapshot}.items():
            with self.subTest(name=name):
                self.assertEqual(
                    [],
                    forbidden_key_paths(payload, PROVIDER_RAW_ID_OR_AUTH_KEYS),
                )
                self.assertEqual(
                    [],
                    forbidden_value_paths(payload, PROVIDER_RAW_ID_OR_AUTH_VALUE_PATTERNS),
                )

        self.assertEqual({"backend_key", "task_ref", "task_url", "title"}, set(task_ref))
        self.assertEqual("external_ref", snapshot["task_ref"]["task_ref"])
        self.assertEqual({"display_link"}, set(snapshot["backend_metadata"]))
        self.assertEqual({"name", "url"}, set(snapshot["backend_metadata"]["display_link"]))

    def test_forbidden_key_scan_covers_nested_backend_metadata(self):
        payload = {
            "task_ref": {"task_ref": "external_ref"},
            "backend_metadata": {
                "display_link": {"name": "Task", "url": "https://example.invalid/tasks/1"},
                "provider_payload": {"field_id": "must-not-leak"},
            },
        }

        self.assertEqual(
            ["$.backend_metadata.provider_payload.field_id"],
            forbidden_key_paths(payload, PROVIDER_RAW_ID_OR_AUTH_KEYS),
        )

    def test_forbidden_value_scan_covers_normalized_provider_raw_ids(self):
        payload = {
            "task_ref": {
                "task_ref": "external_ref",
                "url": "https://example.invalid/tasks/1",
            },
            "backend_metadata": {
                "provider_payload": {
                    "safe_key": "field_id: must-not-leak",
                },
            },
        }

        self.assertEqual(
            ["$.backend_metadata.provider_payload.safe_key"],
            forbidden_value_paths(payload, PROVIDER_RAW_ID_OR_AUTH_VALUE_PATTERNS),
        )

    def test_query_and_write_result_stay_backend_neutral(self):
        query = self.load_fixture("task-query.example.json")
        result = self.load_fixture("task-write-result.example.json")

        self.assertEqual(
            {"backend_key", "work_unit_id", "task_type", "status", "due_before", "limit"},
            set(query),
        )
        self.assertEqual(
            {
                "result_type",
                "ok",
                "status",
                "operation_type",
                "backend_key",
                "destination_ref",
                "task_ref",
                "error",
            },
            set(result),
        )
        self.assertEqual("TaskWriteResult", result["result_type"])
        self.assertTrue(result["ok"])
        self.assertEqual("created", result["status"])
        self.assertIsNone(result["error"])
        self.assertEqual("external_ref", result["task_ref"]["task_ref"])

    def test_reference_document_names_contracts_and_forbids_clients(self):
        doc = CONTRACT_DOC.read_text(encoding="utf-8")
        normalized_doc = " ".join(doc.split())

        for contract_name in (
            "TaskDraft",
            "TaskRef",
            "TaskQuery",
            "TaskSnapshot",
            "TaskWriteResult",
            "TaskBackendRoute",
            "TaskBackendDestination",
        ):
            self.assertIn(contract_name, doc)

        for forbidden_phrase in (
            "direct GraphQL client",
            "gh command planner",
            "provider-specific raw IDs",
            "credentials",
            "`task_sha`",
            "duplicate-prevention store",
            "local task ledger",
        ):
            self.assertIn(forbidden_phrase, normalized_doc)

        self.assertIn("first backend route", normalized_doc)
        self.assertIn("not a permanent architecture", normalized_doc)


if __name__ == "__main__":
    unittest.main()
