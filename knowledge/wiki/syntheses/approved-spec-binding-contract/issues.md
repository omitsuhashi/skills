# Loop Skill Approved Spec Binding Contract Issues

## 状態

ASBC-001 から ASBC-006 は local 実装・独立 review・full verification を完了した。2026-07-22 の利用者 feedback に基づく artifact lifecycle follow-up では、consolidated spec の exact path/raw-byte digest に対する Written Spec Gate 承認後、ASBC-007 と ASBC-008 を `COMPLETE`、ASBC-009 を local `PR_READY` とした。mandatory controller task review / broad whole-branch review後のpushとDraft PR #32更新だけが非blocking delivery stepとして残る。

## Source

- Epic ID: `approved-spec-binding-contract`
- Approved consolidated revision: [spec.md](spec.md)
- Approved revision digest: `sha256:2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`
- Artifact lifecycle Spec Gate approval: 2026-07-22T07:36:04+09:00 `session-user`
- Prior approved spec (historical Git path): `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-spec.md`。current treeではconsolidated revisionへsupersede済み。
- Spec digest: `sha256:6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`
- Spec Gate commit: `bbf1585e05ad510242af3e4fa59be2447574d6ea`
- Issue Gate commit: `fd6a3a38d52f1e83f293c133a6658912fbcdef99`
- Execution Plan Gate commit: `2b8623047f723ba433f25997080377e3dec81f1e`
- Spec Gate approval: 2026-07-21 `session-user`
- Issue Gate approval: 2026-07-21。ユーザーの「承認」「skill 作成のベストプラクティスに則った実装」依頼を、承認済み scope を変更しない本 ledger の実装承認とする。
- Remote policy: branch `codex/approved-spec-binding-contract` push and Draft PR #32 update approved; PR ready、merge、release、live install are not approved
- Current Input Packet v2: `knowledge/wiki/syntheses/approved-spec-binding-contract/input-packet.json`、raw SHA-256 `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`
- Tracked current Execution Envelope: なし。prior flat Envelopeはcurrent treeから削除し、次のinstantiated EnvelopeはGit common runtime rootだけに生成する。
- Approved binding gate commit: `ad9adeab69bcafd761d8457e9c33d1b4c26096d5`
- Local branch: `codex/approved-spec-binding-contract`

## Baseline RED Evidence

fresh agent が新仕様を読まず current skill だけを使った pressure test で、次を確認した。

- planning handoff は spec digest を “when available” とし、1 byte drift を機械的に停止できない。
- `loop-review-governance-input-packet.json` の保存 digest `97d2944021187b529761751b6dd5fb90547c131d5c9a9090adb32ff93fa5001f` と current spec digest `7f1ede3e01231b2cddd03336232ba81aa4efe61a0ecbb45a75cc50cc5b5c2cf5` が不一致でも、input packet validator と Required Immediate Guard は exit `0` / `ok=true` を返した。
- 現行 contract は「scope-neutral な変更」と合理化して execution を継続できる。digest-backed stop は存在しない。
- delivery pressure test では、spec file を変更しても normal terminal routing と explicit routing はともに `deliver`、delivery/resume validation はともに `ok=true` のままだった。explicit `deliver` は envelope/runtime 読み取り前に返り、resume は envelope/runtime/events だけを fingerprint する。targeted 33 tests はこの現行挙動を成功契約として通した。

この RED は production change 前に取得した。新仕様を baseline evaluator へ漏らしていない。

## Artifact Layout Baseline RED Evidence

2026-07-22 に、new layout と診断を渡さず current skill entrypoints だけを使う read-only evaluator 3件を実行した。

- planning evaluator 2件は spec、issues、implementation plan、Input Packetを`knowledge/wiki/syntheses/`直下へEpic prefix付きで平置きした。Epic directoryを選ぶ明示契約は見つからなかった。
- 一方でexecution evaluator 2件はEnvelope、runtime state、events、reports、reviews、decisions、deliveryをGit common runtime rootへ置き、Git非追跡と判断した。
- current repository testは`synthesis_root.glob("*input-packet.json")`と`glob("*execution-envelope.json")`を使い、nested Epic directoryを探索しない。
- current tracked Envelopeはhost-local absolute worktree pathを含む。runtime contractがGit非追跡を指示する一方、初回implementation planはEnvelopeをsynthesesへ追加・commitする手順だった。

このbaselineは「durable planning filesのfolder ownership不足」と「planning evidenceとruntime contractの不一致」を再現した。production skill/codeはまだ変更していない。

