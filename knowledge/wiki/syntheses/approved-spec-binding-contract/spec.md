# Loop Skill Approved Spec Binding Contract 仕様

## 状態

2026-07-21 に承認された Approved Spec Binding 実装へ、Epic 単位の durable artifact root と Git 非追跡 runtime root を追加する consolidated revision candidate。2026-07-22 の user decision は設計方向を承認済みだが、この page の exact path/raw-byte digest に対する Written Spec Gate は未承認。approval decision は対象 spec bytes の中へ自己記録せず、`knowledge/log.md` と、承認後に再 seal する Input Packet v2 に記録する。

## Epic ID

`approved-spec-binding-contract`

## 問題設定

`grill-to-pr-loop` は人間が承認した planning spec を `issue-implementation-loop` へ渡すが、現行の executable contract は「同じ承認済み revision を prepare、executor、reviewer、resume、completion、delivery が使った」ことを機械的に保証していない。

- Input Packet v1 は `spec.path` だけを必須とし、`approved_revision` と `approved_hash` は任意である。
- input packet validator は spec file の存在、repo containment、symlink、digest、approval evidence を検証しない。
- Execution Envelope は input packet または approved spec の binding を持たない。
- Worker Packet V2 は envelope、runtime state、issue source だけを hash 化し、approved spec binding を伝播しない。
- runtime state、event、worker/reviewer report、resume metadata、execution result、delivery plan は同じ binding identity を要求しない。
- explicit `status` / `deliver` routing は artifact validation より前に決定でき、stale spec の再検証を迂回できる。
- Envelope v1〜v3、Worker Packet V1、metadata のない resume brief を受理する compatibility branch と成功テストが残っている。

実データでも、`knowledge/wiki/syntheses/loop-review-governance-input-packet.json` に記録された spec digest と現在の spec bytes が不一致であるにもかかわらず、現行 validator は成功する。これは単なる未実装ではなく、optional digest と legacy acceptance を正としている現行契約の gap である。

初回実装後の実利用では、同一 Epic の spec、ledger、plan、packet、Envelope が `knowledge/wiki/syntheses/` 直下へ長い prefix 付きで平置きされた。さらに tracked Envelope に host 固有の absolute worktree path が保存された。prefix は directory ownership の代替にならず、host-local execution context を Git の durable knowledge と混在させるため、artifact lifecycle の seam を追加で固定する。

## 契約目的

次の一方向 chain を、local-first かつ fail-closed に固定する。

```text
final spec raw bytes
  -> input packet の spec_binding + approval_evidence
  -> envelope の ApprovedSpecBindingRef
  -> runtime / events / executor packet / reviewer packet
  -> worker report / reviewer report / review approval
  -> execution result / completion / delivery
```

各 state-changing gate は同じ input packet bytes と、その packet が指す同じ spec bytes を fresh に検証する。どこか一つでも欠落、malformed、stale、不一致なら状態を進めず、適切な human gate へ戻す。

## 採用した判断

- 新しい user-facing skill と独立した `approved-handoff.json` manifest は追加しない。
- normalized input packet を spec binding と machine-readable approval evidence の唯一の正本にする。
- `grill-to-pr-loop` は final spec、human Spec Gate、承認対象 digest の提示、seal 開始を所有する。
- `issue-implementation-loop` は schema、path/digest rule、seal/verify の機械処理、全 execution-stage revalidation を所有する。
- physical implementation は `issue-implementation-loop` の internal deep module に置き、cross-skill seam は Python import ではなく sealed JSON packet と host-neutral CLI にする。
- Companies / CTO council front は common packet を渡す consumer に留め、固有 schema、queue、dispatcher、result store をこの契約へ追加しない。
- Codex と Hermes Agent は同じ `SKILL.md`、JSON artifact、Python CLI を使う。host 固有 session metadata は binding identity に含めない。
- persisted artifact から absolute `repo_root` を削除する。trusted repo/worktree root は実行時に caller または Git checkout から解決する。
- backward compatibility は実装しない。旧 artifact の migration/resume branch、shim、成功テストを残さない。
- durable planning root の直下へ `<epic-id>/` directory を必須化し、この repository のdefault basenameとして`spec.md`、`issues.md`、`implementation-plan.md`、`input-packet.json`を同居させる。
- Input Packet v2 は承認された execution intent の lock artifact であり、spec と同じ gate commit に含める。ファイル形式が JSON であることを理由に Git 管理から外さない。
- Execution Envelope v4 と、それ以後の instantiated JSON/JSONL artifact は coordinator-owned runtime context とし、`$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/` に保存して Git 管理しない。
- skill の schema、template、fixture は product contract であり、Epic instance artifact ではないため Git 管理を継続する。

