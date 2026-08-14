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
AUTHORIZED_MIGRATION_BASELINE = "f07aebce7bbf854cd64184311d204cf04055fd28"
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


def tree_entries(repository: Path, object_name: str) -> Tuple[str, ...]:
    return tuple(
        line
        for line in run_git(
            repository,
            "ls-tree",
            "-r",
            object_name,
            "--",
            TRANSIENT_PATHSPEC,
        ).splitlines()
        if line
    )


def index_entries(repository: Path) -> Tuple[str, ...]:
    entries: List[str] = []
    for line in run_git(
        repository, "ls-files", "--stage", "--", TRANSIENT_PATHSPEC
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


def require_migration_baseline(
    repository: Path, migration_baseline: Optional[str]
) -> bool:
    if migration_baseline is None:
        return False
    if migration_baseline != AUTHORIZED_MIGRATION_BASELINE:
        raise ValidationFailure(
            "migration_baseline_unauthorized",
            "only the immutable amendment migration baseline is authorized",
        )
    if tree_entries(repository, migration_baseline) != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_baseline_mismatch",
            "authorized migration baseline mode/blob/path entries do not match",
        )
    if index_entries(repository) != AUTHORIZED_MIGRATION_ENTRIES:
        raise ValidationFailure(
            "migration_baseline_mismatch",
            "current index is not the exact unchanged migration baseline set",
        )
    return True


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


def reject_index_entries(repository: Path, migration_allowed: bool) -> None:
    entries = index_entries(repository)
    if entries and not migration_allowed:
        raise ValidationFailure(
            "index_entry", "current Git index contains .superpowers/**"
        )


def reject_tree_entries(
    repository: Path, object_names: Sequence[str], category: str, label: str
) -> None:
    for object_name in object_names:
        if tree_entries(repository, object_name):
            raise ValidationFailure(category, f"{label} contains .superpowers/**")


def validate(args: argparse.Namespace) -> None:
    repository = repository_root(Path(args.repository))
    validate_scratch(repository, args.scratch_path, args.scratch_reason)
    migration_allowed = require_migration_baseline(
        repository, args.migration_baseline
    )
    reject_index_entries(repository, migration_allowed)
    reject_tree_entries(
        repository, args.candidate_tree, "candidate_tree_entry", "candidate tree"
    )
    reject_tree_entries(
        repository, args.new_commit, "new_commit_entry", "post-cleanup new commit"
    )
    reject_tree_entries(
        repository, args.final_tree, "final_tree_entry", "final tree"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=str(REPOSITORY_ROOT))
    parser.add_argument("--migration-baseline")
    parser.add_argument("--scratch-path")
    parser.add_argument("--scratch-reason")
    parser.add_argument("--candidate-tree", action="append", default=[])
    parser.add_argument("--new-commit", action="append", default=[])
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
