# GitHub Projects 直接接続型 Task Management Skill 仕様

## 状態

2026-07-23 の対話で設計方向を承認済み。本 page の exact path と raw-byte SHA-256 に対する Written Spec Gate は未承認であり、Issue 分解、実装計画、production skill 変更はまだ行わない。

## Epic ID

`direct-github-projects-task-management`

## 問題設定

現行の `task-management` は `plugins/task-management/` に plugin、Python facade、backend route、provider adapter、host 固有 registration、backend-neutral task schema をまとめている。しかし、タスク管理の正本を GitHub Projects に決めた後は、この抽象化が次の不整合を生む。

- 唯一の採用 backend が GitHub Projects であるにもかかわらず、backend-neutral facade と adapter dispatch を保守する必要がある。
- task read と write のために、GitHub MCP までの間へ独自 tool、route config、operation envelope、provider result normalization が入る。
- task の実体、work unit、Project item、Issue repository の関係が独自 schema と GitHub の両方へ二重記録される。
- plugin manifest、runtime registration、host 固有 setup guidance が task-management skill の本来の手順と混在する。
- Project、Issue、field、権限の不足を独自 adapter error へ翻訳するため、実際の GitHub 状態が利用者から見えにくい。

一方、薄い wrapper を削除するだけでは、接続先 Project の選択、Issue の保存先、承認境界、部分失敗、field contract が各呼び出し側へ分散する。新しい skill は runtime adapter を持たず、GitHub MCP へ直接接続しながら、これらの運用契約だけを一貫して所有する必要がある。

## 成功条件

- `task-management` は `skills/task-management/` の standalone skill になる。
- 通常の task read / write は利用可能な GitHub MCP capability を直接使い、独自 facade、adapter、provider-neutral schema、CLI fallback を経由しない。
- 1 個の caller-selected GitHub Project が複数 repository の Issue を集約する task portfolio の正本になる。
- 各 task の内容は GitHub Issue、Project membership と workflow field は GitHub Project item を正本とする。
- Issue repository を work unit の管理境界とし、`work_unit_id` custom field を二重管理しない。
- skill は特定の利用者、Project、repository、agent host を埋め込まず、caller が既定 target を一度設定して必要時だけ上書きできる。
- 高確度かつ非破壊の操作は自動実行し、低確度、破壊的変更、大規模な一括変更だけを人間確認へ送る。
- MCP、認証、権限、Project schema が不足する場合は fail closed とし、別の client や local backend へ切り替えない。

## 採用した判断

### 1. standalone skill と direct MCP

- `plugins/task-management/` は全体を廃止し、同名 skill を `skills/task-management/` に作り直す。
- production runtime の Python package、plugin manifest、registered read tool、backend config、local JSON backend、external provider adapter、smoke script は残さない。
- task operation は GitHub MCP が公開する Issue / Projects capability を直接使う。
- `gh`、REST client、GraphQL client、browser automation、別 provider plugin、local JSON を fallback にしない。
- MCP server 自体、credential、host registration、token、secret は skill の所有物にしない。
- Python は repository contract test にだけ使用でき、task operation の runtime facade には使用しない。

### 2. caller-owned target configuration

skill は特定の target を保存しない。caller は必要に応じて次の logical input を渡す。

```yaml
project_url: https://github.com/users/OWNER/projects/NUMBER
inbox_repository: OWNER/REPOSITORY
```

- `project_url` は個人所有 Project の `/users/<owner>/projects/<number>` と Organization 所有 Project の `/orgs/<owner>/projects/<number>` を受け付ける。
- 利用者に `project_number` 単体を要求しない。MCP capability が owner と number を必要とする場合だけ、skill が URL から意味を読み取る。
- `inbox_repository` は repository に属さない task を扱う caller-owned fallback であり、skill 内に既定値を持たない。
- caller の profile、上位 skill、agent instruction、session context のどこへ既定値を保存するかは caller の責務とする。task-management は保存形式や host path を規定しない。
- 呼び出し時の明示値は caller default を上書きするが、その上書きを永続設定へ逆流させない。
- 各 caller は通常運用の正本として 1 個の既定 Project を指定する。上書きは別 caller での再利用または明示的な例外操作のためであり、複数 Project への自動 routing には使わない。

