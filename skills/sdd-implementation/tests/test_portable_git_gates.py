from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SUPERPOWERS_PREFIX = ".superpowers"


class GateFailure(RuntimeError):
    def __init__(self, category: str, detail: str) -> None:
        super().__init__(f"{category}: {detail}")
        self.category = category


@dataclass(frozen=True)
class GateEvidence:
    gate: str
    target: str
    binding: tuple[str, ...]


def git_result(repository: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )


def git(repository: Path, *args: str, input_text: str | None = None) -> str:
    result = git_result(repository, *args, input_text=input_text)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def fail(gate: str, detail: str) -> None:
    raise GateFailure(f"gate_{gate.replace('-', '_')}", detail)


def bind_target(target: Path, installed_skill_dir: Path = SKILL_DIR) -> Path:
    if not (installed_skill_dir / "SKILL.md").is_file():
        raise GateFailure("skill_package", "installed SKILL.md is unavailable")
    supplied = Path(target)
    try:
        resolved = supplied.resolve(strict=True)
    except OSError as error:
        raise GateFailure("target_runtime", str(error)) from error
    if not supplied.is_absolute() or supplied != resolved:
        raise GateFailure("target_runtime", "target is not canonical and absolute")
    top = git_result(resolved, "rev-parse", "--show-toplevel")
    inside = git_result(resolved, "rev-parse", "--is-inside-work-tree")
    if top.returncode != 0 or inside.returncode != 0:
        raise GateFailure("target_runtime", "Git target probes failed")
    if inside.stdout.strip() != "true" or top.stdout.rstrip("\n") != str(resolved):
        raise GateFailure("target_runtime", "Git top-level does not equal target")
    return resolved


def current_head(repository: Path, gate: str) -> str:
    result = git_result(repository, "rev-parse", "--verify", "HEAD^{commit}")
    if result.returncode != 0:
        fail(gate, "HEAD commit is unavailable")
    return result.stdout.strip()


def full_state(repository: Path) -> tuple[str, str]:
    return (
        git(repository, "ls-files", "--stage", "-z"),
        git(
            repository,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignored=matching",
        ),
    )


def superpowers_entries(repository: Path, treeish: str, gate: str) -> tuple[str, ...]:
    result = git_result(
        repository,
        "ls-tree",
        "-r",
        "--name-only",
        treeish,
        "--",
        SUPERPOWERS_PREFIX,
    )
    if result.returncode != 0:
        fail(gate, f"cannot inspect tree {treeish}")
    return tuple(path for path in result.stdout.splitlines() if path)


def exceptional_scratch_gate(
    target: Path,
    relative_path: str,
    reason: str,
    starting_head_sha: str,
    installed_skill_dir: Path = SKILL_DIR,
) -> GateEvidence:
    gate = "exceptional-local-scratch-pre-write"
    repository = bind_target(target, installed_skill_dir)
    relative = PurePosixPath(relative_path)
    if (
        not reason.strip()
        or not relative_path
        or relative.is_absolute()
        or relative_path != relative.as_posix()
        or ".." in relative.parts
    ):
        fail(gate, "reason and normalized target-relative path are required")
    leaf = repository.joinpath(*relative.parts)
    try:
        resolved_leaf = leaf.resolve(strict=False)
        resolved_leaf.relative_to(repository)
    except (OSError, ValueError) as error:
        fail(gate, f"scratch ownership is outside target: {error}")
    if leaf.is_symlink():
        fail(gate, "scratch leaf is a symlink")
    if current_head(repository, gate) != starting_head_sha:
        fail(gate, "HEAD no longer matches starting_head_sha")
    if git_result(repository, "cat-file", "-e", f"{starting_head_sha}^{{commit}}").returncode:
        fail(gate, "starting_head_sha is not a commit")
    ignored = git_result(
        repository, "check-ignore", "--no-index", "-v", "--", relative_path
    )
    if ignored.returncode != 0:
        fail(gate, "scratch path is not ignored")
    if git(repository, "ls-files", "--stage", "--", relative_path):
        fail(gate, "scratch path is present in the index")
    if superpowers_entries(repository, "HEAD", gate) and git(
        repository, "ls-tree", "-r", "--name-only", "HEAD", "--", relative_path
    ):
        fail(gate, "scratch path is present in HEAD")
    index_state, working_state = full_state(repository)
    return GateEvidence(
        gate,
        str(repository),
        (
            relative_path,
            str(resolved_leaf),
            reason,
            starting_head_sha,
            ignored.stdout,
            index_state,
            working_state,
        ),
    )


