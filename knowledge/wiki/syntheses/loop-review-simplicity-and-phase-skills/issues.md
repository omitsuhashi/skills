# Loop Review Simplicity And Phase Skills Issue 台帳

## 状態

Issue Gate 再承認済み。amended spec の phase-owned / task-triggered skill boundary に reconcile 済みであり、local ledger が canonical、GitHub Issue mirror は未作成である。

## Issue 一覧

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loop-review-simplicity-and-phase-skills | LRSP-001 | material review と phase-scoped skill contract を実装する | 承認済み | 実行可能 | なし | なし | 未作成 | 未実施 | 未作成 |

## Blocker graph

```text
LRSP-001
```

- cycle: なし。
- runnable: `LRSP-001`。
- blocked: なし。
- execution order: `LRSP-001` のみ。

## LRSP-001: material review と phase-scoped skill contract を実装する

### 目的

両 loop skill の review を material finding に限定し、operation ごとの current actor / dispatch actor が常に読む phase-owned workflow skill を schema v3 contract として固定する。task-triggered skill は該当 phase で on-demand に読み、新しい loader、worker packet field、review runtime、finding schema は作らない。

### 仕様

- [Loop Review Simplicity And Phase Skills 仕様](spec.md)
- Epic ID: `loop-review-simplicity-and-phase-skills`
- approved spec SHA-256: `2e86698433cc4a95719bffc8a2f5a6e76aa3fea5b71f743ec8f71ef39edc4719`
- Spec Gate commit: `9f6dba0`

### Write scope

- `path:skills/grill-to-pr-loop`
- `path:skills/issue-implementation-loop`
- `path:scripts/skill_context`
- `path:scripts/inspect_skill_context.py`
- `path:scripts/report_skill_context.py`
- `path:scripts/test_report_skill_context.py`
- `path:knowledge/wiki/syntheses/skill-repository-optimization-v4-context-baseline.json`

planning coordinator は本台帳、`implementation-plan.md`、`input-packet.json`、`knowledge/index.md`、`knowledge/log.md` を所有し、implementation worker の write scope には含めない。

### 実装契約

1. skill edit 前に、現行 review / context contract の baseline failure を pressure scenario で観測する。
2. schema v3 の `skills` / `dispatch_skills` validation と phase mapping の failing test を先に追加し、expected RED を確認する。
3. shared context parser と `issue-implementation-loop` runtime selector を同じ schema v3 semantics にする。
4. 両 loop contract の全 operation に phase-owned `skills` / `dispatch_skills` を明示し、`final-review` operation を追加する。
5. inspector / report は supplemental skill boundary を reference read-set と分けて表示する。
6. spec self-review、Issue implementation review、final spec alignment review を「要件達成、material simplicity、material risk」の順に揃える。
7. reviewer は `Critical` / `Important` だけを報告し、`Minor` / nit / 好み / 任意改善を finding にしない。
8. material simplicity gap は具体的な simpler alternative がある場合だけ `intent_gap` / `Important` とする。
9. existing schema v1 / v2、mechanical validation、hardening / safety / classification boundary を維持する。
10. task-triggered `writing-skills` は本 skill-edit task の implementation phase で on-demand に使用し、generic loop contractへ固定しない。
11. fresh full verification と同一 pressure scenario の GREEN evaluation を残す。

### 受け入れ条件

- [ ] schema v3 の両 loop context contract は全 operation に `skills` / `dispatch_skills` を持つ。
- [ ] `grill-with-docs`、`tdd`、`requesting-code-review` は approved phase mapping 以外に宣言されない。
- [ ] inspector は current operation の reference read-set、`skills`、`dispatch_skills` を同時に表示する。
- [ ] report は supplemental skill 名を repo-local reference budget と分けて返す。
- [ ] validator は schema v3 の field 欠落、不正型、空文字、同一 field 内重複を拒否する。
- [ ] schema v1 / v2 と `llm-wiki` context contract の既存挙動は維持される。
- [ ] planning / execution coordinator は future operation または dispatch 先の phase-owned workflow skill を自分の instruction context に読まない契約を持つ。
- [ ] task-triggered skill は該当 phase だけで on-demand に読み、universal allowlist、worker packet field、generic loaderを追加しない。
- [ ] spec self-review、Issue implementation review、final spec alignment review は要件達成、material simplicity、material risk の 3 観点を持つ。
- [ ] routine review は `Minor` / nit / 好み / 任意改善を finding として報告しない。
- [ ] material simplicity finding は同じ要件を満たす具体的な simpler alternative を示し、`intent_gap` / `Important` として blocking になる。
- [ ] future-only hardening、`safety_escalation`、`classification_needed` の既存 boundary は維持される。
- [ ] skill authoring TDD の RED / GREEN evidence と fresh verification evidence が記録される。

### 非目標

- 新しい standalone skill、generic skill loader、review runtime、finding schema。
- task-triggered skill の universal allowlist、worker packet field、install inventory validator。
- Gate、worker/runtime artifact、review/fix cycle の追加。
- loop family 以外への schema v3 field 必須化。
- future-only hardening の routine review への再導入。
- mechanical validator、schema、digest、test の検出範囲縮小。
- GitHub Issue mirror、issue PR、ready-for-review、merge、release、live install。

### 検証

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
python3 scripts/validate_skill_architecture.py --all
python3 scripts/validate_skill_context.py --all
python3 scripts/report_skill_context.py --all --json
python3 scripts/validate_dual_host_compatibility.py --skill skills/grill-to-pr-loop
python3 scripts/validate_dual_host_compatibility.py --skill skills/issue-implementation-loop
git diff --check
```

変更した両 skill に対し、Execution Plan Gate で実在 command を確認した skill-creator quick validator を実行する。

### Review contract

- committed `BASE_SHA..HEAD_SHA` を review する。
- verdict を先頭に置く。
- finding は evidence、material impact、required fix を持つ。
- material simplicity finding は同じ要件を満たす具体的な simpler alternative を追加で持つ。
- `Critical` / `Important` がなければ、nit を補充せず approved とする。
- current PR scope 外の future-only hardening を列挙しない。
- review / fix は既存どおり最大 2 cycle。

### Remote policy

`per_action`。local `PR_READY` 後に branch push と draft PR 作成だけを exact Remote Gate に提示する。GitHub Issue mirror、issue PR、ready-for-review、merge、release、live install は行わない。

### 停止条件

- approved spec binding が変わる。
- write scope が別 worktree の変更と重なる。
- shared parser と runtime selector の schema semantics が一致しない。
- required phase skill が entry 時に見つからず、approved equivalent もない。
- task-triggered skill を current phase より前に読む、または該当 task で必須なのに読まない。
- baseline RED または post-change GREEN を fresh context で確認できない。
- existing schema v1 / v2、context baseline、dual-host compatibility が壊れる。
- concrete simpler alternative を示せない指摘を blocking finding にしようとする。
- 未承認 remote write または destructive action が必要になる。

## 関連ページ

- [Loop Review Simplicity And Phase Skills 仕様](spec.md)
- [Loop Review Governance Spec](../loop-review-governance-spec.md)
- [Loop Skill 運用単純化仕様](../loop-skill-operational-simplicity-spec.md)

## 出典

- `../../../../skills/grill-to-pr-loop/references/local-issue-ledger.md`
- `../../../../skills/grill-to-pr-loop/references/execution-handoff.md`
- `../../../../skills/issue-implementation-loop/references/review-gate.md`
