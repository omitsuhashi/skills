---
title: SDD fail-closed worktree gate 実装計画
page_type: synthesis
date: 2026-08-14
created_date: 2026-08-14
last_updated: 2026-08-14
approved_on: 2026-08-14
tags:
  - sdd-implementation
  - worktree
  - fail-closed
  - implementation-plan
aliases:
  - SDD fail-closed worktree gate implementation plan
status: accepted
lifecycle_state: active
implementation_status: local-complete-with-parked-harness-risks
artifact_kind: implementation-plan
decision: accepted-scope-revision
decision_actor: Human / repository maintainer (Canonical Owner)
decision_date: 2026-08-14
decision_reason: Human が最小scopeのcurrent implementation planを承認したため
source_draft: "[[wiki/drafts/sdd-fail-closed-worktree-gate-implementation-plan|SDD fail-closed worktree gate 実装計画（昇格済み draft）]]"
source_spec: "[[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|SDD fail-closed worktree gate 仕様]]"
provenance:
  - Human の implementation plan 明示承認（2026-08-14）
  - Human の scope-reduction owner decision（2026-08-14）
  - "[[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|SDD fail-closed worktree gate 仕様]]"
relations:
  - "[[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|Implements: SDD fail-closed worktree gate 仕様]]"
  - "[[wiki/syntheses/sdd-plan-ownership-alignment|Composes with: SDD Plan Ownership Alignment 仕様]]"
---

# SDD fail-closed worktree gate 実装計画

> [!success] Human-approved current plan
> 本計画は2026-08-14のscope reductionを反映する。旧draftはhistorical proposal evidenceであり、guard/activation設計をcurrent planとして復活させない。

## Status and constraints