Project target は次の順序で解決する。

1. 現在の依頼で明示された `project_url`
2. caller が渡した既定 `project_url`
3. 現在の会話で既に確定している target
4. GitHub MCP の read capability で一意かつ矛盾なく特定できる open Project
5. 複数候補、認証主体不明、owner 不一致、closed / template との競合があれば人間確認

title だけの一致や「最近使った」という理由だけでは state-changing operation の target を確定しない。URL が不正、Project が存在しない、または権限不足の場合も推定で別 Project へ切り替えない。

### 3. 1 Project・Issue-backed task

- 1 つの caller-selected Project を task portfolio の正本として扱い、複数 repository の Issue を Project item として追加する。
- task は Project draft item ではなく GitHub Issue として作成する。
- task の Outcome、Context、Acceptance criteria、References は Issue を正本とする。
- Project membership、Status、Priority、Due date は Project item を正本とする。
- Done / Cancelled になった item も Project から削除せず、履歴として残す。
- skill は work unit ごとの空 repository、Project、Project field、Project view を通常 task operation の副作用として作成しない。

### 4. repository を work unit boundary にする

- Issue の保存先 repository を work unit の正本とする。
- GitHub Project が持つ repository 情報で絞り込みと集計を行う。
- `work_unit_id`、`work_unit_name`、target repository を表す重複 custom field は作らない。
- 1 repository 内に複数の独立 work unit を区別する実需要が現れた時だけ、別 revision で追加 field を検討する。

Issue repository は次の順序で解決する。

1. 利用者が明示した repository
2. 現在作業中の repository に直接属する task であることが高確度な場合、その repository
3. 参照された Issue、PR、仕様書、対象コードから 1 repository に一意に帰属できる場合、その repository
4. repository に属さない横断 task、非開発 task、未分類 capture であり、caller が `inbox_repository` を渡している場合、その inbox
5. 複数 repository が競合する、または帰属判断に自信がない場合は人間確認

曖昧な task を自動的に inbox へ逃がさない。inbox は「推定に失敗した場所」ではなく、「repository 非依存または未分類であることが task の現在状態として正しい場所」とする。

### 5. Project field contract

Project は次の field contract を持つ。

#### Status

| Option | 意味 |
|---|---|
| `Inbox` | 未整理 |
| `Backlog` | 実施候補だが未着手 |
| `Ready` | 着手可能 |
| `In progress` | 進行中 |
| `Blocked` | 外部要因などで停止中 |
| `Done` | 完了 |
| `Cancelled` | 実施しないと決定 |

#### Priority

| Option | 意味 |
|---|---|
| `P0` | 即時対応 |
| `P1` | 高優先 |
| `P2` | 通常。指定がなければ既定値 |
| `P3` | 低優先 |

#### Due date

- 期限がある task だけに設定する任意の日付 field とする。
- 期限が不明な場合に推定日を埋めない。

Repository、Assignees、Labels、Milestone、Issue type、parent / sub-issue など GitHub が既に持つ情報を同名 custom field として複製しない。agent 名、automation mode、approval required も Project field にしない。

通常 operation は既存 schema を利用する。field や option が不足する場合は書き込みを止め、必要な差分を報告する。Project schema の初期化・修復は、利用者が明示的に setup を依頼し、MCP capability と権限が確認できた別操作として扱う。

### 6. Issue contract

Issue title は内部作業名ではなく、達成する結果を短く表す。Issue body の既定形は次とする。

```markdown
## Outcome
このIssueで実現する結果。

## Context
必要になった背景と判断材料。

## Acceptance criteria
- [ ] 完了を判定できる条件

## References
関連するIssue、PR、仕様書、確定済みの外部参照。
```

