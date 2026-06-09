# Lint Mode

単一 source の処理ではなく、wiki 全体の health check をするときに使います。

Read first: `references/core.md`, chosen topology reference, then this file. Read `references/optional-tooling.md` only if better search or reporting is needed.

## Goal

wiki が断片的な summary の寄せ集めへ劣化する前に、構造的な弱点を見つける。lint は検出、軽微修正、`draft-review` / `canonicalize` への routing を主責務とする。

## Check First

- `index.md` が重要 page を網羅しているか。
- owner として扱う root では、`Draft Target` に未整理 draft が残っていないか。
- `log.md` に recent ingest はあるのに wiki 更新が追随していない箇所はないか。
- inbound link のない page はどれか。
- 新しい source で superseded されていそうな claim はどれか。
- 繰り返し言及されるのに独立 page を持たない concept はどれか。

## Default Procedure

1. `index.md` と `log.md` を走査する。
2. owner として扱う root では `Draft Target` を確認し、未整理 draft を `draft-review` 候補として記録する。
3. orphan page, stale page, contradiction candidate, recurring unnamed concept を洗う。
4. 編集前に対象 page を確認して問題を確定する。
5. link 修正、明白な `index.md` catalog 漏れ、stale claim の superseded 明記など軽微な修正だけ行う。
6. draft 採否判断は `draft-review`、rename / merge / archive / split / rehome は `canonicalize` へ routing する。
7. 具体的な gap がある箇所だけ targeted な source 追加や web check を提案する。
8. 所見、routing 結果、軽微修正を `log.md` の `lint` entry へ記録する。

## Common Lint Findings

- inbound link を持たない page。
- 同じ concept の重複 page。
- entity / concept へ波及していない source summary。
- citation trail のない assertion。
- newer source を反映していない synthesis page。
