# Planning Worktree Gate Issue 台帳

## Epic

- `Epic ID`: `planning-worktree-gate`
- `仕様`: [Planning Worktree Gate 仕様](spec.md)
- `リモート方針`: `local_only`
- `planning branch`: `codex/planning-worktree-gate/planning`
- `planning base SHA`: `b3b869b60dfb785b325f754292dccf675e47313b`

## 台帳

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| planning-worktree-gate | PWTG-001 | Planning Worktree Gate CLI と skill contract を追加する | 承認済み | 完了 | なし | PWTG-002, PWTG-004 | 未作成 | Critical 0 / Important 0 | 未作成 |
| planning-worktree-gate | PWTG-002 | packet / runtime repository guard を追加する | 承認済み | 完了 | PWTG-001 | PWTG-003, PWTG-004 | 未作成 | Critical 0 / Important 0 | 未作成 |
| planning-worktree-gate | PWTG-003 | PR_READY / delivery integrity guard を追加する | 承認済み | 完了 | PWTG-002 | PWTG-004 | 未作成 | Critical 0 / Important 0 | 未作成 |
| planning-worktree-gate | PWTG-004 | wiki 同期と全体 verification / review を完了する | 承認済み | 完了 | PWTG-001, PWTG-002, PWTG-003 | なし | 未作成 | production Critical 0 / Important 0 | 未作成 |

## Blocker graph

```text
PWTG-001 -> PWTG-002 -> PWTG-003 -> PWTG-004
PWTG-001 ---------------------------> PWTG-004
PWTG-002 ---------------------------> PWTG-004
```

cycle はない。`PWTG-004` は統合 validation / review issue であり、複数 blocker head を worker が任意 merge する実装 issue ではない。

## PWTG-001 Planning Worktree Gate CLI と skill contract を追加する

- `実行状態`: `完了`
- `実装 commit`: `5770a69cae1d5cd6d43b42cfc0016eac5b89666a`, `89cb0e38ece73c852855888dfb455f1a44ba4627`, `0b5fe8cd6adb1fd3d67e8e386634dc26d8641f4a`, `94eaf0fef6385ab690067d7fc2287904afec6192`, `dfc04b5f28cd67077d394edef91286d13ffeca84`, `971b178c50e2dc856e41584854e3c51f532958cd`, `22ebb42d13e44019ac198582be9fc7326ea792a7`
- `review`: adoption、runtime reuse、default snapshot/index、post-add race、hostile Git environment、physical ancestry の修正後に Critical 0 / Important 0。
- `write scope`:
  - `skills/grill-to-pr-loop/SKILL.md`
  - `skills/grill-to-pr-loop/references/`
  - `skills/grill-to-pr-loop/scripts/`
  - `skills/grill-to-pr-loop/tests/`
- `受け入れ条件`:
  - clean `main` で `prepare` が `codex/<epic-id>/planning` と Epic-scoped worktree を作る。
  - 同じ branch の registered worktree があれば path を変えずに再利用する。
  - repeated Gate entry が同じ planning worktree identity を返す。
  - `git worktree add` failure 時に default checkout の tracked/untracked content、index、HEAD を変更しない。
  - pre-existing dirt の bytes と porcelain status を変更しない。
  - skill contract が default checkout write/stage/commit禁止、作成失敗時停止、worktree preference再確認不要、Gate間再利用を明記する。
- `非目標`:
  - generic worktree manager。
  - Gate ごとの worktree。
  - `.gitignore` の自動編集。
- `検証`:
  - `python3 -m unittest skills.grill-to-pr-loop.tests.test_planning_worktree_gate`
  - `python3 -m unittest discover -s skills/grill-to-pr-loop/tests`

## PWTG-002 packet / runtime repository guard を追加する

- `実行状態`: `完了`
- `ブロック元`: `PWTG-001`
- `実装 commit`: `59c6a3151728abfedf493cd94f8f6ecd16cc1c22`, `747227b97a116e3e54304db11cb141fd0e18d5ae`, `9253c6b877e392203781986b78444986140c1c0c`, `724bc31473a99bc686c2fec7baaf2322853d6bf2`, `a2dcd18df54efc1f5877b23a7f84b97ee9aeebf5`, `9f8eca6f8cb9fe38263dfe0f8c9b63c2edcc8ed3`, `bc557bef95cabea39a2ac5220ce4ec09d59f980e`
- `review`: new seal / legacy compatibility、runtime binding、hostile Git environment、physical Gate ancestry、default-checkout identity の修正後に Critical 0 / Important 0。
- `write scope`:
  - `skills/issue-implementation-loop/assets/`
  - `skills/issue-implementation-loop/references/`
  - `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/`
  - `skills/issue-implementation-loop/tests/`