## Local Issue Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| approved-spec-binding-contract | ASBC-001 | Approved Spec Binding core と Input Packet v2 を実装する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-002, ASBC-003, ASBC-005 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-002 | Envelope v4 と worker/reviewer chain を current-only 化する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-004 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-003 | runtime/event/report/auxiliary/resume chain を current-only 化する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-004 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-004 | routing/review/completion/delivery gate を fail closed にする | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-006 | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-005 | planning/execution skill contract と legacy surface を更新する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-006 | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-006 | bootstrap seal、forward test、full verification、durable evidence を完了する | 承認済み | LOCAL_COMPLETE | 解消済み | なし | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-007 | Epic単位のdurable artifact layoutを契約化する | 承認済み | COMPLETE | 解消済み | ASBC-008 | Draft PR #32 | `10c0d0c..ce70e6c` review完了・open findingなし | Draft PR #32 |
| approved-spec-binding-contract | ASBC-008 | current Epicを新layoutへ移しruntime JSONをGit管理外にする | 承認済み | COMPLETE | 解消済み | ASBC-009 | Draft PR #32 | `ce70e6c..a15e7dc` review完了・open findingなし | Draft PR #32 |
| approved-spec-binding-contract | ASBC-009 | forward test・全検証・Draft PR更新を完了する | 承認済み | PR_READY | 解消済み | なし | Draft PR #32 | local self-review完了・controller review pending | Draft PR #32 update pending |

## Blocker Graph

```text
ASBC-001
  -> ASBC-002
  -> ASBC-003
  -> ASBC-005
ASBC-002 + ASBC-003 -> ASBC-004
ASBC-004 + ASBC-005 -> ASBC-006
ASBC-006 -> ASBC-007 -> ASBC-008 -> ASBC-009
```

- Dependency graph は順序どおり解消済み。first runnable issue は `ASBC-001` であり、最終 issue `ASBC-006` まで local completion 済み。
- `ASBC-002` と `ASBC-003` は ASBC-001 の sealed packet/ref API 固定後、`ASBC-004` は両 state artifact family 固定後、`ASBC-006` は ASBC-004 / ASBC-005 完了後に実行した。
- completion/delivery は ASBC-006 の acceptance/review/full verification 完了後にのみ local completion とした。
- follow-up は ASBC-007 の TDD contract変更、ASBC-008 のartifact migration/reseal、ASBC-009 のfresh-agent/full verificationとlocal risk reviewまで完了した。ASBC-009は`PR_READY`で、controller review後のpush/Draft PR更新だけがpending。
- Cyclic blocker: なし。

## ASBC-001: Approved Spec Binding core と Input Packet v2 を実装する

### 目的

raw-byte spec identity、safe repo-relative path、approval evidence、deterministic seal、chain verification の canonical owner を追加し、Input Packet v2 以外を拒否する。

### Scope

- `skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/approved_spec_binding.py`
- `skills/issue-implementation-loop/scripts/approved_spec_binding.py`
- Input Packet schema/template/validator/public CLI
- `skills/issue-implementation-loop/tests/test_approved_spec_binding.py`
- related validation helpers/tests

### Acceptance Criteria

- public `identify` / `seal` / `verify` が ASB-01〜ASB-09 と ASB-20〜ASB-21 を実 repo fixture で通す。
- seal は spec bytes を変更せず、expected digest と current bytes が異なる場合に atomic write を行わない。
- absolute、`.`、`..`、backslash、escape、symlink、non-regular file を stable error code で拒否する。
- Input Packet v2 の 7 top-level field、closed object、6-field approval scope、1件以上の work item を厳密に検証する。
- Input Packet v1 と optional digest semantics を成功させる branch/test を残さない。

### Non-goals

- signature、PKI、remote approval service。
- spec digest の自動更新、approval evidence の推測。

## ASBC-002: Envelope v4 と worker/reviewer chain を current-only 化する

### 目的

gate commit 付き `ApprovedSpecBindingRef` を Envelope v4 から executor/reviewer packet/report へ一貫して伝播する。

### Scope

- Execution Envelope schema/template/validator/reference/tests
- Worker/Reviewer Packet schema/template/builder/validator/reference/tests
- Worker/Reviewer Report schema/validator/tests
- `worker-packet-v1.schema.json` と version compatibility surface の削除

### Acceptance Criteria

- Envelope v4 は top-level binding を無条件必須とし、v1〜v3 を `SCHEMA_UNSUPPORTED` で拒否する。
- gate commit missing、非 ancestor、tree 内 spec/packet blob mismatch を ASB-26〜ASB-28 の code で拒否する。
- Worker/Reviewer Packet v3 と Report v2 は dispatch/runtime binding と一致しなければならない。
- Worker v1/v2 builder option、validator branch、positive compatibility tests を削除する。
- report intake は runtime A に binding B の report を受理しない。

### Non-goals

- branch policy、review range policy 自体の再設計。
- historical wiki artifact の削除や in-place migration。

## ASBC-003: runtime/event/report/auxiliary/resume chain を current-only 化する

### 目的

event fold、runtime rebuild、human wait、hardening registry、resume cache が active binding を失わない current-only epoch contract に置換する。

### Scope

- Event v2 / Runtime State v2 / Human Request v2 / Hardening Registry v2 schemas/templates/validators
- runtime rebuild、scheduler、candidate registry、resume brief metadata v3
- related fixtures/tests/references

### Acceptance Criteria

