from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
SOURCE_ROOT = SKILL_DIR.parents[1]
TESTS_DIR = SKILL_DIR / "tests"
sys.path.insert(0, str(TESTS_DIR))

from test_portable_git_gates import (  # noqa: E402
    GateFailure,
    GitFixture,
    MANDATORY_PACKAGE_RESOURCES,
    pre_commit_gate,
)


@unittest.skipIf(
    os.environ.get("SDD_ISOLATED_INSTALL_CHILD") == "1",
    "avoid recursively copying the installed package from its own child suite",
)
class IsolatedInstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.install_root = Path(self.temporary_directory.name).resolve()
        self.installed_skill = self.install_root / "installed-sdd-implementation"
        shutil.copytree(SKILL_DIR, self.installed_skill)
        self.target = GitFixture()

    def tearDown(self) -> None:
        self.target.close()
        self.temporary_directory.cleanup()

    def assert_package_failure(self, probe) -> None:
        with self.assertRaises(GateFailure) as raised:
            probe()
        self.assertEqual("broken skill installation", raised.exception.category)

    def test_copied_install_discovers_and_runs_its_package_suite(self) -> None:
        environment = os.environ.copy()
        environment.pop("PYTHONPATH", None)
        environment["PYTHONNOUSERSITE"] = "1"
        environment["SDD_ISOLATED_INSTALL_CHILD"] = "1"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(self.installed_skill / "tests"),
                "-p",
                "test_*.py",
                "-v",
            ],
            cwd=self.target.root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        self.assertEqual(0, result.returncode, output)
        self.assertNotIn(str(SOURCE_ROOT), output)

    def test_direct_git_validation_uses_the_copy_and_explicit_synthetic_target(self) -> None:
        evidence = pre_commit_gate(
            self.target.root,
            installed_skill_dir=self.installed_skill,
        )
        self.assertEqual("pre-commit-candidate", evidence.gate)
        self.assertEqual(str(self.target.root), evidence.target)

    def test_mandatory_inventory_matches_the_actual_portable_package(self) -> None:
        actual_resources = {
            path.relative_to(self.installed_skill).as_posix()
            for path in self.installed_skill.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix in {".md", ".py", ".yaml"}
        }
        self.assertEqual(set(MANDATORY_PACKAGE_RESOURCES), actual_resources)

    def test_missing_mandatory_resource_is_a_broken_installation(self) -> None:
        (self.installed_skill / "prompts" / "plan-reviewer.md").unlink()
        self.assert_package_failure(
            lambda: pre_commit_gate(
                self.target.root,
                installed_skill_dir=self.installed_skill,
            )
        )

    def test_resource_resolving_outside_the_package_is_a_broken_installation(self) -> None:
        outside = self.install_root / "outside-plan-contract.md"
        outside.write_text("outside package\n", encoding="utf-8")
        resource = self.installed_skill / "references" / "plan-contract.md"
        resource.unlink()
        resource.symlink_to(outside)
        self.assert_package_failure(
            lambda: pre_commit_gate(
                self.target.root,
                installed_skill_dir=self.installed_skill,
            )
        )

    def test_portable_package_has_no_host_or_repository_identity(self) -> None:
        absolute_roots = ("Users", "home", "tmp", "private" + "/" + "tmp")
        absolute_path = re.compile(
            r"/(?:" + "|".join(re.escape(root) for root in absolute_roots) + r")/\S+"
        )
        repository_only_path = re.compile(
            r"(?<![A-Za-z0-9_./])(?:scripts|[.]github)/"
            r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*"
        )
        literal_hash_identity = re.compile(r"\b[0-9a-f]{7,64}\b")
        repository_page = re.compile(
            r"knowledge/wiki/(?:drafts|syntheses)/(?P<page>[a-z0-9-]+\.md)"
        )
        allowed_pages = {"scenario-spec.md", "scenario-plan.md"}
        dynamic_probes = (str(SOURCE_ROOT),)

        errors: list[str] = []
        for relative_path in MANDATORY_PACKAGE_RESOURCES:
            text = (self.installed_skill / relative_path).read_text(encoding="utf-8")
            if absolute_path.search(text):
                errors.append(f"absolute host path: {relative_path}")
            if any(probe in text for probe in dynamic_probes):
                errors.append(f"dynamic host identity: {relative_path}")
            if repository_only_path.search(text):
                errors.append(f"repository-only resource path: {relative_path}")
            if any(
                len(set(match.group(0))) > 1
                for match in literal_hash_identity.finditer(text)
            ):
                errors.append(f"literal Git/hash identity: {relative_path}")
            for match in repository_page.finditer(text):
                if match.group("page") not in allowed_pages:
                    errors.append(f"repository page identity: {relative_path}")
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
