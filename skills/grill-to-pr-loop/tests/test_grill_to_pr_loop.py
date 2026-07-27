from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
CHECK_PREREQS = SKILL_DIR / "scripts" / "check_prereqs.py"
CORE_REFERENCE = SKILL_DIR / "references" / "core.md"
PLANNING_CONTRACT = SKILL_DIR / "references" / "planning-contract.md"
EXECUTION_HANDOFF = SKILL_DIR / "references" / "execution-handoff.md"
ISSUE_LOOP_DIR = REPO_ROOT / "skills" / "issue-implementation-loop"
GRILL_AGENT_YAML = SKILL_DIR / "agents" / "openai.yaml"
ISSUE_AGENT_YAML = REPO_ROOT / "skills" / "issue-implementation-loop" / "agents" / "openai.yaml"


def load_check_prereqs():
    spec = importlib.util.spec_from_file_location("grill_to_pr_check_prereqs", CHECK_PREREQS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_default_prompt(path: Path) -> str:
    prefix = "  default_prompt: "
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            value = line[len(prefix) :]
            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]
    raise AssertionError(f"default_prompt not found in {path}")


def tracked_current_execution_envelope_v4_paths(repo_root: Path) -> list[str]:
    tracked = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "ls-files",
            "-z",
            "--",
            "knowledge/wiki/syntheses",
        ],
        check=True,
        capture_output=True,
    ).stdout
    detected: list[str] = []
    for encoded_path in tracked.split(b"\0"):
        if not encoded_path or not encoded_path.endswith(b".json"):
            continue
        path = os.fsdecode(encoded_path)
        blob = subprocess.run(
            ["git", "-C", str(repo_root), "show", f":{path}"],
            check=True,
            capture_output=True,
        ).stdout
        try:
            payload = json.loads(blob)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and payload.get("schema_version") == 4:
            detected.append(path)
    return detected


