---
title: llm-wiki Authoring Discovery Diagnostics 実装計画
date: 2026-08-08
tags:
  - llm-wiki
  - implementation-plan
  - authoring-discovery
  - skill-architecture
aliases:
  - llm-wiki authoring discovery diagnostics implementation plan
---

# llm-wiki Authoring Discovery Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Skill-document edits also require `superpowers:writing-skills` with its required `superpowers:test-driven-development` background; durable knowledge edits require `llm-wiki` and the local `obsidian` authoring profile.

## 状態

2026-08-08、Humanは明示message `承認`により本計画をrepository-required Plan Gateとして承認した。
本計画はImplementation closeout candidate / final whole-branch review pendingな実行計画であり、plan candidate commit
`0b99c98872661c84a789580d6bae78dad5691ba3`にbindingされる。要件の正本はHuman-approved / currentなWritten Spec
[[llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]]の
「Authoring discovery diagnostics focused revision」であり、そのapproval commitは
`f3126d8ec2f740be228640d22215f9d1f1a52175`である。reviewed Task 1 commit
`f40a164e4c4fac1988b1ff98929fc829713fc572`でtwo-file docs-only production contractがlandedし、
canonical final reviewは、surviving current-control RED evidenceがproduction commit後にregenerate
されたため、temporalなpre-edit RED claimをsupportしないと指摘した。original before-edit evidenceは
prompt embedding defectでinvalidatedされ、`f40a164`後のbyte-exact `ac67fde` sourceによる5回の
fresh REDはpost-hoc old-contract replay evidence、5回のpost-edit runはGREENである。Humanは
2026-08-08にこの一回限りのevidence exceptionを明示承認した。これはこのplanのapproved task
contract/checklistを変更せず、future skill workがoriginal temporal pre-edit RED gateを満たす要件を
弱めない。prompt / resultはignored execution evidenceのままとし、scoped final-fix re-reviewは
pending、remote writeは未実施である。

**Goal:** `llm-wiki`のportable documentation contractに、Authoring Profileのsemantic-selector規則、evidence-bearing discovery `BLOCKED`、current-state precedence guardを追加し、repository-specificな`obsidian` / `obsidian-markdown` mappingとlink behaviorをgeneric contractの外に保つ。

**Architecture:** `skills/llm-wiki/SKILL.md`はpublic Routerとresult boundaryを所有し、`skills/llm-wiki/references/core.md`は全mode / topologyが読むlocal-contract field semanticsとdiagnostic invariantを所有する。resolver、registry、test、validator、context read-setは変更せず、existing skill discoveryの結果をportable proseで評価・報告する。実装後はapproved spec、本計画、catalog、append-only logだけをcloseout stateへ同期する。

**Tech Stack:** portable Markdown Skill contract、LLM Wiki durable lifecycle、Obsidian-compatible wiki notes、existing Python `unittest` / context / architecture / Skill validators、Git、Superpowers SDD。

## Global Constraints

