---
title: SDD portable validation と責務単純化仕様
date: 2026-08-14
status: accepted
review_state: approved
approved_on: 2026-08-14
approval_snapshot_sha256: 1a8d209ca01e73828043b19c8bfe22d35bd1afa64603add1b7a180a20487285c
amended_on: 2026-08-14
amendment_authority: human-directed-origin-main-incorporation
amendment_baseline_sha: 4d67bed6d297ba4e9a0f44559d3ca45c9a035976
implementation_state: closeout-candidate-final-review-pending
north_star_identity: sdd-portable-validation-simplification#目標@2026-08-14
tags:
  - sdd-implementation
  - skill-portability
  - validation
  - specification
aliases:
  - SDD Portable Validation Simplification
---

# SDD portable validation と責務単純化仕様

> [!success] Human-approved Written Spec
> Human は2026-08-14に本仕様全体をWritten Specとして承認し、その後current `origin/main`を取り込んで重複を整合した上で修正を継続するbounded amendmentを直接指示した。statusは`accepted`、review stateは`approved`のままとし、portable direct-Git goalと承認済みauthorityは変更しない。remote actionは別途明示承認を要する。

## 問題

現行の `sdd-implementation` は、install 単位に含まれない repository-root validator を必須実行し、その validator と package 内 test はこの source repository 固有の Git 履歴、hash、canonical plan、絶対 path に依存している。このため source checkout の test が成功しても、同じ skill を install した別 repository では必須 validation と package test を完結できない。

同時に、次の責務が重複または曖昧になっている。

- portable skill と repository owner の双方が repository 固有 policy を所有している。
- Superpowers が所有する generic lifecycle / worktree 手法を SDD が再定義している。
- validation の実行点が「すべての repository validation gate」とだけ記され、実際の引数と時点が一意でない。
- parallel issue execution について、Human opt-in / issue-plan approval を要求する仕様と、Written Spec 後は agent / repository が選ぶ仕様が併存している。
- package に必要な resource、runtime capability、isolated install での自己完結性が一つの closure として検証されていない。

## 目標

1. install 済み `sdd-implementation` が、この source repository を参照せず、明示された任意の target repository に対して実行可能であること。
2. generic validation を Git の既存 capability で直接実行し、standalone validator を追加せず、repository 固有の Git / migration / CI policy を各 repository owner に戻すこと。
3. SDD を、Superpowers lifecycle と `llm-wiki` を接続する薄い repository-independent composition にすること。
4. 必須 resource と capability、実行点、failure を一意にし、isolated package test と synthetic Git repository で証明すること。
5. Human と agent の authority を、Written Spec と remote action の境界に沿って統一すること。

## 非目標

- repository validation adapter、hook registry、scheduler、永続 state、telemetry、追加 protocol を新設しない。
- portable skill 用の standalone / bundled validator executable を新設しない。
- target repository の branch、worktree、migration、history、CI policy を portable skill に標準化しない。
- Superpowers の generic lifecycle、worktree allocation、TDD、worker dispatch、review、branch finishing の手法を fork または再実装しない。
- current SDD First-Write Worktree Gateのentry、single-writer ownership、containment、zero-write、no-fallback、original-checkout preservationを削除または弱体化しない。
- `keep-implementation-simple`のdependency preflightと、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerの七roleへのbounded適用を削除しない。
- Human-approved Written Spec の内容を agent が拡張したり、未承認の remote action を実行したりしない。
- 過去の migration evidence を削除または改変しない。

## Architecture と ownership seam

### 1. Portable skill package

`skills/sdd-implementation/` は public contract と、それを実行するための package closure を所有する。

- `SKILL.md` は inputs、outputs、required capabilities、composition order、三つの validation 実行点、failure boundary だけを定義する。
- fresh worker / model selection、repository-external handoff、path binding の共通 guard は public contract の一つの runtime capability boundary に集約し、stage reference と worker prompt はその owner を参照して worker 固有 input だけを追加する。
- generic validation は caller が明示した target repository に対する direct Git probe として実行する。実行時 CWD、installed skill の source checkout、親 directory から target を推定しない。
- public contract、package test、fixture は repository 名、canonical wiki page、commit / blob hash、個人の絶対 path、完了済み migration marker を含まない。
- package 内 test は synthetic target repository と package-relative resource だけで完結する。

