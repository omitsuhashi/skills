---
title: SDD Plan Ownership Alignment 実装計画
date: 2026-08-14
tags:
  - sdd-implementation
  - planning
  - implementation-plan
  - skill-architecture
status: active
review_state: independently-reviewed
plan_readiness: ready
aliases:
  - SDD agent-owned execution plan
  - SDD plan readiness implementation plan
---

# SDD Plan Ownership Alignment 実装計画

## 状態と binding

本計画は、Planning Controller から Human-approved current Written Spec として渡された
[[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]]を、agent-owned execution
contract へ変換した Plan Author 成果物である。Human に plan approval、file choice、command choice、
prospective code、commit granularity の判断を求めない。

- planning worktree: `/Users/omitsuhashi/repos/omitsuhashi/skills/.worktrees/sdd-plan-ownership-alignment-planning`
- integration branch: `codex/sdd-plan-ownership-alignment-planning`
- repository baseline: `c370fe14de1641aa5ee30b3fa001f4d857078091`
- approved spec path: `knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md`
- approved spec SHA-256: `1f9a7dc5f740c51addfabde96bac6fe3fbf5036003d1783cde60ac58e5ae7559`
- upstream methodology: active discovery で解決した `superpowers:writing-plans` v6.2.0
- local precedence: approved spec の Plan Contract Overlay が、upstream の保存先、prospective body、
  Human execution-choice prompt、plan approval semantics と衝突する output / routing contract を上書きする

Plan Author self-review後、fresh independent Plan Reviewとblocking finding修復後のre-reviewは
`.superpowers/reviews/sdd-plan-ownership-alignment/plan-review.md`と
`.superpowers/reviews/sdd-plan-ownership-alignment/plan-rereview.md`に記録され、最終re-reviewは
`Repository readiness classification: ready`、decision request `none`、material risk `none`を返した。
Planning Controllerはapproved spec bindingとplan pathを確認し、Plan Readiness Gateを`ready`、Control Returnを
`status: complete`としてImplementation Stageへentryした。その後POA-1 / POA-2実装とtask review、POA-3
closeout candidateまで進んでいる。これはHuman plan approval、canonical final whole-branch review、
`LOCAL_COMPLETE`、remote action authorizationを意味しない。

## Goal

Human approval を North Star と Written Spec に限定し、承認済み scope 内の plan creation、repair、
review、readiness、task ordering、serialized integration、combined verification を agent / repository
ownership に移す。

## Architecture

current `sdd-implementation` の Superpowers-first lifecycle と Planning Controller / fresh worker 分離は
維持する。新しい local Plan Contract Overlay が durable plan schema、禁止内容、coverage invariant、
ordering / integration contract、readiness vocabulary を所有し、`planning-context.md` が fresh Plan
Author と独立 Plan Reviewer の routing と repair loop を接続する。production runtime、scheduler、
packet、event log、resume protocol、upstream fork は追加しない。

## Tech Stack

Markdown Skill instructions、Python 3.9+ standard-library `unittest` contract tests、Obsidian-compatible
LLM Wiki、current Superpowers lifecycle skills。

## Global Constraints

- Human-owned product boundary は approved North Star / Written Spec だけである。plan はその scope を
  拡張、縮小、再解釈しない。
- plan creation、review、repair、readiness は agent / repository ownership とし、Human plan approval
  または execution-choice promptを追加しない。
- Human へ戻すのは material North Star / Written Spec change または repository evidence だけでは
  解消できない material decision の一件だけである。
- remote、privileged、destructive action の separate authorization boundary を維持する。その未承認は
  対象 action だけを止め、plan readiness や local completion を遡って block しない。
- `superpowers:writing-plans` を required methodology として維持し、fork、vendor、copy、replacementを
  作らない。
- upstream の task sizing、file responsibility、TDD sequence、interface reasoning、self-review を使うが、
  durable plan に prospective production / test code、script body、patch body、擬似 patch、commit command
  body を保存しない。
- exact path は current-tree責務の識別に必要な範囲だけ記録する。line range、shell command、snippet、
  commit boundary は durable plan の required content や Human checkpoint にしない。
