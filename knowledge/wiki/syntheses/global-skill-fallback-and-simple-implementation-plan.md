---
title: Global Skill Fallback And Simple Implementation Plan
date: 2026-08-14
tags:
  - sdd-implementation
  - skill-discovery
  - implementation-simplicity
  - implementation-plan
status: implemented-task-reviewed-pending-final-review
lifecycle_state: accepted
decision: approved-for-local-implementation
decision_authority: Human-approved requirements plus repository plan review
approved_on: 2026-08-14
aliases:
  - Global Skill Fallback And Simple Implementation Plan
  - グローバルSkill fallbackと単純実装の計画
---

# Global Skill Fallback And Simple Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan. Use `superpowers:writing-skills` and `superpowers:test-driven-development` for the Skill change. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** required skillがinjected/current listになくてもreadableなglobal installがあればSDDを継続し、実装・reviewを要求結果に必要な最小surfaceへ戻す独立Skillを追加する。

**Architecture:** 既存`skills/sdd-implementation/SKILL.md`のDependency Preflightだけを最小修正し、active discoveryの後にruntime-exposed global rootsとaccess可能な`~/.agents/skills`を確認する。一般的な単純化guidanceは、SDDへ組み込まず、portableな`skills/keep-implementation-simple/SKILL.md`一つで提供する。

**Tech Stack:** portable Markdown `SKILL.md`、fresh-agent behavior evaluation、既存repository validator、skill-creator validator。

## Status And Provenance

- 状態: local implementation・task review・knowledge closeout済み。final whole-branch review待ちのため`LOCAL_COMPLETE`は未宣言。
- authority: Human-approved requirements、およびmaterial requirement/scope defectなしとしたindependent repository plan review。
- baseline: `c370fe14de1641aa5ee30b3fa001f4d857078091`。
- worktree / branch: `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/global-skill-discovery-planning` / `codex/global-skill-fallback-simple`。
- implementation commit: `e40fa348db056be005a254c1e5a84b51d7447629`（`feat: keep skill discovery fallback simple`）。
- task review: approved。2つのfresh-agent behavior check、focused validation、non-goalを確認し、open material findingなし。
- pending: `c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`のfinal diff checkとfresh final whole-branch review。
- observed RED: current conversationとrejected `codex/global-skill-discovery-planning` branchが、simple fallbackへresolver等のsupporting machineryを追加した過剰実装をすでに示している。新しいbaseline ritualは行わず、そのbranchのcontentも再利用しない。

## Global Constraints

- active runtime discoveryを最初に使い、その後にruntimeが公開するglobal skill rootsを確認する。access可能なcross-runtime alias `~/.agents/skills`を候補に含める。
- readableな`<root>/<required-skill>/SKILL.md`があれば読み、使い、routeを継続する。
- active/global checkが完了してreadable matchがない場合だけmissingを返す。checkを完了できない場合は、missingへ丸めず、失敗phase/pathとunderlying errorを報告する。
- `keep-implementation-simple`はportableな独立general skillであり、SDD sub-skill、default implementation route、scheduler/process frameworkではない。portable inputs、outputs、required capabilitiesを宣言する。
- resolver、classifier、provenance/evidence model、dependency closure、trace、cache、dedup、cycle model、test-only runtime/model、schema、protocol、supporting fileを追加しない。
- `skill-architecture.toml`、tests、scripts、CI、context contract、runtime stateを変更しない。
- live install、remote write、push、PR、merge、releaseを行わない。

---

### Task 1: Implement both minimal Skill surfaces

**Files:**

- Modify: `skills/sdd-implementation/SKILL.md`
- Create: `skills/keep-implementation-simple/SKILL.md`

**Interfaces:**

- `sdd-implementation` consumes a required skill identity plus active/global discovery evidence and produces continue, true missing, or a concrete discovery/read failure.
- `keep-implementation-simple` consumes the requested observable outcome, accepted criteria, repository rules, and current evidence; it produces the smallest owner/surface, mapped changes, and a bounded implementation/review verdict.

- [x] **Step 1: Make the minimal Dependency Preflight edit**

Keep the existing family/route conditions and missing result strings. Immediately after the current active-runtime discovery instruction, add only this behavior:

```markdown
If active discovery has no readable match, check the globally installed skill roots exposed by the runtime, including the cross-runtime alias `~/.agents/skills` when that alias is accessible. When `<root>/<required-skill>/SKILL.md` is readable, read it, use it, and continue the selected route.

Report a required family as missing only after active discovery and every accessible global-root check complete with no readable match. If discovery or a root/candidate read cannot be completed, report `BLOCKED: dependency preflight failed` together with the observed phase or path and underlying error. Do not report that failure as missing.
```

Do not add a resolver, helper, candidate model, registry, cache, trace, test runtime, schema, or state.

