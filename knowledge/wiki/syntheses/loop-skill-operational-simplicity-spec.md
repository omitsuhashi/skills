# Loop Skill 運用単純化仕様

## 状態

Spec Gate / Issue Gate / Execution Plan Gate 承認済み。LSOS-001 から LSOS-004 の実装は完了済み。ユーザー承認により branch push と draft PR #22 作成は実施済み。追加のリモート書き込み、PR の ready 化、merge は未承認。

## 問題設定

`grill-to-pr-loop` と `issue-implementation-loop` は、長いリポジトリ変更を安全に進めるために、context contract、worker packet、resume brief、runtime state、review gate を備えた。ただし、現状は次の 3 つの運用摩擦が残っている。

- 小さい変更にも loop 系を使うべきか判断しづらく、適用範囲が広く見えすぎる。
- `issue-implementation-loop` の coordinator / worker / reviewer / runtime state の関係が、読む前に把握しづらい。
- `report_skill_context.py` / `validate_skill_context.py` は read-set の context budget を測るが、人間が感じる workflow complexity は直接測っていない。

この仕様は、既存のユーザー向け skill 数と worker-only execution policy を維持したまま、loop 系の露出複雑性を下げる。

## Epic ID

`loop-skill-operational-simplicity`

## 現在の前提

- `git status --short`: clean。
- 計画前提チェック: `python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase planning` は通過済み。
- GitHub remote は存在する。初期計画時点ではリモート書き込み未承認として扱った。
- `skill-architecture.toml` は repository-change-loop family のユーザー向け skill を `grill-to-pr-loop` と `issue-implementation-loop` の 2 つに固定している。
- `scripts/validate_skill_architecture.py --all` と `scripts/validate_skill_context.py --all` は現在の checkout で通る。
- `scripts/report_skill_context.py --all` は read-set ごとの推定 token 数、file 数、headroom を返すが、gate 数、runtime artifact 数、worker-context requirement、human wait / review / delivery の有無を集約した実行者向け complexity を返さない。

## 採用した判断

- 新しいユーザー向け skill は追加しない。
- scheduler、runtime-state、review-gate、worker-contract、remote-delivery などの内部機構は独立 skill にしない。
- `grill-to-pr-loop` は計画 / 構成 skill のままにし、実装 worker にはしない。
- `issue-implementation-loop` は承認済み packet から `PR_READY` までを扱う実行 coordinator のままにする。
- 小さい単発修正、単一ファイルの明確な修正、既存 issue 1 件の軽微な docs 修正には、原則として loop 系を使わない適用基準を明文化する。
- 役割境界モデルは default read-set を大きくしない形で追加する。入口には短い要約を置き、詳細は実行者向け reference または durable synthesis として読む。
- workflow complexity 指標は context 指標と別軸にする。context budget が健全でも、gate / artifact / worker / review / delivery の組み合わせで運用リスクを警告できるようにする。
- 実装ループ中のリモート書き込み方針は `local_only` とする。PR 作成は実装完了後の別承認で扱う。
- 生成する仕様書 / PRD / Issue 台帳 / human-facing report / packet の title、見出し、label、status、本文は日本語ベースにする。安定 ID、path、command、code symbol、schema key、API 名、branch 名、error message、外部 issue / PR 参照は互換性のため英語のまま維持する。

## 非目標

- 新しい skill の追加。
- `issue-implementation-loop` の scheduler semantics、runtime schema、delivery policy の変更。
- `context-contract.toml` を workflow complexity の唯一の正本にすること。
- 実装ループ内での GitHub issue mirror、push、PR 作成、merge、final PR merge。
- 外部 dependency の追加。
- 既存 V4 成果の再実装。

## Issue 分解方針

Spec Gate 承認後に、日本語 local-first ledger として次の blocker order で issue 化する。

1. **LSOS-001: loop 系の適用基準を明文化する**
   - `grill-to-pr-loop` と `issue-implementation-loop` の入口に、使う条件 / 使わない条件 / stop 条件を短く追加する。
   - 適用基準は既存 `skill-architecture.toml` の 2 skill policy と矛盾させない。
   - 小さい単発修正は通常 skill / 直接実装に逃がす。

2. **LSOS-002: loop 系の役割境界モデルを 1 ページ化する**
   - coordinator、worker、reviewer、runtime state、local ledger、remote delivery の関係を 1 ページで説明する。
   - default read-set は必要以上に増やさない。
   - `issue-implementation-loop` の実装者が最初に読むべき役割境界を明確にする。

3. **LSOS-003: workflow complexity レポートを追加する**
   - `scripts/report_skill_context.py --all --json` に、context metrics とは別の `workflow_complexity` summary を追加する。
   - 集計対象は gate 数、operation 数、runtime artifact / schema / template / script の数、worker-context requirement、review cycle、human wait、remote delivery policy などの実行者向け complexity とする。
   - text report では warning だけを簡潔に表示し、JSON では内訳を返す。
   - `validate_skill_context.py` は read-set budget validator のままにし、complexity は report 側の advisory metric とする。

