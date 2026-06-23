# Worktree Lifecycle

Use one branch/worktree reservation per approved issue. The coordinator owns creation and activation decisions.

## States

- `reserved`: branch/path approved but no physical worktree yet.
- `create_on_run`: create the worktree when dispatching the issue.
- `active`: worktree exists and is assigned.
- `missing`: expected worktree is absent during recovery.

## Procedure

1. Validate envelope branch/path uniqueness.
2. Reconcile existing branches, worktrees, and filesystem paths.
3. Stop only the affected issue when its reservation collides.
4. Create physical worktrees only for runnable issues.
5. Never reuse one active worktree for multiple concurrent issues.
6. Do not reset, clean, delete, or move worktrees without explicit approval.

Use:

```bash
python3 <skill-dir>/scripts/reconcile_git_state.py <execution-envelope.json> --json
```
