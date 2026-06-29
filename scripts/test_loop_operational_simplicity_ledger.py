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
        self.assertIn("| loop-skill-operational-simplicity | LSOS-004 | regression tests と wiki 台帳を更新する | 承認済み | 完了 |", text)

        lsos004 = text.split("## LSOS-004", 1)[1]
        for required in (
            "- [x] 適用基準、役割境界モデルの discoverability、workflow complexity JSON shape が tests で固定されている。",
            "- [x] `knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md` に各 issue の実装証跡、検証結果、レビュー結果が反映されている。",
            "- [x] `knowledge/index.md` と `knowledge/log.md` が final ledger を発見できる。",
            "- [x] full verification が通る。",
            "- [x] remote write は行われていない。",
            "### 実装証跡",
            "Regression coverage:",
            "レビュー結果:",
            "実装ループ中の remote write は行っていない。",
        ):
            self.assertIn(required, lsos004)

    def test_index_and_log_make_final_ledger_discoverable(self) -> None:
        index_text = INDEX.read_text(encoding="utf-8")
        log_text = LOG.read_text(encoding="utf-8")

        self.assertIn("[Loop Skill 運用単純化 Issue 台帳](wiki/syntheses/loop-skill-operational-simplicity-issues.md)", index_text)
        self.assertIn("final ledger", index_text)
        self.assertIn("実装証跡", index_text)

        self.assertIn("[2026-06-29] docs | Loop skill 運用単純化 docs 日本語化", log_text)
        self.assertIn("knowledge/wiki/syntheses/loop-skill-operational-simplicity-issues.md", log_text)
        self.assertIn("日本語ベースの見出し・本文", log_text)
        self.assertIn("draft PR #22 作成は実施済み", log_text)

    def test_final_ledger_does_not_retain_stale_status_language(self) -> None:
        text = ISSUE_LEDGER.read_text(encoding="utf-8")

        for stale in (
            "実装、push、PR 作成、remote write は未承認",
            "LSOS-004 は LSOS-003 完了待ち",
            "| 承認済み | COMPLETE |",
        ):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main()
