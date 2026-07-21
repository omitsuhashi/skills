# Task Management Write / Preflight Execution Handoff Brief

## Purpose

`portfolio-os-task-backend-plugin-skill` の承認済み write / preflight 設計を、planning transcript に依存せず fresh `issue-implementation-loop` coordinator が実装するための bounded handoff。正本は以下の artifact であり、この brief は paths-first cache とする。

## Canonical Artifacts

- Interface spec: `knowledge/wiki/syntheses/task-management-write-preflight-interface-spec.md`
- GitHub Adapter spec: `knowledge/wiki/syntheses/task-adapter-github-projects-spec.md`
- Implementation plan: `knowledge/wiki/syntheses/2026-07-21-task-management-write-preflight-implementation-plan.md`
- Issue ledger: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-issues.md`
- Input packet: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-write-preflight-input-packet.json`
- Execution Envelope: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-write-preflight-execution-envelope.json`
- Preflight evidence: `knowledge/wiki/syntheses/portfolio-os-task-backend-plugin-skill-write-preflight-execution-preflight.json`

## Carry-Forward Capsule

- Spec Gate、Issue Gate、POTASK-015 / 019 integration ownership amendmentは承認済み。POTASK-012からPOTASK-019をTDD順に実行する。
- `worker_context_required=true`、`coordinator_may_implement=false`。issueごとに専用branch/worktree、独立review、最大2 review cycleを使う。
- POTASK-012完了後、POTASK-013 / 014 / 016をreleaseできる。POTASK-015はPOTASK-013をbaseにreview-approved POTASK-014を統合する。POTASK-019はPOTASK-018をbaseにreview-approved POTASK-015を統合する。
- public v2は`task_query`、`task_preflight`、`task_apply`。createはlinked Issue onlyでdraft item概念を追加しない。確証不足はhuman confirmation、十分な確証かつeligibleな場合だけ`confidence_authorized`を許可する。
- task-managementはprovider-neutral validation / routing / approval binding / normalizationを所有し、GitHub tool・mapping・auth・provider orchestrationは別pluginが所有する。
- remote policyは`local_only`。GitHub Issue、push、PR、merge、live Hermes / MCP / credential / Project / Issue変更を行わない。

## Stop Conditions

- worker contextを作れない、approved spec / digestが変わる、write scope外変更が必要、同一findingが2 cycleで解消しない、またはlive / remote writeが必要になった場合は停止して人間へ返す。
- unrelated dirty / untracked filesを変更しない。特にmain checkoutの`skills/llm-wiki/DESCRIPTION.md`を保持する。
