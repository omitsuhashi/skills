# Knowledge Root Registry

## Roots

| Root ID | Root URI/Path | Scope | Canonical Owner | Read | Write | Draft Target |
|---|---|---|---|---|---|---|
| global | file:/absolute/path/to/global-wiki | system-wide |  | allowed | write-owned |  |
| profile:<name> | file:/absolute/path/to/profile-wiki | profile |  | allowed | write-owned |  |
| role:<name> | file:/absolute/path/to/role-wiki | role |  | allowed | write-with-approval |  |
| project:<name> | repo:<name>:knowledge | project |  | allowed | write-with-approval |  |
| project-role:<project>:<role> | repo:<name>:knowledge/roles/<role> | project-role |  | allowed | write-with-approval |  |

## Column Rules

- `Root ID` is a stable root id used in cross-root links and citations.
- `Root URI/Path` is a root URI. Allowed forms: `file:/absolute/path`, `repo:<repo-name>:<relative-path>`, `memory:<path>`.
- `Scope` is one of `system-wide`, `profile`, `role`, `project`, `project-role`.
- `Canonical Owner` names the authority holder for verified claims. It can be a human, team, role, AI profile, or operating process.
- `Read` is one of `allowed`, `restricted`, `no-access`.
- `Write` is one of `write-owned`, `write-with-approval`, `draft-only`, `read-only`, `no-access`.
- `Draft Target` is where non-owner proposals go when direct verified edits are not allowed. It is required when `Write` is `write-with-approval` or `draft-only`.

## Routing Notes

-
