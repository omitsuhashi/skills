from __future__ import annotations

from _helpers import *


class SchedulerTests(unittest.TestCase):
    def test_compute_next_actions_does_not_wait_for_wave_barrier(self) -> None:
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
                            "status": "PR_READY",
                            "base_sha": BASE_SHA,
                            "head_sha": HEAD_SHA,
                            "review": {
                                "status": "approved",
                                "range": REVIEW_RANGE,
                            },
                        },
                        "G2PR-002": {"status": "RUNNING"},
                        "G2PR-003": {"status": "PENDING"},
                    },
                    "human_requests": [],
                },
            )

            result = run_script(
                "compute_next_actions.py",
                str(envelope_path),
                str(runtime_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("G2PR-003", payload["runnable"])
            self.assertNotIn("G2PR-002", payload["runnable"])

    def test_compute_next_actions_does_not_release_review_approved_dependency_from_success_status_alone(self) -> None:
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
                            "status": "PR_READY",
                            "base_sha": BASE_SHA,
                            "head_sha": HEAD_SHA,
                            "review": {
                                "status": "changes_requested",
                                "range": REVIEW_RANGE,
                            },
                        },
                        "G2PR-002": {"status": "PENDING"},
                        "G2PR-003": {"status": "PENDING"},
                    },
                    "human_requests": [],
                },
            )

            result = run_script(
                "compute_next_actions.py",
                str(envelope_path),
                str(runtime_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.status must be approved", result.stderr)

    def test_issue_scoped_human_wait_does_not_block_unrelated_work(self) -> None:
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
                        "G2PR-003": {"status": "PENDING"},
                    },
                    "human_requests": [
                        {
                            "id": "HR-001",
                            "scope": "issue",
                            "issue": "G2PR-001",
                            "reason": "needs decision",
                        }
                    ],
                },
            )

            result = run_script(
                "compute_next_actions.py",
                str(envelope_path),
                str(runtime_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("G2PR-002", payload["runnable"])
            self.assertIn("G2PR-001", payload["waiting_human"])
            self.assertNotIn("G2PR-003", payload["runnable"])

    def test_resource_scoped_human_wait_blocks_only_matching_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-001"]["write_scope"] = ["path:shared"]
            envelope["work_items"]["G2PR-002"]["write_scope"] = ["path:other"]
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, envelope)
            write_json(
                runtime_path,
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "PENDING"},
                        "G2PR-002": {"status": "PENDING"},
                        "G2PR-003": {"status": "PENDING"},
                    },
                    "human_requests": [
                        {
                            "id": "HR-001",
                            "scope": "resource",
                            "resource": "path:shared",
                            "reason": "shared docs decision",
                        }
                    ],
                },
            )

            result = run_script(
                "compute_next_actions.py",
                str(envelope_path),
                str(runtime_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("G2PR-002", payload["runnable"])
            self.assertIn("G2PR-001", payload["waiting_human"])

    def test_pending_runnable_candidates_with_overlapping_scope_are_serialized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-001"]["write_scope"] = ["path:shared"]
            envelope["work_items"]["G2PR-002"]["write_scope"] = ["path:shared/sub"]
            envelope_path = Path(tmp) / "envelope.json"
            runtime_path = Path(tmp) / "runtime.json"
            write_json(envelope_path, envelope)
            write_json(
                runtime_path,
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {"status": "PENDING"},
                        "G2PR-002": {"status": "PENDING"},
                        "G2PR-003": {"status": "PENDING"},
                    },
                    "human_requests": [],
                },
            )

            result = run_script(
                "compute_next_actions.py",
                str(envelope_path),
                str(runtime_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertIn("G2PR-001", payload["runnable"])
            self.assertNotIn("G2PR-002", payload["runnable"])
            self.assertEqual(payload["blocked"]["G2PR-002"], ["resource:G2PR-001"])