direct Git probe は package resource を追加しない。required prompt / reference / test resource が package に存在しない、読めない、または package contract と一致しない場合は `broken skill installation` として fail closed にする。これは target repository の deficiency ではない。

### 2. Target repository owner

target repository は `AGENTS.md`、root-owned validator、test、CI など既存の最小 surface で、自身の Git / migration / canonical fixture / branch / worktree policy を所有する。この repository のcurrent authorityは、repository固有policy boundary以後のcurrent index、nominated candidate tree、post-policy new commit、final treeに対するstrict-zero contractとcanonical plan parityである。policy boundaryのcommit identityと到達可能historyの解釈はroot `scripts/` と `.github/` のconcernとし、portable contractまたはpackage testから参照しない。

portable skill は repository-local validator の存在を前提にせず、自動 discovery や adapter seam も追加しない。repository-local rule が Superpowers の generic default より厳しい場合、その override は repository rule にだけ置く。

この source repository では、root `scripts/validate_sdd_transient_artifacts.py` がexplicit repository rootを検証し、current index、nominated candidate tree、repository固有policy boundary以後の全new commit、final treeの各surfaceに`.superpowers/**` entryがzeroであることをfail closedに検証する。ignored・untracked・unstaged・uncommitted scratchは具体的reasonとexact ignore coverageがある場合だけ許容し、staged deletionとpolicy boundaryより前のhistorical ancestor blobはcurrent strict-zero違反がなければ許容する。completed migration markerや過去のexact path / mode / blob / lineageはcurrent validation authorityではなくhistorical evidenceである。root regression test、`.github/workflows/skill-architecture.yml`からのinvocation、それを固定する`scripts/test_skill_ci_workflow.py`は継続必須とする。canonical SDD plan parityはroot-owned fixture / regression testで所有し、同じCIで実行する。

### 3. Superpowers と SDD

Superpowers は generic lifecycle、worktree allocation methodology、planning、TDD、dispatch、review/fix、branch finishing を所有する。SDD は applicable Superpowers skill を呼ぶ順序、SDD固有のrepository-change entryとfirst-write containment、research / Written Spec / knowledge composition、portable validationを所有する。

SDDはgeneric worktree allocation algorithmやhost-specific writable-root mutationを再記述しない。一方、repository changeのfirst entryでdefault checkoutをread-onlyとし、最初のcontent/artifact write前にtask-linked worktreeをcreateまたはverifyし、Git registration、common directory、branch、canonical path、original checkoutとの分離、minted task-owner capabilityのidentityを証明するcontainment contractはSDDが所有する。repository root、CWD、全writable pathをそのowned worktreeへbindし、raw handoffは別のbounded repository-external capabilityへbindする。一つのwritable gateはcomplete data-only planからexactly one absent artifactだけをatomic publishし、commitはverified worktree CWDに固定した別のdata-only native Git planで行う。binding、ownership、capability、permission、allocation、path、original-checkout preservationのいずれかが欠落または不一致ならzero writeで`blocked`を返し、original/current checkout、sibling、fallback root、old loopへ進まない。後続の重複整理はこのobservable contractを一つのownerへ収束できるが、削除または緩和してはならない。

### 4. Keep Implementation Simple

`keep-implementation-simple`は新しいscheduler、adapter、validator、state、またはrole taxonomyではなく、既存SDD lifecycleに対するrequired supporting skillである。dependency preflightでreadable canonical skill pathを一度解決し、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerの七roleへ同じresolved pathを渡し、各roleは作業前に全文を読む。各roleはrequested observable outcome、accepted criteria、applicable repository rules、current evidenceに変更surfaceを対応付け、対応しない追加概念を除外する。pathのdiscovery/read failureはaffected work前にrole / phase、path、underlying errorを示してfail closedにし、ad hoc simplicity protocolやtest-only runtimeへfallbackしない。