- 全 event と runtime state が同じ binding を持ち、mixed/unknown binding event fold を拒否する。
- Human Request と Hardening Registry は active runtime と異なる binding を `AUXILIARY_ARTIFACT_BINDING_MISMATCH` で拒否する。
- Resume metadata v3 は binding を必須とし、meta-less と v2 metadata の成功経路を削除する。
- reseal 後に旧 request/registry/cache をコピーして成功させない。
- Event/Runtime/Human Request/Registry v1 と Resume v2/meta-less は `SCHEMA_UNSUPPORTED` になる。

### Non-goals

- scheduler algorithm、human authority、hardening candidate policy の再設計。
- 旧 run の移行・resume。

## ASBC-004: routing/review/completion/delivery gate を fail closed にする

### 目的

state-changing operation のすべてで active binding を fresh verify し、explicit mode や completion/delivery が検証を迂回できないようにする。

### Scope

- operation selection、scheduler/dispatch/report intake
- review gate、execution result v2、delivery plan v2、delivery loader
- status diagnostics、completion/delivery tests/references

### Acceptance Criteria

- binding invalid 時、`status` だけ read-only success とし `binding_valid=false` / state advance blocked を返す。
- explicit `deliver`、resume、completion、review は binding guard より前に short-circuit しない。
- review approval は binding と `BASE_SHA..HEAD_SHA` の両方へ結び付く。
- Execution Result v2 と Delivery Plan v2 は active binding を必須にし、v1 を拒否する。
- ASB-04、ASB-12〜ASB-19、ASB-22、ASB-29〜ASB-30 を public entrypoint hook 経由で通す。

### Non-goals

- remote authorization、delivery mode、merge authority の変更。
- status 読み取り自体の禁止。

## ASBC-005: planning/execution skill contract と legacy surface を更新する

### 目的

user-facing surface を増やさず、planning が一度 seal し execution が自動検証する ownership seam を Codex/Hermes 共通 skill instructions と current docs に同期する。

### Scope

- `skills/grill-to-pr-loop/SKILL.md` と既存 references/tests/context contract
- `skills/issue-implementation-loop/SKILL.md` と既存 references/tests/context contract
- historical wiki index annotations
- active docs/tests の legacy wording と compatibility assumptions

### Acceptance Criteria

- skill description は trigger だけを記述し、contract 本文を frontmatter へ詰め込まない。
- planning/execution の owner、approval/reapproval、status exception、remote boundary が default reader surface から発見できる。
- verbose な新規 default reference を追加せず、既存 reference wording を置換・圧縮する。
- current docs から “when available” と legacy resumable/compatible の成功保証を除去する。
- historical packet/envelope JSON は保持するが、current validator では非実行であることを index に明記する。
- architecture/context/dual-host/skill-creator validators が成功する。

### Non-goals

- 新しい user-facing skill、`description.md`、consumer 固有 schema。
- live Codex/Hermes install。

## ASBC-006: bootstrap seal、forward test、full verification、durable evidence を完了する

### 目的

bootstrap approval を恒久 fallback にせず、実装済み v2 contract でこの spec 自身を seal/verify して acceptance と skill behavior を独立評価する。

### Scope

- normalized Input Packet v2 / Execution Envelope v4
- temporary repo/worktree acceptance fixtures
- fresh-agent planning/execution/delivery forward tests
- issue ledger、implementation plan、`knowledge/index.md`、`knowledge/log.md`

### Acceptance Criteria

- exact spec digest `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc` を Input Packet v2 へ seal し、gate commit を含む Envelope v4 を current validator が成功させる。
- baseline と同等の fresh prompts で、planning/execution/delivery の全 agent が stale binding を合理化せず停止する。
- ASB-01〜ASB-30、full loop tests、architecture/context/report/dual-host/creator validators、wiki tests、`git diff --check` が成功する。
- issue ごとの commit/evidence/review/verification と残余リスクを ledger/log に同期する。
- push、PR、merge、live install は行わない。

### Non-goals

- baseline raw response を repository へ保存すること。
- remote delivery や live environment の変更。

## ASBC-007: Epic単位のdurable artifact layoutを契約化する

### 目的

filename prefixへ依存するflat layoutを廃止し、durable planning rootの下に`<epic-id>/` ownershipを固定する。

### Scope

- `skills/grill-to-pr-loop/SKILL.md`、planning/handoff references、tests
- Input Packet v2 artifact layout validation、template、tests
- `skills/issue-implementation-loop` runtime/envelope references

### Acceptance Criteria

- `artifact_root`の末尾segmentが`epic_id`と一致しないpacketを`ARTIFACT_LAYOUT_MISMATCH`で拒否する。
- spec、local issue source、seal outputはすべて`<artifact_root>`直下だけをcurrent layoutとして受理する。
- planning skillは`<durable-planning-root>/<epic-id>/`と4つのcanonical basenameをdefault reader surfaceから提示する。
- execution skillはEnvelope以降のinstance artifactをGit common runtime rootへ置き、Git commit対象から除外する。

