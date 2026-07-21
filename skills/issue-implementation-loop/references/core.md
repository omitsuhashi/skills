# Core Contract

After issue approval, the coordinator owns packet/envelope, runtime/events, blockers/waits, completion/`PR_READY`, reports, and remote boundaries. Planning does not implement; workers own assigned branch/worktree/scope/evidence, and reviewers own packet-scoped findings.

## Input Packet

Input Packet v2 is the only executable packet:

- `schema_version: 2`, `epic_id`, repo-relative `artifact_root`
- required `spec_binding`, complete `approval_evidence` and `work_items[]` intent
- `delivery_intent`: `batch_issue_prs` sends issue PRs to `codex/<epic-id>/epic-base`, then a final PR to `main`

Use the packet template/schema and `validate_input_packet.py`. Seal only if `check_capabilities.py --json` supports `approved_spec_seal`; otherwise `PLATFORM_UNSUPPORTED`.

## Output Contract

Return Execution Result v2 with active binding, envelope/runtime identity, per-issue commit/review/verification, requests, delivery candidates, and residual risks. Start from its template and run `validate_execution_result.py` before completion; v1 is unsupported.

Execution Envelope v4 pins Input Packet v2 through `approved_spec_binding`, including gate commit ancestry and exact packet/spec blobs.

## Binding Gate Map

Prepare; dispatch and fix redispatch; review dispatch and approval intake; resume and rebuild; completion; and delivery all freshly verify the same active `approved_spec_binding`. Read-only status may return `binding_valid=false`, but state advance remains blocked. Packet drift has three outcomes. Exact restoration of unintended packet byte drift plus fresh validation retains the existing approved binding, Envelope revision, and runtime epoch. An intended non-spec packet byte change goes through the Execution Plan Gate for reconciliation and revalidation, a new reseal, and a new Envelope revision and runtime epoch, without a new human Spec Gate approval. A change to spec bytes, `spec_binding`, or `approval_evidence` goes through the human Spec Gate for a new approval and seal, then a new Envelope revision and runtime epoch. This exhaustive non-spec route covers execution-intent-only packet drift and any other sealed packet byte drift while `spec_binding` and `approval_evidence` remain exact, including other packet fields and serialization or whitespace-only drift. On it, reseal only when the changed bytes are intended; exact restoration reuses the seal. Never reuse old reports/results across either new-seal epoch.

## Non-Goals

- Do not redesign issues, implement from the coordinator, add a generic scheduler/framework, or write remotely without envelope and human authorization.
