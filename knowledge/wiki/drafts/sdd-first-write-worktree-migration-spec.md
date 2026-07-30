# SDD first-write worktree migration 仕様（昇格済み draft）

## Status

- 状態: promoted
- 対象: `sdd-implementation` の pre-implementation write boundary と、同一 Epic 内の opt-in parallel issue orchestration
- 正本性: この文書は non-owner actor による proposal の履歴であり、verified canonical specification は昇格先にある
- owner decision: `promote`
- decision actor: Human / repository maintainer（Canonical Owner）
- decision date: 2026-07-30
- decision reason: Human が Written Spec として明示承認したため
- destination: [[wiki/syntheses/sdd-first-write-worktree-migration-spec|SDD first-write worktree migration 仕様]]

## Problem

repository policy は、task がどの branch の checkout から始まっても、その
checkout を task work について read-only に保ち、最初の repository write
より前に Epic-scoped planning worktree を作成または再利用することを要求して
いる。しかし現在の SDD contract は、Planning Controller、Research Worker、
Spec Synthesis Worker、Spec Reviewer、Plan Author に generic な repository
root と artifact path を渡すだけで、first-write 前の worktree allocation、
同一 worktree への path binding、その証明、失敗時の停止を定義していない。
このため transient Research Report が original checkout に対する最初の write
になり得る。

さらに、repository policy は execution isolation のための issue worktree を
許可している一方、canonical Superpowers SDD は一つの approved plan を一つの
isolated working tree で sequential に実行する。複数 issue を同時進行させる
場合にも、同一 worktree の concurrent writer、SDD 内部 scheduler の改変、
issue ごとの成功を Epic 全体の成功とみなすことを許してはならない。

## Goals

1. 同じ user-facing chat / main session を継続したまま、最初の content または
   artifact write より前に Epic planning linked worktree を allocate または
   reuse する。
2. planning phase の controller と全 worker に渡す repository root、CWD、
   writable artifact path を、その planning worktree に一貫して bind する。
3. original checkout の starting branch、HEAD、index、tracked files、既存の
   dirty state を一切変更しない。
4. binding と original-checkout preservation を証明できなければ、write 前に
   fail closed する。
5. canonical Superpowers SDD の一 issue 内の sequential task/review/fix flow と
   whole-branch review authority を維持する。
6. Human が明示的に選んだ場合だけ、独立性を確認できる同一 Epic の複数 issue
   を、issue ごとに分離した branch/worktree/session で進行可能にする。
7. integration を single-writer で `integration_branch` に直列化し、全 issue
   commit を含む final PR head に対する combined verification と
   whole-branch review を completion gate にする。
8. chat 開始時の `starting_branch` と immutable な `starting_head_sha` を
   planning branch、integration ancestry、eventual PR base の一貫した基準に
   する。
9. approved implementation plan より前は compact binding tuple を既存の
   Planning Controller Stage Capsule/control context だけに保持し、plan が
   canonical Superpowers SDD に入る通常時に ordinary plan-owned
   workspace/progress ledger へ transfer する。

## Non-goals

- Superpowers SDD の task decomposition、task brief、implementer/reviewer 選択、
  per-task review/fix loop、ledger、recovery、whole-branch review を複製または
  改変すること
- 一つの worktree、branch、plan、ledger、`HEAD` に複数 writer を許すこと
- 同一 SDD run 内で複数 implementer を concurrent に dispatch すること
- generic parallel dispatch を SDD の代替 scheduler として扱うこと
- scheduler、lock service、event schema、packet format、runtime snapshot、
  runtime state、独自 resume protocol を新設すること
- file path の非重複だけを independence の十分条件とすること
- original checkout で in-place implementation へ fallback すること
- worktree allocation を host-native current-task self-handoff が成功したかの
  ように表現すること
- branch cleanup、worktree deletion、force operation、destructive recovery を
  自動化すること
- repository default branch や publication 時の別 branch を PR base として
  暗黙に推定すること
- target branch の drift を理由に、PR base 名または integration target を
  silently retarget すること
- adapter 独自の repeated whole-branch review/fix loop を作ること
- approved plan 前に repo-local workspace reservation、compatibility bridge、
  recovery file、resume record を作ること

## Terms

### Original checkout

task 開始時に main session が置かれていた filesystem checkout。開始 branch
は default branch に限らず任意の local branch でよいが、detached HEAD は
valid な starting branch を持たない。この checkout の path、branch/HEAD、
index、tracked/untracked state、status が preservation baseline になる。

### Starting branch and starting head SHA

`starting_branch` は chat 開始時に original checkout で checked out されて
いた branch 名であり、eventual PR の唯一の base branch である。
`starting_head_sha` は同じ瞬間にその branch が指していた commit SHA であり、
task 中は immutable な planning/integration baseline とする。

detached HEAD で開始した場合、この pair は存在しないため unsupported とする。
branch を推定・選択・再構成せず、durable task write 前に fail closed する。

### Original-checkout binding tuple

Planning Controller が保持する compact control tuple。original checkout
path、`starting_branch`、`starting_head_sha`、captured starting status、
`integration_branch` とその worktree path/binding identity を、original
checkout preservation と path binding の比較に必要な最小情報として扱う。
approved implementation plan より前は既存の Stage Capsule/control context
だけに存在し、repo-local durable artifact には書かない。

### Epic planning linked worktree

