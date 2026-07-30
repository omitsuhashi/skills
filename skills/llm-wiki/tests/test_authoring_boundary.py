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
SEMANTIC_SCHEMA_KEYS = (
    "page_type",
    "purpose",
    "required_fields",
    "optional_fields",
    "relation_kinds",
    "lifecycle_state",
    "discoverability_metadata",
    "provenance_requirement",
    "index_log_effect",
)
KNOWLEDGE_MIGRATION_FILES = (
    REPO_ROOT / "knowledge/AGENTS.md",
    REPO_ROOT / "knowledge/index.md",
    REPO_ROOT / "knowledge/log.md",
    REPO_ROOT / "knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md",
    REPO_ROOT / "knowledge/wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md",
    REPO_ROOT / "knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md",
)
INVENTORY_ASSETS = (
    (
        "knowledge-root-local-contract",
        TEMPLATE_ASSETS[0],
        (
            "root-registry policy",
            "index purpose",
            "log purpose",
            "Authoring Profile",
            "Compatibility Requirement",
            "immutable-source destination",
            "supported lifecycle operations",
            "profile selection",
        ),
    ),
    (
        "repository-router",
        TEMPLATE_ASSETS[1],
        (
            "repository identity",
            "thin-router boundary",
            "durable planning or decision outputs",
            "blocked-write conditions",
            "supported lifecycle operations",
            "repository governance",
        ),
    ),
    (
        "root-registry",
        TEMPLATE_ASSETS[2],
        (
            "registry identity",
            "Root URI or Path identity",
            "Authoring Profile",
            "predecessor root",
            "lifecycle states",
            "adapter or governance authority",
            "affected-root log events",
        ),
    ),
    (
        "discovery-index",
        TEMPLATE_ASSETS[3],
        (
            "representative reader-task shortcuts",
            "page types",
            "lifecycle inclusion rule",
            "canonical title",
            "primary search terms",
            "active canonical page target",
            "change-log event",
        ),
    ),
    (
        "change-log",
        TEMPLATE_ASSETS[4],
        (
            "affected index identity",
            "canonicalization action",
            "proposal",
            "decision or action",
            "decision authority",
            "append-only active history",
            "deleting or rewriting prior history",
        ),
    ),
    (
        "source-summary",
        TEMPLATE_ASSETS[5],
        (
            "maintained knowledge",
            "source limitations",
            "confidence",
            "immutable-source identity",
            "competing source",
            "primary search terms",
        ),
    ),
    (
        "entity",
        TEMPLATE_ASSETS[6],
        (
            "identity boundary",
            "entity kind",
            "related entity",
            "disputed interpretation",
            "primary search terms",
            "maintain one active canonical index record",
        ),
    ),
    (
        "concept",
        TEMPLATE_ASSETS[7],
        (
            "working definition",
            "scope exclusions",
            "confidence",
            "related concept",
            "contradiction",
            "one-line summary",
        ),
    ),
    (
        "synthesis",
        TEMPLATE_ASSETS[8],
        (
            "non-goal",
            "acceptance",
            "implementation progress ledger",
            "decision authority",
            "artifact kind",
            "operating guidance",
        ),
    ),
    (
        "query-note",
        TEMPLATE_ASSETS[9],
        (
            "originating question",
            "follow-up disposition",
            "candidate page updates",
            "answer kind",
            "disputed claim",
            "canonical index record",
        ),
    ),
    (
        "draft-note",
        TEMPLATE_ASSETS[10],
        (
            "reason direct update was unavailable",
            "requested owner action",
            "current status",
            "never active-canonical discovery while unverified",
            "decision log event",
            "promoted or merged canonical targets",
        ),
    ),
    (
        "implementation-progress-ledger",
        TEMPLATE_ASSETS[11],
        (
            "slice id",
            "landed scope",
            "remaining scope",
            "next trigger",
            "review condition",
            "implemented-unverified",
            "unblock",
            "ledger lifecycle update",
        ),
    ),
)
LEGACY_BASELINE_FIELDS = {
    "entity": (
        "kind",
        "created",
        "updated",
        "source_files",
        "title",
        "summary",
        "key facts",
        "timeline",
        "related pages",
        "open questions",
        "sources",
    ),
    "concept": (
        "kind",
        "created",
        "updated",
        "source_files",
        "title",
        "working definition",
        "importance",
        "supporting claims",
        "tensions and counterevidence",
        "related pages",
        "sources",
    ),
    "query-note": (
        "kind",
        "created",
        "updated",
        "source_files",
        "title",
        "originating question",
        "durable answer",
        "decision material",
        "related pages",
        "follow-up disposition",
        "sources",
    ),
    "source-summary": (
        "kind",
        "created",
        "updated",
        "source_files",
        "title",
        "source position",
        "key claims",
        "related pages",
        "open questions",
        "sources",
    ),
    "synthesis": (
        "kind",
        "created",
        "updated",
        "source_files",
        "title",
        "decision",
        "supporting claims",
        "decision material",
        "operating guidance",
        "tensions and counterevidence",
        "related pages",
        "sources",
    ),
}
LEGACY_FIELD_MAPPINGS = {
    "entity": (
        ("kind", "page_type"),
        ("created", "creation identity"),
        ("updated", "last-update identity"),
        ("source_files", "provenance"),
        ("title", "title"),
        ("summary", "summary"),
        ("key facts", "key facts"),
        ("timeline", "timeline"),
        ("related pages", "relation_kinds"),
        ("open questions", "open questions"),
        ("sources", "provenance"),
    ),
    "concept": (
        ("kind", "page_type"),
        ("created", "creation identity"),
        ("updated", "last-update identity"),
        ("source_files", "provenance"),
        ("title", "title"),
        ("working definition", "working definition"),
        ("importance", "importance"),
        ("supporting claims", "supporting claims"),
        ("tensions and counterevidence", "tensions"),
        ("related pages", "relation_kinds"),
        ("sources", "provenance"),
    ),
    "query-note": (
        ("kind", "page_type"),
        ("created", "creation identity"),
        ("updated", "last-update identity"),
        ("source_files", "provenance"),
        ("title", "title"),
        ("originating question", "originating question"),
        ("durable answer", "durable answer"),
        ("decision material", "decision material"),
        ("related pages", "relation_kinds"),
        ("follow-up disposition", "follow-up disposition"),
        ("sources", "provenance"),
    ),
    "source-summary": (
        ("kind", "page_type"),
        ("created", "creation identity"),
        ("updated", "last-update identity"),
        ("source_files", "source identity"),
        ("title", "title"),
        ("source position", "source position"),
        ("key claims", "key claims"),
        ("related pages", "relation_kinds"),
        ("open questions", "open questions"),
        ("sources", "provenance"),
    ),
    "synthesis": (
        ("kind", "page_type"),
        ("created", "creation identity"),
        ("updated", "last-update identity"),
        ("source_files", "provenance"),
        ("title", "title"),
        ("decision", "decision"),
        ("supporting claims", "provenance"),
        ("decision material", "implications"),
        ("operating guidance", "operating guidance"),
        ("tensions and counterevidence", "risks"),
        ("related pages", "relation_kinds"),
        ("sources", "provenance"),
    ),
}
AFFECTED_LEGACY_ASSETS = {
    "entity": SKILL_DIR / "assets/templates/entity.md",
    "concept": SKILL_DIR / "assets/templates/concept.md",
    "query-note": SKILL_DIR / "assets/templates/query-note.md",
    "source-summary": SKILL_DIR / "assets/templates/source-summary.md",
    "synthesis": SKILL_DIR / "assets/templates/synthesis.md",
}


