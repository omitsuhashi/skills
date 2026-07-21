from __future__ import annotations

from _helpers import *


class ValidationTests(unittest.TestCase):
    def test_asb_04_execution_envelope_v4_verifies_valid_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, gate_commit = create_binding_repo(Path(tmp))
            envelope_path = repo / "execution-envelope.json"
            write_json(envelope_path, binding_envelope(repo, binding))

            result = run_script(
                "validate_execution_envelope.py",
                str(envelope_path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["errors"], [])
            self.assertEqual(binding["gate_commit"], gate_commit)

    def test_execution_envelope_v1_through_v3_are_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for version in (1, 2, 3):
                with self.subTest(version=version):
                    envelope = base_envelope()
                    envelope["schema_version"] = version
                    path = Path(tmp) / f"envelope-v{version}.json"
                    write_json(path, envelope)
                    result = run_script(
                        "validate_execution_envelope.py", str(path), "--json"
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
                    )

    def test_asb_26_execution_envelope_requires_gate_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            del binding["gate_commit"]
            path = repo / "missing-gate.json"
            write_json(path, binding_envelope(repo, binding))

            result = run_script(
                "validate_execution_envelope.py",
                str(path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["GATE_COMMIT_MISSING"]
            )

    def test_asb_27_execution_envelope_rejects_non_ancestor_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, gate_commit = create_binding_repo(Path(tmp))
            base_commit = git(repo, "rev-parse", f"{gate_commit}^")
            packet_bytes = (repo / binding["path"]).read_bytes()
            spec_bytes = (repo / "knowledge/wiki/syntheses/spec.md").read_bytes()
            git(repo, "checkout", "-q", "-b", "side", base_commit)
            synthesis = repo / "knowledge/wiki/syntheses"
            synthesis.mkdir(parents=True)
            (synthesis / "spec.md").write_bytes(spec_bytes)
            (synthesis / "issues.md").write_text("# Issues\n", encoding="utf-8")
            (repo / binding["path"]).write_bytes(packet_bytes)
            git(repo, "add", "knowledge")
            git(repo, "commit", "-q", "-m", "side projection")
            target = git(repo, "rev-parse", "HEAD")
            path = repo / "not-ancestor.json"
            write_json(path, binding_envelope(repo, binding, target))

            result = run_script(
                "validate_execution_envelope.py",
                str(path),
                "--repo-root",
                str(repo),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["GATE_COMMIT_NOT_ANCESTOR"]
            )

    def test_asb_28_execution_envelope_rejects_gate_tree_blob_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for changed_path in ("input-packet", "spec"):
                with self.subTest(changed_path=changed_path):
                    case_root = root / changed_path
                    case_root.mkdir()
                    repo, binding, gate_commit = create_binding_repo(case_root)
                    if changed_path == "input-packet":
                        packet_path = repo / binding["path"]
                        packet_path.write_bytes(packet_path.read_bytes() + b"\n")
                        binding["sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
                    else:
                        spec_path = repo / "knowledge/wiki/syntheses/spec.md"
                        spec_path.write_text("new approved spec\n", encoding="utf-8")
                        packet_path = repo / binding["path"]
                        packet = json.loads(packet_path.read_text(encoding="utf-8"))
                        packet["spec_binding"]["sha256"] = hashlib.sha256(
                            spec_path.read_bytes()
                        ).hexdigest()
                        write_json(packet_path, packet)
                        binding["sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
                    git(repo, "add", "knowledge")
                    git(repo, "commit", "-q", "-m", "new projection")
                    binding["gate_commit"] = gate_commit
                    path = repo / "gate-blob-mismatch.json"
                    write_json(path, binding_envelope(repo, binding))

                    result = run_script(
                        "validate_execution_envelope.py",
                        str(path),
                        "--repo-root",
                        str(repo),
                        "--json",
                    )

                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"],
                        ["GATE_COMMIT_BLOB_MISMATCH"],
                    )

    def test_validate_execution_envelope_requires_context_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            del envelope["context_policy"]
            path = Path(tmp) / "missing-context-policy.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context_policy", result.stderr)

    def test_validate_input_packet_v2_rejects_closed_shape_and_binding_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            spec_path = repo / "knowledge/wiki/syntheses/spec.md"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text("spec\n", encoding="utf-8")
            issues_path = spec_path.with_name("issues.md")
            issues_path.write_text("issues\n", encoding="utf-8")
            linked_issues = spec_path.with_name("linked-issues.md")
            linked_issues.symlink_to(issues_path)
            outside = repo / "outside-target"
            outside.mkdir()
            (repo / "linked-outside").symlink_to(outside, target_is_directory=True)
            packet = current_input_packet(repo)
            cases = []
            v1 = base_packet()
            cases.append(("v1", v1, "SCHEMA_UNSUPPORTED"))
            missing_approval = copy.deepcopy(packet)
            del missing_approval["approval_evidence"]
            cases.append(("missing-approval", missing_approval, "APPROVAL_MISSING"))
            incomplete = copy.deepcopy(packet)
            incomplete["approval_evidence"]["scope"]["verification"] = False
            cases.append(("incomplete-scope", incomplete, "APPROVAL_SCOPE_INCOMPLETE"))
            malformed = copy.deepcopy(packet)
            malformed["spec_binding"]["sha256"] = "sha256:bad"
            cases.append(("malformed-hash", malformed, "DIGEST_MALFORMED"))
            unknown = copy.deepcopy(packet)
            unknown["unknown"] = True
            cases.append(("unknown-field", unknown, "SCHEMA_UNSUPPORTED"))
            empty = copy.deepcopy(packet)
            empty["work_items"] = []
            cases.append(("empty-work-items", empty, "SCHEMA_UNSUPPORTED"))
            malformed_item = copy.deepcopy(packet)
            malformed_item["work_items"][0]["id"] = 1
            cases.append(("malformed-item", malformed_item, "SCHEMA_UNSUPPORTED"))
            unsafe = copy.deepcopy(packet)
            unsafe["spec_binding"]["path"] = "../spec.md"
            cases.append(("unsafe-path", unsafe, "PATH_TRAVERSAL"))
            unsafe_source = copy.deepcopy(packet)
            unsafe_source["work_items"][0]["source"]["path"] = (
                "knowledge/wiki/syntheses/linked-issues.md"
            )
            cases.append(("unsafe-source", unsafe_source, "PATH_SYMLINK"))
            unsafe_scope = copy.deepcopy(packet)
            unsafe_scope["work_items"][0]["write_scope"] = [
                "path:linked-outside/file"
            ]
            cases.append(("unsafe-write-scope", unsafe_scope, "PATH_SYMLINK"))
            for index, timestamp in enumerate(
                (
                    "2026-07-21 17:55:36+09:00",
                    "2026-07-21T17:55:36+0900",
                    "2026-07-21T17:55:36",
                    "2026-07-21T17:55:36+09:60",
                )
            ):
                invalid_time = copy.deepcopy(packet)
                invalid_time["approval_evidence"]["approved_at"] = timestamp
                cases.append((f"invalid-time-{index}", invalid_time, "SCHEMA_UNSUPPORTED"))
            for name, value, expected in cases:
                path = repo / f"{name}.json"
                write_json(path, value)
                result = run_script(
                    "validate_input_packet.py",
                    str(path),
                    "--repo-root",
                    str(repo),
                    "--json",
                )
                self.assertNotEqual(result.returncode, 0, name)
                self.assertEqual(json.loads(result.stdout)["errors"][0], expected, name)

    def test_validate_input_packet_accepts_current_v2_closed_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            spec_path = repo / "knowledge/wiki/syntheses/spec.md"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text("spec\n", encoding="utf-8")
            spec_path.with_name("issues.md").write_text("issues\n", encoding="utf-8")
            path = repo / "packet.json"
            write_json(path, current_input_packet(repo))

            result = run_script("validate_input_packet.py", str(path), "--repo-root", str(repo))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_input_packet_runtime_rejects_whitespace_only_strings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            spec_path = repo / "knowledge/wiki/syntheses/spec.md"
            spec_path.parent.mkdir(parents=True)
            spec_path.write_text("spec\n", encoding="utf-8")
            spec_path.with_name("issues.md").write_text("issues\n", encoding="utf-8")
            packet = current_input_packet(repo)
            cases = []
            actor = copy.deepcopy(packet)
            actor["approval_evidence"]["actor_expression"] = "   "
            cases.append(("actor", actor))
            title = copy.deepcopy(packet)
            title["work_items"][0]["title"] = "\t"
            cases.append(("title", title))
            criterion = copy.deepcopy(packet)
            criterion["work_items"][0]["acceptance_criteria"] = ["  "]
            cases.append(("criterion", criterion))
            for name, value in cases:
                path = repo / f"{name}.json"
                write_json(path, value)
                result = run_script(
                    "validate_input_packet.py",
                    str(path),
                    "--repo-root",
                    str(repo),
                    "--json",
                )
                self.assertEqual(result.returncode, 1, name)
                self.assertEqual(
                    json.loads(result.stdout)["errors"],
                    ["SCHEMA_UNSUPPORTED"],
                )

    def test_validate_input_packet_cli_discovery_and_json_errors_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            result = run_script("validate_input_packet.py", str(outside), "--json")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["PATH_OUTSIDE_REPO"]
            )
            self.assertNotIn("Traceback", result.stderr)

            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            malformed = repo / "malformed.json"
            malformed.write_text("{not-json}\n", encoding="utf-8")
            result = run_script(
                "validate_input_packet.py",
                str(malformed),
                "--repo-root",
                str(repo),
                "--json",
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )
            self.assertNotIn("Traceback", result.stderr)

    def test_input_packet_schema_path_patterns_match_runtime_lexical_rules(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets/schemas/input-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        patterns = [
            schema["properties"]["artifact_root"]["pattern"],
            schema["properties"]["spec_binding"]["properties"]["path"]["pattern"],
            schema["properties"]["work_items"]["items"]["properties"]["source"]["properties"]["path"]["pattern"],
        ]
        invalid_paths = (
            "/absolute",
            "~/home",
            "a/../outside",
            "a/./file",
            "a//file",
            "a\\file",
            "a/invalid\x00file",
        )
        for pattern in patterns:
            self.assertIsNotNone(re.fullmatch(pattern, "knowledge/wiki/spec.md"))
            for value in invalid_paths:
                with self.subTest(pattern=pattern, value=value):
                    self.assertIsNone(re.fullmatch(pattern, value))
        scope_pattern = schema["properties"]["work_items"]["items"]["properties"]["write_scope"]["items"]["pattern"]
        self.assertIsNotNone(re.fullmatch(scope_pattern, "path:skills/example"))
        for value in ("path:/absolute", "path:../outside", "path:a/./file", "path:a\\file"):
            with self.subTest(value=value):
                self.assertIsNone(re.fullmatch(scope_pattern, value))

    def test_input_packet_schema_rejects_whitespace_only_runtime_strings(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets/schemas/input-packet.schema.json").read_text(
                encoding="utf-8"
            )
        )
        actor_pattern = schema["properties"]["approval_evidence"]["properties"]["actor_expression"]["pattern"]
        item_properties = schema["properties"]["work_items"]["items"]["properties"]
        self.assertIsNone(re.search(actor_pattern, "   "))
        self.assertIsNone(re.search(item_properties["title"]["pattern"], "\t"))
        for field in ("acceptance_criteria", "non_goals", "verification"):
            self.assertIsNone(
                re.search(item_properties[field]["items"]["pattern"], "  ")
            )

    def test_validate_execution_envelope_rejects_invalid_context_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("paths_first", {"paths_first": False}, "paths_first"),
                ("packet_budget", {"max_worker_packet_words": 0}, "max_worker_packet_words"),
                ("report_budget", {"max_worker_report_words": 0}, "max_worker_report_words"),
                ("full_spec", {"include_full_spec_text": True}, "include_full_spec_text"),
                ("full_ledger", {"include_full_ledger_text": True}, "include_full_ledger_text"),
            ]
            for name, patch, expected in cases:
                envelope = base_envelope()
                envelope["context_policy"].update(patch)
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_requires_session_compaction_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            del envelope["context_policy"]["session_compaction"]
            path = Path(tmp) / "missing-session-compaction.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("context_policy.session_compaction", result.stderr)

    def test_validate_execution_envelope_rejects_invalid_session_compaction_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("soft_trigger", {"soft_trigger_percent": 64}, "soft_trigger_percent"),
                ("hard_stop", {"hard_stop_percent": 76}, "hard_stop_percent"),
                ("handoff", {"mandatory_handoff_compaction": 0}, "mandatory_handoff_compaction"),
                ("phase_gc", {"mandatory_phase_transition_gc": False}, "mandatory_phase_transition_gc"),
                (
                    "capsule_default",
                    {"carry_forward_capsule_words_default": 401},
                    "carry_forward_capsule_words_default",
                ),
                (
                    "capsule_hard",
                    {"carry_forward_capsule_words_hard": 601},
                    "carry_forward_capsule_words_hard",
                ),
                (
                    "inline_lines",
                    {"inline_json_code_diff_lines_hard": 81},
                    "inline_json_code_diff_lines_hard",
                ),
                ("unknown", {"session_notes": "coordinator-only"}, "unknown field"),
            ]
            for name, patch, expected in cases:
                with self.subTest(name):
                    envelope = base_envelope()
                    envelope["context_policy"]["session_compaction"].update(patch)
                    path = Path(tmp) / f"{name}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_accepts_legacy_context_policy_without_worker_packet_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            for field in (
                "worker_packet_schema",
                "worker_packet_template",
                "worker_packet_validator",
            ):
                del envelope["context_policy"][field]
            path = Path(tmp) / "legacy-envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_requires_all_worker_packet_references_when_any_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for field in (
                "worker_packet_schema",
                "worker_packet_template",
                "worker_packet_validator",
            ):
                with self.subTest(field):
                    envelope = base_envelope()
                    envelope["context_policy"].update(
                        {
                            "worker_packet_schema": "assets/schemas/worker-packet.schema.json",
                            "worker_packet_template": "assets/templates/worker-packet.json",
                            "worker_packet_validator": "scripts/validate_worker_packet.py",
                        }
                    )
                    del envelope["context_policy"][field]
                    path = Path(tmp) / f"missing-{field}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0, field)
                    self.assertIn(f"context_policy.{field}", result.stderr)

    def test_execution_envelope_schema_is_current_only(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        context_schema = schema["properties"]["context_policy"]

        self.assertEqual(schema["properties"]["schema_version"].get("const"), 4)
        self.assertIn("approved_spec_binding", schema["required"])
        self.assertIn("session_compaction", context_schema["required"])
        for field in (
            "worker_packet_schema",
            "worker_packet_template",
            "worker_packet_validator",
        ):
            self.assertNotIn(field, context_schema["required"])
            self.assertEqual(
                sorted(context_schema["dependentRequired"][field]),
                [
                    "worker_packet_schema",
                    "worker_packet_template",
                    "worker_packet_validator",
                ],
            )

    def test_validate_execution_envelope_requires_phase_branch_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            del envelope["phase_branch_policy"]
            path = Path(tmp) / "missing-phase-branch-policy.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("phase_branch_policy", result.stderr)

    def test_validate_execution_envelope_rejects_invalid_phase_branch_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("planning_branch", {"planning_artifacts_branch": "epic_base"}, "planning_artifacts_branch"),
                ("approval_commit", {"phase_approval_commit_required": False}, "phase_approval_commit_required"),
                ("clean_scope", {"phase_transition_requires_clean_scope": False}, "phase_transition_requires_clean_scope"),
                ("context", {"execution_coordinator_context": "same_expanded_thread"}, "execution_coordinator_context"),
                ("planning_impl", {"main_planning_session_may_implement": True}, "main_planning_session_may_implement"),
                ("worktree", {"worktree_per_issue": False}, "worktree_per_issue"),
                ("prefix", {"branch_prefix": "feature"}, "branch_prefix"),
                ("epic_pattern", {"epic_base_ref_pattern": "main"}, "epic_base_ref_pattern"),
                ("issue_pattern", {"issue_branch_pattern": "codex/<epic-id>/<slug>"}, "issue_branch_pattern"),
                ("epic_owner", {"epic_base_owner": "worker"}, "epic_base_owner"),
                ("issue_owner", {"issue_branch_owner": "coordinator"}, "issue_branch_owner"),
                ("integration", {"integration_branch_policy": "ad_hoc_merge"}, "integration_branch_policy"),
                ("unknown", {"branch_cleanup": "auto"}, "unknown field"),
            ]
            for name, patch, expected in cases:
                with self.subTest(name):
                    envelope = base_envelope()
                    envelope["phase_branch_policy"].update(patch)
                    path = Path(tmp) / f"{name}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_execution_envelope_schema_defines_codex_phase_branch_policy(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        policy_schema = schema["properties"]["phase_branch_policy"]
        template = json.loads(
            (SKILL_DIR / "assets" / "templates" / "execution-envelope.json").read_text(
                encoding="utf-8"
            )
        )
        expected_policy = {
            "planning_artifacts_branch": "current_session_branch",
            "phase_approval_commit_required": True,
            "phase_transition_requires_clean_scope": True,
            "execution_coordinator_context": "fresh_or_compacted",
            "main_planning_session_may_implement": False,
            "worktree_per_issue": True,
            "branch_prefix": "codex",
            "epic_base_ref_pattern": "codex/<epic-id>/epic-base",
            "issue_branch_pattern": "codex/<epic-id>/<local-id>-<slug>",
            "epic_base_owner": "execution_coordinator",
            "issue_branch_owner": "worker",
            "integration_branch_policy": "approved_integration_work_item_only",
        }

        self.assertEqual(template["schema_version"], 4)
        self.assertEqual(template["phase_branch_policy"], expected_policy)
        self.assertEqual(policy_schema["required"], list(expected_policy))
        self.assertFalse(policy_schema["additionalProperties"])
        for field, value in expected_policy.items():
            self.assertEqual(policy_schema["properties"][field]["const"], value)

    def test_validate_execution_envelope_rejects_tracked_legacy_envelopes(self) -> None:
        envelope_dir = SKILL_DIR.parents[1] / "knowledge" / "wiki" / "syntheses"

        for name in (
            "loop-skill-architecture-v3-execution-envelope.json",
            "loop-skill-operational-simplicity-execution-envelope.json",
            "skill-repository-optimization-v4-execution-envelope.json",
        ):
            with self.subTest(name):
                result = run_script(
                    "validate_execution_envelope.py",
                    str(envelope_dir / name),
                    "--json",
                )
                self.assertEqual(result.returncode, 1)
                self.assertEqual(
                    json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
                )

    def test_loop_skill_v3_execution_envelope_records_worker_packet_context_references(self) -> None:
        envelope_path = (
            SKILL_DIR.parents[1]
            / "knowledge"
            / "wiki"
            / "syntheses"
            / "loop-skill-architecture-v3-execution-envelope.json"
        )
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        context_policy = envelope["context_policy"]

        self.assertEqual(
            context_policy["worker_packet_schema"],
            "skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json",
        )
        self.assertEqual(
            context_policy["worker_packet_template"],
            "skills/issue-implementation-loop/assets/templates/worker-packet.json",
        )
        self.assertEqual(
            context_policy["worker_packet_validator"],
            "skills/issue-implementation-loop/scripts/validate_worker_packet.py",
        )

    def test_validate_execution_envelope_rejects_non_object_remote_write_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["remote_write_policy"] = None
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote_write_policy must be an object", result.stderr)

    def test_validate_execution_envelope_requires_review_cycle_budget_of_two_or_less(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing", None, "review_policy.max_review_cycles"),
                ("too_many", 3, "review_policy.max_review_cycles"),
                ("zero", 0, "review_policy.max_review_cycles"),
            ]
            for name, value, expected in cases:
                envelope = base_envelope()
                if value is None:
                    del envelope["review_policy"]["max_review_cycles"]
                else:
                    envelope["review_policy"]["max_review_cycles"] = value
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_execution_envelope_template_schema_and_validator_define_hardening_candidate_policy(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        template = json.loads(
            (SKILL_DIR / "assets" / "templates" / "execution-envelope.json").read_text(
                encoding="utf-8"
            )
        )
        expected_policy = {
            "candidate_registry_path": "decisions/hardening-candidates.json",
            "max_candidates_per_issue": 5,
            "max_summary_words": 80,
            "issue_completion_blocking": False,
            "ready_or_merge_requires_decisions": True,
            "worker_packet_decision_state": "forbidden",
        }

        self.assertEqual(template["review_policy"]["hardening_candidates"], expected_policy)

        policy_schema = schema["properties"]["review_policy"]["properties"]["hardening_candidates"]
        self.assertFalse(policy_schema["additionalProperties"])
        for field, value in expected_policy.items():
            self.assertIn(field, policy_schema["required"])
            field_schema = policy_schema["properties"][field]
            if field in {
                "candidate_registry_path",
                "issue_completion_blocking",
                "ready_or_merge_requires_decisions",
                "worker_packet_decision_state",
            }:
                self.assertEqual(field_schema["const"], value)
        self.assertEqual(policy_schema["properties"]["max_candidates_per_issue"]["maximum"], 5)
        self.assertEqual(policy_schema["properties"]["max_summary_words"]["maximum"], 80)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "envelope.json"
            write_json(path, base_envelope())

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_rejects_malformed_hardening_candidate_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                (
                    "registry_path",
                    {"candidate_registry_path": "inline-candidates.json"},
                    "review_policy.hardening_candidates.candidate_registry_path",
                ),
                (
                    "too_many_candidates",
                    {"max_candidates_per_issue": 999},
                    "review_policy.hardening_candidates.max_candidates_per_issue",
                ),
                (
                    "long_summary",
                    {"max_summary_words": 999},
                    "review_policy.hardening_candidates.max_summary_words",
                ),
                (
                    "completion_blocking",
                    {"issue_completion_blocking": True},
                    "review_policy.hardening_candidates.issue_completion_blocking",
                ),
                (
                    "ready_or_merge_not_gated",
                    {"ready_or_merge_requires_decisions": False},
                    "review_policy.hardening_candidates.ready_or_merge_requires_decisions",
                ),
                (
                    "worker_decision_state",
                    {"worker_packet_decision_state": "included"},
                    "review_policy.hardening_candidates.worker_packet_decision_state",
                ),
                (
                    "unknown_decision_state",
                    {"candidate_decisions": []},
                    "unknown field: review_policy.hardening_candidates.candidate_decisions",
                ),
            ]
            for name, patch, expected in cases:
                with self.subTest(name):
                    envelope = base_envelope()
                    envelope["review_policy"]["hardening_candidates"].update(patch)
                    path = Path(tmp) / f"{name}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0, name)
                    self.assertIn(expected, result.stderr)

    def test_validate_execution_envelope_requires_worker_context_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = [
                ("missing_worker_required", "worker_context_required", None, "worker_context_required"),
                ("worker_not_required", "worker_context_required", False, "worker_context_required"),
                ("missing_coordinator", "coordinator_may_implement", None, "coordinator_may_implement"),
                ("coordinator_allowed", "coordinator_may_implement", True, "coordinator_may_implement"),
                ("missing_serial_mode", "serial_fallback_mode", None, "serial_fallback_mode"),
                ("coordinator_serial", "serial_fallback_mode", "coordinator_direct", "serial_fallback_mode"),
            ]
            for name, field, value, expected in cases:
                envelope = base_envelope()
                if value is None:
                    del envelope["execution_policy"][field]
                else:
                    envelope["execution_policy"][field] = value
                path = Path(tmp) / f"{name}.json"
                write_json(path, envelope)

                result = run_script("validate_execution_envelope.py", str(path))

                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn(expected, result.stderr)

    def test_execution_envelope_schema_requires_worker_context_boundaries(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        execution_schema = schema["properties"]["execution_policy"]

        self.assertIn("worker_context_required", execution_schema["required"])
        self.assertIn("coordinator_may_implement", execution_schema["required"])
        self.assertIn("serial_fallback_mode", execution_schema["required"])
        self.assertEqual(execution_schema["properties"]["worker_context_required"]["const"], True)
        self.assertEqual(execution_schema["properties"]["coordinator_may_implement"]["const"], False)
        self.assertEqual(
            execution_schema["properties"]["serial_fallback_mode"]["const"],
            "worker_context_only",
        )

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

    def test_validate_execution_envelope_accepts_batch_issue_prs_to_epic_base_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_accepts_final_pr_auto_create_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [
                    "final_pr_push_head",
                    "final_pr_create_draft",
                ],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_rejects_unknown_approved_remote_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [
                    "final_pr_create_ready",
                    "force_push",
                ],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("remote_write_policy.approved_actions[0]", result.stderr)
            self.assertIn("remote_write_policy.approved_actions[1]", result.stderr)

    def test_validate_execution_envelope_rejects_ready_or_high_risk_final_pr_fields(self) -> None:
        forbidden_fields = {
            "ready_for_review": True,
            "force_push": True,
            "production": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            for field, value in forbidden_fields.items():
                with self.subTest(field):
                    envelope = base_envelope()
                    envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
                    envelope["epic_base"]["branch_state"] = "reserved"
                    envelope["remote_write_policy"] = {
                        "mode": "batch_issue_prs",
                        "approved_actions": [
                            "final_pr_push_head",
                            "final_pr_create_draft",
                        ],
                        "issue_prs": {
                            "base": "epic_base.ref",
                            "merge": "agent_default_with_human_escalation",
                        },
                        "final_pr": {
                            "head": "epic_base.ref",
                            "base": "main",
                            "merge": "human_only",
                            field: value,
                        },
                    }
                    path = Path(tmp) / f"forbidden-{field}.json"
                    write_json(path, envelope)

                    result = run_script("validate_execution_envelope.py", str(path))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(f"remote_write_policy.final_pr.{field}", result.stderr)
                    self.assertIn("human-only", result.stderr)

    def test_validate_execution_envelope_requires_epic_base_branch_state_for_batch_issue_prs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("epic_base.branch_state", result.stderr)

    def test_validate_execution_envelope_rejects_relative_epic_base_worktree_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["epic_base"]["worktree_path"] = "relative/worktree"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("epic_base.worktree_path", result.stderr)

    def test_validate_execution_envelope_rejects_batch_issue_prs_without_epic_base_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("codex/issue-implementation-loop/epic-base", result.stderr)

    def test_validate_execution_envelope_rejects_batch_issue_prs_when_final_pr_merge_is_not_human_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            envelope = base_envelope()
            envelope["epic_base"]["ref"] = "codex/issue-implementation-loop/epic-base"
            envelope["epic_base"]["branch_state"] = "reserved"
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "agent_default_with_human_escalation",
                },
            }
            path = Path(tmp) / "envelope.json"
            write_json(path, envelope)

            result = run_script("validate_execution_envelope.py", str(path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("final_pr.merge", result.stderr)

    def test_execution_envelope_schema_requires_batch_issue_prs_shape(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        remote_schema = schema["properties"]["remote_write_policy"]
        batch_rule = next(
            rule
            for rule in remote_schema["allOf"]
            if rule["if"]["properties"]["mode"]["const"] == "batch_issue_prs"
        )

        self.assertEqual(batch_rule["then"]["required"], ["issue_prs", "final_pr"])
        self.assertEqual(
            remote_schema["properties"]["issue_prs"]["required"],
            ["base", "merge"],
        )
        self.assertEqual(
            remote_schema["properties"]["final_pr"]["required"],
            ["head", "base", "merge"],
        )
        self.assertEqual(
            remote_schema["properties"]["final_pr"]["additionalProperties"],
            False,
        )

    def test_execution_envelope_schema_defines_approved_remote_action_enum(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        approved_actions = schema["properties"]["remote_write_policy"]["properties"]["approved_actions"]

        self.assertEqual(approved_actions["items"]["enum"], [
            "final_pr_push_head",
            "final_pr_create_draft",
        ])
        self.assertEqual(approved_actions["uniqueItems"], True)

    def test_execution_envelope_schema_defines_epic_base_branch_lifecycle(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        epic_base_schema = schema["properties"]["epic_base"]

        self.assertIn("branch_state", epic_base_schema["properties"])
        self.assertIn("worktree_path", epic_base_schema["properties"])
        self.assertEqual(
            epic_base_schema["properties"]["branch_state"]["enum"],
            ["reserved", "create_on_run", "active", "missing"],
        )

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

    def test_validate_worker_report_requires_commit_metadata_for_pr_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            report = current_worker_report(repo, binding, packet)
            del report["base_sha"]
            del report["head_sha"]
            write_json(report_path, report)

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base_sha", result.stderr)
            self.assertIn("head_sha", result.stderr)

    def test_validate_worker_report_accepts_committed_pr_ready_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_worker_report_rejects_pr_ready_with_unapproved_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            report = current_worker_report(repo, binding, packet)
            report["implementation_review"]["status"] = "changes_requested"
            write_json(report_path, report)

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("implementation_review.status must be approved", result.stderr)

    def test_worker_report_v1_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            report = current_worker_report(repo, binding, packet)
            report["schema_version"] = 1
            write_json(report_path, report)

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )

    def test_asb_13_worker_report_intake_rejects_resealed_runtime_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))
            runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime["approved_spec_binding"]["sha256"] = "a" * 64
            write_json(runtime_path, runtime)

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
            )

    def test_asb_22_reviewer_report_rejects_final_alignment_binding_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding, task_kind="review")
            packet_path = repo / "reviewer-packet.json"
            report_path = repo / "reviewer-report.json"
            runtime_path = repo / "runtime-state.json"
            write_json(packet_path, packet)
            report = current_worker_report(repo, binding, packet)
            report["approved_spec_binding"]["sha256"] = "b" * 64
            write_json(report_path, report)

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
            )
