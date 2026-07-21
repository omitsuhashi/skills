#!/usr/bin/env python3
"""Rebuild runtime-state JSON from an events.jsonl stream."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import dump_json
from issue_implementation_loop.runtime_state import EventFoldError, rebuild_state_from_events


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_jsonl")
    args = parser.parse_args()

    try:
        state, _warnings = rebuild_state_from_events(Path(args.events_jsonl))
    except (EventFoldError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(dump_json(state), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
