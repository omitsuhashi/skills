from __future__ import annotations

from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
COMMON_SCRIPT = SCRIPTS_DIR / "_common.py"
LIB_DIR = SCRIPTS_DIR / "lib" / "issue_implementation_loop"
TESTS_DIR = SKILL_DIR / "tests"


class CommonLibSplitTests(unittest.TestCase):
    def test_common_helpers_live_in_domain_modules(self) -> None:
        expected_modules = [
            "__init__.py",
            "constants.py",
            "io.py",
            "identifiers.py",
            "review.py",
            "graph.py",
            "scheduler.py",
            "delivery.py",
            "git_state.py",
            "skill_discovery.py",
            "validation/__init__.py",
            "validation/input_packet.py",
            "validation/execution_envelope.py",
            "validation/runtime_state.py",
            "validation/worker_report.py",
            "validation/delivery_plan.py",
        ]

        for module in expected_modules:
            self.assertTrue((LIB_DIR / module).exists(), module)

    def test_common_py_is_import_facade_not_implementation_home(self) -> None:
        source = COMMON_SCRIPT.read_text(encoding="utf-8")
        moved_functions = [
            "validate_input_packet",
            "validate_execution_envelope",
            "validate_runtime_state",
            "validate_worker_report",
            "validate_delivery_plan",
            "dependency_cycle",
            "compute_next_actions",
            "git_output",
            "skill_roots",
            "find_skill",
        ]

        for function_name in moved_functions:
            self.assertIsNone(
                re.search(rf"^def {function_name}\(", source, re.MULTILINE),
                function_name,
            )

    def test_tests_are_split_by_behavior_domain(self) -> None:
        expected_tests = [
            "test_entrypoint.py",
            "test_skill_discovery.py",
            "test_validation.py",
            "test_runtime_state.py",
            "test_delivery.py",
            "test_scheduler.py",
            "test_git_reconcile.py",
        ]

        for test_file in expected_tests:
            self.assertTrue((TESTS_DIR / test_file).exists(), test_file)
        self.assertFalse((TESTS_DIR / "test_issue_implementation_loop.py").exists())
