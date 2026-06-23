#!/usr/bin/env python3
"""Check local capabilities before running issue-implementation-loop."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

from _common import dump_json, find_skill, git_output, load_json, validate_input_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Optional normalized input packet to validate.")
    parser.add_argument("--repo", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    git_path = shutil.which("git")
    repo_result = git_output(["rev-parse", "--show-toplevel"], cwd=args.repo) if git_path else None
    common_dir_result = git_output(["rev-parse", "--git-common-dir"], cwd=args.repo) if git_path else None
    packet_errors: list[str] = []
    if args.input:
        packet_errors = validate_input_packet(load_json(args.input))

    result = {
        "ok": bool(git_path)
        and bool(repo_result and repo_result.returncode == 0)
        and not packet_errors,
        "git": {
            "path": git_path,
            "repo_root": repo_result.stdout.strip()
            if repo_result and repo_result.returncode == 0
            else None,
            "common_dir": common_dir_result.stdout.strip()
            if common_dir_result and common_dir_result.returncode == 0
            else None,
        },
        "input_packet": {
            "path": args.input,
            "ok": not packet_errors,
            "errors": packet_errors,
        },
        "skills": {
            "tdd": find_skill("tdd"),
            "requesting-code-review": find_skill("requesting-code-review"),
        },
        "parallel_execution": {
            "available": None,
            "note": "Platform-dependent; approve serial fallback in the Execution Envelope when uncertain.",
        },
        "remote_delivery": {
            "gh": shutil.which("gh"),
            "note": "Remote writes still need explicit user approval.",
        },
    }
    if args.json:
        print(dump_json(result), end="")
    else:
        if result["ok"]:
            print("CAPABILITY CHECK OK")
        else:
            print("CAPABILITY CHECK FAILED", file=sys.stderr)
        if packet_errors:
            for error in packet_errors:
                print(error, file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
