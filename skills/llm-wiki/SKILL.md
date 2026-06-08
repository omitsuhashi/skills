---
name: llm-wiki
description: Use when building or maintaining a persistent knowledge base in a local Markdown wiki (Obsidian-friendly) where raw sources stay immutable and the LLM incrementally updates wiki pages, index.md, and log.md.
---

# LLM Wiki

## Overview

この skill は、local Markdown wiki（Obsidian-friendly）を都度再発見する RAG ではなく、蓄積される knowledge base として運用するためのものです。耐久性のある成果物は wiki であり、`raw/` は不変、`index.md` と `log.md` は first-class の運用ファイルとして扱います。wiki documentation は本文を日本語で保つことを基本にします。

mixed repo では、wiki 専用の `knowledge root` を 1 つ決めます。repo root の `AGENTS.md` は thin router に留め、knowledge root の `AGENTS.md` もこの skill への導線と local override だけを書く thin contract として扱います。汎用的な wiki 運用ルールの canonical source はこの skill です。

作業のたびに、まずどの層を触るかを決めます。

- `knowledge root/`: wiki 運用の起点となる directory。mixed repo では `knowledge/`, `research/knowledge-base/` などの subdirectory に置いてよい。
- `raw/`: source of truth. Read only. Never edit.
- `wiki/`: LLM-managed pages. Create and update freely.
- `AGENTS.md`: this skill への router と local contract。knowledge root 固有の前提や override だけを書き、汎用運用ルールは重複させない。

## Quick Workflow

1. Identify the mode: `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, or `lint`.
2. Determine the wiki topology and target knowledge root before editing. In `single-root` topology, use the knowledge-root `AGENTS.md` as the entrypoint, record canonical owner and write boundary there, follow a repo-root thin router `AGENTS.md` when one exists, and do not create a root registry. In `multi-root` topology, use the system-specific root registry adapter and `references/federated-knowledge-roots.md`.
3. Read only the matching reference file sections instead of loading everything.
4. Inspect `index.md` before touching wiki pages unless the task is pure bootstrap.
5. During `bootstrap`, define in repo-root and knowledge-root `AGENTS.md` where other workflows should save durable docs. Route superpowers-style outputs such as roadmap, ADR, spec, design doc, and implementation plan into the knowledge root instead of leaving them in repo-root `docs/` by default.
6. For routine durable changes, update canonical pages directly only when the actor is the canonical owner and the target root allows `Write: owned`; otherwise route durable proposals to a draft note. In owner `draft-review` and `canonicalize` modes, treat owner canonical updates as a separate authority resolved by the local contract or adapter.
7. Update `index.md` and `log.md` for every direct durable change, `draft-review` decision, `canonicalize` action, ingest, durable query output, or lint pass.
8. If an answer creates durable value, file it back into the wiki instead of leaving it in chat only.
9. Pause only for ambiguous, high-impact, or multi-page changes. Routine low-risk updates proceed autonomously.

## Mode Entry Checks

### `bootstrap`

wiki / repo の境界を確認し、まず `single-root` / `multi-root` topology と knowledge root を確定します。dedicated wiki repo なら knowledge root は repo root で構いません。mixed repo なら wiki 専用 subdirectory を knowledge root に切り出します。`single-root` では root registry を作らず、repo root の `AGENTS.md` は参照先を示す thin router に留めます。`multi-root` では system-specific root registry adapter を用意し、各 root の owner / access / draft target を解決できるようにします。Markdown registry を使う場合だけ `assets/templates/root-registry.md` を雛形にしてよい。bootstrap 時には、superpowers など他 workflow が出力する durable な spec / ADR / plan / roadmap も knowledge root へ保存する routing を `AGENTS.md` に明示します。構成や命名に複数の妥当案があり、後戻りコストが高いときだけ user と揃えます。

Read:

- `references/schema-and-conventions.md`
- `references/operations.md`

### `ingest`

新しい source と `index.md`, `log.md`, 既存の関連ページを確認します。まず source summary を作るか更新し、その後で entity / concept / synthesis へ変更を波及させます。1 source が複数 page 境界を崩しそう、または解釈が割れるときだけ立ち止まって揃えます。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`

### `query`

