from __future__ import annotations

import ast
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
LIB_DIR = SCRIPTS_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))


def binding_module():
    from issue_implementation_loop import approved_spec_binding

    return approved_spec_binding


def capability_script_module():
    spec = importlib.util.spec_from_file_location(
        "issue_loop_check_capabilities_under_test",
        SCRIPTS_DIR / "check_capabilities.py",
    )
    assert spec and spec.loader
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


ASB_PUBLIC_ACCEPTANCE_MATRIX = {
    "ASB-01": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_01_02_identify_and_seal_preserve_spec_and_verify",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_01_02_seal_rolls_back_when_spec_changes_during_publication",
    ),
    "ASB-02": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_01_02_identify_and_seal_preserve_spec_and_verify",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_01_02_seal_rolls_back_when_spec_changes_during_publication",
    ),
    "ASB-03": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_03_changed_spec_prevents_seal_and_output_mutation",
    ),
    "ASB-04": (
        "test_validation.ValidationTests.test_asb_04_execution_envelope_v4_verifies_valid_chain",
        "test_worker_packet.WorkerPacketTests.test_build_worker_packet_outputs_valid_v3_bounded_packet",
        "test_operation_selection.OperationSelectionTests.test_asb_04_valid_binding_allows_review_selection",
        "test_review_gate.ReviewGateTests.test_asb_04_execution_result_v2_accepts_active_binding_and_review_range",
    ),
    "ASB-05": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_05_missing_spec_has_stable_error",
    ),
    "ASB-06": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_06_approval_failures_have_stable_errors",
    ),
    "ASB-07": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_07_missing_and_malformed_digests_have_stable_errors",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_07_rejects_malformed_packet_digest",
    ),
    "ASB-08": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_08_current_spec_drift_invalidates_sealed_packet",
    ),
    "ASB-09": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_09_packet_drift_invalidates_pinned_ref",
    ),
    "ASB-10": (
        "test_worker_packet.WorkerPacketTests.test_asb_10_11_worker_projection_missing_and_drift_fail_closed",
    ),
    "ASB-11": (
        "test_worker_packet.WorkerPacketTests.test_asb_10_11_worker_projection_missing_and_drift_fail_closed",
        "test_worker_packet.WorkerPacketTests.test_asb_11_reviewer_projection_one_byte_drift_fails_before_start",
    ),
    "ASB-12": (
        "test_worker_packet.WorkerPacketTests.test_asb_12_worker_packet_rejects_runtime_binding_mismatch",
    ),
    "ASB-13": (
        "test_validation.ValidationTests.test_asb_13_worker_report_intake_rejects_resealed_runtime_binding",
    ),
    "ASB-14": (
        "test_review_gate.ReviewGateTests.test_asb_14_completion_rechecks_current_spec_before_terminal_result",
        "test_operation_selection.OperationSelectionTests.test_asb_14_to_16_stale_spec_blocks_review_and_delivery_but_not_status",
    ),
    "ASB-15": (
        "test_delivery.DeliveryTests.test_asb_15_delivery_rechecks_spec_after_terminal_runtime",
    ),
    "ASB-16": (
        "test_operation_selection.OperationSelectionTests.test_asb_14_to_16_stale_spec_blocks_review_and_delivery_but_not_status",
    ),
    "ASB-17": (
        "test_resume_brief.ResumeBriefTests.test_resume_rejects_stale_packet_even_when_runtime_envelope_and_events_are_unchanged",
        "test_resume_brief.ResumeBriefTests.test_asb_17_spec_drift_after_resume_metadata_publication_is_rejected",
    ),
    "ASB-18": (
        "test_runtime_state.RuntimeStateTests.test_rebuild_runtime_state_rejects_mixed_binding_events",
    ),
    "ASB-19": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_19_connected_reseal_epoch_accepts_b_rejects_a_artifacts",
    ),
    "ASB-20": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_20_rejects_unsafe_and_non_regular_spec_paths",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_20_embedded_nul_is_stable_in_python_and_cli",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_20_public_cli_escape_returns_stable_path_outside_repo_json",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_20_repo_escape_is_path_outside_repo",
    ),
    "ASB-21": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_21_detects_file_replacement_during_validation",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_21_detects_parent_symlink_replacement_during_validation",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_21_seal_rejects_output_parent_swap_without_external_write",
    ),
    "ASB-22": (
        "test_review_gate.ReviewGateTests.test_asb_22_completion_rejects_result_binding_or_review_range_mismatch",
        "test_validation.ValidationTests.test_asb_22_reviewer_report_rejects_final_alignment_binding_mismatch",
        "test_delivery.DeliveryTests.test_asb_22_delivery_rejects_stale_execution_result_binding",
    ),
    "ASB-23": (
        "test_validation.ValidationTests.test_validate_input_packet_v2_rejects_closed_shape_and_binding_errors",
        "test_validation.ValidationTests.test_execution_envelope_v1_through_v3_are_unsupported",
        "test_worker_packet.WorkerPacketTests.test_worker_packet_v1_and_v2_are_unsupported_and_v1_schema_is_removed",
        "test_runtime_state.RuntimeStateTests.test_rebuild_runtime_state_rejects_event_v1_and_missing_binding",
        "test_runtime_state.RuntimeStateTests.test_validate_runtime_state_rejects_v1_and_old_epoch_human_request",
        "test_validation.ValidationTests.test_worker_report_v1_is_unsupported",
        "test_candidate_registry.CandidateRegistryTests.test_registry_v1_is_schema_unsupported",
        "test_resume_brief.ResumeBriefTests.test_resume_metadata_v3_binds_current_epoch_and_rejects_v2_or_meta_less",
        "test_review_gate.ReviewGateTests.test_execution_result_v1_is_unsupported",
        "test_delivery.DeliveryTests.test_delivery_plan_v1_is_unsupported",
    ),
    "ASB-24": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_24_all_current_artifact_surfaces_are_generic",
    ),
    "ASB-25": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_25_codex_and_hermes_host_envs_return_same_cli_binding_and_error",
        "test_entrypoint.EntrypointTests.test_skill_entrypoint_documents_seal_host_capability_boundary",
    ),
    "ASB-26": (
        "test_validation.ValidationTests.test_asb_26_execution_envelope_requires_gate_commit",
    ),
    "ASB-27": (
        "test_validation.ValidationTests.test_asb_27_execution_envelope_rejects_non_ancestor_gate",
    ),
    "ASB-28": (
        "test_validation.ValidationTests.test_asb_28_execution_envelope_rejects_gate_tree_blob_mismatch",
    ),
    "ASB-29": (
        "test_candidate_registry.CandidateRegistryTests.test_delivery_rejects_registry_from_old_binding_epoch",
    ),
    "ASB-30": (
        "test_runtime_state.RuntimeStateTests.test_asb_30_reapproval_rejects_old_and_accepts_rerecorded_request",
    ),
    "ASB-31": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_31_32_rejects_artifact_layout_mutations_without_output_mutation",
    ),
    "ASB-32": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_31_32_rejects_artifact_layout_mutations_without_output_mutation",
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_32_rejects_packet_copied_outside_artifact_root",
    ),
    "ASB-33": (
        "test_approved_spec_binding.ApprovedSpecBindingTests.test_asb_01_02_identify_and_seal_preserve_spec_and_verify",
    ),
    "ASB-34": (
        "test_grill_to_pr_loop.GrillToPrLoopTests.test_asb_34_current_epic_tracks_only_durable_planning_artifacts",
        "test_grill_to_pr_loop.GrillToPrLoopTests.test_asb_34_detects_tracked_flat_v4_execution_envelope",
    ),
    "ASB-35": (
        "test_worker_packet.WorkerPacketTests.test_asb_35_linked_coordinator_uses_exact_git_common_runtime_root",
    ),
    "ASB-36": (
        "test_grill_to_pr_loop.GrillToPrLoopTests.test_asb_36_tracked_json_templates_use_nested_epic_paths",
    ),
}


