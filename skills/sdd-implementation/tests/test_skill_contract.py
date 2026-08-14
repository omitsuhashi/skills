from __future__ import annotations

from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"

def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def markdown_section(text: str, heading: str, next_heading: str) -> str:
    if heading not in text:
        return ""
    return text.split(heading, 1)[1].split(next_heading, 1)[0]


class SddImplementationSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.openai_text = read_or_empty(OPENAI_YAML)

    def test_frontmatter_triggers_for_the_full_repository_change_lifecycle(self) -> None:
        frontmatter = self.skill_text.split("---", 2)[1] if "---" in self.skill_text else ""
        self.assertIn("name: sdd-implementation", frontmatter)
        self.assertIn(
            "description: Use when a repository change needs specification, planning, "
            "or local implementation through the Superpowers development lifecycle.",
            frontmatter,
        )

    def test_superpowers_owns_the_ordered_lifecycle(self) -> None:
        brainstorming = self.skill_text.index("superpowers:brainstorming")
        writing_plans = self.skill_text.index("superpowers:writing-plans")
        sdd = self.skill_text.index("superpowers:subagent-driven-development")
        self.assertLess(brainstorming, writing_plans)
        self.assertLess(writing_plans, sdd)
        self.assertIn("Superpowers is the authoritative development methodology.", self.skill_text)
        for forbidden in ("custom scheduler", "worker packet schema", "runtime snapshot"):
            self.assertIn(forbidden, self.skill_text)

    def test_public_contract_is_thin_and_does_not_reimplement_generic_methodology(self) -> None:
        for forbidden_heading in (
            "## Epic Parallel Issue Adapter",
            "## Runtime Model And Effort",
            "## Superpowers-Owned Parallel Safety Outcomes",
        ):
            self.assertNotIn(forbidden_heading, self.skill_text)
        for leaked_algorithm in (
            "descendant advance",
            "non-descendant rewrite",
            "selected cherry-pick",
            "one fixer",
            "exactly one scoped re-review",
            "second fix wave",
            "repeated whole-branch review",
        ):
            with self.subTest(leaked_algorithm=leaked_algorithm):
                self.assertNotIn(leaked_algorithm, self.skill_text)
        normalized = " ".join(self.skill_text.split())
        self.assertIn("Superpowers owns generic worktree allocation", normalized)
        self.assertIn("TDD, worker dispatch, review and repair, and branch finishing", normalized)

    def test_entry_maturity_skips_completed_stages(self) -> None:
        for state in (
            "Change request or incomplete specification",
            "Human-approved current specification",
            "Repository-ready `ready` plan bound to the current specification",
        ):
            self.assertIn(state, self.skill_text)
        self.assertIn("Do not repeat a completed stage.", self.skill_text)

    def test_implementation_entry_requires_current_ready_evidence(self) -> None:
        maturity = self.skill_text.split("## Route By Input Maturity", 1)[1].split("## Spec Stage", 1)[0]
        normalized = " ".join(maturity.split())
        for required in (
            "approved North Star identity",
            "approved Written Spec identity",
            "baseline binding",
            "independent review verdict `ready`",
            "repository validation evidence",
        ):
            self.assertIn(required, normalized)
        for rejected in ("`issues_found`", "stale", "absent"):
            self.assertIn(rejected, normalized)
        self.assertIn("must not enter the Implementation Stage", normalized)

    def test_human_approval_is_limited_to_north_star_and_written_spec(self) -> None:
        self.assertIn("Human North Star and Written Spec authority", self.skill_text)
        lower = self.skill_text.lower()
        self.assertNotIn("repository-approved", lower)
        self.assertNotIn("approved plan", lower)
        for forbidden in (
            "human-approved issue plan",
            "human plan approval",
            "human approval of the plan",
            "human approval for the plan",
        ):
            self.assertNotIn(forbidden, lower)

    def test_plan_stage_routes_reviewed_readiness_without_remote_authorization(self) -> None:
        section = self.skill_text.split("## Plan Stage", 1)[1].split("## Implementation Stage", 1)[0]
        normalized = " ".join(section.split())
        for value in (
            "`references/plan-contract.md`",
            "fresh Plan Author",
            "fresh independent Plan Reviewer",
            "`needs_repair`",
            "`needs_decision`",
            "`blocked`",
            "`ready`",
            "Implementation Stage",
            "remote publication authorization",
        ):
            self.assertIn(value, normalized)

    def test_incomplete_spec_preserves_settled_portions(self) -> None:
        self.assertIn(
            "Preserve approved and complete portions of an incomplete specification.",
            self.skill_text,
        )
        self.assertIn(
            "Use Grill with Docs only for unresolved material decisions.",
            self.skill_text,
        )

    def test_grill_with_docs_is_required_for_spec_authoring_and_refinement(self) -> None:
        self.assertIn("REQUIRED SUB-SKILL: Use grill-with-docs", self.skill_text)
        for trigger in (
            "no Human-approved written specification exists",
            "material ambiguity remains",
            "repository evidence conflicts with the proposed specification",
        ):
            self.assertIn(trigger, self.skill_text)
        self.assertIn("Ask one decision question at a time.", self.skill_text)
        self.assertIn("Do not silently replace Grill with Docs with ad hoc questioning.", self.skill_text)
        self.assertIn("not_needed", self.skill_text)

    def test_llm_wiki_owns_query_and_three_durable_checkpoints(self) -> None:
        self.assertIn("REQUIRED SUB-SKILL: Use llm-wiki", self.skill_text)
        for checkpoint in (
            "Human-approved written specification",
            "Reviewed implementation plan",
            "Implementation closeout",
        ):
            self.assertIn(checkpoint, self.skill_text)
        self.assertIn("knowledge/index.md", self.skill_text)
        self.assertIn("knowledge/log.md", self.skill_text)
        self.assertIn("Do not create parallel `CONTEXT.md` or `docs/adr/` stores.", self.skill_text)
        self.assertIn("not_applicable", self.skill_text)

    def test_public_contract_binds_every_git_probe_to_one_explicit_target(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        normalized = " ".join(section.split())
        for statement in (
            "caller-supplied canonical absolute target",
            "installed skill directory",
            "`git -C <target> rev-parse --show-toplevel`",
            "`git -C <target> rev-parse --is-inside-work-tree`",
            "exactly equals the canonical target",
            "Every probe in all three gates uses that same target binding",
            "Never infer the target from the skill package, process CWD, or ambient checkout",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, normalized)

    def test_public_contract_owns_three_direct_git_gates_once(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        for gate in (
            "exceptional-local-scratch-pre-write",
            "pre-commit-candidate",
            "final-closeout",
        ):
            with self.subTest(gate=gate):
                self.assertEqual(1, section.count(f"| `{gate}` |"))
        self.assertIn("`git check-ignore --no-index`", section)
        self.assertIn("`git write-tree`", section)
        self.assertIn("`git ls-tree`", section)
        self.assertIn("`git cat-file`", section)
        self.assertIn("every commit in `starting_head_sha..HEAD`", section)

    def test_public_scratch_gate_requires_a_new_owned_superpowers_leaf(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        scratch_row = next(
            line
            for line in section.splitlines()
            if line.startswith("| `exceptional-local-scratch-pre-write` |")
        )
        self.assertIn("normalized target-relative `.superpowers/**` leaf", scratch_row)
        self.assertIn("already exists or its ownership is foreign or unknown", scratch_row)
        self.assertNotIn("starting_head_sha", scratch_row)

    def test_public_contract_rejects_repository_specific_or_ambiguous_gate_owners(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        for forbidden in (
            "migration manifest",
            "nominated candidate tree",
            "for every repository validation gate",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, section)

    def test_public_contract_fails_closed_by_failure_owner(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        normalized = " ".join(section.split())
        for classification in (
            "`broken skill installation`",
            "`BLOCKED: target/runtime unavailable`",
            "`FAIL: exceptional-local-scratch-pre-write`",
            "`FAIL: pre-commit-candidate`",
            "`FAIL: final-closeout`",
        ):
            with self.subTest(classification=classification):
                self.assertIn(classification, normalized)
        legacy_package_failure = "/".join(("skill", "package")) + " unavailable"
        self.assertNotIn(legacy_package_failure, normalized)
        self.assertIn(
            "Evidence is single-use: recompute the selected gate from current Git objects and state",
            normalized,
        )

    def test_model_selection_is_owned_upstream_without_a_local_role_table(self) -> None:
        self.assertIn("Follow the current Superpowers SDD Model Selection contract.", self.skill_text)
        self.assertIn("Every worker dispatch states the resolved explicit model.", self.skill_text)
        self.assertIn("A user model override takes precedence.", self.skill_text)
        self.assertNotIn("| Superpowers task class |", self.skill_text)
        self.assertNotIn("| orchestrator |", self.skill_text)
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_required_skill_families_are_preflighted_in_the_active_runtime(self) -> None:
        self.assertIn(
            "Before entering a selected route, use the active runtime's skill discovery "
            "to verify applicable dependencies and required capabilities.",
            self.skill_text,
        )
        for dependency in (
            "Superpowers lifecycle skills",
            "`grill-with-docs`",
            "`llm-wiki`",
        ):
            self.assertIn(dependency, self.skill_text)
        for blocker in (
            "`BLOCKED: missing Superpowers lifecycle dependency`",
            "`BLOCKED: missing grill-with-docs dependency`",
            "`BLOCKED: missing llm-wiki dependency`",
        ):
            self.assertIn(blocker, self.skill_text)

    def test_dependency_preflight_respects_route_conditions(self) -> None:
        self.assertIn(
            "Check the Superpowers lifecycle skills for every route.",
            self.skill_text,
        )
        self.assertIn(
            "Check `grill-with-docs` when the Spec Stage requires it.",
            self.skill_text,
        )
        self.assertIn(
            "Check `llm-wiki` when a knowledge root exists.",
            self.skill_text,
        )

    def test_common_runtime_capability_guard_is_the_single_capability_owner(self) -> None:
        self.assertEqual(1, self.skill_text.count("## Common Runtime Capability Guard"))
        section = markdown_section(
            self.skill_text,
            "## Common Runtime Capability Guard",
            "## Route By Input Maturity",
        )
        for capability in (
            "installed resource paths",
            "explicit target repository",
            "owned worktree",
            "bound CWD",
            "write destinations",
            "fresh isolated dispatch",
            "explicit model",
            "result collection",
        ):
            self.assertIn(capability, section)
        self.assertIn(
            "before the first affected mutation",
            section,
        )
        for field in ("`status: blocked`", "`artifact_path: none`", "`decision_requests: none`", "`material_risks`"):
            self.assertIn(field, section)
        for diagnosis in ("role or phase", "failed capability or path", "underlying error"):
            self.assertIn(diagnosis, section)
        self.assertNotIn("Codex", self.skill_text)
        self.assertNotIn("Hermes Agent", self.skill_text)

    def test_required_capability_absence_blocks_before_mutation(self) -> None:
        section = markdown_section(
            self.skill_text,
            "## Common Runtime Capability Guard",
            "## Route By Input Maturity",
        )
        normalized = " ".join(section.split())
        self.assertIn(
            "Synchronous dispatch that returns a completed result is a valid "
            "result-collection mechanism.",
            normalized,
        )
        self.assertIn(
            "Asynchronous dispatch requires both wait and resume capabilities.",
            normalized,
        )
        self.assertIn(
            "If neither synchronous result collection nor asynchronous wait/resume "
            "is available, block before the first affected mutation.",
            normalized,
        )
        self.assertIn("Do not infer an unverified substitute", normalized)

    def test_review_is_bounded_to_material_findings(self) -> None:
        for lens in ("requirements fit", "material simplicity", "material current risk"):
            self.assertIn(lens, self.skill_text)
        self.assertIn(
            "A blocking finding needs evidence of a requirement gap,",
            self.skill_text,
        )
        self.assertRegex(
            self.skill_text,
            re.compile(
                r"Do not block on\s+style, formatting, future-only concerns, "
                r"scope-external hardening, or equivalent\s+preferences\."
            ),
        )
        self.assertIn(
            "Do not reduce mechanical validation or required test coverage.",
            self.skill_text,
        )

    def test_local_only_remote_boundary_is_explicit(self) -> None:
        self.assertIn(
            "Do not push, create a PR, merge, release, or install live without separate",
            self.skill_text,
        )
        self.assertIn("explicit authorization.", self.skill_text)

    def test_every_remote_write_requires_explicit_authorization(self) -> None:
        self.assertIn(
            "Do not perform any remote write without separate explicit authorization.",
            self.skill_text,
        )
        self.assertIn(
            "This includes push, PR, merge, release, live install, issue, comment, "
            "and project changes.",
            self.skill_text,
        )

    def test_knowledge_closeout_precedes_final_review(self) -> None:
        task_review = self.skill_text.index("All implementation tasks and task reviews")
        closeout = self.skill_text.index("## Implementation Closeout")
        final_review = self.skill_text.index("## Final Whole-Branch Review")
        self.assertLess(task_review, closeout)
        self.assertLess(closeout, final_review)
        final_section = self.skill_text[final_review:]
        normalized = " ".join(final_section.split())
        canonical_review = (
            "After Implementation Closeout, run exactly one canonical whole-branch "
            "review through the Superpowers review contract."
        )
        self.assertEqual(1, normalized.count(canonical_review))
        self.assertEqual(
            0,
            self.skill_text[:final_review].lower().count("whole-branch review"),
        )

    def test_skill_has_only_the_internal_stage_resource_shape(self) -> None:
        children = (
            {
                path.name
                for path in SKILL_DIR.iterdir()
                if path.is_file() or any(path.iterdir())
            }
            if SKILL_DIR.is_dir()
            else set()
        )
        self.assertEqual(
            {"SKILL.md", "agents", "prompts", "references", "tests"},
            children,
        )
        self.assertEqual(
            {"plan-contract.md", "planning-context.md", "research-stage.md"},
            {path.name for path in (SKILL_DIR / "references").iterdir()},
        )
        self.assertEqual(
            {
                "repository-researcher.md",
                "spec-synthesizer.md",
                "plan-reviewer.md",
                "spec-reviewer.md",
            },
            {path.name for path in (SKILL_DIR / "prompts").iterdir()},
        )
        self.assertFalse((SKILL_DIR / "description.md").exists())
        self.assertFalse((SKILL_DIR / "context-contract.toml").exists())

    def test_openai_metadata_matches_the_skill(self) -> None:
        self.assertIn('display_name: "SDD Implementation"', self.openai_text)
        self.assertIn(
            'short_description: "Develop changes with Superpowers, Grill, and LLM Wiki."',
            self.openai_text,
        )
        self.assertIn(
            'default_prompt: "Use $sdd-implementation to take this repository change '
            'through specification, planning, implementation, and local completion."',
            self.openai_text,
        )

    def test_first_write_gate_precedes_controller(self) -> None:
        self.assertLess(self.skill_text.index("## First-Write Worktree Gate"), self.skill_text.index("## Planning Controller"))
        gate = self.skill_text.split("## First-Write Worktree Gate", 1)[1].split("## Planning Controller", 1)[0]
        for value in ("read-only discovery", "primary/default checkout", "`starting_branch`", "`starting_head_sha`", "task-linked worktree", "shared Git metadata", "zero content/artifact writes", "fallback root"):
            self.assertIn(value, gate)

    def test_execution_shape_and_authority_are_observable_without_an_adapter_algorithm(self) -> None:
        section = markdown_section(
            self.skill_text,
            "## Execution Shape And Authority",
            "## Implementation Closeout",
        )
        for value in (
            "agent / repository-owned",
            "dependency evidence",
            "write-conflict evidence",
            "unknown",
            "sequential execution",
            "material Written Spec change",
            "remote action",
            "Agent-repairable evidence gaps",
        ):
            self.assertIn(value, section)
        self.assertNotIn("North Star", section)
        for forbidden in (
            "explicit Human opt-in",
            "Human-approved issue plan",
            "Human execution-method choice",
            "sequential execution or Human decision",
        ):
            self.assertNotIn(forbidden, section)
        implementation = markdown_section(
            self.skill_text,
            "## Implementation Stage",
            "## Execution Shape And Authority",
        )
        self.assertIn(
            "Within one selected execution unit, run SDD tasks sequentially.",
            implementation,
        )
        self.assertNotIn("Run SDD sequentially.", implementation)

    def test_parallel_units_retain_single_writer_and_reviewed_result_boundaries(self) -> None:
        section = markdown_section(
            self.skill_text,
            "## Execution Shape And Authority",
            "## Implementation Closeout",
        )
        normalized = " ".join(section.split())
        for outcome in (
            "one writer owns each unit and integration",
            "no unit contains concurrent implementers",
            "blocked or unreviewed results are ineligible",
            "Integrate ready units serially",
            "partial integrated state as completion",
        ):
            self.assertIn(outcome, normalized)

    def test_parallel_results_revalidate_actual_changes_and_commit_reachability(self) -> None:
        section = markdown_section(
            self.skill_text,
            "## Execution Shape And Authority",
            "## Implementation Closeout",
        )
        normalized = " ".join(section.split())
        for outcome in (
            "actual commit ranges",
            "changed paths",
            "dependencies",
            "conflicts",
            "every required task commit",
            "history transformation",
        ):
            self.assertIn(outcome, normalized)

    def test_parallel_target_drift_and_combined_review_remain_fail_closed(self) -> None:
        section = markdown_section(
            self.skill_text,
            "## Execution Shape And Authority",
            "## Implementation Closeout",
        )
        normalized = " ".join(section.split())
        for outcome in (
            "integration target must remain the captured target",
            "verified compatible advance",
            "Divergence, rewrite, or uncertainty blocks without retargeting",
            "fresh combined verification",
            "original-checkout preservation",
        ):
            self.assertIn(outcome, normalized)
        self.assertNotIn("whole-branch review", normalized.lower())

    def test_upstream_model_contract_preserves_override_and_optional_effort(self) -> None:
        guard = markdown_section(
            self.skill_text,
            "## Common Runtime Capability Guard",
            "## Route By Input Maturity",
        )
        normalized = " ".join(guard.split())
        self.assertIn("A user model override takes precedence.", normalized)
        self.assertIn("Independent effort control is optional", normalized)
        self.assertIn("its absence does not block", normalized)

    def test_completion_and_publication_boundary(self) -> None:
        for value in ("original-checkout preservation", "`LOCAL_COMPLETE`", "separate explicit authorization"):
            self.assertIn(value, self.skill_text)


if __name__ == "__main__":
    unittest.main()
