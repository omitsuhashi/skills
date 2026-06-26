# Skill Repository Optimization V4 Issues

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。SRO4-001 から SRO4-005 は runtime-state 上で `COMPLETE`、implementation review はすべて `approved`。SRO4-006 は 2026-06-26 に SRO4-005 head `e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf` ベースへ、承認済み SRO4-004 head `e4f7551b49df4082d1266b04b32249a0770d7481` を競合なしで merge した。merge commit は `0435b90e5227cf84ef0f6e546463b6f8d3d545df`。remote policy は `local_only` のため、GitHub issue mirror、push、PR 作成、merge は実行していない。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| skill-repository-optimization-v4 | SRO4-001 | 粒度 policy・baseline・V4 spec を正本化する | 承認済み | COMPLETE | なし | SRO4-002, SRO4-004 | 未作成 | approved: `a073a10d38744771c2ed10fe8d9d351e5bf0e588..53fd68f64403505064373100d8ec35543be9c04d` | 未作成 |
| skill-repository-optimization-v4 | SRO4-002 | Context Contract V2 と共通 validator を導入する | 承認済み | COMPLETE | SRO4-001 | SRO4-003 | 未作成 | approved: `53fd68f64403505064373100d8ec35543be9c04d..be17b274c27745f64d0d629ea22d96edcd3fb0ac` | 未作成 |
| skill-repository-optimization-v4 | SRO4-003 | loop skill routing を single-source 化する | 承認済み | COMPLETE | SRO4-002 | SRO4-005 | 未作成 | approved: `be17b274c27745f64d0d629ea22d96edcd3fb0ac..839ce87713c4077cdfca650c8873cd947f67e813` | 未作成 |
| skill-repository-optimization-v4 | SRO4-004 | Worker Packet V2 と Resume Brief V2 を導入する | 承認済み | COMPLETE | SRO4-001 | SRO4-005 | 未作成 | approved: `53fd68f64403505064373100d8ec35543be9c04d..e4f7551b49df4082d1266b04b32249a0770d7481` | 未作成 |
| skill-repository-optimization-v4 | SRO4-005 | `llm-wiki` contract と CI を追加する | 承認済み | COMPLETE | SRO4-003, SRO4-004 | SRO4-006 | 未作成 | approved: `839ce87713c4077cdfca650c8873cd947f67e813..e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf` | 未作成 |
| skill-repository-optimization-v4 | SRO4-006 | 統合検証・移行 shim・wiki ledger を仕上げる | 承認済み | COMPLETE: final local ledger commit | SRO4-005 | なし | 未作成 | final worker self-check + full verification | 未作成 |

## ブロッカーグラフ

- SRO4-001: COMPLETE; ブロック元 なし; SRO4-002 と SRO4-004 を release 済み
- SRO4-002: COMPLETE; ブロック元 SRO4-001; SRO4-003 を release 済み
- SRO4-003: COMPLETE; ブロック元 SRO4-002; SRO4-005 を release 済み
- SRO4-004: COMPLETE; ブロック元 SRO4-001; SRO4-005 の gating dependency として approved head を SRO4-006 で統合済み
- SRO4-005: COMPLETE; ブロック元 SRO4-003, SRO4-004; SRO4-006 を release 済み
- SRO4-006: COMPLETE; ブロック元 SRO4-005; ブロック先 なし

## SRO4-001

### Epic ID

`skill-repository-optimization-v4`

### タイトル

粒度 policy・baseline・V4 spec を正本化する

### 作るもの

user-facing loop skill を 2 つに固定する family policy と V4 planning artifact を repo-local 正本にする。現状 context metrics の baseline を保存し、後続 issue が context regression を比較できるようにする。

### 受け入れ条件

- [x] `skill-architecture.toml` が repository-change-loop family、user-facing skill 2 件、forbidden standalone skill 名を持つ。
- [x] `skill-architecture.toml` の forbidden list は validator code へ重複ハードコードされない。
- [x] current checkout の operation context metrics が baseline JSON として保存される。
- [x] `knowledge/wiki/syntheses/skill-repository-optimization-v4-spec.md` とこの ledger が `knowledge/index.md` から発見できる。
- [x] `knowledge/log.md` に ingest / planning artifact 追加が記録される。
- [x] 新しい user-facing skill は追加されない。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: なし
- ブロック先: SRO4-002, SRO4-004 release 済み

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

