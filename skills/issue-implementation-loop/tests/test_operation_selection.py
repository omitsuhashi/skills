from __future__ import annotations

from _helpers import *


class OperationSelectionTests(unittest.TestCase):
    def assert_diagnostic_status_and_blocked_mode(
        self,
        *,
        envelope_path: Path,
        runtime_path: Path,
        requested_mode: str,
    ) -> None:
        status = self.run_selector(
            envelope_path=envelope_path,
            runtime_path=runtime_path,
            requested_mode="status",
        )
        self.assertEqual(status["operation"], "status")
        self.assertFalse(status["binding_valid"])
        self.assertTrue(status["state_advance_blocked"])

        blocked = self.run_selector(
            envelope_path=envelope_path,
            runtime_path=runtime_path,
            requested_mode=requested_mode,
        )
        self.assertEqual(blocked["operation"], "prepare")
        self.assertFalse(blocked["binding_valid"])
        self.assertTrue(blocked["state_advance_blocked"])

    def test_invalid_envelope_reservation_and_runtime_mismatch_keep_status_diagnostic(self) -> None:
        cases = {
            "legacy-envelope": lambda envelope, runtime: envelope.update(
                {"schema_version": 3}
            ),
            "incomplete-reservation": lambda envelope, runtime: envelope[
                "work_items"
            ]["G2PR-001"].pop("worktree_path"),
            "runtime-branch-mismatch": lambda envelope, runtime: runtime["issues"].update(
                {
                    "G2PR-001": {
                        "status": "RUNNING",
                        "branch": "codex/issue-implementation-loop/G2PR-001-wrong",
                    }
                }
            ),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                envelope = base_envelope()
                runtime = current_runtime(
                    {
                        "epic_id": envelope["epic_id"],
                        "envelope_revision": envelope["revision"],
                        "issues": {},
                        "human_requests": [],
                    }
                )
                mutate(envelope, runtime)
                envelope_path = Path(tmp) / "envelope.json"
                runtime_path = Path(tmp) / "runtime.json"
                write_json(envelope_path, envelope)
                write_json(runtime_path, runtime)
                self.assert_diagnostic_status_and_blocked_mode(
                    envelope_path=envelope_path,
                    runtime_path=runtime_path,
                    requested_mode="deliver",
                )

    def test_invalid_existing_envelope_blocks_prepare_execute_and_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["schema_version"] = 3
            runtime = current_runtime(
                {
                    "epic_id": envelope["epic_id"],
                    "envelope_revision": envelope["revision"],
                    "issues": {},
                    "human_requests": [],
                }
            )
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, envelope)
            write_json(runtime_path, runtime)
            for mode in ("prepare", "execute", "resume"):
                with self.subTest(mode=mode):
                    blocked = self.run_selector(
                        envelope_path=envelope_path,
                        runtime_path=runtime_path,
                        requested_mode=mode,
                    )
                    self.assertEqual(blocked["operation"], "prepare")
                    self.assertTrue(blocked["state_advance_blocked"])

    def test_scheduler_reference_places_binding_gate_before_explicit_modes(self) -> None:
        text = (SKILL_DIR / "references" / "scheduler.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("before explicit `deliver`, `status`, or `resume` routing", text)
        self.assertIn("`binding_valid: false`", text)
        self.assertIn("`state_advance_blocked: true`", text)

    def run_selector(
        self,
        *,
        envelope_path: Path | None = None,
        runtime_path: Path | None = None,
        repo_root: Path | None = None,
        requested_mode: str = "execute",
    ) -> dict:
        if repo_root is None and envelope_path is not None and envelope_path.is_file():
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            prior_binding = copy.deepcopy(envelope.get("approved_spec_binding"))
            repo_root = envelope_path.parent
            binding, _ = bind_envelope_fixture_repo(repo_root, envelope)
            write_json(envelope_path, envelope)
            if runtime_path is not None and runtime_path.is_file():
                runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
                if runtime.get("approved_spec_binding") in (
                    prior_binding,
                    approved_spec_binding(),
                ):
                    runtime["approved_spec_binding"] = copy.deepcopy(binding)
                    for request in runtime.get("human_requests", []):
                        if isinstance(request, dict):
                            request["approved_spec_binding"] = copy.deepcopy(binding)
                    write_json(runtime_path, runtime)
        args = ["--requested-mode", requested_mode, "--json"]
        if envelope_path is not None:
            args.extend(["--envelope", str(envelope_path)])
        if runtime_path is not None:
            args.extend(["--runtime", str(runtime_path)])
        if repo_root is not None:
            args.extend(["--repo-root", str(repo_root)])
        result = run_script("select_operation.py", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_reviewable_issue_takes_priority_over_runnable_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "IMPLEMENTED"},
                        "G2PR-002": {"status": "PENDING"},
                    },
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)
            self.assertEqual(payload["operation"], "execute.review")
            self.assertEqual(payload["target_issue"], "G2PR-001")
            self.assertEqual(payload["priority"], "reviewable")
            self.assertIn("skills/issue-implementation-loop/references/review-gate.md", payload["read_set"])
            self.assertTrue(payload["word_budget_result"]["within_budget"])

    def test_status_is_diagnostic_but_deliver_is_blocked_without_binding_state(self) -> None:
        status = self.run_selector(requested_mode="status")
        self.assertEqual(status["operation"], "status")
        self.assertFalse(status.get("binding_valid"))
        self.assertTrue(status.get("state_advance_blocked"))

        deliver = self.run_selector(requested_mode="deliver")
        self.assertEqual(deliver["operation"], "prepare")
        self.assertEqual(deliver["priority"], "reapproval_required")
        self.assertFalse(deliver.get("binding_valid"))
        self.assertTrue(deliver.get("state_advance_blocked"))

    def test_asb_04_valid_binding_allows_review_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope_path, runtime_path, _ = write_binding_sources(repo, binding)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["issues"] = {"ASBC-002": {"status": "IMPLEMENTED"}}
            write_json(runtime_path, runtime)

            payload = self.run_selector(
                envelope_path=envelope_path,
                runtime_path=runtime_path,
                repo_root=repo,
            )

            self.assertEqual(payload["operation"], "execute.review")
            self.assertTrue(payload["binding_valid"])
            self.assertFalse(payload["state_advance_blocked"])

    def test_asb_14_to_16_stale_spec_blocks_review_and_delivery_but_not_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope_path, runtime_path, _ = write_binding_sources(repo, binding)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["issues"] = {
                "ASBC-002": {
                    "status": "PR_READY",
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "review": {"status": "approved", "range": REVIEW_RANGE},
                }
            }
            write_json(runtime_path, runtime)
            (repo / "knowledge/wiki/syntheses/spec.md").write_text(
                "approved spec changed\n", encoding="utf-8"
            )

            for requested_mode in ("execute", "deliver", "resume"):
                with self.subTest(requested_mode=requested_mode):
                    payload = self.run_selector(
                        envelope_path=envelope_path,
                        runtime_path=runtime_path,
                        repo_root=repo,
                        requested_mode=requested_mode,
                    )
                    self.assertEqual(payload["operation"], "prepare")
                    self.assertEqual(payload["binding_error"]["code"], "SPEC_DIGEST_MISMATCH")
                    self.assertFalse(payload["binding_valid"])
                    self.assertTrue(payload["state_advance_blocked"])

            status = self.run_selector(
                envelope_path=envelope_path,
                runtime_path=runtime_path,
                repo_root=repo,
                requested_mode="status",
            )
            self.assertEqual(status["operation"], "status")
            self.assertEqual(status["binding_error"]["code"], "SPEC_DIGEST_MISMATCH")
            self.assertFalse(status["binding_valid"])
            self.assertTrue(status["state_advance_blocked"])

    def test_status_is_diagnostic_and_other_modes_block_on_unsupported_runtime_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope_path, runtime_path, _ = write_binding_sources(repo, binding)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["schema_version"] = 1
            write_json(runtime_path, runtime)

            status = self.run_selector(
                envelope_path=envelope_path,
                runtime_path=runtime_path,
                repo_root=repo,
                requested_mode="status",
            )
            self.assertEqual(status["operation"], "status")
            self.assertEqual(status["binding_error"]["code"], "SCHEMA_UNSUPPORTED")
            self.assertFalse(status["binding_valid"])
            self.assertTrue(status["state_advance_blocked"])

            for mode in ("execute", "resume", "deliver"):
                with self.subTest(mode=mode):
                    blocked = self.run_selector(
                        envelope_path=envelope_path,
                        runtime_path=runtime_path,
                        repo_root=repo,
                        requested_mode=mode,
                    )
                    self.assertEqual(blocked["operation"], "prepare")
                    self.assertEqual(
                        blocked["binding_error"]["code"], "SCHEMA_UNSUPPORTED"
                    )

    def test_missing_envelope_selects_prepare(self) -> None:
        payload = self.run_selector(requested_mode="execute")

        self.assertEqual(payload["operation"], "prepare")
        self.assertEqual(payload["priority"], "missing_envelope")
        self.assertIn("skills/issue-implementation-loop/references/execution-envelope.md", payload["read_set"])

    def test_unreserved_issue_beats_runtime_state_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            del envelope["work_items"]["G2PR-001"]["worktree_path"]
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, envelope)
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "other-epic",
                    "envelope_revision": 99,
                    "issues": {},
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "prepare")
            self.assertEqual(payload["priority"], "reapproval_required")
            self.assertTrue(payload["state_advance_blocked"])

    def test_state_mismatch_beats_reviewable_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {
                            "status": "IMPLEMENTED",
                            "branch": "codex/other-epic/G2PR-001-wrong",
                        }
                    },
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "prepare")
            self.assertEqual(payload["priority"], "reapproval_required")
            self.assertTrue(payload["state_advance_blocked"])

    def test_fixable_issue_takes_priority_over_human_wait_and_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "REVIEW_CHANGES_REQUESTED"},
                        "G2PR-002": {"status": "WAITING_HUMAN"},
                    },
                    "human_requests": [
                        {"id": "HR-001", "scope": "issue", "issue": "G2PR-002"}
                    ],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.dispatch")
            self.assertEqual(payload["priority"], "fixable")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_human_wait_selects_wait_read_set_and_takes_priority_over_runnable_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "WAITING_HUMAN"},
                        "G2PR-002": {"status": "PENDING"},
                    },
                    "human_requests": [
                        {"id": "HR-001", "scope": "issue", "issue": "G2PR-001"}
                    ],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.wait")
            self.assertEqual(payload["priority"], "waiting_human")
            self.assertEqual(payload["target_issue"], "G2PR-001")
            self.assertIn("skills/issue-implementation-loop/references/human-wait.md", payload["read_set"])
            self.assertIn("skills/issue-implementation-loop/references/runtime-state.md", payload["read_set"])
            self.assertNotIn("skills/issue-implementation-loop/references/scheduler.md", payload["read_set"])
            self.assertNotIn("skills/issue-implementation-loop/references/worker-contract.md", payload["read_set"])

    def test_runnable_issue_selects_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {},
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.dispatch")
            self.assertEqual(payload["priority"], "runnable")
            self.assertEqual(payload["target_issue"], "G2PR-001")
            self.assertNotIn("skills/issue-implementation-loop/references/human-wait.md", payload["read_set"])

    def test_terminal_state_selects_deliver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        issue_id: {
                            "status": "PR_READY",
                            "base_sha": BASE_SHA,
                            "head_sha": HEAD_SHA,
                            "review": {"status": "approved", "range": REVIEW_RANGE},
                        }
                        for issue_id in ("G2PR-001", "G2PR-002", "G2PR-003")
                    },
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "deliver")
            self.assertEqual(payload["priority"], "terminal")

    def test_active_only_state_selects_reconcile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                current_runtime({
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "RUNNING"},
                        "G2PR-002": {"status": "RUNNING"},
                        "G2PR-003": {"status": "RUNNING"},
                    },
                    "human_requests": [],
                }),
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "resume")
            self.assertEqual(payload["priority"], "reconcile")


if __name__ == "__main__":
    unittest.main()
