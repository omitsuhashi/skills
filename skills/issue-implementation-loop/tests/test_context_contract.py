from __future__ import annotations

from _helpers import *


REPO_ROOT = SKILL_DIR.parents[1]
VALIDATE_CONTEXT = REPO_ROOT / "scripts" / "validate_loop_skill_context.py"
INSPECT_CONTEXT = REPO_ROOT / "scripts" / "inspect_loop_skill_context.py"


def run_context_validator(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_CONTEXT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_context_inspector(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSPECT_CONTEXT), *args],
        check=False,
        capture_output=True,
        text=True,
    )


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

            result = run_context_validator("--skill", str(skill_dir))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing reference", result.stderr)

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

                    result = run_context_validator("--skill", str(skill_dir))

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

                    result = run_context_validator("--skill", str(skill_dir))

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

            result = run_context_validator("--skill", str(skill_dir))

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_inspector_returns_issue_review_read_set(self) -> None:
        result = run_context_inspector(
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
        self.assertGreaterEqual(payload["budget_headroom"], 0)


if __name__ == "__main__":
    unittest.main()