- portable contract は inputs、outputs、required capabilities で記述し、concrete runtime、tool name、
  model、provider、agent ID、run-specific routing を固定しない。
- task implementation と task review は canonical SDD に従って一件ずつ完了させる。並列 issue adapter は
  本変更へ適用しない。
- plan 本体を runtime ledger にしない。実行時のtuple、task result、review evidence、recovery state は
  ordinary plan-owned transient progress ledger に保持する。
- historical plan / approval / execution evidence は書き換えず、current design page には supersession
  relation と landed behavior だけを同期する。
- `knowledge/raw/**` は変更しない。

## File Responsibility Map

| Path | Operation | Responsibility |
|---|---|---|
| `skills/sdd-implementation/references/plan-contract.md` | Create in POA-2 | repo-local Plan Contract Overlay、plan semantic fields、coverage / order / integration invariants、禁止内容、review / readiness taxonomy の正本 |
| `skills/sdd-implementation/tests/fixtures/plan-contract/ready-plan.md` | Create in POA-2 | implementation body を持たず、全 required semantic field を備える representative ready-plan fixture |
| `skills/sdd-implementation/tests/test_plan_contract.py` | Create in POA-1; repair only as needed in POA-2 | POA-1 が complete coverage、orphan / unknown ID、dependency cycle、ordering、integration、prohibited body、readiness mapping の executable RED contract を定義し、POA-2 は GREEN 化に必要な test-contract defect だけを修正する |
| `skills/sdd-implementation/SKILL.md` | Modify | input maturity、Durable Knowledge、Plan Stage、Implementation entry、remote authorization の user-facing portable contract |
| `skills/sdd-implementation/references/planning-context.md` | Modify | fresh Plan Author / independent Plan Reviewer dispatch、repair loop、Control Return mapping、Controller read boundary |
| `skills/sdd-implementation/prompts/plan-reviewer.md` | Create | independent reviewer の evidence scope、finding classification、`ready` / `issues_found` verdict と bounded return contract |
| `skills/sdd-implementation/tests/test_skill_contract.py` | Modify in POA-1 and POA-2 | POA-1 が overlay resource の欠落を RED にする strict reference-set expectation を定義し、POA-2 が resource を供給した同じ state 上で public lifecycle、Human approval boundary、remote-action isolation の GREEN contract を追加する |
| `skills/sdd-implementation/tests/test_preimplementation_context.py` | Modify in POA-1 and POA-2 | POA-1 が overlay resource の欠落を RED にする strict reference-set expectation を定義し、POA-2 が overlay / fixture の供給と author/reviewer isolation、repair routing、readiness-to-Control-Return mapping、Controller non-ownership の GREEN contract を追加する |
| `knowledge/wiki/syntheses/sdd-implementation-skill-design.md` | Modify at closeout | broader current design に landed Plan Stage ownership と supersession relation を統合 |
| `knowledge/wiki/syntheses/sdd-preimplementation-context-isolation-spec.md` | Modify at closeout | current context-isolation design の Plan Author seam に successor relation を明記し、historical evidence は保持 |
| `knowledge/wiki/syntheses/sdd-plan-ownership-alignment.md` | Modify at closeout | implementation result、acceptance evidence、current lifecycle state を product boundary を変えずに同期 |
| `knowledge/index.md` | Modify | current spec / plan / landed design の canonical discoverability を一意に維持 |
| `knowledge/log.md` | Modify | plan authoring、implementation closeout、review / verification effect を append-only で追跡 |

## Task Decomposition

### Task 1: POA-1 — Plan Contract の executable RED regression

**Deliverable:** approved spec の plan-level / task-level fields、coverage、dependency、execution / integration、
combined verification、prohibition、readiness vocabulary を executable tests と strict resource-shape expectations
として固定し、未実装の overlay / representative fixture の欠落だけを原因に意図した RED になる。

**Coverage:** contributing `R-02`、`R-05`〜`R-15`、`AC-02`〜`AC-12`。POA-1 はこれらの
RED evidence contract を所有し、最終 behavior の primary owner は GREEN 化を所有する POA-2 とする。

