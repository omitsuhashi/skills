# Loop Review Governance Spec

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。Execution Envelope revision 2 prepare 済み。LRG-001 から LRG-005 は final PR branch に統合済み。draft PR 作成はユーザー承認済み。GitHub issue mirror、ready-for-review、merge、force push、deploy、credential、permission、billing、production、destructive action は未承認。

## 仕様レビュー

ユーザー提示仕様に異論はない。採用する。

ただし、実装契約としては「堅牢化提案をレビューから消す」のではなく、「Issue 意図適合レビュー」と「堅牢化候補」を別 lane として扱う必要がある。前者は毎回の Issue 実装レビューで必須、後者は AI が発見してよいが、修正実行は最終 PR 前の人間判断まで禁止する。

追加の設計補強として、堅牢化候補のうち credential、権限、データ破壊、security regression、production impact など delivery risk があるものは、勝手に直さず、かつ黙って通さず、`safety_escalation` として人間判断待ちにする。

## 問題設定 / 成功条件

現行の `issue-implementation-loop` は、Issue 実装レビューで Critical / Important in-scope finding を修正する契約を持つ。この契約は Issue の意図を守るには有効だが、reviewer が「より堅牢にするならこうするべき」という scope-expanding hardening を Important finding として返した場合、AI coordinator / worker が Issue の意図を越えて修正しようとする余地がある。

成功条件は次の通り。

- Issue ごとの実装レビューでは、承認済み Issue / spec / acceptance criteria / non-goals / write scope / verification evidence に照らした意図適合を必ず確認する。
- Issue 意図、受け入れ条件、既存承認 scope に対する gap は blocking finding として扱い、既存 review/fix cycle の中で修正または人間 risk acceptance を要求する。
- 承認済み Issue を越える堅牢化、設計改善、保守性改善、追加検証、追加防御は `hardening_candidate` として記録し、Issue completion / blocker release のために自動修正しない。
- final PR delivery 前に、未判断の `hardening_candidate` を人間へ提示し、取り込む / 後続へ送る / 採用しない / risk acceptance のどれかを明示決定する。
- 人間が「取り込む」を選んだ候補だけを、current PR の追加 scope として local issue ledger / execution packet / envelope revision に載せて実装する。

## Epic ID

`loop-review-governance`

## 現在の前提

- spec 作成前の `git status --short`: clean。作成後の未コミット差分は、この spec、`knowledge/index.md`、`knowledge/log.md` のみ。
- 計画前提チェック: `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase planning` は通過済み。
- 2026-07-01 にユーザーが Spec Gate を承認した。
- 2026-07-01 にユーザーが Issue Gate を承認した。
- 2026-07-01 にユーザーが Execution Plan Gate を承認した。
- `grill-to-pr-loop` は planning / spec / issue ledger / execution packet を所有し、実装は `issue-implementation-loop` に委譲する。
- `issue-implementation-loop/references/review-gate.md` は、現在「approved local/remote issue、requirements/spec、acceptance criteria、non-goals、write scope、verification evidence」に対する gap だけを review scope としている。
- `issue-implementation-loop` は issue implementation review を 2 cycle まで実行し、未解決 Critical / Important in-scope finding は人間 risk acceptance なしに completion / blocker release / PR readiness へ進めない。
- runtime root は `.git/agent-runs/issue-implementation-loop/<epic-id>/` 配下で、reports、reviews、decisions、events、runtime-state を coordinator が管理する。
- final PR 作成は remote policy が承認済みの場合だけ可能で、final PR merge、ready-for-review、force push、production / credential / permission / billing / destructive action は常に別の人間 action である。

## 採用した判断