`index.md` から入り、関連する wiki page と必要な raw citation へ掘ります。まず maintained wiki を再利用して答え、再利用価値がある結果なら query note か synthesis page として保存し、`index.md` と `log.md` に登録します。保存先や page boundary が曖昧で、既存 page を広く組み替える必要があるときだけ user と揃えます。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`

### `draft-review`

owner actor として proposed note を review queue から閉じるときに使います。対象 draft、canonical page、`index.md`, `log.md` を確認し、decision を `promote`, `merge`, `reject`, `defer` のいずれかにします。`promote` / `merge` では、canonical owner が draft-review authority を持ち、local contract または adapter が owner canonical update を許す場合に verified claim として canonical page に反映し、`index.md` と `log.md` を更新します。`reject` / `defer` でも理由と判断履歴を draft 側または `log.md` に残し、履歴なしに削除しません。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`
- `references/federated-knowledge-roots.md` when resolving multi-root owner / draft target

### `canonicalize`

owner actor として page boundary を整理するときに使います。rename, merge, archive, split, rehome のどれかを選び、canonical discoverability を保ちます。action 後に canonical page、関連 link、`index.md`, `log.md` を直接更新できるのは canonical owner が canonicalize authority を持ち、local contract または adapter が owner canonical update を許す場合です。それ以外の actor や owner update が禁止された root では canonical page を直接組み替えず、draft note へ routing します。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`
- `references/federated-knowledge-roots.md` when action crosses roots

### `lint`

`index.md`, `log.md`, orphan page, contradictions, stale claim, 独立 page を持たない recurring concept を点検します。軽微な link や catalog 修正は行ってよいが、draft 採否は `draft-review`、page boundary の組み替えは `canonicalize` へ routing します。missing source や web 調査は、具体的な gap が見えたときだけ提案します。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`
- `references/optional-tooling.md` only if better search or reporting is needed

## Reference Map

- `references/federated-knowledge-roots.md`
  複数 knowledge root を持つ system で、local adapter の `Scope` / `Canonical Owner` / access / draft target から保存先を判断するためのルール。
- `references/operations.md`
  `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint` の標準手順、pause rules、page boundary 整理の実務ルール。
- `references/schema-and-conventions.md`
  knowledge root の推奨ディレクトリ構成、page 種別、draft status、page boundary、canonicalization、リンク規約、citation 規約、`index.md` / `log.md` invariant。
- `references/optional-tooling.md`
  Obsidian Web Clipper, local image handling, Dataview, Marp, `qmd` などの任意ツール。どれも必須ではありません。
- `assets/templates/`
  knowledge-root 用 thin `AGENTS.md`, repo root 用 `root-AGENTS.md`, Markdown registry を採用する multi-root 用 `root-registry.md`, `index.md`, `log.md`, source/entity/concept/synthesis/query note, `draft-note.md` の初期雛形。

## Common Mistakes

- `raw/` の source file を編集すること。
- 既存 wiki を見ずに記憶だけで答えること。
- page を更新したのに `index.md` や `log.md` を更新しないこと。
- canonical owner authority がない、または local contract / adapter が禁止しているのに canonical page を直接更新すること。
- proposed draft を判断履歴なしに削除すること。
- draft を active page として `index.md` の現役一覧に載せること。
- 価値のある query output を chat にだけ残して wiki に還元しないこと。
- superpowers など別 workflow が作る durable な spec / ADR / roadmap / plan を knowledge root の外へ散らし、wiki の catalog と切り離すこと。
- 重複 page を見つけても canonical page を決めずに増やし続けること。
- scope 固有 claim をより広い shared root や別 actor root に混ぜること。
- role 固有 strategy を project domain wiki など別 scope の root に混ぜること。
- 複数 knowledge root 間で canonical owner を決めず、同じ知識を copy すること。
- lint で検出した rename / merge / archive / split / rehome を、`canonicalize` decision なしに大きく進めること。
- wiki documentation を英語へ寄せて、継続運用の読みやすさを落とすこと。
- knowledge root の `AGENTS.md` に汎用運用ルールを複写し、skill 側と二重管理にすること。
- mixed repo なのに detailed な wiki 運用契約を repo root の `AGENTS.md` に長く書くこと。
- 全 reference を最初から読み込むこと。必要な section だけ読むこと。