Git common directory を original checkout と共有し、Epic の Written Spec、
Spec Gate、Issue Gate、Execution Plan Gate、planning documentation sync を
担う一つの linked worktree。同一 Epic の planning では作り直さず、安全に
同定できる既存 worktree を再利用する。

### First repository write

tracked/untracked を問わず repository 内の content または artifact を作成・
更新・削除する最初の操作。Research Report、Decision Record、draft spec、
review report、plan、wiki sync、worker output、test-generated repository
artifact を含む。planning worktree を allocate するための Git common
metadata 変更は content/artifact write ではないが、許可範囲は worktree
allocation に必要な shared Git metadata に限る。

### Binding

controller または worker が使用する repository root、CWD、全 writable path
が、その phase で認可された linked worktree に解決され、original checkout
に解決されないこと。文字列上の path 指定だけでなく、実際の解決先を確認
できなければ binding は成立しない。

### Issue execution unit

一つの Human-approved issue plan、一つの isolated branch、一つの isolated
issue worktree、一つの SDD artifact workspace、一つの controller/session
から成る concurrent mutation の最小単位。unit 内では canonical
Superpowers SDD を sequential に実行する。

### Epic adapter

canonical Superpowers SDD の上位に置かれる、thin かつ opt-in の repository
adapter。issue readiness、dependency/conflict verdict、execution unit の
allocation、wait/result routing、serialized integration だけを所有する。

### Integration branch

`integration_branch` は `starting_head_sha` から作る Epic planning branch
であり、planning artifacts と serialized issue integration を所有し、delivery
時には対象 Epic の required issue/task commit をすべて reachability を
保ったまま含む final PR head branch になる。
combined verification と Superpowers whole-branch review はこの integrated
branch range に対して行う。`starting_branch` は PR base だけを意味し、
integration destination や PR head には使わない。

## Ownership

### Human

- Written Spec と issue/plan set を承認する
- parallel issue mode を opt in する
- adapter が安全性を確定できない dependency、overlap、resource conflict、
  integration choice を裁定する
- material scope、risk acceptance、completion を最終承認する

### Main session / Planning Controller

- user-facing dialogue、Confirmed/Open Decisions、approval routing を所有する
- first-write gate を通過するまで read-only discovery だけを行う
- original checkout baseline を確認し、planning worktree の allocate/reuse と
  binding proof を完了してから writable worker を dispatch する
- approved plan 前は original-checkout binding tuple を既存 Stage Capsule/
  control context だけに保持する
- approved plan が canonical Superpowers SDD に入るとき、その tuple を通常の
  plan-owned workspace/progress ledger へ transfer する
- planning artifacts の write destination を planning worktree に限定する
- worker の短い return を統合するが、repository research や full artifact
  authoring を自ら代行しない

### Canonical Superpowers SDD

- issue plan 以下の task decomposition と実装順序
- fresh implementer/reviewer、per-task commit/test/review/fix
- issue 内 ledger と recovery
- issue branch review および integrated final branch の whole-branch review
- branch finishing methodology

この authority は adapter に移譲しない。

### Epic adapter

- parallel eligibility の readiness/dependency/conflict verdict
- approved issue plan と isolated branch/worktree/session の対応付け
- pinned starting point の確認
- actual issue commit range、changed paths、semantic/resource assumptions、
  target ancestry の integration 直前再検証
- issue unit の allocation、wait、completion/blocker return の routing
- `integration_branch` への single-writer serialized integration
- required issue/task commit の reachability 確認、combined verification、
  canonical whole-branch review への routing

adapter は issue code を修正せず、review finding を再解釈せず、SDD の task
loop を所有しない。

### Issue controller/session

- 自 unit にだけ write する
- 自 issue の approved plan に対して canonical SDD を sequential に実行する
- completion または blocker を adapter に短く返す
- sibling issue、planning worktree、final integration target を直接変更しない

## Startup and First-Write Gate

### 1. Read-only start

同じ chat は任意の checked-out branch から開始できる。gate 完了前に許される
repository 操作は discovery、applicable instruction の読取り、Git/worktree
identity と original checkout baseline の read-only inspection に限る。

開始時に少なくとも次を比較可能な形で把握する。

- original checkout の canonical path
- `starting_branch`
- immutable な `starting_head_sha`
- starting status。既存の staged、unstaged、untracked state を区別できること
- Git common directory と現在登録されている linked worktree
- Epic identity と、対象 planning branch/path

detached HEAD では valid な `starting_branch` を capture できないため、
unsupported として fail closed とし、durable task write を行わない。Human
target selection を同じ run の compatibility path として提供せず、repository
default branch を推定して補完しない。

original checkout の uncommitted content は planning branch の source に
含めない。task がその content を必要とする場合、copy、stash、commit を
controller が代行せず、Human が source-of-truth を解決するまで fail closed
する。

### 2. Allocate or reuse

Planning Controller は repository の native worktree mechanism を優先し、
利用できない場合だけ Git worktree operation を用いて、一つの Epic planning
linked worktree を allocate または reuse する。

新しい planning branch/worktree は必ず captured `starting_head_sha` から
作成する。default branch head、allocation 時点で進んだ `starting_branch`
head、または別の inferred commit を base にしない。planning branch の
starting commit が captured SHA と一致しなければ write 前に停止する。

lock-free ownership proof は次に限定する。

