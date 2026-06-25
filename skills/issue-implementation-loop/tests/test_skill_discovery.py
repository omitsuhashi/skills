from __future__ import annotations

from _helpers import *


class SkillDiscoveryTests(unittest.TestCase):
    def test_skill_roots_prefers_repo_local_over_global(self) -> None:
        common = load_common_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            local_skill = repo / "skills" / "example" / "SKILL.md"
            global_skill = home / ".agents" / "skills" / "example" / "SKILL.md"
            local_skill.parent.mkdir(parents=True)
            global_skill.parent.mkdir(parents=True)
            local_skill.write_text("---\nname: example\ndescription: local\n---\n", encoding="utf-8")
            global_skill.write_text("---\nname: example\ndescription: global\n---\n", encoding="utf-8")

            previous_cwd = Path.cwd()
            try:
                os.chdir(repo)
                with mock.patch.object(common.Path, "home", return_value=home):
                    roots = common.skill_roots()
                    found = common.find_skill("example")
            finally:
                os.chdir(previous_cwd)

        self.assertEqual(roots[:3], [
            repo.resolve() / "skills",
            repo.resolve() / ".agents" / "skills",
            repo.resolve() / "agents" / "skills",
        ])
        self.assertEqual(found, str(local_skill.resolve()))