## Interface contract

### Inputs

- Human-approved Written Spec、または Written Spec 作成に必要な Human-confirmed decisions。
- caller が明示し、実行時に canonical absolute path へ解決する target repository path。
- installed `sdd-implementation` directory と、そこから相対解決できる required resources。
- target repository が宣言する applicable local instructions と remote-action policy。

### Outputs

- approved scope に対する local implementation / verification result と、変更 file / commit / remaining risk の evidence。
- Human decision が必要な material spec change または remote action の明示的な停止理由。
- package、target、runtime capability、repository policy のどの境界で失敗したかを区別した診断。

### Required capabilities

- installed skill directory から required resource を相対解決できること。
- target repository identity、CWD、write destination を canonical absolute path として検証できること。
- repository-external temporary report を安全に作成し、bounded handoff できること。
- applicable Superpowers / `llm-wiki` / authoring skill を discovery し、その contract に従えること。
- fresh worker dispatch、bounded read/write、result collection ができること。
- target policy が要求する Git / worktree 操作と、選択 workspace への write binding ができること。
- task-owner capability identity、Git worktree registration、original-checkout fingerprint、contained writable path、repository-external handoff pathを検証し、data-only write / commit planをnative runnerへ渡せること。
- canonical `keep-implementation-simple/SKILL.md`をdiscoveryし、七roleがaffected work前に全文を読めること。
- explicit target に対して `rev-parse`、`check-ignore`、`ls-files`、`write-tree`、`ls-tree`、`cat-file`、ancestry verification を実行し、終了状態と出力を判定できること。

capability が存在しない場合、別 runtime 固有機能を推定して代用せず、最初の該当 mutation 前に fail closed にする。

## Concrete control flow

1. **Resolve**: installed skill directory と explicit target repository を別 identity として解決する。required resource closure を確認し、resource 欠落は `broken skill installation`、target 不在・非 repository・authority 不足は target-side failure として分離する。
2. **Load ownership**: target の local instructions を読み、generic lifecycle は Superpowers、repository override は repository owner、knowledge routing は対象 knowledge root に委ねる。SDD 内の重複した worktree / lifecycle 手順は参照しない。
3. **Bind workspace**: original checkoutのcanonical path、starting branch / HEAD / statusをcaptureし、task-linked worktreeとminted owner capabilityをverifyする。repository root、CWD、全durable write pathをowned worktreeへ、raw handoffを別のrepository-external bounded pathへbindする。worker output受入れ前とcommit前にbindingをrevalidateし、安全なbindingまたはoriginal-checkout preservationを証明できなければzero writeで停止する。
4. **Research and spec**: repository-external research report から Written Spec を作成し、material decisions は Human approval に戻す。承認済み Written Spec 内では agent が execution decomposition を行う。Spec / Planの四roleとImplementation / Final Reviewの三roleはresolved KIS skillを読み、approved criterionまたはcurrent evidenceに対応しないsurfaceを増やさない。
5. **Choose execution shape**: dependency と write-conflict の非存在を evidence で確認できる issue だけ parallel eligible とする。unknown な dependency / conflict は sequential execution に落とす。追加の Human execution-method approval または issue-plan approval は要求しない。
6. **Validate at three named mechanical points**: 次節の normative direct-Git gate contract に従う。relevant mutation 後は該当 gate を再実行するが、これ以外の stage transition では generic probe を追加しない。
7. **Implement and review**: TDD、worker review/fix、whole-branch review、branch finishing は applicable Superpowers contract に従う。repository-specific validator / CI は target owner の定義した時点で別途実行する。
8. **Close out**: direct Git probes、target-owned checks、isolated package tests、required repository tests の fresh evidence を集約する。remote action は既存の明示的 authorization がある場合だけ実行する。

### Direct Git normative gate contract

