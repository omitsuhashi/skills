---
summary: タスクの役割よりリスクを優先して思考強度を選ぶ当時の変更とレビュー証跡を確認できる。
knowledge_status: historical
aliases:
- 思考強度のリスク優先
---
# SDD Reasoning Effort Risk Precedence Implementation Plan

## 適用範囲と履歴

当時の SDD 設計・実装証跡であり、本文の current / active / 実行可能は当時の範囲を指す。SDD 既定ルートは [PR #58](https://github.com/omitsuhashi/skills/pull/58)、KIS / decide-in-order 本体は commit `99fdaf2` で削除されている。現行の作業ツリー保全規約は repository root の `AGENTS.md` を参照する。部分的な仕様置換と当時の承認・未承認の区別は本文に保持する。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Use `superpowers:writing-skills` and `superpowers:test-driven-development` for the Skill contract change.

> **Status:** `LOCAL_COMPLETE`。2026-07-28にHumanが承認したlow / medium / high mappingとrisk-over-role precedenceをTask 1で実装し、independent reviewはapprovedとなった。final whole-branch reviewのImportant 2件はbounded fixで解消し、scoped re-reviewはresolved 2/2、新規Critical / Importantなしで`APPROVED`となった。remote writeは未実施である。

**Goal:** `sdd-implementation`のreasoning effort overlayに、roleではなく実taskのcomplexity / riskを優先する判定規則を追加し、通常のtask reviewはmedium、architecture-sensitive / high-risk task reviewはhighになることを固定する。

**Architecture:** Superpowers SDDのmodel tier ownershipは変更しない。repo-local runtime-only overlayの既定値もlow / medium / highのまま維持し、複数classに該当する場合だけ高いrisk classを優先する。host-specificなhigher effort levelは共有default contractへ追加せず、明示的runtime overrideに限定する。

**Tech Stack:** Markdown Skill instructions、Python 3.9+ `unittest` contract tests、LLM Wiki。

## Constraints

- upstream Superpowers SDD Model Selectionをmodel tierの唯一の正本とする。
- reasoning effortはmodel tierと独立したruntime-only overlayとする。
- 全taskを一段上げず、既定mappingはlow / medium / highのまま維持する。
- task classificationがrole defaultより優先される。high-risk task reviewはhighとする。
- explicit user runtime effort override、stuck-fix one-step escalation、`not_supported` handlingは維持する。
- `xhigh`、`max`、`ultra`その他host-specific levelを共有default vocabularyに追加しない。
- concrete model、effort、provider、availability、agent ID、run-specific resolutionをdurable artifactへ保存しない。
- Codex / Hermes Agentの両方で読めるhost-neutral contractを維持する。
- push、PR、merge、release、live installはscope外とする。

## Task 1: Add risk-over-role effort precedence

**Files:**
- Modify: `skills/sdd-implementation/tests/test_skill_contract.py`
- Modify: `skills/sdd-implementation/SKILL.md`

- [x] `superpowers:writing-skills`と`superpowers:test-driven-development`を適用する。
- [x] high-risk task reviewがhighになる明示規則と、共有default vocabularyがlow / medium / highに限定されることをcontract testへ追加する。
- [x] focused testを実行し、既存Skillで期待どおりREDになることを確認する。
- [x] `SKILL.md`へtask complexity / riskがrole defaultより優先される規則を最小追加する。
- [x] focused testを再実行しGREENを確認する。
- [x] implementer reportとdiffを独立task reviewerへ渡し、material findingなしの`APPROVED`を得る。

## Task 2: Close out durable knowledge and verify

**Files:**
- Modify: `knowledge/wiki/syntheses/sdd-implementation-skill-design.md`
- Modify: `knowledge/wiki/syntheses/sdd-effort-risk-precedence-implementation-plan.md`
- Modify: `knowledge/index.md`
- Modify: `knowledge/log.md`

- [x] canonical design、index、append-only logを実装結果へ同期する。
- [x] focused tests、repository validators、dual-host compatibility、Skill quick validation、`git diff --check`をfreshに実行する。
- [x] final whole-branch reviewerがspec、plan、Skill、tests、knowledge artifactsを同じbranch rangeで確認し、knowledge discoverability / provenanceのImportant 2件を返す。
- [x] bounded fix `a7d0d294a6ccdbeec84f44c0cd6f3060967de5d1`へのscoped re-reviewで両finding解消、新規Critical / Importantなしの`APPROVED`を得る。
- [x] material findingがないことを確認し、local completionを記録する。

## Completion Evidence

- Task 1のspec / plan commitは`c49fa714c917d4a0e7948ab92dfb828f2748b555`（`docs: define SDD effort risk precedence`）、implementation commitは`2549892c07dc3f65c22094ca27b9208c831e65b0`（`Clarify SDD effort risk precedence`）である。
- Task 1 implementer reportは、REDの18 tests中1 failureからGREENの18/18 `OK`への移行、`git diff --check`成功、独立task reviewerの`APPROVED`とmaterial findingなしを記録している。
- closeout candidateのfresh verificationは、SDD contract 18 tests、repository scripts 43 tests、LLM Wiki 5 testsが各`OK`、`validate_skill_architecture.py --all`、`validate_skill_context.py --all`、scoped dual-host compatibility、skill quick validation、`git diff --check`が成功である。
- closeout candidate `ffa8339df00a5a8dfec90f572e843509516f49fe`へのfinal whole-branch reviewは、indexの検索語associationとfocused planのrelated-page / provenance不足をImportant 2件として返した。bounded fix `a7d0d294a6ccdbeec84f44c0cd6f3060967de5d1`後のLLM Wiki 5 testsと`git diff --check`は成功した。
- bounded fixへのscoped re-reviewは両Important findingをresolvedと確認し、新規Critical / Importantなしで`APPROVED`となった。`c49fa714c917d4a0e7948ab92dfb828f2748b555`、`2549892c07dc3f65c22094ca27b9208c831e65b0`、`ffa8339df00a5a8dfec90f572e843509516f49fe`、`a7d0d294a6ccdbeec84f44c0cd6f3060967de5d1`を含むlocal completion contractは完了した。
- `LOCAL_COMPLETE`を記録する。push、PR、merge、release、live installその他のremote writeは未実施である。

## 関連ページ

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — risk-over-role precedenceとlow / medium / high vocabularyを定義するcanonical Written Spec。
- [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) — upstream model tier ownershipとrepo-local reasoning effort境界を確認する調査。

## 出典

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — 本planの要件、acceptance criteria、completion contractの正本。
- [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) — Superpowersのmodel selectionとreasoning effort非所有を確認した一次情報調査のsynthesis。

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

high-risk task reviewをhighとして扱い、共有default effort vocabularyを増やさない変更は、Task 1、final review、bounded fix、scoped re-reviewを完了した`LOCAL_COMPLETE` plan。

## 訂正履歴への入口

当時の主張・承認・検証の訂正は [[log|保存された履歴]] の次の見出しを検索して確認する。先行する完了・適用表現だけでは判断しない。

- `[2026-07-28] final-review-fix-candidate | SDD Reasoning Effort Risk Precedence`