### 実装 evidence

- `skill-architecture.toml` を追加し、repository-change-loop family の user-facing skills と forbidden standalone skill 名を policy file に集約した。
- `scripts/validate_skill_architecture.py` は forbidden standalone skill 名を `skill-architecture.toml` から読み、validator 内に list を重複保持しない。
- `scripts/report_skill_context.py --all --json` の出力を `knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json` として保存した。
- `knowledge/index.md` と `knowledge/log.md` に SRO4-001 policy / baseline artifact を登録した。
- 新しい `skills/*/SKILL.md` は追加していない。
- Implementation review: approved, range `a073a10d38744771c2ed10fe8d9d351e5bf0e588..53fd68f64403505064373100d8ec35543be9c04d`。SRO4-001 worker report は pending 表示を含むが、runtime-state / events の最終 review status を採用する。

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

- [x] `scripts/skill_context/contract.py` が schema version 1 / 2 を読める。
- [x] `scripts/skill_context/metrics.py` が `character_count`、`non_whitespace_character_count`、`estimated_token_count`、`file_count`、`headroom_percent` を返す。
- [x] estimated token は外部 dependency なしで CJK / ascii / other chars を保守的に見積もる。
- [x] `scripts/validate_skill_context.py --all` が missing reference、duplicate reference、reference depth、file count、char budget、estimated token budget、headroom を検出する。
- [x] `scripts/inspect_skill_context.py` と `scripts/report_skill_context.py` が JSON output を持つ。
- [x] `scripts/validate_loop_skill_context.py` と `scripts/inspect_loop_skill_context.py` は compatibility wrapper として既存 CLI を維持する。
- [x] tests は v1 compatibility、v2 budget、Japanese context estimation、failure cases をカバーする。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: SRO4-001
- ブロック先: SRO4-003 release 済み

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

### 実装 evidence

- `scripts/skill_context/` に共通 contract / metrics library を追加し、schema v1/v2、CJK を含む estimated token、headroom、file count を検証対象にした。
- `validate_skill_context.py` / `inspect_skill_context.py` / `report_skill_context.py` を canonical CLI とし、`validate_loop_skill_context.py` / `inspect_loop_skill_context.py` は旧運用向け compatibility wrapper として残した。
- 検証: `validate_skill_context.py --all`、`report_skill_context.py --all --json`、`validate_loop_skill_context.py --all`、grill tests、issue-loop tests、`git diff --check` は SRO4-002 worker report で pass。
- Implementation review: approved, range `53fd68f64403505064373100d8ec35543be9c04d..be17b274c27745f64d0d629ea22d96edcd3fb0ac`。
- 残リスク: estimated token は実モデル tokenizer ではなく保守的 heuristic。schema v2 への実 skill migration は SRO4-003 / SRO4-005 側で完了。

## SRO4-003

### Epic ID

`skill-repository-optimization-v4`

### タイトル

loop skill routing を single-source 化する

### 作るもの

`context-contract.toml` を loop skill read-set の唯一の正本にし、`SKILL.md` と `workflow-contract.md` から operation-specific reference map を消す。`waiting_human` 専用の `execute.wait` operation を追加し、human wait 中の不要 context load を減らす。さらに、implementation handoff 前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを必須手順として skill contract に加える。

### 受け入れ条件

