import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "config" / "github-projects.example.toml"
CREATE_OPERATION = (
    PLUGIN_ROOT
    / "tests"
    / "fixtures"
    / "adapter-v2"
    / "accept"
    / "operation-create.json"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.adapter import GithubProjectsAdapter  # noqa: E402
from task_adapter_github_projects.config import load_config  # noqa: E402


PROJECT_FIELDS = [
    {"id": 9101, "name": "Work Unit ID", "data_type": "text"},
    {"id": 9102, "name": "Work Unit", "data_type": "text"},
    {"id": 9103, "name": "Task Type", "data_type": "single_select"},
    {"id": 9104, "name": "Due Date", "data_type": "date"},
    {"id": 9105, "name": "Urgency", "data_type": "single_select"},
    {"id": 9106, "name": "Importance", "data_type": "single_select"},
    {"id": 9107, "name": "Automation Mode", "data_type": "single_select"},
    {"id": 9108, "name": "Approval Required", "data_type": "single_select"},
    {"id": 9109, "name": "Source", "data_type": "text"},
    {"id": 9110, "name": "Source URL", "data_type": "text"},
]


def public_success(payload, *, include_structured_content=False):
    envelope = {"result": json.dumps(payload, ensure_ascii=False)}
    if include_structured_content:
        envelope["structuredContent"] = payload
    return json.dumps(envelope, ensure_ascii=False)


def public_error(message):
    return json.dumps({"error": message}, ensure_ascii=False)


class GithubProjectsPreflightTests(unittest.TestCase):
    def test_create_preflight_uses_only_read_probes_and_returns_readiness_not_approval(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            method = arguments["method"]
            if method == "get_project":
                return public_success(
                    {
                        "id": "PVT_private",
                        "number": 7,
                        "title": "Portfolio OS Tasks",
                        "owner": {"login": "example-owner"},
                    }
                )
            if method == "list_project_fields":
                return public_success(
                    {
                        "fields": PROJECT_FIELDS,
                        "pageInfo": {"hasNextPage": False, "nextCursor": None},
                    },
                    include_structured_content=True,
                )
            if method == "list_project_items":
                return public_success(
                    {
                        "items": [],
                        "pageInfo": {"hasNextPage": False, "nextCursor": None},
                    }
                )
            self.fail(f"unexpected provider method: {method}")

        adapter = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        )
        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"
        result = adapter.preflight(
            {
                "adapter_contract_version": 2,
                "operation": operation,
                "destination_label": "Portfolio OS Tasks",
                "content_target_ref": "task-content:portfolio-os",
                "required_capability": "task.create",
            }
        )

        self.assertEqual(
            [
                "mcp__github__projects_get",
                "mcp__github__projects_list",
                "mcp__github__projects_list",
            ],
            [tool_name for tool_name, _arguments in calls],
        )
        self.assertEqual(
            ["get_project", "list_project_fields", "list_project_items"],
            [arguments["method"] for _tool_name, arguments in calls],
        )
        self.assertTrue(result["ok"])
        self.assertNotIn("status", result)
        self.assertTrue(result["readiness"]["ok"])
        self.assertEqual(
            [
                "content.create",
                "destination.attach",
                "fields.update",
                "task.read_back",
            ],
            [effect["effect_type"] for effect in result["expected_side_effects"]],
        )
        self.assertTrue(result["requires_human_confirmation"])
        self.assertNotIn("approval_preview", result)
        self.assertNotIn("approval_digest", result)
        self.assertNotIn("approved", result)

    def test_preflight_accepts_all_exact_lowercase_official_field_types(self):
        self.assertEqual(
            {"text", "date", "single_select"},
            {field["data_type"] for field in PROJECT_FIELDS},
        )

        def dispatch(_tool_name, arguments):
            if arguments["method"] == "get_project":
                return public_success(
                    {
                        "number": 7,
                        "title": "Portfolio OS Tasks",
                        "owner": {"login": "example-owner"},
                    }
                )
            if arguments["method"] == "list_project_fields":
                return public_success(
                    {
                        "fields": PROJECT_FIELDS,
                        "pageInfo": {"hasNextPage": False, "nextCursor": None},
                    }
                )
            return public_success(
                {
                    "items": [],
                    "pageInfo": {"hasNextPage": False, "nextCursor": None},
                }
            )

        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"
        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).preflight(
            {
                "adapter_contract_version": 2,
                "operation": operation,
                "destination_label": "Portfolio OS Tasks",
                "content_target_ref": "task-content:portfolio-os",
                "required_capability": "task.create",
            }
        )

        self.assertTrue(result["ok"])

    def test_preflight_follows_bounded_field_pagination(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if arguments["method"] == "get_project":
                return public_success(
                    {
                        "number": 7,
                        "title": "Portfolio OS Tasks",
                        "owner": {"login": "example-owner"},
                    }
                )
            if arguments["method"] == "list_project_fields":
                if arguments.get("after") is None:
                    return public_success(
                        {
                            "fields": PROJECT_FIELDS[:5],
                            "pageInfo": {
                                "hasNextPage": True,
                                "nextCursor": "fields-page-2",
                            },
                        }
                    )
                return public_success(
                    {
                        "fields": PROJECT_FIELDS[5:],
                        "pageInfo": {"hasNextPage": False, "nextCursor": None},
                    }
                )
            if arguments["method"] == "list_project_items":
                return public_success(
                    {
                        "items": [],
                        "pageInfo": {"hasNextPage": False, "nextCursor": None},
                    }
                )
            self.fail(f"unexpected provider method: {arguments['method']}")

        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"
        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).preflight(
            {
                "adapter_contract_version": 2,
                "operation": operation,
                "destination_label": "Portfolio OS Tasks",
                "content_target_ref": "task-content:portfolio-os",
                "required_capability": "task.create",
            }
        )

        self.assertTrue(result["ok"])
        field_calls = [
            arguments
            for _tool_name, arguments in calls
            if arguments["method"] == "list_project_fields"
        ]
        self.assertEqual(2, len(field_calls))
        self.assertNotIn("after", field_calls[0])
        self.assertEqual("fields-page-2", field_calls[1]["after"])

    def test_preflight_maps_provider_failures_to_safe_stable_blockers(self):
        cases = (
            ("MCP tool disabled: method not found", "tool_disabled"),
            ("unauthorized: authentication required", "auth_missing"),
            ("forbidden: permission denied", "permission_failure"),
            ("project not found", "destination_unresolved"),
            ("MCP call failed: ConnectionError", "adapter_unavailable"),
        )
        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"

        for provider_error, expected_code in cases:
            with self.subTest(provider_error=provider_error):
                calls = []

                def dispatch(tool_name, arguments):
                    calls.append((tool_name, arguments))
                    return public_error(
                        f"{provider_error}; Authorization: Bearer must-not-leak"
                    )

                result = GithubProjectsAdapter(
                    config=load_config(EXAMPLE_CONFIG),
                    dispatch=dispatch,
                ).preflight(
                    {
                        "adapter_contract_version": 2,
                        "operation": operation,
                        "destination_label": "Portfolio OS Tasks",
                        "content_target_ref": "task-content:portfolio-os",
                        "required_capability": "task.create",
                    }
                )

                self.assertFalse(result["ok"])
                self.assertNotIn("status", result)
                self.assertFalse(result["requires_human_confirmation"])
                self.assertEqual(expected_code, result["error"]["code"])
                self.assertFalse(result["readiness"]["ok"])
                self.assertEqual([], result["expected_side_effects"])
                self.assertNotIn("must-not-leak", json.dumps(result))
                self.assertEqual(1, len(calls))

    def test_preflight_maps_route_field_delegation_and_capability_blockers(self):
        cases = (
            ("unknown_destination", "destination_unresolved"),
            ("missing_field", "required_field_missing"),
            ("field_type", "field_type_mismatch"),
            ("unsafe_delegation", "unsafe_delegation_exposure"),
            ("capability", "capability_mismatch"),
        )

        for case, expected_code in cases:
            with self.subTest(case=case):
                operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
                operation["destination_ref"] = "tasks:portfolio-os"
                request = {
                    "adapter_contract_version": 2,
                    "operation": operation,
                    "destination_label": "Portfolio OS Tasks",
                    "content_target_ref": "task-content:portfolio-os",
                    "required_capability": "task.create",
                }
                config = load_config(EXAMPLE_CONFIG)
                provider_fields = [dict(field) for field in PROJECT_FIELDS]
                if case == "unknown_destination":
                    operation["destination_ref"] = "tasks:unknown"
                if case == "missing_field":
                    provider_fields = [
                        field
                        for field in provider_fields
                        if field["name"] != "Due Date"
                    ]
                if case == "field_type":
                    next(
                        field
                        for field in provider_fields
                        if field["name"] == "Due Date"
                    )["data_type"] = "text"
                if case == "unsafe_delegation":
                    config = replace(
                        config,
                        host_attestation={
                            **config.host_attestation,
                            "raw_mcp_exposure": "model_visible",
                        },
                    )
                if case == "capability":
                    request["required_capability"] = "task.update"

                calls = []

                def dispatch(tool_name, arguments):
                    calls.append((tool_name, arguments))
                    if arguments["method"] == "get_project":
                        return public_success(
                            {
                                "number": 7,
                                "title": "Portfolio OS Tasks",
                                "owner": {"login": "example-owner"},
                            }
                        )
                    if arguments["method"] == "list_project_fields":
                        return public_success(
                            {
                                "fields": provider_fields,
                                "pageInfo": {
                                    "hasNextPage": False,
                                    "nextCursor": None,
                                },
                            }
                        )
                    return public_success(
                        {
                            "items": [],
                            "pageInfo": {"hasNextPage": False, "nextCursor": None},
                        }
                    )

                result = GithubProjectsAdapter(
                    config=config,
                    dispatch=dispatch,
                ).preflight(request)

                self.assertFalse(result["ok"])
                self.assertEqual(expected_code, result["error"]["code"])
                self.assertEqual([], result["expected_side_effects"])
                if case in {
                    "unknown_destination",
                    "unsafe_delegation",
                    "capability",
                }:
                    self.assertEqual([], calls)

    def test_preflight_rejects_a_provider_project_identity_mismatch(self):
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            return public_success(
                {
                    "number": 999,
                    "title": "Different Project",
                    "owner": {"login": "example-owner"},
                }
            )

        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"
        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).preflight(
            {
                "adapter_contract_version": 2,
                "operation": operation,
                "destination_label": "Portfolio OS Tasks",
                "content_target_ref": "task-content:portfolio-os",
                "required_capability": "task.create",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual("destination_unresolved", result["error"]["code"])
        self.assertEqual(["get_project"], [call[1]["method"] for call in calls])

    def test_preflight_fails_typed_on_a_repeated_pagination_cursor(self):
        def dispatch(_tool_name, arguments):
            if arguments["method"] == "get_project":
                return public_success(
                    {
                        "number": 7,
                        "title": "Portfolio OS Tasks",
                        "owner": {"login": "example-owner"},
                    }
                )
            return public_success(
                {
                    "fields": PROJECT_FIELDS[:1],
                    "pageInfo": {
                        "hasNextPage": True,
                        "nextCursor": "repeated-cursor",
                    },
                }
            )

        operation = json.loads(CREATE_OPERATION.read_text(encoding="utf-8"))
        operation["destination_ref"] = "tasks:portfolio-os"
        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).preflight(
            {
                "adapter_contract_version": 2,
                "operation": operation,
                "destination_label": "Portfolio OS Tasks",
                "content_target_ref": "task-content:portfolio-os",
                "required_capability": "task.create",
            }
        )

        self.assertFalse(result["ok"])
        self.assertEqual("adapter_unavailable", result["error"]["code"])
        self.assertEqual([], result["expected_side_effects"])


if __name__ == "__main__":
    unittest.main()
