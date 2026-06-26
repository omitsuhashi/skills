# Skill Repository Optimization V4 Issues

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。2026-06-26 のユーザー追補として、実装開始前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを skill 契約へ追加する scope を SRO4-003 に反映済み。実装は `issue-implementation-loop prepare` 以降で進める。GitHub issue mirror、push、PR 作成、merge は未実行。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill-repository-optimization-v4 | SRO4-001 | 粒度 policy・baseline・V4 spec を正本化する | 承認済み | 実行可能 | なし | SRO4-002, SRO4-004 | 未作成 | 未実施 | 未作成 |
| skill-repository-optimization-v4 | SRO4-002 | Context Contract V2 と共通 validator を導入する | 承認済み | ブロック中 | SRO4-001 | SRO4-003 | 未作成 | 未実施 | 未作成 |
| skill-repository-optimization-v4 | SRO4-003 | loop skill routing を single-source 化する | 承認済み | ブロック中 | SRO4-002 | SRO4-005 | 未作成 | 未実施 | 未作成 |
| skill-repository-optimization-v4 | SRO4-004 | Worker Packet V2 と Resume Brief V2 を導入する | 承認済み | ブロック中 | SRO4-001 | SRO4-005 | 未作成 | 未実施 | 未作成 |
| skill-repository-optimization-v4 | SRO4-005 | `llm-wiki` contract と CI を追加する | 承認済み | ブロック中 | SRO4-003, SRO4-004 | SRO4-006 | 未作成 | 未実施 | 未作成 |
| skill-repository-optimization-v4 | SRO4-006 | 統合検証・移行 shim・wiki ledger を仕上げる | 承認済み | ブロック中 | SRO4-005 | なし | 未作成 | 未実施 | 未作成 |

## ブロッカーグラフ

- SRO4-001: 実行可能; ブロック元 なし; ブロック先 SRO4-002, SRO4-004
- SRO4-002: ブロック中; ブロック元 SRO4-001; ブロック先 SRO4-003
- SRO4-003: ブロック中; ブロック元 SRO4-002; ブロック先 SRO4-005
- SRO4-004: ブロック中; ブロック元 SRO4-001; ブロック先 SRO4-005
- SRO4-005: ブロック中; ブロック元 SRO4-003, SRO4-004; ブロック先 SRO4-006
- SRO4-006: ブロック中; ブロック元 SRO4-005; ブロック先 なし

## SRO4-001

### Epic ID

`skill-repository-optimization-v4`

### タイトル

粒度 policy・baseline・V4 spec を正本化する

### 作るもの

user-facing loop skill を 2 つに固定する family policy と V4 planning artifact を repo-local 正本にする。現状 context metrics の baseline を保存し、後続 issue が context regression を比較できるようにする。

### 受け入れ条件

- [ ] `skill-architecture.toml` が repository-change-loop family、user-facing skill 2 件、forbidden standalone skill 名を持つ。
- [ ] `skill-architecture.toml` の forbidden list は validator code へ重複ハードコードされない。
- [ ] current checkout の operation context metrics が baseline JSON として保存される。
- [ ] `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` とこの ledger が `knowledge/index.md` から発見できる。
- [ ] `knowledge/log.md` に ingest / planning artifact 追加が記録される。
- [ ] 新しい user-facing skill は追加されない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: SRO4-002, SRO4-004

### 想定 write scope

