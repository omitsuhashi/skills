# Page Authoring

canonical page、draft note、source summary、query note を作成または本文更新する時だけ読む reference です。index/log だけを見る routine query では読まない。

## Page Boundary And Canonicalization

- 1 file 1 durable topic を守る。
- 強く重なる page を見つけたら、どちらを canonical page にするか決める。
- canonical page は標準的な名前、明確な scope、継続参照しやすさを優先して選ぶ。検索語を filename に詰め込まず、`index.md` の summary / 検索語、heading、本文 link で補う。
- `rename`, `merge`, `archive`, `split`, `rehome` は lightweight に扱い、後継 page と discoverability を残す。

direct canonicalize 後は最低限、`index.md`, `log.md`, 触った page の link、canonical page への inbound link を更新する。authority を満たさない actor は canonical page を直接編集せず、draft note へ routing する。

## Discovery Authoring Checklist

canonical page を作成または本文更新したら、direct update が許される場合だけ次を確認する。

- `index.md` の目的別入口に reader task の代表 shortcut として載せるべきか判断する。全 page を載せる必要はない。
- `index.md` の Active Page Catalog に 1 回だけ載せ、1 行 summary と主要検索語を付ける。entry は `- [[Page]] — summary` の次行に `検索語: ...` を置く 2 行構成を基本にする。
- procedure / operation 系 page は、該当する検索語だけを英日混在で入れる。例: `setup`, `install`, `update`, `operate`, `troubleshoot`, `セットアップ`, `インストール`, `アップデート`, `運用`, `トラブルシュート`。
- synthesis, query-note, procedure / operation 系 page には `## 関連ページ` または同等の outward links を置く。
- source summary, entity, concept page でも、読者が次に辿る意味のある page があるなら outward link を置く。
- 新しい durable page には `index.md` からの inbound link を持たせる。

## Linking Rules

- Markdown link を基本にする。
- Obsidian-friendly root では `[[LLM Wiki Architecture]]` のような wikilink を推奨標準にする。非 Obsidian 環境や portability を優先する root では Markdown link でもよい。
- summary page から entity / concept / synthesis へ outward link を張る。
- 新しい durable page には最低 1 本の inbound link を作る。
- 強く重なる 2 page は明示的に link し、境界を説明する。

## Citation Rules

- durable page には `## 出典` section を置く。
- 関連する raw file か source summary page へ戻れるようにする。
- 争点がある claim や驚く claim は、平坦化せず inline で disagreement を書く。

推奨 citation パターン:

```markdown
## 出典

- [2026-04-12 Article Title](wiki/sources/2026-04-12%20Article%20Title.md)
- [raw/sources/article-title.md](raw/sources/article-title.md)
```

wikilink を使う環境なら、次のように置き換えてもよい。

```markdown
## 出典

- [[2026-04-12 Article Title]]
- [[raw/sources/article-title.md]]
```