1. 対象 branch/path が未登録であることを確認した controller が atomic に
   allocation を成功させた場合、その continuing controller/chat が owner に
   なる。
2. approved plan 前に reuse を自動許可できるのは、同じ continuing
   controller/chat が既に bind 済みであり、current Stage Capsule/control
   context の trusted tuple と current Git/worktree facts が同じ
   `integration_branch`、path、starting SHA、current bound state を示す場合
   だけである。
3. 独立 chat が同じ Epic worktree を発見した場合、clean であっても ownership
   は ambiguous として停止する。
4. planning worktree の `HEAD`、index、tracked、untracked state に trusted
   Stage Capsule tuple または、plan transfer 後の canonical progress ledger
   へ帰属できない差分が一つでもあれば、stale/foreign state として停止する。

二つの allocator が同じ Epic ID を選んだ場合、一方の atomic allocation
だけが成功できる。敗者は既存 worktree へ attach せず停止する。repository
に lease/lock contract がないため、上記以外の inference で active writer
不在を証明したことにしない。

allocation 時に変更してよいのは、linked worktree の登録や branch ref など、
worktree allocation に必要な shared Git metadata だけである。original
checkout の checkout、switch、reset、stash、clean、add、commit、および
content write は禁止する。

### 3. Hold and transfer the binding tuple

approved implementation plan が存在する前は、original-checkout binding tuple
を既存の Planning Controller Stage Capsule/control context だけに保持する。
pre-plan workspace を予約せず、repo-local compatibility bridge、runtime
snapshot、reservation ledger、scheduler、resume record を書かない。

Stage Capsule tuple は original checkout の captured HEAD/status と current
binding を比較するための compact control information であり、durable wiki/
task artifact ではない。pre-plan compaction/context loss の後、この current
Stage Capsule から tuple を信頼できなければ `BLOCKED` を返し、Human restart/
confirmation を要求する。Git current state や会話断片から tuple を再構成・
推測してはならない。

Human-approved implementation plan が canonical Superpowers SDD に入るとき、
ordinary plan-owned workspace/progress ledger が canonical flow によって通常
作成される。その時点で初めて、trusted Stage Capsule tuple を同 ledger の
recovery context へ transfer する。adapter や repository wrapper は plan
workspace を先行作成せず、独自 schema/record を追加しない。transfer 後の
compaction/recovery は canonical Superpowers ledger contract に従う。

### 4. Prove preservation and binding

最初の writable worker dispatch または controller write より前に、次をすべて
証明する。

1. Epic planning worktree が意図した Git common directory、branch、path に
   登録されている。
2. planning branch の creation base が captured `starting_head_sha`
   である。
3. original checkout の branch/HEAD/status が、利用可能な captured Stage
   Capsule tuple、または plan transfer 後の canonical progress ledger tuple
   と一致する。
4. controller が以後使う repository root と CWD が planning worktree に
   解決される。
5. 最初の transient Research Report を含む全 writable artifact path が
   planning worktree 配下に解決される。
6. worker invocation が同じ bound repository root、CWD、writable paths を
   受け取る。
7. original checkout path が writable root、fallback root、worker CWD、
   artifact destination のいずれにも残っていない。

証明できない項目が一つでもあれば、content/artifact write を開始せず停止する。

### 5. Maintain the binding

planning phase の Research、Spec Synthesis、Spec Review、Plan Authoring、
Gate artifacts、wiki sync は同じ Epic planning worktree を再利用する。
worker を fresh context で dispatch することは、filesystem binding の証明を
代替しない。各 writable handoff で bound root/CWD/path を維持する。

Original checkout は必要な read-only comparison の source にはできるが、
write destination や fallback にはしない。同じ chat を継続することと、
repository root/CWD を planning worktree へ bind することは両立し、native
self-handoff capability の存在を前提にしない。

## Path Migration Contract

### Planning phase

- generic な `repository root` は Epic planning worktree root に置き換える
- controller command の CWD は Epic planning worktree に置く
- relative writable path は planning worktree root を基準に解決する
- absolute writable path は planning worktree 内に解決される場合だけ許可する
- worker が返す artifact path は実際の解決先を再確認してから受理する
- original checkout を指す stale path を検出したら write 前に拒否する

### Issue execution phase

parallel mode で allocation された issue controller では、repository root、
CWD、SDD artifact workspace、全 writable path をその issue worktree に
bind する。planning worktree や sibling issue worktree を writable path に
含めない。各 issue worktree に writer は一つだけとする。

sequential mode でも、original checkout を execution fallback にしては
ならない。repository policy に沿う isolated execution location を使う。

### Integration phase

integration writer だけが `integration_branch` の worktree に write できる。
issue controller は commit/result を返すだけで、integration target を直接
変更しない。integration target の root/CWD/write paths も original checkout
ではないことを証明する。`integration_branch` は Epic planning branch と
final PR head を兼ね、`starting_branch` は exclusively PR base とする。この
二つを同一 branch として扱ったり、別 branch に silently retarget したり
しない。

## Parallel Issue Flow

### 1. Opt-in

default は sequential execution とする。parallel issue flow は、Human が
対象 Epic と issue set を明示的に opt in し、各 issue plan を承認した場合
だけ開始する。

### 2. Eligibility

adapter は active issue set ごとに、少なくとも次を確認する。

- issue 間に未解決の dependency edge がない
- expected write set に overlap がない
- API、generated artifact、schema/migration、test fixture、shared external
  service/resource に競合がない