全 gate は共通必須 input として caller が明示した canonical absolute target repository path を使う。`git -C TARGET rev-parse --show-toplevel` の canonical result が TARGET と完全一致し、`--is-inside-work-tree` が true でなければ停止する。全 probe は同じ `git -C TARGET` binding を使い、CWD、installed skill の source checkout、親 directory、別 worktree の index / object database を代用しない。

| Gate | Trigger / invalidation | Mandatory input と direct probe | Pass condition | Block boundary |
|---|---|---|---|---|
| `exceptional-local-scratch-pre-write` | repository-external default を使えない具体的 reason があり、distinct scratch leaf に最初の payload byte を書く直前。target、path、ownership、ignore rule、HEAD、index が変われば次の write 前に再実行する。 | target-relative exact path と non-empty reason。path は `.superpowers/...` 内へ normalize し、absolute、`.` / `..`、symlink escape、既存・foreign・unknown ownership を拒否する。`check-ignore --no-index --quiet -- PATH` が成功し、`ls-files --stage -- PATH` と `ls-tree -r --name-only HEAD -- PATH` が空であることを確認する。 | task/session-bound の新しい leaf が ignored、untracked、unstaged、uncommittedで、target外へescapeせず、external routeでは満たせないreasonが記録される。 | failure / state不明はそのpayload writeだけをblockする。external routeへ戻せなければ当該stageを停止する。 |
| `pre-commit-candidate` | final staging 後、各commit / amend attempt直前。検査後のindex、`.superpowers/**` working-tree state、またはrelevant ignore ruleのmutationで失効し、commit前に再実行する。 | current indexから`git write-tree`でcandidate tree OIDを導出する。nonzeroはunmergedを含むfailureとしてblockする。`ls-tree -r --name-only CANDIDATE -- .superpowers`、`ls-files --stage -- .superpowers`、`ls-files --others --exclude-standard -- .superpowers`が空であることを確認する。 | candidate/indexに`.superpowers/**` entryがなく、unignored working pathもない。ignored・untracked・unstaged・uncommitted scratchと、candidateからentryを除くstaged deletionは許容する。 | failureは当該commit / amendをblockする。修復・restage・working-tree/ignore mutation後は再実行する。 |
| `final-closeout` | 全task commitとcloseout write後、completion verdict直前。検査後のHEAD、index、`.superpowers/**` working-tree state、relevant ignore rule、またはtrusted baseline bindingのmutationで失効する。 | pre-commit probeをcurrent indexへ再実行する。`HEAD^{tree}`を導出し、同treeの`.superpowers/**` entryがzeroであることを確認する。trusted tupleのimmutable `starting_head_sha`をBASELINEとし、BASELINEがcommit objectかつHEADのancestorであることを確認する。`git rev-list BASELINE..HEAD`相当でpost-baseline commit setをGit object graphからfreshに全件導出し、各commit treeの`.superpowers/**` entryがzeroであることを確認する。 | current candidate、HEAD final tree、`BASELINE..HEAD`の全commit treeがzero。ignored・untracked・unstaged・uncommitted local scratchは残ってよく、destructive cleanupを要求しない。 | failure、baseline非ancestor、またはcommit range導出不能はcloseout verdictをblockする。修復mutation後はaffected gateを再実行する。 |

この表だけを generic gate methodology の normative source とする。public `SKILL.md` はdirect Git contractを保持し、prompt / reference / testはgate名と必要inputだけを参照する。exactly-once実行、validator state、証跡cacheを導入せず、relevant mutation後の再実行でfreshnessを保つ。

## Implementation closeout candidate

2026-08-14に、rebound baseline `0ed5f358979ae9281fb7dde8fe47647175720ca8`
からのserialized implementationを現行branch上で再確認した。Task 1
`481d424`、Task 2 `42ce4df`、Task 3 `07a1e8d`、Task 4 `f29c0fd`
はすべてcurrent HEADからreachableで、各taskのindependent reviewは修正後に
open findingなしで完了している。landed ownershipは次の通りである。

