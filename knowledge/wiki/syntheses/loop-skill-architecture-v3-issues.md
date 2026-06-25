# Loop Skill Architecture V3 Issues

## 状態

Issue Gate / Execution Plan Gate 承認済み。Execution Packet は [loop-skill-architecture-v3-input-packet.json](loop-skill-architecture-v3-input-packet.json)、Execution Envelope は [loop-skill-architecture-v3-execution-envelope.json](loop-skill-architecture-v3-execution-envelope.json) に置く。G2PR-001 から G2PR-006 は実装レビュー承認済み。実装ループ中の GitHub issue mirror、push、PR 作成、merge は `local_only` により未実行だったが、完了後にユーザーの明示依頼で統合 branch を push し、draft PR [#19](https://github.com/omitsuhashi/skills/pull/19) を作成した。

## Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-skill-architecture-v3 | G2PR-001 | context contract と検証基盤を導入する | 承認済み | 完了 | なし | G2PR-002, G2PR-003, G2PR-004, G2PR-005 | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |
| loop-skill-architecture-v3 | G2PR-002 | entrypoint と reference ownership を圧縮整理する | 承認済み | 完了 | G2PR-001 | G2PR-006 | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |
| loop-skill-architecture-v3 | G2PR-003 | operation selection を構造化 state で決定する | 承認済み | 完了 | G2PR-001 | G2PR-006 | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |
| loop-skill-architecture-v3 | G2PR-004 | worker packet を正規化し context budget を強制する | 承認済み | 完了 | G2PR-001 | G2PR-006 | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |
| loop-skill-architecture-v3 | G2PR-005 | resume brief を派生 artifact として追加する | 承認済み | 完了 | G2PR-001 | G2PR-006 | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |
| loop-skill-architecture-v3 | G2PR-006 | 統合テストと wiki ledger を仕上げる | 承認済み | 完了 | G2PR-002, G2PR-003, G2PR-004, G2PR-005 | なし | 未作成 | 承認済み | [draft PR #19](https://github.com/omitsuhashi/skills/pull/19) |

## ブロッカーグラフ

- G2PR-001: 完了; ブロック元 なし; ブロック先 G2PR-002, G2PR-003, G2PR-004, G2PR-005
- G2PR-002: 完了; ブロック元 G2PR-001; ブロック先 G2PR-006
- G2PR-003: 完了; ブロック元 G2PR-001; ブロック先 G2PR-006
- G2PR-004: 完了; ブロック元 G2PR-001; ブロック先 G2PR-006
- G2PR-005: 完了; ブロック元 G2PR-001; ブロック先 G2PR-006
- G2PR-006: 完了; ブロック元 G2PR-002, G2PR-003, G2PR-004, G2PR-005; ブロック先 なし

## 実装・検証 evidence

Runtime root は `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-architecture-v3`。G2PR-006 の依存 edge は G2PR-002 から G2PR-005 まで全て `base_effect: none` のため、G2PR-006 branch へ各 blocker head は merge していない。

| Issue | 実装状態 | Base | Head | Verification evidence | Implementation review |
| --- | --- | --- | --- | --- | --- |
| G2PR-001 | COMPLETE | `84a2278e9692a3b592fa3195cb956cf74f075a39` | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `validate_loop_skill_context.py --all` passed; `inspect_loop_skill_context.py` returned `budget_headroom=496`; grill tests `Ran 7 tests OK`; issue tests `Ran 55 tests OK` | approved; range `84a2278e9692a3b592fa3195cb956cf74f075a39..2b5637cbecbc044c3a341696e2e9824930f11c81`; Critical/Important/Minor 0 |
| G2PR-002 | COMPLETE | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `d99f16c63b9500034216830f4d824adbe53ff156` | `validate_loop_skill_context.py --all` passed; grill tests `Ran 10 tests OK`; word counts `551 / 507 / 389`; `git diff --check` passed | approved; range `2b5637cbecbc044c3a341696e2e9824930f11c81..d99f16c63b9500034216830f4d824adbe53ff156`; Critical/Important/Minor 0 |
| G2PR-003 | COMPLETE | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `25d4cddbefaad7521a671316aa0dc9057164c742` | `select_operation.py` representative CLI passed; issue tests `Ran 65 tests OK`; `validate_loop_skill_context.py --all` passed; `git diff --check` passed | approved; range `2b5637cbecbc044c3a341696e2e9824930f11c81..25d4cddbefaad7521a671316aa0dc9057164c742`; Critical/Important/Minor 0 |
| G2PR-004 | COMPLETE | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `bc8193584108a7bf56f702284da6fe49702c815f` | issue tests `Ran 65 tests OK`; `build_worker_packet.py` representative CLI passed; `validate_worker_packet.py` returned `ok: true`; `validate_execution_envelope.py` passed; `git diff --check` passed | approved; range `2b5637cbecbc044c3a341696e2e9824930f11c81..bc8193584108a7bf56f702284da6fe49702c815f`; Critical/Important/Minor 0 |
| G2PR-005 | COMPLETE | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `56955c790ffcc98852e519403d695534bfb1749a` | `build_resume_brief.py` representative CLI passed; issue tests `Ran 61 tests OK`; `validate_loop_skill_context.py --all` passed; `git diff --check` passed | approved; range `2b5637cbecbc044c3a341696e2e9824930f11c81..56955c790ffcc98852e519403d695534bfb1749a`; Critical/Important/Minor 0 |
| G2PR-006 | COMPLETE | `2b5637cbecbc044c3a341696e2e9824930f11c81` | `ef5ff23f9c2d03b847d03020a16ef3c494f425d1` | Fresh representative verification below passed, except `quick_validate.py` dependency cache unavailable | approved; range `2b5637cbecbc044c3a341696e2e9824930f11c81..ef5ff23f9c2d03b847d03020a16ef3c494f425d1`; Critical/Important/Minor 0 |

### G2PR-006 fresh verification

- G2PR-006 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all` passed with `OK: validated 2 loop skill context contract(s)`.
- G2PR-006 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/inspect_loop_skill_context.py --skill skills/issue-implementation-loop --operation execute.review --json` returned `word_count=1404`, `word_budget=1900`, `budget_headroom=496`, `file_count=5`.
- G2PR-002 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests` passed with `Ran 10 tests`.
- G2PR-003 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/select_operation.py --envelope /Users/omitsuhashi/.codex/worktrees/d8af/skills/knowledge/wiki/syntheses/loop-skill-architecture-v3-execution-envelope.json --runtime /Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-architecture-v3/runtime-state.json --requested-mode execute --json` passed; output selected `operation=resume`, `priority=reconcile`, `budget_headroom=855`.
- G2PR-004 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_worker_packet.py ... --output /private/tmp/g2pr-006-worker-packet.json` wrote a representative packet; `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py /private/tmp/g2pr-006-worker-packet.json --json` returned `ok: true`.
- G2PR-005 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_resume_brief.py /Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-skill-architecture-v3 --envelope /Users/omitsuhashi/.codex/worktrees/d8af/skills/knowledge/wiki/syntheses/loop-skill-architecture-v3-execution-envelope.json --output /private/tmp/g2pr-006-resume-brief.md --stdout` passed; output reported `COMPLETE=5`, `RUNNING=1`, active `G2PR-006`, pending remote action `none - remote policy local_only`.
- Issue tests passed in relevant worktrees: G2PR-003 `Ran 65 tests`, G2PR-004 `Ran 65 tests`, G2PR-005 `Ran 61 tests`, G2PR-006 `Ran 55 tests`.
- G2PR-002 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json` returned `ok: true`; GitHub auth failure remained optional.
- G2PR-006 worktree: `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --input knowledge/wiki/syntheses/loop-skill-architecture-v3-input-packet.json --json` returned `ok: true`.
- `quick_validate.py` for `skills/grill-to-pr-loop` and `skills/issue-implementation-loop` was attempted in the G2PR-002 worktree and was not verified because the dependency cache was unavailable: both commands failed with `ModuleNotFoundError: No module named 'yaml'`.
- Remote writes were not executed during the implementation loop because the approved execution envelope has `remote_write_policy.mode=local_only`, `approved_actions=[]`, and there was no Remote Gate approval at that point.
- After implementation-loop completion, the user explicitly requested PR creation; integrated branch `codex/skill-loop-optimization` was pushed and draft PR [#19](https://github.com/omitsuhashi/skills/pull/19) was created against `main`. GitHub issue mirror and merge remain unexecuted.

## G2PR-001

### Epic ID

`loop-skill-architecture-v3`

### タイトル

context contract と検証基盤を導入する

### 作るもの

`grill-to-pr-loop` と `issue-implementation-loop` の read set / budget を `context-contract.toml` に移し、operation ごとの context load を検証できる deterministic script を追加する。実行挙動は変えず、後続 issue が entrypoint や worker packet を安全に削れる土台を作る。

### 受け入れ条件

- [ ] `skills/grill-to-pr-loop/context-contract.toml` と `skills/issue-implementation-loop/context-contract.toml` が存在する。
- [ ] 各 contract は skill 名、entrypoint、base references、operation references、word budget、max file count を持つ。
- [ ] `scripts/validate_loop_skill_context.py --all` が valid TOML、missing reference、duplicate reference、reference depth、budget、forbidden standalone skill 名を検証する。
- [ ] `scripts/inspect_loop_skill_context.py --skill <skill> --operation <operation> --json` が files、word count、budget headroom を返す。
- [ ] tests は validator failure cases と successful read-set inspection をカバーする。
- [ ] 外部 dependency を追加しない。

### ブロッカー

- 実行状態: 実行可能
- ブロック元: なし
- ブロック先: G2PR-002, G2PR-003, G2PR-004, G2PR-005

### 想定 write scope

- `path:skills/grill-to-pr-loop/context-contract.toml`
- `path:skills/issue-implementation-loop/context-contract.toml`
- `path:scripts/validate_loop_skill_context.py`
- `path:scripts/inspect_loop_skill_context.py`
- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- skill creator 制約: `SKILL.md` は薄く、詳細は references / scripts に分ける。追加 script は実行検証する。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/inspect_loop_skill_context.py --skill skills/issue-implementation-loop --operation execute.review --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`

## G2PR-002

### Epic ID

`loop-skill-architecture-v3`

### タイトル

entrypoint と reference ownership を圧縮整理する

### 作るもの

`grill-to-pr-loop/SKILL.md` を operation router と gate の入口に圧縮し、global workflow context を `references/core.md` に移す。branch、packet、remote delivery、ledger の詳細は各 reference の所有に寄せる。agents metadata の default prompt も詳細 policy を含まない短い prompt へ整理する。

### 受け入れ条件

- [ ] `skills/grill-to-pr-loop/SKILL.md` が 850 words 以下になる。
- [ ] `skills/issue-implementation-loop/SKILL.md` は 520 words 以下を維持する。
- [ ] `skills/grill-to-pr-loop/references/core.md` が追加され、workflow lifecycle、責任境界、gate、local-first、remote approval を 600 words 以下で持つ。
- [ ] `workflow-contract.md` と `context-contract.toml` の routing が矛盾しない。
- [ ] `remote-delivery.md` を rename する場合は互換 shim または全参照更新を行い、GitHub mirror / ledger sync の正本が 1 つになる。
- [ ] `agents/openai.yaml` の default prompt は各 32 words 以下で、branch / review / delivery 詳細 policy を含まない。
- [ ] `skill-creator` の方針に従い、SKILL body へ reference と重複する詳細説明を戻さない。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001
- ブロック先: G2PR-006

### 想定 write scope

- `path:skills/grill-to-pr-loop/SKILL.md`
- `path:skills/grill-to-pr-loop/context-contract.toml`
- `path:skills/grill-to-pr-loop/references`
- `path:skills/grill-to-pr-loop/agents/openai.yaml`
- `path:skills/issue-implementation-loop/agents/openai.yaml`
- `path:skills/grill-to-pr-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- 既存 reference: `skills/grill-to-pr-loop/references/workflow-contract.md`
- skill creator 制約: YAML frontmatter は `name` と `description` を基本とし、trigger 情報は description に寄せる。agents metadata は SKILL と整合させる。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `wc -w skills/grill-to-pr-loop/SKILL.md skills/issue-implementation-loop/SKILL.md skills/grill-to-pr-loop/references/core.md`
- `git diff --check`

## G2PR-003

### Epic ID

`loop-skill-architecture-v3`

### タイトル

operation selection を構造化 state で決定する

### 作るもの

`issue-implementation-loop` の operation を LLM の自由分類ではなく、execution envelope、runtime state、requested mode から deterministic に選ぶ `select_operation.py` を追加する。返却値には operation、reason、対象 issue、read set、word budget 判定を含める。

### 受け入れ条件

- [ ] `skills/issue-implementation-loop/scripts/select_operation.py` が存在する。
- [ ] input は envelope、runtime、requested mode を受け取り、JSON output を返す。
- [ ] priority は spec の順序に従う: explicit deliver/status、未作成 envelope、未予約、git/state 不整合、reviewable、fixable、human wait、runnable、terminal、reconcile。
- [ ] output は `context-contract.toml` 由来の read set と budget 判定を含む。
- [ ] operation selection のために追加 LLM router を使わない。
- [ ] tests は代表 state と priority conflict をカバーする。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001
- ブロック先: G2PR-006

### 想定 write scope

- `path:skills/issue-implementation-loop/scripts/select_operation.py`
- `path:skills/issue-implementation-loop/scripts/lib/issue_implementation_loop`
- `path:skills/issue-implementation-loop/tests`
- `path:skills/issue-implementation-loop/references`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- 既存 runtime / scheduler / recovery references。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/select_operation.py --envelope <execution-envelope.json> --runtime <runtime-state.json> --requested-mode execute --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all`

## G2PR-004

### Epic ID

`loop-skill-architecture-v3`

### タイトル

worker packet を正規化し context budget を強制する

### 作るもの

worker dispatch 用の schema、template、builder、validator を追加し、worker prompt へ full spec / full ledger を貼らない paths-first 契約を機械的に強制する。budget 超過時は silent truncate せず fail-fast にする。

### 受け入れ条件

- [ ] `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json` が存在する。
- [ ] `skills/issue-implementation-loop/assets/templates/worker-packet.json` が存在する。
- [ ] `skills/issue-implementation-loop/scripts/build_worker_packet.py` と `validate_worker_packet.py` が存在する。
- [ ] default 450 words、hard 800 words、read paths 8 件以下、inline excerpt 1 file 120 words以下、inline 合計 300 words以下を強制する。
- [ ] full spec / full ledger を含む packet を拒否する。
- [ ] budget 超過は `PACKET_CONTEXT_BUDGET_EXCEEDED` 相当で失敗し、自動切り落としをしない。
- [ ] worker contract reference と execution envelope context policy が新 packet を参照する。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001
- ブロック先: G2PR-006

### 想定 write scope

- `path:skills/issue-implementation-loop/assets/schemas`
- `path:skills/issue-implementation-loop/assets/templates`
- `path:skills/issue-implementation-loop/scripts/build_worker_packet.py`
- `path:skills/issue-implementation-loop/scripts/validate_worker_packet.py`
- `path:skills/issue-implementation-loop/scripts/lib/issue_implementation_loop`
- `path:skills/issue-implementation-loop/references/worker-contract.md`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- 既存 `context_policy` schema / template / validator。
- skill creator 制約: fragile で繰り返す処理は script に寄せ、追加 script は実行検証する。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_worker_packet.py <args>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py <worker-packet.json>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `git diff --check`

## G2PR-005

### Epic ID

`loop-skill-architecture-v3`

### タイトル

resume brief を派生 artifact として追加する

### 作るもの

長時間実行後の再開で full event log や過去会話に戻らないよう、runtime state と events から 600 words 以下の `resume-brief.md` を生成する builder と template を追加する。brief は canonical state ではなく、再生成可能な cache として扱う。

### 受け入れ条件

- [ ] `skills/issue-implementation-loop/assets/templates/resume-brief.md` が存在する。
- [ ] `skills/issue-implementation-loop/scripts/build_resume_brief.py` が存在する。
- [ ] brief は Epic ID、overall status、runnable、active、reviewable、fixable、waiting human、pending remote action、verified commit ranges、latest report paths、recommended next operation を持つ。
- [ ] brief は 600 words 以下を強制する。
- [ ] brief は execution envelope、runtime state、events から再生成できる cache であり、canonical state として扱わない。
- [ ] runtime-state / recovery references が resume brief の読み方と不整合時の調査方針を説明する。
- [ ] tests は normal brief、budget overflow、不整合時の handling をカバーする。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-001
- ブロック先: G2PR-006

### 想定 write scope

- `path:skills/issue-implementation-loop/assets/templates/resume-brief.md`
- `path:skills/issue-implementation-loop/scripts/build_resume_brief.py`
- `path:skills/issue-implementation-loop/scripts/lib/issue_implementation_loop`
- `path:skills/issue-implementation-loop/references/runtime-state.md`
- `path:skills/issue-implementation-loop/references/recovery.md`
- `path:skills/issue-implementation-loop/tests`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- 既存 runtime rebuild / recovery scripts。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/build_resume_brief.py <runtime-root>`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `git diff --check`

## G2PR-006

### Epic ID

`loop-skill-architecture-v3`

### タイトル

統合テストと wiki ledger を仕上げる

### 作るもの

G2PR-002 から G2PR-005 までの成果を統合し、context validation、operation selection、worker packet、resume brief、entrypoint budget、skill metadata の契約を横断で検証する。local ledger には実装状態、verification、implementation review 結果を反映する。

### 受け入れ条件

- [x] `scripts/validate_loop_skill_context.py --all` が通る。
- [x] `scripts/inspect_loop_skill_context.py` が代表 operation で budget headroom を返す。
- [x] `select_operation.py`、`validate_worker_packet.py`、`build_resume_brief.py` の代表 CLI が通る。
- [x] `python3 -m unittest discover -s skills/grill-to-pr-loop/tests` が通る。
- [x] `python3 -m unittest discover -s skills/issue-implementation-loop/tests` が通る。
- [x] `check_prereqs.py --phase execution --json` と `check_capabilities.py --json` が通る。
- [x] `quick_validate.py` は dependency cache が使える場合に `skills/grill-to-pr-loop` と `skills/issue-implementation-loop` で実行する。使えない場合は未検証理由を ledger に残す。
- [x] local issue ledger に実装状態、verification、implementation review 結果、remote write 未実行理由が反映されている。

### ブロッカー

- 実行状態: ブロック中
- ブロック元: G2PR-002, G2PR-003, G2PR-004, G2PR-005
- ブロック先: なし

### 想定 write scope

- `path:skills/grill-to-pr-loop/tests`
- `path:skills/issue-implementation-loop/tests`
- `path:knowledge/wiki/syntheses/loop-skill-architecture-v3-issues.md`
- `path:knowledge/index.md`
- `path:knowledge/log.md`

### 必要な文脈

- 仕様: [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- この ledger。
- skill creator 制約: substantial skill revision では forward-test を検討する。ただし subagent / remote / long-running validation が必要な場合は別途承認を取る。

### 検証

- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json`
- `PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --json`
- `git diff --check`

## Remote Policy

実装ループ中は `local_only`。GitHub auth は optional failure であり、Remote Gate の明示承認もなかったため、GitHub issue / PR / push / merge は実行しない方針だった。

G2PR-006 でも remote write は実行していない。理由は approved execution envelope の `remote_write_policy.mode=local_only`、`approved_actions=[]`、および Remote Gate の明示承認なし。

完了後、ユーザーの明示依頼により統合 branch `codex/skill-loop-optimization` を `origin` へ push し、draft PR [#19](https://github.com/omitsuhashi/skills/pull/19) を `main` 向けに作成した。GitHub issue mirror と merge は未実行。

## Execution Plan Gate 承認事項

- Packet: [loop-skill-architecture-v3-input-packet.json](loop-skill-architecture-v3-input-packet.json)
- Envelope: [loop-skill-architecture-v3-execution-envelope.json](loop-skill-architecture-v3-execution-envelope.json)
- Capability preflight: `ok: true`
- Delivery intent: `local_only`
- reviewer capability: `requesting-code-review` available
- TDD capability: available
- remote writes: 未承認のため実行しない
- parallel execution: platform-dependent。worker contexts が使えない場合は実装前に停止
- G2PR-006 は複数 blocker head を直接 merge しないよう、dependency `base_effect` を `none` にする

## Prepare 結果

- Envelope revision: 1
- `epic_base.ref`: `codex/loop-skill-architecture-v3/epic-base`
- `epic_base.sha`: `84a2278e9692a3b592fa3195cb956cf74f075a39`
- physical worktree creation: 未実行
- runnable on prepare: G2PR-001 のみ `create_on_run`
- blocked reservations: G2PR-002, G2PR-003, G2PR-004, G2PR-005, G2PR-006 は `reserved`
- `validate_execution_envelope.py`: `EXECUTION ENVELOPE OK`
- `reconcile_git_state.py --json`: `ok: true`, collisions 0
- `check_capabilities.py --input loop-skill-architecture-v3-input-packet.json --json`: `ok: true`

## Issue Gate 承認事項

- 粒度: 6 issue。
- 依存: G2PR-001 を土台にし、G2PR-002 から G2PR-005 を並列化可能、G2PR-006 を統合仕上げにする。
- G2PR-002 の `remote-delivery.md` rename は、実装時に互換 shim または全参照更新を必須にする。
- forward-test は G2PR-006 の検討事項に留め、実行が長い・subagent が必要・追加承認が必要な場合は止める。

## 関連ページ

- [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- [Loop Skill Architecture V3 Design](../sources/2026-06-25-loop-skill-architecture-v3-design.md)
- [Loop Skill Context Optimization Issues](loop-skill-context-optimization-issues.md)
- [Issue Implementation Loop Common Lib Split Issues](issue-implementation-loop-common-lib-split-issues.md)

## 出典

- [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- [Loop Skill Architecture V3 Design](../sources/2026-06-25-loop-skill-architecture-v3-design.md)
- [raw/sources/2026-06-25-loop-skill-architecture-v3-design.md](../../raw/sources/2026-06-25-loop-skill-architecture-v3-design.md)
