# SDD Implementation Skill 設計

## 状態

Phase 1 の local implementation と verification は完了済みである。本書は、その後の調査と Human の方向性承認を反映し、2026-07-27にHumanがWritten Specとして承認した **Superpowers-first revision** である。

2026-07-28にHumanは、skill contractをagent-agnosticにするrevisionを承認した。skillは実行環境の名称を判定材料にせず、入力、依存skill、必要capabilityだけで同じflowを選ぶ。依存確認はactive runtimeのdiscovery surfaceで一度行い、別runtimeを並行検査しない。isolated dispatch、model selection、optional effort、wait / resumeはruntime capabilityとして解決し、agent名による手順分岐、agent別dependency check、agent別fallbackをcurrent contractから削除する。

同日のpublish前feedbackで、Humanはcross-runtime compatibility自体を非要件とした。標準`SKILL.md`によるagent-agnostic behaviorは維持するが、複数runtime向けpackageの併設、manifest整合、repository compatibility validator、compatibility CI gateはcurrent contractに含めない。pluginは必要なruntimeを個別にtargetでき、別runtime向けadapterを互換性だけのために追加しない。

このcompatibility-free contractはTask 1 commit `a1a177b877ebb07258bb69aa6d1f6f3429e9bc6e`（`Remove cross-runtime compatibility requirements`）でrepository surfaceへ反映された。独立reviewは`APPROVED`（Critical / Important / Minorなし）であり、current repositoryにはcompatibility validatorもcompatibility CI gateも存在しない。旧dual-host designはskill behaviorだけでなくplugin packaging compatibilityについてもhistorical / non-executableであり、過去のplanとlogは実行指示ではなく証跡として保持する。current local completionはこのdesign、follow-up plan、index、append-only logとfresh verificationを同期して判断し、pushとPull Request作成だけがlocal completion後に承認済みである。merge、release、live mutationは未承認のままである。

この agent-agnostic revision の spec / plan baseline は `c1f3791` である。Task 1 は `33fe86b240efcd03e8e9c6020f6620e87747da2d`（`Make skill runtime contracts agent agnostic`）で完了し、独立 task review は 0 findings で **Approved** となった。Task 2 は `171d4f1`、fix は `0501c45` であり、scoped re-review は **Approved** となった。baseline pressure scenario が検出した named dual-runtime preflight は、active runtime の一回だけの dependency / capability discovery に置換された。

final review は Critical 0 / Important 3 / Minor 0 を返したが、bounded final fix `44edcf0` が3件を解消した。final scoped re-review は全3件の解消、新規Critical / Important breakageなし、**APPROVED** を確認した。fresh pressure scenarioでは、synchronous dispatchがcompleted resultを返す場合はwait / resumeなしで継続し、asynchronous dispatchがwaitまたはresumeを欠く場合は`BLOCKED`、optional effortがない場合は`not_supported`として継続する。したがってcurrent agent-agnostic designは `LOCAL_COMPLETE` であり、residual material riskはない。remote writeおよびlive mutationは実施していない。

先行する Superpowers-first revision の実装、Task 1〜2 の task review、Task 3 の knowledge closeout、fresh verification、最終 whole-branch review は完了しており、local completion の要件を満たした。候補コミット`ec12012`に対する最終 review は Critical 0、Important 5、Minor 1 を検出したが、限定したfix commit `8b35113`で6件すべてを解消し、scoped re-review は全finding解消・新規Critical/Importantなしで承認された。post-fix evidence はSDD 17/17、LLM Wiki 6/6、scoped dual-host compatibility、skill-creator quick validator、`git diff --check`の成功を含む。Task 2 のfull bundle（scripts 68/68、architecture / context validators）もcloseout candidateに記録したとおり成功している。残るmaterial riskはない。[SDD Implementation Superpowers-first Revision Implementation Plan](sdd-implementation-superpowers-first-implementation-plan.md)は実装済みbaselineであり、そのruntime固有部分はagent-agnostic revisionにsupersedeされた。current runtime behaviorのdeltaは[SDD Agent-Agnostic Runtime Contract Implementation Plan](sdd-agent-agnostic-runtime-implementation-plan.md)であり、同planは`LOCAL_COMPLETE`である。push、PR、merge、release、live installその他のremote writeは実施していない。

