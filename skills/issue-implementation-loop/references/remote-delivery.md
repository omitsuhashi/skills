# Remote Delivery

Default terminal state is local `PR_READY`. Remote writes are optional and require explicit current approval.

## Modes

- `local_only`: no remote writes.
- `per_action`: approve each push/PR/link action separately.
- `batch_draft_prs`: approve exact branches, target, draft PR creation, and issue linkage as a batch.

## Always Separate Approval

- merge
- force push
- ready-for-review change
- deploy
- billing, credential, permission, or production action
- destructive remote action

Remote failure should not stop local implementation/review lanes unless the envelope explicitly makes that remote state a dependency.
