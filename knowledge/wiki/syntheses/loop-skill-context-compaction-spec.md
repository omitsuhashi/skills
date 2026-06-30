# Loop Skill Context Compaction Spec

## 状態

Spec Gate / Issue Gate 承認済み。Execution Plan Gate、実装、GitHub issue mirror、push、PR 作成、merge は未承認。

## 問題設定

`grill-to-pr-loop` は計画と gate、`issue-implementation-loop` は承認済み packet からの worker-only 実行を分担している。既存契約では、implementation handoff 前に main planning session の context 圧縮または fresh execution coordinator への切り替えを必須としている。

ただし、現状は次の 3 点が未定義である。

- 圧縮を開始する session context pressure の閾値。
- `grill-to-pr-loop` と、そこから呼ばれる loop 系 skill で「忘れてはいけない情報」と「圧縮してよい情報」の分類。
- intake / grill / spec / issue / execution / review / resume / delivery の各 phase で許可される圧縮処理。

この spec は、既存の 2 skill 構成、worker-only execution policy、paths-first packet / resume brief / runtime state を維持したまま、長い loop 実行で context が破綻する前に明示的に圧縮する契約を追加する。

## Epic ID

`loop-skill-context-compaction`

## 現在の前提

- `git status --short`: clean。
- current branch: `main`。
- current HEAD: `4ec31c42c9a15347bcea3903596d8b8fce9e95c9`。
- planning prereq: `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase planning` は通過済み。
- GitHub remote は存在するが、GitHub auth は optional unavailable。remote write は未承認。
- `scripts/report_skill_context.py --all --json` は warnings なし。
- 現行 read-set metric では `grill-to-pr-loop execution-plan` が `7216 / 10000` estimated tokens、headroom `27%`。
- `issue-implementation-loop` の主要実行 read-set は `prepare: 5216 / 8000`、`execute.dispatch: 5190 / 8000`、`execute.review: 5253 / 8000` estimated tokens。
- これらは operation read-set budget であり、今回扱う session context pressure とは別の指標である。

## 成功条件

- loop family の session context pressure soft trigger を `65%` として明文化する。
- `65%` 到達時点で、次の phase boundary を待たずに context 圧縮 checkpoint を開始する。
- `75%` を hard stop とし、圧縮 checkpoint または fresh coordinator 切り替えなしに新しい phase / worker dispatch へ進まない。
- session pressure が直接計測できない環境でも、Spec Gate、Issue Gate、Execution Plan Gate、worker dispatch、review/fix cycle、resume、delivery で必ず checkpoint できる。
- phase transition 自体を mandatory compaction point とし、次 phase は carry-forward capsule と canonical artifact path から再開する。
- read-set budget と session context pressure を混同しない。`validate_skill_context.py` は read-set budget validator のまま維持する。
- 圧縮結果は chat だけに置かず、spec、issue ledger、normalized input packet、Execution Envelope、runtime state、resume brief、worker report のいずれかの durable artifact に寄せる。
- 圧縮後に復元が必要な情報は、path、hash、revision、ID、branch、command、review range、approval state から再読込できる。

## 採用した判断

- 新しい user-facing skill は追加しない。`context-compaction` は internal reference / family policy / script advisory として扱う。
- family-level の session pressure policy は `skill-architecture.toml` の `repository-change-loop` family に置く。
- `grill-to-pr-loop` には短い trigger rule と詳細 reference `references/context-compaction.md` を追加する。
- `issue-implementation-loop` には execution coordinator / runtime / worker packet 向けの context compaction rule を追加する。
- `context-contract.toml` には dedicated `context-compaction` operation を追加する。ただし通常 operation read-set へ常時混ぜない。65% trigger 時は current operation を維持したまま、`context-compaction` read-set を conditional overlay として追加で読む。
- `skill-architecture.toml` の policy 表現は、現行 architecture parser が読める TOML subset に合わせる。boolean を使う場合は parser / validator / test 拡張を同じ issue に含める。
- `report_skill_context.py` は operator-supplied session pressure を advisory 表示できるようにする。session pressure は host / UI / runtime が持つ値であり、repo 内 read-set metrics から推定しない。
- `Execution Envelope.context_policy` には session compaction policy を持たせる。ただし worker packet の `context_policy` は strict schema のため、worker packet には session-level field を混ぜない。
- phase transition では pressure に関係なく context GC を実行する。これは host transcript の物理削除ではなく、次 phase が前 phase の raw discussion / raw JSON / full output / diff 全文を前提にしない operational contract とする。
- 実装 handoff 前は、session pressure が 65% 未満でも必ず圧縮済み handoff brief または fresh execution coordinator を使う。
- 生成する仕様、Issue 台帳、human-facing report、packet の user-facing string は日本語ベースにする。schema key、path、command、ID、branch、hash、error message は維持する。

