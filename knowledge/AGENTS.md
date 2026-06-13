# LLM Wiki Router

この directory は `skills` repository の persistent な LLM-maintained wiki の knowledge root です。

## Canonical Procedure

- wiki の `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` の汎用手順は `llm-wiki` スキルを canonical source として扱う
- 汎用的な schema, naming, citation, canonicalization, `index.md` / `log.md` 更新規約も `llm-wiki` スキルに従う
- `llm-wiki` skill の base read set は skill-local `references/core.md` + topology reference + 該当 `references/modes/*.md` とし、detail references は必要時だけ読む
- この file はスキルの複製ではなく、この knowledge root 固有の前提と差分だけを書く

## Local Contract

- knowledge root はこの directory とする
- Canonical Owner は repository maintainer または maintainer-delegated actor とする
- Write Boundary は `owned` とし、owner actor だけが verified claim を直接更新できる
- non-owner actor の durable proposal は `wiki/drafts/` に routing する
- この repository は single-root topology として扱い、root registry は作らない
- `raw/` は不変の source material として扱い、読んでも編集しない
- `wiki/` は maintained knowledge base として扱い、作成と更新はここで行う
- `index.md` は active canonical durable wiki page の catalog として扱う
- `log.md` は bootstrap, ingest, query, draft-review decision, canonicalize action, lint, Goal command preparation の append-only timeline として扱う
- canonical link style は relative Markdown link とし、Obsidian wikilink `[[...]]` は使わない
- root を跨ぐ参照は Markdown link にせず、`root-id:path/inside/root.md` 形式で書く
- wiki documentation の本文は日本語を基本にする
- Goal command 用の長い詳細仕様、実装契約、acceptance criteria は `wiki/syntheses/` に保存する
- Goal prompt は短く保ち、詳細仕様ファイルを明示的に参照する

## Local Overrides

- `skills/` 配下の skill 本体は実装対象であり、knowledge root ではない
- Goal command preparation の成果物は、直接 skill reference に混ぜず、まず `knowledge/wiki/syntheses/` に保存する
- 汎用運用ルールをここへ再掲しない

## Conflict Rule

- この file の local rule が `llm-wiki` スキルと衝突する場合は、この file をこの knowledge root の優先ルールとして扱う
