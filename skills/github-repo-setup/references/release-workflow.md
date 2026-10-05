# Release workflow

deployment の導入・既存 workflow の修正時に読む。既存 CI・build・deploy を利用し、別のサンプルアプリを生成しない。コマンド・成果物・デプロイ先が決まらない部分は未完了として示す。

## 導入する経路

1. `push.tags` を正式 release pattern（既定 `v*`）に限定する。既存の main push / release event / manual dispatch による実 deployment も調べ、保護を迂回する経路を残さない。既存経路の停止は影響を示して承認を得る。PR 由来の信頼できないコードへ deployment 資格情報を渡す経路は作らない。
2. staging job では完全な SHA で固定した checkout Action を使い、全履歴を取得する。外部 Action の SHA は公式 repository の release tag と照合する。branch・tag・pull_request の取り違えを避け、build・資格情報の使用前にタグ commit が対象 branch の履歴上にあることを検査する。
3. 対象 stack の CI と必要な staging 動作確認を行い、release bundle を一度 build する。production は `needs: staging` で接続し、同じ run の固定成果物または immutable image digest を参照する。再 checkout・rebuild した別物を本番へ昇格しない。
4. production job に、設定 readback 済みの `environment` を明示する。Environment の資格情報をこの job 内だけで使用し、承認後も checksum / digest と commit・tag・run を照合して実際の deploy コマンドを実行する。必要な `id-token: write` 等はこの job だけに付ける。
5. environment 単位の `concurrency`、`cancel-in-progress: false`、用途に合う timeout を設定する。commit、tag、run/attempt、artifact hash、結果を summary／必要な証跡に記録する。retention は用途に合わせ、Actions artifact の既定保持を正式な監査保管と扱わない。

## GitHub Release を公開する場合

GitHub Release の作成も依頼範囲にあるか、既存 workflow が Release を公開する場合に適用する。Release immutability と整合するよう、Draft 作成 → 全 assets 添付 → Publish の順序にする。全 assets のアップロード成功を確認してから公開し、公開後の追加・差替えを前提とする処理はこの順序へ修正する。修正版の導入状況は [GitHub 設定](github-settings.md#release-immutability)の有効化条件と照合する。

実際の Release 発行を依頼された場合は、公開後に対象 Release の `immutable: true` と commit・tag・assets を確認する。repository 設定の readback と、個別 Release の固定確認を分けて報告する。setup の依頼だけでは検証用 Release を発行しない。

## タグ commit の検査

`fetch-depth: 0` の checkout 後、build や資格情報の使用より前に置く Bash step の例。`RELEASE_BRANCH` は解決済みの保護対象 branch を workflow の `env` から渡す。式を shell 本文へ直接埋め込まず environment variable で扱う。

```bash
set -euo pipefail
test "$GITHUB_REF_TYPE" = tag
git check-ref-format "refs/heads/$RELEASE_BRANCH"
git fetch --no-tags origin "refs/heads/$RELEASE_BRANCH:refs/remotes/origin/$RELEASE_BRANCH"
release_commit=$(git rev-parse --verify "$GITHUB_SHA^{commit}")
test "$(git rev-parse HEAD)" = "$release_commit"
git merge-base --is-ancestor "$release_commit" "refs/remotes/origin/$RELEASE_BRANCH"
```

これは「履歴上にある commit」の検査であり、main の最新 tip だけを許可する制御ではない。最新 tip 限定が明示された場合は equality check にする。annotated tag は commit に peel して判定する。

Environment の tag pattern や tag ruleset 自体は ancestry を検査しない。また、tag 上の workflow 自体を書き換えられる発行者に対し、この step だけで改変を防ぐことはできない。正式タグの作成権限は信頼された発行者に限定し、workflow の変更を PR review 範囲に含める。独立した強制境界が必要という依頼では、保護された reusable workflow やクラウド側 trust policy の別途設計が必要と示す。

## 検証

- この skill の guard 例を変更したら `python3 tests/check_release_guard.py` を skill directory から実行する。local Git fixture だけを使い、live tag を発行しない。
- workflow の syntax / expression / `needs` / `environment` と、対象 stack の実コマンドを検証する。既存の workflow validator があれば利用する。
- ancestry step を local temporary Git fixture で確認する。main の commit と祖先は通り、main に入っていない branch commit は失敗する。annotated tag、main 以外の保護対象 branch、tag 以外の event も含める。fixture は本番 remote を使わない。
- bootstrap PR の CI check が観測され、必須チェックへ登録されたことを readback する。PR 上の workflow と main 上の workflow を区別する。
- live tag の発行・デプロイは実行依頼がある場合のみ。承認待ちの観測は deployment 成功ではない。成功は対象 run/attempt、承認と反映結果、昇格した成果物の同一性を確認してから報告する。

## 参照実装と資料

- [github-change-management-mvp](https://github.com/omitsuhashi/github-change-management-mvp) は構成例。Python アプリ、production-demo、発行者・承認者の個人名、一人デモの一時例外、模擬反映は対象へコピーしない。
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
- [Reviewing deployments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments)
- [Immutable releases の公開手順](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases#best-practices-for-publishing-immutable-releases)
- [Releases API](https://docs.github.com/en/rest/releases/releases)
