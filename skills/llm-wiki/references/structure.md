# Structure And Routing

knowledge root の layout、page type、durable document routing、naming を決める時だけ読む reference です。routine query では読まない。

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
- `wiki/syntheses/`: 比較、thesis、timeline、due diligence note、briefing、短い report、roadmap、ADR、spec、design doc、implementation plan、implementation progress ledger。
- `wiki/queries/`: 質問起点で保存価値がある回答、比較メモ、判断材料メモ、短報。
- `wiki/drafts/`: owner 以外の actor が作る proposed note。

## Durable Document Routing

他 workflow が durable な文書を作る場合も、knowledge root に回収できるようにする。デフォルト routing:

- roadmap, ADR, spec, design doc, implementation plan, briefing, comparison note は `wiki/syntheses/`
- partial implementation, roadmap progress, remaining scope を横断して追う implementation progress ledger は `wiki/syntheses/`
- 質問起点の短い判断メモや比較メモは `wiki/queries/`

project 固有の下位構造を使うなら、knowledge-root `AGENTS.md` に local override として明記する。

implementation progress ledger は、個別の spec / plan / progress note を置き換えない。複数の implementation slice の状態、残 scope、証跡、次回 review 条件へリンクする discovery surface として扱う。active canonical page なので `index.md` の Active Page Catalog から発見できるようにし、更新時は `log.md` に lifecycle entry を残す。validator, scheduler, Dataview, Obsidian plugin, issue tracker 連携は必須にしない。

## Naming Defaults

- wiki page の filename は URL と CLI で扱いやすい lower-kebab-case slug を基本にする。
- filename は ASCII slug を優先し、正式名称や日本語 title は page heading と `index.md` の label / summary に残す。
- 1 file 1 durable topic を守る。
- raw source の filename はそのまま保つ。
- chronology が重要な source summary や query note は date prefix を付ける。

推奨 filename パターン:

- `wiki/sources/2026-04-12-article-title.md`
- `wiki/entities/vannevar-bush.md`
- `wiki/concepts/persistent-knowledge-base.md`
- `wiki/syntheses/llm-wiki-architecture.md`
- `wiki/syntheses/checkout-api-phase-1-spec.md`
- `wiki/syntheses/checkout-implementation-progress-ledger.md`
- `wiki/queries/2026-04-12-compare-rag-and-llm-wiki.md`
- `wiki/drafts/2026-04-12-proposed-update-to-checkout-claims.md`

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
