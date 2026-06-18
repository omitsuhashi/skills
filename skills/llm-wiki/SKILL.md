---
name: llm-wiki
description: Use when building or maintaining a persistent knowledge base in a local Markdown wiki, with optional Obsidian compatibility, where raw sources stay immutable and the LLM incrementally updates wiki pages, index.md, and log.md.
---

# LLM Wiki

## Overview

この skill は、local Markdown wiki を都度再発見する RAG ではなく、蓄積される knowledge base として運用するためのものです。canonical な link style は relative Markdown link を基本とし、Obsidian は optional viewer / tooling として扱います。耐久性のある成果物は wiki であり、`raw/` は不変、`index.md` と `log.md` は first-class の運用ファイルとして扱います。wiki documentation は本文を日本語で保つことを基本にします。

mixed repo では、wiki 専用の `knowledge root` を 1 つ決めます。repo root の `AGENTS.md` は thin router に留め、knowledge root の `AGENTS.md` もこの skill への導線と local override だけを書く thin contract として扱います。汎用的な wiki 運用ルールの canonical source はこの skill です。

## Router

作業前に mode と topology を判定し、必要な reference だけを読む。全 reference を最初から読まない。

1. Mode を 1 つ選ぶ: `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint`。
2. Topology を判定する:
   - `single-root`: knowledge-root `AGENTS.md` を authority source とし、root registry は作らない。
   - `multi-root`: system-specific root registry adapter で Root ID / URI / Scope / Owner / Read / Write / Draft Target を解決する。
3. Read set を選ぶ:
   - Always read: `references/core.md`
   - `single-root`: add `references/single-root.md`
   - `multi-root`: add `references/multi-root.md`
   - Add exactly one mode file under `references/modes/`
   - 作業中に必要になった detail reference だけを追加で読む。

Do not read `references/multi-root.md` for ordinary `single-root` ingest or query. Do not read every mode file to start a task.

## Read Sets

Base read set for every task:

- `references/core.md`
- exactly one topology file: `references/single-root.md` or `references/multi-root.md`
- exactly one mode file under `references/modes/`

Detail references are conditional:

- `references/structure.md`: read only when choosing or creating layout, page type, durable document routing, naming, or frontmatter.
- `references/page-authoring.md`: read only before creating/updating page body text, citations, links, or page boundaries.
- `references/optional-tooling.md`: read only when optional tools are directly useful.

## Quick Rules

- Inspect `index.md` before touching wiki pages unless the task is pure bootstrap.
- Direct canonical update is allowed only when actor is canonical owner, target has `Read: allowed`, target allows `Write: owned`, and the local contract or adapter allows the action.
- In multi-root topology, proposed notes are allowed only when adapter resolution returns `Read: allowed`, `Write: owned` or `propose`, and a resolved in-root `Draft Target`.
- If adapter resolution returns `Read: restricted`, `Read: no-access`, `Write: closed`, unresolved target root, or unresolved `Draft Target`, do not write a verified claim or proposed note; confirm with the session user or local governance.
- Non-owner durable proposals route to a draft note only when the write boundary permits it; draft is not a verified claim.
- Owner `draft-review` decisions are exactly `promote`, `merge`, `reject`, `defer`.
- `canonicalize` actions are exactly `rename`, `merge`, `archive`, `split`, `rehome`.
- Update `index.md` and `log.md` for direct durable changes, draft-review decisions, canonicalize actions, ingest, durable query filing, and lint passes. Treat `index.md` as the reader-facing discovery surface: purpose shortcuts plus an Active Page Catalog with summary and search terms.
- If an answer creates durable value, file it back into the wiki instead of leaving it in chat only when write boundary permits.
- Pause only for ambiguous, high-impact, or multi-page changes. Routine low-risk updates proceed autonomously.

## Reference Map

- `references/core.md`
  `raw/`, `wiki/`, draft status, write boundary, `Index Invariant`, `Log Invariant` の最小共通契約。
- `references/single-root.md`
  root registry を作らない topology。knowledge-root `AGENTS.md` を authority source とし、owner / write boundary / draft target を local contract に置く。
- `references/multi-root.md`
  複数 knowledge root を持つ system で、adapter の Root ID / URI / Scope / Owner / Read / Write / Draft Target から保存先と cross-root policy を判断するルール。
- `references/structure.md`
  layout, page type, durable document routing, naming, frontmatter guidance。必要な時だけ読む。
- `references/page-authoring.md`
  page boundary, linking, citation rules。本文作成・更新時だけ読む。
- `references/modes/*.md`
  mode ごとの check first, default procedure, pause rules。
- `references/optional-tooling.md`
  Obsidian Web Clipper, local image handling, Dataview, Marp, `qmd` などの任意ツール。どれも必須ではありません。
- `assets/templates/`
  knowledge-root 用 thin `AGENTS.md`, repo root 用 `root-AGENTS.md`, Markdown registry を採用する multi-root 用 `root-registry.md`, `index.md`, `log.md`, source/entity/concept/synthesis/query note, implementation progress ledger, `draft-note.md` の初期雛形。

## Common Mistakes

- `raw/` の source file を編集すること。
- 既存 wiki を見ずに記憶だけで答えること。
- page を更新したのに `index.md` や `log.md` を更新しないこと。
- canonical owner authority がない、または local contract / adapter が禁止しているのに canonical page を直接更新すること。
- proposed draft を判断履歴なしに削除すること。
- draft を active page として `index.md` の現役一覧に載せること。
- `index.md` を path catalog だけにして、目的別入口、summary、検索語を欠いたままにすること。
- 発見性を Python validator, CI check, graph generator, Dataview 必須化, Obsidian plugin 依存で機械的に採点しようとすること。
- 価値のある query output を chat にだけ残して wiki に還元しないこと。
- superpowers など別 workflow が作る durable な spec / ADR / roadmap / plan を knowledge root の外へ散らし、wiki の catalog と切り離すこと。
- 重複 page を見つけても canonical page を決めずに増やし続けること。
- scope 固有 claim をより広い shared root や別 actor root に混ぜること。
- role 固有 strategy を project domain wiki など別 scope の root に混ぜること。
- 複数 knowledge root 間で canonical owner を決めず、同じ知識を copy すること。
- lint で検出した rename / merge / archive / split / rehome を、`canonicalize` decision なしに大きく進めること。
- wiki documentation を英語へ寄せて、継続運用の読みやすさを落とすこと。
- knowledge root の `AGENTS.md` に汎用運用ルールを複写し、skill 側と二重管理にすること。
- mixed repo なのに detailed な wiki 運用契約を repo root の `AGENTS.md` に長く書くこと。
- 全 reference を最初から読み込むこと。必要な section だけ読むこと。
