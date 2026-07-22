# Task Management Plugin

`task-management` is the backend-neutral consumer surface for task work. Codex
receives the bundled workflow skill. Hermes additionally registers the native
public tools below from `plugin.yaml` and `__init__.py`:

- `task-management-read:task_query`
- `task-management-write:task_preflight`
- `task-management-write:task_apply`

Version `0.4.0` uses task interface v2 and adapter contract v2. It does not
bundle an MCP server, provider client, credentials, or provider-specific field
mapping.

## Dual-host install

```bash
hermes plugins install git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```

Codex discovers `skills/task-management/SKILL.md` from
`.codex-plugin/plugin.json`. Hermes registers that same skill with
`ctx.register_skill`, so the shared `SKILL.md` is the workflow authority on both
hosts. The optional `$decide-in-order` companion remains a separate install;
mechanical reads and already-reviewed operations continue when it is absent,
while unresolved material decisions stop for human review.

```bash
hermes skills install omitsuhashi/skills/skills/decide-in-order
hermes skills list
```

Mechanical task operations continue if it is unavailable; do not claim that
decision support ran.

Repository compatibility is not live availability. An approved live check must
confirm the enabled version with `hermes plugins list --plain --no-bundled`; it
must match `plugin.yaml`.
Ordinary repository validation does not install, enable, or update a live
profile.

## Host-owned route

Set one credential-free unified route file:

```bash
export TASK_MANAGEMENT_ROUTES_FILE=/host-owned/task-backends.toml
```

Start from `config/task-backends.example.toml`. Contract version 2 binds each
backend to exactly one `query`, `preflight`, and `apply` adapter tool plus
logical destinations. Callers provide only neutral task values and an opaque
`destination_ref`; they do not select adapter tools, route files, GitHub owners,
repositories, project numbers, field IDs, or credentials.

The example pairs with `task-adapter-github-projects` and therefore uses
`tasks:portfolio-os` plus the opaque `task-content:portfolio-os`. Install and
configure that adapter separately. The route file and adapter config must agree
on those opaque references.

`local_json` is retained only for plugin-owned tests and the isolated read
smoke. It is not a normal runtime backend, an operator runtime backend, or a
mutable task store.

## Public flow

1. `task_query` resolves the host route, dispatches its fixed adapter query
   tool, and returns only normalized `TaskSnapshotResult` data.
2. `task_preflight` validates one operation, resolves the same route, performs
   read-only adapter preflight, and returns a reviewable `ApprovalPreview` plus
   digest. Readiness never grants write approval.
3. A human approves the exact preview, or a host policy uses
   `confidence_authorized` only when the preflight explicitly permits it.
4. `task_apply` reloads the route, re-runs preflight, verifies route, operation,
   side-effect, and digest identity, then dispatches the fixed adapter apply
   tool once.
5. The facade returns a backend-neutral `TaskWriteResult`. Partial or unknown
   outcomes require inspection; only an explicit provider response stating
   that no write occurred may be retryable.

Approval mismatch, human-required confidence decisions, missing route/config,
and blocked preflight all stop before adapter apply. The task-management package
never calls raw GitHub MCP tools directly.

## Verification

Hermetic tests and smokes use temporary config, a fake public adapter/MCP
boundary, and temporary `HERMES_HOME` state. They make no network call and edit
no live profile:

```bash
python3 -m unittest discover -s plugins/task-management/tests
python3 plugins/task-management/scripts/smoke_test_hermes_read.py
python3 plugins/task-management/scripts/smoke_test_hermes_write.py
```

The full fake end-to-end test lives with the GitHub adapter so both plugin
entrypoints and the adapter's provider boundary are exercised together.

## Live activation boundary

Repository completion proves only code, contract, manifest, docs, and hermetic
runtime behavior. Installing the plugins, configuring the route and adapter,
registering GitHub MCP tools, authenticating, enabling toolsets, or mutating a
real GitHub Project/Issue requires a separate live activation gate.

## Update caveat

A subdirectory install usually does not retain `.git`, so
`hermes plugins update task-management` may report that it is not a git
checkout. Refresh only in an approved live workflow:

```bash
hermes plugins install --force git@github.com:omitsuhashi/skills.git#plugins/task-management
hermes plugins enable task-management
```