- Review finding を `intent_gap`、`implementation_regression`、`hardening_candidate`、`safety_escalation`、`classification_needed` に分類する。
- `intent_gap` は承認済み Issue / spec / acceptance criteria / non-goals / write scope / verification evidence が満たされていない状態とする。これは blocking。
- `implementation_regression` は今回の実装が既存挙動、契約、検証対象を壊した状態とする。Issue scope 内または changed-code caused なら blocking。
- `hardening_candidate` は「承認済み source artifact は満たしているが、より堅牢にする提案」とする。Issue completion の blocker ではなく、final PR 前の人間判断 queue に送る。
- `safety_escalation` は未承認 scope でも delivery risk が高いものとする。自動修正は禁止し、delivery 前に人間判断を必須にする。
- 分類不能な finding は `classification_needed` として、人間確認または coordinator の evidence-based classification を必要とする。曖昧なまま自動修正しない。
- 既存の 2 review cycle 上限は `intent_gap` / `implementation_regression` の fix loop に適用する。`hardening_candidate` の記録だけでは fix cycle を消費しない。
- `hardening_candidate` を current PR に取り込む場合は、追加 scope として local issue ledger に amendment issue を作り、Execution Envelope revision を上げて通常の issue 実装レビューを通す。
- `hardening_candidate` を採用しない場合も、候補 ID、判断、理由、判断者、日時、対象 issue を coordinator-owned decision artifact に残す。
- Issue 実装レビューの既定手段は `superpowers:requesting-code-review` とする。利用できない場合は、承認済み equivalent reviewer または manual fallback へ切り替える判断を人間に確認し、黙って省略しない。

## Finding 分類

| 分類 | 判定基準 | Issue completion blocker | 自動修正 | 人間判断 |
| --- | --- | --- | --- | --- |
| `intent_gap` | 承認済み Issue / spec / acceptance criteria / non-goals / write scope / verification evidence を満たしていない | はい | scope 内なら可 | 2 cycle 後も残る場合は必要 |
| `implementation_regression` | 今回の変更で既存契約、検証対象、互換性、データ形状を壊した | はい | scope 内なら可 | scope 外または判断が必要なら必要 |
| `hardening_candidate` | source artifact は満たすが、防御、検証、保守性、設計余裕を増やせる | いいえ | 不可 | final PR 前に必要 |
| `safety_escalation` | security、credential、permission、destructive、production、data loss など delivery risk がある | delivery blocker | 不可 | 必須 |
| `classification_needed` | 上記分類を evidence で決めきれない | 対象 issue または delivery を一時停止 | 不可 | 必須 |

## Context / token budget 方針

この spec は分類語彙を増やすが、実行時 context を増やすためのものではない。運用上は次の制約を acceptance とする。

- 分類は compact enum として扱い、各 finding に長い説明を持たせない。
- `SKILL.md` に詳細を追加しない。既存 reference に短い差分を入れ、必要なら `execute.review` / `deliver` だけで読む conditional reference に分ける。
- review packet は paths-first とし、full spec、full ledger、full diff、full review transcript を貼らない。issue summary / acceptance excerpt / non-goals excerpt は各 120 words 以下、packet 全体は default 600 words / hard 900 words を目安にする。
- reviewer report の carry-forward は `review_range`、verdict、blocking finding summary、candidate registry path だけにする。full report は path 参照に留める。
- `hardening_candidate` は 1 candidate 80 words 以下、1 issue 5 件以下を default とする。超過する場合は reviewer が priority 付き summary に圧縮し、必要なら人間が追加探索を明示する。
- final PR 前の decision brief は candidate ごとの full text ではなく、ID、source issue、summary、risk、recommended decision の compact table にする。詳細は `hardening-candidates.json` を path で参照する。
- 実装後は `validate_skill_context.py --all` と `report_skill_context.py --all --json` で read-set 増加を確認する。context baseline が悪化する場合は、reference 分割または wording 圧縮を先に行う。

## 詳細設計

### 1. Issue 実装レビュー packet

reviewer へ渡す packet は、現在の narrow review intent を維持しつつ、出力を 2 lane に分ける。

レビュー手段は `superpowers:requesting-code-review` を第一候補にする。`BASE_SHA` / `HEAD_SHA` を使った committed range review とし、レビュー依頼には下の narrow intent を含める。

```text
まず「Issue 意図適合レビュー」を行う。
対象は approved issue、spec、acceptance criteria、non-goals、write scope、verification evidence に対する gap だけ。
ここで見つかった gap は intent_gap または implementation_regression として分類する。

次に「堅牢化候補」を任意で列挙する。
source artifact は満たしているが、より堅牢にする提案は hardening_candidate として分類する。
hardening_candidate は、この review/fix cycle では修正要求にしない。

分類できない finding は classification_needed として返す。
```

review report は少なくとも次を coordinator へ返す。