## 忘れてはいけないこと

圧縮後も durable artifact または bounded brief に必ず残す。

### 保持情報の責務境界

- `grill-to-pr-loop` が保持責務を持つ planning / gate 情報: ユーザー要件、採用済み判断、非目標、Epic ID、spec path、Issue 台帳 path、gate 承認状態、blocker graph、remote policy、handoff brief。
- `issue-implementation-loop` が保持責務を持つ execution / runtime 情報: normalized input packet path、Execution Envelope、runtime root / event log、worker packet、worker report、review range / finding、verification、PR_READY / delivery candidate。
- 両 skill で共有して消してはいけない approval / safety 情報: external write、push、PR 作成、merge、credential、permission、billing、destructive action の承認状態、human-only final merge boundary、source revision / hash。

### 共通保持リスト

- ユーザーの最終要件、採用済み判断、明示的な非目標。
- `Epic ID`、spec path、issue ledger path、packet path、envelope path、runtime root。
- gate 承認状態、承認日時、承認対象、commit 延期の例外。
- remote write policy、未承認 action、human-only merge boundary。
- Issue ID、タイトル、acceptance criteria、non-goals、write scope、dependency / blocker graph。
- `epic_base.ref`、`epic_base.sha`、branch / worktree reservation、base policy。
- 実行中の issue status、pending human request、blocker release condition。
- review range、Critical / Important finding、fix status、accepted residual risk。
- verification command と結果。長い output は report file に置き、summary と path を残す。
- source revision、runtime revision、digest / hash、resume brief freshness metadata。
- dirty changes がある場合の overlap 判断と保護対象。
- 外部送信、push、PR 作成、merge、credential、permission、billing、destructive action の承認有無。

## 忘れてもいいこと / 圧縮してよいこと

次の情報は、必要な要約・結論・path が durable artifact に残った後は chat context から落としてよい。

- 採用されなかった探索案の長い往復。採用しない理由は spec の `非目標` または `採用しなかった案` に短く残す。
- `rg` / `sed` / test output の全文。意味のある failure / result / command だけ残す。
- 既に `index.md`、`log.md`、spec、ledger に反映済みの説明。
- full spec、full issue ledger、full ADR、full glossary、full source summary。以後は path / hash / relevant section で参照する。
- raw JSON / raw YAML / raw TOML の全文。schema version、path、digest、重要 key summary だけを carry-forward capsule に残す。
- diff 全文、patch 全文、review log 全文。review range、commit、affected file summary、finding / fix status に圧縮する。
- worker が再読込できる code excerpt。worker packet には短い excerpt だけ残す。
- stale な draft wording、古い branch 名候補、却下済み issue 分解案。
- resolved review comments の詳細な議論。final finding、fix commit、review range は残す。
- repeated tool preflight output。最後に使った preflight command と結果だけ残す。
- implementation worker の局所的な試行錯誤。worker report と commit / verification に集約する。

## 圧縮してはいけないこと

