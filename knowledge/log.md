# ログ

append-only で使います。すべての entry は予測しやすい header で始めます。

## [2026-06-08] bootstrap | Initialize skills repo knowledge root

- repo root に thin router `AGENTS.md` を追加
- `knowledge/` を single-root topology の knowledge root として作成
- `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を作成
- Goal command 用の詳細仕様を `knowledge/wiki/syntheses/` に保存する routing を明確化

## [2026-06-08] ingest | LLM Wiki Draft Review And Canonicalize Design

- 添付設計を `knowledge/raw/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md` に保存
- source summary `knowledge/wiki/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md` を追加
- Goal 実装契約 `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` を追加
- `index.md` に source summary と synthesis を登録

## [2026-06-09] canonicalize | LLM Wiki reference read set

- `skills/llm-wiki` の always-read contract を `core.md` に絞り、layout / page authoring detail を conditional reference へ分離
- `knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md` の stale reference 名を更新
- `knowledge/AGENTS.md` に skill-local base read set と conditional detail reference の方針を追記

## [2026-06-10] query | Portfolio OS install review and procedure

- Portfolio OS 固有 runtime が `skills/llm-wiki` 本体に混入していないことを確認
- `knowledge/wiki/syntheses/Portfolio OS Install Review And Procedure.md` に導入レビューと install procedure を追加
- `index.md` に synthesis を登録

## [2026-06-13] lint | Markdown-first link policy

- `skills/llm-wiki` の link policy と templates を relative Markdown link canonical に更新
- `knowledge/` の active wiki links を Obsidian wikilink から relative Markdown link に更新
- rename / canonicalize は今回行わず、既存 filename を維持