**Dependencies:** なし。approved spec と current upstream `writing-plans` を直接 consume する。

**Behavioral interface:**

- Consumes: approved spec identity、requirement / acceptance inventory、current upstream plan methodology、
  repository file responsibility evidence。
- Produces: executable RED tests、complete requirement / acceptance inventory assertions、strict reference-set
  expectations、期待する failure reason と GREEN pass condition。
- Does not produce: `plan-contract.md`、representative ready-plan fixture、Plan Stage routing / prompt、GREEN
  implementation、scheduler、runtime validator service、worker packet、prospective implementation body、upstream skill copy。

**Files:** create `tests/test_plan_contract.py`; modify only the strict reference-set expectations in
`tests/test_skill_contract.py` and `tests/test_preimplementation_context.py`。POA-1 は overlay / fixture / routing /
prompt を作成しない。

**TDD and verification intent:**

1. RED contract authoring: define the representative-plan validator and mutations for approved-spec identity、
   complete inventory / coverage、unknown ID、orphan task、undefined dependency、cycle、execution order、
   serialized integration / combined verification、prospective body、Human plan-approval language。
2. Expected RED evidence: contract tests fail because `plan-contract.md` and ready-plan fixture are absent、and both
   strict resource-shape suites fail because `plan-contract.md` is absent。Import、syntax、test discovery、or
   unrelated assertion failure does not satisfy this gate。
3. Review gate: the POA-1 reviewer confirms the tests express approved-spec behavior、the exact expected failures
   are recorded、the changed paths contain tests only、and no overlay / fixture / production routing was introduced。
4. Transition: reviewed intentional RED is POA-1's completion condition and I-1 precondition。It is not Plan
   Readiness `ready`、not product GREEN、and not permission to skip POA-2。

**Integration placement:** first as a reviewed intentional-RED checkpoint。Task POA-2 consumes the executable
failure contract and is solely responsible for turning the combined state GREEN。

**Failure owner:** Task POA-1 implementer repairs RED test semantics / harness defects; independent task reviewer
verifies spec fit、expected-failure provenance、and absence of premature implementation。

### Task 2: POA-2 — Agent-owned Plan Stage routing と independent review loop

**Deliverable:** POA-1 の reviewed RED contract を local Plan Contract Overlay、representative fixture、
compatibility repair、Plan Stage routing / reviewer prompt で GREEN にする。Planning Controller は approved spec と
bounded paths を fresh Plan Author へ渡し、author self-review 後に独立 Plan Reviewer を dispatchし、
plan deficiency を Human へ返さず修復し、`ready` だけを Implementation Stage entry へ接続する。

**Coverage:** primary `R-01`〜`R-15`、`AC-01`〜`AC-13`。contributing `AC-14`。POA-2 が
overlay / fixture / routing / prompt と、POA-1 の executable contract を GREEN にする全 compatibility / route
test changes を所有する。

**Dependencies:** reviewed intentional-RED Task POA-1 integrated at I-1。POA-2 は POA-1 が作成した
executable failure contract と strict reference-set expectations を consume する。POA-1 GREEN、overlay、fixture、
reviewer prompt、or routing implementation を predecessor output として要求しない。

**Behavioral interface:**

- Consumes: approved spec path / approval state、trusted worktree and baseline binding、upstream skill path、
  POA-1 executable RED contract / strict resource expectations、Plan Author result、independent reviewer verdict。
- Produces: local Plan Contract Overlay、representative ready-plan fixture、focused / compatibility GREEN、fresh
  author dispatch、fresh independent review、internal `needs_repair` loop、material conflict onlyの`needs_decision`、
  non-decision blockerの`blocked`、`ready`から既存Control Return `complete`への一意 mapping。
- Preserves: Planning Controller の bounded read set、Superpowers lifecycle ownership、Human Written Spec authority、
  implementation task review、knowledge closeout、remote authorization boundary。

