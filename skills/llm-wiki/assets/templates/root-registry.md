# Knowledge Root Registry

## Roots

| Root ID | Root URI/Path | Scope | Canonical Owner | Read | Write | Draft Target |
|---|---|---|---|---|---|---|
| shared | file:/absolute/path/to/shared-wiki | shared policy and operations | <canonical-owner> | allowed | owned | wiki/drafts/ |
| actor:<name> | file:/absolute/path/to/actor-wiki | actor working memory | <canonical-owner> | allowed | owned | wiki/drafts/ |
| domain:<name> | repo:<name>:knowledge | product or domain knowledge | <canonical-owner> | allowed | propose | wiki/drafts/ |

## Column Rules

- `Root ID` is a stable root id used in cross-root links and citations.
- `Root URI/Path` is a root URI. Allowed forms: `file:/absolute/path`, `repo:<repo-name>:<relative-path>`, `memory:<path>`.
- `Scope` describes the local ownership boundary. Use the taxonomy that matches the system; the examples above are not mandatory categories.
- `Canonical Owner` names the authority holder for verified claims. Replace `<canonical-owner>` with a human, team, role, AI profile, or operating process before using the registry.
- `Read` is one of `allowed`, `restricted`, `no-access`.
- `Write` is the write mode available to the current actor during routine work. It is one of `owned`, `propose`, `closed`.
- Direct canonical update is allowed only when the actor is the canonical owner, `Write` is `owned`, and the local contract or adapter permits the action.
- `Draft Target` is where proposed notes go. It is required when `Write` is `propose`, and required for non-owner proposals when `Write` is `owned`.
- `Draft Target` must resolve as a root-relative directory inside the target root. Prefer `wiki/drafts/`. Do not use absolute paths, `~`, `..`, or paths that resolve outside the target root.

## Routing Notes

- Example: domain-specific customer claims go to that domain root; reusable actor workflow notes go to the actor root and link back to the domain root when needed.
- Cross-root links and citations should use `root-id:path/inside/root.md`; do not copy private or restricted source text into roots without access.
