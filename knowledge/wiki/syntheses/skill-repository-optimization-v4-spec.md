# Skill Repository Optimization V4 Spec

## 状態

Spec Gate 承認済み。承認日時は 2026-06-26。2026-06-26 のユーザー追補として、実装開始前にメイン planning session の context 圧縮または fresh execution coordinator への切り替えを skill 契約へ追加する。Issue ledger と input packet は同じ source から作ったゲート確認用 draft であり、Issue Gate / Execution Plan Gate は未承認。実装、GitHub issue mirror、push、PR 作成、merge は行わない。

## Problem Statement

PR #19 で loop skill V3 最適化は `main` に入り、context contract、operation selection、worker packet、resume brief は導入済みになった。ただし現在の実装はまだ V4 の品質境界に届いていない。

- `grill-to-pr-loop/context-contract.toml` は存在するが、base read-set に `references/workflow-contract.md` が残っており、read-set 正本が contract と router reference に分散している。
- `context-contract.toml` は schema version を持たず、word budget と file count に依存している。日本語中心の context では word count が token 量を過小評価し得る。
- `issue-implementation-loop` の `waiting_human` は `execute.dispatch` に routing され、human wait 中にも scheduler / worker contract を読み得る。
- worker packet は paths-first / bounded になったが、schema version 1 のまま `task_kind`、`access_mode`、revision 照合、root 境界検証がない。
- resume brief は生成できるが、`resume-brief.meta.json` による鮮度検証や source digest がなく、古い brief の再利用を機械的に拒否できない。
- `llm-wiki` も複数 mode / topology reference を持つが、機械可読 context contract の検証対象に入っていない。
- forbidden standalone skill 名は validator code にハードコードされており、skill family policy の正本が独立 artifact になっていない。

## Success Criteria

- user-facing loop skill は `grill-to-pr-loop` と `issue-implementation-loop` の 2 つに固定し、内部機構を standalone skill にしない。
- `skill-architecture.toml` が repository-change-loop family policy と forbidden standalone skill を機械可読に持つ。
- `context-contract.toml` schema version 2 が read-set、file count、character budget、estimated token budget、headroom を持つ唯一の read-set 正本になる。
- `SKILL.md` は operation-specific reference filename を列挙せず、trigger / guard / operation resolver / invariant / stop condition に集中する。
- `workflow-contract.md` は deprecated shim とし、base read-set から外れる。
- `issue-implementation-loop` に `execute.wait` が追加され、`waiting_human` は worker dispatch ではなく wait 専用 read-set へ routing される。
- Worker Packet V2 が implement / fix / review / inspect を表現し、review / inspect は read-only で write scope を持たない。
- Worker Packet V2 と Resume Brief V2 は source revision / runtime revision を照合し、stale artifact を実行前に拒否する。
- `grill-to-pr-loop` は approved execution handoff 前に、メイン planning session の context 圧縮または fresh execution coordinator への切り替えを必須手順として案内する。
- `llm-wiki` の topology × mode read-set が context contract で検証される。
- CI が skill architecture、context contract、packet / resume schema、context regression、loop skill tests を検証する。

## Epic ID

`skill-repository-optimization-v4`

## Current Baseline

2026-06-26 の current checkout で確認した状態は次の通り。

- active branch: `main`。
- HEAD: `74c774b Merge pull request #19 from omitsuhashi/codex/skill-loop-optimization`。
- `git status --short`: clean だった。
- `grill-to-pr-loop` planning prereq: passed。
- GitHub remote は存在するが `gh` auth は unavailable。remote write は未承認として扱う。
- word count: `skills/grill-to-pr-loop/SKILL.md` 611 words、`skills/issue-implementation-loop/SKILL.md` 507 words、`skills/grill-to-pr-loop/references/core.md` 421 words、`skills/issue-implementation-loop/references/core.md` 264 words。
- `grill-to-pr-loop/context-contract.toml` は `base_references = ["references/core.md", "references/workflow-contract.md"]` を持ち、operation read-set と router reference が二重管理になっている。
- `issue-implementation-loop/context-contract.toml` は `execute.dispatch` に `scheduler.md`、`worker-contract.md`、`human-wait.md`、`runtime-state.md` を含み、`execute.wait` は未定義。
- `scripts/validate_loop_skill_context.py` は external dependency なしの TOML subset parser と word count validator を持つが、schema version / char count / estimated token count / headroom percent / policy file 読み込みは未実装。
- `skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json` は schema version 1 で、`task_kind`、`access_mode`、`source_revision`、root 境界検証を持たない。
- `skills/issue-implementation-loop/scripts/build_resume_brief.py` は `resume-brief.md` を生成するが、`resume-brief.meta.json` は生成しない。

## Accepted Decisions

