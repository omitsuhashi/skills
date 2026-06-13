---
kind: synthesis
created: 2026-06-08
updated: 2026-06-09
source_files:
  - knowledge/raw/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md
---

# LLM Wiki Draft Review And Canonicalize Goal Spec

## 目的

`skills/llm-wiki` を、local Markdown wiki の汎用 lifecycle skill として強化する。今回の実装は Portfolio OS などの固有 runtime には触れず、既存文書とテンプレートだけを更新する。

Goal command は短く保ち、このファイルを詳細な実装契約として参照する。

## 実装範囲

対象は `skills/llm-wiki/` 配下の文書とテンプレートに限定する。

- `skills/llm-wiki/SKILL.md`
- `skills/llm-wiki/references/core.md`
- `skills/llm-wiki/references/structure.md`
- `skills/llm-wiki/references/page-authoring.md`
- `skills/llm-wiki/references/single-root.md`
- `skills/llm-wiki/references/multi-root.md`
- `skills/llm-wiki/references/modes/*.md`
- `skills/llm-wiki/assets/templates/draft-note.md`
- `skills/llm-wiki/assets/templates/index.md`
- `skills/llm-wiki/assets/templates/log.md`
- `skills/llm-wiki/assets/templates/AGENTS.md`
- `skills/llm-wiki/agents/openai.yaml`

今回は validator, script, test harness, external orchestrator は追加しない。

## 非対象

次は実装しない。

- Portfolio OS 固有 runtime
- Hermes profile
- work unit / work_unit
- commander / council
- registry-core / governance-core
- TOML registry schema
- companies repo 固有 path
- profile-set
- canonical owner の system-specific 実装
- draft 採否判断や canonical merge 判断を行う script

## 実装方針

### 1. `SKILL.md`

- mode list を `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` に更新する。
- Router で base read set を `core.md` + topology reference + 該当 mode file に限定する。
- `structure.md`, `page-authoring.md`, `optional-tooling.md` は必要時だけ読む conditional detail reference として扱う。
- direct durable change と proposed draft の違いを明確にする。
- `Reference Map` と `Common Mistakes` が新 mode と矛盾しないように更新する。

### 2. `references/modes/*.md`

- 各 mode は `core.md`、topology reference、自身の mode file だけで開始できるようにする。
- `draft-review` は owner actor が proposed note を `promote`, `merge`, `reject`, `defer` のいずれかで閉じる procedure として定義する。
- `canonicalize` の action set は rename, merge, archive, split, rehome とする。
- `lint` は検出、軽微修正、`draft-review` / `canonicalize` への routing に責務を寄せる。
- page 本文、link、citation、page boundary を触る時だけ `page-authoring.md` を読む。

### 3. `core.md`, `structure.md`, `page-authoring.md`

- `core.md` は layers, draft status, write boundary, `Index Invariant`, `Log Invariant` だけを持つ最小 always-read reference とする。
- `structure.md` は default layout, page type, durable document routing, naming, frontmatter guidance を持つ。
- `page-authoring.md` は page boundary, linking, citation rules を持つ。
- Page Boundary に split と rehome を含める。

### 4. `multi-root.md`

- system-specific root registry adapter hook を追加する。
- generic `llm-wiki` が必要とする field は `Root ID`, `Root URI/Path`, `Scope`, `Canonical Owner`, `Read`, `Write`, `Draft Target` に限定する。
- registry file format, approval workflow, project taxonomy, runtime names は local adapter または local `AGENTS.md` に残す。
- Root Types は固定 taxonomy ではなく common examples として扱う。

### 5. Templates

- `draft-note.md` に `Status`, `Review State`, `Related Pages`, `Source Summary`, `Confidence`, `Open Questions`, `Destination Page`, `Log Entry`, `Follow-up` を追加する。
- `index.md` template に draft / rejected / deferred note を active page として載せない旨を追加する。
- `log.md` template に `draft-review` entry example と `canonicalize` entry example を追加する。
- `AGENTS.md` template の canonical procedure と log 説明に `draft-review`, `canonicalize` を含める。
- skill-local reference path であることを template に明記し、生成先 knowledge root の相対 path と誤読させない。

## Acceptance Criteria

- `SKILL.md` に `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` がすべて現れる。
- `SKILL.md` の base read set が `core.md` + topology reference + exactly one mode file に限定されている。
- `core.md` が always-read invariant に絞られ、layout / page type / naming / citation / frontmatter detail を持たない。
- `references/modes/draft-review.md` に `promote`, `merge`, `reject`, `defer` の decision が明記されている。
- `references/modes/canonicalize.md` に rename, merge, archive, split, rehome の action が明記されている。
- direct write boundary が維持されている。owner かつ `Write: owned` の場合だけ direct canonical update し、non-owner は draft note に回す。
- `core.md` に `Index Invariant` と `Log Invariant` がある。
- `multi-root.md` に system-specific adapter hook がある。
- template 更新が新 mode と一致している。
- 汎用 `llm-wiki` skill 本体に禁止語彙が入っていない。

## Verification Commands

Goal 実装後、最低限次を実行する。

```bash
rg -n "draft-review|canonicalize|promote|merge|reject|defer|Index Invariant|Log Invariant|adapter" skills/llm-wiki
```

```bash
rg -n "operations\\.md|schema-and-conventions\\.md|federated-knowledge-roots\\.md" skills/llm-wiki knowledge/AGENTS.md
```

```bash
rg -n "Portfolio OS|Hermes|work_unit|commander|council|registry-core|governance-core|companies|Kanban" skills/llm-wiki
```

2つ目と3つ目の command は no matches が期待値。禁止語彙 command は raw source や `knowledge/` ではなく `skills/llm-wiki` だけを対象にする。

## Goal Prompt Draft

```text
/goal `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` を実装契約として読み、`skills/llm-wiki/` の既存文書とテンプレートだけを更新してください。validator/script/test harness は追加しないでください。`draft-review` と `canonicalize` を first-class mode にし、`index.md` / `log.md` invariant、generic root adapter hook、draft-note/log/index/AGENTS templates を spec 通りに反映してください。完了条件は spec の Acceptance Criteria を満たし、Verification Commands の確認結果を報告することです。
```

## 出典

- [2026-06-08 LLM Wiki Draft Review And Canonicalize Design](../sources/2026-06-08%20LLM%20Wiki%20Draft%20Review%20And%20Canonicalize%20Design.md)
- [raw source](../../raw/sources/2026-06-08%20LLM%20Wiki%20Draft%20Review%20And%20Canonicalize%20Design.md)
