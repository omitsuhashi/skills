from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import inspect
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import stat
import subprocess
from typing import Any, Mapping

from .constants import DELIVERY_INTENTS
from .identifiers import is_issue_id, is_lower_kebab


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d"
    r"(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$"
)
APPROVAL_SCOPE_FIELDS = frozenset(
    {
        "accepted_decisions",
        "non_goals",
        "acceptance_criteria",
        "verification",
        "remote_policy",
        "stop_conditions",
    }
)
PACKET_FIELDS = frozenset(
    {
        "schema_version",
        "epic_id",
        "artifact_root",
        "spec_binding",
        "approval_evidence",
        "work_items",
        "delivery_intent",
    }
)
WORK_ITEM_FIELDS = frozenset(
    {
        "id",
        "title",
        "source",
        "acceptance_criteria",
        "non_goals",
        "verification",
        "write_scope",
        "dependencies",
    }
)
APPROVAL_FIELDS = frozenset(
    {"decision", "subject", "actor_expression", "approved_at", "scope"}
)


DEFAULT_ACTIONS = {
    "SPEC_MISSING": "return_to_spec_gate",
    "APPROVAL_MISSING": "return_to_spec_gate",
    "APPROVAL_NOT_APPROVED": "return_to_spec_gate",
    "APPROVAL_SCOPE_INCOMPLETE": "return_to_spec_gate",
    "DIGEST_MISSING": "return_to_spec_gate",
    "DIGEST_MALFORMED": "return_to_spec_gate",
    "SPEC_DIGEST_MISMATCH": "return_to_spec_gate",
    "INPUT_PACKET_DIGEST_MISMATCH": "return_to_execution_plan_gate",
    "BINDING_MISMATCH": "return_to_execution_plan_gate",
    "PROJECTION_MISSING": "return_to_execution_plan_gate",
    "PROJECTION_MISMATCH": "return_to_execution_plan_gate",
    "GATE_COMMIT_MISSING": "return_to_execution_plan_gate",
    "GATE_COMMIT_NOT_ANCESTOR": "return_to_execution_plan_gate",
    "GATE_COMMIT_BLOB_MISMATCH": "return_to_execution_plan_gate",
    "AUXILIARY_ARTIFACT_BINDING_MISMATCH": "regenerate_for_active_binding",
    "PATH_ABSOLUTE": "regenerate_artifact",
    "PATH_TRAVERSAL": "regenerate_artifact",
    "PATH_OUTSIDE_REPO": "regenerate_artifact",
    "PATH_SYMLINK": "regenerate_artifact",
    "PATH_NOT_REGULAR_FILE": "regenerate_artifact",
    "FILE_CHANGED_DURING_VALIDATION": "retry_validation",
    "SCHEMA_UNSUPPORTED": "create_new_run",
    "REAPPROVAL_REQUIRED": "return_to_spec_gate",
    "PLATFORM_UNSUPPORTED": "use_supported_host",
}


class BindingError(Exception):
    """Stable, non-sensitive failure returned by binding operations."""

    def __init__(
        self,
        code: str,
        *,
        action: str | None = None,
        path: str | None = None,
        recovery_path: str | None = None,
        missing_capabilities: tuple[str, ...] = (),
    ) -> None:
        self.code = code
        self.action = action or DEFAULT_ACTIONS[code]
        self.path = path
        self.recovery_path = recovery_path
        self.missing_capabilities = missing_capabilities
        super().__init__(code)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "valid": False,
            "code": self.code,
            "action": self.action,
        }
        if self.path is not None:
            result["path"] = self.path
        if self.recovery_path is not None:
            result["recovery_path"] = self.recovery_path
        if self.missing_capabilities:
            result["missing_capabilities"] = list(self.missing_capabilities)
        return result


@dataclass(frozen=True)
class SealCapabilities:
    supported: bool
    missing: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"supported": self.supported, "missing": list(self.missing)}


@dataclass(frozen=True)
class SpecRevision:
    path: str
    sha256: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "sha256": self.sha256}


@dataclass(frozen=True)
class InputPacketRef:
    path: str
    sha256: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "sha256": self.sha256}


