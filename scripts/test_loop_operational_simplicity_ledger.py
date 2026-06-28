from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ISSUE_LEDGER = REPO_ROOT / "knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md"
INDEX = REPO_ROOT / "knowledge/index.md"
LOG = REPO_ROOT / "knowledge/log.md"


class LoopOperationalSimplicityLedgerTests(unittest.TestCase):
    def test_final_ledger_records_lsos004_completion_and_remote_boundary(self) -> None:
        text = ISSUE_LEDGER.read_text(encoding="utf-8")

        self.assertIn("| loop-skill-operational-simplicity | LSOS-004 |", text)
        self.assertIn("| loop-skill-operational-simplicity | LSOS-004 | regression tests と wiki ledger を更新する | 承認済み | COMPLETE |", text)

        lsos004 = text.split("## LSOS-004", 1)[1]
        for required in (
            "- [x] 適用基準、mental model discoverability、workflow complexity JSON shape が tests で固定されている。",
            "- [x] `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に各 issue の実装 evidence、検証結果、review 結果が反映されている。",
            "- [x] `knowledge/index.md` と `knowledge/log.md` が final ledger を発見できる。",
            "- [x] full verification が通る。",
            "- [x] remote write は行われていない。",
            "### 実装 evidence",
            "Regression coverage:",
            "Review result:",
            "Remote write は行っていない。",
        ):
            self.assertIn(required, lsos004)

    def test_index_and_log_make_final_ledger_discoverable(self) -> None:
        index_text = INDEX.read_text(encoding="utf-8")
        log_text = LOG.read_text(encoding="utf-8")

        self.assertIn("[Loop Skill Operational Simplicity Issues](wiki/syntheses/loop-skill-operational-simplicity-issues.md)", index_text)
        self.assertIn("final ledger", index_text)
        self.assertIn("implementation evidence", index_text)

        self.assertIn("[2026-06-28] implementation | Loop skill operational simplicity LSOS-004 regression ledger", log_text)
        self.assertIn("knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md", log_text)
        self.assertIn("full verification", log_text)
        self.assertIn("remote policy は `local_only`", log_text)

    def test_final_ledger_does_not_retain_stale_status_language(self) -> None:
        text = ISSUE_LEDGER.read_text(encoding="utf-8")

        for stale in (
            "実装、push、PR 作成、remote write は未承認",
            "LSOS-004 は LSOS-003 完了待ち",
        ):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