## Artifact lifecycle contract

repository ごとの durable planning root を `<durable-planning-root>` とする。この repository では `knowledge/wiki/syntheses` である。新しい current Epic は次の tracked tree を持つ。

```text
<durable-planning-root>/<epic-id>/
├── spec.md
├── issues.md
├── implementation-plan.md
└── input-packet.json
```

- Input Packet `artifact_root` は `<durable-planning-root>/<epic-id>` と完全一致し、最後の path segment は packet の `epic_id` と一致しなければならない。
- `spec_binding.path`、local work item の `source.path`、seal output はすべて`<artifact_root>`直下に置く。この repository の新規artifactは`spec.md`、`issues.md`、`input-packet.json`を使う。
- repo-local ruleが別basenameを要求する場合はbasenameだけを置換できるが、Epic directory containmentは緩和しない。
- `artifact_root` 外の spec、ledger、packet output は `ARTIFACT_LAYOUT_MISMATCH` で fail closed にする。
- implementation plan は human-readable gate evidence であり packet binding の入力ではないが、同じ Epic directory に保存する。
- `knowledge/index.md` は nested relative path を catalog し、`knowledge/log.md` は gate/implementation/delivery timeline を append-only で記録する。

execution coordinator は次の untracked runtime tree を持つ。

```text
$(git rev-parse --git-common-dir)/agent-runs/issue-implementation-loop/<epic-id>/
├── execution-envelope.json
├── runtime-state.json
├── events.jsonl
├── reports/
├── reviews/
├── decisions/
├── recovery/
└── delivery/
```

- Envelope、runtime snapshot、event log、worker/reviewer packet/report、human request、decision registry、resume metadata、execution result、delivery plan は instantiated execution context として Git に commit しない。
- runtime root は Git common directory 内にあるため repository `.gitignore` entry を要求しない。別 runtime adapter を使う場合も tracked worktree 外を必須にする。
- Envelope に branch/worktree reservation の absolute path を持つことは許可するが、その host-local 値を durable planning artifact や binding identity として伝播しない。
- durable ledger は status、commit/review range、verification、remote delivery evidence、residual risk を記録する。runtime JSON の全文を履歴証拠として複製しない。

## Ownership と module boundary

内部 module の canonical owner は次とする。

`skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/approved_spec_binding.py`

公開する概念上の operation は 3 つに限定する。

```python
identify_spec(repo_root, spec_path) -> SpecRevision
seal_input_packet(repo_root, draft_packet_path, expected_spec_revision, approval) -> InputPacketRef
verify_chain(repo_root, artifact_refs) -> VerifiedBinding
```

- `identify_spec` は read-only で final spec の repo-relative path と exact raw-byte SHA-256 を返す。
- `seal_input_packet` は human に提示済みの expected digest と current bytes を再照合した場合だけ、approval evidence を packet に書き、sealed packet bytes の ref を返す。spec 自体は編集しない。
- `verify_chain` は artifact ごとの adapter、path safety、file identity、digest、schema、binding equality を内部に隠し、caller へ stable result/error だけを返す。

Codex / Hermes 共通 CLI adapter は 1 本とし、`identify`、`seal`、`verify` subcommand を提供する。`grill-to-pr-loop` は internal Python package を直接 import せず、この CLI と sealed packet contract を利用する。

## Input Packet v2

Input Packet v2 は `spec_binding` と `approval_evidence` を必須にする。

```json
{
  "schema_version": 2,
  "epic_id": "example",
  "artifact_root": "knowledge/wiki/syntheses/example",
  "spec_binding": {
    "path": "knowledge/wiki/syntheses/example/spec.md",
    "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  },
  "approval_evidence": {
    "decision": "approved",
    "subject": "spec_binding",
    "actor_expression": "requesting-human",
    "approved_at": "2026-07-21T17:00:00+09:00",
    "scope": {
      "accepted_decisions": true,
      "non_goals": true,
      "acceptance_criteria": true,
      "verification": true,
      "remote_policy": true,
      "stop_conditions": true
    }
  },
  "work_items": [
    {
      "id": "ASBC-001",
      "title": "短い日本語 issue タイトル",
      "source": {
        "type": "local",
        "path": "knowledge/wiki/syntheses/example/issues.md"
      },
      "acceptance_criteria": ["観測可能な受け入れ条件"],
      "non_goals": ["対象外の挙動"],
      "verification": ["python3 -m unittest discover -s tests"],
      "write_scope": ["path:skills/example"],
      "dependencies": []
    }
  ],
  "delivery_intent": "local_only"
}
```

