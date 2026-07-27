from __future__ import annotations

import shutil

from _helpers import *


REPO_ROOT = SKILL_DIR.parents[1]
VALIDATE_SKILL_CONTEXT = REPO_ROOT / "scripts" / "validate_skill_context.py"
INSPECT_SKILL_CONTEXT = REPO_ROOT / "scripts" / "inspect_skill_context.py"
REPORT_SKILL_CONTEXT = REPO_ROOT / "scripts" / "report_skill_context.py"
METRICS_FILE = REPO_ROOT / "scripts" / "skill_context" / "metrics.py"


def run_generic_context_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_SKILL_CONTEXT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_generic_context_inspector(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSPECT_SKILL_CONTEXT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_generic_context_report(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPORT_SKILL_CONTEXT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def load_metrics_module():
    spec = importlib.util.spec_from_file_location("skill_context_metrics_under_test", METRICS_FILE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_example_skill(root: Path, name: str, contract_text: str) -> Path:
    skill_dir = root / "skills" / name
    references_dir = skill_dir / "references"
    (references_dir / "nested").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Example\n\nsmall entrypoint text\n", encoding="utf-8")
    (references_dir / "core.md").write_text("core reference words\n", encoding="utf-8")
    (references_dir / "extra.md").write_text("extra reference words\n", encoding="utf-8")
    (references_dir / "nested" / "deep.md").write_text("deep reference words\n", encoding="utf-8")
    (skill_dir / "context-contract.toml").write_text(contract_text, encoding="utf-8")
    return skill_dir


def write_japanese_skill(root: Path, contract_text: str) -> Path:
    skill_dir = root / "skills" / "japanese-loop"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "# Japanese Loop\n\nこれは日本語の長い説明です。承認、検証、実装境界を扱います。\n",
        encoding="utf-8",
    )
    (references_dir / "core.md").write_text(
        "追加の文脈です。worker は write scope を守り、remote write を行いません。\n",
        encoding="utf-8",
    )
    (references_dir / "extra.md").write_text("extra ascii reference words\n", encoding="utf-8")
    (skill_dir / "context-contract.toml").write_text(contract_text, encoding="utf-8")
    return skill_dir


class ContextContractTests(unittest.TestCase):
    SPEC_FORBIDDEN_STANDALONE_SKILLS = (
        "scheduler",
        "execution-envelope",
        "dependency-graph",
        "runtime-state",
        "worktree-lifecycle",
        "review-gate",
        "human-wait",
        "remote-delivery",
        "worker-contract",
        "context-manager",
    )

    def test_loop_specific_context_wrappers_are_removed(self) -> None:
        self.assertFalse((REPO_ROOT / "scripts" / "validate_loop_skill_context.py").exists())
        self.assertFalse((REPO_ROOT / "scripts" / "inspect_loop_skill_context.py").exists())

    def test_validator_rejects_missing_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "example-loop"
            references_dir = skill_dir / "references"
            references_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Example\n", encoding="utf-8")
            (skill_dir / "context-contract.toml").write_text(
                "\n".join(
                    [
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/missing.md"]',
                        "word_budget = 100",
                        "max_file_count = 3",
                        "",
                        "[operations.test]",
                        "references = []",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_generic_context_validator("--skill", str(skill_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing reference", result.stderr)

    def test_metrics_preserve_file_boundaries_for_words_and_tokens(self) -> None:
        metrics = load_metrics_module().collect_text_metrics(["a", "a"], {"estimated_token_budget": 10})

        self.assertEqual(metrics["word_count"], 2)
        self.assertEqual(metrics["estimated_token_count"], 2)
        self.assertEqual(metrics["character_count"], 2)
        self.assertEqual(metrics["non_whitespace_character_count"], 2)

    def test_generic_validator_accepts_absolute_skill_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_example_skill(
                Path(tmp),
                "cwd-loop",
                "\n".join(
                    [
                        'skill = "cwd-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
            )

            result = run_generic_context_validator("--skill", str(skill_dir))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_generic_inspector_accepts_absolute_skill_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_example_skill(
                Path(tmp),
                "cwd-loop",
                "\n".join(
                    [
                        'skill = "cwd-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
            )

            result = run_generic_context_inspector(
                "--skill",
                str(skill_dir),
                "--operation",
                "test",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["skill"], "cwd-loop")

    def test_generic_v3_requires_phase_skill_fields_for_every_operation(self) -> None:
        cases = (
            ("skills", 'dispatch_skills = []', "operations.test.skills must be an array"),
            ("dispatch_skills", 'skills = []', "operations.test.dispatch_skills must be an array"),
        )
        for field, present_field, expected in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                skill_dir = write_example_skill(
                    Path(tmp),
                    "example-loop",
                    "\n".join(
                        [
                            "schema_version = 3",
                            'skill = "example-loop"',
                            'entrypoint = "SKILL.md"',
                            'base_references = ["references/core.md"]',
                            "character_budget = 5000",
                            "estimated_token_budget = 1000",
                            "max_file_count = 4",
                            "min_headroom_percent = 0",
                            "",
                            "[operations.test]",
                            'references = ["references/extra.md"]',
                            present_field,
                        ]
                    ),
                )

                result = run_generic_context_validator("--skill", str(skill_dir))

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_generic_v3_rejects_empty_or_duplicate_phase_skill_names(self) -> None:
        cases = (
            (
                'skills = [""]',
                "dispatch_skills = []",
                "operations.test.skills must be an array of non-empty strings",
            ),
            (
                "skills = []",
                'dispatch_skills = ["tdd", "tdd"]',
                "operations.test.dispatch_skills contains duplicate skill: tdd",
            ),
        )
        for skills_field, dispatch_skills_field, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as tmp:
                skill_dir = write_example_skill(
                    Path(tmp),
                    "example-loop",
                    "\n".join(
                        [
                            "schema_version = 3",
                            'skill = "example-loop"',
                            'entrypoint = "SKILL.md"',
                            'base_references = ["references/core.md"]',
                            "character_budget = 5000",
                            "estimated_token_budget = 1000",
                            "max_file_count = 4",
                            "min_headroom_percent = 0",
                            "",
                            "[operations.test]",
                            'references = ["references/extra.md"]',
                            skills_field,
                            dispatch_skills_field,
                        ]
                    ),
                )

                result = run_generic_context_validator("--skill", str(skill_dir))

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_generic_v3_inspector_returns_phase_skill_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_example_skill(
                Path(tmp),
                "example-loop",
                "\n".join(
                    [
                        "schema_version = 3",
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "character_budget = 5000",
                        "estimated_token_budget = 1000",
                        "max_file_count = 4",
                        "min_headroom_percent = 0",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                        'skills = ["requesting-code-review"]',
                        "dispatch_skills = []",
                    ]
                ),
            )

            json_result = run_generic_context_inspector(
                "--skill",
                str(skill_dir),
                "--operation",
                "test",
                "--json",
            )
            text_result = run_generic_context_inspector(
                "--skill",
                str(skill_dir),
                "--operation",
                "test",
            )

            self.assertEqual(json_result.returncode, 0, json_result.stderr)
            payload = json.loads(json_result.stdout)
            self.assertEqual(payload["skills"], ["requesting-code-review"])
            self.assertEqual(payload["dispatch_skills"], [])
            self.assertIn("skills: requesting-code-review", text_result.stdout)
            self.assertIn("dispatch_skills: none", text_result.stdout)

    def test_generic_validator_preserves_v1_v2_compatibility(self) -> None:
        for schema in (1, 2):
            with self.subTest(schema=schema), tempfile.TemporaryDirectory() as tmp:
                budget_lines = (
                    ["word_budget = 100"]
                    if schema == 1
                    else [
                        "schema_version = 2",
                        "character_budget = 5000",
                        "estimated_token_budget = 1000",
                        "min_headroom_percent = 0",
                    ]
                )
                skill_dir = write_example_skill(
                    Path(tmp),
                    "example-loop",
                    "\n".join(
                        [
                            'skill = "example-loop"',
                            'entrypoint = "SKILL.md"',
                            'base_references = ["references/core.md"]',
                            *budget_lines,
                            "max_file_count = 4",
                            "",
                            "[operations.test]",
                            'references = ["references/extra.md"]',
                        ]
                    ),
                )

                result = run_generic_context_validator("--skill", str(skill_dir))
                inspect_result = run_generic_context_inspector(
                    "--skill",
                    str(skill_dir),
                    "--operation",
                    "test",
                    "--json",
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(inspect_result.returncode, 0, inspect_result.stderr)
                payload = json.loads(inspect_result.stdout)
                self.assertEqual(payload.get("skills"), [])
                self.assertEqual(payload.get("dispatch_skills"), [])

    def test_validator_rejects_context_contract_failure_cases(self) -> None:
        cases = [
            (
                "duplicate",
                "example-loop",
                "\n".join(
                    [
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/core.md"]',
                    ]
                ),
                "duplicate reference",
            ),
            (
                "depth",
                "example-loop",
                "\n".join(
                    [
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/nested/deep.md"]',
                    ]
                ),
                "reference depth > 1",
            ),
            (
                "budget",
                "example-loop",
                "\n".join(
                    [
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 1",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
                "word budget exceeded",
            ),
            (
                "max-files",
                "example-loop",
                "\n".join(
                    [
                        'skill = "example-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 2",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
                "max file count exceeded",
            ),
            (
                "invalid-toml",
                "example-loop",
                'skill = "example-loop\n',
                "invalid TOML",
            ),
        ]
        for case_name, skill_name, contract_text, expected in cases:
            with self.subTest(case_name):
                with tempfile.TemporaryDirectory() as tmp:
                    skill_dir = write_example_skill(Path(tmp), skill_name, contract_text)

                    result = run_generic_context_validator("--skill", str(skill_dir))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_validator_rejects_spec_forbidden_standalone_skill_names(self) -> None:
        for skill_name in self.SPEC_FORBIDDEN_STANDALONE_SKILLS:
            with self.subTest(skill_name):
                with tempfile.TemporaryDirectory() as tmp:
                    skill_dir = write_example_skill(
                        Path(tmp),
                        skill_name,
                        "\n".join(
                            [
                                f'skill = "{skill_name}"',
                                'entrypoint = "SKILL.md"',
                                'base_references = ["references/core.md"]',
                                "word_budget = 100",
                                "max_file_count = 4",
                                "",
                                "[operations.test]",
                                'references = ["references/extra.md"]',
                            ]
                        ),
                    )

                    result = run_generic_context_validator("--skill", str(skill_dir))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("forbidden standalone skill name", result.stderr)

    def test_validator_allows_dependency_contract_reference_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_example_skill(
                Path(tmp),
                "dependency-contract",
                "\n".join(
                    [
                        'skill = "dependency-contract"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "word_budget = 100",
                        "max_file_count = 4",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
            )

            result = run_generic_context_validator("--skill", str(skill_dir))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_inspector_returns_issue_review_read_set(self) -> None:
        result = run_generic_context_inspector(
            "--skill",
            "skills/issue-implementation-loop",
            "--operation",
            "execute.review",
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skill"], "issue-implementation-loop")
        self.assertEqual(payload["operation"], "execute.review")
        self.assertEqual(
            payload["files"],
            [
                "skills/issue-implementation-loop/SKILL.md",
                "skills/issue-implementation-loop/references/core.md",
                "skills/issue-implementation-loop/references/review-gate.md",
                "skills/issue-implementation-loop/references/worker-contract.md",
                "skills/issue-implementation-loop/references/runtime-state.md",
            ],
        )
        self.assertGreater(payload["word_count"], 0)
        self.assertGreaterEqual(payload["headroom_percent"], 0)

    def test_generic_validator_and_inspector_accept_current_issue_loop_contract(self) -> None:
        result = run_generic_context_validator("--skill", "skills/issue-implementation-loop")

        self.assertEqual(result.returncode, 0, result.stderr)

        inspect_result = run_generic_context_inspector(
            "--skill",
            "skills/issue-implementation-loop",
            "--operation",
            "execute.review",
            "--json",
        )

        self.assertEqual(inspect_result.returncode, 0, inspect_result.stderr)
        payload = json.loads(inspect_result.stdout)
        self.assertEqual(payload["schema_version"], 3)
        self.assertEqual(payload["skill"], "issue-implementation-loop")
        self.assertEqual(payload["skills"], ["requesting-code-review"])
        self.assertEqual(payload["dispatch_skills"], [])
        self.assertGreater(payload["character_count"], 0)
        self.assertGreater(payload["non_whitespace_character_count"], 0)
        self.assertGreater(payload["estimated_token_count"], 0)
        self.assertIn("headroom_percent", payload)
        self.assertIsNone(payload["word_budget"])
        self.assertGreater(payload["budget"]["estimated_token_budget"], 0)

    def test_generic_validator_rejects_phase_skill_mapping_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "issue-implementation-loop"
            shutil.copytree(SKILL_DIR, skill_dir)
            contract_path = skill_dir / "context-contract.toml"
            contract_text = contract_path.read_text(encoding="utf-8")
            contract_text = contract_text.replace(
                'skills = ["requesting-code-review"]',
                "skills = []",
                1,
            )
            contract_path.write_text(contract_text, encoding="utf-8")

            result = run_generic_context_validator("--skill", str(skill_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "unexpected phase skill mapping: "
                "issue-implementation-loop execute.review.skills",
                result.stderr,
            )

    def test_issue_loop_contract_defines_wait_operation_and_slim_dispatch(self) -> None:
        dispatch_result = run_generic_context_inspector(
            "--skill",
            "skills/issue-implementation-loop",
            "--operation",
            "execute.dispatch",
            "--json",
        )
        wait_result = run_generic_context_inspector(
            "--skill",
            "skills/issue-implementation-loop",
            "--operation",
            "execute.wait",
            "--json",
        )

        self.assertEqual(dispatch_result.returncode, 0, dispatch_result.stderr)
        self.assertEqual(wait_result.returncode, 0, wait_result.stderr)
        dispatch_payload = json.loads(dispatch_result.stdout)
        wait_payload = json.loads(wait_result.stdout)
        self.assertEqual(dispatch_payload.get("skills"), [])
        self.assertEqual(dispatch_payload.get("dispatch_skills"), ["tdd"])
        self.assertEqual(wait_payload.get("skills"), [])
        self.assertEqual(wait_payload.get("dispatch_skills"), [])
        self.assertNotIn(
            "skills/issue-implementation-loop/references/human-wait.md",
            dispatch_payload["files"],
        )
        self.assertEqual(
            wait_payload["files"],
            [
                "skills/issue-implementation-loop/SKILL.md",
                "skills/issue-implementation-loop/references/core.md",
                "skills/issue-implementation-loop/references/human-wait.md",
                "skills/issue-implementation-loop/references/runtime-state.md",
            ],
        )

    def test_generic_validator_accepts_v2_budget_and_japanese_estimation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = write_japanese_skill(
                Path(tmp),
                "\n".join(
                    [
                        "schema_version = 2",
                        'skill = "japanese-loop"',
                        'entrypoint = "SKILL.md"',
                        'base_references = ["references/core.md"]',
                        "character_budget = 5000",
                        "estimated_token_budget = 1000",
                        "max_file_count = 4",
                        "min_headroom_percent = 20",
                        "",
                        "[operations.test]",
                        'references = ["references/extra.md"]',
                    ]
                ),
            )

            result = run_generic_context_validator("--skill", str(skill_dir))
            inspect_result = run_generic_context_inspector(
                "--skill",
                str(skill_dir),
                "--operation",
                "test",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(inspect_result.returncode, 0, inspect_result.stderr)
            payload = json.loads(inspect_result.stdout)
            self.assertEqual(payload["schema_version"], 2)
            self.assertGreater(payload["character_count"], payload["word_count"])
            self.assertGreaterEqual(
                payload["estimated_token_count"],
                payload["non_whitespace_character_count"] // 2,
            )
            self.assertGreaterEqual(payload["headroom_percent"], 20)

    def test_generic_validator_rejects_v2_budget_failures(self) -> None:
        cases = [
            ("char-budget", "character_budget = 10", "character budget exceeded"),
            ("token-budget", "estimated_token_budget = 5", "estimated token budget exceeded"),
            ("headroom", "min_headroom_percent = 99", "headroom below minimum"),
        ]
        for case_name, override, expected in cases:
            with self.subTest(case_name):
                with tempfile.TemporaryDirectory() as tmp:
                    defaults = {
                        "character_budget": "character_budget = 5000",
                        "estimated_token_budget": "estimated_token_budget = 1000",
                        "min_headroom_percent": "min_headroom_percent = 0",
                    }
                    key = override.split("=", 1)[0].strip()
                    defaults[key] = override
                    skill_dir = write_japanese_skill(
                        Path(tmp),
                        "\n".join(
                            [
                                "schema_version = 2",
                                'skill = "japanese-loop"',
                                'entrypoint = "SKILL.md"',
                                'base_references = ["references/core.md"]',
                                defaults["character_budget"],
                                defaults["estimated_token_budget"],
                                "max_file_count = 4",
                                defaults["min_headroom_percent"],
                                "",
                                "[operations.test]",
                                'references = ["references/extra.md"]',
                            ]
                        ),
                    )

                    result = run_generic_context_validator("--skill", str(skill_dir))

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected, result.stderr)

    def test_report_skill_context_emits_json_metrics(self) -> None:
        result = run_generic_context_report("--all", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["report_type"], "skill-context-report")
        operations = [
            operation
            for skill in payload["skills"]
            for operation in skill["operations"]
            if operation["skill"] == "issue-implementation-loop"
        ]
        self.assertTrue(operations)
        self.assertTrue(all("estimated_token_count" in operation for operation in operations))

    def test_current_context_baseline_covers_every_operation_without_warnings(self) -> None:
        result = run_generic_context_report(
            "--all",
            "--json",
            "--require-baseline",
            "--fail-on-warning",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["warnings"], [])

    def test_context_contract_keeps_exactly_eight_existing_operations(self) -> None:
        contract_text = (SKILL_DIR / "context-contract.toml").read_text(
            encoding="utf-8"
        )
        operation_headers = re.findall(
            r'^\[operations\.(?:"([^"]+)"|([^\]]+))\]$',
            contract_text,
            re.MULTILINE,
        )
        operations = {quoted or plain for quoted, plain in operation_headers}
        self.assertEqual(len(operations), 8)
        self.assertNotIn("blocked.reapproval", operations)
        baseline = json.loads(
            (
                REPO_ROOT
                / "knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json"
            ).read_text(encoding="utf-8")
        )
        issue_rows = [
            operation
            for skill in baseline["skills"]
            for operation in skill.get("operations", [])
            if operation.get("skill") == "issue-implementation-loop"
        ]
        self.assertEqual(len(issue_rows), 8)
        self.assertNotIn(
            "blocked.reapproval",
            {operation["operation"] for operation in issue_rows},
        )

    def test_report_skill_context_can_fail_when_required_baseline_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            baseline_path = Path(tmp) / "baseline.json"
            write_json(baseline_path, {"skills": []})

            result = run_generic_context_report(
                "--skill",
                "skills/issue-implementation-loop",
                "--json",
                "--baseline",
                str(baseline_path),
                "--require-baseline",
                "--fail-on-warning",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("WARNING: issue-implementation-loop", result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["warnings"])
        self.assertTrue(all("missing baseline" in warning for warning in payload["warnings"]))


if __name__ == "__main__":
    unittest.main()
