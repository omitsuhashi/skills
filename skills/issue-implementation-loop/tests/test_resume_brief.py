from __future__ import annotations

import re

from _helpers import *


class ResumeBriefTests(unittest.TestCase):
    def write_runtime_root(
        self,
        root: Path,
        *,
        envelope: dict | None,
        runtime: dict,
        events: list[dict],
    ) -> None:
        root.mkdir()
        if envelope is not None:
            write_json(root / "execution-envelope.json", envelope)
        write_json(root / "runtime-state.json", runtime)
        (root / "events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )
        reports = root / "reports"
        reviews = root / "reviews"
        reports.mkdir()
        reviews.mkdir()
        write_json(reports / "G2PR-001-worker-report.json", {"issue_id": "G2PR-001"})
        write_json(reviews / "G2PR-001-review.json", {"issue_id": "G2PR-001"})

    def rich_envelope(self) -> dict:
        envelope = batch_issue_prs_envelope()
        for issue_id, scope in {
            "G2PR-004": "path:skills/d",
            "G2PR-005": "path:skills/e",
            "G2PR-006": "path:skills/f",
        }.items():
            envelope["work_items"][issue_id] = {
                "branch": f"codex/issue-implementation-loop/{issue_id}-x",
                "worktree_path": f"/tmp/skills/issue-implementation-loop/{issue_id}-x",
                "worktree_state": "create_on_run",
                "base_policy": {"type": "epic_base"},
                "write_scope": [scope],
                "dependencies": [],
            }
        return envelope

    def rich_runtime(self) -> dict:
        return {
            "schema_version": 1,
            "epic_id": "issue-implementation-loop",
            "envelope_revision": 1,
            "issues": {
                "G2PR-001": {
                    "status": "PR_READY",
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                    "review": {"status": "approved", "range": REVIEW_RANGE},
                },
                "G2PR-002": {"status": "RUNNING"},
                "G2PR-003": {"status": "IMPLEMENTED"},
                "G2PR-004": {"status": "REVIEW_CHANGES_REQUESTED"},
                "G2PR-005": {"status": "WAITING_HUMAN"},
                "G2PR-006": {"status": "PENDING"},
            },
            "human_requests": [
                {
                    "id": "HR-001",
                    "scope": "issue",
                    "issue": "G2PR-005",
                    "reason": "needs decision",
                }
            ],
        }

    def rich_events(self) -> list[dict]:
        events: list[dict] = [
            {
                "event_id": "E-001-review",
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "type": "review_status_changed",
                "issue": "G2PR-001",
                "status": "approved",
                "base_sha": BASE_SHA,
                "head_sha": HEAD_SHA,
                "range": REVIEW_RANGE,
            },
            {
                "event_id": "E-001-status",
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "type": "issue_status_changed",
                "issue": "G2PR-001",
                "status": "PR_READY",
                "base_sha": BASE_SHA,
                "head_sha": HEAD_SHA,
            },
        ]
        for index, (issue_id, status) in enumerate(
            {
                "G2PR-002": "RUNNING",
                "G2PR-003": "IMPLEMENTED",
                "G2PR-004": "REVIEW_CHANGES_REQUESTED",
                "G2PR-005": "WAITING_HUMAN",
                "G2PR-006": "PENDING",
            }.items(),
            start=2,
        ):
            events.append(
                {
                    "event_id": f"E-{index:03d}-status",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": issue_id,
                    "status": status,
                }
            )
        events.append(
            {
                "event_id": "E-010-human",
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "type": "human_request_opened",
                "id": "HR-001",
                "scope": "issue",
                "issue": "G2PR-005",
                "reason": "needs decision",
            }
        )
        return events

    def test_build_resume_brief_writes_budgeted_cache_with_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=self.rich_events(),
            )

            result = run_script("build_resume_brief.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            brief_path = root / "resume-brief.md"
            brief = brief_path.read_text(encoding="utf-8")
            self.assertIn("Epic ID: issue-implementation-loop", brief)
            self.assertIn("Overall status:", brief)
            self.assertIn("Runnable: G2PR-006", brief)
            self.assertIn("Active: G2PR-002", brief)
            self.assertIn("Reviewable: G2PR-003", brief)
            self.assertIn("Fixable: G2PR-004", brief)
            self.assertIn("Waiting human: G2PR-005", brief)
            self.assertIn("Pending remote action:", brief)
            self.assertIn(f"Verified commit ranges: G2PR-001 {REVIEW_RANGE}", brief)
            self.assertIn("Latest report paths: reports/G2PR-001-worker-report.json", brief)
            self.assertIn("reviews/G2PR-001-review.json", brief)
            self.assertIn("Recommended next operation: execute.review G2PR-003", brief)
            self.assertIn("cache only", brief)
            self.assertLessEqual(len(re.findall(r"\S+", brief)), 600)

    def test_build_resume_brief_fails_fast_when_word_budget_is_exceeded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=self.rich_events(),
            )

            result = run_script("build_resume_brief.py", str(root), "--max-words", "10")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_BRIEF_WORD_BUDGET_EXCEEDED", result.stderr)

    def test_build_resume_brief_surfaces_runtime_event_inconsistencies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            runtime = {
                "schema_version": 1,
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "issues": {"G2PR-001": {"status": "RUNNING"}},
                "human_requests": [],
            }
            events = [
                {
                    "event_id": "E-001",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": "G2PR-001",
                    "status": "COMPLETE",
                }
            ]
            self.write_runtime_root(root, envelope=None, runtime=runtime, events=events)

            result = run_script("build_resume_brief.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            self.assertIn("Runnable: unavailable - execution envelope missing", brief)
            self.assertIn(
                "runtime/events mismatch for G2PR-001 status: runtime=RUNNING events=COMPLETE",
                brief,
            )
            self.assertIn("Recommended next operation: resume.recover", brief)