- [x] `skills/grill-to-pr-loop/context-contract.toml` が schema version 2 になる。
- [x] `skills/issue-implementation-loop/context-contract.toml` が schema version 2 になる。
- [x] `grill-to-pr-loop` の base read-set から `references/workflow-contract.md` が外れる。
- [x] `workflow-contract.md` は deprecated shim として残るが、default read-set には含まれない。
- [x] `SKILL.md` は operation-specific reference filename を列挙しない。
- [x] `issue-implementation-loop/context-contract.toml` に `execute.wait` が追加される。
- [x] `select_operation.py` は `waiting_human` を `execute.wait` に routing する。
- [x] `execute.dispatch` から `human-wait.md` が外れ、`execute.wait` が `human-wait.md` と `runtime-state.md` だけを読む。
- [x] `grill-to-pr-loop/SKILL.md` が、approved execution handoff 前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを行うよう指示している。
- [x] `grill-to-pr-loop/references/execution-handoff.md` が、implementation を肥大化した planning context から直接始めず、normalized packet と圧縮済み handoff brief から始める契約を説明している。
- [x] tests は implementation handoff 前の context 圧縮 / fresh coordinator requirement が skill contract から消えないことを検証する。
- [x] global lifecycle、approval、remote boundary、stop condition は `core.md` から発見できる。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: SRO4-002
- ブロック先: SRO4-005 release 済み

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

### 実装 evidence

- loop skill の read-set 正本を `context-contract.toml` に寄せ、`SKILL.md` から operation-specific file 列挙を外した。
- `workflow-contract.md` は deprecated shim として残し、default read-set から外した。旧 link / 外部参照を壊さず、read-set regression は `validate_skill_context.py --all` で検出する。
- `execute.wait` を追加し、`waiting_human` runtime fixture で `select_operation.py` が `execute.wait` を選ぶことを確認した。
- `grill-to-pr-loop` の handoff 前 context 圧縮 / fresh execution coordinator requirement を `SKILL.md` と `references/execution-handoff.md` に固定し、tests で回帰防止した。
- Implementation review: approved, range `be17b274c27745f64d0d629ea22d96edcd3fb0ac..839ce87713c4077cdfca650c8873cd947f67e813`。
- 残リスク: live runtime には `waiting_human` issue がなかったため、`execute.wait` は `/private/tmp` fixture で代表検証した。

## SRO4-004

### Epic ID

`skill-repository-optimization-v4`

### タイトル

Worker Packet V2 と Resume Brief V2 を導入する

### 作るもの

worker / reviewer / resume の context artifact を revision 付きで管理する。Worker Packet V2 は task kind と access mode を明示し、Resume Brief V2 は metadata により stale reuse を拒否できるようにする。

### 受け入れ条件

- [x] `skills/issue-implementation-loop/assets/schemas/worker-packet-v1.schema.json` が既存 schema の互換参照として残る。
- [x] `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json` が schema version 2 default になる。
- [x] Worker Packet V2 は `task_kind`、`access_mode`、`source_revision`、`read_paths[].purpose` を必須にする。
- [x] `implement` / `fix` は `access_mode=read_write` かつ non-empty `write_scope` を要求する。
- [x] `review` / `inspect` は `access_mode=read_only` かつ `write_scope=[]` を要求する。
- [x] packet validator は path traversal と worktree 外 path を拒否する。
- [x] packet validator は stale envelope / runtime / issue revision を拒否する。
- [x] `build_resume_brief.py` は `resume-brief.md` と `resume-brief.meta.json` を生成する。
- [x] `validate_resume_brief.py` は meta と current runtime / envelope / events を比較し、不一致時に stale と判定する。
- [x] V1 packet と旧 brief は既存 run の resume 用に読める。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: SRO4-001
- ブロック先: SRO4-005 の gating dependency として approved head を SRO4-006 で merge 済み

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

### 実装 evidence

- Approved head `e4f7551b49df4082d1266b04b32249a0770d7481` を SRO4-006 branch に merge し、merge commit `0435b90e5227cf84ef0f6e546463b6f8d3d545df` として統合した。merge conflict はなし。
- Worker Packet V2 schema / builder / validator / tests と Resume Brief V2 builder / validator / tests を追加した。
- `worker-packet-v1.schema.json` と旧 brief warning は既存 run の resume 用 compatibility surface として残した。
- `/private/tmp/sro4-006-cli.F6FKUM` fixture で Worker Packet V2 build / validate、stale runtime SHA 拒否、Resume Brief V2 build / validate、stale events SHA 拒否を確認した。
- Implementation review: approved, range `53fd68f64403505064373100d8ec35543be9c04d..e4f7551b49df4082d1266b04b32249a0770d7481`。
- 残リスク: actual runtime/events をそのままコピーした resume fixture は event replay 側が最初の `envelope_revision` を保持するため、`runtime=4 events=1` の mismatch を brief 本文に表示する。CLI validation は current source hash と meta freshness を検証して pass するが、この recovery signal は coordinator-owned runtime/event semantics の後続 hardening 候補。

