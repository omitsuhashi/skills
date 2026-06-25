from __future__ import annotations

from _helpers import *


class ValidationTests(unittest.TestCase):
    def test_validate_execution_envelope_requires_context_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            del envelope["context_policy"]
            path = Path(tmp) / "missing-context-policy.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context_policy", result.stderr)

    def test_validate_input_packet_rejects_missing_or_invalid_delivery_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing", None, "delivery_intent"),
                ("invalid", "unsafe_final_pr_agent_merge", "delivery_intent"),
            ]
            for name, value, expected in cases:
                packet = base_packet()
                if value is None:
                    del packet["delivery_intent"]
                else:
                    packet["delivery_intent"] = value
                path = Path(tmp) / f"{name}.json"
                write_json(path, packet)

                result = run_script("validate_input_packet.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_input_packet_accepts_batch_issue_prs_delivery_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "packet.json"
            write_json(path, base_packet())

            result = run_script("validate_input_packet.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_rejects_invalid_context_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("paths_first", {"paths_first": False}, "paths_first"),
                ("packet_budget", {"max_worker_packet_words": 0}, "max_worker_packet_words"),
                ("report_budget", {"max_worker_report_words": 0}, "max_worker_report_words"),
                ("full_spec", {"include_full_spec_text": True}, "include_full_spec_text"),
                ("full_ledger", {"include_full_ledger_text": True}, "include_full_ledger_text"),
            ]
            for name, patch, expected in cases:
                envelope = base_envelope()
                envelope["context_policy"].update(patch)
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_accepts_legacy_context_policy_without_worker_packet_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            for field in (
                "worker_packet_schema",
                "worker_packet_template",
                "worker_packet_validator",
            ):
                del envelope["context_policy"][field]
            path = Path(tmp) / "legacy-envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_requires_all_worker_packet_references_when_any_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for field in (
                "worker_packet_schema",
                "worker_packet_template",
                "worker_packet_validator",
            ):
                with self.subTest(field):
                    envelope = base_envelope()
                    envelope["context_policy"].update(
                        {
                            "worker_packet_schema": "assets/schemas/worker-packet.schema.json",
                            "worker_packet_template": "assets/templates/worker-packet.json",
                            "worker_packet_validator": "scripts/validate_worker_packet.py",
                        }
                    )
                    del envelope["context_policy"][field]
                    path = Path(tmp) / f"missing-{field}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0, field)
                    self.assertIn(f"context_policy.{field}", result.stderr)

    def test_execution_envelope_schema_allows_legacy_or_complete_worker_packet_context_references(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        context_schema = schema["properties"]["context_policy"]

        for field in (
            "worker_packet_schema",
            "worker_packet_template",
            "worker_packet_validator",
        ):
            self.assertNotIn(field, context_schema["required"])
            self.assertEqual(
                sorted(context_schema["dependentRequired"][field]),
                [
                    "worker_packet_schema",
                    "worker_packet_template",
                    "worker_packet_validator",
                ],
            )

    def test_loop_skill_v3_execution_envelope_records_worker_packet_context_references(self) -> None:
        envelope_path = (
            SKILL_DIR.parents[1]
            / "knowledge"
            / "wiki"
            / "syntheses"
            / "loop-skill-architecture-v3-execution-envelope.json"
        )
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        context_policy = envelope["context_policy"]

        self.assertEqual(
            context_policy["worker_packet_schema"],
            "skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json",
        )
        self.assertEqual(
            context_policy["worker_packet_template"],
            "skills/issue-implementation-loop/assets/templates/worker-packet.json",
        )
        self.assertEqual(
            context_policy["worker_packet_validator"],
            "skills/issue-implementation-loop/scripts/validate_worker_packet.py",
        )

    def test_validate_execution_envelope_rejects_non_object_remote_write_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["remote_write_policy"] = None
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote_write_policy must be an object", result.stderr)

    def test_validate_execution_envelope_requires_review_cycle_budget_of_two_or_less(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing", None, "review_policy.max_review_cycles"),
                ("too_many", 3, "review_policy.max_review_cycles"),
                ("zero", 0, "review_policy.max_review_cycles"),
            ]
            for name, value, expected in cases:
                envelope = base_envelope()
                if value is None:
                    del envelope["review_policy"]["max_review_cycles"]
                else:
                    envelope["review_policy"]["max_review_cycles"] = value
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_requires_worker_context_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing_worker_required", "worker_context_required", None, "worker_context_required"),
                ("worker_not_required", "worker_context_required", False, "worker_context_required"),
                ("missing_coordinator", "coordinator_may_implement", None, "coordinator_may_implement"),
                ("coordinator_allowed", "coordinator_may_implement", True, "coordinator_may_implement"),
                ("missing_serial_mode", "serial_fallback_mode", None, "serial_fallback_mode"),
                ("coordinator_serial", "serial_fallback_mode", "coordinator_direct", "serial_fallback_mode"),
            ]
            for name, field, value, expected in cases:
                envelope = base_envelope()
                if value is None:
                    del envelope["execution_policy"][field]
                else:
                    envelope["execution_policy"][field] = value
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_execution_envelope_schema_requires_worker_context_boundaries(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        execution_schema = schema["properties"]["execution_policy"]

        self.assertIn("worker_context_required", execution_schema["required"])
        self.assertIn("coordinator_may_implement", execution_schema["required"])
        self.assertIn("serial_fallback_mode", execution_schema["required"])
        self.assertEqual(execution_schema["properties"]["worker_context_required"]["const"], True)
        self.assertEqual(execution_schema["properties"]["coordinator_may_implement"]["const"], False)
        self.assertEqual(
            execution_schema["properties"]["serial_fallback_mode"]["const"],
            "worker_context_only",
        )

    def test_validate_execution_envelope_rejects_invalid_epic_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing_ref", {"sha": BASE_SHA}, "epic_base.ref"),
                ("missing_sha", {"ref": "main"}, "epic_base.sha"),
                ("short_sha", {"ref": "main", "sha": "0123456789abcdef"}, "epic_base.sha"),
            ]
            for name, epic_base, expected in cases:
                envelope = base_envelope()
                envelope["epic_base"] = epic_base
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_accepts_batch_issue_prs_to_epic_base_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_requires_epic_base_branch_state_for_batch_issue_prs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("epic_base.branch_state", result.stderr)

    def test_validate_execution_envelope_rejects_relative_epic_base_worktree_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["epic_base"]["worktree_path"] = "relative/worktree"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("epic_base.worktree_path", result.stderr)

    def test_validate_execution_envelope_rejects_batch_issue_prs_without_epic_base_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("codex/issue-implementation-loop/epic-base", result.stderr)

    def test_validate_execution_envelope_rejects_batch_issue_prs_when_final_pr_merge_is_not_human_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "agent_default_with_human_escalation",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.merge", result.stderr)

    def test_execution_envelope_schema_requires_batch_issue_prs_shape(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        remote_schema = schema["properties"]["remote_write_policy"]
        batch_rule = next(
            rule
            for rule in remote_schema["allOf"]
            if rule["if"]["properties"]["mode"]["const"] == "batch_issue_prs"
        )

        self.assertEqual(batch_rule["then"]["required"], ["issue_prs", "final_pr"])
        self.assertEqual(
            remote_schema["properties"]["issue_prs"]["required"],
            ["base", "merge"],
        )
        self.assertEqual(
            remote_schema["properties"]["final_pr"]["required"],
            ["head", "base", "merge"],
        )

    def test_execution_envelope_schema_defines_epic_base_branch_lifecycle(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        epic_base_schema = schema["properties"]["epic_base"]

        self.assertIn("branch_state", epic_base_schema["properties"])
        self.assertIn("worktree_path", epic_base_schema["properties"])
        self.assertEqual(
            epic_base_schema["properties"]["branch_state"]["enum"],
            ["reserved", "create_on_run", "active", "missing"],
        )

    def test_validate_execution_envelope_rejects_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-001"]["dependencies"] = [
                {
                    "issue": "G2PR-003",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                }
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cycle", result.stderr.lower())

    def test_validate_execution_envelope_rejects_multiple_blocker_heads_without_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {
                "type": "blocker_head",
                "issue": "G2PR-001",
            }
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                },
                {
                    "issue": "G2PR-002",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                },
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple blocker heads", result.stderr.lower())

    def test_validate_execution_envelope_requires_integration_base_policy_for_integration_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {"type": "epic_base"}
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                }
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("integration_head", result.stderr)

    def test_validate_execution_envelope_rejects_multiple_integration_heads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {
                "type": "integration_head",
                "integration_issue": "G2PR-001",
            }
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                },
                {
                    "issue": "G2PR-002",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                },
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple integration heads", result.stderr.lower())

    def test_validate_worker_report_requires_commit_metadata_for_pr_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "worker-report.json"
            write_json(
                report_path,
                {
                    "epic_id": "issue-implementation-loop",
                    "issue_id": "G2PR-001",
                    "branch": "codex/issue-implementation-loop/G2PR-001-a",
                    "worktree": "/tmp/skills/issue-implementation-loop/G2PR-001-a",
                    "changed_files": ["skills/a/SKILL.md"],
                    "verification": [{"command": "python3 -m unittest", "result": "passed"}],
                    "implementation_review": {"status": "approved", "range": REVIEW_RANGE},
                    "status": "PR_READY",
                },
            )

            result = run_script("validate_worker_report.py", str(report_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base_sha", result.stderr)
            self.assertIn("head_sha", result.stderr)

    def test_validate_worker_report_accepts_committed_pr_ready_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "worker-report.json"
            write_json(
                report_path,
                {
                    "epic_id": "issue-implementation-loop",
                    "issue_id": "G2PR-001",
                    "branch": "codex/issue-implementation-loop/G2PR-001-a",
                    "worktree": "/tmp/skills/issue-implementation-loop/G2PR-001-a",
                    "changed_files": ["skills/a/SKILL.md"],
                    "verification": [{"command": "python3 -m unittest", "result": "passed"}],
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "implementation_review": {"status": "approved", "range": REVIEW_RANGE},
                    "status": "PR_READY",
                },
            )

            result = run_script("validate_worker_report.py", str(report_path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_worker_report_rejects_pr_ready_with_unapproved_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "worker-report.json"
            write_json(
                report_path,
                {
                    "epic_id": "issue-implementation-loop",
                    "issue_id": "G2PR-001",
                    "branch": "codex/issue-implementation-loop/G2PR-001-a",
                    "worktree": "/tmp/skills/issue-implementation-loop/G2PR-001-a",
                    "changed_files": ["skills/a/SKILL.md"],
                    "verification": [{"command": "python3 -m unittest", "result": "passed"}],
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "implementation_review": {"status": "changes_requested", "range": REVIEW_RANGE},
                    "status": "PR_READY",
                },
            )

            result = run_script("validate_worker_report.py", str(report_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("implementation_review.status must be approved", result.stderr)
