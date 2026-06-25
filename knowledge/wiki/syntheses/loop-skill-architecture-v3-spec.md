# Loop Skill Architecture V3 Spec

## 状態

Spec Gate / Issue Gate 承認済み。承認済み local issue ledger は [Loop Skill Architecture V3 Issues](loop-skill-architecture-v3-issues.md) に置く。Execution Packet 作成へ進める。GitHub issue mirror、実装、push、PR 作成は Execution Plan Gate 承認後まで行わない。

## Problem Statement

`grill-to-pr-loop` と `issue-implementation-loop` は長い repository change を扱えるようになったが、loop skill の運用にはまだ次の摩擦が残っている。

- `grill-to-pr-loop/SKILL.md` が 1265 words あり、entrypoint と詳細契約の境界がまだ太い。
- read set の正本が `SKILL.md` と reference router に分散しており、operation ごとの context budget を機械的に検証できない。
- worker dispatch 時に full spec / ledger を貼らない方針はあるが、worker packet schema / builder / validator で強制されていない。
- resume 時に短い resume brief から再開する仕組みが未実装で、長い event log や過去 conversation へ戻りやすい。
- operation selection が構造化 state から決定されず、LLM の自由分類に寄りやすい。
- default prompt に branch policy や review policy が混ざり、user-facing trigger と実装詳細の境界が曖昧になる。

## Success Criteria

- user-facing loop skill は `grill-to-pr-loop` と `issue-implementation-loop` の 2 つだけに留める。
- scheduler、runtime、worktree、review gate、remote delivery、worker context は独立 skill にしない。
- `context-contract.toml` が各 skill の base references、operation references、word budgets を機械可読に持つ。
- `SKILL.md` は context contract と operation routing の入口に圧縮され、詳細契約は operation-specific references に置かれる。
- operation ごとの read set と word budget を local script で検証できる。
- worker packet / resume brief が paths-first、budgeted、fail-fast な durable artifact として作れる。
- current implementation behavior、schema version 1、remote write/final merge policy を弱めない。

## Epic ID

`loop-skill-architecture-v3`

## Current Baseline

2026-06-25 の current checkout で確認した状態は次の通り。

- `git status --short`: clean。
- active branch: `main`。
- `grill-to-pr-loop` planning prereq: passed。
- GitHub remote は存在するが、`gh` auth は unavailable。remote write は未承認として扱う。
- `issue-implementation-loop-common-lib-split` は完了済みで、`scripts/lib/issue_implementation_loop/` と behavior-domain test files は存在する。
- `context-contract.toml`、worker-packet schema/template、resume-brief template、`select_operation.py`、`validate_loop_skill_context.py`、`inspect_loop_skill_context.py` は未存在。
- word count は `grill-to-pr-loop/SKILL.md` が 1265 words、`issue-implementation-loop/SKILL.md` が 507 words。

## Accepted Decisions

- 直接呼ぶ loop skill は `grill-to-pr-loop` と `issue-implementation-loop` の 2 つに固定する。
- 新しい standalone skill として scheduler、execution-envelope、dependency-graph、runtime-state、worktree-lifecycle、review-gate、human-wait、remote-delivery、worker-contract、context-manager を追加しない。
- long spec / implementation contract / Goal preparation artifact は `knowledge/wiki/syntheses/` に置く。
- local issue ledger は日本語 local-first を canonical とし、GitHub issue は明示承認後の mirror に限定する。
- remote write は未承認のため `local_only`。GitHub issue / PR / push / merge はこの spec では行わない。
- `_common.py` lib split と test split は既存実装済みとして扱い、今回の実装 scope では再実装しない。

## Decisions Requiring Spec Gate Approval

- `context-contract.toml` を各 loop skill の read-set 正本として導入する。
- `SKILL.md` から branch/base、packet field、remote delivery、local ledger の詳細説明を削り、operation router に圧縮する。
- `grill-to-pr-loop/references/core.md` を追加し、global workflow context を 600 words 以下で保持する。
- `grill-to-pr-loop/references/remote-delivery.md` は必要なら `delivery-coordination.md` へ rename し、GitHub mirror と ledger sync の正本名を整理する。
- `issue-implementation-loop` に構造化 operation selection、worker packet builder、resume brief builder を追加する。
- root-level `scripts/validate_loop_skill_context.py` と `scripts/inspect_loop_skill_context.py` を追加し、context budget を検証対象に入れる。

## Non-Goals

- 新しい user-facing skill の追加。
- `issue-implementation-loop` の scheduler semantics、runtime schema、delivery policy の仕様変更。
- schema version 1 artifact の破壊的変更。
- GitHub issue / PR 作成、push、merge、remote write。
- final PR merge の自動化。
- 外部 Python dependency の追加。
- 過去の `loop-skill-context-optimization` と `issue-implementation-loop-common-lib-split` の再実装。

## Issue Decomposition Strategy

Spec Gate 承認後に、日本語 local-first ledger として次の blocker order で issue 化する。

1. **LSO3-001: context contract と validator を導入する**
   - `context-contract.toml` を 2 skill に追加する。
   - `validate_loop_skill_context.py` と `inspect_loop_skill_context.py` を追加する。
   - read set、word budget、reference existence、reference depth、forbidden standalone skill 名を検証する。

2. **LSO3-002: entrypoint と reference ownership を整理する**
   - `grill-to-pr-loop/SKILL.md` を 850 words 以下へ圧縮する。
   - `grill-to-pr-loop/references/core.md` を追加する。
   - handoff / delivery の所有境界を context contract と一致させる。
   - default prompt を各 32 words 以下へ整理する。

3. **LSO3-003: operation selection を構造化 state から決定する**
   - `select_operation.py` を追加する。
   - envelope / runtime / requested mode から operation、reason、read set、budget result を返す。
   - 追加 LLM router に依存しない。

