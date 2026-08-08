---
title: llm-wiki authoring 責務分離仕様
date: 2026-07-30
tags:
  - llm-wiki
  - skill-architecture
  - obsidian
  - specification
aliases:
  - llm-wiki structural-only specification
  - llm-wiki authoring discovery diagnostics specification
---

# llm-wiki authoring 責務分離仕様

## 状態

2026-07-30にHumanは基礎となるauthoring責務分離をWritten Specとして承認し、
その実装は同日のcloseoutまで完了した。この既承認decisionと実装履歴は維持する。

2026-08-08にHumanはauthoring discovery diagnosticsのfocused revisionをWritten Specとして承認した。
本書の「Authoring discovery diagnostics focused revision」はHuman-approved / currentである。
Plan Stage、production contract変更、remote writeは別の承認まで未実施であり、
`skills/llm-wiki/SKILL.md`、`skills/llm-wiki/references/core.md`、validator、test、runtime stateは
この承認記録では変更しない。

### Retained baselineの時間的scope

以下の「問題」から「実装状態」までと、focused revision後の「責務境界」から末尾の
「Stop conditions」までは、2026-07-30に承認したpre-migration problem、decision、
migration contract、implementation historyを当時の意味のまま保持するbaseline evidenceである。
その中の「現行」「このmigration」「本仕様作成時点」という表現は2026-07-30時点を指し、
2026-08-08のcurrent checkoutまたはcurrent contractを記述しない。current interpretationは、
同じcheckoutのlocal contract、current production contract、current approved specを照合して決める。
今回のfocused revisionだけがHuman-approved / currentなoperative deltaである。Plan Stageへは
別のHuman承認まで進まない。

## 問題

2026-07-30のmigration前の `llm-wiki` は、durable wiki の topology、authority、routing、lifecycle と、Markdown / Obsidian の記法、frontmatter、link、見出し、表示形式を同じ contract、reference、mode、template で所有していた。この混在により、authoring skill と責務が重複し、knowledge root の local rule と選択した authoring profile が衝突し、profile を切り替えても `llm-wiki` 側の syntax policy が出力を上書きできる状態だった。

この仕様は `llm-wiki` を durable knowledge の structural / lifecycle coordinator に限定し、文書の serialization を knowledge root が選択した authoring skill へ委譲する。semantic template / page schema は `llm-wiki` に残し、Markdown の具体表現は残さない。

## Goals

1. `llm-wiki` の所有範囲を durable wiki structure、topology、authority、routing、page lifecycle、canonicalization、index/log invariant に限定する。
2. Markdown / Obsidian の syntax、format、frontmatter serialization、internal link、callout、embed、presentation を applicable authoring skill の単一責務にする。
3. knowledge root が authoring profile と必要 capability を local に宣言し、active skill discovery で解決できる portable handoff contract を定義する。
4. semantic schema と serialization を分離し、page type や必須の意味項目を失わずに authoring profile を交換可能にする。
5. この repository の `obsidian` profile への移行を完了し、internal note link を wikilink、external URL を standard Markdown link に統一する。
6. capability 不足、曖昧な解決、validation failure では durable write を開始しない fail-closed behavior を保証する。

## Non-goals

- `raw/` の source material を変更すること。
- `llm-wiki` が CommonMark、GFM、Obsidian syntax の実装や解説を持つこと。
- authoring skill 固有の callout、embed、CSS、presentation 機能を必須化すること。
- owner、read/write boundary、draft-review、canonicalize action、index/log の意味論を変更すること。
- runtime、model、provider、agent 固有の discovery metadata を portable contract に入れること。
- migration と無関係な wiki 本文の内容修正、page rename、merge、split、archive、rehome を行うこと。
- authoring skill の代替として `llm-wiki` 内に fallback renderer を残すこと。

## Confirmed Decisions

1. `llm-wiki` が所有するのは durable wiki structure、topology、ownership / write authority、`raw/` / `wiki/` / draft routing、page lifecycle、canonicalization modes、index/log invariants のみとする。
2. Markdown と Obsidian の syntax、formatting、frontmatter serialization、internal-link syntax、callout、embed、presentation は applicable installed authoring skill が所有し、`llm-wiki` に複製しない。
3. knowledge root は authoring profile / capability を local に宣言または選択する。local `AGENTS.md` は repository 固有の本文言語や compatibility requirement を宣言できるが、authoring syntax を再記載しない。
4. この repository は `obsidian` authoring profile を選択する。internal note link は relative Markdown link から Obsidian wikilink へ移行し、external URL は standard Markdown link のまま維持する。
5. 責務重複を防ぐため、この boundary と migration を採用する。

## Open Decisions

なし。

## 実装状態

