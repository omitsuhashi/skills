from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_skill_architecture import DEFAULT_POLICY_PATH, REQUIRED_FAMILY_ID, load_policy


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SKILL_ARCHITECTURE = REPO_ROOT / "scripts" / "validate_skill_architecture.py"


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_SKILL_ARCHITECTURE), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def repository_change_loop_family() -> dict[str, object]:
    policy = load_policy(DEFAULT_POLICY_PATH)
    families = policy["families"]
    assert isinstance(families, dict)
    family = families[REQUIRED_FAMILY_ID]
    assert isinstance(family, dict)
    return family


class SkillArchitecturePolicyTests(unittest.TestCase):
    def test_repository_change_loop_defines_context_compaction_policy(self) -> None:
        family = repository_change_loop_family()

        self.assertEqual(
            family["context_compaction"],
            {
                "soft_trigger_percent": 65,
                "hard_stop_percent": 75,
                "mandatory_handoff_compaction": 1,
            },
        )

    def test_validator_rejects_context_compaction_policy_drift(self) -> None:
        policy_text = DEFAULT_POLICY_PATH.read_text(encoding="utf-8")
        policy_text = policy_text.replace("hard_stop_percent = 75", "hard_stop_percent = 76")

        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "skill-architecture.toml"
            policy_path.write_text(policy_text, encoding="utf-8")
            result = run_validator("--all", "--policy", str(policy_path), "--json")

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("context_compaction.hard_stop_percent must be exactly 75", payload["errors"])

    def test_context_compaction_is_not_a_standalone_skill(self) -> None:
        self.assertFalse((REPO_ROOT / "skills" / "context-compaction" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
