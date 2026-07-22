import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ACCEPT_FIXTURES = PLUGIN_ROOT / "tests" / "fixtures" / "adapter-v2" / "accept"
sys.path.insert(0, str(PLUGIN_ROOT))

from task_management.preflight import (  # noqa: E402
    PreflightPolicyError,
    approval_mode_for_operation,
    build_preflight_result,
)
from task_management.approval import approval_digest  # noqa: E402


def _load(name):
    return json.loads((ACCEPT_FIXTURES / name).read_text(encoding="utf-8"))


class ApprovalModeTests(unittest.TestCase):
    def setUp(self):
        self.operation = _load("operation-create.json")
        task = self.operation["payload"]["task"]
        task["approval_required"] = False
        task["fields"]["review_notes"] = []

    def test_ready_certain_operation_is_confidence_eligible(self):
        self.assertEqual(
            "confidence_eligible",
            approval_mode_for_operation(
                self.operation,
                preflight_passed=True,
                adapter_uncertainty=False,
            ),
        )

    def test_explicit_approval_review_notes_or_uncertainty_force_human(self):
        cases = []

        approval_required = deepcopy(self.operation)
        approval_required["payload"]["task"]["approval_required"] = True
        cases.append(("approval_required", approval_required, False))

        review_notes = deepcopy(self.operation)
        review_notes["payload"]["task"]["fields"]["review_notes"] = [
            "Destination needs confirmation."
        ]
        cases.append(("review_notes", review_notes, False))

        cases.append(("adapter_uncertainty", self.operation, True))

        for label, operation, uncertain in cases:
            with self.subTest(label=label):
                self.assertEqual(
                    "human_required",
                    approval_mode_for_operation(
                        operation,
                        preflight_passed=True,
                        adapter_uncertainty=uncertain,
                    ),
                )

    def test_adapter_uncertainty_requires_an_explicit_boolean(self):
        for value in (0, 1, None, "false", []):
            with self.subTest(value=value):
                with self.assertRaises(PreflightPolicyError) as raised:
                    approval_mode_for_operation(
                        self.operation,
                        preflight_passed=True,
                        adapter_uncertainty=value,
                    )
                self.assertEqual("invalid_adapter_uncertainty", raised.exception.code)


class ReadinessSeparationTests(unittest.TestCase):
    def test_blocked_readiness_issues_no_approval_material(self):
        operation = _load("operation-create.json")
        destination = _load("destination.json")
        preview = _load("approval-preview.json")
        result = build_preflight_result(
            operation,
            destination,
            preview["route_binding"],
            preview["expected_side_effects"],
            readiness={
                "ok": False,
                "checks": [{"code": "destination_unresolved", "ok": False}],
            },
            adapter_uncertainty=True,
            error={
                "error_type": "setup_blocker",
                "code": "destination_unresolved",
                "message": "The configured destination is unavailable.",
                "stage": "preflight",
            },
        )

        self.assertFalse(result["ok"])
        self.assertEqual("blocked", result["status"])
        self.assertIsNone(result["approval_mode"])
        self.assertIsNone(result["approval_preview"])
        self.assertIsNone(result["approval_digest"])

        with self.assertRaises(PreflightPolicyError) as raised:
            approval_mode_for_operation(
                operation,
                preflight_passed=False,
                adapter_uncertainty=False,
            )
        self.assertEqual("preflight_not_ready", raised.exception.code)

    def test_ready_preflight_issues_preview_but_not_write_approval(self):
        preview_fixture = _load("approval-preview.json")
        operation = deepcopy(preview_fixture["operation"])
        operation["payload"]["task"]["approval_required"] = False
        operation["payload"]["task"]["fields"]["review_notes"] = []

        result = build_preflight_result(
            operation,
            preview_fixture["destination"],
            preview_fixture["route_binding"],
            preview_fixture["expected_side_effects"],
            readiness={"ok": True, "checks": []},
            adapter_uncertainty=False,
            error=None,
        )

        self.assertTrue(result["ok"])
        self.assertEqual("ready", result["status"])
        self.assertEqual("confidence_eligible", result["approval_mode"])
        self.assertEqual(
            approval_digest(result["approval_preview"]),
            result["approval_digest"],
        )
        self.assertNotIn("decision", result)
        self.assertNotIn("approval_receipt", result)


if __name__ == "__main__":
    unittest.main()