2026-07-30、[[llm-wiki-authoring-responsibility-separation-implementation-plan|llm-wiki authoring 責務分離実装計画]]は`Implemented / closeout verified`となった。実装は本仕様のauthoring responsibility boundaryを変更せず、`llm-wiki`のstructural / lifecycle coordinationとselected authoring skillのserialization責務をそのまま維持する。

final whole-branch reviewの3件のImportant findingに対する一回のfix waveでは、portable output / recovery stateとauthority-scoped edit capability、5つのlegacy templateのcreation / last-update semantic identity、adapter-resolved cross-root target identityのsyntax-neutral ownershipを補完した。product boundaryとacceptance criteriaは変更していない。focused RED/GREENとfull fresh verificationは完了したが、Step 7のfresh whole-branch re-reviewはcontroller-owned gateとしてpendingであり、`LOCAL_COMPLETE`は宣言しない。

2026-08-08、Authoring discovery diagnostics focused revisionのreviewed Task 1 commit
`f40a164e4c4fac1988b1ff98929fc829713fc572`により、`skills/llm-wiki/SKILL.md`と
`skills/llm-wiki/references/core.md`の二つだけからなるdocs-only contractがlandedした。
Authoring Profileのsemantic selector、evidence-bearing discovery `BLOCKED`、current-state
precedenceを確認し、pre-edit REDとpost-edit GREENのpressure gateは完了した。prompt / resultは
ignored execution evidenceのままとし、repository-specificなmappingはgeneric contractの外に保つ。
final whole-branch reviewはpendingである。

## Authoring discovery diagnostics focused revision

### 問題設定

現行portable contractは、selected Authoring Profileからexactly one applicableかつreadableな
authoring `SKILL.md`をexisting skill discoveryで解決すると定める。一方、Authoring Profileの
値とskill IDの関係、およびdiscovery failure時の最小evidenceは明記していない。そのため、
semantic profile `obsidian`をexact skill IDとして検索して、differently namedな
`obsidian-markdown`だけが見つかった状態をmissingと誤判定したり、候補と判定根拠を示さず
`BLOCKED`を返したりできる。

また、append-only logやsuperseded specを広く検索すると、現行contractから削除済みの
relative Markdown link ruleが見つかる。current local contractとcurrent approved specを
同じcheckoutで確認せずにhistorical evidenceを採用すると、既に移行済みのruleを再提案できる。

### Focused goals

1. Authoring Profileをportableなsemantic selectorとして明文化し、profile名とskill IDの
   text equalityをdiscovery preconditionにしない。
2. discovery起因の`BLOCKED`を、抽出したprofile、Compatibility Requirement、候補、
   exact causeを持つevidence-bearing resultにする。
3. local-contract mutationの提案前に、current local contract、current approved spec、
   current checkoutを比較するprecedence guardを明文化する。
4. 既承認のstructural / lifecycle coordinatorとauthoring serializationの責務境界、
   runtime-neutral discovery、fail-closed write boundaryを変更せずに再発余地だけを閉じる。

### Focused non-goals

- validator、test、runtime resolver、host adapter、executable codeを追加または変更すること。
- sidecar、manifest、candidate registry、runtime state、structured discovery metadataを新設すること。
- local contractのprofile値をexact skill IDへrenameすること。
- `knowledge/AGENTS.md`へgeneric discovery ruleまたはauthoring syntaxを複製すること。
- `obsidian`から`obsidian-markdown`への対応をportable selectorのhardcoded mappingにすること。
- Obsidian wikilinkまたはexternal Markdown linkのsyntaxをportable `llm-wiki` contractが所有すること。
- historical log、superseded spec、raw source、siblingまたはolder worktreeをcurrent ruleへ昇格すること。
- visual artifactを作成すること。

### Focused Confirmed Decisions

1. Authoring Profileはsemantic selectorであり、local contractが明示的にexact ID semanticsを
   宣言しない限り、その文字列はskill IDと一致する必要がない。name mismatchだけでは
   missingまたはincompatibleと判定しない。
2. applicable candidateは、抽出したAuthoring Profile、Compatibility Requirement、
   requested authoring operationを、discoveryされたreadable `SKILL.md`のdocumented scopeと
   手順に照合して判定する。portable contractはhost固有のdiscovery tool名やcandidate schemaを
   規定しない。
3. discovery起因の結果statusは常に`BLOCKED`とし、少なくとも次を報告する。
   - local contractから抽出したAuthoring Profile。
   - local contractから抽出したCompatibility Requirement。
   - discoveryを実行できた場合は、観測したcandidate authoring skillのidentity一覧と、
     `missing`、`ambiguous`、`incompatible`、`unreadable`のいずれかのcandidate outcome、
     およびそのoutcomeを候補へ適用した具体的理由。
   - discovery自体を実行できなかった場合は、candidate outcomeとは別のdiagnostic conditionとして
     `discovery unavailable`を明記し、discoveryを妨げた具体的理由をexact causeとして報告する。
     candidate setは`unobserved`とし、missing、ambiguous、incompatible、unreadableのいずれにも
     推論または分類しない。

