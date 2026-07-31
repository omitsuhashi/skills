---
title: Task Management Hermes Schedule Secretary Readiness Issue 台帳
date: 2026-07-31
updated: 2026-07-31
tags:
  - task-management
  - github-projects
  - hermes
  - schedule-secretary
  - implementation-ledger
status: review-pending
aliases:
  - Task Management Hermes Readiness Issues
  - Schedule Secretary Task Management MVP Issue Ledger
---

# Task Management Hermes Schedule Secretary Readiness Issue 台帳

## 現在地

本台帳は `task-management-hermes-readiness` の local-first durable execution
ledger である。portable Skills Tasks 1〜5とwhole-branch指摘への修正実装は完了している。
ただし修正後のwhole-branch再reviewはpendingであり、現時点では
`LOCAL_COMPLETE`またはremote publish可能とは判定しない。

Task 6 cross-repository handoffは、修正済みSkills revisionが`origin/main`へmergeされた
証拠、すなわちmerged revisionのexact identityを得るまで`blocked`である。
Companies、install、Schedule Secretary、
live Hermes / GitHub MCPの状態は本台帳から推定しない。

## Authority と binding

- approved spec: [[spec|Task Management Hermes Schedule Secretary Readiness 仕様]]
- approved spec raw-byte SHA-256:
  `338e0c1e192949c352a1fdd6deec1231ad495f19b68729e2aff3f330356ced4f`
- Written Spec approval commit:
  `088b91669813649363ddda28ea3d45387b92dbc3`
- Human-approved plan:
  [[implementation-plan|Task Management Hermes Schedule Secretary Readiness Implementation Plan]]
- Execution Plan Gate approval commit:
  `14abd1677eb9a790bdfc3ed30bd416df4a6725b8`

HumanのExecution Plan Gate承認は、承認済みplanが記述したSkills Tasks 1〜5のlocal実装と、
merge prerequisite成立後に作るTask 6 handoffを対象とした。承認時点では本
`issues.md`は存在していなかったため、存在しないpre-execution fileへのIssue Gate承認が
あったとは扱わない。本台帳は承認内容を変更せず、実際のexecution evidenceとcurrent
gateを事後にdurable化する。

## 実装slice

| Slice | 状態 | 実装commit | 独立task review | Remaining / next trigger |
| --- | --- | --- | --- | --- |
| Task 1 operation-scoped capability | verified | `6b9721dfc13fd4a18c904e99e492237a15f9a7cb`, `aa2ea023d1377727a7a06e8650cfdf6f9ab11804`, `544a34976d3e08e673acbdf31201215ba56bc456` | spec PASS / quality PASS。target-scopeとnegative assertionの指摘を修正後、findingなし | なし |
| Task 2 canonical reconciliation / continuation | verified | `1efacf0c3708a5eb31162f98ae2d2d7df856cf18`, `4a4cf986e4354917648b6dc9665035911e72d29d` | spec PASS / quality PASS。field freshness指摘を修正・再review済み | whole-branch checkpoint補強はfix wave参照 |
| Task 3 Status / completeness / duplicate | verified | `c2b94574cfd6c013d176ca0f7dd325857c3468bf`, `d1d1d2d25ef2b9ebee1b58fe61ec58cfe0e25284` | spec PASS / quality PASS。exhaustive discoveryとduplicate outcomeを修正・再review済み | whole-branch executor補強はfix wave参照 |
| Task 4 terminal / reopen | verified | `0256102471980819edcaf463def64b0ad04554f5`, `6fb93e511369a212ce5a990bd0b385ab937b7fdb` | spec PASS / quality PASS。retry safetyとcontradiction guardを修正・再review済み | whole-branch close-reason補強はfix wave参照 |
| Task 5 metadata / portable closeout | verified | `eb0fa84f10c627658c74c0e974189ee45f709594`, `df001eee038d0003b834dd9a39afcbe6da287300` | spec PASS / quality PASS。findingなし | whole-branch shared declaration補強はfix wave参照 |
| Whole-branch fix wave | implemented / review pending | `836c80bebbea0820803c76cf29056eadb9a7a07b` | initial whole-branch reviewはFAIL: Critical 0 / Important 9 / Minor 1。10件を一つのcoherent TDD waveで修正した。修正後再reviewはpending | fresh whole-branch再review |
| Task 6 cross-repository handoff | blocked | なし | 未着手 | 修正済みSkills revisionが`origin/main`へmergeされたexact evidence |

## Portable acceptance mapping