- pinned starting points と integration assumptions が相互に矛盾しない
- integration decision が worker に委ねられていない
- issue ごとに独立した branch/worktree/session/plan/artifact workspace を
  allocate できる

path が disjoint でも semantic dependency や shared resource conflict が
あれば eligible ではない。情報不足、unknown overlap、unknown dependency、
unknown resource ownership は「安全」と推定せず、sequential execution または
Human decision に戻す。

### 3. Allocation and execution

eligible な各 issue に一つの issue execution unit を割り当てる。同じ plan、
branch、worktree、ledger、`HEAD` に二つの controller/implementer を割り当て
ない。

各 issue controller は canonical Superpowers SDD を変更せずに呼び出し、
その task/review/fix loop を sequential に完了する。generic parallel dispatch
を issue 内の concurrent implementation に使用しない。adapter は issue
unit の進行を待ち、completion または blocker return を受け取るが、内部 task
を schedule しない。

### 4. Result routing

各 issue result は少なくとも、対象 issue/approved plan を一意に識別でき、
approved pinned base、issue tip、verification/review の成否、未解消 blocker
を adapter が判断できる形で返す。さらに adapter は、既存 Superpowers
progress ledger と Git history から、その issue の全 SDD task commit set、
actual commit range、actual changed paths を導出する。新しい event schema
や runtime ledger は要求しない。既存 Superpowers の成果物と Git の
observable state を authoritative evidence として扱う。

issue を integration-ready にする直前に、adapter は actual commit range と
changed paths を全 sibling result と比較し、declared dependency、semantic
assumption、shared mutable resource、pinned-base ancestry を再検証する。
expected write set と実結果が異なる場合は実結果を優先する。新しい overlap、
dependency、resource conflict、ancestry ambiguity、または unknown があれば、
Git が clean merge できる場合でも integration-ready にせず、sequential
handling または Human decision に戻す。

blocked、未 review、全 task commit set を一意に確定できない、または一つでも
task commit が issue tip から reachable でない issue は integration-ready
にしない。squash や selected cherry-pick により original task commit の
reachability が失われる result は受理しない。

## Serialized Integration

1. 最初の integration と各 subsequent integration の直前に、
   `starting_branch` の current target head を取得し、captured
   `starting_head_sha` と比較する。
2. target head が captured SHA と同じなら、その ancestry を基準にする。
   target head が advanced している場合、branch 名は変更せず、current target
   head に対して全 issue の ancestry、actual overlap、dependency/resource
   assumptions、integration conflict を再計算する。non-descendant rewrite
   または material divergence があれば fail closed して Human に返す。
   material divergence がなくても current PR base head を
   `integration_branch` ancestry に反映した後、combined verification を
   fresh に行う。PR base 名は `starting_branch` のままとし、別 branch へ
   silently retarget してはならない。
3. 各 integration の直前に、対象 issue の actual commit range/changed paths
   を、current target の starting SHA 以後の変更、既に integrated な sibling、
   まだ pending な sibling と再比較し、semantic/resource assumptions と
   pinned-base ancestry を再検証する。clean textual merge は eligibility の
   代替にならない。
4. adapter は ready な issue result を Human-approved constraints と再検証済み
   dependency order に従って、一つずつ `integration_branch` へ取り込む。
5. integration target の writer は常に一つとし、複数 issue controller に
   concurrent write を許さない。
6. conflict または semantic integration choice が発生したら自動推測せず、
   integration を停止して sequential resolution または Human decision に
   route する。
7. 全 required issue の integration 後、existing Superpowers ledger と Git
   history が示す全 issue/task commit を列挙し、各 commit が
   `integration_branch` から reachable であることを一件ずつ executable
   ancestry check で確認する。
   issue tip だけの確認では不十分とし、reachability を失う squash/rewrite は
   completion 条件を満たさない。
8. integrated state に対して fresh combined verification を実行する。
9. canonical Superpowers whole-branch review を、`starting_branch` base と
   `integration_branch` head の net
   range に対して一度 invoke する。finding があれば adapter 独自 loop を
   開かず、canonical contract の one fixer、exactly one scoped re-review、
   adjudication/stop flow にそのまま従う。fix 後の fresh combined
   verification は行うが、二つ目の fix wave や repeated whole-branch review
   を開始しない。
10. 全 required issue/task commit、combined verification、canonical
   whole-branch review、original-checkout preservation が揃うまで
   `LOCAL_COMPLETE` または同等の completion を返さない。

### Publication boundary

remote publication は integration/completion とは別の明示 authorization を
必要とする。publication 時にも remote の `starting_branch` が valid な PR
base であることと、その current head を確認する。PR head は
`integration_branch` とし、base/head roles を入れ替えない。

remote `starting_branch` が存在しない、保護/権限/policy 上 PR base として
無効、またはその head drift が material divergence を生む場合、default
branch や別 branch を推定せず Human resolution を要求する。Human が target
branch 自体の変更を望む場合、それは silent retarget ではなく、新しい
authoritative branch/SHA pair に対する明示的な再 baseline と integration/
verification/review gate の再実行を必要とする。authorization なしに push、
PR creation、その他 remote mutation を行わない。

## Failure Handling

### Allocation or reuse failure

