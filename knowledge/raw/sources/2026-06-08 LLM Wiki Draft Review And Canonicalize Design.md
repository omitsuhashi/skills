以下は、**Portfolio OS ではなく、汎用 `llm-wiki` skill 本体に入れるべき強化だけ**に絞った詳細設計です。

前提として、`llm-wiki` はすでに「local Markdown wiki を persistent knowledge base として運用する skill」であり、`raw/` は不変、`wiki/` は LLM-managed、`index.md` と `log.md` は first-class 運用ファイルとして扱う設計になっています。さらに、mixed repo では knowledge root を切り出し、汎用 wiki 運用ルールの canonical source は skill 側に置く方針も明記されています。

したがって今回の設計は、**外部 script で workflow を組むのではなく、LLM が skill を読んで自己運用できる procedure を増やす**方向です。この考え方は、手順全体を context に入れてモデルに自己実行させる方が、外部 orchestrator で細かく状態遷移させるより安定する、という添付論文の方向性とも合っています。

---

# 0. 結論

`llm-wiki` skill に追加・強化すべき汎用変更は、主にこの5つです。

```text
1. draft-review mode を first-class mode に昇格する
2. canonical-merge / canonicalize mode を first-class mode にする
3. index.md / log.md 更新を page lifecycle invariant として明文化する
4. multi-root / federated root の adapter hook を汎用化する
5. lint を「検査」だけでなく「保守作業の入口」として再整理する
```

ただし、入れてはいけないものも明確です。

```text
入れない:
  - Portfolio OS
  - Hermes
  - work_unit
  - commander
  - governance-core
  - registry-core
  - TOML schema
  - companies repo 固有の path
  - profile-set
  - canonical_owner の具体的実装
```

`llm-wiki` 側が扱うのは、あくまで **Markdown wiki の汎用 lifecycle** です。
特定 OS / agent runtime / registry schema への接続は、外部 adapter skill の責務に残します。

---

# 1. 現状の `llm-wiki` にすでにあるもの

まず、現在の `llm-wiki` は土台としてかなり良いです。

## 1.1 基本 mode はある

現在の `SKILL.md` では、作業時に `bootstrap` / `ingest` / `query` / `lint` の mode を決めるとされています。

```text
現状 mode:
  bootstrap
  ingest
  query
  lint
```

これは良いですが、足りないのは **owner が draft を閉じる mode** と、**canonical page の merge / rename / archive を行う mode** が独立していないことです。

---

## 1.2 draft review の概念はすでにある

`wiki/drafts/` は、owner 以外の actor が作る proposed note の置き場であり、owner が `promote` / `merge` するまでは verified claim ではなく、`index.md` の現役 page 一覧にも載せない、と定義されています。

さらに federated roots 側には、draft は未整理 inbox ではなく owner review queue として扱い、owner が `promote` / `merge` / `reject` / `defer` で閉じる、という workflow もすでに書かれています。

つまり、**概念はあるが、操作 mode として弱い**状態です。

---

## 1.3 direct write / draft routing の基本ルールはある

`operations.md` の `ingest` では、書き込み先 root の `Read`、`Write`、owner、`Draft Target` を見て更新経路を決めること、owner かつ `Write: owned` の場合だけ direct update し、それ以外は draft に proposed note を作ることが定義されています。

`query` でも同じく、owner でなければ durable output を `Draft Target` に proposed note として残す設計です。

これは非常に良いです。
ただし、今後はこの判断を「Portfolio OS 固有の registry 解決」ではなく、**generic な root authority resolution procedure** として明文化する必要があります。

---

## 1.4 page lifecycle の基本はある

`operations.md` には、重複や強い重なりを見つけたら canonical page を選び、rename / merge / archive するルールがあります。merge では destination を1つ決め、unique な内容だけを canonical page に移し、統合元は削除せず merged / superseded の案内を残す、と定義されています。

また、lifecycle action 後には `index.md`、`log.md`、outbound link、inbound link を確認することも明記されています。

これも良いです。
ただし、これもまだ「lint の下にある補助ルール」に近く、独立した operational mode としては弱いです。

---

# 2. 足りないもの

現状の不足を、汎用 `llm-wiki` skill の観点で整理するとこうです。

