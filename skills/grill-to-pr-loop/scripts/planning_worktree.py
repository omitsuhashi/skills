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
FULL_OBJECT_ID_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
RUNTIME_V1_FIELDS = frozenset(
    {
        "schema_version",
        "epic_id",
        "planning_branch",
        "planning_base_sha",
        "default_checkout",
        "worktree_root",
        "planning_worktree",
        "default_checkout_start",
    }
)
DEFAULT_SNAPSHOT_FIELDS = frozenset({"head", "status_porcelain"})
REPOSITORY_ROUTING_ENVIRONMENT = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CEILING_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_DIR",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_QUARANTINE_PATH",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    }
)


class GateError(RuntimeError):
    """A planning worktree cannot be prepared safely."""


def git_environment(*, read_only: bool) -> dict[str, str]:
    environment = os.environ.copy()
    for name in tuple(environment):
        if (
            name in REPOSITORY_ROUTING_ENVIRONMENT
            or name.startswith("GIT_CONFIG_KEY_")
            or name.startswith("GIT_CONFIG_VALUE_")
        ):
            environment.pop(name)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_GRAFT_FILE"] = os.devnull
    if read_only:
        environment["GIT_OPTIONAL_LOCKS"] = "0"
    else:
        environment.pop("GIT_OPTIONAL_LOCKS", None)
    return environment


def git(repo_root: Path, *args: str, read_only: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
        env=git_environment(read_only=read_only),
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def read_only_git_succeeds(repo_root: Path, *args: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            capture_output=True,
            text=True,
            env=git_environment(read_only=True),
        ).returncode
        == 0
    )


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


def create_json_atomically(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary_path, path)
        except FileExistsError as error:
            raise GateError(
                "planning runtime identity artifact already exists"
            ) from error
        os.unlink(temporary_path)
    except BaseException:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def reject_duplicate_json_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for field, value in pairs:
        if field in payload:
            raise GateError(
                f"planning runtime identity artifact has duplicate field {field}"
            )
        payload[field] = value
    return payload


