#!/usr/bin/env python3
"""Fail closed when SDD transient artifacts enter a nominated Git surface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TRANSIENT_PATHSPEC = ".superpowers"
MIGRATION_MARKER_PATH = "scripts/sdd-transient-artifact-migration.json"
STRICT_POLICY_PATH = "scripts/validate_sdd_transient_artifacts.py"
AUTHORIZED_MIGRATION_BASELINE = "f07aebce7bbf854cd64184311d204cf04055fd28"
AUTHORIZED_MARKER_PARENT = "c7aced8d7b3975f081ec8bfcd065dcaa57bb2eec"
AUTHORIZED_MARKER_INTRODUCTION = "91cbd5aec3d062f534937953ee8241f415d8db33"
AUTHORIZED_MARKER_BLOB = "ef384328ad21f49f4c2e4834cef3d401c350d9a8"
AUTHORIZED_STRICT_POLICY_BLOB = "7ee1a07f030aaa77edcb0051a2d656ec07162ab3"
AUTHORIZED_SQUASH_POLICY_ROOT = "82dcd32157ff9690ae038f982f3916009e449f80"
AUTHORIZED_PRE_POLICY_TIP = "f54c6f082ce8a1eb4dd2f8d46d2171443d143817"
ORIGIN_MAIN_REF = "refs/remotes/origin/main"
AUTHORIZED_MIGRATION_ENTRIES = (
    "100644 blob b50ed8e434725cb70bc0f1d2c6daa1a053e0ccc1\t"
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
    "approved-residual-fix-report.md",
    "100644 blob c884197bf566cc93f319f3c2a1b6d2ad1563d10e\t"
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
    "final-fix-report.md",
    "100644 blob da22b7580961fb9a2087ab1eb034fb34000711f8\t"
    ".superpowers/sdd/sdd-plan-ownership-alignment-implementation-plan/"
    "task-2-report.md",
)
EXPECTED_MIGRATION_MANIFEST = {
    "schema_version": 1,
    "migration_baseline": AUTHORIZED_MIGRATION_BASELINE,
    "allowed_entries": [
        {
            "mode": entry.split(" ", 1)[0],
            "blob": entry.split(" blob ", 1)[1].split("\t", 1)[0],
            "path": entry.split("\t", 1)[1],
        }
        for entry in AUTHORIZED_MIGRATION_ENTRIES
    ],
}
AUTHORIZED_MARKER_ENTRY = (
    f"100644 blob {AUTHORIZED_MARKER_BLOB}\t{MIGRATION_MARKER_PATH}"
)
AUTHORIZED_STRICT_POLICY_ENTRY = (
    f"100755 blob {AUTHORIZED_STRICT_POLICY_BLOB}\t{STRICT_POLICY_PATH}"
)


class ValidationFailure(Exception):
    """A single fail-closed validation result."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category
        self.message = message


def run_git(repository: Path, *args: str, input_text: Optional[str] = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
        input=input_text,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise ValidationFailure("repository_error", detail)
    return result.stdout


def repository_root(candidate: Path) -> Path:
    resolved = candidate.resolve()
    top_level = Path(run_git(resolved, "rev-parse", "--show-toplevel").strip()).resolve()
    if top_level != resolved:
        raise ValidationFailure(
            "repository_error", "--repository must name the Git worktree root"
        )
    return resolved


def tree_entries(
    repository: Path, object_name: str, pathspec: str = TRANSIENT_PATHSPEC
) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository,
            "ls-tree",
            "-r",
            object_name,
            "--",
            pathspec,
        ).splitlines()
        if line
    )


def index_entries(
    repository: Path, pathspec: str = TRANSIENT_PATHSPEC
) -> Tuple[str, ...]:
    entries: List[str] = []
    for line in run_git(
        repository, "ls-files", "--stage", "--", pathspec
    ).splitlines():
        if not line:
            continue
        metadata, separator, path = line.partition("\t")
        parts = metadata.split()
        if not separator or len(parts) != 3:
            raise ValidationFailure("repository_error", "malformed Git index entry")
        mode, blob, stage = parts
        if stage != "0":
            raise ValidationFailure("index_entry", f"unmerged index entry: {path}")
        entries.append(f"{mode} blob {blob}\t{path}")
    return tuple(entries)


