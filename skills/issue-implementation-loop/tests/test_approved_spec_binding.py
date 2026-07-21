from __future__ import annotations

import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_DIR / "scripts"
LIB_DIR = SCRIPTS_DIR / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))


def binding_module():
    from issue_implementation_loop import approved_spec_binding

    return approved_spec_binding


def capability_script_module():
    spec = importlib.util.spec_from_file_location(
        "issue_loop_check_capabilities_under_test",
        SCRIPTS_DIR / "check_capabilities.py",
    )
    assert spec and spec.loader
    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class ApprovedSpecBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.spec_path = "knowledge/wiki/syntheses/example-spec.md"
        self.issues_path = "knowledge/wiki/syntheses/example-issues.md"
        (self.repo / self.spec_path).parent.mkdir(parents=True)
        (self.repo / self.spec_path).write_bytes("承認済み仕様\n".encode())
        (self.repo / self.issues_path).write_text("# Issues\n", encoding="utf-8")
        self.draft_path = self.repo / "draft.json"
        self.output_path = self.repo / "knowledge/wiki/syntheses/example-input-packet.json"
        self.draft_path.write_text(
            json.dumps(self.draft(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def draft(self) -> dict:
        return {
            "schema_version": 2,
            "epic_id": "example",
            "artifact_root": "knowledge/wiki/syntheses",
            "work_items": [
                {
                    "id": "ASBC-001",
                    "title": "承認済み仕様を packet に束縛する",
                    "source": {"type": "local", "path": self.issues_path},
                    "acceptance_criteria": ["public operation が成功する"],
                    "non_goals": ["remote write は行わない"],
                    "verification": ["python3 -m unittest"],
                    "write_scope": ["path:skills/issue-implementation-loop"],
                    "dependencies": [],
                }
            ],
            "delivery_intent": "local_only",
        }

    @staticmethod
    def approval() -> dict:
        return {
            "decision": "approved",
            "subject": "spec_binding",
            "actor_expression": "session-user",
            "approved_at": "2026-07-21T17:55:36+09:00",
            "scope": {
                "accepted_decisions": True,
                "non_goals": True,
                "acceptance_criteria": True,
                "verification": True,
                "remote_policy": True,
                "stop_conditions": True,
            },
        }

    def seal(self):
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        ref = module.seal_input_packet(
            self.repo,
            self.draft_path.relative_to(self.repo).as_posix(),
            self.output_path.relative_to(self.repo).as_posix(),
            revision,
            self.approval(),
        )
        return module, revision, ref

    def assert_code(self, expected: str, operation) -> None:
        module = binding_module()
        with self.assertRaises(module.BindingError) as raised:
            operation()
        self.assertEqual(raised.exception.code, expected)

    def test_asb_01_02_identify_and_seal_preserve_spec_and_verify(self) -> None:
        before = (self.repo / self.spec_path).read_bytes()

        module, revision, ref = self.seal()

        self.assertEqual((self.repo / self.spec_path).read_bytes(), before)
        self.assertEqual(revision.path, self.spec_path)
        self.assertEqual(len(revision.sha256), 64)
        self.assertEqual(ref.path, self.output_path.relative_to(self.repo).as_posix())
        sealed = self.output_path.read_bytes()
        self.assertTrue(sealed.endswith(b"\n"))
        self.assertNotIn(b"\\u", sealed)
        verified = module.verify_chain(self.repo, {"input_packet": ref.to_dict()})
        self.assertTrue(verified.valid)
        self.assertEqual(verified.spec_revision, revision)
        _, repeated_revision, repeated_ref = self.seal()
        self.assertEqual(repeated_revision, revision)
        self.assertEqual(repeated_ref, ref)
        self.assertEqual(self.output_path.read_bytes(), sealed)

    def test_asb_03_changed_spec_prevents_seal_and_output_mutation(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        (self.repo / self.spec_path).write_bytes("承認後の変更\n".encode())
        sentinel = b"existing output\n"
        self.output_path.write_bytes(sentinel)

        self.assert_code(
            "SPEC_DIGEST_MISMATCH",
            lambda: module.seal_input_packet(
                self.repo,
                self.draft_path.relative_to(self.repo).as_posix(),
                self.output_path.relative_to(self.repo).as_posix(),
                revision,
                self.approval(),
            ),
        )
        self.assertEqual(self.output_path.read_bytes(), sentinel)

    def test_asb_05_missing_spec_has_stable_error(self) -> None:
        module = binding_module()
        self.assert_code(
            "SPEC_MISSING",
            lambda: module.identify_spec(self.repo, "knowledge/missing.md"),
        )

    def test_asb_06_approval_failures_have_stable_errors(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        cases = []
        cases.append(("APPROVAL_MISSING", None))
        not_approved = self.approval()
        not_approved["decision"] = "rejected"
        cases.append(("APPROVAL_NOT_APPROVED", not_approved))
        incomplete = self.approval()
        incomplete["scope"]["verification"] = False
        cases.append(("APPROVAL_SCOPE_INCOMPLETE", incomplete))
        for expected, approval in cases:
            with self.subTest(expected=expected):
                self.assert_code(
                    expected,
                    lambda approval=approval: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        revision,
                        approval,
                    ),
                )

    def test_asb_07_missing_and_malformed_digests_have_stable_errors(self) -> None:
        module = binding_module()
        for expected, value in (("DIGEST_MISSING", ""), ("DIGEST_MALFORMED", "sha256:bad")):
            with self.subTest(expected=expected):
                self.assert_code(
                    expected,
                    lambda value=value: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        {"path": self.spec_path, "sha256": value},
                        self.approval(),
                    ),
                )
        module, _, ref = self.seal()
        self.assert_code(
            "DIGEST_MISSING",
            lambda: module.verify_chain(
                self.repo, {"input_packet": {"path": ref.path}}
            ),
        )

    def test_asb_08_current_spec_drift_invalidates_sealed_packet(self) -> None:
        module, _, ref = self.seal()
        (self.repo / self.spec_path).write_bytes("one byte drift!\n".encode())

        self.assert_code(
            "SPEC_DIGEST_MISMATCH",
            lambda: module.verify_chain(self.repo, {"input_packet": ref.to_dict()}),
        )

    def test_asb_09_packet_drift_invalidates_pinned_ref(self) -> None:
        module, _, ref = self.seal()
        self.output_path.write_bytes(self.output_path.read_bytes() + b" ")

        self.assert_code(
            "INPUT_PACKET_DIGEST_MISMATCH",
            lambda: module.verify_chain(self.repo, {"input_packet": ref.to_dict()}),
        )

    def test_asb_20_rejects_unsafe_and_non_regular_spec_paths(self) -> None:
        module = binding_module()
        symlink_target = self.repo / "target.md"
        symlink_target.write_text("target\n", encoding="utf-8")
        (self.repo / "linked.md").symlink_to(symlink_target)
        (self.repo / "linked-dir").symlink_to(self.repo / "knowledge", target_is_directory=True)
        cases = [
            ("PATH_ABSOLUTE", str(self.repo / self.spec_path)),
            ("PATH_TRAVERSAL", "knowledge/../target.md"),
            ("PATH_TRAVERSAL", "knowledge\\target.md"),
            ("PATH_SYMLINK", "linked.md"),
            ("PATH_SYMLINK", "linked-dir/wiki/syntheses/example-spec.md"),
            ("PATH_NOT_REGULAR_FILE", "knowledge"),
        ]
        for expected, path in cases:
            with self.subTest(path=path):
                self.assert_code(expected, lambda path=path: module.identify_spec(self.repo, path))

    def test_asb_20_embedded_nul_is_stable_in_python_and_cli(self) -> None:
        module, _, ref = self.seal()
        self.assert_code(
            "PATH_TRAVERSAL",
            lambda: module.identify_spec(self.repo, "knowledge/invalid\x00spec.md"),
        )
        packet = json.loads(self.output_path.read_text(encoding="utf-8"))
        packet["spec_binding"]["path"] = "knowledge/invalid\x00spec.md"
        raw = (json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
        self.output_path.write_bytes(raw)
        packet_digest = __import__("hashlib").sha256(raw).hexdigest()

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "verify",
                "--repo-root",
                str(self.repo),
                "--input-packet",
                ref.path,
                "--input-packet-sha256",
                packet_digest,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["code"], "PATH_TRAVERSAL")
        self.assertNotIn("Traceback", result.stderr)

    def test_asb_21_detects_file_replacement_during_validation(self) -> None:
        module = binding_module()
        original_read = module.os.read
        replaced = False
        original_inode = os.lstat(self.repo / self.spec_path).st_ino

        def replacing_read(fd: int, count: int) -> bytes:
            nonlocal replaced
            chunk = original_read(fd, count)
            if chunk and not replaced and os.fstat(fd).st_ino == original_inode:
                replaced = True
                replacement = self.repo / "replacement.md"
                replacement.write_bytes("replacement\n".encode())
                os.replace(replacement, self.repo / self.spec_path)
            return chunk

        with mock.patch.object(module.os, "read", side_effect=replacing_read):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_asb_21_detects_parent_symlink_replacement_during_validation(self) -> None:
        module = binding_module()
        original_read = module.os.read
        replaced = False
        original_inode = os.lstat(self.repo / self.spec_path).st_ino

        def replacing_parent(fd: int, count: int) -> bytes:
            nonlocal replaced
            chunk = original_read(fd, count)
            if chunk and not replaced and os.fstat(fd).st_ino == original_inode:
                replaced = True
                os.replace(self.repo / "knowledge", self.repo / "knowledge-original")
                (self.repo / "knowledge").symlink_to(
                    self.repo / "knowledge-original", target_is_directory=True
                )
            return chunk

        with mock.patch.object(module.os, "read", side_effect=replacing_parent):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_asb_21_seal_rejects_output_parent_swap_without_external_write(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        output_parent = self.output_path.parent
        moved_parent = self.repo / "moved-syntheses"
        original_open = module.os.open
        capabilities = module.probe_seal_capabilities()
        swapped = False
        sentinel = b"existing output\n"
        self.output_path.write_bytes(sentinel)

        with tempfile.TemporaryDirectory() as outside_tmp:
            outside = Path(outside_tmp)

            def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
                nonlocal swapped
                rendered = os.fspath(path)
                if not swapped and ".example-input-packet.json." in rendered:
                    swapped = True
                    os.rename(output_parent, moved_parent)
                    output_parent.symlink_to(outside, target_is_directory=True)
                if dir_fd is None:
                    return original_open(path, flags, mode)
                return original_open(path, flags, mode, dir_fd=dir_fd)

            with mock.patch.object(
                module, "probe_seal_capabilities", return_value=capabilities
            ), mock.patch.object(module.os, "open", side_effect=swapping_open):
                self.assert_code(
                    "FILE_CHANGED_DURING_VALIDATION",
                    lambda: module.seal_input_packet(
                        self.repo,
                        self.draft_path.relative_to(self.repo).as_posix(),
                        self.output_path.relative_to(self.repo).as_posix(),
                        revision,
                        self.approval(),
                    ),
                )
            self.assertFalse((outside / self.output_path.name).exists())
            self.assertFalse(any(outside.iterdir()))
            self.assertEqual((moved_parent / self.output_path.name).read_bytes(), sentinel)

    def test_failed_rollback_preserves_discoverable_recovery_copy(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        sentinel = b"original packet bytes\n"
        self.output_path.write_bytes(sentinel)
        original_verify = module._verify_directory_chain
        original_replace = module.os.replace
        capabilities = module.probe_seal_capabilities()
        verify_calls = 0
        replace_calls = 0

        def fail_after_install(identities, output_path):
            nonlocal verify_calls
            verify_calls += 1
            if verify_calls == 3:
                raise module.BindingError(
                    "FILE_CHANGED_DURING_VALIDATION", path=output_path
                )
            return original_verify(identities, output_path)

        def fail_rollback(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
            nonlocal replace_calls
            replace_calls += 1
            if replace_calls == 2:
                raise OSError("injected rollback failure")
            return original_replace(
                src,
                dst,
                src_dir_fd=src_dir_fd,
                dst_dir_fd=dst_dir_fd,
            )

        with mock.patch.object(
            module, "_verify_directory_chain", side_effect=fail_after_install
        ), mock.patch.object(
            module, "probe_seal_capabilities", return_value=capabilities
        ), mock.patch.object(module.os, "replace", side_effect=fail_rollback):
            with self.assertRaises(module.BindingError) as raised:
                module.seal_input_packet(
                    self.repo,
                    self.draft_path.relative_to(self.repo).as_posix(),
                    self.output_path.relative_to(self.repo).as_posix(),
                    revision,
                    self.approval(),
                )

        self.assertEqual(raised.exception.code, "FILE_CHANGED_DURING_VALIDATION")
        self.assertIsNotNone(raised.exception.recovery_path)
        recovery = self.repo / raised.exception.recovery_path
        self.assertTrue(recovery.is_file())
        self.assertEqual(recovery.read_bytes(), sentinel)
        self.assertNotEqual(self.output_path.read_bytes(), sentinel)
        self.assertEqual(
            raised.exception.to_dict()["recovery_path"],
            raised.exception.recovery_path,
        )

    def test_malformed_root_and_read_os_errors_are_stable(self) -> None:
        module = binding_module()
        self.assert_code(
            "PATH_OUTSIDE_REPO",
            lambda: module.identify_spec(None, self.spec_path),
        )
        original_fstat = module.os.fstat
        spec_inode = os.lstat(self.repo / self.spec_path).st_ino

        def failing_fstat(descriptor):
            result = original_fstat(descriptor)
            if result.st_ino == spec_inode:
                raise OSError("injected fstat failure with sensitive payload")
            return result

        with mock.patch.object(module.os, "fstat", side_effect=failing_fstat):
            self.assert_code(
                "FILE_CHANGED_DURING_VALIDATION",
                lambda: module.identify_spec(self.repo, self.spec_path),
            )

    def test_binding_cli_failure_is_stable_json_without_traceback(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "identify",
                "--repo-root",
                "",
                "--spec-path",
                self.spec_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["code"], "PATH_OUTSIDE_REPO")
        self.assertNotIn("Traceback", result.stderr)

    def test_seal_platform_capability_is_probed_and_fails_closed(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        self.output_path.write_bytes(b"unchanged\n")
        unsupported = module.SealCapabilities(
            supported=False,
            missing=("dir_fd:open",),
        )
        with mock.patch.object(
            module, "probe_seal_capabilities", return_value=unsupported
        ):
            self.assert_code(
                "PLATFORM_UNSUPPORTED",
                lambda: module.seal_input_packet(
                    self.repo,
                    self.draft_path.relative_to(self.repo).as_posix(),
                    self.output_path.relative_to(self.repo).as_posix(),
                    revision,
                    self.approval(),
                ),
            )
        self.assertEqual(self.output_path.read_bytes(), b"unchanged\n")

    def test_check_capabilities_default_repo_validates_v2_packet(self) -> None:
        _, _, ref = self.seal()
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "check_capabilities.py"),
                "--input",
                ref.path,
                "--json",
            ],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["input_packet"]["ok"])
        self.assertTrue(payload["approved_spec_seal"]["supported"])
        self.assertEqual(payload["approved_spec_seal"]["missing"], [])

    def test_unsupported_seal_capability_allows_read_only_diagnostics(self) -> None:
        binding = binding_module()
        script = capability_script_module()
        unsupported = binding.SealCapabilities(
            supported=False,
            missing=("dir_fd:open",),
        )
        stdout = StringIO()
        with mock.patch.object(
            script, "probe_seal_capabilities", return_value=unsupported
        ), mock.patch.object(
            sys,
            "argv",
            ["check_capabilities.py", "--repo", str(self.repo), "--json"],
        ), mock.patch("sys.stdout", stdout):
            returncode = script.main()

        payload = json.loads(stdout.getvalue())
        self.assertEqual(returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["approved_spec_seal"]["supported"])
        self.assertFalse(payload["approved_spec_seal"]["blocking"])
        self.assertEqual(
            payload["approved_spec_seal"]["required_for"],
            ["seal", "state_change"],
        )

    def test_asb_24_contract_surface_has_no_consumer_specific_vocabulary(self) -> None:
        binding_module()
        paths = [
            SKILL_DIR / "scripts/lib/issue_implementation_loop/approved_spec_binding.py",
            SKILL_DIR / "assets/schemas/input-packet.schema.json",
            SKILL_DIR / "assets/templates/input-packet.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in paths).lower()
        self.assertIsNone(re.search(r"\bcompanies\b", text))
        self.assertIsNone(re.search(r"\bcto\b", text))

    def test_asb_25_python_and_cli_identify_return_same_binding(self) -> None:
        module = binding_module()
        revision = module.identify_spec(self.repo, self.spec_path)
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "approved_spec_binding.py"),
                "identify",
                "--repo-root",
                str(self.repo),
                "--spec-path",
                self.spec_path,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["spec_revision"], revision.to_dict())


if __name__ == "__main__":
    unittest.main()
