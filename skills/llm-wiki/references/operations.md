# Operations

mode ごとの標準手順をまとめたファイルです。現在の作業に対応する section だけを読みます。

## Default Stance

- routine な low-risk 更新は自律で進める
- 曖昧さが高く、影響が広く、後戻りコストが大きい変更だけ user と揃える
- durable な wiki documentation は本文を日本語で保つ

## `bootstrap`

新規 local Markdown wiki を作るとき、または既存の Markdown repo / vault を LLM Wiki パターンへ寄せるときに使います。

### Goal

raw source を不変に保ちつつ、knowledge root, wiki の page 種別, `AGENTS.md` の local contract が明確で、汎用運用は `llm-wiki` skill に集約された構成を作ります。加えて、superpowers など他 workflow が作る durable な spec / ADR / plan / roadmap の保存先も knowledge root に寄せます。

### Check First

- 既存の local Markdown wiki または Markdown repo はあるか
- dedicated wiki repo か、mixed repo 内の subdirectory wiki か
- wiki topology は `single-root` か `multi-root` か
- knowledge root はどこに置くべきか
- 複数 knowledge root を持つ system なら、root registry adapter はどこに置き、どの router `AGENTS.md` から参照するか
- knowledge root の `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` は既にあるか
- `single-root` の場合、canonical owner と write boundary は `AGENTS.md` で明示できるか
- 既存の naming convention を維持すべきか
- 小規模な personal wiki か、継続的な research / team wiki か
- superpowers や他 workflow が durable doc をどこへ書くべきか

### Default Procedure

1. dedicated wiki repo か mixed repo かを決める。
2. `single-root` / `multi-root` topology を判定し、target knowledge root を確定する。
3. mixed repo なら `assets/templates/root-AGENTS.md` を元に repo root に thin router `AGENTS.md` を置き、knowledge root の `AGENTS.md` への導線と、他 workflow の durable doc を knowledge root へ保存する routing だけを書く。
4. `single-root` なら root registry は作らず、repo root または knowledge root の `AGENTS.md` を entrypoint にし、canonical owner, write boundary, non-owner proposal target を local contract に書く。
5. `multi-root` なら、system-specific root registry adapter を用意し、各 router `AGENTS.md` から adapter と canonical root へ辿れるようにする。Markdown registry を採用する場合だけ `assets/templates/root-registry.md` を元にしてよい。
6. 無ければ knowledge root に `assets/templates/AGENTS.md`, `index.md`, `log.md` をコピーする。knowledge root の `AGENTS.md` には skill への導線、local authority、local override、superpowers などの durable doc routing を書く。
7. `references/schema-and-conventions.md` の推奨サブディレクトリを knowledge root 配下に作る。
8. roadmap, ADR, spec, design doc, implementation plan の default 保存先を `wiki/syntheses/` にするか、project 固有の subdirectory を使うか決めて `AGENTS.md` に明記する。
9. YAML frontmatter を使うか決める。
10. 初期構成を knowledge root の `index.md` に記録する。`multi-root` の場合は registry の所在地と root id も記録する。
11. knowledge root の `log.md` に `bootstrap` エントリを追加する。`multi-root` の場合は registry の作成・更新も記録する。

### Pause And Align When

- directory layout や naming に複数の妥当案があり、後で rename / relink が多発しそう
- `single-root` / `multi-root` のどちらにするかで owner / access / durable doc routing が変わる
- repo root を knowledge root のまま使うべきか、subdirectory に切り出すべきかで運用コストが変わる
- 既存 wiki と新規ルールのどちらを canonical にするかで運用コストが変わる
- 1 回の bootstrap で広範囲の page 再配置を伴う
- 既存 workflow が repo-root `docs/` など別の durable doc 置き場に強く依存しており、routing 変更の影響が読めない

### Output Expectations

- knowledge root に local contract と entrypoint がある
- repo root から wiki に辿りやすい entrypoint がある
- `single-root` の場合は root registry なしで entrypoint と write authority が分かる
- 複数 root の場合は root registry adapter があり、root id / URI / owner / read-write policy / draft target が解決できる
- 後続 session が ingest / query / lint のやり方を再発明せずに済む

## `ingest`

`raw/` に新しい source が入り、wiki へ統合するときに使います。

### Goal

新しい source の知識を一度だけコンパイルし、その結果を persistent wiki 全体へ配ることで、後続 query が毎回 synthesis をやり直さなくて済むようにします。

### Check First

- 新しく入った source file はどれか
- 複数 root の場合、その source と claim の canonical root はどれか
- 書き込み先 root の `Read` は `allowed` か
- 書き込み先 root の `Write` は `owned`, `propose`, `closed` のどれか
- actor が owner でない場合、`Draft Target` は解決できるか
- 影響を受ける既存 page はどれか
- この source や topic の summary page は既にあるか
- raw source へ直接 citation すべき claim はどれか

### Default Procedure

