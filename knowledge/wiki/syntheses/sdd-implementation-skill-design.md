# SDD Implementation Skill 設計

## 状態

Phase 1 の local implementation と verification は完了済みである。本書は、その後の調査と Human の方向性承認を反映した **Superpowers-first revision の Written Spec 候補**である。

この revision は、`sdd-implementation` の入口を承認済み implementation plan だけに限定せず、spec 定義・精緻化から implementation、knowledge closeout までを一つの開発体験として構成する。production skill の変更、新しい implementation plan、push、PR、merge、release、live install はまだ行っていない。Human が本書を Written Spec として承認した後に、新しい implementation plan を作成する。

## 調査で確認した前提

Superpowers v6.2.0 では、開発フローの責任が次のように分かれている。

- `brainstorming`: requirements、constraints、success criteria、approach、design/spec、Human approval。
- `writing-plans`: 承認済み spec を exact files、tests、verification、commit 単位の実行可能 plan へ変換。
- `subagent-driven-development`: plan preflight、fresh implementer、task review、fix loop、final whole-branch review。

SDD には dispatch ごとの model 選択がすでにあり、全 dispatch に model 指定を要求する。task の complexity / risk に応じた relative capability tier も upstream が所有する。一方、model と独立した Thinking Effort / `reasoning_effort` の選択・伝播・escalation contract はなく、Hermes Agent の公式 host adapter もない。

詳細な evidence は [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) に保存する。

## 問題設定

現行の `sdd-implementation` は承認済み implementation plan から始まるため、spec を定義・精緻化する段階が user-facing flow の外にある。また、repo-local skill が implementer / reviewer の model policy まで所有しており、現行 Superpowers の per-dispatch model selection と責務が重複する。

一方、repository 固有の価値は upstream flow を置き換えることではなく、次の薄い integration にある。

1. spec stage で `Grill with Docs` を使い、一問一答で曖昧さを解消し、domain terminology と decision を明確にする。
2. `llm-wiki` を使い、既存知識の参照と、承認済み spec / plan / closeout の永続化を行う。
3. Superpowers の abstract model tier を各 host の concrete model へ解決し、host が対応する場合だけ reasoning effort を追加する。
4. Codex と Hermes Agent の capability 差を adapter boundary で扱う。

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
       -> repository-required plan review / approval
       -> llm-wiki durable plan sync
  -> Superpowers subagent-driven-development
       -> upstream per-dispatch model selection
       -> repo-local host model resolution
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
- repo-local host adapter は model resolution、optional reasoning effort、dispatch capability mapping だけを所有する。
- runtime ledger、reports、diff、test logs、agent IDs は Superpowers の transient workspace に置き、wiki へ保存しない。

### Review は material finding だけを扱う

task review と final review は、requirements fit、同じ要件をより単純に満たせる material な余地、current change の material risk の順に確認する。

style preference、具体的 failure path のない将来懸念、scope 外 refactor / hardening、軽微な formatting、同等案への好みは blocking finding にしない。mechanical validator、formatter、linter、schema check、required test suite の実行範囲は狭めない。

## Ownership

| Concern | Owner | Repo-local composition |
|---|---|---|
| requirements / design / written spec | Superpowers `brainstorming` + Human | `Grill with Docs` と `llm-wiki` を stage 内で呼ぶ |
| ambiguity resolution / domain sharpening | `Grill with Docs` | 一問一答、decision ごとの合意、用語の明確化 |
| durable knowledge | `llm-wiki` | repository topology、write boundary、index / log に従う |
| executable implementation plan | Superpowers `writing-plans` | repository-required approval と wiki sync を加える |
| implementation / TDD / task review / fix loop | Superpowers SDD | upstream template と lifecycle をそのまま使う |
| dispatch model tier | Superpowers SDD | host の concrete model へ解決するだけ |
| reasoning effort | repo-local host adapter | host が独立制御を提供する場合だけ適用 |
| final review / branch finish | Superpowers | wiki closeout を review 対象 range に含める |

`Grill with Docs` の `domain-modeling` が通常提案する `CONTEXT.md` や `docs/adr/` は、この repository では別の durable store として作らない。repository の `AGENTS.md` と `llm-wiki` write boundary を優先し、恒久的な glossary、ADR、spec、decision は `knowledge/wiki/...` の canonical page に統合する。

## Entry Classification

### Change request だけがある

`brainstorming` へ入り、relevant な knowledge root があれば `llm-wiki` で既存 spec、terms、decision を query する。その後 `Grill with Docs` を必須で使い、material ambiguity を一つずつ解消する。Written Spec を作成して self-review し、Human approval を得るまで planning / implementation へ進まない。

### Spec はあるが未承認または不完全

