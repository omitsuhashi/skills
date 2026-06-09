# Multi Root Topology

複数の knowledge root を持つ system で、どの知識をどこへ保存するかを決めるための reference です。

## Core Rule

各 knowledge root は、独立した llm-wiki root として扱う。

- 各 root は `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を持つ。
- `raw/` は root ごとに不変 source として扱う。
- `wiki/` は root ごとの maintained knowledge として扱う。
- `index.md` は root 内の lookup surface として扱う。
- `log.md` は root 内の append-only ledger として扱う。

複数 root を常用する system では、system-specific root registry adapter を用意し、router `AGENTS.md` からその adapter と canonical roots へ辿れるようにする。adapter は Markdown registry, config file, local documentation, runtime lookup のどれでもよいが、generic `llm-wiki` skill は file format や approval workflow を固定しない。

## System-Specific Adapter Hook

adapter は root 発見、path 解決、access 判断の first lookup surface として扱う。generic `llm-wiki` が必要とする field は次に限定する。

- `Root ID`
- `Root URI/Path`
- `Scope`
- `Canonical Owner`
- `Read`
- `Write`
- `Draft Target`

registry file format、approval workflow、root taxonomy、runtime names、owner の実装詳細は local adapter または local `AGENTS.md` に残す。新規 bootstrap で Markdown registry を使う場合だけ、`assets/templates/root-registry.md` を雛形にしてよい。

## Authority Terms

owner, actor, session user は人間 / AI の種別ではなく、authority と responsibility で区別する。

- `owner`: root の verified claim を承認、昇格、修正、却下できる責務主体。人間、team、role、AI profile、operating process のいずれでもよい。
- `actor`: 今回の作業で root を読み書きする実行主体。多くの場合は LLM agent。
- `session user`: 今回の session で actor に明示指示を出している依頼者。

## Root URI/Path Rules

- `file:/absolute/path` は local filesystem 上の絶対 path を指す。
- `repo:<repo-name>:<relative-path>` は adapter が属する workspace から識別できる repo root 相対 path を指す。
- `memory:<path>` は agent memory など、通常の repo 外にある managed knowledge root を指す。
- bare relative path や環境依存の shell expansion は adapter に書かない。
- cross-root link や citation では `root-id:path/inside/root.md` を使う。
- URI / path が解決できない root には書かない。読む必要がある場合は session user に確認する。

## Access Values

- `Read`: `allowed`, `restricted`, `no-access`。
- `Write`: `owned`, `propose`, `closed`。
- `Write` は通常作業で actor が取れる write mode を表す。owner が draft review や canonicalize を閉じる権限そのものではない。
- `owned`: owner actor だけが verified claim を直接更新できる。non-owner actor は `Read: allowed` かつ `Draft Target` がある場合だけ proposed note を書ける。
- `propose`: routine actor は verified claim を直接更新できない。`Read: allowed` かつ `Draft Target` がある actor だけ proposed note を書ける。owner `draft-review` / `canonicalize` でも canonical page へ直接反映しない。
- `closed`: verified claim も proposed note も書かない。
- `Read` が `restricted` または `no-access` の root には、verified claim も proposed note も書かない。読む必要がある場合は session user に確認する。

## Draft Target Rules

- `Draft Target` は target root 内の root-relative directory として解決する。
- 通常は `wiki/drafts/` を使う。
- absolute path、`~`、`..`、root 外へ解決される path は使わない。
- `Draft Target` が未設定、未解決、または root 外へ解決される場合は proposed note を書かず、session user に確認する。

## Routing Rules

- local adapter の `Scope` と `Canonical Owner` を first lookup surface として扱う。
- scope 固有 claim をより広い shared root や別 actor root に置かない。
- source note は、その source が支える claim の所属 root に置く。
- 複数 root にまたがる場合は、canonical root を 1 つ決め、他 root から link する。
- project + role など local な scope taxonomy は adapter 側で定義し、skill 側では固定しない。

## Canonical Owner

各 root は canonical owner を持つ。verified claim を通常作業で直接更新できるのは owner actor かつ `Write: owned` の場合だけ。owner 以外の actor は、adapter が許す場合に draft / proposed note だけを作る。

owner による `draft-review` / `canonicalize` の canonical update は、対象 root が `Read: allowed` で、`Write: owned` で、local contract または adapter が owner canonical update を許す場合に限る。`Read: restricted`, `Read: no-access`, `Write: propose`, `Write: closed`, または local override が owner direct update を禁止する場合は、decision と必要な owner action を draft 側または `log.md` に記録する。

## Draft Review Workflow

draft は未整理の inbox ではなく、owner が閉じる review queue として扱う。

- non-owner actor は verified claim を直接更新せず、adapter が示す `Draft Target` に proposed note を書く。
- draft を作成できるのは、target root の `Read` が `allowed` で、`Write` が `owned` または `propose` で、`Draft Target` が解決できる actor だけ。
- proposed note は最低限、対象 root、対象 canonical page / claim、提案内容、根拠 source、作成 actor、owner に求める action、作成日を持つ。
- owner は定期的に、または `ingest`, `query`, `lint` のタイミングで `Draft Target` を確認する。
- owner は各 draft を `promote`, `merge`, `reject`, `defer` のどれかに分類する。
- `promote` は canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許す場合に、draft を verified claim として canonical page へ反映する。
- `merge` は canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許す場合に、draft の unique な内容を既存 canonical page へ統合する。
- `reject` は採用しない理由を draft 側または `log.md` に残し、現役 queue から外す。
- `defer` は未判断の理由と次に必要な source / owner action を draft 側に残す。
- `promote` / `merge` したら、`Write: owned` かつ owner canonical update が許される場合だけ対象 root の canonical page, `index.md`, `log.md` を更新する。許されない場合は decision と必要な owner action を draft 側または `log.md` に残す。
- いずれの decision でも、draft の `Current Status` を final status に更新する。
- `reject` / `defer` も日付、判断者、理由を残す。判断履歴なしに draft を削除しない。

## Cross-Root Links

root 間 link は許可するが、copy-paste による重複 canonical page は避ける。

## Cross-Root Source Policy

- 同じ raw source が複数 root の claim を支える場合、raw source の canonical root を 1 つ決める。
- canonical root 以外には source summary の短い pointer か citation だけを置き、raw source を複製しない。
- cross-root citation は `root-id:path/inside/root.md` 形式で書く。
- private / restricted root の source は、権限のない root へ本文や sensitive detail を複写しない。必要なら claim の存在と確認先だけを書く。
- source の解釈が root 間で分かれる場合は、各 root の synthesis に差分を明示し、canonical raw への citation を保つ。

## Common Mistakes

- scope 固有の事実を広すぎる root に書くこと。
- owner 以外の actor が verified claim を直接更新すること。
- root ごとの `index.md` / `log.md` を更新しないこと。
- adapter に解決不能な相対 path や曖昧な owner / access を残すこと。
- draft を owner review queue として閉じず、第二の未整理 inbox にすること。
