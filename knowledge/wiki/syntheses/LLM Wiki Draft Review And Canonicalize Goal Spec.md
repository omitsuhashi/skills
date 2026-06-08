---
kind: synthesis
created: 2026-06-08
updated: 2026-06-08
source_files:
  - knowledge/raw/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md
---

# LLM Wiki Draft Review And Canonicalize Goal Spec

## 目的

`skills/llm-wiki` を、local Markdown wiki の汎用 lifecycle skill として強化する。今回の実装は Portfolio OS などの固有 runtime には触れず、既存文書とテンプレートだけを更新する。

Goal command は短く保ち、このファイルを詳細な実装契約として参照する。

## 実装範囲

対象は `skills/llm-wiki/` 配下の既存ファイルに限定する。

- `skills/llm-wiki/SKILL.md`
- `skills/llm-wiki/references/operations.md`
- `skills/llm-wiki/references/schema-and-conventions.md`
- `skills/llm-wiki/references/federated-knowledge-roots.md`
- `skills/llm-wiki/assets/templates/draft-note.md`
- `skills/llm-wiki/assets/templates/index.md`
- `skills/llm-wiki/assets/templates/log.md`
- `skills/llm-wiki/assets/templates/AGENTS.md`

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
- Quick Workflow で direct durable change と proposed draft の違いを明確にする。
- `draft-review` mode entry check を追加する。
- `canonicalize` mode entry check を追加する。
- `Reference Map` と `Common Mistakes` が新 mode と矛盾しないように更新する。

### 2. `operations.md`

- `query` と `lint` の間に `draft-review` section を追加する。
- `draft-review` は owner actor が proposed note を `promote`, `merge`, `reject`, `defer` のいずれかで閉じる procedure として定義する。
- `promote` / `merge` 後は canonical page, `index.md`, `log.md` を更新する。
- `reject` / `defer` でも理由と判断履歴を draft 側または `log.md` に残し、判断履歴なしに削除しない。
- 既存の `Page Lifecycle And Canonicalization` を `canonicalize` mode として昇格する。
- `canonicalize` の action set は rename, merge, archive, split, rehome とする。
- `lint` は検出、軽微修正、`draft-review` / `canonicalize` への routing に責務を寄せる。

### 3. `schema-and-conventions.md`

- `wiki/drafts/` に draft status convention を追加する。
- status は `proposed`, `promoted`, `merged`, `rejected`, `deferred` とする。
- frontmatter は必須にせず、local convention がなければ `Owner Decision` section を使う。
- `index.md` を canonical discoverability invariant として定義する。
- `log.md` を durable change audit trail invariant として定義する。
- Page Boundary に split と rehome を追加する。

### 4. `federated-knowledge-roots.md`

- system-specific root registry adapter hook を追加する。
- generic `llm-wiki` が必要とする field は `Root ID`, `Root URI/Path`, `Scope`, `Canonical Owner`, `Read`, `Write`, `Draft Target` に限定する。
- registry file format, approval workflow, project taxonomy, runtime names は local adapter または local `AGENTS.md` に残す。
- Root Types は固定 taxonomy ではなく common examples として扱う。

### 5. Templates

- `draft-note.md` に `Status`, `Review State`, `Related Pages`, `Source Summary`, `Confidence`, `Open Questions`, `Destination Page`, `Log Entry`, `Follow-up` を追加する。
- `index.md` template に draft / rejected / deferred note を active page として載せない旨を追加する。
- `log.md` template に `draft-review` entry example と `canonicalize` entry example を追加する。
- `AGENTS.md` template の canonical procedure と log 説明に `draft-review`, `canonicalize` を含める。

## Acceptance Criteria

- `SKILL.md` に `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` がすべて現れる。
- `operations.md` に `draft-review` section があり、`promote`, `merge`, `reject`, `defer` の decision が明記されている。
- `operations.md` に `canonicalize` section があり、rename, merge, archive, split, rehome の action が明記されている。
- direct write boundary が維持されている。owner かつ `Write: owned` の場合だけ direct canonical update し、non-owner は draft note に回す。
- `schema-and-conventions.md` に `Index Invariant` と `Log Invariant` がある。
- `federated-knowledge-roots.md` に system-specific adapter hook がある。
- template 更新が新 mode と一致している。
- 汎用 `llm-wiki` skill 本体に禁止語彙が入っていない。

## Verification Commands

Goal 実装後、最低限次を実行する。

```bash
rg -n "draft-review|canonicalize|promote|merge|reject|defer|Index Invariant|Log Invariant|adapter" skills/llm-wiki
```

```bash
rg -n "Portfolio OS|Hermes|work_unit|commander|council|registry-core|governance-core|companies|Kanban" skills/llm-wiki
```

2つ目の command は no matches が期待値。ただし raw source や `knowledge/` ではなく `skills/llm-wiki` だけを対象にする。

## Goal Prompt Draft

```text
/goal `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` を実装契約として読み、`skills/llm-wiki/` の既存文書とテンプレートだけを更新してください。validator/script/test harness は追加しないでください。`draft-review` と `canonicalize` を first-class mode にし、`index.md` / `log.md` invariant、generic root adapter hook、draft-note/log/index/AGENTS templates を spec 通りに反映してください。完了条件は spec の Acceptance Criteria を満たし、Verification Commands の確認結果を報告することです。
```

## 出典

- [[2026-06-08 LLM Wiki Draft Review And Canonicalize Design]]
- [raw source](../../raw/sources/2026-06-08%20LLM%20Wiki%20Draft%20Review%20And%20Canonicalize%20Design.md)