### Non-goals

- historical flat artifact全件のmigration。
- schema/template/test fixture JSONのGit除外。

## ASBC-008: current Epicを新layoutへ移しruntime JSONをGit管理外にする

### 目的

このEpicのdurable sourceをnested rootへ移し、host-local absolute pathを含むtracked Envelopeを削除してnew binding epochをsealする。

### Scope

- `knowledge/wiki/syntheses/approved-spec-binding-contract/{spec.md,issues.md,initial-implementation-plan.md,implementation-plan.md,input-packet.json}`
- old flat current artifact pathsの削除
- `knowledge/index.md`、append-only `knowledge/log.md`

### Acceptance Criteria

- final treeでcurrent spec/ledger/plans/packetはEpic directory内だけに存在する。
- `loop-skill-approved-spec-binding-contract-execution-envelope.json`はGit indexから削除される。
- new Input Packetはapproved consolidated spec digest、new canonical paths、ASBC-007〜ASBC-009を持ちpublic validatorを通る。
- gate commitはnew specとpacketのexact blobsを含み、new runtime EnvelopeはGit common runtime rootでのみ生成可能なcontractになる。

### Non-goals

- completed historical runtimeのresume。
- PR ready化、merge、release、live install。

## ASBC-009: forward test・全検証・Draft PR更新を完了する

### 目的

artifact lifecycleがfuture agentへ伝わることをfresh contextで確認し、repository全体の回帰検証後に既存Draft PRへ反映する。

### Scope

- no-guidance/current-guidance baselineとupdated-skill forward tests
- issue-loop、grill、wiki、scripts、architecture/context/dual-host/creator validators
- branch push、Draft PR #32 body/check summary更新

### Acceptance Criteria

- fresh evaluatorはspec/ledger/plan/packetをEpic directory、Envelope/runtime/events/reports/decisions/deliveryをGit common runtime rootへ置く。
- current test suitesと全repository validatorがwarning/errorなく成功する。
- final diff reviewでCritical/Important findingが0になる。
- pushは`codex/approved-spec-binding-contract`、PR操作はDraft PR #32更新だけに限定し、merge/live installを行わない。

### Non-goals

- final PR merge。
- marketplace publishまたはlive Codex/Hermes verification。

## Local Completion Evidence

各 `review/diff range` は Git の `base..head`、`landed commits` はその range 内で当該 issue に属する exact SHA を表す。

### ASBC-001

- Review/diff range: `2b8623047f723ba433f25997080377e3dec81f1e..ad9adeab69bcafd761d8457e9c33d1b4c26096d5`（landed commits: `f3820ca18f839d37a16eacd864650103d2e4fff8`、`a75611e8f78dd5d22dfb5e5f029e5b5182f47932`、`9fd5988af9a95202f540e4a2eaeaa05825f2a1a9`、`205409d04a5efdb813e97310309bb4cb39603481`、`ad9adeab69bcafd761d8457e9c33d1b4c26096d5`）。
- Landed scope: safe raw-byte identity、deterministic/atomic seal、stable error/host-capability surface、Input Packet v2、normalized packet seal。seal host が unsupported でも read-only status/recovery diagnostics だけは維持する。
- Review: 2 task-local cycle と status/guidance derivative review を完了。rollback recovery、parent swap、symlink、stable error、platform capability、read-only exception を修正し、open Critical / Important finding なし。
- Evidence: focused binding/validation/entrypoint と issue-loop full suite が各 cycle で成功。spec と packet の exact digest は不変。

### ASBC-002

- Review/diff range: `ad9adeab69bcafd761d8457e9c33d1b4c26096d5..1ef7fd9c23b7c114d0d2ff4ab9008319735b0b81`（landed commits: `9663919b83e4a7231ddcf04c8c82c4cd3eee534f`、`1ef7fd9c23b7c114d0d2ff4ab9008319735b0b81`）。
- Landed scope: Execution Envelope v4、gate commit/tree/ancestor verification、Worker/Reviewer Packet v3、Report v2、dispatch/runtime binding intake、legacy Worker V1 schema/options/branches の削除。
- Review: missing runtime binding と malformed `residual_risks` を public RED/GREEN で閉じ、open Critical / Important finding なし。
- Evidence: Envelope v4 validator `ok=true`。full issue-loop / grill、architecture/context/dual-host/creator validators が成功。

### ASBC-003

- Review/diff range: `1ef7fd9c23b7c114d0d2ff4ab9008319735b0b81..9eefaf5fb562f11344b10480b230b04a6033e0d1`（landed commits: `a44e36ba0a5d2385f99836ba14e63ba3dab94171`、`1b1c01508b4d87163e1252046dccde5af7b3617d`、`9eefaf5fb562f11344b10480b230b04a6033e0d1`）。
- Landed scope: Event / Runtime / Human Request / Hardening Registry v2、Resume metadata v3、shared binding epoch fold/rebuild、closed schemas、atomic resume snapshot publication、exact integer validation。
- Review: event/runtime closure、complete human request/registry validation、resume source-snapshot race、boolean-as-integer regression を閉じ、open Critical / Important finding なし。
- Evidence: final Task 3 issue-loop suite 188 tests、repository validators、immutable digest checksが成功。

