# GitHub 設定

Settings の調査・適用時に読む。以下は新規設定の例であり、既存設定の PUT 用 replacement ではない。既存 ruleset を更新するときは追加の rules・厳しい parameters・bypass 制約を保持し、明示された変更だけを統合する。

## 調査と API の扱い

`gh` が利用できる場合の読取例。`repo` は照合済み owner/repo、`branch` と `environment` は解決済みの名前を URL encode した値にする。他の認可済み API client でも同じ endpoint を使える。

```bash
gh api "repos/$repo"
gh api --paginate "repos/$repo/rulesets?includes_parents=true&per_page=100"
gh api "repos/$repo/rulesets/$ruleset_id"
gh api --paginate "repos/$repo/rules/branches/$branch?per_page=100"
gh api "repos/$repo/branches/$branch/protection"
gh api --paginate "repos/$repo/environments?per_page=100"
gh api "repos/$repo/environments/$environment"
gh api --paginate "repos/$repo/environments/$environment/deployment-branch-policies?per_page=100"
gh api "repos/$repo/actions/permissions"
gh api "repos/$repo/actions/permissions/workflow"
```

確認項目:

- repository の `default_branch`、`private`、`permissions` と organization 由来の制約。Organization ruleset は repository 内で編集できない。
- ruleset 一覧に出ない bypass は詳細 endpoint で読む。詳細を取得できなければ「bypass なし」と断定しない。
- CI は PR の `check-runs` / commit status から check 名と App ID を採取する。workflow の display name ではない。matrix・path filter・skip で必須 check が永遠に pending にならないことも確認する。
- CODEOWNERS の owner は対象で権限を持つ実在 user/team に解決する。workflow と CODEOWNERS 自身を review 範囲へ含める。
- 既存 Actions allowlist・repository の Token 既定権限を確認し、必要な Action が組織側で拒否されないことを確かめる。

変更前の settings JSON と適用 payload を、Secret を含めず一時領域へ保存する。JSON の boolean・number・array は型を維持し、例えば `gh api --method PUT ... --input payload.json` を使う。API version は対象 host が提供する公式資料に合わせる。

## Squash のみ

`PATCH /repos/{owner}/{repo}`:

```json
{
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false
}
```

この変更は repository 全体の merge 方法に影響する。main だけを対象にする明示指定がある場合は、対応する ruleset の `allowed_merge_methods` で制限する。既存 merge queue がある場合は、その merge method との整合も確認する。

## Main ruleset

`POST /repos/{owner}/{repo}/rulesets` で作成、既存なら対応する ID へ `PUT .../rulesets/{id}`。例の `main` は実際の保護対象 branch に置換する。

```json
{
  "name": "github-repo-setup/main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "required_linear_history"},
    {
      "type": "pull_request",
      "parameters": {
        "allowed_merge_methods": ["squash"],
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": true,
        "required_approving_review_count": 1,
        "required_review_thread_resolution": true
      }
    }
  ]
}
```

有効な CODEOWNERS を導入・確認した場合は `require_code_owner_review: true` にする。既存で true の設定を例の false で上書きしない。独立したレビュー担当者がいない場合は体制を解決し、無断で review count を下げたり bypass を追加したりしない。

CI の観測後、同じ ruleset の rules に次の型の rule を統合する。`test` と `integration_id` は観測値に置換する。App が不明なら値を推測せず、発行元未検証と示す。

```json
{
  "type": "required_status_checks",
  "parameters": {
    "do_not_enforce_on_create": false,
    "required_status_checks": [{"context": "test", "integration_id": 15368}],
    "strict_required_status_checks_policy": true
  }
}
```

PR を要求するのは `pull_request` rule。branch の `update` rule は通常の PR merge まで禁止するので、main の PR-only 制御には使わない。

## 正式タグ: 作成制限と immutable を分離

二つの tag ruleset を作る。同じ actor に作成だけ許可しても、既存タグの更新・削除は許可しないための分離。

共通の target は `tag`、enforcement は `active`、conditions は `{"ref_name":{"include":["refs/tags/v*"],"exclude":[]}}`。実際の release pattern に合わせ、Environment と workflow の pattern と整合させる。

| name | rules | bypass_actors |
| --- | --- | --- |
| `github-repo-setup/release-creation` | `[{"type":"creation"}]` | 解決済み正式発行者だけ |
| `github-repo-setup/release-immutable` | `[{"type":"update","parameters":{"update_allows_fetch_and_merge":false}},{"type":"deletion"}]` | `[]` |

ユーザーが Repository Admin を発行者に指定した場合の作成側だけの例:

```json
[{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}]
```

`RepositoryRole` の ID を user ID と混同しない。Team / Integration は対象で解決した ID を使い、actor type の対応可否を確認する。発行者なしでは全員の tag 作成を止めるので、権限主体を解決してから作成制限を有効化する。既存の発行者を変更する場合は影響を示す。

## Environment

`staging` / `production` は既定の名前。既存の同じ役割の環境を再利用する。新規 production の `PUT /repos/{owner}/{repo}/environments/{environment_name}` は次の内容にする。reviewer ID は user/team と repository access を照合する。

```json
{
  "prevent_self_review": true,
  "can_admins_bypass": false,
  "reviewers": [{"type": "User", "id": 123}],
  "deployment_branch_policy": {"protected_branches": false, "custom_branch_policies": true}
}
```

`123` は説明用。実際の ID に置換する。既存環境の wait timer・reviewer・他の保護も保持する。複数 Required reviewers は全員承認ではなく、登録された一人の承認で進む。複数人承認が必要なら別の統制が必要。

Environment を先に作成・更新してから、`POST .../environments/{environment_name}/deployment-branch-policies` で `{"name":"v*","type":"tag"}` を設定する。一覧の `(name,type)` が一致する policy を再利用する。許可済み branch や広い pattern が残れば tag-only にならないので、依頼範囲で余分な policy を整理する。既存経路を止める変更は承認を得てから行う。staging も tag-only にし、既存の検証用途を停止する場合は先に影響を解決する。

`protected_branches: true` は main 上の commit を指すタグの検査にはならない。tag ancestry は workflow で確認する。

`can_admins_bypass` 等を利用中の API client が書けない場合は対応 API または UI で設定し、GET で false を確認する。取得・適用・readback ができない項目は完了扱いにしない。

## Actions

workflow 内の最小権限と SHA 固定を先に整える。新規 repository の Token 既定値は `PUT .../actions/permissions/workflow` の `{"default_workflow_permissions":"read","can_approve_pull_request_reviews":false}` を使える。既存 workflow の必要権限は job ごとに明示し、既存機能を止める変更は影響を解決する。

repository 全体の Action allowlist を導入・変更する場合は、全 workflow の `uses:` を列挙し、既存の承認済み Action と今回の固定 SHA を保持する。参照元の 3 Action だけをコピーして既存 CI を壊さない。organization policy の緩和はこの repository setup の範囲外。

## 一次資料

- [Repository API](https://docs.github.com/en/rest/repos/repos#update-a-repository)
- [Rules API](https://docs.github.com/en/rest/repos/rules)
- [Ruleset の提供範囲](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Environment API](https://docs.github.com/en/rest/deployments/environments)
- [Deployment branch / tag policy API](https://docs.github.com/en/rest/deployments/branch-policies)
- [Environment の提供範囲](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
- [Actions permissions API](https://docs.github.com/en/rest/actions/permissions)