`discovery unavailable`は新しいresult status、lifecycle state、candidate outcome、host-specific
schemaではない。`BLOCKED`のまま、candidateを観測できなかった理由を正直に表すcause evidenceである。
4. local contractのmutationを提案する前に、同じcurrent checkout上のlocal contract、
   current approved specが存在する場合はそのspec、変更対象のcurrent file stateを比較する。
   historical spec、old memory、append-only history、siblingまたはolder worktreeのruleは
   provenanceとして参照できるが、current contractをoverrideできない。
5. このrepositoryでは、current local contractのsemantic profile `obsidian`に対し、
   current discoveryで得たreadable `obsidian-markdown`がdocumented scopeとCompatibility
   Requirementを満たす。これはcurrent repository evidenceであり、portable hardcoded mappingではない。
6. このrepositoryのinternal noteがwikilink、external URLがstandard Markdown linkとなる
   current behaviorは、local Compatibility Requirementとdiscovered `obsidian-markdown`の
   documented procedureによる。generic selectorへこのsyntax ruleを持ち込まない。

### Focused Open Decisions

なし。

### Portable contract delta

後続implementationは、既存のdiscovery orderとwrite前のfail-closed boundaryを維持したまま、
次の意味だけをportable proseへ追加する。

1. local contractからAuthoring ProfileとCompatibility Requirementを抽出する。
2. Authoring Profileをsemantic selectorとして扱い、profile文字列とskill IDのequalityではなく、
   profile、Compatibility Requirement、requested operationとcandidateのdocumented contractを照合する。
3. applicableかつreadableなcandidateが一意なら既存handoffへ進む。
4. discoveryを実行できたが一意に解決できなければdurable write前に停止し、観測候補、
   4つのcandidate outcomeの一つ、具体的理由を`BLOCKED`へ含める。discoveryを実行できなければ、
   candidateを推論せず、`discovery unavailable`、`unobserved`なcandidate set、実行不能のexact causeを
   `BLOCKED`へ含める。
5. local-contract mutation案を作る場合はFocused Confirmed Decision 4のcurrent-state comparisonを
   先に行い、historical evidenceだけを根拠にcurrent ruleを置換しない。

このdeltaはdiscovery engineを実装せず、active runtimeのexisting skill discoveryを引き続き利用する。
「semantic selector」はcandidate適用判定のcontractであり、新しいresolver、registry、alias table、
capability ID、machine-readable outputを意味しない。

### Exact affected surfaces for the focused revision

Written Spec承認後のimplementation対象は次のportable documentation surfaceだけとする。

- `skills/llm-wiki/SKILL.md`
- `skills/llm-wiki/references/core.md`

durable lifecycle同期として、本canonical spec、[[index|durable catalog]]、append-only
`knowledge/log.md`をimplementation stateへ更新する。`knowledge/AGENTS.md`、mode reference、
topology reference、template、validator、test、script、workflow、runtime fileは変更対象外とする。
追加surfaceが必要ならscopeを自動拡張せず、Written Specへ戻ってHumanの再承認を得る。

### Focused acceptance criteria

1. `SKILL.md`と`references/core.md`がAuthoring Profileをsemantic selectorと明記し、
   profile / skill IDのname mismatchだけをfailureにしない。
2. candidate applicabilityがprofile、Compatibility Requirement、requested operationとreadableな
   documented skill contractの照合で決まり、host固有discovery metadataを正本にしない。
3. discovery起因の全`BLOCKED`がprofileとCompatibility Requirementを持つ。discovery実行済みなら
   candidate一覧、4つのcandidate outcomeの一つ、具体的理由を持つ。discovery実行不能なら
   `discovery unavailable`、`unobserved`なcandidate set、実行不能のexact causeを持ち、
   4つのcandidate outcomeへ誤分類しない。
4. current local contract、current approved spec、current checkoutの比較がlocal-contract mutation
   proposalより先に要求され、historical evidenceだけではcurrent ruleをoverrideできない。
5. `obsidian`からcurrent discovered `obsidian-markdown`へのmappingとcurrent wikilink behaviorが
   repository-specific evidenceとして残り、portable hardcoded ruleにならない。
6. diffが2つのportable documentation surfaceとdurable spec/index/log同期だけに限定され、
   validator、test、runtime resolver、code、新runtime metadataを含まない。
7. Written Spec承認前にPlan Stageまたはimplementationへ進まず、production contractを変更しない。

### Focused stop conditions

- semantic selectorをexact-name alias tableまたはruntime resolverとして実装する必要が生じる。
- evidence-bearing `BLOCKED`のためにhost固有schemaまたは新runtime metadataが必要になる。
- current checkoutのlocal contract、または存在するcurrent approved specを確認できないまま
  mutationを提案する。
