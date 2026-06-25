from __future__ import annotations

from _helpers import *


class EntrypointTests(unittest.TestCase):
    def test_skill_entrypoint_is_bounded_and_trigger_only(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")
        description = re.search(r"^description: (.+)$", text, re.MULTILINE)

        self.assertIsNotNone(description)
        self.assertEqual(
            description.group(1),
            "Use when implementing approved repository issues after spec, acceptance criteria, and issue decomposition are approved.",
        )
        self.assertLessEqual(len(re.findall(r"\S+", text)), 520)

    def test_skill_entrypoint_names_session_and_worker_semantics(self) -> None:
        text = SKILL_FILE.read_text(encoding="utf-8")

        for required in (
            "one execution coordinator context",
            "planning/grill session must not implement issue work",
            "Do not create user-owned Codex threads",
            "bounded worker-context jobs",
        ):
            self.assertIn(required, text)
