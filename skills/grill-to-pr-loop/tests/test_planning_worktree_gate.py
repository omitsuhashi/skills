from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


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
) -> subprocess.CompletedProcess[str]:
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
    )


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

    def test_reuse_preserves_initial_runtime_identity_after_default_branch_advances(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo = initialize_repository(Path(temporary_directory))
            worktree_root = repo / ".worktrees"
            first = run_prepare(repo, worktree_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_payload = json.loads(first.stdout)
            initial_state = json.loads(
                Path(first_payload["runtime_state_path"]).read_text(encoding="utf-8")
            )

            (repo / "README.md").write_text("advanced default branch\n", encoding="utf-8")
            git(repo, "add", "README.md")
            git(repo, "commit", "-qm", "advance main")

            second = run_prepare(repo, worktree_root)

            self.assertEqual(second.returncode, 0, second.stderr)
            second_payload = json.loads(second.stdout)
            persisted_state = json.loads(
                Path(second_payload["runtime_state_path"]).read_text(encoding="utf-8")
            )
            self.assertTrue(second_payload["reused"])
            self.assertNotEqual(default_snapshot(repo)[0], initial_state["planning_base_sha"])
            self.assertEqual(second_payload["planning_base_sha"], initial_state["planning_base_sha"])
            self.assertEqual(persisted_state, initial_state)

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


if __name__ == "__main__":
    unittest.main()
