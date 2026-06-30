from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "knowledge/wiki/syntheses/loop-skill-autonomous-gates-issues.md"
INDEX = REPO_ROOT / "knowledge/index.md"
LOG = REPO_ROOT / "knowledge/log.md"
GRILL_TESTS = REPO_ROOT / "skills/grill-to-pr-loop/tests/test_grill_to_pr_loop.py"
TASK_GITHUB_TESTS = REPO_ROOT / "plugins/task-management/tests/test_github_mcp_route.py"
TASK_DISPATCH_TESTS = REPO_ROOT / "plugins/task-management/tests/test_adapter_dispatch.py"
DELIVERY_TESTS = REPO_ROOT / "skills/issue-implementation-loop/tests/test_delivery.py"


class LoopAutonomousGatesLedgerTests(unittest.TestCase):
    def test_regression_tests_pin_all_autonomous_gate_contracts(self) -> None:
        grill_text = GRILL_TESTS.read_text(encoding="utf-8")
        github_text = TASK_GITHUB_TESTS.read_text(encoding="utf-8")
        dispatch_text = TASK_DISPATCH_TESTS.read_text(encoding="utf-8")
        delivery_text = DELIVERY_TESTS.read_text(encoding="utf-8")

        for required in (
            "test_gate_taxonomy_separates_human_preflight_and_remote_boundaries",
            "test_execution_plan_gate_auto_continue_keeps_evidence_and_stop_conditions",
        ):
            self.assertIn(required, grill_text)

        self.assertIn(
            "test_live_root_and_adapter_availability_are_readiness_not_write_approval",
            github_text,
        )
        self.assertIn("test_readiness_failures_are_setup_blockers", github_text)
        self.assertIn("test_dispatch_approval_is_separate_from_readiness_gate", dispatch_text)
        self.assertIn(
            "test_validate_delivery_plan_requires_approved_final_pr_actions",
            delivery_text,
        )
        self.assertIn("test_validate_delivery_plan_rejects_ready_final_pr_creation", delivery_text)

    def test_final_ledger_aggregates_lsag001_through_lsag006_evidence(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")

        for issue_id in ("LSAG-001", "LSAG-002", "LSAG-003", "LSAG-004", "LSAG-005", "LSAG-006"):
            self.assertIn(f"| loop-skill-autonomous-gates | {issue_id} |", text)

        self.assertIn("| loop-skill-autonomous-gates | LSAG-005 | regression tests と wiki discoverability を追加する | 承認済み | 完了 |", text)
        self.assertIn("| loop-skill-autonomous-gates | LSAG-006 | integration base に LSAG-002/003/004 を集約する | 承認済み | 完了 |", text)

        for required in (
            "## 最終実装証跡",
            "LSAG-001: `17e743e44cd0617da896618dbff10d0ece39fcc4`",
            "LSAG-002: `9a7fee240b283b65906ad8ff17239905b4c20d8c`",
            "LSAG-003: `be8f906d814ef2dff7c6ca5bec6cdb6517f37c07`",
            "LSAG-004: `5a9e77ed608fd46f1e7901aad12686cf4eb83333`",
            "LSAG-005: `0d179d188c126a8ea9112a43aecc0d62e5ec9b71`",
            "LSAG-006: `6bcf0ed93a8199e04094c33e0ae8a76bdfe7e7d9`",
            "レビュー結果: LSAG-001 から LSAG-004 と LSAG-006 は review cycle 1 approved",
            "LSAG-005 は初回 review で Important 1 件を修正し、review-fix 後の re-review approved",
            "GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push は実行していない",
        ):
            self.assertIn(required, text)

        lsag005 = text.split("## LSAG-005", 1)[1]
        for required in (
            "- [x] gate taxonomy、Execution Plan Gate auto-continue、Live Root / Adapter Availability readiness semantics、final PR auto-create approved action が tests で固定されている。",
            "- [x] `knowledge/index.md` が仕様と issue ledger を discoverable にしている。",
            "- [x] `knowledge/log.md` が Issue Gate、Execution Plan Gate、実装完了、delivery state を追える。",
            "- [x] final ledger に LSAG-001 から LSAG-006 の implementation evidence、review result、verification result が集約される。",
        ):
            self.assertIn(required, lsag005)

    def test_completed_issue_sections_do_not_retain_stale_review_wait_wording(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")

        self.assertNotIn("実装済み / coordinator review 待ち", text)
        self.assertNotIn("coordinator review 後に判断する", text)

        for issue_id in ("LSAG-001", "LSAG-002", "LSAG-003", "LSAG-004", "LSAG-006"):
            section = text.split(f"## {issue_id}", 1)[1].split("\n## ", 1)[0]
            self.assertIn("- 実行状態: 完了", section)
            self.assertIn("review cycle 1 approved", section)

        lsag005 = text.split("## LSAG-005", 1)[1].split("\n## ", 1)[0]
        self.assertIn("- 実行状態: 完了", lsag005)
        self.assertIn("review-fix 後の re-review approved", lsag005)

    def test_index_and_log_expose_spec_ledger_packet_and_delivery_state(self) -> None:
        index_text = INDEX.read_text(encoding="utf-8")
        log_text = LOG.read_text(encoding="utf-8")

        for required in (
            "[Loop Skill 自動継続 Gate 仕様](wiki/syntheses/loop-skill-autonomous-gates-spec.md)",
            "[Loop Skill 自動継続 Gate Issue 台帳](wiki/syntheses/loop-skill-autonomous-gates-issues.md)",
            "[Loop Skill 自動継続 Gate Input Packet](wiki/syntheses/loop-skill-autonomous-gates-input-packet.json)",
            "最終台帳",
            "LSAG-001 から LSAG-006",
            "delivery evidence",
        ):
            self.assertIn(required, index_text)

        for required in (
            "[2026-06-30] decision | Loop skill autonomous gates Issue Gate approved",
            "[2026-06-30] auto-continue | Loop skill autonomous gates Execution Plan Gate packet",
            "[2026-06-30] implementation | Loop skill autonomous gates LSAG-005 regression ledger",
            "LSAG-005 は regression tests、wiki discoverability、最終台帳集約だけを実装 scope とした",
            "delivery state は local-only evidence として、GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push を未実行に保った",
        ):
            self.assertIn(required, log_text)


if __name__ == "__main__":
    unittest.main()