- 生の会話 transcript、内部 prompt、chain-of-thought、credential、agent 名を保存しない。
- 実装 task は対象 repository の durable spec、Issue、PR、file path へ可能な範囲で参照を残す。
- acceptance criteria がなく完了判定できない場合は、低確度 task として作成前に確認する。
- task type や domain は repository の既存 label / Issue type を優先し、全 repository 共通 taxonomy をこの skill が強制しない。

### 7. default operation flow

新規 task は次の順序で処理する。

1. task outcome と acceptance criteria を抽出する。
2. `project_url` を target resolution rule で確定する。
3. Issue repository を repository resolution rule で確定する。
4. 対象 repository の open Issue と target Project item を read-only 検索し、同一 task の明白な再実行かを確認する。
5. 完全一致に近い既存 Issue があり同一性が高確度なら、その Issue を再利用する。title 類似だけで別 task を統合しない。
6. Issue がなければ Issue contract に従って作成する。
7. Issue を target Project へ追加する。
8. 明示値がなければ `Status=Inbox`、`Priority=P2`、`Due date` 未設定にする。
9. Issue URL、repository、Project URL、Project item への反映結果、未完了工程を返す。

利用者が「着手中として登録」など明示的な状態を指定した場合は、その Status を既定値より優先する。更新、comment、status change、検索、一覧も同じ target / approval / failure contract を使う。

### 8. terminal status と Issue state

- `Done` は Issue close reason `completed` と対応する。
- `Cancelled` は Issue close reason `not planned` と対応する。
- terminal transition は Project Status と Issue close を 1 logical operation として扱う。
- 利用者が完了・中止・close を明示した場合、その依頼自体を承認として扱い、同じ操作を重ねて確認しない。
- checklist 完了や文脈だけから terminal transition を推定する場合は、実行前に確認する。
- 外部で既に close された Issue の reason が取得できる場合、Project Status との整合を高確度な非破壊更新として修復できる。
- `Done` / `Cancelled` への遷移で Project item を remove / archive しない。

### 9. approval policy

独自の `task_preflight`、approval digest、operation envelope は作らない。会話上の intent と MCP host の通常確認機構を使う。

自動実行してよい操作:

- read、search、list、capability check
- target と内容が高確度な単一 Issue の create / edit / comment
- Project への Issue 追加
- 非 terminal な Status、Priority、Due date の高確度更新
- 明示された task の不足 metadata 補完
- 既に close 済み Issue の明白な Project Status 整合

確認が必要な操作:

- Project または Issue repository を一意に決められない書き込み
- acceptance criteria や task outcome が決まらない create
- 推定による Issue close、transfer、delete、Project item remove / archive
- 既存 Issue body の情報を失わせる全面置換
- Project field / option / workflow / visibility の変更
- 複数 Issue にまたがる一括 mutation
- private content の公開範囲を変え得る操作

利用者が対象と操作を明示している場合、その発話を当該操作の確認として扱う。ただし、対象 URL の不一致、権限主体の矛盾、想定外の大量件数が判明した場合は停止して再確認する。

### 10. capability と failure contract

書き込み前に、現在の host で少なくとも次を意味的に確認する。

- Issue の read / search / create / update / comment
- Project の read、item add、field value update
- target owner / repository / Project に対する認証と必要権限

tool の具体名は host ごとに異なり得るため、skill contract は特定の MCP function 名を固定しない。ただし使用する provider は GitHub MCP に限定し、意味の似た CLI や別 API client へ置換しない。

不足時は次のように fail closed にする。

- MCP unavailable: GitHub MCP が利用できないことを報告する。
- capability missing: 不足する Issue / Projects operation を列挙する。
- authentication / permission failure: target と拒否された operation を報告し、credential 自体は要求・保存しない。
- schema mismatch: 不足 field / option と期待 contract を報告する。
- ambiguous result: write を行わず候補を提示する。

Issue create 後に Project add または field update が失敗した場合、作成済み Issue を削除しない。Issue URL、成功済み step、未完了 step、再実行方法を返す。再実行時は既存 Issue を起点に残りの step だけを行い、重複 Issue を作らない。terminal transition の片側だけが成功した場合も自動 rollback せず、不整合と残 step を報告する。

### 11. host-neutral authoring

