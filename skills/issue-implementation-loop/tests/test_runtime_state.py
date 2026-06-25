from __future__ import annotations

from _helpers import *


class RuntimeStateTests(unittest.TestCase):
    def test_validate_runtime_state_requires_committed_review_range_for_success_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for status in ("PR_READY", "COMPLETE", "DONE"):
                runtime_path = Path(tmp) / f"{status}.json"
                write_json(
                    runtime_path,
                    {
                        "schema_version": 1,
                        "epic_id": "issue-implementation-loop",
                        "envelope_revision": 1,
                        "issues": {
                            "G2PR-001": {
                                "status": status,
                                "review": {"status": "approved"},
                            }
                        },
                        "human_requests": [],
                    },
                )

                result = run_script("validate_runtime_state.py", str(runtime_path))

                self.assertNotEqual(result.returncode, 0, status)
                self.assertIn("review.range", result.stderr)

    def test_validate_runtime_state_rejects_pr_ready_working_tree_review_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_path = Path(tmp) / "runtime.json"
            write_json(
                runtime_path,
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {
                            "status": "PR_READY",
                            "review": {
                                "status": "approved",
                                "range": f"{BASE_SHA}..working-tree",
                            },
                        }
                    },
                    "human_requests": [],
                },
            )

            result = run_script("validate_runtime_state.py", str(runtime_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("working-tree", result.stderr)

    def test_validate_runtime_state_requires_base_and_head_sha_for_success_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_path = Path(tmp) / "runtime.json"
            write_json(
                runtime_path,
                {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {
                        "G2PR-001": {
                            "status": "PR_READY",
                            "review": {
                                "status": "approved",
                                "range": REVIEW_RANGE,
                            },
                        }
                    },
                    "human_requests": [],
                },
            )

            result = run_script("validate_runtime_state.py", str(runtime_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base_sha", result.stderr)
            self.assertIn("head_sha", result.stderr)

    def test_validate_runtime_state_requires_review_range_to_match_base_and_head_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_path = Path(tmp) / "runtime.json"
            other_head = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
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
                                "range": f"{BASE_SHA}..{other_head}",
                            },
                        }
                    },
                    "human_requests": [],
                },
            )

            result = run_script("validate_runtime_state.py", str(runtime_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("match base_sha..head_sha", result.stderr)

    def test_validate_runtime_state_rejects_success_status_with_unapproved_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_path = Path(tmp) / "runtime.json"
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
                        }
                    },
                    "human_requests": [],
                },
            )

            result = run_script("validate_runtime_state.py", str(runtime_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.status must be approved", result.stderr)

    def test_rebuild_runtime_state_preserves_committed_review_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                json.dumps(
                    {
                        "event_id": "E-001",
                        "epic_id": "issue-implementation-loop",
                        "envelope_revision": 1,
                        "type": "review_status_changed",
                        "issue": "G2PR-001",
                        "status": "approved",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "range": REVIEW_RANGE,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            issue = payload["issues"]["G2PR-001"]
            self.assertEqual(issue["base_sha"], BASE_SHA)
            self.assertEqual(issue["head_sha"], HEAD_SHA)
            self.assertEqual(issue["review"]["range"], REVIEW_RANGE)

    def test_rebuild_runtime_state_records_pr_created_and_merged_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event_id": "E-001",
                                "epic_id": "issue-implementation-loop",
                                "envelope_revision": 1,
                                "type": "pr_created",
                                "issue": "G2PR-001",
                                "pr": "https://github.com/org/repo/pull/1",
                            }
                        ),
                        json.dumps(
                            {
                                "event_id": "E-002",
                                "epic_id": "issue-implementation-loop",
                                "envelope_revision": 1,
                                "type": "pr_merged",
                                "issue": "G2PR-001",
                                "pr": "https://github.com/org/repo/pull/1",
                                "merge_commit": HEAD_SHA,
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            issue = json.loads(result.stdout)["issues"]["G2PR-001"]
            self.assertEqual(issue["pr"], "https://github.com/org/repo/pull/1")
            self.assertTrue(issue["pr_opened"])
            self.assertTrue(issue["pr_merged"])
            self.assertEqual(issue["merge_commit"], HEAD_SHA)

    def test_rebuild_runtime_state_ignores_duplicate_event_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "event_id": "E-001",
                                "epic_id": "issue-implementation-loop",
                                "type": "issue_status_changed",
                                "issue": "G2PR-001",
                                "status": "RUNNING",
                            }
                        ),
                        json.dumps(
                            {
                                "event_id": "E-001",
                                "epic_id": "issue-implementation-loop",
                                "type": "issue_status_changed",
                                "issue": "G2PR-001",
                                "status": "PR_READY",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["issues"]["G2PR-001"]["status"], "RUNNING")
            self.assertEqual(payload["rebuild"]["duplicate_events_ignored"], 1)
