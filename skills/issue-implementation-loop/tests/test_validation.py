from __future__ import annotations

try:
    from _helpers import *
except ModuleNotFoundError:
    from ._helpers import *

LIB_DIR = SCRIPTS_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop.validation.execution_envelope import (
    validate_execution_envelope,
)


class ExecutionEnvelopeReferenceTests(unittest.TestCase):
    def test_reference_requires_exact_closed_packet_projection(self) -> None:
        text = (SKILL_DIR / "references" / "execution-envelope.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "closed at every object level",
            "must exactly project the",
            "verified Input Packet",
            "exact `epic_base.sha`",
            "new sealed packet",
        ):
            self.assertIn(required, text)


class ValidationTests(unittest.TestCase):
    @staticmethod
    def legacy_guardless_envelope_fixture(
        root: Path,
    ) -> tuple[Path, dict, str, str]:
        repo, binding, gate_commit = create_binding_repo(root)
        packet = json.loads((repo / binding["path"]).read_text(encoding="utf-8"))
        if {"planning_branch", "planning_base_sha"} & set(packet):
            raise AssertionError("fixture must remain a real legacy packet")
        gate_parent = git(repo, "rev-parse", f"{gate_commit}^")
        gate_tree = git(repo, "rev-parse", f"{gate_commit}^{{tree}}")
        physical_epic_base = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "commit-tree",
                gate_tree,
                "-p",
                gate_parent,
            ],
            check=True,
            capture_output=True,
            text=True,
            input="physical legacy epic base without Gate\n",
        ).stdout.strip()
        envelope = binding_envelope(repo, binding, physical_epic_base)
        if "repository_guard" in envelope:
            raise AssertionError("legacy fixture must be guardless")
        return repo, envelope, gate_commit, physical_epic_base

    def test_repository_guard_git_sanitizes_local_environment(self) -> None:
        from issue_implementation_loop import git_environment

        hostile_environment = {
            name: f"hostile-{index}"
            for index, name in enumerate(
                git_environment.REPOSITORY_LOCAL_GIT_ENVIRONMENT
            )
        }
        hostile_environment.update(
            {
                "GIT_CONFIG_KEY_0": "core.worktree",
                "GIT_CONFIG_VALUE_0": "/hostile/repository",
                "GIT_OPTIONAL_LOCKS": "1",
                "HOME": "/preserved/home",
                "XDG_CONFIG_HOME": "/preserved/xdg",
                "GIT_CONFIG_GLOBAL": "/preserved/global-config",
                "GIT_CONFIG_SYSTEM": "/preserved/system-config",
            }
        )
        with mock.patch.dict(os.environ, hostile_environment):
            environment = git_environment.repository_git_environment()

        self.assertEqual(environment["GIT_OPTIONAL_LOCKS"], "0")
        trusted_overrides = {
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_GRAFT_FILE": os.devnull,
        }
        for name in (
            git_environment.REPOSITORY_LOCAL_GIT_ENVIRONMENT
            - trusted_overrides.keys()
        ):
            self.assertNotIn(name, environment)
        self.assertEqual(
            {
                name: environment.get(name)
                for name in trusted_overrides
            },
            trusted_overrides,
        )
        self.assertNotIn("GIT_CONFIG_KEY_0", environment)
        self.assertNotIn("GIT_CONFIG_VALUE_0", environment)
        for name in (
            "HOME",
            "XDG_CONFIG_HOME",
            "GIT_CONFIG_GLOBAL",
            "GIT_CONFIG_SYSTEM",
        ):
            self.assertEqual(environment[name], hostile_environment[name])

    def test_repository_guard_sanitizer_covers_git_local_environment_variables(
        self,
    ) -> None:
        from issue_implementation_loop import git_environment

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, "init", "-q")
            local_environment = set(
                git(repo, "rev-parse", "--local-env-vars").splitlines()
            )

        self.assertEqual(len(local_environment), 15)
        self.assertEqual(
            local_environment
            - git_environment.REPOSITORY_LOCAL_GIT_ENVIRONMENT,
            set(),
        )
        self.assertEqual(
            local_environment
            & {"GIT_NO_REPLACE_OBJECTS", "GIT_GRAFT_FILE"},
            {"GIT_NO_REPLACE_OBJECTS", "GIT_GRAFT_FILE"},
        )
        for global_environment in (
            "GIT_CONFIG_GLOBAL",
            "GIT_CONFIG_SYSTEM",
            "HOME",
            "XDG_CONFIG_HOME",
        ):
            self.assertNotIn(
                global_environment,
                git_environment.REPOSITORY_LOCAL_GIT_ENVIRONMENT,
            )

    @staticmethod
    def planning_guard_fixture(
        root: Path,
        *,
        preexisting_dirt: bool = False,
    ) -> tuple[Path, Path, dict, dict, str]:
        repo = root / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "Test User")
        git(repo, "branch", "-M", "main")
        (repo / "README.md").write_text("base\n", encoding="utf-8")
        git(repo, "add", "README.md")
        git(repo, "commit", "-q", "-m", "base")
        planning_base = git(repo, "rev-parse", "HEAD")
        if preexisting_dirt:
            (repo / "preexisting.txt").write_text("leave me alone\n", encoding="utf-8")
        default_status = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        planning = root / "planning"
        planning_branch = "codex/approved-spec-binding/planning"
        git(
            repo,
            "worktree",
            "add",
            "-q",
            "-b",
            planning_branch,
            str(planning),
            planning_base,
        )
        synthesis = planning / FIXTURE_ARTIFACT_ROOT
        synthesis.mkdir(parents=True)
        (synthesis / "spec.md").write_text("approved spec\n", encoding="utf-8")
        (synthesis / "issues.md").write_text("# Issues\n", encoding="utf-8")
        packet_path = synthesis / "input-packet.json"
        packet = current_input_packet(planning)
        packet.update(
            {
                "planning_branch": planning_branch,
                "planning_base_sha": planning_base,
            }
        )
        write_json(packet_path, packet)
        git(planning, "add", "knowledge")
        git(planning, "commit", "-q", "-m", "planning gate")
        gate_commit = git(planning, "rev-parse", "HEAD")
        binding = {
            "path": packet_path.relative_to(planning).as_posix(),
            "sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
            "gate_commit": gate_commit,
        }
        envelope = binding_envelope(planning, binding)
        envelope["repository_guard"] = {
            "planning_worktree_path": str(planning.resolve()),
            "planning_branch": planning_branch,
            "planning_base_sha": planning_base,
            "default_checkout": {
                "path": str(repo.resolve()),
                "branch": "main",
                "head": planning_base,
                "status_porcelain_v1": default_status,
            },
        }
        write_planning_runtime_identity(
            planning,
            epic_id=packet["epic_id"],
            planning_branch=planning_branch,
            planning_base_sha=planning_base,
            default_checkout=repo,
            planning_worktree=planning,
            default_status=default_status,
        )
        return repo, planning, packet, envelope, planning_base

    def test_repository_guard_rejects_packet_branch_or_base_mismatch(self) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            _, planning, packet, valid, _ = self.planning_guard_fixture(
                Path(tmp)
            )
            cases = {
                "branch": ("planning_branch", "codex/another-epic/planning"),
                "base": ("planning_base_sha", git(planning, "rev-parse", "HEAD")),
            }
            for name, (field, value) in cases.items():
                with self.subTest(name=name):
                    envelope = copy.deepcopy(valid)
                    envelope["repository_guard"][field] = value
                    self.assertEqual(
                        validate_repository_guard(envelope, packet, planning),
                        ["REPOSITORY_GUARD_MISMATCH"],
                    )

    def test_repository_guard_is_required_only_for_packets_with_planning_identity(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            _, planning, packet, envelope, _ = self.planning_guard_fixture(Path(tmp))
            envelope.pop("repository_guard")
            self.assertEqual(
                validate_repository_guard(envelope, packet, planning),
                ["REPOSITORY_GUARD_MISSING"],
            )

            legacy_packet = copy.deepcopy(packet)
            legacy_packet.pop("planning_branch")
            legacy_packet.pop("planning_base_sha")
            self.assertEqual(
                validate_repository_guard(envelope, legacy_packet, planning),
                [],
            )

    def test_repository_guard_rejects_unregistered_planning_path(self) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, planning, packet, envelope, _ = self.planning_guard_fixture(root)
            unregistered = root / "unregistered"
            unregistered.mkdir()
            envelope["repository_guard"]["planning_worktree_path"] = str(
                unregistered.resolve()
            )

            self.assertEqual(
                validate_repository_guard(envelope, packet, planning),
                ["REPOSITORY_GUARD_WORKTREE_INVALID"],
            )

    def test_repository_guard_rejects_default_checkout_head_or_status_drift(self) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, planning, packet, envelope, _ = self.planning_guard_fixture(root)
            (repo / "README.md").write_text("drifted\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-q", "-m", "default head drift")
            self.assertEqual(
                validate_repository_guard(envelope, packet, planning),
                ["DEFAULT_CHECKOUT_DRIFT"],
            )

            status_root = root / "status-case"
            status_root.mkdir()
            status_repo, status_planning, status_packet, status_envelope, _ = (
                self.planning_guard_fixture(status_root)
            )
            (status_repo / "new-untracked.txt").write_text(
                "status drift\n", encoding="utf-8"
            )
            self.assertEqual(
                validate_repository_guard(
                    status_envelope,
                    status_packet,
                    status_planning,
                ),
                ["DEFAULT_CHECKOUT_DRIFT"],
            )

    def test_repository_guard_rejects_clean_registered_substitute_for_drifted_default(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, planning, packet, envelope, planning_base = (
                self.planning_guard_fixture(root)
            )
            substitute = root / "substitute"
            git(
                repo,
                "worktree",
                "add",
                "-q",
                "-b",
                "not-main",
                str(substitute),
                planning_base,
            )
            (repo / "main-drift.txt").write_text(
                "actual main drift\n",
                encoding="utf-8",
            )
            envelope["repository_guard"]["default_checkout"] = {
                "path": str(substitute.resolve()),
                "branch": "not-main",
                "head": planning_base,
                "status_porcelain_v1": "",
            }

            self.assertEqual(
                validate_repository_guard(envelope, packet, planning),
                ["REPOSITORY_GUARD_RUNTIME_MISMATCH"],
            )

    def test_repository_guard_rejects_runtime_identity_mismatches(self) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        def replace_snapshot_head(payload: dict, _: Path, __: str) -> None:
            payload["planning_base_sha"] = "1" * 40
            payload["default_checkout_start"]["head"] = "1" * 40

        mutations = {
            "planning path": lambda payload, root, base: payload.update(
                planning_worktree=str(root.resolve())
            ),
            "default path": lambda payload, root, base: payload.update(
                default_checkout=str(root.resolve())
            ),
            "snapshot head": replace_snapshot_head,
            "snapshot status": lambda payload, root, base: payload[
                "default_checkout_start"
            ].update(status_porcelain="?? replaced.txt\n"),
            "planning branch": lambda payload, root, base: payload.update(
                planning_branch="codex/other/planning"
            ),
            "planning base": replace_snapshot_head,
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _, planning, packet, envelope, planning_base = (
                    self.planning_guard_fixture(root)
                )
                runtime_path = (
                    git_common_directory(planning)
                    / "agent-runs"
                    / "grill-to-pr-loop"
                    / packet["epic_id"]
                    / "planning-worktree.json"
                )
                payload = json.loads(runtime_path.read_text(encoding="utf-8"))
                mutate(payload, root, planning_base)
                write_json(runtime_path, payload)

                self.assertEqual(
                    validate_repository_guard(envelope, packet, planning),
                    ["REPOSITORY_GUARD_RUNTIME_MISMATCH"],
                )

    def test_repository_guard_rejects_missing_corrupt_and_symlink_runtime_identity(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        for case in (
            "missing",
            "corrupt",
            "wrong-version",
            "unknown-field",
            "duplicate-field",
            "noncanonical-path",
            "symlink",
            "symlink-parent",
        ):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _, planning, packet, envelope, _ = self.planning_guard_fixture(root)
                runtime_path = (
                    git_common_directory(planning)
                    / "agent-runs"
                    / "grill-to-pr-loop"
                    / packet["epic_id"]
                    / "planning-worktree.json"
                )
                if case == "missing":
                    runtime_path.unlink()
                elif case == "corrupt":
                    runtime_path.write_text("{", encoding="utf-8")
                elif case == "wrong-version":
                    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
                    payload["schema_version"] = True
                    write_json(runtime_path, payload)
                elif case == "unknown-field":
                    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
                    payload["unknown"] = "rejected"
                    write_json(runtime_path, payload)
                elif case == "duplicate-field":
                    raw = runtime_path.read_text(encoding="utf-8")
                    runtime_path.write_text(
                        raw.replace(
                            '"schema_version": 1',
                            '"schema_version": 1, "schema_version": 1',
                            1,
                        ),
                        encoding="utf-8",
                    )
                elif case == "noncanonical-path":
                    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
                    payload["default_checkout"] = str(
                        root / "repo" / ".." / "repo"
                    )
                    write_json(runtime_path, payload)
                elif case == "symlink":
                    target = root / "runtime-target.json"
                    target.write_bytes(runtime_path.read_bytes())
                    runtime_path.unlink()
                    runtime_path.symlink_to(target)
                else:
                    real_parent = runtime_path.parent.with_name(
                        f"{runtime_path.parent.name}-real"
                    )
                    runtime_path.parent.rename(real_parent)
                    runtime_path.parent.symlink_to(real_parent, target_is_directory=True)

                self.assertEqual(
                    validate_repository_guard(envelope, packet, planning),
                    ["REPOSITORY_GUARD_RUNTIME_INVALID"],
                )

    def test_repository_guard_rejects_runtime_artifact_replaced_during_validation(
        self,
    ) -> None:
        from issue_implementation_loop import repository_integrity

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, planning, packet, envelope, _ = self.planning_guard_fixture(root)
            runtime_path = (
                git_common_directory(planning)
                / "agent-runs"
                / "grill-to-pr-loop"
                / packet["epic_id"]
                / "planning-worktree.json"
            )
            original_match = repository_integrity._runtime_identity_matches_guard

            def replace_after_match(*args: object, **kwargs: object) -> bool:
                matched = original_match(*args, **kwargs)
                replacement = runtime_path.with_suffix(".replacement")
                replacement.write_bytes(runtime_path.read_bytes())
                os.replace(replacement, runtime_path)
                return matched

            with mock.patch.object(
                repository_integrity,
                "_runtime_identity_matches_guard",
                side_effect=replace_after_match,
            ):
                errors = repository_integrity.validate_repository_guard(
                    envelope,
                    packet,
                    planning,
                )

            self.assertEqual(errors, ["REPOSITORY_GUARD_RUNTIME_INVALID"])

    def test_repository_guard_rejects_drift_under_hostile_git_routing_environment(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").mkdir()
            repo, planning, packet, envelope, _ = self.planning_guard_fixture(
                root / "a"
            )
            repo_b = root / "b"
            repo_b.mkdir()
            git(repo_b, "init", "-q")
            git(repo_b, "config", "user.email", "test@example.com")
            git(repo_b, "config", "user.name", "Test User")
            (repo_b / "README.md").write_text("base\n", encoding="utf-8")
            git(repo_b, "add", "README.md")
            git(repo_b, "commit", "-q", "-m", "repo B base")
            git(repo_b, "config", "core.worktree", str(repo_b.resolve()))

            repo_b_git = repo_b / ".git"
            before_b = {
                "head": git(repo_b, "rev-parse", "HEAD"),
                "status": subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo_b),
                        "status",
                        "--porcelain=v1",
                        "--untracked-files=all",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout,
                "index": (repo_b_git / "index").read_bytes(),
                "config": (repo_b_git / "config").read_bytes(),
                "refs": git(repo_b, "show-ref"),
                "worktrees": git(repo_b, "worktree", "list", "--porcelain"),
            }
            (repo / "drift.txt").write_text("real default drift\n", encoding="utf-8")
            hostile_environment = {
                "GIT_DIR": str(repo_b_git),
                "GIT_WORK_TREE": str(repo_b.resolve()),
                "GIT_COMMON_DIR": str(repo_b_git),
                "GIT_INDEX_FILE": str(repo_b_git / "index"),
                "GIT_OBJECT_DIRECTORY": str(repo_b_git / "objects"),
                "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(repo_b_git / "objects"),
                "GIT_CONFIG": str(repo_b_git / "config"),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.worktree",
                "GIT_CONFIG_VALUE_0": str(repo_b.resolve()),
            }

            with mock.patch.dict(os.environ, hostile_environment):
                errors = validate_repository_guard(
                    envelope,
                    packet,
                    planning,
                )

            self.assertEqual(errors, ["DEFAULT_CHECKOUT_DRIFT"])
            self.assertEqual(git(repo_b, "rev-parse", "HEAD"), before_b["head"])
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo_b),
                        "status",
                        "--porcelain=v1",
                        "--untracked-files=all",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout,
                before_b["status"],
            )
            self.assertEqual((repo_b_git / "index").read_bytes(), before_b["index"])
            self.assertEqual((repo_b_git / "config").read_bytes(), before_b["config"])
            self.assertEqual(git(repo_b, "show-ref"), before_b["refs"])
            self.assertEqual(
                git(repo_b, "worktree", "list", "--porcelain"),
                before_b["worktrees"],
            )

    def test_repository_guard_rejects_drift_hidden_by_hostile_work_tree(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, planning, packet, envelope, _ = self.planning_guard_fixture(root)
            clean_mirror = root / "clean-mirror"
            clean_mirror.mkdir()
            (clean_mirror / "README.md").write_text("base\n", encoding="utf-8")
            (repo / "real-drift.txt").write_text(
                "must remain visible to the guard\n",
                encoding="utf-8",
            )
            hostile_status = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ],
                check=True,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "GIT_WORK_TREE": str(clean_mirror.resolve()),
                    "GIT_OPTIONAL_LOCKS": "0",
                },
            ).stdout
            self.assertEqual(hostile_status, "")

            with mock.patch.dict(
                os.environ,
                {"GIT_WORK_TREE": str(clean_mirror.resolve())},
            ):
                errors = validate_repository_guard(
                    envelope,
                    packet,
                    planning,
                )

            self.assertEqual(errors, ["DEFAULT_CHECKOUT_DRIFT"])

    def test_repository_guard_allows_unchanged_preexisting_dirt(self) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_repository_guard,
        )

        with tempfile.TemporaryDirectory() as tmp:
            _, planning, packet, envelope, _ = self.planning_guard_fixture(
                Path(tmp), preexisting_dirt=True
            )

            self.assertEqual(
                validate_repository_guard(envelope, packet, planning),
                [],
            )
            self.assertEqual(validate_execution_envelope(envelope, planning), [])

    def test_success_repository_integrity_rejects_default_checkout_drift(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_success_repository_integrity,
        )

        for status in ("PR_READY", "COMPLETE", "DONE"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                repo, planning, _, envelope, _ = self.planning_guard_fixture(
                    Path(tmp)
                )
                runtime = {
                    "issues": {
                        "ASBC-002": {
                            "status": status,
                        }
                    }
                }
                (repo / "README.md").write_text(
                    f"default checkout {status} drift\n",
                    encoding="utf-8",
                )

                self.assertEqual(
                    validate_success_repository_integrity(
                        envelope,
                        runtime,
                        planning,
                    ),
                    ["DEFAULT_CHECKOUT_DRIFT"],
                )

    def test_success_repository_integrity_allows_unchanged_preexisting_dirt(
        self,
    ) -> None:
        from issue_implementation_loop.repository_integrity import (
            validate_success_repository_integrity,
        )

        with tempfile.TemporaryDirectory() as tmp:
            _, planning, _, envelope, _ = self.planning_guard_fixture(
                Path(tmp),
                preexisting_dirt=True,
            )
            runtime = {
                "issues": {
                    "ASBC-002": {
                        "status": "PR_READY",
                    }
                }
            }

            self.assertEqual(
                validate_success_repository_integrity(
                    envelope,
                    runtime,
                    planning,
                ),
                [],
            )

    def test_execution_envelope_reports_gate_commit_not_ancestor_with_repository_guard(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            git(repo, "init", "-q")
            git(repo, "config", "user.email", "test@example.com")
            git(repo, "config", "user.name", "Test User")
            git(repo, "branch", "-M", "main")
            (repo / "README.md").write_text("base\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-q", "-m", "base")
            planning_base = git(repo, "rev-parse", "HEAD")
            planning = root / "planning"
            planning_branch = "codex/approved-spec-binding/planning"
            git(
                repo,
                "worktree",
                "add",
                "-q",
                "-b",
                planning_branch,
                str(planning),
                planning_base,
            )

            synthesis = repo / FIXTURE_ARTIFACT_ROOT
            synthesis.mkdir(parents=True)
            (synthesis / "spec.md").write_text("approved spec\n", encoding="utf-8")
            (synthesis / "issues.md").write_text("# Issues\n", encoding="utf-8")
            packet_path = synthesis / "input-packet.json"
            packet = current_input_packet(repo)
            packet.update(
                {
                    "planning_branch": planning_branch,
                    "planning_base_sha": planning_base,
                }
            )
            write_json(packet_path, packet)
            git(repo, "add", "knowledge")
            git(repo, "commit", "-q", "-m", "gate only on main")
            gate_commit = git(repo, "rev-parse", "HEAD")
            binding = {
                "path": packet_path.relative_to(repo).as_posix(),
                "sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
                "gate_commit": gate_commit,
            }
            envelope = binding_envelope(repo, binding, planning_base)
            envelope["repository_guard"] = {
                "planning_worktree_path": str(planning.resolve()),
                "planning_branch": planning_branch,
                "planning_base_sha": planning_base,
                "default_checkout": {
                    "path": str(repo.resolve()),
                    "branch": "main",
                    "head": gate_commit,
                    "status_porcelain_v1": "",
                },
            }

            self.assertEqual(
                validate_execution_envelope(envelope, repo),
                ["GATE_COMMIT_NOT_ANCESTOR"],
            )

    def test_execution_envelope_rejects_replace_ref_that_fakes_gate_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, planning, _, envelope, planning_base = (
                self.planning_guard_fixture(Path(tmp))
            )
            gate_commit = envelope["approved_spec_binding"]["gate_commit"]
            gate_tree = git(planning, "rev-parse", f"{gate_commit}^{{tree}}")
            physical_epic_base = subprocess.run(
                [
                    "git",
                    "-C",
                    str(planning),
                    "commit-tree",
                    gate_tree,
                    "-p",
                    planning_base,
                ],
                check=True,
                capture_output=True,
                text=True,
                input="physical epic base without Gate\n",
            ).stdout.strip()
            replacement = subprocess.run(
                [
                    "git",
                    "-C",
                    str(planning),
                    "commit-tree",
                    gate_tree,
                    "-p",
                    gate_commit,
                ],
                check=True,
                capture_output=True,
                text=True,
                input="replacement-only Gate ancestry\n",
            ).stdout.strip()
            git(
                planning,
                "update-ref",
                f"refs/replace/{physical_epic_base}",
                replacement,
            )
            envelope["epic_base"]["sha"] = physical_epic_base
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(planning),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                ).returncode,
                0,
            )

            errors = validate_execution_envelope(envelope, planning)

            self.assertEqual(errors, ["GATE_COMMIT_NOT_ANCESTOR"])

    def test_execution_envelope_rejects_info_graft_that_fakes_gate_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, planning, _, envelope, planning_base = (
                self.planning_guard_fixture(Path(tmp))
            )
            gate_commit = envelope["approved_spec_binding"]["gate_commit"]
            gate_tree = git(planning, "rev-parse", f"{gate_commit}^{{tree}}")
            physical_epic_base = subprocess.run(
                [
                    "git",
                    "-C",
                    str(planning),
                    "commit-tree",
                    gate_tree,
                    "-p",
                    planning_base,
                ],
                check=True,
                capture_output=True,
                text=True,
                input="physical epic base without Gate\n",
            ).stdout.strip()
            common_dir = git_common_directory(planning)
            graft_file = common_dir / "info" / "grafts"
            graft_file.parent.mkdir(parents=True, exist_ok=True)
            graft_file.write_text(
                f"{physical_epic_base} {gate_commit}\n",
                encoding="utf-8",
            )
            envelope["epic_base"]["sha"] = physical_epic_base
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(planning),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                    env={
                        **os.environ,
                        "GIT_GRAFT_FILE": str(graft_file),
                        "GIT_NO_REPLACE_OBJECTS": "0",
                    },
                ).returncode,
                0,
            )

            with mock.patch.dict(
                os.environ,
                {
                    "GIT_GRAFT_FILE": str(graft_file),
                    "GIT_NO_REPLACE_OBJECTS": "0",
                },
            ):
                errors = validate_execution_envelope(envelope, planning)

            self.assertEqual(errors, ["GATE_COMMIT_NOT_ANCESTOR"])

    def test_legacy_guardless_envelope_rejects_replace_ref_semantic_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, gate_commit, physical_epic_base = (
                self.legacy_guardless_envelope_fixture(Path(tmp))
            )
            gate_tree = git(repo, "rev-parse", f"{gate_commit}^{{tree}}")
            replacement = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "commit-tree",
                    gate_tree,
                    "-p",
                    gate_commit,
                ],
                check=True,
                capture_output=True,
                text=True,
                input="replacement-only legacy Gate ancestry\n",
            ).stdout.strip()
            git(
                repo,
                "update-ref",
                f"refs/replace/{physical_epic_base}",
                replacement,
            )
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                ).returncode,
                0,
            )
            self.assertNotEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                    env={
                        **os.environ,
                        "GIT_NO_REPLACE_OBJECTS": "1",
                        "GIT_GRAFT_FILE": os.devnull,
                    },
                ).returncode,
                0,
            )

            self.assertEqual(
                validate_execution_envelope(envelope, repo),
                ["GATE_COMMIT_NOT_ANCESTOR"],
            )

    def test_legacy_guardless_envelope_rejects_common_dir_info_graft_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, envelope, gate_commit, physical_epic_base = (
                self.legacy_guardless_envelope_fixture(Path(tmp))
            )
            graft_file = git_common_directory(repo) / "info" / "grafts"
            graft_file.parent.mkdir(parents=True, exist_ok=True)
            graft_file.write_text(
                f"{physical_epic_base} {gate_commit}\n",
                encoding="utf-8",
            )
            self.assertEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                ).returncode,
                0,
            )
            self.assertNotEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "merge-base",
                        "--is-ancestor",
                        gate_commit,
                        physical_epic_base,
                    ],
                    check=False,
                    env={
                        **os.environ,
                        "GIT_NO_REPLACE_OBJECTS": "1",
                        "GIT_GRAFT_FILE": os.devnull,
                    },
                ).returncode,
                0,
            )

            self.assertEqual(
                validate_execution_envelope(envelope, repo),
                ["GATE_COMMIT_NOT_ANCESTOR"],
            )

    def test_legacy_guardless_envelope_accepts_physical_gate_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, gate_commit = create_binding_repo(Path(tmp))
            packet = json.loads((repo / binding["path"]).read_text(encoding="utf-8"))
            self.assertFalse(
                {"planning_branch", "planning_base_sha"} & set(packet)
            )
            envelope = binding_envelope(repo, binding, gate_commit)
            self.assertNotIn("repository_guard", envelope)

            self.assertEqual(validate_execution_envelope(envelope, repo), [])

    def test_execution_envelope_schema_and_template_define_repository_guard(self) -> None:
        schema = json.loads(ENVELOPE_SCHEMA_FILE.read_text(encoding="utf-8"))
        guard_schema = schema["properties"]["repository_guard"]
        default_schema = guard_schema["properties"]["default_checkout"]
        template = json.loads(
            (
                SKILL_DIR / "assets/templates/execution-envelope.json"
            ).read_text(encoding="utf-8")
        )

        self.assertNotIn("repository_guard", schema["required"])
        self.assertEqual(
            set(guard_schema["required"]),
            {
                "planning_worktree_path",
                "planning_branch",
                "planning_base_sha",
                "default_checkout",
            },
        )
        self.assertFalse(guard_schema["additionalProperties"])
        self.assertEqual(
            set(default_schema["required"]),
            {"path", "branch", "head", "status_porcelain_v1"},
        )
        self.assertFalse(default_schema["additionalProperties"])
        self.assertIn("repository_guard", template)

    def test_execution_envelope_rejects_every_approved_intent_projection_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet_path = repo / binding["path"]
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["work_items"].append(
                {
                    "id": "ASBC-003",
                    "title": "Bind runtime state",
                    "source": {
                        "type": "local",
                        "path": "knowledge/wiki/syntheses/approved-spec-binding/issues.md",
                    },
                    "acceptance_criteria": ["Reject mixed runtime bindings."],
                    "non_goals": ["Do not migrate old runs."],
                    "verification": ["python3 -m unittest"],
                    "write_scope": ["path:skills/issue-implementation-loop"],
                    "dependencies": ["ASBC-002"],
                }
            )
            write_json(packet_path, packet)
            binding["sha256"] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
            git(repo, "add", binding["path"])
            git(repo, "commit", "-q", "-m", "seal two approved items")
            binding["gate_commit"] = git(repo, "rev-parse", "HEAD")
            valid = binding_envelope(repo, binding)
            cases = {
                "id": lambda value: value["work_items"].__setitem__(
                    "ASBC-999", value["work_items"].pop("ASBC-003")
                ),
                "title": lambda value: value["work_items"]["ASBC-002"].__setitem__(
                    "title", "Substituted title"
                ),
                "source": lambda value: value["work_items"]["ASBC-002"][
                    "source"
                ].__setitem__("path", FIXTURE_SPEC_PATH),
                "acceptance": lambda value: value["work_items"]["ASBC-002"].__setitem__(
                    "acceptance_criteria", ["Caller-selected acceptance"]
                ),
                "non_goals": lambda value: value["work_items"]["ASBC-002"].__setitem__(
                    "non_goals", ["Caller-selected non-goal"]
                ),
                "verification": lambda value: value["work_items"]["ASBC-002"].__setitem__(
                    "verification", ["true"]
                ),
                "write_scope": lambda value: value["work_items"]["ASBC-002"].__setitem__(
                    "write_scope", ["path:plugins"]
                ),
                "dependencies": lambda value: value["work_items"]["ASBC-003"].__setitem__(
                    "dependencies", []
                ),
                "dependency_strength": lambda value: value["work_items"]["ASBC-003"][
                    "dependencies"
                ][0].__setitem__("strength", "soft"),
                "dependency_release": lambda value: value["work_items"]["ASBC-003"][
                    "dependencies"
                ][0].__setitem__("release_on", "artifact_ready"),
                "dependency_base_effect": lambda value: value["work_items"]["ASBC-003"][
                    "dependencies"
                ][0].__setitem__("base_effect", "branch_from_blocker_head"),
                "remote_policy": lambda value: value["remote_write_policy"].__setitem__(
                    "mode", "per_action"
                ),
                "remote_actions": lambda value: value["remote_write_policy"].__setitem__(
                    "approved_actions", ["final_pr_push_head"]
                ),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    envelope = copy.deepcopy(valid)
                    mutate(envelope)
                    path = repo / f"substituted-{name}.json"
                    write_json(path, envelope)
                    result = run_script(
                        "validate_execution_envelope.py",
                        str(path),
                        "--repo-root",
                        str(repo),
                        "--json",
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
                    )

    def test_execution_envelope_is_closed_and_rejects_boolean_integers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            valid = binding_envelope(repo, binding)
            cases = {
                "missing_human_policy": lambda value: value.pop("human_policy"),
                "unknown_top_level": lambda value: value.__setitem__("human_polciy", {}),
                "revision_bool": lambda value: value.__setitem__("revision", True),
                "unknown_nested": lambda value: value["human_policy"].__setitem__(
                    "typo", True
                ),
                "nested_integer_bool": lambda value: value["review_policy"].__setitem__(
                    "max_review_cycles", True
                ),
                "session_boolean_as_integer": lambda value: value["context_policy"][
                    "session_compaction"
                ].__setitem__("mandatory_phase_transition_gc", 1),
                "phase_boolean_as_integer": lambda value: value[
                    "phase_branch_policy"
                ].__setitem__("phase_approval_commit_required", 1),
            }
            for name, mutate in cases.items():
                with self.subTest(name=name):
                    envelope = copy.deepcopy(valid)
                    mutate(envelope)
                    path = repo / f"closed-{name}.json"
                    write_json(path, envelope)
                    result = run_script(
                        "validate_execution_envelope.py",
                        str(path),
                        "--repo-root",
                        str(repo),
                    )
                    self.assertNotEqual(result.returncode, 0)

    def test_prepare_rejects_packet_or_spec_blob_drift_at_exact_epic_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for changed_path in ("packet", "spec"):
                with self.subTest(changed_path=changed_path):
                    case_root = root / changed_path
                    case_root.mkdir()
                    repo, binding, gate_commit = create_binding_repo(case_root)
                    if changed_path == "packet":
                        target = repo / binding["path"]
                    else:
                        target = (
                            repo
                            / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
                        )
                    target.write_bytes(target.read_bytes() + b"drift")
                    git(repo, "add", target.relative_to(repo).as_posix())
                    git(repo, "commit", "-q", "-m", "drift projection")
                    epic_base = git(repo, "rev-parse", "HEAD")
                    target.write_bytes(
                        subprocess.run(
                            ["git", "-C", str(repo), "show", f"{gate_commit}:{target.relative_to(repo).as_posix()}"],
                            check=True,
                            capture_output=True,
                        ).stdout
                    )
                    envelope = binding_envelope(repo, binding, epic_base)
                    path = repo / f"epic-base-{changed_path}.json"
                    write_json(path, envelope)
                    result = run_script(
                        "validate_execution_envelope.py",
                        str(path),
                        "--repo-root",
                        str(repo),
                        "--json",
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(
                        json.loads(result.stdout)["errors"], ["PROJECTION_MISMATCH"]
                    )

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
            spec_bytes = (
                repo / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
            ).read_bytes()
            git(repo, "checkout", "-q", "-b", "side", base_commit)
            synthesis = repo / "knowledge/wiki/syntheses/approved-spec-binding"
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
                        spec_path = (
                            repo
                            / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
                        )
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
            spec_path = repo / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
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
                "knowledge/wiki/syntheses/approved-spec-binding/linked-issues.md"
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
            spec_path = repo / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
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
            spec_path = repo / "knowledge/wiki/syntheses/approved-spec-binding/spec.md"
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

    def test_validate_execution_envelope_accepts_current_context_policy_without_optional_worker_packet_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            envelope = binding_envelope(repo, binding)
            for field in (
                "worker_packet_schema",
                "worker_packet_template",
                "worker_packet_validator",
            ):
                del envelope["context_policy"][field]
            path = repo / "current-envelope-without-worker-packet-refs.json"
            write_json(path, envelope)

            result = run_script(
                "validate_execution_envelope.py", str(path), "--repo-root", str(repo)
            )

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
            repo, binding, _ = create_binding_repo(Path(tmp))
            path = repo / "envelope.json"
            write_json(path, binding_envelope(repo, binding))

            result = run_script(
                "validate_execution_envelope.py", str(path), "--repo-root", str(repo)
            )

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
            repo, binding, _ = create_binding_repo(
                Path(tmp), delivery_intent="batch_issue_prs"
            )
            envelope = binding_envelope(repo, binding)
            path = repo / "envelope.json"
            write_json(path, envelope)

            result = run_script(
                "validate_execution_envelope.py", str(path), "--repo-root", str(repo)
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_execution_envelope_accepts_final_pr_auto_create_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(
                Path(tmp), delivery_intent="batch_issue_prs"
            )
            envelope = binding_envelope(repo, binding)
            envelope["remote_write_policy"]["approved_actions"] = [
                "final_pr_push_head",
                "final_pr_create_draft",
            ]
            path = repo / "envelope.json"
            write_json(path, envelope)

            result = run_script(
                "validate_execution_envelope.py", str(path), "--repo-root", str(repo)
            )

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
        local_rule = next(
            rule
            for rule in schema["properties"]["remote_write_policy"]["allOf"]
            if rule["if"]["properties"]["mode"].get("const") == "local_only"
        )
        self.assertEqual(
            local_rule["then"]["properties"]["approved_actions"]["maxItems"],
            0,
        )

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
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
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
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base_sha", result.stderr)
            self.assertIn("head_sha", result.stderr)

    def test_validate_worker_report_accepts_committed_pr_ready_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
            write_json(packet_path, packet)
            write_json(report_path, current_worker_report(repo, binding, packet))

            result = run_script(
                "validate_worker_report.py",
                str(report_path),
                "--dispatch-packet",
                str(packet_path),
                "--runtime-state",
                str(runtime_path),
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validate_worker_report_rejects_pr_ready_with_unapproved_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
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
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("implementation_review.status must be approved", result.stderr)

    def test_worker_report_v1_is_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
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
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["SCHEMA_UNSUPPORTED"]
            )

    def test_worker_report_v2_requires_well_formed_residual_risks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = (
                ("missing", lambda report: report.pop("residual_risks"), "residual_risks must be a list"),
                ("not-list", lambda report: report.update({"residual_risks": "none"}), "residual_risks must be a list"),
                ("empty-item", lambda report: report.update({"residual_risks": ["  "]}), "residual_risks[0] must be a non-empty string"),
            )
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    case_root = root / name
                    case_root.mkdir()
                    repo, binding, _ = create_binding_repo(case_root)
                    packet = current_worker_packet(repo, binding)
                    envelope_path, runtime_path = runtime_artifact_paths(repo)
                    packet_path = repo / "worker-packet.json"
                    report_path = repo / "worker-report.json"
                    write_json(packet_path, packet)
                    report = current_worker_report(repo, binding, packet)
                    mutate(report)
                    write_json(report_path, report)

                    result = run_script(
                        "validate_worker_report.py",
                        str(report_path),
                        "--dispatch-packet",
                        str(packet_path),
                        "--runtime-state",
                        str(runtime_path),
                        "--envelope",
                        str(envelope_path),
                        *worker_report_trust_args(repo),
                    )

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(expected, result.stderr)

    def test_worker_report_v2_schema_requires_residual_risks(self) -> None:
        schema = json.loads(
            (SKILL_DIR / "assets/schemas/worker-report.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn("residual_risks", schema["required"])
        self.assertEqual(
            schema["properties"]["residual_risks"]["items"]["pattern"],
            r".*\S.*",
        )

    def test_asb_13_worker_report_intake_rejects_resealed_runtime_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, binding, _ = create_binding_repo(Path(tmp))
            packet = current_worker_packet(repo, binding)
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "worker-packet.json"
            report_path = repo / "worker-report.json"
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
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
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
            envelope_path, runtime_path = runtime_artifact_paths(repo)
            packet_path = repo / "reviewer-packet.json"
            report_path = repo / "reviewer-report.json"
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
                "--envelope",
                str(envelope_path),
                *worker_report_trust_args(repo),
                "--json",
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(result.stdout)["errors"], ["BINDING_MISMATCH"]
            )