- `issue_id`
- `review_range`
- `intent_review.status`: `approved` / `changes_requested` / `classification_needed`
- `intent_findings[]`: `id`, `classification`, `severity`, `source_artifact`, `why_blocking`, `required_fix`
- `hardening_candidates[]`: `candidate_id`, `source_issue`, `summary`, `rationale`, `suggested_change`, `risk_if_deferred`, `estimated_scope`, `delivery_blocker`
- `safety_escalations[]`: `candidate_id`, `reason`, `required_human_decision`

Markdown fallback の場合も同じ見出しを必須にし、機械可読 JSON を必須にしない。最初の実装では、既存 reviewer report を壊さず、coordinator が summary artifact へ正規化する。

### 2. Coordinator-owned candidate registry

`hardening_candidate` は worker branch に混ぜず、runtime root の coordinator-owned artifact に集約する。

推奨 path:

```text
<runtime-root>/decisions/hardening-candidates.json
```

形は次を最小 contract とする。

```json
{
  "schema_version": 1,
  "epic_id": "loop-review-governance",
  "candidates": [
    {
      "candidate_id": "HC-G2PR-001-001",
      "source_issue": "G2PR-001",
      "classification": "hardening_candidate",
      "summary": "追加の境界ケース検証を入れる",
      "rationale": "現在の acceptance criteria は満たすが、将来の入力拡張に強くなる",
      "suggested_change": "対象 validator に追加 fixture を加える",
      "risk_if_deferred": "低。既存 Issue の成功条件には影響しない",
      "estimated_scope": ["tests/...", "skills/..."],
      "delivery_blocker": false,
      "decision": "pending_decision",
      "decision_reason": null,
      "decided_by": null,
      "decided_at": null,
      "implementation_issue": null
    }
  ]
}
```

`decision` は `pending_decision`、`approved_for_current_pr`、`deferred_follow_up`、`declined`、`risk_accepted`、`implemented` のいずれかにする。

### 3. Runtime / scheduler semantics

- `intent_gap` / `implementation_regression` が残る issue は既存通り `fixable` または `WAITING_HUMAN` にする。
- `hardening_candidate` だけが残る issue は、Issue completion / blocker release / local `PR_READY` を妨げない。
- `safety_escalation` または `classification_needed` は、scope に応じて issue / descendants / resource / epic の `human_request_opened` を出す。
- `hardening_candidate` は issue-level work を止めず、final delivery lane の pending decision として扱う。
- resume brief は `Pending hardening decisions: N` と candidate registry path を短く出す。

### 4. Draft Final PR 後の Human Decision Gate

draft final PR を作成する前に、coordinator は `hardening-candidates.json` を読み、`pending_decision` を人間が読める compact table と PR body に集約する。

`pending_decision` は draft final PR 作成を止めない。統合 diff を見たうえで、ready-for-review、merge、risk acceptance、または candidate 取り込み実装へ進む前に、人間が全 candidate を一括判断する。

提示単位は candidate ごとに次を含める。

- candidate ID
- source issue
- 提案 summary
- なぜ Issue 意図適合ではなく堅牢化候補なのか
- 取り込む場合の想定 write scope
- 取り込まない場合の risk
- coordinator 推奨: `取り込む` / `後続へ送る` / `採用しない` / `risk acceptance`

人間の選択肢は次に固定する。

- `取り込む`: current PR scope に追加する。local issue ledger に amendment issue を追加し、Execution Envelope revision を上げ、`issue-implementation-loop` で通常実装する。
- `後続へ送る`: current PR には入れない。必要なら follow-up issue / synthesis に残す。
- `採用しない`: current PR に入れず、理由を decision artifact に残す。
- `risk acceptance`: `safety_escalation` など delivery risk を認識したうえで delivery 継続を許可する。対象と理由を明記する。

`pending_decision` が残ったまま ready-for-review 化、merge、risk acceptance、または candidate 取り込み実装へ進んではならない。draft final PR 作成は許可する。

### 5. 判断点と判断主体

