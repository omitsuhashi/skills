from __future__ import annotations

from pathlib import Path
import re
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


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

    def test_public_contract_rejects_repository_specific_or_ambiguous_gate_owners(self) -> None:
        section = self.skill_text.split("## Repository Validation Gate", 1)[1].split(
            "## Plan Stage", 1
        )[0]
        for forbidden in (
            "scripts/validate_sdd_transient_artifacts.py",
            "migration manifest",
            "f07aebc",
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
            "`BLOCKED: skill/package unavailable`",
            "`BLOCKED: target/runtime unavailable`",
            "`FAIL: exceptional-local-scratch-pre-write`",
            "`FAIL: pre-commit-candidate`",
            "`FAIL: final-closeout`",
        ):
            with self.subTest(classification=classification):
                self.assertIn(classification, normalized)
        self.assertIn(
            "Evidence is single-use: recompute the selected gate from current Git objects and state",
            normalized,
        )

    def test_upstream_owns_model_tiers_and_local_contract_only_adds_effort(self) -> None:
        self.assertIn("Follow the current Superpowers SDD Model Selection contract.", self.skill_text)
        self.assertIn("Every subagent dispatch must state its model.", self.skill_text)
        self.assertIn("| Mechanical task or small scoped re-review | `low` |", self.skill_text)
        self.assertIn("| Multi-file integration, normal debugging, or task review | `medium` |", self.skill_text)
        self.assertIn("| Architecture-sensitive or high-risk task, or final review | `high` |", self.skill_text)
        self.assertIn("`not_supported`", self.skill_text)
        self.assertNotIn("| orchestrator |", self.skill_text)
        self.assertNotIn("economical balanced", self.skill_text)
        self.assertNotRegex(self.skill_text, re.compile(r"\bgpt-[0-9]"))

    def test_user_model_and_effort_overrides_have_independent_precedence(self) -> None:
        self.assertIn(
            "An explicit user runtime model override takes precedence over "
            "upstream model-tier resolution.",
            self.skill_text,
        )
        self.assertIn(
            "An explicit user runtime effort override takes precedence over "
            "the default effort overlay.",
            self.skill_text,
        )

    def test_task_complexity_and_risk_override_role_effort_defaults(self) -> None:
        self.assertIn(
            "Task complexity and current risk take precedence over role defaults.",
            self.skill_text,
        )
        self.assertIn(
            "A high-risk task review uses `high`, regardless of its role default.",
            self.skill_text,
        )
        self.assertIn(
            "The shared default effort vocabulary is limited to `low`, `medium`, and `high`.",
            self.skill_text,
        )

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

    def test_runtime_capability_boundary_distinguishes_optional_effort_from_required_dispatch(self) -> None:
        self.assertIn("## Runtime Capability Boundary", self.skill_text)
        for capability in (
            "isolated dispatch",
            "explicit model",
            "optional effort",
            "wait",
            "resume",
        ):
            self.assertIn(capability, self.skill_text)
        self.assertIn(
            "Lack of independent effort control does not block the flow.",
            self.skill_text,
        )
        self.assertIn(
            "Lack of isolated dispatch with an explicit model is `BLOCKED`.",
            self.skill_text,
        )
        self.assertNotIn("Codex", self.skill_text)
        self.assertNotIn("Hermes Agent", self.skill_text)

    def test_result_collection_requires_sync_completion_or_async_coordination(self) -> None:
        normalized = " ".join(self.skill_text.split())
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
            "is available, return `BLOCKED`.",
            normalized,
        )

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

    def test_skill_has_only_the_internal_stage_resource_shape(self) -> None:
        children = {path.name for path in SKILL_DIR.iterdir()} if SKILL_DIR.is_dir() else set()
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
        for value in ("read-only discovery", "Detached HEAD", "default-branch inference", "`starting_branch`", "`starting_head_sha`", "Epic branch/path", "shared Git metadata", "zero content/artifact write", "original checkout fallback"):
            self.assertIn(value, gate)

    def test_parallel_adapter_leaves_issue_sdd_sequential(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("Within an issue, never dispatch concurrent implementers.", "Do not advance to the next task until its task review and any canonical fix are complete.", "Each issue execution unit has exactly one branch/worktree/session/plan/artifact workspace and exactly one writer.", "does not schedule issue-internal tasks"):
            self.assertIn(value, section)

    def test_parallel_eligibility_is_fail_closed(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("agent / repository-owned eligibility", "repository-ready issue plan", "one branch/worktree/session/plan/artifact workspace", "expected write overlap", "shared mutable resource", "pinned-base ancestry", "unknown", "sequential handling"):
            self.assertIn(value, section)
        for forbidden in ("explicit Human opt-in", "Human-approved issue plan", "Human execution-method choice", "sequential handling or Human decision"):
            self.assertNotIn(forbidden, section)
        self.assertIn(
            "Only an evidenced material North Star / Written Spec conflict returns to Human authority.",
            section,
        )

    def test_actual_result_revalidation_is_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("actual commit range", "actual changed paths", "semantic/resource assumptions", "Before integration-ready", "before every serialized integration", "sibling results"):
            self.assertIn(value, section)

    def test_every_task_commit_reachability_is_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("blocked or unreviewed result is not integration-ready", "every required issue/task commit", "reachable", "issue tip", "squash", "selected cherry-pick"):
            self.assertIn(value, section)

    def test_serialized_integration_and_target_drift_are_required(self) -> None:
        section = self.skill_text.split("## Epic Parallel Issue Adapter", 1)[1].split("## Runtime Model", 1)[0]
        for value in ("target head is unchanged", "single-writer serialized integration", "one ready issue at a time", "partial integrated state", "descendant advance", "non-descendant rewrite", "silently retarget"):
            self.assertIn(value, section)

    def test_combined_gate_is_canonical_and_single_pass(self) -> None:
        for value in ("fresh combined verification", "whole-branch review", "one fixer", "exactly one scoped re-review", "second fix wave", "repeated whole-branch review"):
            self.assertIn(value, self.skill_text)

    def test_completion_and_publication_boundary(self) -> None:
        for value in ("original-checkout preservation", "`LOCAL_COMPLETE`", "separate explicit authorization", "PR base", "PR head", "valid remote PR base"):
            self.assertIn(value, self.skill_text)


if __name__ == "__main__":
    unittest.main()