@dataclass(frozen=True)
class ApprovedSpecBindingRef:
    path: str
    sha256: str
    gate_commit: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "gate_commit": self.gate_commit,
        }


@dataclass(frozen=True)
class VerifiedBinding:
    spec_revision: SpecRevision
    input_packet: InputPacketRef
    valid: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "spec_revision": self.spec_revision.to_dict(),
            "input_packet": self.input_packet.to_dict(),
        }


def _trusted_repo_root(repo_root: str | os.PathLike[str]) -> Path:
    try:
        candidate = Path(repo_root)
        if not candidate.is_absolute():
            raise BindingError("PATH_OUTSIDE_REPO")
        canonical = candidate.resolve(strict=True)
    except BindingError:
        raise
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None
    try:
        if not canonical.is_dir():
            raise BindingError("PATH_OUTSIDE_REPO")
    except BindingError:
        raise
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None
    try:
        result = subprocess.run(
            ["git", "-C", str(canonical), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if result.returncode != 0:
        raise BindingError("PATH_OUTSIDE_REPO")
    try:
        git_root = Path(result.stdout.strip()).resolve(strict=True)
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if git_root != canonical:
        raise BindingError("PATH_OUTSIDE_REPO")
    return canonical


def trusted_argument_path(
    repo_root: str | os.PathLike[str], path: str | os.PathLike[str]
) -> str:
    """Convert a trusted CLI path argument to a safe repository-relative path."""

    root = _trusted_repo_root(repo_root)
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            return _parse_repo_path(os.fspath(path))
        return candidate.resolve(strict=False).relative_to(root).as_posix()
    except BindingError:
        raise
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None


def discover_repo_root(start: str | os.PathLike[str]) -> Path:
    try:
        rendered = os.fspath(start)
        result = subprocess.run(
            ["git", "-C", rendered, "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except (OSError, TypeError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if result.returncode != 0:
        raise BindingError("PATH_OUTSIDE_REPO")
    return _trusted_repo_root(result.stdout.strip())


def _parse_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise BindingError("PATH_TRAVERSAL")
    if value.startswith("/") or value.startswith("~"):
        raise BindingError("PATH_ABSOLUTE", path=value)
    if "\x00" in value or "\\" in value or "//" in value or value.endswith("/"):
        raise BindingError("PATH_TRAVERSAL", path=value)
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise BindingError("PATH_TRAVERSAL", path=value)
    path = PurePosixPath(value)
    if path.is_absolute():
        raise BindingError("PATH_ABSOLUTE", path=value)
    return path.as_posix()


def _identity(value: os.stat_result) -> tuple[int, int, int, int]:
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)


def _node_identity(value: os.stat_result) -> tuple[int, int]:
    return (value.st_dev, value.st_ino)


def _read_regular_file(
    root: Path,
    repo_path: str,
    *,
    missing_code: str,
) -> tuple[bytes, str]:
    safe_path = _parse_repo_path(repo_path)
    current = root
    parts = safe_path.split("/")
    before_path: os.stat_result | None = None
    component_identities: list[tuple[Path, tuple[int, int, int, int]]] = []
    for index, part in enumerate(parts):
        current = current / part
        try:
            component = os.lstat(current)
        except FileNotFoundError:
            raise BindingError(missing_code, path=safe_path) from None
        except OSError:
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path) from None
        if stat.S_ISLNK(component.st_mode):
            raise BindingError("PATH_SYMLINK", path=safe_path)
        if index < len(parts) - 1 and not stat.S_ISDIR(component.st_mode):
            raise BindingError("PATH_NOT_REGULAR_FILE", path=safe_path)
        component_identities.append((current, _identity(component)))
        before_path = component
    assert before_path is not None
    if not stat.S_ISREG(before_path.st_mode):
        raise BindingError("PATH_NOT_REGULAR_FILE", path=safe_path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(current, flags)
    except FileNotFoundError:
        raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path) from None
    except OSError:
        raise BindingError("PATH_SYMLINK", path=safe_path) from None
    try:
        before_fd = os.fstat(descriptor)
        if not stat.S_ISREG(before_fd.st_mode):
            raise BindingError("PATH_NOT_REGULAR_FILE", path=safe_path)
        if _identity(before_fd) != _identity(before_path):
            raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path)
        digest = hashlib.sha256()
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            chunks.append(chunk)
        after_fd = os.fstat(descriptor)
        try:
            after_path = os.lstat(current)
        except OSError:
            raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path) from None
        for component_path, before_identity in component_identities:
            try:
                after_component = os.lstat(component_path)
            except OSError:
                raise BindingError(
                    "FILE_CHANGED_DURING_VALIDATION", path=safe_path
                ) from None
            if stat.S_ISLNK(after_component.st_mode) or _identity(after_component) != before_identity:
                raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path)
        if (
            stat.S_ISLNK(after_path.st_mode)
            or _identity(before_fd) != _identity(after_fd)
            or _identity(after_fd) != _identity(after_path)
        ):
            raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path)
        return b"".join(chunks), digest.hexdigest()
    except BindingError:
        raise
    except (OSError, ValueError):
        raise BindingError(
            "FILE_CHANGED_DURING_VALIDATION", path=safe_path
        ) from None
    finally:
        try:
            os.close(descriptor)
        except OSError:
            pass


