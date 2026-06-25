from __future__ import annotations

from _helpers import *


class WorkerPacketTests(unittest.TestCase):
    def test_build_worker_packet_outputs_valid_bounded_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "worker-packet.json"

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
                "/tmp/skills/G2PR-004-worker-packet-budget",
                "--write-scope",
                "path:skills/issue-implementation-loop/scripts/build_worker_packet.py",
                "--read-path",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-spec.md",
                "--read-path",
                "knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md",
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
            self.assertEqual(packet["context_policy"]["max_packet_words"], 450)
            self.assertEqual(packet["context_policy"]["hard_max_packet_words"], 800)
            self.assertEqual(len(packet["read_paths"]), 2)

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
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["properties"]["task"]["additionalProperties"])
        self.assertEqual(packet_template["context_policy"]["hard_max_packet_words"], 800)
        context_schema = envelope_schema["properties"]["context_policy"]["properties"]
        self.assertIn("worker_packet_schema", context_schema)
        self.assertIn("worker_packet_template", context_schema)
        self.assertIn("worker_packet_validator", context_schema)
        self.assertEqual(
            envelope_template["context_policy"]["worker_packet_schema"],
            "assets/schemas/worker-packet.schema.json",
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


if __name__ == "__main__":
    unittest.main()
