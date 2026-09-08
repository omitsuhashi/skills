# Issue tracker: GitHub

- Repository: `omitsuhashi/skills`
- Issue tracker: GitHub Issues
- Project: #8
- 操作には `gh` CLI を使用する。
- Issue 作成後、指定 Project に登録する。
- Project の所有者と URL は登録前に確認し、別の Project で代用しない。
- 仕様・設計・実装計画の正本は `knowledge/wiki/` に保存し、Issue から参照する。

## Operations

以下の Issue 操作は `omitsuhashi/skills` の checkout 内で実行する。

- 作成: `gh issue create --repo omitsuhashi/skills --title "..." --body-file <file>`
- 参照: `gh issue view <number> --repo omitsuhashi/skills --comments`
- 一覧: `gh issue list --repo omitsuhashi/skills`
- ラベル変更: `gh issue edit <number> --add-label "..." --remove-label "..."`
- Project 登録: `gh project item-add 8 --owner <verified-owner> --url <issue-url>`
- コメントやクローズは、その操作がユーザーに承認されている場合に行う。

## Pull requests as a triage surface

PRs as a request surface: no.
