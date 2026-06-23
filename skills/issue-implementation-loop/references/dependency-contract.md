# Dependency Contract

Represent dependency edges as `blocked issue -> required prerequisite`.

## Edge Fields

- `issue`: prerequisite issue ID.
- `strength`: `hard` or `soft`
- `release_on`: `artifact_ready`, `review_approved`, `integrated`, `pr_opened`, `pr_merged`, `human_decision`, or `external_condition`
- `base_effect`: `none`, `branch_from_blocker_head`, or `branch_from_integration_head`

## Rules

- Validate references and cycles before execution.
- A hard edge must explain why downstream cannot safely start yet.
- `release_on` must be observable from a coordinator event or runtime state.
- `base_effect` must describe whether downstream branch creation needs blocker code.
- Do not let downstream workers merge multiple blocker heads ad hoc. Use an approved integration work item or integration branch.
- Release descendants immediately after the release condition is observed; do not wait for unrelated wave siblings.
