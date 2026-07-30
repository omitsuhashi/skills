---
title: Task Management Hermes Schedule Secretary Readiness 仕様
date: 2026-07-30
updated: 2026-07-31
tags:
  - task-management
  - github-projects
  - hermes
  - schedule-secretary
  - specification
status: approved
approved_on: 2026-07-31
aliases:
  - Task Management Hermes Readiness
  - Schedule Secretary Task Management MVP
---

# Task Management Hermes Schedule Secretary Readiness 仕様

## Status

2026-07-31、Human が本 page を Written Spec として承認した。Written Spec Gate は
承認済みである。Issue ledger、Issue Gate、implementation plan、Execution Plan Gate、
implementation は未実施であり、それぞれの current gate を通過するまで開始しない。
Companies repository の変更、managed-native apply、live Hermes / GitHub MCP の設定変更と
task mutation は本承認に含まれず、引き続き別の明示承認を要する。

本書は [[../direct-github-projects-task-management/spec|GitHub Projects 直接接続型 Task Management Skill 仕様]]
を置き換えるものではない。同仕様を現在の task semantics の基礎とし、
Hermes Agent の Schedule Secretary で personal-use MVP を成立させるための
portable contract revision、managed-native delivery、live readiness の追加境界を定義する。
既存実装の履歴と完了状態は
[[../direct-github-projects-task-management/issues|GitHub Projects 直接接続型 Task Management Skill Issue 台帳]]
を参照する。

## Epic ID

`task-management-hermes-readiness`

## Problem

standalone `task-management` skill は GitHub Projects を正本とし、GitHub MCP を直接使う
基本契約を既に持つ。しかし Schedule Secretary に install されたという事実だけでは、
personal-use MVP が安全に使えるとは判定できない。

- write preflight が操作単位でなければ、comment や title edit が無関係な create /
  Project write capability の不足で停止する。
- close-side の整合契約はあっても、reopen 時に戻す Project Status と部分失敗の再開規則がない。
- Status-filtered list、pagination、truncation、duplicate discovery の completeness 表現が
  未定義だと、不完全な読み取りを完全な結果として扱い得る。
- portable skill、Companies / Portfolio OS の managed-native install、live Hermes /
  GitHub MCP の credential・permission・tool・target・schema は異なる owner と証拠を持つが、
  一つの「ready」に畳むと未確認部分が隠れる。
- repository 外の permission / configuration work を durable に計画しなければ、
  repository implementation 完了が live 利用可能性と誤認される。

## Goals

1. Schedule Secretary が personal-use MVP として実行する task operation の意味論を
   portable `task-management` skill に固定する。
2. preflight を operation-scoped にし、当該操作と未完了 side に必要な semantic
   capability だけを fail-closed で確認する。
3. Status-filtered list、pagination、completeness、truncation、continuation、duplicate
   discovery の読み取り契約を固定する。
4. Done / Cancelled からの reopen を Issue と Project Status の一つの logical
   operation として定義し、resume-only partial failure を保証する。
5. portable skill、Companies / Portfolio OS、live Hermes / GitHub MCP の ownership、
   durable artifact、acceptance evidence、approval boundary、delivery sequence を分離する。
6. Schedule Secretary readiness を単独 report として出力し、各 operation の
   `ready` / `partial` / `blocked` と不足 seam を判別可能にする。
7. GitHub MCP 以外へ fallback せず、未確認・truncated・権限不足を成功として扱わない。

## Non-goals

- GitHub 以外の provider、CLI、REST client、GraphQL client、browser automation、
  local backend を fallback として追加すること。
- GitHub の assignee、label、milestone、Issue type、parent / sub-issue を作成、追加、
  削除、置換、または同期すること。
- repository 間の label / Issue type taxonomy を統一すること。
- Project field、option、view、workflow、repository、Project を通常 task operation の
  副作用として作成または修復すること。
- Project native draft item、Portfolio OS の task mirror、skill-owned credential /
  default store を追加すること。
- Schedule Secretary 以外の profile を MVP の delivery target に含めること。
- live credential、secret value、token、agent ID、会話 transcript、実行 transcript、
  concrete run evidence を durable artifact に保存すること。
- 本仕様の承認だけで branch push、PR、merge、release、Companies change、live install、
  permission change、schema setup、GitHub task mutation を承認すること。

## Confirmed Decisions

