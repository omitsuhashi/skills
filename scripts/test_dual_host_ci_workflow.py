from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "skill-architecture.yml"
HERMES_MANIFEST_TEST = (
    REPO_ROOT / "plugins" / "task-management" / "tests" / "test_hermes_plugin_manifest.py"
)


class DualHostCiWorkflowTests(unittest.TestCase):
    def test_python_matrix_runs_focused_decision_and_hermes_contracts(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("python-version:\n          - \"3.9\"\n          - \"3.12\"", text)
        self.assertIn("Run decide-in-order tests", text)
        self.assertIn(
            "python3 -m unittest discover -s skills/decide-in-order/tests", text
        )
        self.assertIn("Run task-management decision-support tests", text)
        self.assertIn(
            "python3 plugins/task-management/tests/test_decision_support_policy.py",
            text,
        )
        self.assertIn("Run task-management Hermes registration tests", text)
        self.assertIn(
            "python3 plugins/task-management/tests/test_hermes_plugin_manifest.py",
            text,
        )

    def test_hermes_manifest_contract_has_no_pyyaml_dependency(self):
        text = HERMES_MANIFEST_TEST.read_text(encoding="utf-8")

        self.assertNotIn("import yaml", text)
        self.assertNotIn("yaml.safe_load", text)


if __name__ == "__main__":
    unittest.main()