def read(name: str) -> str:
    return (SKILL_DIR / name).read_text(encoding="utf-8")


def read_repo(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


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
    def test_local_contract_selects_obsidian_without_copying_authoring_syntax(self) -> None:
        contract = read_repo("knowledge/AGENTS.md")

        self.assertIn("authoring profile: obsidian", contract)
        self.assertIn("Obsidian compatibility requirement", contract)
        self.assertNotIn("relative Markdown link", contract)
        self.assertNotIn("[[...]]", contract)
        self.assertIn("adapter-resolved cross-root target identity", contract)
        self.assertIn("selected authoring skill", contract)
        self.assertNotIn("root-id:path/inside/root.md", contract)
        self.assertNotIn("root を跨ぐ参照は Markdown link にせず", contract)

    def test_migrated_knowledge_uses_wikilinks_and_preserves_external_urls(self) -> None:
        for path in KNOWLEDGE_MIGRATION_FILES:
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"\[[^]]+\]\((?:\.\.?/)?wiki/")
        self.assertIn(
            "[Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)",
            read_repo(
                "knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md"
            ),
        )

    def test_historical_specs_are_preserved_and_explicitly_superseded(self) -> None:
        current_spec = "[[llm-wiki-authoring-responsibility-separation-spec]]"
        old_goal_spec = read_repo(
            "knowledge/wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md"
        )
        sro4_spec = read_repo("knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md")

        self.assertIn("# LLM Wiki Draft Review And Canonicalize Goal Spec", old_goal_spec)
        self.assertIn("draft-review", old_goal_spec)
        self.assertIn(current_spec, old_goal_spec)
        self.assertIn("superseded", old_goal_spec)
        self.assertIn("# Skill Repository Optimization V4 Spec", sro4_spec)
        self.assertIn("PR #19", sro4_spec)
        self.assertIn(current_spec, sro4_spec)
        self.assertIn("superseded", sro4_spec)

    def test_sro4_uses_qualified_maintained_source_links_and_preserves_raw_citation(self) -> None:
        sro4_spec = read_repo("knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md")
        maintained_source = (
            "[[wiki/sources/2026-06-26-skill-repository-optimization-v4-design|"
            "Skill Repository Optimization V4 Design]]"
        )
        raw_citation = (
            "[raw/sources/2026-06-26-skill-repository-optimization-v4-design.md]"
            "(../../raw/sources/2026-06-26-skill-repository-optimization-v4-design.md)"
        )

        self.assertEqual(sro4_spec.count(maintained_source), 2)
        self.assertNotIn("[[2026-06-26-skill-repository-optimization-v4-design|", sro4_spec)
        self.assertIn(raw_citation, sro4_spec)

    def test_migration_log_is_append_only_and_discoverable(self) -> None:
        log = read_repo("knowledge/log.md")

        self.assertEqual(
            log.count("implementation | llm-wiki authoring responsibility separation"),
            1,
        )
        self.assertIn("[[llm-wiki-authoring-responsibility-separation-spec]]", log)
        self.assertIn(
            "[[llm-wiki-authoring-responsibility-separation-implementation-plan]]",
            log,
        )

    def test_boundary_uses_no_semantic_schema_serialization_parser(self) -> None:
        for forbidden_global in ("re", "semantic_schema_fields", "inventory_entry"):
            self.assertNotIn(forbidden_global, globals())

    def test_public_contract_declares_portable_handoff_and_fail_closed_boundary(self) -> None:
        skill = read("SKILL.md")

        for heading in ("## Inputs", "## Outputs", "## Required Capabilities"):
            self.assertIn(heading, skill)
        self.assertIn("existing skill discovery", skill)
        self.assertIn("`BLOCKED`", skill)
        self.assertNotIn("fallback renderer", skill.casefold())

    def test_public_contract_reports_completion_and_recovery_state(self) -> None:
        skill = read("SKILL.md")

        for required_output in (
            "authored or changed document identity",
            "required index/log sync set",
            "completion state",
            "operation success",
            "`BLOCKED`",
            "exact changed-file set",
            "failed check",
        ):
            self.assertIn(required_output, skill)
        self.assertIn(
            "apply durable file edits only within resolved authority",
            skill,
        )

    def test_context_operations_keep_only_structural_four_file_read_sets(self) -> None:
        operation = report_operation("single-root.ingest")

        self.assertEqual(len(operation["files"]), 4)
        self.assertNotIn("obsidian-markdown", "\n".join(operation["files"]))

    def test_single_root_declares_read_access_for_canonical_and_proposal_writes(self) -> None:
        single_root = read("references/single-root.md")

        self.assertIn("- `Read`: `allowed`, `restricted`, or `no-access`.", single_root)
        self.assertIn("Direct canonical update requires `Read: allowed`", single_root)
        self.assertIn("Proposal routing requires `Read: allowed`", single_root)

    def test_every_semantic_template_is_syntax_neutral(self) -> None:
        for asset in TEMPLATE_ASSETS:
            text = asset.read_text(encoding="utf-8")
            self.assertIn("semantic fields", text.casefold())
            for forbidden in ("YAML frontmatter", "relative Markdown link", "wikilink", "callout", "embed"):
                self.assertNotIn(forbidden.casefold(), text.casefold())

    def test_inventory_and_assets_share_one_complete_semantic_contract(self) -> None:
        inventory = read("references/page-authoring.md").casefold()
        self.assertIn("authoritative semantic contract", inventory)

        for page_identity, asset, semantic_tokens in INVENTORY_ASSETS:
            asset_text = asset.read_text(encoding="utf-8").casefold()
            for key in SEMANTIC_SCHEMA_KEYS:
                self.assertIn(key.casefold(), inventory, page_identity)
                self.assertIn(key.casefold(), asset_text, str(asset))
            for token in (page_identity, *semantic_tokens):
                self.assertIn(token.casefold(), inventory, page_identity)
                self.assertIn(token.casefold(), asset_text, str(asset))

    def test_every_legacy_semantic_field_maps_to_exactly_one_current_identity(self) -> None:
        inventory = read("references/page-authoring.md").casefold()

        self.assertEqual(
            set(LEGACY_BASELINE_FIELDS),
            set(LEGACY_FIELD_MAPPINGS),
        )
        for page_identity, baseline_fields in LEGACY_BASELINE_FIELDS.items():
            mappings = LEGACY_FIELD_MAPPINGS[page_identity]
            mapped_legacy_fields = tuple(legacy for legacy, _current in mappings)
            self.assertCountEqual(mapped_legacy_fields, baseline_fields, page_identity)
            self.assertEqual(len(mapped_legacy_fields), len(set(mapped_legacy_fields)))

            asset = AFFECTED_LEGACY_ASSETS[page_identity]
            asset_text = asset.read_text(encoding="utf-8").casefold()
            for legacy_field, current_identity in mappings:
                self.assertTrue(current_identity, legacy_field)
                self.assertIn(current_identity.casefold(), inventory, legacy_field)
                self.assertIn(current_identity.casefold(), asset_text, legacy_field)

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
