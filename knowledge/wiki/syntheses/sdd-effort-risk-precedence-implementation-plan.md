# SDD Reasoning Effort Risk Precedence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Use `superpowers:writing-skills` and `superpowers:test-driven-development` for the Skill contract change.

> **Status:** 2026-07-28にHumanが現状のlow / medium / high mappingを維持し、task complexity / riskをrole defaultより優先する方針を承認した。Task 1のlocal implementationとindependent reviewは完了・approved、knowledge closeout candidateは作成済みである。final whole-branch reviewは未実施のため`LOCAL_COMPLETE`ではない。

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
- [ ] final whole-branch reviewerがspec、plan、Skill、tests、knowledge artifactsを同じbranch rangeで確認する。
- [ ] material findingがなければlocal completionを記録する。

## Completion Evidence

- Task 1のspec / plan commitは`c49fa714c917d4a0e7948ab92dfb828f2748b555`（`docs: define SDD effort risk precedence`）、implementation commitは`2549892c07dc3f65c22094ca27b9208c831e65b0`（`Clarify SDD effort risk precedence`）である。
- Task 1 implementer reportは、REDの18 tests中1 failureからGREENの18/18 `OK`への移行、`git diff --check`成功、独立task reviewerの`APPROVED`とmaterial findingなしを記録している。
- closeout candidateのfresh verificationは、SDD contract 18 tests、repository scripts 43 tests、LLM Wiki 5 testsが各`OK`、`validate_skill_architecture.py --all`、`validate_skill_context.py --all`、scoped dual-host compatibility、skill quick validation、`git diff --check`が成功である。
- final whole-branch reviewの実施・approvalはpendingであり、`LOCAL_COMPLETE`、`local-complete` log entry、remote writeはいずれも未実施である。