- repository-specific mappingまたはwikilink behaviorをgeneric portable ruleへ昇格する必要が生じる。
- exact affected surfaces外のproduction file、validator、test、codeを変更する必要が生じる。
- HumanのWritten Spec承認前にPlan Stageへ進む必要が生じる。

以下の責務境界から末尾のStop conditionsまでは、冒頭の「Retained baselineの時間的scope」が
定める2026-07-30のhistorical baselineである。その既承認decisionは維持するが、同sectionにある
当時のaffected surfaces、test追加、migration順序を今回のfocused revisionの実装scopeとして
再実行しない。focused revisionのscopeとacceptanceは直前のfocused sectionを正本とする。

## 責務境界

| Surface | `llm-wiki` の責務 | authoring skill の責務 | local knowledge contract の責務 |
|---|---|---|---|
| root / topology | knowledge root、single/multi-root、scope、root identity、cross-root target の解決 | 解決済み target の表現 | repository の topology と root 固有条件の宣言 |
| authority / routing | owner、read/write boundary、draft target、`raw/` immutable、durable artifact の保存先 | なし | local owner と write boundary の宣言 |
| page model | page type、topic boundary、semantic field、relation、lifecycle state、canonical target | schema を選択 profile の文書へ serialization | 本文言語など repository 固有の semantic requirement |
| template | syntax-neutral な semantic template / page schema | headings、lists、tables、properties、link 等を含む具体文書の生成 | profile と required capability の選択 |
| links | internal / external / cross-root という relation kind と target identity | wikilink、Markdown URL 等の syntax | repository 固有 compatibility requirement |
| citations | provenance の要否、source identity、claim との semantic relation | citation section、footnote、link 等の表現 | repository 固有の必須 provenance 条件 |
| lifecycle | ingest、query filing、draft-review、canonicalize、lint の状態遷移 | lifecycle operation が要求した文書 edit の表現 | local override が許す操作 |
| discovery | local contract の selected profile と requested operation を active runtime の既存 skill discovery へ渡し、適用可能な skill の readable な文書契約を解決する | 自身の `SKILL.md` で authoring scope と手順を文書化する | authoring profile と compatibility requirement の宣言 |
| index / log | active catalog と append-only audit の意味論、更新要否、同期完了条件 | entry / table / properties の serialization | local catalog shortcut など semantic requirement |
| presentation | なし | callout、embed、layout、rendering compatibility | 必要な compatibility level の宣言のみ |
| validation | semantic field / relation の保存、authority、path、bounded write set、index/log effect の検査 | 自身の文書化された手順に従う Markdown / Obsidian syntax、profile conformance、rendering compatibility の確認 | required compatibility level の宣言 |

### Semantic schema と serialization の seam

`llm-wiki` の schema は、少なくとも page type、purpose、required / optional semantic fields、relation kind、lifecycle state、discoverability metadata、provenance requirement、index/log effect を表現する。field をどの heading、property、table、list、link syntax で表すかは schema に含めない。

orchestrating workflow は schema と content payload を selected authoring skill の文書化された手順へ渡し、semantic field を欠落・改名せず、選択 profile に適合する文書 edit を作る。authoring skill には通常の成功 / 失敗以外の machine-readable result、sidecar、manifest を要求しない。`llm-wiki` は生成された serialization を再整形せず、Markdown / Obsidian parser、regex、formatter による syntax の解析や再検証も行わない。

## Portable skill contract

### Inputs

- `operation`: `bootstrap`、`ingest`、`query`、`draft-review`、`canonicalize`、`lint` のいずれか。
- `knowledge_root` と解決済み topology context。
- actor と authority context。
- source / query / review / canonicalization の operation payload。
- local knowledge contract に宣言された selected authoring profile と compatibility requirement。
- 対象 page type の syntax-neutral semantic schema。
- existing document state と target relation identity。

### Outputs

- authority と routing を満たす operation result。
- selected authoring skill の文書化された手順に従って作成または変更された文書。
- index/log の required sync set と、その完了または未実施状態。
- 通常の operation success、または write 前に停止した `BLOCKED`。実行途中の検査失敗では未完了として exact changed-file set と失敗した check を報告する。

### Required capabilities

- knowledge root と declared read-set を読み取る capability。
- authority が許す範囲だけに durable file edit を適用する capability。
- active runtime の既存 skill discovery から selected profile と requested authoring operation に適用可能な skill を解決し、その `SKILL.md` を読める capability。
- selected authoring skill の文書化された contract に従い、semantic schema を profile-compatible document へ lossless に serialization し、その skill が指示する確認を実行する capability。
- Markdown / Obsidian syntax を解釈せず、semantic field / relation preservation、authority、path、bounded write set、index/log effect だけを検証する capability。

