from __future__ import annotations

from _helpers import *


class CandidateRegistryTests(unittest.TestCase):
    def run_delivery(
        self, envelope_path: Path, runtime_path: Path, plan_path: Path
    ) -> subprocess.CompletedProcess[str]:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["schema_version"] = 2
        plan["approved_spec_binding"] = copy.deepcopy(
            envelope["approved_spec_binding"]
        )
        write_json(plan_path, plan)
        result_path = plan_path.with_name("execution-result.json")
        write_json(result_path, current_execution_result(envelope, runtime))
        return run_script(
            "validate_delivery_plan.py",
            str(envelope_path),
            str(runtime_path),
            str(result_path),
            str(plan_path),
            "--repo-root",
            str(REPO_ROOT),
        )

    def test_delivery_rejects_incomplete_or_open_registry_v2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            envelope_path = root / "envelope.json"
            runtime_path = root / "runtime-state.json"
            plan_path = root / "delivery-plan.json"
            registry_path = root / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )
            mutations = {
                "missing-registry-path": lambda registry: registry.pop("registry_path"),
                "missing-limits": lambda registry: registry.pop("limits"),
                "unknown-root": lambda registry: registry.update({"injected": True}),
                "unknown-candidate": lambda registry: registry["candidates"][0].update(
                    {"injected": True}
                ),
            }
            for name, mutate in mutations.items():
                with self.subTest(name=name):
                    write_hardening_registry(
                        registry_path, [hardening_candidate("HC-G2PR-001-001")]
                    )
                    registry = json.loads(registry_path.read_text(encoding="utf-8"))
                    mutate(registry)
                    write_json(registry_path, registry)

                    result = self.run_delivery(envelope_path, runtime_path, plan_path)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_delivery_rejects_registry_from_old_binding_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            envelope_path = root / "envelope.json"
            runtime_path = root / "runtime-state.json"
            plan_path = root / "delivery-plan.json"
            registry_path = root / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            runtime = merged_runtime_state()
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_hardening_registry(registry_path, [])
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["approved_spec_binding"] = approved_spec_binding(sha256="a" * 64)
            write_json(registry_path, registry)
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(envelope_path, runtime_path, plan_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("AUXILIARY_ARTIFACT_BINDING_MISMATCH", result.stderr)

    def test_registry_v1_is_schema_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            envelope_path = root / "envelope.json"
            runtime_path = root / "runtime-state.json"
            plan_path = root / "delivery-plan.json"
            registry_path = root / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_hardening_registry(registry_path, [])
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["schema_version"] = 1
            registry.pop("approved_spec_binding", None)
            write_json(registry_path, registry)
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(envelope_path, runtime_path, plan_path)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_candidate_registry_schema_and_template_define_bounded_artifact(self) -> None:
        schema_path = SKILL_DIR / "assets" / "schemas" / "hardening-candidates.schema.json"
        template_path = SKILL_DIR / "assets" / "templates" / "hardening-candidates.json"

        self.assertTrue(schema_path.exists(), schema_path)
        self.assertTrue(template_path.exists(), template_path)

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        template = json.loads(template_path.read_text(encoding="utf-8"))

        self.assertEqual(template["schema_version"], 2)
        self.assertEqual(template["approved_spec_binding"]["path"], "knowledge/wiki/syntheses/<epic-id>-input-packet.json")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
        self.assertIn("approved_spec_binding", schema["required"])

        self.assertEqual(
            template["registry_path"],
            "<runtime-root>/decisions/hardening-candidates.json",
        )
        self.assertEqual(template["limits"]["hardening_candidate_summary_words_default"], 80)
        self.assertEqual(template["limits"]["hardening_candidates_per_issue_default"], 5)

        root_required = set(schema["required"])
        self.assertGreaterEqual(
            root_required,
            {"schema_version", "epic_id", "registry_path", "limits", "candidates"},
        )

        candidate_schema = schema["properties"]["candidates"]["items"]
        self.assertGreaterEqual(
            set(candidate_schema["required"]),
            {
                "candidate_id",
                "source_issue",
                "classification",
                "summary",
                "risk",
                "estimated_scope",
                "decision",
                "implementation_issue",
            },
        )
        self.assertEqual(
            candidate_schema["properties"]["classification"]["enum"],
            ["hardening_candidate", "safety_escalation", "classification_needed"],
        )
        self.assertEqual(
            candidate_schema["properties"]["decision"]["enum"],
            [
                "pending_decision",
                "approved_for_current_pr",
                "deferred_follow_up",
                "declined",
                "risk_accepted",
                "implemented",
            ],
        )

        fixture_candidate = template["candidates"][0]
        for field in candidate_schema["required"]:
            self.assertIn(field, fixture_candidate)
        self.assertLessEqual(len(re.findall(r"\S+", fixture_candidate["summary"])), 80)
        self.assertFalse(
            (SKILL_DIR / "decisions" / "hardening-candidates.json").exists(),
            "worker branch must not track a runtime candidate registry artifact",
        )

    def test_references_define_candidate_registry_carry_forward_and_wait_scope(self) -> None:
        runtime_text = (SKILL_DIR / "references" / "runtime-state.md").read_text(
            encoding="utf-8"
        )
        human_wait_text = (SKILL_DIR / "references" / "human-wait.md").read_text(
            encoding="utf-8"
        )
        compaction_text = (SKILL_DIR / "references" / "context-compaction.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "<runtime-root>/decisions/hardening-candidates.json",
            "coordinator-owned",
            "candidate_id",
            "source_issue",
            "classification",
            "summary",
            "risk",
            "estimated_scope",
            "decision",
            "implementation_issue",
            "80 words",
            "5 件",
            "worker branch",
        ):
            self.assertIn(required, runtime_text)

        for required in (
            "safety_escalation",
            "classification_needed",
            "human_request_opened",
            "smallest affected scope",
            "issue",
            "descendants",
            "resource",
        ):
            self.assertIn(required, human_wait_text)

        for required in (
            "Pending hardening decisions: N",
            "<runtime-root>/decisions/hardening-candidates.json",
            "candidate full text",
            "path",
        ):
            self.assertIn(required, compaction_text)