def pre_commit_gate(
    target: Path, installed_skill_dir: Path = SKILL_DIR
) -> GateEvidence:
    gate = "pre-commit-candidate"
    repository = bind_target(target, installed_skill_dir)
    candidate_result = git_result(repository, "write-tree")
    if candidate_result.returncode != 0:
        fail(gate, "index cannot produce a candidate tree")
    candidate = candidate_result.stdout.strip()
    if superpowers_entries(repository, candidate, gate):
        fail(gate, "candidate tree contains .superpowers")
    if git(repository, "ls-files", "--stage", "--", SUPERPOWERS_PREFIX):
        fail(gate, "index contains .superpowers")
    unignored = git(
        repository,
        "ls-files",
        "--others",
        "--exclude-standard",
        "--",
        SUPERPOWERS_PREFIX,
    )
    if unignored:
        fail(gate, "working tree contains unignored .superpowers paths")
    index_state, working_state = full_state(repository)
    return GateEvidence(
        gate,
        str(repository),
        (candidate, index_state, working_state, unignored),
    )


def final_closeout_gate(
    target: Path,
    starting_head_sha: str,
    installed_skill_dir: Path = SKILL_DIR,
) -> GateEvidence:
    gate = "final-closeout"
    repository = bind_target(target, installed_skill_dir)
    try:
        candidate = pre_commit_gate(repository, installed_skill_dir)
    except GateFailure as error:
        if error.category == "gate_pre_commit_candidate":
            fail(gate, str(error))
        raise
    head = current_head(repository, gate)
    if git_result(repository, "cat-file", "-e", f"{starting_head_sha}^{{commit}}").returncode:
        fail(gate, "starting_head_sha is not a commit")
    if git_result(
        repository, "merge-base", "--is-ancestor", starting_head_sha, head
    ).returncode:
        fail(gate, "starting_head_sha is not an ancestor of HEAD")
    head_tree = git(repository, "rev-parse", "HEAD^{tree}").strip()
    if git_result(repository, "cat-file", "-e", f"{head_tree}^{{tree}}").returncode:
        fail(gate, "HEAD tree object is unavailable")
    if superpowers_entries(repository, head_tree, gate):
        fail(gate, "HEAD tree contains .superpowers")
    commits = tuple(
        commit
        for commit in git(
            repository, "rev-list", "--reverse", f"{starting_head_sha}..{head}"
        ).splitlines()
        if commit
    )
    trees: list[str] = []
    for commit in commits:
        if git_result(repository, "cat-file", "-e", f"{commit}^{{commit}}").returncode:
            fail(gate, f"commit object is unavailable: {commit}")
        tree = git(repository, "rev-parse", f"{commit}^{{tree}}").strip()
        if git_result(repository, "cat-file", "-e", f"{tree}^{{tree}}").returncode:
            fail(gate, f"tree object is unavailable: {tree}")
        if superpowers_entries(repository, tree, gate):
            fail(gate, f"commit tree contains .superpowers: {commit}")
        trees.append(tree)
    return GateEvidence(
        gate,
        str(repository),
        candidate.binding + (starting_head_sha, head, head_tree, *commits, *trees),
    )


def evidence_is_fresh(evidence: GateEvidence, probe) -> bool:
    try:
        return probe() == evidence
    except GateFailure:
        return False