この repository の local contract は `knowledge/AGENTS.md` で `obsidian` profile、日本語本文、Obsidian compatibility を宣言する。現行 active runtime が discovery できる `obsidian-markdown` の readable な `SKILL.md` は、[Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown) の作成・編集、properties、wikilink、external link、reading view 確認を文書化しているため、この repository の authoring operation に適用可能である。standard Markdown は同 skill の前提知識として扱い、別 capability ID や manifest を新設しない。外部 installed `obsidian-markdown` skill はこの migration の変更対象外である。

## Authoring skill discovery と fail-closed behavior

1. read-only query 以外で authoring operation が必要になった時点で、local `AGENTS.md` の selected profile と requested operation を active runtime の既存 skill discovery へ渡す。
2. discovery された候補の portable `SKILL.md` を読み、description、documented scope、workflow、inputs / outputs / required capabilities が宣言されている場合はそれらを含む文書契約が selected profile と requested operation に適用できるか確認する。optional UI metadata、filesystem 固有 path、新しい sidecar は discovery の正本にしない。
3. applicable skill を一意に解決して instruction を読めた場合だけ authoring を開始する。候補がない、曖昧、instruction を読めない、または documented contract が requested operation を覆わない場合は `BLOCKED` を返し、page / index / log を書かない。
4. selected authoring skill の手順に従って文書を作成・編集し、その skill が指示する通常の確認を実行する。失敗した場合は completion を宣言しない。skill 固有の structured result、validation JSON、capability manifest は要求しない。
5. `llm-wiki` は semantic field / relation preservation、authority、path、bounded write set、index/log effect だけを確認し、Markdown / Obsidian syntax の解析・検証・fallback rendering を行わない。

read-only query は authoring skill が未解決でも、durable output を生成しない範囲で回答材料を収集できる。ただし file-back、query note 作成、log 記録を伴う時点で discovery が必須となる。

## Control flow

1. mode と topology を解決し、authority と write target を検証する。
2. local contract から authoring profile、本文言語、compatibility requirement を解決する。
3. active runtime の既存 discovery と readable な skill contract から authoring skill を一意に解決し、`BLOCKED` 時は write 前に停止する。
4. `llm-wiki` が page type と semantic schema、routing、lifecycle effect、index/log sync set を決める。
5. orchestrating workflow が selected authoring skill の手順に従って document edits を作成し、同 skill が指示する確認を行う。
6. `llm-wiki` が structural / lifecycle invariant と required index/log sync を検査する。
7. operation の通常の success / failure を返す。

### Repository migration の write safety

この migration は planning worktree 内だけで実施する。implementation plan は着手前に、変更・追加する repository-relative file を wildcard なしの explicit write set として列挙する。実装中に追加 target が必要になった場合は plan の write set を更新して scope を再確認してから編集する。unexpected dirty file、`raw/**`、scope 外 file が含まれる場合は停止する。

Human-approved execution-policy override により、spec / plan correction 自体を先に commit し、Task 1、Task 2、Task 3 は各々 implement、scoped verification、scoped commit、実装者とは別の fresh reviewer による independent task review の順に完了する。Task 4 は durable knowledge closeout、full fresh verification、selected `obsidian-markdown` skill-directed authoring review、exact approved-write-set assertion、一件の scoped closeout commit、post-closeout whole-branch review を行う。SDD review loop が修正を要求した場合、Task 4 は必要な scoped review-fix commit を追加でき、各fixを実装者とは別のfresh reviewerが独立re-reviewする。この追加はTask 4のexecution historyだけを変更し、product responsibility boundaryは変更しない。Task 1–3のreviewed commitsはamend、squash、revertしない。review または check が失敗した task は次へ進めず、修正 commit と scoped re-review を行う。isolated worktree と task-scoped Git history を recovery boundary とし、exact changed-file set、review package、report、failing check を残して repair と再検証を可能にする。generic transaction subsystem、recovery bundle、custom lifecycle state、commit に連動する runtime completion state は導入しない。

この override は execution order、commit / review gate、recovery policy だけを変更する。Goals、Non-goals、Confirmed Decisions、責務境界、semantic schema と serialization の seam は変更しない。

## Failure handling

- authority、root、draft target、canonical target が未解決なら structural `BLOCKED` とし、authoring discovery を開始しない。
- applicable authoring skill が未検出、曖昧、unreadable、または requested operation に非適合なら `BLOCKED` とし、durable file を変更しない。
- semantic schema を profile に lossless serialization できない場合は schema / profile incompatibility として停止する。
- selected authoring skill が指示する authoring check が失敗した場合は未完了として停止し、`llm-wiki` 自身では syntax を判定しない。
- internal link target が一意に解決できない場合は link を推測せず停止する。
- external URL は migration で書き換えない。URL と link label の保持を検証する。
- `raw/` への write が write set に含まれた場合は操作全体を拒否する。
- index/log invariant を同じ operation で満たせない場合は durable change の完了を宣言しない。
- task-scoped check または independent review が失敗した場合は後続 task に進まず、isolated worktree と直前の task commit を recovery boundary として repair、再検証、再レビューする。Task 4 の pre-commit closeout check が失敗した場合は closeout commit を作らず、post-commit review が修正を要求した場合はscoped review-fix commitを追加して独立re-reviewする。Task 1–3のreviewed commitsはamend、squash、revertしない。

