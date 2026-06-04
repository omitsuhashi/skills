# Federated Knowledge Roots

## Purpose

複数の knowledge root を持つ system で、どの知識をどこへ保存するかを決める。

## Core Rule

各 knowledge root は、独立した llm-wiki root として扱う。

- 各 root は `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を持つ。
- `raw/` は root ごとに不変 source として扱う。
- `wiki/` は root ごとの maintained knowledge として扱う。
- `index.md` は root 内の lookup surface として扱う。
- `log.md` は root 内の append-only ledger として扱う。

複数 root を常用する system では、global root か system-level router の近くに `root-registry.md` を 1 つ置く。新規 bootstrap 時は `assets/templates/root-registry.md` を使い、repo/profile/router `AGENTS.md` から registry へ辿れるようにする。

## Root Registry

registry は root 発見、path 解決、access 判断の first lookup surface として扱う。各 root 行は安定した `Root ID`, `Root URI/Path`, `Scope`, `Canonical Owner`, `Read`, `Write`, `Draft Target` を持つ。

## Authority Terms

owner, actor, session user は人間 / AI の種別ではなく、authority と responsibility で区別する。

- `owner`: root の verified claim を承認、昇格、修正、却下できる責務主体。人間、team、role、AI profile、operating process のいずれでもよい。
- `actor`: 今回の作業で root を読み書きする実行主体。多くの場合は LLM agent。
- `session user`: 今回の session で actor に明示指示を出している依頼者。
- `approval`: registry 上の authority を持つ主体からの承認。人間 / AI の種別では決めない。
- `session-user override`: owner approval が取れない場合に、session user が明示的に責任を引き受けて verified claim の直接更新を許可する例外。

### Root URI Rules

- `file:/absolute/path` は local filesystem 上の絶対 path を指す。
- `repo:<repo-name>:<relative-path>` は registry が属する workspace から識別できる repo root 相対 path を指す。
- `memory:<path>` は agent memory など、通常の repo 外にある managed knowledge root を指す。
- bare relative path や環境依存の shell expansion は registry に書かない。
- cross-root link や citation では `root-id:path/inside/root.md` を使う。
- URI が解決できない root には書かない。読む必要がある場合は user に確認する。

### Access Values

- `Read`: `allowed`, `restricted`, `no-access`。
- `Write`: `write-owned`, `write-with-approval`, `draft-only`, `read-only`, `no-access`。
- `write-owned` は canonical owner として verified claim を更新してよい。
- `write-with-approval` は owner approval を原則必須にする。session user approval は owner approval が取れない場合の明示 override としてだけ扱う。
- session-user override で verified claim を更新した場合は、対象 root の `log.md` に `session-user override`、承認者、理由を残す。
- session-user override が claim の信頼性、出典、または provenance に影響する場合だけ、canonical page の `## 出典` または短い注記にも override 経緯を残す。
- `draft-only` は `Draft Target` に proposed note だけを書く。verified claim へ昇格するときは owner が該当 root の `index.md` と `log.md` を更新する。
- owner 不在、access 不明、または private boundary をまたぐ場合は `draft-only` と同じ扱いに倒す。
- `write-with-approval` または `draft-only` の root は `Draft Target` を必須にする。`Draft Target` が空なら draft を書かず、session user に確認する。

## Root Types

### Global Root

system 全体で共有する運用知識、agent 設計、共通失敗例、共通 policy を置く。

### Profile Root

特定 profile が繰り返し使う経験知、失敗例、調査 pattern、review pattern を置く。

### Role Root

CMO / CTO / COO など role 固有の判断軸、playbook、strategy pattern を置く。

### Project Root

特定 project の顧客、商品、業務、stakeholder、source、claim、decision を置く。

### Project-Role Root

特定 project x role の施策、最終判断、成果物、実験ログを置く。

## Routing Rules

- project + role に固有の施策、判断、実験ログは project-role root に置く。
- project の顧客、商品、業務、stakeholder、source、claim、decision は project root に置く。
- role に一般化された判断軸、playbook、strategy pattern は role root に置く。
- profile の作業改善知は profile root に置く。
- project 固有 claim を global root や profile root に置かない。
- role 固有 strategy を project domain root に混ぜない。
- source note は、その source が支える claim の所属 root に置く。
- 複数 root にまたがる場合は、canonical root を 1 つ決め、他 root から link する。

## Canonical Owner

各 root は canonical owner を持つ。owner 以外の actor は draft / proposed note を作ってよいが、verified claim への昇格は owner が行う。

## Draft Review Workflow

draft は未整理の inbox ではなく、owner が閉じる review queue として扱う。

- non-owner actor は verified claim を直接更新せず、registry の `Draft Target` に proposed note を書く。
- `write-with-approval` の root でも、owner approval がない場合は `Draft Target` に proposed note を書く。session-user override がある場合だけ verified claim を直接更新できる。
- owner は定期的に、または `ingest`, `query`, `lint` のタイミングで `Draft Target` を確認する。
- owner は各 draft を `promote`, `merge`, `reject`, `defer` のどれかに分類する。
- `promote` は draft を verified claim として canonical page へ反映する。
- `merge` は draft の unique な内容だけを既存 canonical page へ統合する。
- `reject` は採用しない理由を draft 側または `log.md` に残し、現役 queue から外す。
- `defer` は未判断の理由と次に必要な source / owner action を draft 側に残す。
- `promote` / `merge` したら対象 root の canonical page, `index.md`, `log.md` を更新する。
- `reject` / `defer` も日付、判断者、理由を残す。判断履歴なしに draft を削除しない。

## Override Recording

session-user override は運用判断なので、全件を対象 root の `log.md` に残す。canonical page 側は監査ログにしない。claim の信頼性、出典、provenance に影響する override だけ、該当 page の `## 出典` または短い注記に残す。

session-user override は次の理由カテゴリのどれかに当てはまる場合だけ許可する。単なる好み、便利さ、通常の owner review 待ち回避には使わない。

- `urgent`: owner approval を待つと期限、外部提出、重要な判断に実害が出る。
- `owner-unavailable`: owner が不在または到達不能で、draft に留めると作業が止まる。
- `low-risk-correction`: typo, broken link, obvious metadata mismatch など、claim の意味を変えない低リスク修正。factual correction は含めず、`source-backed-fix` として扱う。
- `source-backed-fix`: canonical source で明確に裏取りでき、現行 claim が誤っている修正。

`log.md` には `session-user override`、理由カテゴリ、承認者、具体的な理由、触った page を残す。

## Cross-Root Links

root 間 link は許可するが、copy-paste による重複 canonical page は避ける。

## Cross-Root Source Policy

- 同じ raw source が複数 root の claim を支える場合、raw source の canonical root を 1 つ決める。
- canonical root 以外には source summary の短い pointer か citation だけを置き、raw source を複製しない。
- cross-root citation は `root-id:path/inside/root.md` 形式で書く。
- private / restricted root の source は、権限のない root へ本文や sensitive detail を複写しない。必要なら claim の存在と確認先だけを書く。
- source の解釈が root 間で分かれる場合は、各 root の synthesis に差分を明示し、canonical raw への citation を保つ。

## Common Mistakes

- project 固有の事実を common wiki に書くこと。
- role 固有の判断を project domain wiki に書くこと。
- profile root に一回限りの project 調査結果を溜めること。
- root ごとの `index.md` / `log.md` を更新しないこと。
- registry に解決不能な相対 path や曖昧な owner / access を残すこと。
- draft を owner review queue として閉じず、第二の未整理 inbox にすること。