- 未解決の設計質問、human wait、risk acceptance request。
- approval boundary と remote policy。
- acceptance criteria、write scope、dependency、stop condition。
- review finding の severity、scope、未対応状態。
- source revision / digest / branch / commit / path / command。
- runtime event ordering。resume brief は cache であり、runtime state と events が canonical。
- secret、credential、個人情報、外部送信前の確認事項。要約で隠してよいが、承認状態は消さない。

## Phase Transition Context GC

すべての phase exit で、session pressure に関係なく context GC を実行する。ここでの GC は transcript の物理削除ではなく、次 phase で参照してよい情報を bounded carry-forward capsule と canonical artifact path に限定する運用契約である。

Phase exit では次を必須にする。

- canonical artifact へ保存済みか確認する。保存先は spec、Issue 台帳、input packet、Execution Envelope、runtime state、event log、worker report、review report、resume brief のいずれかに限定する。
- carry-forward capsule を作る。内容は current phase result、next phase entrypoint、canonical paths、revision / digest、open decision、approval state、pending risk、verification summary に限定する。
- raw discussion、raw JSON、full command output、diff / patch 全文、古い draft、却下済み分岐、局所的な実装試行錯誤を drop 対象にする。
- 次 phase は capsule と canonical paths から再開する。前 phase の chat context、長い JSON、長い tool output、過去 diff を前提にしない。
- 再読込が必要な場合は、capsule に残した path / revision / digest から scope を絞って読む。chat 上の記憶から復元しない。

carry-forward capsule の上限は default 400 words、hard 600 words とする。JSON / code / diff を inline する場合は、合計 80 lines を hard limit とし、それ以上は file path と digest に寄せる。

## Phase 別の圧縮処理

| Phase | 圧縮 trigger | 許可される圧縮処理 | 圧縮後に残す正本 |
| --- | --- | --- | --- |
| Intake / Applicability | session pressure `>=65%`、または loop 適用判断が長引いた時 | ユーザー要件、採用仮定、未解決質問を 1 つの intake summary に集約。小さい task と判断した場合は loop を終了する | spec draft または chat summary。loop 継続時は `knowledge/wiki/syntheses/<epic>-spec.md` |
| Grill / Design Interrogation | 65% 到達、または unresolved choice が 3 件以上残る時 | Q&A の全文を落とし、accepted decisions、rejected alternatives、open questions に分ける | spec draft の `採用した判断`、`非目標`、`停止条件` |
| Spec Synthesis / Spec Gate | Spec Gate 提示前、または 65% 到達 | raw discussion を spec に反映し、gate presentation は path、Epic ID、主要判断、AC、検証、remote policy に限定する | spec path、spec hash / revision、`knowledge/index.md`、`knowledge/log.md` |
| Issue Gate | issue 分解後、Issue Gate 提示前、または 65% 到達 | issue rationale の長文を各 issue の短い acceptance / non-goal に圧縮。blocker graph を表へ集約 | local issue ledger、blocker graph、issue status |
| Execution Plan Gate | 必須。65% 未満でも handoff 前に実行 | main planning context を normalized packet + bounded handoff brief に圧縮。full spec / ledger は貼らない | normalized input packet、handoff brief、capability preflight、ledger/log |
| `issue-implementation-loop prepare` | execution coordinator 開始時、または 65% 到達 | packet と approved ledger から Execution Envelope を作り、planning chat 依存を切る | Execution Envelope、runtime root、event log |
| Worker Dispatch | 各 worker / reviewer dispatch 前 | worker packet を paths-first / max 450 words default / hard 800 words / read paths 8 件以下 / inline excerpt 300 words 以下に圧縮 | worker packet、source revision、assigned read paths |
| Human Wait | human request 作成時、または wait が長引く時 | affected issue / decision だけに scope を絞り、epic 全体の文脈を貼らない | human request artifact、runtime event、pending scope |
| Review / Fix Cycle | review report 受領時、fix dispatch 前、2 cycle 目開始前 | finding を severity / scope / required fix / risk acceptance に圧縮。diff 全文は report path へ逃がす | review report、fix worker packet、runtime state |
| Resume / Status | interruption 後、65% 到達、または status request | `build_resume_brief.py` で 600 words 以下の cache を生成し、meta freshness を検証する | runtime state、events、resume-brief.md、resume-brief.meta.json |
| Delivery / Remote Gate | external write 前は常に | PR-ready branch、remote action set、approval state だけに圧縮。implementation detail は execution result path へ逃がす | local ledger、execution result、Remote Gate record |
| Completion Report | 完了報告前 | 実装詳細を issue status / verification / review / residual risk に圧縮 | completion report、ledger、index/log |

