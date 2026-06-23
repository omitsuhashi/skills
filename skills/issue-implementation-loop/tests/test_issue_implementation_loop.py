from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
BASE_SHA = "0123456789abcdef0123456789abcdef01234567"
HEAD_SHA = "89abcdef0123456789abcdef0123456789abcdef"
REVIEW_RANGE = f"{BASE_SHA}..{HEAD_SHA}"


def run_script(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def base_envelope() -> dict:
    return {
        "schema_version": 1,
        "epic_id": "issue-implementation-loop",
        "revision": 1,
        "epic_base": {"ref": "main", "sha": BASE_SHA},
        "execution_policy": {
            "parallel_preferred": True,
            "serial_fallback_preapproved": True,
            "implementation_slots": 4,
            "review_slots": 2,
            "wave_is_barrier": False,
        },
        "review_policy": {
            "primary": "requesting-code-review",
            "fallbacks": ["manual"],
            "manual_fallback_preapproved": False,
            "max_fix_cycles": 3,
            "same_finding_limit": 2,
        },
        "human_policy": {
            "default_scope": "issue",
            "epic_scope_requires_reason": True,
        },
        "remote_write_policy": {"mode": "local_only", "approved_actions": []},
        "work_items": {
            "G2PR-001": {
                "branch": "codex/issue-implementation-loop/G2PR-001-a",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-001-a",
                "worktree_state": "create_on_run",
                "base_policy": {"type": "epic_base"},
                "write_scope": ["path:skills/a"],
                "dependencies": [],
            },
            "G2PR-002": {
                "branch": "codex/issue-implementation-loop/G2PR-002-b",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-002-b",
                "worktree_state": "create_on_run",
                "base_policy": {"type": "epic_base"},
                "write_scope": ["path:skills/b"],
                "dependencies": [],
            },
            "G2PR-003": {
                "branch": "codex/issue-implementation-loop/G2PR-003-c",
                "worktree_path": "/tmp/skills/issue-implementation-loop/G2PR-003-c",
                "worktree_state": "reserved",
                "base_policy": {
                    "type": "blocker_head",
                    "issue": "G2PR-001",
                },
                "write_scope": ["path:skills/c"],
                "dependencies": [
                    {
                        "issue": "G2PR-001",
                        "strength": "hard",
                        "release_on": "review_approved",
                        "base_effect": "branch_from_blocker_head",
                    }
                ],
            },
        },
    }


class IssueImplementationLoopTests(unittest.TestCase):
    def test_validate_execution_envelope_rejects_invalid_epic_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing_ref", {"sha": BASE_SHA}, "epic_base.ref"),
                ("missing_sha", {"ref": "main"}, "epic_base.sha"),
                ("short_sha", {"ref": "main", "sha": "0123456789abcdef"}, "epic_base.sha"),
            ]
            for name, epic_base, expected in cases:
                envelope = base_envelope()
                envelope["epic_base"] = epic_base
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_rejects_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-001"]["dependencies"] = [
                {
                    "issue": "G2PR-003",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                }
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cycle", result.stderr.lower())

    def test_validate_execution_envelope_rejects_multiple_blocker_heads_without_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {
                "type": "blocker_head",
                "issue": "G2PR-001",
            }
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                },
                {
                    "issue": "G2PR-002",
                    "strength": "hard",
                    "release_on": "review_approved",
                    "base_effect": "branch_from_blocker_head",
                },
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple blocker heads", result.stderr.lower())

    def test_validate_execution_envelope_requires_integration_base_policy_for_integration_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {"type": "epic_base"}
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                }
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("integration_head", result.stderr)

    def test_validate_execution_envelope_rejects_multiple_integration_heads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["work_items"]["G2PR-003"]["base_policy"] = {
                "type": "integration_head",
                "integration_issue": "G2PR-001",
            }
            envelope["work_items"]["G2PR-003"]["dependencies"] = [
                {
                    "issue": "G2PR-001",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                },
                {
                    "issue": "G2PR-002",
                    "strength": "hard",
                    "release_on": "integrated",
                    "base_effect": "branch_from_integration_head",
                },
            ]
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("multiple integration heads", result.stderr.lower())

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


if __name__ == "__main__":
    unittest.main()