def _digest(value: Any, *, action: str = "return_to_spec_gate") -> str:
    if value is None or value == "":
        raise BindingError("DIGEST_MISSING", action=action)
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise BindingError("DIGEST_MALFORMED", action=action)
    return value


def _coerce_spec_revision(value: SpecRevision | Mapping[str, Any]) -> SpecRevision:
    if isinstance(value, SpecRevision):
        return SpecRevision(_parse_repo_path(value.path), _digest(value.sha256))
    if not isinstance(value, Mapping):
        raise BindingError("DIGEST_MISSING")
    return SpecRevision(
        _parse_repo_path(value.get("path")),
        _digest(value.get("sha256")),
    )


def _validate_approval(value: Any) -> dict[str, Any]:
    if value is None:
        raise BindingError("APPROVAL_MISSING")
    if not isinstance(value, dict):
        raise BindingError("APPROVAL_MISSING")
    if value.get("decision") != "approved":
        raise BindingError("APPROVAL_NOT_APPROVED")
    scope = value.get("scope")
    if not isinstance(scope, dict) or any(scope.get(field) is not True for field in APPROVAL_SCOPE_FIELDS):
        raise BindingError("APPROVAL_SCOPE_INCOMPLETE")
    if set(scope) != APPROVAL_SCOPE_FIELDS:
        raise BindingError("SCHEMA_UNSUPPORTED")
    if set(value) != APPROVAL_FIELDS or value.get("subject") != "spec_binding":
        raise BindingError("SCHEMA_UNSUPPORTED")
    actor = value.get("actor_expression")
    timestamp = value.get("approved_at")
    if (
        not isinstance(actor, str)
        or not actor.strip()
        or not isinstance(timestamp, str)
        or not RFC3339_RE.fullmatch(timestamp)
    ):
        raise BindingError("SCHEMA_UNSUPPORTED")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise BindingError("SCHEMA_UNSUPPORTED") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise BindingError("SCHEMA_UNSUPPORTED")
    return value