Phase 2 は fresh coordinator verification と final whole-branch review を含めて `LOCAL_COMPLETE` である。`sdd-implementation` が既定かつ唯一の user-facing 実装入口であり、`skills/grill-to-pr-loop/` と `skills/issue-implementation-loop/`、および専用 runtime / context surface は current tree から削除済みである。historical wiki と旧 baseline は非実行の証跡として保持する。本 branch は Superpowers-first revision を含む `main` のコミット `dec5647` を統合し、Draft PR #41 として公開済みである。PR merge、release、live install は未実施である。

2026-07-28のreasoning effort risk precedence変更は`LOCAL_COMPLETE`である。Task 1を`2549892c07dc3f65c22094ca27b9208c831e65b0`で実装し、独立task reviewはapproved（material findingなし）となった。closeout candidate `ffa8339df00a5a8dfec90f572e843509516f49fe`へのfinal whole-branch reviewはknowledge discoverability / provenanceのImportant 2件を返したが、bounded fix `a7d0d294a6ccdbeec84f44c0cd6f3060967de5d1`で両方を解消し、scoped re-reviewはresolved 2/2、新規Critical / Importantなしで`APPROVED`となった。fresh verificationはSDD contract 18 tests、repository scripts 43 tests、LLM Wiki 5 tests、skill architecture / context validator、scoped dual-host compatibility、skill quick validation、`git diff --check`が成功している。push、PR、merge、release、live installその他のremote writeは実施していない。