class GrillToPrLoopTests(unittest.TestCase):
    def test_asb_34_current_epic_tracks_only_durable_planning_artifacts(self) -> None:
        current_root = "knowledge/wiki/syntheses/approved-spec-binding-contract"
        tracked = set(
            subprocess.run(
                ["git", "-C", str(REPO_ROOT), "ls-files", current_root],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        )
        required = {
            f"{current_root}/spec.md",
            f"{current_root}/issues.md",
            f"{current_root}/implementation-plan.md",
            f"{current_root}/input-packet.json",
        }
        forbidden_names = {
            "execution-envelope.json",
            "runtime-state.json",
            "events.jsonl",
            "execution-result.json",
            "delivery-plan.json",
        }

        self.assertLessEqual(required, tracked)
        self.assertFalse(
            {path for path in tracked if Path(path).name in forbidden_names}
        )
        self.assertEqual(
            tracked_current_execution_envelope_v4_paths(REPO_ROOT), []
        )

    def test_asb_34_detects_tracked_flat_v4_execution_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(
                ["git", "init", "-q", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            synthesis_root = repo / "knowledge" / "wiki" / "syntheses"
            synthesis_root.mkdir(parents=True)
            current_flat = (
                synthesis_root
                / "approved-spec-binding-contract-execution-envelope.json"
            )
            historical = synthesis_root / "historical-execution-envelope.json"
            malformed = synthesis_root / "not-an-artifact.json"
            product_template = (
                repo
                / "skills"
                / "issue-implementation-loop"
                / "assets"
                / "templates"
                / "execution-envelope.json"
            )
            product_template.parent.mkdir(parents=True)
            envelope_shape = {
                "schema_version": 4,
                "epic_id": "approved-spec-binding-contract",
                "revision": 1,
                "approved_spec_binding": {},
                "work_items": {},
            }
            current_flat.write_text(
                json.dumps(envelope_shape, sort_keys=True), encoding="utf-8"
            )
            historical.write_text(
                json.dumps({**envelope_shape, "schema_version": 3}, sort_keys=True),
                encoding="utf-8",
            )
            malformed.write_text("{not-json\n", encoding="utf-8")
            product_template.write_text(
                json.dumps(envelope_shape, sort_keys=True), encoding="utf-8"
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "add",
                    "knowledge/wiki/syntheses",
                    "skills/issue-implementation-loop/assets/templates",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            detected = tracked_current_execution_envelope_v4_paths(repo)

            self.assertEqual(
                detected,
                [
                    "knowledge/wiki/syntheses/"
                    "approved-spec-binding-contract-execution-envelope.json"
                ],
            )

    def test_artifact_lifecycle_references_keep_current_ownership_seam(self) -> None:
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        handoff_text = EXECUTION_HANDOFF.read_text(encoding="utf-8")
        issue_skill_text = (ISSUE_LOOP_DIR / "SKILL.md").read_text(encoding="utf-8")
        envelope_text = (
            ISSUE_LOOP_DIR / "references" / "execution-envelope.md"
        ).read_text(encoding="utf-8")
        runtime_text = (
            ISSUE_LOOP_DIR / "references" / "runtime-state.md"
        ).read_text(encoding="utf-8")
        combined = "\n".join(
            (planning_text, handoff_text, issue_skill_text, envelope_text, runtime_text)
        )

        required = (
            "<durable-planning-root>/<epic-id>/",
            "spec.md",
            "issues.md",
            "implementation-plan.md",
            "input-packet.json",
            "$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/",
            "execution-envelope.json",
            "Do not commit instantiated execution artifacts",
        )
        for value in required:
            self.assertIn(value, combined)

        planning_guidance = f"{planning_text}\n{handoff_text}"
        self.assertNotRegex(
            planning_guidance,
            r"(?i)commit(?: the)? (?:an? )?Execution Envelope",
        )

    def test_asb_36_tracked_json_templates_use_nested_epic_paths(self) -> None:
        template_dir = ISSUE_LOOP_DIR / "assets" / "templates"
        schema_dir = ISSUE_LOOP_DIR / "assets" / "schemas"
        product_json = sorted(template_dir.glob("*.json")) + sorted(
            schema_dir.glob("*.json")
        )
        tracked = set(
            subprocess.run(
                ["git", "-C", str(REPO_ROOT), "ls-files"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        )
        for path in product_json:
            relative = path.relative_to(REPO_ROOT).as_posix()
            with self.subTest(path=relative):
                self.assertIn(relative, tracked)
                json.loads(path.read_text(encoding="utf-8"))

        expected_parameterized = (
            "knowledge/wiki/syntheses/<epic-id>/input-packet.json"
        )
        expected_example = "knowledge/wiki/syntheses/example/input-packet.json"
        envelope = json.loads(
            (template_dir / "execution-envelope.json").read_text(encoding="utf-8")
        )
        worker = json.loads(
            (template_dir / "worker-packet.json").read_text(encoding="utf-8")
        )
        hardening = json.loads(
            (template_dir / "hardening-candidates.json").read_text(encoding="utf-8")
        )
        delivery = json.loads(
            (template_dir / "delivery-plan.json").read_text(encoding="utf-8")
        )
        result = json.loads(
            (template_dir / "execution-result.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            envelope["approved_spec_binding"]["path"], expected_parameterized
        )
        self.assertEqual(
            envelope["work_items"]["G2PR-001"]["source"]["path"],
            "knowledge/wiki/syntheses/<epic-id>/issues.md",
        )
        self.assertEqual(
            worker["source_revision"]["approved_spec_binding"]["path"],
            expected_parameterized,
        )
        self.assertEqual(
            worker["source_revision"]["issue_source"]["path"],
            "knowledge/wiki/syntheses/<epic-id>/issues.md",
        )
        self.assertEqual(
            [entry["path"] for entry in worker["read_paths"]],
            [
                "knowledge/wiki/syntheses/<epic-id>/spec.md",
                "knowledge/wiki/syntheses/<epic-id>/issues.md",
            ],
        )
        self.assertEqual(
            worker["inline_context"][0]["path"],
            "knowledge/wiki/syntheses/<epic-id>/issues.md",
        )
        self.assertEqual(
            hardening["approved_spec_binding"]["path"], expected_parameterized
        )
        self.assertEqual(delivery["approved_spec_binding"]["path"], expected_example)
        self.assertEqual(result["approved_spec_binding"]["path"], expected_example)

    def test_remote_delivery_reference_uses_current_delivery_validator_signature(self) -> None:
        text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(
            encoding="utf-8"
        )
        command = (
            "validate_delivery_plan.py <execution-envelope.json> "
            "<runtime-state.json> <execution-result.json> <delivery-plan.json> "
            "--repo-root <trusted-worktree-root> --json"
        )
        self.assertIn(command, text)
        self.assertNotIn(
            "<runtime-state.json> <delivery-plan.json> --json", text
        )

    def test_skill_description_is_trigger_only(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        description = next(
            line.removeprefix("description: ")
            for line in text.splitlines()
            if line.startswith("description: ")
        )

        self.assertEqual(
            description,
            "Use when a repository change requires approved durable design, issue decomposition, and worker-only implementation.",
        )

    def test_planning_authority_contract_separates_integration_advice_and_decision(
        self,
    ) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        combined = f"{skill_text}\n{planning_text}"

        for required in (
            "main planning context integrates canonical spec/issue ledger/execution plan/sealed packet",
            "finalizes the Human Gate approval candidate",
            "Human decides the Gate",
        ):
            self.assertIn(required, skill_text)

        for required in (
            "integrates canonical content across the spec, issue ledger, execution plan, and sealed Input Packet",
            "finalizes the approval candidate presented to the Human Gate",
            "Human decides the Gate",
        ):
            self.assertIn(required, planning_text)

        for required in (
            "main planning context is the integration owner",
            "supporting agents are advisory-only and read-only",
            "Human is the decision authority",
            "bounded question",
            "repo-relative read paths",
            "evidence",
            "must not write canonical planning artifacts",
            "approve a spec or scope",
            "seal an Input Packet",
            "compares evidence when advice conflicts",
            "never uses a vote or majority",
            "authority-bearing ambiguity",
            "Human gate",
            "fresh primary context",
            "explicit ownership transfer",
            "not a supporting dispatch",
            "A user-selected model change or host model unavailability is host runtime state, not spec or packet drift.",
        ):
            self.assertIn(required, combined)

    def test_planning_contract_seals_the_exact_approved_spec_revision(self) -> None:
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(
            encoding="utf-8"
        )
        combined = f"{planning_text}\n{handoff_text}"

        for required in (
            "one Spec Gate approval",
            "repo-relative spec path",
            "exact raw-byte SHA-256",
            "accepted_decisions",
            "non_goals",
            "acceptance_criteria",
            "verification",
            "remote_policy",
            "stop_conditions",
            "check_prereqs.py --phase execution --json",
            'required["issue-implementation-loop"]',
            "<issue-implementation-loop-skill-dir>/scripts/approved_spec_binding.py identify",
            "<issue-implementation-loop-skill-dir>/scripts/approved_spec_binding.py seal",
            "<issue-implementation-loop-skill-dir>/scripts/validate_input_packet.py",
            "<issue-implementation-loop-skill-dir>/scripts/check_capabilities.py",
            "--draft-packet",
            "--output-packet",
            "--spec-path",
            "--spec-sha256",
            "--decision approved",
            "--subject spec_binding",
            "--actor-expression",
            "--approved-at",
            "Any spec byte change requires re-approval and a new seal",
            "Input Packet v2",
            "Execution Envelope v4",
        ):
            self.assertIn(required, combined)

        for scope_field in (
            "accepted_decisions",
            "non_goals",
            "acceptance_criteria",
            "verification",
            "remote_policy",
            "stop_conditions",
        ):
            self.assertIn(f"--approve-scope {scope_field}", combined)

        self.assertNotIn("when available", combined)
        self.assertNotIn("schema version `3` Execution Envelope", combined)
        self.assertNotIn("skills/issue-implementation-loop/", combined)

    def test_planning_contract_splits_spec_and_execution_intent_drift_routes(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(
            encoding="utf-8"
        )
        combined = f"{skill_text}\n{handoff_text}"

        lifecycle_outcomes = (
            "Exact restoration of unintended packet byte drift plus fresh validation "
            "retains the existing approved binding, Envelope revision, and runtime epoch.",
            "An intended non-spec packet byte change goes through the Execution Plan Gate "
            "for reconciliation and revalidation, a new reseal, and a new Envelope revision "
            "and runtime epoch, without a new human Spec Gate approval.",
            "A change to spec bytes, `spec_binding`, or `approval_evidence` goes through the "
            "human Spec Gate for a new approval and seal, then a new Envelope revision and "
            "runtime epoch.",
        )
        for outcome in lifecycle_outcomes:
            self.assertIn(outcome, combined)
        self.assertNotIn("Both routes", combined)

        for required in (
            "spec bytes, `spec_binding`, or `approval_evidence`",
            "human Spec Gate",
            "new approval and seal",
            "execution-intent-only packet drift",
            "issue scope, dependencies, write scope, or delivery intent",
            "any other sealed packet byte drift",
            "while `spec_binding` and `approval_evidence` remain exact",
            "other packet fields",
            "serialization or whitespace-only drift",
            "Execution Plan Gate",
            "reconciliation and revalidation",
            "reseal only when the changed bytes are intended",
            "without a new human Spec Gate approval",
        ):
            self.assertIn(required, combined)

    def test_execution_handoff_requires_planning_identity_for_new_drafts(self) -> None:
        handoff_text = EXECUTION_HANDOFF.read_text(encoding="utf-8")

        self.assertIn("Every new draft must include both", handoff_text)
        self.assertIn('"planning_branch": "codex/<epic-id>/planning"', handoff_text)
        self.assertIn('"planning_base_sha": "<full-40-or-64-character-sha>"', handoff_text)

    def test_historical_packets_and_envelopes_are_indexed_as_non_executable(self) -> None:
        index_text = (REPO_ROOT / "knowledge" / "index.md").read_text(encoding="utf-8")
        synthesis_root = REPO_ROOT / "knowledge" / "wiki" / "syntheses"
        historical_paths: list[Path] = []
        for pattern, current_version in (
            ("*input-packet.json", 2),
            ("*execution-envelope.json", 4),
        ):
            for path in synthesis_root.glob(pattern):
                payload = json.loads(path.read_text(encoding="utf-8"))
                if payload.get("schema_version") != current_version:
                    historical_paths.append(path)

        self.assertTrue(historical_paths)
        for path in historical_paths:
            entry = next(
                (line for line in index_text.splitlines() if path.name in line),
                None,
            )
            self.assertIsNotNone(entry, f"historical artifact is not indexed: {path.name}")
            assert entry is not None
            self.assertIn("historical", entry, path.name)
            self.assertIn("non-executable", entry, path.name)

    def test_core_reference_owns_global_workflow_context(self) -> None:
        text = CORE_REFERENCE.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.split()), 600)
        for required in (
            "Lifecycle",
            "Responsibilities",
            "Gates",
            "Local-first",
            "Remote approval",
        ):
            self.assertIn(required, text)

    def test_github_mirror_read_set_contains_remote_gate(self) -> None:
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(encoding="utf-8")
        remote_text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(encoding="utf-8")

        self.assertIn('[operations.delivery]', contract_text)
        self.assertIn('"references/remote-delivery.md"', contract_text)
        self.assertIn("## GitHub Mirror Gate", remote_text)
        for required in (
            "Confirm the remote points to GitHub.",
            "Confirm GitHub tool/CLI auth.",
            "Present exact local issues to publish.",
            "Ask for explicit approval.",
            "Update the local ledger before continuing.",
        ):
            self.assertIn(required, remote_text)

    def test_final_pr_delivery_requires_spec_alignment_review(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        remote_text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(encoding="utf-8")
        combined = f"{skill_text}\n{remote_text}"

        for required in (
            "superpowers:requesting-code-review",
            "spec alignment",
            "スペックに対して過不足がないか",
            "スペックに対してずれた実装をしていないか",
            "After all issue PRs are merged",
            "before creating the final PR",
            "final PR ready-for-review",
            "implementation review summary",
            "spec alignment review summary",
        ):
            self.assertIn(required, combined)

    def test_skill_entrypoint_points_to_context_contract_router(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(text.split()), 950)
        self.assertIn("references/core.md", text)
        self.assertIn("context-contract.toml", text)
        self.assertIn("operation router", text)
        for operation_reference in (
            "planning-contract.md",
            "local-issue-ledger.md",
            "execution-handoff.md",
            "remote-delivery.md",
            "common-mistakes.md",
            "workflow-contract.md",
        ):
            self.assertNotIn(operation_reference, text)

    def test_skill_entrypoint_defines_loop_applicability(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        for required in (
            "Use loop skills when",
            "Do not use loop skills for",
            "Stop before implementation when",
            "small one-off edits",
            "direct implementation",
            "approved packet",
            "worker context",
        ):
            self.assertIn(required, text)

    def test_entrypoint_discovers_issue_execution_mental_model_without_default_read_set(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(encoding="utf-8")
        issue_mental_model = REPO_ROOT / "skills" / "issue-implementation-loop" / "references" / "mental-model.md"

        self.assertIn("mental-model.md", text)
        self.assertTrue(issue_mental_model.exists())
        self.assertNotIn("mental-model.md", contract_text)

        model_text = issue_mental_model.read_text(encoding="utf-8")
        for required in (
            "coordinator",
            "worker",
            "reviewer",
            "runtime state",
            "local ledger",
            "remote delivery",
        ):
            self.assertIn(required, model_text)

    def test_generated_specs_and_packets_default_to_japanese_base_language(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(encoding="utf-8")
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(encoding="utf-8")
        worker_contract_text = (REPO_ROOT / "skills" / "issue-implementation-loop" / "references" / "worker-contract.md").read_text(encoding="utf-8")
        input_template = (REPO_ROOT / "skills" / "issue-implementation-loop" / "assets" / "templates" / "input-packet.json").read_text(encoding="utf-8")
        worker_template = (REPO_ROOT / "skills" / "issue-implementation-loop" / "assets" / "templates" / "worker-packet.json").read_text(encoding="utf-8")

        for text in (skill_text, core_text, planning_text):
            self.assertIn("Japanese", text)
            self.assertIn("schema keys", text)

        for required in (
            "問題設定 / 成功条件",
            "採用した判断",
            "非目標",
            "Issue 分解方針",
            "受け入れ条件",
            "リモート書き込み方針",
            "人間レビューゲート",
            "停止条件 / 既知のリスク",
        ):
            self.assertIn(required, planning_text)

        self.assertIn("English spec/PRD", mistakes_text)
        for required in (
            "work_items[].title",
            "acceptance_criteria",
            "non_goals",
        ):
            self.assertIn(required, handoff_text)
        for required in (
            "issue_title",
            "task.summary",
            "task.acceptance_criteria",
            "task.stop_conditions",
        ):
            self.assertIn(required, worker_contract_text)
        self.assertIn("user-facing packet string は日本語をベースにする", handoff_text)
        self.assertIn("user-facing packet string は日本語をベースにする", worker_contract_text)
        self.assertIn("短い日本語 issue タイトル", input_template)
        self.assertIn("必要な挙動の短い要約", worker_template)
        self.assertNotIn("Short issue title", input_template + worker_template)

    def test_phase_gate_approvals_require_local_commit(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        planning_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(encoding="utf-8")
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(encoding="utf-8")

        self.assertIn("phase approval commit", skill_text)
        self.assertIn("phase_branch_policy", skill_text)
        self.assertIn("commit the approved artifacts", core_text)
        self.assertIn("Spec Gate approval", planning_text)
        self.assertIn("Issue Gate approval", planning_text)
        self.assertIn("Execution Plan Gate approval", handoff_text)
        self.assertIn("current planning branch", handoff_text)
        self.assertIn("Execution Envelope v4", handoff_text)
        self.assertIn("Moving to the next phase without committing an approved gate", mistakes_text)

    def test_gate_taxonomy_separates_human_preflight_and_remote_boundaries(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(encoding="utf-8")
        combined = f"{skill_text}\n{core_text}"

        for required in (
            "Spec Gate",
            "Issue Gate",
            "human decision gate",
            "Execution Plan Gate",
            "agent preflight + commit boundary",
            "not a human approval gate",
            "Remote Gate",
            "outside approved remote policy",
            "external write",
            "human-only",
        ):
            self.assertIn(required, combined)

        self.assertIn("draft final PR", mistakes_text)
        self.assertIn("approved remote policy", mistakes_text)
        self.assertNotIn("Treating PR creation as implicit | Get explicit approval first.", mistakes_text)

    def test_execution_plan_gate_auto_continue_keeps_evidence_and_stop_conditions(self) -> None:
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(encoding="utf-8")
        core_text = CORE_REFERENCE.read_text(encoding="utf-8")
        combined = f"{handoff_text}\n{core_text}"

        for required in (
            "auto-continue without another human approval",
            "validate_input_packet.py",
            "capability preflight",
            "normalized packet path and validation result",
            "approved write scope",
            "dependency graph",
            "phase_branch_policy",
            "remote policy summary",
            "commit the approved artifacts",
            "knowledge/log.md",
            "issue-implementation-loop prepare",
            "fresh or compacted coordinator context",
            "dirty changes overlap planned write scope",
            "worker context is unavailable",
            "remote policy does not match the approved remote policy",
            "planning/grill session must not become an implementation worker",
        ):
            self.assertIn(required, combined)

    def test_agent_default_prompts_are_short_and_policy_free(self) -> None:
        for path, skill_name in (
            (GRILL_AGENT_YAML, "$grill-to-pr-loop"),
            (ISSUE_AGENT_YAML, "$issue-implementation-loop"),
        ):
            default_prompt = extract_default_prompt(path)
            self.assertIn(skill_name, default_prompt)
            self.assertLessEqual(len(default_prompt.split()), 32)
            for forbidden in (
                "branch",
                "delivery",
                "review",
                "merge",
                "worktree",
                "epic-base",
            ):
                self.assertNotIn(forbidden, default_prompt.lower())

    def test_candidate_roots_prefers_explicit_then_repo_local_then_global(self) -> None:
        module = load_check_prereqs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            explicit = root / "explicit-skills"
            repo.mkdir()
            home.mkdir()

            previous_cwd = Path.cwd()
            try:
                os.chdir(repo)
                with (
                    mock.patch.object(module.Path, "home", return_value=home),
                    mock.patch.dict(module.os.environ, {}, clear=True),
                ):
                    roots = module.candidate_roots([str(explicit)])
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(roots[:5], [
            explicit,
            repo.resolve() / "skills",
            repo.resolve() / ".agents" / "skills",
            repo.resolve() / "agents" / "skills",
            home / ".agents" / "skills",
        ])

    def test_find_skill_prefers_repo_local_over_global(self) -> None:
        module = load_check_prereqs()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            local_skill = repo / "skills" / "example" / "SKILL.md"
            global_skill = home / ".agents" / "skills" / "example" / "SKILL.md"
            local_skill.parent.mkdir(parents=True)
            global_skill.parent.mkdir(parents=True)
            local_skill.write_text("---\nname: example\ndescription: local\n---\n", encoding="utf-8")
            global_skill.write_text("---\nname: example\ndescription: global\n---\n", encoding="utf-8")

            previous_cwd = Path.cwd()
            try:
                os.chdir(repo)
                with (
                    mock.patch.object(module.Path, "home", return_value=home),
                    mock.patch.dict(module.os.environ, {}, clear=True),
                ):
                    found = module.find_skill("example", module.candidate_roots([]))
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(found, local_skill.resolve())


if __name__ == "__main__":
    unittest.main()
