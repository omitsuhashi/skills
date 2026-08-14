from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SUPERPOWERS_PREFIX = ".superpowers"
MANDATORY_PACKAGE_RESOURCES = (
    "prompts/plan-reviewer.md",
    "prompts/repository-researcher.md",
    "prompts/spec-reviewer.md",
    "prompts/spec-synthesizer.md",
    "references/plan-contract.md",
    "references/planning-context.md",
    "references/research-stage.md",
)


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
    try:
        return subprocess.run(
            ["git", "-C", str(repository), *args],
            check=False,
            capture_output=True,
            text=True,
            input=input_text,
        )
    except OSError as error:
        raise GateFailure("target_runtime", f"Git capability unavailable: {error}") from error


def git(repository: Path, *args: str, input_text: str | None = None) -> str:
    result = git_result(repository, *args, input_text=input_text)
    if result.returncode != 0:
        raise GateFailure("target_runtime", result.stderr or result.stdout)
    return result.stdout


def fail(gate: str, detail: str) -> None:
    raise GateFailure(f"gate_{gate.replace('-', '_')}", detail)


def bind_target(target: Path, installed_skill_dir: Path = SKILL_DIR) -> Path:
    try:
        package = Path(installed_skill_dir).resolve(strict=True)
    except OSError as error:
        raise GateFailure(
            "broken skill installation",
            f"installed skill folder is unreadable: {error}",
        ) from error
    for relative_path in MANDATORY_PACKAGE_RESOURCES:
        resource = package / relative_path
        try:
            resolved_resource = resource.resolve(strict=True)
            resolved_resource.relative_to(package)
            content = resource.read_bytes()
        except ValueError as error:
            raise GateFailure(
                "broken skill installation",
                f"installed resource escapes package: {relative_path}",
            ) from error
        except OSError as error:
            raise GateFailure(
                "broken skill installation",
                f"mandatory installed resource is unreadable: {relative_path}: {error}",
            ) from error
        if not content:
            raise GateFailure(
                "broken skill installation",
                f"mandatory installed resource is empty: {relative_path}",
            )
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


def repository_identity(repository: Path) -> tuple[str, str, str]:
    common_dir_value = git(repository, "rev-parse", "--git-common-dir").strip()
    common_dir = Path(common_dir_value)
    if not common_dir.is_absolute():
        common_dir = repository / common_dir
    try:
        common_dir = common_dir.resolve(strict=True)
        stat = common_dir.stat()
    except OSError as error:
        raise GateFailure("target_runtime", f"Git common directory is unreadable: {error}") from error
    return (str(common_dir), str(stat.st_dev), str(stat.st_ino))


def require_object(repository: Path, object_spec: str) -> None:
    result = git_result(repository, "cat-file", "-e", object_spec)
    if result.returncode != 0:
        raise GateFailure(
            "target_runtime",
            f"Git object is unavailable or unreadable: {object_spec}",
        )


def current_head(repository: Path, gate: str) -> str:
    result = git_result(repository, "rev-parse", "--verify", "HEAD^{commit}")
    if result.returncode != 0:
        raise GateFailure("target_runtime", "HEAD commit is unavailable")
    return result.stdout.strip()


def content_identity(repository: Path, path: Path) -> str:
    if path.is_symlink():
        try:
            return f"symlink:{os.readlink(path)}"
        except OSError as error:
            raise GateFailure("target_runtime", f"cannot read symlink {path}: {error}") from error
    if not path.exists():
        return "missing"
    if not path.is_file():
        return "non-file"
    result = git_result(repository, "hash-object", "--no-filters", str(path))
    if result.returncode != 0:
        raise GateFailure("target_runtime", f"cannot hash working path: {path}")
    return result.stdout.strip()


