from __future__ import annotations

from _helpers import *


REVIEW_GATE = SKILL_DIR / "references" / "review-gate.md"


class ReviewGateTests(unittest.TestCase):
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