契約上の意味は次のとおり。

- `spec_binding.sha256` は human に提示され、承認された final spec bytes の digest である。
- `approval_evidence` は sibling の `spec_binding` 全体を subject とし、別 revision や path へ転用できない。
- `actor_expression` は durable audit label であり、暗号学的な本人認証を主張しない。
- `approved_at` は timezone を含む RFC 3339 timestamp とする。
- `scope` の 6 field はすべて `true` を必須とし、欠落、`false`、未知 field を拒否する。
- spec 本文に自分自身の digest を書かない。spec 内には human-readable な承認範囲を置けるが、machine-readable approval record は packet にだけ置く。
- input packet は自分自身の digest を内包しない。後続 artifact が sealed packet の raw-byte digest を保持する。
- `additionalProperties` は契約 object ごとに `false` とし、typo や未検証 field を黙って受理しない。

v2 top-level の required/allowed field は `schema_version`、`epic_id`、`artifact_root`、`spec_binding`、`approval_evidence`、`work_items`、`delivery_intent` の 7 件だけとする。

- `artifact_root` は repo-relative Epic directory とし、write 前に containment、symlink rule、末尾 segment と `epic_id` の一致を検証する。
- `work_items` は 1 件以上を要求し、各 item は `id`、`title`、local `source.path`、`acceptance_criteria`、`non_goals`、`verification`、`write_scope`、`dependencies` を必須にする。
- sealed packet 内の `acceptance_criteria`、`non_goals`、`verification`、`write_scope`、`dependencies` が execution intent の正本である。source ledger は traceability evidence であり、後から packet の意味を上書きしない。
- `delivery_intent` は `local_only`、`per_action`、`batch_draft_prs`、`batch_issue_prs` のいずれかとする。

## ApprovedSpecBindingRef

Input packet より後の artifact は spec metadata を複製せず、同一 shape の ref を必須で持つ。

```json
{
  "approved_spec_binding": {
    "path": "knowledge/wiki/syntheses/example/input-packet.json",
    "sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
    "gate_commit": "0123456789abcdef0123456789abcdef01234567"
  }
}
```

`gate_commit` は spec と sealed packet の exact blobs を含む full Git object ID であり、Envelope 生成時に追加する。packet 自身へ gate commit を書くと commit hash の self-reference になるため、Input Packet v2 には含めない。validator は固定長を推測せず、current repository の object format に対する full lowercase object ID として Git で検証する。

current-only version と配置は次で固定する。version 番号は schema family の clean break を表し、旧 version の読み取り許可ではない。

| Artifact | Current version | Binding placement |
|---|---:|---|
| Input Packet | 2 | `spec_binding` + `approval_evidence` を所有 |
| Execution Envelope | 4 | top-level `approved_spec_binding` |
| Event | 2 | 全 event の top-level `approved_spec_binding` |
| Runtime State | 2 | top-level `approved_spec_binding` |
| Worker / Reviewer Packet | 3 | `source_revision.approved_spec_binding` |
| Worker / Reviewer Report | 2 | top-level `approved_spec_binding` と dispatch identity |
| Human Request | 2 | top-level `approved_spec_binding` |
| Hardening Candidate Registry | 2 | top-level `approved_spec_binding` |
| Resume metadata | 3 | `sources.approved_spec_binding` |
| Execution Result | 2 | top-level `approved_spec_binding` |
| Delivery Plan | 2 | top-level `approved_spec_binding` |

executor packet と reviewer packet は同じ schema family を使い、`task_kind` と access policy だけを変える。review approval は binding と `BASE_SHA..HEAD_SHA` の両方へ結び付ける。report intake は dispatch 時の binding と report の binding を比較し、runtime state の active binding と異なる report を受理しない。

runtime の routing、completion、delivery に影響する auxiliary artifact も binding chain の一部である。少なくとも human request と `decisions/hardening-candidates.json` は active runtime と同じ binding を必須にし、delivery loader は registry を読む前に検証する。reseal 後は旧 binding の registry/request をコピーせず、new binding の下で空から再生成するか human decision を明示的に再記録する。

## Approval と seal の順序

