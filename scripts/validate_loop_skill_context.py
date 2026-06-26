#!/usr/bin/env python3
"""Compatibility wrapper for validating loop-skill context contracts."""

from __future__ import annotations

from typing import Sequence

from skill_context.contract import (
    ContractError,
    REPO_ROOT,
    all_skill_dirs,
    inspect_operation,
    load_contract,
    operation_read_set,
    parse_contract_text,
    validate_contract,
    validate_reference_path,
    validate_skill_dir,
)
from validate_skill_context import run_validation


def main(argv: Sequence[str] | None = None) -> int:
    return run_validation(argv, success_label="loop skill context")


if __name__ == "__main__":
    raise SystemExit(main())
