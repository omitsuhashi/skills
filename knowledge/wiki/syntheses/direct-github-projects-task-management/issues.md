# GitHub Projects 直接接続型 Task Management Skill Issue 台帳

## 状態

2026-07-23にIssue Gate承認済み。DGPTM-001をfirst runnable candidateとし、Execution Plan Gate承認まではproduction実装を開始しない。

## Epic ID

`direct-github-projects-task-management`

## Approved spec binding

- path: `knowledge/wiki/syntheses/direct-github-projects-task-management/spec.md`
- raw-byte SHA-256: `9200996f2ed046ecb351fad96930c6e4e9a1580fdde14472ecc8b68b98f36c94`
- gate commit: `62281b1f2fbcfa580b19446fd51b1ecbd0a3d4c9`
- approval actor expression: `session-user`
- approval scope: accepted decisions / non-goals / acceptance criteria / verification / remote policy / stop conditions

## Issue 一覧

| Epic | Issue | タイトル | Gate | 実行状態 | Dependencies | Write scope |
|---|---|---|---|---|---|---|
| `direct-github-projects-task-management` | DGPTM-001 | standalone skill の executable contract を test-first で固定する | 承認済み | 実行可能 | なし | `skills/task-management/` |
| `direct-github-projects-task-management` | DGPTM-002 | direct GitHub MCP の task workflow と安全境界を実装する | 承認済み | ブロック中 | DGPTM-001 | `skills/task-management/` |
| `direct-github-projects-task-management` | DGPTM-003 | 旧 task-management plugin を削除して CI と回帰契約を移行する | 承認済み | ブロック中 | DGPTM-002 | `plugins/task-management/`, `.github/workflows/skill-architecture.yml`, `scripts/test_dual_host_ci_workflow.py`, `scripts/test_loop_autonomous_gates_ledger.py`, `skills/task-management/tests/` |
| `direct-github-projects-task-management` | DGPTM-004 | historical supersession と統合検証を完了する | 承認済み | ブロック中 | DGPTM-003 | `knowledge/index.md`, `knowledge/log.md`, `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md` |

## Blocker graph

```text
DGPTM-001
└── DGPTM-002
    └── DGPTM-003
        └── DGPTM-004
```

Issue Gate 承認後の first runnable issue は DGPTM-001。各 Issue は直前 Issue のreviewed commitをbaseにし、同一pathを変更するDGPTM-001 / DGPTM-002は並列実行しない。

## 実行順序

1. DGPTM-001: standalone skill directory、contract tests、最小entrypointを作る。
2. DGPTM-002: approved spec のtarget resolution、Issue / Project contract、approval / failure behaviorをreferencesへ実装する。
3. DGPTM-003: 新skillが検証可能になった後で旧pluginを削除し、CIとrepository regressionを切り替える。
4. DGPTM-004: active wikiを新contractへ切り替え、fresh scenario evaluationと全体検証を完了する。

## DGPTM-001: standalone skill の executable contract を test-first で固定する

### Outcome

`skills/task-management/` が独立skillとして検証可能になり、approved specの禁止事項と必須surfaceをrepository testで固定する。

### Write scope

- `skills/task-management/SKILL.md`
- `skills/task-management/tests/test_task_management_contract.py`
- DGPTM-001に必要な最小reference file

### Acceptance criteria

- [ ] 最初に failing contract test を追加し、旧plugin内のskillを新skillとしてcopyしただけでは失敗することを確認する。
- [ ] `SKILL.md` frontmatterの`name`は`task-management`、descriptionはGitHub Projects direct task operationをtriggerできる内容である。
- [ ] caller-supplied `project_url`、optional `inbox_repository`、1 caller / 1 canonical default Project、invocation overrideの存在をtestが要求する。
- [ ] Issue-backed task、repository-as-work-unit、no Project draft item、no `work_unit_id` fieldをtestが要求する。
- [ ] plugin manifest、production Python、backend adapter、task state file、credential fileを新skillへ追加しない。
- [ ] user-facing skill proseに特定agent host名、専用runtime tool名、専用install commandがない。
- [ ] `skill-creator` quick validatorとfocused unit testが成功する。

### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task-management-read|task_adapter__|work_unit_id" skills/task-management
git diff --check
```

### Non-goals

- このIssueで旧pluginを削除しない。
- Project field / status transition / partial failureの全referenceを完成させない。
- live MCPを呼ばない。

## DGPTM-002: direct GitHub MCP の task workflow と安全境界を実装する

### Outcome

新skillだけを読めば、caller target解決からIssue作成、Project追加、field更新、terminal transition、部分失敗再開までをGitHub MCPへ直接委譲できる。

### Write scope

- `skills/task-management/SKILL.md`
- `skills/task-management/references/core.md`
- `skills/task-management/references/github-projects.md`
- `skills/task-management/references/issue-contract.md`
- `skills/task-management/references/safety-and-failures.md`
- `skills/task-management/tests/test_task_management_contract.py`

### Acceptance criteria

- [ ] target resolutionはinvocation value、caller default、session-established target、unique discovery、human confirmationの順である。
- [ ] title-only / recency-onlyでstate-changing targetを選ばず、owner / URL / visibility / permission mismatchをfail closedにする。
- [ ] repository resolutionはexplicit、current repository、unique referenced repository、configured inbox、human confirmationの順である。
- [ ] inboxはambiguous fallbackではなくrepository-independent / unclassified taskだけに使う。
- [ ] Issue templateはOutcome、Context、Acceptance criteria、Referencesを持ち、raw transcript、internal prompt、credential、agent名を保存しない。
- [ ] Status 7 option、Priority 4 option、optional Due date、default Inbox / P2が固定される。
- [ ] Done / CancelledとIssue close reasonのmapping、explicit terminal instructionのno-double-confirm、inferred terminal transitionのconfirmationが固定される。
- [ ] high-confidence safe single mutationはauto、uncertain / destructive / bulk mutationはconfirmationという境界が具体化される。
- [ ] GitHub MCP semantic capability checkを行い、CLI / REST / GraphQL / browser / local backendへfallbackしない。
- [ ] Issue create後のProject write failureとterminal partial failureはdelete rollbackせず、残stepのidempotent continuationを返す。
- [ ] 別skillを必須dependencyにしない。
- [ ] focused testsとskill validatorが成功する。

### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
rg -n --glob '!**/tests/**' "Hermes|Codex|task_adapter__|mcp__<server>__task_query|work_unit_id" skills/task-management
rg -n --glob '!**/tests/**' "subprocess|requests|urllib|graphql|\bgh\b" skills/task-management
git diff --check
```