## Exact affected surfaces

### Public skill contract

- `skills/llm-wiki/SKILL.md`
- `skills/llm-wiki/DESCRIPTION.md`
- `skills/llm-wiki/agents/openai.yaml`
- `skills/llm-wiki/context-contract.toml`

これらから generic Markdown / relative-link / 日本語 formatting ownership を除き、portable Inputs、Outputs、Required Capabilities、existing skill discovery、fail-closed boundary を公開する。optional UI metadata は behavior や discovery の正本にしない。新しい authoring contract sidecar は追加しない。

### Structural references と mode

- `skills/llm-wiki/references/core.md`
- `skills/llm-wiki/references/single-root.md`
- `skills/llm-wiki/references/multi-root.md`
- `skills/llm-wiki/references/structure.md`
- `skills/llm-wiki/references/page-authoring.md`
- `skills/llm-wiki/references/optional-tooling.md`
- `skills/llm-wiki/references/modes/bootstrap.md`
- `skills/llm-wiki/references/modes/ingest.md`
- `skills/llm-wiki/references/modes/query.md`
- `skills/llm-wiki/references/modes/draft-review.md`
- `skills/llm-wiki/references/modes/canonicalize.md`
- `skills/llm-wiki/references/modes/lint.md`

`page-authoring.md` の page boundary、canonical page、relation / provenance requirement は structural reference に保持または移設し、syntax / formatting 部分は削除する。`optional-tooling.md` の authoring tool guidance は `llm-wiki` の contract から外す。各 mode は concrete template を直接読まず、semantic schema と discovered authoring skill へ route する。

### Schema と assets

- `skills/llm-wiki/assets/templates/AGENTS.md`
- `skills/llm-wiki/assets/templates/root-AGENTS.md`
- `skills/llm-wiki/assets/templates/root-registry.md`
- `skills/llm-wiki/assets/templates/index.md`
- `skills/llm-wiki/assets/templates/log.md`
- `skills/llm-wiki/assets/templates/source-summary.md`
- `skills/llm-wiki/assets/templates/entity.md`
- `skills/llm-wiki/assets/templates/concept.md`
- `skills/llm-wiki/assets/templates/synthesis.md`
- `skills/llm-wiki/assets/templates/query-note.md`
- `skills/llm-wiki/assets/templates/draft-note.md`
- `skills/llm-wiki/assets/templates/implementation-progress-ledger.md`

完成 Markdown template は `llm-wiki` の canonical asset ではなくする。各 asset から page type、semantic field、lifecycle state、relation、index/log effect を syntax-neutral schema として抽出し、authoring skill が profile ごとの文書を生成する。thin router template は authoring profile / capability の宣言 slot を semantic field として持つが、wikilink や frontmatter の書き方は説明しない。

### Repository-local contract と durable knowledge

- `knowledge/AGENTS.md`
- `knowledge/wiki/**/*.md`
- `knowledge/index.md`
- `knowledge/log.md`
- [[llm-wiki-draft-review-and-canonicalize-goal-spec]]
- [[skill-repository-optimization-v4-spec]]

`knowledge/AGENTS.md` は `obsidian` profile、日本語本文、Obsidian compatibility requirement だけを local difference として宣言し、relative Markdown link の canonical rule と wikilink 禁止を削除する。別 profile manifest は追加しない。既存 canonical spec はこの仕様により supersede される authoring ownership を明示し、structural/lifecycle decision は保持する。`raw/**` は migration 対象外とする。

[[llm-wiki-draft-review-and-canonicalize-goal-spec]] の concrete page serialization、link notation、frontmatter guidance と、[[skill-repository-optimization-v4-spec]] の `llm-wiki` authoring contract / context guidance における同じ ownership clause は、この仕様が supersede する。両仕様の draft-review / canonicalize、context contract、lifecycle、historical acceptance evidence の決定は保持する。

### Validators、tests、CI

- `skills/llm-wiki/tests/test_context_contract.py`
- `scripts/validate_skill_context.py`
- `scripts/report_skill_context.py`
- `scripts/validate_skill_architecture.py`
- `.github/workflows/skill-architecture.yml`
- `skills/llm-wiki/tests/test_authoring_boundary.py`