def marker_manifest(repository: Path, entry: str) -> Dict[str, object]:
    if entry != AUTHORIZED_MARKER_ENTRY:
        raise ValidationFailure(
            "migration_marker_mismatch", "migration marker blob is not exact"
        )
    mode, separator, blob_and_path = entry.partition(" ")
    if mode != "100644" or not separator or "\t" not in blob_and_path:
        raise ValidationFailure("migration_marker_mismatch", "malformed marker entry")
    kind_and_blob, _, path = blob_and_path.partition("\t")
    kind, _, blob = kind_and_blob.partition(" ")
    if kind != "blob" or path != MIGRATION_MARKER_PATH:
        raise ValidationFailure("migration_marker_mismatch", "invalid marker entry")
    try:
        manifest = json.loads(run_git(repository, "cat-file", "blob", blob))
    except json.JSONDecodeError as exc:
        raise ValidationFailure(
            "migration_marker_mismatch", "migration marker is not valid JSON"
        ) from exc
    if not isinstance(manifest, dict) or manifest != EXPECTED_MIGRATION_MANIFEST:
        raise ValidationFailure(
            "migration_marker_mismatch", "migration marker content does not match"
        )
    return manifest


def require_ancestor(repository: Path, ancestor: str, descendant: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        raise ValidationFailure(
            "migration_marker_lineage", "marker authority is outside planned lineage"
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or "cannot verify marker ancestry"
        raise ValidationFailure("repository_error", detail)


def marker_history_events(
    repository: Path, diff_filter: str
) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository,
            "log",
            "--full-history",
            "--ancestry-path",
            f"--diff-filter={diff_filter}",
            "--format=%H",
            f"{AUTHORIZED_MARKER_PARENT}..HEAD",
            "--",
            MIGRATION_MARKER_PATH,
        ).splitlines()
        if line
    )


def commit_parents(repository: Path, commit: str) -> Tuple[str, ...]:
    fields = run_git(repository, "rev-list", "--parents", "-n", "1", commit).split()
    if not fields or fields[0] != commit:
        raise ValidationFailure(
            "history_unavailable", f"cannot resolve cleanup boundary commit: {commit}"
        )
    return tuple(fields[1:])


def cleanup_deletion_events(repository: Path) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository,
            "log",
            "--full-history",
            "--diff-filter=D",
            "--format=%H",
            "HEAD",
            "--",
            MIGRATION_MARKER_PATH,
        ).splitlines()
        if line
    )


def semantic_cleanup_boundary(repository: Path, commit: str) -> bool:
    parents = commit_parents(repository, commit)
    if len(parents) != 1:
        return False
    parent = parents[0]
    return (
        tree_entries(repository, parent) == AUTHORIZED_MIGRATION_ENTRIES
        and tree_entries(repository, parent, MIGRATION_MARKER_PATH)
        == (AUTHORIZED_MARKER_ENTRY,)
        and not tree_entries(repository, commit)
        and not tree_entries(repository, commit, MIGRATION_MARKER_PATH)
    )


def squash_policy_events(repository: Path) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository,
            "log",
            "--first-parent",
            "--no-patch",
            "--diff-merges=first-parent",
            "--diff-filter=A",
            "--format=%H",
            "HEAD",
            "--",
            STRICT_POLICY_PATH,
        ).splitlines()
        if line
    )