| 判断点 | タイミング | 一次判断者 | 入力 | 出力 | 自動実行してよいこと |
| --- | --- | --- | --- | --- | --- |
| finding 分類 | Issue 実装レビュー中 | `superpowers:requesting-code-review` reviewer が提案し、coordinator が source artifact と照合して確定 | review packet、spec / issue path、acceptance criteria、review range | `intent_gap` / `implementation_regression` / `hardening_candidate` / `safety_escalation` / `classification_needed` | `intent_gap` / `implementation_regression` の scope 内 fix |
| 分類不能の扱い | review intake 直後 | coordinator、必要なら人間 | reviewer finding、source artifact、write scope | issue-scoped `human_request_opened` または分類確定 | なし。曖昧なまま修正しない |
| candidate 登録 | review intake 後、issue completion 前 | coordinator | reviewer の `hardening_candidate` / `safety_escalation` summary | `<runtime-root>/decisions/hardening-candidates.json` | registry への記録のみ |
| Issue completion / blocker release | candidate 登録後 | coordinator | review verdict、blocking findings、candidate registry path | completion / release / `PR_READY` 判断 | `hardening_candidate` だけなら issue completion 可 |
| draft PR 後 candidate 採否 | draft final PR 作成後、ready-for-review / merge / candidate 取り込み前 | 人間 | PR diff、compact decision brief、candidate registry path、coordinator 推奨 | `approved_for_current_pr` / `deferred_follow_up` / `declined` / `risk_accepted` | なし。採否決定は人間のみ |
| current PR 取り込み | 人間が `approved_for_current_pr` を選んだ後 | planning coordinator | human decision、candidate scope | amendment issue、ledger 更新、envelope revision | 承認済み amendment issue の実装 handoff |
| draft PR delivery preflight | draft final PR delivery plan validation 時 | coordinator / validator | runtime state、delivery plan、candidate registry | draft PR allowed / validation error / decision gate blocker report | 未判断候補を PR body に載せて draft final PR を作成する |

`safety_escalation` は draft PR 作成を止めず、ready-for-review / merge blocker として扱う。人間が risk acceptance するか、追加 issue として修正するまで ready-for-review / merge へ進まない。

### 6. Delivery validation

`validate_delivery_plan.py` または delivery preflight は、draft final PR action の前に candidate registry を確認する。

- `hardening-candidates.json` が存在し、`pending_decision` または unresolved `safety_escalation` がある場合、draft final PR 作成は fail せず、`pending_hardening_candidates` と `decision_gate_blockers` に出す。
- `deferred_follow_up` / `declined` / `risk_accepted` は draft final PR 作成を許可するが、completion report に residual risk として出す。
- `approved_for_current_pr` は、対応する `implementation_issue` が `PR_READY` / integrated / review approved でなければ `decision_gate_blockers` に残す。
- `local_only` の completion report でも、未判断候補があれば `pending_hardening_candidates` として報告する。

### 7. Skill surface update

`skill-creator` の方針に従い、`SKILL.md` は短く保つ。詳細は reference 側へ置く。

想定変更先:

- `skills/issue-implementation-loop/references/review-gate.md`
  - `superpowers:requesting-code-review` を第一候補とし、finding taxonomy、2 lane review intent、candidate handling を追加する。
- `skills/issue-implementation-loop/references/human-wait.md`
  - `hardening_candidate` は issue execution を止めず、final delivery decision として扱うことを追加する。
- `skills/issue-implementation-loop/references/remote-delivery.md`
  - final PR delivery 前の candidate decision gate と validation を追加する。
- `skills/issue-implementation-loop/references/runtime-state.md`
  - candidate registry path と resume brief 表示を追加する。
- `skills/issue-implementation-loop/assets/templates/execution-envelope.json`
  - `review_policy.hardening_candidates` 相当の既定値を追加するか、reference-only policy に留めるかを Issue Gate で決める。
- `skills/issue-implementation-loop/assets/schemas/*`
  - candidate registry を schema 化する場合は最小 schema を追加する。
- `skills/issue-implementation-loop/tests/*`
  - intent finding は blocking、hardening candidate は auto-fix されず delivery 前に人間判断へ送られる regression を追加する。
- `skills/grill-to-pr-loop/references/execution-handoff.md`
  - input packet / envelope に review governance policy を含める場合の handoff contract を追加する。
- `knowledge/wiki/syntheses/*`
  - Issue Gate 後に local issue ledger、input packet、execution envelope を追加する。

## 非目標