## 実装範囲

Spec Gate 承認後、次の slice として実装する。

1. `skill-architecture.toml` に repository-change-loop family の `context_compaction` policy を追加する。
   - `soft_trigger_percent = 65`
   - `hard_stop_percent = 75`
   - `mandatory_handoff_compaction = 1`
   - `mandatory_handoff_compaction` は現行 TOML subset の integer flag として `1` を mandatory とする。boolean を採用する場合は、architecture parser / validator / regression test の更新を LSCC-001 に含める。
2. `grill-to-pr-loop` に context compaction reference を追加する。
   - entrypoint には 65% trigger と conditional overlay router だけを置く。
   - 詳細な keep/drop taxonomy、phase transition GC rule、phase matrix は `references/context-compaction.md` に置く。
   - `context-contract.toml` には dedicated `context-compaction` operation を追加する。65% trigger 時は current operation の required references を維持したまま conditional overlay として読み、通常 operation read-set は増やさない。
3. `issue-implementation-loop` に execution context compaction reference を追加する。
   - Execution Envelope、runtime state、resume brief、worker packet の責務境界を明示する。
   - prepare / execute / review / resume / deliver の phase exit で carry-forward capsule を作り、次 phase が raw worker JSON / full report / diff 全文に依存しないことを固定する。
   - worker packet schema には session-level field を混ぜない。
4. `Execution Envelope.context_policy` に `session_compaction` を追加する。
   - soft / hard trigger、handoff brief 上限、phase transition GC、mandatory checkpoint phase を schema / template / validator で固定する。
   - context policy 変更時は envelope revision を要求する。
5. `report_skill_context.py` に session pressure advisory を追加する。
   - 例: `--session-pressure-percent 65` を受け取り、`session_context.compaction_required=true` を JSON/text に出す。
   - report advisory は evidence / operator feedback であり、workflow trigger の唯一の source にはしない。phase checkpoint と conditional overlay rule を別途 skill contract で固定する。
   - `validate_skill_context.py` は read-set budget only のまま維持する。
6. regression tests と wiki ledger を更新する。
   - 65% trigger、hard stop、keep/drop taxonomy、phase matrix、envelope validation、report advisory、worker packet strictness を固定する。

## 非目標

- 新しい user-facing skill の追加。
- context compaction を LLM 任せの別 workflow framework にすること。
- session context pressure を read-set estimated token count から推定すること。
- `validate_skill_context.py` を session pressure validator にすること。
- worker packet に full spec / full ledger / full ADR を貼ること。
- worker packet schema に session-level policy を混ぜること。
- scheduler、dependency graph、runtime state の意味論を変更すること。
- GitHub issue mirror、push、PR 作成、merge、final PR merge。
- external dependency の追加。

## Issue 分解方針

Spec Gate 承認後に、日本語 local-first ledger として次の blocker order で Issue Gate に出す。

1. **LSCC-001: family-level context compaction policy を追加する**
   - `skill-architecture.toml`、architecture validator、report helper から 65% / 75% policy を読めるようにする。
   - 現行 architecture parser の TOML subset に合わせ、mandatory handoff compaction は integer flag `1` として固定する。boolean を使うなら parser / validator / regression を同時に更新する。
   - 新しい standalone skill を作らないことを regression で固定する。

