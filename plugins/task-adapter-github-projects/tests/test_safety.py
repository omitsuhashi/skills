import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.safety import (  # noqa: E402
    SafetyValidationError,
    validate_adapter_arguments,
    validate_host_attestation,
)


SAFE_ATTESTATION = {
    "projects_toolset_enabled": True,
    "issue_write_enabled": True,
    "comment_write_enabled": True,
    "raw_mcp_exposure": "adapter_only",
    "adapter_write_exposure": "task_management_only",
}


class AdapterSafetyTests(unittest.TestCase):
    def assert_rejected(self, value, expected_code):
        with self.assertRaises(SafetyValidationError) as raised:
            validate_adapter_arguments(value)
        self.assertEqual(expected_code, raised.exception.code)

    def test_rejects_credentials_at_any_depth(self):
        cases = [
            {"token": "not-a-real-token"},
            {"nested": {"authorization": "redacted"}},
            {"note": "Authorization: redacted"},
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assert_rejected(value, "unsafe_data")

    def test_rejects_caller_supplied_tool_selection(self):
        cases = [
            {"tool_name": "mcp__github__projects_write"},
            {"nested": {"mcp_tool": "mcp__github__projects_get"}},
            {"selection": "mcp__github__issue_write"},
        ]
        for value in cases:
            with self.subTest(value=value):
                self.assert_rejected(value, "caller_tool_selection")

    def test_rejects_arbitrary_dispatch_fields(self):
        for key in ("dispatch", "dispatcher", "dispatch_tool"):
            with self.subTest(key=key):
                self.assert_rejected({key: "anything"}, "arbitrary_dispatch")

    def test_host_attestation_is_exact_and_fail_closed(self):
        self.assertEqual(SAFE_ATTESTATION, validate_host_attestation(SAFE_ATTESTATION))

        unsafe_cases = [
            {**SAFE_ATTESTATION, "raw_mcp_exposure": "model_visible"},
            {**SAFE_ATTESTATION, "adapter_write_exposure": "child_agents"},
            {**SAFE_ATTESTATION, "projects_toolset_enabled": False},
            {**SAFE_ATTESTATION, "extra": True},
        ]
        for attestation in unsafe_cases:
            with self.subTest(attestation=attestation):
                with self.assertRaises(SafetyValidationError) as raised:
                    validate_host_attestation(attestation)
                self.assertEqual("unsafe_delegation_exposure", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