## SRO4-005

### Epic ID

`skill-repository-optimization-v4`

### タイトル

`llm-wiki` contract と CI を追加する

### 作るもの

loop skill だけでなく、複数 mode と topology reference を持つ `llm-wiki` も context contract の検証対象に入れる。CI で architecture policy、context regression、tests を固定する。

### 受け入れ条件

- [x] `skills/llm-wiki/context-contract.toml` が topology × mode read-set を表現する。
- [x] `llm-wiki` contract は single-root / multi-root と各 mode の read-set を機械検証できる。
- [x] `skills/llm-wiki/SKILL.md` は contract と矛盾する manual read-set を持たない。
- [x] `.github/workflows/skill-architecture.yml` が Python 3.9 / 3.12 matrix で実行される。
- [x] CI は `validate_skill_architecture.py --all`、`validate_skill_context.py --all`、`report_skill_context.py --all --json`、loop skill tests、`git diff --check` を実行する。
- [x] budget 超過、context増加率 10% 超、file count 超過、forbidden standalone skill 追加は CI で失敗または明示 warning になる。
- [x] context report artifact は PR review で読める JSON として出力される。

### ブロッカー

- 実行状態: COMPLETE
- ブロック元: SRO4-003, SRO4-004
- ブロック先: SRO4-006 release 済み

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

### 実装 evidence

- `llm-wiki/context-contract.toml` で single-root / multi-root と 6 modes の read-set を検証対象にした。
- `llm-wiki/SKILL.md` の router と contract を揃え、manual read-set drift を context validator で検出できるようにした。
- `.github/workflows/skill-architecture.yml` に architecture / context / report JSON / loop tests / `llm-wiki` tests / `git diff --check` を固定した。
- Implementation review: approved, range `839ce87713c4077cdfca650c8873cd947f67e813..e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf`。
- 残リスク: GitHub Actions matrix 自体は local-only policy のため未実行。YAML parse と同等コマンドのローカル実行で確認した。

## SRO4-006

### Epic ID

`skill-repository-optimization-v4`

### タイトル

統合検証・移行 shim・wiki ledger を仕上げる

### 作るもの

V4 の全変更を統合し、V1 compatibility、V2 default、deprecated shim、CI、wiki ledger を一貫させる。Execution Plan Gate 後に実装された場合、この issue が completion evidence を local ledger に集約する。

### 受け入れ条件

- [x] `validate_skill_architecture.py --all` が通る。
- [x] `validate_skill_context.py --all` が通る。
- [x] `report_skill_context.py --all --json` が baseline 比較を返す。
- [x] loop skill tests、`llm-wiki` tests、代表 packet / resume CLI が通る。
- [x] deprecated shim と compatibility wrapper の残置理由と削除条件が references または ledger に記録される。
- [x] `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md` に各 issue の実装状態、verification、implementation review result が反映される。
- [x] `knowledge/index.md` と `knowledge/log.md` が V4 の実装状態と residual risks を発見できる。
- [x] remote write を実行しない場合、その理由が ledger に残る。

### ブロッカー

- 実行状態: COMPLETE
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

### 統合 evidence

- SRO4-004 approved head `e4f7551b49df4082d1266b04b32249a0770d7481` を、SRO4-005 approved head `e61c6b1a0f402eb4bb4892dbe5980213f88b0fbf` ベースの SRO4-006 branch に merge した。merge commit は `0435b90e5227cf84ef0f6e546463b6f8d3d545df`、conflict はなし。
- Merge 後の SRO4-006 追加編集は packet write scope 内の `knowledge/wiki/syntheses/skill-repository-optimization-v4-issues.md`、`knowledge/index.md`、`knowledge/log.md` に限定した。
- Worker Packet V2 / Resume Brief V2 representative CLI は `/private/tmp/sro4-006-cli.F6FKUM` fixture で実行した。
- `report_skill_context.py --all --json` は schema version 2、3 skills、warnings `[]`、`llm-wiki` 12 operations を返した。