- 状態: `accepted` / `active`; source implementationは `LOCAL_COMPLETE_WITH_PARKED_HARNESS_RISKS`。Task review、fresh verification、whole-branch review後の唯一のfix waveとscoped re-reviewを完了した。
- 実装は [[wiki/syntheses/sdd-fail-closed-worktree-gate-spec|accepted specification]] の5要件だけを満たす。
- original checkout `/Users/omitsuhashi/repos/omitsuhashi/skills` の `main` はtask workでread-onlyであり、task commitを受けない。
- first source / canonical durable repository write前にtask-linked worktreeをcreate/verifyしてbindingできなければ、writeなしの `BLOCKED` で止まる。native commitも同じworktreeへbindし、fallbackはない。raw transient handoffは[[wiki/syntheses/sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]が所有するrepository-external bounded capabilityへrouteする。
- current cloneのhook/config activation、external cache、install、remote、CI新設は実施しない。main/#49由来のtransient-artifact validator / CI contractは維持し、integrationで生じたregressionだけをそのauthority内で最小修正する。

## Task 0: Scope-reduction cleanup and durable-document sync

旧guard/activation/lifecycle/tuple/bootstrap要件をcanonical specとこのplanから撤回し、`knowledge/index.md`とappend-only `knowledge/log.md`を同期する。promoted draftsは変更せず、historical proposal evidenceとして保持する。

Acceptance: canonical spec/planの規範が最小5要件だけであり、indexはminimal gateを説明し、logはHuman decisionとimplementation in progressを記録する。

## Task 1: Remove over-design and simplify the First-Write Gate

`skills/sdd-implementation/scripts/prepare-commit-msg` を削除する。guard-specific contractとtestsを削除し、少なくとも `skills/sdd-implementation/tests/test_commit_guard_behavior.py`、guard/bootstrap/lifecycle portions of `skills/sdd-implementation/tests/test_fail_closed_entry_behavior.py`、およびguard-only scenario harness contractを除去または最小gate contractへ置換する。

既存 `skills/sdd-implementation/tests/test_first_write_worktree_contract.py` と `skills/sdd-implementation/tests/test_skill_contract.py` を、SDD-first、original `main` unchanged、verified linked worktreeへのsource / canonical durable writeとnative commitのbinding、repository-external bounded capabilityへのraw transient handoff、failure zero-write `BLOCKED`、no fallbackを検査する形に簡素化する。`skills/sdd-implementation/SKILL.md` と関連router/reference proseからguard activation、hook/config inventory、rollback、one-time bootstrap、exact tuple authorityを削除する。

Acceptance: raw Git-level manual-commit prohibitionを主張せず、repo-owned SDD workflowの最小boundaryだけがsourceとfocused testsに残る。

Final-review fix waveでは、multi-output rollback harnessを削除し、opaque owner identity、single-new-artifact atomic publish、gate-owned native commit plan、EPERM / missing dependency / writer-construction failureのfour-field `BLOCKED` normalizationへ限定して補正する。original/stale CWDはrunner前に拒否し、pre-existing target replacementはharnessのzero-write保証対象に含めない。

## Task 2: Validate architecture, context, skill, and preservation

実装後、current repoの次を実行する。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 -m unittest discover -s skills/sdd-implementation/tests -v
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 -m unittest discover -s scripts -v
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 scripts/report_skill_context.py --all --json --fail-on-warning
PYTHONPYCACHEPREFIX=/private/tmp/sdd-fail-closed-worktree-gate python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/sdd-implementation
git diff --check c370fe14de1641aa5ee30b3fa001f4d857078091..HEAD
git -C /Users/omitsuhashi/repos/omitsuhashi/skills status --short
```

Acceptance: architecture/context/skill validationとfull SDD suiteがpassし、full branch rangeにwhitespace errorがなく、original checkoutはcleanのまま `main@c370fe14de1641aa5ee30b3fa001f4d857078091` である。

Closeout evidenceでは、このliteral HEAD clauseは外部state changeにより一致しない。original checkoutは開始時clean `main@c370fe14de1641aa5ee30b3fa001f4d857078091`から外部でclean `main@82dcd32157ff9690ae038f982f3916009e449f80`へforward advanceした。開始SHAはcurrent `main`のancestorで、16 task commitsはいずれも`main`に含まれない。literal HEAD preservationまたはintegrationを主張しない。

## Task 3: Implementation closeout and one whole-branch review

Task 1--2 evidenceをcurrent spec/planへ同期し、source implementation completionをclaimする前にfresh whole-branch reviewを1回実施する。reviewはこのapproved minimal scopeへの適合、withdrawn guard/activation designのnon-return、original checkout preservation、verification evidenceを確認する。

Acceptance: one whole-branch reviewにmaterial findingがなく、required checksとoriginal-checkout preservation evidenceが記録される。未実施のcheck、review、またはsource workがあれば `in progress` を維持し、完了を先取りしない。

Final-review fix waveのfocused REDは23 tests中7 failures / 3 errorsで、requested gapを再現した。最小実装後のfocused GREENは23/23、full SDD suiteは66/66、scriptsは19/19である。architecture/context/context-report/skill-creatorはすべてpassし、context reportは`warnings: []`、complete branch rangeの`git diff --check`はcleanである。

Task reviewはfix round 4後にclean。whole-branch reviewの4 Important findingに対する唯一のfix wave `90acc95b33935fec82c3bf03fb39405d2bd19894` はtask-owner / commit-CWD bindingとcatalog supersessionを補正し、scoped re-reviewで確認された。

2件はcontroller-parkedのnon-production harness fidelity riskとして残る。harness modelではcheck後のconcurrent target creationを`os.replace`がclobberし得ること、cleanup `unlink` failureで`.sdd-stage-*`が残りescapeし得ることである。このharnessはproduction-strength concurrent transactionではなく、いずれのriskもrepo-owned SDDからoriginal `main`へwrite/commitするpathを作らない。

このためmaterial findingなしというideal acceptanceは文字どおりには満たしていない。controller adjudicationにより、最小5要件とraw Git boundaryを満たすsource resultを`LOCAL_COMPLETE_WITH_PARKED_HARNESS_RISKS`とし、無条件の`LOCAL_COMPLETE`は主張しない。withdrawn済みのguard、hook、activation、inventory、bootstrap、lifecycle、external-cache、exact-tuple、general rollback設計は不在のままである。resultはlocal-onlyで、push、PR、install、activation、`main` integrationは未実施。