| 不足                   | 現状                           | 追加すべきもの                                    |
| -------------------- | ---------------------------- | ------------------------------------------ |
| draft を閉じる操作         | federated roots に説明はある       | `draft-review` mode                        |
| canonical page への統合  | page lifecycle の補足として存在      | `canonicalize` / `canonical-merge` mode    |
| index/log 更新         | rules はある                    | invariant / checklist 化                    |
| multi-root authority | root registry はある            | adapter hook / schema非依存の解決手順              |
| lint                 | health check と lifecycle が混在 | lint は検出、review/merge は別 mode              |
| draft template       | 最低限の項目はある                    | status / closure / target / evidence を少し強化 |
| page update判断        | ingest/query内に散在             | reusable update decision table             |
| cross-root movement  | link / citation rule はある     | rehome / copy禁止 / canonical root選択の手順      |

---

# 3. 設計原則

## 3.1 Generic first

`llm-wiki` skill は、どの system でも使える必要があります。

そのため、skill 本体に入れてよい語彙はこの範囲です。

```text
入れてよい:
  knowledge root
  root registry
  owner
  actor
  session user
  draft target
  canonical page
  verified claim
  proposed note
  source
  entity
  concept
  synthesis
  query note
  lint
  lifecycle
  root adapter
```

入れてはいけない語彙はこれです。

```text
入れない:
  Portfolio OS
  work unit
  commander
  council
  registry-core
  governance-core
  capture-core
  companies
  Hermes profile
  Kanban
```

`profile`、`project`、`role` という語は現状の federated root example に含まれていますが、これは一般概念としてなら許容できます。ただし、今後は「固定 root type」ではなく「例」として扱う方が安全です。

---

## 3.2 Procedure belongs in skill, not script

`index.md` / `log.md` をどう更新するか、draft をどう閉じるか、canonical page にどう merge するかは、script ではなく `llm-wiki` skill の procedure として持たせます。

script があるとしても、許されるのは以下だけです。

```text
許される script:
  - template copy
  - directory validation
  - broken link check
  - grep/report
  - format check

許されない script:
  - draft の採否判断
  - canonical merge の意味判断
  - index.md に何を載せるかの判断
  - log.md に何を書くかの判断
  - root 間でどちらを canonical にするかの判断
```

---

## 3.3 Owner review is a wiki-native lifecycle

draft は inbox ではありません。
draft は owner review queue です。

この思想はすでに current skill にあります。
今回の更新では、これを skill の中心 mode にします。

---

## 3.4 `index.md` と `log.md` は副作用ではなく invariant

`index.md` は最初の lookup surface、`log.md` は append-only ledger として定義済みです。

したがって、今後はこう表現します。

```text
Any durable wiki change must leave the root in a discoverable and auditable state.

Discoverable:
  index.md reflects canonical pages

Auditable:
  log.md records durable changes and lifecycle decisions
```

つまり、`index.md` / `log.md` 更新は「おまけ」ではなく、LLM Wiki の整合性条件です。

---

# 4. 提案するファイル変更

対象は `omitsuhashi/skills/skills/llm-wiki/` の中だけです。

```text
skills/llm-wiki/
├── SKILL.md
├── references/
│   ├── operations.md
│   ├── schema-and-conventions.md
│   ├── federated-knowledge-roots.md
│   └── optional-tooling.md
└── assets/templates/
    ├── draft-note.md
    ├── index.md
    ├── log.md
    ├── root-registry.md
    └── AGENTS.md
```

新規ファイルは最小限にします。
基本は既存ファイルの強化で十分です。

---

# 5. `SKILL.md` の詳細設計

## 5.1 Mode list を拡張する

現状は `bootstrap`, `ingest`, `query`, `lint` です。

更新後はこうします。

```text
Mode:
  bootstrap
  ingest
  query
  draft-review
  canonicalize
  lint
```

### 追加 mode 1: `draft-review`

目的:

```text
owner actor が wiki/drafts/ の proposed note を確認し、
promote / merge / reject / defer のいずれかで閉じる。
```

### 追加 mode 2: `canonicalize`

目的:

```text
重複、強い重なり、stale page、superseded page を整理し、
rename / merge / archive / split / rehome の判断を行う。
```

`canonicalize` という名前を推奨します。
理由は、merge だけでなく rename / archive / split / rehome も含められるからです。

---

## 5.2 Quick Workflow の修正案

