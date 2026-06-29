# TaskDraft Composition Contract

This reference defines how the task-management skill turns capture or chat text into a backend-neutral `TaskDraft`. It is a composition and review contract only; backend task state belongs to the selected task backend.

## TaskDraft Fields

Every create preview should be built from these neutral fields:

- `title`: one action-oriented sentence, written as the task owner should see it in the backend.
- `body`: concise operational context, expected outcome, acceptance notes, and review questions.
- `task_type`: one of `implementation`, `review`, `research`, `decision`, `coordination`, `maintenance`, or `inbox_triage`.
- `work_unit_id`: stable routing key for the work unit. Use `inbox` when the correct work unit is unknown.
- `work_unit_name`: human display label for the work unit. Use `Inbox` when `work_unit_id` falls back to `inbox`.
- `due_date`: ISO date when provided or clearly implied; otherwise omit it.
- `urgency`: `low`, `normal`, `high`, or `blocked`.
- `importance`: `low`, `normal`, `high`, or `critical`.
- `automation_mode`: `manual_only`, `assistive`, or `trusted_after_approval`.
- `approval_required`: boolean. State-changing adapter dispatch requires explicit approval.
- `source_ref`: a sanitized source summary or durable source trail reference, not a raw platform payload.
- `review_notes`: uncertainties, routing rationale, and fields the human should confirm.

## Title Rules

- Start with a verb or concrete outcome: "Implement", "Review", "Decide", "Prepare", "Follow up".
- Include the object of work and the smallest useful scope.
- Avoid channel prefixes, raw sender names, platform ids, timestamps, or routing metadata.
- Keep it short enough to scan in a project board; move context and caveats to `body`.

Good examples:

- `Implement task create preview contract`
- `Review Portfolio OS inbox fallback behavior`
- `Decide backend destination for task-management`

Poor examples:

- `Discord 123456789 says maybe do the task thing`
- `TODO`
- `Need help with all task management work`

## Body Rules

The body should be useful after the source chat has disappeared. Compose it with these sections when available:

1. `Outcome`: the concrete result expected from the task.
2. `Context`: summarized source context and why this task exists.
3. `Acceptance`: observable completion checks.
4. `Review`: unclear fields or decisions that need human confirmation.

Do not paste the raw chat transcript or transport envelope. Summarize only the task-relevant content.

## Taxonomy Guidance

Use the narrowest `task_type` that matches the requested work:

| task_type | Use when | Typical title shape |
| --- | --- | --- |
| `implementation` | Code, docs, config, or artifact changes are requested. | `Implement <specific change>` |
| `review` | The work is evaluation, critique, QA, or signoff. | `Review <surface> for <risk>` |
| `research` | The task requires gathering evidence before a decision. | `Research <question>` |
| `decision` | The output is a choice, approval, or architecture direction. | `Decide <choice area>` |
| `coordination` | The main work is follow-up, scheduling, handoff, or dependency release. | `Follow up on <dependency>` |
| `maintenance` | The work keeps an existing process healthy. | `Refresh <asset or workflow>` |
| `inbox_triage` | The source is actionable but cannot be routed confidently. | `Triage <source summary>` |

Urgency describes time pressure. Importance describes business or product impact. Do not make a task `high` urgency only because the source text sounds emphatic.

Automation modes:

- `manual_only`: human must perform or approve the work outside automation.
- `assistive`: an agent can draft, inspect, or prepare artifacts, but state-changing writes still need approval.
- `trusted_after_approval`: the task may be executed by an approved automation policy after the review gate. This initial plugin scope does not create that policy.

## Inbox Fallback

Use `work_unit_id: inbox` only when the source is actionable but the correct work unit cannot be determined from caller context, explicit override, profile config, or durable source trail.

`inbox` means "needs human routing during review"; it is not a permanent work unit and it is not a local Portfolio OS task state store. A preview using the fallback must set `work_unit_name: Inbox` and include a review note asking the human to confirm or replace the work unit before adapter dispatch.

## Source Boundary

`source_ref` may contain:

- a sanitized source summary
- a durable source trail reference supplied by the caller
- a link or opaque reference already approved for task context

`TaskDraft` must not store:

- raw platform payloads
- platform message ids
- transport metadata such as channel ids, event ids, webhook headers, request headers, delivery receipts, or auth context
- credentials, tokens, cookies, or MCP server configuration

If exact provenance is needed, store it in the caller-owned source trail and pass only a sanitized reference into `TaskDraft`.

## Review Preview Expectations

Before any adapter-facing create preview is approved, show:

- task title and body
- task type, urgency, importance, automation mode, and approval requirement
- `work_unit_id` and `work_unit_name`, including `inbox` / `Inbox` fallback when used
- sanitized `source_ref`
- routing rationale and review notes
- the selected backend and destination when those are already known

The preview is for human review. It is not proof that an external backend write occurred.
