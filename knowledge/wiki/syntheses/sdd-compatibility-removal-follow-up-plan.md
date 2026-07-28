# SDD Compatibility Removal Follow-up Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** agent-agnosticなskill behaviorを維持したまま、非要件となったcross-runtime compatibility policy、validator、CI gateをcurrent repository surfaceから削除する。

**Architecture:** Skillsは標準`SKILL.md`、入力、出力、必要capabilityだけを共有契約とする。Pluginsは必要なruntimeを個別にtargetでき、複数runtime向けmanifestやadapterの併設を要求しない。互換性だけを検証するrepository-wide scriptとCI stepは削除し、skill architecture、context、skill固有tests、creator validationだけを残す。

**Tech Stack:** Markdown、Python 3 standard library、`unittest`、GitHub Actions、LLM Wiki。

## 実施状況

Task 1は`a1a177b877ebb07258bb69aa6d1f6f3429e9bc6e`（`Remove cross-runtime compatibility requirements`）で完了した。独立reviewは`APPROVED`で、Critical / Important / Minorのfindingはない。current repositoryは標準`SKILL.md`とactive-runtime capability boundaryを維持しつつ、repository compatibility validatorとcompatibility CI gateを持たない。旧dual-host designとそのimplementation planは、skill behaviorとplugin packaging compatibilityの双方についてhistorical / non-executableな証跡として原文を保持する。

Task 2はこのcloseoutでcanonical design、historical boundary、catalog、append-only logを同期する。local verification後にbranchはPR-readyとなる。pushとPull Request作成は承認済みだが、本taskでは実行しない。merge、release、live mutationは未承認である。

## Global Constraints

- Agent-agnostic skill behavior and the active-runtime capability boundary remain unchanged.
- Cross-runtime compatibility is not a requirement.
- Do not preserve compatibility shims, paired manifests, or validators solely for compatibility.
- Historical plans and logs remain append-only evidence, never current execution instructions.
- Push and Pull Request creation are authorized after local completion; merge, release, and live mutation are not authorized.

---

### Task 1: Remove the compatibility layer

**Files:**
- Modify: `AGENTS.md`
- Modify: `skills/AGENTS.md`
- Modify: `plugins/AGENTS.md`
- Modify: `.github/workflows/skill-architecture.yml`
- Modify: `scripts/test_skill_authoring_guidance.py`
- Modify: `scripts/test_skill_ci_workflow.py`
- Delete: `scripts/validate_repository_compatibility.py`
- Delete: `scripts/test_validate_repository_compatibility.py`

**Interfaces:**
- Consumes: Human-approved compatibility-removal amendment in `sdd-implementation-skill-design.md`.
- Produces: portable skill authoring contract without compatibility validation; runtime-selected plugin packaging; CI without repository compatibility steps.

- [x] **Step 1: Write failing guidance and CI tests**

Update authoring tests to require:

```text
Plugins may target one runtime.
Do not add another runtime package solely for compatibility.
```

Update CI contract tests to require that neither compatibility script path nor compatibility workflow step remains.

- [x] **Step 2: Run RED**

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_authoring_guidance.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_ci_workflow.py
```

Expected: both suites fail against the still-current compatibility policy and CI steps.

- [x] **Step 3: Remove current compatibility requirements**

Keep `AGENTS.md` as a short router. In `skills/AGENTS.md`, retain standard
`SKILL.md`, capability-based behavior, architecture validation, and
skill-creator validation; remove repository compatibility validation. In
`plugins/AGENTS.md`, allow one selected runtime and forbid extra packages added
solely for compatibility. Delete the compatibility validator and tests, and
remove their CI steps.

- [x] **Step 4: Run GREEN**

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_authoring_guidance.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/test_skill_ci_workflow.py
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/sdd-implementation/tests
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation
git diff --check
```

Expected: all commands exit 0; repository script test count decreases by the deleted compatibility suite.

- [x] **Step 5: Commit Task 1**

```bash
git add AGENTS.md skills/AGENTS.md plugins/AGENTS.md .github/workflows/skill-architecture.yml scripts
git commit -m "Remove cross-runtime compatibility requirements"
```

### Task 2: Durable closeout and publication readiness

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Modify: `knowledge/wiki/syntheses/sdd-compatibility-removal-follow-up-plan.md`
- Modify: `knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

**Interfaces:**
- Consumes: Task 1 commit, independent review, and fresh verification.
- Produces: current compatibility-free contract, historical dual-host boundary, local-complete evidence, and PR-ready branch.

- [x] **Step 1: Close historical and current boundaries**

Mark the old dual-host design historical for both skill behavior and plugin
packaging compatibility. Record that no current compatibility validator or CI
gate exists. Preserve historical implementation plans and prior log entries.

- [x] **Step 2: Synchronize index and log**

Add this plan once to the Active Page Catalog, update the current SDD design
summary if needed, and append closeout evidence with exact tests, review
verdicts, residual risks, and authorized/unperformed remote actions.

- [x] **Step 3: Run verification**

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s scripts
git diff --check
```

- [x] **Step 4: Commit Task 2**

```bash
git add knowledge/wiki/syntheses/sdd-implementation-skill-design.md knowledge/wiki/syntheses/sdd-compatibility-removal-follow-up-plan.md knowledge/wiki/syntheses/hermes-dual-host-authoring-contract-design.md knowledge/index.md knowledge/log.md
git commit -m "Close out compatibility removal"
```

## 関連ページ

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — current agent-agnostic and compatibility-free contract。
- [SDD Agent-Agnostic Runtime Contract Implementation Plan](sdd-agent-agnostic-runtime-implementation-plan.md) — preceding runtime behavior change and review evidence。
- [Codex / Hermes Dual-host Authoring Contract 設計](hermes-dual-host-authoring-contract-design.md) — historical compatibility design。

## 出典

- Human publish choice and clarification: 2026-07-28, “2。ただし、互換性は不要です。”
- `AGENTS.md`
- `skills/AGENTS.md`
- `plugins/AGENTS.md`
