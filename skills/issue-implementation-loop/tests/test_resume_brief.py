from __future__ import annotations

import re

from _helpers import *


class ResumeBriefTests(unittest.TestCase):
    def brief_line(self, brief: str, label: str) -> str:
        prefix = f"- {label}: "
        for line in brief.splitlines():
            if line.startswith(prefix):
                return line.removeprefix(prefix)
        self.fail(f"missing brief line: {label}")

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
            self.assertIn("Latest report paths:", brief)
            self.assertIn("reports/G2PR-001-worker-report.json", brief)
            self.assertIn("reviews/G2PR-001-review.json", brief)
            self.assertIn("Recommended next operation: execute.review G2PR-003", brief)
            self.assertIn("cache only", brief)
            self.assertLessEqual(len(re.findall(r"\S+", brief)), 600)

    def test_build_resume_brief_orders_latest_report_paths_by_mtime_across_reports_and_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=self.rich_events(),
            )
            files_by_age = [
                root / "reviews" / "newest-review.json",
                root / "reports" / "middle-report.json",
                root / "reviews" / "old-review.json",
                root / "reports" / "G2PR-001-worker-report.json",
                root / "reviews" / "G2PR-001-review.json",
            ]
            for path in files_by_age:
                write_json(path, {"path": path.name})
            for offset, path in enumerate(files_by_age):
                timestamp = 1_700_000_000 - offset
                os.utime(path, (timestamp, timestamp))

            result = run_script("build_resume_brief.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            latest_paths = self.brief_line(brief, "Latest report paths")
            self.assertTrue(
                latest_paths.startswith(
                    "reviews/newest-review.json, reports/middle-report.json, reviews/old-review.json"
                ),
                latest_paths,
            )

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

    def test_build_resume_brief_compares_remote_pr_fields_from_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            runtime = {
                "schema_version": 1,
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "issues": {
                    "G2PR-001": {
                        "status": "PR_READY",
                        "base_sha": BASE_SHA,
                        "head_sha": HEAD_SHA,
                        "review": {"status": "approved", "range": REVIEW_RANGE},
                    }
                },
                "human_requests": [],
            }
            events = [
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
                    "event_id": "E-002-status",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": "G2PR-001",
                    "status": "PR_READY",
                    "base_sha": BASE_SHA,
                    "head_sha": HEAD_SHA,
                },
                {
                    "event_id": "E-003-pr",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "pr_created",
                    "issue": "G2PR-001",
                    "pr": "https://github.com/org/repo/pull/1",
                },
            ]
            self.write_runtime_root(root, envelope=batch_issue_prs_envelope(), runtime=runtime, events=events)

            result = run_script("build_resume_brief.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            self.assertIn(
                "runtime/events mismatch for G2PR-001 pr_opened: runtime=None events=True",
                brief,
            )
            self.assertIn("Pending remote action: none", brief)
            self.assertIn("Recommended next operation: resume.recover", brief)

    def test_build_resume_brief_verified_ranges_exclude_unapproved_or_non_success_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            fix_base = "a" * 40
            fix_head = "b" * 40
            unapproved_base = "c" * 40
            unapproved_head = "d" * 40
            fix_range = f"{fix_base}..{fix_head}"
            unapproved_range = f"{unapproved_base}..{unapproved_head}"
            runtime = {
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
                    "G2PR-002": {
                        "status": "REVIEW_CHANGES_REQUESTED",
                        "base_sha": fix_base,
                        "head_sha": fix_head,
                        "review": {"status": "changes_requested", "range": fix_range},
                    },
                    "G2PR-003": {
                        "status": "COMPLETE",
                        "base_sha": unapproved_base,
                        "head_sha": unapproved_head,
                        "review": {"status": "changes_requested", "range": unapproved_range},
                    },
                },
                "human_requests": [],
            }
            events = [
                {
                    "event_id": f"E-{issue_id}-review",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "review_status_changed",
                    "issue": issue_id,
                    "status": record["review"]["status"],
                    "base_sha": record["base_sha"],
                    "head_sha": record["head_sha"],
                    "range": record["review"]["range"],
                }
                for issue_id, record in runtime["issues"].items()
            ] + [
                {
                    "event_id": f"E-{issue_id}-status",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": issue_id,
                    "status": record["status"],
                    "base_sha": record["base_sha"],
                    "head_sha": record["head_sha"],
                }
                for issue_id, record in runtime["issues"].items()
            ]
            self.write_runtime_root(root, envelope=self.rich_envelope(), runtime=runtime, events=events)

            result = run_script("build_resume_brief.py", str(root))

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            verified_ranges = self.brief_line(brief, "Verified commit ranges")
            self.assertEqual(verified_ranges, f"G2PR-001 {REVIEW_RANGE}")
            self.assertNotIn(fix_range, verified_ranges)
            self.assertNotIn(unapproved_range, verified_ranges)
