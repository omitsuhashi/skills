# Domain Docs

## Layout and reading rules

- single-context とする。
- 最初に `knowledge/AGENTS.md` を読み、そこにある生成目録・本文検索・関連リンクの手順から対象領域の用語・知識・調査結果を参照する。実装仕様・実装計画は `docs/agents/issue-tracker.md` に従って該当 GitHub Issue を参照する。
- 既存の `CONTEXT.md` / `CONTEXT-MAP.md` があれば参照する。
- 文書が存在しない場合、セットアップのためだけに作成しない。
- 再利用可能なドメイン知識・調査結果・運用知識は `knowledge/AGENTS.md` に従い `knowledge/wiki/` 配下へ保存する。実装変更に固有の仕様・設計判断・計画・受入条件は GitHub Issue 本文を正本とする。
- 既存文書で定義された用語を使用する。
- 既存の設計判断と矛盾する提案は、その矛盾を明示する。
