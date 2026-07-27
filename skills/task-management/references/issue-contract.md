# Issue Contract

## Title

Write the observable result, not an internal activity label. Keep the title concise enough to scan in Project views.

## Body

```markdown
## Outcome
The result this Issue must achieve.

## Context
Why the work is needed and the confirmed decision context.

## Acceptance criteria
- [ ] An observable completion condition.

## References
Related Issues, PRs, durable specifications, files, or confirmed external references.

<!-- portfolio-os-task-key: sha256:<64 lowercase hex digits> -->
```

Do not store raw conversation transcripts, internal prompts, hidden reasoning, credentials, or agent names. Prefer durable repository references for implementation work. Use existing repository labels and Issue types rather than imposing a global taxonomy.

## Idempotency key

End every new Issue body with exactly one stable marker in the documented format. Its idempotency key is the SHA-256 digest of the normalized repository, Project URL, Outcome, Acceptance Criteria, and durable References. Normalize these inputs before deriving the key so equivalent input produces the same marker.

## Creation gate

Do not create the Issue when the outcome or acceptance criteria cannot support an observable completion decision. Ask one decision-changing question and then resume.

## Duplicate handling

Search the exact stable marker in open Issues and current Project items read-only before title similarity. Reuse the matching Issue and never create a second marker for the same idempotency key. Similar titles alone are not sufficient. After a partial failure, resume from the returned Issue URL and never create a second Issue for the same operation.

When reusing an Issue or Project item, never create a second Issue. Preserve its current fields unless the requested operation or a documented unfinished partial-failure step requires a particular missing write. Do not reapply creation defaults or repeat completed steps.