class GitFixture:
    def __init__(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = (Path(self.temporary_directory.name) / "repository").resolve()
        self.root.mkdir()
        git(self.root, "init", "-b", "main")
        git(self.root, "config", "user.name", "Test User")
        git(self.root, "config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        (self.root / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(self.root, "add", ".gitignore", "tracked.txt")
        git(self.root, "commit", "-m", "base")
        self.starting_head = git(self.root, "rev-parse", "HEAD").strip()

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, relative_path: str, content: str = "content\n") -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def commit_regular_change(self, message: str = "regular change") -> str:
        path = self.root / "tracked.txt"
        path.write_text(path.read_text(encoding="utf-8") + message + "\n", encoding="utf-8")
        git(self.root, "add", "tracked.txt")
        git(self.root, "commit", "-m", message)
        return git(self.root, "rev-parse", "HEAD").strip()

    def commit_contamination(self) -> str:
        self.write(".superpowers/committed.md")
        git(self.root, "add", "-f", ".superpowers/committed.md")
        git(self.root, "commit", "-m", "contaminated commit")
        return git(self.root, "rev-parse", "HEAD").strip()

    def commit_cleanup(self) -> str:
        git(self.root, "rm", "--cached", ".superpowers/committed.md")
        git(self.root, "commit", "-m", "clean contamination")
        return git(self.root, "rev-parse", "HEAD").strip()

    def install_unmerged_index(self) -> None:
        base = git(self.root, "hash-object", "-w", "tracked.txt").strip()
        ours = git_result(
            self.root, "hash-object", "-w", "--stdin", input_text="ours\n"
        ).stdout.strip()
        theirs = git_result(
            self.root, "hash-object", "-w", "--stdin", input_text="theirs\n"
        ).stdout.strip()
        index_info = (
            f"100644 {base} 1\tconflict.txt\n"
            f"100644 {ours} 2\tconflict.txt\n"
            f"100644 {theirs} 3\tconflict.txt\n"
        )
        git(self.root, "update-index", "--index-info", input_text=index_info)


class PortableGitGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = GitFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def assert_gate_failure(self, category: str, probe) -> None:
        with self.assertRaises(GateFailure) as raised:
            probe()
        self.assertEqual(category, raised.exception.category)

    def test_target_binding_rejects_alias_and_missing_skill_package(self) -> None:
        alias = self.fixture.root.parent / "repository-alias"
        alias.symlink_to(self.fixture.root, target_is_directory=True)
        self.assert_gate_failure("target_runtime", lambda: pre_commit_gate(alias))
        missing = self.fixture.root.parent / "missing-skill"
        self.assert_gate_failure(
            "skill_package",
            lambda: pre_commit_gate(self.fixture.root, installed_skill_dir=missing),
        )

    def test_exceptional_scratch_requires_ignored_untracked_uncommitted_owned_leaf(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        evidence = exceptional_scratch_gate(
            self.fixture.root, scratch, "runtime cannot use external temp", self.fixture.starting_head
        )
        self.assertEqual("exceptional-local-scratch-pre-write", evidence.gate)

        self.fixture.write(scratch)
        git(self.fixture.root, "add", "-f", scratch)
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                scratch,
                "runtime cannot use external temp",
                self.fixture.starting_head,
            ),
        )

    def test_exceptional_scratch_rejects_escape_and_stale_head_index_or_ignore_evidence(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        probe = lambda: exceptional_scratch_gate(
            self.fixture.root, scratch, "runtime cannot use external temp", self.fixture.starting_head
        )
        evidence = probe()
        self.fixture.write("staged.txt")
        git(self.fixture.root, "add", "staged.txt")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        git(self.fixture.root, "reset", "HEAD", "staged.txt")
        (self.fixture.root / ".gitignore").write_text("# no scratch ignore\n", encoding="utf-8")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        (self.fixture.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        self.fixture.commit_regular_change()
        self.assertFalse(evidence_is_fresh(evidence, probe))

        outside = self.fixture.root.parent / "outside"
        outside.mkdir()
        (self.fixture.root / "escape").symlink_to(outside, target_is_directory=True)
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                "escape/report.md",
                "runtime cannot use external temp",
                git(self.fixture.root, "rev-parse", "HEAD").strip(),
            ),
        )

    def test_pre_commit_distinguishes_force_add_unmerged_deletion_and_add_then_delete(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        self.fixture.write(scratch)
        git(self.fixture.root, "add", "-f", scratch)
        self.assert_gate_failure("gate_pre_commit_candidate", lambda: pre_commit_gate(self.fixture.root))

        git(self.fixture.root, "reset", "HEAD", scratch)
        (self.fixture.root / scratch).unlink()
        self.fixture.install_unmerged_index()
        self.assert_gate_failure("gate_pre_commit_candidate", lambda: pre_commit_gate(self.fixture.root))

        git(self.fixture.root, "reset", "--hard", "HEAD")
        self.fixture.commit_contamination()
        git(self.fixture.root, "rm", "--cached", ".superpowers/committed.md")
        self.assertEqual("pre-commit-candidate", pre_commit_gate(self.fixture.root).gate)

        git(self.fixture.root, "reset", "--hard", self.fixture.starting_head)
        self.fixture.write(scratch)
        git(self.fixture.root, "add", "-f", scratch)
        (self.fixture.root / scratch).unlink()
        git(self.fixture.root, "add", "-u", "--", scratch)
        self.assertEqual("pre-commit-candidate", pre_commit_gate(self.fixture.root).gate)

    def test_pre_commit_evidence_is_invalidated_by_index_worktree_or_ignore_mutation(self) -> None:
        probe = lambda: pre_commit_gate(self.fixture.root)
        evidence = probe()
        self.fixture.write("staged.txt")
        git(self.fixture.root, "add", "staged.txt")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        git(self.fixture.root, "reset", "--hard", "HEAD")
        evidence = probe()
        self.fixture.write("untracked.txt")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        (self.fixture.root / "untracked.txt").unlink()
        evidence = probe()
        (self.fixture.root / ".gitignore").write_text("# no ignore\n", encoding="utf-8")
        self.assertFalse(evidence_is_fresh(evidence, probe))

    def test_final_closeout_checks_candidate_head_and_every_new_commit_tree(self) -> None:
        self.fixture.commit_regular_change()
        evidence = final_closeout_gate(self.fixture.root, self.fixture.starting_head)
        self.assertEqual("final-closeout", evidence.gate)

        self.fixture.commit_contamination()
        self.fixture.commit_cleanup()
        self.assert_gate_failure(
            "gate_final_closeout",
            lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head),
        )

    def test_final_closeout_rejects_staged_deletion_and_stale_bindings(self) -> None:
        self.fixture.commit_regular_change()
        probe = lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head)
        evidence = probe()
        self.fixture.write("staged.txt")
        git(self.fixture.root, "add", "staged.txt")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        git(self.fixture.root, "reset", "--hard", "HEAD")
        evidence = probe()
        self.fixture.write("untracked.txt")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        (self.fixture.root / "untracked.txt").unlink()
        evidence = probe()
        (self.fixture.root / ".gitignore").write_text("# no ignore\n", encoding="utf-8")
        self.assertFalse(evidence_is_fresh(evidence, probe))

        git(self.fixture.root, "reset", "--hard", "HEAD")
        self.fixture.commit_contamination()
        git(self.fixture.root, "rm", "--cached", ".superpowers/committed.md")
        self.assert_gate_failure(
            "gate_final_closeout",
            lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head),
        )

        git(self.fixture.root, "reset", "--hard", "HEAD^")
        wrong_baseline = git(self.fixture.root, "rev-parse", "HEAD").strip()
        self.assertFalse(
            evidence_is_fresh(
                evidence,
                lambda: final_closeout_gate(self.fixture.root, wrong_baseline),
            )
        )

    def test_final_closeout_classifies_candidate_contamination_as_final_failure(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        self.fixture.write(scratch)
        git(self.fixture.root, "add", "-f", scratch)
        self.assert_gate_failure(
            "gate_final_closeout",
            lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head),
        )


if __name__ == "__main__":
    unittest.main()