現状の Quick Workflow は良いので、mode list だけ拡張します。

更新案:

```md
## Quick Workflow

1. Identify the mode: `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, or `lint`.
2. Determine the wiki topology and target knowledge root before editing.
3. If the system uses multiple roots, resolve the target root, owner, access mode, write mode, and draft target before changing durable wiki content.
4. Read only the matching reference file sections instead of loading everything.
5. Inspect `index.md` before touching wiki pages unless the task is pure bootstrap.
6. For direct durable changes, update the relevant canonical page, `index.md`, and `log.md` in the same work session.
7. For non-owner or non-direct changes, write a proposed note to the root’s draft target and do not update canonical pages, `index.md`, or `log.md`.
8. If an answer creates durable value, file it back into the wiki or into a draft note, depending on write authority.
9. Pause only for ambiguous, high-impact, or multi-page changes. Routine low-risk updates proceed autonomously.
```

ポイントは、**direct durable change と draft proposal を明確に分ける**ことです。

---

## 5.3 Mode Entry Checks の追加

`SKILL.md` に次を追加します。

```md
### `draft-review`

Owner actor が `wiki/drafts/` または root registry の `Draft Target` にある proposed note を閉じるときに使います。draft は未整理 inbox ではなく owner review queue です。各 draft について `promote`, `merge`, `reject`, `defer` のいずれかを選びます。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`
- `references/federated-knowledge-roots.md` only if multiple roots are involved
```

```md
### `canonicalize`

重複 page、強く重なる page、古い page、誤った root に置かれた page、または canonical boundary が崩れている page を整理するときに使います。rename / merge / archive / split / rehome のいずれかを選び、discoverability と auditability を保ちます。

Read:

- `references/operations.md`
- `references/schema-and-conventions.md`
- `references/federated-knowledge-roots.md` only if moving or linking across roots
```

---

# 6. `operations.md` の詳細設計

`operations.md` が今回の中心です。

---

## 6.1 `draft-review` section を新設する

追加場所は `query` と `lint` の間がよいです。

```md
## `draft-review`

Owner actor が proposed note を確認し、canonical wiki に反映するか、却下・保留するかを決めるときに使います。

### Goal

`wiki/drafts/` を第二の未整理 inbox にせず、owner review queue として閉じます。採用する内容は canonical page に反映し、採用しない内容も判断履歴を残します。

### Check First

- actor は target root の owner として振る舞えるか
- 対象 root の `Read` は `allowed` か
- 対象 root の `Write` は `owned` または `propose` か
- `Draft Target` は解決できるか
- review 対象 draft はどれか
- draft は target root / target canonical page / requested owner action / evidence を持つか
- 関連 canonical page はどれか
- 既存 page と矛盾・重複・古さがあるか
- source evidence は十分か
```

---

## 6.2 `draft-review` の Default Procedure

```md
### Default Procedure

1. Root registry または local `AGENTS.md` から target root と owner authority を確認する。
2. `index.md` を読み、target canonical page と関連 page を特定する。
3. 対象 draft を読む。
4. draft が参照する source / source summary を確認する。
5. 関連 canonical page を読む。
6. draft ごとに decision を選ぶ。

Decision:

- `promote`: 新しい canonical page として採用する
- `merge`: unique な内容だけ既存 canonical page へ統合する
- `reject`: 採用しない
- `defer`: 追加 source / owner action / clarification が必要なため保留する

7. `promote` の場合:
   - appropriate page type を選ぶ
   - canonical page を作成する
   - `index.md` に登録する
   - `log.md` に `draft-review` entry を追加する
   - draft に decision metadata を残す

8. `merge` の場合:
   - destination canonical page を1つ決める
   - draft の unique な claim / source / framing だけを統合する
   - 重複内容を増やさない
   - `index.md` を必要に応じて更新する
   - `log.md` に `draft-review` entry を追加する
   - draft に decision metadata を残す

9. `reject` の場合:
   - 採用しない理由を draft の `Owner Decision` に残す
   - 必要なら `log.md` に short entry を残す
   - draft を現役 queue から外すため、local convention に従って `wiki/drafts/rejected/` などへ移すか、status を `rejected` にする

10. `defer` の場合:
   - 不足している source / clarification / owner action を draft に残す
   - review_after または next action を書く
   - draft を active queue に残すか、local convention に従って `deferred/` に移す
```