2. **LSCC-002: `grill-to-pr-loop` の context compaction contract を追加する**
   - `SKILL.md` には短い trigger rule。
   - `references/context-compaction.md` に owner 境界つき keep/drop taxonomy、phase transition GC rule、planning phase matrix。
   - `context-contract.toml` に dedicated `context-compaction` operation を追加し、65% trigger 時だけ current operation の conditional overlay として読む。通常 operation read-set を肥大化させない。

3. **LSCC-003: `issue-implementation-loop` の execution compaction contract を追加する**
   - Execution Envelope / runtime / resume / worker packet の圧縮境界を reference に追加。
   - `context_policy.session_compaction` と phase transition GC を schema / template / validator に追加。
   - raw worker JSON、full report、diff 全文、実装試行錯誤を phase exit 後の carry-forward 対象から外す。
   - worker packet の strict `context_policy` は維持する。

4. **LSCC-004: session pressure advisory と regression を追加する**
   - `report_skill_context.py --session-pressure-percent` を追加。
   - JSON/text advisory、65% required、75% hard-stop warning、`--fail-on-warning` 挙動をテストする。
   - advisory は phase checkpoint / conditional overlay の代替ではないことを regression または contract test で固定する。
   - `validate_skill_context.py` が read-set budget only であることを引き続き確認する。

5. **LSCC-005: wiki ledger / packet / verification を仕上げる**
   - local issue ledger、input packet、Execution Envelope、index/log を更新。
   - full verification と implementation review evidence を集約する。

## 受け入れ条件