### ASBC-004

- Review/diff range: `9eefaf5fb562f11344b10480b230b04a6033e0d1..be9bd7ff1bf03c535299325c7747b754763eb790`（landed commits: `e13668bfd17fe0e54d154237b38d79e781d1325e`、`4c3e03bed28a9d88f5dd873afd4c91dcf635c624`、`6e8cc84476dcb8c3d8e62871981a9b87f755be5c`、`be9bd7ff1bf03c535299325c7747b754763eb790`）。
- Landed scope: explicit routing 前の binding verification、read-only status、fresh review/report intake、Execution Result v2、Delivery Plan v2、terminal/delivery fresh binding、stable malformed-artifact errors。
- Review: 2 task-local cyclesと local-only epic-base derivative review を完了。`batch_issue_prs` だけが live exact epic-base ref を要求し、`local_only` は planned ref を許す approved boundary を復元。final derivative review は Critical / Important / Minor すべて 0。
- Evidence: final Task 4 issue-loop suite 216 tests、grill 20 tests、repository validatorsが成功。

### ASBC-005

- Review/diff range: `be9bd7ff1bf03c535299325c7747b754763eb790..2ba3ce920b15b63a8e560d3eb8319882c153e775`（landed commits: `5bb00e78040acda5152a690352cf6f1c5d0b7456`、`f07a23f058cb0a05bbf212a31f9cb282f24930b4`、`f9d106534f9ee139b30413f0f2e7c2d03e3c1065`、`2ba3ce920b15b63a8e560d3eb8319882c153e775`）。
- Landed scope: trigger-only descriptions、portable installed-skill CLI resolution、complete six-scope seal recipe、exact restore/reseal/reapproval lifecycle、planning/execution default guards、active legacy wording除去、historical artifact index annotations。
- Review: 2 cycle と derivative closure を完了。final review は Critical / Important / Minor すべて 0。
- Evidence: grill 24 tests、issue-loop 219 tests、warning-free context report、architecture/context/dual-host/creator validatorsが成功。historical JSON bytes は変更していない。

### ASBC-006

- Review/diff range: `2ba3ce920b15b63a8e560d3eb8319882c153e775..b3bfa4b5a8cb1dd7788aa61398679ce6c5f995dd`（landed commits: `8401b7a40087075342e91df65792b1bb959e30c8`、`a405262512e05b36d5f5e37093aa02f8b6da6579`、`b3bfa4b5a8cb1dd7788aa61398679ce6c5f995dd`）。
- Landed scope: ASB-01〜ASB-30 の重複なし public acceptance matrix、connected reseal epoch、isolated Codex/Hermes CLI parity、complete current artifact/executable inventory、strict warning-free context baseline。
- Review: task-local 2 cycle後の focused reviewに続き、initial closeout後の whole-branch reviewと final hardening reviewを実施した。両 review wave の全 blockerに加えて Worker Packet binding metadata parity と strict context baseline self-consistencyを閉じ、commit `18a7fc4e8439421b28499f9105bf7653888b22de` の最終 focused reviewは Approved、Critical / Important / Minor すべて 0。
- Evidence: issue-loop 245 tests、grill 25 tests、llm-wiki 6 tests、scripts 59 tests、strict context report current / baseline operation count `8 == 8`、`warnings=[]`、全 repository/creator validators、Packet v2 / corrected Envelope v4 current validation が成功。

### ASBC-007

- Review/diff range: `10c0d0cffc5960c1a841b7fdacb0cd7a7b592e32..ce70e6cf8ddacc07948c72320443f306c32585b2`。
- Landed commit: `ce70e6cf8ddacc07948c72320443f306c32585b2` (`feat: separate durable and runtime epic artifacts`)。
- Landed scope: Epic単位のtracked durable root、canonical basenames、artifact layout validator、Git common runtime rootとのownership seam。
- Review: task-local review完了、open findingなし。
- Evidence: public ASB-31〜ASB-36、issue-loop 247 tests、grill 26 testsが成功し、seal capabilityは`approved_spec_seal.supported=true`。Input Packet v2 / Execution Envelope v4を含むschema versionは変更していない。

### ASBC-008

