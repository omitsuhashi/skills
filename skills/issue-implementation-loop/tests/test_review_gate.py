from __future__ import annotations

from _helpers import *


REVIEW_GATE = SKILL_DIR / "references" / "review-gate.md"


class ReviewGateTests(unittest.TestCase):
    def test_worker_report_reference_requires_fresh_envelope_and_repo_root(self) -> None:
        text = (SKILL_DIR / "references" / "worker-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("--envelope <execution-envelope.json>", text)
        self.assertIn("--repo-root <repo-root>", text)
        self.assertIn("fresh envelope -> packet -> spec", text)

    def result_artifacts(
        self, root: Path
    ) -> tuple[Path, dict, Path, dict, Path, dict]:
        repo, binding, _ = create_binding_repo(root)
        envelope = binding_envelope(repo, binding)
        runtime = {
            "schema_version": 2,
            "approved_spec_binding": copy.deepcopy(binding),
            "epic_id": envelope["epic_id"],
            "envelope_revision": envelope["revision"],
            "issues": {
                "ASBC-002": {
                    "status": "PR_READY",
                    "branch": envelope["work_items"]["ASBC-002"]["branch"],
                    "worktree": envelope["work_items"]["ASBC-002"]["worktree_path"],
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "review": {"status": "approved", "range": REVIEW_RANGE},
                }
            },
            "human_requests": [],
        }
        result = current_execution_result(envelope, runtime)
        envelope_path = repo / "execution-envelope.json"
        runtime_path = repo / "runtime-state.json"
        result_path = repo / "execution-result.json"
        write_json(envelope_path, envelope)
        write_json(runtime_path, runtime)
        write_json(result_path, result)
        return repo, envelope, runtime_path, runtime, result_path, result

    def validate_result(
        self, repo: Path, runtime_path: Path, result_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return run_script(
            "validate_execution_result.py",
            str(repo / "execution-envelope.json"),
            str(runtime_path),
            str(result_path),
            "--repo-root",
            str(repo),
            "--json",
        )

    def test_review_report_intake_freshly_verifies_envelope_packet_spec_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding, task_kind="review")
            packet_path = repo / "reviewer-packet.json"
            report_path = repo / "reviewer-report.json"
            runtime_path = repo / "runtime-state.json"
            envelope_path = repo / "execution-envelope.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))
            (repo / "knowledge/wiki/syntheses/spec.md").write_text(
                "stale before review intake\n", encoding="utf-8"
            )

            intake = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--envelope",
                str(envelope_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(intake.returncode, 1)
            self.assertEqual(
                json.loads(intake.stdout)["errors"], ["SPEC_DIGEST_MISMATCH"]
            )

    def test_review_report_intake_rejects_stale_dispatch_source_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding, task_kind="review")
            packet["source_revision"]["execution_envelope"]["sha256"] = "a" * 64
            packet_path = repo / "reviewer-packet.json"
            report_path = repo / "reviewer-report.json"
            runtime_path = repo / "runtime-state.json"
            envelope_path = repo / "execution-envelope.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))

            intake = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--envelope",
                str(envelope_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(intake.returncode, 1)
            self.assertTrue(json.loads(intake.stdout)["errors"])

    def test_review_report_intake_requires_active_source_snapshot_equality(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding, task_kind="review")
            envelope_path = repo / "execution-envelope.json"
            runtime_path = repo / "runtime-state.json"
            alternate_envelope_path = repo / "alternate-envelope.json"
            alternate_runtime_path = repo / "alternate-runtime.json"
            alternate_envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            alternate_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            alternate_envelope["revision"] = 2
            alternate_runtime["envelope_revision"] = 2
            write_json(alternate_envelope_path, alternate_envelope)
            write_json(alternate_runtime_path, alternate_runtime)
            packet["source_revision"]["execution_envelope"] = {
                "path": str(alternate_envelope_path),
                "revision": 2,
                "sha256": hashlib.sha256(alternate_envelope_path.read_bytes()).hexdigest(),
            }
            packet["source_revision"]["runtime_state"] = {
                "path": str(alternate_runtime_path),
                "envelope_revision": 2,
                "sha256": hashlib.sha256(alternate_runtime_path.read_bytes()).hexdigest(),
            }
            packet_path = repo / "reviewer-packet.json"
            report_path = repo / "reviewer-report.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))

            intake = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--envelope",
                str(envelope_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(intake.returncode, 1)
            self.assertIn("BINDING_MISMATCH", json.loads(intake.stdout)["errors"])

    def test_worker_report_malformed_or_unreadable_json_returns_stable_error(self) -> None:
        for artifact in ("report", "packet", "runtime", "envelope"):
            for failure in ("malformed", "unreadable"):
                with self.subTest(artifact=artifact, failure=failure), tempfile.TemporaryDirectory() as tmp:
                    repo, binding, _ = create_binding_repo(Path(tmp))
                    packet = current_worker_packet(repo, binding, task_kind="review")
                    paths = {
                        "report": repo / "reviewer-report.json",
                        "packet": repo / "reviewer-packet.json",
                        "runtime": repo / "runtime-state.json",
                        "envelope": repo / "execution-envelope.json",
                    }
                    write_json(paths["report"], current_worker_report(repo, binding, packet))
                    write_json(paths["packet"], packet)
                    target = paths[artifact]
                    if failure == "malformed":
                        target.write_text("{not-json", encoding="utf-8")
                    else:
                        target = repo / f"missing-{artifact}.json"
                        paths[artifact] = target

                    checked = run_script(
                        "validate_worker_report.py",
                        str(paths["report"]),
                        "--dispatch-packet",
                        str(paths["packet"]),
                        "--runtime-state",
                        str(paths["runtime"]),
                        "--envelope",
                        str(paths["envelope"]),
                        "--repo-root",
                        str(repo),
                        "--json",
                    )

                    self.assertEqual(checked.returncode, 1)
                    self.assertEqual(
                        json.loads(checked.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
                    )
                    self.assertEqual(checked.stderr, "")

    def test_execution_result_v2_closes_epic_base_and_delivery_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = {
                "unknown-epic-base": lambda result: result["epic_base"].update(
                    {"injected": True}
                ),
                "wrong-epic-branch": lambda result: result["epic_base"].update(
                    {"branch": "codex/other/epic-base"}
                ),
                "boolean-current-sha": lambda result: result["epic_base"].update(
                    {"current_sha": True}
                ),
                "non-boolean-exists": lambda result: result["epic_base"].update(
                    {"branch_exists": 1}
                ),
                "empty-candidates": lambda result: result.update(
                    {"delivery_candidates": []}
                ),
                "duplicate-candidates": lambda result: result.update(
                    {"delivery_candidates": ["ASBC-002", "ASBC-002"]}
                ),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, _, runtime_path, _, result_path, result = self.result_artifacts(
                        case_root
                    )
                    mutate(result)
                    write_json(result_path, result)
                    checked = self.validate_result(repo, runtime_path, result_path)
                    self.assertEqual(checked.returncode, 1)

    def test_execution_result_v2_verifies_epic_base_against_real_git_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, runtime_path, _, result_path, result = self.result_artifacts(
                Path(tmp)
            )
            original_branch = git(repo, "branch", "--show-current")
            epic_ref = "codex/approved-spec-binding/epic-base"
            git(repo, "checkout", "-q", "-b", epic_ref)
            envelope["epic_base"]["ref"] = epic_ref
            envelope["epic_base"]["branch_state"] = "active"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
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
            result["epic_base"]["branch"] = epic_ref
            write_json(repo / "execution-envelope.json", envelope)
            (repo / "epic-change.txt").write_text("advance\n", encoding="utf-8")
            git(repo, "add", "epic-change.txt")
            git(repo, "commit", "-q", "-m", "advance epic base")
            write_json(result_path, result)

            stale = self.validate_result(repo, runtime_path, result_path)

            self.assertEqual(stale.returncode, 1)
            self.assertIn("BINDING_MISMATCH", json.loads(stale.stdout)["errors"])

            result["epic_base"]["current_sha"] = git(repo, "rev-parse", epic_ref)
            result["epic_base"]["branch_exists"] = True
            write_json(result_path, result)
            current = self.validate_result(repo, runtime_path, result_path)
            self.assertEqual(current.returncode, 0, current.stderr)

            git(repo, "checkout", "-q", original_branch)
            git(repo, "branch", "-D", epic_ref)
            missing = self.validate_result(repo, runtime_path, result_path)
            self.assertEqual(missing.returncode, 1)

    def test_execution_result_v2_local_only_allows_planned_epic_base_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, runtime_path, _, result_path, result = self.result_artifacts(
                Path(tmp)
            )
            planned_ref = "codex/approved-spec-binding/planned-epic-base"
            envelope["epic_base"]["ref"] = planned_ref
            result["epic_base"].update(
                {
                    "branch": planned_ref,
                    "current_sha": "a" * 40,
                    "branch_exists": False,
                }
            )
            write_json(repo / "execution-envelope.json", envelope)
            write_json(result_path, result)

            checked = self.validate_result(repo, runtime_path, result_path)

            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertEqual(json.loads(checked.stdout)["errors"], [])

    def test_execution_result_v2_binds_registry_residual_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, runtime_path, runtime, result_path, result = self.result_artifacts(
                Path(tmp)
            )
            risk = "Deferred guard may leave the delivery boundary under-protected."
            registry_path = runtime_path.parent / "decisions" / "hardening-candidates.json"
            registry_path.parent.mkdir()
            candidate = hardening_candidate(
                "HC-ASBC-002-001", decision="deferred_follow_up"
            )
            candidate.update({"source_issue": "ASBC-002", "risk": risk})
            write_json(
                registry_path,
                {
                    "schema_version": 2,
                    "approved_spec_binding": copy.deepcopy(envelope["approved_spec_binding"]),
                    "epic_id": envelope["epic_id"],
                    "registry_path": str(registry_path),
                    "limits": {
                        "hardening_candidate_summary_words_default": 80,
                        "hardening_candidates_per_issue_default": 5,
                    },
                    "candidates": [candidate],
                },
            )

            missing = self.validate_result(repo, runtime_path, result_path)
            self.assertEqual(missing.returncode, 1)

            result["issues"]["ASBC-002"]["residual_risks"] = [risk]
            write_json(result_path, result)
            included = self.validate_result(repo, runtime_path, result_path)
            self.assertEqual(included.returncode, 0, included.stderr)

            for risks in (["  "], [risk, risk]):
                with self.subTest(risks=risks):
                    result["issues"]["ASBC-002"]["residual_risks"] = risks
                    write_json(result_path, result)
                    malformed = self.validate_result(repo, runtime_path, result_path)
                    self.assertEqual(malformed.returncode, 1)

    def test_execution_result_v2_compares_issue_and_optional_pr_fields_to_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = {
                "runtime-branch": lambda runtime, result: runtime["issues"][
                    "ASBC-002"
                ].update({"branch": "codex/other/ASBC-002-wrong"}),
                "runtime-worktree": lambda runtime, result: runtime["issues"][
                    "ASBC-002"
                ].update({"worktree": "/tmp/wrong"}),
                "pr-value": lambda runtime, result: (
                    runtime["issues"]["ASBC-002"].update(
                        {"pr": "https://github.com/org/repo/pull/2"}
                    ),
                    result["issues"]["ASBC-002"].update(
                        {"pr": "https://github.com/org/repo/pull/3"}
                    ),
                ),
                "pr-opened-type": lambda runtime, result: (
                    runtime["issues"]["ASBC-002"].update({"pr_opened": True}),
                    result["issues"]["ASBC-002"].update({"pr_opened": 1}),
                ),
                "missing-runtime-pr-merged": lambda runtime, result: runtime[
                    "issues"
                ]["ASBC-002"].update({"pr_merged": True}),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, _, runtime_path, runtime, result_path, result = (
                        self.result_artifacts(case_root)
                    )
                    mutate(runtime, result)
                    write_json(runtime_path, runtime)
                    write_json(result_path, result)
                    checked = self.validate_result(repo, runtime_path, result_path)
                    self.assertEqual(checked.returncode, 1)

    def test_execution_result_malformed_json_returns_stable_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, runtime_path, _, result_path, _ = self.result_artifacts(Path(tmp))
            result_path.write_text("{not-json", encoding="utf-8")

            checked = self.validate_result(repo, runtime_path, result_path)

            self.assertEqual(checked.returncode, 1)
            self.assertTrue(checked.stdout, checked.stderr)
            self.assertEqual(
                json.loads(checked.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )
            self.assertEqual(checked.stderr, "")

    def test_asb_04_execution_result_v2_accepts_active_binding_and_review_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope = binding_envelope(repo, binding)
            envelope_path = repo / "execution-envelope.json"
            runtime_path = repo / "runtime-state.json"
            result_path = repo / "execution-result.json"
            runtime = {
                "schema_version": 2,
                "approved_spec_binding": copy.deepcopy(binding),
                "epic_id": envelope["epic_id"],
                "envelope_revision": envelope["revision"],
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "review": {"status": "approved", "range": REVIEW_RANGE},
                    }
                },
                "human_requests": [],
            }
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_json(result_path, current_execution_result(envelope, runtime))

            completed = run_script(
                "validate_execution_result.py",
                str(envelope_path),
                str(runtime_path),
                str(result_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["errors"], [])

    def test_asb_14_completion_rechecks_current_spec_before_terminal_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope = binding_envelope(repo, binding)
            envelope_path = repo / "execution-envelope.json"
            runtime_path = repo / "runtime-state.json"
            result_path = repo / "execution-result.json"
            runtime = {
                "schema_version": 2,
                "approved_spec_binding": copy.deepcopy(binding),
                "epic_id": envelope["epic_id"],
                "envelope_revision": envelope["revision"],
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "review": {"status": "approved", "range": REVIEW_RANGE},
                    }
                },
                "human_requests": [],
            }
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_json(result_path, current_execution_result(envelope, runtime))
            (repo / "knowledge/wiki/syntheses/spec.md").write_text(
                "drift after review\n", encoding="utf-8"
            )

            completed = run_script(
                "validate_execution_result.py",
                str(envelope_path),
                str(runtime_path),
                str(result_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(
                json.loads(completed.stdout)["errors"], ["SPEC_DIGEST_MISMATCH"]
            )

    def test_asb_22_completion_rejects_result_binding_or_review_range_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope = binding_envelope(repo, binding)
            envelope_path = repo / "execution-envelope.json"
            runtime_path = repo / "runtime-state.json"
            runtime = {
                "schema_version": 2,
                "approved_spec_binding": copy.deepcopy(binding),
                "epic_id": envelope["epic_id"],
                "envelope_revision": envelope["revision"],
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "review": {"status": "approved", "range": REVIEW_RANGE},
                    }
                },
                "human_requests": [],
            }
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            cases = {
                "binding": lambda result: result["approved_spec_binding"].update(
                    {"sha256": "b" * 64}
                ),
                "range": lambda result: result["issues"]["ASBC-002"][
                    "implementation_review"
                ].update({"range": f"{BASE_SHA}..{'a' * 40}"}),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    result_path = repo / f"execution-result-{name}.json"
                    result = current_execution_result(envelope, runtime)
                    mutate(result)
                    write_json(result_path, result)
                    completed = run_script(
                        "validate_execution_result.py",
                        str(envelope_path),
                        str(runtime_path),
                        str(result_path),
                        "--repo-root",
                        str(repo),
                        "--json",
                    )
                    self.assertEqual(completed.returncode, 1)
                    self.assertIn(
                        "BINDING_MISMATCH",
                        json.loads(completed.stdout)["errors"],
                    )

    def test_execution_result_v1_is_unsupported(self) -> None:
        template = json.loads(
            (SKILL_DIR / "assets/templates/execution-result.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(template["schema_version"], 2)
        self.assertIn("approved_spec_binding", template)

        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope = binding_envelope(repo, binding)
            envelope_path = repo / "execution-envelope.json"
            runtime_path = repo / "runtime-state.json"
            result_path = repo / "execution-result-v1.json"
            runtime = {
                "schema_version": 2,
                "approved_spec_binding": copy.deepcopy(binding),
                "epic_id": envelope["epic_id"],
                "envelope_revision": envelope["revision"],
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "review": {"status": "approved", "range": REVIEW_RANGE},
                    }
                },
                "human_requests": [],
            }
            result = current_execution_result(envelope, runtime)
            result["schema_version"] = 1
            result.pop("approved_spec_binding")
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            write_json(result_path, result)

            rejected = run_script(
                "validate_execution_result.py",
                str(envelope_path),
                str(runtime_path),
                str(result_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(
                json.loads(rejected.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )

    def test_review_gate_defines_finding_taxonomy_and_fix_loop_rules(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for classification in (
            "`intent_gap`",
            "`implementation_regression`",
            "`hardening_candidate`",
            "`safety_escalation`",
            "`classification_needed`",
        ):
            self.assertIn(classification, text)

        self.assertIn("intent_gap / implementation_regression", text)
        self.assertIn("blocking finding", text)
        self.assertIn("existing fix loop", text)
        self.assertIn("hardening_candidate is not a fix request", text)
        self.assertIn("classification_needed stops the issue", text)
        self.assertIn("coordinator or human decision", text)

    def test_review_packet_is_paths_first_committed_range_with_budget(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "paths-first",
            "`BASE_SHA` / `HEAD_SHA`",
            "committed range review",
            "Current PR delivery risk",
            "default 600 words",
            "hard 900 words",
            "Do not paste full spec",
            "Do not paste full ledger",
            "active `approved_spec_binding`",
            "fresh envelope -> packet -> spec verification",
            "binding and `BASE_SHA..HEAD_SHA`",
        ):
            self.assertIn(required, text)

    def test_review_packet_excludes_future_only_hardening_by_default(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        for required in (
            "Automatic review checks",
            "Issue intent fit",
            "Implementation regression",
            "Current PR delivery risk",
            "Non-automatic handling",
            "classification_needed is not an automatic review viewpoint",
            "Hardening is not an automatic review viewpoint",
            "Future-only hardening suggestions are out of review scope by default",
            "Do not ask the reviewer to enumerate general hardening ideas",
            "explicitly requested by the human",
            "do not auto-fix",
        ):
            self.assertIn(required, text)

        self.assertNotIn("Hardening candidate lane", text)
        self.assertNotIn("optional lane", text)
        self.assertNotIn("Review approved issue, spec, acceptance, non-goals, write scope, and verification evidence. Classify gaps as `intent_gap`, `implementation_regression`, or `classification_needed`.", text)

    def test_requesting_code_review_is_primary_reviewer_contract(self) -> None:
        text = REVIEW_GATE.read_text(encoding="utf-8")

        self.assertIn("superpowers:requesting-code-review", text)
        self.assertIn("first candidate", text)
        self.assertIn("approved equivalent/manual fallback", text)