1. **Operation-scoped semantic capability preflight**
   各 operation は capability matrix の必要意味能力だけを確認する。retry は未完了 side
   に必要な能力だけを再確認する。tool 名は portable contract に固定しない。
2. **Independent Schedule Secretary readiness report**
   readiness は portable contract、managed-native delivery、live MCP の三層を別々に
   判定し、profile 全体や別 operation の不足を当該 operation の readiness と混同しない。
3. **Portable semantics ownership**
   `skills/task-management/` が task semantics、failure / continuation contract、
   fixture-backed behavioral tests を所有する。
4. **Managed-native ownership**
   Companies / Portfolio OS が source selection、install、content hash、profile discovery、
   caller default materialization、readiness orchestration を所有する。skill 本文を
   Companies に複製しない。
5. **Live boundary ownership**
   live Hermes / GitHub MCP が credential、permission、exact tool mapping、target access、
   live schema を所有する。setup は通常操作から分離し、対象と副作用を示した別承認を要する。
6. **Reopen target**
   利用者が reopen 後の Status を明示した場合はその Status を優先する。Status 指定のない
   bare reopen は `Backlog` を既定値とする。
7. **Reopen atomicity semantics**
   Issue reopen と Project Status 更新は一つの logical operation だが、provider 上の
   atomic transaction とはみなさない。片側成功時は rollback せず、成功済み side を保存し、
   retry は残 side だけを実行する。
8. **GitHub-native metadata exclusion**
   assignee、label、milestone、Issue type、parent / sub-issue の write は MVP から除外する。
   title/body edit、comment、Status/Priority/Due date、terminal/reopen operation は、
   これら既存 native metadata を変更しない。
9. **Status-filtered list limit**
   七つの Status と利用者の通常表現を受け付ける。raw Project items を pagination し、
   matching item を最大 50 件集めるか raw source exhaustion まで続ける。
10. **Completeness contract**
    list result は `complete` または `partial`、truncation の有無、continuation の有無を
    明示する。50 件上限、tool page limit、permission failure、schema ambiguity その他で
    読み取りが打ち切られた結果を `complete` と主張しない。
11. **Completeness-required query**
    duplicate discovery や「全件」を前提とする query は exhaustion まで paginate するか
    `partial` を返す。duplicate discovery が truncated なら「重複なし」と結論しない。
12. **MVP operation set**
    read / search / list、create / register、title / body edit、comment、Status / Priority /
    Due date、Done / Cancelled、reopen のみを対象にする。
13. **No fallback**
    必要な GitHub MCP capability、permission、target、schema が不足または不確実なら
    fail closed とし、別 transport や別 backend に切り替えない。
14. **Live workflow is planned, not authorized**
    live delivery は `dry-run -> apply -> status -> readback` を必要工程として計画するが、
    現時点では apply、permission/configuration mutation、live task write を承認しない。

## Open Decisions

なし。repository research と Confirmed Decisions の間に material conflict はない。

## Architecture / Seams

| Seam | Durable owner | Owns | Must not own |
|---|---|---|---|
| Portable semantics | Skills repository | operation contract、Status mapping、pagination/completeness、reopen、partial failure、behavioral tests | credential、exact live tool name、profile path、caller default value、live schema ID |
| Managed-native delivery | Companies / Portfolio OS | approved source identity、install/hash、Schedule Secretary discovery、default materialization、readiness aggregation、update receipts | task semantics の fork、credential、GitHub task state、silent live setup |
| Live execution | Hermes Schedule Secretary / GitHub MCP | authenticated identity、exact tools、permissions、target access、schema readback、separately authorized setup | portable semantics の再定義、repository completion の代替証拠 |

end-to-end flow は次の一方向とする。

1. Schedule Secretary が caller-owned `project_url` と optional `inbox_repository` を
   invocation context へ提供する。
2. portable skill が intent を MVP operation に分類し、必要 semantic capability と
   target / completeness contract を決める。
3. managed-native readiness が installed bytes、discovery、default materialization を
   独立に示す。
4. live readiness が当該 operation の exact tool mapping、authenticated identity、
   permission、target access、schema を read-only で確認する。
5. readiness が揃った operation だけを GitHub MCP で実行し、exact target readback と
   completion / partial result を返す。

どの seam も他 seam の未確認状態を推定で補完しない。

## Operation Capability Matrix

