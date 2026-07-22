import json
import unittest
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_V2_FIXTURES = PLUGIN_ROOT / "tests" / "fixtures" / "adapter-v2"
sys.path.insert(0, str(PLUGIN_ROOT))

import task_management.contracts as contracts
from task_management.contracts import (
    ContractValidationError,
    validate_contract,
    validate_approval_preview,
    validate_approval_receipt,
    validate_operation_envelope,
    validate_task_preflight_result,
    validate_task_write_result,
    validate_task_backend_destination,
    validate_task_draft,
)
from task_management.provider_adapters import ADAPTER_CONTRACT_VERSION, TaskBackendAdapter


def task_draft():
    return {
        "title": "Implement write contracts",
        "body": "Add strict backend-neutral contract validation.",
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


def create_operation():
    return {
        "adapter_contract_version": 2,
        "operation_type": "task.create",
        "backend_key": "remote_tasks",
        "destination_ref": "tasks:default",
        "task_ref": None,
        "payload": {"task": task_draft()},
    }


def task_ref():
    return {
        "backend_key": "remote_tasks",
        "task_ref": "task:opaque",
        "task_url": "https://example.invalid/tasks/opaque",
        "title": "Implement write contracts",
    }


def approval_preview():
    return {
        "preview_version": 1,
        "operation": create_operation(),
        "destination": {
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "destination_label": "Default tasks",
            "content_target_ref": "task-content:default",
        },
        "route_binding": {
            "adapter_key": "github_projects",
            "binding_digest": "sha256:" + "b" * 64,
        },
        "expected_side_effects": [
            {
                "effect_type": "content.create",
                "description": "Create a linked task.",
            },
            {
                "effect_type": "task.read_back",
                "description": "Read the resulting task state.",
            },
        ],
    }


class OperationEnvelopeContractTests(unittest.TestCase):
    def test_valid_create_operation_is_returned_as_an_independent_safe_value(self):
        operation = create_operation()

        validated = validate_operation_envelope(operation)

        self.assertEqual(operation, validated)
        self.assertIsNot(operation, validated)
        self.assertIsNot(operation["payload"], validated["payload"])

    def test_create_operation_rejects_task_ref(self):
        operation = create_operation()
        operation["task_ref"] = task_ref()

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("invalid_task_ref", raised.exception.code)

    def test_operation_rejects_a_missing_required_key(self):
        operation = create_operation()
        del operation["task_ref"]

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("missing_field", raised.exception.code)
        self.assertEqual("$.task_ref", raised.exception.path)

    def test_operation_rejects_unexpected_fields(self):
        operation = create_operation()
        operation["extra"] = "unsupported"

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unexpected_field", raised.exception.code)
        self.assertEqual("$.extra", raised.exception.path)

    def test_valid_update_operation_requires_a_nonempty_backend_neutral_patch(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.update",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "payload": {"changes": {"importance": "critical"}},
        }

        self.assertEqual(operation, validate_operation_envelope(operation))

    def test_update_operation_rejects_provider_specific_change_fields(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.update",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "payload": {"changes": {"repository": "owner/repo"}},
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unexpected_field", raised.exception.code)
        self.assertEqual("$.payload.changes.repository", raised.exception.path)

    def test_existing_task_operation_rejects_unsafe_task_url(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.update",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": {**task_ref(), "task_url": "http://example.invalid/tasks/opaque"},
            "payload": {"changes": {"importance": "critical"}},
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unsafe_url", raised.exception.code)

    def test_valid_comment_operation_requires_a_nonempty_comment_body(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.comment",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "payload": {"comment": {"body": "Contract implementation is ready."}},
        }

        self.assertEqual(operation, validate_operation_envelope(operation))

    def test_comment_operation_rejects_an_empty_body(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.comment",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "payload": {"comment": {"body": ""}},
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("invalid_payload", raised.exception.code)

    def test_comment_operation_rejects_a_task_ref_for_another_backend(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.comment",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": {**task_ref(), "backend_key": "different_backend"},
            "payload": {"comment": {"body": "Contract implementation is ready."}},
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("invalid_task_ref", raised.exception.code)

    def test_report_operation_rejects_missing_verification(self):
        operation = {
            "adapter_contract_version": 2,
            "operation_type": "task.report",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "payload": {
                "report": {
                    "summary": "Implemented contract v2.",
                    "work_performed": ["Added strict validators."],
                    "residuals": [],
                }
            },
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("invalid_payload", raised.exception.code)

    def test_operation_rejects_float_as_a_noncanonical_wire_value(self):
        operation = create_operation()
        operation["payload"]["task"]["fields"]["estimate"] = 1.5

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("invalid_canonical_value", raised.exception.code)
        self.assertEqual("$.payload.task.fields.estimate", raised.exception.path)

    def test_operation_rejects_nested_credentials(self):
        operation = create_operation()
        operation["payload"]["task"]["fields"]["access_token"] = "not-a-real-token"

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unsafe_data", raised.exception.code)
        self.assertEqual("$.payload.task.fields.access_token", raised.exception.path)

    def test_operation_rejects_raw_provider_identifiers(self):
        operation = create_operation()
        operation["payload"]["task"]["fields"]["field_id"] = "PVTF_raw"

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unsafe_data", raised.exception.code)
        self.assertEqual("$.payload.task.fields.field_id", raised.exception.path)

    def test_operation_rejects_credential_like_string_values(self):
        operation = create_operation()
        operation["payload"]["task"]["body"] = "Authorization: Bearer not-a-real-token"

        with self.assertRaises(ContractValidationError) as raised:
            validate_operation_envelope(operation)

        self.assertEqual("unsafe_data", raised.exception.code)
        self.assertEqual("$.payload.task.body", raised.exception.path)


class BackendNeutralValueContractTests(unittest.TestCase):
    def test_task_draft_and_destination_preserve_only_backend_neutral_fields(self):
        destination = {
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "destination_label": "Default tasks",
            "content_target_ref": "task-content:default",
        }

        self.assertEqual(task_draft(), validate_task_draft(task_draft()))
        self.assertEqual(
            destination,
            validate_task_backend_destination(destination),
        )


class ApprovalReceiptContractTests(unittest.TestCase):
    def test_approved_receipt_binds_one_sha256_operation_digest(self):
        receipt = {
            "receipt_version": 1,
            "decision": "approved",
            "operation_digest": "sha256:" + "a" * 64,
        }

        self.assertEqual(receipt, validate_approval_receipt(receipt))

    def test_receipt_version_rejects_boolean_alias_for_integer_one(self):
        receipt = {
            "receipt_version": True,
            "decision": "approved",
            "operation_digest": "sha256:" + "a" * 64,
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_approval_receipt(receipt)

        self.assertEqual("unsupported_receipt_version", raised.exception.code)


class ApprovalPreviewContractTests(unittest.TestCase):
    def test_preview_binds_operation_destination_route_and_ordered_side_effects(self):
        preview = approval_preview()

        self.assertEqual(preview, validate_approval_preview(preview))


class TaskPreflightResultContractTests(unittest.TestCase):
    def test_ready_preflight_includes_preview_digest_and_separate_readiness(self):
        result = {
            "result_type": "TaskPreflightResult",
            "ok": True,
            "status": "ready",
            "operation_type": "task.create",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "approval_mode": "human_required",
            "approval_preview": approval_preview(),
            "approval_digest": "sha256:" + "c" * 64,
            "readiness": {"ok": True, "checks": []},
            "error": None,
        }

        self.assertEqual(result, validate_task_preflight_result(result))

    def test_blocked_preflight_rejects_unknown_error_fields(self):
        result = {
            "result_type": "TaskPreflightResult",
            "ok": False,
            "status": "blocked",
            "operation_type": "task.create",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "approval_mode": None,
            "approval_preview": None,
            "approval_digest": None,
            "readiness": {"ok": False, "checks": []},
            "error": {
                "error_type": "setup_blocker",
                "code": "auth_missing",
                "message": "The configured adapter is unavailable.",
                "provider_status": 401,
            },
        }

        with self.assertRaises(ContractValidationError) as raised:
            validate_task_preflight_result(result)

        self.assertEqual("unexpected_field", raised.exception.code)
        self.assertEqual("$.error.provider_status", raised.exception.path)


class TaskWriteResultContractTests(unittest.TestCase):
    def test_created_result_exposes_only_backend_neutral_safe_fields(self):
        result = {
            "result_type": "TaskWriteResult",
            "ok": True,
            "status": "created",
            "operation_type": "task.create",
            "backend_key": "remote_tasks",
            "destination_ref": "tasks:default",
            "task_ref": task_ref(),
            "retryable": False,
            "human_action": None,
            "error": None,
        }

        self.assertEqual(result, validate_task_write_result(result))


class AdapterInterfaceContractTests(unittest.TestCase):
    def test_shared_adapter_contract_version_is_two(self):
        self.assertEqual(2, ADAPTER_CONTRACT_VERSION)

    def test_shared_adapter_interface_exposes_only_query_preflight_and_apply(self):
        public_operations = {
            name for name in TaskBackendAdapter.__dict__ if not name.startswith("_")
        }

        self.assertEqual({"query", "preflight", "apply"}, public_operations)


class PublicContractSurfaceTests(unittest.TestCase):
    def test_contract_module_exports_only_approved_types_and_validators(self):
        self.assertEqual(
            {
                "ADAPTER_CONTRACT_VERSION",
                "ContractValidationError",
                "TaskDraft",
                "TaskBackendDestination",
                "OperationEnvelope",
                "ApprovalPreview",
                "ApprovalReceipt",
                "TaskPreflightResult",
                "TaskWriteResult",
                "validate_task_draft",
                "validate_task_backend_destination",
                "validate_operation_envelope",
                "validate_approval_preview",
                "validate_approval_receipt",
                "validate_task_preflight_result",
                "validate_task_write_result",
                "validate_contract",
            },
            set(contracts.__all__),
        )


class NormativeFixtureContractTests(unittest.TestCase):
    def test_manifest_accepts_and_rejects_normative_adapter_v2_vectors(self):
        manifest = json.loads((ADAPTER_V2_FIXTURES / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(2, manifest["adapter_contract_version"])
        for case in manifest["accept"]:
            with self.subTest(kind="accept", name=case["name"]):
                payload = json.loads((ADAPTER_V2_FIXTURES / case["path"]).read_text(encoding="utf-8"))
                self.assertEqual(payload, validate_contract(case["contract"], payload))
        for case in manifest["reject"]:
            with self.subTest(kind="reject", name=case["name"]):
                payload = json.loads((ADAPTER_V2_FIXTURES / case["path"]).read_text(encoding="utf-8"))
                with self.assertRaises(ContractValidationError) as raised:
                    validate_contract(case["contract"], payload)
                self.assertEqual(case["error_code"], raised.exception.code)


if __name__ == "__main__":
    unittest.main()
