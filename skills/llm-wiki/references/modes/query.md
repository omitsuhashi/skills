# Query Mode

maintained wiki に対して質問へ答えるときに使います。

Read first: `references/core.md`, chosen topology reference, then this file. Read `references/structure.md` only when filing a new durable output. Read `references/page-authoring.md` only when updating page body text, links, or citations.

## Goal

compiled wiki を再利用して根拠付きで素早く答え、その出力自体を wiki に残すべきか判断する。

## Check First

- `index.md` のどこが関連 page を指しているか。
- actor が owner ではない場合、durable output を `Draft Target` に proposed note として残せるか。
- 既に必要 topic をまとめている wiki page はあるか。
- 裏取りや dispute resolution に raw source が要るか。
- 回答は一時的なものか、durable page にすべきか。

## Default Procedure

1. `index.md` から始める。
2. 必要最小限の wiki page を読む。
3. wiki が薄い、争点がある、古い場合だけ raw citation を追加で引く。
4. 必要に応じて wiki page と raw source を引用して答える。
5. 再利用価値があり、`Read: allowed`, `Write: owned`, actor が canonical owner のすべてを満たす場合だけ、`wiki/queries/` か `wiki/syntheses/` に page を作るか更新する。
6. direct update できず `Read: allowed`, `Write: owned` または `propose`, `Draft Target` 解決済みの場合は、durable output を root 内の `Draft Target` に proposed note として残す。
7. direct update した場合だけ、新しい durable page を `index.md` に登録し、`log.md` に `query` entry を追加する。書けない root では canonical page, `index.md`, `log.md` を直接更新しない。

## File-Back Rule

次のいずれかに当てはまるなら、回答を wiki へ戻す。

- 比較や synthesis を後で再利用しそう。
- taxonomy, table, framing など durable な整理を作れた。
- query が露出させた gap を新しい page が埋めた。
- user が durable note, memo, briefing, deck, report を明示的に求めた。

## Pause And Align When

- query の結果をどの page に落とすべきか曖昧で、既存 page を大きく再編しそう。
- 回答が複数の durable artifact 候補にまたがり、emphasis の置き方で成果物が変わる。
- query への回答が broad rewrite や rename / merge 判断を伴う。
