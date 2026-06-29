import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = REPO_ROOT / "plugins/task-management/skills/task-management/SKILL.md"
REFERENCE = REPO_ROOT / "plugins/task-management/skills/task-management/references/task-draft-contract.md"
EXAMPLE = REPO_ROOT / "plugins/task-management/examples/task-create-preview.example.md"


class TaskDraftContractExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.reference_text = REFERENCE.read_text(encoding="utf-8")
        cls.example_text = EXAMPLE.read_text(encoding="utf-8")

    def test_skill_entrypoint_references_task_draft_contract(self):
        self.assertIn("references/task-draft-contract.md", self.skill_text)

    def test_reference_defines_composition_rules_and_taxonomy(self):
        text = self.reference_text

        self.assertIn("# TaskDraft Composition Contract", text)
        self.assertIn("## Title Rules", text)
        self.assertIn("## Body Rules", text)
        self.assertIn("## Taxonomy Guidance", text)

        for task_type in (
            "implementation",
            "review",
            "research",
            "decision",
            "coordination",
            "maintenance",
            "inbox_triage",
        ):
            self.assertRegex(text, rf"`{task_type}`")

    def test_preview_example_displays_both_work_unit_fields(self):
        text = self.example_text

        self.assertIn('work_unit_id: "portfolio-os-task-backend-plugin-skill"', text)
        self.assertIn('work_unit_name: "Portfolio OS Task Backend Plugin Skill"', text)
        self.assertIn("Work unit id: `portfolio-os-task-backend-plugin-skill`", text)
        self.assertIn("Work unit name: `Portfolio OS Task Backend Plugin Skill`", text)

    def test_inbox_fallback_is_explicit_in_reference_and_example(self):
        reference = self.reference_text
        example = self.example_text

        self.assertIn("## Inbox Fallback", reference)
        self.assertIn("needs human routing during review", reference)
        self.assertIn('work_unit_id: "inbox"', example)
        self.assertIn('work_unit_name: "Inbox"', example)
        self.assertIn("Human review should replace inbox", example)

    def test_contract_excludes_raw_platform_storage(self):
        reference = self.reference_text

        for required_phrase in (
            "raw platform payloads",
            "platform message ids",
            "transport metadata",
            "credentials, tokens, cookies, or MCP server configuration",
        ):
            self.assertIn(required_phrase, reference)

        self.assertRegex(reference, r"`TaskDraft` must not store:")

    def test_example_uses_sanitized_source_ref_instead_of_raw_payload_shape(self):
        text = self.example_text

        self.assertIn('source_ref: "source-trail:portfolio-os-task-backend-plugin-skill/POTASK-003"', text)
        self.assertIn('source_ref: "source-summary:unrouted-task-management-note"', text)

        raw_payload_markers = (
            r"\bmessage_id\s*:",
            r"\bchannel_id\s*:",
            r"\bevent_id\s*:",
            r"\bwebhook_headers\s*:",
            r"\bauthorization\s*:",
            r"\btoken\s*:",
        )
        for marker in raw_payload_markers:
            self.assertIsNone(re.search(marker, text, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
