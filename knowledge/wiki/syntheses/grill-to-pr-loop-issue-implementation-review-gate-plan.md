# Grill To PR Loop Issue Implementation Review Gate Plan

## 目的

`skills/grill-to-pr-loop` に、各 issue 実装が「issue の内容どおり正しく、理想的に実装されているか」を確認する実装レビューゲートを追加する。これは PR 作成後のレビュー監視ではなく、local issue completion、blocker release、PR 作成の前に必ず通す issue 単位の品質ゲートとして扱う。

## Grill セッションの結論

- レビュー対象は PR 全体ではなく、承認済み local issue とその acceptance criteria、spec / PRD、write scope、verification evidence に対する実装差分。
- 既存の `Goal Loop Definition` にある `Request code review or perform a review pass` は曖昧すぎる。必須の `Issue Implementation Review Gate` として独立定義する。
- 既定のレビュー手段は `superpowers:requesting-code-review`。未導入または subagent を起動できない環境では、黙って省略せず、同じ review packet で手動レビューへ切り替えるか、導入して続行するかをユーザーに確認する。
- `requesting-code-review` の template は `BASE_SHA` / `HEAD_SHA` 前提なので、issue worker は final verification 後に scoped local commit を作り、その commit range をレビューさせる。指摘対応後は amend または追加 commit を作り、同じ base から新しい head で再レビューする。
- Critical / Important 指摘は修正するか、人間が明示的に risk acceptance するまで issue 完了扱いにしない。Minor は ledger に残して completion 可能。
- parallel wave では各 worker が自分の worktree / branch / issue range だけをレビュー依頼に渡し、coordinator-owned ledger の完了更新と blocker release は親 session がレビュー通過後に行う。

## 追加する概念

### Issue Implementation Review Gate

各 issue worker の完了条件に次を追加する。

1. issue-owned docs / progress 更新後に fresh final verification を実行する。
2. issue scope だけを含む local commit を作成する。
3. `BASE_SHA` は worktree map に記録済みの base commit、`HEAD_SHA` は issue commit 後の head とする。
4. `superpowers:requesting-code-review` に次の意図を明示して依頼する。

```text
<local issue id> の実装について、issue の内容が実装が正しく、理想的に実装されているかレビューしてください。
```

5. review packet には local issue, remote issue がある場合の URL, spec / PRD path, acceptance criteria, non-goals, write scope, verification results, base/head SHA を含める。
6. Critical / Important を修正し、targeted verification と fresh final verification を再実行する。
7. 必要なら再レビューする。
8. reviewer verdict、未対応 Minor、risk acceptance、final verification result を coordinator へ報告する。
9. coordinator が local ledger に review result と commit SHA を記録し、初めて issue 完了 / blocker release / PR readiness に進む。

### Ledger Fields

local ledger には issue draft review の `レビュー状態` と混同しない別 field を追加する。

- `実装レビュー`: `未実施`, `依頼済み`, `指摘対応中`, `承認済み`, `手動レビュー済み`, `差し戻し`
- `レビュー範囲`: `<base sha>..<head sha>` または手動レビュー対象の diff
- `レビュー結果`: reviewer verdict、Critical / Important / Minor summary、risk acceptance の有無

## 実装計画

1. `skills/grill-to-pr-loop/SKILL.md` を更新する。
   - sub-skill list に `superpowers:requesting-code-review` を「issue 実装レビュー」の推奨 sub-skill として追加する。
   - Required Operating Rules に「各 issue completion / blocker release / PR creation 前に実装レビューゲートを通す」を追加する。
   - State Machine の Parallel Goal Loop Scheduler と PR Review の間に review gate を明示する。
   - Goal Prompt Contract に review packet、base/head SHA、レビュー依頼文、severity handling、ledger update fields を追加する。
   - Stop Conditions に「reviewer capability がなく、ユーザーが手動 fallback も導入も選んでいない」「Critical / Important が未処理」を追加する。
   - Completion Report に issue 実装レビュー結果を追加する。

2. `skills/grill-to-pr-loop/references/workflow-contract.md` を更新する。
   - Sub-Skill Contract に `requesting-code-review` を追加する。
   - Local Ledger Update Invariant に review result、review range、risk acceptance を追加する。
   - Local issue template と worktree map に `実装レビュー` 関連 field を追加する。
   - `Issue Implementation Review Gate` section を新設し、review packet、SHA range、severity policy、manual fallback、parallel wave での扱いを定義する。
   - `Goal Loop Definition` は commit と review の順序を `fresh verification -> scoped local commit -> review -> fixes/re-review -> coordinator report` に変更する。
   - `PR Review Definition` は「issue implementation review gate 通過後にのみ PR 作成へ進む」と明記する。
   - Common Mistakes に「PR review を issue 実装レビューの代替にする」「Important 指摘を残して blocker を release する」を追加する。