def is_ancestor(repository: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    detail = result.stderr.strip() or "cannot verify cleanup-boundary ancestry"
    raise ValidationFailure("history_unavailable", detail)


def required_ref_tip(repository: Path, ref: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValidationFailure(
            "history_unavailable", f"required cleanup authority ref is unavailable: {ref}"
        )
    return result.stdout.strip()


def commit_exists(repository: Path, commit: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def revision_range(repository: Path, start: str, end: str) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository, "rev-list", "--reverse", f"{start}..{end}"
        ).splitlines()
        if line
    )


def policy_history_root(repository: Path, commit: str) -> Optional[str]:
    parents = commit_parents(repository, commit)
    if (
        not parents
        or tree_entries(repository, parents[0], STRICT_POLICY_PATH)
        or tree_entries(repository, commit)
        or tree_entries(repository, commit, MIGRATION_MARKER_PATH)
    ):
        return None
    if commit == AUTHORIZED_SQUASH_POLICY_ROOT:
        return (
            commit
            if len(parents) == 1
            and tree_entries(repository, commit, STRICT_POLICY_PATH)
            == (AUTHORIZED_STRICT_POLICY_ENTRY,)
            else None
        )
    if len(parents) != 2:
        return None
    imported_parent = parents[1]
    if parents[0] != AUTHORIZED_PRE_POLICY_TIP:
        return None
    if imported_parent != required_ref_tip(repository, ORIGIN_MAIN_REF):
        raise ValidationFailure(
            "cleanup_boundary_invalid",
            f"integration parent does not match {ORIGIN_MAIN_REF}",
        )
    if not is_ancestor(repository, AUTHORIZED_SQUASH_POLICY_ROOT, imported_parent):
        return None
    if (
        tree_entries(
            repository, AUTHORIZED_SQUASH_POLICY_ROOT, STRICT_POLICY_PATH
        )
        != (AUTHORIZED_STRICT_POLICY_ENTRY,)
        or tree_entries(repository, AUTHORIZED_SQUASH_POLICY_ROOT)
        or tree_entries(
            repository, AUTHORIZED_SQUASH_POLICY_ROOT, MIGRATION_MARKER_PATH
        )
    ):
        return None
    imported_policy = tree_entries(repository, imported_parent, STRICT_POLICY_PATH)
    if (
        len(imported_policy) != 1
        or tree_entries(repository, commit, STRICT_POLICY_PATH) != imported_policy
        or tree_entries(repository, imported_parent)
        or tree_entries(repository, imported_parent, MIGRATION_MARKER_PATH)
    ):
        return None
    return AUTHORIZED_SQUASH_POLICY_ROOT


def resolve_cleanup_boundary(repository: Path) -> Tuple[str, str]:
    if run_git(repository, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise ValidationFailure(
            "history_unavailable",
            "post-cleanup validation requires complete repository history",
        )

    deletion_events = cleanup_deletion_events(repository)
    if deletion_events:
        exact_deletions = tuple(
            commit
            for commit in deletion_events
            if semantic_cleanup_boundary(repository, commit)
        )
        if len(deletion_events) > 1 or len(exact_deletions) > 1:
            raise ValidationFailure(
                "cleanup_boundary_ambiguous",
                "multiple migration-marker deletion boundaries exist",
            )
        if len(exact_deletions) != 1:
            raise ValidationFailure(
                "cleanup_boundary_invalid",
                "migration-marker deletion is not the exact cleanup transition",
            )
        return exact_deletions[0], exact_deletions[0]

    policy_events = squash_policy_events(repository)
    exact_policy_events = tuple(
        (commit, history_root)
        for commit in policy_events
        if (history_root := policy_history_root(repository, commit)) is not None
    )
    if len(policy_events) > 1 or len(exact_policy_events) > 1:
        raise ValidationFailure(
            "cleanup_boundary_ambiguous",
            "multiple strict-policy introduction boundaries exist",
        )
    if len(exact_policy_events) != 1:
        raise ValidationFailure(
            "cleanup_boundary_unavailable",
            "no exact cleanup transition or authorized squash boundary exists",
        )
    return exact_policy_events[0]


def post_cleanup_commits(repository: Path) -> Tuple[str, ...]:
    boundary, history_root = resolve_cleanup_boundary(repository)
    parents = commit_parents(repository, history_root)
    if not parents:
        raise ValidationFailure(
            "history_unavailable", "cleanup boundary parent is unavailable"
        )
    commits = revision_range(repository, parents[0], "HEAD")
    if (
        history_root == AUTHORIZED_SQUASH_POLICY_ROOT
        and commit_exists(repository, AUTHORIZED_PRE_POLICY_TIP)
        and is_ancestor(repository, AUTHORIZED_PRE_POLICY_TIP, "HEAD")
    ):
        authorized_pre_policy_history = set(
            revision_range(repository, parents[0], AUTHORIZED_PRE_POLICY_TIP)
        )
        commits = tuple(
            commit for commit in commits if commit not in authorized_pre_policy_history
        )
    if boundary not in commits:
        raise ValidationFailure(
            "cleanup_boundary_invalid",
            "cleanup boundary is outside the post-cleanup ancestry path",
        )
    if history_root not in commits:
        raise ValidationFailure(
            "cleanup_boundary_invalid",
            "authorized cleanup history root is outside the ancestry path",
        )
    return commits


def require_marker_history_authority(repository: Path) -> None:
    if run_git(repository, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise ValidationFailure(
            "migration_marker_history_unavailable",
            "marker authority requires complete repository history",
        )
    require_ancestor(
        repository, AUTHORIZED_MIGRATION_BASELINE, AUTHORIZED_MARKER_PARENT
    )
    require_ancestor(
        repository, AUTHORIZED_MARKER_PARENT, AUTHORIZED_MARKER_INTRODUCTION
    )
    require_ancestor(repository, AUTHORIZED_MARKER_INTRODUCTION, "HEAD")
    if run_git(
        repository, "rev-parse", f"{AUTHORIZED_MARKER_INTRODUCTION}^"
    ).strip() != AUTHORIZED_MARKER_PARENT:
        raise ValidationFailure(
            "migration_marker_lineage", "marker introduction parent does not match"
        )
    if tree_entries(
        repository, AUTHORIZED_MARKER_PARENT, MIGRATION_MARKER_PATH
    ):
        raise ValidationFailure(
            "migration_marker_lineage", "planned marker parent already contains marker"
        )
    if tree_entries(
        repository, AUTHORIZED_MARKER_PARENT
    ) != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_marker_lineage", "planned marker parent baseline does not match"
        )
    if tree_entries(
        repository, AUTHORIZED_MARKER_INTRODUCTION, MIGRATION_MARKER_PATH
    ) != (AUTHORIZED_MARKER_ENTRY,):
        raise ValidationFailure(
            "migration_marker_lineage", "authorized introduction marker does not match"
        )
    if tree_entries(
        repository, AUTHORIZED_MARKER_INTRODUCTION
    ) != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_marker_lineage", "authorized introduction reports do not match"
        )
    current_marker = tree_entries(repository, "HEAD", MIGRATION_MARKER_PATH)
    if not current_marker:
        raise ValidationFailure(
            "migration_marker_reintroduced",
            "migration marker was already removed and cannot be reintroduced",
        )
    if current_marker != (AUTHORIZED_MARKER_ENTRY,):
        raise ValidationFailure(
            "migration_marker_lineage", "current HEAD marker is inexact"
        )
    if marker_history_events(repository, "A") != (
        AUTHORIZED_MARKER_INTRODUCTION,
    ):
        raise ValidationFailure(
            "migration_marker_lineage", "marker introduction history is not singular"
        )
    if marker_history_events(repository, "D"):
        raise ValidationFailure(
            "migration_marker_lineage", "marker deletion exists in current ancestry"
        )


def authorize_candidate_surface(
    repository: Path,
    transient_entries: Tuple[str, ...],
    marker_entries: Tuple[str, ...],
    violation_category: str,
) -> None:
    if not marker_entries:
        if transient_entries:
            raise ValidationFailure(
                violation_category,
                "candidate surface contains .superpowers/** without migration marker",
            )
        return
    if len(marker_entries) != 1:
        raise ValidationFailure(
            "migration_marker_mismatch", "candidate surface must contain one marker"
        )
    marker_manifest(repository, marker_entries[0])
    require_marker_history_authority(repository)
    if tree_entries(
        repository, AUTHORIZED_MIGRATION_BASELINE
    ) != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_baseline_mismatch",
            "authorized migration baseline mode/blob/path entries do not match",
        )
    if transient_entries != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_baseline_mismatch",
            "candidate surface is not the exact unchanged migration baseline set",
        )


