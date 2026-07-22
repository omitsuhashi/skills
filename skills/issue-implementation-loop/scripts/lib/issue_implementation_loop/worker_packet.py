from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approved_spec_binding import (
    BindingError,
    load_verified_input_packet,
)
from .identifiers import is_lower_kebab


DEFAULT_PACKET_WORDS = 450
HARD_PACKET_WORDS = 800
MAX_READ_PATHS = 8
MAX_INLINE_EXCERPT_WORDS_PER_FILE = 120
MAX_INLINE_EXCERPT_WORDS_TOTAL = 300
PACKET_CONTEXT_BUDGET_EXCEEDED = "PACKET_CONTEXT_BUDGET_EXCEEDED"

WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*|[^\W\s_]+", re.UNICODE)
TASK_KINDS = {"implement", "fix", "review", "inspect"}
ACCESS_MODES = {"read_write", "read_only"}


@dataclass(frozen=True)
class TrustedWorkerContext:
    repo_root: Path
    assigned_worktree: Path
    envelope_path: Path
    runtime_state_path: Path
    envelope: dict[str, Any]
    runtime_state: dict[str, Any]
    approved_packet: dict[str, Any]
    approved_item: dict[str, Any]
    envelope_item: dict[str, Any]
    issue_source: Path


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def packet_word_count(value: Any) -> int:
    if isinstance(value, str):
        return count_words(value)
    if isinstance(value, list):
        return sum(packet_word_count(item) for item in value)
    if isinstance(value, dict):
        return sum(packet_word_count(item) for item in value.values())
    return 0


def worker_packet_context_policy(max_packet_words: int = DEFAULT_PACKET_WORDS) -> dict[str, Any]:
    return {
        "paths_first": True,
        "max_packet_words": max_packet_words,
        "hard_max_packet_words": HARD_PACKET_WORDS,
        "max_read_paths": MAX_READ_PATHS,
        "max_inline_excerpt_words_per_file": MAX_INLINE_EXCERPT_WORDS_PER_FILE,
        "max_inline_excerpt_words_total": MAX_INLINE_EXCERPT_WORDS_TOTAL,
        "include_full_spec_text": False,
        "include_full_ledger_text": False,
    }


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def source_revision_record(
    *,
    envelope_path: str | Path,
    runtime_path: str | Path,
    issue_source_path: str | Path,
) -> dict[str, Any]:
    envelope_file = Path(envelope_path).resolve(strict=False)
    runtime_file = Path(runtime_path).resolve(strict=False)
    issue_source_file = Path(issue_source_path).resolve(strict=False)
    envelope = _load_json(envelope_file)
    runtime = _load_json(runtime_file)
    return {
        "approved_spec_binding": envelope.get("approved_spec_binding"),
        "execution_envelope": {
            "path": str(envelope_file),
            "revision": envelope.get("revision"),
            "sha256": file_sha256(envelope_file),
        },
        "runtime_state": {
            "path": str(runtime_file),
            "envelope_revision": runtime.get("envelope_revision"),
            "sha256": file_sha256(runtime_file),
        },
        "issue_source": {
            "path": str(issue_source_file),
            "sha256": file_sha256(issue_source_file),
        },
    }


def _canonical_existing_path(
    raw_path: str | Path,
    *,
    directory: bool,
) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        raise ValueError("BINDING_MISMATCH")
    try:
        canonical = candidate.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        raise ValueError("BINDING_MISMATCH") from None
    if directory and not canonical.is_dir():
        raise ValueError("BINDING_MISMATCH")
    if not directory and not canonical.is_file():
        raise ValueError("BINDING_MISMATCH")
    return canonical


def _contains(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath([str(root), str(candidate)]) == str(root)
    except ValueError:
        return False


def _trusted_git_common_directory(repo_root: Path) -> Path:
    environment = os.environ.copy()
    for variable in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    ):
        environment.pop(variable, None)
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--git-common-dir"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
    except (OSError, TypeError, ValueError):
        raise ValueError("BINDING_MISMATCH") from None
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 1 or not lines[0].strip():
        raise ValueError("BINDING_MISMATCH")
    common_directory = Path(lines[0].strip())
    if not common_directory.is_absolute():
        common_directory = repo_root / common_directory
    try:
        canonical = common_directory.resolve(strict=True)
    except OSError:
        raise ValueError("BINDING_MISMATCH") from None
    if not canonical.is_dir():
        raise ValueError("BINDING_MISMATCH")
    return canonical