1. spec candidate の本文、accepted decisions、non-goals、acceptance criteria、verification、remote policy、stop conditions を最終化する。
2. `identify_spec` が final raw bytes を読み、path と SHA-256 を human へ提示する。
3. human は提示された path、digest、scope を明示承認する。
4. `seal_input_packet` は spec を再読し、承認時の expected digest と一致することを確認する。
5. seal は spec を変更せず、approval evidence を normalized packet へ deterministic に書く。
6. sealed packet と final spec を含む gate commit を作り、その commit を `epic_base` と全 issue/review worktree の ancestor にする。
7. Envelope v4 は gate commit、gate commit 内の packet path、packet raw-byte digest を取得し、`ApprovedSpecBindingRef` を完成させる。
8. prepare 以降は各 worktree 内の repo-relative projection を検証し、canonical checkout と同じ binding へ収束することを確認する。

spec 内に approval section を追記する場合は、追記後の bytes を新しい final bytes として digest を再提示し、再承認してから seal する。承認後の spec を seal 処理が編集してはならない。

## Worktree projection contract

- `spec_binding.path` と `approved_spec_binding.path` は repo-root-relative POSIX path とする。
- gate commit は `epic_base` の ancestor でなければならない。
- gate commit の tree に、binding が指す exact spec blob と exact packet blob が存在しなければならない。
- issue/review branch は gate commit から spec と packet の read-only copy を継承する。「planning artifact を issue branch に置かない」は「issue worker が author/edit しない」を意味し、worker から artifact が見えないことを意味しない。
- prepare は canonical checkout と `epic_base` projection の packet/spec digest が一致することを確認する。
- dispatch と review は assigned worktree 内の packet/spec を fresh に検証する。
- worker projection の artifact が missing、dirty replacement、digest mismatch、symlink の場合は scheduling または worker start 前に停止する。
- absolute planning checkout path を packet identity として伝播しない。worktree ごとに同じ repo-relative pathを trusted local root へ解決する。

## Path と digest の規則

- path は空でない repo-root-relative POSIX path だけを許可する。
- trusted repo/worktree root は caller または Git が与えた absolute directory を一度 canonicalize し、artifact field から上書きできない。
- absolute path、`~`、backslash、空 segment、`.`、`..`、repo escape を拒否する。
- repo root から target まで、親 component と final target の symlink をすべて拒否する。
- target は existing regular file でなければならない。
- SHA-256 は prefix のない lowercase `[0-9a-f]{64}` とする。
- digest は UTF-8/改行/Unicode/JSON whitespace を正規化せず、open file descriptor から読んだ exact raw bytes に対して計算する。
- deterministic packet serialization は UTF-8、unescaped Unicode、LF、2-space indent、lexicographic key order、末尾 newline とする。同じ意味でも packet bytes が変われば後続 ref は stale になる。

TOCTOU を完全に消せるとは主張しない。各検証では path component の `lstat`、no-follow open、`fstat` regular-file check、open descriptor からの streaming hash、hash 前後の device/inode/size/mtime 比較、hash 後の path identity 再確認を行う。検証中の mutation または atomic replacement は `FILE_CHANGED_DURING_VALIDATION` で拒否し、state-changing gate ごとに再検証する。

## Gate hook contract

| Boundary | Required behavior |
|---|---|
| Planning identify | final spec path/digest/scope を human へ提示 |
| Planning seal | expected digest を再照合し、spec 非変更のまま packet を atomic write |
| Prepare | packet→spec、envelope→packet、canonical→epic_base projection を検証 |
| Operation selection | explicit mode short-circuit より先に binding status を評価 |
| Status | read-only diagnostic は常に許可するが、`binding_valid=false` と state advance blocked を返す |
| Dispatch / fix redispatch | scheduling と packet build の前後で active binding を検証 |
| Worker start | assigned worktree projection と worker packet binding を検証 |
| Worker report intake | dispatch、runtime、report の binding 一致を検証 |
| Human wait / decision registry | request/registry と active runtime binding の一致を検証 |
| Review dispatch/start | reviewer packet、runtime、current spec、implementation range を検証 |
| Review report/approval | binding と `BASE_SHA..HEAD_SHA` の一致を検証 |
| Resume/rebuild | resume cache 使用前、event fold 前後に binding を検証。mixed/unknown binding event を拒否 |
| Completion/result | terminal transition 前に current spec と executor/reviewer/runtime binding を再検証 |
| Delivery | explicit `deliver` でも envelope→packet→spec と plan/result binding を fresh に検証 |

binding failure は `git_state_mismatch` や一般的な resume advisory に変換しない。planning/human re-approval が必要な独立 blocker として返す。

## Stable error contract

machine-readable failure は `valid=false`、stable `code`、`action`、対象 path/ref を返し、artifact や runtime state を変更しない。

