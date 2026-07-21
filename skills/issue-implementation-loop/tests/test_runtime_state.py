from __future__ import annotations

from _helpers import *


class RuntimeStateTests(unittest.TestCase):
    def event(self, event_id: str, *, binding: dict | None = None, **fields: object) -> dict:
        return {
            "schema_version": 2,
            "event_id": event_id,
            "epic_id": "issue-implementation-loop",
            "envelope_revision": 1,
            "approved_spec_binding": copy.deepcopy(binding or approved_spec_binding()),
            **fields,
        }

    def test_rebuild_runtime_state_binds_same_epoch_events_to_runtime_v2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                json.dumps(
                    self.event(
                        "E-001",
                        type="issue_status_changed",
                        issue="G2PR-001",
                        status="RUNNING",
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["schema_version"], 2)
            self.assertEqual(payload["approved_spec_binding"], approved_spec_binding())

    def test_rebuild_runtime_state_rejects_mixed_binding_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binding_b = approved_spec_binding(sha256="a" * 64)
            events_path = Path(tmp) / "events.jsonl"
            events_path.write_text(
                "".join(
                    json.dumps(event) + "\n"
                    for event in (
                        self.event(
                            "E-001",
                            type="issue_status_changed",
                            issue="G2PR-001",
                            status="RUNNING",
                        ),
                        self.event(
                            "E-002",
                            binding=binding_b,
                            type="issue_status_changed",
                            issue="G2PR-001",
                            status="PR_READY",
                        ),
                    )
                ),
                encoding="utf-8",
            )

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BINDING_MISMATCH", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_rebuild_runtime_state_rejects_event_v1_and_missing_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = {
                "v1": {
                    "schema_version": 1,
                    "event_id": "E-001",
                    "epic_id": "issue-implementation-loop",
                    "type": "issue_status_changed",
                },
                "missing-binding": {
                    "schema_version": 2,
                    "event_id": "E-001",
                    "epic_id": "issue-implementation-loop",
                    "type": "issue_status_changed",
                },
            }
            for name, event in cases.items():
                with self.subTest(name=name):
                    events_path = Path(tmp) / f"{name}.jsonl"
                    events_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

                    result = run_script("rebuild_runtime_state.py", str(events_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_rebuild_runtime_state_rejects_unknown_event_type_and_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = {
                "unknown-type": self.event("E-001", type="epoch_rewritten"),
                "unknown-field": self.event(
                    "E-001",
                    type="issue_status_changed",
                    issue="G2PR-001",
                    status="RUNNING",
                    injected=True,
                ),
            }
            for name, event in cases.items():
                with self.subTest(name=name):
                    events_path = Path(tmp) / f"{name}.jsonl"
                    events_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

                    result = run_script("rebuild_runtime_state.py", str(events_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_rebuild_runtime_state_rejects_boolean_envelope_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "events.jsonl"
            event = self.event(
                "E-001",
                type="issue_status_changed",
                issue="G2PR-001",
                status="RUNNING",
            )
            event["envelope_revision"] = True
            events_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

            result = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_validate_runtime_state_rejects_unknown_root_and_issue_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = {
                "root": current_runtime(
                    {
                        "schema_version": 2,
                        "epic_id": "issue-implementation-loop",
                        "envelope_revision": 1,
                        "issues": {},
                        "human_requests": [],
                        "injected": True,
                    }
                ),
                "issue": current_runtime(
                    {
                        "schema_version": 2,
                        "epic_id": "issue-implementation-loop",
                        "envelope_revision": 1,
                        "issues": {
                            "G2PR-001": {"status": "RUNNING", "injected": True}
                        },
                        "human_requests": [],
                    }
                ),
            }
            for name, runtime in cases.items():
                with self.subTest(name=name):
                    runtime_path = Path(tmp) / f"{name}.json"
                    write_json(runtime_path, runtime)

                    result = run_script("validate_runtime_state.py", str(runtime_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_validate_runtime_state_rejects_booleans_for_integer_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = {
                "envelope-revision": {
                    "envelope_revision": True,
                },
                "events-applied": {
                    "envelope_revision": 1,
                    "rebuild": {
                        "events_applied": True,
                        "duplicate_events_ignored": 0,
                    },
                },
                "duplicates-ignored": {
                    "envelope_revision": 1,
                    "rebuild": {
                        "events_applied": 1,
                        "duplicate_events_ignored": False,
                    },
                },
            }
            for name, fields in cases.items():
                with self.subTest(name=name):
                    runtime = current_runtime(
                        {
                            "schema_version": 2,
                            "epic_id": "issue-implementation-loop",
                            "issues": {},
                            "human_requests": [],
                            **fields,
                        }
                    )
                    runtime_path = Path(tmp) / f"{name}.json"
                    write_json(runtime_path, runtime)

                    result = run_script("validate_runtime_state.py", str(runtime_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_rebuild_runtime_state_rejects_invalid_human_request_fold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for missing in ("id", "scope", "reason"):
                with self.subTest(missing=missing):
                    fields = {
                        "type": "human_request_opened",
                        "id": "HR-001",
                        "scope": "issue",
                        "issue": "G2PR-001",
                        "reason": "needs decision",
                    }
                    del fields[missing]
                    events_path = Path(tmp) / f"missing-{missing}.jsonl"
                    events_path.write_text(
                        json.dumps(self.event("E-001", **fields)) + "\n",
                        encoding="utf-8",
                    )

                    result = run_script("rebuild_runtime_state.py", str(events_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("SCHEMA_UNSUPPORTED", result.stderr)

    def test_validate_runtime_state_rejects_v1_and_old_epoch_human_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binding_b = approved_spec_binding(sha256="a" * 64)
            cases = {
                "runtime-v1": {
                    "schema_version": 1,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {},
                    "human_requests": [],
                },
                "runtime-missing-binding": {
                    "schema_version": 2,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 1,
                    "issues": {},
                    "human_requests": [],
                },
                "request-v1": {
                    "schema_version": 2,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 2,
                    "approved_spec_binding": binding_b,
                    "issues": {},
                    "human_requests": [
                        {
                            "schema_version": 1,
                            "id": "HR-001",
                            "scope": "epic",
                            "reason": "old epoch",
                        }
                    ],
                },
                "old-request": {
                    "schema_version": 2,
                    "epic_id": "issue-implementation-loop",
                    "envelope_revision": 2,
                    "approved_spec_binding": binding_b,
                    "issues": {},
                    "human_requests": [
                        {
                            "schema_version": 2,
                            "approved_spec_binding": approved_spec_binding(),
                            "id": "HR-001",
                            "scope": "epic",
                            "reason": "reconfirm after reseal",
                        }
                    ],
                },
            }
            expected = {
                "runtime-v1": "SCHEMA_UNSUPPORTED",
                "runtime-missing-binding": "SCHEMA_UNSUPPORTED",
                "request-v1": "SCHEMA_UNSUPPORTED",
                "old-request": "AUXILIARY_ARTIFACT_BINDING_MISMATCH",
            }
            for name, runtime in cases.items():
                with self.subTest(name=name):
                    runtime_path = Path(tmp) / f"{name}.json"
                    write_json(runtime_path, runtime)

                    result = run_script("validate_runtime_state.py", str(runtime_path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected[name], result.stderr)

    def test_asb_30_reapproval_rejects_old_and_accepts_rerecorded_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binding_a = approved_spec_binding()
            binding_b = approved_spec_binding(sha256="a" * 64)
            old_request_runtime = {
                "schema_version": 2,
                "epic_id": "issue-implementation-loop",
                "envelope_revision": 2,
                "approved_spec_binding": binding_b,
                "issues": {},
                "human_requests": [
                    {
                        "schema_version": 2,
                        "approved_spec_binding": binding_a,
                        "id": "HR-001",
                        "scope": "epic",
                        "reason": "decision from old binding",
                    }
                ],
            }
            old_path = root / "runtime-old-request.json"
            write_json(old_path, old_request_runtime)

            rejected = run_script("validate_runtime_state.py", str(old_path), "--json")

            self.assertEqual(rejected.returncode, 1)
            self.assertEqual(
                json.loads(rejected.stdout)["errors"],
                ["AUXILIARY_ARTIFACT_BINDING_MISMATCH"],
            )

            events_path = root / "events-b.jsonl"
            opened = self.event(
                "E-B-001",
                binding=binding_b,
                envelope_revision=2,
                type="human_request_opened",
                id="HR-B-001",
                scope="epic",
                reason="re-record decision under binding B",
            )
            resolved = self.event(
                "E-B-002",
                binding=binding_b,
                envelope_revision=2,
                type="human_request_resolved",
                id="HR-B-001",
            )
            events_path.write_text(json.dumps(opened) + "\n", encoding="utf-8")

            accepted_request = run_script("rebuild_runtime_state.py", str(events_path))

            self.assertEqual(accepted_request.returncode, 0, accepted_request.stderr)
            open_runtime = json.loads(accepted_request.stdout)
            self.assertEqual(
                open_runtime["human_requests"][0]["approved_spec_binding"], binding_b
            )

            events_path.write_text(
                json.dumps(opened) + "\n" + json.dumps(resolved) + "\n",
                encoding="utf-8",
            )
            accepted_resolution = run_script(
                "rebuild_runtime_state.py", str(events_path)
            )

            self.assertEqual(
                accepted_resolution.returncode, 0, accepted_resolution.stderr
            )
            rebuilt = json.loads(accepted_resolution.stdout)
            self.assertEqual(rebuilt["approved_spec_binding"], binding_b)
            self.assertEqual(rebuilt["human_requests"], [])

    def test_runtime_event_and_human_request_schemas_are_current_only_v2(self) -> None:
        schema_root = SKILL_DIR / "assets" / "schemas"
        for name in ("event", "runtime-state", "human-request"):
            with self.subTest(name=name):
                schema = json.loads(
                    (schema_root / f"{name}.schema.json").read_text(encoding="utf-8")
                )
                self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
                self.assertIn("approved_spec_binding", schema["required"])

    def test_validate_runtime_state_requires_committed_review_range_for_success_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for status in ("PR_READY", "COMPLETE", "DONE"):
                runtime_path = Path(tmp) / f"{status}.json"
                write_json(
                    runtime_path,
                    {
                        "schema_version": 2,
                        "approved_spec_binding": approved_spec_binding(),
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
                    "schema_version": 2,
                    "approved_spec_binding": approved_spec_binding(),
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
                    "schema_version": 2,
                    "approved_spec_binding": approved_spec_binding(),
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
                    "schema_version": 2,
                    "approved_spec_binding": approved_spec_binding(),
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
                    "schema_version": 2,
                    "approved_spec_binding": approved_spec_binding(),
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
                    self.event(
                        "E-001",
                        type="review_status_changed",
                        issue="G2PR-001",
                        status="approved",
                        base_sha=BASE_SHA,
                        head_sha=HEAD_SHA,
                        range=REVIEW_RANGE,
                    )
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
                            self.event(
                                "E-001",
                                type="pr_created",
                                issue="G2PR-001",
                                pr="https://github.com/org/repo/pull/1",
                            )
                        ),
                        json.dumps(
                            self.event(
                                "E-002",
                                type="pr_merged",
                                issue="G2PR-001",
                                pr="https://github.com/org/repo/pull/1",
                                merge_commit=HEAD_SHA,
                            )
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
                            self.event(
                                "E-001",
                                type="issue_status_changed",
                                issue="G2PR-001",
                                status="RUNNING",
                            )
                        ),
                        json.dumps(
                            self.event(
                                "E-001",
                                type="issue_status_changed",
                                issue="G2PR-001",
                                status="PR_READY",
                            )
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
