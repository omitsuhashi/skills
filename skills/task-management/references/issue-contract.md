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

Do not store raw conversation transcripts, internal prompts, hidden reasoning, credentials, or agent names. Do not store or return credential, secret, or authentication token values. Prefer durable repository references for implementation work. Use existing repository labels and Issue types rather than imposing a global taxonomy.

## Creation gate

Do not create the Issue when the outcome or acceptance criteria cannot support an observable completion decision. Ask one decision-changing question and then resume.

## Duplicate handling

Search open Issues and current Project items read-only before creation. Duplicate discovery is a completeness-required investigation: keep at most 50 returned items but follow opaque provider continuations and reconcile the aggregate discovery to source exhaustion. Classify the exhausted discovery as `none`, `unique_high_confidence`, or `ambiguous_or_multiple`. Repository, outcome, and references must establish a high-confidence identity; similar titles alone are not sufficient. After a partial failure, resume from the returned Issue URL and never create a second Issue for the same operation.

Only a `complete` / `source_exhausted` discovery with outcome `none` may claim
no duplicate and set `create_allowed=true`. Outcome `unique_high_confidence`
reuses the existing Issue only after exhausted discovery. Outcome
`ambiguous_or_multiple` stops for resolution. A `partial` or `truncated`
discovery always sets `create_allowed=false` and stops, regardless of observed
candidates.

### Duplicate discovery decision matrix

| Envelope | Discovery outcome | no_duplicate_claim | create_allowed | reuse_existing | Action |
| --- | --- | --- | --- | --- | --- |
| `complete` / `source_exhausted` | `none` | true | true | false | proceed to create |
| `complete` / `source_exhausted` | `unique_high_confidence` | false | false | true | reuse existing |
| `complete` / `source_exhausted` | `ambiguous_or_multiple` | false | false | false | stop |
| `partial` or `truncated` | any | false | false | false | stop |

When reusing an Issue or Project item, never create a second Issue. Preserve its current fields unless the requested operation or a documented unfinished partial-failure step requires a particular missing write. Do not reapply creation defaults or repeat completed steps.

For `register_existing_issue`, add only the resolved Project membership and
explicitly requested Project fields or applicable defaults. Preserve
`assignees`, `labels`, `milestone`, `issue_type`, `parent_issue`, and
`sub_issues`, and require their exact readback with the requested Project
changes.
