from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from validate_skill_architecture import (
    DEFAULT_POLICY_PATH,
    REQUIRED_FAMILY_ID,
    load_policy,
    validate_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SKILL_ARCHITECTURE = REPO_ROOT / "scripts" / "validate_skill_architecture.py"
REPO_ROUTER = REPO_ROOT / "AGENTS.md"


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


class SddDefaultImplementationRouteTests(unittest.TestCase):
    def test_sdd_is_the_default_implementation_skill(self) -> None:
        family = repository_change_loop_family()
        self.assertEqual(
            ["grill-to-pr-loop", "issue-implementation-loop"],
            family["user_facing_skills"],
        )
        self.assertEqual(
            "sdd-implementation",
            family["default_implementation_skill"],
        )

    def test_repository_router_uses_sdd_for_the_full_change_lifecycle(self) -> None:
        router = REPO_ROUTER.read_text(encoding="utf-8")
        self.assertIn(
            "For repository changes, use `sdd-implementation` by default.",
            router,
        )
        self.assertIn(
            "Superpowers lifecycle, `grill-with-docs`, and `llm-wiki`",
            router,
        )
        self.assertIn(
            "Use `grill-to-pr-loop` or `issue-implementation-loop` only when "
            "the user explicitly names one",
            router,
        )

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
        family["default_implementation_skill"] = "issue-implementation-loop"

        self.assertIn(
            "repository-change-loop.default_implementation_skill must be "
            "sdd-implementation",
            validate_policy(policy),
        )


if __name__ == "__main__":
    unittest.main()