ここで重要なのは、`reject` / `defer` でも「何も消さない」ことです。
現状の federated roots でも、判断履歴なしに draft を削除しないとされています。

---

## 6.3 `draft-review` の Pause Rules

```md
### Pause And Align When

- draft の採否が root の基本方針を変える
- 既存 canonical page の boundary を大きく変える
- 複数 root のどれを canonical にするかが曖昧
- source が不足していて、採用すると誤情報になり得る
- private / restricted / sensitive な source を別 root に要約・複写しそう
- promote / merge により多くの backlink 修正が必要
```

---

## 6.4 `canonicalize` section を新設する

追加場所は `lint` の後、現行の `Page Lifecycle And Canonicalization` を置き換える形がよいです。

現状の page lifecycle section は良いですが、`canonicalize` mode として独立させます。現在も canonical page の選定、rename、merge、archive、after action は定義済みです。

更新案:

```md
## `canonicalize`

重複、強い重なり、古い page、誤った root に置かれた page、または canonical boundary が崩れた page を整理するときに使います。

### Goal

page を増やし続けず、1 durable topic = 1 canonical page の原則を保ちます。discoverability と auditability を落とさずに、rename / merge / archive / split / rehome を行います。
```

---

## 6.5 `canonicalize` の Action Set

```md
### Actions

#### Rename

canonical 名称へ寄せます。旧 page を消すだけで discoverability を失うなら、短い案内 stub を残して新 page へ誘導します。

#### Merge

destination canonical page を1つ決め、unique な内容だけを canonical page へ移します。統合元は削除せず、merged / superseded の案内を短く残すか archive します。

#### Archive

obsolete, superseded, duplicate のときだけ使います。archive 先または後継 page を明示し、現役 page と誤認される書き方を避けます。

#### Split

1 page が複数 durable topic を抱えすぎている場合に使います。split 後は親 page か synthesis page から分割先へ link します。

#### Rehome

page が誤った root にある場合に使います。cross-root copy を増やさず、canonical root を1つ選び、元 root には pointer か short summary だけを残します。
```

`split` と `rehome` は現状弱いので、追加する価値があります。
特に `rehome` は multi-root wiki で重要ですが、特定 OS には依存しません。

---

## 6.6 `canonicalize` の Default Procedure

```md
### Default Procedure

1. `index.md` を読み、対象 page 群の現在の見え方を確認する。
2. 対象 page と inbound / outbound links を確認する。
3. source summary や raw citation が必要な場合だけ確認する。
4. どの action かを決める:
   - rename
   - merge
   - archive
   - split
   - rehome
5. canonical page を1つ決める。
6. unique な内容だけを移し、重複 claim を増やさない。
7. stale / superseded / rejected な claim は黙って消さず、必要なら status を明示する。
8. 旧 page には pointer / merged note / archive note を残す。
9. `index.md` では canonical page だけを現役一覧に残す。
10. `log.md` に `canonicalize` entry を追加する。
11. 触った page の outbound link を見直す。
12. canonical page に最低1本の inbound link が残ることを確認する。
```

これは現状の `After Any Lifecycle Action` を mode procedure として具体化するものです。

---

## 6.7 `lint` の責務を整理する

現在 `lint` の中に、draft 分類や lifecycle action が入っています。
これは強すぎるので、`lint` は以下に寄せます。

```text
lint:
  問題を見つける
  軽微な修正はする
  大きな draft review / canonicalize は mode を切り替える
```

更新案:

```md
### Default Procedure

1. `index.md` と `log.md` を走査する。
2. orphan page, stale page, contradiction candidate, duplicate candidate, recurring unnamed concept を洗う。
3. owner として扱う root では `Draft Target` に未整理 draft が残っているか確認する。
4. 軽微な link 修正、明らかな index omission、明らかな log omission は修正する。
5. draft の採否判断が必要なら `draft-review` mode に切り替える。
6. rename / merge / archive / split / rehome が必要なら `canonicalize` mode に切り替える。
7. 所見と軽微な修正を `log.md` の `lint` entry に記録する。
```

これで `lint` が過剰な workflow executor にならず、**検出 mode** として扱いやすくなります。

---

# 7. `schema-and-conventions.md` の詳細設計

## 7.1 `wiki/drafts/` section を強化する