1. `raw/` から source を読む。
2. `index.md` を見て関連 page を当てる。
3. 編集前に直接関係する entity / concept / synthesis page を開く。
4. 書き込み先 root の `Read`, `Write`, owner, `Draft Target` から更新経路を決める。
5. `Read: allowed`, `Write: owned`, actor が canonical owner のすべてを満たす場合だけ、source summary page と関係 page, `index.md`, `log.md` を直接更新する。
6. direct update できず `Read: allowed`, `Write: owned` または `propose`, `Draft Target` 解決済みの場合は、root 内の `Draft Target` に proposed note を作る。canonical page, `index.md`, `log.md` は直接更新しない。
7. `closed`, `restricted`, `no-access`, target 不明、または `Draft Target` 未解決の場合は書かずに session user へ確認する。

### Editing Rules

- raw file は不変に保つ。
- 自然に分解できるなら、大きな 1 枚より小さな複数 page を優先する。
- 古い claim を黙って置き換えず、矛盾を明示する。
- source summary から entity / concept へ事実を運ぶときも citation を保つ。

### Pause And Align When

- 1 つの source が複数 page の境界を作り直しそう
- 既存 page の canonical 名称や topic boundary を変える必要がある
- source の解釈が割れ、どの framing を採るかで downstream page が大きく変わる

それ以外の routine な summary 追加、citation 補強、軽い cross-link 追加は自律で進めます。

## `query`

maintained wiki に対して質問へ答えるときに使います。

### Goal

compiled wiki を再利用して根拠付きで素早く答え、その出力自体を wiki に残すべきか判断します。

### Check First

- `index.md` のどこが関連 page を指しているか
- 複数 root の場合、root registry adapter 上で読むべき root と書ける root はどれか
- actor が owner ではない場合、durable output を `Draft Target` に proposed note として残せるか
- 既に必要 topic をまとめている wiki page はあるか
- 裏取りや dispute resolution に raw source が要るか
- 回答は一時的なものか、durable page にすべきか

### Default Procedure

1. `index.md` から始める。
2. 必要最小限の wiki page を読む。
3. wiki が薄い、争点がある、古い場合だけ raw citation を追加で引く。
4. 必要に応じて wiki page と raw source を引用して答える。
5. 再利用価値があり、`Read: allowed`, `Write: owned`, actor が canonical owner のすべてを満たす場合だけ、`wiki/queries/` か `wiki/syntheses/` に page を作るか更新する。
6. direct update できず `Read: allowed`, `Write: owned` または `propose`, `Draft Target` 解決済みの場合は、durable output を root 内の `Draft Target` に proposed note として残す。
7. direct update した場合だけ、新しい durable page を `index.md` に登録し、`log.md` に `query` エントリを追加する。書けない root では canonical page, `index.md`, `log.md` を直接更新しない。

### Pause And Align When

- query の結果をどの page に落とすべきか曖昧で、既存 page を大きく再編しそう
- 回答が複数の durable artifact 候補にまたがり、emphasis の置き方で成果物が変わる
- query への回答が broad rewrite や rename / merge 判断を伴う

### File-Back Rule

次のいずれかに当てはまるなら、回答を wiki へ戻します。

- 比較や synthesis を後で再利用しそう
- taxonomy, table, framing など durable な整理を作れた
- query が露出させた gap を新しい page が埋めた
- user が durable note, memo, briefing, deck, report を明示的に求めた

## `draft-review`

owner actor が proposed note を review queue から閉じるときに使います。draft は verified claim ではなく、owner が `promote`, `merge`, `reject`, `defer` のいずれかで判断するまで canonical wiki page にはしません。

### Goal

owner decision を明示し、採用した内容だけを canonical page へ反映します。採用しない、またはまだ判断できない draft も履歴を残して閉じるか保留し、判断履歴なしに削除しません。

### Check First

- actor は対象 root の canonical owner か
- 対象 root の `Read` は `allowed` か
- owner が canonical page を更新する場合、root は `Write: owned` か
- draft note の status / review state / requested action は何か
- draft が指す canonical page / claim は存在するか
- draft の evidence と source summary は十分か
- `index.md` に active page として載せるべき canonical page はどれか
- `log.md` に残すべき decision history は何か

### Default Procedure

1. `Draft Target` から対象 draft を読む。
2. 関連する canonical page と `index.md`, `log.md` を読む。
3. draft の evidence, open questions, requested action を確認する。
4. decision を `promote`, `merge`, `reject`, `defer` のいずれかに決める。
5. `promote` の場合は、owner かつ `Write: owned` の boundary を満たすときだけ、draft の提案を verified claim として新規または既存 canonical page に反映する。
6. `merge` の場合は、owner かつ `Write: owned` の boundary を満たすときだけ、draft の unique な内容を既存 canonical page へ統合する。
7. `reject` の場合は、採用しない理由を draft 側または `log.md` に残し、active review queue から外す。
8. `defer` の場合は、未判断の理由、次に必要な source / owner action、再確認条件を draft 側または `log.md` に残す。
9. `promote` / `merge` 後は direct update boundary を満たす場合だけ canonical page と `index.md` を更新し、`log.md` に `draft-review` entry を追加する。boundary を満たさない場合は decision と必要な owner action を draft 側または `log.md` に残す。
10. `promote` / `merge` / `reject` / `defer` のいずれでも、draft status を final status に更新するか、draft の `Owner Decision` に final status を残す。
11. `reject` / `defer` でも `log.md` または draft の `Owner Decision` に日付、判断者、理由を残す。履歴なしに draft を削除しない。

