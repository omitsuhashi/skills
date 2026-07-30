# llm-wiki Authoring Responsibility Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `llm-wiki` を durable knowledge の structural / lifecycle coordinator に限定し、Obsidian 文書の serialization を選択済み authoring skill へ fail-closed で委譲する。

**Architecture:** portable contract は operation、topology、authority、semantic schema、relation identity を所有し、selected authoring profile の discovery と readable `SKILL.md` を write 前の gate にする。既存の `context-contract.toml` は entrypoint + core + topology + mode の四つの structural read-set を維持し、authoring skill を内部 reference、sidecar、runtime 固有 metadata として追加しない。semantic template は `llm-wiki` に残すが、headings、frontmatter、link notation、callout、embed、presentation の serialization instruction は selected authoring skill にだけ残す。

**Tech Stack:** portable `SKILL.md` contract、TOML context contract、Markdown / Obsidian WikiLink、Python `unittest`、既存 repository validators。

## Global Constraints

- Baseline は `5f08fe27e2899865dea9e4347e5301d126744c90`。実装は `llm-wiki-authoring-separation-planning` planning worktree 内だけで行う。
- 現在の approved source of truth は [[llm-wiki-authoring-responsibility-separation-spec]]。`raw/**` は read-only で、external installed `obsidian-markdown` skill は変更しない。
- portable `SKILL.md` contract は non-empty Inputs、Outputs、Required Capabilities を宣言し、runtime / model / provider / agent 固有 metadata、authoring contract sidecar、structured authoring result を正本にしない。
- `llm-wiki` は topology、authority、routing、lifecycle、semantic field / relation preservation、index/log effect だけを所有する。Markdown / Obsidian parser、renderer、formatter、syntax validator、fallback renderer を追加しない。
- この knowledge root は local contract で `obsidian` profile、日本語本文、Obsidian compatibility requirement を選択する。internal note link は wikilink、external URL は standard Markdown link のままにする。
- migration write set は各 task の Files に列挙した repository-relative path のみ。unexpected dirty file、scope 外 file、`knowledge/raw/**` が含まれたら停止し、計画を更新して再承認されるまで書かない。
- validator / test / authoring check の一つでも失敗したら completion / commit を宣言しない。承認仕様の transaction 条件に従い、Task 1–3 は commit せず、Task 4 の全 fresh verification 成功後に全 explicit write set を一つだけ scoped commit にする。

---

## File structure and responsibility map

| Area | Files | Responsibility after this plan |
| --- | --- | --- |
| Public portable contract | `skills/llm-wiki/SKILL.md`, `DESCRIPTION.md`, `agents/openai.yaml`, `context-contract.toml` | structural Inputs / Outputs / Required Capabilities、existing discovery、four-file structural read-set |
| Structural kernel and modes | `references/core.md`, `single-root.md`, `multi-root.md`, `structure.md`, `page-authoring.md`, six `references/modes/*.md` | topology、authority、semantic schema、relation kind、lifecycle、authoring handoff |
| Semantic assets | twelve `assets/templates/*.md` files | page type、required / optional semantic field、relation、lifecycle state、provenance、index/log effect。serialization examples は持たない |
| Regression proof | `tests/test_context_contract.py`, new `tests/test_authoring_boundary.py` | structural read-set continuity、unique semantic ownership、delegation / fail-closed wording、syntax-policy non-ownership。Obsidian parsing はしない |
| Local migration and closeout | `knowledge/AGENTS.md`, `knowledge/index.md`, `knowledge/log.md`, three named synthesis pages | `obsidian` profile selection、active internal links の wikilink 化、superseded authoring ownership の durable record |

### Task 1: Portable contract、discovery gate、structural read-set を固定する

**Files:**

- Modify: `skills/llm-wiki/SKILL.md`
- Modify: `skills/llm-wiki/DESCRIPTION.md`
- Modify: `skills/llm-wiki/agents/openai.yaml`
- Modify: `skills/llm-wiki/context-contract.toml`
- Modify: `skills/llm-wiki/references/core.md`
- Modify: `skills/llm-wiki/references/single-root.md`
- Modify: `skills/llm-wiki/references/multi-root.md`
- Modify: `skills/llm-wiki/tests/test_context_contract.py`
- Create: `skills/llm-wiki/tests/test_authoring_boundary.py`

**Interfaces:**

