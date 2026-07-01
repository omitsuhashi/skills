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
        self.assertIn("coordinator or human decision", text)

    def test_review_packet_is_paths_first_committed_range_with_budget(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "paths-first",
            "`BASE_SHA` / `HEAD_SHA`",
            "committed range review",
            "Current PR delivery risk",
            "default 600 words",
            "hard 900 words",
            "Do not paste full spec",
            "Do not paste full ledger",
        ):
            self.assertIn(required, text)

    def test_review_packet_excludes_future_only_hardening_by_default(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "Automatic review checks",
            "Issue intent fit",
            "Implementation regression",
            "Current PR delivery risk",
            "Non-automatic handling",
            "classification_needed is not an automatic review viewpoint",
            "Hardening is not an automatic review viewpoint",
            "Future-only hardening suggestions are out of review scope by default",
            "Do not ask the reviewer to enumerate general hardening ideas",
            "explicitly requested by the human",
            "do not auto-fix",
        ):
            self.assertIn(required, text)

        self.assertNotIn("Hardening candidate lane", text)
        self.assertNotIn("optional lane", text)
        self.assertNotIn("Review approved issue, spec, acceptance, non-goals, write scope, and verification evidence. Classify gaps as `intent_gap`, `implementation_regression`, or `classification_needed`.", text)

    def test_requesting_code_review_is_primary_reviewer_contract(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        self.assertIn("superpowers:requesting-code-review", text)
        self.assertIn("first candidate", text)
        self.assertIn("approved equivalent/manual fallback", text)
