# Loop Review Governance Hardening Candidate Decisions

## 状態

Human Decision Gate pending。

このファイルは `loop-review-governance` の final PR 作成前に、人間が判断する必要がある `hardening_candidate` を一覧化するための decision artifact です。

## Source

- Runtime registry: `/Users/omitsuhashi/repos/omitsuhashi/skills/.git/agent-runs/issue-implementation-loop/loop-review-governance/decisions/hardening-candidates.json`
- Runtime registry の `candidates[]` に `decision: "pending_decision"` として 4 件が記録されている。
- これらは Issue 意図適合の blocker ではなく、承認済み scope を越える堅牢化候補である。

## 判断方法

各 candidate について、`人間判断` を次のいずれかに更新する。

- `approved_for_current_pr`: current PR に取り込む。追加 Issue / envelope revision / review gate が必要。
- `deferred_follow_up`: current PR には入れず、後続候補として残す。
- `declined`: 採用しない。理由を残す。
- `risk_accepted`: risk を認識したうえで delivery 継続を許可する。通常は `safety_escalation` 用。

`pending_decision` が残っている間は、final PR 作成に進まない。

## 判断対象

| Candidate ID | Source issue | 候補 summary | 延期した場合の risk | 想定 scope | 推奨 | 人間判断 | 判断理由 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `HC-LRG-002-001` | `LRG-002` | `build_resume_brief.py` が candidate registry を動的に読み、runtime data から `Pending hardening decisions: N` を出すようにする。 | 低。LRG-002 の reference / schema contract は満たしているが、resume output は script enforcement ではなく convention に留まる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-003-001` | `LRG-003` | `check_capabilities.py` に worker packet v2 と `validate_worker_packet` routing の coverage を追加する。 | 低。delivery preflight の acceptance は満たしているが、将来 worker packet routing が drift する可能性が残る。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-003-002` | `LRG-003` | `pending_hardening_candidates` / `residual_risks` helper output を将来の `local_only` completion report validator に接続する。 | 低。remote delivery preflight は enforced だが、`local_only` completion report validation は documented reporting contract に留まる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests`, `skills/issue-implementation-loop/references` | `deferred_follow_up` | `pending_decision` | 未判断 |
| `HC-LRG-004-001` | `LRG-004` | acceptance criteria が validator 変更を要求しているのに write scope が validator path を含まない mismatch を dispatch / preflight で検出する。 | 低。LRG-004 の具体的 validator gap は修正済みだが、将来 packet で同じ mismatch が再発しうる。 | `skills/issue-implementation-loop/scripts`, `skills/issue-implementation-loop/tests`, `skills/grill-to-pr-loop/references` | `deferred_follow_up` | `pending_decision` | 未判断 |

## PR 作成条件

final PR を作るには、上の 4 件すべてについて `人間判断` が `pending_decision` 以外になっている必要がある。

全件 `deferred_follow_up` を選ぶ場合は、current PR の実装 scope は増やさず、completion report に residual hardening candidate として残す。

いずれかを `approved_for_current_pr` にする場合は、current PR scope が増えるため、amendment issue を追加して通常の実装レビューを通す。

## 現時点の coordinator 推奨

4 件とも risk は低く、Issue の受け入れ条件は満たしているため、current PR では `deferred_follow_up` とするのが最小 scope の推奨。