- Task 1: explicit targetと三つのdirect Git gate、fresh recomputation、failure taxonomy。
- Task 2: root canonical parityを先にGREENにした後のpackage dependency removal、portable fixture、isolated installed-folder closure。
- Task 3: root parityとisolated closureのCI接続、current strict-zero / `--post-policy-history` / clean-clone / no-`origin/main` contractの維持。
- Task 4: thin composition、single common runtime guard、Authority A、unknown-to-sequential、First-Write fail-closed containment、exact seven-role KIS wiring。

closeout candidate作成前のfresh combined verificationは、package 139 tests、root
scripts 39 tests、First-Write / fail-closed / exact-seven KIS 29 tests、llm-wiki
21 tests、architecture / context / warning-free context report / Skill validatorを成功させた。
scripts suiteはroot canonical parity、current strict-zero regression、CI invocation、reachable
clean clone、`origin/main` ref不在、post-policy add-then-delete、shallow historyの
fail-closed casesを含む。

reviewed implementationとfresh local checksから新しいmaterial riskは検出されていない。
ただし、本更新は`LOCAL_COMPLETE`を宣言しない。knowledge commit後の
final direct-Git gateと、controllerが一度だけdispatchするfresh whole-branch reviewは
pendingである。push、PR、merge、release、live installを含むremote actionは
未実施かつ未承認である。

## Failure handling

| Condition | Owner classification | Required behavior |
|---|---|---|
| required package resource が欠落・読取不能 | skill package | `broken skill installation` として mutation 前に停止する |
| required Git operation が利用不能、nonzero、または状態を一意に判定不能 | runtime / target capability | 影響するscratch write、commit、またはcloseout gateだけをfail closedにする |
| explicit target が不在、非 Git repository、または authority 外 | caller / target | target-side input / authority failure として停止する |
| workspace binding、fresh dispatch、external temporary handoff 等の capability がない | runtime | 該当 mutation 前に不足 capability を示して停止する |
| task-owner identity、worktree登録、bound CWD/path、single writer、original-checkout preservationが欠落または不一致 | SDD first-write containment | writer / downstream runnerを呼ばず、artifact / commitを作らず、四field `blocked` returnで停止する |
| canonical KIS pathのdiscoveryまたは七roleでのfull readが失敗 | supporting skill dependency | affected role / phase、path、underlying errorを示して、そのroleのwork前に停止する |
| repository-local policy check が失敗 | target repository | generic package failure と混同せず、owner surface と evidence を示して停止する |
| parallel independence の evidence が不足 | execution planning | failure にせず sequential execution に切り替える |
| approved Written Spec を変える必要がある | Human authority | material差分を提示し、再承認まで停止する |
| remote action の authorization がない | Human / repository policy | local completion に留め、remote action を実行しない |

途中失敗時は新しい durable runtime state を作らず、既存の Superpowers / repository workflow が定める回復可能な artifact と Git evidence だけを返す。

## Testing strategy

### Portable package tests

- skill folder だけを isolated temporary directory へ copy / install し、source repository とその親を read path に含めず test を実行する。
- isolated synthetic Git repository を explicit target に渡し、normative gate table の各 direct Git probe と positive / negative stateを検証する。ignored scratch、force-add、unmerged index、staged deletion、`BASELINE..HEAD`内のadd-then-delete commit、index / working-tree / ignore mutationによるstale evidence、mutation後の再実行をforward testする。
- prompt、reference、fixture、testの全 mandatory resource が package 内に存在し、skill-relative に解決されることをclosure testで確認する。standalone validator executableは期待しない。
- package test と fixture に repository-specific hash、canonical plan、username / absolute path がないことを regression test で固定する。
- required resource欠落が`broken skill installation`、不正targetまたはGit capability failureがtarget/runtime-side failureとして区別されることを確認する。

### Repository-owned tests

