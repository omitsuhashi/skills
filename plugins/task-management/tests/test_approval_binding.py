import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = PLUGIN_ROOT / "tests" / "fixtures" / "adapter-v2" / "approval-binding"
sys.path.insert(0, str(PLUGIN_ROOT))

from task_management.approval import (  # noqa: E402
    ApprovalBindingError,
    CanonicalJsonError,
    approval_digest,
    authorize_apply,
    canonical_digest,
    canonical_json,
)


class CanonicalJsonTests(unittest.TestCase):
    def test_known_vector_normalizes_nfc_sorts_objects_and_hashes_utf8(self):
        vector = json.loads(
            (FIXTURES / "canonical-value.json").read_text(encoding="utf-8")
        )

        self.assertEqual(vector["canonical"], canonical_json(vector["value"]))
        self.assertEqual(vector["digest"], canonical_digest(vector["value"]))

    def test_rejects_values_outside_the_limited_canonical_domain(self):
        unsupported = [
            1.25,
            float("nan"),
            float("inf"),
            b"bytes",
            ("tuple",),
            object(),
            {1: "non-string-key"},
            {"é": 1, "é": 2},
        ]

        for value in unsupported:
            with self.subTest(value=repr(value)):
                with self.assertRaises(CanonicalJsonError) as raised:
                    canonical_json(value)
                self.assertEqual("invalid_canonical_value", raised.exception.code)


class ApprovalBindingTests(unittest.TestCase):
    def setUp(self):
        self.preview = json.loads(
            (
                PLUGIN_ROOT
                / "tests"
                / "fixtures"
                / "adapter-v2"
                / "accept"
                / "approval-preview.json"
            ).read_text(encoding="utf-8")
        )
        self.digest = approval_digest(self.preview)
        self.receipt = {
            "receipt_version": 1,
            "decision": "approved",
            "operation_digest": self.digest,
        }

    def test_exact_preview_and_receipt_authorize_without_dispatching(self):
        authorized = authorize_apply(
            self.preview,
            self.receipt,
            self.preview,
            approval_mode="human_required",
            preflight_passed=True,
            unresolved_uncertainty=False,
        )

        self.assertEqual(self.preview, authorized)

    def test_every_bound_mutation_is_approval_mismatch_before_apply(self):
        mutations = {
            "preview_version": lambda value: value.__setitem__("preview_version", 2),
            "operation_type": lambda value: value["operation"].__setitem__(
                "operation_type", "task.comment"
            ),
            "backend_key": lambda value: value["operation"].__setitem__(
                "backend_key", "changed_backend"
            ),
            "destination_ref": lambda value: value["operation"].__setitem__(
                "destination_ref", "tasks:changed"
            ),
            "task_ref": lambda value: value["operation"].__setitem__(
                "task_ref", {"backend_key": "remote_tasks"}
            ),
            "task_content": lambda value: value["operation"]["payload"]["task"].__setitem__(
                "title", "Changed title"
            ),
            "task_fields": lambda value: value["operation"]["payload"]["task"].__setitem__(
                "importance", "critical"
            ),
            "destination_label": lambda value: value["destination"].__setitem__(
                "destination_label", "Changed destination"
            ),
            "content_target_ref": lambda value: value["destination"].__setitem__(
                "content_target_ref", "task-content:changed"
            ),
            "route_adapter": lambda value: value["route_binding"].__setitem__(
                "adapter_key", "changed_adapter"
            ),
            "route_digest": lambda value: value["route_binding"].__setitem__(
                "binding_digest", f"sha256:{'d' * 64}"
            ),
            "side_effect": lambda value: value["expected_side_effects"][0].__setitem__(
                "description", "Changed effect"
            ),
            "side_effect_order": lambda value: value["expected_side_effects"].reverse(),
        }

        for label, mutate in mutations.items():
            with self.subTest(label=label):
                current = deepcopy(self.preview)
                mutate(current)
                apply_calls = []
                try:
                    authorized = authorize_apply(
                        self.preview,
                        self.receipt,
                        current,
                        approval_mode="human_required",
                        preflight_passed=True,
                        unresolved_uncertainty=False,
                    )
                    apply_calls.append(authorized)
                except ApprovalBindingError as error:
                    self.assertEqual("approval_mismatch", error.code)
                self.assertEqual([], apply_calls)

        changed_receipt = deepcopy(self.receipt)
        changed_receipt["operation_digest"] = f"sha256:{'e' * 64}"
        with self.assertRaises(ApprovalBindingError) as raised:
            authorize_apply(
                self.preview,
                changed_receipt,
                self.preview,
                approval_mode="human_required",
                preflight_passed=True,
                unresolved_uncertainty=False,
            )
        self.assertEqual("approval_mismatch", raised.exception.code)

    def test_confidence_authorization_requires_ready_eligible_certain_preflight(self):
        confidence_receipt = {
            **self.receipt,
            "decision": "confidence_authorized",
        }
        blocked_cases = [
            ("confidence_eligible", False, False, "preflight_not_ready"),
            ("human_required", True, False, "human_approval_required"),
            ("confidence_eligible", True, True, "human_approval_required"),
        ]

        for mode, passed, uncertain, expected_code in blocked_cases:
            with self.subTest(
                mode=mode, passed=passed, uncertain=uncertain
            ):
                with self.assertRaises(ApprovalBindingError) as raised:
                    authorize_apply(
                        self.preview,
                        confidence_receipt,
                        self.preview,
                        approval_mode=mode,
                        preflight_passed=passed,
                        unresolved_uncertainty=uncertain,
                    )
                self.assertEqual(expected_code, raised.exception.code)

        self.assertEqual(
            self.preview,
            authorize_apply(
                self.preview,
                confidence_receipt,
                self.preview,
                approval_mode="confidence_eligible",
                preflight_passed=True,
                unresolved_uncertainty=False,
            ),
        )

        with self.assertRaises(ApprovalBindingError) as raised:
            authorize_apply(
                self.preview,
                self.receipt,
                self.preview,
                approval_mode="human_required",
                preflight_passed=False,
                unresolved_uncertainty=False,
            )
        self.assertEqual("preflight_not_ready", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
