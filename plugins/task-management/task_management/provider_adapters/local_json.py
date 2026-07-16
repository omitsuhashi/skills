"""Read a versioned bootstrap task snapshot from a host-fixed local file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from . import ADAPTER_CONTRACT_VERSION, AdapterError, AdapterTaskSnapshotResult
from ..route_config import ResolvedTaskReadRequest


MAX_SNAPSHOT_BYTES = 5 * 1024 * 1024


class LocalJsonAdapter:
    def __init__(self, *, read_root: Path, source_path: Path):
        self._read_root = read_root.resolve()
        self._source_path = source_path.resolve()
        try:
            self._source_path.relative_to(self._read_root)
        except ValueError:
            raise AdapterError("invalid_read_route", "Local snapshot source is outside its read root.")

    def query(self, request: ResolvedTaskReadRequest, **_kwargs: Any) -> AdapterTaskSnapshotResult:
        try:
            if not self._source_path.is_file():
                raise OSError("not a regular file")
            if self._source_path.stat().st_size > MAX_SNAPSHOT_BYTES:
                raise OSError("snapshot is too large")
            document = json.loads(self._source_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            raise AdapterError("task_source_unreadable", "Local task snapshot is unavailable or invalid.")
        if not isinstance(document, dict) or document.get("adapter_contract_version") != ADAPTER_CONTRACT_VERSION:
            raise AdapterError("adapter_contract_mismatch", "Local task snapshot contract version is unsupported.")
        items = document.get("items")
        if not isinstance(items, list):
            raise AdapterError("invalid_adapter_result", "Local task snapshot must contain an items array.")

        filtered = [item for item in items if self._matches(item, request.query)]
        limit = request.query.get("limit", 100)
        return AdapterTaskSnapshotResult(ADAPTER_CONTRACT_VERSION, filtered[:limit])

    @staticmethod
    def _matches(item: Any, query: Dict[str, Any]) -> bool:
        if not isinstance(item, dict):
            return True  # The facade owns final shape validation and will fail closed.
        for field in ("work_unit_id", "task_type", "status"):
            if field in query and item.get(field) != query[field]:
                return False
        due_before = query.get("due_before")
        if due_before is not None:
            due_date = item.get("due_date")
            if due_date is None or not isinstance(due_date, str) or due_date > due_before:
                return False
        return True

