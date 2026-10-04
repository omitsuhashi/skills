#!/usr/bin/env python3
"""Run the documented release guard against disposable local Git repositories."""

import os
from pathlib import Path
import subprocess
import tempfile


def main():
    reference = Path(__file__).resolve().parents[1] / "references/release-workflow.md"
    guard = reference.read_text().split("```bash\n", 1)[1].split("```", 1)[0]
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Fixture",
        "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "Fixture",
        "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }

    def git(directory, *args):
        return subprocess.check_output(
            ["git", "-c", "core.hooksPath=" + os.devnull, *args],
            cwd=directory, env=env, stderr=subprocess.DEVNULL, text=True,
        ).strip()

    with tempfile.TemporaryDirectory(prefix="github-repo-setup-") as temporary:
        source = Path(temporary) / "source"
        checkout = Path(temporary) / "checkout"
        source.mkdir()
        git(source, "init", "-b", "main")
        git(source, "commit", "--allow-empty", "-m", "Initial")
        ancestor = git(source, "rev-parse", "HEAD")
        git(source, "commit", "--allow-empty", "-m", "Reviewed")
        tip = git(source, "rev-parse", "HEAD")
        git(source, "tag", "-a", "v1.0.0", "-m", "Release")
        tag_object = git(source, "rev-parse", "v1.0.0")
        git(source, "branch", "release/stable")
        git(source, "checkout", "-b", "feature", ancestor)
        git(source, "commit", "--allow-empty", "-m", "Unmerged")
        feature = git(source, "rev-parse", "HEAD")
        git(source, "checkout", "main")
        git(source, "clone", str(source), str(checkout))

        def check(commit, expected, *, branch="main", ref_type="tag", head=None):
            git(checkout, "checkout", "--detach", head or commit)
            result = subprocess.run(
                ["bash", "-c", guard], cwd=checkout,
                env={**env, "GITHUB_SHA": commit, "GITHUB_REF_TYPE": ref_type,
                     "RELEASE_BRANCH": branch},
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            assert (result.returncode == 0) == expected, (
                commit, branch, ref_type, expected, result.stderr,
            )

        check(tip, True)
        check(ancestor, True)
        check(tag_object, True)
        check(tip, True, branch="release/stable")
        check(feature, False)
        check(tip, False, ref_type="branch")
        check(tip, False, branch="missing")
        check(tip, False, branch="../main")
        check(tip, False, head=ancestor)
        check("0" * 40, False, head=tip)
    print("Release guard: 10 cases passed (local Git fixtures only)")


if __name__ == "__main__":
    main()
