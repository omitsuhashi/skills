import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

try:
    from task_management import write_adapter
except ImportError:
    write_adapter = None


def operation(*, approval_required=True):
    return {
        "adapter_contract_version": 2,
        "operation_type": "task.create",
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "task_ref": None,
        "payload": {
            "task": {
                "title": "Implement write facade",
                "body": "Add an approval-bound adapter dispatch.",
                "work_unit_id": "portfolio-os",
                "work_unit_name": "Portfolio OS",
                "task_type": "implementation",
                "due_date": None,
                "urgency": "normal",
                "importance": "high",
                "automation_mode": "assistive",
                "approval_required": approval_required,
                "source_ref": {
                    "kind": "conversation",
                    "ref": "source:opaque",
                    "label": "Approved planning discussion",
                },
                "fields": {"review_notes": []},
            }
        },
    }


def route_text(*, adapter="github_projects"):
    return f'''contract_version = 2
default_backend = "remote_tasks"
[backends.remote_tasks]
adapter_key = "{adapter}"
query_tool = "task_adapter__{adapter}__task_query"
preflight_tool = "task_adapter__{adapter}__task_preflight"
apply_tool = "task_adapter__{adapter}__task_apply"
[backends.remote_tasks.destinations.default]
public_ref = "tasks:default"
destination_label = "Default tasks"
content_target_ref = "task-content:default"
'''


class FakeDispatcher:
    def __init__(self):
        self.calls = []
        self.effects = [
            {
                "effect_type": "content.create",
                "description": "Create a linked task.",
            }
        ]
        self.preflight_ok = True
        self.requires_human_confirmation = False

    def __call__(self, tool_name, arguments, **_kwargs):
        self.calls.append((tool_name, deepcopy(arguments)))
        operation_value = arguments["operation"]
        if tool_name.endswith("__task_preflight"):
            if not self.preflight_ok:
                return {
                    "adapter_contract_version": 2,
                    "ok": False,
                    "operation_type": operation_value["operation_type"],
                    "backend_key": operation_value["backend_key"],
                    "destination_ref": operation_value["destination_ref"],
                    "readiness": {"ok": False, "checks": []},
                    "expected_side_effects": [],
                    "requires_human_confirmation": False,
                    "error": {
                        "error_type": "setup_blocker",
                        "code": "auth_missing",
                        "message": "raw adapter auth detail",
                    },
                }
            return {
                "adapter_contract_version": 2,
                "ok": True,
                "operation_type": operation_value["operation_type"],
                "backend_key": operation_value["backend_key"],
                "destination_ref": operation_value["destination_ref"],
                "readiness": {"ok": True, "checks": []},
                "expected_side_effects": deepcopy(self.effects),
                "requires_human_confirmation": self.requires_human_confirmation,
                "error": None,
            }
        if tool_name.endswith("__task_apply"):
            return {
                "adapter_contract_version": 2,
                "ok": True,
                "status": "created",
                "operation_type": operation_value["operation_type"],
                "backend_key": operation_value["backend_key"],
                "destination_ref": operation_value["destination_ref"],
                "task_ref": {
                    "backend_key": operation_value["backend_key"],
                    "task_ref": "task:opaque",
                    "task_url": "https://example.invalid/tasks/opaque",
                    "title": "Implement write facade",
                },
                "retryable": False,
                "human_action": None,
                "error": None,
            }
        raise AssertionError(f"unexpected tool {tool_name}")


class TaskWriteAdapterTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(
            write_adapter,
            "task_management.write_adapter must implement the public write facade",
        )

    def write_route(self, root, *, text=None):
        path = Path(root) / "routes.toml"
        path.write_text(text or route_text(), encoding="utf-8")
        return path

    def preflight(self, dispatcher, route, *, operation_value=None):
        return write_adapter.preflight_task(
            {
                "interface_version": 2,
                "operation": operation_value or operation(),
            },
            dispatch=dispatcher,
            routes_file=str(route),
        )

    def test_preflight_dispatches_only_the_fixed_route_tool(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)

            result = self.preflight(dispatcher, route)

        self.assertTrue(result["ok"])
        self.assertEqual("human_required", result["approval_mode"])
        self.assertEqual(
            ["task_adapter__github_projects__task_preflight"],
            [name for name, _ in dispatcher.calls],
        )
        self.assertEqual(
            {"adapter_key", "binding_digest"},
            set(result["approval_preview"]["route_binding"]),
        )
        self.assertNotIn("task_preflight", json.dumps(result["approval_preview"]))

    def test_missing_route_and_caller_selector_fail_before_dispatch(self):
        for label, arguments, routes_file in (
            (
                "missing-route",
                {"interface_version": 2, "operation": operation()},
                None,
            ),
            (
                "caller-selector",
                {
                    "interface_version": 2,
                    "operation": {**operation(), "tool_name": "task_apply"},
                },
                "unused.toml",
            ),
        ):
            with self.subTest(label=label):
                dispatcher = FakeDispatcher()
                result = write_adapter.preflight_task(
                    arguments,
                    dispatch=dispatcher,
                    routes_file=routes_file,
                )

                self.assertFalse(result["ok"])
                self.assertEqual([], dispatcher.calls)
                self.assertNotIn("tool_name", str(result))

    def test_approved_receipt_repreflights_then_dispatches_exact_apply_tool(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)
            preflight = self.preflight(dispatcher, route)
            result = write_adapter.apply_task(
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
                dispatch=dispatcher,
                routes_file=str(route),
            )

        self.assertTrue(result["ok"])
        self.assertEqual("created", result["status"])
        self.assertEqual(
            [
                "task_adapter__github_projects__task_preflight",
                "task_adapter__github_projects__task_preflight",
                "task_adapter__github_projects__task_apply",
            ],
            [name for name, _ in dispatcher.calls],
        )
        apply_arguments = dispatcher.calls[-1][1]
        self.assertEqual(preflight["approval_digest"], apply_arguments["operation_digest"])
        self.assertEqual(operation(), apply_arguments["operation"])
        self.assertNotIn("approval_receipt", apply_arguments)

    def test_human_required_confidence_receipt_dispatches_no_apply(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)
            preflight = self.preflight(dispatcher, route)
            result = write_adapter.apply_task(
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "confidence_authorized",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
                dispatch=dispatcher,
                routes_file=str(route),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("approval_required", result["error"]["code"])
        self.assertEqual(
            [],
            [name for name, _ in dispatcher.calls if name.endswith("__task_apply")],
        )

    def test_side_effect_mismatch_dispatches_no_apply(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)
            preflight = self.preflight(dispatcher, route)
            dispatcher.effects.append(
                {
                    "effect_type": "fields.update",
                    "description": "Update reviewed fields.",
                }
            )
            result = write_adapter.apply_task(
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
                dispatch=dispatcher,
                routes_file=str(route),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("approval_mismatch", result["error"]["code"])
        self.assertEqual(
            [],
            [name for name, _ in dispatcher.calls if name.endswith("__task_apply")],
        )

    def test_route_binding_change_dispatches_no_apply(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)
            preflight = self.preflight(dispatcher, route)
            route.write_text(route_text(adapter="other_adapter"), encoding="utf-8")

            result = write_adapter.apply_task(
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
                dispatch=dispatcher,
                routes_file=str(route),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("approval_mismatch", result["error"]["code"])
        self.assertEqual(
            [],
            [name for name, _ in dispatcher.calls if name.endswith("__task_apply")],
        )

    def test_blocked_repreflight_returns_safe_failure_without_apply(self):
        dispatcher = FakeDispatcher()
        with tempfile.TemporaryDirectory() as tmp:
            route = self.write_route(tmp)
            preflight = self.preflight(dispatcher, route)
            dispatcher.preflight_ok = False

            result = write_adapter.apply_task(
                {
                    "interface_version": 2,
                    "approval_preview": preflight["approval_preview"],
                    "approval_receipt": {
                        "receipt_version": 1,
                        "decision": "approved",
                        "operation_digest": preflight["approval_digest"],
                    },
                },
                dispatch=dispatcher,
                routes_file=str(route),
            )

        self.assertFalse(result["ok"])
        self.assertEqual("blocked", result["status"])
        self.assertEqual("auth_missing", result["error"]["code"])
        self.assertNotIn("raw adapter auth detail", str(result))
        self.assertEqual(
            [],
            [name for name, _ in dispatcher.calls if name.endswith("__task_apply")],
        )


if __name__ == "__main__":
    unittest.main()