implementation plan は上記候補と実際の migration target を照合し、具体的な write set を file 単位で固定する。既存 validator scripts は command surface として利用し、責務分離に変更が不要なら編集対象へ含めない。

## Migration

1. 現行 template と reference から semantic field / lifecycle requirement と Markdown serialization rule を inventory 化し、各項目を一方の owner に割り当てる。未割当または二重割当があれば停止する。
2. `llm-wiki` の portable Inputs / Outputs / Required Capabilities と、local `AGENTS.md` の `obsidian` profile selection を更新し、existing discovery / fail-closed boundary test を先に作る。
3. syntax-neutral schema を既存 skill contract / reference 内に導入し、現行 template の全 semantic field が lossless に対応することを確認する。新しい schema sidecar は作らない。
4. `SKILL.md`、core / topology / structure / page boundary、各 mode から syntax ownership と concrete authoring examples を除き、schema-to-authoring handoff に置き換える。
5. `knowledge/AGENTS.md` を `obsidian` profile selection へ変更する。repository 固有の日本語本文と compatibility requirement は保持するが、wikilink syntax 自体は再記載しない。external installed `obsidian-markdown` は変更しない。
6. implementation plan で explicit write set を inventory してから、その集合に含まれる `knowledge/wiki/` pages、`knowledge/index.md`、`knowledge/log.md` の internal note link を wikilink に変換する。external URL は standard Markdown link のまま保持し、`raw/**` は変更しない。既存 `knowledge/log.md` entry は対象 internal link がない限り書き換えない。
7. llm-wiki の concrete Markdown templates を semantic schema へ置換し、installed `/Users/omitsuhashi/.agents/skills/obsidian-markdown/SKILL.md` を全部読んだ fresh read-only authoring reviewer が、exact maintained-note / template write set を同 skill の手順に照らして確認する。Obsidian reading-view control が active runtime にない場合はその capability limitation を report に明記し、static skill-directed review を最強の利用可能な evidence とする。repository text test を rendered proof と扱わない。
8. 既存 durable spec の authoring ownership を superseded として同期し、index/log を migration の durable change として最後に更新する。
9. selected authoring skill-directed review と repository validator / test suite を fresh に実行し、semantic field loss、duplicate ownership、read-set drift がないことを確認する。authoring syntax の判定は `llm-wiki` test / validator に実装しない。
10. Tasks 1–3 は各 scoped check 成功後に scoped commit と independent task reviewを完了し、Task 4 は closeout edit と全 fresh check 成功後に一件のscoped closeout commitを作成する。後続SDD review loopが修正を要求した場合だけscoped review-fix commitを追加し、各fixを独立re-reviewする。これはexecution historyだけの変更でありproduct responsibility boundaryを変更せず、Task 1–3のreviewed commitsをamendまたはsquashしない。
11. closeout commit 後、approved baseline `f23bde7` から `HEAD` までの SDD review package を作成し、fresh な most-capable reviewer に code、tests、approved spec / plan、knowledge artifacts の whole-branch review を依頼する。blocking finding が解消されるまで implementation complete を宣言しない。

各段階は同じ migration branch で行い、profile declaration と authoring capability が利用可能になる前に local link policy を切り替えない。2026-07-30の基礎仕様作成時点では `knowledge/index.md` と `knowledge/log.md` を更新しない、という当時のmigration sequencingであった。

## Tests and validators

### Contract tests

- `llm-wiki` が non-empty Inputs、Outputs、Required Capabilities を portable contract として公開する。
- local authoring profile が operation read-set から解決され、runtime 固有 metadata や sidecar manifest に依存しない。
- structural reference に frontmatter、wikilink、relative Markdown link、callout、embed、presentation の canonical syntax instruction が残っていない。
- semantic schema の全 field に owner が一つだけ存在し、serialization field を含まない。

### Discovery / failure tests

- active discovery で selected profile と requested operation に applicable な skill が一意に解決され、その `SKILL.md` を読めた場合だけ handoff が実行される。
- skill missing、ambiguous、incompatible、instruction unreadable の各 case で write 前に `BLOCKED` となる。
- authoring result が semantic field を欠落させた場合、validation が durable write 前に失敗する。
- authoring skill が指示する check の failure が completion failure として伝播し、`llm-wiki` 内に syntax checker や structured validation result を要求しない。
- read-only query は write を伴わない範囲で動作し、file-back 時に discovery gate を通る。

### Profile integration tests

- selected authoring skill の文書化された手順で、`obsidian` profile の internal note link は wikilink、external URL は standard Markdown link になることを確認する。
- properties の serialization と Obsidian reading view compatibility を selected authoring skill の手順で確認する。
- actual Obsidian reading-view rendering capability が利用できない場合は、authoring review report に `unavailable` と理由を記録し、skill-directed static review のみを主張する。repository test / validator の成功を rendering evidence として代用しない。
- required semantic field、relation、provenance、lifecycle state、index/log effect が round-trip で保持される。
- unknown または ambiguous internal target を推測して link 化しない。

