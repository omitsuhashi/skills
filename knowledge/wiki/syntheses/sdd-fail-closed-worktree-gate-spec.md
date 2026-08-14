---
title: SDD fail-closed worktree gate 仕様
page_type: synthesis
date: 2026-08-14
created_date: 2026-08-14
last_updated: 2026-08-14
approved_on: 2026-08-14
tags:
  - sdd-implementation
  - worktree
  - fail-closed
  - specification
aliases:
  - SDD fail-closed worktree gate specification
status: accepted
lifecycle_state: active
artifact_kind: specification
decision: accepted-scope-revision
decision_actor: Human / repository maintainer (Canonical Owner)
decision_date: 2026-08-14
decision_reason: Human が過剰設計を撤回し、最小のrepo-owned SDD workflow boundaryを明示承認したため
source_draft: "[[wiki/drafts/sdd-fail-closed-worktree-gate-spec|SDD fail-closed worktree gate 仕様（昇格済み draft）]]"
provenance:
  - Human の Written Spec 明示承認（2026-08-14）
  - Human の scope-reduction owner decision（2026-08-14）
  - .superpowers/research/sdd-fail-closed-worktree-gate/research.md
  - skills/sdd-implementation/SKILL.md
  - "[[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]]"
relations:
  - "[[wiki/syntheses/sdd-first-write-worktree-migration-spec|Scoped predecessor: SDD first-write worktree migration 仕様]]"
---

# SDD fail-closed worktree gate 仕様

> [!success] Human-approved accepted revision
> 2026-08-14 のHuman owner decisionにより、本書は最小スコープへ改訂された。promoted draftは歴史的なproposal evidenceとして保持し、currentな規範は本書だけとする。

## Status

- 状態: `accepted` / `active`
- canonical identity: `knowledge/wiki/syntheses/sdd-fail-closed-worktree-gate-spec.md`
- 決定: `accepted-scope-revision`
- 決定権者: Human / repository maintainer（Canonical Owner）
- source implementation: `in progress`。final-review fix後のscoped re-review前であり、実装完了を主張しない。

## Problem and earlier evidence

repository change が直接のwritable supporting skillから始まると、original/default checkout にartifact、source、commitが入る余地がある。worktree allocation、permission、path、ownership、capability、dependency、またはbindingを確認できないときに別directoryで続行することも、repo-owned SDD workflowの安全境界に反する。

既存検討では Git commit guard、hook/config inventory、activation transaction、rollback、bootstrap exception、external cache/lifecycle split を追加していた。しかしHumanは、これらは元の要求に対する過剰設計であり、current scopeから撤回すると決定した。

## Accepted normative requirements

1. repository work は `sdd-implementation` から開始する。
2. このrepositoryのoriginal primary/default checkout、すなわち `main` は task work では read-only であり、task commitを受けない。
3. 最初のrepository content/artifact writeより前に、task-linked worktreeを作成または検証し、すべてのwriteとcommitをそのworktreeにbindする。
4. allocation、permission、path、ownership、capability、dependency、またはbindingを満たせない場合は、content/artifact writeなしで `BLOCKED` を返す。
5. current/original directory、その他のdirectory、または別workflowへのfallbackは行わない。

## Boundary and non-goals

この保証はrepository-owned SDD workflowのboundaryである。任意のmanual shell commitをraw Git levelで禁止するものではない。

次はHumanによりwithdrawnであり、non-goalである。

- Git hook、commit-guard source、`--no-verify` defense
- hook/config inventory、activation transaction、rollback machinery、operational activation
- lifecycle split、one-time guard bootstrap、exact tuple authority
- external cache treatmentを含むguard固有のruntime/operational design

本仕様はexternal plugin cache、remote publication、install、CIの新設を要求しない。promoted draftは変更せず、歴史的proposal evidenceとして残す。

### Executable evidence boundary

最小gateのwrite evidenceは、controllerがmintしたopaque owner capabilityをallocator resultへidentityでbindし、1 invocationにつき「既存parent配下の新規artifact 1件」だけをcomplete data planとして検証してからworktree内でstageし、atomic publishする。複数artifactとpre-existing target replacementはmutation前に`BLOCKED`とし、best-effort rollbackを保証しない。

commit evidenceはwrite invocationと分離したgate-owned data-only `git commit` planをnative runnerで実行する。verified task worktreeと一致しないoriginal/stale CWDはrunner invocation前に`BLOCKED`とし、arbitrary callbackは受け取らない。このharness boundaryはraw Git一般を禁止する新規mechanismではない。

## Acceptance criteria

- repository changeは `sdd-implementation` をfirst entryとする。
- original `main` checkoutはtask開始時から終了時までtask write・task commitを受けない。
- すべてのrepository content/artifact writeとcommitは、作成または検証済みのtask-linked worktree内にある。
- allocation、permission、path、ownership、capability、dependency、binding failureは、writeなしの `BLOCKED` になる。
- original/current directory、他directory、direct writable subskillへのfallbackはない。direct writable subskillはrepository workを開始できず `BLOCKED` になる。

## Provenance and lifecycle

本書は2026-08-14のHuman Written Spec approval、同日のscope-reduction owner decision、ならびに先行researchと既存 `sdd-implementation` contractを根拠とする。source implementation、active install、remote stateの完了はこのcanonical revisionから推論しない。

predecessor [[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]]のFirst-Write規範は本書がscoped supersedeする。predecessorのうち本書が扱わない後続Epicのopt-in parallel adapter部分だけは、影響を受けない参照範囲として残る。
