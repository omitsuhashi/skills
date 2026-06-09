# Core Invariants

すべての mode と topology で最初に読む最小契約です。layout、page type、citation などの作業依存 detail はここに置かず、必要になった時だけ別 reference を読む。

## Layers

- `knowledge root`: wiki 運用の単位。
- `raw/`: immutable source material. 読んでも編集しない。
- `wiki/`: maintained knowledge base. durable page を置く。
- `AGENTS.md`: skill への router と local contract。汎用運用ルールは複写しない。
- `index.md`: active canonical durable wiki page の catalog。
- `log.md`: durable change の append-only audit trail。

durable な wiki documentation は本文を日本語で保つ。

## Draft Contract

draft note は verified claim ではない。owner が `promote` または `merge` するまで canonical page へ反映せず、`index.md` の active page 一覧にも載せない。

最低限、対象 root、対象 canonical page / claim、提案内容、根拠 source、作成 actor、owner に求める action、作成日を持つ。

Draft status values:

- `proposed`: owner decision 前の提案。
- `promoted`: verified claim として新規または既存 canonical page に反映済み。
- `merged`: unique な内容だけを既存 canonical page に統合済み。
- `rejected`: 採用しない理由を残して active queue から外した状態。
- `deferred`: 未判断の理由と次の条件を残して保留した状態。

## Write Boundary

direct canonical update は、actor が canonical owner であり、target root が `Read: allowed` かつ `Write: owned` であり、local contract または adapter がその action を許す場合だけ行う。

non-owner actor は verified claim を直接更新しない。durable proposal は target root が `Read: allowed` で、`Write: owned` または `propose` で、draft target が root 内に解決済みの場合だけ draft note に route する。`Read: restricted`, `Read: no-access`, `Write: closed`, draft target 未解決、または root 外へ解決される場合は verified claim も proposed note も書かずに session user または local governance へ確認する。

owner `draft-review` と `canonicalize` は routine write とは別の authority だが、canonical page へ直接反映できるのは target root が `Read: allowed` かつ `Write: owned` で、local contract または adapter が owner canonical update を許す場合に限る。

## Index Invariant

`index.md` は canonical discoverability invariant です。active canonical durable wiki page は `index.md` から発見できなければなりません。

- active canonical durable wiki page を 1 回ずつ載せる。
- 各 page に 1 行 summary を付ける。
- draft は verified claim ではないため、現役 page 一覧に載せない。
- rejected note, deferred note, archived duplicate, merged source page は active page として載せない。
- rename / merge / archive 後は canonical page だけを現役一覧に残す。
- split / rehome 後は新しい canonical page と保存先だけを現役一覧に残す。

## Log Invariant

`log.md` は durable change audit trail invariant です。verified claim、canonical page、`index.md`、draft decision、canonicalization action に影響する変更は追える必要があります。

- bootstrap, ingest, query filing, lint pass ごとに 1 entry。
- draft-review decision ごとに 1 entry、または draft の `Owner Decision` section と紐づく entry。
- rename / merge / archive / split / rehome の canonicalize action も 1 entry。
- 予測しやすい prefix で始める。
- 何が変わり、どの page を触ったかを残す。
