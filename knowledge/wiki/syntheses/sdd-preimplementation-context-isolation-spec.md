# SDD 実装前コンテキスト分離仕様

## 状態

2026-07-29にHumanとのGrand Design上のshared understandingを確認し、同日に
Humanが本書をWritten Specとして承認した。本書のfresh Planning Controller / worker isolationは
current contractとして維持する。2026-08-14の[[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]が、
本書のPlan Stageに残っていたHuman / repository plan approval、artifact content、readiness、Human return
semanticsをsupersedeする。同仕様のHuman-approved transient-artifact amendmentは、本書のrepository-contained
Research Report destinationと全pre-implementation raw handoff write bindingも競合範囲でsupersedeする。POA-5の
repository-external migration / validatorとPOA-6のexact three-report cleanupはreview済みでlandedし、POA-7で
canonical closeoutを同期した。POA-7 lifecycle correction後のfresh scoped re-reviewはprior Important 2件の解消と
新規Critical / Importantなしを確認して`ready`となった。Planning Controller / fresh worker isolation、source /
durable worktree boundary、Human Written Spec authorityは維持する。POA-8のfresh whole-branch reviewとremote branch
updateはpendingである。

## Epic ID

`sdd-preimplementation-context-isolation`

## 問題設定

現行の`sdd-implementation`はchange requestからSpec Stage、Plan Stage、
Implementation Stage、knowledge closeoutまでを一つのuser-facing routeとして扱う。
Implementation Stageではmain sessionをorchestratorに限定し、fresh implementerと
independent reviewerへ実作業を委譲している。

一方、Spec StageとPlan Stageではmain sessionがHumanとの対話に加えてrepository探索、
複数fileの取得、wiki query、spec synthesis、plan authoringまで担う。長い探索結果と
対話履歴が同じcontextへ蓄積するため、compaction後に解決済みの問いが再発したり、
accepted decisionを再発見したりすることがある。

このrevisionは、実装前段にもcontroller / worker分離を適用し、Humanとの連続した
意思決定を維持したまま、repositoryを読む作業と大きなartifact authoringをfresh
workerへ移す。

## 目的

- `sdd-implementation`を唯一のuser-facing repository-change entrypointとして維持する。
- Spec StageとPlan Stageでもmain sessionをPlanning Controllerに限定する。
- repository探索、Spec Synthesis、Plan Authoringをfresh workerへ委譲する。
- raw tool outputと長いartifact本文をPlanning Controllerのcontextへ入れない。
- compaction後もDecision Recordとcanonical artifact pathから再開できるようにする。
- 解決済みの問いを、materialな新規evidenceなしにHumanへ聞き直さない。
- upstream Superpowersと既存`llm-wiki` lifecycleを正本として維持する。

## 採用しなかった案

### すべてを`SKILL.md`へ直接追加する

entrypoint自身のread量とinterfaceを肥大化させ、今回減らしたいcontext pressureを
増やすため採用しない。

### 新しいuser-facing `spec-research` skillを追加する

現時点の主要callerは`sdd-implementation`だけである。独立skillを削除した時に
複雑性が複数callerへ戻る状態ではないため、外部seamにはせずSDD内部seamとして
実装する。独立callerが複数確認された場合だけ将来の抽出を再検討する。

### 旧loop familyのcontext runtimeを復活させる

旧scheduler、Execution Envelope、runtime state、worker packet schema、event log、
resume protocol、session-pressure reporterは再導入しない。旧context-compaction設計の
うち、artifact pathへ退避しphase間のcarry-forwardをboundedにする原則だけを使う。

## 用語

### Planning Controller

実装前段のmain session。Humanとの対話、accepted decision、approval、stage routing、
短いverdictを所有する。repository探索、full artifact synthesis、implementationは
所有しない。

### Pre-Implementation Worker

Planning Controllerからisolated fresh-context dispatchされるread / authoring worker。
Research Worker、Spec Synthesis Worker、Plan Author Workerを含む。Humanのdecision
authorityを持たず、supporting authorityはadvisory-onlyである。

### Control Return

workerがPlanning Controllerへ直接返す短い制御情報。`status`、`artifact_path`、
`decision_requests`、`material_risks`を中心とし、詳細本文を含めない。

### Stage Capsule

次stageが前stageのraw discussionやtool outputへ依存しないための短いcarry-forward。
current result、canonical paths、open decisions、approval state、material riskだけを持つ。

### Decision Record

planning worktree上のspec draftに置く`Confirmed Decisions`と`Open Decisions`。
別ledger、`CONTEXT.md`、repo-root `docs/adr/`は作らない。

## Grand Design

```text
Change Request / Incomplete Spec / Approved Spec / Reviewed Repository-Ready Plan
  -> Planning Controller
       -> Research Worker
       -> Human Decision Loop with Grill with Docs
       -> Spec Synthesis Worker
       -> Spec Reviewer
       -> Human Written Spec Approval
       -> Plan Author Worker using Superpowers writing-plans
       -> Repository Plan Contract Overlay
       -> Independent Plan Reviewer
       -> Agent-owned Plan Readiness Gate
  -> Superpowers subagent-driven-development
  -> Knowledge Closeout Worker
  -> Final Whole-Branch Review
```

入力がapproved current specまたはreview済みrepository-ready planの場合は、現行のinput maturity routingに
従って完了済みstageを再実行しない。

## Planning Controller Contract

### 所有する責務

- Humanの依頼と現在の一問を保持する。
- input maturityとcurrent stageを分類する。
- workerをrouteし、Control Returnを評価する。
- Humanへ一度に一つのmaterial decisionだけを提示する。
- Confirmed DecisionsとOpen Decisionsを小さく更新する。
- approval stateとstage transitionを管理する。
- accepted spec / planと次stageのbindingを確認する。

### 直接読んでよいもの

- 適用するskill instructionsとrepositoryの`AGENTS.md`。
- repository root、branch、worktree、statusなどのrouting metadata。
- Control ReturnとStage Capsule。
- 現在の一問に必要なspec / planの短い該当箇所。
- approval stateとcanonical artifact path。

spec / planの該当箇所はworkerがControl Returnまたは専用excerpt fileとして切り出す。
Planning Controller自身がfull artifactを読んで該当箇所を探索しない。

### 直接読まないもの

- source code。
- 広範なwiki / docs page。
- full spec / full plan。
- git diff、test output、raw command output。
- 複数fileにまたがるrepository探索結果。

Planning Controllerはfull artifactを統合する代わりに、必要なworkerへpathを渡す。
Decision Recordの小さな更新はHuman decision ownershipの一部であり、worker dispatchを
増やさずPlanning Controllerが行ってよい。

## Research Stage

### Research Worker

Research Workerは親conversationを継承せず、repository root、調査質問、applicable
constraints、report pathだけを受け取る。

次を担当する。

- repository structure、source code、docs、git historyの必要範囲を調べる。
- relevant knowledge rootがあれば`llm-wiki` query contractで既存decisionを調べる。
- current spec、runtime contract、test、validatorとのconflictを確認する。
- claimごとにpathとline evidenceを残す。
- confirmed fact、conflict、unknownを分離する。

設計判断、scope approval、risk acceptance、Humanへの質問文の最終決定は行わない。

### Research Report

Research reportはruntimeがtask / session用に解決したrepository外temporary locationへ置く。write前に
repository root、planning worktree、original checkoutの外にあるbounded pathであることを確認する。wiki、Git、
canonical specの正本ではなく、task-scoped evidence cacheとして扱う。

repository-local `.superpowers/**`は通常のhandoff destinationにしない。concreteなoperational reasonがある
場合だけ、write前にroot `.gitignore` coverageをmechanically確認し、ignored / untracked / unstaged /
uncommitted local scratchとして使用できる。このcurrent write bindingのauthorityは
[[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]にあり、本書はworker isolationとcarry-forward
semanticsだけを所有する。

Humanが採用した判断と将来も必要な根拠だけをWritten Specへ昇格させる。raw reportを
`knowledge/index.md`へ登録せず、implementation closeout後に不要なら削除できる。

## Human Decision Loop

`grill-with-docs`を使い、一度に一つのmaterial decisionだけを確認する。環境を調べれば
分かるfactをHumanへ質問しない。

質問前にDecision Recordを確認する。Confirmed Decisionsの問いは、new repository
evidenceとのmaterial conflictがある場合だけOpen Decisionsへ戻せる。その場合は、
旧decision、conflicting evidence、decision impactを一緒に提示する。

## Spec Synthesis Stage

Spec Synthesis Workerはfresh contextで次だけを読む。

- Research Report paths。
- Confirmed DecisionsとOpen Decisions。
- current spec draft。
- applicable repository / knowledge authoring rules。

workerはarchitecture、interfaces、control flow、failure handling、testing、
acceptance criteria、non-goalsをWritten Specへ統合する。未解決decisionを暗黙の
assumptionで埋めない。

Spec Reviewerは別のfresh workerとし、少なくとも次を確認する。

- accepted decisionがすべて反映されている。
- resolved questionを再度openにしていない。
- repository evidenceと矛盾していない。
- unknownをconfirmed factとして書いていない。
- acceptance criteria、non-goals、stop conditionが十分である。

HumanがWritten Specを確認し承認するまでPlan Stageへ進まない。

## Plan Stage

Plan Author Workerはfresh contextでSuperpowers `writing-plans`を使い、approved specと
必要なcanonical pathだけからexecutable implementation planを作る。repository
[Plan Contract Overlay](../../../skills/sdd-implementation/references/plan-contract.md)を適用し、
required plan/task fields、complete coverage、dependency / execution / serialized integration order、
combined verification、readiness evidenceを保存する。prospective implementation bodyはplanへ保存しない。

Planning Controllerはrepository file mappingやcode探索を繰り返さず、Control Return、
plan path、spec binding、readiness resultだけを扱う。fresh Plan Authorのself-review後にfresh independent
Plan Reviewerをdispatchし、`needs_repair`をfresh author / reviewer loopへ戻す。approved North Star /
Written Specとのmaterial conflictだけを`needs_decision`としてHumanへ返し、capability、binding、authority
不足はdecision requestなしの`blocked`とする。`ready`だけがImplementation Stageへ進む。Human plan approval
またはHumanによるexecution method選択は要求しない。

## Context Handoff

物理的なcontext削除やsession usage telemetryには依存しない。stage transition時に
次stageが参照してよい入力を限定する。

| Transition | Carry forward |
| --- | --- |
| Research -> Decision | report path、confirmed fact summary、conflict、open decision |
| Decision -> Spec | Confirmed Decisions、Open Decisions、research paths |
| Spec -> Plan | approved spec path、binding evidence、material constraints |
| Plan -> Implementation | reviewed repository-ready plan path、spec path、readiness evidence、verification scope |
| Implementation -> Closeout | commits、worker reports、review / verification paths |

Control Returnは200 words程度、Stage Capsuleは400 words程度を目安にする。ただし
word-count schema、validator、script、超過時のBLOCKED処理は作らない。重要なのは
semantic fieldを短く保ち、詳細をartifact pathへ置くことである。

このtableのresearch / worker / review pathはrepository外temporary locationを指す。durable spec、reviewed plan、
source、knowledge closeoutだけをtrusted planning worktreeへ書き、raw handoffをrepository artifact identityや
clone-stable provenanceとして扱わない。

## Runtime And Failure Policy

isolated fresh-context dispatchとexplicit model selectionは通常の前提条件とする。
Pre-Implementation Workerごとのmodel tierはcurrent Superpowers model selectionを
task complexity / current riskに応じて解決し、concrete modelやrun-specific routingを
durable artifactへ保存しない。

新しいfallback matrix、retry scheduler、capability schema、main-session exploration
fallbackは作らない。required capabilityを利用できないruntimeでは、既存のSDD
dependency / capability不足として単純に停止する。

## Skill Structure

`sdd-implementation`を外部interfaceとし、内部実装をstage別に分ける。

```text
skills/sdd-implementation/
├── SKILL.md
├── references/
│   ├── plan-contract.md
│   ├── planning-context.md
│   └── research-stage.md
├── prompts/
│   ├── plan-reviewer.md
│   ├── repository-researcher.md
│   ├── spec-synthesizer.md
│   └── spec-reviewer.md
└── tests/
```

`SKILL.md`はinput maturity routing、required stage、Planning Controller invariant、
worker dispatch requirementだけを持つ。stage detailとpromptは必要な時だけ読む。

新しいuser-facing skill、standalone context manager、`context-contract.toml`、
runtime schema、event storeは追加しない。

## Knowledge Lifecycle

current `llm-wiki` durable checkpointsを維持し、Plan checkpointのauthority表現だけをcurrent contractへ揃える。

1. Human-approved Written Spec。
2. Agent-reviewed / repository-ready implementation planとspec binding / readiness evidence。
3. Implementation closeout。

Research Report、Control Return、Stage Capsule、review transcript、raw outputはwikiへ
保存しない。durable spec / plan / closeoutを変更した時だけ`knowledge/index.md`と
`knowledge/log.md`を同期する。raw handoffはrepository外temporary locationへ置き、例外的なrepository-local
scratchは[[sdd-plan-ownership-alignment|current alignment spec]]のreason / ignore gateに従う。

## Testing Strategy

### Contract tests

- `sdd-implementation`が唯一のuser-facing repository-change skillである。
- Planning Controllerのallowed / forbidden read contractが明示される。
- Research、Spec Synthesis、Plan Authoringがfresh workerへrouteされる。
- workerがparent conversationを継承しない。
- main-session exploration fallbackを持たない。
- Control Returnが短いsemantic fieldsとartifact pathを使う。
- Decision Recordがspec draft内にあり、別ledgerや`CONTEXT.md`を作らない。
- session pressure、manual compaction、word-count validatorをrequired機能にしない。
- old loop skill、scheduler、runtime state、packet schemaへfallbackしない。

### Fresh forward scenarios

1. rough change requestをfresh Research Workerへ渡し、Planning Controllerがsource fileを
   読まず一つのdecision questionへ到達できる。
2. worker reportが長くてもControl Returnはpathとmaterial pointだけを返す。
3. accepted decisionがDecision Recordへ入り、fresh coordinatorが同じ問いを再度
   Humanへ聞かない。
4. new evidenceがaccepted decisionとmaterial conflictした場合だけ問いを再openする。
5. fresh Spec Synthesis Workerがresearch pathsとDecision Recordからcomplete specを作る。
6. fresh Plan Author Workerがapproved specからplanを作り、Planning Controllerがcodeを
   探索しない。
7. required worker capabilityがない場合にmain-session explorationへfallbackしない。

forward scenarioは期待文面の一致ではなく、read ownership、decision authority、
artifact handoff、duplicate-question prevention、scope simplicityを評価する。

## Acceptance Criteria

- change request / incomplete specのrepository探索がfresh workerだけで行われる。
- Planning Controllerがsource code、broad wiki / docs、full diff / outputを直接読まない。
- Planning ControllerがHuman対話、Decision Record、approval、routingに限定される。
- Research、Spec Synthesis、Plan Authoringがそれぞれfresh workerである。
- workerの詳細結果がartifactへ保存され、Control Returnが短い。
- spec draftのConfirmed Decisions / Open Decisionsが唯一のDecision Recordである。
- accepted decisionはmaterial conflictなしに再質問されない。
- stage transition後はcapsuleとcanonical pathから再開できる。
- context telemetry、manual compaction、strict word validatorを追加しない。
- new user-facing skill、custom scheduler、runtime/context schemaを追加しない。
- current Superpowers、planning authority、llm-wiki lifecycle、remote boundaryを維持する。
- Plan Author / independent Plan Reviewer / Plan Readiness Gateがplan method、repair、readinessを所有し、Human plan approvalを要求しない。

## 非目標

- session context使用率の計測。
- 60% / 65% soft trigger、75% hard stop。
- host transcriptの物理的なcompaction実行。
- strict word-count enforcement。
- main-session fallback implementation。
- new retry / resume framework。
- new user-facing research / planning skill。
- old loop runtime / packet / event modelの復活。
- Humanのdecision authorityをworkerへ移すこと。
- push、PR作成、merge、release、live installその他のremote write。

## Stop Conditions

- worker isolationを実現するためにcustom schedulerまたはruntime stateが必要になる。
- Planning Controllerが通常経路でsource codeやbroad repository contentを読む。
- research reportやworker transcriptをdurable wikiの正本にしようとする。
- Decision Recordとは別のplanning ledger / `CONTEXT.md`を作る。
- numerical context controlをrequired correctness gateへ変える。
- workerがHuman approvalまたはmaterial design decisionを確定する。
- current Superpowers lifecycleや`llm-wiki` write boundaryと両立しない。
- remote writeまたはlive mutationが必要になる。

## Migration

- current`sdd-implementation`のinput maturity route、Human approval gate、
  Implementation Stage、knowledge closeout、final reviewを維持する。
- Spec StageとPlan StageへPlanning Controller / worker isolationを追加する。
- `skill-architecture.toml`の`user_facing_skills = ["sdd-implementation"]`と
  `decision_authority = "human"`を維持する。
- historical loop context documentsはnon-executable evidenceのまま保持し、current
  runtime surfaceへ戻さない。
- implementation closeout時にcurrent canonical
  [SDD Implementation Skill 設計](sdd-implementation-skill-design.md)へlanded behaviorを
  統合し、本focused revisionとのcurrent / historical関係を明示する。

## リモート書き込み方針

`local_only`。push、PR、merge、release、live install、issue、comment、project変更は
別途明示承認がない限り実行しない。

## 関連ページ

- [[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]] — 本書のPlan Stageにおけるapproval、artifact、readiness、Human return semanticsと、repository-contained transient destination / write bindingをsupersedeするcurrent source。
- [[sdd-plan-ownership-alignment-implementation-plan|SDD Plan Ownership Alignment 実装計画]] — Plan Stage alignmentのagent-authored execution / integration contract。
- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) — current lifecycle、
  ownership、runtime capability、knowledge checkpointのcanonical baseline。
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md) — Planning Controller、
  supporting worker、Human decision authorityの既存policy。
- [Loop Skill Context Compaction Spec](loop-skill-context-compaction-spec.md) — historical /
  non-executableな旧設計。artifact handoff原則だけを参照し、runtime surfaceは再利用しない。
- [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md)
  — upstream brainstorming、writing-plans、SDD ownershipの調査。

## 出典

- [SDD Implementation Skill 設計](sdd-implementation-skill-design.md)
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md)
- [Loop Skill Context Compaction Spec](loop-skill-context-compaction-spec.md)
- [sdd-implementation SKILL.md](../../../skills/sdd-implementation/SKILL.md)
- [skill-architecture.toml](../../../skill-architecture.toml)