- `受け入れ条件`:
  - new Input Packet v2 が `planning_branch` / `planning_base_sha` を表現し、pair 欠落、非canonical branch、短縮 SHA を拒否する。
  - existing sealed v2 packet bytes を変更せず読み取り互換を保つ。
  - Execution Envelope v4 の untracked `repository_guard` が planning worktree path と default checkout開始snapshotを保持する。
  - packet fields と runtime guard の branch/base mismatch を prepare が拒否する。
  - registered planning worktree / default checkout snapshot mismatch を prepare が拒否する。
  - Gate commit が `epic_base.sha` から到達不能なら `GATE_COMMIT_NOT_ANCESTOR` を返す。
- `非目標`:
  - host path の tracked packet 保存。
  - existing sealed packet の migration / reseal。
- `検証`:
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_validation`
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_approved_spec_binding`

## PWTG-003 PR_READY / delivery integrity guard を追加する

- `実行状態`: `完了`
- `ブロック元`: `PWTG-002`
- `実装 commit`: `c355b088a9f12954f502406b9f192559f8c9ea23`
- `review`: PR_READY / completion / delivery の physical planning base・Gate・全candidate到達性を含む累積 review で Critical 0 / Important 0。
- `write scope`:
  - `skills/issue-implementation-loop/references/`
  - `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/`
  - `skills/issue-implementation-loop/tests/`
- `受け入れ条件`:
  - success status / completion validation が default checkout HEAD/status drift を拒否する。
  - pre-existing dirt が開始時 snapshot と同一なら許可する。
  - final PR head が approved Gate commit、`planning_base_sha`、全 delivery candidate `head_sha` を含まなければ delivery validation が失敗する。
  - `pr_merged: true` だけでは integration proof としない。
  - guard は default checkout の reset、clean、stash、file move、delete を行わない。
- `非目標`:
  - remote ref の mutation。
  - default checkout の自動復元。
- `検証`:
  - `python3 -m unittest skills.issue-implementation-loop.tests.test_delivery`
  - `python3 -m unittest discover -s skills/issue-implementation-loop/tests`

## PWTG-004 wiki 同期と全体 verification / review を完了する

- `実行状態`: `完了`
- `ブロック元`: `PWTG-001`, `PWTG-002`, `PWTG-003`
- `実装結果`: 本台帳、Implementation Plan、`knowledge/index.md`、`knowledge/log.md` を同じ planning branch で同期し、fresh verification と production clearance を完了した。
- `write scope`:
  - `knowledge/wiki/syntheses/planning-worktree-gate/`
  - `knowledge/index.md`
  - `knowledge/log.md`
- `受け入れ条件`:
  - spec、Issue台帳、実装計画、実装結果の status / evidence が一致する。
  - changed-skill scoped dual-host / skill architecture / context validators、skill-creator quick validator、両 skill full suite が通る。
  - final PR candidate branch が全 planning / implementation commit を含む。
  - default checkout の HEAD/status が runtime start snapshot と一致する。
- `非目標`:
  - push、PR作成、merge。
- `検証`:
  - `python3 scripts/validate_skill_architecture.py --all`
  - `python3 scripts/validate_skill_context.py --all`
  - `python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop`
  - `python3 scripts/validate_dual_host_compatibility.py --skill skills/issue-implementation-loop`
  - `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop`
  - `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop`
  - `python3 -m unittest discover -s scripts`
  - `git diff --check`

## 実装 closeout evidence

### Commit chain

pre-closeout の ancestry chain は planning base を含む次の 19 commits で、すべて本 planning branch HEAD の ancestor である。

