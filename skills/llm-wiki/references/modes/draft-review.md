# Draft Review Mode

owner actor が proposed note を review queue から閉じるときに使います。draft は verified claim ではなく、owner が判断するまで canonical wiki page にはしません。

Read first: `references/core.md`, chosen topology reference, then this file.

## Goal

owner decision を明示し、採用した内容だけを canonical page へ反映する。採用しない、またはまだ判断できない draft も履歴を残して閉じるか保留し、判断履歴なしに削除しない。

## Check First

- actor は対象 root の canonical owner か。
- 対象 root の `Read` は `allowed` か。
- owner が canonical page を更新する場合、target root は `Write: owned` で、local contract または adapter は owner canonical update を許すか。
- draft note の status / review state / requested action は何か。
- draft が指す canonical page / claim は存在するか。
- draft の evidence と source summary は十分か。
- `index.md` に active page として載せるべき canonical page はどれか。
- `log.md` に残すべき decision history は何か。

## Decision Set

- `promote`: canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許す場合に、draft を verified claim として canonical page へ反映する。
- `merge`: canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許す場合に、draft の unique な内容を既存 canonical page へ統合する。
- `reject`: 採用しない理由を残し、active queue から外す。
- `defer`: 未判断の理由と次の条件を残し、保留する。

## Default Procedure

1. `Draft Target` から対象 draft を読む。
2. 関連する canonical page と `index.md`, `log.md` を読む。
3. draft の evidence, open questions, requested action を確認する。
4. decision を `promote`, `merge`, `reject`, `defer` のいずれかに決める。
5. `promote` の場合は、canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許すときだけ、draft の提案を verified claim として新規または既存 canonical page に反映する。
6. `merge` の場合は、canonical owner が draft-review authority を持ち、`Write: owned` で、local contract または adapter が owner canonical update を許すときだけ、draft の unique な内容を既存 canonical page へ統合する。
7. `reject` の場合は、採用しない理由を draft 側または `log.md` に残し、active review queue から外す。
8. `defer` の場合は、未判断の理由、次に必要な source / owner action、再確認条件を draft 側または `log.md` に残す。
9. `promote` / `merge` 後は `Write: owned` かつ owner canonical update が許される場合だけ canonical page と `index.md` を更新し、`log.md` に `draft-review` entry を追加する。許されない場合は decision と必要な owner action を draft 側または `log.md` に残す。
10. いずれの decision でも、draft の `Current Status` を final status に更新する。
11. `reject` / `defer` でも日付、判断者、理由を残す。履歴なしに draft を削除しない。

## Pause And Align When

- actor が owner か不明。
- draft の evidence が弱く、採否で downstream page が大きく変わる。
- `promote` / `merge` が rename, split, rehome を伴う。
- `reject` が重要な competing interpretation を消す可能性がある。
