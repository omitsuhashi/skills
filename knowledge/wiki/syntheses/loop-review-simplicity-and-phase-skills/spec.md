# Loop Review Simplicity And Phase Skills 仕様

## 状態

Spec Gate approval target。設計会話で方針、実装範囲、remote policy まで確認済みである。exact revision の承認 evidence は `knowledge/log.md` と sealed Input Packet に記録し、承認後にこの状態文を変更しない。

## 問題設定 / 成功条件

`grill-to-pr-loop` と `issue-implementation-loop` は、要件適合、regression、delivery risk を確認する review gate と、operation 別の reference read-set を持つ。一方、次の 2 つが未解決である。

- review contract が `Minor` finding を許しており、実装判断を変えない nit、表記上の好み、任意の改善が review output と fix cycle を冗長にし得る。
- `context-contract.toml` は operation 別 reference を宣言するが、現在 actor と dispatch 先が読む supplemental skill を宣言しない。そのため、planning 中の `tdd`、implementation 中の planning skill、review 以外での review skill など、将来 phase の skill を先読みしない境界を machine-readable に確認できない。

成功条件は、review を「要件達成」「material simplicity」「material risk」の判断に集中させ、各 operation が必要な supplemental skill だけを読める contract を、既存 loop architecture を増築せずに追加することである。

## Epic ID

`loop-review-simplicity-and-phase-skills`

## 現在の根拠

- `skills/issue-implementation-loop/references/review-gate.md` は Issue intent fit、implementation regression、current PR delivery risk を automatic review checks とする。
- 同 reference は future-only hardening を automatic review viewpoint から除外済みであり、この narrow scope は維持する。
- `skills/issue-implementation-loop/references/mental-model.md` は reviewer が `Critical`、`Important`、`Minor` を報告すると記載している。
- `skills/grill-to-pr-loop/references/remote-delivery.md` は final PR 前の spec alignment review を要求するが、material simplicity を独立観点として要求しない。
- 両 loop skill の `context-contract.toml` は operation 別 `references` を持つが、supplemental skill の read boundary を持たない。
- `skills/grill-to-pr-loop/scripts/check_prereqs.py` と `skills/issue-implementation-loop/scripts/check_capabilities.py` は skill availability を確認できる。availability check は skill instruction の読込ではない。
- planning prereq は `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase planning` で通過済みである。
- Planning Worktree Gate は `codex/loop-review-simplicity-and-phase-skills/planning` を作成し、planning base SHA `f5d151e34de5089d75be68249e09da8a2d14f282` を記録済みである。

## 採用した判断

### 1. Material review standard

loop family の spec self-review、Issue implementation review、final spec alignment review は、次の順に判定する。

1. 承認済み要件、acceptance criteria、non-goals、write scope、verification を過不足なく満たすか。
2. 同じ要件と risk boundary を、明確に少ない仕組み、分岐、層、重複、抽象化で実現できる materially simpler な具体案がないか。
3. correctness、safety、regression、current delivery に material risk がないか。

「ベスト」は絶対的な完璧さではなく、承認済み要件と material risk の範囲で、review 時点に確認できる最も単純な実装とする。

reviewer は判断または実装を変える `Critical` / `Important` finding だけを報告する。`Minor`、nit、表記上の好み、任意の refactor、将来だけに効く改善は finding として出さない。mechanical validator、schema check、digest check、test suite はこの reporting threshold の対象外であり、従来どおり網羅的に実行する。

要件を満たす実装に対して simplicity finding を出す場合は、同じ要件を満たす materially simpler な代案、現行構造が増やす仕組み、変更による material impact を具体的に示す。具体案を示せない好みや数行の短縮は finding にしない。material simplicity gap は既存 taxonomy の `intent_gap` / `Important` として扱い、新しい finding taxonomy は追加しない。

`hardening_candidate`、`safety_escalation`、`classification_needed` の既存境界は維持する。future-only hardening を通常レビューへ戻さない。

### 2. Operation-scoped skill contract

両 loop skill の `context-contract.toml` を schema v3 にする。schema v1 / v2 の既存 contract は読み取り可能なまま維持する。

schema v3 の各 operation は、その operation が常に必要とする phase-owned workflow skill を次の 2 field で必ず持つ。

- `skills`: 現在 operation の actor が読む supplemental skill。
- `dispatch_skills`: 現在 operation が作る bounded worker/reviewer context だけが読む supplemental skill。

両 field は string array とし、不要な operation でも空 array を明示する。current actor は current operation の phase-owned `skills` だけを読み、`dispatch_skills` を自分の context に読まない。dispatch 先だけが current operation の phase-owned `dispatch_skills` を読む。未来の operation の workflow skill は先読みしない。