既存 spec と repository evidence を入力に `brainstorming` を継続する。material ambiguity、未確定 trade-off、acceptance criteria 不足が一つでもあれば `Grill with Docs` を使う。承認済みで完全な部分を無意味に聞き直さない。

### Human-approved spec がある

spec の authority、current applicability、requirements / acceptance criteria の充足を確認する。問題がなければ `Grill with Docs` を再実行せず、`writing-plans` へ進む。material conflict を発見した場合だけ spec stage へ戻す。

### Current spec に binding された承認済み plan がある

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

承認済み spec を Superpowers `writing-plans` に渡し、exact paths、interfaces、test-first steps、verification、commit boundaries を含む executable plan を作る。

Superpowers 自体が要求する spec coverage self-review に加え、repository policy が Execution Plan Gate や Human approval を要求する場合はそれを満たす。承認前の plan を SDD に渡さない。

knowledge root がある場合、承認済み plan を durable page として同期する。plan に concrete model 名、reasoning effort 値、provider、agent ID、run ごとの availability を固定しない。

## SDD Stage

### Upstream model selection

implementer、task reviewer、re-reviewer、final reviewer の model tier は Superpowers SDD の current `Model Selection` contract を正本とする。repo-local skill は別の role-to-model policy tableを持たない。

全 dispatch で upstream が要求する model field を明示する。host adapter は upstream の relative tier を、その実行時に利用可能な concrete model へ解決する。user が runtime model を明示した場合は、その指定を優先する。

### Reasoning effort overlay

reasoning effort は model tier と独立した optional runtime overlay とする。

| Superpowers task class | Abstract effort |
|---|---|
| clear spec の mechanical task、small scoped re-review | low |
| multi-file integration、normal debugging、task review | medium |
| architecture-sensitive / high-risk task、final whole-branch review | high |

fix loop が同じ failure で収束しない場合は、まず available な範囲で effort を一段上げる。それでも不足する場合は、Superpowers の model escalation に従う。user が runtime effort を明示した場合は、その指定を優先する。

host が独立した effort control を提供しない場合は `not_supported` として扱い、Superpowers の model selection だけで継続する。reasoning effort がないことだけを理由に全 flow を block しない。model を明示して isolated dispatch する能力自体がない場合は `BLOCKED` とする。

concrete model、effort、provider、availability、agent ID、run-specific resolution は runtime-only とし、spec、plan、wiki、ledger、schemaへ永続化しない。

### Host adapter

- Codex: isolated subagent dispatch、per-dispatch model、利用可能なら reasoning effort、wait / resume lifecycle を current host capability へ写像する。
- Hermes Agent: upstream の公式 adapter があると仮定せず、fresh worker / reviewer、model selector、effort control、resume lifecycle の actual capability を検出して写像する。
- host-specific tool name や model catalog を共通 `SKILL.md` の durable contract に固定しない。
- required SDD capability を安全に満たせない場合、main session implementation や旧 loop skill へ silent fallback しない。

## Knowledge Lifecycle

`llm-wiki` は三つの durable checkpoint を所有する。

1. Human-approved Written Spec: canonical spec、related terminology / ADR、index、log。
2. Repository policy により承認された implementation plan: spec binding、plan、index、log。
3. Implementation closeout: 実装結果、material decision、verification、残課題、index、log。

runtime progress ledger、worker report、review transcript、diff、test log は durable knowledge ではなく、Superpowers workspace の transient evidence とする。

すべての implementation task と task review が完了した後、final whole-branch review の前に closeout を行う。final reviewer は code、tests、spec、plan、wiki、index、log を同じ branch range で確認する。

knowledge root が存在するのに authority、canonical target、write boundary、index / log sync、validation のいずれかを解決できない場合は `LOCAL_COMPLETE` にしない。knowledge root がない場合は `not_applicable` とする。

## Error Handling And Stop Conditions

- material ambiguity が残る場合は `Grill with Docs` を継続し、暗黙の assumption で spec を確定しない。
- Written Spec の Human approval がなければ plan stage へ進まない。
- plan と spec の binding が失われていれば SDD へ進まず、plan stage へ戻す。
- current tree と spec / plan が material に不一致なら evidence を保存し、Human に decision を戻す。
- SDD、isolated implementer、independent reviewer、required worktree、必要な domain skill が利用不能なら停止する。
- reviewer finding と approved spec / plan が衝突する場合、authority-bearing decision は Human に戻す。
- requirement または material current risk に紐づかない observation は fix loop に入れない。
- remote write、push、PR、merge、release、live install は、別途明示承認がない限り実行しない。

## Acceptance Criteria