**Files:** create `references/plan-contract.md`、`tests/fixtures/plan-contract/ready-plan.md`、
`prompts/plan-reviewer.md`; modify `SKILL.md`、`references/planning-context.md`、
`tests/test_plan_contract.py`、`tests/test_preimplementation_context.py`、`tests/test_skill_contract.py`。The test
files are shared sequentially: POA-2 preserves POA-1's reviewed RED intent、repairs any contract-test defect needed
to exercise that intent、provides the missing resources、and adds only the Plan Stage routing / prompt assertions it owns。

**TDD and verification intent:**

1. Pre-implementation observation: I-1 is intentionally RED for the exact missing overlay / fixture reasons。Before
   changing the implementation、routing-focused tests also expose current literals requiring an approved /
   repository-approved plan、missing independent reviewer seam、missing repair disposition、and the existing
   prompt-set expectation。
2. GREEN implementation: create the overlay and fixture、repair strict resource compatibility、then change routing /
   prompt / focused tests so Human approval subjects are only North Star / Written Spec、Plan Author and
   Reviewer are isolated、`issues_found` is deterministically classified、`needs_repair` never leaves the agent loop、
   only material spec conflict yields one decision request、and remote-action authorization is not a plan blocker。
3. GREEN gate: the plan-contract、public-contract、and pre-implementation-context suites all pass together。
   No expected RED remains at POA-2 completion。
4. Forward evidence: representative plan flows cover ready、unassigned acceptance repair、prospective-body repair、
   dependency-cycle repair、current-tree method correction、material spec conflict、serialized integration、and
   unauthorized remote publication without changing local readiness。

**Integration placement:** second, after the reviewed POA-1 intentional-RED commit is reachable on the integration
target。I-2 is the first GREEN combined state。POA-2 must not duplicate the overlay schema inside `SKILL.md` or
`planning-context.md`。

**Failure owner:** Task POA-2 implementer owns overlay / fixture / compatibility / route / prompt / test defects;
independent task reviewer verifies authority boundaries and current-tree buildability。Only an evidenced material
spec conflict returns to Human authority。

### Task 3: POA-3 — Durable closeout と combined repository verification

**Deliverable:** landed Plan Stage semantics、supersession relations、canonical discovery、append-only lifecycle
recordが一致し、full integrated branch が全 acceptance と repository authoring / architecture checks を満たす。

**Coverage:** primary `AC-14`。contributing `R-01`〜`R-15`、`AC-01`〜`AC-13`。

**Dependencies:** POA-1 の reviewed RED result、POA-2 の reviewed combined-GREEN result、integrated
changed-path revalidation がすべて完了していること。

**Behavioral interface:**

- Consumes: reviewed POA-1 / POA-2 results、actual changed paths、fresh focused validation evidence、approved spec
  identity、current / historical design identities。
- Produces: current designのlanded contract、supersession relation、canonical index entry、append-only closeout、
  final whole-branch review candidate。
- Preserves: historical plan / approval / execution evidence、raw sources、planのnon-ledger boundary、separate
  remote authorization。

**Files:** modify `sdd-implementation-skill-design.md`、`sdd-preimplementation-context-isolation-spec.md`、
`sdd-plan-ownership-alignment.md`、`knowledge/index.md`、`knowledge/log.md`。本plan本文はruntime result ledgerへ
変換しない。

**TDD and verification intent:**

1. Baseline observation: current catalog and current design do not yet expose the Plan Contract Overlay or its
   supersession relation; append-only log has no implementation-closeout event for this change。
2. GREEN behavior: one canonical relation for spec and plan is discoverable、broader SDD design points to the local
   Plan Stage authority、historical records remain historical、and closeout records exact fresh evidence without
   claiming remote action or final review before it occurs。
3. Final evidence: focused SDD tests、repository script tests、LLM Wiki tests、skill architecture validation、skill
   context validation / warning-free report、skill authoring validation、knowledge link / index / log inspection、
   complete branch whitespace check、original-checkout preservation、fresh whole-branch review all succeed。

**Integration placement:** third and last。Knowledge closeout is integrated only after POA-1 and POA-2 are reachable
and reviewed。Final whole-branch review happens once after this closeout candidate。