branch/path collision、ambiguous existing worktree、native mechanism failure、
Git worktree creation failure、ownership ambiguity があれば、最初の
content/artifact write 前に停止する。original checkout で作業を続行しない。
独立 chat が existing same-Epic worktree を発見した場合や、recovery map に
帰属できない clean/dirty state がある場合も ambiguity とする。

### Binding failure

repository root、CWD、artifact path の一つでも authorized worktree への解決を
証明できない、または original checkout への stale reference が残る場合、
writable action と worker dispatch を拒否する。

### Original checkout drift

starting baseline と branch、HEAD、index、tracked files、dirty state が一致
しなくなった場合、原因を推測して修復しない。以後の write/integration を
停止し、差分を保持して Human に返す。自動 reset、checkout、stash、clean は
行わない。

### Concurrent writer risk

same-Epic planning worktree または issue worktree に別 writer が存在する可能性
を排除できない場合、attach/fan-out を行わない。lock service が存在するとは
仮定せず、sequential execution または Human decision に戻す。

### Target branch drift

current `starting_branch` head が captured `starting_head_sha` から advanced
していれば、同じ branch の current head に対して ancestry、actual overlap、
dependency/resource assumptions、conflict、combined verification を再計算
する。non-descendant rewrite、material semantic divergence、または安全性の
unknown があれば停止する。branch 名を default/別 target に変えず、Human
resolution を要求する。

### Issue failure

issue unit の test/review/blocker failure はその worktree に隔離し、未完成の
result を final branch に統合しない。adapter は issue code を修復せず、
canonical SDD の retry/recovery または Human decision に route する。

### Integration failure

merge/cherry-pick 相当の具体的 integration operation が conflict を返した場合、
single integration writer のまま停止する。競合解消が material design choice
を伴う場合は Human に返す。partial integrated state を completion としない。

### Combined gate failure

per-issue green でも combined verification または whole-branch review が
fail した場合、Epic は incomplete のままとする。whole-branch finding は
canonical Superpowers contract の one fixer、exactly one scoped re-review、
adjudication/stop flow に渡す。adapter は repeated review/fix loop を作らない。
fix 後の fresh combined verification は許可するが、canonical contract が
許可しない second fix wave や second full review は実行しない。

## Recovery

1. approved plan 前の compaction/context loss では、current Planning
   Controller Stage Capsule/control context に trusted binding tuple が残る
   場合だけ継続する。残らない、欠落している、または trust できない場合は
   `BLOCKED` を返し、Human restart/confirmation を要求する。
2. pre-plan tuple を Git current state、worktree registration、会話断片から
   reconstruct/guess しない。repo-local resume record や compatibility bridge
   を後付けしない。
3. approved plan が canonical Superpowers SDD に入った後は、通常作成された
   plan-owned workspace/progress ledger に transfer 済みの tuple と Git の
   observable worktree/branch/HEAD/status を比較する。
4. original checkout の HEAD/status preservation は、利用可能な captured
   Stage Capsule tuple、または plan transfer 後の canonical ledger tuple と
   比較する。どちらも trusted でなければ `BLOCKED` とする。
5. planning worktree を reuse できるのは同じ continuing controller/chat
   だけで、pre-plan なら trusted Stage Capsule tuple、post-transfer なら
   canonical ledger tuple が同じ `integration_branch`、path、starting SHA、
   bound state を示し、current state と一致する場合に限る。independent chat
   は同じ Git state を見ても自動 attach できない。
6. issue worktree は canonical Superpowers recovery contract が同じ
   plan/controller continuation と state attribution を証明できる場合だけ
   reuse する。
7. allocation が shared Git metadata を部分的に変更した場合、まず original
   checkout が不変であることと、変更対象が今回新規に作った registration
   だけであることを確認する。
8. cleanup が必要でも、対象と ownership を一意に証明できない限り自動削除
   しない。既存 worktree、branch、user changes を推測で消さない。
9. interrupted issue は同じ plan/worktree/ledger に second controller を
   concurrent attach せず、canonical Superpowers recovery contract または
   Human direction に従う。
10. recovery のために pre-plan workspace reservation、独自 scheduler、
    lease database、event log、runtime snapshot、resume record を追加しない。

## Test Requirements

### First-write and preservation

temporary repository fixture または同等の isolated test で、次を検証する。

1. clean default-branch checkout から planning worktree を作成し、最初の
   Research Report が planning worktree にだけ作成される。
2. non-default `starting_branch` から開始したとき、その chat-start
   `starting_head_sha` から planning branch/worktree が作られ、default
   branch head を base にしない。
3. detached HEAD は unsupported として durable write 前に fail closed し、
   target branch selection や default-branch inference へ fallback しない。
4. task-relevant な uncommitted original content が必要な case は自動 copy/
   stash/commit をせず fail closed する。
5. original checkout に staged、unstaged、untracked state がある場合、その
   state を byte-for-byte 相当で保持し、planning write を分離できる。
6. 一つの continuing controller/chat は、pre-plan では trusted Stage
   Capsule tuple、post-transfer では canonical plan ledger tuple と current
   state が一致する既存 Epic planning worktree を再利用できる。
7. 二つの chats/allocators が同じ Epic ID を同時選択した場合、一つだけが
   atomic allocation に成功し、他方は既存 worktree へ attach せず停止する。
8. independently discovered clean worktree、stale dirty worktree、trusted
   tuple に帰属しない HEAD/index/tracked/untracked state を fail closed に
   する。