```text
b3b869b60dfb785b325f754292dccf675e47313b  planning base / Task Worktree Policy
651189999590c9a04fefe9a1d6239a47d7f113bb  Written Spec
e87a7e3a9cca37af9ae6677e1f9c46df78fbe96a  Issue Gate
863711a95817f66520246ce978d20923009e10f8  Execution Plan Gate
5770a69cae1d5cd6d43b42cfc0016eac5b89666a  PWTG-001
89cb0e38ece73c852855888dfb455f1a44ba4627  PWTG-001 review fix
59c6a3151728abfedf493cd94f8f6ecd16cc1c22  PWTG-002
747227b97a116e3e54304db11cb141fd0e18d5ae  PWTG-002 review fix
c355b088a9f12954f502406b9f192559f8c9ea23  PWTG-003
0b5fe8cd6adb1fd3d67e8e386634dc26d8641f4a  PWTG-001 adoption / index fix
94eaf0fef6385ab690067d7fc2287904afec6192  PWTG-001 race fix
dfc04b5f28cd67077d394edef91286d13ffeca84  PWTG-001 Git environment fix
9253c6b877e392203781986b78444986140c1c0c  PWTG-002 new-seal fix
971b178c50e2dc856e41584854e3c51f532958cd  PWTG-001 runtime-reuse fix
724bc31473a99bc686c2fec7baaf2322853d6bf2  PWTG-002 guard environment fix
22ebb42d13e44019ac198582be9fc7326ea792a7  PWTG-001 post-add / physical ancestry fix
a2dcd18df54efc1f5877b23a7f84b97ee9aeebf5  PWTG-002 physical ancestry fix
9f8eca6f8cb9fe38263dfe0f8c9b63c2edcc8ed3  PWTG-002 legacy prepare physical ancestry fix
bc557bef95cabea39a2ac5220ce4ec09d59f980e  PWTG-002 runtime identity binding fix
```

PWTG-004 の scoped closeout documentation commit は `4d96bfd71b63c86727ad36b2d3d8fd0beb710a78` であり、本 review-fix で post-commit 独立 review の stale status finding を訂正する。

### Fresh verification

- `skills/grill-to-pr-loop/tests`: `58/58` pass。
- `skills/issue-implementation-loop/tests`: `284/284` pass。
- `scripts`: `58/58` pass。
- `skills/llm-wiki/tests`: `6/6` pass。
- Acceptance 1〜8 focused regressions: `18/18` pass。
- skill architecture validator: pass。
- skill context validator: 3 contracts pass。
- changed-skill scoped dual-host compatibility: 2 skills とも pass。
- skill-creator quick validator: 2 skills とも `Skill is valid!`。
- `git diff --check`: pass。

approved spec に記録された `validate_dual_host_authoring.py` は historical plan defect であり、sealed spec と Input Packet の bytes は変更していない。実在する repository validator は `validate_dual_host_compatibility.py` である。変更対象2 skillの scoped validationは passし、repository-wide `--all` は未変更の `llm-wiki` DESCRIPTION discovery finding だけを返したため、repository-wide passとは記録しない。

### Acceptance 1〜8

1. clean default branchからfirst write前に planning worktreeを作成する実repo testがpass。
2. CLI実行前から存在するexact registered worktreeの安全なadoptionと、同一Epicのreuse testがpass。
3. Spec Gate、Issue Gate、Execution Plan Gate、index/log同期は同じplanning branch chainにある。
4. create/add failureとpost-checkout driftでdefault checkoutへwrite/stage/commitせずfail closedにするtestがpass。
5. pre-existing dirtとdefault index bytesを変更・移動・削除しないtestがpass。
6. new guard付きpacketとlegacy guardless packetの両方でphysical Gate ancestryを要求するtestがpass。
7. final headがphysical planning base、Gate、全candidate commitを含まない場合に拒否するtestがpass。
8. runtime identityへbindingしたactual default checkoutのHEAD/status driftとclean substitute worktreeを拒否し、同一pre-existing dirtだけを許可するtestがpass。

### Repository / review / delivery

- default checkoutのHEADとexact porcelain statusはruntime start snapshotと一致した。
- approved spec SHA-256 `f4b8cebd19a832963aa5e4d022759b21ef73dc417ff6d2f1555b87419b578ec3`、sealed Input Packet SHA-256 `7b7ecc562d1ff2aa2066438099741dad9e70ccb889c9dada4620eebb2224e219`は不変である。
- prior production Important findingsはすべて修正され、最終fix reviewはCritical 0 / Important 0である。
- non-blocking MinorはGit environment policyのskill間重複、runtime load/validate stabilization sequenceの反復、planning/default identity parameter data clumpである。
- remote policyは`local_only`。push、PR、merge、GitHub mutation、destructive recoveryは実行していない。

## Issue Gate 判断

- `decision`: `approved`
- `actor`: `session-user`
- `scope`: user提示の方針、Acceptance Tests 1〜8、Non-goals を上記4 issueへ分解した dependency / write scope / criteria。
- `remote action`: なし。

## 関連ページ

- [Planning Worktree Gate 仕様](spec.md) は本台帳の scope と停止条件を定義する。
- [Grill To PR Loop Branch Policy Spec](../grill-to-pr-loop-branch-policy-spec.md) は execution issue branch / worktree ownership の既存契約である。

## 出典

- [Planning Worktree Gate 仕様](spec.md)