- `skills/task-management/**` の user-facing prose は特定 agent host の名称、専用 toolset、install command、profile path、runtime registration を含めない。
- skill discovery は共有 `SKILL.md` を entrypoint とし、特定 host 専用 plugin manifest や registration code を要求しない。
- host ごとの install / discovery / live availability は repository-level validation または別の運用文書の責務とし、task-management の task semantics に混ぜない。
- `decide-in-order` を含む別 skill を task creation の必須 dependency にしない。未解決の重大判断がある場合は通常の one-question-at-a-time confirmation で停止できる。

## 対象構成

実装後の product tree は最小限、次を想定する。

```text
skills/task-management/
├── SKILL.md
├── references/
│   ├── core.md
│   ├── github-projects.md
│   ├── issue-contract.md
│   └── safety-and-failures.md
└── tests/
    └── test_task_management_contract.py
```

reference 分割は implementation plan で最終化するが、runtime code、provider adapter、task state file、credential file、host-specific manifest は追加しない。

## 移行方針

- `plugins/task-management/` は部分移植せず、directory 全体を削除する。
- `.github/workflows/skill-architecture.yml` の旧 plugin focused tests を standalone skill tests へ置き換える。
- `scripts/test_dual_host_ci_workflow.py` と `scripts/test_loop_autonomous_gates_ledger.py` が旧 plugin path や旧 adapter test 名を executable dependency にしているため、新 contract の検証先へ更新する。
- `skills/decide-in-order/` 自体は task storage を所有していないため削除しない。ただし task-management から companion dependency と integration policy を持ち込まない。
- 旧 task-management spec、Issue ledger、implementation plan、Input Packet、Execution Envelope、source summary は historical evidence として削除しない。新しい active contract から実行可能な参照として扱わず、`knowledge/index.md` では本 spec を current canonical entry とする。
- immutable / sealed historical JSON の bytes は変更しない。
- repository-wide authoring / compatibility guidance は維持するが、新 skill 本文には host 固有説明を置かない。

## 非目標

- GitHub 以外の task backend を同じ skill から扱うこと。
- backend-neutral task schema、provider adapter SDK、routing registry、local JSON backend を残すこと。
- GitHub MCP server、OAuth、PAT、secret、credential store を実装または設定すること。
- `gh`、REST、GraphQL、browser automation を fallback として実装すること。
- 通常 task create のついでに Project、repository、field、view、workflow を作ること。
- work unit ごとに空の Issue repository を自動作成すること。
- `work_unit_id` custom field を先回りして追加すること。
- Project native draft item を task の正本にすること。
- repository 間で label / Issue type taxonomy を統一すること。
- caller profile の保存形式や host 固有 config path を標準化すること。
- live GitHub Project、inbox repository、credential、installed skill state をこの repository change の一部として変更すること。
- PR 作成、merge、release、marketplace publish、live installation をこの仕様の暗黙の権限に含めること。
- historical POTASK artifact の内容を書き換えて新設計に見せること。

## Issue 分解方針

Written Spec Gate 承認後、少なくとも次の独立責務へ分解する。

1. standalone skill contract と failing contract tests
2. caller target / repository resolution、Issue / Project field、approval / failure references
3. 旧 plugin removal と repository CI / regression references の置換
4. skill / repository validators、fresh scenario evaluation、wiki supersession の統合検証

各 Issue は test-first とし、旧 plugin 削除と CI 参照更新が分離して main を常時壊す場合は、同一 Issue または明示 dependency で一体化する。Issue Gate 前に ID、write scope、blocker graph、acceptance criteria、verification を ledger へ固定する。

## 受け入れ条件

### Product contract

