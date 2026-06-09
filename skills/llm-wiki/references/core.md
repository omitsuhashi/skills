# Core Contracts

すべての mode と topology で共有する契約です。ここには root の数に依存しない invariant だけを置きます。

## Contents

- Layers
- Default Layout
- Page Types
- Durable Document Routing
- Draft Contract
- Write Boundary
- Page Boundary And Canonicalization
- Citation Rules
- Index Invariant
- Log Invariant

## Layers

- `knowledge root`: wiki 運用の単位。dedicated wiki repo なら repo root、mixed repo なら `knowledge/` などの subdirectory に置いてよい。
- `raw/`: immutable source material. 読んでも編集しない。
- `wiki/`: maintained knowledge base. LLM が作成・更新する durable page を置く。
- `AGENTS.md`: skill への router と local contract。汎用運用ルールは重複させない。
- `index.md`: active canonical durable wiki page の catalog。
- `log.md`: durable change の append-only audit trail。

durable な本文は日本語を基本にする。

## Default Layout

Mixed repository:

```text
repo-root/
├── AGENTS.md
└── <knowledge-root>/
    ├── raw/
    │   ├── sources/
    │   └── assets/
    ├── wiki/
    │   ├── sources/
    │   ├── entities/
    │   ├── concepts/
    │   ├── syntheses/
    │   ├── queries/
    │   └── drafts/
    ├── index.md
    ├── log.md
    └── AGENTS.md
```

Dedicated wiki repository:

```text
repo-root/
├── raw/
│   ├── sources/
│   └── assets/
├── wiki/
│   ├── sources/
│   ├── entities/
│   ├── concepts/
│   ├── syntheses/
│   ├── queries/
│   └── drafts/
├── index.md
├── log.md
└── AGENTS.md
```

## Page Types

- `wiki/sources/`: source summary。主要 claim、この source が重要な理由、open question、entity / concept / synthesis への outbound link を持つ。
- `wiki/entities/`: 人、組織、製品、場所、登場人物などの named thing。
- `wiki/concepts/`: 複数 source をまたぐ theme, method, argument, framework, recurring idea。
- `wiki/syntheses/`: 比較、thesis、timeline、due diligence note、briefing、短い report、roadmap、ADR、spec、design doc、implementation plan。
- `wiki/queries/`: 質問起点で保存価値がある回答、比較メモ、判断材料メモ、短報。
- `wiki/drafts/`: owner 以外の actor が作る proposed note。draft は canonical wiki page ではなく、owner review queue として扱う。

## Durable Document Routing

他 workflow が durable な文書を作る場合も、knowledge root に回収できるようにする。デフォルト routing:

- roadmap, ADR, spec, design doc, implementation plan, briefing, comparison note は `wiki/syntheses/`
- 質問起点の短い判断メモや比較メモは `wiki/queries/`

project 固有の下位構造を使うなら、knowledge-root `AGENTS.md` に local override として明記する。

## Naming Defaults

- wiki page の filename は読みやすい Title Case を基本にする。
- 1 file 1 durable topic を守る。
- raw source の filename はそのまま保つ。
- chronology が重要な source summary や query note は date prefix を付ける。

推奨 filename パターン:

- `wiki/sources/2026-04-12 Article Title.md`
- `wiki/entities/Vannevar Bush.md`
- `wiki/concepts/Persistent Knowledge Base.md`
- `wiki/syntheses/LLM Wiki Architecture.md`
- `wiki/syntheses/Checkout API Phase 1 Spec.md`
- `wiki/queries/2026-04-12 Compare RAG And LLM Wiki.md`
- `wiki/drafts/2026-04-12 Proposed Update To Checkout Claims.md`

## Draft Contract

draft note は verified claim ではない。owner が `promote` または `merge` するまで canonical page へ反映せず、`index.md` の active page 一覧にも載せない。

draft note は最低限、対象 root、対象 canonical page / claim、提案内容、根拠 source、作成 actor、owner に求める action、作成日を持つ。

Draft status values:

