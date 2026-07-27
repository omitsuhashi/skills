from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


TEST_PATH = Path(__file__).resolve()
REPO_ROOT = TEST_PATH.parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_skill_architecture import load_policy


FORBIDDEN_MODEL_FIELDS = {
    "model",
    "model_name",
    "model_reasoning_effort",
    "reasoning_level",
    "intelligence_level",
}
APPROVED_PLANNING_AUTHORITY = {
    "integration_owner": "main_planning_context",
    "supporting_agent_authority": "advisory_only",
    "decision_authority": "human",
    "model_selection": "host_runtime",
    "model_persistence": "forbidden",
}
RUNTIME_BOUNDARY_SENTENCE = (
    "A user-selected model change or host model unavailability is host runtime "
    "state, not spec or packet drift."
)
ISSUE_LOOP_DIR = REPO_ROOT / "skills" / "issue-implementation-loop"
EXECUTION_SCHEMA_PATH = (
    ISSUE_LOOP_DIR / "assets" / "schemas" / "execution-envelope.schema.json"
)
EXECUTION_TEMPLATE_PATH = (
    ISSUE_LOOP_DIR / "assets" / "templates" / "execution-envelope.json"
)
MODEL_CLOSED_SCHEMA_PATHS = (
    ISSUE_LOOP_DIR / "assets" / "schemas" / "input-packet.schema.json",
    EXECUTION_SCHEMA_PATH,
    ISSUE_LOOP_DIR / "assets" / "schemas" / "worker-packet.schema.json",
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


class PlanningAuthorityPolicyTests(unittest.TestCase):
    def assert_planning_authority_contract(
        self, planning_authority: dict[str, object]
    ) -> None:
        self.assertEqual(planning_authority, APPROVED_PLANNING_AUTHORITY)
        self.assertTrue(
            FORBIDDEN_MODEL_FIELDS.isdisjoint(planning_authority),
            msg="planning authority must not persist concrete model routing",
        )

    def assert_closed_schema_rejects_model_fields(
        self, schema: dict[str, object]
    ) -> None:
        self.assertIs(schema["additionalProperties"], False)
        properties = schema["properties"]
        self.assertIsInstance(properties, dict)
        self.assertTrue(
            FORBIDDEN_MODEL_FIELDS.isdisjoint(properties),
            msg="closed root schema must not expose model routing fields",
        )

    def assert_runtime_boundary(self, planning_contract: str) -> None:
        self.assertIn(RUNTIME_BOUNDARY_SENTENCE, planning_contract)

    def assert_worker_only_phase_policy(
        self,
        execution_schema: dict[str, object],
        execution_template: dict[str, object],
    ) -> None:
        schema_policy = execution_schema["properties"]["phase_branch_policy"][
            "properties"
        ]
        template_policy = execution_template["phase_branch_policy"]
        expected = {
            "execution_coordinator_context": "fresh_or_compacted",
            "main_planning_session_may_implement": False,
            "issue_branch_owner": "worker",
        }
        for field, value in expected.items():
            self.assertEqual(schema_policy[field]["const"], value)
            self.assertEqual(template_policy[field], value)

    def test_planning_authority_delegates_model_selection_to_host_runtime(self) -> None:
        policy = load_policy(REPO_ROOT / "skill-architecture.toml")
        planning_authority = policy["families"]["repository-change-loop"][
            "planning_authority"
        ]

        self.assert_planning_authority_contract(planning_authority)

    def test_closed_execution_schemas_reject_model_routing_fields(self) -> None:
        for schema_path in MODEL_CLOSED_SCHEMA_PATHS:
            with self.subTest(schema=schema_path.name):
                self.assert_closed_schema_rejects_model_fields(
                    load_json(schema_path)
                )

    def test_model_runtime_change_is_not_spec_or_packet_drift(self) -> None:
        planning_contract = (
            REPO_ROOT
            / "skills"
            / "grill-to-pr-loop"
            / "references"
            / "planning-contract.md"
        ).read_text(encoding="utf-8")

        self.assert_runtime_boundary(planning_contract)

    def test_existing_worker_only_phase_policy_is_unchanged(self) -> None:
        self.assert_worker_only_phase_policy(
            load_json(EXECUTION_SCHEMA_PATH),
            load_json(EXECUTION_TEMPLATE_PATH),
        )
