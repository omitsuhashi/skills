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
REPO_ROUTER = REPO_ROOT / "AGENTS.md"
LEGACY_GRILL_SKILL = "-".join(("grill", "to", "pr", "loop"))
LEGACY_ISSUE_SKILL = "-".join(("issue", "implementation", "loop"))


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

class SddDefaultImplementationRouteTests(unittest.TestCase):
    def test_legacy_implementation_skill_directories_are_absent(self) -> None:
        self.assertFalse((REPO_ROOT / "skills" / LEGACY_GRILL_SKILL).exists())
        self.assertFalse((REPO_ROOT / "skills" / LEGACY_ISSUE_SKILL).exists())

    def test_sdd_is_the_only_user_facing_implementation_skill(self) -> None:
        family = repository_change_loop_family()
        self.assertEqual(["sdd-implementation"], family["user_facing_skills"])
        self.assertEqual("sdd-implementation", family["default_implementation_skill"])

    def test_validator_rejects_user_facing_implementation_skill_drift(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        family["user_facing_skills"] = ["llm-wiki"]

        self.assertIn(
            "repository-change-loop.user_facing_skills must be exactly "
            "['sdd-implementation']",
            validate_policy(policy),
        )

    def test_repository_router_uses_only_sdd_for_the_full_change_lifecycle(self) -> None:
        router = REPO_ROUTER.read_text(encoding="utf-8")
        self.assertIn(
            "For repository changes, use `sdd-implementation` by default.",
            router,
        )
        self.assertIn(
            "Superpowers lifecycle, `grill-with-docs`, and `llm-wiki`",
            router,
        )
        self.assertNotIn(f"Use `{LEGACY_GRILL_SKILL}`", router)
        self.assertNotIn(f"`{LEGACY_ISSUE_SKILL}`", router)

    def test_repository_change_family_describes_requirements_to_completion(self) -> None:
        family = repository_change_loop_family()
        self.assertEqual(
            "Repository change workflow skills that move work from requirements "
            "through specification, planning, and local implementation.",
            family["description"],
        )

    def test_validator_rejects_default_implementation_skill_drift(self) -> None:
        policy = architecture_policy()
        family = repository_change_loop_family(policy)
        family["default_implementation_skill"] = LEGACY_ISSUE_SKILL

        self.assertIn(
            "repository-change-loop.default_implementation_skill must be "
            "sdd-implementation",
            validate_policy(policy),
        )


if __name__ == "__main__":
    unittest.main()