task 内容によって適用が決まる skill は universal allowlist にしない。たとえば skill edit worker の `writing-skills`、security task の security skill は、通常の skill trigger に従って該当 phase に入ってから on-demand で読む。task-triggered skill を future phase で先読みしてはならないが、すべての task-specific skill を context contract、worker packet schema、generic loader に列挙する機構は追加しない。

availability check、path resolution、capability preflight は instruction loading と区別する。skill が存在するかを先に調べてもよいが、該当 operation に入るまで `SKILL.md` 本文を読まない。

`issue-implementation-loop` は supplemental skill ではない。Execution Plan Gate 完了後、fresh または compacted coordinator が top-level skill を切り替えて初めて読む。

### 3. Phase mapping

`grill-to-pr-loop`:

| Operation | `skills` | `dispatch_skills` |
| --- | --- | --- |
| `intake` | `[]` | `[]` |
| `grill` | `["grill-with-docs"]` | `[]` |
| `spec` | `[]` | `[]` |
| `issue-gate` | `[]` | `[]` |
| `execution-plan` | `[]` | `[]` |
| `resume` | `[]` | `[]` |
| `completion-report` | `[]` | `[]` |
| `delivery` | `[]` | `[]` |
| `final-review` | `["requesting-code-review"]` | `[]` |
| `ambiguity-check` | `[]` | `[]` |
| `context-compaction` | `[]` | `[]` |

通常の GitHub mirror / delivery と final spec alignment review を分け、review skill を final review 以外で読まない。

`issue-implementation-loop`:

| Operation | `skills` | `dispatch_skills` |
| --- | --- | --- |
| `prepare` | `[]` | `[]` |
| `execute.dispatch` | `[]` | `["tdd"]` |
| `execute.wait` | `[]` | `[]` |
| `execute.review` | `["requesting-code-review"]` | `[]` |
| `resume` | `[]` | `[]` |
| `status` | `[]` | `[]` |
| `deliver` | `[]` | `[]` |
| `context-compaction` | `[]` | `[]` |

`tdd` は implement / fix worker だけが読み、execution coordinator と reviewer は読まない。reviewer fallback の承認ルールは既存 review gate を維持する。

### 4. Parser / inspector / validator

- shared `scripts/skill_context/contract.py` は schema v3 を受理し、各 operation の `skills` / `dispatch_skills` を検証する。
- `issue-implementation-loop` の runtime operation selector も同じ schema v3 field を保持して返す。
- inspector の JSON / text output は operation の `skills` / `dispatch_skills` を表示する。
- schema v3 では field 欠落、non-array、空文字、同一 field 内重複を validation error にする。
- validator は phase-owned workflow skill の mapping を検証する。task-triggered skill の universal allowlist や install inventory validator にはしない。
- static validator は host ごとに異なる install path や availability を要求しない。該当 operation の entry guard が availability を確認し、missing skill では既存の approved equivalent / stop rule に従う。
- skill 本文の token 数は host install に依存するため、repo-local reference budget に混ぜない。report では宣言 skill 名を別 field として表示する。

### 5. Skill authoring TDD

skill edit 前に、現行 contract を使った pressure scenario で baseline failure を観測する。少なくとも次を分離する。

- 多数の nit と 1 件の material requirement gap がある変更。
- 要件は満たすが不要な層・重複機構を持つ変更。
- planning 中に将来 phase の implementation / review skill を先読みしたくなる状況。

baseline の exact failure / rationalization を記録してから、contract test と review wording test を RED にし、最小変更で GREEN にする。実装後は同じ scenario を fresh context で再評価し、material finding に収束し nit を報告しないことを確認する。

## 検討した選択肢

1. `SKILL.md` に review 方針と phase skill 一覧だけを書く案は、agent の注意に依存し contract drift を検出できないため採用しない。
2. operation contract に `skills` / `dispatch_skills` を加え、既存 parser / inspector / validator と review reference を最小更新する案を採用する。
3. 専用 skill loader、review schema、review runtime を新設する案は、今回の目的に対して機構を増やし、simplicity 方針と矛盾するため採用しない。

## Issue 分解方針

本変更は 1 つの cohesive issue `LRSP-001` とする。context schema、phase mapping、review contract、tests、wiki sync は互いに同じ acceptance boundary を構成し、別 issue / branch に分けると contract と利用側が一時的に不整合になるためである。

GitHub Issue mirror と issue PR は作らない。

## 受け入れ条件

1. schema v3 の両 loop context contract は全 operation に `skills` / `dispatch_skills` を持つ。
2. `grill-with-docs`、`tdd`、`requesting-code-review` は採用した phase mapping 以外に宣言されない。
3. inspector は current operation の reference read-set と supplemental skill boundary を同時に表示する。
4. validator は schema v3 の field 欠落、不正型、空文字、重複を拒否し、既存 schema v1 / v2 contract を壊さない。
5. planning / execution coordinator は future operation または dispatch 先の phase-owned workflow skill を自分の instruction context に読まない。task-triggered skill は該当 phase でだけ on-demand に読む。
6. spec self-review、Issue implementation review、final spec alignment review は、要件達成、material simplicity、material risk の 3 観点を持つ。
7. routine review は `Minor`、nit、好み、任意の改善を finding として報告しない。
8. material simplicity finding は、同じ要件を満たす具体的な simpler alternative を必須とし、`intent_gap` / `Important` として blocking にする。
9. mechanical validation と既存 hardening / safety / classification boundary は弱めない。
10. skill authoring TDD の RED / GREEN evidence、loop full verification、dual-host / skill validator、wiki / git checks が残る。