現状の draft section は良いです。draft は owner review queue であり、owner が `promote` / `merge` するまで verified claim ではない、と定義されています。

追加すべきは、draft の status convention です。

```md
### Draft Status

Draft は次の status を持てます。

- `proposed`: owner review 待ち
- `promoted`: 新しい canonical page として採用済み
- `merged`: 既存 canonical page に統合済み
- `rejected`: 採用しないと判断済み
- `deferred`: 追加 source / clarification / owner action 待ち

status は frontmatter で持っても、`Owner Decision` section で持っても構いません。local convention がない場合は `Owner Decision` section を使います。
```

frontmatter を必須にしないのが重要です。
現状でも frontmatter は任意であり、実際に保守しない metadata は増やさない方針です。

---

## 7.2 `index.md` Rules を invariant 化する

現状 `index.md` は first lookup surface で、durable wiki page を1回ずつ載せ、draft は現役 page 一覧に載せない、とされています。

追加案:

```md
### Index Invariant

`index.md` は canonical discoverability を保証します。

After any direct durable change:

- 新しい canonical page は載せる
- renamed page は新名称だけを現役一覧に残す
- merged / archived page は現役一覧から外す
- draft / rejected / deferred note は現役 page 一覧に載せない
- page type または local taxonomy に沿って配置する
- 各 entry は1行 summary を持つ

If no `index.md` update is needed, the actor should be able to explain why.
```

---

## 7.3 `log.md` Rules を invariant 化する

現状 `log.md` は append-only で、bootstrap、ingest、query filing、lint pass、rename / merge / archive などを記録するとされています。

追加案:

```md
### Log Invariant

`log.md` は durable change の audit trail です。

Add one entry for:

- bootstrap
- ingest that updates wiki
- query filing
- draft-review decision
- canonicalize action
- lint pass
- direct correction of index/link/citation
- significant deferred decision

Each entry should include:

- date
- mode
- short title
- changed page(s)
- decision summary
- source or draft reference when relevant
```

推奨 header も増やします。

```md
## [2026-04-12] draft-review | Proposed Update To Checkout Claims
## [2026-04-12] canonicalize | Merge Duplicate Authentication Pages
```

現在の `log.md` template には lifecycle entry の例があります。
そこに `draft-review` 例を足すだけでよいです。

---

## 7.4 Page Boundary に `split` と `rehome` を追加する

現状は rename / merge / archive が中心です。

追加案:

```md
### Split

1 page が複数 durable topic を抱え、後続 query や maintenance を難しくしている場合は split します。split 後は、元 page を synthesis / overview として残すか、分割先への pointer にします。

### Rehome

page が誤った knowledge root にある場合は、canonical root を1つ選んで移します。元 root には pointer を残し、同じ canonical claim を複数 root に copy しません。
```

---

# 8. `federated-knowledge-roots.md` の詳細設計

現状の federated root file はかなり良いです。

各 root は独立した `llm-wiki` root として扱い、`raw/`、`wiki/`、`index.md`、`log.md`、`AGENTS.md` を持つとされています。

また root registry は root discovery、path resolution、access 判断の first lookup surface で、各 root 行は `Root ID`、`Root URI/Path`、`Scope`、`Canonical Owner`、`Read`、`Write`、`Draft Target` を持つとされています。

ここで追加したいのは、**system-specific adapter hook** です。

---

## 8.1 Adapter Hook section を追加する

```md
## System-Specific Root Registry Adapters

Some systems may already have a root registry in another format, such as TOML, YAML, JSON, database records, or an application-specific manifest.

The generic `llm-wiki` skill does not require a specific registry file format. When a system-specific adapter is available, use it only to resolve the following generic fields:

- Root ID
- Root URI/Path
- Scope
- Canonical Owner
- Read
- Write
- Draft Target

After these fields are resolved, apply the generic `llm-wiki` write and draft-review rules.

Do not copy system-specific registry schema, approval workflow, project taxonomy, or runtime names into this generic skill. Keep those rules in the local adapter or local `AGENTS.md`.
```

これが非常に重要です。

これにより、Portfolio OS でも、他の wiki runtime でも、`llm-wiki` skill は同じまま使えます。

---

## 8.2 Root Types を「例」に落とす

現在は Global / Profile / Role / Project / Project-Role が定義されています。

