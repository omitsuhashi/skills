#!/usr/bin/env python3
"""Fail-fast prerequisite check for the grill-to-pr-loop composition skill."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


PLANNING_REQUIRED_SKILLS = ("grill-with-docs",)
EXECUTION_REQUIRED_SKILLS = ("issue-implementation-loop",)
OPTIONAL_SKILLS = (
    "to-prd",
    "to-issues",
    "tdd",
    "grill-me",
    "handoff",
    "requesting-code-review",
)


def plugin_skill_roots(home: Path) -> list[Path]:
    cache_root = home / ".codex" / "plugins" / "cache"
    if not cache_root.exists():
        return []

    roots: list[Path] = []
    for pattern in ("*/skills", "*/*/skills", "*/*/*/skills"):
        roots.extend(path for path in cache_root.glob(pattern) if path.is_dir())
    return roots


def candidate_roots(extra_roots: list[str]) -> list[Path]:
    roots: list[Path] = []
    for root in extra_roots:
        roots.append(Path(root).expanduser())

    roots.extend(
        [
            Path.cwd() / "skills",
            Path.cwd() / ".agents" / "skills",
            Path.cwd() / "agents" / "skills",
        ]
    )

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        roots.append(Path(codex_home).expanduser() / "skills")

    home = Path.home()
    roots.extend(
        [
            home / ".agents" / "skills",
            home / ".codex" / "skills",
        ]
    )
    roots.extend(plugin_skill_roots(home))

    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.expanduser()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def find_skill(skill_name: str, roots: list[Path]) -> Path | None:
    for root in roots:
        skill_file = root / skill_name / "SKILL.md"
        if skill_file.exists():
            return skill_file
    return None


def git_github_remotes() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "remote", "-v"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []

    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if "github.com" in line]


def gh_auth_status(gh_path: str | None) -> dict[str, str | int | None]:
    if not gh_path:
        return {
            "status": "not_checked",
            "returncode": None,
            "summary": "gh CLI not found",
        }

    try:
        completed = subprocess.run(
            [gh_path, "auth", "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "returncode": None,
            "summary": "gh auth status timed out",
        }
    except OSError as exc:
        return {
            "status": "error",
            "returncode": None,
            "summary": str(exc),
        }

    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "returncode": completed.returncode,
        "summary": "authenticated"
        if completed.returncode == 0
        else "not authenticated or unavailable",
    }


def required_for_phase(phase: str) -> tuple[str, ...]:
    if phase == "planning":
        return PLANNING_REQUIRED_SKILLS
    return PLANNING_REQUIRED_SKILLS + EXECUTION_REQUIRED_SKILLS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that required skills for grill-to-pr-loop are installed."
    )
    parser.add_argument(
        "--phase",
        choices=("planning", "execution"),
        default="planning",
        help="planning requires grill-with-docs; execution also requires issue-implementation-loop.",
    )
    parser.add_argument(
        "--skills-root",
        action="append",
        default=[],
        help="Additional skills root to search. May be repeated.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    roots = candidate_roots(args.skills_root)
    required_names = required_for_phase(args.phase)
    required = {name: find_skill(name, roots) for name in required_names}
    optional = {name: find_skill(name, roots) for name in OPTIONAL_SKILLS}
    missing_required = [name for name, path in required.items() if path is None]
    gh_path = shutil.which("gh")
    github = {
        "gh_cli": gh_path,
        "gh_auth_status": gh_auth_status(gh_path),
        "github_remotes": git_github_remotes(),
    }
    execution_skill = find_skill("issue-implementation-loop", roots)

    result = {
        "ok": not missing_required,
        "phase": args.phase,
        "checked_roots": [str(path) for path in roots],
        "required": {name: str(path) if path else None for name, path in required.items()},
        "optional": {name: str(path) if path else None for name, path in optional.items()},
        "execution_required": {
            "available": execution_skill is not None,
            "issue-implementation-loop": str(execution_skill)
            if execution_skill
            else None,
        },
        "reviewer_optional": {
            "available": optional["requesting-code-review"] is not None,
            "requesting-code-review": str(optional["requesting-code-review"])
            if optional["requesting-code-review"]
            else None,
        },
        "github_optional": github,
        "missing_required": missing_required,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Phase: {args.phase}")
        for name, path in required.items():
            if path:
                print(f"OK required skill: {name} ({path})")
            else:
                print(f"ERROR missing required skill: {name}")
        if args.phase == "planning" and execution_skill:
            print(f"OK execution skill available for later: issue-implementation-loop ({execution_skill})")
        elif args.phase == "planning":
            print("WARN execution skill missing for later: issue-implementation-loop")
        for name, path in optional.items():
            if path:
                print(f"OK optional skill: {name} ({path})")
            else:
                print(f"WARN missing optional skill: {name}")
        if github["gh_cli"]:
            print(f"OK optional GitHub CLI: {github['gh_cli']}")
        else:
            print("WARN optional GitHub CLI not found: gh")
        auth = github["gh_auth_status"]
        if auth["status"] == "ok":
            print(f"OK optional GitHub auth: {auth['summary']}")
        else:
            print(f"WARN optional GitHub auth: {auth['summary']}")
        if github["github_remotes"]:
            print("OK optional GitHub remote detected")
            for remote in github["github_remotes"]:
                print(f"- {remote}")
        else:
            print("WARN optional GitHub remote not detected in current directory")
        if missing_required:
            print("STOP: install missing required skills before continuing.")
            print("Checked roots:")
            for root in roots:
                print(f"- {root}")
        else:
            print("PREREQ CHECK PASSED")

    return 2 if missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
