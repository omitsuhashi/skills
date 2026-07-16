"""Stable internal contract for read-only task provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol


ADAPTER_CONTRACT_VERSION = 1


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