### SRO4-006 full verification

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all` -> passed: repository-change-loop architecture policy.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all` -> passed: validated 3 skill context contracts.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json` -> passed: baseline comparison JSON, warnings `[]`.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` -> passed: 13 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests` -> passed: 98 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests` -> passed: 5 tests.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_worker_packet.py ... --output /private/tmp/sro4-006-cli.F6FKUM/worker-packet-v2.json` -> passed.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py /private/tmp/sro4-006-cli.F6FKUM/worker-packet-v2.json --json` -> passed: `ok: true`.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py /private/tmp/sro4-006-cli.F6FKUM/worker-packet-v2-stale.json --json` -> expected failure: `source_revision.runtime_state.sha256 is stale`.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_resume_brief.py /private/tmp/sro4-006-cli.F6FKUM/clean-runtime --envelope ... --max-words 300 --stdout` -> passed: active SRO4-006, inconsistencies none.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_resume_brief.py /private/tmp/sro4-006-cli.F6FKUM/clean-runtime --json` -> passed: `ok: true`.
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_resume_brief.py /private/tmp/sro4-006-cli.F6FKUM/runtime-root --meta /private/tmp/sro4-006-cli.F6FKUM/runtime-root/resume-brief-stale.meta.json --json` -> expected failure: `events.sha256 is stale`.

### Compatibility / shim rationale and removal conditions

- `scripts/validate_loop_skill_context.py` と `scripts/inspect_loop_skill_context.py` は、既存 runbook / CI / user muscle memory を壊さず generic `validate_skill_context.py` / `inspect_skill_context.py` へ移行するために残す。削除条件は、repo 内 docs / tests / workflow / worker packet から wrapper 参照が消え、少なくとも 1 execution epic で canonical CLI のみで運用できたこと。
- `skills/grill-to-pr-loop/references/workflow-contract.md` は旧 deep link 用 deprecated shim として残す。削除条件は、`context-contract.toml`、`SKILL.md`、tests、knowledge ledger、既知 worker/resume artifacts から `workflow-contract.md` 参照が消え、default read-set 外であることを 1 cycle 維持できたこと。
- `worker-packet-v1.schema.json` と legacy resume brief warning は既存 V1 packet / old brief を持つ runtime の復旧用に残す。削除条件は、active runtime と archived handoff artifacts が V2 packet / V2 resume meta へ移行済みで、`validate_worker_packet.py` の V1 compatibility test を削除しても復旧契約を失わないこと。

### Remote policy / residual risks

- Remote policy は execution envelope revision 4 の `remote_write_policy.mode=local_only`。ユーザーから push、PR 作成、GitHub issue mirror、merge の明示承認がないため remote write は実行しない。
- GitHub Actions matrix は local-only policy のため未実行。ローカルでは workflow と同等の required commands を実行し、SRO4-005 では YAML parse を確認済み。
- Resume Brief V2 は clean fixture では inconsistencies none だが、現 coordinator runtime/events をコピーした fixture では `runtime=4 events=1` の revision mismatch を本文に表示する。これは final ledger write scope 外の coordinator event replay semantics であり、後続 hardening 候補として残す。
- SRO4-001 worker report は古い `implementation_review.status=pending` 表示を含むが、runtime-state と event log の最終状態は approved / COMPLETE。final ledger は runtime-state を coordinator source として採用する。

## Execution Plan Gate Draft

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

## 関連ページ

- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [Loop Skill Architecture V3 Issues](loop-skill-architecture-v3-issues.md)

## 出典

- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [raw/sources/2026-06-26-skill-repository-optimization-v4-design.md](../../raw/sources/2026-06-26-skill-repository-optimization-v4-design.md)
