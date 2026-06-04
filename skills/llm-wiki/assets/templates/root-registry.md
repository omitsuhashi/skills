# Knowledge Root Registry

## Roots

| Root ID | Root URI/Path | Scope | Canonical Owner | Read | Write | Draft Target |
|---|---|---|---|---|---|---|
| global | file:/absolute/path/to/global-wiki | system-wide |  | allowed | owned | wiki/drafts/ |
| profile:<name> | file:/absolute/path/to/profile-wiki | profile |  | allowed | owned | wiki/drafts/ |
| role:<name> | file:/absolute/path/to/role-wiki | role |  | allowed | propose | wiki/drafts/ |
| project:<name> | repo:<name>:knowledge | project |  | allowed | propose | wiki/drafts/ |
| project-role:<project>:<role> | repo:<name>:knowledge/roles/<role> | project-role |  | allowed | propose | wiki/drafts/ |

## Column Rules

- `Root ID` is a stable root id used in cross-root links and citations.
- `Root URI/Path` is a root URI. Allowed forms: `file:/absolute/path`, `repo:<repo-name>:<relative-path>`, `memory:<path>`.
- `Scope` is one of `system-wide`, `profile`, `role`, `project`, `project-role`.
- `Canonical Owner` names the authority holder for verified claims. It can be a human, team, role, AI profile, or operating process.
- `Read` is one of `allowed`, `restricted`, `no-access`.
- `Write` is the write mode available to the current actor during routine work. It is one of `owned`, `propose`, `closed`.
- `Draft Target` is where proposed notes go. It is required when `Write` is `propose`, and required for non-owner proposals when `Write` is `owned`.

## Routing Notes

- Example: project-specific customer claims go to `project:<name>`; role-general strategy notes go to `role:<name>` and link back to the project root when needed.
