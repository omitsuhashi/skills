from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
VALIDATE_CONTEXT = REPO_ROOT / "scripts" / "validate_skill_context.py"
INSPECT_CONTEXT = REPO_ROOT / "scripts" / "inspect_skill_context.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class GrillContextContractTests(unittest.TestCase):
    def test_context_contract_v2_loads_core_without_workflow_router(self) -> None:
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(encoding="utf-8")

        self.assertIn("schema_version = 2", contract_text)
        self.assertIn(
            'base_references = ["references/core.md"]',
            contract_text,
        )
        self.assertNotIn("references/workflow-contract.md", contract_text)
        self.assertIn("max_file_count = 6", contract_text)
        self.assertFalse((SKILL_DIR / "references" / "workflow-contract.md").exists())

    def test_all_skill_context_contracts_validate(self) -> None:
        result = run_script(VALIDATE_CONTEXT, "--all")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: validated 3", result.stdout)

    def test_inspector_returns_execution_plan_read_set(self) -> None:
        result = run_script(
            INSPECT_CONTEXT,
            "--skill",
            "skills/grill-to-pr-loop",
            "--operation",
            "execution-plan",
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skill"], "grill-to-pr-loop")
        self.assertEqual(payload["operation"], "execution-plan")
        self.assertEqual(
            payload["files"],
            [
                "skills/grill-to-pr-loop/SKILL.md",
                "skills/grill-to-pr-loop/references/core.md",
                "skills/grill-to-pr-loop/references/planning-contract.md",
                "skills/grill-to-pr-loop/references/local-issue-ledger.md",
                "skills/grill-to-pr-loop/references/execution-handoff.md",
            ],
        )
        self.assertEqual(payload["schema_version"], 2)
        self.assertGreater(payload["word_count"], 0)
        self.assertGreaterEqual(payload["headroom_percent"], 0)

    def test_execution_handoff_requires_compressed_or_fresh_context_guard(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(encoding="utf-8")
        combined = f"{skill_text}\n{handoff_text}"

        self.assertRegex(combined, r"context.*圧縮")
        self.assertIn("fresh execution coordinator", combined)
        self.assertIn("handoff brief", handoff_text)
        self.assertIn("normalized packet", handoff_text)

    def test_context_compaction_trigger_is_discoverable_from_entrypoint(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        reference_text = (SKILL_DIR / "references" / "context-compaction.md").read_text(encoding="utf-8")

        self.assertIn("65%", skill_text)
        self.assertIn("references/context-compaction.md", skill_text)
        self.assertIn("conditional overlay", skill_text)
        self.assertIn("忘れてはいけないこと", reference_text)
        self.assertIn("忘れてもいいこと", reference_text)
        self.assertIn("圧縮してはいけないこと", reference_text)
        self.assertIn("Phase Transition Context GC", reference_text)
        self.assertIn("Phase 別圧縮 matrix", reference_text)

    def test_context_compaction_is_conditional_overlay_not_default_read_set(self) -> None:
        execution_plan = run_script(
            INSPECT_CONTEXT,
            "--skill",
            "skills/grill-to-pr-loop",
            "--operation",
            "execution-plan",
            "--json",
        )
        overlay = run_script(
            INSPECT_CONTEXT,
            "--skill",
            "skills/grill-to-pr-loop",
            "--operation",
            "context-compaction",
            "--json",
        )

        self.assertEqual(execution_plan.returncode, 0, execution_plan.stderr)
        self.assertEqual(overlay.returncode, 0, overlay.stderr)
        execution_payload = json.loads(execution_plan.stdout)
        overlay_payload = json.loads(overlay.stdout)

        self.assertNotIn(
            "skills/grill-to-pr-loop/references/context-compaction.md",
            execution_payload["files"],
        )
        self.assertEqual(
            execution_payload["files"],
            [
                "skills/grill-to-pr-loop/SKILL.md",
                "skills/grill-to-pr-loop/references/core.md",
                "skills/grill-to-pr-loop/references/planning-contract.md",
                "skills/grill-to-pr-loop/references/local-issue-ledger.md",
                "skills/grill-to-pr-loop/references/execution-handoff.md",
            ],
        )
        self.assertEqual(
            overlay_payload["files"],
            [
                "skills/grill-to-pr-loop/SKILL.md",
                "skills/grill-to-pr-loop/references/core.md",
                "skills/grill-to-pr-loop/references/context-compaction.md",
            ],
        )

        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("keep the current operation read-set loaded", skill_text)


if __name__ == "__main__":
    unittest.main()
