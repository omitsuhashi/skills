# Loop Skill Approved Spec Binding Contract Issues

## 状態

Written Spec Gate / Issue Gate / Execution Plan Gate を通過し、ASBC-001 から ASBC-006 は 2026-07-21 に local 実装・独立 review・full verification を完了した。全 issue は `LOCAL_COMPLETE`。remote policy は承認どおり `local_only` であり、push、PR、merge、live install は意図的に実行していない。

## Source

- Epic ID: `approved-spec-binding-contract`
- 承認済み spec: [loop-skill-approved-spec-binding-contract-spec.md](loop-skill-approved-spec-binding-contract-spec.md)
- Spec digest: `sha256:6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`
- Spec Gate commit: `bbf1585e05ad510242af3e4fa59be2447574d6ea`
- Issue Gate commit: `fd6a3a38d52f1e83f293c133a6658912fbcdef99`
- Execution Plan Gate commit: `2b8623047f723ba433f25997080377e3dec81f1e`
- Spec Gate approval: 2026-07-21 `session-user`
- Issue Gate approval: 2026-07-21。ユーザーの「承認」「skill 作成のベストプラクティスに則った実装」依頼を、承認済み scope を変更しない本 ledger の実装承認とする。
- Remote policy: `local_only`
- Current Input Packet v2: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-input-packet.json`、raw SHA-256 `3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7`
- Current Execution Envelope v4: `knowledge/wiki/syntheses/loop-skill-approved-spec-binding-contract-execution-envelope.json`、raw SHA-256 `ac7630bf404b1c3607eb504bc18377bc45aef2c3b128be04e38d6737ca351af4`
- Approved binding gate commit: `ad9adeab69bcafd761d8457e9c33d1b4c26096d5`
- Local branch: `codex/approved-spec-binding-contract`

## Baseline RED Evidence

fresh agent が新仕様を読まず current skill だけを使った pressure test で、次を確認した。

- planning handoff は spec digest を “when available” とし、1 byte drift を機械的に停止できない。
- `loop-review-governance-input-packet.json` の保存 digest `97d2944021187b529761751b6dd5fb90547c131d5c9a9090adb32ff93fa5001f` と current spec digest `7f1ede3e01231b2cddd03336232ba81aa4efe61a0ecbb45a75cc50cc5b5c2cf5` が不一致でも、input packet validator と Required Immediate Guard は exit `0` / `ok=true` を返した。
- 現行 contract は「scope-neutral な変更」と合理化して execution を継続できる。digest-backed stop は存在しない。
- delivery pressure test では、spec file を変更しても normal terminal routing と explicit routing はともに `deliver`、delivery/resume validation はともに `ok=true` のままだった。explicit `deliver` は envelope/runtime 読み取り前に返り、resume は envelope/runtime/events だけを fingerprint する。targeted 33 tests はこの現行挙動を成功契約として通した。

この RED は production change 前に取得した。新仕様を baseline evaluator へ漏らしていない。

## Local Issue Ledger

| Epic ID | ローカルID | タイトル | レビュー状態 | 実行状態 | ブロック元 | ブロック先 | GitHub Issue | 実装レビュー | PR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| approved-spec-binding-contract | ASBC-001 | Approved Spec Binding core と Input Packet v2 を実装する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-002, ASBC-003, ASBC-005 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-002 | Envelope v4 と worker/reviewer chain を current-only 化する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-004 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-003 | runtime/event/report/auxiliary/resume chain を current-only 化する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-004 | 未作成（local_only） | 完了・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-004 | routing/review/completion/delivery gate を fail closed にする | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-006 | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-005 | planning/execution skill contract と legacy surface を更新する | 承認済み | LOCAL_COMPLETE | 解消済み | ASBC-006 | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |
| approved-spec-binding-contract | ASBC-006 | bootstrap seal、forward test、full verification、durable evidence を完了する | 承認済み | LOCAL_COMPLETE | 解消済み | なし | 未作成（local_only） | Approved・open finding なし | 未作成（local_only） |

## Blocker Graph

```text
ASBC-001
  -> ASBC-002
  -> ASBC-003
  -> ASBC-005
