from __future__ import annotations

from _helpers import *


class DeliveryTests(unittest.TestCase):
    def test_remote_delivery_docs_define_final_pr_auto_create_contract(self) -> None:
        text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(encoding="utf-8")
        envelope_text = (SKILL_DIR / "references" / "execution-envelope.md").read_text(encoding="utf-8")
        template = json.loads((SKILL_DIR / "assets" / "templates" / "delivery-plan.json").read_text(encoding="utf-8"))

        for required in (
            "final_pr_push_head",
            "final_pr_create_draft",
            "delivery plan validation",
            "hardening-candidates.json",
            "pending_decision",
            "safety_escalation",
            "approved_for_current_pr",
            "pending_hardening_candidates",
            "ok: true",
            "draft",
            "ledger",
            "runtime state",
            "completion report",
        ):
            self.assertIn(required, text)
        for required in (
            "ready-for-review",
            "final PR merge",
            "force push",
            "human action",
        ):
            self.assertIn(required, text)
        self.assertIn("final_pr_push_head", envelope_text)
        self.assertIn("final_pr_create_draft", envelope_text)
        self.assertIs(template["draft"], True)

    def test_validate_delivery_plan_rejects_final_pr_from_issue_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/G2PR-003-c",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.head must be codex/issue-implementation-loop/epic-base", result.stderr)
            self.assertIn("issue branch", result.stderr)

    def test_validate_delivery_plan_requires_issue_pr_merges_before_final_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, merged_runtime_state(missing_merge="G2PR-003"))
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("issues.G2PR-003.pr_merged must be true before final PR", result.stderr)

    def test_validate_delivery_plan_json_allows_draft_final_pr_with_pending_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_hardening_registry(
                registry_path,
                [hardening_candidate("HC-G2PR-001-001", decision="pending_decision")],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["errors"], [])
            self.assertEqual(
                [candidate["candidate_id"] for candidate in payload["pending_hardening_candidates"]],
                ["HC-G2PR-001-001"],
            )
            self.assertIn("ready-for-review", payload["decision_gate_blockers"][0])
            self.assertIn("pending_decision", payload["decision_gate_blockers"][0])

    def test_validate_delivery_plan_reports_approved_candidate_until_implementation_issue_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            runtime = merged_runtime_state()
            runtime["issues"]["G2PR-004"] = {
                "status": "IMPLEMENTED",
                "review": {"status": "pending"},
            }
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_hardening_registry(
                registry_path,
                [
                    hardening_candidate(
                        "HC-G2PR-001-002",
                        decision="approved_for_current_pr",
                        implementation_issue="G2PR-004",
                    )
                ],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["errors"], [])
            self.assertIn("approved_for_current_pr", payload["decision_gate_blockers"][0])
            self.assertIn("G2PR-004", payload["decision_gate_blockers"][0])

    def test_validate_delivery_plan_reports_safety_escalation_declined_or_deferred(self) -> None:
        for decision in ("declined", "deferred_follow_up"):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as tmp:
                envelope_path = Path(tmp) / "envelope.json"
                runtime_path = Path(tmp) / "runtime-state.json"
                plan_path = Path(tmp) / "delivery-plan.json"
                registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
                envelope = batch_issue_prs_envelope()
                envelope["remote_write_policy"]["approved_actions"] = [
                    "final_pr_push_head",
                    "final_pr_create_draft",
                ]
                write_json(envelope_path, envelope)
                write_json(runtime_path, merged_runtime_state())
                write_hardening_registry(
                    registry_path,
                    [
                        hardening_candidate(
                            f"HC-G2PR-001-{decision}",
                            classification="safety_escalation",
                            decision=decision,
                        )
                    ],
                )
                write_json(
                    plan_path,
                    {
                        "action": "final_pr",
                        "head": "codex/issue-implementation-loop/epic-base",
                        "base": "main",
                        "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                    },
                )

                result = run_script(
                    "validate_delivery_plan.py",
                    str(envelope_path),
                    str(runtime_path),
                    str(plan_path),
                    "--json",
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["errors"], [])
                self.assertIn("unresolved safety_escalation", payload["decision_gate_blockers"][0])
                self.assertEqual(
                    [candidate["decision"] for candidate in payload["pending_hardening_candidates"]],
                    [decision],
                )

    def test_validate_delivery_plan_allows_resolved_candidates_and_reports_residual_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_hardening_registry(
                registry_path,
                [
                    hardening_candidate("HC-G2PR-001-003", decision="deferred_follow_up"),
                    hardening_candidate("HC-G2PR-001-004", decision="declined"),
                    hardening_candidate(
                        "HC-G2PR-001-005",
                        classification="safety_escalation",
                        decision="risk_accepted",
                    ),
                ],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["pending_hardening_candidates"], [])
            self.assertEqual(
                [risk["candidate_id"] for risk in payload["residual_risks"]],
                ["HC-G2PR-001-003", "HC-G2PR-001-004", "HC-G2PR-001-005"],
            )

    def test_validate_delivery_plan_requires_approved_final_pr_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote_write_policy.approved_actions must include final_pr_push_head", result.stderr)
            self.assertIn("remote_write_policy.approved_actions must include final_pr_create_draft", result.stderr)

    def test_validate_delivery_plan_rejects_ready_final_pr_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "draft": False,
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.draft must be true; ready-for-review is a separate human action", result.stderr)

    def test_validate_delivery_plan_rejects_runtime_state_from_different_epic_or_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            runtime = merged_runtime_state()
            runtime["epic_id"] = "other-epic"
            runtime["envelope_revision"] = 99
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, runtime)
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("runtime_state.epic_id must match envelope.epic_id", result.stderr)
            self.assertIn("runtime_state.envelope_revision must match envelope.revision", result.stderr)

    def test_validate_delivery_plan_requires_active_epic_base_for_final_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for branch_state in ("reserved", "create_on_run", "missing"):
                envelope_path = Path(tmp) / f"{branch_state}-envelope.json"
                runtime_path = Path(tmp) / f"{branch_state}-runtime.json"
                plan_path = Path(tmp) / f"{branch_state}-delivery-plan.json"
                envelope = batch_issue_prs_envelope()
                envelope["epic_base"]["branch_state"] = branch_state
                write_json(envelope_path, envelope)
                write_json(runtime_path, merged_runtime_state())
                write_json(
                    plan_path,
                    {
                        "action": "final_pr",
                        "head": "codex/issue-implementation-loop/epic-base",
                        "base": "main",
                        "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                    },
                )

                result = run_script(
                    "validate_delivery_plan.py",
                    str(envelope_path),
                    str(runtime_path),
                    str(plan_path),
                )

                self.assertNotEqual(result.returncode, 0, branch_state)
                self.assertIn("epic_base.branch_state must be active before final PR", result.stderr)

    def test_validate_delivery_plan_rejects_issue_pr_when_envelope_branch_is_not_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["work_items"]["G2PR-001"]["branch"] = "feature/issue-implementation-loop/G2PR-001-a"
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "issue_pr",
                    "issue": "G2PR-001",
                    "head": "feature/issue-implementation-loop/G2PR-001-a",
                    "base": "codex/issue-implementation-loop/epic-base",
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("work_items.G2PR-001.branch must match codex/issue-implementation-loop/G2PR-001-<slug>", result.stderr)

    def test_validate_delivery_plan_accepts_final_pr_from_epic_base_after_issue_pr_merges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DELIVERY PLAN OK", result.stdout)

    def test_validate_delivery_plan_defaults_final_pr_scope_to_all_work_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state(missing_merge="G2PR-003"))
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                },
            )

            result = run_script(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("issues.G2PR-003.pr_merged must be true before final PR", result.stderr)
