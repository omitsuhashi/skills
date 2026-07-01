# Loop Review Governance Issue 台帳

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。LRG-001 から LRG-004 は PR_READY / review approved。LRG-005 は regression discoverability branch で検証済み。GitHub issue mirror、push、PR 作成、ready-for-review、merge は未承認。

## Source

- Epic ID: `loop-review-governance`
- 承認済み spec: [loop-review-governance-spec.md](loop-review-governance-spec.md)
- Spec Gate approval commit: `3a8069b9a0e80e13cda4b547974abba639ddb59e`
- Spec digest: `sha256:70f6d8879a4e17f219a532b7294863e775857d79a80f7e0c04fb346c16588edd`
- Issue Gate approval: 2026-07-01 user approved this local issue ledger.
- Execution Plan Gate approval: 2026-07-01 approved local-only worker execution from the normalized input packet and Execution Envelope.
- Remote policy: `local_only`

## Phase Transition Capsule

- Current phase result: Execution Plan Gate 承認済み。LRG-001 から LRG-004 は PR_READY / review approved。LRG-005 は regression / discoverability 同期を担当する。
- Next phase entrypoint: LRG-005 local scoped commit and coordinator review intake。
- Canonical paths: spec は [loop-review-governance-spec.md](loop-review-governance-spec.md)、issue ledger はこの file。
- Open decisions: pending hardening candidates を current PR に取り込む / 後続へ送る / 採用しない / risk acceptance のどれにするか。
- Pending risk: 未判断 hardening candidate は final PR delivery 前の人間判断が必要。LRG-005 ではこれらを実装しない。
- Execution Plan artifacts:
  - [loop-review-governance-input-packet.json](loop-review-governance-input-packet.json)
  - [loop-review-governance-execution-envelope.json](loop-review-governance-execution-envelope.json)
  - [loop-review-governance-handoff-brief.md](loop-review-governance-handoff-brief.md)
- Execution Plan preflight evidence:
  - `validate_input_packet.py knowledge/wiki/syntheses/loop-review-governance-input-packet.json`: `INPUT PACKET OK`
  - `validate_input_packet.py ... --json`: `{"ok": true, "errors": []}`
  - `check_capabilities.py --input ... --json`: `ok: true`; `requesting-code-review` と `tdd` 検出済み。remote write は未承認。
- Runtime evidence root: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance`

## Local Issue Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-review-governance | LRG-001 | review finding taxonomy と 2 lane packet を定義する | 承認済み | PR_READY | なし | LRG-002, LRG-004, LRG-005 | 未作成 | approved cycle 2 | 未作成 |
| loop-review-governance | LRG-002 | candidate registry と bounded decision artifact を追加する | 承認済み | PR_READY | LRG-001 | LRG-003, LRG-004, LRG-005 | 未作成 | approved cycle 1 | 未作成 |
| loop-review-governance | LRG-003 | final delivery preflight に pending candidate check を追加する | 承認済み | PR_READY | LRG-002 | LRG-005 | 未作成 | approved cycle 2 | 未作成 |
| loop-review-governance | LRG-004 | execution handoff / envelope policy を同期する | 承認済み | PR_READY | LRG-001, LRG-002 | LRG-005 | 未作成 | approved cycle 2 | 未作成 |
| loop-review-governance | LRG-005 | regression tests と wiki discoverability を更新する | 承認済み | 検証済み | LRG-001, LRG-002, LRG-003, LRG-004 | なし | 未作成 | 未実施 | 未作成 |

## Blocker Graph

```text
LRG-001
  -> LRG-002
  -> LRG-004
  -> LRG-005
LRG-002
  -> LRG-003
  -> LRG-004
  -> LRG-005