- Review/diff range: `ce70e6cf8ddacc07948c72320443f306c32585b2..a15e7dc04a7c830ac09773268a820479ff25cea2`。
- Landed commits: `bc1f32dd7a4ac01dd8651744ae7929402dfa9356` (`docs: group approved spec binding artifacts`) と `a15e7dc04a7c830ac09773268a820479ff25cea2` (`docs: record artifact lifecycle gate commit`)。
- Landed scope: consolidated spec/ledger/plans/sealed packetを`knowledge/wiki/syntheses/approved-spec-binding-contract/`へ集約し、指定されたflat current 5 artifactsだけを削除した。
- Binding: spec SHA-256 `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed packet SHA-256 `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`。
- Review: task-local migration review完了、open findingなし。
- Evidence: public seal、Input Packet validator、binding verify、issue-loop / grill / llm-wiki suitesが成功。nested packetはtracked、current instantiated EnvelopeはGit indexに存在しない。spec/packet bytesはgate commit後も不変。
- Remote/live action: なし。Draft PR更新、PR ready化、merge、release、live installはASBC-008では実行していない。

### ASBC-009

- Local verification range: `a15e7dc04a7c830ac09773268a820479ff25cea2..806917123a78d1b614861c3106c961f813ba5813`。closeout commitでlocal `PR_READY` evidenceを固定した。
- Fresh evaluator evidence: `cross-host-release-attestation`、`epic-runtime-boundary-audit`、`portable-approval-evidence-refresh`の3 read-only scenarioを、approved spec/desired answerを渡さずcurrent loop skill entrypointだけから評価した。3/3が`knowledge/wiki/syntheses/<epic-id>/{spec.md,issues.md,implementation-plan.md,input-packet.json}`をtracked durable tree、`$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/`配下のEnvelope/runtime treeをuntrackedと判断した。raw transcriptはcommitしていない。
- Full verification: issue-loop 247 tests、grill 26 tests、llm-wiki 6 tests、scripts 59 tests、architecture/context/strict context/dual-host/両creator validators、`git diff --check`が成功した。strict contextはissue-loop operation count `8 == 8`、top-level `warnings=[]`。initial briefのunsupported `--strict`はcurrent CLI/CI/test契約どおり`--require-baseline --fail-on-warning`へplan correctionした。
- Local risk review: `origin/main...HEAD`をspec/implementation alignment、host-specific tracked path、stale flat current link、historical migration、schema/version drift、remote-scope expansionの6観点で確認し、local Critical / Important findingは0。initial plan内のflat pathはhistorical archive、test helperのflat basenameはlegacy drift fixture用test-only hard-link shimでありcurrent guidance/runtime pathではない。
- Binding: spec SHA-256 `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed packet SHA-256 `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`。両bytesを編集していない。
- Delivery boundary: mandatory controller task review / broad whole-branch review、branch push、Draft PR #32 summary/check更新はpending。これはlocal correctness concernではなく、controllerがreview後に実行する非blocking remote delivery stepである。PR ready化、merge、release、live installは引き続き非承認。

## Whole-Branch Hardening Re-closeout

2026-07-21 の commit `6f0158c66710ee0dcce1f868d0fbe6c85bc72602` による初回 durable closeout は、その後の whole-branch review で completion claim を再オープンした。初回 log entry は当時の事実として保持し、以下の corrective evidence が supersede する。

### Review wave 1

- Review range: `cab8bd88351727f3495b657df447f7f64aa881d1..6f0158c66710ee0dcce1f868d0fbe6c85bc72602`。
- Verdict: Not ready。2 Critical / 6 Important。
- Critical: Envelope が sealed Input Packet の work items / write scope / dependencies / remote policy を exact projectionしておらず、Worker/Reviewer Packet が caller-supplied issue/task/scope semantics を受理できた。
- Important: Envelope closed/strict validation、runtime/rebuild post-fold fresh verification、remote-delivery command、approved eight-operation context contract、status diagnostic exception、exact `epic_base.sha` blob verificationが不足していた。
- Fix commit: `f8f69bb3b9396ee5daa49f0fb710a28e1086ee94` (`fix: bind approved intent end to end`)。Envelope intent correspondence、worker/reviewer projection、runtime/resume fresh verification、status/docs/context/remote-delivery contractを修正した。

### Review wave 2

- Review range: `6f0158c66710ee0dcce1f868d0fbe6c85bc72602..f8f69bb3b9396ee5daa49f0fb710a28e1086ee94`。
- Verdict: Not ready。2 Critical / 1 Important / 1 Minor。
- Critical: Envelope dependency edge の `strength` / `release_on` / `base_effect` が未bindingで、Worker/Reviewer validator が packet-selected worktree/source pathを trust rootとして扱い active Runtime epochを独立検証していなかった。
- Important / Minor: fixed policy boolean の exact type と Worker Packet schema-required field parityが不足していた。
- Fix commit: `7e9515a7e74f632c3202ae2ab81dd65e7102b4ac` (`fix: verify worker trust boundaries`)。dependency edge semantics、trusted repo/assigned worktree/active Envelope/Runtime boundary、exact primitive types、closed required fieldsを修正した。

### Final closure

- Final focused review range: `f8f69bb3b9396ee5daa49f0fb710a28e1086ee94..7e9515a7e74f632c3202ae2ab81dd65e7102b4ac`。
- Verdict: Approved。Critical / Important / Minor すべて 0。
- Corrected Envelope v4 raw SHA-256: `c15a7e9f4dc18acf8899f8e660f8f6eff8753f39b9f72a5772e44daf22d89497`。approved spec と sealed Input Packet bytes は変更していない。
- Remote/live action: なし。`local_only` boundaryを維持した。