- [ ] `skills/task-management/SKILL.md` が standalone entrypoint として存在し、frontmatter `name` が directory 名と一致する。
- [ ] `plugins/task-management/` が存在しない。
- [ ] `skills/task-management/**` に production Python、plugin manifest、backend config、provider adapter、local task state、credential material がない。
- [ ] skill は caller-supplied `project_url` と optional `inbox_repository` の resolution order、override、ambiguity stop を定義する。
- [ ] skill は特定 owner、Project number、inbox repository を既定値として埋め込まない。
- [ ] Issue-backed task、1 Project aggregation、repository-as-work-unit、no `work_unit_id` field が明記される。
- [ ] Status 7 option、Priority 4 option、optional Due date と Issue state mapping が明記される。
- [ ] Issue body が Outcome、Context、Acceptance criteria、References を持つ。
- [ ] high-confidence safe auto-execution と uncertain / destructive / bulk confirmation の境界が具体例付きで固定される。
- [ ] GitHub MCP capability 不足、認証失敗、schema mismatch、partial failure、retry の fail-closed behavior が固定される。
- [ ] skill 本文と references に特定 agent host 名、専用 runtime tool 名、専用 install command がない。
- [ ] 別 skill がなくても task create / read / update の契約が完結する。

### Repository integration

- [ ] `.github/workflows/skill-architecture.yml` が standalone task-management test を Python 3.9 / 3.12 で実行し、削除済み plugin test を参照しない。
- [ ] `scripts/test_dual_host_ci_workflow.py` が新しい CI contract を検証する。
- [ ] `scripts/test_loop_autonomous_gates_ledger.py` が旧 adapter test file に依存せず、新 approval / capability contract または historical evidence を正しく検証する。
- [ ] active `knowledge/index.md` が本 spec と後続 ledger / plan を発見可能にし、旧 plugin contract を current implementation として案内しない。
- [ ] `knowledge/log.md` が Spec Gate、Issue Gate、implementation、verification、delivery state を append-only に追跡する。
- [ ] 既存の unrelated user change `skills/llm-wiki/DESCRIPTION.md` を変更、削除、stage しない。

### Scenario behavior

- [ ] caller default Project を持つ明確な repository task は追加確認なしで Issue 作成、Project 追加、既定 field 設定へ進める。
- [ ] 呼び出し時 `project_url` が caller default を上書きし、永続 default は変更されない。
- [ ] 複数 Project または複数 repository が競合する task は write 前に停止する。
- [ ] repository 非依存 task は configured inbox を使い、inbox 未設定なら確認する。
- [ ] 明示的な完了 / 中止は追加確認なく terminal transition を行い、推定 terminal transition は確認する。
- [ ] Issue create 後の Project write failure は Issue を削除せず、残 step を再実行可能に報告する。
- [ ] MCP capability がない場合、CLI、browser、local backend へ fallback しない。

## 検証方針

実装は static contract test と scenario-oriented fresh evaluation を中心に検証する。repository CI では live GitHub write を行わない。