LRG-003 -> LRG-005
LRG-004 -> LRG-005
```

- PR_READY: LRG-001、LRG-002、LRG-003、LRG-004。
- 検証済み: LRG-005。
- ブロック中: なし。
- Cyclic blocker: なし。
- GitHub issue mirror / push / PR 作成 / merge: `local_only` のため未承認。
- Issue Gate 承認済みのため、全 issue の `レビュー状態` は `承認済み` とする。

## LRG-001: review finding taxonomy と 2 lane packet を定義する

### 目的

Issue 実装レビューで、Issue 意図適合の blocking finding と、堅牢化候補の non-blocking finding を混同しない review gate contract を追加する。

### Scope

- `skills/issue-implementation-loop/references/review-gate.md`
- `skills/issue-implementation-loop/tests/`
- 必要なら `skills/issue-implementation-loop/assets/templates/` の review packet 例

### Acceptance Criteria

- `review-gate.md` が `intent_gap`、`implementation_regression`、`hardening_candidate`、`safety_escalation`、`classification_needed` の分類を定義する。
- `superpowers:requesting-code-review` を Issue 実装レビューの第一候補として明記する。
- reviewer packet は `BASE_SHA` / `HEAD_SHA` の committed range review を前提にする。
- reviewer packet は Issue 意図適合レビューを必須 lane、堅牢化候補列挙を任意 lane として分ける。
- `intent_gap` / `implementation_regression` は blocking finding として既存 fix loop に乗る。
- `hardening_candidate` は review/fix cycle では自動修正要求にしない。
- `classification_needed` は曖昧なまま自動修正せず、coordinator か人間判断へ送る。
- review packet は paths-first で、default 600 words / hard 900 words の budget 方針を持つ。

### Non-goals

- reviewer report を初回から完全 JSON 必須にすること。
- `SKILL.md` を肥大化させること。

### 想定 write scope

- `path:skills/issue-implementation-loop/references/review-gate.md`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-review-governance-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `rg -n "intent_gap|hardening_candidate|requesting-code-review|600 words|900 words" skills/issue-implementation-loop`
- `git diff --check`

## LRG-002: candidate registry と bounded decision artifact を追加する

### 目的

`hardening_candidate` / `safety_escalation` を worker branch に混ぜず、coordinator-owned runtime artifact として集約し、final PR 前の人間判断に使える bounded decision surface を作る。

### Scope

- `skills/issue-implementation-loop/references/runtime-state.md`
- `skills/issue-implementation-loop/references/human-wait.md`
- `skills/issue-implementation-loop/references/context-compaction.md`
- `skills/issue-implementation-loop/assets/templates/` または `assets/schemas/` の candidate registry。schema-backed にするか reference-only にするかは Issue Gate で確認する。
- resume brief / runtime state tests

### Acceptance Criteria

- `<runtime-root>/decisions/hardening-candidates.json` を coordinator-owned artifact として定義する。
- candidate は ID、source issue、classification、summary、risk、estimated scope、decision、implementation issue を持つ。
- `hardening_candidate` は 1 件 80 words 以下、1 issue 5 件以下を default とする。
- candidate registry は worker branch に含めない。
- resume brief は `Pending hardening decisions: N` と registry path だけを carry-forward する。
- `safety_escalation` / `classification_needed` は必要最小 scope の `human_request_opened` へ送る。
- candidate full text を phase carry-forward に貼らず、path 参照にする。

### Non-goals

- candidate registry を local issue ledger の代替 source of truth にすること。
- human wait を常に epic-wide にすること。

### 想定 write scope

- `path:skills/issue-implementation-loop/references/runtime-state.md`
- `path:skills/issue-implementation-loop/references/human-wait.md`
- `path:skills/issue-implementation-loop/references/context-compaction.md`
- `path:skills/issue-implementation-loop/assets`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-review-governance-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- candidate registry schema / template を追加した場合は対象 validator または fixture test
- `rg -n "hardening-candidates|Pending hardening decisions|80 words|5 件" skills/issue-implementation-loop`
- `git diff --check`

## LRG-003: final delivery preflight に pending candidate check を追加する

### 目的

未判断の `hardening_candidate` や unresolved `safety_escalation` が残ったまま final PR delivery plan を通さない validation を追加する。

### Scope

- `skills/issue-implementation-loop/references/remote-delivery.md`
- `skills/issue-implementation-loop/scripts/validate_delivery_plan.py`
- delivery validation tests
- 必要なら delivery plan template

### Acceptance Criteria

- final PR delivery plan validation は candidate registry を確認する。
- `pending_decision` または unresolved `safety_escalation` があれば final PR delivery plan は fail する。
- `deferred_follow_up`、`declined`、`risk_accepted` は delivery を許可するが、completion report の residual risk に残す。
- `approved_for_current_pr` は対応する `implementation_issue` が `PR_READY` / integrated / review approved でなければ delivery を許可しない。
- `local_only` completion report でも未判断 candidate があれば `pending_hardening_candidates` として報告する。
- final PR merge、ready-for-review、force push、deploy、credential、permission、billing、production、destructive action の別承認境界は弱めない。

### Non-goals

- final PR ready-for-review 化や merge の自動化。
- local `PR_READY` だけで epic-base integration 済みと推定すること。

### 想定 write scope

- `path:skills/issue-implementation-loop/references/remote-delivery.md`
- `path:skills/issue-implementation-loop/scripts`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-review-governance-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `python3 skills/issue-implementation-loop/scripts/validate_delivery_plan.py <execution-envelope.json> <runtime-state.json> <delivery-plan.json> --json` の新規 fixture tests
- `rg -n "pending_decision|safety_escalation|hardening-candidates|final PR" skills/issue-implementation-loop`
- `git diff --check`

## LRG-004: execution handoff / envelope policy を同期する

### 目的

`grill-to-pr-loop` から `issue-implementation-loop` への handoff に review governance policy を含め、execution packet / envelope / worker packet の責務境界を揃える。

### Scope

- `skills/grill-to-pr-loop/references/execution-handoff.md`
- `skills/issue-implementation-loop/references/execution-envelope.md`
- `skills/issue-implementation-loop/assets/templates/execution-envelope.json`
- `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json`
- envelope / handoff tests

### Acceptance Criteria

- execution handoff が review governance policy を伝える。
- `review_policy.hardening_candidates` 相当を Execution Envelope に持たせるか、reference-only policy とするかが実装で一貫している。
- envelope に持たせる場合、schema / template / validator / tests が一致する。
- reference-only にする場合、`context-contract.toml` の read-set と reference ownership が明確で、packet に full policy text を貼らない。
- worker packet に session-level candidate decision state を混ぜない。
- planning/grill session が issue work を直接実装しない境界は維持される。

### Non-goals

- coordinator direct implementation の許可。
- execution envelope を人間判断 queue の source of truth にすること。

### 想定 write scope

- `path:skills/grill-to-pr-loop/references/execution-handoff.md`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/references/execution-envelope.md`
- `path:skills/issue-implementation-loop/assets`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-review-governance-issues.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- Execution Envelope validator / template fixture tests
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `git diff --check`

