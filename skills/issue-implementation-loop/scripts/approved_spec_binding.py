#!/usr/bin/env python3
"""Identify, seal, and verify approved-spec bindings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop.approved_spec_binding import (  # noqa: E402
    APPROVAL_SCOPE_FIELDS,
    BindingError,
    SpecRevision,
    identify_spec,
    seal_input_packet,
    verify_chain,
)


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    identify = subparsers.add_parser("identify")
    identify.add_argument("--repo-root", required=True)
    identify.add_argument("--spec-path", required=True)

    seal = subparsers.add_parser("seal")
    seal.add_argument("--repo-root", required=True)
    seal.add_argument("--draft-packet", required=True)
    seal.add_argument("--output-packet", required=True)
    seal.add_argument("--spec-path", required=True)
    seal.add_argument("--spec-sha256", required=True)
    seal.add_argument("--decision", required=True)
    seal.add_argument("--subject", required=True)
    seal.add_argument("--actor-expression", required=True)
    seal.add_argument("--approved-at", required=True)
    seal.add_argument(
        "--approve-scope",
        action="append",
        choices=sorted(APPROVAL_SCOPE_FIELDS),
        default=[],
    )

    verify = subparsers.add_parser("verify")
    verify.add_argument("--repo-root", required=True)
    verify.add_argument("--input-packet", required=True)
    verify.add_argument("--input-packet-sha256", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "identify":
            revision = identify_spec(args.repo_root, args.spec_path)
            _print({"valid": True, "spec_revision": revision.to_dict()})
        elif args.command == "seal":
            approval = {
                "decision": args.decision,
                "subject": args.subject,
                "actor_expression": args.actor_expression,
                "approved_at": args.approved_at,
                "scope": {field: field in args.approve_scope for field in APPROVAL_SCOPE_FIELDS},
            }
            ref = seal_input_packet(
                args.repo_root,
                args.draft_packet,
                args.output_packet,
                SpecRevision(args.spec_path, args.spec_sha256),
                approval,
            )
            _print({"valid": True, "input_packet": ref.to_dict()})
        else:
            ref = {"path": args.input_packet, "sha256": args.input_packet_sha256}
            _print(verify_chain(args.repo_root, {"input_packet": ref}).to_dict())
    except BindingError as error:
        _print(error.to_dict())
        return 1
    except (OSError, TypeError, ValueError):
        error = BindingError("FILE_CHANGED_DURING_VALIDATION")
        _print(error.to_dict())
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
