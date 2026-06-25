from __future__ import annotations

from _helpers import *


class DeliveryTests(unittest.TestCase):
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

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DELIVERY PLAN OK", result.stdout)

    def test_validate_delivery_plan_defaults_final_pr_scope_to_all_work_items(self) -> None:
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
