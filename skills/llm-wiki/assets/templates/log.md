# ログ

append-only で使います。すべての entry は予測しやすい header で始めます。

## [2026-04-12] bootstrap | Initialize wiki

- `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を作成
- `llm-wiki` skill を canonical procedure とし、local contract の置き場を確定

## [2026-04-12] ingest | 記事タイトル

- `wiki/sources/2026-04-12 記事タイトル.md` を追加
- `wiki/entities/サンプルエンティティ.md` を更新
- `wiki/concepts/サンプル概念.md` を更新

## [2026-04-12] query | RAG と LLM Wiki を比較する

- `wiki/queries/2026-04-12 RAG と LLM Wiki を比較する.md` を追加
- 比較メモを `index.md` に登録

## [2026-04-12] draft-review | Proposed Update To Checkout Claims

- Decision: merge
- Actor: checkout-owner
- Owner: checkout-owner
- Write Boundary: owner + `Write: owned`
- `wiki/drafts/2026-04-12 Proposed Update To Checkout Claims.md` の unique な内容を canonical page へ統合
- `wiki/concepts/サンプル概念.md` と `index.md` を更新

## [2026-04-12] canonicalize | 重複した概念ページを統合

- Action: merge
- Actor: wiki-owner
- Owner: wiki-owner
- Write Boundary: owner + `Write: owned`
- `wiki/concepts/サンプル概念.md` を canonical page として維持
- 重複 page を merged 扱いにし、案内 link を追加
- `index.md` と関連 link を更新
