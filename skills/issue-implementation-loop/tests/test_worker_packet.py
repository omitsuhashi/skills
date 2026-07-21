from __future__ import annotations

from _helpers import *


class WorkerPacketTests(unittest.TestCase):
    def test_build_worker_packet_outputs_valid_v3_bounded_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope, runtime, issue_source = write_binding_sources(repo, binding)
            packet_path = repo / "worker-packet.json"

            result = run_script(
                "build_worker_packet.py",
                "--epic-id",
                "approved-spec-binding",
                "--issue-id",
                "ASBC-002",
                "--issue-title",
                "Propagate approved binding",
                "--dispatch-id",
                "dispatch-001",
                "--branch",
                "codex/approved-spec-binding/ASBC-002-workers",
                "--worktree",
                str(repo),
                "--task-kind",
                "implement",
                "--access-mode",
                "read_write",
                "--write-scope",
                "path:skills/issue-implementation-loop",
                "--read-path",
                "knowledge/wiki/syntheses/spec.md",
                "--read-purpose",
                "spec",
                "--read-path",
                "knowledge/wiki/syntheses/issues.md",
                "--read-purpose",
                "issue-ledger",
                "--source-envelope",
                str(envelope),
                "--source-runtime",
                str(runtime),
                "--source-issue",
                str(issue_source),
                "--summary",
                "Propagate one approved binding through the dispatch packet.",
                "--acceptance",
                "Reject mismatched worker projections.",
                "--verification",
                "python3 -m unittest discover -s skills/issue-implementation-loop/tests",
                "--stop-condition",
                "Stop before remote writes.",
                "--inline-excerpt",
                "knowledge/wiki/syntheses/issues.md::ASBC-002 requires binding propagation.",
                "--output",
                str(packet_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            validate_result = run_script("validate_worker_packet.py", str(packet_path))
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["schema_version"], 3)
            self.assertEqual(packet["source_revision"]["approved_spec_binding"], binding)
            self.assertEqual(packet["task_kind"], "implement")
            self.assertEqual(packet["access_mode"], "read_write")
            self.assertEqual(packet["context_policy"]["hard_max_packet_words"], 800)
            self.assertEqual(len(packet["read_paths"]), 2)

    def test_builder_has_no_schema_version_compatibility_option(self) -> None:
        result = run_script("build_worker_packet.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--schema-version", result.stdout)

    def test_worker_packet_budget_overflow_fails_without_truncating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope, runtime, issue_source = write_binding_sources(repo, binding)
            packet_path = repo / "overflow.json"
            long_summary = " ".join(f"word{i}" for i in range(451))
            result = run_script(
                "build_worker_packet.py",
                "--epic-id",
                "approved-spec-binding",
                "--issue-id",
                "ASBC-002",
                "--issue-title",
                "Propagate approved binding",
                "--dispatch-id",
                "dispatch-002",
                "--branch",
                "codex/approved-spec-binding/ASBC-002-workers",
                "--worktree",
                str(repo),
                "--write-scope",
                "path:skills/issue-implementation-loop",
                "--read-path",
                "knowledge/wiki/syntheses/spec.md",
                "--source-envelope",
                str(envelope),
                "--source-runtime",
                str(runtime),
                "--source-issue",
                str(issue_source),
                "--summary",
                long_summary,
                "--acceptance",
                "Reject overflow.",
                "--verification",
                "python3 -m unittest",
                "--stop-condition",
                "Stop before remote writes.",
                "--output",
                str(packet_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PACKET_CONTEXT_BUDGET_EXCEEDED", result.stderr)
            self.assertFalse(packet_path.exists())

    def test_worker_packet_v1_and_v2_are_unsupported_and_v1_schema_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            for version in (1, 2):
                with self.subTest(version=version):
                    packet = current_worker_packet(repo, binding)
                    packet["schema_version"] = version
                    path = repo / f"worker-v{version}.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path), "--json")
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
                    )
        self.assertFalse(
            (SKILL_DIR / "assets/schemas/worker-packet-v1.schema.json").exists()
        )

    def test_validate_worker_packet_rejects_full_text_and_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                (
                    "full_text",
                    lambda packet: packet.update({"full_spec_text": "full spec"}),
                    "full spec/full ledger text is forbidden",
                ),
                (
                    "top_level",
                    lambda packet: packet.update({"coordinator_notes": "extra"}),
                    "unknown field: coordinator_notes",
                ),
                (
                    "nested_task",
                    lambda packet: packet["task"].update({"notes": "extra"}),
                    "unknown field: task.notes",
                ),
                (
                    "session_compaction",
                    lambda packet: packet["context_policy"].update(
                        {"session_compaction": {"soft_trigger_percent": 65}}
                    ),
                    "unknown field: context_policy.session_compaction",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    mutate(packet)
                    packet_path = repo / f"{name}.json"
                    write_json(packet_path, packet)
                    result = run_script("validate_worker_packet.py", str(packet_path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_enforces_context_limits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
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
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    packet["context_policy"]["max_packet_words"] = 800
                    mutate(packet)
                    path = repo / f"{name}.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_enforces_task_kind_access_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                (
                    "implement_read_only",
                    "implement",
                    lambda packet: packet.update({"access_mode": "read_only"}),
                    "implement packets require access_mode=read_write",
                ),
                (
                    "fix_empty_scope",
                    "fix",
                    lambda packet: packet.update({"write_scope": []}),
                    "fix packets require a non-empty write_scope",
                ),
                (
                    "review_read_write",
                    "review",
                    lambda packet: packet.update({"access_mode": "read_write"}),
                    "review packets require access_mode=read_only",
                ),
                (
                    "inspect_write_scope",
                    "inspect",
                    lambda packet: packet.update({"write_scope": ["path:skills"]}),
                    "inspect packets require write_scope=[]",
                ),
            ]
            for name, task_kind, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding, task_kind=task_kind)
                    mutate(packet)
                    path = repo / f"{name}.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_rejects_worktree_external_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                (
                    "read_path",
                    lambda packet: packet["read_paths"][0].update({"path": "../outside.md"}),
                    "read_paths[0].path must stay within worktree",
                ),
                (
                    "write_scope",
                    lambda packet: packet.update({"write_scope": ["path:../outside"]}),
                    "write_scope[0] must stay within worktree",
                ),
                (
                    "inline_context",
                    lambda packet: packet.update(
                        {"inline_context": [{"path": "../issues.md", "excerpt": "short"}]}
                    ),
                    "inline_context[0].path must stay within worktree",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    mutate(packet)
                    path = repo / f"{name}.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validate_worker_packet_rejects_stale_source_revisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("envelope", "runtime", "issue"):
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    source = packet["source_revision"]
                    if name == "envelope":
                        path = Path(source["execution_envelope"]["path"])
                        value = json.loads(path.read_text(encoding="utf-8"))
                        value["revision"] = 2
                        write_json(path, value)
                        expected = "source_revision.execution_envelope.revision is stale"
                    elif name == "runtime":
                        path = Path(source["runtime_state"]["path"])
                        value = json.loads(path.read_text(encoding="utf-8"))
                        value["envelope_revision"] = 2
                        write_json(path, value)
                        expected = "source_revision.runtime_state.envelope_revision is stale"
                    else:
                        Path(source["issue_source"]["path"]).write_text("changed", encoding="utf-8")
                        expected = "source_revision.issue_source.sha256 is stale"
                    packet_path = repo / f"{name}.json"
                    write_json(packet_path, packet)
                    result = run_script("validate_worker_packet.py", str(packet_path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_asb_10_11_worker_projection_missing_and_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, expected in (
                ("missing", "PROJECTION_MISSING"),
                ("drift", "PROJECTION_MISMATCH"),
            ):
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    dispatch_path = repo / "worker.json"
                    write_json(dispatch_path, packet)
                    bound_packet = repo / binding["path"]
                    if name == "missing":
                        bound_packet.unlink()
                    else:
                        bound_packet.write_bytes(bound_packet.read_bytes() + b"\n")
                    result = run_script(
                        "validate_worker_packet.py", str(dispatch_path), "--json"
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout)["errors"], [expected])

    def test_asb_12_worker_packet_rejects_runtime_binding_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for task_kind in ("implement", "review"):
                with self.subTest(task_kind=task_kind):
                    case_root = root / task_kind
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding, task_kind=task_kind)
                    runtime_path = Path(packet["source_revision"]["runtime_state"]["path"])
                    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
                    runtime["approved_spec_binding"]["sha256"] = "a" * 64
                    write_json(runtime_path, runtime)
                    packet["source_revision"]["runtime_state"]["sha256"] = hashlib.sha256(
                        runtime_path.read_bytes()
                    ).hexdigest()
                    path = repo / "binding-mismatch.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path), "--json")
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
                    )

    def test_worker_packet_schema_template_and_envelope_are_current(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets/schemas/worker-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        template = json.loads(
            (SKILL_DIR / "assets/templates/worker-packet.json").read_text(
                encoding="utf-8"
            )
        )
        envelope_template = json.loads(
            (SKILL_DIR / "assets/templates/execution-envelope.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 3)
        self.assertIn(
            "approved_spec_binding",
            schema["properties"]["source_revision"]["required"],
        )
        self.assertEqual(template["schema_version"], 3)
        self.assertEqual(envelope_template["schema_version"], 4)
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(template["context_policy"]["hard_max_packet_words"], 800)

    def test_worker_packet_rejects_session_level_hardening_decision_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                ("top", lambda p: p.update({"hardening_candidates": []}), "unknown field: hardening_candidates"),
                ("task", lambda p: p["task"].update({"candidate_decisions": []}), "unknown field: task.candidate_decisions"),
                (
                    "context",
                    lambda p: p["context_policy"].update(
                        {"candidate_registry_path": "decisions/hardening-candidates.json"}
                    ),
                    "unknown field: context_policy.candidate_registry_path",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    mutate(packet)
                    path = repo / f"{name}.json"
                    write_json(path, packet)
                    result = run_script("validate_worker_packet.py", str(path))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_worker_contract_points_to_current_packet_tools_and_binding(self) -> None:
        contract = (SKILL_DIR / "references/worker-contract.md").read_text(encoding="utf-8")
        for required in (
            "assets/templates/worker-packet.json",
            "assets/schemas/worker-packet.schema.json",
            "scripts/build_worker_packet.py",
            "scripts/validate_worker_packet.py",
            "PACKET_CONTEXT_BUDGET_EXCEEDED",
            "task_kind",
            "access_mode",
            "source_revision.approved_spec_binding",
            "Worker Packet v3",
            "Worker Report v2",
        ):
            self.assertIn(required, contract)
        self.assertNotIn("worker-packet-v1.schema.json", contract)
        self.assertNotIn("remains readable", contract)


if __name__ == "__main__":
    unittest.main()
