from __future__ import annotations

from _helpers import *


class WorkerPacketTests(unittest.TestCase):
    def write_v2_sources(self, root: Path) -> tuple[Path, Path, Path]:
        (root / "knowledge" / "wiki" / "syntheses").mkdir(parents=True, exist_ok=True)
        issue_source = root / "knowledge" / "wiki" / "syntheses" / "issues.md"
        envelope = root / "execution-envelope.json"
        runtime = root / "runtime-state.json"
        issue_source.write_text("## G2PR-004\nNormalize worker packet.\n", encoding="utf-8")
        write_json(envelope, {"schema_version": 1, "epic_id": "loop-skill-architecture-v3", "revision": 2})
        write_json(
            runtime,
            {
                "schema_version": 1,
                "epic_id": "loop-skill-architecture-v3",
                "envelope_revision": 2,
                "issues": {},
                "human_requests": [],
            },
        )
        return envelope, runtime, issue_source

    def test_build_worker_packet_outputs_valid_v2_bounded_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            root.mkdir()
            envelope, runtime, issue_source = self.write_v2_sources(root)
            packet_path = root / "worker-packet.json"

            result = run_script(
                "build_worker_packet.py",
                "--epic-id",
                "loop-skill-architecture-v3",
                "--issue-id",
                "G2PR-004",
                "--issue-title",
                "Normalize worker packet",
                "--dispatch-id",
                "dispatch-001",
                "--branch",
                "codex/loop-skill-architecture-v3/G2PR-004-worker-packet-budget",
                "--worktree",
                str(root),
                "--task-kind",
                "implement",
                "--access-mode",
                "read_write",
                "--write-scope",
                "path:skills/issue-implementation-loop/scripts/build_worker_packet.py",
                "--read-path",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md",
                "--read-purpose",
                "spec",
                "--read-path",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md",
                "--read-purpose",
                "issue-ledger",
                "--source-envelope",
                str(envelope),
                "--source-runtime",
                str(runtime),
                "--source-issue",
                str(issue_source),
                "--summary",
                "Add paths-first worker dispatch packet generation and validation.",
                "--acceptance",
                "Reject context budget overflow without truncating packet text.",
                "--verification",
                "python3 -m unittest discover -s skills/issue-implementation-loop/tests",
                "--stop-condition",
                "Stop before remote writes.",
                "--inline-excerpt",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md::G2PR-004 requires a schema, template, builder, and validator.",
                "--output",
                str(packet_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(packet_path.exists())

            validate_result = run_script("validate_worker_packet.py", str(packet_path))

            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["schema_version"], 2)
            self.assertEqual(packet["task_kind"], "implement")
            self.assertEqual(packet["access_mode"], "read_write")
            self.assertEqual(packet["source_revision"]["execution_envelope"]["revision"], 2)
            self.assertEqual(packet["source_revision"]["runtime_state"]["envelope_revision"], 2)
            self.assertIn("sha256", packet["source_revision"]["issue_source"])
            self.assertEqual(packet["context_policy"]["max_packet_words"], 450)
            self.assertEqual(packet["context_policy"]["hard_max_packet_words"], 800)
            self.assertEqual(len(packet["read_paths"]), 2)
            self.assertEqual(packet["read_paths"][0]["purpose"], "spec")

    def test_worker_packet_budget_overflow_fails_without_truncating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "overflow.json"
            long_summary = " ".join(f"word{i}" for i in range(451))

            result = run_script(
                "build_worker_packet.py",
                "--epic-id",
                "loop-skill-architecture-v3",
                "--issue-id",
                "G2PR-004",
                "--issue-title",
                "Normalize worker packet",
                "--dispatch-id",
                "dispatch-002",
                "--branch",
                "codex/loop-skill-architecture-v3/G2PR-004-worker-packet-budget",
                "--worktree",
                "/tmp/skills/G2PR-004-worker-packet-budget",
                "--schema-version",
                "1",
                "--write-scope",
                "path:skills/issue-implementation-loop/scripts/build_worker_packet.py",
                "--read-path",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md",
                "--summary",
                long_summary,
                "--acceptance",
                "Reject overflow.",
                "--verification",
                "python3 -m unittest discover -s skills/issue-implementation-loop/tests",
                "--stop-condition",
                "Stop before remote writes.",
                "--output",
                str(packet_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PACKET_CONTEXT_BUDGET_EXCEEDED", result.stderr)
            self.assertFalse(packet_path.exists())

    def test_v1_worker_packet_remains_valid_for_existing_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "packet-v1.json"
            write_json(packet_path, valid_worker_packet())

            result = run_script("validate_worker_packet.py", str(packet_path))

            self.assertEqual(result.returncode, 0, result.stderr)
            v1_schema = json.loads(
                (SKILL_DIR / "assets" / "schemas" / "worker-packet-v1.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(v1_schema["properties"]["schema_version"]["const"], 1)

    def test_validate_worker_packet_rejects_full_spec_and_ledger_text_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet = valid_worker_packet()
            packet["full_spec_text"] = "Do not paste the full spec here."
            packet["task"]["full_ledger_text"] = "Do not paste the full ledger here."
            packet_path = Path(tmp) / "packet.json"
            write_json(packet_path, packet)

            result = run_script("validate_worker_packet.py", str(packet_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("full spec/full ledger text is forbidden", result.stderr)

    def test_validate_worker_packet_rejects_unknown_top_level_and_nested_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                (
                    "top_level",
                    lambda packet: packet.update({"coordinator_notes": "extra context"}),
                    "unknown field: coordinator_notes",
                ),
                (
                    "nested_task",
                    lambda packet: packet["task"].update({"notes": "extra context"}),
                    "unknown field: task.notes",
                ),
                (
                    "full_spec_bypass",
                    lambda packet: packet.update({"spec": {"text": "pasted full spec"}}),
                    "unknown field: spec",
                ),
                (
                    "full_ledger_bypass",
                    lambda packet: packet.update({"ledger": {"text": "pasted full ledger"}}),
                    "unknown field: ledger",
                ),
                (
                    "session_compaction",
                    lambda packet: packet["context_policy"].update(
                        {
                            "session_compaction": {
                                "soft_trigger_percent": 65,
                                "hard_stop_percent": 75,
                            }
                        }
                    ),
                    "unknown field: context_policy.session_compaction",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    packet = valid_worker_packet()
                    mutate(packet)
                    packet_path = Path(tmp) / f"{name}.json"
                    write_json(packet_path, packet)

                    result = run_script("validate_worker_packet.py", str(packet_path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_enforces_read_path_and_inline_excerpt_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                (
                    "read_paths",
                    lambda packet: packet.update(
                        {
                            "read_paths": [
                                {"path": f"knowledge/source-{index}.md", "purpose": "source"}
                                for index in range(9)
                            ]
                        }
                    ),
                    "read_paths must contain at most 8 paths",
                ),
                (
                    "per_file_excerpt",
                    lambda packet: packet.update(
                        {
                            "inline_context": [
                                {
                                    "path": "knowledge/wiki/syntheses/issues.md",
                                    "excerpt": " ".join(f"word{index}" for index in range(121)),
                                }
                            ]
                        }
                    ),
                    "exceeds 120 words",
                ),
                (
                    "total_inline_excerpt",
                    lambda packet: packet.update(
                        {
                            "inline_context": [
                                {
                                    "path": f"knowledge/source-{index}.md",
                                    "excerpt": " ".join(f"word{word}" for word in range(101)),
                                }
                                for index in range(3)
                            ]
                        }
                    ),
                    "inline_context exceeds 300 total words",
                ),
                (
                    "same_path_excerpt_total",
                    lambda packet: packet.update(
                        {
                            "inline_context": [
                                {
                                    "path": "knowledge/wiki/syntheses/issues.md",
                                    "excerpt": " ".join(f"first{word}" for word in range(70)),
                                },
                                {
                                    "path": "knowledge/wiki/syntheses/issues.md",
                                    "excerpt": " ".join(f"second{word}" for word in range(70)),
                                },
                            ]
                        }
                    ),
                    "inline_context path knowledge/wiki/syntheses/issues.md exceeds 120 words",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    packet = valid_worker_packet()
                    packet["context_policy"]["max_packet_words"] = 800
                    mutate(packet)
                    packet_path = Path(tmp) / f"{name}.json"
                    write_json(packet_path, packet)

                    result = run_script("validate_worker_packet.py", str(packet_path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_v2_enforces_task_kind_access_mode_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            root.mkdir()
            source_paths = self.write_v2_sources(root)
            cases = [
                (
                    "implement_read_only",
                    lambda packet: packet.update({"access_mode": "read_only"}),
                    "implement packets require access_mode=read_write",
                ),
                (
                    "fix_empty_write_scope",
                    lambda packet: packet.update({"task_kind": "fix", "write_scope": []}),
                    "fix packets require a non-empty write_scope",
                ),
                (
                    "review_read_write",
                    lambda packet: packet.update({"task_kind": "review", "access_mode": "read_write"}),
                    "review packets require access_mode=read_only",
                ),
                (
                    "inspect_write_scope",
                    lambda packet: packet.update({"task_kind": "inspect", "access_mode": "read_only"}),
                    "inspect packets require write_scope=[]",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    packet = valid_worker_packet_v2(root, *source_paths)
                    mutate(packet)
                    packet_path = root / f"{name}.json"
                    write_json(packet_path, packet)

                    result = run_script("validate_worker_packet.py", str(packet_path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

            review_packet = valid_worker_packet_v2(root, *source_paths)
            review_packet["task_kind"] = "review"
            review_packet["access_mode"] = "read_only"
            review_packet["write_scope"] = []
            review_path = root / "review.json"
            write_json(review_path, review_packet)

            result = run_script("validate_worker_packet.py", str(review_path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_worker_packet_v2_rejects_path_traversal_and_worktree_external_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            root.mkdir()
            source_paths = self.write_v2_sources(root)
            outside = Path(tmp) / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            cases = [
                (
                    "read_path_traversal",
                    lambda packet: packet["read_paths"][0].update({"path": "../outside.md"}),
                    "read_paths[0].path must stay within worktree",
                ),
                (
                    "read_path_external_absolute",
                    lambda packet: packet["read_paths"][0].update({"path": str(outside)}),
                    "read_paths[0].path must stay within worktree",
                ),
                (
                    "write_scope_traversal",
                    lambda packet: packet.update({"write_scope": ["path:../outside"]}),
                    "write_scope[0] must stay within worktree",
                ),
                (
                    "inline_context_traversal",
                    lambda packet: packet.update(
                        {"inline_context": [{"path": "../issues.md", "excerpt": "short"}]}
                    ),
                    "inline_context[0].path must stay within worktree",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    packet = valid_worker_packet_v2(root, *source_paths)
                    mutate(packet)
                    packet_path = root / f"{name}.json"
                    write_json(packet_path, packet)

                    result = run_script("validate_worker_packet.py", str(packet_path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_v2_rejects_stale_source_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worktree"
            root.mkdir()
            envelope, runtime, issue_source = self.write_v2_sources(root)
            cases = [
                (
                    "envelope",
                    lambda: write_json(
                        envelope,
                        {
                            "schema_version": 1,
                            "epic_id": "loop-skill-architecture-v3",
                            "revision": 3,
                        },
                    ),
                    "source_revision.execution_envelope.revision is stale",
                ),
                (
                    "runtime",
                    lambda: write_json(
                        runtime,
                        {
                            "schema_version": 1,
                            "epic_id": "loop-skill-architecture-v3",
                            "envelope_revision": 3,
                            "issues": {},
                            "human_requests": [],
                        },
                    ),
                    "source_revision.runtime_state.envelope_revision is stale",
                ),
                (
                    "issue",
                    lambda: issue_source.write_text("changed", encoding="utf-8"),
                    "source_revision.issue_source.sha256 is stale",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name):
                    envelope, runtime, issue_source = self.write_v2_sources(root)
                    packet = valid_worker_packet_v2(root, envelope, runtime, issue_source)
                    mutate()
                    packet_path = root / f"{name}.json"
                    write_json(packet_path, packet)

                    result = run_script("validate_worker_packet.py", str(packet_path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_worker_packet_schema_template_and_envelope_context_policy_are_linked(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets" / "schemas" / "worker-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        packet_template = json.loads(
            (SKILL_DIR / "assets" / "templates" / "worker-packet.json").read_text(
                encoding="utf-8"
            )
        )
        envelope_schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        envelope_template = json.loads(
            (SKILL_DIR / "assets" / "templates" / "execution-envelope.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(schema["properties"]["context_policy"]["properties"]["max_packet_words"]["default"], 450)
        self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["task"]["additionalProperties"])
        self.assertEqual(packet_template["schema_version"], 2)
        self.assertEqual(packet_template["context_policy"]["hard_max_packet_words"], 800)
        context_schema = envelope_schema["properties"]["context_policy"]["properties"]
        self.assertIn("worker_packet_schema", context_schema)
        self.assertIn("worker_packet_template", context_schema)
        self.assertIn("worker_packet_validator", context_schema)
        session_schema = context_schema["session_compaction"]
        self.assertEqual(session_schema["properties"]["soft_trigger_percent"]["const"], 65)
        self.assertEqual(session_schema["properties"]["hard_stop_percent"]["const"], 75)
        self.assertEqual(
            envelope_template["context_policy"]["worker_packet_schema"],
            "assets/schemas/worker-packet.schema.json",
        )
        self.assertEqual(
            envelope_template["context_policy"]["session_compaction"]["soft_trigger_percent"],
            65,
        )

    def test_worker_contract_points_workers_to_normalized_packet_tools(self) -> None:
        worker_contract = (SKILL_DIR / "references" / "worker-contract.md").read_text(
            encoding="utf-8"
        )

        for required in (
            "assets/templates/worker-packet.json",
            "assets/schemas/worker-packet.schema.json",
            "scripts/build_worker_packet.py",
            "scripts/validate_worker_packet.py",
            "PACKET_CONTEXT_BUDGET_EXCEEDED",
            "task_kind",
            "access_mode",
            "source_revision",
        ):
            self.assertIn(required, worker_contract)


def valid_worker_packet() -> dict:
    return {
        "schema_version": 1,
        "packet_type": "issue_worker_dispatch",
        "epic_id": "loop-skill-architecture-v3",
        "issue_id": "G2PR-004",
        "issue_title": "Normalize worker packet",
        "dispatch_id": "dispatch-valid",
        "branch": "codex/loop-skill-architecture-v3/G2PR-004-worker-packet-budget",
        "worktree": "/tmp/skills/G2PR-004-worker-packet-budget",
        "write_scope": ["path:skills/issue-implementation-loop"],
        "context_policy": {
            "paths_first": True,
            "max_packet_words": 450,
            "hard_max_packet_words": 800,
            "max_read_paths": 8,
            "max_inline_excerpt_words_per_file": 120,
            "max_inline_excerpt_words_total": 300,
            "include_full_spec_text": False,
            "include_full_ledger_text": False,
        },
        "read_paths": [
            {
                "path": "knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md",
                "purpose": "spec",
            }
        ],
        "inline_context": [],
        "task": {
            "summary": "Add a worker packet builder and validator.",
            "acceptance_criteria": ["Budget overflow fails."],
            "verification": ["python3 -m unittest discover -s skills/issue-implementation-loop/tests"],
            "stop_conditions": ["Stop before remote writes."],
        },
        "report_contract": {
            "format": "worker-report.json",
            "validator": "skills/issue-implementation-loop/scripts/validate_worker_report.py",
        },
    }


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_worker_packet_v2(
    root: Path,
    envelope: Path,
    runtime: Path,
    issue_source: Path,
) -> dict:
    return {
        "schema_version": 2,
        "packet_type": "issue_worker_dispatch",
        "task_kind": "implement",
        "access_mode": "read_write",
        "source_revision": {
            "execution_envelope": {
                "path": str(envelope),
                "revision": 2,
                "sha256": _sha256(envelope),
            },
            "runtime_state": {
                "path": str(runtime),
                "envelope_revision": 2,
                "sha256": _sha256(runtime),
            },
            "issue_source": {
                "path": str(issue_source),
                "sha256": _sha256(issue_source),
            },
        },
        "epic_id": "loop-skill-architecture-v3",
        "issue_id": "G2PR-004",
        "issue_title": "Normalize worker packet",
        "dispatch_id": "dispatch-valid",
        "branch": "codex/loop-skill-architecture-v3/G2PR-004-worker-packet-budget",
        "worktree": str(root),
        "write_scope": ["path:skills/issue-implementation-loop"],
        "context_policy": {
            "paths_first": True,
            "max_packet_words": 450,
            "hard_max_packet_words": 800,
            "max_read_paths": 8,
            "max_inline_excerpt_words_per_file": 120,
            "max_inline_excerpt_words_total": 300,
            "include_full_spec_text": False,
            "include_full_ledger_text": False,
        },
        "read_paths": [
            {
                "path": "knowledge/wiki/syntheses/issues.md",
                "purpose": "issue-ledger",
            }
        ],
        "inline_context": [],
        "task": {
            "summary": "Add a worker packet builder and validator.",
            "acceptance_criteria": ["Budget overflow fails."],
            "verification": ["python3 -m unittest discover -s skills/issue-implementation-loop/tests"],
            "stop_conditions": ["Stop before remote writes."],
        },
        "report_contract": {
            "format": "worker-report.json",
            "validator": "skills/issue-implementation-loop/scripts/validate_worker_report.py",
        },
    }


if __name__ == "__main__":
    unittest.main()
