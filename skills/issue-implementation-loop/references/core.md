# Core Contract

After issue approval, the coordinator owns packet/envelope, runtime/events, blockers/waits, completion/`PR_READY`, reporting, and remote boundaries.

Planning does not implement. Workers own assigned branch/worktree/scope/evidence; reviewers own packet-scoped findings.

## Input Packet

Input Packet v2 is the only executable packet:

- `schema_version: 2`, `epic_id`, and repo-relative `artifact_root`
- required `spec_binding` and complete `approval_evidence`
- complete `work_items[]` execution intent
- `delivery_intent`: use `batch_issue_prs` for issue PRs into `codex/<epic-id>/epic-base` and a final PR to `main`

Use `assets/templates/input-packet.json` / `assets/schemas/input-packet.schema.json` and run `validate_input_packet.py`. Seal only when `check_capabilities.py --json` reports `approved_spec_seal` supported; otherwise `PLATFORM_UNSUPPORTED`.

## Output Contract

Return Execution Result v2 with the active binding, envelope/runtime identity, per-issue commit/review/verification state, requests, delivery candidates, and residual risks. Start from `assets/templates/execution-result.json` and run `validate_execution_result.py` before terminal completion; v1 is unsupported.

Execution Envelope v4 pins Input Packet v2 through `approved_spec_binding`, including gate commit ancestry and exact packet/spec blobs.

## Binding Gate Map

Prepare; dispatch and fix redispatch; review dispatch and approval intake; resume and rebuild; completion; and delivery all freshly verify the same active `approved_spec_binding`. Read-only status may return `binding_valid=false`, but state advance remains blocked. Changes to spec bytes, `spec_binding`, or `approval_evidence` return to the human Spec Gate for a new approval and seal. execution-intent-only packet drift is only an example: any other sealed packet byte drift while `spec_binding` and `approval_evidence` remain exact, including other packet fields and serialization or whitespace-only drift, returns to the Execution Plan Gate for reconciliation and revalidation. Restore unintended drift; reseal only when the changed bytes are intended, without a new human Spec Gate approval. Both routes start a new envelope/runtime epoch; never reuse old reports/results.

## Non-Goals

- Do not redesign issues, implement from the coordinator, add a generic scheduler/framework, or write remotely without envelope and human authorization.