def validate_scratch(
    repository: Path, scratch_path: Optional[str], scratch_reason: Optional[str]
) -> None:
    if scratch_path is None and scratch_reason is None:
        return
    if scratch_path is None:
        raise ValidationFailure("scratch_path_invalid", "scratch reason has no path")
    if scratch_reason is None or not scratch_reason.strip():
        raise ValidationFailure(
            "scratch_reason_missing", "repository-local scratch needs a concrete reason"
        )

    relative = Path(scratch_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValidationFailure(
            "scratch_path_invalid", "scratch path must be repository-relative"
        )
    resolved = (repository / relative).resolve()
    try:
        normalized = resolved.relative_to(repository).as_posix()
    except ValueError as exc:
        raise ValidationFailure(
            "scratch_path_invalid", "scratch path escapes the repository"
        ) from exc
    if not normalized.startswith(".superpowers/"):
        raise ValidationFailure(
            "scratch_path_invalid", "scratch path must be under .superpowers/"
        )

    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", "--", normalized],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        raise ValidationFailure(
            "scratch_ignore_missing",
            "scratch path is not covered by Git ignore rules before write",
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or "git check-ignore failed"
        raise ValidationFailure("repository_error", detail)

    if index_entries(repository, normalized) or tree_entries(
        repository, "HEAD", normalized
    ):
        raise ValidationFailure(
            "scratch_state_invalid",
            "nominated scratch path must be independently untracked and uncommitted",
        )


def validate_index(repository: Path) -> None:
    authorize_candidate_surface(
        repository,
        index_entries(repository),
        index_entries(repository, MIGRATION_MARKER_PATH),
        "index_entry",
    )


def validate_candidate_trees(
    repository: Path, object_names: Sequence[str]
) -> None:
    for object_name in object_names:
        authorize_candidate_surface(
            repository,
            tree_entries(repository, object_name),
            tree_entries(repository, object_name, MIGRATION_MARKER_PATH),
            "candidate_tree_entry",
        )


def reject_strict_trees(
    repository: Path, object_names: Sequence[str], category: str, label: str
) -> None:
    for object_name in object_names:
        if tree_entries(repository, object_name) or tree_entries(
            repository, object_name, MIGRATION_MARKER_PATH
        ):
            raise ValidationFailure(
                category, f"{label} contains transient entries or migration marker"
            )


def validate(args: argparse.Namespace) -> None:
    repository = repository_root(Path(args.repository))
    if args.post_cleanup_history and args.new_commit:
        raise ValidationFailure(
            "argument_conflict",
            "--post-cleanup-history cannot be combined with --new-commit",
        )
    validate_scratch(repository, args.scratch_path, args.scratch_reason)
    validate_index(repository)
    validate_candidate_trees(repository, args.candidate_tree)
    new_commits = (
        post_cleanup_commits(repository)
        if args.post_cleanup_history
        else args.new_commit
    )
    reject_strict_trees(
        repository, new_commits, "new_commit_entry", "post-cleanup new commit"
    )
    reject_strict_trees(
        repository, args.final_tree, "final_tree_entry", "final tree"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=str(REPOSITORY_ROOT))
    parser.add_argument("--scratch-path")
    parser.add_argument("--scratch-reason")
    parser.add_argument("--candidate-tree", action="append", default=[])
    parser.add_argument("--new-commit", action="append", default=[])
    parser.add_argument("--post-cleanup-history", action="store_true")
    parser.add_argument("--final-tree", action="append", default=[])
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validate(args)
    except (OSError, ValidationFailure) as exc:
        if isinstance(exc, ValidationFailure):
            category, message = exc.category, exc.message
        else:
            category, message = "repository_error", str(exc)
        print(f"ERROR category={category} message={message}", file=sys.stderr)
        return 1
    print("OK: validated SDD transient artifact Git surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