semantic capability は実装 tool 名ではなく意味能力で表す。`target read` は Issue /
Project identity、current state、必要 field/schema の読み取りを含む。

| Operation | Required read capability | Required write capability | Completeness / readback |
|---|---|---|---|
| read | target Issue / Project item read | なし | requested entity の identity と current values |
| search | Issue search、Project item read/list | なし | query が completeness-required なら exhaustion、不能なら `partial` |
| Status-filtered list | Project item read/list、Status field read | なし | raw pagination、最大50 matching、complete/partial/truncation/continuation |
| create | duplicate discovery、target repository / Project / schema read | Issue create、Project item add、Status/Priority/Due date field update | Issue と Project item の exact readback。部分成功は残 side を返す |
| register existing Issue | Issue read、duplicate/membership discovery、target Project / schema read | Project item add、Status/Priority/Due date field update | 既存 Issue を変更せず Project item を exact readback。Issue create capability は要求しない |
| title / body edit | Issue read | Issue title/body update | edited field と native metadata preservation の readback |
| comment | Issue read | Issue comment create | created comment identity の readback |
| Status / Priority / Due date | Project item / field read | requested field value update | requested field だけを readback |
| Done / Cancelled | Issue state/reason、Project Status read | Issue close、Project Status update | 両 side の state。片側成功は `partial` |
| reopen | Issue state、Project Status read | Issue reopen、Project Status update | 両 side の state。片側成功は `partial`、retry は残 side のみ |

create / register の duplicate discovery が `partial` の場合、既存 task がないとは
断定しない。high-confidence な同一 task を一意に確認できなければ create を停止する。

## Flows

### Read / search / list

1. target Project / repository / Issue を現行 direct GitHub Projects contract の順序で解決する。
2. operation に必要な read capability だけを preflight する。
3. filtering がある場合も raw page を一ページだけ読んで終えず、Status / query match を
   client-side または tool-supported filter の結果として数える。
4. result とともに completeness、truncation、continuation、未確認範囲を返す。
5. read operation から create、register、field update、comment を起動しない。

### Create / register

1. outcome、acceptance criteria、Issue repository、Project target を確定する。
2. duplicate discovery を completeness-required query として実行する。
3. 新規作成なら Issue create と後続 Project write、既存 Issue の register なら未完了の
   Project write だけを preflight する。
4. Issue を新規作成するか、高確度に同一な既存 Issue を再利用する。
5. Project membership と requested/default field を不足分だけ反映する。
6. exact readback で Issue、Project item、Status、Priority、Due date、成功済み step、
   未完了 step を返す。

新規 item の既定値は `Status=Inbox`、`Priority=P2`、Due date 未設定とする。retry や
既存 Issue 再利用では、既存 field を既定値へ reset しない。

### Edit / comment / field update

requested property だけを更新する。title/body edit は assignee、label、milestone、
Issue type、parent / sub-issue を保持する。comment は Issue 本文や Project field を
変更しない。Status/Priority/Due date は指定された Project field だけを変更する。

### Done / Cancelled

`Done` は Issue close reason `completed`、`Cancelled` は `not planned` と対応する。
Issue close と Project Status は一つの logical operation とし、明示依頼なら追加確認を
重ねない。文脈からの推定だけなら実行前に確認する。片側成功時は reopen と同じ
resume-only partial failure contract を使う。

## Status / Pagination

### Accepted Status values and user wording

| Canonical Status | 受け付ける代表的な利用者表現 |
|---|---|
| `Inbox` | Inbox、受信箱、未整理 |
| `Backlog` | Backlog、バックログ、実施候補 |
| `Ready` | Ready、着手可能、準備完了 |
| `In progress` | In progress、進行中、着手中、対応中 |
| `Blocked` | Blocked、ブロック中、停止中 |
| `Done` | Done、完了、終了 |
| `Cancelled` | Cancelled、Canceled、中止、キャンセル |

曖昧な表現を複数 Status へ推定しない。利用者表現は canonical Status へ正規化してから
schema option と照合し、option 不在または重複時は schema mismatch として停止する。

### Canonical identity and page reconciliation

Issue-backed MVP の canonical identity は次の順序で解決する。

1. `canonical_task_identity`: GitHub が返す stable Issue identity。利用可能なら opaque な
   global Issue ID、なければ canonical Issue URL、さらに URL が得られない場合だけ
   normalized `owner/repository#number` を使う。