2026-08-14の[[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]により、current Plan Stageはagent-owned contractへ移行した。Human approvalはNorth StarとWritten Specに限定し、fresh Plan Author、fresh independent Plan Reviewer、Plan Readiness Gateがplanの作成・修復・readinessを所有する。local [Plan Contract Overlay](../../../skills/sdd-implementation/references/plan-contract.md)はupstream `writing-plans`をrequired methodologyとして保持しつつ、prospective implementation bodyとHuman plan approvalをdurable planから除外する。Task POA-1のreviewed intentional RED、Task POA-2のreviewed combined GREEN、Task POA-3のoriginal closeoutはlanded済みである。

同仕様のHuman-approved transient-artifact amendmentは、Researchからknowledge closeoutまでのnormal SDD stageにおけるraw handoffをtask / session boundedなrepository外temporary locationへ移すcurrent contractである。POA-5のall-stage migration / fail-closed validator / CI integrationと、POA-6のexact three-report cleanupはindependent task reviewを通過してlandedした。current Git index / final treeは`.superpowers/**` entry zeroであり、必要なlocal copyはroot `.gitignore`のcoverage下でignored / untrackedのまま保持できる。pre-amendment ancestor historyはrewriteしない。POA-7は本書、focused context specification、canonical spec / plan、catalog、append-only logをこのlanded stateへ同期し、lifecycle correction後のfresh scoped re-reviewはprior Important 2件の解消、新規Critical / Importantなしで`ready`となった。POA-8のfresh combined verificationとcanonical whole-branch reviewもbounded fix / scoped re-reviewを経て完了し、本amendmentは`LOCAL_COMPLETE`である。authorized non-force remote branch updateはpending / unpublishedで、merge、release、live installは未承認のままである。

2026-08-14の[[sdd-portable-validation-simplification|portable validation仕様]]と
[[sdd-portable-validation-simplification-implementation-plan|reviewed implementation plan]]は、
本設計のvalidation / execution ownership seamのcurrent successorである。reviewed
Task 1〜4は、explicit target向け三direct-Git gate、root-only strict-zero / canonical
parity / CI ownership、isolated package closure、thin Superpowers compositionをlandさせ、
First-Write fail-closed containmentとexact seven-role KIS wiringを保持した。fresh local
verificationはpackage 139、root scripts 39、First-Write / KIS 29、llm-wiki 21
testsとarchitecture / context / Skill validatorsを成功させている。

portable-validation changeはknowledge closeoutからcanonical whole-branch reviewまで完了した。
review head `9f4787f`のCritical 0 / Important 4 / Minor 0はbounded final fix
`e9d1bcb`で全件addressされ、scoped re-reviewが新たに検出したKIS
spec/plan SHA binding driftはHuman-approved repair `3ef7564`が、歴史的snapshot
`1a99024e9f04791a4194304d01a50c42a29b516c4c2887b144079239f09dcfbd`の保持と
current approved spec `0c9570f9d3d54821d3ce6302c0a46824192b0d5c05c3b2e03e6923a0565d4aa4`
へのbindingを分離して解消した。final scoped re-reviewはresidual `ADDRESSED`、
new Critical 0 / Important 0と判定した。したがってcurrent local dispositionは
`LOCAL_COMPLETE`で、residual material riskはない。本設計の既存のhistorical
completion factは書き換えない。remote publication / merge / release / live installは
未実施かつ未承認である。

## 調査で確認した前提

Superpowers v6.2.0 では、開発フローの責任が次のように分かれている。

- `brainstorming`: requirements、constraints、success criteria、approach、design/spec、Human approval。
- `writing-plans`: 承認済み spec を exact files、tests、verification、commit 単位の実行可能 plan へ変換。
- `subagent-driven-development`: plan preflight、fresh implementer、task review、fix loop、final whole-branch review。

SDD には dispatch ごとの model 選択がすでにあり、全 dispatch に model 指定を要求する。task の complexity / risk に応じた relative capability tier も upstream が所有する。一方、model と独立した Thinking Effort / `reasoning_effort` の選択・伝播・escalation contract と、すべてのruntimeに共通するadapterはない。

詳細な evidence は [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) に保存する。

## 問題設定

現行の `sdd-implementation` は承認済み implementation plan から始まるため、spec を定義・精緻化する段階が user-facing flow の外にある。また、repo-local skill が implementer / reviewer の model policy まで所有しており、現行 Superpowers の per-dispatch model selection と責務が重複する。

一方、repository 固有の価値は upstream flow を置き換えることではなく、次の薄い integration にある。

1. spec stage で `Grill with Docs` を使い、一問一答で曖昧さを解消し、domain terminology と decision を明確にする。
2. `llm-wiki` を使い、既存知識の参照と、承認済み spec / plan / closeout の永続化を行う。
3. Superpowers の abstract model tier をactive runtimeで利用可能な concrete modelへ解決し、capabilityがある場合だけreasoning effortを追加する。
4. runtime identityではなく、isolated dispatch、model selector、optional effort、wait / resumeというcapability boundaryで実行可否を決める。

## 目的

`sdd-implementation` を、Superpowers の標準 lifecycle を主系とする user-facing development entrypoint にする。

```text
requirements
  -> Superpowers brainstorming
       -> llm-wiki query when prior knowledge is relevant
       -> Grill with Docs when spec is absent or materially unresolved
       -> Human-approved written spec
       -> llm-wiki durable spec sync
  -> Superpowers writing-plans
       -> repository Plan Contract Overlay
       -> fresh Plan Author self-review / independent Plan Reviewer
       -> agent-owned Plan Readiness Gate
       -> llm-wiki durable plan sync
  -> Superpowers subagent-driven-development
       -> upstream per-dispatch model selection
       -> repo-local runtime capability resolution
       -> repo-local reasoning effort overlay when supported
  -> llm-wiki knowledge closeout
  -> Superpowers final review / branch finishing
  -> LOCAL_COMPLETE | BLOCKED
```

caller は change request、既存 spec、または既存 implementation plan のいずれかを渡せる。entrypoint は入力の成熟度を判定し、完了済み stage を再実行しない。

## 最優先原則

### Superpowers を開発方法論の正本にする

- lifecycle、Human approval gate、plan structure、TDD、worker dispatch、review、fix loop、worktree、branch finishing は Superpowers に従う。
- repo-local skill は upstream skill を fork、vendor、要約再実装しない。
- upstream と local policy が重なる場合は、明示的な repository policy または Human override がない限り upstream を正本とする。
- current Superpowers version で提供される責務を「不足機能」として重複実装しない。

### Integration を薄く保つ

- `Grill with Docs` は spec refinement の対話技法だけを所有する。
- `llm-wiki` は durable knowledge の query / ingest / closeout だけを所有する。
- repo-local runtime boundary は model resolution、optional reasoning effort、dispatch capability mapping だけを所有する。
- runtime ledger、reports、diff、test logs、agent IDs はtask / session boundedなrepository外temporary locationに置き、wikiへ保存しない。repository-local `.superpowers/**`は[[sdd-plan-ownership-alignment|current alignment spec]]が定めるreason / ignore gateを満たすignored local scratchに限る。

### Review は material finding だけを扱う

task review と final review は、requirements fit、同じ要件をより単純に満たせる material な余地、current change の material risk の順に確認する。

style preference、具体的 failure path のない将来懸念、scope 外 refactor / hardening、軽微な formatting、同等案への好みは blocking finding にしない。mechanical validator、formatter、linter、schema check、required test suite の実行範囲は狭めない。

## Ownership

| Concern | Owner | Repo-local composition |
|---|---|---|
| requirements / design / written spec | Superpowers `brainstorming` + Human | `Grill with Docs` と `llm-wiki` を stage 内で呼ぶ |
| ambiguity resolution / domain sharpening | `Grill with Docs` | 一問一答、decision ごとの合意、用語の明確化 |
| durable knowledge | `llm-wiki` | repository topology、write boundary、index / log に従う |
| executable implementation plan | Superpowers `writing-plans` + fresh Plan Author / independent Plan Reviewer | local Plan Contract Overlay、agent-owned readiness、wiki syncを加える |
| implementation / TDD / task review / fix loop | Superpowers SDD | upstream template と lifecycle をそのまま使う |
| dispatch model tier | Superpowers SDD | host の concrete model へ解決するだけ |
| reasoning effort | repo-local host adapter | host が独立制御を提供する場合だけ適用 |
| final review / branch finish | Superpowers | wiki closeout を review 対象 range に含める |

`Grill with Docs` の `domain-modeling` が通常提案する `CONTEXT.md` や `docs/adr/` は、この repository では別の durable store として作らない。repository の `AGENTS.md` と `llm-wiki` write boundary を優先し、恒久的な glossary、ADR、spec、decision は `knowledge/wiki/...` の canonical page に統合する。

## 実装前 Planning Controller

実装前のmain sessionはPlanning Controllerであり、Human対話、current decision、
spec draft内の`Confirmed Decisions` / `Open Decisions`、approval、stage routing、
短いControl Returnだけを所有する。source code、broad wiki / docs、full spec /
plan、diff、test output、複数file探索は直接読まない。

Change requestまたはincomplete specではfresh Research Workerが、runtimeがtask / session用に解決した
repository外temporary locationへpath / line evidence付きreportを書く。write前にrepository root、planning
worktree、original checkoutの外にあるbounded pathであることを確認する。
accepted decisionが揃った後はfresh Spec Synthesis Worker、別のfresh Spec
Reviewer、fresh Plan Author Worker、fresh independent Plan Reviewerへ順にrouteする。workerはparent
conversationを継承しない。Humanはmaterial decisionとWritten Spec approvalを保持し、Plan Author /
Reviewerはplan method、repair、readinessを所有する。

workerの直接returnは`status`、`artifact_path`、`decision_requests`、
`material_risks`へ限定し、詳細はartifact pathへ置く。stage transitionはcurrent
result、canonical paths、open decisions、approval state、material riskだけを
Stage Capsuleへcarryする。Control ReturnとStage Capsuleの長さは運用目安であり、
context telemetry、manual compaction、word-count validatorをcorrectness gateにしない。

このseamは`skills/sdd-implementation/references/`と`prompts/`に閉じる。新しい
user-facing skill、custom scheduler、context contract、runtime state、packet schema、
fallback matrix、main-session exploration fallbackは追加しない。Superpowers、
`grill-with-docs`、`llm-wiki`の既存ownershipを変更しない。

## Entry Classification

### Change request だけがある

`brainstorming` へ入り、relevant な knowledge root があれば `llm-wiki` で既存 spec、terms、decision を query する。その後 `Grill with Docs` を必須で使い、material ambiguity を一つずつ解消する。Written Spec を作成して self-review し、Human approval を得るまで planning / implementation へ進まない。

### Spec はあるが未承認または不完全

既存 spec と repository evidence を入力に `brainstorming` を継続する。material ambiguity、未確定 trade-off、acceptance criteria 不足が一つでもあれば `Grill with Docs` を使う。承認済みで完全な部分を無意味に聞き直さない。

### Human-approved spec がある

spec の authority、current applicability、requirements / acceptance criteria の充足を確認する。問題がなければ `Grill with Docs` を再実行せず、`writing-plans` へ進む。material conflict を発見した場合だけ spec stage へ戻す。

### Current spec に binding されたreview済み repository-ready planがある

spec digest または同等の binding、current tree との compatibility、verification scope を確認する。問題がなければ brainstorming と plan writing を再実行せず、SDD preflight へ進む。

## Spec Stage

### `llm-wiki` query

knowledge root が存在し、既存の decision、terminology、architecture、prior implementation が current spec に material な影響を与え得る場合に query する。単純な change で relevant knowledge がない場合は、儀式として query を強制しない。

knowledge root が存在しない repository では `not_applicable` とし、自動 bootstrap は行わない。

### `Grill with Docs`

次の場合に必須とする。

- Human-approved written spec がない。
- requirements、scope、trade-off、acceptance criteria、non-goal、domain terminology のいずれかが material に未確定。
- repository evidence と提示 spec が conflict しており、Human decision が必要。

`Grill with Docs` は一度に一問だけを扱い、調べれば分かる事実を Human に質問せず、decision ごとの shared understanding を確認する。spec authoring と仕様を詰める作業の標準手段とする。

必要な場面で `Grill with Docs` が利用できない場合は、通常の ad hoc 質問へ silent fallback せず `BLOCKED` とする。すでに Human-approved で current な spec がある場合は `not_needed` とする。

### Written Spec と Human approval

Superpowers `brainstorming` の contract に従い、少なくとも architecture、components、data / control flow、error handling、testing、acceptance criteria、non-goals を current task に必要な粒度で文書化する。repository に knowledge root がある場合は `llm-wiki` の write boundary に従って canonical spec として保存し、`knowledge/index.md` と `knowledge/log.md` を同期する。

Human が Written Spec を明示承認するまで `writing-plans` を開始しない。

## Plan Stage

承認済み spec を Superpowers `writing-plans` に渡し、repositoryの
[Plan Contract Overlay](../../../skills/sdd-implementation/references/plan-contract.md)を適用する。
upstream methodologyはrequired dependencyとして保持するが、durable planにはrequired plan/task fields、
complete coverage、acyclic dependency、execution order、serialized integration、combined verification、
readiness evidenceだけを保存し、prospective production / test body、script / patch body、commit command bodyを
保存しない。

fresh Plan Authorのself-review後にfresh independent Plan Reviewerがplanを確認する。`needs_repair`はfresh
author / reviewer loopに閉じ、approved North Star / Written Specとのmaterial conflictだけを一件の
`needs_decision`としてHumanへ戻す。capability、binding、authority不足はdecision requestなしの`blocked`である。
`ready`だけをControl Return `status: complete`へmapし、Implementation Stage entryを許可する。Humanにplan
approvalやexecution methodの選択を求めず、remote authorization不足をplan readiness blockerにしない。

knowledge root がある場合、agent-reviewed / repository-ready planとspec binding、coverage、readiness evidenceを
durable pageとして同期する。planにconcrete model名、reasoning effort値、provider、agent ID、runごとの
availabilityを固定しない。

## SDD Stage

### Upstream model selection

implementer、task reviewer、re-reviewer、final reviewer の model tier は Superpowers SDD の current `Model Selection` contract を正本とする。repo-local skill は別の role-to-model policy tableを持たない。

全 dispatch で upstream が要求する model field を明示する。active runtimeのcapability layerはupstreamのrelative tierを、その実行時に利用可能なconcrete modelへ解決する。user が runtime model を明示した場合は、その指定を優先する。

### Reasoning effort overlay

reasoning effort は model tier と独立した optional runtime overlay とする。

| Superpowers task class | Abstract effort |
|---|---|
| clear spec の mechanical task、small scoped re-review | low |
| multi-file integration、normal debugging、task review | medium |
| architecture-sensitive / high-risk task、final whole-branch review | high |

effort は worker role だけでなく、実際の task complexity / risk で分類する。複数行に該当する場合は、より高い complexity / risk の行を優先する。したがって、通常の task review は medium だが、architecture-sensitive または high-risk な task review は high とする。全 task を機械的に一段上げることはしない。

fix loop が同じ failure で収束しない場合は、まず available な範囲で effort を一段上げる。それでも不足する場合は、Superpowers の model escalation に従う。user が runtime effort を明示した場合は、その指定を優先する。

active runtimeが独立した effort control を提供しない場合は `not_supported` として扱い、Superpowers の model selection だけで継続する。reasoning effort がないことだけを理由に全 flow を block しない。model を明示して isolated dispatch する能力自体がない場合は `BLOCKED` とする。

共有 contract の既定 vocabulary は low / medium / high に限定する。runtimeがそれより高い effort level を提供していても、通常のtask classへ追加せず、明示的なruntime overrideとしてのみ扱う。

concrete model、effort、provider、availability、agent ID、run-specific resolution は runtime-only とし、spec、plan、wiki、ledger、schemaへ永続化しない。

### Runtime capability boundary

- active runtimeのdiscovery surfaceでapplicable dependencyを一度確認する。別runtimeのinstallationやdiscoveryを同じrunのpreflightへ追加しない。
- fresh worker / reviewer、model selector、optional effort、wait / resumeをactual capabilityとして検出し、runtime名ではなくcapabilityの有無へ写像する。
- completed resultを返すsynchronous dispatchは有効なresult-collection mechanismとする。asynchronous dispatchはwaitとresumeの両capabilityを必須とし、synchronous result collectionもasynchronous wait / resumeも利用できない場合は`BLOCKED`を返す。
- runtime固有のtool nameやmodel catalogを共通`SKILL.md`のdurable contractに固定しない。
- required SDD capability を安全に満たせない場合、main session implementation や旧 loop skill へ silent fallback しない。

## Knowledge Lifecycle

`llm-wiki` は三つの durable checkpoint を所有する。

1. Human-approved Written Spec: canonical spec、related terminology / ADR、index、log。
2. Agent-reviewed / repository-ready implementation plan: spec binding、coverage、readiness、plan、index、log。
3. Implementation closeout: 実装結果、material decision、verification、残課題、index、log。

runtime progress ledger、worker report、review transcript、diff、test log は durable knowledge ではなく、task / session boundedなrepository外temporary evidenceとする。例外的なrepository-local scratchは[[sdd-plan-ownership-alignment|current alignment spec]]のconcrete-reason / pre-write ignore gateに従い、ignored / untracked / unstaged / uncommittedに限定する。

すべての implementation task と task review が完了した後、final whole-branch review の前に closeout を行う。final reviewer は code、tests、spec、plan、wiki、index、log を同じ branch range で確認する。

knowledge root が存在するのに authority、canonical target、write boundary、index / log sync、validation のいずれかを解決できない場合は `LOCAL_COMPLETE` にしない。knowledge root がない場合は `not_applicable` とする。

## Error Handling And Stop Conditions

- material ambiguity が残る場合は `Grill with Docs` を継続し、暗黙の assumption で spec を確定しない。
- Written Spec の Human approval がなければ plan stage へ進まない。
- plan と spec の binding が失われていれば SDD へ進まず、plan stage へ戻す。
- plan deficiencyはfresh Plan Author / Reviewerのrepair loopへ戻し、Humanへplan reviewやmethod choiceを求めない。
- current tree とapproved North Star / Written Specがmaterialに不一致なら、conflict evidenceと一件のdecision requestだけをHumanに戻す。
- SDD、isolated implementer、independent reviewer、required worktree、必要な domain skill が利用不能なら停止する。
- reviewer finding と approved spec / plan が衝突する場合、authority-bearing decision は Human に戻す。
- requirement または material current risk に紐づかない observation は fix loop に入れない。
- remote write、push、PR、merge、release、live install は、別途明示承認がない限り実行しない。

## Acceptance Criteria

- change request から Human-approved Written Spec、implementation plan、SDD、knowledge closeout までの一貫した route が定義される。
- spec authoring または material な仕様精緻化では `Grill with Docs` が必須になる。
- complete なHuman-approved specまたはreview済みrepository-ready planがある場合は、完了済みstageを重複実行しない。
- Superpowers が lifecycle、plan、TDD、dispatch、review、model tier の正本であり、repo-local skill がそれらを再実装しない。
- `llm-wiki` がrelevant knowledge queryと、approved spec / agent-reviewed repository-ready plan / closeoutのdurable storageを所有する。
- Grill / Domain Modeling の既定出力を使って `CONTEXT.md` や repo-root `docs/adr/` という並行正本を作らない。
- repo-local model logic は upstream tier の active-runtime resolution に限定される。
- reasoning effort は `low` / `medium` / `high` の runtime-only overlay として選択され、capabilityがない場合はmodel routingのみで継続できる。
- skill behaviorはruntime identityで分岐せず、入力、依存skill、必要capabilityだけで決まる。
- concrete model / effort / provider / agent ID / run-specific resolution を durable artifact に保存しない。
- knowledge root がある場合、spec、plan、closeout、index、log、validation が completion contract に含まれる。
- old loop skill、独自 scheduler、packet schema、event store、runtime snapshot を fallback または新規依存として導入しない。
- 任意の対応runtimeが同じ`SKILL.md`を読み、標準entrypointとrepository skill validatorを通過する。
- `sdd-implementation` 以外の user-facing 実装 skill directory と専用 runtime / context surface が current tree に存在しない。

## Testing Strategy

### Contract tests

- entry inputをchange request / incomplete spec / approved spec / reviewed repository-ready planに分類できる。
- spec 不在または material ambiguity ありでは `Grill with Docs` が required になる。
- approved current spec では Grill が `not_needed` になり、plan stage へ進む。
- Written Spec approval なしでは plan / implementation に進めない。
- upstream model selection を参照し、重複する repo-local role-to-model table を持たない。
- effort overlay が low / medium / high、risk-over-role precedence、user override / escalation を定義する。
- architecture-sensitive / high-risk task review が generic task-review default の medium ではなく high になる。
- 共有 contract の既定 vocabulary に runtime固有の higher effort level を追加しない。
- effort unsupported は `not_supported`、isolated model dispatch unsupported は `BLOCKED` になる。
- synchronous dispatchはcompleted resultを直接収集でき、asynchronous dispatchはwait / resumeを要求し、どちらのresult collectionもない場合は`BLOCKED`になる。
- knowledge root の有無と write boundary に応じて query / ingest / closeout を選べる。
- concrete runtime choice を durable artifact へ保存しない。
- old loop skillへ silent fallback しない。
- active runtimeでapplicable dependencyを一度だけ確認し、repository skill validatorを通過する。

### Forward scenarios

1. rough change request を wiki query と Grill に通し、Human-approved spec、plan、SDD へ進める。
2. incomplete spec の未確定 decision だけを一問一答で詰める。
3. approved spec を再 grilling せず plan 化する。
4. current specにbindingされたreview済みrepository-ready planを直接SDDへ渡す。
5. mechanical / integration / high-risk dispatch で upstream model tier と local effort overlay が独立して解決される。
6. architecture-sensitive / high-risk task review で role default より risk classification が優先され、high が選ばれる。
7. effort capabilityがないruntimeでupstream model selectionにより正常継続する。
8. synchronous dispatchがcompleted resultを返すruntimeではwait / resumeなしで正常収集する。
9. asynchronous dispatchだけを持ちwait / resumeのいずれかを欠くruntimeでは`BLOCKED`としてfail closedにする。
10. knowledge root ありで approved spec / plan / closeout、index、log を同期してから final review する。
11. knowledge root なしで wiki stage を `not_applicable` にする。
12. wiki validation failure が `LOCAL_COMPLETE` を block する。

### 実装前コンテキスト分離の landed verification coverage

Task 2では、各scenarioをparent conversation非継承のfresh worker / controllerへ
限定入力で渡し、次の7件をすべて`PASS`として確認した。詳細なreport、worker return、
test outputはtransient evidenceに留め、wikiへはcurrent behaviorだけを統合する。

1. rough change requestではfresh Research Workerだけがscoped repository evidenceを調査し、Planning Controllerはsourceを読まず、materialなdecision requestを1件だけ返した。
2. 325行・2,365語のlong reportでは詳細をartifact pathへ置き、直接returnを`status`、`artifact_path`、`decision_requests`、`material_risks`の4 fieldだけに保った。
3. confirmed decisionではfresh Planning Controllerが同じ質問を繰り返さず、forbidden readやauthoringなしに次のopen decisionへrouteした。
4. material conflictでは矛盾したdecisionだけを再openし、prior decision、current conflict、impactを一緒に提示してHuman authorityを維持した。
5. spec synthesis / reviewでは別々のfresh workerがconfirmed decisionを保持し、Spec Reviewerはadvisory-onlyの`ready_for_human_review`を返してHuman Written Spec approvalを要求した。
6. Plan Authorではfresh workerがbaseline `66d93ae`、approved spec、repository rules、upstream `writing-plans`にbindingしたTDD planを作成・self-reviewし、直接returnをControl Returnだけに保った。
7. isolated fresh-context dispatchがない場合は`BLOCKED`を返し、optional effortを`not_supported`として扱い、Planning Controllerへresearchやauthoringをfallbackしなかった。

## Completion Contract

`LOCAL_COMPLETE` は次をすべて満たす場合だけ返す。

- Human-approved Written Spec に current implementation が binding されている。
- repository Plan Contract Overlayとfresh independent Plan Reviewを満たし、readinessが`ready`である。
- reviewed planの全taskがSuperpowers SDDのtask reviewを通過している。
- required verification が fresh に成功している。
- scoped commits が current branch に含まれる。
- knowledge root がある場合、spec / plan / closeout、index、log、validation が完了している。
- knowledge closeout 後の whole-branch final review が approved である。
- blocker、residual risk、未実施 remote action が短く報告されている。

## Migration

- 既存 Phase 1 implementation は current behavior の evidence として保持する。
- 既存の [SDD Implementation Skill 実装計画](sdd-implementation-skill-implementation-plan.md) は Phase 1 の historical plan とし、この revision の実行には再利用しない。
- Superpowers-first successor implementation は `main` へ統合済みである。
- Phase 2 は別 task / PR として実行し、`skills/grill-to-pr-loop/` と `skills/issue-implementation-loop/`、専用 runtime / context surface を current tree から削除した。
- historical wiki source / spec / ledger と `skill-repository-optimization-v4-context-baseline.json` は、実行可能 artifact として再利用せず非実行の evidence として保持する。
- Phase 2 の fresh coordinator verification（SDD 9、llm-wiki 5、scripts 42 tests、architecture / context / dual-host / skill validators、legacy absence / link checks）と、`8ff2bdc..804c2c7` の final review（Critical 0、Important 0、Minor 0、Ready to merge Yes）は完了済みである。
- [SDD 実装前コンテキスト分離仕様](sdd-preimplementation-context-isolation-spec.md)と[その実装計画](sdd-preimplementation-context-isolation-implementation-plan.md)がsupersedeするのはpre-implementation context ownershipの部分だけである。historicalなloop context documentsはnon-executable evidenceとして保持し、そのruntime machineryは復元しない。
- [[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]は、本書と実装前コンテキスト分離仕様に残っていたPlan StageのHuman / repository approval、artifact content、readiness、Human return semanticsをsupersedeする。さらに同仕様のHuman-approved transient-artifact amendmentは、Research、Spec、Plan、Implementation、task review、repair、integration、final review、knowledge closeoutを含むすべてのnormal SDD stageで競合するrepository-contained transient research / report / brief / handoff destinationとwrite bindingをsupersedeする。Superpowers-firstのbroader lifecycle、fresh worker isolation、trusted planning worktree内のsource code / durable knowledge write boundaryは本書および同focused specificationをcurrent sourceとして維持する。

## 非目標

- Superpowers skills を fork、vendor、再実装する。
- Superpowers が所有する per-dispatch model selection を repo-local policy で置き換える。
- `Grill with Docs` に planning、execution、durable storage を所有させる。
- `llm-wiki` に scheduler、runtime ledger、worker report、review transcript を保存する。
- provider 固有 model catalog、price、latency、benchmarkを repository で管理する。
- concrete model / reasoning choiceを wiki、plan、ledger、schemaへ保存する。
- custom scheduler、queue、event store、runtime snapshot、worker packet、resume cacheを作る。
- knowledge root を暗黙に bootstrap する。
- old loop skill の削除、push、PR作成、merge、release、live installを successor implementation と同時に行う。

## 関連ページ

- [[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]] — current Plan Stage authority、artifact、review、readiness semanticsと、全normal SDD stageのrepository-external transient destination / Git zero-tree boundaryのcanonical source。
- [[sdd-plan-ownership-alignment-implementation-plan|SDD Plan Ownership Alignment 実装計画]] — approved specへbindingしたagent-authored planとPOA-1〜8のserialized integration contract。
- [SDD Compatibility Removal Follow-up Plan](sdd-compatibility-removal-follow-up-plan.md) — publish前feedbackで非要件となったcross-runtime compatibility layerを削除するcurrent follow-up plan。
- [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) — upstream v6.2.0 の model、effort、host、spec / plan / SDD ownership の evidence。
- [SDD Agent-Agnostic Runtime Contract Implementation Plan](sdd-agent-agnostic-runtime-implementation-plan.md) — current runtime behaviorのdelta / closeout candidate。
- [SDD Implementation Superpowers-first Revision Implementation Plan](sdd-implementation-superpowers-first-implementation-plan.md) — runtime固有部分がsupersedeされた実装済みbaseline。
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md) — Human authority と runtime model persistence の既存契約。
- [SDD Implementation Skill 実装計画](sdd-implementation-skill-implementation-plan.md) — Phase 1 の historical implementation plan。
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md) — 旧 loop family の複雑性と適用基準。

## 出典

- [Planning Authority Policy 仕様](planning-authority-policy/spec.md)
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- historical production path（Phase 2で削除済み）: `skills/grill-to-pr-loop/SKILL.md`
- historical production path（Phase 2で削除済み）: `skills/issue-implementation-loop/SKILL.md`
- `codex-plugin-cache:openai-curated-remote/superpowers/6.2.0/skills/subagent-driven-development/SKILL.md`
- [Superpowers v6.2.0](https://github.com/obra/superpowers/tree/v6.2.0)
- [Superpowers Basic Workflow](https://github.com/obra/superpowers/blob/v6.2.0/README.md#L184-L197)
- [Superpowers Brainstorming](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md)
- [Superpowers Writing Plans](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md)
- [Superpowers Subagent-Driven Development](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md)
- `local-skill:/Users/omitsuhashi/.agents/skills/grill-with-docs/SKILL.md`
- [skills/llm-wiki/SKILL.md](../../../skills/llm-wiki/SKILL.md)
