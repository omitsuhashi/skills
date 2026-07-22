"""Stable internal contract for read-only task provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


ADAPTER_CONTRACT_VERSION = 2


class AdapterError(Exception):
    """Safe, typed adapter failure whose message never includes provider data."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AdapterTaskSnapshotResult:
    adapter_contract_version: int
    items: List[Dict[str, Any]]


class ReadAdapter(Protocol):
    def query(self, request: Any, **kwargs: Any) -> AdapterTaskSnapshotResult:
        """Return canonical snapshot candidates for one resolved request."""


class TaskBackendAdapter(Protocol):
    """Version-2 adapter seam; provider-specific CRUD is intentionally absent."""

    def query(self, request: Any, **kwargs: Any) -> Any:
        """Return backend-neutral task snapshots."""

    def preflight(self, operation: Any, **kwargs: Any) -> Any:
        """Return safe readiness, side effects, and approval hints."""

    def apply(self, operation: Any, **kwargs: Any) -> Any:
        """Apply one already preflighted backend-neutral operation."""