def load_runtime_identity(
    state_path: Path,
    *,
    epic_id: str,
    planning_branch: str,
    default_checkout: Path,
    worktree_root: Path,
    planning_worktree: Path,
) -> dict[str, Any]:
    try:
        payload = json.loads(
            state_path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_json_fields,
        )
    except FileNotFoundError as error:
        raise GateError(
            "registered planning worktree is missing its runtime identity artifact"
        ) from error
    except UnicodeDecodeError as error:
        raise GateError(
            "planning runtime identity artifact is not valid UTF-8"
        ) from error
    except json.JSONDecodeError as error:
        raise GateError("planning runtime identity artifact is invalid JSON") from error

    if not isinstance(payload, dict):
        raise GateError("planning runtime identity artifact must be an object")
    if set(payload) != RUNTIME_V1_FIELDS:
        raise GateError("planning runtime identity artifact has invalid v1 shape")
    if type(payload.get("schema_version")) is not int:
        raise GateError("planning runtime identity artifact has invalid schema_version")
    expected = {
        "schema_version": 1,
        "epic_id": epic_id,
        "planning_branch": planning_branch,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            raise GateError(f"planning runtime identity artifact has invalid {field}")

    for field, expected_path in (
        ("default_checkout", default_checkout),
        ("worktree_root", worktree_root),
        ("planning_worktree", planning_worktree),
    ):
        value = payload.get(field)
        if not isinstance(value, str):
            raise GateError(
                f"planning runtime identity artifact has invalid absolute {field}"
            )
        try:
            stored_path = Path(value)
            resolved_path = stored_path.resolve()
            valid_directory = stored_path.is_dir()
        except (OSError, RuntimeError, ValueError) as error:
            raise GateError(
                f"planning runtime identity artifact has invalid absolute {field}"
            ) from error
        if not stored_path.is_absolute():
            raise GateError(
                f"planning runtime identity artifact has invalid absolute {field}"
            )
        if value != str(resolved_path) or resolved_path != expected_path:
            raise GateError(f"planning runtime identity artifact has invalid {field}")
        if not valid_directory:
            raise GateError(
                f"planning runtime identity artifact {field} is not a directory"
            )

    planning_base_sha = payload.get("planning_base_sha")
    if not isinstance(planning_base_sha, str) or not FULL_OBJECT_ID_PATTERN.fullmatch(
        planning_base_sha
    ):
        raise GateError(
            "planning runtime identity artifact has invalid planning_base_sha"
        )
    start = payload.get("default_checkout_start")
    if (
        not isinstance(start, dict)
        or set(start) != DEFAULT_SNAPSHOT_FIELDS
        or not isinstance(start.get("head"), str)
        or not isinstance(start.get("status_porcelain"), str)
    ):
        raise GateError("planning runtime identity artifact has invalid default snapshot")
    if start["head"] != planning_base_sha:
        raise GateError(
            "planning runtime identity artifact snapshot head does not match "
            "planning_base_sha"
        )
    return payload


def default_checkout_snapshot(default_checkout: Path) -> tuple[str, str]:
    head_before = git(default_checkout, "rev-parse", "HEAD").strip()
    status_before = git(
        default_checkout,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    head_after = git(default_checkout, "rev-parse", "HEAD").strip()
    status_after = git(
        default_checkout,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if (head_before, status_before) != (head_after, status_after):
        raise GateError(
            "default checkout changed while its snapshot was collected"
        )
    return head_after, status_after


def require_ancestor(
    repo_root: Path, ancestor: str, descendant: str, *, message: str
) -> None:
    if not read_only_git_succeeds(
        repo_root, "merge-base", "--is-ancestor", ancestor, descendant
    ):
        raise GateError(message)


def verify_registered_planning_worktree(
    planning_worktree: Path,
    *,
    planning_branch: str,
    expected_common_dir: Path,
    default_head: str,
) -> None:
    actual_branch = git(
        planning_worktree, "symbolic-ref", "--quiet", "HEAD"
    ).strip()
    wanted_branch = f"refs/heads/{planning_branch}"
    if actual_branch != wanted_branch:
        raise GateError(
            "registered planning worktree is not on the exact planning branch"
        )
    if git_common_dir(planning_worktree) != expected_common_dir:
        raise GateError(
            "registered planning worktree does not share the default repository"
        )
    planning_head = git(planning_worktree, "rev-parse", "HEAD").strip()
    require_ancestor(
        planning_worktree,
        default_head,
        planning_head,
        message=(
            "current default HEAD is not an ancestor of the registered "
            "planning worktree HEAD"
        ),
    )


def verify_current_worktree_registration(
    default_checkout: Path,
    planning_worktree: Path,
    *,
    default_branch: str,
    planning_branch: str,
) -> None:
    worktrees = parse_worktree_list(
        git(default_checkout, "worktree", "list", "--porcelain")
    )
    expected = (
        (default_checkout, f"refs/heads/{default_branch}", "default checkout"),
        (planning_worktree, f"refs/heads/{planning_branch}", "planning worktree"),
    )
    for expected_path, expected_branch, label in expected:
        branch_records = [
            worktree
            for worktree in worktrees
            if worktree.get("branch") == expected_branch
            and "worktree" in worktree
        ]
        if (
            len(branch_records) != 1
            or Path(branch_records[0]["worktree"]).resolve() != expected_path
        ):
            raise GateError(
                f"current registered {label} does not match its exact path and branch"
            )


def validate_runtime_reuse(
    state_payload: dict[str, Any],
    *,
    default_checkout: Path,
    default_branch: str,
    planning_worktree: Path,
    planning_branch: str,
    expected_common_dir: Path,
) -> None:
    planning_base_sha = state_payload["planning_base_sha"]
    verify_current_worktree_registration(
        default_checkout,
        planning_worktree,
        default_branch=default_branch,
        planning_branch=planning_branch,
    )
    verify_registered_planning_worktree(
        planning_worktree,
        planning_branch=planning_branch,
        expected_common_dir=expected_common_dir,
        default_head=planning_base_sha,
    )
    current_snapshot = default_checkout_snapshot(default_checkout)
    start = state_payload["default_checkout_start"]
    stored_snapshot = (start["head"], start["status_porcelain"])
    if current_snapshot != stored_snapshot:
        raise GateError(
            "current default checkout does not match its stored start snapshot"
        )


def runtime_payload(
    *,
    epic_id: str,
    planning_branch: str,
    planning_base_sha: str,
    default_checkout: Path,
    worktree_root: Path,
    planning_worktree: Path,
    start_status: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "epic_id": epic_id,
        "planning_branch": planning_branch,
        "planning_base_sha": planning_base_sha,
        "default_checkout": str(default_checkout),
        "worktree_root": str(worktree_root),
        "planning_worktree": str(planning_worktree),
        "default_checkout_start": {
            "head": planning_base_sha,
            "status_porcelain": start_status,
        },
    }


def revalidate_before_runtime_publication(
    default_checkout: Path,
    planning_worktree: Path,
    *,
    default_branch: str,
    planning_branch: str,
    expected_common_dir: Path,
    default_head: str,
    default_status: str,
    created: bool,
) -> None:
    try:
        verify_current_worktree_registration(
            default_checkout,
            planning_worktree,
            default_branch=default_branch,
            planning_branch=planning_branch,
        )
        verify_registered_planning_worktree(
            planning_worktree,
            planning_branch=planning_branch,
            expected_common_dir=expected_common_dir,
            default_head=default_head,
        )
        if default_checkout_snapshot(default_checkout) != (
            default_head,
            default_status,
        ):
            raise GateError(
                "current default checkout does not match its captured start snapshot"
            )
    except GateError as error:
        disposition = (
            "was created and left in place"
            if created
            else "was already registered and left in place"
        )
        raise GateError(
            f"planning worktree {planning_worktree} on branch {planning_branch} "
            f"{disposition} for manual inspection; runtime identity was not "
            f"published: {error}"
        ) from error


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
    planning_branch = f"codex/{args.epic_id}/planning"
    wanted_branch = f"refs/heads/{planning_branch}"

    for worktree in worktrees:
        if worktree.get("branch") == wanted_branch and "worktree" in worktree:
            planning_worktree = Path(worktree["worktree"]).resolve()
            reused = True
            break
    else:
        reused = False

    common_dir = git_common_dir(default_checkout)
    state_path = runtime_state_path(common_dir, args.epic_id)
    if reused:
        if state_path.exists():
            state_payload = load_runtime_identity(
                state_path,
                epic_id=args.epic_id,
                planning_branch=planning_branch,
                default_checkout=default_checkout,
                worktree_root=worktree_root,
                planning_worktree=planning_worktree,
            )
            validate_runtime_reuse(
                state_payload,
                default_checkout=default_checkout,
                default_branch=args.default_branch,
                planning_worktree=planning_worktree,
                planning_branch=planning_branch,
                expected_common_dir=common_dir,
            )
            final_state_payload = load_runtime_identity(
                state_path,
                epic_id=args.epic_id,
                planning_branch=planning_branch,
                default_checkout=default_checkout,
                worktree_root=worktree_root,
                planning_worktree=planning_worktree,
            )
            if final_state_payload != state_payload:
                raise GateError(
                    "planning runtime identity artifact changed during reuse validation"
                )
            validate_runtime_reuse(
                final_state_payload,
                default_checkout=default_checkout,
                default_branch=args.default_branch,
                planning_worktree=planning_worktree,
                planning_branch=planning_branch,
                expected_common_dir=common_dir,
            )
            confirmed_state_payload = load_runtime_identity(
                state_path,
                epic_id=args.epic_id,
                planning_branch=planning_branch,
                default_checkout=default_checkout,
                worktree_root=worktree_root,
                planning_worktree=planning_worktree,
            )
            if confirmed_state_payload != final_state_payload:
                raise GateError(
                    "planning runtime identity artifact changed during reuse validation"
                )
            validate_runtime_reuse(
                confirmed_state_payload,
                default_checkout=default_checkout,
                default_branch=args.default_branch,
                planning_worktree=planning_worktree,
                planning_branch=planning_branch,
                expected_common_dir=common_dir,
            )
            state_payload = confirmed_state_payload
        else:
            start_head, start_status = default_checkout_snapshot(default_checkout)
            verify_registered_planning_worktree(
                planning_worktree,
                planning_branch=planning_branch,
                expected_common_dir=common_dir,
                default_head=start_head,
            )
            state_payload = runtime_payload(
                epic_id=args.epic_id,
                planning_branch=planning_branch,
                planning_base_sha=start_head,
                default_checkout=default_checkout,
                worktree_root=worktree_root,
                planning_worktree=planning_worktree,
                start_status=start_status,
            )
            revalidate_before_runtime_publication(
                default_checkout,
                planning_worktree,
                default_branch=args.default_branch,
                planning_branch=planning_branch,
                expected_common_dir=common_dir,
                default_head=start_head,
                default_status=start_status,
                created=False,
            )
            create_json_atomically(state_path, state_payload)
        return {
            "ok": True,
            "epic_id": args.epic_id,
            "planning_branch": planning_branch,
            "planning_base_sha": state_payload["planning_base_sha"],
            "reused": True,
            "runtime_state_path": str(state_path),
            "default_checkout": str(default_checkout),
            "planning_worktree": str(planning_worktree),
        }

    if state_path.exists():
        raise GateError(
            "planning runtime identity artifact exists without a registered worktree"
        )

    start_head, start_status = default_checkout_snapshot(default_checkout)
    ignored = read_only_git_succeeds(
        repo_root,
        "check-ignore",
        "--no-index",
        "-q",
        "--",
        f"{ignored_relative_root.as_posix().rstrip('/')}/",
    )
    if not ignored:
        raise GateError("--worktree-root must be ignored by the repository")

    planning_worktree = worktree_root / args.epic_id
    if planning_worktree.exists():
        raise GateError(
            "planning worktree destination already exists but is not registered"
        )
    branch_exists = read_only_git_succeeds(
        repo_root,
        "show-ref",
        "--verify",
        "--quiet",
        f"refs/heads/{planning_branch}",
    )
    worktree_add = ["worktree", "add"]
    if branch_exists:
        branch_head = git(
            repo_root, "rev-parse", f"refs/heads/{planning_branch}"
        ).strip()
        require_ancestor(
            repo_root,
            start_head,
            branch_head,
            message=(
                "current default HEAD is not an ancestor of the existing "
                "planning branch HEAD"
            ),
        )
        worktree_add.extend((str(planning_worktree), planning_branch))
    else:
        worktree_add.extend(("-b", planning_branch, str(planning_worktree), start_head))
    worktree_root.mkdir(parents=True, exist_ok=True)
    git(repo_root, *worktree_add, read_only=False)
    planning_worktree = planning_worktree.resolve()
    revalidate_before_runtime_publication(
        default_checkout,
        planning_worktree,
        default_branch=args.default_branch,
        planning_branch=planning_branch,
        expected_common_dir=common_dir,
        default_head=start_head,
        default_status=start_status,
        created=True,
    )
    state_payload = runtime_payload(
        epic_id=args.epic_id,
        planning_branch=planning_branch,
        planning_base_sha=start_head,
        default_checkout=default_checkout,
        worktree_root=worktree_root,
        planning_worktree=planning_worktree,
        start_status=start_status,
    )
    create_json_atomically(state_path, state_payload)
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