| Code | Meaning | Action |
|---|---|---|
| `SPEC_MISSING` | spec target が存在しない | `return_to_spec_gate` |
| `APPROVAL_MISSING` | approval evidence がない | `return_to_spec_gate` |
| `APPROVAL_NOT_APPROVED` | decision が `approved` でない | `return_to_spec_gate` |
| `APPROVAL_SCOPE_INCOMPLETE` | 6 field のいずれかが欠落/false | `return_to_spec_gate` |
| `DIGEST_MISSING` | required digest がない | 対象 gate へ戻る |
| `DIGEST_MALFORMED` | digest format が不正 | 対象 gate へ戻る |
| `SPEC_DIGEST_MISMATCH` | current spec bytes が承認 digest と異なる | `return_to_spec_gate` |
| `INPUT_PACKET_DIGEST_MISMATCH` | descendant が pin した packet bytes と異なる | `return_to_execution_plan_gate` |
| `BINDING_MISMATCH` | artifact 間で path/hash が異なる | `return_to_execution_plan_gate` |
| `PROJECTION_MISSING` | worktree に spec/packet がない | `return_to_execution_plan_gate` |
| `PROJECTION_MISMATCH` | canonical/worktree bytes が異なる | `return_to_execution_plan_gate` |
| `GATE_COMMIT_MISSING` | binding が full gate commit を持たない | `return_to_execution_plan_gate` |
| `GATE_COMMIT_NOT_ANCESTOR` | gate commit が epic/worktree history にない | `return_to_execution_plan_gate` |
| `GATE_COMMIT_BLOB_MISMATCH` | gate commit 内の spec/packet blob が binding と異なる | `return_to_execution_plan_gate` |
| `AUXILIARY_ARTIFACT_BINDING_MISMATCH` | human request/decision registry が別 binding | new binding の下で再生成・再判断 |
| `PATH_ABSOLUTE` | absolute path | 対象 artifact を再生成 |
| `PATH_TRAVERSAL` | `.`, `..`, backslash 等 | 対象 artifact を再生成 |
| `PATH_OUTSIDE_REPO` | trusted root 外へ解決 | 対象 artifact を再生成 |
| `PATH_SYMLINK` | path component が symlink | 対象 artifact を再生成 |
| `PATH_NOT_REGULAR_FILE` | regular file でない | 対象 artifact を再生成 |
| `FILE_CHANGED_DURING_VALIDATION` | hash 中に identity/metadata が変化 | 再試行後も続けば停止 |
| `SCHEMA_UNSUPPORTED` | current-only version 以外 | new run を作る |
| `REAPPROVAL_REQUIRED` | active binding では続行不能 | `return_to_spec_gate` |

## Change と re-approval

- spec bytes が 1 byte でも変われば旧 approval は無効。human Spec Gate に戻り、new digest、new approval、new seal を作る。
- `spec_binding` または `approval_evidence` が変われば Spec Gate に戻る。
- spec/approval は同一だが sealed packet の issue scope、dependency、write scope、delivery intent 等が変われば Execution Plan Gate に戻る。
- new seal は new Envelope revision と new runtime epoch を要求する。
- 旧 binding の worker/reviewer packet、report、review approval、resume cache、execution result、delivery plan は再利用しない。
- 旧 binding の human request と hardening candidate registry は再利用しない。未解決 decision を持ち越す場合は new binding の下で human が再判断する。
- implementation commit を再利用する場合でも、new binding の reviewer packet と review range で再reviewする。
- verifier と seal command は approval evidence を推測、補完、自動更新しない。

## Bootstrap adoption rule

この契約自身の実装前には current-only validator がまだ存在しないため、旧 compatibility code を使って自己検証したとは扱わない。

- この written spec の human approval と、承認後に append する独立した `spec-approval` log entry を bootstrap approval evidence とする。candidate entry は approval evidence ではない。
- `spec-approval` entry は exact spec path、raw-byte SHA-256、6 項目の scope、`actor_expression`、timezone付き `approved_at` を必須で持つ。digest 提示後は spec bytes を変更せず、log だけを append する。
- この log evidence は本契約を実装する bootstrap authorization に限る。`seal` / `verify` が読む代替 approval source、恒久運用、compatibility branch として使わない。
- implementation plan はこの spec の exact path/digest を記録し、local-only の bounded implementation とする。
- binding module と current schema が landed した後、final review/completion 前にこの spec を Input Packet v2 へ seal し、new chain の acceptance scenarios を通す。
- bootstrap のために旧 packet/envelope/resume branch を追加または維持しない。

## Clean break と supersession

実装時に次を削除または置換する。

