---
name: github-repo-setup
description: Set up GitHub repository change management with PR-only protected branches, squash merges, immutable release tags, and Environment-gated deployments. Use for a new repository or an explicit request to adopt this workflow.
---

# GitHub Repository Setup

## 入力・出力・必要な能力

- 入力: 対象の GitHub repository または checkout、セットアップ範囲。CI・レビュー体制・正式タグの発行者・Environment の承認者・デプロイ先は、既存設定と依頼から解決する。
- 出力: 対象ごとの設定差分、適用した GitHub 設定、workflow の変更または PR、検証結果と未完了項目。
- 必要な能力: GitHub の repository・ruleset・Actions・Environment の読取と管理 API、対象ファイルの読取・編集、Git とテストの実行。workflow の publication には Contents / Workflows の書込みが必要。利用できる CLI・connector・UI を使う。管理機能が使えなければ該当項目を `BLOCKED` として、具体的な payload・ファイル差分まで準備する。

## 既定の結果

明示された設定を優先し、指定がなければ次を採用する。既存のより強い保護は維持する。

| 対象 | 結果 |
| --- | --- |
| main | PR 経由、承認 1 名、変更時の承認失効、会話の解決、実在する必須 CI、force push・削除禁止、通常 bypass なし |
| merge | squash のみ。linear history だけでは rebase を排除できない |
| 正式タグ | `v*` の作成者を限定。既存タグの移動・削除は bypass なしで禁止 |
| deployment | main 上の commit を指すタグ → staging 検証 → production 承認 → 同じ成果物を反映 |
| production | タグだけ許可、必須承認者、自己承認禁止、管理者の承認 bypass 禁止 |
| workflow | 完全な commit SHA で Action を固定。Token は read を基本に job ごとに必要権限を追加 |

既存 default branch が main 以外なら、その branch を保護対象として示す。branch の改名は依頼された場合に行う。CODEOWNERS は有効な owner が解決できる場合に設定し、レビュー必須にする。

一人運用では独立した PR レビュー・自己承認禁止の deployment を完了できない。承認者の追加か、ユーザーが選んだ別の運用が必要。参照実装の一時 bypass や個人名を既定値としてコピーしない。

## 対象の確認と差分

1. checkout の remote と GitHub の owner/repo・default branch・visibility を照合し、対象を確定する。権限、適用される organization ruleset、既存 branch protection、Environment とその deployment policy、Actions policy、workflow、CI・build・deploy の入口を読む。404 は、権限や機能提供の確認なしに「設定なし」と扱わない。
2. Settings と workflow の具体的な変更を用意する。Settings を扱う場合は [GitHub 設定](references/github-settings.md)、deployment を扱う場合は [Release workflow](references/release-workflow.md) を読む。未知の CI 名・承認者・タグ発行者・デプロイ先は必要な範囲だけ質問し、依存しない準備は進める。
3. 現在値 → 変更後、影響する branch/tag、必須チェック、承認者、workflow の導入順序を示す。セットアップの依頼はその範囲の設定適用を含む。相談・preview なら差分まで。保護の緩和、既存 deployment 経路の停止、契約変更など範囲外の判断は、具体的な差分を作ってから承認を求める。

GitHub plan・visibility によって ruleset や Environment の Required reviewers が利用できない。機能の可否を公式資料と対象の readback で確認する。利用できない必須統制を無言で省略せず、該当項目を `BLOCKED` とする。公開化・契約変更・保護方式の格下げは自動で行わない。

## 適用

- 既存の同じ役割の ruleset・Environment・workflow を ID／path で再利用する。再実行は現在値との差分だけにし、重複や保護の一時解除を作らない。無関係な設定を保持する。
- 空の repository では初回 commit と default branch の作成範囲を解決してから、PR 保護を有効化する。既存 main への直接 push で workflow を導入しない。
- CI を追加する場合は作業 branch の PR で実行を観測し、check 名と発行 App を確認して必須チェックへ登録する。まだ存在しない check を先に必須化して導入 PR を詰まらせない。PR 必須・履歴保護は維持し、必須 CI が未登録の期間は未完了とする。
- deployment の Environment 保護を設定し readback してから、その Environment を参照する workflow を導入する。クラウド資格情報・Secret・OIDC の発行や変更は、その作業が依頼範囲にある場合に扱う。
- API に失敗したら現在値を読み直す。認証・権限・機能提供の失敗は同じ書込みを反復せず、影響しない作業を完了する。応答不明の作成は readback で存在を確認してから再試行する。partial apply は残った設定と未適用項目を示し、保護を自動で元の弱い状態へ戻さない。

setup の依頼だけで release tag の発行・PR merge・deployment の開始・承認代行は行わない。検証実行を別途依頼された場合は、その実行範囲に従う。

## 完了判定

- repository の merge flags、各 ruleset の詳細と実際の保護対象 branch に適用される active rules、production の reviewers・自己承認防止・admin bypass・tag policy を再取得し、用意した差分と照合する。既存 branch protection も合わせて確認する。
- CI の実際の check 名・発行 App・実行結果と、workflow の Git 差分・構文・テストを確認する。実際の build/deploy コマンドが不明なら workflow を成功扱いの模擬処理で埋めず、該当部分を未完了として返す。
- 「設定 readback 済み」「workflow は PR 上／main 導入済み」「CI 観測済み」「実 deployment 検証済み」を区別する。設定成功だけで deployment 成功や監査対応を主張しない。設定変更権限を持つ管理者自身による保護変更までは防げない。

## 呼び出し例

```text
$github-repo-setup owner/new-repo をセットアップして。
production 承認者は @release-reviewer、正式タグの発行者は Repository Admin。
CI と build/deploy コマンドは既存 workflow から使って。
```

```text
$github-repo-setup この repository の設定差分だけ見せて。
GitHub への書込みはしないで。
```