**Failure owner:** Task POA-3 knowledge worker repairs authoring / discoverability / provenance defects; implementation
or integration failures return to the owning POA task; one bounded final fixer and one scoped re-review handle a material
final-review finding under the existing SDD contract。

## Dependency Graph

| Task | Direct predecessors | Dependency reason |
|---|---|---|
| POA-1 | none | Defines the executable RED contract and exact expected failures consumed by GREEN implementation |
| POA-2 | POA-1 | Must implement overlay / routing against the reviewed RED contract; does not depend on predecessor GREEN or overlay output |
| POA-3 | POA-1, POA-2 | Can close out only reviewed landed behavior and actual integrated paths |

The graph is acyclic。The only topological execution order is `POA-1 → POA-2 → POA-3`。

## Execution Order

1. Execute POA-1 as the test-first contract task。Record the exact overlay / fixture absence failures、prove the
   harness and test syntax are sound、obtain independent task review of that intentional RED deliverable、then
   integrate it at I-1。Do not create the overlay / fixture or claim product GREEN in POA-1。
2. Execute POA-2 from reviewed I-1 RED。Create the overlay / fixture、apply routing / prompt / compatibility-test
   changes、and require the complete focused group to turn GREEN before independent task review and I-2。
3. Revalidate actual result paths and spec binding, then execute POA-3 durable closeout and integrated checks。
4. Dispatch one canonical fresh whole-branch review after closeout。If it finds a material defect, use the existing one-fixer、
   one-scoped-re-review boundary; do not repeat the whole-branch review。

### POA-1 → POA-2 Gate Transition

POA-1 は「実装済み behavior」ではなく「実行可能な期待 failure contract」を deliver する特別な
test-first task である。そのため task completion / dependency satisfaction と product GREEN を次のように
分離する。

1. POA-1 completion: test syntax / discovery が正常で、recorded failures が missing overlay / fixture と
   それに紐づく strict resource expectation に限定され、independent review が test contract を承認する。
2. Dependency release: その reviewed RED commit が I-1 で reachable になった時点で POA-2 を開始できる。
   POA-1 GREEN、overlay、fixture、routing output はこの precondition ではない。
3. POA-2 completion: POA-2 が overlay / fixture / compatibility / routing / prompt を実装し、POA-1 の RED
   contract と POA-2 route tests が全て GREEN になり、independent review が承認する。
4. GREEN release: I-2 後にだけ POA-3、Plan Readiness evaluation、その他の GREEN state consumer
   は進行できる。I-1 の intentional RED を repository-ready または implementation-ready とみなさない。

## Serialized Integration Order

Execution order describes when work is performed; this section describes when reviewed results become part of the
integration target。

| Integration slot | Preconditions | Integrated result | Combined-state expectation |
|---|---|---|---|
| I-1: POA-1 | contract test syntax / discovery is valid、failures are exactly the declared missing overlay / fixture and strict resource expectations、independent task review ready、actual paths are test-only | executable RED contract tests and strict resource-shape expectations | integration target is intentionally RED for the recorded reasons; no overlay / fixture / routing implementation is present and no Plan Readiness claim is made |
| I-2: POA-2 | I-1 reachable、overlay / fixture and routing changes make plan-contract / public-contract / pre-implementation-context suites GREEN together、independent task review ready、no undefined overlay reference | local overlay、representative fixture、compatibility repair、agent-owned route、review prompt、repair / readiness mapping | the reviewed RED contract is satisfied; authoring、review、repair、Control Return mapping form the first coherent GREEN Plan Stage and Human plan approval is absent |
| I-3: POA-3 | I-1 and I-2 reachable and reviewed、all required task results present、current spec binding valid | canonical knowledge closeout and final-review candidate | code / tests / current design / spec relation / index / log describe the same integrated behavior |

Integration is single-writer and serialized。A clean textual merge、partial task presence、unreviewed result、or missing
required task result is not integration completion。

## Post-Integration Combined Verification