- Input Packet v1 semantics、`repo_root` persisted field、任意の `approved_revision` / `approved_hash`
- Execution Envelope v1〜v3 acceptance と conditional compatibility branch
- `worker-packet-v1.schema.json`
- Worker Packet v1/v2 builder/validator branch と `--schema-version` compatibility option
- metadata のない resume brief を warning だけで受理する branch
- old envelope/worker/resume artifact を成功させる test helper と positive tests
- active skill docs の “when available”、 “legacy remains readable/resumable” wording
- binding validation より先に `status` / `deliver` / resume routing を返す branch

historical wiki syntheses、過去の input packet/envelope JSON、過去の execution evidence は削除しない。ただし current validator、resume surface、active example から外し、historical/non-executable と明記する。

実装時の executable inventory は最低限次を含む。

| Contract area | Replace/delete targets |
|---|---|
| Input Packet | `assets/schemas/input-packet.schema.json`、`assets/templates/input-packet.json`、`validation/input_packet.py`、input packet test helpers/tests、grill execution handoff |
| Envelope | `assets/schemas/execution-envelope.schema.json`、template、`validation/execution_envelope.py`、v1/v2/v3 compatibility tests、active envelope docs |
| Worker/Reviewer Packet | `worker-packet-v1.schema.json`、current worker schema/template、`build_worker_packet.py` の version option、builder/validator version branches、V1/V2 positive tests、worker contract docs |
| Runtime/Event/Report | runtime/event/worker-report/human-request/hardening-candidates schemas、hardening registry template/loader、runtime rebuild、scheduler/operation/worker/report/delivery fixtures、binding なしの report/decision intake |
| Resume | `resume_brief.py` の meta-less success branch、Resume meta v2 handling、resume validator/tests、recovery/runtime docs |
| Completion/Delivery | execution result/delivery plan templates・validators・tests、binding guard 前の operation-selection short-circuit |

Input Packet v1、Runtime State v1、Human Request v1、Hardening Candidate Registry v1 は複数version branchではなく current contract 自体なので、compatibility branch を探して残すのではなく v2 へ全面置換する。context-contract v1/v2、operation-selection output v1、`_common.py` facade は別契約であり、version番号だけを理由に削除しない。

この仕様は次の旧 narrow clause を supersede する。

- `loop-skill-architecture-v3-spec.md` の schema version 1 compatibility requirement
- `loop-skill-codex-optimization-spec.md` の Envelope v1/v2 resume acceptance requirement
- `skill-repository-optimization-v4-spec.md` の legacy artifact resume を停止条件とする requirement

旧 page のその他の context、branch、worker-only、review、remote boundary は維持する。

## 非目標

- human identity の暗号学的認証、署名基盤、PKI の導入。
- remote approval service、database、queue、dispatcher、result store の追加。
- Companies、CTO council、特定 consumer の domain field を generic schema に追加すること。
- GitHub issue/PR、push、merge、live Codex/Hermes installation の実行。
- scheduler、branch policy、review policy、remote authorization の binding に無関係な再設計。
- historical artifact の in-place migration、旧 run の resume、compatibility shim。
- spec、packet、runtime の continuous immutability を保証すること。

## Acceptance matrix

