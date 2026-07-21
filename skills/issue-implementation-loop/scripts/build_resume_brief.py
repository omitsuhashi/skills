#!/usr/bin/env python3
"""Build a regenerable resume brief from issue-implementation-loop runtime state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from issue_implementation_loop.resume_brief import (  # noqa: E402
    DEFAULT_MAX_WORDS,
    DEFAULT_META_NAME,
    DEFAULT_OUTPUT_NAME,
    ResumeBriefBudgetError,
    ResumeBriefError,
    build_resume_brief,
    build_resume_brief_meta,
    resume_source_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime_root", help="Runtime root containing runtime-state.json/events.jsonl")
    parser.add_argument("--envelope", help="Optional execution-envelope.json path")
    parser.add_argument("--output", help="Output path; defaults to <runtime-root>/resume-brief.md")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS)
    parser.add_argument("--stdout", action="store_true", help="Also print the brief markdown")
    parser.add_argument("--repo-root", help="Trusted Git worktree root (defaults to cwd).")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parents[1]
    template_path = script_dir / "assets" / "templates" / "resume-brief.md"
    template_text = template_path.read_text(encoding="utf-8")
    runtime_root = Path(args.runtime_root)
    output_path = Path(args.output) if args.output else runtime_root / DEFAULT_OUTPUT_NAME

    output_temp: Path | None = None
    meta_temp: Path | None = None
    try:
        source_snapshot = resume_source_snapshot(
            runtime_root, envelope_path=args.envelope
        )
        content, words = build_resume_brief(
            runtime_root,
            template_text,
            envelope_path=args.envelope,
            max_words=args.max_words,
            repo_root=args.repo_root or Path.cwd(),
        )
        if (
            resume_source_snapshot(runtime_root, envelope_path=args.envelope)
            != source_snapshot
        ):
            raise ResumeBriefError("RESUME_SOURCE_CHANGED")

        meta_path = runtime_root / DEFAULT_META_NAME
        brief_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        meta = build_resume_brief_meta(
            runtime_root,
            brief_path=output_path,
            envelope_path=args.envelope,
            word_count=words,
            max_words=args.max_words,
            sources=source_snapshot,
            brief_sha256=brief_sha256,
        )
        if (
            resume_source_snapshot(runtime_root, envelope_path=args.envelope)
            != source_snapshot
        ):
            raise ResumeBriefError("RESUME_SOURCE_CHANGED")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output_path.parent, delete=False
        ) as handle:
            handle.write(content)
            output_temp = Path(handle.name)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=meta_path.parent, delete=False
        ) as handle:
            handle.write(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            meta_temp = Path(handle.name)

        if (
            resume_source_snapshot(runtime_root, envelope_path=args.envelope)
            != source_snapshot
        ):
            raise ResumeBriefError("RESUME_SOURCE_CHANGED")
        os.replace(output_temp, output_path)
        output_temp = None
        os.replace(meta_temp, meta_path)
        meta_temp = None
    except ResumeBriefBudgetError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (ResumeBriefError, OSError, json.JSONDecodeError) as exc:
        if str(exc) == "RESUME_SOURCE_CHANGED":
            print("RESUME_SOURCE_CHANGED", file=sys.stderr)
        else:
            print(f"RESUME_BRIEF_BUILD_FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        for temp_path in (output_temp, meta_temp):
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    if args.stdout:
        print(content, end="")
    else:
        print(
            json.dumps(
                {
                    "path": str(output_path),
                    "meta_path": str(meta_path),
                    "word_count": words,
                    "max_words": args.max_words,
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