これは便利ですが、固定しすぎると汎用性を損ねます。
変更案:

```md
## Common Root Type Examples

The following root types are examples, not required categories.

- Global Root
- Collection Root
- Actor/Profile Root
- Role Root
- Project Root
- Project-Role Root
- Source Collection Root

A local adapter or local `AGENTS.md` may define other root types. Generic `llm-wiki` behavior depends on owner, access, write mode, draft target, and canonical boundary, not on the root type name itself.
```

これで、Portfolio OS 以外でも使いやすくなります。

---

# 9. `assets/templates/draft-note.md` の詳細設計

現状の draft template は最低限の項目を持っています。Target、Proposal、Evidence、Context、Owner Decision があり、Root ID、Canonical Page / Claim、Requested Owner Action、Created By、Reason Direct Update Was Not Used、Decision などが入っています。

これを少しだけ強化します。
ただし、TOML / YAML を必須にしません。Markdown only で保ちます。

---

## 9.1 更新後 template 案

```md
# Draft Note

## Status

- Status: proposed
- Review State: active

## Target

- Root ID:
- Canonical Page / Claim:
- Requested Owner Action: promote | merge | reject | defer
- Related Pages:

## Proposal

提案内容を書く。既存 page に統合する場合は、どの claim / section に入れる想定かを書く。

## Evidence

- Source:
- Source Summary:
- Citation / Link:
- Confidence:
- Open Questions:

## Context

- Created At:
- Created By:
- Reason Direct Update Was Not Used:
- Triggering Task / Query:
- Scope Notes:

## Owner Decision

- Decision: promote | merge | reject | defer
- Decided At:
- Decided By:
- Reason:
- Destination Page:
- Log Entry:
- Follow-up:
```

追加したいのは以下です。

```text
Status
Review State
Related Pages
Source Summary
Confidence
Open Questions
Destination Page
Log Entry
Follow-up
```

ただし、これ以上は増やしません。
draft-note が重すぎると、日常運用で使われなくなります。

---

# 10. `assets/templates/index.md` の詳細設計

現状の `index.md` template は、wiki の最初の navigation surface として、durable page をすべて1回だけ載せ、canonical page だけを現役一覧に残す設計です。

このまま維持し、1行だけ追加する程度で十分です。

追加案:

```md
> Draft / rejected / deferred notes are not listed here as active pages. Owner-reviewed promoted or merged content is listed through its canonical page.
```

日本語なら:

```md
> draft / rejected / deferred note は現役 page としてここに載せません。owner review 後に promote / merge された内容だけを canonical page 経由で載せます。
```

---

# 11. `assets/templates/log.md` の詳細設計

現状の `log.md` template は append-only で使い、bootstrap / ingest / query / lifecycle の例があります。

追加すべき例は `draft-review` です。

```md
## [2026-04-12] draft-review | Proposed Update To Checkout Claims

- Decision: merge
- Draft: `wiki/drafts/2026-04-12 Proposed Update To Checkout Claims.md`
- Destination: `wiki/syntheses/Checkout Claims.md`
- Reason: evidence was sufficient and unique claims fit the existing canonical page
- `index.md` unchanged because no new canonical page was created
```

この例は重要です。
「merge の場合は index.md 更新不要なこともある」という判断例を示せます。

---

# 12. `assets/templates/AGENTS.md` の詳細設計

現状の AGENTS template は、汎用手順は `llm-wiki` skill を canonical source とし、この file は local override だけを書く、という非常に良い設計です。

ここに追加するなら、`draft-review` と `canonicalize` を lifecycle に含めるだけで十分です。

変更案:

```md
- wiki の `bootstrap`, `ingest`, `query`, `draft-review`, `canonicalize`, `lint`, page lifecycle の汎用手順は `llm-wiki` スキルを canonical source として扱う
```

`log.md` の説明も少し更新します。

```md
- `log.md` は bootstrap, ingest, query, draft-review, canonicalize, lint, lifecycle action の append-only timeline として扱う
```

---

# 13. Modeごとの最終仕様

## 13.1 `bootstrap`

責務は現状維持です。

```text
- dedicated wiki repo か mixed repo か決める
- single-root / multi-root を決める
- knowledge root を作る
- raw/wiki/index/log/AGENTS を揃える
- root registry が必要なら作る
- durable docs の routing を決める
```