- 新しい user-facing skill は作らない。`scheduler`、`runtime-state`、`review-gate`、`worker-contract`、`context-manager`、`remote-delivery`、`worktree-lifecycle` は internal reference / schema / script / library とする。
- `context-contract.toml` を operation read-set の唯一の正本にする。
- `SKILL.md` は skill-creator の原則に従い、trigger と必須 invariant を残して短く保つ。詳細 contract は references、deterministic script、schema に置く。
- budget は word count だけでなく `character_count`、`non_whitespace_character_count`、`estimated_token_count`、`file_count`、`headroom_percent` で検証する。
- estimated token は外部 tokenizer dependency なしの保守的な近似でよい。
- `llm-wiki` は generic skill として V4 contract 対象に含めるが、Portfolio OS など system-specific adapter logic は混ぜない。
- 実装開始前に、メイン planning session の肥大化した context をそのまま implementation worker / coordinator に持ち込まない。圧縮済み handoff brief または normalized packet から始まる fresh execution coordinator を使う。
- remote write は未承認のため `local_only`。GitHub issue / PR / push / merge はこの spec では行わない。

## Decisions Requiring Spec Gate Approval

- root の `skill-architecture.toml` を family policy の正本として追加する。
- `scripts/skill_context/` を追加し、contract parsing、metrics、inspection、validation を root validator から分離する。
- `validate_loop_skill_context.py` / `inspect_loop_skill_context.py` を compatibility wrapper として残し、汎用 `validate_skill_context.py` / `inspect_skill_context.py` / `report_skill_context.py` を追加する。
- `grill-to-pr-loop` と `issue-implementation-loop` の context contract を schema version 2 に移行する。
- `grill-to-pr-loop` の base read-set から `workflow-contract.md` を外し、`workflow-contract.md` を deprecated shim にする。
- `issue-implementation-loop` に `execute.wait` operation を追加し、`waiting_human` routing を移す。
- `grill-to-pr-loop` の implementation handoff 手順に、メイン planning session の context 圧縮または fresh execution coordinator への切り替えを追加する。
- Worker Packet V2 schema/template/builder/validator を追加し、V1 artifact は resume 互換用に読み続ける。
- Resume Brief V2 の `.meta.json` を追加し、resume 時に freshness を検証する。
- `.github/workflows/skill-architecture.yml` を追加する。

## Non-Goals

- 新しい user-facing skill の追加。
- scheduler / runtime / delivery の semantics 変更。
- schema version 1 artifact の破壊的変更。
- GitHub issue mirror、push、PR 作成、merge、final PR merge。
- 外部 Python dependency の追加。
- 既存 V3 成果の再実装。
- `llm-wiki` に project-specific runtime adapter を混ぜること。

## Issue Decomposition Strategy

Spec Gate 承認後に、日本語 local-first ledger として次の blocker order で承認する。

1. **SRO4-001: 粒度 policy・baseline・V4 spec を正本化する**
   - `skill-architecture.toml` を追加する。
   - 現状 context baseline を JSON で保存する。
   - V4 spec / source summary / local ledger を discoverable にする。

2. **SRO4-002: Context Contract V2 と共通 validator を導入する**
   - schema version 1 / 2 を読める context parser と metrics を追加する。
   - chars / estimated tokens / file count / headroom を検証する。
   - compatibility wrappers を残す。

3. **SRO4-003: loop skill routing を single-source 化する**
   - loop skill の `SKILL.md` から operation-specific filename 列挙を消す。
   - `workflow-contract.md` を base read-set から外す。
   - `execute.wait` を追加し、`waiting_human` を wait 専用 operation へ routing する。
   - implementation handoff 前に、メイン planning session の context 圧縮または fresh execution coordinator への切り替えを必須化する。

4. **SRO4-004: Worker Packet V2 と Resume Brief V2 を導入する**
   - packet schema/template/builder/validator を V2 対応にする。
   - `resume-brief.meta.json` を生成 / 検証する。
   - stale packet / stale brief を拒否する。

5. **SRO4-005: `llm-wiki` contract と CI を追加する**
   - `skills/llm-wiki/context-contract.toml` を追加する。
   - context report と architecture validation を CI に載せる。
   - budget 超過 / forbidden standalone skill / duplicate read-set を CI failure にする。

6. **SRO4-006: 統合検証・移行 shim・wiki ledger を仕上げる**
   - V1 compatibility、V2 default、CI、docs、ledger 更新を統合検証する。
   - local issue ledger に実装 evidence と review result を反映する。

## Acceptance Criteria

