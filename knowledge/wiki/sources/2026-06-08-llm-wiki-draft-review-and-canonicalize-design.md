---
kind: source
created: 2026-06-08
updated: 2026-06-13
source_files:
  - knowledge/raw/sources/2026-06-08 LLM Wiki Draft Review And Canonicalize Design.md
---

# 2026-06-08 LLM Wiki Draft Review And Canonicalize Design

## 要約

添付設計は、汎用 `llm-wiki` skill 本体に入れるべき強化を、Portfolio OS などの固有 runtime から切り離して整理している。中心は、`draft-review` と `canonicalize` を first-class mode として追加し、`index.md` と `log.md` 更新を page lifecycle invariant として明文化すること。

## 主要 Claim

- `llm-wiki` は外部 orchestrator ではなく、LLM が読んで自己運用できる procedure として強化する。
- 既存の `bootstrap`, `ingest`, `query`, `lint` は維持し、`draft-review` と `canonicalize` を追加する。
- draft は未整理 inbox ではなく owner review queue として扱い、`promote`, `merge`, `reject`, `defer` のいずれかで閉じる。
- `canonicalize` は rename / merge / archive だけでなく、split / rehome も扱える mode にする。
- `index.md` は canonical discoverability、`log.md` は durable change audit trail を担保する invariant として扱う。
- multi-root / federated root は特定 registry format に依存せず、generic field を解決する adapter hook として扱う。
- 汎用 `llm-wiki` skill 本体には Portfolio OS, Hermes, commander, registry-core などの固有語彙を入れない。

## Goal Spec への反映

- Goal command の長さ制限を避けるため、詳細実装契約は [LLM Wiki Draft Review And Canonicalize Goal Spec](../syntheses/llm-wiki-draft-review-and-canonicalize-goal-spec.md) に保存する。
- Goal prompt は同 spec を参照し、既存 `skills/llm-wiki/` 文書とテンプレートだけを更新する。

## Open Questions

- 実装後、この Goal spec を knowledge wiki に残し続けるか、実装完了後に retrospective note へ圧縮するか。
- 今回は validator/script を追加しないが、将来 skill repo 全体の lint command を持つか。

## 出典

- [raw source](../../raw/sources/2026-06-08%20LLM%20Wiki%20Draft%20Review%20And%20Canonicalize%20Design.md)