9. branch collision、path collision、ambiguous registration、別 writer の
   可能性がある reuse を fail closed にする。
10. allocation failure 時に content/artifact write がゼロで、original
   checkout の HEAD/index/tracked files/status が不変である。
11. worktree allocation に必要な shared Git metadata 変更だけを許し、
   original checkout の switch/reset/stash/clean/add/commit を行わない。
12. relative/absolute/stale path を含む root/CWD/artifact path binding を検査し、
   planning worktree 外へ解決される write を拒否する。
13. Research、spec、review、plan、wiki sync の全 path が同じ planning
   worktree に留まる。
14. fresh conversational context が path binding の代替にならず、worker
    invocation ごとに bound paths が渡る。
15. approved plan 前は binding tuple が Stage Capsule/control context だけに
    存在し、repo-local reservation、snapshot、resume record が作られない。
16. approved plan が canonical Superpowers SDD に入る通常時に、tuple が
    ordinary plan-owned workspace/progress ledger へ transfer される。
17. pre-plan compaction fixture で trusted Stage Capsule tuple が残れば継続し、
    context loss で trust できなければ `BLOCKED` と Human restart/confirmation
    を返す。Git state から reconstruct しない。
18. post-transfer compaction/restart fixture は canonical Superpowers ledger
    から original checkout HEAD/status と binding を再証明する。

### Sequential SDD preservation

1. 一 issue 内で implementer が複数同時に起動されない。
2. task review/fix が完了する前に次 task へ進まない。
3. adapter が task brief、review finding、ledger、fix loop を再実装しない。
4. existing Superpowers SDD tests と repository skill-shape tests を維持し、
   contract surface を意図的に変更する場合は対応 test を明示的に更新する。
5. integrated final review が canonical whole-branch review を一度 invoke し、
   finding 時は one fixer、exactly one scoped re-review、adjudication/stop
   flow に従い、second fix wave/repeated full review を作らない。

### Parallel issue adapter

1. opt-in と Human-approved issue plan がない場合は sequential のままになる。
2. explicit dependency、expected overlap、shared resource conflict、
   unknown conflict の各 case が fan-out されず、sequential/Human route に
   戻る。
3. eligible な二つ以上の issue が、それぞれ異なる
   branch/worktree/session/plan/artifact workspace を持つ。
4. 同じ worktree、branch、plan、ledger、`HEAD` に concurrent writer を
   割り当てない。
5. issue completion/blocker を adapter が route でき、blocked result を
   integration-ready にしない。
6. initially independent な issues が後から同じ file を変更した case を
   actual changed-path comparison で検出し、clean textual merge でも
   integration-ready にしない。
7. file-disjoint でも actual semantic/resource assumption が衝突した case を
   integration 前の再検証で停止する。
8. issue B が issue A integration 前の base に基づく case で、B の actual
   ancestry/dependency を current target と A result に対して再検証し、
   unknown/material dependency を sequential/Human route に戻す。
9. integration が一つずつ行われ、integration target に writer が一人だけ
   である。
10. existing ledger/Git history から全 issue の全 SDD task commit set を導出
    し、一つでも `integration_branch` から reachable でなければ gate が
    fail する。
    issue tip だけを含む case と task commit を落とす squash/cherry-pick case
    を negative test に含める。
11. integration conflict が single writer を停止し、partial state を
    completion としない。
12. `starting_branch` head が unchanged、descendant advance、
    non-descendant rewrite の各 case を検証する。advance 時は actual
    overlap/ancestry/resource/conflict を current target に対して再計算し、
    material divergence を fail closed にする。
13. per-issue verification が green でも combined verification を必ず fresh に
   実行する。
14. combined state に canonical whole-branch review とその既存 scoped
    re-review contract を適用し、material finding が残る間は completion を
    返さない。
15. publication 未承認では remote mutation を行わず、remote
    `starting_branch` が valid PR base でない case は別 branch を推定せず
    Human resolution を要求する。
16. parallel flow の完了後も original checkout が starting
    branch/HEAD/index/tracked files/status と一致する。

## Acceptance Criteria

1. task は any named-branch original checkout から同じ chat で開始できるが、
   gate 前は read-only である。detached HEAD は unsupported として durable
   write 前に fail closed する。
2. 最初の content/artifact write より前に、Epic planning worktree が
   allocate/reuse される。
3. new `integration_branch`/Epic planning worktree は captured
   `starting_head_sha` から作られる。eventual PR base は
   `starting_branch`、PR head は `integration_branch` と完全一致する。
4. planning repository root、CWD、全 writable artifact path が同 worktree に
   bind され、実際の解決先を証明できる。
5. original checkout は starting branch、HEAD、index、tracked files、dirty
   state を保ち、task 中に一度も write fallback として使われない。
6. allocation による変更は必要な shared Git metadata に限定される。
7. allocation、reuse、binding、writer ownership の証明に失敗すれば、最初の
   repository write 前に停止する。
8. same-Epic reuse は atomic allocator の continuing controller/chat に
   限定され、pre-plan は trusted Stage Capsule tuple、post-transfer は
   canonical plan ledger tuple で証明する。independent chat、stale dirty
   state、unattributable state は fail closed する。
9. approved plan 前は compact binding tuple を既存 Stage Capsule/control
   context だけに保持し、plan が canonical SDD に入る通常時に ordinary
   plan-owned workspace/progress ledger へ transfer する。pre-plan
   reservation/snapshot/resume record は作らない。