予定する local verification:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_dual_host_ci_workflow.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_loop_autonomous_gates_ledger.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_*.py'
git diff --check
```

static negative checks:

```bash
rg -n --glob '!**/tests/**' "plugins/task-management|task-management-read" .github/workflows skills/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task_adapter__|mcp__<server>__task_query|work_unit_id" skills/task-management
rg -n --glob '!**/tests/**' "subprocess|requests|urllib|graphql|\bgh\b" skills/task-management
```

最初の command は旧 executable path、2 つ目は host-specific contract が残っていないことを確認し、いずれも no match を期待する。3 つ目は runtime client / fallback の混入がないことを確認する。test は prohibited token の不在を assertion するため文字列を引用できるが、production prose / code には許容しない。

fresh evaluation は期待回答を渡さず、少なくとも次を確認する。

- 明確な repository task と caller default Project
- invocation-level Project override
- 複数 Project の曖昧性
- 複数 repository の曖昧性
- repository 非依存 task と inbox fallback
- 明示的 terminal transition と推定 terminal transition
- MCP Projects write capability 不足
- Issue create 後の Project add failure と idempotent retry

live write test は別の明示承認を必要とし、専用 test Issue / Project を用意できる場合だけ実施する。実データを使う場合も create / update scope、cleanup、残存 artifact を事前に提示する。

## リモート書き込み方針

`local_only`。

本仕様の承認は、repository 内 spec、Issue ledger、implementation plan、skill、tests、CI、wiki の local change だけを対象とする。branch push、GitHub Issue mirror、PR 作成・更新、Project / repository 作成、Project schema 更新、live task write、skill install、release、merge は別の明示依頼または各 gate を必要とする。

## 人間レビューゲート

1. **Written Spec Gate**: 本 `spec.md` の exact repo-relative path、raw-byte SHA-256、accepted decisions、non-goals、acceptance criteria、verification、remote policy、stop conditions を一括承認する。
2. **Issue Gate**: local Issue ledger の ID、blocker graph、dependency order、acceptance criteria、write scope を承認する。
3. **Execution Plan Gate**: test-first implementation plan、sealed Input Packet、execution / delivery boundary を承認する。
4. **Live Write Gate**: live GitHub Project または Issue を使う試験が必要な場合だけ、対象と副作用を別途承認する。
5. **Remote Delivery Gate**: push、PR、GitHub Issue mirror を行う場合だけ、publication set と branch / PR state を別途承認する。

## 停止条件

次の場合は production change または external write を進めず停止する。

- Written Spec Gate、Issue Gate、Execution Plan Gate の対象 bytes / scope が未承認または stale。
- user-owned change と write scope が衝突し、安全に分離できない。
- GitHub MCP に必要 capability がない、認証主体が不明、または対象権限が確認できない。
- Project URL、Issue repository、既存 Issue の同一性を高確度に決められない。
- Project field contract が不足し、通常 task operation の範囲で安全に補えない。
- 削除対象 plugin が別 active consumer の runtime dependency であることが新たに判明し、移行先がない。
- repository validator を通すために host-specific instruction を新 skill へ戻す必要が生じる。
- live write、push、PR、merge、install など local-only scope を超える操作が必要になる。
- unrelated untracked file `skills/llm-wiki/DESCRIPTION.md` へ変更が必要になる。

## 既知のリスク

- GitHub MCP の toolset や引数名は host integration により異なり得る。skill は semantic capability を記述するため、live environment ごとの discovery は残る。
- Issue 作成と Project item / field 更新は atomic transaction ではなく、部分成功が起こり得る。削除 rollback ではなく idempotent continuation で扱う。
- repository を work unit boundary にしたため、将来 1 repository 内の複数 work unit を Project view で分離したくなれば schema revision が必要になる。
- caller-owned default の保存場所を skill が規定しないため、複数 host / profile 間で設定が揃わない可能性がある。target URL を invocation context で確認可能にし、暗黙の別 target へ切り替えないことで抑制する。
- personal Project に private organization Issue を追加しても、Project viewer が元 repository の権限を持たなければ Issue content を閲覧できない。Project visibility は repository access を代替しない。
- custom field 名や option が手動変更されると通常 write が停止する。silent remapping は行わず、schema mismatch として setup / repair へ分離する。
- 旧 historical docs には廃止後の path と architecture が残る。active index と新 spec で supersession を明示し、historical evidence 自体は改変しない。

## 関連ページ

- [Portfolio OS Task Backend Plugin Skill Spec](../portfolio-os-task-backend-plugin-skill-spec.md) — 廃止対象となる backend-neutral plugin architecture の historical contract。
- [Task Management Provider Adapters 実装計画](../2026-07-16-task-management-provider-adapters-implementation-plan.md) — 削除対象となる facade / adapter 実装の historical plan。
- [Decide In Order Skill 設計](../decide-in-order-skill-design.md) — standalone decision skill 自体は維持するが、task-management integration は新 contract へ継承しない。
- [Loop Skill Approved Spec Binding Contract 仕様](../approved-spec-binding-contract/spec.md) — Written Spec Gate と Epic artifact lifecycle の現行 contract。

## 出典

- [2026-06-28 Portfolio OS Task Backend Plugin / Skill Handoff](../../sources/2026-06-28-portfolio-os-task-backend-plugin-skill-handoff.md)
- [GitHub Projects documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Finding your projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/finding-your-projects)
- [GitHub GraphQL ProjectV2 owner reference](https://docs.github.com/en/graphql/reference/orgs#projectv2)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