- root `scripts/validate_sdd_transient_artifacts.py`のcurrent strict-zero behaviorを固定する。explicit repository root、current index、nominated candidate tree、repository固有policy boundary以後の到達可能な全new commit、final treeを個別に検証し、markerがnonzero indexをauthorizeしないこと、strict-zero violationを一つのexact diagnostic categoryでfail closedにすること、staged deletionとpre-policy historical ancestor blobを許容することをroot regression testで証明する。repository固有policy-root identityとそのactual parentはroot fixture / validatorだけに留める。
- canonical SDD plan parity を repository-level fixture / regression test へ移し、installed package test からは除外する。移動後も parity coverage を削らない。
- `.github/workflows/skill-architecture.yml` は root validator のpost-policy strict-zero history invocation、対応する root regression tests、canonical-plan parity、isolated package closure test を source checkout CI で実行する。`scripts/test_skill_ci_workflow.py` は`--post-policy-history`を含むinvocation setをcontract testとして固定する。quick shape validation の成功だけを installability evidence にしない。

### Contract and integration tests

- public contract に inputs、outputs、required capabilities、explicit target、三つの execution point が一度だけ定義されていること。
- fresh worker / model selection、repository-external path rejection、binding failure の共通 guard が prompts / references に複製されていないこと。
- public contract が repository 固有 hash / path / migration と generic worktree fallback algorithm を含まないこと。
- parallel eligibility は agent / repository-owned、unknown は sequential、Human approval は Written Spec material change と別途 authorization が必要な remote action に限定されること。
- SDD first entry、owned task-linked worktree、single artifact atomic write、separate commit plan、original-checkout rejection、zero-write / no-fallback behaviorをcurrent fail-closed scenario testsで固定すること。
- KIS dependency preflightと、Spec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerのexact seven-role wiringをcontract testで固定すること。
- repository architecture validator、skill-creator validator、skill tests、root tests、workflow contract tests、`git diff --check` を fresh に実行すること。

## Acceptance criteria

1. isolated install の `sdd-implementation` が source repository への access なしで synthetic target に対する必須 resource resolution、direct Git validation、package tests を完了する。
2. standalone / bundled generic validator executableがportable packageに存在せず、public contractはexplicit target repositoryをcanonical absolute pathへ解決して同じ`git -C TARGET` bindingだけを使う。
3. required package resource欠落はtarget deficiencyではなく`broken skill installation`、Git probeの利用不能は影響するgateのcapability failureとしてmutation前に失敗する。
4. portable `SKILL.md`、prompt、reference、fixture に、この repository 固有の commit / blob hash、canonical wiki path、migration marker、個人の絶対 path が存在しない。
5. current root-owned validator / regression / CI contractは、repository固有policy boundary以後のindex、candidate、全new commit、final treeをstrict-zeroで検証し、completed markerや過去のexact path / mode / blob / lineageをcurrent executable authorityにしない。policy-root identityとそのactual parent、canonical-plan parityはportable packageに存在せず、root ownerに留まる。`.github/workflows/skill-architecture.yml`が`--post-policy-history`を含むcurrent invocationをfresh実行し、`scripts/test_skill_ci_workflow.py`が欠落を失敗にする。
6. mechanical validation pointはnormative gate tableの三つだけである。各gateのmandatory input、direct Git surface、scratch state、positive / negative result、mutation後のevidence invalidationがisolated testで観測でき、exactly-once stateを持たない。
7. package closure test が mandatory resource の欠落、package 外参照、source topology 依存を検出する。
8. SDDのpublic contractはgeneric allocation algorithm / TDD / review / finishingを再定義せずSuperpowers ownershipを参照する一方、repository-change entry、owned worktree binding、single-writer containment、zero-write / no-fallback、original-checkout preservationを一つのSDD-owned First-Write Worktree Gateとして保持する。
9. required runtime capabilities と unavailable 時の pre-mutation stop が contract test で固定される。
10. parallel eligibility の independence evidence、unknown 時の sequential fallback、Human authority boundary が contract test で固定される。
11. source checkout の全 relevant tests、isolated installed-copy tests、repository validators、CI contract tests が fresh run で成功する。
12. implementation diff は既存 owner / surface の修正に限定され、新しい adapter seam、scheduler、state、telemetry、protocol を追加しない。
13. current fail-closed scenario testsが、direct supporting-skill entry、allocation/binding/path/owner/preservation failure、original-checkout commit attemptをmutation前にblockし、exactly one new artifactと別commit planだけを許可する。
14. KIS dependency preflightとexact seven-role wiringがcurrent-tree contractと一致し、各roleのfull-read failureがaffected work前にbounded failureとなる。SPV-4の重複整理はこのwiringまたはFirst-Write Worktree Gateを削除しない。