既存の bootstrap procedure でも、knowledge root に `AGENTS.md`, `index.md`, `log.md` をコピーし、推奨サブディレクトリを作る手順になっています。

追加は少しだけです。

```text
- draft-review と canonicalize が skill の mode であることを local AGENTS.md に反映
- multi-root の場合、system-specific adapter があればそれを root registry resolver として扱う
```

---

## 13.2 `ingest`

現状維持を基本にします。

変更点:

```text
- direct write できる場合:
    source summary / related pages / index.md / log.md を更新

- direct write できない場合:
    draft note だけを作る
    canonical page / index.md / log.md は更新しない

- draft が増えた場合:
    owner に draft-review mode が必要であることを残す
```

これは現状の `ingest` procedure と一致します。

---

## 13.3 `query`

現状維持を基本にします。

変更点:

```text
- durable output の保存価値を判断する
- direct write 可能なら wiki/queries または wiki/syntheses に保存
- direct write 不可なら draft note
- 保存しない場合でも、なぜ一時回答でよいかを判断する
```

現状でも、再利用価値がある query output は wiki に戻す rule があります。

---

## 13.4 `draft-review`

新規 first-class mode です。

```text
Input:
  - target root
  - draft note(s)
  - owner actor context

Output:
  - promoted canonical page
  - merged canonical page update
  - rejected draft with reason
  - deferred draft with next action
  - index.md update if needed
  - log.md entry
```

Decision table:

| Decision | 使う場面                         | canonical page | index.md         | log.md         | draft           |
| -------- | ---------------------------- | -------------- | ---------------- | -------------- | --------------- |
| promote  | 新しい durable topic として独立価値がある | create         | add              | append         | status promoted |
| merge    | 既存 canonical page に入れるのが自然   | update         | update if needed | append         | status merged   |
| reject   | 根拠不足・scope外・重複・誤り            | no change      | no change        | optional/short | status rejected |
| defer    | 判断に不足がある                     | no change      | no change        | optional/short | status deferred |

---

## 13.5 `canonicalize`

新規 first-class mode です。

```text
Input:
  - duplicate / stale / overlapping / misplaced pages
  - lint finding
  - owner request
  - query/ingest中に見つかった boundary problem

Output:
  - renamed page
  - merged page
  - archived page
  - split page set
  - rehomed page
  - updated links
  - updated index.md
  - updated log.md
```

Action table:

| Action  | 使う場面                              | 注意                            |
| ------- | --------------------------------- | ----------------------------- |
| rename  | 名前だけ canonical に寄せたい              | 旧名から discoverability を残す      |
| merge   | 2 page が同じ durable topic          | unique な内容だけ移す                |
| archive | obsolete / superseded / duplicate | 後継 page を明示                   |
| split   | 1 page が複数 topic を抱える             | overview / synthesis link を残す |
| rehome  | root が間違っている                      | copy ではなく canonical root を選ぶ  |

---

## 13.6 `lint`

責務を軽くします。

```text
lint does:
  - detect
  - report
  - perform low-risk repair
  - route to draft-review / canonicalize

lint does not:
  - heavy owner review
  - broad merge
  - multi-root rehome
  - disputed canonical decision
```

---

# 14. Root authority の汎用仕様

`llm-wiki` skill は特定 registry format を持ちません。

必要なのは、どの system でも最終的に以下を解決できることです。

```text
Root ID
Root URI/Path
Scope
Canonical Owner
Read
Write
Draft Target
```

これは現状の root registry 仕様と一致しています。
`Read` / `Write` の値も現状のままでよいです。`Read` は `allowed`, `restricted`, `no-access`、`Write` は `owned`, `propose`, `closed` です。

追加する考え方はこれです。

```text
Generic llm-wiki:
  resolved fields を使って判断する

System adapter:
  独自 registry / manifest / database / policy から fields を解決する
```

この分離により、Portfolio OS でも、個人 wiki でも、研究 wiki でも、チーム wiki でも使えます。

---

# 15. 期待する最終挙動

## 15.1 non-owner が更新提案する場合

```text
1. actor が root を解決する
2. actor != owner
3. Write が owned または propose
4. Draft Target がある
5. draft-note.md を使って proposed note を作る
6. canonical page / index.md / log.md は触らない
```

---

## 15.2 owner が draft を閉じる場合

