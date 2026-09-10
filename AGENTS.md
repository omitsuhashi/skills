# Repository Router

- This repository contains a persistent LLM-maintained wiki under `knowledge/`.
- When bootstrapping, ingesting, querying, reviewing drafts, canonicalizing pages, or linting the wiki, read `knowledge/AGENTS.md` first and treat `knowledge/` as the knowledge root.
- Store implementation specifications, implementation designs, acceptance criteria, and implementation plans in GitHub Issues according to `docs/agents/issue-tracker.md`. Keep reusable domain knowledge and research in `knowledge/wiki/...` according to `knowledge/AGENTS.md`; do not duplicate implementation documents there.
- Keep repo-root guidance here short. Do not duplicate wiki-wide rules in this file.

## Skill and plugin authoring

- Skills created or changed in this repository must use a portable shared `SKILL.md`
  contract with declared inputs, outputs, and required capabilities.
- For skill requirements, follow `skills/AGENTS.md`.
- For plugin requirements, follow `plugins/AGENTS.md`.

## Task Worktree Policy

- Default branch checkout is read-only for task work.
- Before the first repository write after discovery or grilling, create or verify one task-linked worktree.
- Reuse that worktree through planning, implementation, review, and documentation sync.
- Additional issue worktrees are used only when execution isolation or parallel worker review requires them.
- If required worktree creation fails, stop before writing; do not continue in the default checkout.
- Before delivery, verify that the PR branch contains every task commit.
- Before completion, verify that the default checkout matches its starting HEAD/status. Never alter pre-existing unrelated changes without explicit approval.

## Agent skills

### Issue tracker

GitHub Issues を使用し、Issue は Project #8 に登録する。
Issue の作成・参照・更新時は `docs/agents/issue-tracker.md` を読む。

### Triage labels

5つの標準ラベルを使用する。
トリアージ時は `docs/agents/triage-labels.md` を読む。

### Domain docs

single-context。再利用可能な知識・調査結果は knowledge wiki、実装仕様・実装計画は GitHub Issue に配置する。
ドメイン調査・設計時は `docs/agents/domain.md` を読む。
