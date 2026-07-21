from .task_adapter_github_projects import register_adapter_tools


def register(ctx):
    """Register the fixed adapter trio without provider dispatch at load time."""
    register_adapter_tools(ctx)
