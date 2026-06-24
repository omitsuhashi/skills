# Local Issue Ledger

Use this reference when drafting, reviewing, publishing, updating, or reporting local issues.

## Local Issue Policy

Local issues are the canonical planning source. Write local issue titles, headings, field labels, status values, ledger labels, blocker summaries, and prose in Japanese. Keep stable IDs, file paths, commands, code symbols, API names, branch names, error messages, and external issue/PR references unchanged.

Use these values:

- `レビュー状態`: `下書き`, `承認済み`, `差し戻し`, `未解決`
- `実行状態`: `実行可能`, `ブロック中`
- `実装レビュー`: `未実施`, `依頼済み`, `指摘対応中`, `承認済み`, `手動レビュー済み`, `差し戻し`
- no blocker / no remote: `なし`, `未作成`

Ledger table:

```markdown
| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <epic-id> | G2PR-001 | <日本語タイトル> | 承認済み | 実行可能 | なし | G2PR-002 | 未作成 | 未実施 | 未作成 |
```

Do not create GitHub issues for `下書き`, `差し戻し`, or `未解決` local issues.

## Blocker Graph

Build a blocker graph before execution planning:

- Every local issue declares `ブロック元`.
- Every local issue should declare `ブロック先` when known.
- `実行可能` means blockers are `なし` or complete.
- `ブロック中` means at least one blocker is not complete.
- Detect cycles before producing the normalized execution packet.
- Do not hand blocked issues to execution as runnable work. Put dependencies in the packet and let `issue-implementation-loop` reserve them.

## Local Ledger Update Invariant

Update the local ledger immediately after:

- GitHub issue creation.
- Execution returns issue implementation review result.
- Execution marks an issue `PR_READY` or complete.
- PR creation.
- PR closure/merge when known.

Do not report remote or local completion when the ledger contradicts reality. If ledger update fails after a remote action, stop and report the consistency problem.
