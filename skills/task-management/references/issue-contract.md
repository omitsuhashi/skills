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
```

Do not store raw conversation transcripts, internal prompts, hidden reasoning, credentials, or agent names. Prefer durable repository references for implementation work. Use existing repository labels and Issue types rather than imposing a global taxonomy.

## Creation gate

Do not create the Issue when the outcome or acceptance criteria cannot support an observable completion decision. Ask one decision-changing question and then resume.

## Duplicate handling

Search open Issues and current Project items read-only before creation. Reuse an Issue only when repository, outcome, and references make identity high-confidence. Similar titles alone are not sufficient. After a partial failure, resume from the returned Issue URL and never create a second Issue for the same operation.

When reusing an Issue or Project item, never create a second Issue. Preserve its current fields unless the requested operation or a documented unfinished partial-failure step requires a particular missing write. Do not reapply creation defaults or repeat completed steps.