- `path:skill-architecture.toml`
- `path:knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md`
- `path:knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md`
- `path:knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json`
- `path:knowledge/index.md`
- `path:knowledge/log.md`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- source: [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- skill-creator 制約: 新しい standalone skill は trigger /成果物 / state 独立性が揃う場合だけ作る。今回は追加しない。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `rg -n "Skill Repository Optimization V4|skill-repository-optimization-v4" knowledge/index.md knowledge/log.md knowledge/wiki/syntheses`
- `git diff --check`

## SRO4-002

### Epic ID

`skill-repository-optimization-v4`

### タイトル

Context Contract V2 と共通 validator を導入する

### 作るもの

loop skill 固有の word count validator を、複数 skill に使える context contract library と validator CLI に発展させる。schema version 1 の互換を維持しつつ、schema version 2 で文字数、非空白文字数、推定 token、headroom を検証する。

### 受け入れ条件

- [ ] `scripts/skill_context/contract.py` が schema version 1 / 2 を読める。
- [ ] `scripts/skill_context/metrics.py` が `character_count`、`non_whitespace_character_count`、`estimated_token_count`、`file_count`、`headroom_percent` を返す。
- [ ] estimated token は外部 dependency なしで CJK / ascii / other chars を保守的に見積もる。
- [ ] `scripts/validate_skill_context.py --all` が missing reference、duplicate reference、reference depth、file count、char budget、estimated token budget、headroom を検出する。
- [ ] `scripts/inspect_skill_context.py` と `scripts/report_skill_context.py` が JSON output を持つ。
- [ ] `scripts/validate_loop_skill_context.py` と `scripts/inspect_loop_skill_context.py` は compatibility wrapper として既存 CLI を維持する。
- [ ] tests は v1 compatibility、v2 budget、Japanese context estimation、failure cases をカバーする。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: SRO4-001
- ブロック先: SRO4-003

### 想定 write scope

- `path:scripts/skill_context`
- `path:scripts/validate_skill_context.py`
- `path:scripts/inspect_skill_context.py`
- `path:scripts/report_skill_context.py`
- `path:scripts/validate_loop_skill_context.py`
- `path:scripts/inspect_loop_skill_context.py`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- 既存: `scripts/validate_loop_skill_context.py`, `scripts/inspect_loop_skill_context.py`
- 既存 contracts: `skills/grill-to-pr-loop/context-contract.toml`, `skills/issue-implementation-loop/context-contract.toml`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`

## SRO4-003

### Epic ID

`skill-repository-optimization-v4`

### タイトル

loop skill routing を single-source 化する

### 作るもの

`context-contract.toml` を loop skill read-set の唯一の正本にし、`SKILL.md` と `workflow-contract.md` から operation-specific reference map を消す。`waiting_human` 専用の `execute.wait` operation を追加し、human wait 中の不要 context load を減らす。さらに、implementation handoff 前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを必須手順として skill contract に加える。

### 受け入れ条件

- [ ] `skills/grill-to-pr-loop/context-contract.toml` が schema version 2 になる。
- [ ] `skills/issue-implementation-loop/context-contract.toml` が schema version 2 になる。
- [ ] `grill-to-pr-loop` の base read-set から `references/workflow-contract.md` が外れる。
- [ ] `workflow-contract.md` は deprecated shim として残るが、default read-set には含まれない。
- [ ] `SKILL.md` は operation-specific reference filename を列挙しない。
- [ ] `issue-implementation-loop/context-contract.toml` に `execute.wait` が追加される。
- [ ] `select_operation.py` は `waiting_human` を `execute.wait` に routing する。
- [ ] `execute.dispatch` から `human-wait.md` が外れ、`execute.wait` が `human-wait.md` と `runtime-state.md` だけを読む。
- [ ] `grill-to-pr-loop/SKILL.md` が、approved execution handoff 前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを行うよう指示している。
- [ ] `grill-to-pr-loop/references/execution-handoff.md` が、implementation を肥大化した planning context から直接始めず、normalized packet と圧縮済み handoff brief から始める契約を説明している。
- [ ] tests は implementation handoff 前の context 圧縮 / fresh coordinator requirement が skill contract から消えないことを検証する。
- [ ] global lifecycle、approval、remote boundary、stop condition は `core.md` から発見できる。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: SRO4-002
- ブロック先: SRO4-005

### 想定 write scope

- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/context-contract.toml`
- `path:skills/grill-to-pr-loop/references`
- `path:skills/issue-implementation-loop/SKILL.md`
- `path:skills/issue-implementation-loop/context-contract.toml`
- `path:skills/issue-implementation-loop/references`
- `path:skills/issue-implementation-loop/scripts/select_operation.py`
- `path:skills/issue-implementation-loop/scripts/lib/issue_implementation_loop`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- 既存: `skills/grill-to-pr-loop/SKILL.md`, `skills/grill-to-pr-loop/references/core.md`, `skills/grill-to-pr-loop/references/workflow-contract.md`
- 既存: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/operation_selection.py`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/inspect_skill_context.py --skill skills/issue-implementation-loop --operation execute.wait --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/select_operation.py --envelope <execution-envelope.json> --runtime <runtime-state.json> --requested-mode execute --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `rg -n "context.*圧縮|fresh execution coordinator|handoff brief" skills/grill-to-pr-loop/SKILL.md skills/grill-to-pr-loop/references/execution-handoff.md`
- `git diff --check`

## SRO4-004

### Epic ID

`skill-repository-optimization-v4`

### タイトル

Worker Packet V2 と Resume Brief V2 を導入する

### 作るもの

worker / reviewer / resume の context artifact を revision 付きで管理する。Worker Packet V2 は task kind と access mode を明示し、Resume Brief V2 は metadata により stale reuse を拒否できるようにする。

### 受け入れ条件

- [ ] `skills/issue-implementation-loop/assets/schemas/worker-packet-v1.schema.json` が既存 schema の互換参照として残る。
- [ ] `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json` が schema version 2 default になる。
- [ ] Worker Packet V2 は `task_kind`、`access_mode`、`source_revision`、`read_paths[].purpose` を必須にする。
- [ ] `implement` / `fix` は `access_mode=read_write` かつ non-empty `write_scope` を要求する。
- [ ] `review` / `inspect` は `access_mode=read_only` かつ `write_scope=[]` を要求する。
- [ ] packet validator は path traversal と worktree 外 path を拒否する。
- [ ] packet validator は stale envelope / runtime / issue revision を拒否する。
- [ ] `build_resume_brief.py` は `resume-brief.md` と `resume-brief.meta.json` を生成する。
- [ ] `validate_resume_brief.py` は meta と current runtime / envelope / events を比較し、不一致時に stale と判定する。
- [ ] V1 packet と旧 brief は既存 run の resume 用に読める。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: SRO4-001
- ブロック先: SRO4-005

### 想定 write scope

- `path:skills/issue-implementation-loop/assets/schemas`
- `path:skills/issue-implementation-loop/assets/templates`
- `path:skills/issue-implementation-loop/scripts/build_worker_packet.py`
- `path:skills/issue-implementation-loop/scripts/validate_worker_packet.py`
- `path:skills/issue-implementation-loop/scripts/build_resume_brief.py`
- `path:skills/issue-implementation-loop/scripts/validate_resume_brief.py`
- `path:skills/issue-implementation-loop/scripts/lib/issue_implementation_loop`
- `path:skills/issue-implementation-loop/references/worker-contract.md`
- `path:skills/issue-implementation-loop/references/runtime-state.md`
- `path:skills/issue-implementation-loop/references/recovery.md`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- 既存: `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json`
- 既存: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/worker_packet.py`
- 既存: `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/resume_brief.py`

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_worker_packet.py <args>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py <worker-packet-v2.json> --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_resume_brief.py <runtime-root> --envelope <execution-envelope.json>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_resume_brief.py <runtime-root>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `git diff --check`

## SRO4-005

### Epic ID

`skill-repository-optimization-v4`

### タイトル

`llm-wiki` contract と CI を追加する

### 作るもの

loop skill だけでなく、複数 mode と topology reference を持つ `llm-wiki` も context contract の検証対象に入れる。CI で architecture policy、context regression、tests を固定する。

### 受け入れ条件

- [ ] `skills/llm-wiki/context-contract.toml` が topology × mode read-set を表現する。
- [ ] `llm-wiki` contract は single-root / multi-root と各 mode の read-set を機械検証できる。
- [ ] `skills/llm-wiki/SKILL.md` は contract と矛盾する manual read-set を持たない。
- [ ] `.github/workflows/skill-architecture.yml` が Python 3.9 / 3.12 matrix で実行される。
- [ ] CI は `validate_skill_architecture.py --all`、`validate_skill_context.py --all`、`report_skill_context.py --all --json`、loop skill tests、`git diff --check` を実行する。
- [ ] budget 超過、context増加率 10% 超、file count 超過、forbidden standalone skill 追加は CI で失敗または明示 warning になる。
- [ ] context report artifact は PR review で読める JSON として出力される。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: SRO4-003, SRO4-004
- ブロック先: SRO4-006

### 想定 write scope

- `path:skills/llm-wiki/context-contract.toml`
- `path:skills/llm-wiki/SKILL.md`
- `path:skills/llm-wiki/tests`
- `path:.github/workflows/skill-architecture.yml`
- `path:scripts/validate_skill_architecture.py`
- `path:scripts/validate_skill_context.py`
- `path:scripts/report_skill_context.py`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- 既存: `skills/llm-wiki/SKILL.md`
- knowledge root contract: [knowledge/AGENTS.md](../../AGENTS.md)

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests`
- `git diff --check`

## SRO4-006

### Epic ID

`skill-repository-optimization-v4`

### タイトル

統合検証・移行 shim・wiki ledger を仕上げる

### 作るもの

V4 の全変更を統合し、V1 compatibility、V2 default、deprecated shim、CI、wiki ledger を一貫させる。Execution Plan Gate 後に実装された場合、この issue が completion evidence を local ledger に集約する。

### 受け入れ条件

- [ ] `validate_skill_architecture.py --all` が通る。
- [ ] `validate_skill_context.py --all` が通る。
- [ ] `report_skill_context.py --all --json` が baseline 比較を返す。
- [ ] loop skill tests、`llm-wiki` tests、代表 packet / resume CLI が通る。
- [ ] deprecated shim と compatibility wrapper の残置理由と削除条件が references または ledger に記録される。
- [ ] `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` に各 issue の実装状態、verification、implementation review result が反映される。
- [ ] `knowledge/index.md` と `knowledge/log.md` が V4 の実装状態と residual risks を発見できる。
- [ ] remote write を実行しない場合、その理由が ledger に残る。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: SRO4-005
- ブロック先: なし

### 想定 write scope

- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`
- `path:skills/llm-wiki/tests`
- `path:knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md`
- `path:knowledge/index.md`
- `path:knowledge/log.md`

### 必要な文脈

- 仕様: [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- Packet: [skill-repository-optimization-v4-input-packet.json](skill-repository-optimization-v4-input-packet.json)

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests`
- `git diff --check`

## Execution Plan Gate 概要

- Packet: [skill-repository-optimization-v4-input-packet.json](skill-repository-optimization-v4-input-packet.json)
- delivery intent: `local_only`
- remote write: 未承認
- fallback: parallel execution は SRO4-002 と SRO4-004 以降の write scope overlap を避ける必要がある。最初は SRO4-001 の完了後、SRO4-002 と SRO4-004 を並列候補にできる。
- final PR merge: human-only

## Execution Plan Gate 承認

- 承認日時: 2026-06-26
- 承認済み packet: [skill-repository-optimization-v4-input-packet.json](skill-repository-optimization-v4-input-packet.json)
- capability preflight: `check_prereqs.py --phase execution --json` は `ok: true`; `check_capabilities.py --input ... --json` は `ok: true`
- worker context policy: `worker_context_required=true`, `coordinator_may_implement=false`, serial fallback は `worker_context_only`
- remote policy: `local_only`; GitHub issue mirror、push、PR 作成、merge は未承認
- 次の手順: approval record を commit した後、`issue-implementation-loop prepare` として Execution Envelope / branch / worktree reservation を作成する

## Prepare 結果

- Envelope: [skill-repository-optimization-v4-execution-envelope.json](skill-repository-optimization-v4-execution-envelope.json)
- Envelope revision: 1
- `epic_base.ref`: `codex/skill-repository-optimization-v4/epic-base`
- `epic_base.sha`: `a073a10d38744771c2ed10fe8d9d351e5bf0e588`
- physical branch / worktree creation: 未実行
- runnable on prepare: SRO4-001 のみ `create_on_run`
- blocked reservations: SRO4-002, SRO4-003, SRO4-004, SRO4-005, SRO4-006 は `reserved`
- SRO4-005 は SRO4-003 / SRO4-004 の hard dependency を維持するが、複数 blocker head の ad hoc merge を避けるため dependency `base_effect` は `none` とする。実装中に両 head の code merge が必要になった場合は stop condition とし、approved integration work item または envelope revision を要求する。
- `validate_execution_envelope.py`: `EXECUTION ENVELOPE OK`
- `reconcile_git_state.py --json`: `ok: true`, collisions 0

## 関連ページ

- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [Loop Skill Architecture V3 Issues](loop-skill-architecture-v3-issues.md)

## 出典

- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [raw/sources/2026-06-26-skill-repository-optimization-v4-design.md](../../raw/sources/2026-06-26-skill-repository-optimization-v4-design.md)
