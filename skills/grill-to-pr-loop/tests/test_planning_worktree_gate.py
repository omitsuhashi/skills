from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
PREPARE = SKILL_DIR / "scripts" / "planning_worktree.py"
REPOSITORY_ROOT = SKILL_DIR.parents[1]


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def initialize_repository(root: Path) -> Path:
    repo = root / "repo"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Planning Worktree Gate tests")
    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    git(repo, "add", ".gitignore", "README.md")
    git(repo, "commit", "-qm", "initial fixture")
    return repo


def default_snapshot(repo: Path) -> tuple[str, str]:
    return (
        git(repo, "rev-parse", "HEAD").stdout.strip(),
        git(repo, "status", "--porcelain=v1", "--untracked-files=all").stdout,
    )


def read_only_git(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        env=environment,
    )


def runtime_state(repo: Path, epic_id: str = "planning-worktree-gate") -> Path:
    common_dir = Path(
        read_only_git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    )
    if not common_dir.is_absolute():
        common_dir = repo / common_dir
    return (
        common_dir.resolve()
        / "agent-runs"
        / "grill-to-pr-loop"
        / epic_id
        / "planning-worktree.json"
    )


def run_prepare(
    repo: Path,
    worktree_root: Path,
    *,
    epic_id: str = "planning-worktree-gate",
    environment_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(environment_overrides or {})
    return subprocess.run(
        [
            sys.executable,
            str(PREPARE),
            "prepare",
            "--repo-root",
            str(repo),
            "--epic-id",
            epic_id,
            "--worktree-root",
            str(worktree_root),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def load_planning_worktree_module():
    module_name = "planning_worktree_test_target"
    spec = importlib.util.spec_from_file_location(module_name, PREPARE)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load planning_worktree.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PlanningWorktreeGateTests(unittest.TestCase):
    def test_planning_worktree_gate_contract_routes_each_planning_operation(self) -> None:
        skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        core_text = (SKILL_DIR / "references" / "core.md").read_text(encoding="utf-8")
        planning_text = (SKILL_DIR / "references" / "planning-contract.md").read_text(
            encoding="utf-8"
        )
        handoff_text = (SKILL_DIR / "references" / "execution-handoff.md").read_text(
            encoding="utf-8"
        )
        mistakes_text = (SKILL_DIR / "references" / "common-mistakes.md").read_text(
            encoding="utf-8"
        )
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(
            encoding="utf-8"
        )

        self.assertIn("Planning Worktree Gate", skill_text)
        self.assertIn("Planning Worktree Gate", core_text)
        self.assertIn("planning_worktree.py prepare", planning_text)
        self.assertIn("one Epic-scoped planning worktree", planning_text)
        self.assertIn("tracked/runtime identity boundary", handoff_text)
        self.assertIn("Planning Worktree Gate", mistakes_text)
        for operation in ('[operations.intake]', '[operations.spec]', '[operations."issue-gate"]', '[operations."execution-plan"]'):
            start = contract_text.index(operation)
            next_operation = contract_text.find("[operations.", start + len(operation))
            operation_block = contract_text[start : next_operation if next_operation != -1 else None]
            self.assertIn('"references/planning-contract.md"', operation_block)
        self.assertTrue((REPOSITORY_ROOT / "AGENTS.md").is_file())

    def test_prepare_creates_planning_worktree_before_first_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            before = default_snapshot(repo)

            result = run_prepare(repo, repo / ".worktrees")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["epic_id"], "planning-worktree-gate")
            self.assertEqual(
                payload["planning_branch"],
                "codex/planning-worktree-gate/planning",
            )
            self.assertEqual(payload["planning_base_sha"], before[0])
            self.assertFalse(payload["reused"])
            self.assertEqual(Path(payload["default_checkout"]), repo.resolve())
            self.assertTrue(Path(payload["runtime_state_path"]).is_file())
            self.assertTrue((repo / ".worktrees" / "planning-worktree-gate").is_dir())
            self.assertEqual(default_snapshot(repo), before)

    def test_prepare_reuses_existing_epic_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)

            second = run_prepare(repo, worktree_root)

            self.assertEqual(second.returncode, 0, second.stderr)
            payload = json.loads(second.stdout)
            self.assertTrue(payload["reused"])
            self.assertEqual(
                Path(payload["runtime_state_path"]),
                Path(json.loads(first.stdout)["runtime_state_path"]),
            )
            self.assertEqual(
                git(repo, "worktree", "list", "--porcelain").stdout.count(
                    "branch refs/heads/codex/planning-worktree-gate/planning"
                ),
                1,
            )

    def test_prepare_adopts_registered_epic_worktree_without_runtime_identity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"
            planning_branch = "codex/planning-worktree-gate/planning"
            git(
                repo,
                "worktree",
                "add",
                "-b",
                planning_branch,
                str(planning_worktree),
                "HEAD",
            )
            (planning_worktree / "planning.md").write_text(
                "pre-existing planning work\n", encoding="utf-8"
            )
            git(planning_worktree, "add", "planning.md")
            git(planning_worktree, "commit", "-qm", "planning before CLI")
            before = default_snapshot(repo)
            state_path = runtime_state(repo)
            self.assertFalse(state_path.exists())

            result = run_prepare(repo, repo / ".worktrees")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            persisted = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["reused"])
            self.assertEqual(
                Path(payload["planning_worktree"]), planning_worktree.resolve()
            )
            self.assertEqual(payload["planning_base_sha"], before[0])
            self.assertEqual(
                persisted["default_checkout_start"],
                {"head": before[0], "status_porcelain": before[1]},
            )
            self.assertEqual(
                persisted["planning_worktree"], str(planning_worktree.resolve())
            )
            self.assertEqual(default_snapshot(repo), before)

    def test_prepare_does_not_replace_invalid_registered_worktree_runtime_identity(
        self,
    ) -> None:
        for artifact in (
            b"{not-json\n",
            b"\xff",
            json.dumps(
                {
                    "schema_version": 1,
                    "epic_id": "different-epic",
                    "planning_branch": "codex/planning-worktree-gate/planning",
                }
            ).encode("utf-8"),
        ):
            with self.subTest(artifact=artifact):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repo = initialize_repository(Path(temporary_directory))
                    planning_worktree = (
                        repo / ".worktrees" / "planning-worktree-gate"
                    )
                    git(
                        repo,
                        "worktree",
                        "add",
                        "-b",
                        "codex/planning-worktree-gate/planning",
                        str(planning_worktree),
                        "HEAD",
                    )
                    state_path = runtime_state(repo)
                    state_path.parent.mkdir(parents=True)
                    state_path.write_bytes(artifact)

                    result = run_prepare(repo, repo / ".worktrees")

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "planning runtime identity artifact",
                        json.loads(result.stdout)["error"],
                    )
                    self.assertEqual(state_path.read_bytes(), artifact)

    def test_prepare_rejects_registered_worktree_without_runtime_identity_when_default_advanced(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"
            git(
                repo,
                "worktree",
                "add",
                "-b",
                "codex/planning-worktree-gate/planning",
                str(planning_worktree),
                "HEAD",
            )
            (repo / "README.md").write_text("advanced default branch\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            state_path = runtime_state(repo)

            result = run_prepare(repo, repo / ".worktrees")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "current default HEAD is not an ancestor",
                json.loads(result.stdout)["error"],
            )
            self.assertTrue(planning_worktree.is_dir())
            self.assertFalse(state_path.exists())

    def test_reuse_rejects_default_head_drift_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_payload = json.loads(first.stdout)
            state_path = Path(first_payload["runtime_state_path"])
            initial_state_bytes = state_path.read_bytes()

            (repo / "README.md").write_text("advanced default branch\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            drifted_snapshot = default_snapshot(repo)

            second = run_prepare(repo, worktree_root)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("default checkout", json.loads(second.stdout)["error"])
            self.assertEqual(state_path.read_bytes(), initial_state_bytes)
            self.assertEqual(default_snapshot(repo), drifted_snapshot)

    def test_reuse_rejects_default_status_drift_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            (repo / "pre-existing.txt").write_text("preserve me\n", encoding="utf-8")
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = Path(json.loads(first.stdout)["runtime_state_path"])
            initial_state_bytes = state_path.read_bytes()

            (repo / "task-drift.txt").write_text("do not remove me\n", encoding="utf-8")
            drifted_snapshot = default_snapshot(repo)

            second = run_prepare(repo, worktree_root)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("default checkout", json.loads(second.stdout)["error"])
            self.assertEqual(state_path.read_bytes(), initial_state_bytes)
            self.assertEqual(default_snapshot(repo), drifted_snapshot)
            self.assertEqual(
                (repo / "pre-existing.txt").read_text(encoding="utf-8"),
                "preserve me\n",
            )
            self.assertEqual(
                (repo / "task-drift.txt").read_text(encoding="utf-8"),
                "do not remove me\n",
            )

    def test_reuse_rejects_planning_head_without_base_ancestry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_payload = json.loads(first.stdout)
            state_path = Path(first_payload["runtime_state_path"])
            initial_state_bytes = state_path.read_bytes()
            tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
            unrelated_head = subprocess.run(
                ["git", "-C", str(repo), "commit-tree", tree],
                check=True,
                capture_output=True,
                text=True,
                input="unrelated planning history\n",
            ).stdout.strip()
            planning_branch = first_payload["planning_branch"]
            git(
                repo,
                "update-ref",
                f"refs/heads/{planning_branch}",
                unrelated_head,
            )
            before = default_snapshot(repo)

            second = run_prepare(repo, worktree_root)

            self.assertNotEqual(second.returncode, 0)
            self.assertIn("planning worktree HEAD", json.loads(second.stdout)["error"])
            self.assertEqual(state_path.read_bytes(), initial_state_bytes)
            self.assertEqual(default_snapshot(repo), before)
            self.assertEqual(
                git(
                    Path(first_payload["planning_worktree"]),
                    "rev-parse",
                    "HEAD",
                ).stdout.strip(),
                unrelated_head,
            )

    def test_reuse_rejects_corrupt_or_mismatched_runtime_identity(self) -> None:
        cases = (
            ("extra top-level field", lambda state, repo: state.update(extra=True)),
            ("boolean schema version", lambda state, repo: state.update(schema_version=True)),
            ("short base", lambda state, repo: state.update(planning_base_sha="abc123")),
            ("nonhex base", lambda state, repo: state.update(planning_base_sha="g" * 40)),
            ("uppercase base", lambda state, repo: state.update(planning_base_sha="A" * 40)),
            (
                "snapshot base mismatch",
                lambda state, repo: state["default_checkout_start"].update(
                    head="0" * 40
                ),
            ),
            (
                "snapshot extra field",
                lambda state, repo: state["default_checkout_start"].update(extra=True),
            ),
            (
                "branch mismatch",
                lambda state, repo: state.update(
                    planning_branch="codex/different-epic/planning"
                ),
            ),
            (
                "relative default path",
                lambda state, repo: state.update(default_checkout="repo"),
            ),
            (
                "invalid default path",
                lambda state, repo: state.update(default_checkout="/\0"),
            ),
            (
                "planning path mismatch",
                lambda state, repo: state.update(planning_worktree=str(repo)),
            ),
            (
                "relative worktree root",
                lambda state, repo: state.update(worktree_root=".worktrees"),
            ),
            (
                "worktree root mismatch",
                lambda state, repo: state.update(
                    worktree_root=str(repo / "other-worktrees")
                ),
            ),
        )
        for name, mutate in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repo = initialize_repository(Path(temporary_directory))
                    worktree_root = repo / ".worktrees"
                    first = run_prepare(repo, worktree_root)
                    self.assertEqual(first.returncode, 0, first.stderr)
                    state_path = Path(json.loads(first.stdout)["runtime_state_path"])
                    corrupt_state = json.loads(state_path.read_text(encoding="utf-8"))
                    mutate(corrupt_state, repo)
                    state_path.write_text(
                        json.dumps(corrupt_state, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                    corrupt_bytes = state_path.read_bytes()
                    before = default_snapshot(repo)

                    second = run_prepare(repo, worktree_root)

                    self.assertNotEqual(second.returncode, 0, second.stdout)
                    self.assertFalse(json.loads(second.stdout)["ok"])
                    self.assertEqual(state_path.read_bytes(), corrupt_bytes)
                    self.assertEqual(default_snapshot(repo), before)

    def test_reuse_revalidates_live_snapshot_immediately_before_return(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            initial_snapshot = default_snapshot(repo)
            module = load_planning_worktree_module()
            arguments = argparse.Namespace(
                repo_root=str(repo),
                epic_id="planning-worktree-gate",
                default_branch="main",
                worktree_root=str(worktree_root),
                json=True,
            )

            with mock.patch.object(
                module,
                "default_checkout_snapshot",
                side_effect=(
                    initial_snapshot,
                    (initial_snapshot[0], initial_snapshot[1] + "?? drift\n"),
                ),
            ) as snapshot:
                with self.assertRaisesRegex(
                    module.GateError, "default checkout"
                ):
                    module.prepare(arguments)

            self.assertEqual(snapshot.call_count, 2)

    def test_default_snapshot_rejects_drift_during_collection(self) -> None:
        module = load_planning_worktree_module()
        for name, observations in (
            (
                "head drift",
                ("a" * 40, "", "b" * 40, ""),
            ),
            (
                "status drift",
                ("a" * 40, "", "a" * 40, "?? drift\n"),
            ),
        ):
            with self.subTest(name=name):
                with mock.patch.object(
                    module,
                    "git",
                    side_effect=observations,
                ):
                    with self.assertRaisesRegex(
                        module.GateError, "changed while its snapshot was collected"
                    ):
                        module.default_checkout_snapshot(Path("/unused"))

    def test_reuse_rechecks_artifact_after_final_live_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = Path(json.loads(first.stdout)["runtime_state_path"])
            module = load_planning_worktree_module()
            original_validate = module.validate_runtime_reuse
            validation_count = 0

            def validate_then_replace_artifact(*args, **kwargs) -> None:
                nonlocal validation_count
                validation_count += 1
                original_validate(*args, **kwargs)
                if validation_count == 2:
                    corrupt_state = json.loads(
                        state_path.read_text(encoding="utf-8")
                    )
                    corrupt_state["planning_base_sha"] = "abc123"
                    state_path.write_text(
                        json.dumps(corrupt_state), encoding="utf-8"
                    )

            arguments = argparse.Namespace(
                repo_root=str(repo),
                epic_id="planning-worktree-gate",
                default_branch="main",
                worktree_root=str(worktree_root),
                json=True,
            )

            with mock.patch.object(
                module,
                "validate_runtime_reuse",
                side_effect=validate_then_replace_artifact,
            ):
                with self.assertRaisesRegex(
                    module.GateError, "planning_base_sha"
                ):
                    module.prepare(arguments)

            self.assertEqual(validation_count, 2)
            self.assertEqual(
                json.loads(state_path.read_text(encoding="utf-8"))[
                    "planning_base_sha"
                ],
                "abc123",
            )

    def test_reuse_rejects_duplicate_runtime_identity_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            state_path = Path(json.loads(first.stdout)["runtime_state_path"])
            valid_text = state_path.read_text(encoding="utf-8")
            corrupt_text = valid_text.replace(
                '"schema_version": 1,',
                '"schema_version": 1, "schema_version": 1,',
                1,
            )
            self.assertNotEqual(corrupt_text, valid_text)
            state_path.write_text(corrupt_text, encoding="utf-8")
            before = default_snapshot(repo)

            second = run_prepare(repo, worktree_root)

            self.assertNotEqual(second.returncode, 0, second.stdout)
            self.assertFalse(json.loads(second.stdout)["ok"])
            self.assertEqual(state_path.read_text(encoding="utf-8"), corrupt_text)
            self.assertEqual(default_snapshot(repo), before)

    def test_runtime_identity_accepts_canonical_sha256_base(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            default_checkout = root / "default"
            worktree_root = root / "worktrees"
            planning_worktree = worktree_root / "planning-worktree-gate"
            default_checkout.mkdir()
            planning_worktree.mkdir(parents=True)
            state_path = root / "planning-worktree.json"
            module = load_planning_worktree_module()
            planning_base_sha = "a" * 64
            payload = module.runtime_payload(
                epic_id="planning-worktree-gate",
                planning_branch="codex/planning-worktree-gate/planning",
                planning_base_sha=planning_base_sha,
                default_checkout=default_checkout.resolve(),
                worktree_root=worktree_root.resolve(),
                planning_worktree=planning_worktree.resolve(),
                start_status="",
            )
            state_path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = module.load_runtime_identity(
                state_path,
                epic_id="planning-worktree-gate",
                planning_branch="codex/planning-worktree-gate/planning",
                default_checkout=default_checkout.resolve(),
                worktree_root=worktree_root.resolve(),
                planning_worktree=planning_worktree.resolve(),
            )

            self.assertEqual(loaded["planning_base_sha"], planning_base_sha)

    def test_repeated_gate_entry_returns_same_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"

            first = run_prepare(repo, worktree_root)
            second = run_prepare(repo, worktree_root)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(
                json.loads(first.stdout)["runtime_state_path"],
                json.loads(second.stdout)["runtime_state_path"],
            )
            self.assertEqual(
                (worktree_root / "planning-worktree-gate").resolve(),
                Path(json.loads(second.stdout)["planning_worktree"]),
            )

    def test_worktree_creation_failure_does_not_write_default_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            before = default_snapshot(repo)

            result = run_prepare(repo, repo / "unignored-worktrees")

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(default_snapshot(repo), before)
            self.assertFalse(
                git(
                    repo,
                    "show-ref",
                    "--verify",
                    "refs/heads/codex/planning-worktree-gate/planning",
                    check=False,
                ).returncode
                == 0
            )

    def test_git_worktree_add_failure_preserves_default_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            before = default_snapshot(repo)
            before_readme = (repo / "README.md").read_text(encoding="utf-8")
            branch_lock = (
                repo
                / ".git"
                / "refs"
                / "heads"
                / "codex"
                / "planning-worktree-gate"
                / "planning.lock"
            )
            branch_lock.parent.mkdir(parents=True)
            branch_lock.write_text("held by test\n", encoding="utf-8")

            result = run_prepare(repo, repo / ".worktrees")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("git worktree add", json.loads(result.stdout)["error"])
            self.assertEqual(default_snapshot(repo), before)
            self.assertEqual((repo / "README.md").read_text(encoding="utf-8"), before_readme)
            self.assertFalse((repo / ".worktrees" / "planning-worktree-gate").exists())

    def test_prepare_preserves_preexisting_dirt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            (repo / "unrelated.txt").write_text("keep me\n", encoding="utf-8")
            before = default_snapshot(repo)

            result = run_prepare(repo, repo / ".worktrees")

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            runtime_state = json.loads(
                Path(payload["runtime_state_path"]).read_text(encoding="utf-8")
            )
            self.assertEqual(runtime_state["default_checkout_start"]["head"], before[0])
            self.assertEqual(runtime_state["default_checkout_start"]["status_porcelain"], before[1])
            self.assertEqual(default_snapshot(repo), before)

            reused = run_prepare(repo, repo / ".worktrees")

            self.assertEqual(reused.returncode, 0, reused.stderr)
            self.assertTrue(json.loads(reused.stdout)["reused"])
            self.assertEqual(default_snapshot(repo), before)

    def test_prepare_preserves_default_index_bytes_with_stale_stat_metadata(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            index_path = Path(
                read_only_git(repo, "rev-parse", "--git-path", "index").stdout.strip()
            )
            if not index_path.is_absolute():
                index_path = repo / index_path
            tracked_file = repo / "README.md"
            tracked_stat = tracked_file.stat()
            os.utime(
                tracked_file,
                ns=(
                    tracked_stat.st_atime_ns,
                    tracked_stat.st_mtime_ns + 2_000_000_000,
                ),
            )
            self.assertEqual(
                read_only_git(
                    repo, "status", "--porcelain=v1", "--untracked-files=all"
                ).stdout,
                "",
            )
            before_bytes = index_path.read_bytes()
            before_hash = hashlib.sha256(before_bytes).hexdigest()

            result = run_prepare(repo, repo / ".worktrees")

            self.assertEqual(result.returncode, 0, result.stderr)
            after_bytes = index_path.read_bytes()
            self.assertEqual(after_bytes, before_bytes)
            self.assertEqual(hashlib.sha256(after_bytes).hexdigest(), before_hash)
            self.assertEqual(
                read_only_git(
                    repo, "status", "--porcelain=v1", "--untracked-files=all"
                ).stdout,
                "",
            )

    def test_prepare_rejects_unregistered_branch_not_based_on_current_default_head(
        self,
    ) -> None:
        for topology in ("behind", "divergent"):
            with self.subTest(topology=topology):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    repo = initialize_repository(Path(temporary_directory))
                    planning_branch = "codex/planning-worktree-gate/planning"
                    git(repo, "switch", "-qc", planning_branch)
                    if topology == "divergent":
                        (repo / "planning.md").write_text(
                            "divergent planning\n", encoding="utf-8"
                        )
                        git(repo, "add", "planning.md")
                        git(repo, "commit", "-qm", "diverge planning")
                    git(repo, "switch", "-q", "main")
                    (repo / "README.md").write_text(
                        f"advance main for {topology}\n", encoding="utf-8"
                    )
                    git(repo, "add", "README.md")
                    git(repo, "commit", "-qm", "advance main")
                    destination = repo / ".worktrees" / "planning-worktree-gate"
                    state_path = runtime_state(repo)

                    result = run_prepare(repo, repo / ".worktrees")

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "current default HEAD is not an ancestor",
                        json.loads(result.stdout)["error"],
                    )
                    self.assertFalse(destination.exists())
                    self.assertFalse(state_path.exists())

    def test_prepare_revalidates_after_worktree_add_hook_mutates_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            incompatible_head = git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "README.md").write_text("advance default\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            planning_branch = "codex/planning-worktree-gate/planning"
            git(repo, "branch", planning_branch, "HEAD")
            hook = repo / ".git" / "hooks" / "post-checkout"
            hook.write_text(
                "#!/bin/sh\n"
                f"git update-ref refs/heads/{planning_branch} {incompatible_head}\n",
                encoding="utf-8",
            )
            hook.chmod(0o755)
            state_path = runtime_state(repo)
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"

            result = run_prepare(repo, repo / ".worktrees")

            self.assertNotEqual(result.returncode, 0)
            error = json.loads(result.stdout)["error"]
            self.assertIn(str(planning_worktree.resolve()), error)
            self.assertIn(planning_branch, error)
            self.assertIn("runtime identity was not published", error)
            self.assertTrue(planning_worktree.is_dir())
            self.assertFalse(state_path.exists())
            self.assertEqual(
                git(planning_worktree, "rev-parse", "HEAD").stdout.strip(),
                incompatible_head,
            )

    def test_prepare_revalidates_default_after_worktree_add_hook_creates_drift(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            preexisting = repo / "pre-existing.txt"
            preexisting.write_text("preserve me\n", encoding="utf-8")
            before = default_snapshot(repo)
            drift = repo / "default-drift.txt"
            quoted_drift = "'" + str(drift).replace("'", "'\"'\"'") + "'"
            hook = repo / ".git" / "hooks" / "post-checkout"
            hook.write_text(
                "#!/bin/sh\n"
                f"printf 'hook drift\\n' > {quoted_drift}\n",
                encoding="utf-8",
            )
            hook.chmod(0o755)
            state_path = runtime_state(repo)
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"

            result = run_prepare(repo, repo / ".worktrees")

            self.assertNotEqual(result.returncode, 0)
            error = json.loads(result.stdout)["error"]
            self.assertIn(str(planning_worktree.resolve()), error)
            self.assertIn(
                "codex/planning-worktree-gate/planning",
                error,
            )
            self.assertIn("was created and left in place", error)
            self.assertIn("manual inspection", error)
            self.assertIn("runtime identity was not published", error)
            self.assertIn("default checkout", error)
            self.assertTrue(planning_worktree.is_dir())
            self.assertFalse(state_path.exists())
            self.assertEqual(
                preexisting.read_text(encoding="utf-8"),
                "preserve me\n",
            )
            self.assertEqual(drift.read_text(encoding="utf-8"), "hook drift\n")
            after = default_snapshot(repo)
            self.assertEqual(after[0], before[0])
            self.assertEqual(
                set(after[1].splitlines()),
                set(before[1].splitlines()) | {"?? default-drift.txt"},
            )

    def test_prepare_revalidates_registered_worktree_immediately_before_publish(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            incompatible_head = git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "README.md").write_text("advance default\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            planning_branch = "codex/planning-worktree-gate/planning"
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"
            git(
                repo,
                "worktree",
                "add",
                "-b",
                planning_branch,
                str(planning_worktree),
                "HEAD",
            )
            state_path = runtime_state(repo)
            module = load_planning_worktree_module()
            original_verify = module.verify_registered_planning_worktree
            verification_count = 0

            def verify_then_mutate(*args, **kwargs) -> None:
                nonlocal verification_count
                verification_count += 1
                original_verify(*args, **kwargs)
                if verification_count == 1:
                    git(
                        repo,
                        "update-ref",
                        f"refs/heads/{planning_branch}",
                        incompatible_head,
                    )

            arguments = argparse.Namespace(
                repo_root=str(repo),
                epic_id="planning-worktree-gate",
                default_branch="main",
                worktree_root=str(repo / ".worktrees"),
                json=True,
            )

            with mock.patch.object(
                module,
                "verify_registered_planning_worktree",
                side_effect=verify_then_mutate,
            ):
                with self.assertRaises(module.GateError):
                    module.prepare(arguments)

            self.assertGreaterEqual(verification_count, 2)
            self.assertFalse(state_path.exists())
            self.assertEqual(
                git(planning_worktree, "rev-parse", "HEAD").stdout.strip(),
                incompatible_head,
            )

    def test_prepare_sanitizes_hostile_repository_routing_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            repo_a = initialize_repository(temporary_root / "a")
            repo_b = initialize_repository(temporary_root / "b")
            git(repo_b, "config", "core.worktree", str(repo_b))
            before_b = default_snapshot(repo_b)
            before_b_index = (repo_b / ".git" / "index").read_bytes()
            before_b_worktrees = git(repo_b, "worktree", "list", "--porcelain").stdout
            hostile_environment = {
                "GIT_DIR": str(repo_b / ".git"),
                "GIT_WORK_TREE": str(repo_b),
                "GIT_COMMON_DIR": str(repo_b / ".git"),
                "GIT_CONFIG": str(repo_b / ".git" / "config"),
                "GIT_INDEX_FILE": str(repo_b / ".git" / "index"),
                "GIT_OBJECT_DIRECTORY": str(repo_b / ".git" / "objects"),
                "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(repo_b / ".git" / "objects"),
                "GIT_NAMESPACE": "hostile",
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.worktree",
                "GIT_CONFIG_VALUE_0": str(repo_b),
            }

            result = run_prepare(
                repo_a,
                repo_a / ".worktrees",
                environment_overrides=hostile_environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(Path(payload["default_checkout"]), repo_a.resolve())
            self.assertEqual(
                Path(payload["planning_worktree"]),
                (repo_a / ".worktrees" / "planning-worktree-gate").resolve(),
            )
            self.assertEqual(default_snapshot(repo_b), before_b)
            self.assertEqual((repo_b / ".git" / "index").read_bytes(), before_b_index)
            self.assertEqual(
                git(repo_b, "worktree", "list", "--porcelain").stdout,
                before_b_worktrees,
            )
            self.assertFalse(runtime_state(repo_b).exists())

    def test_prepare_rejects_replace_ref_that_rewrites_physical_branch_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            replaced_head = git(repo, "rev-parse", "HEAD").stdout.strip()
            planning_branch = "codex/planning-worktree-gate/planning"
            git(repo, "branch", planning_branch, replaced_head)
            (repo / "README.md").write_text("advance default\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            default_head = git(repo, "rev-parse", "HEAD").stdout.strip()
            tree = git(repo, "rev-parse", f"{replaced_head}^{{tree}}").stdout.strip()
            replacement = subprocess.run(
                ["git", "-C", str(repo), "commit-tree", tree, "-p", default_head],
                check=True,
                capture_output=True,
                text=True,
                input="replacement history\n",
            ).stdout.strip()
            git(
                repo,
                "update-ref",
                f"refs/replace/{replaced_head}",
                replacement,
            )
            self.assertEqual(
                git(
                    repo,
                    "merge-base",
                    "--is-ancestor",
                    default_head,
                    planning_branch,
                    check=False,
                ).returncode,
                0,
            )
            no_replace_environment = os.environ.copy()
            no_replace_environment["GIT_NO_REPLACE_OBJECTS"] = "1"
            self.assertNotEqual(
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(repo),
                        "merge-base",
                        "--is-ancestor",
                        default_head,
                        planning_branch,
                    ],
                    check=False,
                    env=no_replace_environment,
                ).returncode,
                0,
            )

            result = run_prepare(
                repo,
                repo / ".worktrees",
                environment_overrides={"GIT_NO_REPLACE_OBJECTS": "0"},
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "current default HEAD is not an ancestor",
                json.loads(result.stdout)["error"],
            )
            self.assertFalse(
                (repo / ".worktrees" / "planning-worktree-gate").exists()
            )
            self.assertFalse(runtime_state(repo).exists())

    def test_prepare_rejects_info_graft_that_rewrites_physical_worktree_ancestry(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            planning_branch = "codex/planning-worktree-gate/planning"
            planning_worktree = repo / ".worktrees" / "planning-worktree-gate"
            git(
                repo,
                "worktree",
                "add",
                "-b",
                planning_branch,
                str(planning_worktree),
                "HEAD",
            )
            (planning_worktree / "planning.md").write_text(
                "divergent planning\n", encoding="utf-8"
            )
            git(planning_worktree, "add", "planning.md")
            git(planning_worktree, "commit", "-qm", "diverge planning")
            planning_head = git(
                planning_worktree, "rev-parse", "HEAD"
            ).stdout.strip()
            (repo / "README.md").write_text("advance default\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")
            default_head = git(repo, "rev-parse", "HEAD").stdout.strip()
            graft_file = repo / ".git" / "info" / "grafts"
            graft_file.write_text(
                f"{planning_head} {default_head}\n",
                encoding="utf-8",
            )
            self.assertEqual(
                git(
                    repo,
                    "merge-base",
                    "--is-ancestor",
                    default_head,
                    planning_branch,
                    check=False,
                ).returncode,
                0,
            )
            state_path = runtime_state(repo)

            result = run_prepare(
                repo,
                repo / ".worktrees",
                environment_overrides={
                    "GIT_GRAFT_FILE": str(graft_file),
                    "GIT_NO_REPLACE_OBJECTS": "0",
                },
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "current default HEAD is not an ancestor",
                json.loads(result.stdout)["error"],
            )
            self.assertTrue(planning_worktree.is_dir())
            self.assertFalse(state_path.exists())
            self.assertEqual(
                git(planning_worktree, "rev-parse", "HEAD").stdout.strip(),
                planning_head,
            )

    def test_sanitizer_covers_git_local_environment_variables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            module = load_planning_worktree_module()
            local_environment = set(
                git(repo, "rev-parse", "--local-env-vars").stdout.splitlines()
            )

            self.assertEqual(
                local_environment - module.REPOSITORY_ROUTING_ENVIRONMENT,
                set(),
            )
            trusted_overrides = {
                "GIT_NO_REPLACE_OBJECTS": "1",
                "GIT_GRAFT_FILE": os.devnull,
            }
            hostile_local_environment = {
                name: "hostile" for name in local_environment
            }
            hostile_local_environment.update(
                {
                    "GIT_CONFIG_KEY_0": "core.worktree",
                    "GIT_CONFIG_VALUE_0": str(repo),
                    "GIT_CONFIG_GLOBAL": "/trusted/global-config",
                    "GIT_CONFIG_SYSTEM": "/trusted/system-config",
                }
            )
            with mock.patch.dict(
                os.environ,
                hostile_local_environment,
                clear=False,
            ):
                read_only_environment = module.git_environment(read_only=True)
                write_environment = module.git_environment(read_only=False)
            for environment in (read_only_environment, write_environment):
                for name in local_environment - trusted_overrides.keys():
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
                self.assertEqual(
                    environment["GIT_CONFIG_GLOBAL"],
                    "/trusted/global-config",
                )
                self.assertEqual(
                    environment["GIT_CONFIG_SYSTEM"],
                    "/trusted/system-config",
                )
            self.assertEqual(read_only_environment["GIT_OPTIONAL_LOCKS"], "0")
            self.assertNotIn("GIT_OPTIONAL_LOCKS", write_environment)
            for global_environment in (
                "GIT_CONFIG_GLOBAL",
                "GIT_CONFIG_SYSTEM",
                "HOME",
                "XDG_CONFIG_HOME",
            ):
                self.assertNotIn(
                    global_environment,
                    module.REPOSITORY_ROUTING_ENVIRONMENT,
                )


if __name__ == "__main__":
    unittest.main()