### Final metadata parity micro-fix

- Fix commit: `18a7fc4e8439421b28499f9105bf7653888b22de` (`fix: close binding metadata parity`)。Worker Packet validatorで Envelope / Runtime / binding metadata の exact parityを固定し、strict context baselineの宣言 operation count と metrics count の self-consistency checkを追加した。
- Final focused review range: `7e9515a7e74f632c3202ae2ab81dd65e7102b4ac..18a7fc4e8439421b28499f9105bf7653888b22de`。
- Verdict: Approved。Critical / Important / Minor すべて 0。
- Approved spec / sealed Input Packet / corrected Envelope bytesは変更していない。remote/live actionはなく、`local_only` boundaryを維持した。

## Fresh-Agent Forward Tests

approved spec 本文、tests、ledger、plan、意図した回答を渡さず、current skill entrypoint/default reference だけを与えた3 evaluatorで確認した。raw response は repository へ保存していない。

- planning one-byte drift: seal/handoff を停止し、変更後の exact digest と6項目 approval、新 seal / Envelope / runtime epoch を要求した。
- urgent execution mismatch: urgency を理由に継続せず `BINDING_MISMATCH` / `blocked.reapproval` で dispatch/state advance を停止した。
- terminal runtime 後の stale delivery/resume: terminal result を grandfather せず、delivery、resume、rebuild、stale result reuse を停止した。
- 3 evaluator とも read-only diagnostic status だけを許可し、stale approval/Envelope/runtime/result を合理化しなかった。

## Final Verification

- Public acceptance: ASB-01〜ASB-36 を current public operations / real entrypoint hooks へ一意に mappingし、artifact lifecycle ASB-31〜ASB-36を含む全 row を実 test methodへ解決した。
- Local suites: issue-implementation-loop 247 tests、grill-to-pr-loop 26 tests、llm-wiki 6 tests、scripts 59 tests が成功。
- Repository checks: skill architecture、skill context、strict context report、dual-host compatibility、両 loop skill の skill-creator quick validation、`git diff --check` が成功。strict context report は current / baseline operation count `8 == 8`、`warnings=[]`。
- Current artifact checks: tracked Input Packet v2 はpublic validator / binding verifyで`ok=true`、current instantiated EnvelopeはGit indexに存在しない。consolidated spec / sealed packet SHA-256は`2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193` / `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`。
- Implementation review: ASBC-007 review range `10c0d0c..ce70e6c`とASBC-008 review range `ce70e6c..a15e7dc`はApproved、open findingなし。ASBC-009 local risk self-reviewはCritical / Important 0で、mandatory controller task review / broad whole-branch reviewはremote delivery前のpending gateとして残す。

## Residual Risks And Remote Boundary

- raw-byte identity は空白だけの変更でも再承認または packet reconciliation を要求する。exact revision contract の意図した保守性である。
- file descriptor validation 後の mutation は理論上残るため、各 state-changing boundary の fresh verification を省略できない。
- `actor_expression` は durable audit label であり、暗号学的本人性を証明しない。
- clean break により historical v1〜v3 artifact / old run は current validator で resume できない。operator action は migration ではなく new approval/new run である。
- Codex/Hermes parity は isolated host-like CLI と repository dual-host validator で確認した。live Codex/Hermes install/runtime は承認範囲外のため未検証・未変更。
- seal に必要な no-follow / descriptor-relative primitive がない host は state change を fail closed に停止する。read-only diagnostics のみ維持する。
- branch `codex/approved-spec-binding-contract`へのpushと既存Draft PR #32更新は承認済みだが、mandatory controller reviewを先に行うsequencingのためpending。PR ready化、merge、release、live installは非承認のまま。
- test-only legacy drift fixtureはnested spec bytesと同一inodeを変異させるhard-link compatibility shimを保持する。product/runtime artifactではなくGit layout contractを迂回しないが、fixture cleanup時の見直し対象である。
- Open implementation blocker: なし。

## Artifact Lifecycle Follow-up Gate

- Written Spec Gate: [spec.md](spec.md) のexact path/raw-byte digestとsix-part scopeを2026-07-22T07:36:04+09:00に`session-user`が明示承認済み。
- Follow-up issue count: 3（ASBC-007〜ASBC-009）。
- Dependency order: `ASBC-007 -> ASBC-008 -> ASBC-009`。
- First runnable issue after approval: ASBC-007。ASBC-007/ASBC-008は`COMPLETE`、ASBC-009はlocal `PR_READY`。
- Approved remote scope: branch `codex/approved-spec-binding-contract`へのpushと既存Draft PR #32更新のみ。
- Pending delivery: mandatory controller task review / broad whole-branch review後のpushとDraft PR #32 summary/check更新。
- PR ready化、merge、release、live installは非承認。

