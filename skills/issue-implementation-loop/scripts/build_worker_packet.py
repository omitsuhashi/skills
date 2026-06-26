#!/usr/bin/env python3
"""Build a bounded issue-implementation-loop worker dispatch packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop import build_worker_packet, dump_json, validate_worker_packet  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epic-id", required=True)
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--issue-title", required=True)
    parser.add_argument("--dispatch-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--schema-version", type=int, choices=(1, 2), default=2)
    parser.add_argument("--task-kind", choices=("implement", "fix", "review", "inspect"), default="implement")
    parser.add_argument("--access-mode", choices=("read_write", "read_only"), default="read_write")
    parser.add_argument("--write-scope", action="append", default=[])
    parser.add_argument("--read-path", action="append", required=True)
    parser.add_argument("--read-purpose", action="append")
    parser.add_argument("--source-envelope")
    parser.add_argument("--source-runtime")
    parser.add_argument("--source-issue")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--acceptance", action="append", required=True)
    parser.add_argument("--verification", action="append", required=True)
    parser.add_argument("--stop-condition", action="append", required=True)
    parser.add_argument("--inline-excerpt", action="append", default=[])
    parser.add_argument("--max-packet-words", type=int, default=450)
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        packet = build_worker_packet(
            epic_id=args.epic_id,
            issue_id=args.issue_id,
            issue_title=args.issue_title,
            dispatch_id=args.dispatch_id,
            branch=args.branch,
            worktree=args.worktree,
            write_scope=args.write_scope,
            read_paths=args.read_path,
            read_purposes=args.read_purpose,
            summary=args.summary,
            acceptance=args.acceptance,
            verification=args.verification,
            stop_conditions=args.stop_condition,
            inline_excerpts=args.inline_excerpt,
            max_packet_words=args.max_packet_words,
            schema_version=args.schema_version,
            task_kind=args.task_kind,
            access_mode=args.access_mode,
            source_envelope=args.source_envelope,
            source_runtime=args.source_runtime,
            source_issue=args.source_issue,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate_worker_packet(packet)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    text = dump_json(packet)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"WORKER PACKET WRITTEN: {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
