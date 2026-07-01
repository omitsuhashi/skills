# Loop Review Governance Hardening Candidate Decisions

## 状態

Human Decision Gate pending。Draft final PR 作成後に統合 diff を見て一括判断する。

このファイルは `loop-review-governance` の draft final PR 上で、人間が一括判断する必要がある `hardening_candidate` を一覧化するための decision artifact です。

## Source

- Runtime registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`
- Runtime registry の `candidates[]` に `decision: "pending_decision"` として 4 件が記録されている。
- これらは Issue 意図適合の blocker ではなく、承認済み scope を越える堅牢化候補である。

## 保存場所と読み方

人間が判断する入口はこの Markdown file です。JSON は runtime / validator が読む machine-readable registry として残し、判断時に直接読む前提にはしない。

- 人間向け判断 file: `knowledge/wiki/syntheses/loop-review-governance-hardening-decisions.md`
- 集約 ledger: `knowledge/wiki/syntheses/loop-review-governance-issues.md` の `Pending Hardening Decisions`
- machine-readable registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`
- PR 上の確認面: draft PR [#27](https://github.com/omitsuhashi/skills/pull/27) の本文

`4 件` は runtime registry の `candidates[]` にある 4 record を指す。PR 判断では、この file の `判断対象` と `出典 / 指している箇所` を見て一括で `deferred_follow_up` などを選ぶ。

## 出典 / 指している箇所

| Candidate ID | 保存されている場所 | どこで出た指摘か | 何を指しているか |
| --- | --- | --- | --- |
| `HC-LRG-002-001` | runtime registry の `candidates[0]`、この file の `判断対象` table、issue ledger の `Pending Hardening Decisions` | `reviews/LRG-002/review-cycle-1.md` の Hardening Candidates。LRG-005 review でも pending decision として再確認。 | resume brief 生成が runtime registry を直接読んで `Pending hardening decisions: N` を出すかどうか。対象候補は `skills/issue-implementation-loop/scripts/build_resume_brief.py`、`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/resume_brief.py`、`skills/issue-implementation-loop/tests/test_resume_brief.py`。 |
| `HC-LRG-003-001` | runtime registry の `candidates[1]`、この file の `判断対象` table、issue ledger の `Pending Hardening Decisions` | `reviews/LRG-003/review-cycle-1.md` / `review-cycle-2.md` で既存 pending candidate として扱われた。primary details は runtime registry。 | `check_capabilities.py` に worker packet v2 / `validate_worker_packet` routing の fixture coverage を足すかどうか。対象候補は `skills/issue-implementation-loop/scripts/check_capabilities.py`、worker packet validation 周辺、`skills/issue-implementation-loop/tests`。 |
| `HC-LRG-003-002` | runtime registry の `candidates[2]`、この file の `判断対象` table、issue ledger の `Pending Hardening Decisions` | `reviews/LRG-003/review-cycle-1.md` / `review-cycle-2.md` で既存 pending candidate として扱われた。primary details は runtime registry。 | `pending_hardening_candidates` / `residual_risks` output を、将来の `local_only` completion report validator に接続するかどうか。現時点の実装箇所は `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/delivery.py` と `skills/issue-implementation-loop/scripts/validate_delivery_plan.py`、契約箇所は `skills/issue-implementation-loop/references/remote-delivery.md`。 |
| `HC-LRG-004-001` | runtime registry の `candidates[3]`、この file の `判断対象` table、issue ledger の `Pending Hardening Decisions` | `reviews/LRG-004/review-cycle-1.md` の Hardening Candidates。`reviews/LRG-004/review-cycle-2.md` で blocker ではなく pending decision と再確認。 | acceptance criteria が validator 変更を要求しているのに worker packet の `write_scope` が validator path を含まない mismatch を dispatch / preflight で検出するかどうか。今回の具体的 validator gap は修正済み。対象候補は `skills/grill-to-pr-loop/references/execution-handoff.md`、`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/validation/execution_envelope.py`、`skills/issue-implementation-loop/tests/test_validation.py`、将来の dispatch / preflight check。 |

## 判断方法

各 candidate について、`人間判断` を次のいずれかに更新する。

- `approved_for_current_pr`: current PR に取り込む。追加 Issue / envelope revision / review gate が必要。
- `deferred_follow_up`: current PR には入れず、後続候補として残す。
- `declined`: 採用しない。理由を残す。
- `risk_accepted`: risk を認識したうえで delivery 継続を許可する。通常は `safety_escalation` 用。

`pending_decision` が残っていても draft final PR 作成には進める。ready-for-review、merge、または candidate 取り込み実装へ進む前に、全 candidate の一括判断を行う。

## 判断対象

| Candidate ID | Source issue | 候補 summary | 延期した場合の risk | 想定 scope | 推奨 | 人間判断 | 判断理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `HC-LRG-002-001` | `LRG-002` | `build_resume_brief.py` が candidate registry を動的に読み、runtime data から `Pending hardening decisions: N` を出すようにする。 | 低。LRG-002 の reference / schema contract は満たしているが、resume output は script enforcement ではなく convention に留まる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-003-001` | `LRG-003` | `check_capabilities.py` に worker packet v2 と `validate_worker_packet` routing の coverage を追加する。 | 低。delivery preflight の acceptance は満たしているが、将来 worker packet routing が drift する可能性が残る。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-003-002` | `LRG-003` | `pending_hardening_candidates` / `residual_risks` helper output を将来の `local_only` completion report validator に接続する。 | 低。remote delivery preflight は enforced だが、`local_only` completion report validation は documented reporting contract に留まる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests`, `skills/issue-implementation-loop/references` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-004-001` | `LRG-004` | acceptance criteria が validator 変更を要求しているのに write scope が validator path を含まない mismatch を dispatch / preflight で検出する。 | 低。LRG-004 の具体的 validator gap は修正済みだが、将来 packet で同じ mismatch が再発しうる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests`, `skills/grill-to-pr-loop/references` | `deferred_follow_up` | `pending_decision` | 未判断 |

## PR / Ready / Merge 条件

draft final PR は、上の 4 件が `pending_decision` のままでも作成できる。PR body とこのファイルに同じ判断対象を載せ、統合 diff を見たうえで一括判断する。

全件 `deferred_follow_up` を選ぶ場合は、current PR の実装 scope は増やさず、completion report に residual hardening candidate として残す。

いずれかを `approved_for_current_pr` にする場合は、current PR scope が増えるため、amendment issue を追加して通常の実装レビューを通す。

ready-for-review、merge、risk acceptance、または candidate 取り込み実装へ進む前には、4 件すべてについて `人間判断` が `pending_decision` 以外になっている必要がある。

## 現時点の coordinator 推奨

4 件とも risk は低く、Issue の受け入れ条件は満たしているため、current PR では `deferred_follow_up` とするのが最小 scope の推奨。
