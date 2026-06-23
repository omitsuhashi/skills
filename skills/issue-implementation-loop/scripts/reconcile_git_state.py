#!/usr/bin/env python3
"""Compare an Execution Envelope with current local git branch/worktree state."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from _common import dump_json, git_output, load_json, validate_execution_envelope


def parse_worktrees(output: str) -> dict[str, dict[str, str]]:
    worktrees: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for line in output.splitlines():
        if line.startswith("worktree "):
            path = line.removeprefix("worktree ")
            current = {"path": path}
            worktrees[path] = current
        elif current is not None and line.startswith("branch "):
            current["branch"] = line.removeprefix("branch refs/heads/")
        elif current is not None and line.startswith("HEAD "):
            current["head"] = line.removeprefix("HEAD ")
    return worktrees


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope")
    parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    errors = validate_execution_envelope(envelope)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    worktree_result = git_output(["worktree", "list", "--porcelain"], cwd=args.repo)
    branch_result = git_output(["branch", "--format=%(refname:short)"], cwd=args.repo)
    common_dir_result = git_output(["rev-parse", "--git-common-dir"], cwd=args.repo)
    if worktree_result.returncode != 0 or branch_result.returncode != 0:
        print("not a git repository or git command failed", file=sys.stderr)
        return 1

    registered = parse_worktrees(worktree_result.stdout)
    branches = set(branch_result.stdout.splitlines())
    reservations = {}
    collisions = []
    for issue_id, item in envelope["work_items"].items():
        path = item["worktree_path"]
        branch = item["branch"]
        registered_record = registered.get(path)
        branch_exists = branch in branches
        path_exists = Path(path).exists()
        path_registered = registered_record is not None
        branch_registered = bool(registered_record and registered_record.get("branch") == branch)
        unexpected_path_collision = path_exists and not path_registered
        if unexpected_path_collision:
            collisions.append(
                {
                    "issue": issue_id,
                    "type": "filesystem_path",
                    "path": path,
                }
            )
        reservations[issue_id] = {
            "branch": branch,
            "branch_exists": branch_exists,
            "worktree_path": path,
            "path_exists": path_exists,
            "path_registered": path_registered,
            "branch_registered_at_path": branch_registered,
            "expected_state": item.get("worktree_state"),
        }

    result = {
        "ok": not collisions,
        "repo": os.path.abspath(args.repo),
        "git_common_dir": common_dir_result.stdout.strip()
        if common_dir_result.returncode == 0
        else None,
        "reservations": reservations,
        "collisions": collisions,
    }
    if args.json:
        print(dump_json(result), end="")
    else:
        print("GIT RECONCILE OK" if result["ok"] else "GIT RECONCILE FOUND COLLISIONS")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
