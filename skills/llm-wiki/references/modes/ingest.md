# Ingest Mode

`raw/` に新しい source が入り、wiki へ統合するときに使います。

Read first: `references/core.md`, chosen topology reference, then this file. Read `references/structure.md` only when choosing destination page type or naming a new page. Read `references/page-authoring.md` before creating or updating page body text.

## Goal

新しい source の知識を一度だけコンパイルし、その結果を persistent wiki 全体へ配ることで、後続 query が毎回 synthesis をやり直さなくて済むようにする。

## Check First

- 新しく入った source file はどれか。
- 書き込み先 root の `Read` は `allowed` か。
- 書き込み先 root の `Write` は `owned`, `propose`, `closed` のどれか。
- actor が owner でない場合、`Draft Target` は解決できるか。
- 影響を受ける既存 page はどれか。
- この source や topic の summary page は既にあるか。
- raw source へ直接 citation すべき claim はどれか。

## Default Procedure

1. `raw/` から source を読む。
2. `index.md` の目的別入口と現役 page catalog を見て関連 page を当てる。
3. 編集前に直接関係する entity / concept / synthesis page を開く。
4. 書き込み先 root の `Read`, `Write`, owner, `Draft Target` から更新経路を決める。
5. `Read: allowed`, `Write: owned`, actor が canonical owner のすべてを満たす場合だけ、source summary page と関係 page, `index.md`, `log.md` を直接更新する。新規または大きく変わった page は `index.md` の Active Page Catalog に summary / 検索語付きで登録し、代表的 reader task に当たる場合だけ目的別入口にも shortcut を追加する。
6. direct update できず `Read: allowed`, `Write: owned` または `propose`, `Draft Target` 解決済みの場合は、root 内の `Draft Target` に proposed note を作る。canonical page, `index.md`, `log.md` は直接更新しない。
7. `closed`, `restricted`, `no-access`, target 不明、または `Draft Target` 未解決の場合は書かずに session user へ確認する。

## Editing Rules

- raw file は不変に保つ。
- 自然に分解できるなら、大きな 1 枚より小さな複数 page を優先する。
- 古い claim を黙って置き換えず、矛盾を明示する。
- source summary から entity / concept へ事実を運ぶときも citation を保つ。
- procedure / operation 系の知識を取り込む場合は、利用者が検索しそうな英日検索語を `index.md` の catalog entry に入れる。

## Pause And Align When

- 1 つの source が複数 page の境界を作り直しそう。
- 既存 page の canonical 名称や topic boundary を変える必要がある。
- source の解釈が割れ、どの framing を採るかで downstream page が大きく変わる。

それ以外の routine な summary 追加、citation 補強、軽い cross-link 追加は自律で進める。
