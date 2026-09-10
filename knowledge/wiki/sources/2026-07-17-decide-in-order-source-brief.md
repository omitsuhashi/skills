---
kind: source
created: 2026-07-17
updated: 2026-07-17
source_files:
  - ../../raw/sources/2026-07-17-decide-in-order-source-brief.md
summary: 目的、守るもの、許容損失、核心の問いから始める実行支援型 skill の一次資料と設計時の解釈。
knowledge_status: historical
aliases:
- 決める順番
---

# Decide In Order Skill 原案

## 適用範囲と履歴

意思決定支援 skill の設計履歴。`decide-in-order` 本体は commit `99fdaf2` で削除されており、本文の current は当時の状態を指す。

## 概要

この source は、条件、期限、不安、既投入工数に引きずられず、何を進め、何を捨て、いつ見直すかを決めるための実行支援型 skill 原案である。一般的な TODO 管理ではなく、判断の質と順番を整えることを目的とする。

## 中核原則

判断は次の順に扱う。

1. `purpose`
2. `must_protect`
3. `acceptable_loss`
4. `core_question`
5. `decision_order`
6. `constraints`
7. `method`
8. `risk`
9. `review`

期限や重要度だけの順位付け、サンクコストによる続行、問いを決める前の情報収集、全選択肢を残した方法比較、不安とリスクの混同を避ける。

## 主な利用場面

- 新しいタスクを実行前の意思決定と分離する。
- 日次計画を時間割ではなく中心となる決定から作る。
- 目的への寄与、依存解除力、不可逆性、学習価値、信頼、コスト、期限の順で優先順位を考える。
- 中止、延期、委任を思考の更新として扱い、損失と復活条件を残す。
- 調査前に核心の問いと停止条件を決める。
- リスクを結果、起こりやすさ、備え、撤退条件で扱う。
- 判断を仮決定として扱い、通常工程として見直す。

## 設計時に加えた解釈

原案の完全な task schema は、そのままユーザー入力や通常出力へ強制しない。承認済み設計では、判断順序を厳密に保ちつつ、内部状態は疎、表示は適応的、永続化境界だけ型付きにする。

思想 skill は task-management から独立させる。task-management は思想を複製せず、動作別の利用ポリシーだけを持つ。

## 関連ページ

- [Decide In Order Skill 設計](../syntheses/decide-in-order-skill-design.md) — 原案を独立 skill と task-management integration policy へ落とした承認済み設計。
- [Portfolio OS Task Backend Plugin Skill Spec](../syntheses/portfolio-os-task-backend-plugin-skill-spec.md) — 連携対象である既存 task-management plugin の責務境界。

## 出典

- [raw source brief](../../raw/sources/2026-07-17-decide-in-order-source-brief.md)
