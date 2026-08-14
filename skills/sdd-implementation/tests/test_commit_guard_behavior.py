from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
GUARD_SOURCE = SKILL_DIR / "scripts" / "prepare-commit-msg"


def run_git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr}"
        )
    return result


class CommitGuardBehaviorTests(unittest.TestCase):
    def make_repository(self, root: Path) -> Path:
        primary = root / "primary"
        primary.mkdir()
        run_git(primary, "init", "-b", "main")
        run_git(primary, "config", "user.name", "Guard Test")
        run_git(primary, "config", "user.email", "guard@example.invalid")
        (primary / "base.txt").write_text("base\n", encoding="utf-8")
        run_git(primary, "add", "base.txt")
        run_git(primary, "commit", "-m", "base")
        return primary

    def install_guard(self, primary: Path) -> Path:
        self.assertTrue(GUARD_SOURCE.is_file(), f"guard source missing: {GUARD_SOURCE}")
        common_dir = Path(
            run_git(
                primary,
                "rev-parse",
                "--path-format=absolute",
                "--git-common-dir",
            ).stdout.strip()
        )
        hook = common_dir / "hooks" / "prepare-commit-msg"
        hook.write_bytes(GUARD_SOURCE.read_bytes())
        hook.chmod(0o755)
        return hook

    def history_fingerprint(self, checkout: Path) -> tuple[str, int]:
        head = run_git(checkout, "rev-parse", "HEAD").stdout.strip()
        count = int(run_git(checkout, "rev-list", "--count", "HEAD").stdout.strip())
        return head, count

    def attempt_commit(self, checkout: Path, filename: str, *extra: str) -> subprocess.CompletedProcess[str]:
        (checkout / filename).write_text(f"candidate:{filename}\n", encoding="utf-8")
        run_git(checkout, "add", filename)
        return run_git(checkout, "commit", *extra, "-m", filename, check=False)

    def test_primary_commit_and_no_verify_are_rejected(self) -> None:
        for extra in ((), ("--no-verify",)):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as temp:
                primary = self.make_repository(Path(temp))
                self.install_guard(primary)
                before = self.history_fingerprint(primary)

                result = self.attempt_commit(primary, "primary.txt", *extra)

                self.assertNotEqual(0, result.returncode)
                self.assertIn(
                    "SDD commit guard: primary checkout rejected",
                    result.stderr,
                )
                self.assertEqual(before, self.history_fingerprint(primary))

    def test_registered_linked_worktree_commit_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            primary = self.make_repository(fixture)
            linked = fixture / "linked"
            run_git(primary, "worktree", "add", "-b", "topic/allowed", str(linked))
            hook = self.install_guard(primary)
            primary_before = self.history_fingerprint(primary)
            linked_status_before = run_git(linked, "status", "--porcelain=v1", "-z").stdout

            first_check = subprocess.run(
                [str(hook), "--self-check"],
                cwd=linked,
                capture_output=True,
                text=True,
            )
            second_check = subprocess.run(
                [str(hook), "--self-check"],
                cwd=linked,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, first_check.returncode, first_check.stderr)
            self.assertEqual(first_check.stdout, second_check.stdout)
            self.assertEqual(
                '{"allowed":true,"reason":"registered linked worktree"}\n',
                first_check.stdout,
            )
            self.assertEqual(primary_before, self.history_fingerprint(primary))
            self.assertEqual(
                linked_status_before,
                run_git(linked, "status", "--porcelain=v1", "-z").stdout,
            )

            result = self.attempt_commit(linked, "linked.txt")

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(primary_before, self.history_fingerprint(primary))
            self.assertEqual(2, self.history_fingerprint(linked)[1])

    def test_unknown_checkout_identity_fails_closed(self) -> None:
        with self.subTest(case="detached-linked-head"), tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            primary = self.make_repository(fixture)
            linked = fixture / "linked"
            run_git(primary, "worktree", "add", "-b", "topic/detached", str(linked))
            run_git(linked, "checkout", "--detach")
            self.install_guard(primary)
            before = self.history_fingerprint(linked)

            result = self.attempt_commit(linked, "detached.txt")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("SDD commit guard:", result.stderr)
            self.assertLess(len(result.stderr), 1000)
            self.assertEqual(before, self.history_fingerprint(linked))
            self.assertEqual("candidate:detached.txt\n", (linked / "detached.txt").read_text())

        with self.subTest(case="copied-checkout-registration-mismatch"), tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp)
            primary = self.make_repository(fixture)
            linked = fixture / "linked"
            copied = fixture / "copied"
            run_git(primary, "worktree", "add", "-b", "topic/copied", str(linked))
            self.install_guard(primary)
            shutil.copytree(linked, copied)
            before = self.history_fingerprint(linked)

            result = self.attempt_commit(copied, "copied.txt")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("SDD commit guard:", result.stderr)
            self.assertLess(len(result.stderr), 1000)
            self.assertEqual(before, self.history_fingerprint(linked))
            self.assertEqual("candidate:copied.txt\n", (copied / "copied.txt").read_text())

        for evidence in ("missing", "ambiguous"):
            with self.subTest(case=f"{evidence}-gitdir-evidence"), tempfile.TemporaryDirectory() as temp:
                fixture = Path(temp)
                primary = self.make_repository(fixture)
                linked = fixture / "linked"
                run_git(primary, "worktree", "add", "-b", f"topic/{evidence}", str(linked))
                hook = self.install_guard(primary)
                git_dir = Path(
                    run_git(linked, "rev-parse", "--absolute-git-dir").stdout.strip()
                )
                backlink = git_dir / "gitdir"
                if evidence == "missing":
                    backlink.unlink()
                else:
                    backlink.write_text(
                        f"{linked / '.git'}\n{linked / '.git'}\n",
                        encoding="utf-8",
                    )
                sentinel = linked / "sentinel.txt"
                sentinel.write_text("unchanged\n", encoding="utf-8")

                result = subprocess.run(
                    [str(hook), "--self-check"],
                    cwd=linked,
                    capture_output=True,
                    text=True,
                )

                self.assertNotEqual(0, result.returncode)
                payload = json.loads(result.stdout)
                self.assertEqual(False, payload["allowed"])
                self.assertLess(len(payload["reason"]), 200)
                self.assertEqual("unchanged\n", sentinel.read_text(encoding="utf-8"))

        with self.subTest(case="git-query-failure"), tempfile.TemporaryDirectory() as temp:
            outside = Path(temp)
            sentinel = outside / "sentinel.txt"
            sentinel.write_text("unchanged\n", encoding="utf-8")
            self.assertTrue(GUARD_SOURCE.is_file(), f"guard source missing: {GUARD_SOURCE}")

            result = subprocess.run(
                [str(GUARD_SOURCE), "--self-check"],
                cwd=outside,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual(False, payload["allowed"])
            self.assertLess(len(payload["reason"]), 200)
            self.assertEqual("unchanged\n", sentinel.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
