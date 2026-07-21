# Loop Skill Approved Spec Binding Contract Issues

## 状態

Written Spec Gate / Issue Gate 承認済み。ASBC-001 から ASBC-006 は未実装。Execution Plan Gate、worker 実装、implementation review、push、PR、merge、live install は未完了。

## Source

- Epic ID: `approved-spec-binding-contract`
- 承認済み spec: [loop-skill-approved-spec-binding-contract-spec.md](loop-skill-approved-spec-binding-contract-spec.md)
- Spec digest: `sha256:6cedbba982f891d8ffceb9204bfc453b276df9e6021dca048cb0612d359a3dcc`
- Spec Gate commit: `bbf1585e05ad510242af3e4fa59be2447574d6ea`
- Spec Gate approval: 2026-07-21 `session-user`
- Issue Gate approval: 2026-07-21。ユーザーの「承認」「skill 作成のベストプラクティスに則った実装」依頼を、承認済み scope を変更しない本 ledger の実装承認とする。
- Remote policy: `local_only`

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
| approved-spec-binding-contract | ASBC-001 | Approved Spec Binding core と Input Packet v2 を実装する | 承認済み | READY | なし | ASBC-002, ASBC-003, ASBC-005 | 未作成 | 未実施 | 未作成 |
| approved-spec-binding-contract | ASBC-002 | Envelope v4 と worker/reviewer chain を current-only 化する | 承認済み | BLOCKED | ASBC-001 | ASBC-004 | 未作成 | 未実施 | 未作成 |
| approved-spec-binding-contract | ASBC-003 | runtime/event/report/auxiliary/resume chain を current-only 化する | 承認済み | BLOCKED | ASBC-001 | ASBC-004 | 未作成 | 未実施 | 未作成 |
| approved-spec-binding-contract | ASBC-004 | routing/review/completion/delivery gate を fail closed にする | 承認済み | BLOCKED | ASBC-002, ASBC-003 | ASBC-006 | 未作成 | 未実施 | 未作成 |
| approved-spec-binding-contract | ASBC-005 | planning/execution skill contract と legacy surface を更新する | 承認済み | BLOCKED | ASBC-001 | ASBC-006 | 未作成 | 未実施 | 未作成 |
| approved-spec-binding-contract | ASBC-006 | bootstrap seal、forward test、full verification、durable evidence を完了する | 承認済み | BLOCKED | ASBC-004, ASBC-005 | なし | 未作成 | 未実施 | 未作成 |

## Blocker Graph

```text
ASBC-001
  -> ASBC-002
  -> ASBC-003
  -> ASBC-005
ASBC-002 + ASBC-003 -> ASBC-004
ASBC-004 + ASBC-005 -> ASBC-006
```

- First runnable issue: `ASBC-001`。
- `ASBC-002` と `ASBC-003` は ASBC-001 の sealed packet/ref API が固定された後にだけ開始する。
- `ASBC-004` は全 state artifact の binding shape が揃うまで開始しない。
- `ASBC-006` までは completion/delivery を成功扱いにしない。
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