- `proposed`: owner decision 前の提案。
- `promoted`: verified claim として新規または既存 canonical page に反映済み。
- `merged`: unique な内容だけを既存 canonical page に統合済み。
- `rejected`: 採用しない理由を残して active queue から外した状態。
- `deferred`: 未判断の理由と次の条件を残して保留した状態。

frontmatter は必須ではない。local convention が frontmatter を安定運用しているなら `status` や `review_state` を置いてよい。そうでない場合は draft note の `Status` section にある `Current Status` を authoritative として扱い、`Owner Decision` section に decision date、decider、reason を残す。

## Write Boundary

direct canonical update は、actor が canonical owner であり、target root が `Write: owned` であり、local contract または adapter がその action を許す場合だけ行う。

non-owner actor は verified claim を直接更新しない。durable proposal は target root の draft note に route する。draft target が未解決、root 外、または write が `closed` の場合は書かずに session user へ確認する。

owner `draft-review` と `canonicalize` は routine write とは別の authority だが、canonical page へ直接反映できるのは `Write: owned` かつ local contract または adapter が owner canonical update を許す場合に限る。

## Page Boundary And Canonicalization

- 1 file 1 durable topic を守る。
- 強く重なる page を見つけたら、どちらを canonical page にするか決める。
- canonical page は標準的な名前、明確な scope、継続参照しやすさを優先して選ぶ。
- `rename`, `merge`, `archive`, `split`, `rehome` は lightweight に扱い、後継 page と discoverability を残す。

direct canonicalize 後は最低限、`index.md`, `log.md`, 触った page の link、canonical page への inbound link を更新する。authority を満たさない actor は canonical page を直接編集せず、draft note へ routing する。

## Linking Rules

- Markdown link を基本にする。
- `[[LLM Wiki Architecture]]` のような wikilink は使える環境なら歓迎する。
- summary page から entity / concept / synthesis へ outward link を張る。
- 新しい durable page には最低 1 本の inbound link を作る。
- 強く重なる 2 page は明示的に link し、境界を説明する。

## Citation Rules

- durable page には `## 出典` section を置く。
- 関連する raw file か source summary page へ戻れるようにする。
- 争点がある claim や驚く claim は、平坦化せず inline で disagreement を書く。

推奨 citation パターン:

```markdown
## 出典

- [2026-04-12 Article Title](wiki/sources/2026-04-12%20Article%20Title.md)
- [raw/sources/article-title.md](raw/sources/article-title.md)
```

wikilink を使う環境なら、次のように置き換えてもよい。

```markdown
## 出典

- [[2026-04-12 Article Title]]
- [[raw/sources/article-title.md]]
```

## Index Invariant

`index.md` は canonical discoverability invariant です。active canonical durable wiki page は `index.md` から発見できなければなりません。

- page type ごとに整理する。
- active canonical durable wiki page を 1 回ずつ載せる。
- 各 page に 1 行 summary を付ける。
- draft は verified claim ではないため、現役 page 一覧に載せない。
- rejected note, deferred note, archived duplicate, merged source page は active page として載せない。
- rename / merge / archive 後は canonical page だけを現役一覧に残す。
- split / rehome 後は新しい canonical page と保存先だけを現役一覧に残す。

## Log Invariant

`log.md` は durable change audit trail invariant です。verified claim、canonical page、`index.md`、draft decision、canonicalization action に影響する変更は、いつ、何を、どの page に対して行ったか追える必要があります。

- bootstrap, ingest, query filing, lint pass ごとに 1 entry。
- draft-review decision ごとに 1 entry、または draft の `Owner Decision` section と紐づく entry。
- rename / merge / archive / split / rehome の canonicalize action も 1 entry。
- 予測しやすい prefix で始める。
- 何が変わり、どの page を触ったかを残す。

推奨 entry header:

```markdown
## [2026-04-12] ingest | Article Title
```

## Frontmatter Guidance

frontmatter は必須ではない。Dataview や構造化 audit を使うなら最小限に保つ。

```yaml
---
kind: concept
created: 2026-04-12
updated: 2026-04-12
tags:
  - llm-wiki
source_files:
  - raw/sources/article-title.md
---
```
