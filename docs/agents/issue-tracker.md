# Issue tracker: GitHub

- Repository: `omitsuhashi/skills`
- Issue tracker: GitHub Issues
- Project: #8
- 操作には `gh` CLI を使用する。
- Issue 作成後、指定 Project に登録する。
- Project の所有者と URL は登録前に確認し、別の Project で代用しない。
- 実装仕様・実装設計・acceptance criteria・実装計画の正本は GitHub Issue 本文に保存する。関連する既存 Issue があればそこを更新し、新規 Issue は Project #8 に登録する。
- 実装用の草案、ローカル Issue 台帳、Goal 用の詳細仕様も Wiki に作らず、同じ Issue で扱う。Goal prompt は該当 Issue を参照する。
- Wiki には再利用可能なドメイン知識・調査結果・運用知識を保存する。Issue との相互参照は必要な場合だけ追加し、実装文書のコピーや要約を Wiki に維持しない。

## Operations

Issue の新規作成・要件見直しでは、内容や粒度を整理する場合に `skills/frame-issues/SKILL.md` を読む。エージェントへ委任する仕事は `skills/agent-workflow/SKILL.md` の「依頼と文脈を揃える」も読み、完了条件・検証方法・操作範囲・未決事項を本文または正本への参照で伝える。確定済み本文の登録だけなら内容を勝手に変更せず、Issue 登録と実装着手を区別する。

以下の Issue 操作は `omitsuhashi/skills` の checkout 内で実行する。

- 作成: `gh issue create --repo omitsuhashi/skills --title "..." --body-file <file>`
- 参照: `gh issue view <number> --repo omitsuhashi/skills --comments`
- 一覧: `gh issue list --repo omitsuhashi/skills`
- ラベル変更: `gh issue edit <number> --add-label "..." --remove-label "..."`
- Project 登録: `gh project item-add 8 --owner <verified-owner> --url <issue-url>`
- コメントやクローズは、その操作がユーザーに承認されている場合に行う。

## Pull requests as a triage surface

PRs as a request surface: no.