4. **LSOS-004: regression tests と wiki ledger を更新する**
   - 適用基準、役割境界モデルの discoverability、workflow complexity JSON の shape を tests で固定する。
   - `knowledge/index.md` と `knowledge/log.md` に仕様、issue ledger、実装 evidence を追加する。

## 受け入れ条件

- `grill-to-pr-loop` は、使うべきケースと使わないケースを 1 screen 相当で説明している。
- `issue-implementation-loop` は、承認済み packet 前提、worker context 必須、coordinator 実装禁止の適用条件を入口で確認できる。
- loop 系の役割境界モデルは coordinator / worker / reviewer / runtime state / ledger / remote delivery の責務境界を 1 ページで説明している。
- 役割境界モデルの追加により、`validate_skill_context.py --all` の budget validation が失敗しない。
- `report_skill_context.py --all --json` は `workflow_complexity` summary を返す。
- `workflow_complexity` は少なくとも operation count、gate count、runtime artifact count、worker-context flag、review-cycle flag、remote-delivery flag を含む。
- text report は context metrics を読みづらくしない。complexity warning は必要な場合だけ短く表示する。
- `validate_skill_architecture.py --all` は引き続きユーザー向け skill 2 件と forbidden standalone skill policy を検証する。
- 新しい独立 skill は追加されない。
- 実装ループ内では remote write を行わない。
- 仕様書 / PRD / Issue 台帳 / human-facing report の生成・更新規約は日本語ベースを明示し、サンプル packet の user-facing string も日本語例を使う。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
rg -n "使わない|worker context|workflow_complexity|coordinator|runtime state" skills scripts knowledge/wiki/syntheses
git diff --check
```

## リモート書き込み方針

実装ループ中は `local_only`。

GitHub issue mirror と merge は未承認のため実行しない。2026-06-29 のユーザー承認により、branch push と draft PR #22 作成は実施済み。final PR merge は常に human-only。

## 人間レビューゲート

- **Spec Gate**: この仕様の Epic ID、採用した判断、非目標、受け入れ条件、検証、停止条件を承認する。
- **Issue Gate**: 日本語 local-first issue ledger の粒度、blocker graph、依存順、acceptance criteria を承認する。
- **Execution Plan Gate**: normalized input packet、write scopes、dependency graph、fallback policy、remote policy を承認する。
- **Implementation Review Gate**: 各 issue completion / blocker release / PR_READY 前に issue-scoped implementation review を実施する。
- **Remote Gate**: 外部 write が必要になった場合だけ exact action set を提示し、明示承認を待つ。

Spec Gate / Issue Gate / Execution Plan Gate は承認後に、承認済み local artifacts と `knowledge/log.md` 更新を commit してから次フェーズへ進む。ユーザーが明示的に commit 延期を指示した場合は、その例外を ledger / log に記録する。

## 停止条件

- 適用基準の追加により、既存の gate、approval、remote boundary、worker-only policy が弱まる。
- 役割境界モデルを default read-set に入れた結果、context budget が悪化する。
- workflow complexity metric が hard validator になり、既存 workflow を advisory なしに止める。
- `context-contract.toml` と complexity metric が二重の read-set source of truth になる。
- scheduler / runtime / delivery semantics を変更しないと実装できない。
- remote write または破壊的操作が必要になる。

## 既知のリスク

- 適用基準を強くしすぎると、ユーザーが明示的に loop 系を使いたいケースまで止める可能性がある。
- 役割境界モデルを短くしすぎると、実行時に必要な停止条件まで省略される可能性がある。
- workflow complexity score は heuristic なので、最初は pass/fail ではなく advisory として扱う必要がある。
- 既存 `report_skill_context.py` の text output に情報を足しすぎると、context budget report としての読みやすさが落ちる。

## 関連ページ

- [Loop Skill Context Optimization Spec](loop-skill-context-optimization-spec.md)
- [Loop Skill Architecture V3 Spec](loop-skill-architecture-v3-spec.md)
- [Skill Repository Optimization V4 Spec](skill-repository-optimization-v4-spec.md)
- [Skill Repository Optimization V4 Context Baseline](skill-repository-optimization-v4-context-baseline.json)

## 出典

- [skills/grill-to-pr-loop/SKILL.md](../../../skills/grill-to-pr-loop/SKILL.md)
- [skills/issue-implementation-loop/SKILL.md](../../../skills/issue-implementation-loop/SKILL.md)
- [skills/grill-to-pr-loop/context-contract.toml](../../../skills/grill-to-pr-loop/context-contract.toml)
- [skills/issue-implementation-loop/context-contract.toml](../../../skills/issue-implementation-loop/context-contract.toml)
- [skill-architecture.toml](../../../skill-architecture.toml)
- [scripts/report_skill_context.py](../../../scripts/report_skill_context.py)
- [scripts/validate_skill_context.py](../../../scripts/validate_skill_context.py)