ASBC-002 + ASBC-003 -> ASBC-004
ASBC-004 + ASBC-005 -> ASBC-006
```

- Dependency graph は順序どおり解消済み。first runnable issue は `ASBC-001` であり、最終 issue `ASBC-006` まで local completion 済み。
- `ASBC-002` と `ASBC-003` は ASBC-001 の sealed packet/ref API 固定後、`ASBC-004` は両 state artifact family 固定後、`ASBC-006` は ASBC-004 / ASBC-005 完了後に実行した。
- completion/delivery は ASBC-006 の acceptance/review/full verification 完了後にのみ local completion とした。
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
- Review: 2 cycle後の final focused review は Critical / Important / Minor すべて 0。ASB-20 は real public CLI の repo escape、ASB-24 は bounded executable discovery で閉じた。
- Evidence: issue-loop 230 tests、grill 24 tests、llm-wiki 6 tests、strict context report `warnings=[]`、全 repository/creator validators、Packet v2 / Envelope v4 current validation が成功。

## Fresh-Agent Forward Tests

approved spec 本文、tests、ledger、plan、意図した回答を渡さず、current skill entrypoint/default reference だけを与えた3 evaluatorで確認した。raw response は repository へ保存していない。

- planning one-byte drift: seal/handoff を停止し、変更後の exact digest と6項目 approval、新 seal / Envelope / runtime epoch を要求した。
- urgent execution mismatch: urgency を理由に継続せず `BINDING_MISMATCH` / `blocked.reapproval` で dispatch/state advance を停止した。
- terminal runtime 後の stale delivery/resume: terminal result を grandfather せず、delivery、resume、rebuild、stale result reuse を停止した。
- 3 evaluator とも read-only diagnostic status だけを許可し、stale approval/Envelope/runtime/result を合理化しなかった。

## Final Verification

- Public acceptance: ASB-01〜ASB-30 を current public operations / real entrypoint hooks へ一意に mappingし、全 row を実 test methodへ解決した。
- Local suites: issue-implementation-loop 230 tests、grill-to-pr-loop 24 tests、llm-wiki 6 tests が成功。
- Repository checks: skill architecture、skill context、strict context report、dual-host compatibility、両 loop skill の skill-creator quick validation、`git diff --check` が成功。strict context report は `warnings=[]`、repository-wide 最小 headroom は 21%、affected issue-loop 最小 headroom は 26%。
- Current artifact checks: Input Packet v2 と Execution Envelope v4 は public validator で `ok=true`。spec / packet / envelope の raw SHA-256 はそれぞれ `6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`、`3779e815b4be7438b36e9fb53073fa1d3ab20f07cd5ad1c531fa075c11b457e7`、`ac7630bf404b1c3607eb504bc18377bc45aef2c3b128be04e38d6737ca351af4`。
- Implementation review: issue ごとの scoped review/fixを完了し、最終時点で open Critical / Important finding はない。

## Residual Risks And Remote Boundary

- raw-byte identity は空白だけの変更でも再承認または packet reconciliation を要求する。exact revision contract の意図した保守性である。
- file descriptor validation 後の mutation は理論上残るため、各 state-changing boundary の fresh verification を省略できない。
- `actor_expression` は durable audit label であり、暗号学的本人性を証明しない。
- clean break により historical v1〜v3 artifact / old run は current validator で resume できない。operator action は migration ではなく new approval/new run である。
- Codex/Hermes parity は isolated host-like CLI と repository dual-host validator で確認した。live Codex/Hermes install/runtime は承認範囲外のため未検証・未変更。
- seal に必要な no-follow / descriptor-relative primitive がない host は state change を fail closed に停止する。read-only diagnostics のみ維持する。
- push、GitHub Issue、PR、merge、live install は `local_only` policy により意図的に未実行。これらは別の明示承認なしに開始しない。
- Open implementation blocker: なし。

## Issue Gate 承認対象

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
