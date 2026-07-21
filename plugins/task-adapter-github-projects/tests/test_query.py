import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG = PLUGIN_ROOT / "config" / "github-projects.example.toml"
QUERY_FIXTURE = (
    PLUGIN_ROOT
    / "tests"
    / "fixtures"
    / "provider"
    / "projects-query-pages.json"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.adapter import GithubProjectsAdapter  # noqa: E402
from task_adapter_github_projects.config import load_config  # noqa: E402


class GithubProjectsQueryTests(unittest.TestCase):
    def test_query_paginates_post_filters_and_returns_only_safe_snapshots(self):
        fixture = json.loads(QUERY_FIXTURE.read_text(encoding="utf-8"))
        calls = []

        def dispatch(tool_name, arguments):
            calls.append((tool_name, arguments))
            if arguments["method"] == "get_project":
                return {
                    "id": "PVT_private",
                    "number": 7,
                    "title": "Portfolio OS Tasks",
                    "owner": {"login": "example-owner"},
                }
            if arguments["method"] == "list_project_fields":
                return {
                    "fields": fixture["fields"],
                    "pageInfo": {"hasNextPage": False, "nextCursor": None},
                }
            if arguments["method"] == "list_project_items":
                return fixture["pages"][1 if arguments.get("after") else 0]
            self.fail(f"unexpected provider method: {arguments['method']}")

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).query(
            {
                "adapter_contract_version": 2,
                "backend_key": "github_projects_mcp",
                "destination_ref": "tasks:portfolio-os",
                "query": {
                    "work_unit_id": "planning",
                    "status": "ready",
                    "due_before": "2026-07-31",
                    "limit": 2,
                },
            }
        )

        item_calls = [
            arguments
            for _tool_name, arguments in calls
            if arguments["method"] == "list_project_items"
        ]
        self.assertEqual(2, len(item_calls))
        self.assertEqual("items-page-2", item_calls[1]["after"])
        self.assertEqual(50, item_calls[0]["per_page"])
        self.assertEqual(
            {str(field["id"]) for field in fixture["fields"]},
            set(item_calls[0]["fields"]),
        )
        self.assertEqual(2, result["adapter_contract_version"])
        self.assertEqual(
            ["Prepare quarterly plan", "Review quarterly plan"],
            [item["title"] for item in result["items"]],
        )
        self.assertTrue(result["items"][0]["approval_required"])
        self.assertFalse(result["items"][1]["approval_required"])
        serialized = json.dumps(result)
        for forbidden in (
            "PVTI_private",
            "I_private",
            "PVTSSF_private",
            "node_id",
            '"fields"',
        ):
            self.assertNotIn(forbidden, serialized)

    def test_query_maps_destination_and_provider_failures_to_safe_codes(self):
        cases = (
            ("unknown_destination", None, "destination_unresolved"),
            ("provider", "tool_disabled", "tool_disabled"),
            ("provider", "unauthorized", "auth_missing"),
            ("provider", "forbidden", "permission_failure"),
            ("provider", "connection_failed", "adapter_unavailable"),
        )
        for case, provider_code, expected_code in cases:
            with self.subTest(case=case, provider_code=provider_code):
                calls = []

                def dispatch(tool_name, arguments):
                    calls.append((tool_name, arguments))
                    return {
                        "error": {
                            "code": provider_code,
                            "message": "Authorization: Bearer must-not-leak",
                        }
                    }

                result = GithubProjectsAdapter(
                    config=load_config(EXAMPLE_CONFIG),
                    dispatch=dispatch,
                ).query(
                    {
                        "adapter_contract_version": 2,
                        "backend_key": "github_projects_mcp",
                        "destination_ref": (
                            "tasks:unknown"
                            if case == "unknown_destination"
                            else "tasks:portfolio-os"
                        ),
                        "query": {"limit": 20},
                    }
                )

                self.assertEqual(2, result["adapter_contract_version"])
                self.assertEqual([], result["items"])
                self.assertEqual(expected_code, result["error"]["code"])
                self.assertNotIn("must-not-leak", json.dumps(result))
                self.assertEqual(0 if case == "unknown_destination" else 1, len(calls))

    def test_query_rejects_noncanonical_or_unbounded_filters_before_dispatch(self):
        invalid_queries = (
            {"limit": 0},
            {"limit": 101},
            {"limit": True},
            {"due_before": "tomorrow"},
            {"unexpected_filter": "value"},
        )
        for query in invalid_queries:
            with self.subTest(query=query):
                calls = []
                result = GithubProjectsAdapter(
                    config=load_config(EXAMPLE_CONFIG),
                    dispatch=lambda *args, **kwargs: calls.append((args, kwargs)),
                ).query(
                    {
                        "adapter_contract_version": 2,
                        "backend_key": "github_projects_mcp",
                        "destination_ref": "tasks:portfolio-os",
                        "query": query,
                    }
                )

                self.assertEqual([], calls)
                self.assertEqual([], result["items"])
                self.assertEqual("invalid_query", result["error"]["code"])

    def test_query_preserves_a_canonical_null_due_date(self):
        fixture = json.loads(QUERY_FIXTURE.read_text(encoding="utf-8"))
        item = fixture["pages"][0]["items"][0]
        next(
            field for field in item["fields"] if field["name"] == "Due Date"
        )["value"] = None

        def dispatch(_tool_name, arguments):
            if arguments["method"] == "get_project":
                return {
                    "number": 7,
                    "title": "Portfolio OS Tasks",
                    "owner": {"login": "example-owner"},
                }
            if arguments["method"] == "list_project_fields":
                return {
                    "fields": fixture["fields"],
                    "pageInfo": {"hasNextPage": False, "nextCursor": None},
                }
            return {
                "items": [item],
                "pageInfo": {"hasNextPage": False, "nextCursor": None},
            }

        result = GithubProjectsAdapter(
            config=load_config(EXAMPLE_CONFIG),
            dispatch=dispatch,
        ).query(
            {
                "adapter_contract_version": 2,
                "backend_key": "github_projects_mcp",
                "destination_ref": "tasks:portfolio-os",
                "query": {"limit": 1},
            }
        )

        self.assertNotIn("error", result)
        self.assertEqual(1, len(result["items"]))
        self.assertIsNone(result["items"][0]["due_date"])


if __name__ == "__main__":
    unittest.main()