## Migration と supersession

Human approval 後、実装は次の順序で移行する。

1. public skillにdirect Git gate contractとexplicit target bindingを実装し、standalone validatorを追加せずsynthetic repository testsを先に成立させる。
2. package tests / fixtures から repository-specific canonical plan、history、absolute path を分離し、既存 canonical-plan parity coverage とcurrent strict-zero post-policy regression coverageをroot-owned test / fixtureに置く。移動中もcoverageを削除またはoptional化しない。
3. current root validatorのstrict-zero index / candidate / post-policy-new-commit / final-tree behaviorをrepository-owned surfaceとして維持する。completed markerと過去のexact lineage assertionをcurrent executable authorityへ戻さない。root regression tests、`.github/workflows/skill-architecture.yml` の `--post-policy-history` invocation、`scripts/test_skill_ci_workflow.py` の invocation contract が GREEN になるまでcutoverしない。
4. `SKILL.md`、prompts、references の重複 gate と lifecycle / worktree prose を一つの portable contract へ収束する。ただしSPV-4はSDD-owned First-Write Worktree Gateのobservable behaviorとexact seven-role KIS wiringを削除、optional化、Superpowers generic defaultへ暗黙fallbackしてはならない。
5. isolated package closure と repository full suite の双方が GREEN になってから旧 package-external dependency を除去する。

承認された時点で、本仕様は以下の current conflict に限って後勝ちする。

- `sdd-first-write-worktree-migration-spec.md` の Human opt-in / Human-approved issue-plan 要求は supersede し、Human-approved Written Spec 内の parallel eligibility を agent / repository-owned とする。
- `sdd-plan-ownership-alignment.md` の「Human approval は North Star / Written Spec、issue plan は agent-owned」という authority を維持し、本仕様が parallel fallback を具体化する。
- `sdd-implementation-skill-design.md` の Superpowers ownership / thin integration を維持し、portable package と repository-local override の境界を本仕様で具体化する。
- 本仕様のorigin/main取り込み前bytesにあった`f07aebc` / marker / exact path / mode / blob lineageをcurrent executable root authorityとして維持する要求はsupersedeする。これらはhistorical evidenceとして保持し、current root authorityは取り込み済みstrict-zero post-policy validator / regression / CI behaviorとする。
- 現行 public skill と test に残る package-external validator dependency、重複 lifecycle / gate prose は本仕様の implementation により置換する。ただしcurrent First-Write Worktree Gateとseven-role KIS wiringは置換対象ではなく、deduplication後もbehavioral authorityとして保持する。

過去の仕様、plan、migration evidence は historical record として保持し、current executable instruction としては参照しない。本仕様のHuman approval以後、上記の限定されたconflictでは本仕様をcurrent authorityとする。

## Stop conditions

- Human Written Spec approval 前は implementation、supersession、index / log sync に進まない。
- resolved spec path が planning worktree 外、original checkout、planning sibling、issue siblingへ向く場合は write しない。
- installed package closure、explicit target identity、write authority、required capability のいずれかを証明できなければ、最初の該当 write 前に停止する。
- material scope / architecture / authority の変更が必要なら、spec 差分を Human に戻して再承認を待つ。
- repository-local policy と generic method が両立しなければ、portable skill が override せず repository owner の判断まで停止する。
- SPV-4のdeduplicationがcurrent First-Write Worktree Gateのentry / ownership / containment / zero-write / no-fallback / original-preservation behavior、またはseven-role KIS wiringを削除・弱体化するなら停止する。
- remote push、PR 作成・更新、merge、release、live install は、別途明示された authorization がなければ実行しない。
- fresh isolated package test と repository verification が揃うまで completion を宣言しない。

