from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "knowledge/wiki/syntheses/loop-review-governance-issues.md"
SPEC = REPO_ROOT / "knowledge/wiki/syntheses/loop-review-governance-spec.md"
INPUT_PACKET = REPO_ROOT / "knowledge/wiki/syntheses/loop-review-governance-input-packet.json"
EXECUTION_ENVELOPE = REPO_ROOT / "knowledge/wiki/syntheses/loop-review-governance-execution-envelope.json"
HANDOFF_BRIEF = REPO_ROOT / "knowledge/wiki/syntheses/loop-review-governance-handoff-brief.md"
INDEX = REPO_ROOT / "knowledge/index.md"
LOG = REPO_ROOT / "knowledge/log.md"


class LoopReviewGovernanceLedgerTests(unittest.TestCase):
    def test_regression_contract_keeps_intent_gap_and_hardening_candidate_separate(self) -> None:
        spec_text = SPEC.read_text(encoding="utf-8")
        ledger_text = LEDGER.read_text(encoding="utf-8")

        for required in (
            "`intent_gap`",
            "`implementation_regression`",
            "`hardening_candidate`",
            "`safety_escalation`",
            "`classification_needed`",
            "Issue completion の blocker ではなく、final PR 前の人間判断 queue",
        ):
            self.assertIn(required, spec_text)

        lrg005 = ledger_text.split("## LRG-005", 1)[1]
        for required in (
            "- [x] `intent_gap` と `hardening_candidate` を混同しない regression がある。",
            "- [x] `hardening_candidate` が auto-fix されず final PR 前 decision queue に送られる regression がある。",
            "- [x] 未判断 candidate は draft final PR 作成を止めず、ready-for-review / merge 前の一括判断 gate に出る regression がある。",
            "- [x] `superpowers:requesting-code-review` 第一候補と fallback boundary の contract が test または docs regression で固定されている。",
        ):
            self.assertIn(required, lrg005)

    def test_ledger_aggregates_lrg001_through_lrg005_evidence_and_pending_decisions(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")

        for issue_id in ("LRG-001", "LRG-002", "LRG-003", "LRG-004", "LRG-005"):
            self.assertIn(f"| loop-review-governance | {issue_id} |", text)

        for required in (
            "## 実装証跡サマリ",
            "LRG-001: `b7a5b989bb856ec0703f490361f7d9898ac521f4..461cea6cb48b4a44b40148e2523a5cd17a386f86`",
            "LRG-002: `461cea6cb48b4a44b40148e2523a5cd17a386f86..1ee5eb11b6fa23a1e33f82649ec38438dd5b6404`",
            "LRG-003: `1ee5eb11b6fa23a1e33f82649ec38438dd5b6404..2a02704943d6d9dc86a130074cafa85c80c06a1f`",
            "LRG-004: `461cea6cb48b4a44b40148e2523a5cd17a386f86..3a85970d9829526bd34e7747f862f2a6d6b27ce7`",
            "LRG-005:",
            "HC-LRG-002-001",
            "HC-LRG-003-001",
            "HC-LRG-003-002",
            "HC-LRG-004-001",
            "`pending_decision`",
            "draft PR 作成を止めない",
        ):
            self.assertIn(required, text)

    def test_index_and_log_expose_execution_artifacts_and_gate_evidence(self) -> None:
        index_text = INDEX.read_text(encoding="utf-8")
        log_text = LOG.read_text(encoding="utf-8")

        for artifact in (
            "[Loop Review Governance Spec](wiki/syntheses/loop-review-governance-spec.md)",
            "[Loop Review Governance Issue 台帳](wiki/syntheses/loop-review-governance-issues.md)",
            "[Loop Review Governance Input Packet](wiki/syntheses/loop-review-governance-input-packet.json)",
            "[Loop Review Governance Execution Envelope](wiki/syntheses/loop-review-governance-execution-envelope.json)",
            "[Loop Review Governance Handoff Brief](wiki/syntheses/loop-review-governance-handoff-brief.md)",
        ):
            self.assertIn(artifact, index_text)

        for required in (
            "[2026-07-01] gate | Loop review governance Issue Gate approval",
            "[2026-07-01] gate | Loop review governance Execution Plan Gate approval",
            "[2026-07-01] implementation | Loop review governance LRG-005 regression discoverability",
            "[2026-07-01] review-fix | Loop review governance draft PR decision surface",
            "pending_decision` は draft PR 作成ではなく",
            "HC-LRG-002-001、HC-LRG-003-001、HC-LRG-003-002、HC-LRG-004-001 は pending_decision",
        ):
            self.assertIn(required, log_text)

    def test_execution_envelope_and_handoff_brief_are_discoverable_artifacts(self) -> None:
        envelope_text = EXECUTION_ENVELOPE.read_text(encoding="utf-8")
        handoff_text = HANDOFF_BRIEF.read_text(encoding="utf-8")
        packet_text = INPUT_PACKET.read_text(encoding="utf-8")

        for required in (
            '"epic_id": "loop-review-governance"',
            '"remote_write_policy"',
            '"mode": "local_only"',
            '"primary": "requesting-code-review"',
            '"hardening_candidates"',
            '"ready_or_merge_requires_decisions": true',
        ):
            self.assertIn(required, envelope_text)

        for required in (
            "Execution Plan Gate",
            "`hardening_candidate` は自動修正せず、final PR 前に人間判断へ送る",
            "Runtime root:",
        ):
            self.assertIn(required, handoff_text)

        self.assertIn('"draft_pr_allows_pending_decisions": true', packet_text)
        self.assertIn('"ready_or_merge_requires_decisions": true', packet_text)


if __name__ == "__main__":
    unittest.main()