- 堅牢化提案を禁止すること。
- reviewer が general quality suggestion を一切出せないようにすること。
- Issue acceptance criteria を満たしていないものを `hardening_candidate` として逃がすこと。
- 人間判断なしで scope-expanding hardening を実装すること。
- final PR ready-for-review、final PR merge、force push、deploy、credential、permission、billing、production、destructive action の自動化。
- 新しい user-facing skill の追加。
- reviewer report を初回から完全 JSON 必須にすること。

## Issue 分解方針

Spec Gate 承認後に、次の blocker order で日本語 local-first ledger を作る。

1. **LRG-001: Review finding taxonomy と 2 lane packet を定義する**
   - `review-gate.md` に intent review と hardening candidate lane を追加する。
   - `superpowers:requesting-code-review` を第一候補とする reviewer prompt / packet wording を固定する。
   - `classification_needed` の停止条件を明記する。

2. **LRG-002: Candidate registry と human decision artifact を追加する**
   - `hardening-candidates.json` の template / schema / coordinator update contract を追加する。
   - runtime / resume brief / human request の扱いを更新する。
   - worker branch に candidate decision artifact を混ぜない境界を固定する。
   - candidate 件数、summary 長、decision brief の context budget を固定する。

3. **LRG-003: Final delivery preflight に pending candidate check を追加する**
   - draft final PR delivery plan validation が unresolved candidate を `pending_hardening_candidates` / `decision_gate_blockers` に出す。
   - `approved_for_current_pr` は amendment issue 実装済みでなければ ready-for-review / merge 不可にする。
   - `deferred_follow_up` / `declined` / `risk_accepted` は completion report に残す。

4. **LRG-004: Execution handoff / envelope policy を同期する**
   - `grill-to-pr-loop` 側の execution handoff に review governance policy を伝える。
   - Envelope に持たせるか reference-only にするかを実装時に固定し、validator / template / docs を一致させる。

5. **LRG-005: Regression tests と wiki discoverability を更新する**
   - intent gap と hardening candidate の混同防止テストを追加する。
   - final PR 前に未判断 candidate があると止まるテストを追加する。
   - context budget が悪化していないことを `validate_skill_context.py --all` と `report_skill_context.py --all --json` で確認する。
   - `knowledge/index.md` / `knowledge/log.md` / local issue ledger を同期する。

## 受け入れ条件

- Issue 実装レビューは、Issue 意図適合を毎回必須で確認する契約になっている。
- Issue 実装レビューは `superpowers:requesting-code-review` を第一候補にし、未利用時は承認済み equivalent / manual fallback を要求する。
- reviewer packet は、`intent_gap` / `implementation_regression` と `hardening_candidate` を混同しない wording を持つ。
- reviewer packet、candidate registry、decision brief に context budget 上限がある。
- `hardening_candidate` は Issue completion / blocker release のために自動修正されない。
- `hardening_candidate` は final PR 前に人間判断 queue として提示される。
- `pending_decision` の候補が残っていても draft final PR は作成でき、PR body / decision artifact に一括判断対象として載る。
- `pending_decision` の候補が残ったまま ready-for-review、merge、risk acceptance、candidate 取り込み実装へ進まない。
- 人間が取り込みを選んだ候補は、追加 Issue / envelope revision / review gate を通る。
- 人間が後続送り、採用しない、risk acceptance を選んだ候補は、completion report と decision artifact に残る。
- `safety_escalation` は自動修正されず、delivery 前に人間判断を必須にする。
- 既存の worker-only policy、2 review cycle limit、remote approval boundary、final merge human-only は弱まらない。
- `SKILL.md` は肥大化させず、詳細は references / templates / schemas / tests に置く。
- `validate_skill_context.py --all` と `report_skill_context.py --all --json` が、review governance 追加後も read-set 増加を許容範囲内に保っている。

## 検証方針 / コマンド