3. `skills/grill-to-pr-loop/scripts/check_prereqs.py` を更新する。
   - optional skill に `requesting-code-review` を追加する。
   - 可能なら `~/.codex/plugins/cache/**/skills/<skill>/SKILL.md` も探索対象に加え、plugin 提供 skill を検出できるようにする。
   - JSON output に reviewer capability の有無が出るようにする。
   - required skill にはしない。未検出時の runtime behavior は skill 本文の stop/fallback rule で扱う。

4. `skills/grill-to-pr-loop/agents/openai.yaml` を確認する。
   - `default_prompt` が古くなる場合だけ、issue implementation review gate を含むように更新する。
   - display metadata の更新は SKILL.md との整合に必要な最小限に留める。

## Skill TDD / 圧力シナリオ

実装フェーズでは、skill 文書の RED/GREEN として少なくとも次を使う。

- Scenario A: worker が tests passing だけで local issue を完了扱いにしようとする。期待結果: review gate 未通過として止まる。
- Scenario B: worker が PR 作成後の review monitoring を issue 実装レビューの代替にする。期待結果: PR 前に issue implementation review が必要だと判断する。
- Scenario C: reviewer が Important finding を返したが、worker が「後で直す」と言って blocker を release しようとする。期待結果: 修正または人間の risk acceptance まで completion しない。
- Scenario D: `requesting-code-review` が見つからない。期待結果: 手動 fallback または skill 導入の確認で止まり、黙って省略しない。

可能なら subagent forward-test を 1 回行う。時間や環境制約がある場合は、上記 scenario を checklist として文書差分レビューに使う。

## 受け入れ条件

- `grill-to-pr-loop` の本体と workflow contract が、issue completion / blocker release / PR creation 前の実装レビューゲートを明示している。
- `superpowers:requesting-code-review` を使う場合の review packet が、local issue、spec、acceptance criteria、write scope、verification results、base/head SHA を含む。
- Critical / Important finding の扱いが明確で、未対応のまま完了扱いにできない。
- PR review と issue implementation review の責務が分離されている。
- local ledger に実装レビュー状態、レビュー範囲、レビュー結果を記録する契約がある。
- `check_prereqs.py --json` で reviewer skill の検出結果を確認できる。
- remote issue creation、push、PR creation の明示承認 gate は既存どおり維持される。

## 検証コマンド

```bash
python3 -m py_compile skills/grill-to-pr-loop/scripts/check_prereqs.py
python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --json
rg -n "requesting-code-review|Issue Implementation Review Gate|実装レビュー|レビュー範囲|レビュー結果" skills/grill-to-pr-loop
git diff -- skills/grill-to-pr-loop/SKILL.md skills/grill-to-pr-loop/references/workflow-contract.md skills/grill-to-pr-loop/scripts/check_prereqs.py skills/grill-to-pr-loop/agents/openai.yaml
```

forward-test を行う場合の prompt は次を基本にする。

```text
Use $grill-to-pr-loop at /Users/omitsuhashi/repos/omitsuhashi/skills/skills/grill-to-pr-loop to coordinate a completed local issue implementation. The worker has run tests and wants to mark the issue complete and release blockers. Decide what must happen before completion.
```

## リスクと未確定事項

- `requesting-code-review` を hard required にすると、superpowers plugin がない環境で `grill-to-pr-loop` 全体が使いにくくなる。計画では optional detection + runtime stop/fallback にする。
- local commit を review 前に作る設計へ変えるため、既存の「review 後に commit」という読みに慣れた利用者には順序変更が見える。理由は `requesting-code-review` template が SHA range 前提だからで、remote write は発生しない。
- subagent forward-test は環境と時間に依存する。実行できない場合でも、圧力シナリオを acceptance checklist として残す。

## 関連ページ

- [LLM Wiki Draft Review And Canonicalize Goal Spec](llm-wiki-draft-review-and-canonicalize-goal-spec.md) は、skill 更新を Goal contract 化する既存例として参照する。

## 出典

- `../../../skills/grill-to-pr-loop/SKILL.md`
- `../../../skills/grill-to-pr-loop/references/workflow-contract.md`
- `../../../skills/grill-to-pr-loop/scripts/check_prereqs.py`
- `/Users/omitsuhashi/.codex/plugins/cache/openai-curated/superpowers/202e9242/skills/requesting-code-review/SKILL.md`
- `/Users/omitsuhashi/.codex/plugins/cache/openai-curated/superpowers/202e9242/skills/requesting-code-review/code-reviewer.md`
- `/Users/omitsuhashi/.codex/plugins/cache/openai-curated/superpowers/202e9242/skills/writing-skills/SKILL.md`