def _nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _validate_packet_shape(packet: Any) -> dict[str, Any]:
    if not isinstance(packet, dict) or packet.get("schema_version") != 2:
        raise BindingError("SCHEMA_UNSUPPORTED")
    if "approval_evidence" not in packet:
        raise BindingError("APPROVAL_MISSING")
    _validate_approval(packet["approval_evidence"])
    binding = packet.get("spec_binding")
    if not isinstance(binding, dict):
        raise BindingError("DIGEST_MISSING")
    if set(binding) != {"path", "sha256"}:
        if "sha256" not in binding:
            raise BindingError("DIGEST_MISSING")
        raise BindingError("SCHEMA_UNSUPPORTED")
    _parse_repo_path(binding.get("path"))
    _digest(binding.get("sha256"))
    if set(packet) != PACKET_FIELDS:
        raise BindingError("SCHEMA_UNSUPPORTED")
    if not isinstance(packet.get("epic_id"), str) or not is_lower_kebab(packet["epic_id"]):
        raise BindingError("SCHEMA_UNSUPPORTED")
    _parse_repo_path(packet.get("artifact_root"))
    if packet.get("delivery_intent") not in DELIVERY_INTENTS:
        raise BindingError("SCHEMA_UNSUPPORTED")
    work_items = packet.get("work_items")
    if not isinstance(work_items, list) or not work_items:
        raise BindingError("SCHEMA_UNSUPPORTED")
    ids = {
        item.get("id")
        for item in work_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    if len(ids) != len(work_items):
        raise BindingError("SCHEMA_UNSUPPORTED")
    for item in work_items:
        if not isinstance(item, dict) or set(item) != WORK_ITEM_FIELDS:
            raise BindingError("SCHEMA_UNSUPPORTED")
        if not is_issue_id(item.get("id")):
            raise BindingError("SCHEMA_UNSUPPORTED")
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise BindingError("SCHEMA_UNSUPPORTED")
        source = item.get("source")
        if not isinstance(source, dict) or set(source) != {"type", "path"} or source.get("type") != "local":
            raise BindingError("SCHEMA_UNSUPPORTED")
        _parse_repo_path(source.get("path"))
        for field in ("acceptance_criteria", "non_goals", "verification", "write_scope"):
            if not _nonempty_string_list(item.get(field)):
                raise BindingError("SCHEMA_UNSUPPORTED")
        for scope in item["write_scope"]:
            if not scope.startswith("path:"):
                raise BindingError("SCHEMA_UNSUPPORTED")
            _parse_repo_path(scope[5:])
        dependencies = item.get("dependencies")
        if not isinstance(dependencies, list) or any(
            not isinstance(dependency, str) or dependency not in ids for dependency in dependencies
        ):
            raise BindingError("SCHEMA_UNSUPPORTED")
    return packet


def _packet_from_bytes(raw: bytes) -> dict[str, Any]:
    try:
        packet = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BindingError("SCHEMA_UNSUPPORTED") from None
    return _validate_packet_shape(packet)


def _validate_directory(root: Path, repo_path: str) -> None:
    safe_path = _parse_repo_path(repo_path)
    current = root
    for part in safe_path.split("/"):
        current = current / part
        try:
            component = os.lstat(current)
        except OSError:
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path) from None
        if stat.S_ISLNK(component.st_mode):
            raise BindingError("PATH_SYMLINK", path=safe_path)
        if not stat.S_ISDIR(component.st_mode):
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path)


def _validate_existing_components(root: Path, repo_path: str) -> None:
    safe_path = _parse_repo_path(repo_path)
    current = root
    parts = safe_path.split("/")
    for index, part in enumerate(parts):
        current = current / part
        try:
            component = os.lstat(current)
        except FileNotFoundError:
            return
        except OSError:
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path) from None
        if stat.S_ISLNK(component.st_mode):
            raise BindingError("PATH_SYMLINK", path=safe_path)
        if index < len(parts) - 1 and not stat.S_ISDIR(component.st_mode):
            raise BindingError("PATH_NOT_REGULAR_FILE", path=safe_path)


def _validate_packet_files(root: Path, packet: Mapping[str, Any]) -> None:
    _validate_directory(root, packet["artifact_root"])
    source_paths = {item["source"]["path"] for item in packet["work_items"]}
    for source_path in sorted(source_paths):
        _read_regular_file(root, source_path, missing_code="PROJECTION_MISSING")
    write_paths = {
        scope[5:]
        for item in packet["work_items"]
        for scope in item["write_scope"]
    }
    for write_path in sorted(write_paths):
        _validate_existing_components(root, write_path)


def identify_spec(
    repo_root: str | os.PathLike[str], spec_path: str
) -> SpecRevision:
    root = _trusted_repo_root(repo_root)
    safe_path = _parse_repo_path(spec_path)
    _, digest = _read_regular_file(root, safe_path, missing_code="SPEC_MISSING")
    return SpecRevision(safe_path, digest)


def _has_keyword_parameters(function: Any, *names: str) -> bool:
    try:
        parameters = inspect.signature(function).parameters
    except (TypeError, ValueError):
        return False
    return all(name in parameters for name in names)