**Scope:** the complete baseline-to-integration-branch range、all `skills/sdd-implementation` instructions / prompts /
references / tests、the approved spec and this plan、current SDD design pages、`knowledge/index.md`、`knowledge/log.md`、
repository skill architecture and knowledge contracts。

**Pass criteria:**

- SDD focused suite passes, including all nine contract regression families and eight forward scenarios from the spec。
- all `R-01`〜`R-15` and `AC-01`〜`AC-14` retain exactly one primary owner and integrated evidence; POA-1 RED evidence and POA-2 GREEN behavior remain distinguishable、and unknown or orphan IDs are absent。
- dependency graph is acyclic; declared execution order is topological; serialized integration and combined verification
  fields are present and internally consistent。
- no durable plan or routing instruction contains prospective production / test body、script / patch body、commit
  command body、Human plan-approval prompt、or Human execution-choice prompt。
- existing first-write worktree、Planning Controller、implementation review、final review、portable capability、remote
  authorization tests remain green。
- repository script tests、skill architecture validation、skill context validation and warning-free report、
  `sdd-implementation` skill authoring validation、LLM Wiki tests、index / log semantic inspection all pass freshly。
- complete branch whitespace validation is clean and the original checkout matches its captured starting state。
- one fresh whole-branch reviewer reports no material requirement gap、scope excess、observable regression、or current risk。

**Required evidence:** fresh test / validator summaries with counts and exit state、coverage inventory result、actual changed
path set、task-review verdicts、whole-branch review verdict、original-checkout preservation result。Evidence belongs in the
transient progress ledger and append-only closeout log, not in this plan as a runtime event stream。

**Failure owner:** a focused failure returns to the POA task that owns the affected contract。A cross-task integration
failure is owned by the integration fixer。A knowledge-only failure is owned by POA-3。A material spec conflict alone
returns one decision request to Human; capability / authority / binding failure returns `blocked` with no decision request。

## Completeness Mapping

### Requirements

| ID | Primary task | Contributing task | Planned evidence |
|---|---|---|---|
| R-01 | POA-2 | POA-3 | approval-boundary contract and route tests |
| R-02 | POA-2 | POA-1, POA-3 | no-plan-approval contract and prohibited-language regression |
| R-03 | POA-2 | POA-3 | material-conflict-only decision routing |
| R-04 | POA-2 | POA-3 | action-specific authorization isolation regression |
| R-05 | POA-2 | POA-1, POA-3 | author / reviewer / repair ownership and isolation tests |
| R-06 | POA-2 | POA-1, POA-3 | required task-field fixture and contract checks |
| R-07 | POA-2 | POA-1, POA-3 | full coverage matrix validation with primary / contributing ownership |
| R-08 | POA-2 | POA-1, POA-3 | acyclic graph and topological-order validation |
| R-09 | POA-2 | POA-1, POA-3 | distinct execution / serialized integration schema and flow |
| R-10 | POA-2 | POA-1, POA-3 | combined-verification scope / criteria / evidence / owner checks |
| R-11 | POA-2 | POA-1, POA-3 | prohibited-body regression and artifact inspection |
| R-12 | POA-2 | POA-1, POA-3 | method metadata remains agent-owned and non-Human checkpoint |
| R-13 | POA-2 | POA-1, POA-3 | external upstream dependency and methodology preservation |
| R-14 | POA-2 | POA-1, POA-3 | explicit local precedence without upstream copy |
| R-15 | POA-2 | POA-1, POA-3 | portable Inputs / Outputs / Capabilities and fail-closed tests |

### Acceptance Criteria