## LRG-005: regression tests と wiki discoverability を更新する

### 目的

Review governance の regression coverage、context budget evidence、wiki discoverability、final ledger synchronization を仕上げる。

### Scope

- `skills/grill-to-pr-loop/tests`
- `skills/issue-implementation-loop/tests`
- `scripts/` tests if needed
- `knowledge/wiki/syntheses/loop-review-governance-issues.md`
- `knowledge/index.md`
- `knowledge/log.md`
- 必要なら input packet / Execution Envelope / handoff brief

### Acceptance Criteria

- `intent_gap` と `hardening_candidate` を混同しない regression がある。
- `hardening_candidate` が auto-fix されず final PR 前 decision queue に送られる regression がある。
- 未判断 candidate がある final PR delivery plan が fail する regression がある。
- `superpowers:requesting-code-review` 第一候補と fallback boundary の contract が test または docs regression で固定されている。
- `validate_skill_context.py --all` が通る。
- `report_skill_context.py --all --json` が warnings なし、または warning の理由と follow-up が ledger に記録される。
- `knowledge/index.md` から spec / issue ledger / execution artifacts を発見できる。
- `knowledge/log.md` に Issue Gate / Execution Plan Gate / implementation evidence が同期される。

### 実装証跡

- 実行状態: 検証済み。
- Branch: `codex/loop-review-governance/LRG-005-regression-discoverability`
- Base: `b7a5b989bb856ec0703f490361f7d9898ac521f4`
- 回帰テスト範囲: `scripts/test_loop_review_governance_ledger.py`
- LRG-005 branch は epic base から開始しているため、LRG-001 から LRG-004 の未統合 code は merge / cherry-pick していない。
- Executable behavior regression for final delivery pending-candidate rejection は LRG-003 approved range で実装済み。LRG-005 ではその証跡と decision gate を docs regression として discoverable に固定する。
- `report_skill_context.py --all --json` は top-level `warnings: []`。`workflow_complexity.warnings` は advisory-only のため hard validator として扱わない。
- 未判断 hardening candidate は実装しない。final PR delivery 前に人間判断へ送る。