## Initial Issue Gate Record

- Approval: 2026-07-21 user approved implementation under skill best practices。
- Local issue count: 6。
- Dependency order: ASBC-001 -> ASBC-002 / ASBC-003 / ASBC-005 -> ASBC-004 -> ASBC-006。
- First runnable issue: ASBC-001。
- Scope change: なし。30 acceptance scenarios、clean break、dual-host、`local_only` は approved spec と同一。
- GitHub issue mirror、push、PR 作成、merge、live install は未承認。

## Verification Plan

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_approved_spec_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/llm-wiki/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

## Whole-Branch Final Review Corrective Wave

- Review range: `cab8bd88351727f3495b657df447f7f64aa881d1..e2db6bfc6e9690f0b3e4bac9e791853ca04b6431`。final reviewでCritical 1、Important 3、Minor 1を受領し、すべてlocal corrective waveでcloseした。
- Critical close: Worker Packetのtrusted runtime rootをlinked worktree内の`.git`表現ではなく、sanitized Git discoveryから得たactual coordinator Git common directoryへ固定した。exact runtime tree、descriptor-relative/no-follow load、regular-file/identity checksを必須化し、linked worktreeのpublic builder成功、symlink/mismatched Epic/arbitrary `.git` path拒否をpublic validator testで固定した。
- Important close: tracked JSON templatesとcurrent remote-delivery guidanceをnested durable artifact rootへ統一した。sealはatomic install後にもapproved spec identityを再確認し、concurrent spec mutation時は旧packetをrestore、旧packetがなければ新packetをremoveして`FILE_CHANGED_DURING_VALIDATION`で停止する。ASB-34〜ASB-36はそれぞれcurrent Git tracking、real linked-worktree runtime trust root、parsed tracked templatesを検証する一意のbehavior testへ置き換えた。
- Minor close: test-only hard-link compatibility shimとflat fixture aliasesを削除し、fixtureはexplicit nested durable pathsを直接使用する。上記Residual Risks And Remote Boundaryに残る「hard-link compatibility shimを保持する」という過去記録は本項でsupersedeされ、current treeには該当shimが存在しない。
- Fresh local verification: issue-implementation-loop 249 tests、grill-to-pr-loop 28 tests、llm-wiki 6 tests、scripts 59 testsが成功した。skill architecture/context、strict context report、dual-host、両loop skillのskill-creator validator、packet validation、binding verification、`py_compile`、`git diff --check`も成功し、strict reportは`warnings=[]`、各contractのminimum headroomは20%以上だった。
- Immutable artifact proof: approved spec SHA-256 `2bd4fcdbed9828c988a9d5c24cdd02242434f0e44e802cceb34fc4a0e7b86193`、sealed Input Packet SHA-256 `e7fd341ce0953a6245058db6326e7e275e70061fd33a11aefd05048397e8693c`。両bytesは変更していない。
- Gate state: ASBC-007/ASBC-008は`COMPLETE`、ASBC-009はlocal `PR_READY`のまま。mandatory controller whole-branch re-review/final reviewはpushとDraft PR #32更新前のpending gateであり、本waveではremote/live actionを行わない。

## ASB-34 Repository-Wide Tracked Envelope Re-review Correction

- Follow-up re-reviewでImportant 1を受領した。前waveのASB-34はcurrent nested Epic rootだけを`git ls-files`で確認していたため、`knowledge/wiki/syntheses/approved-spec-binding-contract-execution-envelope.json`のようなformer flat pathや別Epic pathにtracked current Execution Envelope v4が再出現しても検出できなかった。
- TDD RED: Git indexへflat v4 Envelope、historical v3 Envelope、malformed JSON、skill-assets配下のv4 product templateを同時に追加するfocused regressionを先に作成し、未実装scanner seamの`NameError`で1 testが失敗することを確認した。
- GREEN contract: ASB-34は`knowledge/wiki/syntheses`配下の全tracked JSONをrepository-wideに列挙し、working-tree bytesではなくGit index blobをparseする。JSONでないtracked contentは安全にskipし、`schema_version == 4`のcurrent instantiated Envelopeをpath layoutに依存せず拒否する。historical v1〜v3 evidenceは許容し、scope外のskill product templateをwiki artifactとして扱わない。
- Public acceptance mappingはcurrent repository ownership checkとdeterministic flat-v4 detection testの2 behaviorへASB-34をmappingした。focused ASB-34は2 tests、matrix resolutionは1 test、grill-to-pr-loopは29 testsが成功した。
- Full local suitesはissue-implementation-loop 249 tests、grill-to-pr-loop 29 tests、llm-wiki 6 tests、scripts 59 testsが成功した。approved spec/Input Packet bytesと全schema versionは変更していない。
- Gate stateは変更しない。ASBC-009はlocal `PR_READY`、mandatory controller whole-branch re-review/final reviewはpendingのままで、本correctionでもpush、PR #32 mutation、ready、merge、release、live installを行わない。
