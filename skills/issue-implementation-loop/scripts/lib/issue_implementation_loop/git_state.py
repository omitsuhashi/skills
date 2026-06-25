from __future__ import annotations

import subprocess


def git_output(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
