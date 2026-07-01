from __future__ import annotations

from _helpers import *


REVIEW_GATE = SKILL_DIR / "references" / "review-gate.md"


class ReviewGateTests(unittest.TestCase):
    def test_review_gate_defines_finding_taxonomy_and_fix_loop_rules(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for classification in (
            "`intent_gap`",
            "`implementation_regression`",
            "`hardening_candidate`",
            "`safety_escalation`",
            "`classification_needed`",
        ):
            self.assertIn(classification, text)

        self.assertIn("intent_gap / implementation_regression", text)
        self.assertIn("blocking finding", text)
        self.assertIn("existing fix loop", text)
        self.assertIn("hardening_candidate is not a fix request", text)
        self.assertIn("classification_needed stops the issue", text)
        self.assertIn("coordinator or human classification decision", text)

    def test_review_packet_is_paths_first_committed_range_with_budget(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "paths-first",
            "`BASE_SHA` / `HEAD_SHA`",
            "committed range review",
            "default 600 words",
            "hard 900 words",
            "Do not paste full spec",
            "Do not paste full ledger",
        ):
            self.assertIn(required, text)

    def test_review_packet_separates_required_intent_lane_from_optional_hardening_lane(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "Issue intent review lane",
            "required lane",
            "Hardening candidate lane",
            "optional lane",
            "source artifacts are already satisfied",
            "do not auto-fix",
        ):
            self.assertIn(required, text)

    def test_requesting_code_review_is_primary_reviewer_contract(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        self.assertIn("superpowers:requesting-code-review", text)
        self.assertIn("first candidate", text)
        self.assertIn("approved equivalent/manual fallback", text)