- `skill-architecture.toml` が repository-change-loop family、user-facing skill 2 件、forbidden standalone skill 名を持つ。
- `scripts/skill_context/` が context contract parsing、metrics、inspection、validation を提供する。
- `scripts/validate_skill_architecture.py --all` が forbidden standalone skill 追加と policy 逸脱を検出する。
- `scripts/validate_skill_context.py --all` が schema v1 / v2、missing reference、duplicate reference、reference depth、file count、char budget、estimated token budget、headroom を検証する。
- `scripts/report_skill_context.py --all --json` が operation ごとの current metrics と baseline 比較を返す。
- compatibility wrappers `validate_loop_skill_context.py` / `inspect_loop_skill_context.py` は既存 CLI を壊さない。
- `grill-to-pr-loop/context-contract.toml` の base read-set から `workflow-contract.md` が外れる。
- `issue-implementation-loop/context-contract.toml` に `execute.wait` が追加される。
- `select_operation.py` は `waiting_human` を `execute.wait` に routing する。
- `grill-to-pr-loop/SKILL.md` と `execution-handoff.md` が、implementation handoff 前のメイン session context 圧縮または fresh execution coordinator 切り替えを必須手順として説明する。
- Worker Packet V2 は `task_kind`、`access_mode`、`source_revision`、`read_paths[].purpose`、root 境界 validation を持つ。
- Review / inspect packet は `access_mode=read_only` かつ `write_scope=[]` でなければならない。
- Resume Brief V2 は `resume-brief.md` と `resume-brief.meta.json` を生成し、revision / sequence / digest 不一致時に再生成または拒否できる。
- `skills/llm-wiki/context-contract.toml` が topology × mode read-set を表現し、validator に含まれる。
- `.github/workflows/skill-architecture.yml` が Python 3.9 / 3.12 matrix で architecture、context、tests、`git diff --check` を実行する。

## Verification Commands

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_loop_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/inspect_loop_skill_context.py --skill skills/issue-implementation-loop --operation execute.wait --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/select_operation.py --envelope <execution-envelope.json> --runtime <runtime-state.json> --requested-mode execute --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_worker_packet.py <worker-packet-v2.json> --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_resume_brief.py <runtime-root>
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
git diff --check
```

`quick_validate.py` は PyYAML が必要なため、dependency cache が利用可能な場合だけ追加検証として実行する。

## Remote Write Policy

`local_only`。

GitHub auth は optional failure であり、Issue Gate / Execution Plan Gate / Remote Gate の明示承認もないため、GitHub issue / PR / push / merge は実行しない。final PR merge は常に human-only。

## Human Review Gates

- **Spec Gate**: この spec の Epic ID、accepted decisions、non-goals、acceptance criteria、verification、stop conditions を承認する。
- **Issue Gate**: 日本語 local-first issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: normalized input packet、write scopes、dependency graph、fallback policy、remote policy を承認する。
- **Implementation Review Gate**: 各 issue completion / blocker release / PR_READY 前に issue-scoped implementation review を実施する。
- **Remote Gate**: 外部 write が必要になった場合だけ exact action set を提示し、明示承認を待つ。

Spec Gate / Issue Gate / Execution Plan Gate は承認後に、承認済み local artifacts と `knowledge/log.md` 更新を commit してから次フェーズへ進む。ユーザーが明示的に commit 延期を指示した場合は、その例外を ledger / log に記録する。

## Stop Conditions

- context 削減により global lifecycle、gate、approval、remote boundary が発見できなくなる。
- `context-contract.toml` と `SKILL.md` / reference router が再び二重の source of truth になる。
- Worker Packet から acceptance criteria、verification、stop condition が欠落する。
- operation selection に追加 LLM router が必要になる。
- scheduler / runtime / delivery semantics を変更しないと実装できない。
- schema version 1 artifact の resume が不可能になる。
- `llm-wiki` の generic contract に system-specific adapter detail が混入する。
- implementation が肥大化したメイン planning session の context をそのまま引き継ぐ必要がある。
- remote write または破壊的操作が必要になる。

## Known Risks

- `workflow-contract.md` を deprecated shim にすると、古い agents が router reference を前提にしたまま動く可能性がある。
- token estimator は保守的近似であり、実 tokenizer と完全一致しない。
- `skill-architecture.toml` と context validator の責務を誤ると policy と metrics が再び一体化する。
- Worker Packet V2 の root 境界検証は worktree / allowed root の正規化が甘いと false positive / false negative を起こす。
- `resume-brief.meta.json` の source digest は runtime event rebuild と更新順序に依存するため、atomic write が必要になる可能性がある。

## 関連ページ

- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [Skill Repository Optimization V4 Issues](skill-repository-optimization-v4-issues.md)
- [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- [Loop Skill Architecture V3 Issues](loop-skill-architecture-v3-issues.md)
- [Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md)
- [Issue Implementation Loop Context Policy Spec](issue-implementation-loop-context-policy-spec.md)

## 出典

- [Skill Repository Optimization V4 Design](../sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [raw/sources/2026-06-26-skill-repository-optimization-v4-design.md](../../raw/sources/2026-06-26-skill-repository-optimization-v4-design.md)
- [skills/grill-to-pr-loop/context-contract.toml](../../../skills/grill-to-pr-loop/context-contract.toml)
- [skills/issue-implementation-loop/context-contract.toml](../../../skills/issue-implementation-loop/context-contract.toml)
- [scripts/validate_loop_skill_context.py](../../../scripts/validate_loop_skill_context.py)
- [skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json](../../../skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json)
- [skills/issue-implementation-loop/scripts/build_resume_brief.py](../../../skills/issue-implementation-loop/scripts/build_resume_brief.py)