## Confirmed Decisions

1. install 済み `sdd-implementation` は、この source repository への hidden dependency なしに任意の明示 target repository で実行できる。repository-specific Git / migration / CI policy は各 repository owner が所有する。
2. standalone generic validatorはbundleしない。explicit targetへdirect Git probeを実行し、mechanical gateをexceptional local scratch pre-write、pre-commit candidate、final closeoutに限定する。required package resource欠落とGit capability failureを区別し、isolated package / synthetic repository testsでhidden source dependencyがないことを証明する。source repositoryのcurrent root validator / tests / CIはstrict-zero post-policy behaviorを所有し、過去のexact marker / path / mode / blob lineageはhistorical evidenceであってcurrent executable authorityではない。
3. repository-specific hash / canonical fixture / policy の portable contract への leakage、曖昧または重複した gate、package closure gap、lifecycle / worktree ownership の重複、未宣言 runtime capability を同じ revision で修復する。既存の最小 owner / surface を使い、新しい repository validation adapter、scheduler、state、telemetry、protocol は作らない。重複整理はcurrent First-Write Worktree Gateまたはseven-role KIS wiringを削除しない。
4. Human-approved Written Spec 内の parallel issue eligibility は agent / repository-owned とする。dependency / conflict evidence が unknown なら sequential に戻す。Human は material Written Spec change と別途 authorization が必要な remote action を決定し、execution method または issue plan の追加承認は不要とする。
5. generic lifecycle / worktree allocation methodologyはSuperpowersが所有する。SDDはrepository-change first entryとowned-worktree write containmentを所有し、current fail-closed、zero-write、no-fallback、original-checkout preservation behaviorを維持する。
6. `keep-implementation-simple`はrequired supporting skillであり、dependency preflight後にSpec Synthesizer、Spec Reviewer、Plan Author、Plan Reviewer、Implementer、Task Reviewer、Final Reviewerの七roleが同じcanonical pathを全文readする。このwiringはSPV-4の削除対象ではない。

## Open Decisions

なし。

## Review verdict

Human-approved direct Git amendment後のfresh independent rereviewは`ready_for_human_review`、decision requestとunresolved material riskはnoneであった。HumanはそのbytesをWritten Specとして承認し、statusを`accepted`、review stateを`approved`へ移した。その後のHuman-directed origin/main incorporation amendmentは、portable three-gate goalとauthority decision Aを変更せず、root authorityをcurrent strict-zero post-policy behaviorへ更新し、current First-Write Worktree Gateとseven-role KIS wiringをSPV-4のpreservation boundaryへ追加した。post-origin fresh independent reviewも`ready_for_human_review`、decision requestとmaterial riskはnoneであり、root validator 10/10、workflow contract 8/8、First-Write / KIS focused evidence 52/52を確認した。Humanのorigin/main incorporation指示をこのbounded amendmentのapproval authorityとし、`accepted` / `approved`を維持する。prior rereviewのroot-lineage記述は当時のhistorical review evidenceとしてのみ扱う。

## Provenance

- audited baseline: `82dcd32157ff9690ae038f982f3916009e449f80`
- authority: Human-confirmed decisionsを保持したadvisory synthesis。2026-08-14にHumanはvalidator necessity reviewの結論を承認し、bundled standalone validator要件をdirect Git gateへ置換した。raw report / transcript / runtime pathはdurable pageへ複製していない。
- Written Spec approval: 2026-08-14にHumanがcurrent spec全体を承認した。`approval_snapshot_sha256`はactivation metadata追加前のreview済みbytesを識別する。
- origin/main incorporation amendment: Humanの直接指示により`origin/main` `15152126fe0785bcf789a9ecbfe752b9e368fc4e`を取り込み、planning baseline `4d67bed6d297ba4e9a0f44559d3ca45c9a035976`で重複current behaviorを整合した。root validatorのclean-clone boundary repairが参照するactual policy-root parent identityはrepository-owned evidenceであり、portable contract、prompt、reference、fixtureへ移さない。