2. `canonical_project_item_identity`: target Project 内の opaque stable Project item ID。
   tool が item ID を返さない場合は
   `(canonical Project URL, canonical_task_identity)` を fallback identity とする。

canonical Issue URL は host を `github.com`、path を
`/{casefold(owner)}/{casefold(repository)}/issues/{decimal number}` とし、query、fragment、
trailing slash を除く。canonical Project URL も owner kind (`users` / `orgs`)、casefold
owner、decimal Project numberだけを保持し、query、fragment、trailing slashを除く。

identity component が不足して一意性を証明できない observation は unique match として
数えず、result を `partial` とする。同じ Project item identity が異なる task identity を
指す場合は identity conflict として両 observation を隔離し、exact readback まで output
にも match count にも入れない。

各 raw observation には取得順の `(page ordinal, item ordinal)` を付け、page 単位で次の
reconciliation を行う。

- 同じ Project item identity の observation は一件へ畳む。双方に authoritative
  `updated_at` があれば field ごとに新しい observation の明示値を採用し、同値なら
  取得順が後の observation を採用する。欠損値は先行 observation の既知値を消さず、
  provider が明示する clear/null だけを値の削除として扱う。`updated_at` がなくても、
  一方だけが非欠損ならその値を採用する。
- 同一 field に競合する非欠損値があり、authoritative timestamp または exact readback で
  順序を決められない場合、その item は `partial` / reconciliation conflict とし、
  match count から外す。
- 同じ task identity が複数 Project item identity に現れた場合、task output は一件に
  deduplicateし、最初に観測した item を表示位置の基準とする。全 membership identity を
  conflict detail として保持し、result は `partial` とする。write operation は一意な
  membership の exact readback まで停止する。
- 更新された observation が Status filter に一致しなくなった場合は、それ以前の match を
  match set から除く。一致するようになった場合は同じ canonical task の一件として追加する。
- output order は canonical task identity の最初の有効 observation 順とし、後続更新でも
  並び順を変えない。

50件判定は raw row 数でも Project item observation 数でもなく、reconciliation 後の
`canonical_task_identity` の unique matching count に対して行う。停止判定は各 raw page
全体を merge して conflict と Status change を反映した後にだけ行い、page 途中では行わない。

### List contract

- filter のない list と Status-filtered list は同じ completeness envelope を返す。
- Status-filtered list は raw Project items を順に paginate し、matching item が
  50 unique canonical task に達するか raw item exhaustion まで続ける。duplicate /
  updated observation は件数を増やさない。
- page reconciliation 後に50 unique matching taskへ達した時点で未走査 raw itemが
  あり得るなら、返却件数が50でも
  `partial` / truncated とし、continuation を示す。
- source exhaustion を確認できた時だけ `complete` とする。
- tool が continuation token / cursor を提供する場合は opaque identity のまま返し、
  skill が値を合成しない。continuation を提供できない打ち切りも `partial` とする。
- permission error、page retrieval failure、schema ambiguity、tool-side hard limit は
  取得済み items を捨てず、`partial`、停止理由、再開可能性を返す。
- completeness-required query は 50 件の表示上限と調査範囲を混同しない。全範囲を
  exhaustion まで調べ、表示を50件へ制限するか、途中停止なら `partial` とする。
- duplicate discovery が truncated / partial の場合、「duplicate なし」「新規作成安全」
  と結論しない。
- result envelope は `raw_observation_count`、`unique_task_count`、`returned_count`、
  deduplicated observation 数、identity/reconciliation conflict 数を持つ。これらの件数は
  pagination 完了条件と表示上限を混同せず、fixture から同じ値を再計算できるものとする。

## Reopen

1. Issue と Project item の exact identity、current Issue state、current Status を読む。
2. 利用者が seven Status の非 terminal target を明示した場合はその Status を使う。
   target 指定のない bare reopen は `Backlog` を使う。
3. `Done` または `Cancelled` を reopen target として指定された場合は矛盾として停止する。
4. Issue reopen と target Status update の両方に必要な semantic capability、permission、
   schema を operation-scoped に preflight する。
5. 両 side を一つの logical operation として実行し、双方を exact readback する。
6. 片側だけ成功した場合は成功 side を rollback せず、result を `partial` とする。
   completed side、remaining side、current Issue state、current Status を返す。
