# LLM Wiki Router

この directory は persistent な LLM-maintained wiki の knowledge root です。

## Canonical Procedure

- wiki の `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` の汎用手順は `llm-wiki` スキルを canonical source として扱う
- 汎用的な schema, naming, citation, canonicalization, `index.md` / `log.md` 更新規約も `llm-wiki` スキルに従う
- single-root 作業では `llm-wiki` skill の router に従い、skill-local `references/core.md` + `references/single-root.md` + 該当 `references/modes/*.md` を読む
- `references/structure.md`, `references/page-authoring.md`, `references/optional-tooling.md` は task が必要とする時だけ読む
- multi-root へ変更した場合だけ skill-local `references/multi-root.md` を読む
- この file はスキルの複製ではなく、この knowledge root 固有の前提と差分だけを書く

## Local Contract

- knowledge root はこの directory とする
- Topology: single-root
- Root Registry: 作らない
- Canonical Owner:
- Write Boundary: owned | propose | closed
- Draft Target: `wiki/drafts/` when Write Boundary is `owned` or `propose`; `closed` roots accept no canonical or draft writes
- Direct canonical update は canonical owner かつ `Write: owned` かつ local contract が許す場合だけ行う
- non-owner actor の durable proposal は Draft Target に route する
- `raw/` は不変の source material として扱い、読んでも編集しない
- `wiki/` は maintained knowledge base として扱い、作成と更新はここで行う
- `index.md` は active canonical durable wiki page の catalog として扱う
- `log.md` は bootstrap, ingest, query, draft-review decision, canonicalize action, lint の append-only timeline として扱う
- wiki documentation の本文は日本語を基本にする
- superpowers など他 workflow が作る durable な roadmap / ADR / spec / design doc / implementation plan も knowledge root 配下へ保存する
- default routing は、roadmap / ADR / spec / design doc / implementation plan / briefing / comparison note を `wiki/syntheses/`、質問起点の短い判断メモを `wiki/queries/` とする

## Local Overrides

- この knowledge root 固有の命名規則、page type の追加、frontmatter 規約、link 規約、durable doc の保存先 override がある場合だけここへ追記する
- multi-root topology へ変更する場合だけ、system-specific root registry adapter の所在地と root resolution rule をここへ追記する
- 汎用運用ルールをここへ再掲しない

## Conflict Rule

- この file の local rule が `llm-wiki` スキルと衝突する場合は、この file をこの knowledge root の優先ルールとして扱う