def _runtime_file_location(
    common_directory: Path,
    raw_path: str | Path,
    *,
    expected_name: str,
) -> tuple[Path, tuple[str, ...], str]:
    try:
        supplied = Path(raw_path)
        if not supplied.is_absolute() or ".." in supplied.parts:
            raise ValueError
        candidate = Path(os.path.abspath(os.fspath(supplied)))
        relative = candidate.relative_to(common_directory)
    except (OSError, TypeError, ValueError):
        raise ValueError("BINDING_MISMATCH") from None
    parts = relative.parts
    if (
        len(parts) != 4
        or parts[:2] != ("agent-runs", "issue-implementation-loop")
        or not is_lower_kebab(parts[2])
        or parts[3] != expected_name
    ):
        raise ValueError("BINDING_MISMATCH")
    return candidate, parts, parts[2]


def _load_trusted_runtime_json(
    common_directory: Path,
    raw_path: str | Path,
    *,
    expected_name: str,
) -> tuple[Path, str, Any]:
    candidate, parts, path_epic_id = _runtime_file_location(
        common_directory,
        raw_path,
        expected_name=expected_name,
    )
    if not hasattr(os, "O_NOFOLLOW"):
        raise ValueError("BINDING_MISMATCH")
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, "O_DIRECTORY"):
        directory_flags |= os.O_DIRECTORY
    file_flags = os.O_RDONLY | os.O_NOFOLLOW
    descriptors: list[int] = []
    try:
        descriptors.append(os.open(common_directory, directory_flags))
        for part in parts[:-1]:
            descriptors.append(
                os.open(part, directory_flags, dir_fd=descriptors[-1])
            )
        file_descriptor = os.open(
            parts[-1], file_flags, dir_fd=descriptors[-1]
        )
        descriptors.append(file_descriptor)
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError
        chunks: list[bytes] = []
        while True:
            chunk = os.read(file_descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(file_descriptor)
        if (
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        ):
            raise ValueError
        value = json.loads(b"".join(chunks).decode("utf-8"))
    except (OSError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("BINDING_MISMATCH") from None
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
    return candidate, path_epic_id, value


def trusted_worker_context(
    *,
    repo_root: str | Path,
    assigned_worktree: str | Path,
    envelope_path: str | Path,
    runtime_state_path: str | Path,
    issue_id: str,
) -> TrustedWorkerContext:
    from .validation.execution_envelope import validate_execution_envelope
    from .validation.runtime_state import validate_runtime_epoch, validate_runtime_state

    canonical_repo = _canonical_existing_path(repo_root, directory=True)
    canonical_worktree = _canonical_existing_path(assigned_worktree, directory=True)
    common_directory = _trusted_git_common_directory(canonical_repo)
    canonical_envelope, envelope_path_epic, envelope = _load_trusted_runtime_json(
        common_directory,
        envelope_path,
        expected_name="execution-envelope.json",
    )
    canonical_runtime, runtime_path_epic, runtime = _load_trusted_runtime_json(
        common_directory,
        runtime_state_path,
        expected_name="runtime-state.json",
    )
    if not isinstance(envelope, dict) or not isinstance(runtime, dict):
        raise ValueError("BINDING_MISMATCH")
    if (
        envelope_path_epic != runtime_path_epic
        or envelope.get("epic_id") != envelope_path_epic
        or runtime.get("epic_id") != envelope_path_epic
    ):
        raise ValueError("BINDING_MISMATCH")
    envelope_errors = validate_execution_envelope(envelope, canonical_repo)
    binding = envelope.get("approved_spec_binding")
    if runtime.get("approved_spec_binding") != binding:
        raise ValueError("BINDING_MISMATCH")
    if runtime.get("envelope_revision") != envelope.get("revision"):
        raise ValueError("BINDING_MISMATCH")
    try:
        packet = load_verified_input_packet(
            canonical_worktree,
            binding,
            ancestor_ref="HEAD",
            projection_errors=True,
        )
    except BindingError as error:
        raise ValueError(error.code) from None
    if envelope_errors:
        raise ValueError(envelope_errors[0])
    runtime_errors = validate_runtime_state(runtime)
    if runtime_errors:
        raise ValueError(runtime_errors[0])
    epoch_errors = validate_runtime_epoch(envelope, runtime)
    if epoch_errors:
        raise ValueError("BINDING_MISMATCH")
    approved = next(
        (
            item
            for item in packet["work_items"]
            if isinstance(item, dict) and item.get("id") == issue_id
        ),
        None,
    )
    envelope_item = envelope.get("work_items", {}).get(issue_id)
    if not isinstance(approved, dict) or not isinstance(envelope_item, dict):
        raise ValueError("BINDING_MISMATCH")
    assigned_by_envelope = envelope_item.get("worktree_path")
    if not isinstance(assigned_by_envelope, str):
        raise ValueError("BINDING_MISMATCH")
    try:
        canonical_assigned = Path(assigned_by_envelope).resolve(strict=True)
    except OSError:
        raise ValueError("BINDING_MISMATCH") from None
    if canonical_assigned != canonical_worktree:
        raise ValueError("BINDING_MISMATCH")
    try:
        issue_source = (
            canonical_worktree / approved["source"]["path"]
        ).resolve(strict=True)
    except (KeyError, OSError, TypeError):
        raise ValueError("BINDING_MISMATCH") from None
    if not issue_source.is_file() or not _contains(canonical_worktree, issue_source):
        raise ValueError("BINDING_MISMATCH")
    return TrustedWorkerContext(
        repo_root=canonical_repo,
        assigned_worktree=canonical_worktree,
        envelope_path=canonical_envelope,
        runtime_state_path=canonical_runtime,
        envelope=envelope,
        runtime_state=runtime,
        approved_packet=packet,
        approved_item=approved,
        envelope_item=envelope_item,
        issue_source=issue_source,
    )


def read_path_record(path: str, purpose: str = "source") -> dict[str, str]:
    return {"path": path, "purpose": purpose}


def inline_excerpt_record(raw: str) -> dict[str, str]:
    path, separator, excerpt = raw.partition("::")
    if not separator or not path.strip() or not excerpt.strip():
        raise ValueError("inline excerpt must use PATH::EXCERPT")
    return {"path": path.strip(), "excerpt": excerpt.strip()}


def build_worker_packet(
    *,
    issue_id: str,
    dispatch_id: str,
    repo_root: str,
    assigned_worktree: str,
    envelope_path: str,
    runtime_state_path: str,
    read_paths: list[str],
    read_purposes: list[str] | None = None,
    inline_excerpts: list[str],
    max_packet_words: int = DEFAULT_PACKET_WORDS,
    task_kind: str = "implement",
) -> dict[str, Any]:
    if read_purposes is None:
        read_purposes = ["source"] * len(read_paths)
    if len(read_purposes) != len(read_paths):
        raise ValueError("--read-purpose must be provided once per --read-path")

    if task_kind not in TASK_KINDS:
        raise ValueError(f"task_kind must be one of {sorted(TASK_KINDS)}")
    trusted = trusted_worker_context(
        repo_root=repo_root,
        assigned_worktree=assigned_worktree,
        envelope_path=envelope_path,
        runtime_state_path=runtime_state_path,
        issue_id=issue_id,
    )
    envelope = trusted.envelope
    approved = trusted.approved_item
    read_only = task_kind in {"review", "inspect"}
    access_mode = "read_only" if read_only else "read_write"
    write_scope = [] if read_only else list(approved["write_scope"])

    packet: dict[str, Any] = {
        "schema_version": 3,
        "packet_type": "issue_worker_dispatch",
        "epic_id": envelope["epic_id"],
        "issue_id": issue_id,
        "issue_title": approved["title"],
        "dispatch_id": dispatch_id,
        "branch": trusted.envelope_item["branch"],
        "worktree": str(trusted.assigned_worktree),
        "write_scope": write_scope,
        "context_policy": worker_packet_context_policy(max_packet_words),
        "read_paths": [
            read_path_record(path, purpose)
            for path, purpose in zip(read_paths, read_purposes)
        ],
        "inline_context": [inline_excerpt_record(excerpt) for excerpt in inline_excerpts],
        "task": {
            "summary": approved["title"],
            "acceptance_criteria": list(approved["acceptance_criteria"]),
            "verification": list(approved["verification"]),
            "stop_conditions": list(approved["non_goals"]),
        },
        "report_contract": {
            "format": "worker-report.json",
            "validator": "skills/issue-implementation-loop/scripts/validate_worker_report.py",
        },
    }
    packet["task_kind"] = task_kind
    packet["access_mode"] = access_mode
    packet["source_revision"] = source_revision_record(
        envelope_path=trusted.envelope_path,
        runtime_path=trusted.runtime_state_path,
        issue_source_path=trusted.issue_source,
    )
    return packet