### Acceptance Evidence

- [x] `intent_gap` と `hardening_candidate` を混同しない regression がある。
- [x] `hardening_candidate` が auto-fix されず final PR 前 decision queue に送られる regression がある。
- [x] 未判断 candidate がある final PR delivery plan が fail する regression がある。
- [x] `superpowers:requesting-code-review` 第一候補と fallback boundary の contract が test または docs regression で固定されている。
- [x] `validate_skill_context.py --all` が通る。
- [x] `report_skill_context.py --all --json` は top-level warnings なし。
- [x] `knowledge/index.md` から spec / issue ledger / execution artifacts を発見できる。
- [x] `knowledge/log.md` に Issue Gate / Execution Plan Gate / implementation evidence が同期される。

### Non-goals

- GitHub issue mirror、push、PR 作成、ready-for-review、merge。
- context complexity advisory を hard validator にすること。

### 想定 write scope

- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`
- `path:scripts`
- `path:knowledge/wiki/syntheses/loop-review-governance-issues.md`
- `path:knowledge/wiki/syntheses/loop-review-governance-input-packet.json`
- `path:knowledge/wiki/syntheses/loop-review-governance-execution-envelope.json`
- `path:knowledge/wiki/syntheses/loop-review-governance-handoff-brief.md`
- `path:knowledge/index.md`
- `path:knowledge/log.md`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts`
- `rg -n "loop-review-governance|hardening_candidate|pending_decision|requesting-code-review" skills scripts knowledge/wiki/syntheses`
- `git diff --check`

## 実装証跡サマリ

- LRG-001: `b7a5b989bb856ec0703f490361f7d9898ac521f4..461cea6cb48b4a44b40148e2523a5cd17a386f86`、review cycle 2 approved、PR_READY。
- LRG-002: `461cea6cb48b4a44b40148e2523a5cd17a386f86..1ee5eb11b6fa23a1e33f82649ec38438dd5b6404`、review cycle 1 approved、PR_READY。
- LRG-003: `1ee5eb11b6fa23a1e33f82649ec38438dd5b6404..2a02704943d6d9dc86a130074cafa85c80c06a1f`、review cycle 2 approved、PR_READY。
- LRG-004: `461cea6cb48b4a44b40148e2523a5cd17a386f86..3a85970d9829526bd34e7747f862f2a6d6b27ce7`、review cycle 2 approved、PR_READY。
- LRG-005: `b7a5b989bb856ec0703f490361f7d9898ac521f4..HEAD`、regression discoverability / wiki synchronization branch。
- Runtime state: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/runtime-state.json`
- Candidate registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`
- Remote policy: `local_only`。GitHub issue mirror、push、PR 作成、ready-for-review、merge、force push、production / credential / permission / billing / destructive action は未実行。

## Pending Hardening Decisions

| Candidate ID | Source issue | Decision | Recommended decision | 実装判断 |
| --- | --- | --- | --- | --- |
| HC-LRG-002-001 | LRG-002 | `pending_decision` | `deferred_follow_up` | 未判断 hardening candidate は実装しない |
| HC-LRG-003-001 | LRG-003 | `pending_decision` | `deferred_follow_up` | 未判断 hardening candidate は実装しない |
| HC-LRG-003-002 | LRG-003 | `pending_decision` | `deferred_follow_up` | 未判断 hardening candidate は実装しない |
| HC-LRG-004-001 | LRG-004 | `pending_decision` | `deferred_follow_up` | 未判断 hardening candidate は実装しない |

未判断 candidate が残る間、final PR delivery plan は人間 decision gate 前に進めない。LRG-005 は candidate decision を実装せず、decision queue の discoverability と regression evidence を同期する。

## 関連ページ

- [Loop Review Governance Spec](loop-review-governance-spec.md)
- [Loop Review Governance Input Packet](loop-review-governance-input-packet.json)
- [Loop Review Governance Execution Envelope](loop-review-governance-execution-envelope.json)
- [Loop Review Governance Handoff Brief](loop-review-governance-handoff-brief.md)
- [Grill To PR Loop Issue Implementation Review Gate Plan](grill-to-pr-loop-issue-implementation-review-gate-plan.md)
