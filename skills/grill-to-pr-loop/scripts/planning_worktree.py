#!/usr/bin/env python3
"""Prepare or reuse the isolated planning worktree for one Epic."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


EPIC_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class GateError(RuntimeError):
    """A planning worktree cannot be prepared safely."""


def git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def absolute_path(value: str, flag: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise GateError(f"{flag} must be an absolute path")
    return path.resolve()


def canonical_repo_root(repo_root: str) -> Path:
    requested = absolute_path(repo_root, "--repo-root")
    return Path(git(requested, "rev-parse", "--show-toplevel").strip()).resolve()


def parse_worktree_list(porcelain: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in porcelain.splitlines():
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        records.append(current)
    return records


def select_default_checkout(
    repo_root: Path, worktrees: list[dict[str, str]], default_branch: str
) -> Path:
    wanted_branch = f"refs/heads/{default_branch}"
    for worktree in worktrees:
        if worktree.get("branch") == wanted_branch and "worktree" in worktree:
            return Path(worktree["worktree"]).resolve()
    raise GateError(
        f"no registered checkout is on the requested default branch {default_branch!r}"
    )


def git_common_dir(default_checkout: Path) -> Path:
    common_dir = Path(git(default_checkout, "rev-parse", "--git-common-dir").strip())
    if not common_dir.is_absolute():
        common_dir = default_checkout / common_dir
    return common_dir.resolve()


def runtime_state_path(common_dir: Path, epic_id: str) -> Path:
    return (
        common_dir
        / "agent-runs"
        / "grill-to-pr-loop"
        / epic_id
        / "planning-worktree.json"
    )


def write_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_path, path)
    except BaseException:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    if not EPIC_ID_PATTERN.fullmatch(args.epic_id):
        raise GateError("--epic-id must be lower-kebab")

    repo_root = canonical_repo_root(args.repo_root)
    worktree_root = absolute_path(
        args.worktree_root or str(repo_root / ".worktrees"), "--worktree-root"
    )
    try:
        ignored_relative_root = worktree_root.relative_to(repo_root)
    except ValueError as error:
        raise GateError("--worktree-root must be project-local") from error

    worktrees = parse_worktree_list(git(repo_root, "worktree", "list", "--porcelain"))
    default_checkout = select_default_checkout(repo_root, worktrees, args.default_branch)
    start_head = git(default_checkout, "rev-parse", "HEAD").strip()
    start_status = git(
        default_checkout, "status", "--porcelain=v1", "--untracked-files=all"
    )
    planning_branch = f"codex/{args.epic_id}/planning"
    wanted_branch = f"refs/heads/{planning_branch}"

    for worktree in worktrees:
        if worktree.get("branch") == wanted_branch and "worktree" in worktree:
            planning_worktree = Path(worktree["worktree"]).resolve()
            reused = True
            break
    else:
        ignored = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "check-ignore",
                "--no-index",
                "-q",
                "--",
                f"{ignored_relative_root.as_posix().rstrip('/')}/",
            ],
            check=False,
            capture_output=True,
            text=True,
        ).returncode == 0
        if not ignored:
            raise GateError("--worktree-root must be ignored by the repository")

        planning_worktree = worktree_root / args.epic_id
        if planning_worktree.exists():
            raise GateError(
                "planning worktree destination already exists but is not registered"
            )
        worktree_root.mkdir(parents=True, exist_ok=True)
        branch_exists = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "show-ref",
                "--verify",
                "--quiet",
                f"refs/heads/{planning_branch}",
            ],
            check=False,
        ).returncode == 0
        worktree_add = ["worktree", "add"]
        if branch_exists:
            worktree_add.extend((str(planning_worktree), planning_branch))
        else:
            worktree_add.extend(("-b", planning_branch, str(planning_worktree), start_head))
        git(repo_root, *worktree_add)
        planning_worktree = planning_worktree.resolve()
        reused = False

    common_dir = git_common_dir(default_checkout)
    state_path = runtime_state_path(common_dir, args.epic_id)
    state_payload: dict[str, Any] = {
        "schema_version": 1,
        "epic_id": args.epic_id,
        "planning_branch": planning_branch,
        "planning_base_sha": start_head,
        "default_checkout": str(default_checkout),
        "worktree_root": str(worktree_root),
        "planning_worktree": str(planning_worktree),
        "default_checkout_start": {
            "head": start_head,
            "status_porcelain": start_status,
        },
    }
    write_json_atomically(state_path, state_payload)
    return {
        "ok": True,
        "epic_id": args.epic_id,
        "planning_branch": planning_branch,
        "planning_base_sha": start_head,
        "reused": reused,
        "runtime_state_path": str(state_path),
        "default_checkout": str(default_checkout),
        "planning_worktree": str(planning_worktree),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subcommands.add_parser("prepare")
    prepare_parser.add_argument("--repo-root", required=True)
    prepare_parser.add_argument("--epic-id", required=True)
    prepare_parser.add_argument("--default-branch", default="main")
    prepare_parser.add_argument("--worktree-root")
    prepare_parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = prepare(args)
    except (GateError, OSError) as error:
        failure = {"ok": False, "error": str(error)}
        if args.json:
            print(json.dumps(failure, ensure_ascii=False, sort_keys=True))
        else:
            print(f"planning worktree gate failed: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(payload["planning_worktree"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