- `skill-architecture.toml` が repository-change-loop family の context compaction policy として `soft_trigger_percent=65` を持つ。
- session pressure `>=75%` では、新しい phase / worker dispatch / remote gate に進む前に圧縮または fresh coordinator 切り替えを要求する。
- `skill-architecture.toml` は `hard_stop_percent=75` を正確に持つ。hard stop の許容値は「75 以上」ではない。
- `skill-architecture.toml` は `mandatory_handoff_compaction=1` を持つ。または boolean 採用時は architecture parser / validator / regression が boolean を明示的に扱う。
- `grill-to-pr-loop` の entrypoint から 65% trigger と context compaction reference を発見できる。
- `grill-to-pr-loop/references/context-compaction.md` が「忘れてはいけないこと」「忘れてもいいこと」「圧縮してはいけないこと」を owner 境界つきで明示する。
- 同 reference が phase transition GC rule と phase 別圧縮 matrix を持つ。
- `context-compaction` operation は current operation の conditional overlay としてだけ使われ、通常 operation read-set には常時含まれない。
- `issue-implementation-loop` が Execution Envelope、runtime state、resume brief、worker packet の圧縮境界を明示する。
- `Execution Envelope.context_policy.session_compaction` が schema / template / validator で検証される。
- `context_policy.session_compaction.soft_trigger_percent` は `65` でなければならない。
- `context_policy.session_compaction.hard_stop_percent` は `75` でなければならない。
- worker packet の `context_policy` は session-level field を拒否し続ける。
- `report_skill_context.py --all --json --session-pressure-percent 65` が `session_context.compaction_required=true` を返す。
- `report_skill_context.py --all --session-pressure-percent 65` の text output は短い advisory 行だけを追加する。
- `validate_skill_context.py --all` は session pressure を扱わず、read-set budget validator のまま通る。
- 各 phase exit で carry-forward capsule が作られ、次 phase は capsule と canonical paths から再開することを契約または regression で確認できる。
- carry-forward capsule は default 400 words / hard 600 words、inline JSON / code / diff は合計 80 lines 以下である。
- raw JSON / full output / diff 全文 / 過去の実装試行錯誤は、phase exit 後の carry-forward context へ残らない。
- existing context budget は、通常 operation read-set の headroom minimum を下回らない。
- Spec / Issue / Execution Plan Gate 承認後の commit boundary は維持される。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json --session-pressure-percent 65
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --session-pressure-percent 75 --fail-on-warning
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_execution_envelope.py <execution-envelope.json>
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py <worker-packet.json> --json
git diff --check
```

`quick_validate.py` は PyYAML dependency が使える場合だけ追加検証とする。

## リモート書き込み方針

`local_only`。

GitHub issue mirror、push、PR 作成、PR ready 化、merge はこの spec では行わない。final PR merge は常に human-only。

## 人間レビューゲート

- **Spec Gate**: この spec の Epic ID、採用した判断、非目標、受け入れ条件、検証、停止条件を承認する。
- **Issue Gate**: LSCC issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: normalized input packet、write scopes、dependency graph、fallback policy、remote policy を承認する。
- **Implementation Review Gate**: 各 issue completion / blocker release / PR_READY 前に issue-scoped implementation review を実施する。
- **Remote Gate**: 外部 write が必要になった場合だけ exact action set を提示し、明示承認を待つ。

Spec Gate / Issue Gate / Execution Plan Gate は承認後に、承認済み local artifacts と `knowledge/log.md` 更新を commit してから次フェーズへ進む。ユーザーが明示的に commit 延期を指示した場合は、その例外を ledger / log に記録する。

## 停止条件

- 65% trigger が文書上の注意だけになり、Execution Plan Gate / worker dispatch / resume で機械的に確認できない。
- context compaction reference を通常 read-set に入れた結果、既存 operation の context budget が悪化する。
- conditional overlay が operation switch になり、current operation の required references を落としてしまう。
- phase transition 後も raw JSON、full output、diff 全文、過去の実装試行錯誤を carry-forward し続ける。
- `context-contract.toml` と family policy が read-set source of truth と session policy source of truth を混同する。
- worker packet に session-level field を混ぜ、worker dispatch schema を曖昧にする。
- 圧縮によって acceptance criteria、write scope、dependency、approval boundary、review finding が欠落する。
- scheduler / runtime / delivery semantics を変更しないと実装できない。
- remote write または破壊的操作が必要になる。

## 既知のリスク

- session pressure は host / UI / model runtime 依存で、repo 内だけでは正確に計測できない。したがって初期実装は operator-supplied advisory と phase checkpoint を組み合わせる。
- host / UI が transcript を保持する場合、skill 側では物理的な context 削除を保証できない。保証するのは、次 phase が raw past context を再利用せず、bounded capsule と canonical artifact だけを入力として扱うこと。
- hard stop を強くしすぎると、緊急の small fix や user clarification を止めすぎる可能性がある。stop は新 phase / worker dispatch / remote action の前に限定する。
- 圧縮 brief を canonical state と誤認すると stale state を固定する危険がある。canonical は spec、ledger、packet、envelope、runtime state、events であり、brief は cache として扱う。
- context compaction reference を詳しくしすぎると、skill 自体の context pressure が悪化する。entrypoint は短く、詳細は dedicated operation で読む。

## 関連ページ

- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Issues](skill-repository-optimization-v4-issues.md)
- [Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md)
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md)
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)

## 出典

- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/core.md](../../../skills/grill-to-pr-loop/references/core.md)
- [skills/grill-to-pr-loop/references/execution-handoff.md](../../../skills/grill-to-pr-loop/references/execution-handoff.md)
- [skills/grill-to-pr-loop/context-contract.toml](../../../skills/grill-to-pr-loop/context-contract.toml)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/issue-implementation-loop/references/core.md](../../../skills/issue-implementation-loop/references/core.md)
- [skills/issue-implementation-loop/references/execution-envelope.md](../../../skills/issue-implementation-loop/references/execution-envelope.md)
- [skills/issue-implementation-loop/references/runtime-state.md](../../../skills/issue-implementation-loop/references/runtime-state.md)
- [skills/issue-implementation-loop/references/worker-contract.md](../../../skills/issue-implementation-loop/references/worker-contract.md)
- [skills/issue-implementation-loop/context-contract.toml](../../../skills/issue-implementation-loop/context-contract.toml)
- [skill-architecture.toml](../../../skill-architecture.toml)
- [scripts/report_skill_context.py](../../../scripts/report_skill_context.py)
- [scripts/validate_skill_context.py](../../../scripts/validate_skill_context.py)