### Decision Set

- `promote`: owner かつ `Write: owned` の場合だけ、draft を verified claim として canonical page へ反映する。
- `merge`: owner かつ `Write: owned` の場合だけ、draft の unique な内容を既存 canonical page へ統合する。
- `reject`: 採用しない理由を残し、active queue から外す。
- `defer`: 未判断の理由と次の条件を残し、保留する。

### Pause And Align When

- actor が owner か不明
- draft の evidence が弱く、採否で downstream page が大きく変わる
- `promote` / `merge` が rename, split, rehome を伴う
- `reject` が重要な competing interpretation を消す可能性がある

## `canonicalize`

重複や強い重なり、境界の崩れを見つけたときに、owner actor が page boundary を整理する mode です。owner かつ `Write: owned` の場合だけ canonical page を直接組み替えます。owner でない actor や `Write: propose` root では draft note へ routing します。

### Goal

page を増やし続けず、canonical page, discoverability, audit trail を保ったまま wiki を整理します。

### Check First

- actor は対象 root の canonical owner か
- 対象 root の `Read` は `allowed` か
- direct canonical update は owner かつ `Write: owned` の boundary を満たすか
- 対象 page は `index.md` にどう載っているか
- 対象 page の inbound / outbound link はどこか
- action は rename, merge, archive, split, rehome のどれか
- 複数 root をまたぐ場合、canonical owner と draft target はどこか

### Default Procedure

1. `index.md` から対象 page と重なり候補を確認する。
2. 編集前に対象 page、関連 page、`log.md` を読む。
3. canonical page と action を決める。
4. owner かつ `Write: owned` の場合だけ canonical page を直接更新する。
5. direct update できない場合は root 内の `Draft Target` に proposed note を作り、canonical page, `index.md`, `log.md` は直接更新しない。
6. direct update した場合は、対象 page、関連 link、`index.md`, `log.md` を更新する。
7. canonical page へ最低 1 本の inbound link が残ることを確認する。

### Action Set

- `rename`: canonical 名称へ寄せる。旧 page を消すだけで discoverability を失うなら、短い案内 stub を残して新 page へ誘導する。
- `merge`: destination を 1 つ決め、unique な内容だけを canonical page へ移す。統合元は削除せず、merged / superseded の案内を短く残すか archive する。
- `archive`: obsolete, superseded, duplicate のときだけ使う。archive 先または後継 page を明示し、現役 page と誤認される書き方を避ける。
- `split`: 1 page に複数の durable topic が混ざったとき、独立 page へ分け、元 page に境界と link を残す。
- `rehome`: page が wrong root / wrong page type / wrong directory にあるとき、canonical owner と保存先を直し、旧位置から新位置へ誘導する。

### Pause And Align When

- canonical owner が不明
- split / rehome が複数 root の authority boundary をまたぐ
- archive が historical context や citation trail を失わせる
- rename / merge により大量の link 更新が必要になる

## `lint`

単一 source の処理ではなく、wiki 全体の health check をするときに使います。

### Goal

wiki が断片的な summary の寄せ集めへ劣化する前に、構造的な弱点を見つけます。lint は検出、軽微修正、`draft-review` / `canonicalize` への routing を主責務とします。

### Check First

- `index.md` が重要 page を網羅しているか
- 複数 root の場合、root registry adapter が最新で、各 root の access / owner / canonical boundary が解決可能か
- owner として扱う root では、`Draft Target` に未整理 draft が残っていないか
- `log.md` に recent ingest はあるのに wiki 更新が追随していない箇所はないか
- inbound link のない page はどれか
- 新しい source で superseded されていそうな claim はどれか
- 繰り返し言及されるのに独立 page を持たない concept はどれか

### Default Procedure

1. `index.md` と `log.md` を走査する。
2. owner として扱う root では `Draft Target` を確認し、未整理 draft を `draft-review` 候補として記録する。
3. orphan page, stale page, contradiction candidate, recurring unnamed concept を洗う。
4. 編集前に対象 page を確認して問題を確定する。
5. link 修正、明白な `index.md` catalog 漏れ、stale claim の superseded 明記など軽微な修正だけ行う。
6. draft 採否判断は `draft-review`、rename / merge / archive / split / rehome は `canonicalize` へ routing する。
7. 具体的な gap がある箇所だけ targeted な source 追加や web check を提案する。
8. 所見、routing 結果、軽微修正を `log.md` の `lint` エントリへ記録する。

### Common Lint Findings

- inbound link を持たない page
- 同じ concept の重複 page
- entity / concept へ波及していない source summary
- citation trail のない assertion
- newer source を反映していない synthesis page
