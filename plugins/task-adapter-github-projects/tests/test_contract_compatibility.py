import json
import sys
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
LOCAL_FIXTURES = PLUGIN_ROOT / "tests" / "fixtures" / "adapter-v2"
SHARED_FIXTURES = (
    REPO_ROOT / "plugins" / "task-management" / "tests" / "fixtures" / "adapter-v2"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from task_adapter_github_projects.contracts import (  # noqa: E402
    ADAPTER_CONTRACT_VERSION,
    ContractValidationError,
    validate_contract,
)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ContractCompatibilityTests(unittest.TestCase):
    def test_local_fixture_set_is_an_exact_frozen_copy(self):
        shared_paths = sorted(
            path.relative_to(SHARED_FIXTURES)
            for path in SHARED_FIXTURES.rglob("*.json")
        )
        local_paths = sorted(
            path.relative_to(LOCAL_FIXTURES)
            for path in LOCAL_FIXTURES.rglob("*.json")
        )

        self.assertEqual(shared_paths, local_paths)
        for relative_path in shared_paths:
            with self.subTest(path=str(relative_path)):
                self.assertEqual(
                    _load(SHARED_FIXTURES / relative_path),
                    _load(LOCAL_FIXTURES / relative_path),
                )

    def test_accepts_every_normative_adapter_v2_fixture(self):
        manifest = _load(LOCAL_FIXTURES / "manifest.json")
        self.assertEqual(2, ADAPTER_CONTRACT_VERSION)
        self.assertEqual(2, manifest["adapter_contract_version"])

        for case in manifest["accept"]:
            with self.subTest(case=case["name"]):
                payload = _load(LOCAL_FIXTURES / case["path"])
                self.assertEqual(payload, validate_contract(case["contract"], payload))

    def test_rejects_every_normative_adapter_v2_fixture_with_exact_code(self):
        manifest = _load(LOCAL_FIXTURES / "manifest.json")

        for case in manifest["reject"]:
            with self.subTest(case=case["name"]):
                payload = _load(LOCAL_FIXTURES / case["path"])
                with self.assertRaises(ContractValidationError) as raised:
                    validate_contract(case["contract"], payload)
                self.assertEqual(case["error_code"], raised.exception.code)


if __name__ == "__main__":
    unittest.main()
