import sys
import unittest
from copy import deepcopy
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

try:
    from task_management import normalization
except ImportError:
    normalization = None


def operation():
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
                "approval_required": True,
                "source_ref": {
                    "kind": "conversation",
                    "ref": "source:opaque",
                    "label": "Approved planning discussion",
                },
                "fields": {"review_notes": []},
            }
        },
    }


def destination():
    return {
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "destination_label": "Default tasks",
        "content_target_ref": "task-content:default",
    }


def route_binding():
    return {
        "adapter_key": "github_projects",
        "binding_digest": "sha256:" + "b" * 64,
    }


def preflight_response():
    return {
        "adapter_contract_version": 2,
        "ok": True,
        "operation_type": "task.create",
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "readiness": {"ok": True, "checks": []},
        "expected_side_effects": [
            {
                "effect_type": "content.create",
                "description": "Create a linked task.",
            }
        ],
        "requires_human_confirmation": False,
        "error": None,
    }


def created_response():
    return {
        "result_type": "TaskWriteResult",
        "adapter_contract_version": 2,
        "ok": True,
        "status": "created",
        "operation_type": "task.create",
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "task_ref": {
            "backend_key": "remote_tasks",
            "task_ref": "task:opaque",
            "task_url": "https://example.invalid/tasks/opaque",
            "title": "Implement write facade",
        },
        "retryable": False,
        "human_action": None,
        "error": None,
    }


class WriteNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(
            normalization,
            "task_management.normalization must implement the adapter-v2 boundary",
        )

    def test_ready_preflight_is_bound_to_the_safe_preview(self):
        result = normalization.normalize_preflight_result(
            preflight_response(),
            operation=operation(),
            destination=destination(),
            route_binding=route_binding(),
        )

        self.assertTrue(result["ok"])
        self.assertEqual("human_required", result["approval_mode"])
        self.assertEqual(
            preflight_response()["expected_side_effects"],
            result["approval_preview"]["expected_side_effects"],
        )
        self.assertRegex(result["approval_digest"], r"^sha256:[0-9a-f]{64}$")

    def test_unknown_preflight_field_fails_closed(self):
        raw = {**preflight_response(), "provider_status": 200}

        result = normalization.normalize_preflight_result(
            raw,
            operation=operation(),
            destination=destination(),
            route_binding=route_binding(),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("contract_failure", result["error"]["error_type"])
        self.assertEqual("invalid_adapter_result", result["error"]["code"])
        self.assertNotIn("provider_status", str(result))

    def test_preflight_contract_version_mismatch_remains_typed(self):
        raw = {**preflight_response(), "adapter_contract_version": 1}

        result = normalization.normalize_preflight_result(
            raw,
            operation=operation(),
            destination=destination(),
            route_binding=route_binding(),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("adapter_contract_mismatch", result["error"]["code"])

    def test_credential_or_raw_provider_data_never_reaches_preflight_output(self):
        raw = preflight_response()
        raw["expected_side_effects"][0]["description"] = (
            "Authorization: Bearer secret-value"
        )

        result = normalization.normalize_preflight_result(
            raw,
            operation=operation(),
            destination=destination(),
            route_binding=route_binding(),
        )

        self.assertFalse(result["ok"])
        self.assertEqual("unsafe_delegation_exposure", result["error"]["code"])
        self.assertNotIn("secret-value", str(result))

    def test_side_effect_count_and_string_lengths_fail_closed(self):
        cases = {
            "count": [
                {"effect_type": f"effect.{index}", "description": "Safe effect."}
                for index in range(21)
            ],
            "type-length": [
                {"effect_type": "x" * 65, "description": "Safe effect."}
            ],
            "description-length": [
                {"effect_type": "content.create", "description": "x" * 501}
            ],
        }
        for label, effects in cases.items():
            with self.subTest(label=label):
                raw = preflight_response()
                raw["expected_side_effects"] = effects

                result = normalization.normalize_preflight_result(
                    raw,
                    operation=operation(),
                    destination=destination(),
                    route_binding=route_binding(),
                )

                self.assertFalse(result["ok"])
                self.assertEqual("invalid_adapter_result", result["error"]["code"])

    def test_safe_created_result_preserves_only_public_fields(self):
        result = normalization.normalize_write_result(
            created_response(),
            operation=operation(),
        )

        self.assertTrue(result["ok"])
        self.assertEqual("created", result["status"])
        self.assertEqual(
            {
                "result_type",
                "ok",
                "status",
                "operation_type",
                "backend_key",
                "destination_ref",
                "task_ref",
                "retryable",
                "human_action",
                "error",
            },
            set(result),
        )

    def test_unknown_write_field_replaces_success_with_safe_contract_failure(self):
        raw = {**created_response(), "provider_status": 201}

        result = normalization.normalize_write_result(raw, operation=operation())

        self.assertFalse(result["ok"])
        self.assertEqual("failed", result["status"])
        self.assertEqual("contract_failure", result["error"]["error_type"])
        self.assertEqual("invalid_adapter_result", result["error"]["code"])
        self.assertNotIn("provider_status", result)

    def test_unsafe_task_url_and_arbitrary_human_action_fail_closed(self):
        for label, mutation in (
            ("url", lambda raw: raw["task_ref"].update({"task_url": "http://example.invalid/task"})),
            ("action", lambda raw: raw.update({"human_action": "Run provider command 123"})),
        ):
            with self.subTest(label=label):
                raw = created_response()
                mutation(raw)

                result = normalization.normalize_write_result(raw, operation=operation())

                self.assertFalse(result["ok"])
                self.assertEqual("contract_failure", result["error"]["error_type"])
                self.assertNotIn("provider command", str(result).lower())

    def test_partial_and_retryable_provider_results_remain_typed(self):
        partial = created_response()
        partial.update(
            {
                "ok": False,
                "status": "partial",
                "human_action": "Inspect the linked task before retrying field updates.",
                "error": {
                    "error_type": "partial_failure",
                    "code": "partial_update_failure",
                    "message": "raw adapter detail must be replaced",
                    "stage": "fields_update",
                },
            }
        )
        retryable = created_response()
        retryable.update(
            {
                "ok": False,
                "status": "failed",
                "task_ref": None,
                "retryable": True,
                "human_action": "Retry after the backend service becomes available.",
                "error": {
                    "error_type": "provider_failure",
                    "code": "rate_limited",
                    "message": "raw provider message",
                },
            }
        )

        normalized_partial = normalization.normalize_write_result(
            partial, operation=operation()
        )
        normalized_retryable = normalization.normalize_write_result(
            retryable, operation=operation()
        )

        self.assertEqual("partial", normalized_partial["status"])
        self.assertEqual("partial_failure", normalized_partial["error"]["error_type"])
        self.assertNotIn("raw adapter detail", str(normalized_partial))
        self.assertTrue(normalized_retryable["retryable"])
        self.assertEqual("provider_failure", normalized_retryable["error"]["error_type"])
        self.assertNotIn("raw provider message", str(normalized_retryable))


if __name__ == "__main__":
    unittest.main()