### Non-goals

- MCP function名をhost共通APIとして固定しない。
- caller configの保存pathを定義しない。
- Project / field / repositoryのsetupを通常task flowへ混ぜない。

## DGPTM-003: 旧 task-management plugin を削除して CI と回帰契約を移行する

### Outcome

repositoryのexecutable task-management surfaceをstandalone skillだけにし、削除済みplugin pathへ依存するCIとrepository testsを新contractへ切り替える。

### Write scope

- delete: `plugins/task-management/`
- `.github/workflows/skill-architecture.yml`
- `scripts/test_dual_host_ci_workflow.py`
- `scripts/test_loop_autonomous_gates_ledger.py`
- `skills/task-management/tests/`のintegration assertions

### Acceptance criteria

- [ ] `plugins/task-management/` directory全体が削除される。
- [ ] plugin manifest、registration、Python facade、route config、provider adapters、fixtures、host-specific smokeが残らない。
- [ ] CIはPython 3.9 / 3.12でstandalone task-management testsを実行し、削除済みtest fileを参照しない。
- [ ] `scripts/test_dual_host_ci_workflow.py`は新CI stepとstandalone skill pathを検証する。
- [ ] `scripts/test_loop_autonomous_gates_ledger.py`は旧adapter test sourceへの実行依存を持たず、現行approval / capability contractまたはhistorical ledger evidenceを検証する。
- [ ] repository内のactive code / workflow / testから`task-management-read`、`plugins/task-management` dependencyが消える。
- [ ] decide-in-order standalone testsはtask-management pluginがなくても成功する。
- [ ] unrelated `skills/llm-wiki/DESCRIPTION.md`を変更、削除、stageしない。

### Verification

```bash
test ! -e plugins/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_dual_host_ci_workflow.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/test_loop_autonomous_gates_ledger.py
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
rg -n "plugins/task-management|task-management-read" .github/workflows skills/task-management --glob '!**/tests/**'
git diff --check
```

### Non-goals

- historical wiki artifactを削除または書き換えない。
- repository-wide compatibility validator自体を削除しない。
- live installed pluginやagent profileを変更しない。

## DGPTM-004: historical supersession と統合検証を完了する

### Outcome

active knowledge surfaceが新skillをcurrent contractとして案内し、historical POTASK artifactを証跡として保持したまま、fresh scenarioとrepository-wide verificationが成功する。

### Write scope

- `knowledge/index.md`
- `knowledge/log.md`
- `knowledge/wiki/syntheses/direct-github-projects-task-management/issues.md`

### Acceptance criteria

- [ ] `knowledge/index.md`は本spec、Issue ledger、implementation plan、Input Packetをnested Epic rootから発見できる。
- [ ] 旧plugin spec / ledger / planをcurrent implementationとして案内せず、historical evidenceとして境界を明示する。
- [ ] historical Input Packet / Execution Envelope JSONのbytesを変更しない。
- [ ] approved `spec.md`、sealed `input-packet.json`、承認済み`implementation-plan.md`を実装Issueのwrite対象にしない。
- [ ] `knowledge/log.md`にSpec Gate、Issue Gate、Execution Plan Gate、implementation / verification状態をappend-onlyに記録する。
- [ ] fresh evaluationが明確なrepository task、Project override、Project / repository ambiguity、inbox、terminal transition、capability missing、partial failure retryを確認する。
- [ ] task-management、decide-in-order、llm-wiki、repository scripts、architecture、compatibility validatorが成功する。
- [ ] static negative checksと`git diff --check`が成功する。
- [ ] local-only scopeを維持し、live GitHub write、push、PR、merge、installを実行しない。

### Verification

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/task-management/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/decide-in-order/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --skill skills/task-management
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/task-management
git diff --check
```

### Non-goals

- live MCPの成功をlocal contract testで偽装しない。
- historical completion evidenceを新architectureの実装証拠として再利用しない。
- remote deliveryを暗黙に開始しない。

## Gate policy

- Issue Gateは2026-07-23に承認済み。DGPTM-001だけを`実行可能`、dependency未充足の後続Issueを`ブロック中`とする。
- implementation planとsealed Input PacketがExecution Plan Gateで承認されるまではproduction implementationを開始しない。
- approval対象は本ledgerのIssue ID、Outcome、blocker graph、dependency order、write scope、acceptance criteria、verification、non-goalsとする。
- ledgerの意味を変える修正後はIssue Gateを再取得する。
- remote policyはapproved specどおり`local_only`とする。

## 関連ページ

- [GitHub Projects 直接接続型 Task Management Skill 仕様](spec.md) — 本ledgerを拘束するapproved spec。
- [Loop Skill Approved Spec Binding Contract 仕様](../approved-spec-binding-contract/spec.md) — Issue Gate、Input Packet、artifact lifecycleの現行contract。

## 出典

- [GitHub Projects 直接接続型 Task Management Skill 仕様](spec.md)
