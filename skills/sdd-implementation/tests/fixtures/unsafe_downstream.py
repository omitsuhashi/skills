from __future__ import annotations

from pathlib import Path
import sys


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: unsafe_downstream.py <marker-path>")
    Path(argv[1]).write_text("unsafe downstream executed\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
