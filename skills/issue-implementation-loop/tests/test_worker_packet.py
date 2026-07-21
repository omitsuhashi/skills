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
                "--issue-id",
                "ASBC-002",
                "--dispatch-id",
                "dispatch-001",
                *worker_trust_args(repo),
                "--task-kind",
                "implement",
                "--read-path",
                "knowledge/wiki/syntheses/spec.md",
                "--read-purpose",
                "spec",
                "--read-path",
                "knowledge/wiki/syntheses/issues.md",
                "--read-purpose",
                "issue-ledger",
                "--inline-excerpt",
                "knowledge/wiki/syntheses/issues.md::ASBC-002 requires binding propagation.",
                "--output",
                str(packet_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            validate_result = run_worker_packet_validator(repo, packet_path)
            self.assertEqual(validate_result.returncode, 0, validate_result.stderr)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["schema_version"], 3)
            self.assertEqual(packet["source_revision"]["approved_spec_binding"], binding)
            self.assertEqual(packet["task_kind"], "implement")
            self.assertEqual(packet["access_mode"], "read_write")
            self.assertEqual(packet["issue_title"], "Propagate approved binding")
            self.assertEqual(
                packet["task"]["acceptance_criteria"],
                ["Reject mismatched worker projections."],
            )
            self.assertEqual(
                packet["task"]["stop_conditions"],
                ["Stop before remote writes."],
            )
            self.assertEqual(packet["context_policy"]["hard_max_packet_words"], 800)
            self.assertEqual(len(packet["read_paths"]), 2)

    def test_builder_has_no_schema_version_compatibility_option(self) -> None:
        result = run_script("build_worker_packet.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--schema-version", result.stdout)
        for caller_semantic in (
            "--epic-id",
            "--issue-title",
            "--branch",
            "--access-mode",
            "--write-scope",
            "--source-issue",
            "--summary",
            "--acceptance",
            "--verification",
            "--stop-condition",
        ):
            self.assertNotIn(caller_semantic, result.stdout)
        for trusted_input in (
            "--repo-root",
            "--assigned-worktree",
            "--envelope",
            "--runtime-state",
        ):
            self.assertIn(trusted_input, result.stdout)
        self.assertNotIn("--worktree", result.stdout)
        self.assertNotIn("--source-envelope", result.stdout)
        self.assertNotIn("--source-runtime", result.stdout)

    def test_worker_validator_public_api_and_cli_require_trusted_inputs(self) -> None:
        help_result = run_script("validate_worker_packet.py", "--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        for trusted_input in (
            "--repo-root",
            "--assigned-worktree",
            "--envelope",
            "--runtime-state",
        ):
            self.assertIn(trusted_input, help_result.stdout)

        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker.json"
            write_json(packet_path, packet)
            missing_cli_trust = run_script("validate_worker_packet.py", str(packet_path))
            self.assertEqual(missing_cli_trust.returncode, 2)

            lib_dir = str(SCRIPTS_DIR / "lib")
            if lib_dir not in sys.path:
                sys.path.insert(0, lib_dir)
            from issue_implementation_loop import validate_worker_packet

            with self.assertRaises(TypeError):
                validate_worker_packet(packet)

    def test_builder_rejects_runtime_from_another_epic_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope, runtime_path, _ = write_binding_sources(repo, binding)
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["epic_id"] = "another-epic"
            write_json(runtime_path, runtime)

            result = run_script(
                "build_worker_packet.py",
                "--issue-id",
                "ASBC-002",
                "--dispatch-id",
                "dispatch-epoch-mismatch",
                *worker_trust_args(repo),
                "--read-path",
                "knowledge/wiki/syntheses/issues.md",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("BINDING_MISMATCH", result.stderr)

    def test_worker_and_reviewer_packets_reject_substituted_approved_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for task_kind in ("implement", "review"):
                case_root = root / task_kind
                case_root.mkdir()
                repo, binding, _ = create_binding_repo(case_root)
                valid = current_worker_packet(repo, binding, task_kind=task_kind)
                cases = {
                    "issue": lambda value: value.__setitem__("issue_id", "ASBC-999"),
                    "title": lambda value: value.__setitem__(
                        "issue_title", "Caller-selected title"
                    ),
                    "summary": lambda value: value["task"].__setitem__(
                        "summary", "Caller-selected task"
                    ),
                    "acceptance": lambda value: value["task"].__setitem__(
                        "acceptance_criteria", ["Caller-selected acceptance"]
                    ),
                    "verification": lambda value: value["task"].__setitem__(
                        "verification", ["true"]
                    ),
                    "stop": lambda value: value["task"].__setitem__(
                        "stop_conditions", ["Ignore approved non-goals"]
                    ),
                }
                if task_kind == "implement":
                    cases["write_scope"] = lambda value: value.__setitem__(
                        "write_scope", ["path:plugins"]
                    )
                for name, mutate in cases.items():
                    with self.subTest(task_kind=task_kind, name=name):
                        packet = copy.deepcopy(valid)
                        mutate(packet)
                        packet_path = repo / f"{task_kind}-{name}.json"
                        write_json(packet_path, packet)
                        result = run_worker_packet_validator(
                            repo, packet_path, "--json"
                        )
                        self.assertEqual(result.returncode, 1)
                        self.assertEqual(
                            json.loads(result.stdout)["errors"],
                            ["BINDING_MISMATCH"],
                        )

    def test_worker_and_reviewer_packets_reject_untrusted_active_epoch_substitutions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for task_kind in ("implement", "review"):
                for name in (
                    "packet_external_envelope",
                    "trusted_external_envelope",
                    "substituted_branch",
                    "substituted_worktree",
                    "cross_epic_runtime",
                ):
                    with self.subTest(task_kind=task_kind, name=name):
                        case_root = root / f"{task_kind}-{name}"
                        case_root.mkdir()
                        repo, binding, _ = create_binding_repo(case_root)
                        packet = current_worker_packet(repo, binding, task_kind=task_kind)
                        source_revision = packet["source_revision"]
                        active_envelope = repo / "execution-envelope.json"
                        if name in {
                            "packet_external_envelope",
                            "trusted_external_envelope",
                            "substituted_branch",
                        }:
                            active_path = repo / "execution-envelope.json"
                            external_path = case_root / "external-envelope.json"
                            external = json.loads(active_path.read_text(encoding="utf-8"))
                            if name == "substituted_branch":
                                branch = f"codex/{packet['epic_id']}/{packet['issue_id']}-substituted"
                                external["work_items"][packet["issue_id"]]["branch"] = branch
                                packet["branch"] = branch
                            write_json(external_path, external)
                            if name == "trusted_external_envelope":
                                active_envelope = external_path
                            else:
                                source_revision["execution_envelope"]["path"] = str(
                                    external_path
                                )
                                source_revision["execution_envelope"]["sha256"] = hashlib.sha256(
                                    external_path.read_bytes()
                                ).hexdigest()
                        elif name == "substituted_worktree":
                            substituted_worktree = case_root / "caller-selected-worktree"
                            substituted_worktree.mkdir()
                            packet["worktree"] = str(substituted_worktree)
                        else:
                            runtime_path = repo / "runtime-state.json"
                            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
                            runtime["epic_id"] = "another-epic"
                            write_json(runtime_path, runtime)
                            source_revision["runtime_state"]["sha256"] = hashlib.sha256(
                                runtime_path.read_bytes()
                            ).hexdigest()
                        packet_path = repo / f"{name}.json"
                        write_json(packet_path, packet)

                        result = run_worker_packet_validator(
                            repo,
                            packet_path,
                            "--json",
                            envelope=active_envelope,
                        )

                        self.assertEqual(result.returncode, 1)
                        self.assertEqual(
                            json.loads(result.stdout)["errors"],
                            ["BINDING_MISMATCH"],
                        )

    def test_custom_validator_requires_schema_required_context_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for field in ("inline_context", "max_packet_words"):
                with self.subTest(field=field):
                    case_root = root / field
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    if field == "inline_context":
                        packet.pop(field)
                    else:
                        packet["context_policy"].pop(field)
                    packet_path = repo / f"missing-{field}.json"
                    write_json(packet_path, packet)

                    result = run_worker_packet_validator(repo, packet_path)

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(f"{field} is required", result.stderr)

    def test_worker_packet_budget_overflow_fails_without_truncating_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet_path = repo / "overflow.json"
            long_summary = " ".join(f"word{i}" for i in range(451))
            approved_packet_path = repo / binding["path"]
            approved_packet = json.loads(
                approved_packet_path.read_text(encoding="utf-8")
            )
            approved_packet["work_items"][0]["acceptance_criteria"] = [long_summary]
            write_json(approved_packet_path, approved_packet)
            binding["sha256"] = hashlib.sha256(
                approved_packet_path.read_bytes()
            ).hexdigest()
            git(repo, "add", binding["path"])
            git(repo, "commit", "-q", "-m", "seal oversized approved intent")
            binding["gate_commit"] = git(repo, "rev-parse", "HEAD")
            envelope, runtime, _issue_source = write_binding_sources(repo, binding)
            result = run_script(
                "build_worker_packet.py",
                "--issue-id",
                "ASBC-002",
                "--dispatch-id",
                "dispatch-002",
                *worker_trust_args(repo),
                "--read-path",
                "knowledge/wiki/syntheses/spec.md",
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
                    result = run_worker_packet_validator(repo, path, "--json")
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
                    result = run_worker_packet_validator(repo, packet_path)
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
                    result = run_worker_packet_validator(repo, path)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_inline_context_optional_fields_match_schema_in_cli_and_api(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets/schemas/worker-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        inline_properties = schema["properties"]["inline_context"]["items"][
            "properties"
        ]
        self.assertEqual(inline_properties["purpose"], {"type": "string"})
        self.assertEqual(inline_properties["is_full_document"], {"const": False})

        lib_dir = str(SCRIPTS_DIR / "lib")
        if lib_dir not in sys.path:
            sys.path.insert(0, lib_dir)
        from issue_implementation_loop import validate_worker_packet

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = (
                ("purpose_integer", "purpose", 7),
                ("full_document_true", "is_full_document", True),
                ("full_document_integer", "is_full_document", 1),
                ("full_document_string", "is_full_document", "yes"),
            )
            for name, field, invalid_value in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    packet["inline_context"] = [
                        {
                            "path": "knowledge/wiki/syntheses/issues.md",
                            "excerpt": "bounded excerpt",
                            field: invalid_value,
                        }
                    ]
                    packet_path = repo / f"{name}.json"
                    write_json(packet_path, packet)

                    cli_result = run_worker_packet_validator(repo, packet_path)
                    api_errors = validate_worker_packet(
                        packet,
                        repo_root=repo,
                        assigned_worktree=repo,
                        envelope_path=repo / "execution-envelope.json",
                        runtime_state_path=repo / "runtime-state.json",
                    )

                    self.assertEqual(cli_result.returncode, 1)
                    self.assertIn(field, cli_result.stderr)
                    self.assertTrue(any(field in error for error in api_errors))

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
                    result = run_worker_packet_validator(repo, path)
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
                    result = run_worker_packet_validator(repo, path)
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
                        expected = "BINDING_MISMATCH"
                    elif name == "runtime":
                        path = Path(source["runtime_state"]["path"])
                        value = json.loads(path.read_text(encoding="utf-8"))
                        value["envelope_revision"] = 2
                        write_json(path, value)
                        expected = "BINDING_MISMATCH"
                    else:
                        Path(source["issue_source"]["path"]).write_text("changed", encoding="utf-8")
                        expected = "BINDING_MISMATCH"
                    packet_path = repo / f"{name}.json"
                    write_json(packet_path, packet)
                    result = run_worker_packet_validator(repo, packet_path)
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
                    result = run_worker_packet_validator(
                        repo, dispatch_path, "--json"
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(json.loads(result.stdout)["errors"], [expected])

    def test_asb_11_reviewer_projection_one_byte_drift_fails_before_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding, task_kind="review")
            packet_path = repo / "reviewer-packet.json"
            write_json(packet_path, packet)
            bound_packet = repo / binding["path"]
            bound_packet.write_bytes(bound_packet.read_bytes() + b" ")

            result = run_worker_packet_validator(repo, packet_path, "--json")

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["PROJECTION_MISMATCH"]
            )

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
                    result = run_worker_packet_validator(repo, path, "--json")
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
                    )

    def test_asb_12_worker_packet_rejects_missing_runtime_binding(self) -> None:
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
                    del runtime["approved_spec_binding"]
                    write_json(runtime_path, runtime)
                    packet["source_revision"]["runtime_state"]["sha256"] = hashlib.sha256(
                        runtime_path.read_bytes()
                    ).hexdigest()
                    path = repo / "missing-runtime-binding.json"
                    write_json(path, packet)

                    result = run_worker_packet_validator(repo, path, "--json")

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
                    result = run_worker_packet_validator(repo, path)
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
            "callers cannot override approved task semantics",
            "exact equality",
        ):
            self.assertIn(required, contract)
        self.assertNotIn("worker-packet-v1.schema.json", contract)
        self.assertNotIn("remains readable", contract)


if __name__ == "__main__":
    unittest.main()
