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
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--dispatch-id", required=True)
    parser.add_argument("--repo-root", required=True, help="Trusted coordinator repo root.")
    parser.add_argument("--assigned-worktree", required=True)
    parser.add_argument("--envelope", required=True, help="Trusted active Envelope path.")
    parser.add_argument("--runtime-state", required=True, help="Trusted active Runtime State path.")
    parser.add_argument("--task-kind", choices=("implement", "fix", "review", "inspect"), default="implement")
    parser.add_argument("--read-path", action="append", required=True)
    parser.add_argument("--read-purpose", action="append")
    parser.add_argument("--inline-excerpt", action="append", default=[])
    parser.add_argument("--max-packet-words", type=int, default=450)
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        packet = build_worker_packet(
            issue_id=args.issue_id,
            dispatch_id=args.dispatch_id,
            repo_root=args.repo_root,
            assigned_worktree=args.assigned_worktree,
            envelope_path=args.envelope,
            runtime_state_path=args.runtime_state,
            read_paths=args.read_path,
            read_purposes=args.read_purpose,
            inline_excerpts=args.inline_excerpt,
            max_packet_words=args.max_packet_words,
            task_kind=args.task_kind,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate_worker_packet(
        packet,
        repo_root=args.repo_root,
        assigned_worktree=args.assigned_worktree,
        envelope_path=args.envelope,
        runtime_state_path=args.runtime_state,
    )
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
