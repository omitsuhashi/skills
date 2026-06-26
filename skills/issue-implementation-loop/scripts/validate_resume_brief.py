#!/usr/bin/env python3
"""Validate an issue-implementation-loop resume brief cache and V2 metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop import dump_json, validate_resume_brief_cache  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime_root", help="Runtime root containing resume-brief.md")
    parser.add_argument("--meta", help="Optional explicit resume-brief.meta.json path")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    errors, warnings = validate_resume_brief_cache(args.runtime_root, meta_path=args.meta)
    if args.json:
        print(dump_json({"ok": not errors, "errors": errors, "warnings": warnings}), end="")
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        if warnings:
            print("; ".join(warnings))
        else:
            print("RESUME BRIEF OK")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
