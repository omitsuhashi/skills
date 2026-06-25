# Grill to PR Loop Workflow Router

Use this reference after loading `references/core.md`. This file is only a routing layer: select the current operation, then load the matching one-level references below. Keep lifecycle, responsibilities, gates, local-first rules, and remote approval boundaries in `core.md`.

End-to-end coordination does not authorize same-session issue implementation. Execution mechanics stay delegated to `issue-implementation-loop`.

## Detail References

- Global lifecycle and gates: `core.md`
- Planning, durable artifacts, spec minimum, and approval gates: `planning-contract.md`
- Japanese local issue ledger, blocker graph, and ledger update invariant: `local-issue-ledger.md`
- Execution packet, branch/base/commit policy, and `issue-implementation-loop` handoff: `execution-handoff.md`
- GitHub mirror, issue PRs, final PR, and remote approval policy: `remote-delivery.md`
- Known failure modes and corrections: `common-mistakes.md`

## Read Sets

- `intake`, `grill`, `spec`: read `planning-contract.md`.
- `issue-gate`: read `planning-contract.md` and `local-issue-ledger.md`.
- `execution-plan`: read `planning-contract.md`, `local-issue-ledger.md`, and `execution-handoff.md`.
- `resume`, `completion-report`: read `local-issue-ledger.md` and `execution-handoff.md`; add `remote-delivery.md` only if remote actions were approved or attempted.
- `delivery`: read `remote-delivery.md`.
- `ambiguity-check`: read `common-mistakes.md`.

## Sub-Skill Contract

- Use `grill-with-docs` for unresolved design interrogation and durable design context.
- Use `to-prd` when approved conversation/docs should become a PRD or spec packet. Keep local-first unless remote publication is approved.
- Use `to-issues` only for draft vertical-slice breakdown and quiz/review until the GitHub Mirror Gate passes.
- Use `issue-implementation-loop` only after local issues and the normalized execution packet are approved.
- Use GitHub/PR specialist workflows only after explicit remote-write approval.

When sub-skills assume remote tracker writes, this workflow's local-first and explicit-approval gates override them.

## Stop If Routing Fails

If the current operation does not map cleanly to a read set, stop and read `common-mistakes.md` before continuing. If the ambiguity changes approved scope, return to the relevant gate.