### Migration tests

- `test_authoring_boundary.py` は ownership declaration、operation read-set routing、`llm-wiki` structural surfaces に duplicated syntax policy がないことだけを検証する。Obsidian Markdown を parse / validate しない。
- migration 前後で semantic field、relation、provenance、external URL と label、index/log effect が保持される。
- `git diff --name-only` が implementation plan の explicit write set 内であり、`knowledge/raw/**` と external installed skill path を含まない。
- legacy template の semantic field と新しい syntax-neutral schema の field 集合が一致する。

### Required verification

- `python3 -m unittest discover -s skills/llm-wiki/tests -v`
- `python3 scripts/validate_skill_context.py --skill skills/llm-wiki --json`
- `python3 scripts/report_skill_context.py --skill skills/llm-wiki --json --fail-on-warning`
- `python3 scripts/validate_skill_architecture.py --all`
- `python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-wiki`
- `python3 -m unittest discover -s skills/llm-wiki/tests -p 'test_authoring_boundary.py' -v`
- `git diff --check f23bde7..HEAD`
- `git diff --check`

全 command は exit `0` を success、non-zero を failure とする。`test_authoring_boundary.py` は ownership declaration、read-set routing、duplicated `llm-wiki` syntax policy の不在だけを検証し、Markdown / Obsidian syntax parser、renderer、formatter を実装しない。syntax / profile correctness は selected authoring skill の文書化された確認へ委ね、その通常の success / failure を orchestration が扱う。

## Acceptance criteria

1. responsibility table の各責務に owner が一つだけあり、`llm-wiki` に Markdown / Obsidian serialization rule が残っていない。
2. `llm-wiki` の public contract に Inputs、Outputs、Required Capabilities と write 前の `BLOCKED` boundary が明記され、runtime 固有 dependency や新しい sidecar manifest を要求しない。
3. page type と template の semantic field が syntax-neutral schema に保持され、legacy template との lossless mapping が test で証明される。
4. knowledge root が profile と compatibility requirement を local `AGENTS.md` で選択でき、syntax を local router に複製しない。
5. この repository の `obsidian` profile に applicable な installed skill が active discovery と readable `SKILL.md` contract から一意に解決され、internal link は wikilink、external URL は standard Markdown link となる。external skill の変更、structured result、新 manifest を要求しない。
6. missing / ambiguous / incompatible / unreadable authoring skill の全 case で write 前に fail closed する。
7. six modes が authority、routing、lifecycle、index/log invariant を維持しながら、serialization を discovered authoring skill に委譲する。
8. `raw/**` が不変で、migration 前後の external URL と semantic field が保持される。
9. affected surface の legacy authoring rule が削除または superseded として同期され、duplicate ownership validator が通る。
10. installed `/Users/omitsuhashi/.agents/skills/obsidian-markdown/SKILL.md` を source of instructions とする fresh read-only authoring review、current llm-wiki tests、context / architecture validators、skill-creator validator、boundary test、baseline range と working tree の diff check が fresh run で成功する。actual Obsidian reading-view rendering が利用不能な場合は limitation を report し、rendered proof を主張しない。
11. implementation plan の literal approved write set だけが `f23bde7` 以降に変更され、Task 1–3 の各 scoped commit / independent review と Task 4 の一件のscoped closeout commitが完了する。SDD review loopが要求するscoped review-fix commitは追加できるが、各fixは独立re-reviewを必須とし、Task 1–3のreviewed commitsをamendまたはsquashしない。失敗時は isolated worktree と Git history から task 単位で repair 可能な状態を保持する。
12. closeout commit 後、`f23bde7` から `HEAD` までの SDD review package を fresh な most-capable reviewer が whole-branch review し、blocking finding がない。

## Stop conditions

- local knowledge contract が authoring profile と compatibility requirement を明確に宣言できない。
- selected profile と requested operation に applicable な skill を active discovery で一意に解決して `SKILL.md` を読めない。
- semantic schema と現行 template の対応で field loss、owner 不明、duplicate owner が見つかる。
- migration 対象の internal link target が一意に解決できない。
- external URL、provenance、lifecycle state、index/log invariant のいずれかを保持できない。
- authority のない canonical page、write-closed root、`raw/**` への変更が必要になる。
- profile switch と link migration を coherent write set として検証できない。
- implementation が runtime / model / provider / agent 固有 metadata を portable contract の正本にする必要がある。
- implementation plan の explicit write set 外、external installed skill、または新しい sidecar manifest の変更が必要になる。
- selected authoring skill の文書化された確認または repository check が失敗する。この場合は commit せず isolated worktree diff を repair 対象として保持する。
- fresh required verification が一つでも失敗する。
