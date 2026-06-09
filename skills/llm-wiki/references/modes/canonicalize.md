# Canonicalize Mode

重複や強い重なり、境界の崩れを見つけたときに、owner actor が page boundary を整理する mode です。

Read first: `references/core.md`, chosen topology reference, then this file.

## Goal

page を増やし続けず、canonical page, discoverability, audit trail を保ったまま wiki を整理する。

## Check First

- actor は対象 root の canonical owner か。
- 対象 root の `Read` は `allowed` か。
- direct canonical update は canonical owner authority、`Write: owned`、local contract / adapter の許可を満たすか。
- 対象 page は `index.md` にどう載っているか。
- 対象 page の inbound / outbound link はどこか。
- action は `rename`, `merge`, `archive`, `split`, `rehome` のどれか。
- 複数 root をまたぐ場合、canonical owner と draft target はどこか。

## Action Set

- `rename`: canonical 名称へ寄せる。旧 page を消すだけで discoverability を失うなら、短い案内 stub を残して新 page へ誘導する。
- `merge`: destination を 1 つ決め、unique な内容だけを canonical page へ移す。統合元は削除せず、merged / superseded の案内を短く残すか archive する。
- `archive`: obsolete, superseded, duplicate のときだけ使う。archive 先または後継 page を明示し、現役 page と誤認される書き方を避ける。
- `split`: 1 page に複数の durable topic が混ざったとき、独立 page へ分け、元 page に境界と link を残す。
- `rehome`: page が wrong root / wrong page type / wrong directory にあるとき、canonical owner と保存先を直し、旧位置から新位置へ誘導する。

## Default Procedure

1. `index.md` から対象 page と重なり候補を確認する。
2. 編集前に対象 page、関連 page、`log.md` を読む。
3. canonical page と action を決める。
4. canonical owner authority があり、`Write: owned` で、local contract または adapter が owner canonical update を許す場合だけ canonical page を直接更新する。
5. direct update できず `Read: allowed`, `Write: owned` または `propose`, `Draft Target` 解決済みの場合だけ、root 内の `Draft Target` に proposed note を作り、canonical page, `index.md`, `log.md` は直接更新しない。
6. `closed`, `restricted`, `no-access`, target 不明、または `Draft Target` 未解決の場合は書かずに session user へ確認する。
7. direct update した場合は、対象 page、関連 link、`index.md`, `log.md` を更新する。
8. canonical page へ最低 1 本の inbound link が残ることを確認する。

## Pause And Align When

- canonical owner が不明。
- split / rehome が複数 root の authority boundary をまたぐ。
- archive が historical context や citation trail を失わせる。
- rename / merge により大量の link 更新が必要になる。
