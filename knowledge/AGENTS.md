# LLM Wiki Router

この directory は `skills` repository の persistent な LLM-maintained wiki の knowledge root です。

## Canonical Procedure

- wiki の `bootstrap`, `ingest`, `query`, `lint` の汎用手順は [llm-wiki](../skills/llm-wiki/SKILL.md) を canonical source として扱う
- 汎用的な schema, naming, citation, `index.md` / `log.md` 更新規約も同じ `SKILL.md` に従う
- 旧版の mode / topology reference は前提としない。`draft-review` / `canonicalize` は下記の repository-local な所有者・草案ルールとして扱う
- この file はスキルの複製ではなく、この knowledge root 固有の前提と差分だけを書く

## Local Contract

- knowledge root はこの directory とする
- Canonical Owner は repository maintainer または maintainer-delegated actor とする
- Read: `allowed`
- Write Boundary は `owned` とし、owner actor だけが verified claim を直接更新できる
- non-owner actor の durable proposal は `wiki/drafts/` に routing する
- `draft-review` は草案の出典・矛盾・統合先を確認し、owner の判断を記録する。review 自体で canonical page を変更しない
- `canonicalize` は owner またはその委任を受けた actor が承認済みの草案を既存 page に統合、または新規 page として採用する。出典を保持し、草案に統合先と処理済みの状態を残し、index / log を同期する
- この repository は single-root topology として扱い、root registry は作らない
- `raw/` は不変の source material として扱い、読んでも編集しない
- `wiki/` は maintained knowledge base として扱い、作成と更新はここで行う
- `index.md` は active canonical durable wiki page の catalog として扱う
- `log.md` は bootstrap, ingest, query, draft-review decision, canonicalize action, lint, Goal command preparation の append-only timeline として扱う
- authoring profile: obsidian
- 既存の internal note link は knowledge root 相対の `[[wiki/...|表示名]]` を維持し、external URL は Markdown link とする。追加の authoring skill は必須としない
- root 外への参照は既存の target identity を保持し、解決できない参照を推測で置換しない
- wiki documentation の本文は日本語を基本にする
- Goal command 用の長い詳細仕様、実装契約、acceptance criteria は `wiki/syntheses/` に保存する
- Goal prompt は短く保ち、詳細仕様ファイルを明示的に参照する

## Local Overrides

- `skills/` 配下の skill 本体は実装対象であり、knowledge root ではない
- Goal command preparation の成果物は、直接 skill reference に混ぜず、まず `knowledge/wiki/syntheses/` に保存する
- 汎用運用ルールをここへ再掲しない

## Conflict Rule

- この file の local rule が `llm-wiki` スキルと衝突する場合は、この file をこの knowledge root の優先ルールとして扱う
