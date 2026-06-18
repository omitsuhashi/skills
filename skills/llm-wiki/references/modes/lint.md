# Lint Mode

単一 source の処理ではなく、wiki 全体の health check をするときに使います。

Read first: `references/core.md`, chosen topology reference, then this file. Read `references/page-authoring.md` only before applying link, citation, or page-boundary fixes. Read `references/optional-tooling.md` only if better search or reporting is needed.

## Goal

wiki が断片的な summary の寄せ集めへ劣化する前に、構造的な弱点を見つける。lint は LLM/human review procedure であり、機械的な品質採点ではない。検出、軽微修正、`draft-review` / `canonicalize` への routing を主責務とする。

## Check First

- `index.md` が reader-facing discovery surface として機能しているか。
- 目的別入口が代表的 reader task への shortcut になっているか。全 page の完全分類になっていないか。
- Active Page Catalog が active canonical durable page を 1 回ずつ載せ、summary と主要検索語を持っているか。
- procedure / operation 系 page の検索語が、該当する英日語彙を含んでいるか。
- owner として扱う root では、`Draft Target` に未整理 draft が残っていないか。
- `log.md` に recent ingest はあるのに wiki 更新が追随していない箇所はないか。
- active な implementation progress ledger がある場合、`index.md` から発見でき、各 slice に status / evidence / review-after または next trigger があるか。
- inbound link のない page はどれか。
- 新しい source で superseded されていそうな claim はどれか。
- 繰り返し言及されるのに独立 page を持たない concept はどれか。

## Default Procedure

1. `index.md` と `log.md` を走査する。
2. owner として扱う root では `Draft Target` を確認し、未整理 draft を `draft-review` 候補として記録する。
3. orphan page, stale page, contradiction candidate, recurring unnamed concept, discovery gap を洗う。
4. 編集前に対象 page を確認して問題を確定する。
5. link 修正、明白な `index.md` catalog 漏れ、summary / 検索語の軽微な補強、stale claim の superseded 明記など軽微な修正だけ行う。
6. draft 採否判断は `draft-review`、rename / merge / archive / split / rehome は `canonicalize` へ routing する。
7. 具体的な gap がある箇所だけ targeted な source 追加や web check を提案する。
8. 所見、routing 結果、軽微修正を `log.md` の `lint` entry へ記録する。

## Common Lint Findings

- inbound link を持たない page。
- `index.md` の Active Page Catalog に summary または検索語がない page。
- procedure / operation 系 page なのに `setup`, `install`, `update`, `インストール`, `アップデート` など reader search terms がない。
- 目的別入口が page catalog の重複版になり、reader task の shortcut になっていない。
- 同じ concept の重複 page。
- entity / concept へ波及していない source summary。
- citation trail のない assertion。
- newer source を反映していない synthesis page。
- implementation progress ledger の `verified` に証跡 link がない、または `deferred` / `blocked` に理由と review-after / 解除条件がない。