10. pre-plan compaction/context loss 後に Stage Capsule tuple を trust
    できなければ `BLOCKED` と Human restart/confirmation を返し、reconstruct
    または guess しない。
11. planning gates と documentation sync は同じ Epic planning worktree を
   再利用する。
12. parallel mode は explicit opt-in で、one approved issue plan per isolated
   branch/worktree/session を満たす場合だけ使用できる。
13. dependency、write overlap、shared mutable resource、integration assumption
   のいずれかが unknown または conflicting なら、sequential/Human route に
   fail closed する。
14. eligibility は expected writes だけでなく、integration-ready 前と各
    serialized integration 直前に actual commit ranges/changed paths、
    semantic/resources、pinned ancestry を current target と sibling results
    に対して再検証する。
15. 各 issue 内の canonical Superpowers SDD は unchanged かつ sequential
    であり、concurrent writer はどの worktree にも存在しない。
16. adapter の責務は readiness/dependency/conflict verdict、
    allocation/wait/result routing、serialized integration に限定される。
17. `integration_branch` は existing Superpowers ledger/Git history が示す
    全 required issue/task commit を一件ずつ reachable な形で含む。
18. `integration_branch` は fresh combined verification を通過し、canonical
    whole-branch review の one fixer / exactly one scoped re-review /
    adjudication-stop contract を満たす。adapter は追加 review loop を作らない。
19. `starting_branch` の current head が captured SHA から advanced した場合、
    同じ branch に対して ancestry/conflict/actual overlap/resource assumptions
    と combined verification を再計算し、material divergence を fail closed
    にする。別 branch へ silently retarget しない。
20. completion 時に original checkout が captured tuple の
    HEAD/branch/status と一致
    し、pre-existing changes が保持される。
21. remote publication は別途明示 authorization を必要とし、publication
    時に `starting_branch` が valid remote PR base でなければ Human
    resolution を要求する。
22. scheduler、lock service、event schema、runtime state、pre-plan
    reservation/resume record、独自 SDD
    methodology が追加されない。

## Migration

### Contract migration

1. `sdd-implementation` entrypoint の最初の route に read-only startup と
   first-write worktree gate を置く。
2. chat start で `starting_branch` / `starting_head_sha` を capture し、
   `integration_branch`/planning branch を同 SHA から作成する contract を
   置く。detached HEAD は unsupported、task-relevant uncommitted content は
   Human resolution まで fail closed にする。
3. planning context contract で、session continuity と checkout identity と
   conversational context isolation を分離し、root/CWD/writable path binding
   を必須にする。
4. approved plan 前は compact binding tuple を既存 Planning Controller
   Stage Capsule/control context だけに保持し、repo-local pre-plan workspace
   reservation/compatibility bridge/resume record を作らない。
5. Research stage と writable worker prompts で、generic repository root を
   resolved planning worktree root に置き換え、最初の transient report から
   containment を要求する。
6. approved plan が canonical Superpowers SDD に入る通常時にだけ、trusted
   tuple を ordinary plan-owned workspace/progress ledger へ transfer する。
7. same-Epic reuse は atomic allocator の continuing chat に限定し、pre-plan
   は trusted Stage Capsule tuple、post-transfer は canonical ledger tuple
   で証明する。
8. implementation phase への handoff で、sequential route と opt-in Epic
   adapter route を明示する。どちらも original checkout fallback を禁止する。
9. adapter contract は Superpowers SDD より上位の薄い repository-specific
   boundary に限定し、actual-result revalidation、every-task-commit
   reachability、serialized integration だけを追加して既存 SDD authority を
   参照する。
10. final review は canonical Superpowers whole-branch review とその one-fixer/
   one-scoped-re-review contract を invoke し、複製しない。
11. publication contract で PR base を `starting_branch`、PR head を
    `integration_branch` に固定し、remote mutation を別 authorization とする。

### Executable coverage migration

1. current pre-implementation context tests に first-write、any-branch start、
   captured-SHA base、detached unconditional failure、Stage Capsule-only
   pre-plan control、lock-free reuse、pre/post-transfer compaction、path
   binding、original preservation の assertions を追加する。
2. temporary Git repository を使う focused tests が必要な場合も、永続
   scheduler/runtime を導入せず、worktree registration と filesystem
   containment を直接検証する。
3. issue adapter coverage に eligibility fail-closed、actual changed-path/
   resource/ancestry revalidation、isolated units、serialized integration、
   every-task-commit containment、target drift、canonical combined gate を
   追加する。
4. exact skill shape assertion を変更する場合は、必要最小の surface に限り、
   test contract を意図的に更新する。helper、scripts directory、追加
   reference は証明上必要でない限り増やさない。

### Rollout

1. contract tests を先に更新し、original-checkout mutation と first-write
   leakage を再現できる failure cases を固定する。
2. planning gate と path propagation を実装し、sequential SDD route を先に
   green にする。
3. parallel adapter を opt-in のまま追加し、sequential fallback と Human
   route を先に検証する。
4. combined verification、whole-branch review、original preservation の
   closeout gate を end-to-end で検証する。
5. Human approval 後にのみ canonical wiki/index/log sync と implementation
   executionへ進む。

## Stop Conditions

次のいずれかで、該当 phase の write または進行を停止する。