def probe_seal_capabilities() -> SealCapabilities:
    """Report whether this host can perform fail-closed descriptor-relative seal."""

    missing: list[str] = []
    if not hasattr(os, "O_NOFOLLOW"):
        missing.append("flag:O_NOFOLLOW")
    if not hasattr(os, "O_DIRECTORY"):
        missing.append("flag:O_DIRECTORY")
    dir_fd_support = getattr(os, "supports_dir_fd", ())
    no_follow_support = getattr(os, "supports_follow_symlinks", ())
    for name in ("open", "stat", "link", "unlink"):
        function = getattr(os, name, None)
        if function is None or function not in dir_fd_support:
            missing.append(f"dir_fd:{name}")
    for name in ("stat", "link"):
        function = getattr(os, name, None)
        if function is None or function not in no_follow_support:
            missing.append(f"no_follow:{name}")
    replace = getattr(os, "replace", None)
    if replace is None or not _has_keyword_parameters(
        replace, "src_dir_fd", "dst_dir_fd"
    ):
        missing.append("dir_fd:replace")
    ordered = tuple(sorted(missing))
    return SealCapabilities(supported=not ordered, missing=ordered)


def _require_seal_capabilities() -> None:
    capabilities = probe_seal_capabilities()
    if not capabilities.supported:
        raise BindingError(
            "PLATFORM_UNSUPPORTED",
            missing_capabilities=capabilities.missing,
        )


def _directory_flags() -> int:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return flags


def _open_directory_chain(
    root: Path, output_path: str
) -> tuple[list[int], list[tuple[Path, tuple[int, int]]], str]:
    safe_path = _parse_repo_path(output_path)
    parts = safe_path.split("/")
    descriptors: list[int] = []
    identities: list[tuple[Path, tuple[int, int]]] = []
    current_path = root
    try:
        current_fd = os.open(root, _directory_flags())
        descriptors.append(current_fd)
        identities.append((root, _node_identity(os.fstat(current_fd))))
        for part in parts[:-1]:
            current_path = current_path / part
            current_fd = os.open(
                part, _directory_flags(), dir_fd=descriptors[-1]
            )
            descriptors.append(current_fd)
            identities.append((current_path, _node_identity(os.fstat(current_fd))))
    except (OSError, TypeError, ValueError):
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=safe_path) from None
    return descriptors, identities, parts[-1]


def _verify_directory_chain(
    identities: list[tuple[Path, tuple[int, int]]], output_path: str
) -> None:
    for component_path, expected_identity in identities:
        try:
            current = os.lstat(component_path)
        except OSError:
            raise BindingError(
                "FILE_CHANGED_DURING_VALIDATION", path=output_path
            ) from None
        if (
            stat.S_ISLNK(current.st_mode)
            or _node_identity(current) != expected_identity
        ):
            raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=output_path)


