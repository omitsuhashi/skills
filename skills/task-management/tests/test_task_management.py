from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
VALIDATE_CONTEXT = REPO_ROOT / "scripts" / "validate_skill_context.py"
INSPECT_CONTEXT = REPO_ROOT / "scripts" / "inspect_skill_context.py"


def load_module(module_name: str, path: Path):
    script_dir = str(path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class TaskManagementSkillTests(unittest.TestCase):
    def test_capture_text_normalizes_to_draft_with_inbox_fallback(self) -> None:
        backend = load_module("task_backend", SKILL_DIR / "scripts" / "task_backend.py")
        drafting = load_module("task_draft", SKILL_DIR / "scripts" / "task_draft.py")

        draft = drafting.normalize_capture_text(
            "Prepare the supplier review memo by 2026-07-03. urgency: high",
            default_work_unit_id="inbox",
            source_ref="chat:local-capture",
        )

        self.assertIsInstance(draft, backend.TaskDraft)
        self.assertEqual(draft.work_unit_id, "inbox")
        self.assertEqual(draft.due_date, "2026-07-03")
        self.assertEqual(draft.urgency, "high")
        self.assertEqual(draft.automation_mode, "draft_only")
        self.assertTrue(draft.approval_required)
        self.assertNotIn("raw_payload", draft.to_public_dict())

    def test_github_projects_fixture_adapter_is_idempotent_and_hides_provider_ids(self) -> None:
        backend = load_module("task_backend", SKILL_DIR / "scripts" / "task_backend.py")
        github = load_module(
            "github_projects_adapter",
            SKILL_DIR / "scripts" / "github_projects_adapter.py",
        )
        adapter = github.InMemoryGitHubProjectsAdapter(
            github.GitHubProjectsConfig(
                owner="the3-inc",
                project_number=7,
                repository="the3-inc/companies",
            )
        )
        draft = backend.TaskDraft(
            title="Review command center routing",
            body="Check routing and capture handoff.",
            work_unit_id="WU-command-center",
            task_type="review",
            urgency="medium",
            importance="high",
            automation_mode="manual",
            source_ref="knowledge:source-123",
            idempotency_key="source-123:review-routing",
        )

        first = adapter.create_task(draft)
        second = adapter.create_task(draft)

        self.assertTrue(first.created)
        self.assertFalse(second.created)
        self.assertEqual(first.task_ref, second.task_ref)
        public_result = first.to_public_dict()
        encoded = json.dumps(public_result, sort_keys=True)
        for forbidden in ("graphql", "projectField", "repositoryId", "statusOption"):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(public_result["task_ref"]["backend"], "github-projects")
        self.assertIn("https://github.com/", public_result["task_ref"]["url"])

    def test_task_draft_rejects_provider_specific_metadata_keys(self) -> None:
        backend = load_module("task_backend", SKILL_DIR / "scripts" / "task_backend.py")

        with self.assertRaises(ValueError):
            backend.TaskDraft(
                title="Review source",
                body="Review raw source.",
                work_unit_id="inbox",
                metadata={"raw_payload": {"message_id": "abc123"}},
            )

    def test_query_update_and_comment_use_backend_neutral_fields(self) -> None:
        backend = load_module("task_backend", SKILL_DIR / "scripts" / "task_backend.py")
        github = load_module(
            "github_projects_adapter",
            SKILL_DIR / "scripts" / "github_projects_adapter.py",
        )
        adapter = github.InMemoryGitHubProjectsAdapter(
            github.GitHubProjectsConfig(owner="the3-inc", project_number=7)
        )
        first = adapter.create_task(
            backend.TaskDraft(
                title="Draft portfolio task review",
                body="Prepare draft.",
                work_unit_id="WU-portfolio",
                due_date="2026-07-03",
                automation_mode="draft_only",
                assignee="omitsuhashi",
                idempotency_key="a",
            )
        ).task_ref
        adapter.create_task(
            backend.TaskDraft(
                title="Manual unrelated task",
                body="Do later.",
                work_unit_id="WU-other",
                due_date="2026-07-04",
                automation_mode="manual",
                assignee="someone",
                idempotency_key="b",
            )
        )

        snapshots = adapter.query_tasks(
            backend.TaskQuery(
                work_unit_id="WU-portfolio",
                due_date="2026-07-03",
                automation_mode="draft_only",
                assignee="omitsuhashi",
            )
        )
        update = adapter.update_fields(first, {"status": "in_progress", "urgency": "high"})
        comment = adapter.add_progress_comment(first, "Prepared review draft.")

        self.assertEqual([snapshot.task_ref for snapshot in snapshots], [first])
        self.assertTrue(update.updated)
        self.assertIn("status", update.changed_fields)
        self.assertTrue(comment.updated)
        with self.assertRaises(ValueError):
            adapter.update_fields(first, {"github_graphql_id": "PVT_kw..."})

    def test_context_contract_validates_and_routes_github_projects_reference(self) -> None:
        result = run_script(VALIDATE_CONTEXT, "--skill", "skills/task-management")

        self.assertEqual(result.returncode, 0, result.stderr)

        inspect = run_script(
            INSPECT_CONTEXT,
            "--skill",
            "skills/task-management",
            "--operation",
            "github-projects",
            "--json",
        )

        self.assertEqual(inspect.returncode, 0, inspect.stderr)
        payload = json.loads(inspect.stdout)
        self.assertEqual(payload["skill"], "task-management")
        self.assertIn(
            "skills/task-management/references/github-projects.md",
            payload["files"],
        )


if __name__ == "__main__":
    unittest.main()