7. retry は readback で成功済み side を確認し、remaining side だけを実行する。
   既に reopen 済みの Issue を再更新したり、成功済み Status を既定値へ戻したりしない。

## Failures

| Failure | Required behavior |
|---|---|
| MCP unavailable | operation を実行せず、GitHub MCP boundary の不足として報告する |
| semantic capability missing | 当該 operation または remaining side に不足する意味能力だけを列挙する |
| authentication / permission failure | rejected target と operation を報告し、credential value を要求・保存しない |
| target ambiguity | write をせず、矛盾する candidate identity を提示する |
| schema mismatch | field / option の期待 contract と不足を報告し、通常操作から setup へ進まない |
| pagination/truncation | 取得済み範囲を `partial` として返し、`complete` や no-duplicate を主張しない |
| partial mutation | 成功済み side を保持し、exact readback、remaining side、resume instruction を返す |
| readback unavailable | mutation success を確定せず `partial` とし、再 mutation より先に readback を要求する |

failure 後に Issue や Project item を削除して rollback しない。別 transport、別 backend、
推定 target、silent schema repair へ fallback しない。

## Readiness

Schedule Secretary readiness は installation status の別名ではなく、次の独立 report とする。

| Section | Required checks | Result vocabulary |
|---|---|---|
| Portable contract | approved semantic revision、behavioral test coverage、no-fallback boundary | `ready` / `blocked` |
| Managed-native delivery | selected source identity、expected content hash、Schedule Secretary install、discovery、caller defaults | `ready` / `partial` / `blocked` |
| Live GitHub MCP | registration、authenticated identity、operation-to-tool mapping、permission、target access、schema、pagination behavior | operationごとの `ready` / `partial` / `blocked` |

### Deterministic classification

readiness は operation ごとに applicable な atomic check を評価し、各 check を次の一つへ
分類する。

- `ready`: required state と non-mutating acceptance evidence が現在値として肯定されている。
- `partial`: required state は否定されていないが、read-only evidence が unknown、
  unavailable、または write authorization を証明するには不十分である。
- `blocked`: required state が missing、stale、mismatched、rejected、または semantic
  capability として不在であり、その operation を安全に実行できない。

集約 precedence は常に `blocked > partial > ready` とする。operation × layer の result は
applicable atomic checks の最大 severity、operation result は portable / managed-native /
live layer の最大 severity、全体 result は requested MVP operations の最大 severity とする。
他 operation にだけ必要な check と `not_applicable` check は集約から除外する。各 result は
最大 severity を生んだ reason code をすべて保持し、単一の曖昧な「not ready」へ畳まない。

| Condition | Classification | Scope / reason code |
|---|---|---|
| approved expected hash と installed hash が一致し、current readback | `ready` | managed-native / `installed_hash_current` |
| installed hash が expected hash と不一致または旧revisionで stale | `blocked` | managed-native / `installed_hash_stale_or_mismatch` |
| expected hash はあるが installed hash を非破壊に取得できない | `partial` | managed-native / `installed_hash_unknown` |
| approved expected hash 自体が未定義 | `blocked` | managed-native / `expected_hash_missing` |
| Schedule Secretary が skill を discovery 済み | `ready` | managed-native / `skill_discovered` |
| discovery check が未実行または結果不明 | `partial` | managed-native / `skill_discovery_unknown` |
| skill が存在しない、無効、または discovery されないことを確認 | `blocked` | managed-native / `skill_not_discovered` |
| operation に必要な caller default が current readback 済み | `ready` | managed-native / `caller_default_current` |
| invocation が exact target を明示しており default を使わない | `not_applicable` | 当該 invocation の default check を集約から除外 |
| default-driven operation で `project_url` がmissing | `blocked` | managed-native / `project_default_missing` |
| repository-independent create で `inbox_repository` がmissing | `blocked` | managed-native / `inbox_default_missing` |
| repository-specific operation で inbox を使わない | `not_applicable` | inbox check を集約から除外 |
| required semantic tool mapping が存在し exact schema を読める | `ready` | live / `semantic_tool_present` |
| required semantic tool が存在しない | `blocked` | live / `semantic_tool_missing` |
| tool inventory / mapping が非破壊に確認できない | `partial` | live / `semantic_tool_unknown` |
| authoritative permission evidence が当該 operation / target を許可 | `ready` | live / `permission_confirmed` |
| permission が unknown、または tool presence とread accessしか確認できない | `partial` | live / `permission_unknown` |
| target permission が拒否された、credential が無効、または認証主体がtargetにaccess不可 | `blocked` | live / `target_permission_rejected` |
| required field/options が exact contract と一致 | `ready` | live / `schema_current` |
| required field/options がmissing、重複、または型/option不一致 | `blocked` | live / `schema_mismatch` |
| schema を非破壊にreadbackできない | `partial` | live / `schema_unknown` |

