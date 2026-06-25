from __future__ import annotations

from _helpers import *


class OperationSelectionTests(unittest.TestCase):
    def run_selector(
        self,
        *,
        envelope_path: Path | None = None,
        runtime_path: Path | None = None,
        requested_mode: str = "execute",
    ) -> dict:
        args = ["--requested-mode", requested_mode, "--json"]
        if envelope_path is not None:
            args.extend(["--envelope", str(envelope_path)])
        if runtime_path is not None:
            args.extend(["--runtime", str(runtime_path)])
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
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "IMPLEMENTED"},
                        "G2PR-002": {"status": "PENDING"},
                    },
                    "human_requests": [],
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)
            self.assertEqual(payload["operation"], "execute.review")
            self.assertEqual(payload["target_issue"], "G2PR-001")
            self.assertEqual(payload["priority"], "reviewable")
            self.assertIn("skills/issue-implementation-loop/references/review-gate.md", payload["read_set"])
            self.assertTrue(payload["word_budget_result"]["within_budget"])

    def test_explicit_status_and_deliver_modes_win_without_state_files(self) -> None:
        cases = [
            ("status", "status", "explicit_status", "references/scheduler.md"),
            ("deliver", "deliver", "explicit_deliver", "references/remote-delivery.md"),
        ]
        for requested_mode, operation, priority, expected_reference in cases:
            with self.subTest(requested_mode):
                payload = self.run_selector(requested_mode=requested_mode)
                self.assertEqual(payload["operation"], operation)
                self.assertEqual(payload["priority"], priority)
                self.assertTrue(any(expected_reference in path for path in payload["read_set"]))

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
                {
                    "schema_version": 1,
                    "epic_id": "other-epic",
                    "envelope_revision": 99,
                    "issues": {},
                    "human_requests": [],
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "prepare")
            self.assertEqual(payload["priority"], "unreserved")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_state_mismatch_beats_reviewable_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                {
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
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "resume")
            self.assertEqual(payload["priority"], "git_state_mismatch")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_fixable_issue_takes_priority_over_human_wait_and_runnable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                {
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
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.dispatch")
            self.assertEqual(payload["priority"], "fixable")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_human_wait_takes_priority_over_runnable_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                {
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
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.dispatch")
            self.assertEqual(payload["priority"], "waiting_human")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_runnable_issue_selects_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {},
                    "human_requests": [],
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "execute.dispatch")
            self.assertEqual(payload["priority"], "runnable")
            self.assertEqual(payload["target_issue"], "G2PR-001")

    def test_terminal_state_selects_deliver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, base_envelope())
            write_json(
                runtime_path,
                {
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
                },
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
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "RUNNING"},
                        "G2PR-002": {"status": "RUNNING"},
                        "G2PR-003": {"status": "RUNNING"},
                    },
                    "human_requests": [],
                },
            )

            payload = self.run_selector(envelope_path=envelope_path, runtime_path=runtime_path)

            self.assertEqual(payload["operation"], "resume")
            self.assertEqual(payload["priority"], "reconcile")


if __name__ == "__main__":
    unittest.main()