| ID | Scenario | Expected result |
|---|---|---|
| ASB-01 | final spec digest を提示し human approval 後に seal | success。seal 前後で spec bytes 不変 |
| ASB-02 | seal operation の前後で spec raw bytes を比較 | 完全一致。seal interface に spec mutation mode なし |
| ASB-03 | approval 後、seal 前に spec を 1 byte変更 | `SPEC_DIGEST_MISMATCH` |
| ASB-04 | valid spec/approval/packet/envelope | prepare、dispatch、review、completion が成功 |
| ASB-05 | spec target が missing | `SPEC_MISSING` |
| ASB-06 | approval missing/not-approved/scope incomplete | 対応する approval error |
| ASB-07 | spec/packet digest missing または malformed | `DIGEST_MISSING` / `DIGEST_MALFORMED` |
| ASB-08 | sealed spec digest が current bytes と異なる | `SPEC_DIGEST_MISMATCH` |
| ASB-09 | packet bytes変更後、Envelope が旧 hash | `INPUT_PACKET_DIGEST_MISMATCH` |
| ASB-10 | canonical は valid、worker projection missing | dispatch 前に `PROJECTION_MISSING` |
| ASB-11 | canonical は valid、worker/reviewer projection が 1 byte違う | start 前に `PROJECTION_MISMATCH` |
| ASB-12 | runtime binding A、executor/reviewer packet B | `BINDING_MISMATCH` |
| ASB-13 | binding A の report を reseal 後の runtime B へ提出 | report intake で拒否 |
| ASB-14 | implementation 後、review/completion 前に spec変更 | review、terminal transition を拒否 |
| ASB-15 | stale binding と explicit `deliver` | delivery を拒否 |
| ASB-16 | stale binding と `status` | read-only status は成功、`binding_valid=false`、state advance不可 |
| ASB-17 | resume metadata生成後に spec/packet変更 | resume cache を拒否 |
| ASB-18 | mixed binding event から runtime rebuild | rebuild を拒否 |
| ASB-19 | spec変更、human re-approval、new seal/envelope/runtime | new epoch は成功、old review/result は失効 |
| ASB-20 | absolute、`..`、escape、parent/final symlink、directory | 各 path error で拒否 |
| ASB-21 | hash 中に file mutation/replacement | `FILE_CHANGED_DURING_VALIDATION` |
| ASB-22 | final alignment review と execution binding が異なる | completion/PR delivery を拒否 |
| ASB-23 | Input v1、Envelope v1〜v3、Event/Runtime/Report/Human Request/Hardening Registry v1、Worker v1/v2、Resume meta v2/meta-less、Result/Delivery v1 | `SCHEMA_UNSUPPORTED`。compatibility branchなし |
| ASB-24 | schema/module/error/user-visible artifact field に CTO/Companies 固有語彙が混入 | generic-contract regression test で拒否 |
| ASB-25 | Codex/Hermes の別 host から同じ repo bytes を検証 | 同じ binding result/error code |
| ASB-26 | `gate_commit` missing | `GATE_COMMIT_MISSING` |
| ASB-27 | gate commit が `epic_base` / assigned worktree の ancestor でない | `GATE_COMMIT_NOT_ANCESTOR` |
| ASB-28 | gate commit 内の spec/packet blob が binding と異なる | `GATE_COMMIT_BLOB_MISMATCH` |
| ASB-29 | binding A の hardening registry を runtime/delivery B が読む | `AUXILIARY_ARTIFACT_BINDING_MISMATCH` |
| ASB-30 | binding A の human request/decision を runtime B へ持ち込む | 拒否し、new binding で再判断 |
| ASB-31 | `artifact_root` が durable planning root 直下または別 Epic 名で終わる | `ARTIFACT_LAYOUT_MISMATCH` |
| ASB-32 | spec、local issue source、seal output のいずれかが `<artifact_root>` 直下にない | `ARTIFACT_LAYOUT_MISMATCH`、packet を書かない |
| ASB-33 | `<durable-planning-root>/<epic-id>/{spec.md,issues.md,input-packet.json}` | identify/seal/verify が成功し gate commit の exact blobs を検証する |
| ASB-34 | tracked current Envelope に host-local absolute worktree path がある | repository lifecycle test で拒否し runtime root へ再生成する |
| ASB-35 | fresh agent が新 Epic の artifact paths と tracking policy を選ぶ | durable 4 files は Epic directory、Envelope 以後は Git common runtime root と判断する |
| ASB-36 | schema、template、test fixture の JSON | product contract として Git tracked のまま維持する |

tests は public 3-operation interface と実 entrypoint hook を通す。private helper だけの単体テストで acceptance を代替しない。temporary repo/worktree fixture で repo containment、projection、one-byte drift、symlink、report intake、resume、delivery を forward-test する。

## 検証コマンド

実装完了時の最小 verification set は次とする。

```bash
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests -p 'test_approved_spec_binding.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s skills/grill-to-pr-loop/tests
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 -m unittest discover -s scripts -p 'test_*.py'
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_architecture.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_skill_context.py --all
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/report_skill_context.py --all --json
PYTHONPYCACHEPREFIX=/private/tmp/skills-pycache python3 scripts/validate_dual_host_compatibility.py --all
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/grill-to-pr-loop
python3 /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
git diff --check
```

context contract は operation を増やさず、既存 `planning-contract.md`、`execution-handoff.md`、`execution-envelope.md`、`worker-contract.md`、`runtime-state.md`、`review-gate.md`、`recovery.md`、`remote-delivery.md` の current wording を置換・圧縮する。default read-set へ verbose な新規 reference を無条件追加しない。

## Remote policy

仕様作成、Issue Gate、implementation plan、実装、検証は local-first とする。この follow-up の approved remote scope は branch `codex/approved-spec-binding-contract` への push と既存 Draft PR #32 の更新までに限定する。PR ready化、merge、release、live Codex/Hermes install は含めず、final merge は human-only のまま維持する。

## Written Spec Gate 承認対象

この page のレビューでは次を一括して承認対象とする。

