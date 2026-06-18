# 実装進捗台帳

この page は、複数の implementation slice / phase / MVP を横断して「何が終わり、何が残っているか」を発見するための durable synthesis です。個別の spec、implementation plan、PROGRESS note、issue tracker を置き換えません。各 slice の状態、残 scope、証跡、次回 review 条件へリンクする discovery surface として使います。

保存先は `wiki/syntheses/<topic>-implementation-progress-ledger.md` を基本にします。active canonical page として `index.md` の Active Page Catalog から発見できるようにし、更新したら `log.md` に lifecycle entry を残します。validator、scheduler、Dataview、Obsidian plugin、issue tracker 連携は任意です。

## 運用ルール

- `verified` には、test、diff、release note、review、manual verification などの証跡 link が必要。
- `deferred` / `blocked` には、理由と `Review after` または解除条件が必要。
- `Remaining scope` が空でない限り、Area 全体を complete と呼ばない。
- ledger は task runner ではない。実行順、担当割当、細かい TODO は個別 plan / issue / progress note に残し、ここからリンクする。
- 行を更新するときは、古い判断を消すだけでなく、必要なら evidence や next trigger に履歴へ辿れる link を残す。

## Status Values

- `planned`: 着手前。scope と入口は見えている。
- `in-progress`: 実装中。landed scope と remaining scope が分かれている。
- `implemented-unverified`: 実装は入ったが、verification / review が未完了。
- `verified`: 証跡 link 付きで検証済み。
- `deferred`: 意図的に後回し。理由と review-after / 再開条件がある。
- `blocked`: 外部条件や判断待ちで停止。理由と解除条件がある。
- `dropped`: 採用しない。理由と判断履歴への link がある。

## Ledger

| ID | Area | Slice / Phase | Status | Landed scope | Remaining scope | Evidence | Next trigger | Owner | Review after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| impl-001 | サンプル領域 | MVP slice | planned | - | 実装対象を spec に分解する | [関連 spec](./sample-synthesis.md) | spec 承認後に着手 | TBD | 2026-04-12 |

## Open Scope Summary

- Area ごとに、まだ残っている scope と未確定判断を短くまとめる。
- 複数 slice にまたがる依存や、review まで complete と呼べない理由を書く。

## Evidence Links

- `verified` の根拠、manual check、test result、release note、review comment などへの link を集約する。

## Next Review Conditions

- 次にこの ledger を見直す条件、日付、milestone、または unblock 条件を書く。