- [x] **Step 2: Create the independent portable Skill**

Create only `skills/keep-implementation-simple/SKILL.md` with this content:

```markdown
---
name: keep-implementation-simple
description: Use when implementing or reviewing a repository change whose proposed design may be more complex than its requested observable outcome or concrete current evidence requires.
---

# Keep Implementation Simple

Keep the change no larger than the requested observable outcome and current evidence require.

## Inputs

- The requested observable outcome and accepted criteria.
- Applicable repository rules and concrete current repository evidence.
- The proposed or actual change surface.

## Outputs

- A one-sentence restatement of the observable outcome.
- The smallest existing owner and surface that can produce it.
- Changes mapped to an accepted criterion or concrete current evidence.
- Verification results or a review verdict with any concrete blocker.

## Required Capabilities

- Read the applicable repository instructions and accepted criteria.
- Inspect the existing owner, surface, and current evidence needed for the change or review.
- Run the existing relevant verification when implementation or review requires it.

If a required capability is unavailable, return `BLOCKED` with the missing capability and concrete cause.

## Method

1. Restate the requested observable outcome in one sentence.
2. Choose the smallest existing owner and surface that can produce it.
3. Map every added concept, component, state, protocol, classifier, resolver, and artifact to an accepted criterion or concrete current repository evidence. Remove anything without a map.
4. For an instruction-only problem, use behavioral evaluation and existing real repository boundaries; do not add a test-only runtime or model.
5. Expand the architecture only after the simple approach demonstrably fails, and cite that failure.
6. In review, block only for a requirement gap, repository rule violation, observable regression, or concrete current risk.
```

- [x] **Step 3: Run two behavior-based GREEN checks with fresh agents**

Give one fresh agent the new Skill and this realistic request:

```text
Use skills/keep-implementation-simple/SKILL.md. A repository change has one accepted outcome: when an existing configuration key is absent, use the existing default key. A proposed design adds a resolver, classifier, cache, and provenance trace for hypothetical future products. Choose the implementation surface and state what blocks review.
```

Pass when the agent restates the outcome in one sentence, chooses the existing configuration owner/surface, removes unmapped machinery, and limits review blockers to requirement gaps, repository rule violations, observable regressions, or concrete current risk.

Give a separate fresh agent the updated SDD Skill and this realistic preflight request:

```text
Use skills/sdd-implementation/SKILL.md. The active/current skill list does not contain llm-wiki. The runtime exposes global skill roots, and ~/.agents/skills/llm-wiki/SKILL.md is readable. State the Dependency Preflight result. Also state how the result differs when all checks complete with no readable match versus when discovery or a candidate read cannot complete.
```

Pass when the agent reads/uses the global Skill and continues in the first case, reports missing only for the complete no-match case, and reports the concrete discovery/read failure rather than missing in the incomplete-check case.

- [x] **Step 4: Run focused validation**

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests -v
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/keep-implementation-simple
git diff --check
```

Expected: all commands exit `0`; existing SDD tests remain unchanged and pass; the architecture policy still names only `sdd-implementation` as the default/user-facing repository-change lifecycle route.

- [x] **Step 5: Commit and perform the mandatory task review**

```bash
git add skills/sdd-implementation/SKILL.md skills/keep-implementation-simple/SKILL.md
git commit -m "feat: keep skill discovery fallback simple"
```

One fresh independent task reviewer checks the Human-approved requirements, this task, the two changed production files, behavior results, focused validation, and non-goals. A blocker requires a requirement gap, repository rule violation, observable regression, or concrete current risk.

## Closeout And Final Review

- [x] After the task review passed, synchronized this plan, its existing index entry, and one append-only log event with the actual commit, two behavior results, focused validation, and unperformed remote actions. No separate closeout artifact was created.
- [ ] Run `git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD`, then perform the one mandatory fresh final whole-branch review over `c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD` against the Human-approved requirements and this plan. Do not add another reviewer gate.
- [ ] Return `LOCAL_COMPLETE` only when the task review, concise wiki closeout, final diff check, final review, and original-checkout preservation all pass. Remote publication and live install remain unperformed.

## Related Pages

- [[wiki/syntheses/sdd-implementation-skill-design|SDD Implementation Skill 設計]] — current SDD lifecycle and review boundary。
- [[wiki/syntheses/sdd-agent-agnostic-runtime-implementation-plan|SDD Agent-Agnostic Runtime Contract Implementation Plan]] — active-runtime discoveryへ移行したhistorical evidence。obsolete implementation contentは再利用しない。

## Provenance

- Human-approved requirements and independent minimalism review, 2026-08-14。
- `AGENTS.md`、`skills/AGENTS.md`、current two Skill surfaces at baseline `c370fe14de1641aa5ee30b3fa001f4d857078091`。
