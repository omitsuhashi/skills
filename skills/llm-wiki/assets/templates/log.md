# ログ

append-only で使います。Log Invariant: verified claim、canonical page、`index.md`、draft decision、canonicalization action に影響する変更は追跡できなければなりません。すべての entry は予測しやすい header で始めます。

## [2026-04-12] bootstrap | Initialize wiki

- `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を作成
- `llm-wiki` skill を canonical procedure とし、local contract の置き場を確定

## [2026-04-12] ingest | 記事タイトル

- `wiki/sources/2026-04-12-article-title.md` を追加
- `wiki/entities/sample-entity.md` を更新
- `wiki/concepts/sample-concept.md` を更新

## [2026-04-12] query | RAG と LLM Wiki を比較する

- `wiki/queries/2026-04-12-compare-rag-and-llm-wiki.md` を追加
- 比較メモを `index.md` に登録

## [2026-04-12] draft-review | Proposed Update To Checkout Claims

- Decision: merge
- Actor: checkout-owner
- Owner: checkout-owner
- Write Boundary: owned; owner canonical update allowed by local contract
- `wiki/drafts/2026-04-12-proposed-update-to-checkout-claims.md` の unique な内容を canonical page へ統合
- `wiki/concepts/sample-concept.md` と `index.md` を更新

## [2026-04-12] canonicalize | 重複した概念ページを統合

- Action: merge
- Actor: wiki-owner
- Owner: wiki-owner
- Write Boundary: owned; owner canonical update allowed by local contract
- `wiki/concepts/sample-concept.md` を canonical page として維持
- 重複 page を merged 扱いにし、案内 link を追加
- `index.md` と関連 link を更新
