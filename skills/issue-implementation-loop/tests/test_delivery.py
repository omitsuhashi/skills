from __future__ import annotations

from _helpers import *


class DeliveryTests(unittest.TestCase):
    def call_delivery(
        self,
        repo: Path,
        runtime_path: Path,
        result_path: Path,
        plan_path: Path,
    ) -> subprocess.CompletedProcess[str]:
        return run_script(
            "validate_delivery_plan.py",
            str(repo / "execution-envelope.json"),
            str(runtime_path),
            str(result_path),
            str(plan_path),
            "--repo-root",
            str(repo),
            "--json",
        )

    def test_delivery_plan_v2_is_closed_per_action(self) -> None:
        final_cases = {
            "issue-field": lambda plan: plan.update({"issue": "ASBC-002"}),
            "ready-field": lambda plan: plan.update({"ready_for_review": False}),
            "draft-not-bool": lambda plan: plan.update({"draft": 1}),
            "scope-not-list": lambda plan: plan.update({"issue_scope": "ASBC-002"}),
            "missing-draft": lambda plan: plan.pop("draft"),
        }
        issue_cases = {
            "draft-field": lambda plan: plan.update({"draft": True}),
            "ready-field": lambda plan: plan.update({"ready_for_review": False}),
            "scope-field": lambda plan: plan.update({"issue_scope": ["ASBC-002"]}),
            "missing-issue": lambda plan: plan.pop("issue"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, mutate in final_cases.items():
                with self.subTest(action="final_pr", name=name):
                    case_root = root / f"final-{name}"
                    case_root.mkdir()
                    repo, envelope, runtime_path, _, result_path, _, plan_path, plan = (
                        self.binding_delivery_artifacts(case_root)
                    )
                    mutate(plan)
                    write_json(plan_path, plan)
                    checked = self.call_delivery(
                        repo, runtime_path, result_path, plan_path
                    )
                    self.assertEqual(checked.returncode, 1)

            for name, mutate in issue_cases.items():
                with self.subTest(action="issue_pr", name=name):
                    case_root = root / f"issue-{name}"
                    case_root.mkdir()
                    repo, envelope, runtime_path, _, result_path, _, plan_path, _ = (
                        self.binding_delivery_artifacts(case_root)
                    )
                    plan = current_delivery_plan(
                        envelope,
                        action="issue_pr",
                        issue="ASBC-002",
                        head=envelope["work_items"]["ASBC-002"]["branch"],
                        base=envelope["epic_base"]["ref"],
                    )
                    mutate(plan)
                    write_json(plan_path, plan)
                    checked = self.call_delivery(
                        repo, runtime_path, result_path, plan_path
                    )
                    self.assertEqual(checked.returncode, 1)

    def test_final_plan_scope_is_optional_full_candidate_shorthand_or_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, runtime_path, runtime, result_path, _, plan_path, _ = (
                self.binding_delivery_artifacts(Path(tmp))
            )
            envelope["work_items"]["ASBC-003"] = copy.deepcopy(
                envelope["work_items"]["ASBC-002"]
            )
            envelope["work_items"]["ASBC-003"].update(
                {
                    "branch": "codex/approved-spec-binding/ASBC-003-follow-up",
                    "worktree_path": str(repo / "ASBC-003"),
                }
            )
            binding, _ = bind_envelope_fixture_repo(repo, envelope)
            runtime["approved_spec_binding"] = copy.deepcopy(binding)
            runtime["issues"]["ASBC-003"] = copy.deepcopy(
                runtime["issues"]["ASBC-002"]
            )
            result = current_execution_result(envelope, runtime)
            write_json(repo / "execution-envelope.json", envelope)
            write_json(runtime_path, runtime)
            write_json(result_path, result)

            omitted = current_delivery_plan(
                envelope,
                head=envelope["epic_base"]["ref"],
                base="main",
                draft=True,
            )
            write_json(plan_path, omitted)
            shorthand = self.call_delivery(repo, runtime_path, result_path, plan_path)
            self.assertEqual(shorthand.returncode, 0, shorthand.stderr)

            for scope in (["ASBC-002"], ["ASBC-002", "ASBC-002"]):
                with self.subTest(scope=scope):
                    subset = copy.deepcopy(omitted)
                    subset["issue_scope"] = scope
                    write_json(plan_path, subset)
                    rejected = self.call_delivery(
                        repo, runtime_path, result_path, plan_path
                    )
                    self.assertEqual(rejected.returncode, 1)

            exact = copy.deepcopy(omitted)
            exact["issue_scope"] = ["ASBC-003", "ASBC-002"]
            write_json(plan_path, exact)
            accepted = self.call_delivery(repo, runtime_path, result_path, plan_path)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            runtime["issues"]["ASBC-003"]["pr_merged"] = False
            result = current_execution_result(envelope, runtime)
            write_json(runtime_path, runtime)
            write_json(result_path, result)
            write_json(plan_path, omitted)
            not_integrated = self.call_delivery(
                repo, runtime_path, result_path, plan_path
            )
            self.assertEqual(not_integrated.returncode, 1)
            self.assertIn("issues.ASBC-003.pr_merged", not_integrated.stdout)

    def test_delivery_malformed_result_or_plan_returns_stable_error(self) -> None:
        for artifact in ("result", "plan"):
            with self.subTest(artifact=artifact), tempfile.TemporaryDirectory() as tmp:
                repo, _, runtime_path, _, result_path, _, plan_path, _ = (
                    self.binding_delivery_artifacts(Path(tmp))
                )
                target = result_path if artifact == "result" else plan_path
                target.write_text("{not-json", encoding="utf-8")

                checked = self.call_delivery(repo, runtime_path, result_path, plan_path)

                self.assertEqual(checked.returncode, 1)
                self.assertTrue(checked.stdout, checked.stderr)
                self.assertEqual(
                    json.loads(checked.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
                )
                self.assertEqual(checked.stderr, "")

    def run_delivery(self, script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
        envelope_path = Path(args[0])
        runtime_path = Path(args[1])
        plan_path = Path(args[2])
        remaining = args[3:]
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        validation_repo = create_delivery_validation_repo(
            plan_path.parent, envelope, runtime
        )
        write_json(envelope_path, envelope)
        write_json(runtime_path, runtime)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan.setdefault("schema_version", 2)
        plan.setdefault(
            "approved_spec_binding", copy.deepcopy(envelope["approved_spec_binding"])
        )
        if plan.get("action") == "final_pr":
            plan.setdefault("draft", True)
            plan.setdefault("issue_scope", list(envelope["work_items"]))
        write_json(plan_path, plan)
        result_path = plan_path.with_name(plan_path.stem + "-execution-result.json")
        execution_result = current_execution_result(envelope, runtime)
        add_registry_residual_risks(
            execution_result,
            runtime_path.parent / "decisions" / "hardening-candidates.json",
        )
        write_json(result_path, execution_result)
        return run_script(
            script_name,
            str(envelope_path),
            str(runtime_path),
            str(result_path),
            str(plan_path),
            "--repo-root",
            str(validation_repo),
            *remaining,
        )

    def binding_delivery_artifacts(
        self, root: Path
    ) -> tuple[Path, dict, Path, dict, Path, dict, Path, dict]:
        repo, binding, _ = create_binding_repo(root)
        envelope = binding_envelope(repo, binding)
        envelope["epic_base"].update(
            {
                "ref": "codex/approved-spec-binding/epic-base",
                "branch_state": "active",
            }
        )
        git(
            repo,
            "branch",
            envelope["epic_base"]["ref"],
            envelope["epic_base"]["sha"],
        )
        envelope["remote_write_policy"] = {
            "mode": "batch_issue_prs",
            "approved_actions": [
                "final_pr_push_head",
                "final_pr_create_draft",
            ],
            "issue_prs": {
                "base": "epic_base.ref",
                "merge": "agent_default_with_human_escalation",
            },
            "final_pr": {
                "head": "epic_base.ref",
                "base": "main",
                "merge": "human_only",
            },
        }
        binding, _ = bind_envelope_fixture_repo(repo, envelope)
        runtime = {
            "schema_version": 2,
            "approved_spec_binding": copy.deepcopy(binding),
            "epic_id": envelope["epic_id"],
            "envelope_revision": envelope["revision"],
            "issues": {
                "ASBC-002": {
                    "status": "COMPLETE",
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "review": {"status": "approved", "range": REVIEW_RANGE},
                    "pr": "https://github.com/org/repo/pull/2",
                    "pr_opened": True,
                    "pr_merged": True,
                    "merge_commit": HEAD_SHA,
                }
            },
            "human_requests": [],
        }
        result = current_execution_result(envelope, runtime)
        plan = current_delivery_plan(
            envelope,
            head=envelope["epic_base"]["ref"],
            base="main",
            draft=True,
            issue_scope=["ASBC-002"],
        )
        envelope_path = repo / "execution-envelope.json"
        runtime_path = repo / "runtime-state.json"
        result_path = repo / "execution-result.json"
        plan_path = repo / "delivery-plan.json"
        write_json(envelope_path, envelope)
        write_json(runtime_path, runtime)
        write_json(result_path, result)
        write_json(plan_path, plan)
        return (
            repo,
            envelope,
            runtime_path,
            runtime,
            result_path,
            result,
            plan_path,
            plan,
        )

    def test_asb_04_delivery_v2_accepts_active_binding_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, runtime_path, _, result_path, _, plan_path, _ = (
                self.binding_delivery_artifacts(Path(tmp))
            )

            delivered = run_script(
                "validate_delivery_plan.py",
                str(repo / "execution-envelope.json"),
                str(runtime_path),
                str(result_path),
                str(plan_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(delivered.returncode, 0, delivered.stderr)
            self.assertEqual(json.loads(delivered.stdout)["errors"], [])

    def test_asb_15_delivery_rechecks_spec_after_terminal_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, runtime_path, _, result_path, _, plan_path, _ = (
                self.binding_delivery_artifacts(Path(tmp))
            )
            (repo / FIXTURE_SPEC_PATH).write_text(
                "drift before delivery\n", encoding="utf-8"
            )

            delivered = run_script(
                "validate_delivery_plan.py",
                str(repo / "execution-envelope.json"),
                str(runtime_path),
                str(result_path),
                str(plan_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(delivered.returncode, 1)
            self.assertEqual(
                json.loads(delivered.stdout)["errors"], ["SPEC_DIGEST_MISMATCH"]
            )

    def test_asb_22_delivery_rejects_stale_execution_result_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, runtime_path, _, result_path, result, plan_path, _ = (
                self.binding_delivery_artifacts(Path(tmp))
            )
            result["approved_spec_binding"]["sha256"] = "b" * 64
            write_json(result_path, result)

            delivered = run_script(
                "validate_delivery_plan.py",
                str(repo / "execution-envelope.json"),
                str(runtime_path),
                str(result_path),
                str(plan_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(delivered.returncode, 1)
            self.assertEqual(
                json.loads(delivered.stdout)["errors"], ["BINDING_MISMATCH"]
            )

    def test_delivery_plan_v1_is_unsupported(self) -> None:
        template = json.loads(
            (SKILL_DIR / "assets/templates/delivery-plan.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(template.get("schema_version"), 2)
        self.assertIn("approved_spec_binding", template)

        with tempfile.TemporaryDirectory() as tmp:
            repo, _, runtime_path, _, result_path, _, plan_path, plan = (
                self.binding_delivery_artifacts(Path(tmp))
            )
            plan.pop("schema_version")
            plan.pop("approved_spec_binding")
            write_json(plan_path, plan)
            rejected = run_script(
                "validate_delivery_plan.py",
                str(repo / "execution-envelope.json"),
                str(runtime_path),
                str(result_path),
                str(plan_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(
                json.loads(rejected.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )

    def test_remote_delivery_docs_define_final_pr_auto_create_contract(self) -> None:
        text = (SKILL_DIR / "references" / "remote-delivery.md").read_text(encoding="utf-8")
        envelope_text = (SKILL_DIR / "references" / "execution-envelope.md").read_text(encoding="utf-8")
        template = json.loads((SKILL_DIR / "assets" / "templates" / "delivery-plan.json").read_text(encoding="utf-8"))

        for required in (
            "final_pr_push_head",
            "final_pr_create_draft",
            "delivery plan validation",
            "hardening-candidates.json",
            "pending_decision",
            "safety_escalation",
            "approved_for_current_pr",
            "pending_hardening_candidates",
            "ok: true",
            "draft",
            "ledger",
            "runtime state",
            "completion report",
            "Execution Result v2",
            "Delivery Plan v2",
            "fresh envelope -> packet -> spec",
            "execution result, delivery plan, runtime state, reviews, and candidate registry",
        ):
            self.assertIn(required, text)
        for required in (
            "ready-for-review",
            "final PR merge",
            "force push",
            "human action",
        ):
            self.assertIn(required, text)
        self.assertIn("final_pr_push_head", envelope_text)
        self.assertIn("final_pr_create_draft", envelope_text)
        self.assertIs(template["draft"], True)

    def test_validate_delivery_plan_rejects_final_pr_from_issue_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/G2PR-003-c",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.head must be codex/issue-implementation-loop/epic-base", result.stderr)
            self.assertIn("issue branch", result.stderr)

    def test_validate_delivery_plan_requires_issue_pr_merges_before_final_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, merged_runtime_state(missing_merge="G2PR-003"))
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("issues.G2PR-003.pr_merged must be true before final PR", result.stderr)

    def test_validate_delivery_plan_json_allows_draft_final_pr_with_pending_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_hardening_registry(
                registry_path,
                [hardening_candidate("HC-G2PR-001-001", decision="pending_decision")],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["errors"], [])
            self.assertEqual(
                [candidate["candidate_id"] for candidate in payload["pending_hardening_candidates"]],
                ["HC-G2PR-001-001"],
            )
            self.assertIn("ready-for-review", payload["decision_gate_blockers"][0])
            self.assertIn("pending_decision", payload["decision_gate_blockers"][0])

    def test_validate_delivery_plan_reports_approved_candidate_until_implementation_issue_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            runtime = merged_runtime_state()
            runtime["issues"]["G2PR-004"] = {
                "status": "IMPLEMENTED",
                "review": {"status": "pending"},
            }
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_hardening_registry(
                registry_path,
                [
                    hardening_candidate(
                        "HC-G2PR-001-002",
                        decision="approved_for_current_pr",
                        implementation_issue="G2PR-004",
                    )
                ],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["errors"], [])
            self.assertIn("approved_for_current_pr", payload["decision_gate_blockers"][0])
            self.assertIn("G2PR-004", payload["decision_gate_blockers"][0])

    def test_validate_delivery_plan_reports_safety_escalation_declined_or_deferred(self) -> None:
        for decision in ("declined", "deferred_follow_up"):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as tmp:
                envelope_path = Path(tmp) / "envelope.json"
                runtime_path = Path(tmp) / "runtime-state.json"
                plan_path = Path(tmp) / "delivery-plan.json"
                registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
                envelope = batch_issue_prs_envelope()
                envelope["remote_write_policy"]["approved_actions"] = [
                    "final_pr_push_head",
                    "final_pr_create_draft",
                ]
                write_json(envelope_path, envelope)
                write_json(runtime_path, merged_runtime_state())
                write_hardening_registry(
                    registry_path,
                    [
                        hardening_candidate(
                            f"HC-G2PR-001-{decision}",
                            classification="safety_escalation",
                            decision=decision,
                        )
                    ],
                )
                write_json(
                    plan_path,
                    {
                        "action": "final_pr",
                        "head": "codex/issue-implementation-loop/epic-base",
                        "base": "main",
                        "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                    },
                )

                result = self.run_delivery(
                    "validate_delivery_plan.py",
                    str(envelope_path),
                    str(runtime_path),
                    str(plan_path),
                    "--json",
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["errors"], [])
                self.assertIn("unresolved safety_escalation", payload["decision_gate_blockers"][0])
                self.assertEqual(
                    [candidate["decision"] for candidate in payload["pending_hardening_candidates"]],
                    [decision],
                )

    def test_validate_delivery_plan_allows_resolved_candidates_and_reports_residual_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime-state.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            registry_path = Path(tmp) / "decisions" / "hardening-candidates.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_hardening_registry(
                registry_path,
                [
                    hardening_candidate("HC-G2PR-001-003", decision="deferred_follow_up"),
                    hardening_candidate("HC-G2PR-001-004", decision="declined"),
                    hardening_candidate(
                        "HC-G2PR-001-005",
                        classification="safety_escalation",
                        decision="risk_accepted",
                    ),
                ],
            )
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["pending_hardening_candidates"], [])
            self.assertEqual(
                [risk["candidate_id"] for risk in payload["residual_risks"]],
                ["HC-G2PR-001-003", "HC-G2PR-001-004", "HC-G2PR-001-005"],
            )

    def test_validate_delivery_plan_requires_approved_final_pr_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            write_json(envelope_path, batch_issue_prs_envelope())
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

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote_write_policy.approved_actions must include final_pr_push_head", result.stderr)
            self.assertIn("remote_write_policy.approved_actions must include final_pr_create_draft", result.stderr)

    def test_validate_delivery_plan_rejects_ready_final_pr_creation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
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
                    "draft": False,
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.draft must be true; ready-for-review is a separate human action", result.stderr)

    def test_validate_delivery_plan_rejects_runtime_state_from_different_epic_or_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            runtime = merged_runtime_state()
            runtime["epic_id"] = "other-epic"
            runtime["envelope_revision"] = 99
            write_json(envelope_path, batch_issue_prs_envelope())
            write_json(runtime_path, runtime)
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                    "issue_scope": ["G2PR-001", "G2PR-002", "G2PR-003"],
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("runtime_state.epic_id must match envelope.epic_id", result.stderr)
            self.assertIn("runtime_state.envelope_revision must match envelope.revision", result.stderr)

    def test_validate_delivery_plan_requires_active_epic_base_for_final_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for branch_state in ("reserved", "create_on_run", "missing"):
                envelope_path = Path(tmp) / f"{branch_state}-envelope.json"
                runtime_path = Path(tmp) / f"{branch_state}-runtime.json"
                plan_path = Path(tmp) / f"{branch_state}-delivery-plan.json"
                envelope = batch_issue_prs_envelope()
                envelope["epic_base"]["branch_state"] = branch_state
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

                result = self.run_delivery(
                    "validate_delivery_plan.py",
                    str(envelope_path),
                    str(runtime_path),
                    str(plan_path),
                )

                self.assertNotEqual(result.returncode, 0, branch_state)
                self.assertIn("epic_base.branch_state must be active before final PR", result.stderr)

    def test_validate_delivery_plan_rejects_issue_pr_when_envelope_branch_is_not_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["work_items"]["G2PR-001"]["branch"] = "feature/issue-implementation-loop/G2PR-001-a"
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state())
            write_json(
                plan_path,
                {
                    "action": "issue_pr",
                    "issue": "G2PR-001",
                    "head": "feature/issue-implementation-loop/G2PR-001-a",
                    "base": "codex/issue-implementation-loop/epic-base",
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("work_items.G2PR-001.branch must match codex/issue-implementation-loop/G2PR-001-<slug>", result.stderr)

    def test_validate_delivery_plan_accepts_final_pr_from_epic_base_after_issue_pr_merges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
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

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DELIVERY PLAN OK", result.stdout)

    def test_validate_delivery_plan_defaults_final_pr_scope_to_all_work_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            plan_path = Path(tmp) / "delivery-plan.json"
            envelope = batch_issue_prs_envelope()
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            write_json(envelope_path, envelope)
            write_json(runtime_path, merged_runtime_state(missing_merge="G2PR-003"))
            write_json(
                plan_path,
                {
                    "action": "final_pr",
                    "head": "codex/issue-implementation-loop/epic-base",
                    "base": "main",
                },
            )

            result = self.run_delivery(
                "validate_delivery_plan.py",
                str(envelope_path),
                str(runtime_path),
                str(plan_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("issues.G2PR-003.pr_merged must be true before final PR", result.stderr)
