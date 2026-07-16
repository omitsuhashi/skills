from pathlib import Path

from .task_management.read_adapter import register_read_tool


def register(ctx):
    plugin_dir = Path(__file__).parent
    skill_path = plugin_dir / "skills" / "task-management" / "SKILL.md"
    ctx.register_skill(
        "task-management",
        skill_path,
        description="Backend-neutral task intake and task backend routing workflow.",
    )
    register_read_tool(ctx)
