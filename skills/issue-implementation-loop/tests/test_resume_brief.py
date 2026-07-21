from __future__ import annotations

import re
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

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
        fixture_envelope = envelope if envelope is not None else base_envelope()
        fixture_envelope["epic_id"] = runtime["epic_id"]
        existing_binding = fixture_envelope.get("approved_spec_binding", {})
        existing_packet = root.parent / str(existing_binding.get("path", ""))
        if (
            isinstance(existing_binding, dict)
            and existing_packet.is_file()
            and hashlib.sha256(existing_packet.read_bytes()).hexdigest()
            == existing_binding.get("sha256")
        ):
            binding = copy.deepcopy(existing_binding)
        else:
            binding, _ = bind_envelope_fixture_repo(root.parent, fixture_envelope)
        root.mkdir()
        runtime = copy.deepcopy(runtime)
        runtime["schema_version"] = 2
        runtime["approved_spec_binding"] = copy.deepcopy(binding)
        for request in runtime.get("human_requests", []):
            request.setdefault("schema_version", 2)
            request["approved_spec_binding"] = copy.deepcopy(binding)
        events = copy.deepcopy(events)
        for event in events:
            event.setdefault("schema_version", 2)
            event.setdefault("envelope_revision", runtime["envelope_revision"])
            existing_binding = event.get("approved_spec_binding")
            if existing_binding is None or existing_binding == approved_spec_binding():
                event["approved_spec_binding"] = copy.deepcopy(binding)
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

    def test_resume_metadata_v3_binds_current_epoch_and_rejects_v2_or_meta_less(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=self.rich_events(),
            )

            build_result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertEqual(build_result.returncode, 0, build_result.stderr)
            meta_path = root / "resume-brief.meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(meta["schema_version"], 3)
            self.assertEqual(
                meta["sources"]["approved_spec_binding"],
                json.loads((root / "runtime-state.json").read_text(encoding="utf-8"))[
                    "approved_spec_binding"
                ],
            )

            meta["schema_version"] = 2
            write_json(meta_path, meta)
            v2_result = run_script(
                "validate_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )
            self.assertNotEqual(v2_result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", v2_result.stderr)

            meta_path.unlink()
            meta_less_result = run_script(
                "validate_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )
            self.assertNotEqual(meta_less_result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", meta_less_result.stderr)

    def test_resume_rejects_stale_packet_even_when_runtime_envelope_and_events_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _gate = create_binding_repo(Path(tmp))
            root = repo / "runtime"
            envelope = binding_envelope(repo, binding)
            runtime = {
                "schema_version": 2,
                "epic_id": "approved-spec-binding",
                "envelope_revision": 1,
                "approved_spec_binding": copy.deepcopy(binding),
                "issues": {},
                "human_requests": [],
            }
            events = [
                {
                    "schema_version": 2,
                    "event_id": "E-001",
                    "epic_id": "approved-spec-binding",
                    "envelope_revision": 1,
                    "approved_spec_binding": copy.deepcopy(binding),
                    "type": "issue_status_changed",
                    "issue": "ASBC-002",
                    "status": "PENDING",
                }
            ]
            self.write_runtime_root(root, envelope=envelope, runtime=runtime, events=events)
            build_result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(repo)
            )
            self.assertEqual(build_result.returncode, 0, build_result.stderr)

            packet_path = repo / binding["path"]
            packet_path.write_bytes(packet_path.read_bytes() + b" ")

            result = run_script(
                "validate_resume_brief.py", str(root), "--repo-root", str(repo)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INPUT_PACKET_DIGEST_MISMATCH", result.stderr)

    def test_asb_17_spec_drift_after_resume_metadata_publication_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            root = repo / "runtime"
            envelope = binding_envelope(repo, binding)
            runtime = {
                "schema_version": 2,
                "epic_id": "approved-spec-binding",
                "envelope_revision": 1,
                "approved_spec_binding": copy.deepcopy(binding),
                "issues": {},
                "human_requests": [],
            }
            events = [
                {
                    "schema_version": 2,
                    "event_id": "E-001",
                    "epic_id": "approved-spec-binding",
                    "envelope_revision": 1,
                    "approved_spec_binding": copy.deepcopy(binding),
                    "type": "issue_status_changed",
                    "issue": "ASBC-002",
                    "status": "PENDING",
                }
            ]
            self.write_runtime_root(
                root, envelope=envelope, runtime=runtime, events=events
            )
            built = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(repo)
            )
            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertTrue((root / "resume-brief.meta.json").is_file())

            (repo / "knowledge/wiki/syntheses/spec.md").write_text(
                "spec drift after metadata publication\n", encoding="utf-8"
            )
            result = run_script(
                "validate_resume_brief.py", str(root), "--repo-root", str(repo)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SPEC_DIGEST_MISMATCH", result.stderr)

    def test_build_resume_brief_rejects_mixed_binding_event_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            events = self.rich_events()
            events[-1]["approved_spec_binding"] = approved_spec_binding(sha256="a" * 64)
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=events,
            )

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BINDING_MISMATCH", result.stderr)

    def test_build_resume_brief_rejects_source_swap_before_metadata_publish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            self.write_runtime_root(
                root,
                envelope=self.rich_envelope(),
                runtime=self.rich_runtime(),
                events=self.rich_events(),
            )
            script_path = SCRIPTS_DIR / "build_resume_brief.py"
            spec = importlib.util.spec_from_file_location(
                "build_resume_brief_under_test", script_path
            )
            assert spec and spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            original_meta_builder = module.build_resume_brief_meta

            def swap_events(*args: object, **kwargs: object) -> dict:
                events_path = root / "events.jsonl"
                with events_path.open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(
                            {
                                "schema_version": 2,
                                "event_id": "E-source-swap",
                                "epic_id": "issue-implementation-loop",
                                "envelope_revision": 1,
                                "approved_spec_binding": approved_spec_binding(),
                                "type": "signal_recorded",
                                "issue": "G2PR-002",
                                "signal": "swapped",
                            }
                        )
                        + "\n"
                    )
                return original_meta_builder(*args, **kwargs)

            stdout = StringIO()
            stderr = StringIO()
            with (
                mock.patch.object(module, "build_resume_brief_meta", side_effect=swap_events),
                mock.patch.object(
                    sys,
                    "argv",
                    [str(script_path), str(root), "--repo-root", str(root.parent)],
                ),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                result = module.main()

            self.assertNotEqual(result, 0)
            self.assertIn("RESUME_SOURCE_CHANGED", stderr.getvalue())
            self.assertFalse((root / "resume-brief.md").exists())
            self.assertFalse((root / "resume-brief.meta.json").exists())

    def test_build_resume_brief_reverifies_binding_before_cache_publication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            runtime_root = repo / "runtime"
            envelope = binding_envelope(repo, binding)
            runtime = {
                "schema_version": 2,
                "epic_id": envelope["epic_id"],
                "envelope_revision": envelope["revision"],
                "approved_spec_binding": copy.deepcopy(binding),
                "issues": {},
                "human_requests": [],
            }
            events = [
                {
                    "schema_version": 2,
                    "event_id": "E-001",
                    "epic_id": envelope["epic_id"],
                    "envelope_revision": envelope["revision"],
                    "approved_spec_binding": copy.deepcopy(binding),
                    "type": "issue_status_changed",
                    "issue": "ASBC-002",
                    "status": "PENDING",
                }
            ]
            self.write_runtime_root(
                runtime_root,
                envelope=envelope,
                runtime=runtime,
                events=events,
            )
            script_path = SCRIPTS_DIR / "build_resume_brief.py"
            spec = importlib.util.spec_from_file_location(
                "build_resume_brief_binding_race", script_path
            )
            assert spec and spec.loader
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            original_meta_builder = module.build_resume_brief_meta

            def drift_spec(*args: object, **kwargs: object) -> dict:
                value = original_meta_builder(*args, **kwargs)
                (repo / "knowledge/wiki/syntheses/spec.md").write_text(
                    "drift before publication\n", encoding="utf-8"
                )
                return value

            stderr = StringIO()
            with (
                mock.patch.object(
                    module, "build_resume_brief_meta", side_effect=drift_spec
                ),
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        str(script_path),
                        str(runtime_root),
                        "--repo-root",
                        str(repo),
                    ],
                ),
                redirect_stderr(stderr),
            ):
                result = module.main()

            self.assertNotEqual(result, 0)
            self.assertIn("SPEC_DIGEST_MISMATCH", stderr.getvalue())
            self.assertFalse((runtime_root / "resume-brief.md").exists())
            self.assertFalse((runtime_root / "resume-brief.meta.json").exists())


    def rich_envelope(self) -> dict:
        envelope = batch_issue_prs_envelope()
        for issue_id, scope in {
            "G2PR-004": "path:skills/d",
            "G2PR-005": "path:skills/e",
            "G2PR-006": "path:skills/f",
        }.items():
            envelope["work_items"][issue_id] = {
                "title": f"Example issue {issue_id}",
                "source": {
                    "type": "local",
                    "path": "knowledge/wiki/syntheses/issues.md",
                },
                "acceptance_criteria": [f"{issue_id} is complete."],
                "non_goals": ["Do not write outside the approved scope."],
                "verification": ["python3 -m unittest"],
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

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

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
            meta_path = root / "resume-brief.meta.json"
            self.assertTrue(meta_path.exists())
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(meta["schema_version"], 3)
            self.assertEqual(
                meta["sources"]["approved_spec_binding"],
                json.loads((root / "runtime-state.json").read_text(encoding="utf-8"))[
                    "approved_spec_binding"
                ],
            )
            self.assertEqual(meta["artifact"], "resume-brief")
            self.assertEqual(meta["sources"]["execution_envelope"]["revision"], 1)
            self.assertEqual(meta["sources"]["runtime_state"]["envelope_revision"], 1)
            self.assertIn("sha256", meta["sources"]["events"])

            validate_result = run_script(
                "validate_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)

    def test_validate_resume_brief_rejects_stale_meta_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                (
                    "runtime",
                    lambda root: write_json(
                        root / "runtime-state.json",
                        {
                            "schema_version": 1,
                            "epic_id": "issue-implementation-loop",
                            "envelope_revision": 2,
                            "issues": {},
                            "human_requests": [],
                        },
                    ),
                    "runtime_state.sha256 is stale",
                ),
                (
                    "envelope",
                    lambda root: write_json(
                        root / "execution-envelope.json",
                        {**self.rich_envelope(), "revision": 2},
                    ),
                    "execution_envelope.revision is stale",
                ),
                (
                    "events",
                    lambda root: (root / "events.jsonl").write_text("", encoding="utf-8"),
                    "events.sha256 is stale",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    root = Path(tmp) / name
                    self.write_runtime_root(
                        root,
                        envelope=self.rich_envelope(),
                        runtime=self.rich_runtime(),
                        events=self.rich_events(),
                    )
                    build_result = run_script(
                        "build_resume_brief.py",
                        str(root),
                        "--repo-root",
                        str(root.parent),
                    )
                    self.assertEqual(build_result.returncode, 0, build_result.stderr)
                    mutate(root)

                    result = run_script(
                        "validate_resume_brief.py",
                        str(root),
                        "--repo-root",
                        str(root.parent),
                    )

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_resume_brief_rejects_brief_without_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            root.mkdir()
            (root / "resume-brief.md").write_text(
                "# Resume Brief\n\nLegacy cache without metadata.\n",
                encoding="utf-8",
            )

            result = run_script("validate_resume_brief.py", str(root))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

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

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

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

            result = run_script(
                "build_resume_brief.py",
                str(root),
                "--max-words",
                "10",
                "--repo-root",
                str(root.parent),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("RESUME_BRIEF_WORD_BUDGET_EXCEEDED", result.stderr)

    def test_build_resume_brief_rejects_missing_execution_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            runtime = {
                "schema_version": 1,
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "issues": {"G2PR-001": {"status": "PENDING"}},
                "human_requests": [],
            }
            events = [
                {
                    "event_id": "E-001",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": "G2PR-001",
                    "status": "RUNNING",
                }
            ]
            self.write_runtime_root(root, envelope=None, runtime=runtime, events=events)

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)
            self.assertFalse((root / "resume-brief.md").exists())
            self.assertFalse((root / "resume-brief.meta.json").exists())

    def test_build_resume_brief_prioritizes_waiting_human_before_runnable_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            runtime = {
                "schema_version": 1,
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 1,
                "issues": {
                    "G2PR-001": {"status": "WAITING_HUMAN"},
                    "G2PR-002": {"status": "PENDING"},
                },
                "human_requests": [
                    {
                        "id": "HR-001",
                        "scope": "issue",
                        "issue": "G2PR-001",
                        "reason": "needs decision",
                    }
                ],
            }
            events = [
                {
                    "event_id": "E-001-waiting",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": "G2PR-001",
                    "status": "WAITING_HUMAN",
                },
                {
                    "event_id": "E-002-pending",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "issue_status_changed",
                    "issue": "G2PR-002",
                    "status": "PENDING",
                },
                {
                    "event_id": "E-003-human",
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "type": "human_request_opened",
                    "id": "HR-001",
                    "scope": "issue",
                    "issue": "G2PR-001",
                    "reason": "needs decision",
                },
            ]
            self.write_runtime_root(root, envelope=batch_issue_prs_envelope(), runtime=runtime, events=events)

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            self.assertIn("Runnable: G2PR-002", brief)
            self.assertIn("Waiting human: G2PR-001", brief)
            self.assertIn("Recommended next operation: human.resolve G2PR-001", brief)

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

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

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
                        "status": "IMPLEMENTED",
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

            result = run_script(
                "build_resume_brief.py", str(root), "--repo-root", str(root.parent)
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            brief = (root / "resume-brief.md").read_text(encoding="utf-8")
            verified_ranges = self.brief_line(brief, "Verified commit ranges")
            self.assertEqual(verified_ranges, f"G2PR-001 {REVIEW_RANGE}")
            self.assertNotIn(fix_range, verified_ranges)
            self.assertNotIn(unapproved_range, verified_ranges)