write operation は、semantic tool の存在だけでは `ready` にしない。authoritative な
operation/target permission evidence を mutation なしで取得できない場合、read-only
preflight の上限は `partial` とする。実 write を readiness probe として行わない。
read operation は required read permission と target readback が肯定されれば `ready` に
できる。schema check はその operation が使う field/options だけを applicable とする。

report は少なくとも次を含む。

- report scope が Schedule Secretary であること。
- portable / managed-native / live の各判定と owner。
- MVP operation ごとの readiness と不足 semantic capability。
- configured target が解決可能か、Status 7 option、Priority 4 option、Due date field が
  read-only で確認可能か。
- list の pagination / continuation / truncation contract を満たせるか。
- setup が必要な場合の exact category と別承認境界。
- live mutation を行っていない場合、その事実。

一つの section が `ready` でも全体を自動的に ready としない。全体 `ready` は対象
operation に必要な三層がすべて ready の時だけ許容する。

## Cross-repo / External Delivery Map

| Sequence | Delivery surface | Owner | Durable artifact | Acceptance evidence | Approval boundary | Required runbooks / receipts |
|---|---|---|---|---|---|---|
| 1 | Skills repository | Skills maintainer | 本 spec、後続 Issue ledger、implementation plan、portable skill/references/tests | approved spec binding、fixture-backed operation/pagination/reopen tests、repository validators | Written Spec Gate、Issue Gate、Execution Plan Gate。push/PR/mergeは別承認 | TDD verification plan、contract change summary、local verification receipt |
| 2 | Companies repository / Portfolio OS | Companies maintainer | managed-native selection/version/hash contract、Schedule Secretary profile declaration、default/readiness contract、update plan | source/hash consistency、planned install/discovery/default assertions、dry-run diff | Companies側のspec/plan approval。live apply、reinstall、profile mutationは別承認 | managed-native dry-run/apply/status/readback runbook、backup/rollback receipt requirements、discovery/default readback receipt |
| 3 | live Hermes Schedule Secretary | Runtime operator | approved runbook identityとredacted readiness receipt。secretやprofile dumpは保存しない | installed hash match、skill discovery、caller default resolution、read-only readiness result | live install/reinstall/restart/profile config applyは対象を示した明示承認 | `dry-run -> apply -> status -> readback`、failure recovery、rollback条件、redacted apply/status/readback receipt |
| 4 | live GitHub MCP / GitHub target | GitHub/runtime operator | permission/setup runbookとredacted capability/schema receipt | authenticated identity category、exact operation mapping、target access、field/options、pagination behaviorのreadback | credential、permission、MCP config、schema mutation、Issue/Project writeはそれぞれ別承認 | read-only preflight、可能ならsetup dry-run、authorized apply、status、exact readback、partial-failure recovery receipt |

delivery は原則 1 → 2 → 3 → 4 とする。read-only discovery で後段 requirements を
事前確認できても、未承認 mutation を前倒ししない。Skills repository の完了は
Companies apply または live readiness を意味しない。

## Permission / Setup Runbook Requirements

### Common requirements

各 runbook は対象 seam、owner、目的、precondition、read-only checks、mutation steps、
stop conditions、readback、failure recovery、approval identity categoryを定義する。
credential、secret value、token、agent ID、transcript、raw profile dump は記録しない。

各 receipt は planned / dry-run / applied / verified / partial / blocked を区別し、
対象の非秘密 identity、operation、timestamp、expected/observed state category、
未完了 step、rollback availability を持つ。具体的な run evidence は実行後の別 artifact
であり、本 spec には含めない。

### Companies / Portfolio OS managed-native runbook

1. approved source revision と expected content hash を解決する。
2. Schedule Secretary だけを対象に selection、install、discovery、caller defaults の
   planned diff を dry-run する。
3. dry-run receipt を Human が確認し、apply authority を別途与えた場合だけ apply する。
4. update status と apply log / backup manifest / rollback bundle の有無を確認する。
5. installed bytes hash、skill discovery、default materialization、readiness report input を
   exact readback する。