ASB24_CURRENT_ARTIFACT_SURFACE = {
    "input_packet": (
        "assets/schemas/input-packet.schema.json",
        "assets/templates/input-packet.json",
        "scripts/lib/issue_implementation_loop/approved_spec_binding.py",
        "scripts/lib/issue_implementation_loop/validation/input_packet.py",
        "scripts/approved_spec_binding.py",
        "scripts/validate_input_packet.py",
    ),
    "execution_envelope": (
        "assets/schemas/execution-envelope.schema.json",
        "assets/templates/execution-envelope.json",
        "scripts/lib/issue_implementation_loop/validation/execution_envelope.py",
        "scripts/validate_execution_envelope.py",
    ),
    "event_runtime_human_request": (
        "assets/schemas/event.schema.json",
        "assets/schemas/runtime-state.schema.json",
        "assets/schemas/human-request.schema.json",
        "scripts/lib/issue_implementation_loop/runtime_state.py",
        "scripts/lib/issue_implementation_loop/validation/runtime_state.py",
        "scripts/rebuild_runtime_state.py",
        "scripts/validate_runtime_state.py",
    ),
    "worker_reviewer_packet_report": (
        "assets/schemas/worker-packet.schema.json",
        "assets/schemas/worker-report.schema.json",
        "assets/templates/worker-packet.json",
        "scripts/lib/issue_implementation_loop/worker_packet.py",
        "scripts/lib/issue_implementation_loop/validation/worker_packet.py",
        "scripts/lib/issue_implementation_loop/validation/worker_report.py",
        "scripts/build_worker_packet.py",
        "scripts/validate_worker_packet.py",
        "scripts/validate_worker_report.py",
    ),
    "hardening_registry": (
        "assets/schemas/hardening-candidates.schema.json",
        "assets/templates/hardening-candidates.json",
        "assets/templates/decisions.md",
        "scripts/lib/issue_implementation_loop/delivery.py",
    ),
    "resume_metadata": (
        "assets/templates/resume-brief.md",
        "scripts/lib/issue_implementation_loop/resume_brief.py",
        "scripts/build_resume_brief.py",
        "scripts/validate_resume_brief.py",
    ),
    "execution_result": (
        "assets/templates/execution-result.json",
        "assets/templates/completion-summary.md",
        "scripts/lib/issue_implementation_loop/validation/execution_result.py",
        "scripts/validate_execution_result.py",
    ),
    "delivery_plan": (
        "assets/templates/delivery-plan.json",
        "scripts/lib/issue_implementation_loop/validation/delivery_plan.py",
        "scripts/validate_delivery_plan.py",
    ),
    "binding_gate_status_capability": (
        "scripts/lib/issue_implementation_loop/operation_selection.py",
        "scripts/check_capabilities.py",
        "scripts/compute_next_actions.py",
        "scripts/reconcile_git_state.py",
        "scripts/select_operation.py",
    ),
}


class ApprovedSpecBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.spec_path = "knowledge/wiki/syntheses/example/spec.md"
        self.issues_path = "knowledge/wiki/syntheses/example/issues.md"
        (self.repo / self.spec_path).parent.mkdir(parents=True)
        (self.repo / self.spec_path).write_bytes("承認済み仕様\n".encode())
        (self.repo / self.issues_path).write_text("# Issues\n", encoding="utf-8")
        self.draft_path = self.repo / "draft.json"
        self.output_path = self.repo / "knowledge/wiki/syntheses/example/input-packet.json"
        self.draft_path.write_text(
            json.dumps(self.draft(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def draft(self) -> dict:
        return {
            "schema_version": 2,
            "epic_id": "example",
            "artifact_root": "knowledge/wiki/syntheses/example",
            "work_items": [
                {
                    "id": "ASBC-001",
                    "title": "承認済み仕様を packet に束縛する",
                    "source": {"type": "local", "path": self.issues_path},
                    "acceptance_criteria": ["public operation が成功する"],
                    "non_goals": ["remote write は行わない"],
                    "verification": ["python3 -m unittest"],
                    "write_scope": ["path:skills/issue-implementation-loop"],
                    "dependencies": [],
                }
            ],
            "delivery_intent": "local_only",
        }

    @staticmethod
    def approval() -> dict:
        return {
            "decision": "approved",
            "subject": "spec_binding",
            "actor_expression": "session-user",
            "approved_at": "2026-07-21T17:55:36+09:00",
            "scope": {
                "accepted_decisions": True,
                "non_goals": True,
                "acceptance_criteria": True,
                "verification": True,
                "remote_policy": True,
                "stop_conditions": True,
            },
        }

    def seal(self):
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        ref = module.seal_input_packet(
            self.repo,
            self.draft_path.relative_to(self.repo).as_posix(),
            self.output_path.relative_to(self.repo).as_posix(),
            revision,
            self.approval(),
        )
        return module, revision, ref

    def assert_code(self, expected: str, operation) -> None:
        module = binding_module()
        with self.assertRaises(module.BindingError) as raised:
            operation()
        self.assertEqual(raised.exception.code, expected)

    def test_asb_public_acceptance_matrix_is_complete_and_public(self) -> None:
        expected_ids = [f"ASB-{number:02d}" for number in range(1, 37)]
        module_tree = ast.parse(
            Path(__file__).read_text(encoding="utf-8"), filename=__file__
        )
        matrix_assignment = next(
            node
            for node in module_tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "ASB_PUBLIC_ACCEPTANCE_MATRIX"
                for target in node.targets
            )
        )
        self.assertIsInstance(matrix_assignment.value, ast.Dict)
        source_ids = [ast.literal_eval(key) for key in matrix_assignment.value.keys]
        self.assertEqual(source_ids, expected_ids)
        self.assertEqual(len(source_ids), len(set(source_ids)))

        matrix_ids = list(ASB_PUBLIC_ACCEPTANCE_MATRIX)
        self.assertEqual(matrix_ids, expected_ids)

        public_tests: set[str] = set()
        public_test_roots = (
            Path(__file__).parent,
            SKILL_DIR.parent / "grill-to-pr-loop" / "tests",
        )
        test_paths = sorted(
            path for root in public_test_roots for path in root.glob("test_*.py")
        )
        for test_path in test_paths:
            tree = ast.parse(
                test_path.read_text(encoding="utf-8"), filename=str(test_path)
            )
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or not any(
                    isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    for base in node.bases
                ):
                    continue
                for child in node.body:
                    if isinstance(
                        child, (ast.FunctionDef, ast.AsyncFunctionDef)
                    ) and child.name.startswith("test_"):
                        public_tests.add(f"{test_path.stem}.{node.name}.{child.name}")

        for acceptance_id, test_names in ASB_PUBLIC_ACCEPTANCE_MATRIX.items():
            with self.subTest(acceptance_id=acceptance_id):
                self.assertTrue(test_names)
                self.assertTrue(all(name in public_tests for name in test_names))

    def test_asb_01_02_identify_and_seal_preserve_spec_and_verify(self) -> None:
        before = (self.repo / self.spec_path).read_bytes()

        module, revision, ref = self.seal()

        self.assertEqual((self.repo / self.spec_path).read_bytes(), before)
        self.assertEqual(revision.path, self.spec_path)
        self.assertEqual(len(revision.sha256), 64)
        self.assertEqual(ref.path, self.output_path.relative_to(self.repo).as_posix())
        sealed = self.output_path.read_bytes()
        self.assertTrue(sealed.endswith(b"\n"))
        self.assertNotIn(b"\\u", sealed)
        verified = module.verify_chain(self.repo, {"input_packet": ref.to_dict()})
        self.assertTrue(verified.valid)
        self.assertEqual(verified.spec_revision, revision)
        _, repeated_revision, repeated_ref = self.seal()
        self.assertEqual(repeated_revision, revision)
        self.assertEqual(repeated_ref, ref)
        self.assertEqual(self.output_path.read_bytes(), sealed)

    def test_asb_01_02_seal_rolls_back_when_spec_changes_during_publication(self) -> None:
        module = binding_module()
        approved_spec = (self.repo / self.spec_path).read_bytes()
        revision = module.identify_spec(self.repo, self.spec_path)
        capabilities = module.probe_seal_capabilities()

        for existing_output in (None, b"previous sealed packet\n"):
            with self.subTest(existing_output=existing_output is not None):
                (self.repo / self.spec_path).write_bytes(approved_spec)
                if existing_output is None:
                    self.output_path.unlink(missing_ok=True)
                else:
                    self.output_path.write_bytes(existing_output)
                original_replace = module.os.replace
                spec_mutated = False

                def mutate_spec_after_install(
                    source,
                    destination,
                    *,
                    src_dir_fd=None,
                    dst_dir_fd=None,
                ):
                    nonlocal spec_mutated
                    result = original_replace(
                        source,
                        destination,
                        src_dir_fd=src_dir_fd,
                        dst_dir_fd=dst_dir_fd,
                    )
                    if (
                        not spec_mutated
                        and destination == self.output_path.name
                    ):
                        (self.repo / self.spec_path).write_bytes(
                            b"spec mutated after packet install\n"
                        )
                        spec_mutated = True
                    return result

                with mock.patch.object(
                    module, "probe_seal_capabilities", return_value=capabilities
                ), mock.patch.object(
                    module.os, "replace", side_effect=mutate_spec_after_install
                ):
                    with self.assertRaises(module.BindingError) as raised:
                        module.seal_input_packet(
                            self.repo,
                            self.draft_path.relative_to(self.repo).as_posix(),
                            self.output_path.relative_to(self.repo).as_posix(),
                            revision,
                            self.approval(),
                        )

                self.assertTrue(spec_mutated, raised.exception.to_dict())
                self.assertEqual(
                    raised.exception.code, "FILE_CHANGED_DURING_VALIDATION"
                )
                if existing_output is None:
                    self.assertFalse(self.output_path.exists())
                else:
                    self.assertEqual(self.output_path.read_bytes(), existing_output)

    def test_asb_03_changed_spec_prevents_seal_and_output_mutation(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        (self.repo / self.spec_path).write_bytes("承認後の変更\n".encode())
        sentinel = b"existing output\n"
        self.output_path.write_bytes(sentinel)

        self.assert_code(
            "SPEC_DIGEST_MISMATCH",
            lambda: module.seal_input_packet(
                self.repo,
                self.draft_path.relative_to(self.repo).as_posix(),
                self.output_path.relative_to(self.repo).as_posix(),
                revision,
                self.approval(),
            ),
        )
        self.assertEqual(self.output_path.read_bytes(), sentinel)

    def test_asb_05_missing_spec_has_stable_error(self) -> None:
        module = binding_module()
        self.assert_code(
            "SPEC_MISSING",
            lambda: module.identify_spec(self.repo, "knowledge/missing.md"),
        )

    def test_asb_06_approval_failures_have_stable_errors(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        cases = []
        cases.append(("APPROVAL_MISSING", None))
        not_approved = self.approval()
        not_approved["decision"] = "rejected"
        cases.append(("APPROVAL_NOT_APPROVED", not_approved))
        incomplete = self.approval()
        incomplete["scope"]["verification"] = False
        cases.append(("APPROVAL_SCOPE_INCOMPLETE", incomplete))
        for expected, approval in cases:
            with self.subTest(expected=expected):
                self.assert_code(
                    expected,
                    lambda approval=approval: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        revision,
                        approval,
                    ),
                )

    def test_asb_07_missing_and_malformed_digests_have_stable_errors(self) -> None:
        module = binding_module()
        for expected, value in (("DIGEST_MISSING", ""), ("DIGEST_MALFORMED", "sha256:bad")):
            with self.subTest(expected=expected):
                self.assert_code(
                    expected,
                    lambda value=value: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        {"path": self.spec_path, "sha256": value},
                        self.approval(),
                    ),
                )
        module, _, ref = self.seal()
        self.assert_code(
            "DIGEST_MISSING",
            lambda: module.verify_chain(
                self.repo, {"input_packet": {"path": ref.path}}
            ),
        )

    def test_asb_07_rejects_malformed_packet_digest(self) -> None:
        module, _, ref = self.seal()

        self.assert_code(
            "DIGEST_MALFORMED",
            lambda: module.verify_chain(
                self.repo,
                {"input_packet": {"path": ref.path, "sha256": "sha256:bad"}},
            ),
        )

    def test_asb_08_current_spec_drift_invalidates_sealed_packet(self) -> None:
        module, _, ref = self.seal()
        (self.repo / self.spec_path).write_bytes("one byte drift!\n".encode())

        self.assert_code(
            "SPEC_DIGEST_MISMATCH",
            lambda: module.verify_chain(self.repo, {"input_packet": ref.to_dict()}),
        )

    def test_asb_09_packet_drift_invalidates_pinned_ref(self) -> None:
        module, _, ref = self.seal()
        self.output_path.write_bytes(self.output_path.read_bytes() + b" ")

        self.assert_code(
            "INPUT_PACKET_DIGEST_MISMATCH",
            lambda: module.verify_chain(self.repo, {"input_packet": ref.to_dict()}),
        )

    def test_asb_31_32_rejects_artifact_layout_mutations_without_output_mutation(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        cases = {
            "flat artifact root": {"artifact_root": "knowledge/wiki/syntheses"},
            "foreign epic root": {
                "artifact_root": "knowledge/wiki/syntheses/another-epic"
            },
            "ledger outside root": {
                "source_path": "knowledge/wiki/syntheses/shared/issues.md"
            },
        }

        for name, mutation in cases.items():
            with self.subTest(name=name):
                draft = self.draft()
                if "artifact_root" in mutation:
                    draft["artifact_root"] = mutation["artifact_root"]
                if "source_path" in mutation:
                    draft["work_items"][0]["source"]["path"] = mutation["source_path"]
                    source = self.repo / mutation["source_path"]
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text("# Shared issues\n", encoding="utf-8")
                self.draft_path.write_text(
                    json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                sentinel = f"existing output: {name}\n".encode()
                self.output_path.write_bytes(sentinel)

                with self.assertRaises(module.BindingError) as raised:
                    module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        revision,
                        self.approval(),
                    )

                self.assertEqual(raised.exception.code, "ARTIFACT_LAYOUT_MISMATCH")
                self.assertEqual(
                    raised.exception.action, "return_to_execution_plan_gate"
                )
                self.assertEqual(self.output_path.read_bytes(), sentinel)

        self.draft_path.write_text(
            json.dumps(self.draft(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        outside_output = self.repo / "knowledge/wiki/syntheses/input-packet.json"
        outside_output.write_bytes(b"outside sentinel\n")
        with self.assertRaises(module.BindingError) as raised:
            module.seal_input_packet(
                self.repo,
                self.draft_path.relative_to(self.repo).as_posix(),
                outside_output.relative_to(self.repo).as_posix(),
                revision,
                self.approval(),
            )
        self.assertEqual(raised.exception.code, "ARTIFACT_LAYOUT_MISMATCH")
        self.assertEqual(outside_output.read_bytes(), b"outside sentinel\n")

    def test_asb_32_rejects_packet_copied_outside_artifact_root(self) -> None:
        module, _, ref = self.seal()
        copied_path = self.repo / "knowledge/wiki/syntheses/input-packet.json"
        copied_path.write_bytes(self.output_path.read_bytes())
        copied_ref = {
            "path": copied_path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(copied_path.read_bytes()).hexdigest(),
        }

        self.assert_code(
            "ARTIFACT_LAYOUT_MISMATCH",
            lambda: module.verify_chain(self.repo, {"input_packet": copied_ref}),
        )

    def test_asb_19_connected_reseal_epoch_accepts_b_rejects_a_artifacts(self) -> None:
        import _helpers as fixtures

        with tempfile.TemporaryDirectory() as tmp:
            repo, binding_a, _ = fixtures.create_binding_repo(Path(tmp))
            envelope_a = fixtures.binding_envelope(repo, binding_a)
            runtime_a = {
                "schema_version": 2,
                "epic_id": envelope_a["epic_id"],
                "envelope_revision": envelope_a["revision"],
                "approved_spec_binding": dict(binding_a),
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                        "base_sha": fixtures.BASE_SHA,
                        "head_sha": fixtures.HEAD_SHA,
                        "review": {
                            "status": "approved",
                            "range": fixtures.REVIEW_RANGE,
                        },
                    }
                },
                "human_requests": [],
            }
            review_packet_a = fixtures.current_worker_packet(
                repo, binding_a, task_kind="review"
            )
            review_a = fixtures.current_worker_report(
                repo, binding_a, review_packet_a
            )
            result_a = fixtures.current_execution_result(envelope_a, runtime_a)
            review_packet_a_path = repo / "review-packet-a.json"
            review_a_path = repo / "review-a.json"
            fixtures.write_json(review_packet_a_path, review_packet_a)
            fixtures.write_json(review_a_path, review_a)
            accepted_review_a = fixtures.run_script(
                "validate_worker_report.py",
                str(review_a_path),
                "--dispatch-packet",
                str(review_packet_a_path),
                "--runtime-state",
                review_packet_a["source_revision"]["runtime_state"]["path"],
                "--envelope",
                review_packet_a["source_revision"]["execution_envelope"]["path"],
                *fixtures.worker_report_trust_args(repo),
                "--json",
            )
            self.assertEqual(accepted_review_a.returncode, 0, accepted_review_a.stderr)
            envelope_a_path = repo / "execution-envelope.json"
            runtime_a_path = repo / "runtime-state.json"
            result_a_path = repo / "execution-result-a.json"
            fixtures.write_json(envelope_a_path, envelope_a)
            fixtures.write_json(runtime_a_path, runtime_a)
            fixtures.write_json(result_a_path, result_a)
            accepted_result_a = fixtures.run_script(
                "validate_execution_result.py",
                str(envelope_a_path),
                str(runtime_a_path),
                str(result_a_path),
                "--repo-root",
                str(repo),
                "--json",
            )
            self.assertEqual(accepted_result_a.returncode, 0, accepted_result_a.stderr)

            packet_path = repo / binding_a["path"]
            packet_a = json.loads(packet_path.read_text(encoding="utf-8"))
            draft_b = {
                key: value
                for key, value in packet_a.items()
                if key not in {"spec_binding", "approval_evidence"}
            }
            draft_path = repo / "draft-b.json"
            fixtures.write_json(draft_path, draft_b)
            spec_path = repo / packet_a["spec_binding"]["path"]
            spec_path.write_text("re-approved spec B\n", encoding="utf-8")
            module = binding_module()
            revision_b = module.identify_spec(repo, packet_a["spec_binding"]["path"])
            approval_b = self.approval()
            approval_b["actor_expression"] = "session-user-reapproval"
            approval_b["approved_at"] = "2026-07-21T20:00:00+09:00"
            ref_b = module.seal_input_packet(
                repo,
                draft_path.relative_to(repo).as_posix(),
                binding_a["path"],
                revision_b,
                approval_b,
            )
            packet_b = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(packet_b["approval_evidence"], approval_b)
            fixtures.git(repo, "add", packet_a["spec_binding"]["path"], ref_b.path)
            fixtures.git(repo, "commit", "-q", "-m", "approved gate B")
            gate_b = fixtures.git(repo, "rev-parse", "HEAD")
            binding_b = {
                "path": ref_b.path,
                "sha256": ref_b.sha256,
                "gate_commit": gate_b,
            }
            self.assertNotEqual(binding_a, binding_b)
            self.assertTrue(
                module.verify_chain(repo, {"input_packet": ref_b.to_dict()}).valid
            )

            envelope_b = fixtures.binding_envelope(repo, binding_b)
            envelope_b["revision"] = 2
            envelope_path = repo / "execution-envelope.json"
            fixtures.write_json(envelope_path, envelope_b)
            checked_envelope = fixtures.run_script(
                "validate_execution_envelope.py",
                str(envelope_path),
                "--repo-root",
                str(repo),
                "--json",
            )
            self.assertEqual(checked_envelope.returncode, 0, checked_envelope.stderr)

            events_path = repo / "events-b.jsonl"
            events_path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "event_id": "E-B-001",
                        "epic_id": envelope_b["epic_id"],
                        "envelope_revision": envelope_b["revision"],
                        "approved_spec_binding": binding_b,
                        "type": "issue_status_changed",
                        "issue": "ASBC-002",
                        "status": "PENDING",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rebuilt = fixtures.run_script(
                "rebuild_runtime_state.py",
                str(events_path),
                "--repo-root",
                str(repo),
                "--envelope",
                str(envelope_path),
            )
            self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
            runtime_b = json.loads(rebuilt.stdout)
            self.assertEqual(runtime_b["approved_spec_binding"], binding_b)
            runtime_path = repo / "runtime-state.json"
            fixtures.write_json(runtime_path, runtime_b)
            checked_runtime = fixtures.run_script(
                "validate_runtime_state.py", str(runtime_path), "--json"
            )
            self.assertEqual(checked_runtime.returncode, 0, checked_runtime.stderr)

            review_packet_b = fixtures.current_worker_packet(
                repo, binding_b, task_kind="review"
            )
            fixtures.write_json(envelope_path, envelope_b)
            fixtures.write_json(runtime_path, runtime_b)
            review_packet_b["source_revision"]["execution_envelope"].update(
                {
                    "revision": envelope_b["revision"],
                    "sha256": hashlib.sha256(envelope_path.read_bytes()).hexdigest(),
                }
            )
            review_packet_b["source_revision"]["runtime_state"].update(
                {
                    "envelope_revision": runtime_b["envelope_revision"],
                    "sha256": hashlib.sha256(runtime_path.read_bytes()).hexdigest(),
                }
            )
            review_packet_path = repo / "review-packet-b.json"
            fixtures.write_json(review_packet_path, review_packet_b)
            rejected_review = fixtures.run_script(
                "validate_worker_report.py",
                str(review_a_path),
                "--dispatch-packet",
                str(review_packet_path),
                "--runtime-state",
                str(runtime_path),
                "--envelope",
                str(envelope_path),
                *fixtures.worker_report_trust_args(repo),
                "--json",
            )
            self.assertEqual(rejected_review.returncode, 1)
            self.assertEqual(
                json.loads(rejected_review.stdout)["errors"], ["BINDING_MISMATCH"]
            )

            rejected_result = fixtures.run_script(
                "validate_execution_result.py",
                str(envelope_path),
                str(runtime_path),
                str(result_a_path),
                "--repo-root",
                str(repo),
                "--json",
            )
            self.assertEqual(rejected_result.returncode, 1)
            self.assertIn(
                "BINDING_MISMATCH", json.loads(rejected_result.stdout)["errors"]
            )

    def test_asb_20_rejects_unsafe_and_non_regular_spec_paths(self) -> None:
        module = binding_module()
        symlink_target = self.repo / "target.md"
        symlink_target.write_text("target\n", encoding="utf-8")
        (self.repo / "linked.md").symlink_to(symlink_target)
        (self.repo / "linked-dir").symlink_to(self.repo / "knowledge", target_is_directory=True)
        cases = [
            ("PATH_ABSOLUTE", str(self.repo / self.spec_path)),
            ("PATH_TRAVERSAL", "knowledge/../target.md"),
            ("PATH_TRAVERSAL", "knowledge\\target.md"),
            ("PATH_SYMLINK", "linked.md"),
            ("PATH_SYMLINK", "linked-dir/wiki/syntheses/example-spec.md"),
            ("PATH_NOT_REGULAR_FILE", "knowledge"),
        ]
        for expected, path in cases:
            with self.subTest(path=path):
                self.assert_code(expected, lambda path=path: module.identify_spec(self.repo, path))

    def test_asb_20_embedded_nul_is_stable_in_python_and_cli(self) -> None:
        module, _, ref = self.seal()
        self.assert_code(
            "PATH_TRAVERSAL",
            lambda: module.identify_spec(self.repo, "knowledge/invalid\x00spec.md"),
        )
        packet = json.loads(self.output_path.read_text(encoding="utf-8"))
        packet["spec_binding"]["path"] = "knowledge/invalid\x00spec.md"
        raw = (json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        self.output_path.write_bytes(raw)
        packet_digest = __import__("hashlib").sha256(raw).hexdigest()

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "verify",
                "--repo-root",
                str(self.repo),
                "--input-packet",
                ref.path,
                "--input-packet-sha256",
                packet_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["code"], "PATH_TRAVERSAL")
        self.assertNotIn("Traceback", result.stderr)

    def test_asb_20_repo_escape_is_path_outside_repo(self) -> None:
        module = binding_module()
        outside_path = self.repo.parent / "outside-spec.md"
        outside_path.write_text("outside\n", encoding="utf-8")

        self.assert_code(
            "PATH_OUTSIDE_REPO",
            lambda: module.trusted_argument_path(self.repo, outside_path),
        )

    def test_asb_20_public_cli_escape_returns_stable_path_outside_repo_json(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        escaped_output = "knowledge/wiki/escaped-input-packet.json"
        command = [
            sys.executable,
            str(SCRIPTS_DIR / "approved_spec_binding.py"),
            "seal",
            "--repo-root",
            str(self.repo),
            "--draft-packet",
            self.draft_path.relative_to(self.repo).as_posix(),
            "--output-packet",
            escaped_output,
            "--spec-path",
            revision.path,
            "--spec-sha256",
            revision.sha256,
            "--decision",
            "approved",
            "--subject",
            "spec_binding",
            "--actor-expression",
            "session-user",
            "--approved-at",
            "2026-07-21T17:55:36+09:00",
        ]
        for field in sorted(module.APPROVAL_SCOPE_FIELDS):
            command.extend(("--approve-scope", field))

        result = subprocess.run(
            command, check=False, capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "valid": False,
                "code": "ARTIFACT_LAYOUT_MISMATCH",
                "action": "return_to_execution_plan_gate",
                "path": escaped_output,
            },
        )
        self.assertEqual(result.stderr, "")
        self.assertFalse((self.repo / escaped_output).exists())

        narrowed_root = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "identify",
                "--repo-root",
                str(self.repo / "knowledge"),
                "--spec-path",
                "wiki/syntheses/example-spec.md",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(narrowed_root.returncode, 1)
        self.assertEqual(
            json.loads(narrowed_root.stdout),
            {
                "valid": False,
                "code": "PATH_OUTSIDE_REPO",
                "action": "regenerate_artifact",
            },
        )
        self.assertEqual(narrowed_root.stderr, "")

    def test_asb_21_detects_file_replacement_during_validation(self) -> None:
        module = binding_module()
        original_read = module.os.read
        replaced = False
        original_inode = os.lstat(self.repo / self.spec_path).st_ino

        def replacing_read(fd: int, count: int) -> bytes:
            nonlocal replaced
            chunk = original_read(fd, count)
            if chunk and not replaced and os.fstat(fd).st_ino == original_inode:
                replaced = True
                replacement = self.repo / "replacement.md"
                replacement.write_bytes("replacement\n".encode())
                os.replace(replacement, self.repo / self.spec_path)
            return chunk

        with mock.patch.object(module.os, "read", side_effect=replacing_read):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_asb_21_detects_parent_symlink_replacement_during_validation(self) -> None:
        module = binding_module()
        original_read = module.os.read
        replaced = False
        original_inode = os.lstat(self.repo / self.spec_path).st_ino

        def replacing_parent(fd: int, count: int) -> bytes:
            nonlocal replaced
            chunk = original_read(fd, count)
            if chunk and not replaced and os.fstat(fd).st_ino == original_inode:
                replaced = True
                os.replace(self.repo / "knowledge", self.repo / "knowledge-original")
                (self.repo / "knowledge").symlink_to(
                    self.repo / "knowledge-original", target_is_directory=True
                )
            return chunk

        with mock.patch.object(module.os, "read", side_effect=replacing_parent):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_asb_21_seal_rejects_output_parent_swap_without_external_write(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        output_parent = self.output_path.parent
        moved_parent = self.repo / "moved-syntheses"
        original_open = module.os.open
        capabilities = module.probe_seal_capabilities()
        swapped = False
        sentinel = b"existing output\n"
        self.output_path.write_bytes(sentinel)

        with tempfile.TemporaryDirectory() as outside_tmp:
            outside = Path(outside_tmp)

            def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                rendered = os.fspath(path)
                if not swapped and ".input-packet.json." in rendered:
                    swapped = True
                    os.rename(output_parent, moved_parent)
                    output_parent.symlink_to(outside, target_is_directory=True)
                if dir_fd is None:
                    return original_open(path, flags, mode)
                return original_open(path, flags, mode, dir_fd=dir_fd)

            with mock.patch.object(
                module, "probe_seal_capabilities", return_value=capabilities
            ), mock.patch.object(module.os, "open", side_effect=swapping_open):
                self.assert_code(
                    "FILE_CHANGED_DURING_VALIDATION",
                    lambda: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        revision,
                        self.approval(),
                    ),
                )
            self.assertFalse((outside / self.output_path.name).exists())
            self.assertFalse(any(outside.iterdir()))
            self.assertEqual((moved_parent / self.output_path.name).read_bytes(), sentinel)

    def test_failed_rollback_preserves_discoverable_recovery_copy(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        sentinel = b"original packet bytes\n"
        self.output_path.write_bytes(sentinel)
        original_verify = module._verify_directory_chain
        original_replace = module.os.replace
        capabilities = module.probe_seal_capabilities()
        verify_calls = 0
        replace_calls = 0

        def fail_after_install(identities, output_path):
            nonlocal verify_calls
            verify_calls += 1
            if verify_calls == 3:
                raise module.BindingError(
                    "FILE_CHANGED_DURING_VALIDATION", path=output_path
                )
            return original_verify(identities, output_path)

        def fail_rollback(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 2:
                raise OSError("injected rollback failure")
            return original_replace(
                src,
                dst,
                src_dir_fd=src_dir_fd,
                dst_dir_fd=dst_dir_fd,
            )

        with mock.patch.object(
            module, "_verify_directory_chain", side_effect=fail_after_install
        ), mock.patch.object(
            module, "probe_seal_capabilities", return_value=capabilities
        ), mock.patch.object(module.os, "replace", side_effect=fail_rollback):
            with self.assertRaises(module.BindingError) as raised:
                module.seal_input_packet(
                    self.repo,
                    self.draft_path.relative_to(self.repo).as_posix(),
                    self.output_path.relative_to(self.repo).as_posix(),
                    revision,
                    self.approval(),
                )

        self.assertEqual(raised.exception.code, "FILE_CHANGED_DURING_VALIDATION")
        self.assertIsNotNone(raised.exception.recovery_path)
        recovery = self.repo / raised.exception.recovery_path
        self.assertTrue(recovery.is_file())
        self.assertEqual(recovery.read_bytes(), sentinel)
        self.assertNotEqual(self.output_path.read_bytes(), sentinel)
        self.assertEqual(
            raised.exception.to_dict()["recovery_path"],
            raised.exception.recovery_path,
        )

    def test_malformed_root_and_read_os_errors_are_stable(self) -> None:
        module = binding_module()
        self.assert_code(
            "PATH_OUTSIDE_REPO",
            lambda: module.identify_spec(None, self.spec_path),
        )
        original_fstat = module.os.fstat
        spec_inode = os.lstat(self.repo / self.spec_path).st_ino

        def failing_fstat(descriptor):
            result = original_fstat(descriptor)
            if result.st_ino == spec_inode:
                raise OSError("injected fstat failure with sensitive payload")
            return result

        with mock.patch.object(module.os, "fstat", side_effect=failing_fstat):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_binding_cli_failure_is_stable_json_without_traceback(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "identify",
                "--repo-root",
                "",
                "--spec-path",
                self.spec_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["code"], "PATH_OUTSIDE_REPO")
        self.assertNotIn("Traceback", result.stderr)

    def test_seal_platform_capability_is_probed_and_fails_closed(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        self.output_path.write_bytes(b"unchanged\n")
        unsupported = module.SealCapabilities(
            supported=False,
            missing=("dir_fd:open",),
        )
        with mock.patch.object(
            module, "probe_seal_capabilities", return_value=unsupported
        ):
            self.assert_code(
                "PLATFORM_UNSUPPORTED",
                lambda: module.seal_input_packet(
                    self.repo,
                    self.draft_path.relative_to(self.repo).as_posix(),
                    self.output_path.relative_to(self.repo).as_posix(),
                    revision,
                    self.approval(),
                ),
            )
        self.assertEqual(self.output_path.read_bytes(), b"unchanged\n")

    def test_check_capabilities_default_repo_validates_v2_packet(self) -> None:
        _, _, ref = self.seal()
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "check_capabilities.py"),
                "--input",
                ref.path,
                "--json",
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["input_packet"]["ok"])
        self.assertTrue(payload["approved_spec_seal"]["supported"])
        self.assertEqual(payload["approved_spec_seal"]["missing"], [])

    def test_unsupported_seal_capability_allows_read_only_diagnostics(self) -> None:
        binding = binding_module()
        script = capability_script_module()
        unsupported = binding.SealCapabilities(
            supported=False,
            missing=("dir_fd:open",),
        )
        stdout = StringIO()
        with mock.patch.object(
            script, "probe_seal_capabilities", return_value=unsupported
        ), mock.patch.object(
            sys,
            "argv",
            ["check_capabilities.py", "--repo", str(self.repo), "--json"],
        ), mock.patch("sys.stdout", stdout):
            returncode = script.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["approved_spec_seal"]["supported"])
        self.assertFalse(payload["approved_spec_seal"]["blocking"])
        self.assertEqual(
            payload["approved_spec_seal"]["required_for"],
            ["seal", "state_change"],
        )

    def test_asb_24_contract_surface_has_no_consumer_specific_vocabulary(self) -> None:
        binding_module()
        paths = [
            SKILL_DIR / "scripts/lib/issue_implementation_loop/approved_spec_binding.py",
            SKILL_DIR / "assets/schemas/input-packet.schema.json",
            SKILL_DIR / "assets/templates/input-packet.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
        self.assertIsNone(re.search(r"\bcompanies\b", text))
        self.assertIsNone(re.search(r"\bcto\b", text))

    def test_asb_24_all_current_artifact_surfaces_are_generic(self) -> None:
        expected_families = {
            "input_packet",
            "execution_envelope",
            "event_runtime_human_request",
            "worker_reviewer_packet_report",
            "hardening_registry",
            "resume_metadata",
            "execution_result",
            "delivery_plan",
            "binding_gate_status_capability",
        }
        self.assertEqual(set(ASB24_CURRENT_ARTIFACT_SURFACE), expected_families)
        inventory = {
            path
            for paths in ASB24_CURRENT_ARTIFACT_SURFACE.values()
            for path in paths
        }
        current_assets = {
            path.relative_to(SKILL_DIR).as_posix()
            for directory in ("schemas", "templates")
            for path in (SKILL_DIR / "assets" / directory).iterdir()
            if path.is_file()
        }
        self.assertEqual(current_assets - inventory, set())
        binding_markers = (
            "approved_spec_seal",
            "approved_spec_binding",
            "binding_error",
            "binding_valid",
            "probe_seal_capabilities",
            "select_operation",
            "validate_execution_envelope",
            "validate_input_packet",
            "validate_runtime_epoch",
        )
        public_scripts = SKILL_DIR / "scripts"
        discovered_executables: set[str] = set()
        for path in public_scripts.glob("*.py"):
            if path.name.startswith("_"):
                continue
            source = path.read_text(encoding="utf-8")
            if (
                path.stem.startswith(("build_", "rebuild_", "validate_"))
                or any(marker in source for marker in binding_markers)
            ):
                discovered_executables.add(path.relative_to(SKILL_DIR).as_posix())
        library_root = public_scripts / "lib" / "issue_implementation_loop"
        for path in library_root.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            source = path.read_text(encoding="utf-8")
            if path.parent.name == "validation" or any(
                marker in source for marker in binding_markers
            ):
                discovered_executables.add(path.relative_to(SKILL_DIR).as_posix())
        inventoried_executables = {path for path in inventory if path.endswith(".py")}
        self.assertEqual(discovered_executables, inventoried_executables)
        inventory_paths = [SKILL_DIR / path for path in sorted(inventory)]
        self.assertTrue(all(path.is_file() for path in inventory_paths))
        text = "\n".join(
            path.read_text(encoding="utf-8") for path in inventory_paths
        ).lower()
        self.assertIsNone(re.search(r"\b(?:companies|cto)\b", text))

    def test_asb_25_python_and_cli_identify_return_same_binding(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "identify",
                "--repo-root",
                str(self.repo),
                "--spec-path",
                self.spec_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["spec_revision"], revision.to_dict())

    def test_asb_25_codex_and_hermes_host_envs_return_same_cli_binding_and_error(self) -> None:
        cli = str(SCRIPTS_DIR / "approved_spec_binding.py")
        host_context = tempfile.TemporaryDirectory()
        self.addCleanup(host_context.cleanup)

        def host_env(host: str) -> dict[str, str]:
            env = {
                "LANG": os.environ.get("LANG", "C.UTF-8"),
                "PATH": os.environ.get("PATH", ""),
                "PYTHONHASHSEED": "0",
            }
            host_root = Path(host_context.name) / f"{host}-host"
            host_root.mkdir()
            if host.startswith("codex"):
                env.update(
                    {"CODEX_HOME": str(host_root), "CODEX_SESSION_ID": "codex-session"}
                )
            else:
                env.update(
                    {
                        "HERMES_HOME": str(host_root),
                        "HERMES_SESSION_ID": "hermes-session",
                    }
                )
            return env

        def identify(env: dict[str, str], spec_path: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    sys.executable,
                    cli,
                    "identify",
                    "--repo-root",
                    str(self.repo),
                    "--spec-path",
                    spec_path,
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

        codex_success = identify(host_env("codex"), self.spec_path)
        hermes_success = identify(host_env("hermes"), self.spec_path)
        self.assertEqual(codex_success.returncode, 0, codex_success.stderr)
        self.assertEqual(hermes_success.returncode, 0, hermes_success.stderr)
        codex_binding = json.loads(codex_success.stdout)
        hermes_binding = json.loads(hermes_success.stdout)
        self.assertEqual(codex_binding, hermes_binding)
        self.assertEqual(set(codex_binding), {"valid", "spec_revision"})

        codex_failure = identify(host_env("codex-failure"), "missing-spec.md")
        hermes_failure = identify(host_env("hermes-failure"), "missing-spec.md")
        self.assertEqual(codex_failure.returncode, 1)
        self.assertEqual(hermes_failure.returncode, 1)
        codex_error = json.loads(codex_failure.stdout)
        hermes_error = json.loads(hermes_failure.stdout)
        self.assertEqual(codex_error["code"], "SPEC_MISSING")
        self.assertEqual(codex_error["code"], hermes_error["code"])
        self.assertNotIn("session", json.dumps(codex_binding).lower())
        self.assertNotIn("session", json.dumps(hermes_binding).lower())


if __name__ == "__main__":
    unittest.main()
