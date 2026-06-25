from __future__ import annotations

from pathlib import Path


def skill_roots() -> list[Path]:
    home = Path.home()
    roots = [
        Path.cwd() / "skills",
        Path.cwd() / ".agents" / "skills",
        Path.cwd() / "agents" / "skills",
        home / ".agents" / "skills",
        home / ".codex" / "skills",
    ]
    cache = home / ".codex" / "plugins" / "cache"
    if cache.exists():
        for pattern in ("*/skills", "*/*/skills", "*/*/*/skills"):
            roots.extend(path for path in cache.glob(pattern) if path.is_dir())
    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if root not in seen:
            unique.append(root)
            seen.add(root)
    return unique


def find_skill(name: str) -> str | None:
    for root in skill_roots():
        skill_file = root / name / "SKILL.md"
        if skill_file.exists():
            return str(skill_file)
    return None
