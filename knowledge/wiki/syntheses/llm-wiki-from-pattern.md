# 原文に基づく LLM Wiki の再作成

2026-09-09、Human は貼り付けた「LLM Wiki」の原文を基準に、自己完結した
`SKILL.md` と必要な参照整合だけを作成する方針を承認した。今回だけ SDD 必須
ルールを例外扱いにし、専用 worktree を使用する。repository 全体の運用変更や
削除済み SDD の復元は対象外とする。

原文は、immutable raw sources、LLM が維持する wiki、Human と育てる schema の
三層と、ingest / query / lint、内容別 index、追記専用 log を提示している。
構造・ツール・出力形式は用途に応じて選ぶという原文の前提を維持する。

[新しい skill](../../../skills/llm-wiki/SKILL.md) はこの三層と操作を一つの portable
contract にまとめる。入力・出力・必要能力を明記し、出典、矛盾、再取り込み、
回答の保存、リンクと index / log の検証を扱う。Obsidian や検索エンジン、画像、
slide、他 skill は必須依存にしない。旧版の multi-root / authoring discovery /
context contract は復元しない。

[local schema](../../AGENTS.md) は所有者と草案の境界、日本語、既存 Obsidian
link を維持する。旧版の存在しない reference への依存を外し、draft-review と
canonicalize のローカルな意味を明記する。旧版の設計文書は履歴として保存し、
今回の新規 skill に過去の実装要件を自動適用しない。

検証は skill-creator validator、変更前後の repository architecture validator、
具体例による取り込み・質問・点検の確認、および差分・main 保全確認で行う。
変更前の architecture validator は削除済み `sdd-implementation` の不在を二件
報告している。この既存不整合は本変更の完了検証と区別する。

## 検証結果

- skill-creator validator と既存 skill authoring guidance の 3 tests は成功。
- 独立した一時 wiki で bootstrap、二資料の ingest、引用付き回答の保存、同じ
  資料の再取り込み、lint を実行し、生成された 4 pages を確認した。新しい資料
  だけで古い主張を消さず、机の台数から席数を推測せず、未確定事項を保持した。
- 同じ一時 wiki の runnable check は、raw のバイト保持、6 段階のログ前方一致、
  再取り込みのページ集合・内容不変、index / link / inbound coverage を検証し成功。
- repository architecture validator は変更前後で同じ既存二件のみを報告する。
  context validator の対象は 0 contracts であり、本 skill の動作検証には数えない。
- 変更した参照リンクと index の一意な登録、既存 raw と log の保全を確認した。
  repository 全体の CI は削除済み skill の検査を残しており、全体成功は主張しない。
