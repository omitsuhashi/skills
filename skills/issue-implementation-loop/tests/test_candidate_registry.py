from __future__ import annotations

from _helpers import *


class CandidateRegistryTests(unittest.TestCase):
    def test_candidate_registry_schema_and_template_define_bounded_artifact(self) -> None:
        schema_path = SKILL_DIR / "assets" / "schemas" / "hardening-candidates.schema.json"
        template_path = SKILL_DIR / "assets" / "templates" / "hardening-candidates.json"

        self.assertTrue(schema_path.exists(), schema_path)
        self.assertTrue(template_path.exists(), template_path)

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        template = json.loads(template_path.read_text(encoding="utf-8"))

        self.assertEqual(
            template["registry_path"],
            "<runtime-root>/decisions/hardening-candidates.json",
        )
        self.assertEqual(template["limits"]["hardening_candidate_summary_words_default"], 80)
        self.assertEqual(template["limits"]["hardening_candidates_per_issue_default"], 5)

        root_required = set(schema["required"])
        self.assertGreaterEqual(
            root_required,
            {"schema_version", "epic_id", "registry_path", "limits", "candidates"},
        )

        candidate_schema = schema["properties"]["candidates"]["items"]
        self.assertGreaterEqual(
            set(candidate_schema["required"]),
            {
                "candidate_id",
                "source_issue",
                "classification",
                "summary",
                "risk",
                "estimated_scope",
                "decision",
                "implementation_issue",
            },
        )
        self.assertEqual(
            candidate_schema["properties"]["classification"]["enum"],
            ["hardening_candidate", "safety_escalation", "classification_needed"],
        )
        self.assertEqual(
            candidate_schema["properties"]["decision"]["enum"],
            [
                "pending_decision",
                "approved_for_current_pr",
                "deferred_follow_up",
                "declined",
                "risk_accepted",
                "implemented",
            ],
        )

        fixture_candidate = template["candidates"][0]
        for field in candidate_schema["required"]:
            self.assertIn(field, fixture_candidate)
        self.assertLessEqual(len(re.findall(r"\S+", fixture_candidate["summary"])), 80)
        self.assertFalse(
            (SKILL_DIR / "decisions" / "hardening-candidates.json").exists(),
            "worker branch must not track a runtime candidate registry artifact",
        )

    def test_references_define_candidate_registry_carry_forward_and_wait_scope(self) -> None:
        runtime_text = (SKILL_DIR / "references" / "runtime-state.md").read_text(
            encoding="utf-8"
        )
        human_wait_text = (SKILL_DIR / "references" / "human-wait.md").read_text(
            encoding="utf-8"
        )
        compaction_text = (SKILL_DIR / "references" / "context-compaction.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "<runtime-root>/decisions/hardening-candidates.json",
            "coordinator-owned",
            "candidate_id",
            "source_issue",
            "classification",
            "summary",
            "risk",
            "estimated_scope",
            "decision",
            "implementation_issue",
            "80 words",
            "5 件",
            "worker branch",
        ):
            self.assertIn(required, runtime_text)

        for required in (
            "safety_escalation",
            "classification_needed",
            "human_request_opened",
            "smallest affected scope",
            "issue",
            "descendants",
            "resource",
        ):
            self.assertIn(required, human_wait_text)

        for required in (
            "Pending hardening decisions: N",
            "<runtime-root>/decisions/hardening-candidates.json",
            "candidate full text",
            "path",
        ):
            self.assertIn(required, compaction_text)