- Consumes: existing `context-contract.toml` operation key `<topology>.<mode>` and existing validator expectation that each operation reads `SKILL.md`, `references/core.md`, one topology reference, and one mode reference.
- Produces: `llm-wiki` public sections `## Inputs`, `## Outputs`, and `## Required Capabilities`; a write-capable operation gate with result `BLOCKED`; local-contract fields `authoring profile` and `compatibility requirement`; unchanged schema-v2 context operation shape and four-file read-set.
- Invariant for later tasks: the public contract names relation identity and syntax-neutral semantic schema, but never declares a Markdown / Obsidian notation as canonical.

- [ ] **Step 1: Write the failing contract and read-set tests.**

  Create `skills/llm-wiki/tests/test_authoring_boundary.py` with text-level, non-parsing assertions such as:

  ```python
  def test_public_contract_declares_portable_handoff_and_fail_closed_boundary(self) -> None:
      skill = read("SKILL.md")
      for heading in ("## Inputs", "## Outputs", "## Required Capabilities"):
          self.assertIn(heading, skill)
      self.assertIn("existing skill discovery", skill)
      self.assertIn("`BLOCKED`", skill)
      self.assertNotIn("fallback renderer", skill.casefold())

  def test_context_operations_keep_only_structural_four_file_read_sets(self) -> None:
      operation = report_operation("single-root.ingest")
      self.assertEqual(len(operation["files"]), 4)
      self.assertNotIn("obsidian-markdown", "\n".join(operation["files"]))
  ```

  Extend `test_context_contract.py` so every topology × mode operation still has exactly `SKILL.md`, `core.md`, its matching topology reference, and its matching mode reference; assert `schema_version == 2`, `max_file_count == 4`, and that no operation reference is `page-authoring.md` or `optional-tooling.md`.

- [ ] **Step 2: Run the focused tests and verify RED.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: FAIL because `test_authoring_boundary.py` has just asserted missing `## Inputs`, `## Outputs`, `## Required Capabilities`, and the existing discovery / `BLOCKED` terms are absent from `SKILL.md`.

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_context_contract.py' -v`

  Expected: FAIL after the new schema-v2 / four-file assertions are added only if the current contract drifts; otherwise PASS is acceptable because this test protects an intentionally retained interface.