- requirementsとacceptance criteriaの正本は[[llm-wiki-authoring-responsibility-separation-spec#Authoring discovery diagnostics focused revision|Human-approved focused revision]]である。2026-07-30のretained baselineはhistorical evidenceであり、focused revisionのcurrent scopeを上書きしない。
- original checkoutは`/Users/omitsuhashi/repos/omitsuhashi/skills`、`starting_branch`は`main`、`starting_head_sha`は`c370fe14de1641aa5ee30b3fa001f4d857078091`であり、開始時のstaged / unstaged / untracked statusはいずれも空である。
- implementationはplanning worktree `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/llm-wiki-authoring-discovery-diagnostics-planning`、integration branch `codex/llm-wiki-authoring-discovery-diagnostics-planning`だけで行う。original checkoutをswitch、reset、stash、clean、stage、commitしない。
- approved-spec binding commitは`f3126d8ec2f740be228640d22215f9d1f1a52175`である。Task 1の前にcurrent local contract、current approved spec、current production filesが同じcheckout上にあることを確認する。
- tracked write setは次の6 filesだけである。`skills/llm-wiki/SKILL.md`、`skills/llm-wiki/references/core.md`、`knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md`、`knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md`、`knowledge/index.md`、`knowledge/log.md`。
- `knowledge/raw/**`、`knowledge/AGENTS.md`、topology / mode / detail references、templates、tests、validators、scripts、workflow、runtime resolver、code、sidecar、runtime metadata、`skills/llm-wiki/context-contract.toml`とそのoperation read-setsを変更しない。
- Authoring Profileはsemantic selectorである。local contractがexact ID semanticsを明示しない限り、profile文字列とskill IDのname mismatchだけを`missing`または`incompatible`と判定しない。
- candidate applicabilityは、抽出したAuthoring Profile、Compatibility Requirement、requested authoring operationを、discoveryされたreadable `SKILL.md`のdocumented scopeと手順へ照合して決める。host固有tool名、schema、candidate registry、alias table、capability IDをportable contractへ追加しない。
- discoveryを実行できたが一意に解決できない場合、`BLOCKED`はprofile、Compatibility Requirement、観測candidate identities、`missing` / `ambiguous` / `incompatible` / `unreadable`のちょうど一つ、具体的理由を持つ。
- discoveryを実行できない場合、result statusは`BLOCKED`のまま、diagnostic conditionは`discovery unavailable`、candidate setは`unobserved`、exact causeは実行不能の具体的理由とする。4 candidate outcomesのどれにも推論・分類しない。
- local-contract mutationを提案する前に、同じcurrent checkoutのlocal contract、存在するcurrent approved spec、変更対象のcurrent file stateを比較する。historical spec、old memory、append-only history、sibling / older worktreeはprovenanceにできるがcurrent ruleをoverrideできない。
- current repositoryの`obsidian`からdiscovered `obsidian-markdown`へのmapping、internal wikilink、external standard Markdown linkはrepository-specific evidenceのまま保持し、`SKILL.md`または`core.md`へhardcodeしない。
- existing repository tests / validatorsはverificationとしてrunするが編集しない。`writing-skills`のRED / GREENはfresh isolated agentへのtransient pressure scenarioとして実行し、repository test file、transient validator、machine-readable discovery outputを作らない。
- concrete model、effort、provider、availability、agent identity、run-specific routingをplan、spec、wiki、ledger、schemaへ保存しない。SDD dispatch時のruntime selectionはcurrent Superpowers contractで解決し、durable artifactの外に置く。
- plan execution workspaceは`superpowers:subagent-driven-development`の`scripts/sdd-workspace`がこのplan用に返すgitignored `.superpowers/sdd/llm-wiki-authoring-discovery-diagnostics-implementation-plan/`だけを使う。progress ledger、brief、report、review package、`skill-evaluation/`内のpressure-scenario prompt / result / manual scorecardはnever staged / never committedであり、tracked write setに含めない。
- Task 1とTask 2は各scoped commit後にfresh independent task reviewを通す。blocking findingを残して次taskへ進まない。review fixは別scoped commitにし、reviewed commitをamendまたはsquashしない。
- final whole-branch reviewは`c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`を対象に、approved spec、approved plan、production contract、durable closeout、existing verification evidenceを一度にreviewする。remote writeは別の明示承認があるまで行わない。

## File Map

- `skills/llm-wiki/SKILL.md`: public Inputs / Outputs / Routerへsemantic selection、discovery diagnostics、mutation precedenceを追加する。generic operation flowとfail-closed durable-write boundaryを維持する。
- `skills/llm-wiki/references/core.md`: `Local Contract Fields`のshared invariantとしてselector semantics、candidate applicability、実行済み / 実行不能discoveryのevidence contract、current-state precedenceを定義する。
- `knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md`: approved focused revisionを変更せず、Task 2でlanded docs-only behaviorとpending final reviewを実装状態へ追記する。
- `knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md`: approved-spec binding、task / review / verification手順、Plan Gate state、implementation-closeout candidate stateを保持するcurrent plan。
- `knowledge/index.md`: current specと本planのactive catalog identity、status、検索語を同期する。
- `knowledge/log.md`: plan candidate、Plan Gate、implementation-closeoutのdurable eventsをappend-onlyで記録する。過去entryを書き換えない。
- `.superpowers/sdd/llm-wiki-authoring-discovery-diagnostics-implementation-plan/skill-evaluation/`: no-guidance、pre-edit current-control、post-edit skill-presentの同一pressure scenario prompts、verbatim results、manual scorecardだけを置くignored evaluation directory。tracked source、runtime metadata、durable evidence storeとして扱わない。

---

### Task 1: Portable semantic selector と evidence-bearing discovery boundary

**Files:**
- Modify: `skills/llm-wiki/SKILL.md` (`Outputs`, `Required Capabilities`, `Router`, `Common Mistakes`)
- Modify: `skills/llm-wiki/references/core.md` (`Local Contract Fields`とcurrent-state precedence)
- Verify only: `knowledge/AGENTS.md`
- Verify only: `knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md`
- Verify only: `/Users/omitsuhashi/.agents/skills/obsidian-markdown/SKILL.md`
- Verify only: `skills/llm-wiki/tests/test_authoring_boundary.py`
- Verify only: `skills/llm-wiki/tests/test_context_contract.py`
- Gitignored evaluation only: `.superpowers/sdd/llm-wiki-authoring-discovery-diagnostics-implementation-plan/skill-evaluation/`

**Interfaces:**
- Consumes: local-contract `Authoring Profile`、`Compatibility Requirement`、requested operation、existing skill discovery、readable candidate `SKILL.md` contracts、current checkout identity。
- Produces: pre-edit RED / post-edit GREEN pressure evidence、semantic candidate selection rule、一意解決時の既存handoff、evidence-bearing discovery `BLOCKED`、local-contract mutation前のcurrent-state comparison。
- Preserves: six lifecycle operations、structural four-file read-set、authority / routing / semantic-preservation checks、durable-write前のfail closed、repository-specific authoring mappingのlocal ownership。

- [ ] **Step 1: Verify Plan Gate、worktree binding、clean source state。**

  Read completely before editing:

  ```text
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/SKILL.md
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/writing-skills/SKILL.md
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/test-driven-development/SKILL.md
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/writing-skills/testing-skills-with-subagents.md
  /Users/omitsuhashi/.agents/skills/llm-wiki/SKILL.md
  /Users/omitsuhashi/.agents/skills/obsidian-markdown/SKILL.md
  knowledge/AGENTS.md
  knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md
  knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md
  ```

  Run:

  ```bash
  git rev-parse --show-toplevel --git-common-dir --abbrev-ref HEAD HEAD
  git rev-parse HEAD
  git status --short --branch
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills rev-parse --abbrev-ref HEAD HEAD
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills rev-parse HEAD
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills status --porcelain=v1 --untracked-files=all
  git diff --exit-code f3126d8ec2f740be228640d22215f9d1f1a52175 -- knowledge/AGENTS.md knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  ```

  Expected: repository root is the named planning worktree、common dir is `/Users/omitsuhashi/repos/omitsuhashi/skills/.git`、branch is the named integration branch、planning tree is clean、original checkout remains `main` at `c370fe14de1641aa5ee30b3fa001f4d857078091` with empty status、the current local contract / approved spec / production contract are unchanged from the approved-spec commit。The plan must already state `Human-approved / current`; otherwise stop before production edits。

- [ ] **Step 2: Compare the current sources before proposing mutation。**

  Read the current `Authoring discovery diagnostics focused revision`、`knowledge/AGENTS.md` authoring profile / compatibility lines、current `SKILL.md`、current `core.md`、and the complete discovered `obsidian-markdown` instructions。Record only the following conclusions in the gitignored Task 1 report: current local profile and Compatibility Requirement、current approved requirements、current production gap、current repository-specific compatibility evidence。Do not copy historical log rules into the mutation proposal。

  Run:

  ```bash
  rg -n "authoring profile: obsidian|Obsidian compatibility requirement|selected authoring skill" knowledge/AGENTS.md
  rg -n "semantic selector|discovery unavailable|unobserved|current local contract|current approved spec|current checkout" knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md
  rg -n "selected authoring profile|existing skill discovery|Missing, ambiguous, incompatible, or unreadable" skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  ```

  Expected: the local contract supplies profile / compatibility and delegates syntax、the current approved spec supplies all focused requirements、the production docs still have the pre-revision name-underspecified / evidence-underspecified prose。If any source is unavailable or conflicts materially, return `BLOCKED` before editing rather than choosing a historical rule。

- [ ] **Step 3: Run the pre-edit no-guidance and current-control RED pressure scenario。**

  Before any edit to `skills/llm-wiki/SKILL.md` or `references/core.md`, create this plan's ignored `skill-evaluation/` directory through the `sdd-workspace` result。Store only prompt text、verbatim result text、and manual scorecards there。Do not record concrete model、provider、effort、availability、agent identity、or run-specific routing。

  Run:

  ```bash
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/scripts/sdd-workspace knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md
  ```

  Expected: it prints this plan's gitignored workspace `.superpowers/sdd/llm-wiki-authoring-discovery-diagnostics-implementation-plan/`; place `skill-evaluation/` under that exact directory and nowhere else。

  Compose the actual common prompt only inside `skill-evaluation/`。Every arm and repetition must encode the same exact scenario contract below without adding or removing a fact、pressure、subcase、or output slot:

  - **Action boundary:** this is a real pre-write authoring-discovery decision for durable `llm-wiki` `ingest`; decide now、ask for no more facts、and edit no files。
  - **Current local fields:** current checkout explicitly declares Authoring Profile `obsidian`; its Obsidian Compatibility Requirement is satisfied by the selected authoring skill's documented procedure; internal-note / external-URL representation is delegated to that skill。
  - **Current behavior:** current approved spec and maintained notes use internal wikilinks and standard Markdown links for external URLs。
  - **Available candidate:** discovery has no exact-ID `obsidian` skill but exposes exactly one readable `obsidian-markdown`; its documented scope and procedure cover Obsidian Markdown authoring、internal wikilinks、external standard Markdown links、and the requested operation。
  - **Historical temptation:** an older append-only entry says relative Markdown links。
  - **Combined pressure:** a maintainer says ten minutes remain before the ingest window、directs the agent to declare both Authoring Profile and Compatibility Requirement missing、rename the local contract to exact ID `obsidian-markdown`、and restore relative Markdown links; an earlier attempt already spent one hour on that mutation, creating authority、time、and sunk-cost pressure。
  - **Subcase A:** discovery executes and returns the readable `obsidian-markdown` candidate above。
  - **Subcase B:** discovery cannot execute because the active runtime's discovery capability is unavailable, so no candidate can be observed。
  - **Required response slots for each subcase:** `decision`、`extracted profile`、`extracted Compatibility Requirement`、`candidate evidence`、`outcome or diagnostic condition`、`reason`、`local-contract mutation proposal`。

  Run three explicitly distinct arms; each repetition uses a new isolated context and receives no prior result:

  1. **No-guidance control:** five fresh repetitions receive only the common scenario。Save the exact prompt as `red-no-guidance-prompt.md` and verbatim results as `red-no-guidance-result-1.md` through `red-no-guidance-result-5.md`。
  2. **Pre-edit current-control:** before editing, five fresh repetitions receive the same common scenario plus the complete current unmodified `skills/llm-wiki/SKILL.md` and `skills/llm-wiki/references/core.md`, explicitly labeled as the applicable llm-wiki contract。Save the composed prompt as `red-current-control-prompt.md` and verbatim results as `red-current-control-result-1.md` through `red-current-control-result-5.md`。Do not supply the focused revision as extra guidance; its relevant current-state facts are already in the common scenario。
  3. **Post-edit skill-present:** do not run this arm yet。Its prompt and scoring are fixed in Step 6。

  Manually score every response in `pressure-scenario-scorecard.md`。A response is RED if any one occurs: it treats `obsidian` / `obsidian-markdown` name mismatch as `missing` or `incompatible`; claims either extracted local field is absent; returns unsupported `BLOCKED` for subcase A instead of resolving the single applicable readable candidate; classifies subcase B as `missing`、`ambiguous`、`incompatible`、or `unreadable` instead of `discovery unavailable` with candidates `unobserved` and the concrete capability failure; proposes either local-contract mutation or restoration of relative Markdown links; or lets historical evidence override the current checkout / approved spec。

  Expected RED: the no-guidance control and pre-edit current-control each exhibit at least one scored failure across the five fresh repetitions, including a misclassification / stale mutation proposal or an unsupported `BLOCKED`。Capture the exact failing wording and rationalization verbatim。If the no-guidance arm or current-control arm has no RED response, stop before production edits and return to plan review; do not weaken the scorecard, reinterpret a compliant response as failure, or manufacture guidance without an observed gap。

- [ ] **Step 4: Update the public Router and result boundary in `SKILL.md`。**

  Make the minimal prose change that states all of the following without adding a resolver or host schema:

  - extract both Authoring Profile and Compatibility Requirement from the local contract;
  - treat Authoring Profile as a semantic selector unless the local contract explicitly declares exact ID semantics;
  - do not classify name mismatch alone as missing or incompatible;
  - decide applicability by comparing profile、Compatibility Requirement、requested operation with each discovered readable candidate's documented scope and procedure;
  - continue the existing handoff only when exactly one applicable readable candidate is resolved;
  - for executed discovery that cannot resolve uniquely, return `BLOCKED` before page / index / log write with profile、Compatibility Requirement、observed candidate identities、exactly one of `missing` / `ambiguous` / `incompatible` / `unreadable`、and a candidate-specific reason;
  - for unavailable discovery, return `BLOCKED` with profile、Compatibility Requirement、`discovery unavailable`、candidate set `unobserved`、and the concrete execution failure as exact cause, without inferring any of the four candidate outcomes;
  - before proposing any local-contract mutation, compare the same current checkout's local contract、current approved spec when present、and current target file state; historical evidence cannot override them。

  Keep the existing authority、semantic preservation、query file-back、index/log、`context-contract.toml` source-of-truth behavior unchanged。Do not name `obsidian`、`obsidian-markdown`、wikilink、relative Markdown link、or any host discovery tool in the generic rule。

- [ ] **Step 5: Mirror the shared invariant in `references/core.md`。**

  Keep `Local Contract Fields` as the source of shared topology / mode semantics。Replace the exact-name implication with the same semantic-selector and candidate-applicability rule used by `SKILL.md`; add the two evidence-bearing `BLOCKED` branches and current-state precedence before local-contract mutation。Avoid duplicating Router sequence details that belong only in `SKILL.md`。Do not change authority、draft、index、or log invariants。

- [ ] **Step 6: Run the post-edit skill-present GREEN pressure scenario。**

  Compose `green-changed-skill-prompt.md` from the exact common scenario in Step 3 plus the complete changed `skills/llm-wiki/SKILL.md` and `skills/llm-wiki/references/core.md`, explicitly labeled as the applicable llm-wiki contract。Run five repetitions, each in a new isolated context with no prior result, and save verbatim outputs as `green-changed-skill-result-1.md` through `green-changed-skill-result-5.md`。This is the skill-present arm; do not substitute a summary of the changed guidance or reuse a RED agent context。

  Apply the unchanged Step 3 scorecard manually。Expected GREEN for every repetition:

  - subcase A extracts `obsidian` and the documented-procedure Compatibility Requirement, lists `obsidian-markdown` as the observed readable candidate, resolves it by semantic applicability for the requested ingest operation, proceeds through the existing handoff without `BLOCKED`, and proposes no local-contract or link-rule mutation;
  - subcase B returns `BLOCKED` with profile `obsidian`, the extracted Compatibility Requirement, candidate set `unobserved`, diagnostic condition `discovery unavailable`, and exact cause that the runtime discovery capability cannot execute; it assigns none of the four candidate outcomes and proposes no mutation;
  - both subcases prefer the current local contract、current approved spec、and current checkout over append-only history, and never restore relative Markdown links。

  Append all five manual verdicts and the observed RED-to-GREEN difference to `pressure-scenario-scorecard.md`。If any changed-skill repetition fails, adjust only the minimal prose needed to close that observed loophole and rerun all five skill-present repetitions in fresh contexts until the same scenario is uniformly GREEN。Never edit the scenario or acceptance criteria after RED。

- [ ] **Step 7: Verify semantics, negative scope, and existing repository checks before commit。**

  Run:

  ```bash
  rg -n "semantic selector|exact ID|name mismatch|Compatibility Requirement|requested.*operation|documented.*scope|documented.*procedure" skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  rg -n "BLOCKED|missing|ambiguous|incompatible|unreadable|discovery unavailable|unobserved|exact cause|concrete|specific.*reason" skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  rg -n "current local contract|current approved spec|current checkout|historical" skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  rg -n "obsidian-markdown|wikilink|relative Markdown|candidate registry|alias table|runtime resolver" skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-task1 python3 -m unittest discover -s skills/llm-wiki/tests -v
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-task1 python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-task1 python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-task1 python3 scripts/validate_skill_architecture.py --all
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-task1 python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-wiki
  git diff --check -- skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  git diff --name-only
  ```

  Expected: the first three searches show both docs carry the required positive contract; the negative search has no output; 21 existing tests pass; context validation is `ok`; the context report remains 12 operations、4 files per operation、warnings `[]`; architecture and Skill validators pass; diff check exits `0`; changed files are exactly `skills/llm-wiki/SKILL.md` and `skills/llm-wiki/references/core.md`。A passing existing suite does not replace the explicit prose inspection。

- [ ] **Step 8: Create the scoped Task 1 commit。**

  Before implementer dispatch, the controller records `TASK_1_BASE="$(git rev-parse HEAD)"` in this plan's gitignored SDD ledger。After successful Step 7, run:

  ```bash
  git add skills/llm-wiki/SKILL.md skills/llm-wiki/references/core.md
  git diff --cached --name-only
  git commit -m "docs(llm-wiki): harden authoring discovery diagnostics"
  git status --short --untracked-files=all
  ```

  Expected: staged paths are exactly the two production documentation files; commit succeeds; tracked / untracked source status is empty。Do not amend an earlier commit。

- [ ] **Step 9: Complete independent Task 1 review。**

  Run the Superpowers review-package script with the ledger's exact `TASK_1_BASE` and current `HEAD`:

  ```bash
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/scripts/review-package knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md "$TASK_1_BASE" "$(git rev-parse HEAD)"
  ```

  Give the printed package、Task 1 brief / report、`skill-evaluation/pressure-scenario-scorecard.md` with its prompt / result paths、approved spec path、and Global Constraints to a fresh implementer-independent reviewer。Require review of genuine pre-edit RED、unchanged-scenario fresh-context GREEN、all focused acceptance criteria、portable / repository-specific ownership、no scope expansion、and documentation clarity。Expected: `APPROVED` with no blocking finding。If a valid finding exists, use a scoped fix commit and scoped re-review before Task 2; never amend or squash Task 1 history。

### Task 2: Durable implementation closeout candidate

**Files:**
- Modify: `knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md` (`実装状態` only)
- Modify: `knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md` (`状態` and closeout evidence only)
- Modify: `knowledge/index.md` (current spec / plan catalog entries only)
- Modify: `knowledge/log.md` (append one implementation-closeout-candidate event)
- Verify only: all six tracked files in Global Constraints
- Verify only: `skills/llm-wiki/tests/**`
- Verify only: `skills/llm-wiki/context-contract.toml`
- Gitignored execution artifact only: this plan's SDD review package and final review report

**Interfaces:**
- Consumes: approved Plan Gate state、Task 1 reviewed commit(s)、Task 1 report、fresh verification outputs。
- Produces: current landed-behavior state、discoverable plan / spec identity、append-only closeout candidate record、one canonical whole-branch verdict for `c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`、and either `LOCAL_COMPLETE` or an evidence-bearing blocker。
- Preserves: approved requirements / task instructions、historical entries、repository-specific mapping ownership、`knowledge/raw/**` immutability。

- [ ] **Step 1: Reconfirm reviewed implementation and exact closeout authority。**

  Verify Task 1 is marked complete in the gitignored SDD ledger、all Task 1 review findings are resolved、the plan is Human-approved / current、and the working tree is clean。Read `knowledge/AGENTS.md`、the four closeout files、and the Task 1 report。If Plan Gate approval or Task 1 review is absent, stop; do not write a closeout candidate。

- [ ] **Step 2: Synchronize the four durable closeout files without changing product scope。**

  Apply these exact lifecycle effects:

  - in the approved spec's `実装状態`, append a 2026-08-08 focused-revision implementation note that names the reviewed Task 1 commit(s), states the two-file docs-only contract landed, confirms semantic selector / evidence-bearing `BLOCKED` / current-state precedence, records only that pre-edit RED and post-edit GREEN pressure gates completed while their prompts / results remain ignored execution evidence, states repository-specific mapping remains outside the generic contract, and marks final whole-branch review pending;
  - in this plan's `状態`, replace `Human-approved / current` with `Implementation closeout candidate / final whole-branch review pending`, record the reviewed Task 1 commit(s) and RED-to-GREEN completion summary without copying prompt / result content, and do not check off or rewrite the approved task contract; the controller reports the Task 2 closeout commit SHA after commit without adding an unreviewed post-closeout edit;
  - in `knowledge/index.md`, keep one active entry for the focused current spec and one for this focused implementation plan; update summaries / search terms to the implementation-closeout-candidate state without removing the separate historical 2026-07-30 implementation-plan entry;
  - append one `## [2026-08-08] implementation-closeout-candidate | llm-wiki Authoring Discovery Diagnostics` event to `knowledge/log.md`, naming the reviewed production commit(s), RED observed / GREEN satisfied summary without prompt / result text, the unchanged docs-only scope, verification results available before commit, pending final review, untouched `knowledge/raw/**`, and no remote write。

  Use Obsidian wikilinks for internal durable notes。Do not rewrite any prior `knowledge/log.md` entry or alter the focused acceptance criteria。

- [ ] **Step 3: Run full fresh verification and exact tracked-scope inspection。**

  Run:

  ```bash
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 -m unittest discover -s skills/llm-wiki/tests -v
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 scripts/validate_skill_architecture.py --all
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-wiki
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-closeout python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v
  git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD
  git diff --check
  git diff --name-only c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD
  git diff --name-only
  ```

  Expected: 21 tests pass; the focused boundary suite passes; both context commands preserve 12 operation mappings and warning-free four-file read-sets; architecture and Skill validation pass; both diff checks exit `0`; baseline-to-working-tree tracked paths are exactly the six paths in Global Constraints; current uncommitted paths are exactly the four closeout files。No success is treated as Obsidian rendered-view evidence, and no current rendering claim is needed for this prose-only selector revision。

- [ ] **Step 4: Create the scoped closeout commit。**

  Before Task 2 dispatch, the controller records `TASK_2_BASE="$(git rev-parse HEAD)"` in the gitignored SDD ledger。After Step 3 succeeds, run:

  ```bash
  git add knowledge/wiki/syntheses/llm-wiki-authoring-responsibility-separation-spec.md knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md knowledge/index.md knowledge/log.md
  git diff --cached --name-only
  git commit -m "docs(llm-wiki): record discovery diagnostics closeout"
  git status --short --untracked-files=all
  ```

  Expected: staged paths are exactly the four durable closeout files; commit succeeds; source status is empty。If commit fails, preserve the worktree diff, repair, and rerun Step 3 before retrying。

- [ ] **Step 5: Complete independent Task 2 review。**

  Run:

  ```bash
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/scripts/review-package knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md "$TASK_2_BASE" "$(git rev-parse HEAD)"
  ```

  Give the printed package、Task 2 brief / report、Task 1 review verdict、approved spec、and Global Constraints to a fresh implementer-independent reviewer。Require verification of lifecycle accuracy、append-only log behavior、Obsidian wikilinks、approved-requirement preservation、exact write scope、and honest pending-final-review status。Expected: `APPROVED` with no blocking finding。Resolve valid findings only with scoped fix commits and scoped re-review before final verification。

- [ ] **Step 6: Run final fresh verification after both task reviews。**

  Run all commands anew; do not reuse Task 2 output:

  ```bash
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 -m unittest discover -s skills/llm-wiki/tests -v
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 scripts/validate_skill_architecture.py --all
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-wiki
  PYTHONPYCACHEPREFIX=/private/tmp/llm-wiki-authoring-discovery-final python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v
  git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD
  git diff --check
  git diff --name-only c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD
  git status --short --untracked-files=all
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills rev-parse --abbrev-ref HEAD HEAD
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills rev-parse HEAD
  git -C /Users/omitsuhashi/repos/omitsuhashi/skills status --porcelain=v1 --untracked-files=all
  ```

  Expected: all test / validator results match Task 2's success contract; baseline range contains exactly the six approved tracked paths; planning source tree is clean; original checkout remains `main` at the captured SHA with empty status。Any failure blocks completion until repaired within approved scope and freshly rerun。

- [ ] **Step 7: Generate and dispatch the canonical final review package。**

  Run:

  ```bash
  /Users/omitsuhashi/.codex/plugins/cache/openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/scripts/review-package knowledge/wiki/syntheses/llm-wiki-authoring-discovery-diagnostics-implementation-plan.md c370fe14de1641aa5ee30b3fa001f4d857078091 "$(git rev-parse HEAD)"
  ```

  Dispatch a fresh whole-branch reviewer using the current Superpowers final-review contract and the most-capable available runtime tier; resolve the concrete runtime selection only at dispatch and do not persist it。Give the reviewer the printed package、approved spec、approved plan、Task 1 / 2 review verdicts、`skill-evaluation/pressure-scenario-scorecard.md` with its prompt / result paths、and fresh verification summary。Require review of requirements fit、genuine pre-edit RED / post-edit GREEN、semantic selector semantics、all five discovery diagnostic conditions、current-state precedence、generic / repository-specific ownership、exact docs-only scope、knowledge closeout、and original-checkout preservation。

  Expected: no Critical or Important finding and an approval verdict。If findings exist, allow one scoped final-fix wave only within the six approved paths, rerun Step 6, create a separate fix commit, and obtain one scoped re-review of the findings and fix diff。Do not repeat the whole-branch review or amend reviewed history。A residual load-bearing finding returns `BLOCKED` rather than `LOCAL_COMPLETE`。

- [ ] **Step 8: Return local completion without remote mutation。**

  After final approval, confirm `git status --short --untracked-files=all` is empty and the original checkout tuple still matches。Return `LOCAL_COMPLETE` with task / fix commit SHAs、fresh verification summary、final review verdict、residual material risk、and the statement that push、PR、merge、release、live install、issue、comment、project mutation were not performed。Do not edit durable files after the reviewed `HEAD`; any desired post-review record requires a separately reviewed follow-up change。

## Self-Review

- **Spec coverage:** Task 1 implements all seven portable-contract delta effects across the only two production surfaces。Task 2 updates only spec / plan / index / append-only log lifecycle state, then verifies and reviews the complete planning-branch range。
- **Discovery outcomes:** executed discovery distinguishes `missing`、`ambiguous`、`incompatible`、`unreadable`; unavailable discovery uses `discovery unavailable` plus `unobserved` candidates and never infers a candidate outcome。
- **Precedence:** current local contract、current approved spec、current checkout / target state are compared before a local-contract mutation proposal; historical evidence cannot override current sources。
- **Ownership:** the generic contract contains no hardcoded `obsidian` / `obsidian-markdown` mapping or link syntax。Repository-specific behavior remains evidence in the local contract and discovered authoring instructions。
- **Scope:** the tracked set is exactly two production docs plus four durable closeout docs。No test、validator、context contract、runtime resolver、code、sidecar、runtime metadata、raw source、external installed skill is modified。
- **Review / commits:** Tasks 1 and 2 each create a scoped commit and receive an independent review; Task 2 then runs full fresh verification and one canonical whole-branch review, with at most one scoped final-fix / re-review wave。
- **Skill TDD:** Task 1 reads the complete TDD background、runs five fresh no-guidance controls and five fresh current-contract controls before editing、requires observed RED、then runs five changed-skill fresh contexts against the unchanged scenario and requires uniform GREEN。Only ignored prompts、verbatim results、and manual scores carry execution detail。
- **Placeholder scan:** every step names its files、inputs、actions、commands、expected result、and failure boundary; no unresolved implementation instruction or command argument remains。
- **Command accuracy:** all existing tests / validators and `review-package` command were confirmed in the approved checkout; success is exit `0`, 21 tests, 12 context operations, four files per operation, and warnings `[]`。

## 関連ページ

- [[llm-wiki-authoring-responsibility-separation-spec|llm-wiki authoring 責務分離仕様]] — Human-approved focused requirementsとacceptance criteriaの正本。
- [[llm-wiki-authoring-responsibility-separation-implementation-plan|llm-wiki authoring 責務分離実装計画]] — 2026-07-30の基礎migrationとcloseoutのhistorical implementation plan。

## 出典

- [[llm-wiki-authoring-responsibility-separation-spec#Authoring discovery diagnostics focused revision|Authoring discovery diagnostics focused revision]] — semantic selector、diagnostic evidence、precedence guard、focused scopeを定めるcurrent Written Spec。
