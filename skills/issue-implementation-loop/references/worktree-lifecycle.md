# Worktree Lifecycle

Use one branch/worktree reservation per approved issue. For `batch_issue_prs`, also track `epic_base` as a top-level delivery branch resource. The coordinator owns creation and activation decisions.

## States

- `reserved`: branch/path approved but no physical worktree yet.
- `create_on_run`: create the worktree when dispatching the issue.
- `active`: worktree exists and is assigned.
- `missing`: expected worktree is absent during recovery.

`epic_base` uses the same state names but is not an issue work item. It may omit `worktree_path` when no physical epic-base checkout is needed.

## Procedure

1. Validate envelope branch/path uniqueness.
2. Reconcile existing branches, worktrees, and filesystem paths.
3. Stop only the affected issue when its reservation collides.
4. Create physical worktrees only for runnable issues.
5. Never reuse one active worktree for multiple concurrent issues.
6. Do not reset, clean, delete, or move worktrees without explicit approval.

For `batch_issue_prs`, do not create the final PR until `epic_base.ref` exists and issue PR merge state has been recorded.

Use:

```bash
python3 <skill-dir>/scripts/reconcile_git_state.py <execution-envelope.json> --json
```