- [ ] **Step 3: Implement the minimum portable contract and structural local-contract seam.**

  In `SKILL.md`, replace the local Markdown / relative-link / Japanese-format ownership in description, Overview, Reference Map, and Common Mistakes with these exact semantic rules:

  ```markdown
  ## Inputs

  - `operation`: `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, or `lint`.
  - resolved `knowledge_root`, topology, actor / authority context, operation payload, existing document state, target relation identity, and syntax-neutral semantic schema.
  - the local contract's selected authoring profile and compatibility requirement.

  ## Outputs

  - an authority- and routing-valid operation result, its required index/log sync set, or `BLOCKED` before a durable write.

  ## Required Capabilities

  - read the declared structural read-set and local contract;
  - resolve an applicable selected authoring skill through existing skill discovery and read its `SKILL.md`;
  - serialize the semantic schema by that skill's documented procedure; and
  - validate only semantic preservation, authority, path, bounded write set, and index/log effect.
  ```

  Add the ordered gate: resolve topology / authority, read local profile, discover exactly one applicable readable authoring `SKILL.md`, hand off serialization, then validate structural effect. State that missing, ambiguous, incompatible, or unreadable discovery returns `BLOCKED` before page, index, or log write; a read-only query may collect material until it would file back.

  In `DESCRIPTION.md` and `agents/openai.yaml`, remove Markdown / Japanese-local formatting as behavior or trigger criteria; keep only durable knowledge lifecycle routing. In `core.md`, `single-root.md`, and `multi-root.md`, retain layers, root identity, owner/read/write/draft routing, cross-root target identity, semantic index/log invariant, and add local profile / compatibility declaration as semantic fields. Remove syntax choices, renderer/tool requirements, and prose-format prescriptions. Preserve `context-contract.toml` schema version, twelve operations, four-file count, and current references; only change comments or prose-adjacent labels if needed to call them structural read sets.

- [ ] **Step 4: Run focused tests and verify GREEN.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_context_contract.py' -v && python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: PASS; every operation reports the same four structural files, and the public contract test proves declared portable handoff / fail-closed language without adding an external reference to the read-set.

- [ ] **Step 5: Preserve the transaction boundary; do not commit this task.**

  Run: `git diff --check -- skills/llm-wiki/SKILL.md skills/llm-wiki/DESCRIPTION.md skills/llm-wiki/agents/openai.yaml skills/llm-wiki/context-contract.toml skills/llm-wiki/references/core.md skills/llm-wiki/references/single-root.md skills/llm-wiki/references/multi-root.md skills/llm-wiki/tests/test_context_contract.py skills/llm-wiki/tests/test_authoring_boundary.py`

  Expected: exit `0`. The only scoped commit command for this migration is intentionally deferred to Task 4: `git commit -m "refactor: separate llm-wiki authoring responsibility"`.

### Task 2: Semantic schema を残し、template・reference・mode から serialization ownership を外す

**Files:**

- Modify: `skills/llm-wiki/references/structure.md`
- Modify: `skills/llm-wiki/references/page-authoring.md`
- Modify: `skills/llm-wiki/references/optional-tooling.md`
- Modify: `skills/llm-wiki/references/modes/bootstrap.md`
- Modify: `skills/llm-wiki/references/modes/ingest.md`
- Modify: `skills/llm-wiki/references/modes/query.md`
- Modify: `skills/llm-wiki/references/modes/draft-review.md`
- Modify: `skills/llm-wiki/references/modes/canonicalize.md`
- Modify: `skills/llm-wiki/references/modes/lint.md`
- Modify: `skills/llm-wiki/assets/templates/AGENTS.md`
- Modify: `skills/llm-wiki/assets/templates/root-AGENTS.md`
- Modify: `skills/llm-wiki/assets/templates/root-registry.md`
- Modify: `skills/llm-wiki/assets/templates/index.md`
- Modify: `skills/llm-wiki/assets/templates/log.md`
- Modify: `skills/llm-wiki/assets/templates/source-summary.md`
- Modify: `skills/llm-wiki/assets/templates/entity.md`
- Modify: `skills/llm-wiki/assets/templates/concept.md`
- Modify: `skills/llm-wiki/assets/templates/synthesis.md`
- Modify: `skills/llm-wiki/assets/templates/query-note.md`
- Modify: `skills/llm-wiki/assets/templates/draft-note.md`
- Modify: `skills/llm-wiki/assets/templates/implementation-progress-ledger.md`
- Modify: `skills/llm-wiki/tests/test_authoring_boundary.py`

**Interfaces:**

- Consumes: Task 1's `semantic schema`, selected profile, readable authoring-skill handoff, and structural four-file read-set.
- Produces: `page-authoring.md` as the single in-skill semantic page-schema inventory; each asset as a syntax-neutral field contract; six modes that delegate serialization after discovery; no `llm-wiki` authoring-tool reference.
- Field contract: every page schema declares `page_type`, `purpose`, `required_fields`, `optional_fields`, `relation_kinds`, `lifecycle_state`, `discoverability_metadata`, `provenance_requirement`, and `index_log_effect`; none declares Markdown headings, tables, YAML, WikiLink notation, callouts, embeds, or rendering.

- [ ] **Step 1: Extend the failing boundary test with unique-owner and no-syntax-policy assertions.**

  Add concrete tests to `test_authoring_boundary.py`:

  ```python
  def test_every_semantic_template_declares_the_complete_schema_without_serialization_fields(self) -> None:
      for asset in TEMPLATE_ASSETS:
          text = asset.read_text(encoding="utf-8")
          self.assertIn("semantic fields", text.casefold())
          for forbidden in ("YAML frontmatter", "relative Markdown link", "wikilink", "callout", "embed"):
              self.assertNotIn(forbidden.casefold(), text.casefold())

  def test_modes_delegate_authoring_without_reading_concrete_templates(self) -> None:
      for mode in MODE_REFERENCES:
          text = mode.read_text(encoding="utf-8")
          self.assertIn("selected authoring skill", text)
          self.assertIn("semantic schema", text)
          self.assertNotIn("assets/templates/", text)
  ```

  Define `TEMPLATE_ASSETS` as the twelve exact asset paths listed in this task and `MODE_REFERENCES` as the six exact `references/modes/*.md` paths. Add an assertion that `optional-tooling.md` does not recommend or require an authoring tool.

- [ ] **Step 2: Run the new assertions and verify RED.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: FAIL because current templates contain frontmatter, headings, Markdown links, and concrete examples; current modes name `assets/templates/` / `page-authoring.md` rather than a selected authoring skill.

- [ ] **Step 3: Replace only serialization policy with syntax-neutral schema and handoff language.**

  Keep `structure.md`'s root layout, durable document routing, page-type directories, and filename identity rules, but remove frontmatter examples and authoring-format instruction. Keep from `page-authoring.md` exactly the one-topic boundary, canonical target decision, relation kind / target identity, provenance requirement, inbound/outbound discoverability requirement, and canonicalization effects; make it the schema inventory defined in this task's interface. Remove its link notation, citation section format, heading, summary, search-term, and presentation directives.

  Make `optional-tooling.md` state only that `llm-wiki` selects no authoring tool and that selected authoring skill documentation controls optional authoring tooling; retain no concrete tool recipe. For each of the six modes, retain its authority, routing, lifecycle, pause, and index/log decision sequence; replace direct template/reference instructions with: resolve a selected authoring skill after the structural read-set, give it the relevant semantic schema and relation identity, propagate its ordinary check failure, and never inspect syntax in `llm-wiki`.

  Convert each of the twelve assets from a completed document example into an explicit semantic schema. For example, `synthesis.md` must declare purpose, required title/status/decision/problem/goal/non-goal/acceptance/provenance fields, optional aliases/tags/relations, and index/log effects, but no property block, heading spelling, link form, or table/list shape. Apply the same field-only conversion to root local contract, root registry, index, log, source summary, entity, concept, query note, draft note, and implementation-progress ledger. Do not create a schema sidecar or move these assets to the external skill.

- [ ] **Step 4: Run the semantic-boundary tests and verify GREEN.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v && python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json`

  Expected: exit `0`; the boundary test confirms all twelve semantic assets and all six mode handoffs, while context validation still reports every topology × mode operation valid within budget.

- [ ] **Step 5: Preserve the transaction boundary; do not commit this task.**

  Run: `git diff --check -- skills/llm-wiki/references skills/llm-wiki/assets/templates skills/llm-wiki/tests/test_authoring_boundary.py`

  Expected: exit `0`. Do not make an intermediate commit; Task 4 makes the sole scoped commit after all migration and validation evidence is fresh.

### Task 3: Repository-local Obsidian selectionと maintained knowledge migration を TDD で同期する

**Files:**

- Modify: `knowledge/AGENTS.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`
- Modify: `knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md`
- Modify: `knowledge/wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md`
- Modify: `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md`
- Modify: `skills/llm-wiki/tests/test_authoring_boundary.py`

**Interfaces:**

- Consumes: Task 1's selected-authoring profile gate and Task 2's syntax-neutral semantic assets / modes.
- Produces: local declaration `authoring profile: obsidian` plus `Obsidian compatibility requirement`; all internal note links in the named maintained files and `knowledge/index.md` as resolvable wikilinks; unchanged external URL destinations and labels; a new append-only migration record in `knowledge/log.md`.
- Migration fixture: `KNOWLEDGE_MIGRATION_FILES` in `test_authoring_boundary.py` is exactly the six knowledge files in this task. It deliberately excludes `knowledge/raw/**` and every historical artifact not named above.

- [ ] **Step 1: Add failing local-contract and migration-preservation tests.**

  Add these text-level assertions; they inspect link kind / known source text only and must not parse or render Obsidian syntax:

  ```python
  def test_local_contract_selects_obsidian_without_copying_authoring_syntax(self) -> None:
      contract = read_repo("knowledge/AGENTS.md")
      self.assertIn("authoring profile: obsidian", contract)
      self.assertIn("Obsidian compatibility requirement", contract)
      self.assertNotIn("relative Markdown link", contract)
      self.assertNotIn("[[...]]", contract)

  def test_migrated_knowledge_uses_wikilinks_and_preserves_external_urls(self) -> None:
      for path in KNOWLEDGE_MIGRATION_FILES:
          text = path.read_text(encoding="utf-8")
          self.assertNotRegex(text, r"\[[^]]+\]\((?:\.\.?/)?wiki/")
      self.assertIn("[Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)",
                    read_repo("knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md"))
  ```

  Also assert the old goal spec and SRO4 spec retain their historical facts while adding an explicit link to the current authoring-responsibility spec with a `superseded` explanation; assert the log contains one `implementation | llm-wiki authoring responsibility separation` entry that names the current spec.

- [ ] **Step 2: Run the migration test and verify RED.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: FAIL because `knowledge/AGENTS.md` currently mandates relative Markdown links and forbids wikilinks, `knowledge/index.md` uses internal Markdown paths, and the prior specs lack their supersession note / the new log entry.

- [ ] **Step 3: Apply the smallest safe local migration.**

  In `knowledge/AGENTS.md`, preserve root, owner, write boundary, raw immutability, single-root, index/log, Japanese-body, and durable-synthesis rules. Replace the relative-link / wikilink prohibition with the semantic declaration `authoring profile: obsidian` and `Obsidian compatibility requirement`; refer to the selected authoring skill for syntax instead of writing WikiLink examples or frontmatter rules there.

  In `knowledge/index.md`, convert each maintained internal Markdown link to a WikiLink with an explicit display alias when the page title differs from its path. Keep all external URL links and their labels byte-for-byte. In the approved current spec, link the two older maintained specifications with WikiLinks and state which authoring-ownership clauses they supersede while retaining structural/lifecycle decisions. In `llm-wiki-draft-review-and-canonicalize-goal-spec.md` and `skill-repository-optimization-v4-spec.md`, add a short historical/superseded note pointing to [[llm-wiki-authoring-responsibility-separation-spec]]; do not revise their historical acceptance evidence or any raw citation. Append one `implementation | llm-wiki authoring responsibility separation` record to `knowledge/log.md` with WikiLinks to the current spec and current implementation plan, the affected local contract/index, and the statement that `raw/**` was untouched.

- [ ] **Step 4: Run migration tests and verify GREEN.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: PASS; the local contract selects Obsidian without duplicating syntax, the explicit maintained-file set has no internal `wiki/` Markdown links, external URL evidence is unchanged, historical specs are preserved and superseded explicitly, and the new append-only log record is discoverable.

- [ ] **Step 5: Preserve the transaction boundary; do not commit this task.**

  Run: `git diff --check -- knowledge/AGENTS.md knowledge/index.md knowledge/log.md knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md knowledge/wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md skills/llm-wiki/tests/test_authoring_boundary.py`

  Expected: exit `0`. No commit occurs before the Task 4 required verification succeeds.

### Task 4: Explicit write set を検査し、full validation と唯一の scoped commit で closeout する

**Files:**

- Modify: no additional source file; inspect the exact files enumerated in Tasks 1–3 only.
- Test: `skills/llm-wiki/tests/test_context_contract.py`
- Test: `skills/llm-wiki/tests/test_authoring_boundary.py`

**Interfaces:**

- Consumes: Task 1–3's contract, semantic schema, migration, and tests.
- Produces: fresh success evidence for the full existing validation stack, an exact changed-file set confined to this plan, and one commit `refactor: separate llm-wiki authoring responsibility`.
- Failure result: do not commit; retain the isolated-worktree diff with the failing command and changed-file set for repair.

- [ ] **Step 1: Write the final failing write-set assertion before closeout.**

  Add the exact `ALLOWED_CHANGED_FILES` tuple to `test_authoring_boundary.py`, containing every path in Tasks 1–3, and test it against `git diff --name-only 5f08fe27e2899865dea9e4347e5301d126744c90 --`:

  ```python
  def test_diff_is_limited_to_the_approved_write_set(self) -> None:
      changed = set(run_git("diff", "--name-only", BASELINE, "--").splitlines())
      self.assertTrue(changed)
      self.assertSetEqual(changed, set(ALLOWED_CHANGED_FILES))
      self.assertFalse(any(path.startswith("knowledge/raw/") for path in changed))
  ```

  `ALLOWED_CHANGED_FILES` must contain the 36 exact files listed in Tasks 1–3 (including the new `test_authoring_boundary.py`) and no glob, directory, external skill path, validator script, or workflow path.

- [ ] **Step 2: Run the closeout test and verify RED if scope has drifted.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`

  Expected: FAIL if any changed file is outside the explicit tuple, a named planned file was missed, `knowledge/raw/**` changed, or the test has not yet been updated to the final tuple. Repair the write set or revert only the unplanned change before proceeding; do not broaden scope implicitly.

- [ ] **Step 3: Run the complete required verification stack.**

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -v`

  Expected: exit `0`, including the existing context tests and all new ownership / migration / write-set tests.

  Run: `python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json`

  Expected: exit `0` and JSON `"ok": true` with valid twelve topology × mode operations.

  Run: `python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning`

  Expected: exit `0`, 12 operations, and no warnings.

  Run: `python3 scripts/validate_skill_architecture.py --all`

  Expected: exit `0`.

  Run: `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-wiki`

  Expected: exit `0` and `Skill is valid!`.

  Run: `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v && git diff --check`

  Expected: exit `0`; no check implements or calls a Markdown / Obsidian parser, renderer, or formatter.

- [ ] **Step 4: Review the exact diff before staging.**

  Run: `git diff --name-only 5f08fe27e2899865dea9e4347e5301d126744c90 -- && git diff --check && git status --short`

  Expected: the output names exactly `ALLOWED_CHANGED_FILES`, contains no `knowledge/raw/` path and no external installed skill path, and `git diff --check` exits `0`.

- [ ] **Step 5: Make the single scoped commit only after all checks pass.**

  Run:

  ```bash
  git add skills/llm-wiki/SKILL.md skills/llm-wiki/DESCRIPTION.md skills/llm-wiki/agents/openai.yaml skills/llm-wiki/context-contract.toml skills/llm-wiki/references/core.md skills/llm-wiki/references/single-root.md skills/llm-wiki/references/multi-root.md skills/llm-wiki/references/structure.md skills/llm-wiki/references/page-authoring.md skills/llm-wiki/references/optional-tooling.md skills/llm-wiki/references/modes/bootstrap.md skills/llm-wiki/references/modes/ingest.md skills/llm-wiki/references/modes/query.md skills/llm-wiki/references/modes/draft-review.md skills/llm-wiki/references/modes/canonicalize.md skills/llm-wiki/references/modes/lint.md skills/llm-wiki/assets/templates/AGENTS.md skills/llm-wiki/assets/templates/root-AGENTS.md skills/llm-wiki/assets/templates/root-registry.md skills/llm-wiki/assets/templates/index.md skills/llm-wiki/assets/templates/log.md skills/llm-wiki/assets/templates/source-summary.md skills/llm-wiki/assets/templates/entity.md skills/llm-wiki/assets/templates/concept.md skills/llm-wiki/assets/templates/synthesis.md skills/llm-wiki/assets/templates/query-note.md skills/llm-wiki/assets/templates/draft-note.md skills/llm-wiki/assets/templates/implementation-progress-ledger.md skills/llm-wiki/tests/test_context_contract.py skills/llm-wiki/tests/test_authoring_boundary.py knowledge/AGENTS.md knowledge/index.md knowledge/log.md knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md knowledge/wiki/syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md
  git commit -m "refactor: separate llm-wiki authoring responsibility"
  ```

  Expected: one commit containing only the staged explicit write set. If staging or commit fails, do not claim completion; inspect `git status --short`, preserve the diff, repair, and rerun every command in Step 3.

## Self-review

- **Spec coverage:** Task 1 covers portable Inputs / Outputs / Required Capabilities, existing discovery, `BLOCKED`, and structural read-set preservation. Task 2 covers all named references, six modes, twelve assets, unique semantic ownership, and the ban on llm-wiki syntax validation. Task 3 covers the selected `obsidian` local profile, wikilink migration, external URL / raw preservation, historic supersession, index, and append-only log. Task 4 covers the exact write set, every required validation command, and the required one scoped commit.
- **No-placeholder scan:** this plan has no TBD / TODO / later-work placeholder, wildcard write target, unspecified test, or unspecified command. `ALLOWED_CHANGED_FILES` is mechanically defined by the exhaustive file lists in Tasks 1–3 and must be materialized as the 36 literal strings before closeout.
- **Interface consistency:** Tasks 2–3 consume the same Task-1 names: `selected authoring skill`, `semantic schema`, `relation identity`, `BLOCKED`, and four-file structural read-set. Tests are text-level ownership / preservation tests only; no task introduces an Obsidian syntax parser, formatter, renderer, manifest, or sidecar.

## Execution handoff

Plan saved at `knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-implementation-plan.md`. Execute it task-by-task with the repository's `sdd-implementation` route; do not begin implementation until the plan receives the required repository approval.