4. **LSO3-004: worker packet を正規化し budget を強制する**
   - worker-packet schema/template/builder/validator を追加する。
   - paths-first、read_paths 上限、inline excerpt 上限、full spec / ledger 禁止を強制する。
   - budget 超過は silent truncate せず fail-fast にする。

5. **LSO3-005: resume brief を派生 artifact として追加する**
   - resume-brief template/builder を追加する。
   - runtime state / events / reports から 600 words 以下の brief を生成する。
   - brief は cache であり canonical state ではないことを reference と tests に明記する。

6. **LSO3-006: tests と wiki ledger を更新する**
   - context validation、operation selection、worker packet、resume brief、entrypoint budget の regression tests を追加する。
   - local issue ledger に実装状態、verification、review result を反映する。

## Acceptance Criteria

- `skills/grill-to-pr-loop/context-contract.toml` と `skills/issue-implementation-loop/context-contract.toml` が存在し、valid TOML として読める。
- 各 context contract は `base_references`、operation references、word budget、max file count を持つ。
- context validator が missing reference、duplicate reference、reference depth > 1、budget 超過、forbidden standalone skill 名を検出する。
- `inspect_loop_skill_context.py` が operation ごとの files、word count、budget headroom を JSON で返す。
- `grill-to-pr-loop/SKILL.md` は 850 words 以下、`issue-implementation-loop/SKILL.md` は 520 words 以下を満たす。
- agents default prompt は各 32 words 以下で、branch / review / delivery の詳細 policy を含まない。
- `select_operation.py` が deterministic priority で operation を返し、追加 LLM routing を使わない。
- worker packet schema / template / builder / validator が存在し、default 450 words / hard 800 words の policy を強制する。
- worker packet は full spec / full ledger を含められず、budget 超過時に `PACKET_CONTEXT_BUDGET_EXCEEDED` 相当で失敗する。
- resume brief builder が 600 words 以下の brief を生成し、brief を canonical state として扱わない。
- scheduler / runtime / delivery の既存 behavior が変わらない。
- schema version 1 artifact の互換性を維持する。
- remote write / final merge policy を弱めない。

## Verification Commands

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/inspect_loop_skill_context.py --skill skills/issue-implementation-loop --operation execute.review --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/select_operation.py --envelope <execution-envelope.json> --runtime <runtime-state.json> --requested-mode execute --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py <worker-packet.json>
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/check_capabilities.py --json
git diff --check
```

`quick_validate.py` は PyYAML が必要なため、dependency cache が利用可能な場合だけ追加検証として実行する。

## Remote Write Policy

`local_only`。

GitHub auth は optional failure であり、Issue Gate / Execution Plan Gate / Remote Gate の明示承認もないため、GitHub issue / PR / push / merge は実行しない。

## Human Review Gates

- **Spec Gate**: この spec の Epic ID、accepted decisions、non-goals、acceptance criteria、verification、stop conditions を承認する。
- **Issue Gate**: 承認後に作る日本語 local-first issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: normalized input packet、write scopes、remote policy、fallback policy を承認する。
- **Implementation Review Gate**: 各 issue completion / blocker release / PR_READY 前に issue-scoped implementation review を実施する。

Spec Gate / Issue Gate / Execution Plan Gate は承認後に、承認済み local artifacts と ledger/log 更新を commit してから次フェーズへ進む。ユーザーが明示的に commit 延期を指示した場合は、その例外を ledger/log に記録する。

## Stop Conditions

- `context-contract.toml` と `SKILL.md` が二重の source of truth になる。
- reference 分割により、実際には全 reference 読込が必要になる。
- budget 削減のために approval / safety rule / stop condition が消える。
- worker packet の短縮で acceptance criteria や stop condition が欠落する。
- resume brief が canonical state として扱われる。
- operation selection のために追加 LLM router が必要になる。
- scheduler、runtime、delivery の既存 behavior が変わる。
- schema version 1 artifact が読めなくなる。
- repo-local skill discovery の優先順位が下がる。
- remote write または破壊的操作が必要になる。

## Known Risks

- `grill-to-pr-loop/SKILL.md` の圧縮時に、gate や stop condition の発見性を落とす可能性がある。
- `delivery-coordination.md` への rename は current `remote-delivery.md` 参照と衝突しやすいため、互換 shim または link 更新を明示する必要がある。
- worker packet の word budget を厳密にすると、既存 worker report / acceptance criteria の要約設計が必要になる。
- resume brief builder は event fold と runtime state の整合に依存するため、既存 `rebuild_runtime_state.py` との境界を崩さないようにする必要がある。

## 関連ページ

- [Loop Skill Architecture V3 Design](../sources/2026-06-25-loop-skill-architecture-v3-design.md)
- [Loop Skill Architecture V3 Issues](loop-skill-architecture-v3-issues.md)
- [Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md)
- [Issue Implementation Loop Common Lib Split Spec](issue-implementation-loop-common-lib-split-spec.md)
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md)
- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md)
- [Grill To PR Loop Epic Base Delivery Policy Spec](grill-to-pr-loop-epic-base-delivery-policy-spec.md)

## 出典

- [Loop Skill Architecture V3 Design](../sources/2026-06-25-loop-skill-architecture-v3-design.md)
- [raw/sources/2026-06-25-loop-skill-architecture-v3-design.md](../../raw/sources/2026-06-25-loop-skill-architecture-v3-design.md)
- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/grill-to-pr-loop/references/workflow-contract.md](../../../skills/grill-to-pr-loop/references/workflow-contract.md)
- [skills/issue-implementation-loop/scripts/lib/issue_implementation_loop](../../../skills/issue-implementation-loop/scripts/lib/issue_implementation_loop)
