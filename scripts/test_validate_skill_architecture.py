from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.validate_skill_architecture import (
    DEFAULT_POLICY_PATH,
    REQUIRED_FAMILY_ID,
    load_policy,
    validate_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SKILL_ARCHITECTURE = REPO_ROOT / "scripts" / "validate_skill_architecture.py"


def run_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_SKILL_ARCHITECTURE), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def architecture_policy() -> dict[str, object]:
    return deepcopy(load_policy(DEFAULT_POLICY_PATH))


def repository_change_loop_family(policy: dict[str, object] | None = None) -> dict[str, object]:
    policy = architecture_policy() if policy is None else policy
    families = policy["families"]
    assert isinstance(families, dict)
    family = families[REQUIRED_FAMILY_ID]
    assert isinstance(family, dict)
    return family


class SkillArchitecturePolicyTests(unittest.TestCase):
    def test_validator_rejects_planning_authority_value_drift(self) -> None:
        invalid_values = (
            ("integration_owner", "supporting_planning_agent", "main_planning_context"),
            ("supporting_agent_authority", "decision_maker", "advisory_only"),
            ("decision_authority", "supporting_agent", "human"),
            ("model_selection", "repository_policy", "host_runtime"),
            ("model_persistence", "allowed", "forbidden"),
        )

        for field, invalid, expected in invalid_values:
            with self.subTest(field=field):
                policy = architecture_policy()
                family = repository_change_loop_family(policy)
                planning_authority = family["planning_authority"]
                assert isinstance(planning_authority, dict)
                planning_authority[field] = invalid

                self.assertIn(
                    f"planning_authority.{field} must be {expected}",
                    validate_policy(policy),
                )

    def test_validator_rejects_unknown_planning_authority_field(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        planning_authority = family["planning_authority"]
        assert isinstance(planning_authority, dict)
        planning_authority["model_name"] = "host-specific"

        self.assertIn(
            "planning_authority unknown field: model_name",
            validate_policy(policy),
        )

    def test_validator_rejects_missing_planning_authority_field(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        planning_authority = family["planning_authority"]
        assert isinstance(planning_authority, dict)
        del planning_authority["model_persistence"]

        self.assertIn(
            "planning_authority missing field: model_persistence",
            validate_policy(policy),
        )

    def test_validator_rejects_missing_planning_authority_table(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        del family["planning_authority"]

        self.assertIn(
            "repository-change-loop.planning_authority must be a table",
            validate_policy(policy),
        )

    def test_repository_change_loop_defines_planning_authority_policy(self) -> None:
        family = repository_change_loop_family()

        self.assertEqual(
            family["planning_authority"],
            {
                "integration_owner": "main_planning_context",
                "supporting_agent_authority": "advisory_only",
                "decision_authority": "human",
                "model_selection": "host_runtime",
                "model_persistence": "forbidden",
            },
        )

class ImplementationRouteTests(unittest.TestCase):
    def test_policy_validates_without_an_implementation_skill(self) -> None:
        family = repository_change_loop_family()
        self.assertEqual([], family["user_facing_skills"])
        self.assertNotIn("default_implementation_skill", family)
        self.assertNotIn("first_entry_skill", family)
        self.assertEqual([], validate_policy(architecture_policy()))
        self.assertEqual(0, run_validator("--all").returncode)

    def test_validator_still_rejects_a_missing_declared_skill(self) -> None:
        policy = architecture_policy()
        repository_change_loop_family(policy)["user_facing_skills"] = ["missing-skill"]
        self.assertIn(
            "missing user-facing skill directory: skills/missing-skill/SKILL.md",
            validate_policy(policy),
        )


if __name__ == "__main__":
    unittest.main()