6. mismatch または partial apply では自動再installせず、残 step と rollback option を返す。

### Live Hermes / GitHub MCP runbook

1. Schedule Secretary profile と target Project / repository の非秘密 identity を確定する。
2. MCP registration、authenticated identity category、exact available tools、operation mapping、
   permissions、target access、schema、pagination behaviorを read-only で preflight する。
3. 不足 configuration / permission / schema を通常 task operation と分離して列挙する。
4. setup mechanism が dry-run を持つ場合は dry-run し、持たない場合は proposed mutation
   と readback を事前提示する。
5. Human が exact target と副作用を承認した場合だけ apply する。
6. status と exact readback を行い、operation-scoped readiness report を再生成する。
7. partial failure では成功済み setup を記録し、remaining side だけを再開する。

現時点では上記 runbook の設計だけが scope であり、apply、permission grant、credential
configuration、schema mutation、Issue / Project mutation は未承認である。

## Acceptance Criteria

### Portable semantics

- [ ] MVP operation set が matrix として固定され、各 operation の required semantic
  capability が最小範囲で定義されている。
- [ ] comment、title/body edit、read/list が無関係な create / Project write capability
  不足で block されない。
- [ ] retry preflight は remaining side だけを対象にする。
- [ ] assignee、label、milestone、Issue type、parent / sub-issue write が明示的に除外され、
  supported operation 後も既存値を保持する。
- [ ] seven Status と利用者表現の正規化、schema ambiguity stop が定義されている。
- [ ] Status-filtered list が raw items を paginate し、最大50 matching item、
  exhaustion、complete/partial、truncation、continuation を正しく表す。
- [ ] Project item / task の canonical identity、page間reconciliation、identity conflict、
  deterministic output order が定義され、50件上限がunique canonical taskだけを数える。
- [ ] completeness-required query は exhaustion または `partial` を返す。
- [ ] truncated duplicate discovery が no-duplicate claim または create へ進まない。
- [ ] explicit reopen target が優先され、bare reopen が `Backlog` になる。
- [ ] reopen が Issue + Project Status の logical operation、no rollback、resume-only
  partial failure、exact readback を持つ。
- [ ] CLI、REST、GraphQL、browser、local backend への fallback がない。

### Managed-native and live readiness

- [ ] Companies / Portfolio OS の責務が source/hash/install/discovery/default/readiness に
  限定され、portable task semantics を複製しない。
- [ ] Schedule Secretary readiness report が portable、managed-native、live の三層と
  operation別 result を独立表示する。
- [ ] readiness のatomic condition mapping、`blocked > partial > ready` precedence、
  `not_applicable`除外、reason code保持が固定され、同じfactsから同じ結果を再計算できる。
- [ ] live readiness が credential value を保存せず、identity category、exact tool mapping、
  permission、target access、schema、pagination behaviorを確認する。
- [ ] schema setup、permission change、credential configuration、live task write が
  separately authorized operation として通常利用から分離される。
- [ ] Skills、Companies、live Hermes、live GitHub の durable artifact、evidence、
  owner、sequence、approval boundary、runbook/receipt が delivery map に固定される。
- [ ] planned live workflow が `dry-run -> apply -> status -> readback` を要求し、
  apply が現時点で未承認と明示される。

### Documentation integrity

- [ ] 本 page、`knowledge/index.md`、`knowledge/log.md` が同期される。
- [ ] 現行 direct GitHub Projects spec / ledger への Obsidian wikilink が解決する。
- [ ] placeholder、credential、secret、agent ID、transcript、concrete live run evidence がない。
- [ ] current approved spec を誤って supersede または historical 扱いしない。

## Verification

### Skills repository

- fixture-backed behavioral tests で operation capability matrix を各行検証する。
- comment/edit/read が unrelated capability 不足の影響を受けない negative scenario を持つ。
- seven Status と利用者表現、raw page traversal、50 matching limit、exhaustion、
  partial/truncation/continuation を deterministic fixture で検証する。
- repeated item、updated Status、missing field、conflicting observation、同一taskの複数itemを
  page境界に配置し、deduplication、merge、unique count、stable order、page単位停止判定、
  result envelope countsをtable-driven fixtureで検証する。