def working_tree_content_state(repository: Path) -> tuple[str, ...]:
    paths: set[str] = set()
    for args in (
        ("ls-files", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
        ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
    ):
        paths.update(path for path in git(repository, *args).split("\0") if path)
    return tuple(
        f"{path}\0{content_identity(repository, repository / path)}"
        for path in sorted(paths)
    )


def ignore_content_state(repository: Path) -> tuple[str, ...]:
    records: list[str] = []
    info_exclude_value = git(repository, "rev-parse", "--git-path", "info/exclude").strip()
    info_exclude = Path(info_exclude_value)
    if not info_exclude.is_absolute():
        info_exclude = repository / info_exclude
    records.append(f"info/exclude\0{content_identity(repository, info_exclude)}")

    excludes = git_result(repository, "config", "--path", "--get-all", "core.excludesFile")
    if excludes.returncode not in (0, 1):
        raise GateFailure("target_runtime", excludes.stderr or excludes.stdout)
    for value in sorted(path for path in excludes.stdout.splitlines() if path):
        exclude_path = Path(value).expanduser()
        if not exclude_path.is_absolute():
            exclude_path = repository / exclude_path
        records.append(f"core.excludesFile:{value}\0{content_identity(repository, exclude_path)}")
    return tuple(records)


def full_state(repository: Path) -> tuple[str, ...]:
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
        *working_tree_content_state(repository),
        *ignore_content_state(repository),
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
        raise GateFailure("target_runtime", f"cannot inspect tree {treeish}")
    return tuple(path for path in result.stdout.splitlines() if path)


def exceptional_scratch_gate(
    target: Path,
    relative_path: str,
    reason: str,
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
        or len(relative.parts) < 2
        or relative.parts[0] != SUPERPOWERS_PREFIX
    ):
        fail(
            gate,
            "reason and normalized target-relative .superpowers leaf are required",
        )
    leaf = repository.joinpath(*relative.parts)
    try:
        resolved_leaf = leaf.resolve(strict=False)
        resolved_leaf.relative_to(repository)
    except (OSError, ValueError) as error:
        fail(gate, f"scratch ownership is outside target: {error}")
    if leaf.is_symlink() or leaf.exists():
        fail(gate, "scratch leaf already exists or ownership is foreign or unknown")
    head = current_head(repository, gate)
    ignored = git_result(
        repository, "check-ignore", "--no-index", "-v", "--", relative_path
    )
    if ignored.returncode == 1:
        fail(gate, "scratch path is not ignored")
    if ignored.returncode != 0:
        raise GateFailure("target_runtime", ignored.stderr or ignored.stdout)
    if git(repository, "ls-files", "--stage", "--", relative_path):
        fail(gate, "scratch path is present in the index")
    if git(repository, "ls-tree", "-r", "--name-only", head, "--", relative_path):
        fail(gate, "scratch path is present in HEAD")
    state = full_state(repository)
    return GateEvidence(
        gate,
        str(repository),
        (
            *repository_identity(repository),
            relative_path,
            str(resolved_leaf),
            reason,
            head,
            ignored.stdout,
            *state,
        ),
    )


def pre_commit_gate(
    target: Path, installed_skill_dir: Path = SKILL_DIR
) -> GateEvidence:
    gate = "pre-commit-candidate"
    repository = bind_target(target, installed_skill_dir)
    candidate_result = git_result(repository, "write-tree")
    if candidate_result.returncode != 0:
        if git(repository, "ls-files", "--unmerged"):
            fail(gate, "index cannot produce a candidate tree")
        raise GateFailure(
            "target_runtime", candidate_result.stderr or candidate_result.stdout
        )
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
    state = full_state(repository)
    return GateEvidence(
        gate,
        str(repository),
        (*repository_identity(repository), candidate, *state, unignored),
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
    require_object(repository, f"{starting_head_sha}^{{commit}}")
    ancestry = git_result(
        repository, "merge-base", "--is-ancestor", starting_head_sha, head
    )
    if ancestry.returncode == 1:
        fail(gate, "starting_head_sha is not an ancestor of HEAD")
    if ancestry.returncode != 0:
        raise GateFailure("target_runtime", ancestry.stderr or ancestry.stdout)
    head_tree = git(repository, "rev-parse", "HEAD^{tree}").strip()
    require_object(repository, f"{head_tree}^{{tree}}")
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
        require_object(repository, f"{commit}^{{commit}}")
        tree = git(repository, "rev-parse", f"{commit}^{{tree}}").strip()
        require_object(repository, f"{tree}^{{tree}}")
        if superpowers_entries(repository, tree, gate):
            fail(gate, f"commit tree contains .superpowers: {commit}")
        trees.append(tree)
    return GateEvidence(
        gate,
        str(repository),
        candidate.binding + (starting_head_sha, head, head_tree, *commits, *trees),
    )


def recompute_gate(probe) -> GateEvidence:
    return probe()


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

    def test_target_binding_rejects_alias_and_missing_installation(self) -> None:
        alias = self.fixture.root.parent / "repository-alias"
        alias.symlink_to(self.fixture.root, target_is_directory=True)
        self.assert_gate_failure("target_runtime", lambda: pre_commit_gate(alias))
        missing = self.fixture.root.parent / "missing-skill"
        self.assert_gate_failure(
            "broken skill installation",
            lambda: pre_commit_gate(self.fixture.root, installed_skill_dir=missing),
        )

    def test_exceptional_scratch_requires_ignored_untracked_uncommitted_owned_leaf(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        evidence = exceptional_scratch_gate(
            self.fixture.root, scratch, "runtime cannot use external temp"
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
            ),
        )

    def test_exceptional_scratch_rejects_paths_outside_superpowers(self) -> None:
        (self.fixture.root / ".gitignore").write_text(
            ".superpowers/\n.local-scratch/\n", encoding="utf-8"
        )
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                ".local-scratch/task/report.md",
                "runtime cannot use external temp",
            ),
        )

    def test_exceptional_scratch_rejects_an_existing_ignored_leaf(self) -> None:
        scratch = ".superpowers/sdd/existing/report.md"
        self.fixture.write(scratch, "foreign content\n")
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                scratch,
                "runtime cannot use external temp",
            ),
        )

    def test_exceptional_scratch_accepts_a_distinct_leaf_after_an_ordinary_commit(self) -> None:
        first = ".superpowers/sdd/first/report.md"
        initial = exceptional_scratch_gate(
            self.fixture.root,
            first,
            "runtime cannot use external temp",
        )
        self.fixture.write(first, "task-owned scratch\n")
        self.fixture.commit_regular_change()
        evidence = exceptional_scratch_gate(
            self.fixture.root,
            ".superpowers/sdd/later/report.md",
            "runtime cannot use external temp",
        )
        self.assertEqual("exceptional-local-scratch-pre-write", evidence.gate)
        self.assertNotEqual(initial.binding, evidence.binding)

    def test_exceptional_scratch_rejects_escape_and_revalidates_current_state(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        probe = lambda: exceptional_scratch_gate(
            self.fixture.root, scratch, "runtime cannot use external temp"
        )
        evidence = probe()
        self.fixture.write("staged.txt")
        git(self.fixture.root, "add", "staged.txt")
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        git(self.fixture.root, "reset", "HEAD", "staged.txt")
        (self.fixture.root / ".gitignore").write_text("# no scratch ignore\n", encoding="utf-8")
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write", lambda: recompute_gate(probe)
        )

        (self.fixture.root / ".gitignore").write_text(".superpowers/\n", encoding="utf-8")
        self.fixture.commit_regular_change()
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        outside = self.fixture.root.parent / "outside"
        outside.mkdir()
        escape = self.fixture.root / ".superpowers" / "escape"
        escape.parent.mkdir()
        escape.symlink_to(outside, target_is_directory=True)
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                ".superpowers/escape/report.md",
                "runtime cannot use external temp",
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
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        git(self.fixture.root, "reset", "--hard", "HEAD")
        evidence = probe()
        self.fixture.write("untracked.txt")
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        (self.fixture.root / "untracked.txt").unlink()
        evidence = probe()
        (self.fixture.root / ".gitignore").write_text("# no ignore\n", encoding="utf-8")
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

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
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        git(self.fixture.root, "reset", "--hard", "HEAD")
        evidence = probe()
        self.fixture.write("untracked.txt")
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        (self.fixture.root / "untracked.txt").unlink()
        evidence = probe()
        (self.fixture.root / ".gitignore").write_text("# no ignore\n", encoding="utf-8")
        refreshed = recompute_gate(probe)
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        git(self.fixture.root, "reset", "--hard", "HEAD")
        self.fixture.commit_contamination()
        git(self.fixture.root, "rm", "--cached", ".superpowers/committed.md")
        self.assert_gate_failure(
            "gate_final_closeout",
            lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head),
        )

        git(self.fixture.root, "reset", "--hard", "HEAD^")
        wrong_baseline = git(self.fixture.root, "rev-parse", "HEAD").strip()
        refreshed = recompute_gate(
            lambda: final_closeout_gate(self.fixture.root, wrong_baseline)
        )
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

    def test_final_closeout_classifies_candidate_contamination_as_final_failure(self) -> None:
        scratch = ".superpowers/sdd/task/report.md"
        self.fixture.write(scratch)
        git(self.fixture.root, "add", "-f", scratch)
        self.assert_gate_failure(
            "gate_final_closeout",
            lambda: final_closeout_gate(self.fixture.root, self.fixture.starting_head),
        )

    def test_dirty_to_dirty_worktree_and_ignore_mutations_invalidate_evidence(self) -> None:
        probe = lambda: pre_commit_gate(self.fixture.root)
        self.fixture.write("untracked.txt", "first\n")
        worktree_evidence = probe()
        self.fixture.write("untracked.txt", "second\n")
        refreshed = recompute_gate(probe)
        self.assertIsNot(worktree_evidence, refreshed)
        self.assertNotEqual(worktree_evidence.binding, refreshed.binding)

        (self.fixture.root / "untracked.txt").unlink()
        (self.fixture.root / ".gitignore").write_text(
            ".superpowers/\n# first rule revision\n", encoding="utf-8"
        )
        ignore_evidence = probe()
        (self.fixture.root / ".gitignore").write_text(
            ".superpowers/\n# second rule revision\n", encoding="utf-8"
        )
        refreshed = recompute_gate(probe)
        self.assertIsNot(ignore_evidence, refreshed)
        self.assertNotEqual(ignore_evidence.binding, refreshed.binding)

    def test_same_path_repository_replacement_invalidates_target_evidence(self) -> None:
        evidence = pre_commit_gate(self.fixture.root)
        original = self.fixture.root.parent / "original-repository"
        self.fixture.root.rename(original)
        git(
            self.fixture.root.parent,
            "clone",
            "--quiet",
            "--no-hardlinks",
            str(original),
            str(self.fixture.root),
        )
        refreshed = recompute_gate(lambda: pre_commit_gate(self.fixture.root))
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

    def test_scratch_path_and_symlink_ownership_mutations_invalidate_evidence(self) -> None:
        first = ".superpowers/first/report.md"
        second = ".superpowers/second/report.md"
        evidence = exceptional_scratch_gate(
            self.fixture.root,
            first,
            "runtime cannot use external temp",
        )
        refreshed = recompute_gate(
            lambda: exceptional_scratch_gate(
                self.fixture.root,
                second,
                "runtime cannot use external temp",
            )
        )
        self.assertIsNot(evidence, refreshed)
        self.assertNotEqual(evidence.binding, refreshed.binding)

        owned_path = ".superpowers/owned/report.md"
        owned_probe = lambda: exceptional_scratch_gate(
            self.fixture.root,
            owned_path,
            "runtime cannot use external temp",
        )
        owned_evidence = owned_probe()
        self.assertEqual("exceptional-local-scratch-pre-write", owned_evidence.gate)
        link = self.fixture.root / ".superpowers" / "owned"
        link.parent.mkdir()
        outside = self.fixture.root.parent / "owned-outside"
        outside.mkdir()
        link.symlink_to(outside, target_is_directory=True)
        self.assert_gate_failure(
            "gate_exceptional_local_scratch_pre_write",
            lambda: recompute_gate(owned_probe),
        )

    def test_failure_taxonomy_rejects_unreadable_package_content(self) -> None:
        package = self.fixture.root.parent / "installed-skill"
        package.mkdir()
        skill = package / "SKILL.md"
        skill.write_text("package content\n", encoding="utf-8")
        skill.chmod(0)
        try:
            self.assert_gate_failure(
                "broken skill installation",
                lambda: pre_commit_gate(
                    self.fixture.root, installed_skill_dir=package
                ),
            )
        finally:
            skill.chmod(0o600)

    def test_failure_taxonomy_rejects_unavailable_git_capability(self) -> None:
        original_path = os.environ.get("PATH")
        os.environ["PATH"] = ""
        try:
            self.assert_gate_failure(
                "target_runtime", lambda: pre_commit_gate(self.fixture.root)
            )
        finally:
            if original_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = original_path

    def test_failure_taxonomy_classifies_missing_objects_as_target_runtime(self) -> None:
        missing_commit = "0" * 40
        self.assert_gate_failure(
            "target_runtime",
            lambda: final_closeout_gate(self.fixture.root, missing_commit),
        )


if __name__ == "__main__":
    unittest.main()
