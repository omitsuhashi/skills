from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
REPORT_CONTEXT = REPO_ROOT / "scripts" / "report_skill_context.py"
TEMPLATE_ASSETS = (
    SKILL_DIR / "assets/templates/AGENTS.md",
    SKILL_DIR / "assets/templates/root-AGENTS.md",
    SKILL_DIR / "assets/templates/root-registry.md",
    SKILL_DIR / "assets/templates/index.md",
    SKILL_DIR / "assets/templates/log.md",
    SKILL_DIR / "assets/templates/source-summary.md",
    SKILL_DIR / "assets/templates/entity.md",
    SKILL_DIR / "assets/templates/concept.md",
    SKILL_DIR / "assets/templates/synthesis.md",
    SKILL_DIR / "assets/templates/query-note.md",
    SKILL_DIR / "assets/templates/draft-note.md",
    SKILL_DIR / "assets/templates/implementation-progress-ledger.md",
)
MODE_REFERENCES = (
    SKILL_DIR / "references/modes/bootstrap.md",
    SKILL_DIR / "references/modes/ingest.md",
    SKILL_DIR / "references/modes/query.md",
    SKILL_DIR / "references/modes/draft-review.md",
    SKILL_DIR / "references/modes/canonicalize.md",
    SKILL_DIR / "references/modes/lint.md",
)


def read(name: str) -> str:
    return (SKILL_DIR / name).read_text(encoding="utf-8")


def report_operation(name: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(REPORT_CONTEXT), "--skill", "skills/llm-wiki", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    payload = json.loads(result.stdout)
    return next(
        operation
        for operation in payload["skills"][0]["operations"]
        if operation["operation"] == name
    )


class AuthoringBoundaryTests(unittest.TestCase):
    def test_public_contract_declares_portable_handoff_and_fail_closed_boundary(self) -> None:
        skill = read("SKILL.md")

        for heading in ("## Inputs", "## Outputs", "## Required Capabilities"):
            self.assertIn(heading, skill)
        self.assertIn("existing skill discovery", skill)
        self.assertIn("`BLOCKED`", skill)
        self.assertNotIn("fallback renderer", skill.casefold())

    def test_context_operations_keep_only_structural_four_file_read_sets(self) -> None:
        operation = report_operation("single-root.ingest")

        self.assertEqual(len(operation["files"]), 4)
        self.assertNotIn("obsidian-markdown", "\n".join(operation["files"]))

    def test_single_root_declares_read_access_for_canonical_and_proposal_writes(self) -> None:
        single_root = read("references/single-root.md")

        self.assertIn("- `Read`: `allowed`, `restricted`, or `no-access`.", single_root)
        self.assertIn("Direct canonical update requires `Read: allowed`", single_root)
        self.assertIn("Proposal routing requires `Read: allowed`", single_root)

    def test_every_semantic_template_declares_the_complete_schema_without_serialization_fields(self) -> None:
        for asset in TEMPLATE_ASSETS:
            text = asset.read_text(encoding="utf-8")
            self.assertIn("semantic fields", text.casefold())
            for forbidden in ("YAML frontmatter", "relative Markdown link", "wikilink", "callout", "embed"):
                self.assertNotIn(forbidden.casefold(), text.casefold())

    def test_modes_delegate_authoring_without_reading_concrete_templates(self) -> None:
        for mode in MODE_REFERENCES:
            text = mode.read_text(encoding="utf-8")
            self.assertIn("selected authoring skill", text)
            self.assertIn("semantic schema", text)
            self.assertNotIn("assets/templates/", text)

    def test_optional_tooling_defers_to_the_selected_authoring_skill(self) -> None:
        optional_tooling = read("references/optional-tooling.md")

        self.assertIn("llm-wiki selects no authoring tool", optional_tooling)
        self.assertIn(
            "selected authoring skill documentation controls optional authoring tooling",
            optional_tooling,
        )
        for concrete_tool in ("Obsidian", "Dataview", "Marp", "`qmd`", "Web Clipper"):
            self.assertNotIn(concrete_tool, optional_tooling)


if __name__ == "__main__":
    unittest.main()
