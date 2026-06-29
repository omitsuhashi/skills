import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
REFERENCE = REPO_ROOT / "plugins/task-management/skills/task-management/references/task-draft-contract.md"
EXAMPLE = REPO_ROOT / "plugins/task-management/examples/task-create-preview.example.md"


class WorkUnitPreviewContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference_text = REFERENCE.read_text(encoding="utf-8")
        cls.example_text = EXAMPLE.read_text(encoding="utf-8")

    def test_reference_separates_stable_id_from_backend_display_label(self):
        text = self.reference_text

        self.assertIn("`work_unit_id` is the stable routing key", text)
        self.assertIn("must not be derived from or overwritten by `work_unit_name`", text)
        self.assertIn("`work_unit_name` is the backend display label", text)
        self.assertIn("not a routing key", text)

    def test_reference_documents_unknown_work_unit_name_review_behavior(self):
        text = self.reference_text

        self.assertIn('`work_unit_name: "Unknown work unit: <work_unit_id>"`', text)
        self.assertIn("A missing display label is a human-review issue, not a routing change.", text)
        self.assertIn("confirm the backend display label before adapter dispatch", text)

    def test_preview_example_displays_id_name_and_unknown_name_fallback(self):
        text = self.example_text

        self.assertIn("- Work unit id: `portfolio-os-task-backend-plugin-skill`", text)
        self.assertIn("- Work unit name: `Portfolio OS Task Backend Plugin Skill`", text)
        self.assertIn("- Routing key: `work_unit_id`", text)
        self.assertIn("- Backend display label: `work_unit_name`", text)
        self.assertIn('work_unit_name: "Unknown work unit: portfolio-os-task-backend-plugin-skill"', text)
        self.assertIn("Human review must confirm the backend display label before adapter dispatch.", text)


if __name__ == "__main__":
    unittest.main()