- change request から Human-approved Written Spec、implementation plan、SDD、knowledge closeout までの一貫した route が定義される。
- spec authoring または material な仕様精緻化では `Grill with Docs` が必須になる。
- complete な Human-approved spec / plan がある場合は、完了済み stage を重複実行しない。
- Superpowers が lifecycle、plan、TDD、dispatch、review、model tier の正本であり、repo-local skill がそれらを再実装しない。
- `llm-wiki` が relevant knowledge query と、approved spec / plan / closeout の durable storage を所有する。
- Grill / Domain Modeling の既定出力を使って `CONTEXT.md` や repo-root `docs/adr/` という並行正本を作らない。
- repo-local model logic は upstream tier の host resolution に限定される。
- reasoning effort は `low` / `medium` / `high` の runtime-only overlay として選択され、unsupported host では model routing のみで継続できる。
- Codex と Hermes Agent の host-specific capability は adapter boundary で解決される。
- concrete model / effort / provider / agent ID / run-specific resolution を durable artifact に保存しない。
- knowledge root がある場合、spec、plan、closeout、index、log、validation が completion contract に含まれる。
- old loop skill、独自 scheduler、packet schema、event store、runtime snapshot を fallback または新規依存として導入しない。

## Testing Strategy

### Contract tests

- entry input を change request / incomplete spec / approved spec / approved plan に分類できる。
- spec 不在または material ambiguity ありでは `Grill with Docs` が required になる。
- approved current spec では Grill が `not_needed` になり、plan stage へ進む。
- Written Spec approval なしでは plan / implementation に進めない。
- upstream model selection を参照し、重複する repo-local role-to-model table を持たない。
- effort overlay が low / medium / high と user override / escalation を定義する。
- effort unsupported は `not_supported`、isolated model dispatch unsupported は `BLOCKED` になる。
- knowledge root の有無と write boundary に応じて query / ingest / closeout を選べる。
- concrete runtime choice を durable artifact へ保存しない。
- old loop skillへ silent fallback しない。
- dual-host discovery / compatibility validator を通過する。

### Forward scenarios

1. rough change request を wiki query と Grill に通し、Human-approved spec、plan、SDD へ進める。
2. incomplete spec の未確定 decision だけを一問一答で詰める。
3. approved spec を再 grilling せず plan 化する。
4. current spec に binding された approved plan を直接 SDD へ渡す。
5. mechanical / integration / high-risk dispatch で upstream model tier と local effort overlay が独立して解決される。
6. effort unsupported host で upstream model selection により正常継続する。
7. Hermes capability 不足を明示して fail closed する。
8. knowledge root ありで approved spec / plan / closeout、index、log を同期してから final review する。
9. knowledge root なしで wiki stage を `not_applicable` にする。
10. wiki validation failure が `LOCAL_COMPLETE` を block する。

## Completion Contract

`LOCAL_COMPLETE` は次をすべて満たす場合だけ返す。

- Human-approved Written Spec に current implementation が binding されている。
- repository policy が要求する plan review / approval を満たしている。
- approved plan の全 task が Superpowers SDD の task review を通過している。
- required verification が fresh に成功している。
- scoped commits が current branch に含まれる。
- knowledge root がある場合、spec / plan / closeout、index、log、validation が完了している。
- knowledge closeout 後の whole-branch final review が approved である。
- blocker、residual risk、未実施 remote action が短く報告されている。

## Migration

- 既存 Phase 1 implementation は current behavior の evidence として保持する。
- 既存の [SDD Implementation Skill 実装計画](sdd-implementation-skill-implementation-plan.md) は Phase 1 の historical plan とし、この revision の実行には再利用しない。
- 本 Written Spec の Human approval 後、Superpowers `writing-plans` で successor implementation plan を作る。
- successor implementation は最小の skill / tests / routing policy 更新に限定し、旧 loop family の削除は別 task とする。
- 実 run evidence と forward verification が揃うまで、旧 skill を削除しない。

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

- [Superpowers SDD のモデル選択・Reasoning・Host 境界調査](sdd-superpowers-model-and-reasoning-research.md) — upstream v6.2.0 の model、effort、host、spec / plan / SDD ownership の evidence。
- [Planning Authority Policy 仕様](planning-authority-policy/spec.md) — Human authority と runtime model persistence の既存契約。
- [SDD Implementation Skill 実装計画](sdd-implementation-skill-implementation-plan.md) — Phase 1 の historical implementation plan。
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md) — 旧 loop family の複雑性と適用基準。

## 出典

- [Superpowers v6.2.0](https://github.com/obra/superpowers/tree/v6.2.0)
- [Superpowers Basic Workflow](https://github.com/obra/superpowers/blob/v6.2.0/README.md#L184-L197)
- [Superpowers Brainstorming](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md)
- [Superpowers Writing Plans](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md)
- [Superpowers Subagent-Driven Development](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md)
- `local-skill:/Users/omitsuhashi/.agents/skills/grill-with-docs/SKILL.md`
- [skills/llm-wiki/SKILL.md](../../../skills/llm-wiki/SKILL.md)
