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

## 判断材料サマリ

4 件はいずれも、今回の Issue 意図適合や draft PR 作成を成立させるための blocker ではない。判断の軸は「この PR で scope を増やしてまで、将来の運用 drift をどこまで先取りするか」です。

| Candidate ID | 判断したい問い | 現在この PR でできていること | 今回取り込む効果 | 今回取り込むコスト / 影響 | coordinator 推奨 |
| --- | --- | --- | --- | --- | --- |
| `HC-LRG-002-001` | resume brief の pending 件数を runtime registry から自動算出すべきか | registry path と `Pending hardening decisions: N` を carry-forward する契約は reference にある。delivery validation は resume brief ではなく registry を読む。 | resume / status 時に pending 件数の手更新漏れを減らせる。 | `build_resume_brief.py` と resume tests の追加実装が必要。delivery correctness には直接効かない。 | `deferred_follow_up` |
| `HC-LRG-003-001` | capability preflight が worker packet v2 / `validate_worker_packet` routing まで検査すべきか | `validate_worker_packet` 自体の tests はあり、delivery preflight の candidate reporting は通っている。 | 将来 worker packet routing が壊れた時に、実行前 preflight で早く検出できる。 | `check_capabilities.py` の責務が広がる。fixture と routing contract の追加が必要。 | `deferred_follow_up` |
| `HC-LRG-003-002` | local-only completion report も pending / residual risk を validator で強制すべきか | remote delivery preflight は `pending_hardening_candidates` / `residual_risks` を出す。reference は local-only completion report にも記載を要求している。 | remote PR を作らない運用でも、未判断候補や残リスクの報告漏れを検出できる。 | completion report artifact / validator の責務定義が必要で、今回 PR の中心 scope より広い。 | `deferred_follow_up` |
| `HC-LRG-004-001` | acceptance criteria と `write_scope` の mismatch を dispatch / preflight で事前検出すべきか | 今回見つかった具体的 validator gap は修正済み。review cycle で mismatch を検出できた。 | 将来、必要な validator path が worker packet から漏れる問題を早めに止められる。 | acceptance criteria から必要 path を推定する設計が必要。単純な自動判定は false positive / false negative を出しやすい。 | `deferred_follow_up` |

## 候補別判断メモ

### `HC-LRG-002-001`: resume brief の pending 件数を動的算出する

- 現状: `runtime-state.md` / `context-compaction.md` は resume brief に `Pending hardening decisions: N` と registry path を出す契約を持つ。ただし、`build_resume_brief.py` が registry を直接読んで件数を算出する実装までは今回 scope に入れていない。
- 取り込む場合: `build_resume_brief.py` / `resume_brief.py` に candidate registry loader を追加し、`pending_decision` 件数と path を resume brief に出す regression を `test_resume_brief.py` に追加する。
- 延期した場合: resume brief の pending 件数が convention / 手動同期寄りになる。ただし final delivery validation は registry を直接読むため、ready-for-review / merge gate の correctness は落ちない。
- 今回入れる判断条件: 中断・再開時の resume brief を primary operational surface として使い、pending 件数の誤表示をこの PR で潰したい場合だけ current PR に取り込む。
- 推奨理由: 便利な運用 hardening だが、今回 PR の中心である review governance / delivery gate の correctness には直接必要ないため、後続送りが妥当。

### `HC-LRG-003-001`: `check_capabilities.py` に worker packet routing coverage を足す

- 現状: `check_capabilities.py` は input packet validation、repo / git、必要 skill、remote delivery capability を見る。worker packet v2 と `validate_worker_packet` の contract は別 tests で検証されている。
- 取り込む場合: `check_capabilities.py --input` が worker packet validator / template / schema の存在や代表 fixture routing まで確認するようにし、capability fixture test を追加する。
- 延期した場合: 将来、worker packet validator の routing が壊れても、capability preflight ではなく worker packet validation / tests 側で検出される。発見タイミングが少し遅くなる。
- 今回入れる判断条件: execution start 前の preflight を「worker packet routing まで含む総合診断」にしたい場合だけ current PR に取り込む。
- 推奨理由: `check_capabilities.py` の責務拡張であり、今回の candidate decision gate とは別の preflight hardening。後続 issue として扱う方が scope が明確。

### `HC-LRG-003-002`: local-only completion report validator に接続する

- 現状: `delivery.py` / `validate_delivery_plan.py` は draft final PR delivery で `pending_hardening_candidates`、`decision_gate_blockers`、`residual_risks` を出す。`remote-delivery.md` は local-only completion report でも同じ情報を出すべきだと記載している。
- 取り込む場合: local-only completion report の artifact shape を固定し、未判断 candidate と residual risk が含まれるかを validator / tests で強制する。
- 延期した場合: remote PR を作る flow では情報が出るが、local-only 完了報告では agent が記載を漏らす可能性が残る。
- 今回入れる判断条件: この PR で remote draft PR だけでなく local-only completion report の machine validation まで完了条件にしたい場合だけ current PR に取り込む。
- 推奨理由: completion report validator は独立した成果物設計を必要とし、今回 PR に入れると review governance から completion reporting の broader scope へ広がる。後続送りが妥当。

### `HC-LRG-004-001`: acceptance criteria と `write_scope` の mismatch preflight

- 現状: LRG-004 では、Execution Envelope に `review_policy.hardening_candidates` を持たせたため validator も同じ contract を拒否できる必要がある、という具体的 gap を review で検出し修正した。つまり今回の不整合そのものは解消済み。
- 取り込む場合: worker dispatch 前に、acceptance criteria が validator / schema / template / tests 変更を要求しているのに `write_scope` が該当 path を含まない場合を検出する preflight を追加する。
- 延期した場合: 同種の packet mismatch は、今回と同じく review cycle で見つかる可能性が高い。dispatch 前には止まらないため、1 cycle 分の手戻りは残る。
- 今回入れる判断条件: 「acceptance criteria から必要 write scope を推定する」ルールをどこまで自動化するかまで、この PR で決めたい場合だけ current PR に取り込む。
- 推奨理由: 自動判定は自然言語 AC と path scope の対応を扱うため、素朴に入れると誤検出しやすい。今回 PR では具体 gap を直し、汎用 preflight は後続で設計する方が堅い。

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