| ID | Primary task | Contributing task | Planned evidence |
|---|---|---|---|
| AC-01 | POA-2 | POA-3 | only North Star / Written Spec approval checkpoints remain |
| AC-02 | POA-2 | POA-1, POA-3 | no Human method-choice or prospective-code judgement route |
| AC-03 | POA-2 | POA-1, POA-3 | independent review and `ready`-only stage entry |
| AC-04 | POA-2 | POA-1, POA-3 | exact task-to-requirement / acceptance trace with primary owners |
| AC-05 | POA-2 | POA-1, POA-3 | unassigned / orphan / undefined dependency rejection |
| AC-06 | POA-2 | POA-1, POA-3 | graph、execution order、serialized integration consistency |
| AC-07 | POA-2 | POA-1, POA-3 | integrated-state verification covers every acceptance |
| AC-08 | POA-2 | POA-1, POA-3 | prohibited prospective body checks |
| AC-09 | POA-2 | POA-1, POA-3 | agent repair loop never becomes a Human plan question |
| AC-10 | POA-2 | POA-1, POA-3 | deterministic `needs_decision` / `blocked` distinction |
| AC-11 | POA-2 | POA-1, POA-3 | upstream required, local output / routing precedence |
| AC-12 | POA-2 | POA-1, POA-3 | portable contract、binding、knowledge sync、fail closed |
| AC-13 | POA-2 | POA-3 | remote / privileged / destructive isolation |
| AC-14 | POA-3 | POA-1, POA-2 | fresh focused、architecture、authoring、knowledge validation |

Coverage result: requirements `15/15` primary-owned、acceptance criteria `14/14` primary-owned、unassigned `0`、
orphan task `0`、unknown ID `0`。

## Readiness Contract

| Internal disposition | External Control Return | Implementation entry | Owner / next route |
|---|---|---|---|
| `ready` | `status: complete`; plan path; no decision request; no material risk | allowed after Controller verifies current spec binding and readiness evidence | Planning Controller passes the reviewed plan to Implementation Stage |
| `needs_repair` | no external return | forbidden | agent repairs exact deficiency and obtains independent re-review |
| `needs_decision` | `status: needs_decision`; one material decision; conflict and impact | forbidden | Spec Stage / Human authority resolves North Star or Written Spec conflict |
| `blocked` | `status: blocked`; no decision request; exact blocker | forbidden | capability、trusted binding、authority、write-boundary failure must be cleared |

Reviewer `issues_found` is not an external status。It must be classified into `needs_repair`、`needs_decision`、or
`blocked`。Remote authorization absence is none of these for Plan Readiness; it is evaluated only at the affected action。

## Plan Author Self-Review

- Spec coverage: pass。Every `R-01`〜`R-15` and `AC-01`〜`AC-14` has exactly one primary task and at least one planned evidence class。
- Task boundaries: pass。Each task has an independently reviewable deliverable and its own failure owner。
- Placeholder scan: pass。No deferred implementation placeholder or instruction to infer unspecified behavior remains。
- Interface consistency: pass。POA-2 consumes only POA-1's reviewed executable RED contract and strict resource expectations、then owns overlay / fixture / routing GREEN; POA-3 consumes reviewed POA-1 / POA-2 results、and no later task references an undefined predecessor output。
- Dependency / order consistency: pass。The graph is acyclic and execution / integration orders both respect it while remaining separately specified。
- Prohibited-body scan: pass。This plan contains no prospective production code、test code、script body、patch body、pseudo-patch、shell commit command、or Human execution-choice prompt。
- Scope check: pass。The plan changes only the current SDD Plan Stage contract、focused regressions、and required durable knowledge; it does not create a scheduler、runtime state、packet、event log、resume protocol、or upstream fork。
- Current-tree applicability: pass。All modify targets exist at baseline; all create targets are contained by the bound planning worktree and have explicit single responsibilities。
- Author verdict: `ready_for_independent_review`。その後のindependent review / repair / re-reviewは完了し、最終repository readinessは`ready`、decision requestとmaterial riskは`none`である。Planning Controllerのbinding確認後にControl Return `status: complete`としてImplementation Stageへentry済みである。canonical final whole-branch reviewと`LOCAL_COMPLETE`は本plan readinessとは別のpending gateである。

## Related Pages

- [[sdd-plan-ownership-alignment|SDD Plan Ownership Alignment 仕様]] — requirement、acceptance、authority boundary の binding source。
- [[sdd-implementation-skill-design|SDD Implementation Skill 設計]] — broader current lifecycle contract。
- [[sdd-preimplementation-context-isolation-spec|SDD 実装前コンテキスト分離仕様]] — Planning Controller / fresh worker boundary の current source。
