# LLM Wiki Router

この directory は `skills` repository の persistent な LLM-maintained wiki の knowledge root です。

## Canonical Procedure

- wiki の `bootstrap`, `ingest`, `query`, `lint` の汎用手順は [llm-wiki](../skills/llm-wiki/SKILL.md) を canonical source として扱う
- 汎用的な schema, naming, citation、ページの探索情報と完了規約も同じ `SKILL.md` に従う
- 旧版の mode / topology reference は前提としない。`draft-review` / `canonicalize` は下記の repository-local な所有者・草案ルールとして扱う
- この file はスキルの複製ではなく、この knowledge root 固有の前提と差分だけを書く

## Local Contract

- knowledge root はこの directory とする
- Canonical Owner は repository maintainer または maintainer-delegated actor とする
- Read: `allowed`
- Write Boundary は `owned` とし、owner actor だけが verified claim を直接更新できる
- non-owner actor の知識ページへの durable proposal は `wiki/drafts/` に routing する。実装仕様・実装計画の草案はこの対象外とし、GitHub Issue で扱う
- `draft-review` は草案の出典・矛盾・統合先を確認し、owner の判断を記録する。review 自体で canonical page を変更しない
- `canonicalize` は owner またはその委任を受けた actor が承認済みの草案を既存 page に統合、または新規 page として採用する。出典を保持し、草案に統合先と処理済みの状態を残し、変更ページと実際に影響する知識の本文・探索情報・出典・リンクを整合させる
- この repository は single-root topology として扱い、root registry は作らない
- `raw/` は不変の source material として扱い、読んでも編集しない
- `wiki/` は maintained knowledge base として扱い、作成と更新はここで行う
- 各ページが知識と探索情報の正本である。`summary` と `knowledge_status` は汎用 skill の意味に従い、既存の実装進捗 `status` と区別する
- `wiki/drafts/` は metadata にかかわらず草案であり、既存の owner decision / canonical destination を優先する
- `index.md` や別名の固定全件目録は作成・更新・復元しない。通常の page create / update に central catalog / global log 同期を要求しない
- 保存しない query と read-only lint は永続書込みを行わない。訂正・判断は該当ページ、または該当知識への明示リンクを持つ判断ページへ統合する
- authoring profile: obsidian
- ノートの作成・編集には installed `obsidian-markdown` skill を読み、properties / link / embed / callout と表示確認の手順に従う。構文規約はここに複製しない
- vault の root はこの knowledge root とし、既存の internal note target identity を維持する
- root 外への参照は既存の target identity を保持し、解決できない参照を推測で置換しない
- wiki documentation の本文は日本語を基本にする
- 実装仕様・実装設計・acceptance criteria・実装計画・ローカル Issue 台帳・実行 packet は Wiki に保存しない。保存先・更新手順は `docs/agents/issue-tracker.md` に従い、GitHub Issue 本文を正本とする
- Goal prompt は短く保ち、詳細を持つ GitHub Issue を参照する。Wiki に実装文書のコピーや要約を作らない

## 探索手順

1. 現行の判断・歴史的経緯・全体像のどれを求めるかを捉える。未知の領域では全件、対象が明確なら範囲を絞って生成目録を取得する。
   repository root から `python3 skills/llm-wiki/scripts/catalog.py knowledge` を実行する。
   `--path syntheses/ --query '作業ツリー'` などで絞れる。条件・全件数・該当件数・除外・診断を確認し、分割した場合は未読範囲を把握する。
2. 候補の本文を読み、要約を回答の根拠にしない。別名と本文検索を併用し、要約にない論点も探す。
3. 関連・前提・反証・後継・出典を必要に応じてたどる。逆リンクは現在のファイルを検索する。相互リンク維持だけのために参照先を編集しない。
4. 現行回答では対象名・別名への参照と訂正も検索する。後継側にだけ置換説明がある場合や、部分的置換を確認する。`current` は承認・実装完了の証明ではなく、旧本文の current 表現や更新日時だけで現行扱いしない。実挙動の質問では現存する skill / code も照合する。
5. 見つからなければ検索語と範囲を広げ、unknown・草案・必要な履歴も確認する。未検索範囲を残して「存在しない」と断定せず、本文の根拠を引用する。

Python / 生成器が使えない場合は、`wiki/` のファイル列挙（例: `rg --files knowledge/wiki`）と本文検索（例: `rg -n '語句' knowledge/wiki`）へ退避し、raw・生成先・別 root を対象から分ける。YAML parser がない場合は metadata 抽出を degraded と明示し、パス・見出し・本文から継続する。欠落・不正 metadata のページも落とさず、要約なし／状態不明と診断を示す。読取失敗や途中変更は不完全と報告して再取得する。生成物なし・絞り込みゼロを知識不在と解釈しない。

生成器は現在の worktree の保存済みファイルを対象とし、未コミット追加も列挙する。他 branch の未統合ページは含まない。目録は標準出力で取得して commit しない。閲覧用ファイルが必要になった場合のみ root 内の `.generated/` を専用生成先とし、再生成可能と明記して Git から除外する。JSON 等は対応する説明ページのリンクからたどる。

独立したページ追加は各ページだけで完了する。統合後に再生成し、同概念の重複・矛盾・後継不整合は変更ページと関連範囲の lint で確認する。Git merge 成功だけを content review の代わりにしない。

## 保持する履歴

- `log.md` は過去履歴として保持し、通常追記しない。原資料 `raw/` も不変とする。現在の実装仕様・計画は GitHub Issue を参照する。
- 2026-09-10 の Human 指示で既存の実装仕様・計画・設計原案の要約・台帳・実行資料を Wiki から削除した。過去版が必要なら `git show 9106339:<repository-relative-path>` を使う。削除資料を Wiki に復元したり、固定の履歴目録を作ったりしない。
- raw と過去 log に残る削除資料・index への参照は、その記録時点の歴史的参照である。上記の Git revision で資料を、`git show f63ba68:knowledge/index.md` で旧目録を確認できる。この例外は保存された履歴に限り、新しい Wiki 本文の壊れたリンクは許容しない。
- 旧 branch の統合時は、実装仕様・計画の追加や改訂を該当 Issue へ回収し、削除資料・index・log の通常追記を auto-merge で再導入しない。

## Local Overrides

- `skills/` 配下の skill 本体は実装対象であり、knowledge root ではない
- この保存先ルールは本 repository の方針であり、汎用 `llm-wiki` skill に他の repository 向けの Issue 利用を強制しない
- 汎用運用ルールをここへ再掲しない

## Conflict Rule

- この file の local rule が `llm-wiki` スキルと衝突する場合は、この file をこの knowledge root の優先ルールとして扱う
