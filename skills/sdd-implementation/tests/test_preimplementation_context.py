from __future__ import annotations

from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL = SKILL_DIR / "SKILL.md"
PLANNING_CONTEXT = SKILL_DIR / "references" / "planning-context.md"
RESEARCH_STAGE = SKILL_DIR / "references" / "research-stage.md"
RESEARCHER_PROMPT = SKILL_DIR / "prompts" / "repository-researcher.md"
SYNTHESIZER_PROMPT = SKILL_DIR / "prompts" / "spec-synthesizer.md"
REVIEWER_PROMPT = SKILL_DIR / "prompts" / "spec-reviewer.md"
PLAN_REVIEWER_PROMPT = SKILL_DIR / "prompts" / "plan-reviewer.md"


def read_or_empty(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def routing_cases(text: str) -> dict[str, tuple[str, str, str, str]]:
    if "## Representative Routing Cases" not in text:
        return {}
    body = text.split("## Representative Routing Cases", 1)[1].split("## ", 1)[0]
    rows = []
    for line in body.splitlines():
        if not line.startswith("|") or set(line.replace("|", "").replace(" ", "")) <= {"-", ":"}:
            continue
        rows.append([cell.strip().strip("`") for cell in line.strip().strip("|").split("|")])
    return {
        row[0]: (row[1], row[2], row[3], row[4])
        for row in rows
        if len(row) == 5 and row[0] != "Case"
    }


class PreImplementationContextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill_text = read_or_empty(SKILL)
        cls.planning_text = read_or_empty(PLANNING_CONTEXT)
        cls.research_text = read_or_empty(RESEARCH_STAGE)
        cls.researcher_text = read_or_empty(RESEARCHER_PROMPT)
        cls.synthesizer_text = read_or_empty(SYNTHESIZER_PROMPT)
        cls.reviewer_text = read_or_empty(REVIEWER_PROMPT)
        cls.plan_reviewer_text = read_or_empty(PLAN_REVIEWER_PROMPT)

    def test_entrypoint_limits_main_session_to_planning_controller(self) -> None:
        self.assertIn("## Planning Controller", self.skill_text)
        for ownership in (
            "Human dialogue",
            "Decision Record",
            "approval state",
            "stage routing",
            "Control Return",
        ):
            self.assertIn(ownership, self.skill_text)
        self.assertIn(
            "Do not inspect source code, broad repository content, full artifacts, "
            "diffs, or raw command output.",
            " ".join(self.skill_text.split()),
        )

    def test_planning_controller_allowed_and_forbidden_reads_are_explicit(self) -> None:
        for allowed in (
            "applicable skill instructions and repository `AGENTS.md`",
            "repository root, branch, worktree, and status metadata",
            "Control Return and Stage Capsule",
            "short excerpt for the current decision",
            "approval state and canonical artifact paths",
        ):
            self.assertIn(allowed, self.planning_text)
        for forbidden in (
            "source code",
            "broad wiki or documentation pages",
            "full specification or full implementation plan",
            "git diff, test output, or raw command output",
            "multi-file repository exploration",
        ):
            self.assertIn(forbidden, self.planning_text)

    def test_spec_draft_is_the_only_decision_record(self) -> None:
        self.assertIn("## Decision Record", self.planning_text)
        self.assertIn("`Confirmed Decisions`", self.planning_text)
        self.assertIn("`Open Decisions`", self.planning_text)
        self.assertIn(
            "Do not create a separate ledger, `CONTEXT.md`, or repo-root `docs/adr/`.",
            self.planning_text,
        )
        self.assertIn(
            "Reopen a confirmed decision only when new repository evidence creates "
            "a material conflict.",
            " ".join(self.planning_text.split()),
        )

    def test_control_return_has_only_bounded_semantic_fields(self) -> None:
        self.assertIn("## Control Return", self.planning_text)
        for field in (
            "`status`",
            "`artifact_path`",
            "`decision_requests`",
            "`material_risks`",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn("Keep detailed findings in the artifact.", self.planning_text)
        self.assertIn(
            "Aim for about 200 words; do not add a word-count validator.",
            self.planning_text,
        )

    def test_stage_capsule_carries_only_current_control_state(self) -> None:
        self.assertIn("## Stage Capsule", self.planning_text)
        for field in (
            "current result",
            "canonical paths",
            "open decisions",
            "approval state",
            "material risks",
        ):
            self.assertIn(field, self.planning_text)
        self.assertIn(
            "Aim for about 400 words; do not copy raw discussion or tool output.",
            self.planning_text,
        )

    def test_plan_author_is_fresh_and_uses_upstream_writing_plans(self) -> None:
        normalized = " ".join(self.planning_text.split())
        self.assertIn("Plan Author Worker", self.planning_text)
        self.assertIn("superpowers:writing-plans", self.planning_text)
        self.assertIn("Do not inherit the parent conversation.", self.planning_text)
        self.assertIn(
            "The Planning Controller evaluates only the Plan Author Control Return, "
            "Plan Reviewer verdict and disposition, plan path, spec binding, and readiness disposition.",
            normalized,
        )
        self.assertIn(
            "It does not repeat repository file mapping or code exploration.",
            normalized,
        )

    def test_plan_author_self_review_precedes_fresh_independent_review(self) -> None:
        section = self.planning_text.split("## Plan Authoring", 1)[1].split("## Failure Boundary", 1)[0]
        normalized = " ".join(section.split())
        for value in (
            "author self-review",
            "fresh independent Plan Reviewer",
            "`prompts/plan-reviewer.md`",
            "approved spec path",
            "local overlay path",
            "Plan Author result",
        ):
            self.assertIn(value, normalized)
        self.assertLess(normalized.index("author self-review"), normalized.index("fresh independent Plan Reviewer"))

    def test_local_overlay_suppresses_upstream_execution_handoff(self) -> None:
        section = self.planning_text.split("## Plan Authoring", 1)[1].split("## Failure Boundary", 1)[0]
        normalized = " ".join(section.split())
        for value in (
            "Local override: skip the upstream `superpowers:writing-plans` `## Execution Handoff`.",
            "Do not offer Subagent-Driven or Inline Execution",
            "Do not ask the Human which execution approach to use",
            "reviewed `ready` deterministically enters the Implementation Stage",
            "`superpowers:subagent-driven-development`",
        ):
            self.assertIn(value, normalized)

    def test_plan_review_routes_only_ready_to_implementation(self) -> None:
        section = self.planning_text.split("## Plan Authoring", 1)[1].split("## Failure Boundary", 1)[0]
        for value in (
            "`ready`",
            "`issues_found`",
            "`needs_repair`",
            "`needs_decision`",
            "`blocked`",
            "Implementation Stage entry",
            "status: complete",
        ):
            self.assertIn(value, section)
        self.assertIn("`needs_repair` remains inside the agent-owned Plan Stage", section)
        self.assertIn("only an evidenced material spec conflict", section)
        self.assertIn("Do not make missing remote publication authorization a plan blocker", section)

    def test_plan_reviewer_maps_each_representative_case_exactly(self) -> None:
        self.assertEqual(
            {
                "ready plan": ("ready", "ready", "none", "status: complete -> Implementation Stage entry"),
                "unassigned acceptance": ("issues_found", "needs_repair", "none", "fresh Plan Author -> fresh independent Plan Reviewer"),
                "prospective body": ("issues_found", "needs_repair", "none", "fresh Plan Author -> fresh independent Plan Reviewer"),
                "dependency cycle": ("issues_found", "needs_repair", "none", "fresh Plan Author -> fresh independent Plan Reviewer"),
                "current-tree method correction": ("issues_found", "needs_repair", "none", "fresh Plan Author -> fresh independent Plan Reviewer"),
                "serialized integration defect": ("issues_found", "needs_repair", "none", "fresh Plan Author -> fresh independent Plan Reviewer"),
                "material spec conflict": ("issues_found", "needs_decision", "one", "one Human decision request"),
                "non-decision blocker": ("issues_found", "blocked", "none", "Control Return status: blocked"),
                "missing remote publication authorization": ("ready", "ready", "none", "status: complete -> Implementation Stage entry"),
            },
            routing_cases(self.plan_reviewer_text),
        )

    def test_only_ready_transitions_and_repairs_never_leave_the_agent_loop(self) -> None:
        cases = routing_cases(self.plan_reviewer_text)
        for _, disposition, decisions, route in cases.values():
            self.assertEqual(disposition == "ready", "Implementation Stage entry" in route)
            self.assertEqual(disposition == "needs_decision", decisions == "one")
            if disposition == "needs_repair":
                self.assertEqual("fresh Plan Author -> fresh independent Plan Reviewer", route)

    def test_missing_fresh_dispatch_never_falls_back_to_controller_exploration(self) -> None:
        self.assertIn(
            "If isolated fresh-context dispatch is unavailable, return `BLOCKED`.",
            self.planning_text,
        )
        self.assertIn(
            "Do not fall back to Planning Controller exploration or artifact authoring.",
            self.planning_text,
        )

    def test_research_stage_routes_only_fresh_repository_exploration(self) -> None:
        normalized = " ".join(self.research_text.split())
        self.assertIn("`.superpowers/research/<epic-id>/`", self.research_text)
        self.assertIn("`prompts/repository-researcher.md`", self.research_text)
        self.assertIn("Do not inherit the parent conversation.", self.research_text)
        self.assertIn(
            "The Planning Controller reads the Control Return, not the report body.",
            normalized,
        )
        for category in ("confirmed facts", "material conflicts", "unknowns"):
            self.assertIn(category, self.research_text)

    def test_non_plan_review_worker_prompts_are_advisory_and_return_control_fields(self) -> None:
        for prompt_text in (
            self.researcher_text,
            self.synthesizer_text,
            self.reviewer_text,
        ):
            self.assertIn("Do not inherit the parent conversation.", prompt_text)
            self.assertIn("advisory-only", prompt_text)
            for field in (
                "`status`",
                "`artifact_path`",
                "`decision_requests`",
                "`material_risks`",
            ):
                self.assertIn(field, prompt_text)

    def test_plan_reviewer_returns_a_bounded_verdict_before_control_mapping(self) -> None:
        self.assertIn("Do not inherit the parent conversation.", self.plan_reviewer_text)
        self.assertIn("advisory-only", self.plan_reviewer_text)
        for field in (
            "`verdict`",
            "`disposition`",
            "`artifact_path`",
            "`decision_requests`",
            "`material_risks`",
        ):
            self.assertIn(field, self.plan_reviewer_text)
        self.assertNotIn("- `status`:", self.plan_reviewer_text)

    def test_research_prompt_requires_path_and_line_evidence(self) -> None:
        for category in (
            "Confirmed Facts",
            "Material Conflicts",
            "Unknowns",
        ):
            self.assertIn(category, self.researcher_text)
        self.assertIn("repository-relative path and line range", self.researcher_text)
        self.assertIn("git history", self.researcher_text)
        self.assertIn("llm-wiki", self.researcher_text)

    def test_spec_synthesis_and_review_are_separate_fresh_workers(self) -> None:
        self.assertIn("Spec Synthesis Worker", self.synthesizer_text)
        self.assertIn("Spec Reviewer", self.reviewer_text)
        self.assertIn("`Confirmed Decisions`", self.synthesizer_text)
        self.assertIn("`Open Decisions`", self.synthesizer_text)
        self.assertIn("Do not fill an unresolved decision with an assumption.", self.synthesizer_text)
        for review_lens in (
            "accepted decisions",
            "resolved questions",
            "repository evidence",
            "unknowns",
            "acceptance criteria",
            "non-goals",
            "stop conditions",
        ):
            self.assertIn(review_lens, self.reviewer_text)

    def test_internal_resource_shape_has_no_new_user_facing_or_runtime_surface(self) -> None:
        references = {
            path.name for path in (SKILL_DIR / "references").iterdir()
        }
        prompts = {
            path.name for path in (SKILL_DIR / "prompts").iterdir()
        }
        self.assertEqual(
            {"plan-contract.md", "planning-context.md", "research-stage.md"},
            references,
        )
        self.assertEqual(
            {
                "repository-researcher.md",
                "spec-synthesizer.md",
                "plan-reviewer.md",
                "spec-reviewer.md",
            },
            prompts,
        )
        for forbidden in (
            "context-contract.toml",
            "runtime-state.json",
            "worker-packet.json",
            "fallback-matrix.md",
            "scheduler.py",
        ):
            self.assertFalse((SKILL_DIR / forbidden).exists())

    def test_contract_rejects_numerical_context_control_and_controller_fallback(self) -> None:
        combined = "\n".join(
            (
                self.skill_text,
                self.planning_text,
                self.research_text,
                self.researcher_text,
                self.synthesizer_text,
                self.reviewer_text,
                self.plan_reviewer_text,
            )
        )
        self.assertIn(
            "Do not require context telemetry, manual compaction, or a strict "
            "word-count validator.",
            combined,
        )
        self.assertIn(
            "Do not fall back to Planning Controller exploration or artifact authoring.",
            combined,
        )

    def test_binding_tuple_lifetime_and_recovery_are_required(self) -> None:
        section = self.planning_text.split("## Stage Capsule", 1)[1].split("## Spec Synthesis And Review", 1)[0]
        for value in ("original checkout path", "`starting_branch`", "`starting_head_sha`", "captured starting status", "`integration_branch`", "Stage Capsule/control context", "plan-owned workspace/progress ledger", "Human restart/confirmation", "`BLOCKED`"):
            self.assertIn(value, section)
        for value in ("reconstruct", "compatibility bridge", "pre-plan reservation", "resume record"):
            self.assertIn(value, section)

    def test_bound_paths_and_first_report_are_required(self) -> None:
        for text in (self.researcher_text, self.synthesizer_text, self.reviewer_text):
            for value in ("resolved planning worktree root", "CWD", "writable artifact path", "original checkout"):
                self.assertIn(value, text)
            self.assertNotIn("- repository root;", text)
        for value in ("first transient Research Report", "relative", "absolute", "stale path", "escape"):
            self.assertIn(value, self.research_text)
        for value in ("original checkout metadata (read-only)", "baseline commit", "epic ID and current research question", "applicable repository and knowledge constraints", "current spec path when one exists"):
            self.assertIn(value, self.research_text)
        self.assertNotIn("- repository root and current baseline commit;", self.research_text)

    def test_plan_author_uses_only_bound_planning_paths(self) -> None:
        section = self.planning_text.split("## Plan Authoring", 1)[1].split("## Failure Boundary", 1)[0]
        normalized = " ".join(section.split())
        for value in ("resolved planning worktree root", "bound CWD", "writable plan artifact path", "original checkout metadata (read-only)", "Plan Author Worker"):
            self.assertIn(value, normalized)
        self.assertNotIn("repository root, baseline commit", normalized)


if __name__ == "__main__":
    unittest.main()