- accepted decisions: packet-rooted ownership、3-operation module、artifact propagation、clean break
- non-goals: signature/remote service/consumer固有化/legacy migrationを行わないこと
- acceptance criteria: ASB-01〜ASB-36
- verification: focused/full tests、architecture/context、dual-host、skill-creator validator
- remote policy: current branch push と Draft PR #32 更新のみ、PR ready化/merge/release/live install は非承認、final merge human-only
- stop conditions: 以下のいずれかに該当したら実装を止めること

## 停止条件

- approval evidence を spec 自身へ書き込み、digest self-reference または承認後 mutation が発生する。
- validator が digest を自動更新、approval を推測、missing evidence を補完する。
- spec/packet path が trusted repo/worktree root 外を参照する。
- executor、reviewer、report、runtime、completion、delivery のどこかで binding mismatch を許容する。
- `status` 以外の operation が invalid binding のまま state を進める。
- bootstrap のために legacy compatibility branch を残す。
- new user-facing skill、consumer固有 schema、remote service が必要になる。
- context budget を守るために approval、stop、reapproval、delivery guard が default reader surface から消える。
- remote write、破壊的操作、live runtime change が必要になる。
- Input Packet 以外の Epic instance JSON/JSONL を tracked worktree に追加する。
- artifact layout を変えず filename prefix だけで Epic ownership を表現する。
- historical artifact 全件の一括 migration が必要になる。

## 既知のリスク

- raw-byte digest は Markdown の空白だけの変更でも再承認を要求する。これは exact revision contract の意図した保守性である。
- all-event binding は event size を増やすが、event replay と runtime rebuild の identity loss を防ぐため必要である。
- Git ancestor/projection check が甘いと canonical checkout だけ正しく worker worktree が stale な状態を見逃す。
- file-descriptor ベース検証でも検証後の mutation は起こり得るため、各 state-changing boundary の再検証を省略できない。
- actor expression は durable audit evidence だが本人性を証明しない。署名要件が将来必要になった場合は別 spec とする。
- clean break により既存 run は resume できない。operator action は migration ではなく new approval/new run である。
- per-Epic directory への移動で path-based link、packet digest、gate commit が変わるため、旧 packet/envelope を書き換えて継続せず new approval/new seal/new runtime epoch を作る。
- Git common runtime root は checkout 間で共有されるため、coordinator は Epic ID と active binding を毎回検証し、別 checkout の stale run を再利用しない。

## 関連ページ

- [Loop Skill Architecture V3 Spec](../loop-skill-architecture-v3-spec.md) — context contract、worker packet、resume brief の旧基盤と superseded compatibility clause。
- [Loop Skill Codex 最適化仕様](../loop-skill-codex-optimization-spec.md) — Envelope v3 と phase branch policy。branch policy は維持し、legacy acceptance だけを supersede する。
- [Skill Repository Optimization V4 Spec](../skill-repository-optimization-v4-spec.md) — Worker Packet V2 / Resume Brief V2 の freshness 基盤と superseded compatibility clause。
- [Loop Skill 運用単純化仕様](../loop-skill-operational-simplicity-spec.md) — user-facing skill を増やさず planning/execution ownership を維持する上位方針。
- [Loop Review Governance Spec](../loop-review-governance-spec.md) — reviewer と final alignment review の human authority boundary。

## 出典

- [grill-to-pr-loop execution handoff](../../../../skills/grill-to-pr-loop/references/execution-handoff.md)
- [issue-implementation-loop input packet schema](../../../../skills/issue-implementation-loop/assets/schemas/input-packet.schema.json)
- [issue-implementation-loop input packet validator](../../../../skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/validation/input_packet.py)
- [issue-implementation-loop execution envelope schema](../../../../skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json)
- [issue-implementation-loop worker packet schema](../../../../skills/issue-implementation-loop/assets/schemas/worker-packet.schema.json)
- [issue-implementation-loop runtime state schema](../../../../skills/issue-implementation-loop/assets/schemas/runtime-state.schema.json)
- [issue-implementation-loop event schema](../../../../skills/issue-implementation-loop/assets/schemas/event.schema.json)
- [issue-implementation-loop worker report schema](../../../../skills/issue-implementation-loop/assets/schemas/worker-report.schema.json)
- [issue-implementation-loop operation selection](../../../../skills/issue-implementation-loop/scripts/lib/issue_implementation_loop/operation_selection.py)
- [issue-implementation-loop review gate](../../../../skills/issue-implementation-loop/references/review-gate.md)
- [issue-implementation-loop recovery contract](../../../../skills/issue-implementation-loop/references/recovery.md)
- 2026-07-21 session user decision: packet-rooted A案を採用。