実装フェーズでは少なくとも次を実行する。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
rg -n "hardening_candidate|intent_gap|safety_escalation|pending_decision|hardening-candidates" skills knowledge/wiki/syntheses scripts
git diff --check
```

追加した schema / validator がある場合は、対象 validator を fixture つきで個別実行する。

## リモート書き込み方針

この spec / Issue Gate / Execution Plan Gate / 実装ループの既定は `local_only` だったが、2026-07-01 のユーザー依頼により draft final PR 作成だけ承認済み。

GitHub issue mirror、ready-for-review、merge、force push、deploy、credential、permission、billing、production、destructive action は未承認。final PR merge は常に human-only。

## 人間レビューゲート

- **Spec Gate**: この spec の Epic ID、採用判断、非目標、受け入れ条件、検証、停止条件を承認する。
- **Issue Gate**: LRG-001 から LRG-005 の粒度、blocker graph、acceptance criteria、candidate registry の schema 化有無を承認する。
- **Execution Plan Gate**: normalized input packet、write scope、Execution Envelope revision、review governance policy、remote policy を確認する。
- **Implementation Review Gate**: 各 issue で intent review を必須にし、hardening candidate を自動修正しないことを確認する。
- **Hardening Candidate Decision Gate**: final PR 前に unresolved candidate の採否を人間が決める。
- **Remote Gate**: 承認済み remote policy 外の外部 write が必要な場合だけ exact action set を提示し、明示承認を待つ。

## 停止条件 / 既知のリスク

停止条件:

- Issue 意図適合の gap を `hardening_candidate` として扱い、blocking fix を回避しようとしている。
- 堅牢化候補を人間判断なしに実装しようとしている。
- `pending_decision` の候補が残ったまま ready-for-review、merge、risk acceptance、candidate 取り込み実装へ進めようとしている。
- `safety_escalation` を optional suggestion として扱っている。
- candidate registry が worker branch に混入している。
- `SKILL.md` に詳細を詰め込み、context budget を悪化させている。
- remote write または destructive / credential / permission / production action が必要になる。

既知のリスク:

- `hardening_candidate` が増えすぎると final PR 前の判断負荷が上がる。candidate は summary、scope、risk、推奨判断を短く揃える。
- 分類と decision artifact を増やしすぎると token 消費が増える。分類は compact enum、report は bounded summary、詳細は path 参照に限定する。
- reviewer が finding を過剰に `safety_escalation` へ寄せる可能性がある。security / credential / data loss / production impact などの明確な基準を reference に置く。
- 取り込み判断後に amendment issue を作るため、final PR 直前に scope が増える可能性がある。人間が「後続へ送る」を選びやすいよう、current PR に入れる条件を狭くする。
- candidate registry を schema 化すると実装量が増える。Issue Gate で reference-only / schema-backed のどちらにするか確認する。

## Spec 自己レビュー

- placeholder は残していない。
- `Epic ID` は `loop-review-governance` で固定した。
- Issue 意図適合と堅牢化候補の責務を分離した。
- Superpowers の `requesting-code-review` を Issue 実装レビューの第一候補として明記した。
- 判断点、判断主体、入力、出力、自動実行可否を表で明記した。
- context / token budget 方針を追加し、runtime に持ち回る情報を bounded summary と path 参照に制限した。
- 人間判断なしの scope expansion を禁止した。
- existing remote boundary、worker-only policy、2 review cycle limit、final merge human-only を弱めていない。
- 詳細は `SKILL.md` ではなく references / templates / schemas / tests に寄せる方針にした。

## 関連ページ

- [Loop Review Governance Issue 台帳](loop-review-governance-issues.md)
- [Grill To PR Loop Issue Implementation Review Gate Plan](grill-to-pr-loop-issue-implementation-review-gate-plan.md)
- [Loop Skill 運用単純化仕様](loop-skill-operational-simplicity-spec.md)
- [Loop Skill Context Compaction Spec](loop-skill-context-compaction-spec.md)
- [Loop Skill 自動継続 Gate 仕様](loop-skill-autonomous-gates-spec.md)

## 出典

- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/planning-contract.md](../../../skills/grill-to-pr-loop/references/planning-contract.md)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/issue-implementation-loop/references/review-gate.md](../../../skills/issue-implementation-loop/references/review-gate.md)
- [skills/issue-implementation-loop/references/human-wait.md](../../../skills/issue-implementation-loop/references/human-wait.md)
- [skills/issue-implementation-loop/references/runtime-state.md](../../../skills/issue-implementation-loop/references/runtime-state.md)
- [skills/issue-implementation-loop/references/remote-delivery.md](../../../skills/issue-implementation-loop/references/remote-delivery.md)
- [skills/issue-implementation-loop/assets/templates/execution-envelope.json](../../../skills/issue-implementation-loop/assets/templates/execution-envelope.json)