- duplicate discovery の complete / partial 両方を検証し、partial から create しない。
- reopen は explicit target、bare `Backlog`、Issue-first partial、Status-first partial、
  exact retry remaining-side-only を state-machine fixture で検証する。
- native metadata fixture を用い、全 supported mutation 後に assignee、label、milestone、
  Issue type、parent / sub-issue が不変であることを検証する。
- existing task-management focused tests、skill validator、repository skill architecture
  validator、`git diff --check` を implementation plan で exact command 化する。

### Companies / Portfolio OS

- managed-native source identity / content hash selection、Schedule Secretary-only discovery、
  caller default materialization、readiness aggregation を repository fixture で検証する。
- stale/mismatch/unknown hash、discovered/unknown/not-discovered skill、default present/missing/
  invocation overrideをatomic reason code fixtureにし、precedence表から期待layer resultを
  直接導出する。
- dry-run が intended target/diff を示し apply しないこと、status/readback が
  installed hash/discovery/default を独立判定することを検証する。
- apply-log、backup/rollback artifact の contract は Companies repository の current
  update-plane に合わせて実装計画で exact file/test へ mapping する。

### Live boundary

- repository gate では live write を行わない。
- live verification は別承認後、まず read-only readiness を実行し、operation-to-tool
  mapping、permission、target access、schema、pagination behaviorを確認する。
- missing/unknown/present semantic tool、permission confirmed/unknown/rejected、
  schema current/unknown/mismatchをtable-driven fixtureで組み合わせ、
  `blocked > partial > ready`、operation scope、non-mutating write ceilingを検証する。
- install/config/setup apply が必要なら、別途承認された
  `dry-run -> apply -> status -> readback` を実行する。
- test Issue / Project mutation はさらに別の Live Write Gate を要し、対象、操作、
  cleanup /残存 artifact、partial failure handling を事前提示する。

## Authorization Boundary

この Written Spec の作成と将来の承認が許可するのは、Skills repository 内の planning
artifact と、後続 gate で承認された local implementation だけである。

次はすべて未承認であり、exact target と副作用を示した別の明示承認を要する。

- Companies repository の変更、push、PR、merge、release。
- managed-native install / reinstall、profile config、default materialization、restart。
- GitHub MCP registration、credential configuration、permission grant。
- Project schema / option / workflow の作成・修復。
- live Issue / Project の create、edit、comment、field update、close、reopen。
- その他の remote write または live mutation。

read-only discovery も対象環境と scope を明示し、結果を別 seam の readiness へ推定で
流用しない。本 spec は live state が ready、missing、または broken だとは主張しない。

## Implementation-planning Constraints

1. Human が本 Written Spec の exact revision を承認するまで Issue ledger と implementation
   plan を作成しない。
2. Issue Gate では少なくとも portable semantics、Companies managed-native delivery、
   live runbook/readiness preparation を別 Issue / owner に分け、dependency order を固定する。
3. Skills repository と Companies repository は repository-local spec / plan / tests を
   それぞれ正本とし、chat handoff だけで delivery を完了扱いしない。
4. portable behavior は TDD と fixture-backed state machine で実装し、static prose
   assertion だけを acceptance evidence にしない。
5. Companies work は current managed-native/update-plane contract を先に research し、
   official dry-run/apply/status/readback path を implementation plan に mapping する。
6. live work は repository implementation と分離し、runbook、approval、redacted receipt
   schemaを先に確定する。live mutation を repository test の前提にしない。
7. exact tool 名、credential、permission、schema ID、profile path は portable skill に
   hard-code しない。
8. no-fallback、operation-scoped preflight、completeness、resume-only partial failure を
   独立 acceptance criteria とし、一つの包括的「works」判定へ畳まない。
9. current [[../direct-github-projects-task-management/spec|direct GitHub Projects spec]] と
   [[../direct-github-projects-task-management/issues|current ledger]] の historical
   evidence を書き換えない。本 follow-up が承認されるまで current contract の
   lifecycle stateを変更しない。

## Provenance

- current product boundary:
  [[../direct-github-projects-task-management/spec|GitHub Projects 直接接続型 Task Management Skill 仕様]]
- current implementation history:
  [[../direct-github-projects-task-management/issues|GitHub Projects 直接接続型 Task Management Skill Issue 台帳]]
- decision authority: 2026-07-30 の Human-confirmed decisions。本 page は approval 前の
  synthesis であり、live readiness や live state の verified claim を含まない。
