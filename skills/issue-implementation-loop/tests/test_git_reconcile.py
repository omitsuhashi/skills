from __future__ import annotations

from _helpers import *


class GitReconcileTests(unittest.TestCase):
    def test_reconcile_git_state_reports_missing_epic_base_branch_for_batch_issue_prs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
            envelope = base_envelope()
            envelope["epic_id"] = "missing-epic-base"
            envelope["epic_base"] = {
                "ref": "codex/missing-epic-base/epic-base",
                "sha": BASE_SHA,
                "branch_state": "reserved",
            }
            envelope["remote_write_policy"] = {
                "mode": "batch_issue_prs",
                "approved_actions": [],
                "issue_prs": {
                    "base": "epic_base.ref",
                    "merge": "agent_default_with_human_escalation",
                },
                "final_pr": {
                    "head": "epic_base.ref",
                    "base": "main",
                    "merge": "human_only",
                },
            }
            envelope["work_items"]["G2PR-001"]["branch"] = "codex/missing-epic-base/G2PR-001-a"
            envelope["work_items"]["G2PR-002"]["branch"] = "codex/missing-epic-base/G2PR-002-b"
            envelope["work_items"]["G2PR-003"]["branch"] = "codex/missing-epic-base/G2PR-003-c"
            envelope_path = Path(tmp) / "envelope.json"
            write_json(envelope_path, envelope)

            result = run_script(
                "reconcile_git_state.py",
                str(envelope_path),
                "--repo",
                str(repo),
                "--json",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["epic_base"]["branch_exists"])
            self.assertEqual(payload["collisions"][0]["type"], "missing_epic_base_branch")