def _write_all(descriptor: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        written = os.write(descriptor, raw[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written


def _atomic_replace(root: Path, output_path: str, raw: bytes) -> None:
    descriptors, identities, leaf = _open_directory_chain(root, output_path)
    parent_fd = descriptors[-1]
    temporary = f".{leaf}.{secrets.token_hex(8)}.tmp"
    backup = f".{leaf}.{secrets.token_hex(8)}.bak"
    temporary_exists = False
    backup_exists = False
    output_existed = False
    preserve_backup = False
    try:
        _verify_directory_chain(identities, output_path)
        try:
            existing = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None:
            if stat.S_ISLNK(existing.st_mode):
                raise BindingError("PATH_SYMLINK", path=output_path)
            if not stat.S_ISREG(existing.st_mode):
                raise BindingError("PATH_NOT_REGULAR_FILE", path=output_path)
            output_existed = True
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(temporary, flags, 0o644, dir_fd=parent_fd)
        temporary_exists = True
        try:
            _write_all(descriptor, raw)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _verify_directory_chain(identities, output_path)
        if output_existed:
            os.link(
                leaf,
                backup,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
            backup_exists = True
        os.replace(
            temporary,
            leaf,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
        temporary_exists = False
        try:
            _verify_directory_chain(identities, output_path)
        except BindingError:
            if output_existed:
                try:
                    os.replace(
                        backup,
                        leaf,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                    backup_exists = False
                except (OSError, TypeError, ValueError):
                    preserve_backup = True
                    recovery_path = (
                        PurePosixPath(output_path).parent / backup
                    ).as_posix()
                    raise BindingError(
                        "FILE_CHANGED_DURING_VALIDATION",
                        path=output_path,
                        recovery_path=recovery_path,
                    ) from None
            else:
                os.unlink(leaf, dir_fd=parent_fd)
            raise
        if backup_exists:
            try:
                os.unlink(backup, dir_fd=parent_fd)
                backup_exists = False
            except (OSError, TypeError, ValueError):
                try:
                    os.replace(
                        backup,
                        leaf,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                    backup_exists = False
                except (OSError, TypeError, ValueError):
                    preserve_backup = True
                    recovery_path = (
                        PurePosixPath(output_path).parent / backup
                    ).as_posix()
                    raise BindingError(
                        "FILE_CHANGED_DURING_VALIDATION",
                        path=output_path,
                        recovery_path=recovery_path,
                    ) from None
                raise BindingError(
                    "FILE_CHANGED_DURING_VALIDATION", path=output_path
                ) from None
    except BindingError:
        raise
    except (OSError, TypeError, ValueError):
        raise BindingError(
            "FILE_CHANGED_DURING_VALIDATION", path=output_path
        ) from None
    finally:
        if temporary_exists:
            try:
                os.unlink(temporary, dir_fd=parent_fd)
            except OSError:
                pass
        if backup_exists and not preserve_backup:
            try:
                os.unlink(backup, dir_fd=parent_fd)
            except OSError:
                pass
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def seal_input_packet(
    repo_root: str | os.PathLike[str],
    draft_packet_path: str,
    output_packet_path: str,
    expected_spec_revision: SpecRevision | Mapping[str, Any],
    approval: Mapping[str, Any] | None,
) -> InputPacketRef:
    _require_seal_capabilities()
    root = _trusted_repo_root(repo_root)
    expected = _coerce_spec_revision(expected_spec_revision)
    current = identify_spec(root, expected.path)
    if current.sha256 != expected.sha256:
        raise BindingError("SPEC_DIGEST_MISMATCH", path=expected.path)
    checked_approval = _validate_approval(approval)
    draft_safe = _parse_repo_path(draft_packet_path)
    output_safe = _parse_repo_path(output_packet_path)
    if output_safe in {draft_safe, expected.path}:
        raise BindingError("BINDING_MISMATCH", path=output_safe)
    raw_draft, _ = _read_regular_file(root, draft_safe, missing_code="PROJECTION_MISSING")
    try:
        draft = json.loads(raw_draft.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise BindingError("SCHEMA_UNSUPPORTED") from None
    if not isinstance(draft, dict) or "spec_binding" in draft or "approval_evidence" in draft:
        raise BindingError("SCHEMA_UNSUPPORTED")
    packet = dict(draft)
    packet["spec_binding"] = expected.to_dict()
    packet["approval_evidence"] = checked_approval
    _validate_packet_shape(packet)
    _validate_packet_files(root, packet)
    if PurePosixPath(output_safe).parent.as_posix() != packet["artifact_root"]:
        raise BindingError("PATH_OUTSIDE_REPO", path=output_safe)
    serialized = (
        json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    final_check = identify_spec(root, expected.path)
    if final_check != current:
        raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=expected.path)
    _atomic_replace(root, output_safe, serialized)
    return InputPacketRef(output_safe, hashlib.sha256(serialized).hexdigest())


def _packet_ref(value: Any) -> tuple[str, str | None]:
    if isinstance(value, InputPacketRef):
        return _parse_repo_path(value.path), _digest(
            value.sha256, action="return_to_execution_plan_gate"
        )
    if isinstance(value, str):
        _parse_repo_path(value)
        raise BindingError("DIGEST_MISSING", action="return_to_execution_plan_gate")
    if not isinstance(value, Mapping):
        raise BindingError("PROJECTION_MISSING")
    path = _parse_repo_path(value.get("path"))
    digest = value.get("sha256")
    if digest is None:
        raise BindingError("DIGEST_MISSING", action="return_to_execution_plan_gate")
    return path, _digest(digest, action="return_to_execution_plan_gate")


def approved_spec_binding_ref(value: Any) -> ApprovedSpecBindingRef:
    if not isinstance(value, Mapping):
        raise BindingError("GATE_COMMIT_MISSING")
    if "gate_commit" not in value or not value.get("gate_commit"):
        raise BindingError("GATE_COMMIT_MISSING")
    if set(value) != {"path", "sha256", "gate_commit"}:
        raise BindingError("SCHEMA_UNSUPPORTED")
    path = _parse_repo_path(value.get("path"))
    digest = _digest(
        value.get("sha256"), action="return_to_execution_plan_gate"
    )
    gate_commit = value.get("gate_commit")
    if not isinstance(gate_commit, str):
        raise BindingError("GATE_COMMIT_MISSING")
    return ApprovedSpecBindingRef(path, digest, gate_commit)


def _git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
        )
    except (OSError, TypeError, ValueError):
        raise BindingError("GATE_COMMIT_MISSING") from None


def _full_git_object_id(root: Path, value: str) -> bool:
    format_result = _git_bytes(root, "rev-parse", "--show-object-format")
    if format_result.returncode != 0:
        return False
    object_format = format_result.stdout.decode("ascii", errors="ignore").strip()
    expected_length = {"sha1": 40, "sha256": 64}.get(object_format)
    if expected_length is None or len(value) != expected_length:
        return False
    return bool(re.fullmatch(r"[0-9a-f]+", value))


def _git_blob(root: Path, commit: str, path: str) -> bytes:
    object_result = _git_bytes(root, "rev-parse", f"{commit}:{path}")
    if object_result.returncode != 0:
        raise BindingError("GATE_COMMIT_BLOB_MISMATCH", path=path)
    object_id = object_result.stdout.decode("ascii", errors="ignore").strip()
    blob_result = _git_bytes(root, "cat-file", "blob", object_id)
    if blob_result.returncode != 0:
        raise BindingError("GATE_COMMIT_BLOB_MISMATCH", path=path)
    return blob_result.stdout


def _projection_blob(root: Path, commit: str, path: str) -> bytes:
    object_result = _git_bytes(root, "rev-parse", f"{commit}:{path}")
    if object_result.returncode != 0:
        raise BindingError("PROJECTION_MISSING", path=path)
    object_id = object_result.stdout.decode("ascii", errors="ignore").strip()
    blob_result = _git_bytes(root, "cat-file", "blob", object_id)
    if blob_result.returncode != 0:
        raise BindingError("PROJECTION_MISSING", path=path)
    return blob_result.stdout


def verify_approved_spec_binding(
    repo_root: str | os.PathLike[str],
    value: Any,
    *,
    ancestor_ref: str | None = None,
    projection_errors: bool = False,
) -> VerifiedBinding:
    """Verify current packet/spec projection plus its immutable Git gate."""

    root = _trusted_repo_root(repo_root)
    binding = approved_spec_binding_ref(value)
    try:
        verified = verify_chain(
            root,
            {"input_packet": {"path": binding.path, "sha256": binding.sha256}},
        )
    except BindingError as error:
        if projection_errors and error.code in {"INPUT_PACKET_DIGEST_MISMATCH", "SPEC_DIGEST_MISMATCH"}:
            raise BindingError("PROJECTION_MISMATCH", path=error.path) from None
        if projection_errors and error.code in {"SPEC_MISSING", "PROJECTION_MISSING"}:
            raise BindingError("PROJECTION_MISSING", path=error.path) from None
        raise

    if not _full_git_object_id(root, binding.gate_commit):
        raise BindingError("GATE_COMMIT_MISSING")
    commit_result = _git_bytes(root, "cat-file", "-e", f"{binding.gate_commit}^{{commit}}")
    if commit_result.returncode != 0:
        raise BindingError("GATE_COMMIT_MISSING")
    if ancestor_ref is not None:
        ancestor_result = _git_bytes(
            root, "merge-base", "--is-ancestor", binding.gate_commit, ancestor_ref
        )
        if ancestor_result.returncode != 0:
            raise BindingError("GATE_COMMIT_NOT_ANCESTOR")

    gate_packet = _git_blob(root, binding.gate_commit, binding.path)
    if hashlib.sha256(gate_packet).hexdigest() != binding.sha256:
        raise BindingError("GATE_COMMIT_BLOB_MISMATCH", path=binding.path)
    try:
        packet = _packet_from_bytes(gate_packet)
        spec = _coerce_spec_revision(packet["spec_binding"])
    except BindingError:
        raise BindingError("GATE_COMMIT_BLOB_MISMATCH", path=binding.path) from None
    gate_spec = _git_blob(root, binding.gate_commit, spec.path)
    if hashlib.sha256(gate_spec).hexdigest() != spec.sha256:
        raise BindingError("GATE_COMMIT_BLOB_MISMATCH", path=spec.path)
    if ancestor_ref is not None:
        projected_packet = _projection_blob(root, ancestor_ref, binding.path)
        if hashlib.sha256(projected_packet).hexdigest() != binding.sha256:
            raise BindingError("PROJECTION_MISMATCH", path=binding.path)
        projected_spec = _projection_blob(root, ancestor_ref, spec.path)
        if hashlib.sha256(projected_spec).hexdigest() != spec.sha256:
            raise BindingError("PROJECTION_MISMATCH", path=spec.path)
    return verified


def load_verified_input_packet(
    repo_root: str | os.PathLike[str],
    value: Any,
    *,
    ancestor_ref: str | None = None,
    projection_errors: bool = False,
) -> dict[str, Any]:
    """Return sealed packet intent only after the full current binding verifies."""

    root = _trusted_repo_root(repo_root)
    binding = approved_spec_binding_ref(value)
    verify_approved_spec_binding(
        root,
        binding.to_dict(),
        ancestor_ref=ancestor_ref,
        projection_errors=projection_errors,
    )
    raw, digest = _read_regular_file(
        root, binding.path, missing_code="PROJECTION_MISSING"
    )
    if digest != binding.sha256:
        raise BindingError("INPUT_PACKET_DIGEST_MISMATCH", path=binding.path)
    return _packet_from_bytes(raw)


def verify_chain(
    repo_root: str | os.PathLike[str], artifact_refs: Mapping[str, Any] | InputPacketRef
) -> VerifiedBinding:
    root = _trusted_repo_root(repo_root)
    if isinstance(artifact_refs, InputPacketRef):
        ref_value: Any = artifact_refs
    elif isinstance(artifact_refs, Mapping) and "input_packet" in artifact_refs:
        ref_value = artifact_refs["input_packet"]
    else:
        ref_value = artifact_refs
    packet_path, expected_packet_digest = _packet_ref(ref_value)
    raw, packet_digest = _read_regular_file(root, packet_path, missing_code="PROJECTION_MISSING")
    if expected_packet_digest is not None and packet_digest != expected_packet_digest:
        raise BindingError("INPUT_PACKET_DIGEST_MISMATCH", path=packet_path)
    packet = _packet_from_bytes(raw)
    _validate_packet_files(root, packet)
    expected_spec = _coerce_spec_revision(packet["spec_binding"])
    current_spec = identify_spec(root, expected_spec.path)
    if current_spec.sha256 != expected_spec.sha256:
        raise BindingError("SPEC_DIGEST_MISMATCH", path=expected_spec.path)
    return VerifiedBinding(
        spec_revision=current_spec,
        input_packet=InputPacketRef(packet_path, packet_digest),
    )


def validate_input_packet(
    packet: dict[str, Any], repo_root: str | os.PathLike[str] | None = None
) -> list[str]:
    try:
        _validate_packet_shape(packet)
        root = discover_repo_root(Path.cwd()) if repo_root is None else _trusted_repo_root(repo_root)
        _validate_packet_files(root, packet)
        expected = _coerce_spec_revision(packet["spec_binding"])
        current = identify_spec(root, expected.path)
        if current.sha256 != expected.sha256:
            raise BindingError("SPEC_DIGEST_MISMATCH", path=expected.path)
    except BindingError as error:
        return [error.code]
    return []
