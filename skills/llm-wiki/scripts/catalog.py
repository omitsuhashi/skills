#!/usr/bin/env python3
"""Read a knowledge root's wiki into a deterministic, disposable JSON catalog.

Python 3.9+. PyYAML is optional; without it metadata extraction is degraded.
No files are written. Exit 1 means incomplete reads or degraded metadata, not
an empty wiki. Use file listing and body search alongside the returned pages.
"""

import argparse
import json
import os
from pathlib import Path
import re

try:
    import yaml
except ImportError:
    yaml = None

STATUSES = ("current", "historical", "mixed", "draft", "unknown")


def inventory(root):
    """Do not follow symlinks or descend into another root or generated data."""
    paths, excluded, errors = [], [], []
    wiki = root / "wiki"
    if wiki.is_symlink() or not wiki.is_dir():
        return [], [], [{"path": "wiki", "error": "missing, unreadable, or symlinked wiki directory"}]

    def onerror(error):
        errors.append({"path": str(error.filename), "error": str(error)})

    for directory, dirs, files in os.walk(wiki, onerror=onerror, followlinks=False):
        base = Path(directory)
        if base != wiki and "wiki" in dirs and {"AGENTS.md", "CLAUDE.md"}.intersection(files):
            excluded.append({"path": base.relative_to(root).as_posix(), "reason": "nested knowledge root"})
            dirs[:] = []
            continue
        for name in dirs[:]:
            path = base / name
            if name in {"raw", ".generated", ".git"} or path.is_symlink():
                excluded.append({"path": path.relative_to(root).as_posix(), "reason": "source, generated, or symlink directory"})
                dirs.remove(name)
        for name in files:
            path = base / name
            if path.is_symlink():
                excluded.append({"path": path.relative_to(root).as_posix(), "reason": "symlink file"})
            elif path.suffix.lower() == ".md":
                paths.append(path)
    return sorted(paths), sorted(excluded, key=lambda entry: entry["path"]), errors


def stamp(path):
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def extract(text):
    """Parse frontmatter with a YAML parser; never guess missing metadata."""
    metadata, diagnostics, body = {}, [], text
    lines = text.lstrip("\ufeff").splitlines()
    if lines and lines[0] == "---":
        end = next((i for i in range(1, len(lines)) if lines[i] in {"---", "..."}), None)
        if end is None:
            diagnostics.append("unterminated YAML frontmatter; metadata unavailable")
        else:
            body = "\n".join(lines[end + 1:])
            if yaml is None:
                diagnostics.append("PyYAML unavailable; metadata extraction degraded")
            else:
                try:
                    metadata = yaml.safe_load("\n".join(lines[1:end]))
                    if metadata is None:
                        metadata = {}
                    if not isinstance(metadata, dict):
                        raise ValueError("frontmatter must be a mapping")
                    for key in ("title", "summary"):
                        if key in metadata and (not isinstance(metadata[key], str) or not metadata[key].strip()):
                            raise ValueError(f"{key} must be a non-empty string")
                    if "knowledge_status" in metadata and metadata["knowledge_status"] not in STATUSES:
                        raise ValueError("invalid knowledge_status")
                    for key in ("aliases", "tags"):
                        if key in metadata and not (
                            isinstance(metadata[key], list)
                            and all(isinstance(item, str) and item.strip() for item in metadata[key])
                        ):
                            raise ValueError(f"{key} must be a list of non-empty strings")
                except (yaml.YAMLError, ValueError) as error:
                    diagnostics.append(f"invalid metadata: {error}")
                    metadata = {}
    heading = re.search(r"^#{1,6}\s+(.+?)(?:\s+#+)?\s*$", body, re.MULTILINE)
    return metadata, heading.group(1) if heading else None, diagnostics


def catalog(root, path_filter="", query="", statuses=()):
    root = Path(root).absolute()
    paths, excluded, errors = inventory(root)
    pages, observed = [], {}
    diagnostics = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        page = {"path": relative, "title": path.stem, "summary": None,
                "knowledge_status": "unknown", "aliases": [], "tags": []}
        body = ""
        try:
            before = stamp(path)
            body = path.read_text(encoding="utf-8")
            observed[path] = before
            metadata, heading, problems = extract(body)
            diagnostics.extend({"path": relative, "error": problem} for problem in problems)
            for key in page.keys() - {"path", "title"}:
                page[key] = metadata.get(key, page[key])
            page["title"] = metadata.get("title") or heading or path.stem
        except (OSError, UnicodeError) as error:
            errors.append({"path": relative, "error": str(error)})
        # Directory authority takes precedence over metadata, including promoted drafts.
        if "drafts" in path.relative_to(root / "wiki").parts[:-1]:
            page["knowledge_status"] = "draft"
        haystack = "\n".join((relative, body, json.dumps(page, ensure_ascii=False))).casefold()
        if path_filter in relative and (not query or query.casefold() in haystack) and (
            not statuses or page["knowledge_status"] in statuses
        ):
            pages.append(page)

    # A second listing and file stamps catch observed changes, not an atomic snapshot.
    after_paths, _, after_errors = inventory(root)
    errors.extend(error for error in after_errors if error not in errors)
    if after_paths != paths:
        errors.append({"path": "wiki", "error": "file set changed during read; rerun catalog"})
    for path, before in observed.items():
        try:
            if stamp(path) != before:
                raise OSError("file changed during read; rerun catalog")
        except OSError as error:
            errors.append({"path": path.relative_to(root).as_posix(), "error": str(error)})

    return {
        "root": str(root), "scope": "wiki/**/*.md (saved files in this root only)",
        "filters": {"path_contains": path_filter, "query_contains": query, "statuses": list(statuses)},
        "excluded": excluded, "total": len(paths), "matched": len(pages),
        "filtered_out": len(paths) - len(pages), "complete": not errors,
        "metadata": "degraded" if yaml is None or diagnostics else "available",
        "missing_summary": "null means no summary", "unknown_status": "unknown means unestablished applicability",
        "errors": errors, "diagnostics": diagnostics, "pages": pages,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="selected knowledge root (containing wiki/)")
    parser.add_argument("--path", default="", help="case-sensitive substring of root-relative path")
    parser.add_argument("--query", default="", help="case-insensitive phrase in path, metadata, or body")
    parser.add_argument("--status", action="append", choices=STATUSES, default=[], help="include this status (repeatable; default: all)")
    args = parser.parse_args()
    result = catalog(args.root, args.path, args.query, args.status)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["complete"] and result["metadata"] == "available" else 1


if __name__ == "__main__":
    raise SystemExit(main())