- Epic identity、planning branch/path、original checkout identity が一意でない
- named `starting_branch` / immutable `starting_head_sha` pair を capture
  できない
- detached HEAD で開始した
- task-relevant uncommitted original content の source-of-truth が未解決
- planning worktree の create/reuse に失敗した
- existing worktree の ownership または single-writer condition を証明できない
- existing planning worktree が independent chat により発見された、または
  HEAD/index/tracked/untracked state を trusted Stage Capsule/plan ledger
  tuple に帰属できない
- approved plan 前の compaction/context loss 後に current Stage Capsule の
  binding tuple を trust できない
- plan transfer 後の canonical Superpowers ledger tuple が欠落、読取不能、
  不一致
- root、CWD、writable artifact path の containment を証明できない
- original checkout の branch、HEAD、index、tracked files、status が drift した
- worker が original checkout または sibling worktree への write を要求した
- issue plan が Human-approved でない
- parallel opt-in がない
- dependency、overlap、shared resource、pinned base、integration assumption が
  unknown または conflicting
- 一つの plan/branch/worktree/ledger/`HEAD` に複数 writer が必要になる
- issue result の commit、verification、review、blocker status を確定できない
- actual changed paths、semantic/resource assumptions、pinned ancestry の
  integration 直前再検証が conflict または unknown を返した
- serialized integration が conflict または material design choice を生んだ
- current `starting_branch` head の drift が non-descendant rewrite または
  material divergence を生んだ
- `integration_branch` に required issue/task commit が一つでも reachable
  でない
- combined verification または whole-branch review に material failure が残る
- remote publication の authorization がない、または `starting_branch` が
  valid remote PR base でない
- destructive recovery または original checkout mutation なしに継続できない

停止時は original checkout へ fallback せず、既存 state を保持し、解決に必要な
最小の evidence と Human decision request を返す。

## Confirmed Decisions

1. 同じ chat は任意の branch 上の original checkout から read-only で開始する。
2. chat start で `starting_branch` とその immutable `starting_head_sha` を
   capture する。
3. planning branch/worktree は `starting_head_sha` から作成する。
4. eventual PR base branch は repository default や inferred target ではなく、
   captured `starting_branch` とする。
5. Epic planning branch は `integration_branch` と呼び、serialized
   integration の destination かつ eventual PR head とする。
6. detached HEAD は valid starting branch を持たないため unsupported とし、
   branch selection fallback なしで durable task write 前に fail closed する。
7. 最初の content/artifact write より前に Epic planning worktree を allocate
   または reuse する。
8. allocation 後は planning の全 repository root、CWD、write path をその
   worktree に bind し、original checkout を変更しない。
9. worktree allocation は必要な shared Git metadata を変更できるが、original
   checkout の HEAD、index、tracked files を変更してはならない。
10. binding と original-checkout preservation を証明できなければ fail closed
   とし、in-place fallback を行わない。
11. approved plan 前は compact original-checkout binding tuple を既存
    Planning Controller Stage Capsule/control context だけに保持し、custom
    runtime snapshot、repo-local reservation/compatibility bridge、scheduler、
    resume record を作らない。
12. approved plan が canonical Superpowers SDD に入る通常時に、trusted tuple
    を ordinary plan-owned workspace/progress ledger へ transfer する。
13. pre-plan compaction/context loss 後に current Stage Capsule tuple を trust
    できなければ `BLOCKED` と Human restart/confirmation を返し、reconstruct
    または guess しない。
14. same-Epic reuse ownership は新しい lock service ではなく、atomic
    allocator の continuing chat に限定する。pre-plan は trusted Stage
    Capsule tuple、post-transfer は canonical plan ledger tuple で再証明し、
    independent chat または unattributable state は停止する。
15. 同一 Epic の parallel issues は、thin な opt-in Epic adapter として scope
   に含める。
16. concurrent mutation unit は one Human-approved issue plan per isolated
   branch/worktree/session とする。
17. canonical Superpowers SDD は変更せず、各 issue 内で sequential に実行する。
18. adapter は readiness/dependency/conflict verdict、allocation/wait/result
   routing、serialized single-writer integration だけを所有する。
19. どの worktree にも concurrent writer を許さない。
20. unknown overlap、dependency、resource conflict は sequential execution
    または Human decision に戻す。
21. actual issue overlap、resource conflicts、pinned ancestry は
    integration-ready 前と各 serialized integration 直前に current target と
    sibling results に対して再検証する。
22. `integration_branch` は existing Superpowers ledger/Git history が示す
    全 required issue/task commit を reachable な形で含まなければならない。
23. combined final review は canonical Superpowers whole-branch review と
    その one fixer、exactly one scoped re-review、adjudication/stop flow を
    invoke し、duplicate review loop を作らない。
24. `starting_branch` head が captured SHA から advanced したら、同じ branch
    に対して ancestry/conflict/combined verification を再計算し、material
    divergence を fail closed にする。silently retarget しない。
25. completion 時、original checkout の HEAD/status は利用可能な captured
    Stage Capsule tuple、または transfer 後の canonical plan ledger tuple と
    一致しなければならない。
26. remote publication は separately authorized とし、publication 時に
    `starting_branch` が valid remote PR base でなければ Human resolution を
    要求する。
27. PR base は exclusively `starting_branch`、PR head は
    `integration_branch` とする。
28. scheduler、lock service、event schema、runtime state を新設しない。

## Open Decisions

なし。