```text
1. owner actor が draft-review mode を選ぶ
2. draft を読む
3. index.md から canonical page を探す
4. source evidence を確認する
5. promote / merge / reject / defer を決める
6. promote / merge なら canonical page を更新する
7. 必要に応じて index.md を更新する
8. log.md に decision を残す
9. draft に Owner Decision を残す
```

---

## 15.3 重複 page を統合する場合

```text
1. canonicalize mode を選ぶ
2. 重複 page を読む
3. canonical page を選ぶ
4. unique 内容だけ移す
5. 統合元に merged / superseded note を残す
6. index.md は canonical page だけにする
7. log.md に canonicalize entry を残す
8. link を見直す
```

---

# 16. 互換性

この変更は backward compatible にできます。

既存の mode:

```text
bootstrap
ingest
query
lint
```

は残します。

新 mode:

```text
draft-review
canonicalize
```

を追加するだけです。

既存の `wiki/drafts/`、`index.md`、`log.md`、root registry、draft template も残します。
既存 root は壊しません。

---

# 17. 追加すべきテスト / チェック

スキル repo に validator があるかどうかに関係なく、設計上の acceptance criteria はこうです。

## 17.1 Generic vocabulary check

`llm-wiki` skill 本体に以下が入っていないこと。

```text
Portfolio OS
Hermes
work_unit
commander
council
registry-core
governance-core
companies
Kanban
```

## 17.2 Mode coverage check

`SKILL.md` に以下があること。

```text
bootstrap
ingest
query
draft-review
canonicalize
lint
```

## 17.3 Draft review check

`operations.md` に以下が明記されていること。

```text
promote
merge
reject
defer
```

かつ、`promote` / `merge` 後は canonical page / `index.md` / `log.md` を更新すること。

## 17.4 Direct write boundary check

`operations.md` に以下が残っていること。

```text
owner + Write: owned の場合だけ direct canonical update
non-owner は draft note
closed / restricted / no-access は書かない
```

## 17.5 Index/log invariant check

`schema-and-conventions.md` に以下があること。

```text
index.md:
  canonical discoverability

log.md:
  durable change audit trail
```

## 17.6 Adapter hook check

`federated-knowledge-roots.md` に以下があること。

```text
system-specific registry formats are allowed
generic llm-wiki only needs resolved generic fields
system-specific policy stays outside the generic skill
```

---

# 18. 実装順序

実装するなら、この順番が安全です。

```text
Phase 1:
  SKILL.md の mode list を更新

Phase 2:
  operations.md に draft-review section を追加

Phase 3:
  operations.md の Page Lifecycle を canonicalize section に昇格

Phase 4:
  schema-and-conventions.md に draft status / index invariant / log invariant を追加

Phase 5:
  federated-knowledge-roots.md に adapter hook を追加

Phase 6:
  draft-note.md / log.md / AGENTS.md templates を軽く更新

Phase 7:
  generic vocabulary check
```

---

# 19. 最終的な `llm-wiki` vNext の姿

```text
llm-wiki
  = local Markdown wiki を persistent knowledge base として保守する汎用 skill

持つもの:
  - bootstrap
  - ingest
  - query
  - draft-review
  - canonicalize
  - lint
  - raw/wiki/index/log layout
  - draft note convention
  - page lifecycle convention
  - multi-root generic authority fields
  - optional system-specific adapter hook

持たないもの:
  - Portfolio OS 固有 runtime
  - Hermes profile
  - TOML registry schema
  - domain-specific workflow
  - script orchestration
```

---

# 20. 最終判断

今回の `llm-wiki` 強化は、**新しい外部 workflow を作る話ではなく、既存の汎用 skill に「owner review」と「canonical maintenance」を first-class procedure として足す話**です。

最小かつ効果が大きい変更はこれです。

```text
1. `draft-review` mode を追加する
2. `canonicalize` mode を追加する
3. `index.md` / `log.md` を invariant として明文化する
4. root registry は format 非依存にし、adapter hook だけ足す
5. draft-note template を少しだけ強化する
```

これにより、Portfolio OS ではもちろん使えますが、同時に、研究 wiki、個人 wiki、チーム wiki、製品仕様 wiki、顧客調査 wiki、Obsidian vault などでもそのまま使える汎用 `llm-wiki` skill になります。