## 検証方針 / コマンド

focused RED / GREEN の後、fresh verification として少なくとも次を実行する。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/report_skill_context.py --all --json
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 scripts/validate_dual_host_compatibility.py --skill skills/issue-implementation-loop
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
git diff --check
```

変更した両 skill に対して skill-creator quick validator も実行する。実在 command は Execution Plan Gate で current validator interface を確認して固定する。

## リモート書き込み方針

`delivery_intent = "per_action"`。

- GitHub Issue mirror と issue PR は作らない。
- local `PR_READY` までは remote write を行わない。
- local verification / review 完了後、対象 branch の push と draft PR 作成だけを Remote Gate で exact action として提示し、承認後に実行する。
- ready-for-review 化、merge、release、live install、その他の GitHub mutation は行わない。
- final merge は常に human-only。

## 人間レビューゲート

- **Spec Gate**: exact `spec.md` raw-byte revision と、採用判断、非目標、受け入れ条件、検証、remote policy、停止条件を人間が承認する。
- **Issue Gate**: `LRSP-001` の scope、acceptance criteria、write scope、実行可能状態を人間が承認する。
- **Execution Plan Gate**: approved scope 内の packet / capability / write scope / dependency / policy preflight と commit boundary。scope が変わらなければ追加の人間 approval は不要。
- **Remote Gate**: branch push と draft PR 作成の exact action を実行前に提示する。
- ready-for-review と merge は本 Epic の agent action に含めない。

## 非目標

- 新しい standalone skill、generic skill loader、review runtime、finding schema を作ること。
- task-triggered skill を列挙する worker packet field、universal skill allowlist、install inventory validator を作ること。
- Gate 数、worker/runtime artifact、review/fix cycle 数を増やすこと。
- `hardening_candidate`、`safety_escalation`、`classification_needed` の既存責務を作り直すこと。
- future-only hardening を routine review に戻すこと。
- mechanical validator、schema check、digest check、test suite の検出範囲を狭めること。
- loop family 以外の context contract や review policy に schema v3 field を必須化すること。
- GitHub Issue mirror、issue PR、ready-for-review、merge、release、live install を行うこと。

## 停止条件 / 既知のリスク

- Planning Worktree Gate の identity、default checkout snapshot、planning branch が不一致になる。
- schema v3 を shared parser と runtime selector の一方だけが解釈し、contract が二重化する。
- phase mapping に必要な skill が entry 時に見つからず、approved equivalent もない。
- task-triggered skill を current phase より前に読み込む、または該当 task で必須なのに読み込まない。
- review wording が nit を別 taxonomy や residual risk として再導入する。
- concrete simpler alternative の要件が曖昧で、単なる好みを `Important` に昇格させる。
- existing schema v1 / v2、`llm-wiki` context contract、context baseline が壊れる。
- pressure scenario を current / changed skill で比較できず、skill behavior change を検証できない。
- task write scope と別 worktree の変更が重なる。
- exact Remote Gate approval なしに push / PR 作成が必要になる。

## 関連ページ

- [Loop Review Governance Spec](../loop-review-governance-spec.md) は future-only hardening を routine review から除外した既存契約。本仕様は materiality と simplicity threshold を追加する。
- [Loop Skill 運用単純化仕様](../loop-skill-operational-simplicity-spec.md) は loop family の意図的な router / worker split と workflow complexity を定義する。本仕様はその operation 単位の supplemental skill boundary を追加する。
- [Planning Worktree Gate 仕様](../planning-worktree-gate/spec.md) は本 Epic の planning branch / worktree lifecycle を提供する。

## 出典

- `../../../../AGENTS.md`
- `../../../../skills/AGENTS.md`
- `../../../../skills/grill-to-pr-loop/SKILL.md`
- `../../../../skills/grill-to-pr-loop/context-contract.toml`
- `../../../../skills/grill-to-pr-loop/references/planning-contract.md`
- `../../../../skills/grill-to-pr-loop/references/remote-delivery.md`
- `../../../../skills/issue-implementation-loop/SKILL.md`
- `../../../../skills/issue-implementation-loop/context-contract.toml`
- `../../../../skills/issue-implementation-loop/references/review-gate.md`
- `../../../../skills/issue-implementation-loop/references/mental-model.md`
- `../../../../scripts/skill_context/contract.py`