| Acceptance criterion | Named executable evidence | Exact implementation commits |
| --- | --- | --- |
| MVP operationごとの最小semantic capability | `test_operation_capability_matrix_matches_every_approved_row`, `test_operation_scoped_cases_derive_requirements_from_markdown` | `6b9721dfc13fd4a18c904e99e492237a15f9a7cb`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| comment / title-body / read-listをunrelated write不足でblockしない | `test_issue_only_operations_require_only_their_resolved_targets`, `test_operation_scoped_cases_derive_requirements_from_markdown` | `aa2ea023d1377727a7a06e8650cfdf6f9ab11804`, `544a34976d3e08e673acbdf31201215ba56bc456`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| retryはremaining sideだけをpreflight | `test_operation_scoped_cases_derive_requirements_from_markdown`, `test_transition_fixtures_execute_complete_partial_and_retry` | `6b9721dfc13fd4a18c904e99e492237a15f9a7cb`, `6fb93e511369a212ce5a990bd0b385ab937b7fdb`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| protected native metadataをwriteせずexact-readback | `test_every_supported_mutation_preserves_native_metadata`, `test_operation_capability_matrix_matches_every_approved_row` | `eb0fa84f10c627658c74c0e974189ee45f709594`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| seven Status、利用者表現、schema ambiguity stop | `test_status_wording_and_schema_ambiguity_contract`, `test_requested_status_filter_controls_reconciled_matches` | `c2b94574cfd6c013d176ca0f7dd325857c3468bf`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| Status-filtered list、unique 50、complete/partial/truncation/continuation | `test_pagination_fixtures_match_exact_counts_conflicts_and_continuation`, `test_unique_51_two_call_continuation_is_lossless`, `test_resume_checkpoint_is_lossless_across_identity_and_field_changes` | `1efacf0c3708a5eb31162f98ae2d2d7df856cf18`, `4a4cf986e4354917648b6dc9665035911e72d29d`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| canonical identity、page reconciliation、conflict、stable order | `test_identity_and_lossless_page_boundary_are_explicit`, `test_reconciliation_tracks_freshness_per_field`, `test_canonical_issue_identity_normalizes_case_and_decimal_number`, `test_due_date_reconciliation_is_independent_and_lossless` | `1efacf0c3708a5eb31162f98ae2d2d7df856cf18`, `4a4cf986e4354917648b6dc9665035911e72d29d`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| ambiguous membershipではProject writeを停止 | `test_ambiguous_project_membership_blocks_project_writes` | `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| completeness-required queryはpage-drivenでexhaustionまたはpartial | `test_completeness_required_traversal_executes_all_pages`, `test_duplicate_discovery_requires_complete_exhaustion` | `d1d1d2d25ef2b9ebee1b58fe61ec58cfe0e25284`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| truncated / partial duplicate discoveryからcreateしない | `test_duplicate_discovery_requires_complete_exhaustion`, `test_completeness_required_traversal_executes_all_pages` | `c2b94574cfd6c013d176ca0f7dd325857c3468bf`, `d1d1d2d25ef2b9ebee1b58fe61ec58cfe0e25284`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| explicit reopen優先、bare reopenはBacklog | `test_reopen_target_allowlist_blocks_terminal_and_unknown_values`, `test_terminal_and_reopen_contract_names_state_machine_outputs` | `0256102471980819edcaf463def64b0ad04554f5`, `6fb93e511369a212ce5a990bd0b385ab937b7fdb` |
| Done / Cancelled / reopenはclose reasonを含む二side、no rollback、resume-only | `test_transition_fixtures_execute_complete_partial_and_retry`, `test_transition_rejects_invalid_operation_and_retry_evidence` | `0256102471980819edcaf463def64b0ad04554f5`, `6fb93e511369a212ce5a990bd0b385ab937b7fdb`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| portable shared Inputs / Outputs / Required Capabilities | `test_skill_declares_portable_inputs_outputs_and_capabilities`, `test_standalone_structure_and_frontmatter` | `836c80bebbea0820803c76cf29056eadb9a7a07b` |
| CLI / REST / browser / local backendへfallbackしない | `test_portable_contract_forbids_secret_values_not_pagination_terms`, `test_capability_and_partial_failures_are_fail_closed` | `eb0fa84f10c627658c74c0e974189ee45f709594`, `836c80bebbea0820803c76cf29056eadb9a7a07b` |

## Whole-branch review とfix wave

initial whole-branch reviewはTasks 1〜5統合結果を`FAIL`とし、Critical 0、
Important 9、Minor 1を報告した。fix wave
`836c80bebbea0820803c76cf29056eadb9a7a07b`は次を修正した。

1. requested Status filterを実際のreconciliationへ使用。
2. cursorだけでなくitem state、field freshness、conflict、order、emitted identityを持つ
   caller-held lossless checkpoint。
3. Due dateのfield-by-field freshness、missing/null preservation、explicit clear、conflict。
4. 全mutation/retryのprotected metadata semantic readback capability。
5. terminal/reopenのclose reason exact state。
6. multiple Project-item membership時のwrite stop。
7. 50件を越えてsource exhaustionまで進むpage-driven completeness-required executor。
8. portable `SKILL.md`のInputs / Outputs / Required Capabilities。
9. 本local Issue ledger、index、append-only logのdurable化。
10. owner/repository casefold、decimal Issue number、不完全identity isolation。

修正後のfocused GREENとfull verificationは本台帳作成後にfresh実行し、whole-branch
再reviewのevidenceとする。再review前にreview completeとは扱わない。

## Remote / external boundary

本台帳とcommitは`local_only`である。次は未承認かつ未実施であり、本branchの完了状態へ
含めない。

- push、PR作成、merge、release。
- Companies repositoryの変更とTask 6 handoffのpublication。
- managed-native install / reinstall、profile/default変更、restart。
- Schedule Secretary discovery/readinessのlive確認。
- GitHub MCP credential / permission / configuration / schema変更。
- live Issue / Projectのcreate、edit、comment、field update、close、reopen。

[[../direct-github-projects-task-management/issues|既存Direct GitHub Projects Issue台帳]]
はprotected historical/current evidenceとして変更していない。

## Next gate

1. fresh repository verificationを完了する。
2. `282fa44a9fe97d9d0feb2e8d6733a6ae47f00f78..HEAD`のwhole-branch再reviewを行う。
3. review findingがあればbounded fixとscoped re-reviewを行う。
4. 修正済みrevisionが`origin/main`へmergeされた後だけTask 6 handoffを作る。
