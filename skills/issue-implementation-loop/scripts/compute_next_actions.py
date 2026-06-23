#!/usr/bin/env python3
"""Compute runnable/reviewable/fixable issues from an envelope and runtime state."""

from __future__ import annotations

import argparse
import sys

from _common import (
    compute_next_actions,
    dump_json,
    load_json,
    validate_execution_envelope,
    validate_runtime_state,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope")
    parser.add_argument("runtime_state")
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    runtime = load_json(args.runtime_state)
    errors = validate_execution_envelope(envelope) + validate_runtime_state(runtime)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(dump_json(compute_next_actions(envelope, runtime)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
