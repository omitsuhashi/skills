#!/usr/bin/env python3
"""Fail closed when SDD transient artifacts enter a nominated Git surface."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TRANSIENT_PATHSPEC = ".superpowers"
AUTHORIZED_SQUASH_POLICY_ROOT = "82dcd32157ff9690ae038f982f3916009e449f80"
AUTHORIZED_PRE_POLICY_TIP = "40c2b67ba68febad508f902ec62dcc1bef9cf8b8"


class ValidationFailure(Exception):
    """A single fail-closed validation result."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category
        self.message = message


def run_git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repository),
        check=False,
        capture_output=True,
        text=True,
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
            "history_unavailable", "post-policy boundary is outside HEAD ancestry"
        )
    if result.returncode != 0:
        detail = result.stderr.strip() or "cannot verify post-policy ancestry"
        raise ValidationFailure("repository_error", detail)


def commit_parents(repository: Path, commit: str) -> Tuple[str, ...]:
    fields = run_git(repository, "rev-list", "--parents", "-n", "1", commit).split()
    if not fields or fields[0] != commit:
        raise ValidationFailure(
            "history_unavailable", f"cannot resolve policy boundary commit: {commit}"
        )
    return tuple(fields[1:])


def revision_range(repository: Path, start: str, end: str) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository, "rev-list", "--reverse", f"{start}..{end}"
        ).splitlines()
        if line
    )


def post_policy_commits(repository: Path) -> Tuple[str, ...]:
    if run_git(repository, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise ValidationFailure(
            "history_unavailable",
            "post-policy validation requires complete repository history",
        )
    require_ancestor(repository, AUTHORIZED_SQUASH_POLICY_ROOT, "HEAD")
    require_ancestor(repository, AUTHORIZED_PRE_POLICY_TIP, "HEAD")
    parents = commit_parents(repository, AUTHORIZED_SQUASH_POLICY_ROOT)
    if len(parents) != 1:
        raise ValidationFailure(
            "history_unavailable", "policy root must have exactly one parent"
        )
    pre_policy_commits = set(
        revision_range(repository, parents[0], AUTHORIZED_PRE_POLICY_TIP)
    )
    return tuple(
        commit
        for commit in revision_range(repository, parents[0], "HEAD")
        if commit not in pre_policy_commits
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
    if index_entries(repository):
        raise ValidationFailure("index_entry", "Git index contains .superpowers/**")


def validate_candidate_trees(
    repository: Path, object_names: Sequence[str]
) -> None:
    for object_name in object_names:
        if tree_entries(repository, object_name):
            raise ValidationFailure(
                "candidate_tree_entry", "candidate tree contains .superpowers/**"
            )


def reject_strict_trees(
    repository: Path, object_names: Sequence[str], category: str, label: str
) -> None:
    for object_name in object_names:
        if tree_entries(repository, object_name):
            raise ValidationFailure(
                category, f"{label} contains .superpowers/**"
            )


def validate(args: argparse.Namespace) -> None:
    repository = repository_root(Path(args.repository))
    if args.post_policy_history and args.new_commit:
        raise ValidationFailure(
            "argument_conflict",
            "--post-policy-history cannot be combined with --new-commit",
        )
    validate_scratch(repository, args.scratch_path, args.scratch_reason)
    validate_index(repository)
    validate_candidate_trees(repository, args.candidate_tree)
    new_commits = (
        post_policy_commits(repository)
        if args.post_policy_history
        else args.new_commit
    )
    reject_strict_trees(
        repository, new_commits, "new_commit_entry", "post-policy new commit"
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
    parser.add_argument("--post-policy-history", action="store_true")
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
