from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
VALIDATE_CONTEXT = REPO_ROOT / "scripts" / "validate_skill_context.py"
REPORT_CONTEXT = REPO_ROOT / "scripts" / "report_skill_context.py"

TOPOLOGIES = ("single-root", "multi-root")
MODES = ("bootstrap", "ingest", "query", "draft-review", "canonicalize", "lint")


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_llm_wiki_fixture(root: Path, contract_text: str) -> Path:
    skill_dir = root / "llm-wiki"
    modes_dir = skill_dir / "references" / "modes"
    modes_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# LLM Wiki\n\nUse contract routing.\n", encoding="utf-8")
    (skill_dir / "references" / "core.md").write_text("core reference\n", encoding="utf-8")
    (skill_dir / "references" / "single-root.md").write_text("single root\n", encoding="utf-8")
    (skill_dir / "references" / "multi-root.md").write_text("multi root\n", encoding="utf-8")
    for mode in MODES:
        (modes_dir / f"{mode}.md").write_text(f"{mode} mode\n", encoding="utf-8")
    (skill_dir / "context-contract.toml").write_text(contract_text, encoding="utf-8")
    return skill_dir


class LlmWikiContextContractTests(unittest.TestCase):
    def test_contract_validates_and_reports_topology_mode_read_set(self) -> None:
        validate_result = run_script(VALIDATE_CONTEXT, "--skill", "skills/llm-wiki")
        report_result = run_script(REPORT_CONTEXT, "--skill", "skills/llm-wiki", "--json")

        self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
        self.assertEqual(report_result.returncode, 0, report_result.stderr)
        payload = json.loads(report_result.stdout)
        operation = next(
            operation
            for operation in payload["skills"][0]["operations"]
            if operation["operation"] == "single-root.ingest"
        )
        self.assertEqual(operation["skill"], "llm-wiki")
        self.assertEqual(operation["topology"], "single-root")
        self.assertEqual(operation["mode"], "ingest")
        self.assertEqual(
            operation["files"],
            [
                "skills/llm-wiki/SKILL.md",
                "skills/llm-wiki/references/core.md",
                "skills/llm-wiki/references/single-root.md",
                "skills/llm-wiki/references/modes/ingest.md",
            ],
        )

    def test_report_includes_every_llm_wiki_topology_mode_pair(self) -> None:
        result = run_script(REPORT_CONTEXT, "--all", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        llm_wiki = next(skill for skill in payload["skills"] if skill["skill"] == "llm-wiki")
        observed = {(operation["topology"], operation["mode"]) for operation in llm_wiki["operations"]}
        expected = {(topology, mode) for topology in TOPOLOGIES for mode in MODES}
        self.assertEqual(observed, expected)
        self.assertEqual(llm_wiki["operation_count"], len(expected))
        self.assertEqual(payload["growth_warning_threshold_percent"], 10)
        self.assertIn("warnings", payload)

    def test_validator_rejects_missing_topology_mode_operation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_llm_wiki_fixture(
                Path(tmp),
                "\n".join(
                    [
                        "schema_version = 2",
                        'skill = "llm-wiki"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        'topologies = ["single-root", "multi-root"]',
                        'modes = ["ingest"]',
                        "character_budget = 1000",
                        "estimated_token_budget = 500",
                        "max_file_count = 4",
                        "min_headroom_percent = 10",
                        "",
                        '[operations."single-root.ingest"]',
                        'topology = "single-root"',
                        'mode = "ingest"',
                        'references = ["references/single-root.md", "references/modes/ingest.md"]',
                    ]
                ),
            )

            result = run_script(VALIDATE_CONTEXT, "--skill", str(skill_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing topology/mode operation: multi-root.ingest", result.stderr)

    def test_validator_rejects_wrong_topology_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_llm_wiki_fixture(
                Path(tmp),
                "\n".join(
                    [
                        "schema_version = 2",
                        'skill = "llm-wiki"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        'topologies = ["single-root"]',
                        'modes = ["ingest"]',
                        "character_budget = 1000",
                        "estimated_token_budget = 500",
                        "max_file_count = 4",
                        "min_headroom_percent = 10",
                        "",
                        '[operations."single-root.ingest"]',
                        'topology = "single-root"',
                        'mode = "ingest"',
                        'references = ["references/multi-root.md", "references/modes/ingest.md"]',
                    ]
                ),
            )

            result = run_script(VALIDATE_CONTEXT, "--skill", str(skill_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "operation single-root.ingest missing topology reference: references/single-root.md",
                result.stderr,
            )

    def test_skill_md_delegates_read_sets_to_context_contract(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("context-contract.toml", skill_text)
        self.assertNotIn("## Read Sets", skill_text)


if __name__ == "__main__":
    unittest.main()
