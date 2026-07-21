from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
from typing import Any, Mapping

from .constants import DELIVERY_INTENTS
from .identifiers import is_issue_id, is_lower_kebab


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
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
    "PATH_ABSOLUTE": "regenerate_artifact",
    "PATH_TRAVERSAL": "regenerate_artifact",
    "PATH_OUTSIDE_REPO": "regenerate_artifact",
    "PATH_SYMLINK": "regenerate_artifact",
    "PATH_NOT_REGULAR_FILE": "regenerate_artifact",
    "FILE_CHANGED_DURING_VALIDATION": "retry_validation",
    "SCHEMA_UNSUPPORTED": "create_new_run",
}


class BindingError(Exception):
    """Stable, non-sensitive failure returned by binding operations."""

    def __init__(self, code: str, *, action: str | None = None, path: str | None = None) -> None:
        self.code = code
        self.action = action or DEFAULT_ACTIONS[code]
        self.path = path
        super().__init__(code)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "valid": False,
            "code": self.code,
            "action": self.action,
        }
        if self.path is not None:
            result["path"] = self.path
        return result


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
    candidate = Path(repo_root)
    if not candidate.is_absolute():
        raise BindingError("PATH_OUTSIDE_REPO")
    try:
        canonical = candidate.resolve(strict=True)
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if not canonical.is_dir():
        raise BindingError("PATH_OUTSIDE_REPO")
    try:
        result = subprocess.run(
            ["git", "-C", str(canonical), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if result.returncode != 0:
        raise BindingError("PATH_OUTSIDE_REPO")
    try:
        git_root = Path(result.stdout.strip()).resolve(strict=True)
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if git_root != canonical:
        raise BindingError("PATH_OUTSIDE_REPO")
    return canonical


def trusted_argument_path(
    repo_root: str | os.PathLike[str], path: str | os.PathLike[str]
) -> str:
    """Convert a trusted CLI path argument to a safe repository-relative path."""

    root = _trusted_repo_root(repo_root)
    candidate = Path(path)
    if not candidate.is_absolute():
        return _parse_repo_path(os.fspath(path))
    try:
        return candidate.resolve(strict=False).relative_to(root).as_posix()
    except (OSError, ValueError):
        raise BindingError("PATH_OUTSIDE_REPO") from None


def discover_repo_root(start: str | os.PathLike[str]) -> Path:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(start), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO") from None
    if result.returncode != 0:
        raise BindingError("PATH_OUTSIDE_REPO")
    return _trusted_repo_root(result.stdout.strip())


def _parse_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise BindingError("PATH_TRAVERSAL")
    if value.startswith("/") or value.startswith("~"):
        raise BindingError("PATH_ABSOLUTE", path=value)
    if "\\" in value or "//" in value or value.endswith("/"):
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
    finally:
        os.close(descriptor)


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
    if not isinstance(actor, str) or not actor.strip() or not isinstance(timestamp, str):
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


def _validate_packet_files(root: Path, packet: Mapping[str, Any]) -> None:
    _validate_directory(root, packet["artifact_root"])
    source_paths = {item["source"]["path"] for item in packet["work_items"]}
    for source_path in sorted(source_paths):
        _read_regular_file(root, source_path, missing_code="PROJECTION_MISSING")


def identify_spec(
    repo_root: str | os.PathLike[str], spec_path: str
) -> SpecRevision:
    root = _trusted_repo_root(repo_root)
    safe_path = _parse_repo_path(spec_path)
    _, digest = _read_regular_file(root, safe_path, missing_code="SPEC_MISSING")
    return SpecRevision(safe_path, digest)


def _prepare_output(root: Path, output_path: str) -> Path:
    safe_path = _parse_repo_path(output_path)
    output = root / safe_path
    current = root
    for part in safe_path.split("/")[:-1]:
        current = current / part
        try:
            component = os.lstat(current)
        except OSError:
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path) from None
        if stat.S_ISLNK(component.st_mode):
            raise BindingError("PATH_SYMLINK", path=safe_path)
        if not stat.S_ISDIR(component.st_mode):
            raise BindingError("PATH_OUTSIDE_REPO", path=safe_path)
    try:
        existing = os.lstat(output)
    except FileNotFoundError:
        return output
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO", path=safe_path) from None
    if stat.S_ISLNK(existing.st_mode):
        raise BindingError("PATH_SYMLINK", path=safe_path)
    if not stat.S_ISREG(existing.st_mode):
        raise BindingError("PATH_NOT_REGULAR_FILE", path=safe_path)
    return output


def _atomic_replace(output: Path, raw: bytes) -> None:
    descriptor = -1
    temporary: str | None = None
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
        temporary = None
    except OSError:
        raise BindingError("PATH_OUTSIDE_REPO", path=output.name) from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def seal_input_packet(
    repo_root: str | os.PathLike[str],
    draft_packet_path: str,
    output_packet_path: str,
    expected_spec_revision: SpecRevision | Mapping[str, Any],
    approval: Mapping[str, Any] | None,
) -> InputPacketRef:
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
    output = _prepare_output(root, output_safe)
    serialized = (
        json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    final_check = identify_spec(root, expected.path)
    if final_check != current:
        raise BindingError("FILE_CHANGED_DURING_VALIDATION", path=expected.path)
    _atomic_replace(output, serialized)
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
