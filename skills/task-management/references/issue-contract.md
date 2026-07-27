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

End every new Issue body with exactly one stable marker. Derive it from these
canonical bytes so every supported host and a later retry produce the same identity:

1. Build a JSON object in this fixed key order: `repository`, `project_url`,
   `outcome`, `acceptance_criteria`, `references`.
2. Normalize `repository` as exactly one `OWNER/REPOSITORY` pair: trim surrounding
   ASCII whitespace and ASCII-lowercase both components.
3. Normalize `project_url` to
   `https://github.com/{orgs|users}/{ascii-lowercase-owner}/projects/{positive-decimal-number}`.
   ASCII-lowercase the scheme, host, kind, and owner; remove a trailing slash;
   render the number without leading zeroes; reject rather than retain a query,
   fragment, credentials, port, extra path segment, or another host.
4. For every text scalar, apply Unicode NFC, convert CRLF and bare CR to LF,
   trim ASCII horizontal whitespace (`U+0009`, `U+000B`, `U+000C`, `U+0020`)
   at each line edge, collapse each internal run of that whitespace to one
   `U+0020`, and remove leading and trailing empty lines. Preserve internal LF
   and the order of Acceptance Criteria.
5. Represent Acceptance Criteria as a JSON array of normalized strings. A
   missing or null collection becomes `[]`; the creation gate still rejects an
   empty result.
6. Represent durable References as a JSON array. A missing or null collection
   becomes `[]`. Normalize each entry as text, remove empty entries, deduplicate
   exact normalized entries, and sort them by unsigned UTF-8 byte order.
7. Serialize compact RFC 8259 JSON with the fixed key order, UTF-8 characters
   unescaped except where JSON requires escaping, separators `,` and `:`, no
   BOM, and no trailing newline.
8. Compute SHA-256 over those exact UTF-8 JSON bytes. The key is
   `sha256:` plus 64 lowercase hexadecimal digits; the marker is exactly
   `<!-- portfolio-os-task-key: sha256:<64 lowercase hex digits> -->`.

Canonical vector:

```json
{"repository":"the3-inc/companies","project_url":"https://github.com/orgs/the3-inc/projects/7","outcome":"Café launch\nnow","acceptance_criteria":["Ready for use","Docs\npublished"],"references":["https://example.com/a","specs/plan.md"]}
```

The vector has no trailing newline in the hashed bytes. Its digest is
`3f9fc3661920a8d3fefaa15a83789083a99521dd61994da2b396f5a03b6ed7f2`.

## Creation gate

Do not create the Issue when the outcome or acceptance criteria cannot support an observable completion decision. Ask one decision-changing question and then resume.

## Duplicate handling

Search the exact stable marker in open Issues and current Project items read-only before title similarity. Zero matches may enter the create route. Multiple matches are ambiguous and block. One match makes normal `task_create` return `duplicate` with zero writes, even when that Issue is not in the selected Project; never turn a duplicate create into implicit registration. Similar titles alone are not sufficient.

Only `task_project_register` may resume Project registration, and only from an exact prior `task_create` partial receipt that binds the repository, Project URL, marker, Issue identity, and unfinished state; never create a second Issue. Preserve its current fields when an Issue or Project item already exists. Change a field only when the requested operation explicitly targets it; a documented unfinished partial-failure step never authorizes creation defaults on an existing item. Do not reapply creation defaults or repeat completed steps.
