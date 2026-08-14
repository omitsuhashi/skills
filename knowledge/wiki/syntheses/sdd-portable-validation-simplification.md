---
title: SDD portable validation と責務単純化仕様
date: 2026-08-14
status: proposed
tags:
  - sdd-implementation
  - skill-portability
  - validation
  - specification
aliases:
  - SDD Portable Validation Simplification
---

# SDD portable validation と責務単純化仕様

> [!warning] Written Spec approval 待ち
> 本仕様の status は `proposed` である。Human が Written Spec として承認するまで、既存仕様の supersession、実装、`knowledge/index.md` / `knowledge/log.md` の同期を行わない。

## 問題

現行の `sdd-implementation` は、install 単位に含まれない repository-root validator を必須実行し、その validator と package 内 test はこの source repository 固有の Git 履歴、hash、canonical plan、絶対 path に依存している。このため source checkout の test が成功しても、同じ skill を install した別 repository では必須 validation と package test を完結できない。

同時に、次の責務が重複または曖昧になっている。

- portable skill と repository owner の双方が repository 固有 policy を所有している。
- Superpowers が所有する generic lifecycle / worktree 手法を SDD が再定義している。
- validation の実行点が「すべての repository validation gate」とだけ記され、実際の引数と時点が一意でない。
- parallel issue execution について、Human opt-in / issue-plan approval を要求する仕様と、Written Spec 後は agent / repository が選ぶ仕様が併存している。
- package に必要な resource、runtime capability、isolated install での自己完結性が一つの closure として検証されていない。

## 目標

1. install 済み `sdd-implementation` が、この source repository を参照せず、明示された任意の target repository に対して実行可能であること。
2. generic validation を skill-relative package に閉じ、repository 固有の Git / migration / CI policy を各 repository owner に戻すこと。
3. SDD を、Superpowers lifecycle と `llm-wiki` を接続する薄い repository-independent composition にすること。
4. 必須 resource と capability、実行点、failure を一意にし、isolated package closure test で証明すること。
5. Human と agent の authority を、Written Spec と remote action の境界に沿って統一すること。

## 非目標

- repository validation adapter、hook registry、scheduler、永続 state、telemetry、追加 protocol を新設しない。
- target repository の branch、worktree、migration、history、CI policy を portable skill に標準化しない。
- Superpowers の generic lifecycle、worktree allocation、TDD、worker dispatch、review、branch finishing の手法を fork または再実装しない。
- Human-approved Written Spec の内容を agent が拡張したり、未承認の remote action を実行したりしない。
- 過去の migration evidence を削除または改変しない。

## Architecture と ownership seam

### 1. Portable skill package

`skills/sdd-implementation/` は public contract と、それを実行するための package closure を所有する。

- `SKILL.md` は inputs、outputs、required capabilities、composition order、三つの validation 実行点、failure boundary だけを定義する。
- fresh worker / model selection、repository-external handoff、path binding の共通 guard は public contract の一つの runtime capability boundary に集約し、stage reference と worker prompt はその owner を参照して worker 固有 input だけを追加する。
- generic validator は `skills/sdd-implementation/scripts/validate_sdd_transient_artifacts.py` に bundle し、常に installed skill directory から相対解決する。
- validator は explicit な target repository path を必須 input とし、受領後に canonical absolute path へ解決する。実行時 CWD、validator の source checkout、親 directory から target を推定しない。
- generic validator と package fixtures は repository 名、canonical wiki page、commit / blob hash、個人の絶対 path、完了済み migration marker を含まない。
- package 内 test は synthetic target repository と package-relative resource だけで完結する。

validator が package に存在しない、読めない、または package contract と一致しない場合は `broken skill installation` として fail closed にする。これは target repository の deficiency ではない。

### 2. Target repository owner

target repository は `AGENTS.md`、root-owned validator、test、CI など既存の最小 surface で、自身の Git / migration / canonical fixture / branch / worktree policy を所有する。この repository 固有の `f07aebc` migration、marker lineage、blob hash、canonical plan parity は root `scripts/` と `.github/` の concern とし、portable contract または package test から参照しない。

portable skill は repository-local validator の存在を前提にせず、自動 discovery や adapter seam も追加しない。repository-local rule が Superpowers の generic default より厳しい場合、その override は repository rule にだけ置く。

この source repository の migration outcome としては、既存の root `scripts/validate_sdd_transient_artifacts.py` が所有する `f07aebc` three-report baseline、marker parent / authorized introduction / cleanup deletion lineage、introduction 時の exact path / mode / blob、cleanup 後の再導入禁止という one-off history check を root surface に隔離して継続する。その root validator の回帰 test と `.github/workflows/skill-architecture.yml` からの invocation、および invocation を固定する `scripts/test_skill_ci_workflow.py` も継続必須とする。canonical SDD plan parity は package test から root-owned fixture / regression test へ移し、同じ CI で実行する。これらを package 外へ隔離することは retire または削除を意味しない。

### 3. Superpowers と SDD

Superpowers は generic lifecycle、worktree methodology、planning、TDD、dispatch、review/fix、branch finishing を所有する。SDD は applicable Superpowers skill を呼ぶ順序と、SDD 固有の research / Written Spec / knowledge composition、portable validation だけを所有する。

SDD は worktree の allocation algorithm、fallback、host-specific writable-root mutation を再記述しない。代わりに、選択された worktree / workspace に CWD と authorized write destination を bind できることを required capability として宣言する。Superpowers または repository-local policy が安全な binding を成立させられなければ、最初の repository write 前に停止する。

## Interface contract

### Inputs

- Human-approved Written Spec、または Written Spec 作成に必要な Human-confirmed decisions。
- caller が明示し、実行時に canonical absolute path へ解決する target repository path。
- installed `sdd-implementation` directory と、そこから相対解決できる bundled resources。
- target repository が宣言する applicable local instructions と remote-action policy。

### Outputs

- approved scope に対する local implementation / verification result と、変更 file / commit / remaining risk の evidence。
- Human decision が必要な material spec change または remote action の明示的な停止理由。
- package、target、runtime capability、repository policy のどの境界で失敗したかを区別した診断。

### Required capabilities

- installed skill directory から resource と bundled validator を相対解決できること。
- target repository identity、CWD、write destination を canonical absolute path として検証できること。
- repository-external temporary report を安全に作成し、bounded handoff できること。
- applicable Superpowers / `llm-wiki` / authoring skill を discovery し、その contract に従えること。
- fresh worker dispatch、bounded read/write、result collection ができること。
- target policy が要求する Git / worktree 操作と、選択 workspace への write binding ができること。

capability が存在しない場合、別 runtime 固有機能を推定して代用せず、最初の該当 mutation 前に fail closed にする。

## Concrete control flow

1. **Resolve**: installed skill directory と explicit target repository を別 identity として解決する。bundled resource closure を確認し、validator 欠落は `broken skill installation`、target 不在・非 repository・authority 不足は target-side failure として分離する。
2. **Load ownership**: target の local instructions を読み、generic lifecycle は Superpowers、repository override は repository owner、knowledge routing は対象 knowledge root に委ねる。SDD 内の重複した worktree / lifecycle 手順は参照しない。
3. **Bind workspace**: Superpowers の methodology と target policy に従い、実行 workspace、CWD、write destination を bind する。安全な binding を証明できなければ最初の repository write 前に停止する。
4. **Research and spec**: repository-external research report から Written Spec を作成し、material decisions は Human approval に戻す。承認済み Written Spec 内では agent が execution decomposition を行う。
5. **Choose execution shape**: dependency と write-conflict の非存在を evidence で確認できる issue だけ parallel eligible とする。unknown な dependency / conflict は sequential execution に落とす。追加の Human execution-method approval または issue-plan approval は要求しない。
6. **Validate at exactly three mechanical points**: 次節の normative gate contract に従う。これ以外の stage transition では generic validator を呼ばない。
7. **Implement and review**: TDD、worker review/fix、whole-branch review、branch finishing は applicable Superpowers contract に従う。repository-specific validator / CI は target owner の定義した時点で別途実行する。
8. **Close out**: package validator、target-owned checks、package closure tests、required repository tests の fresh evidence を集約する。remote action は既存の明示的 authorization がある場合だけ実行する。

### Generic validator normative gate contract

全 gate は installed skill directory から相対解決した同一 executable を使い、共通必須 input として `--target-repository <canonical-absolute-path>` と `--gate <gate-name>` を受け取る。validator は target を Git worktree として解決し、その worktree に対応する index を Git から取得する。CWD、validator の配置 repository、親 directory、別 worktree の index を代用しない。tree input は target Git object database に存在する full tree OID とし、曖昧な ref、working-tree snapshot、別 repository の object は拒否する。

| Gate | 一意な trigger と呼出回数 | point-specific mandatory inputs | 検査する exact surface | Pass condition | Failure condition / diagnostic | Block boundary |
|---|---|---|---|---|---|---|
| `exceptional-local-scratch-pre-write` | repository-external default を使えない具体的な operational reason があり、target 内の distinct scratch path に最初の byte を書く直前に、その path ごとに一回。target、path、ignore rule、index のいずれかが変われば evidence は失効し、次の write 前に再実行する。 | `--scratch-path <target-relative-exact-path>`、`--scratch-reason <non-empty-reason>` | canonical target 内に解決した exact path（directory の場合は subtree pathspec）、target の current `.gitignore` 判定、対応する current Git index / staging area、既存 path の working-tree state。path は `.superpowers/**` 内でなければならない。 | path が target 内の `.superpowers/**` に閉じ、exact path が `git check-ignore --no-index` 相当で ignore され、index に tracked entry がなく、staged add / modify / rename がなく、既存 entry がある場合も全て ignored・untracked・unstaged である。reason は trim 後に空でなく、local-only consumer / operation と external path では満たせない理由を記録する。 | path escape、非 `.superpowers/**`、reason が trim 後に空、ignore 不成立、tracked / staged entry、または state を証明不能なら `transient-artifact-policy violation`。reason の内容が required facts を記録していない場合も caller contract failure として同じ write を block する。 | その repository-local scratch write を block する。repository-external route が使えるならそこへ戻し、使えなければ当該 stage を停止する。この gate 自体は commit または closeout を許可しない。 |
| `pre-commit-candidate` | final staging 後、各 `commit` または `commit --amend` attempt の直前に一回。検査後の index mutation は evidence を失効させ、commit attempt 前に再実行する。 | `--candidate-tree <full-tree-oid>`。OID は invocation 時の target worktree index に対する `git write-tree` 相当値と一致しなければならない。 | nominated candidate tree、target worktree の current index と staging area、working tree の `.superpowers/**` namespace。unstaged non-scratch path はこの generic policy の対象外。 | candidate OID が current index tree と一致し、candidate tree と index / staged diff に `.superpowers/**` entry がなく、working tree に残る `.superpowers/**` entry がある場合は全て ignored・untracked・unstaged である。 | stale / foreign / unresolved tree、candidate と index の不一致、candidate / index / staged diff 内の `.superpowers/**`、tracked または staged scratch、または state を証明不能なら `transient-artifact-policy violation`。 | 当該 commit / amend を block する。修復 write と restaging は許すが、その後は新しい candidate OID で gate を再実行する。この gate は closeout を代替しない。 |
| `final-closeout` | 全実装 commit と scratch cleanup の後、`LOCAL_COMPLETE`、`PR_READY` その他の completion verdict を返す各 closeout attempt の直前に一回。検査後の HEAD、index、または scratch state mutation は evidence を失効させる。 | `--final-tree <full-tree-oid>`。OID は invocation 時の target worktree `HEAD^{tree}` と一致しなければならない。 | nominated final tree、target worktree の current `HEAD^{tree}`、current index / staging area、working tree の `.superpowers/**` namespace（ignored / untracked を含む）。 | nominated OID が `HEAD^{tree}` と一致し、final tree、index、staged diff、working tree のいずれにも `.superpowers/**` entry が一件もなく、scratch cleanup が完了している。 | stale / foreign / unresolved tree、HEAD tree 不一致、いずれかの inspected surface に残る `.superpowers/**` entry、または state を証明不能なら `transient-artifact-policy violation`。 | closeout verdict を block する。cleanup write は許す。cleanup が tracked tree を変える場合は pre-commit gate と commit を経てから final gate を再実行する。 |

この表だけを generic gate methodology の normative source とする。public `SKILL.md` は表の contract を保持し、prompt / reference / test は gate 名と必要 input を参照するだけで trigger、Git surface、pass / fail prose を複製しない。

## Failure handling

| Condition | Owner classification | Required behavior |
|---|---|---|
| bundled validator / required resource が欠落・読取不能 | skill package | `broken skill installation` として mutation 前に停止する |
| explicit target が不在、非 Git repository、または authority 外 | caller / target | target-side input / authority failure として停止する |
| workspace binding、fresh dispatch、external temporary handoff 等の capability がない | runtime | 該当 mutation 前に不足 capability を示して停止する |
| repository-local policy check が失敗 | target repository | generic package failure と混同せず、owner surface と evidence を示して停止する |
| parallel independence の evidence が不足 | execution planning | failure にせず sequential execution に切り替える |
| approved Written Spec を変える必要がある | Human authority | material差分を提示し、再承認まで停止する |
| remote action の authorization がない | Human / repository policy | local completion に留め、remote action を実行しない |

途中失敗時は新しい durable runtime state を作らず、既存の Superpowers / repository workflow が定める回復可能な artifact と Git evidence だけを返す。

## Testing strategy

### Portable package tests

- skill folder だけを isolated temporary directory へ copy / install し、source repository とその親を read path に含めず test を実行する。
- isolated synthetic Git repository を explicit target に渡し、normative gate table の各 mandatory input と positive / negative state を検証する。distinct scratch path の first-write、各 commit / amend attempt、各 closeout attempt につき invocation が一回であること、および invalidating mutation 後の再実行を event fixture で直接検証する。
- validator、prompt、reference、fixture の全 mandatory resource が package 内に存在し、skill-relative に解決されることを closure test で確認する。
- package test と fixture に repository-specific hash、canonical plan、username / absolute path がないことを regression test で固定する。
- bundled validator 欠落が `broken skill installation`、不正 target が target-side failure として区別されることを確認する。

### Repository-owned tests

- この repository の既存 one-off compatibility を root `scripts/validate_sdd_transient_artifacts.py` に保持し、`f07aebc` three-report baseline、marker の planned parent / sole authorized introduction、introduction 時の exact path / mode / blob、cleanup 前 ancestry の marker deletion 不在、cleanup transition の exact marker / three-report deletion、cleanup 後の再導入不在を root-owned regression test で固定する。
- canonical SDD plan parity を repository-level fixture / regression test へ移し、installed package test からは除外する。移動後も parity coverage を削らない。
- `.github/workflows/skill-architecture.yml` は root validator の one-off history / migration invocation、対応する root regression tests、canonical-plan parity、isolated package closure test を source checkout CI で実行する。`scripts/test_skill_ci_workflow.py` はこの invocation set を contract test として固定する。quick shape validation の成功だけを installability evidence にしない。

### Contract and integration tests

- public contract に inputs、outputs、required capabilities、explicit target、三つの execution point が一度だけ定義されていること。
- fresh worker / model selection、repository-external path rejection、binding failure の共通 guard が prompts / references に複製されていないこと。
- public contract が repository 固有 hash / path / migration と generic worktree fallback algorithm を含まないこと。
- parallel eligibility は agent / repository-owned、unknown は sequential、Human approval は Written Spec material change と別途 authorization が必要な remote action に限定されること。
- repository architecture validator、skill-creator validator、skill tests、root tests、workflow contract tests、`git diff --check` を fresh に実行すること。

## Acceptance criteria

1. isolated install の `sdd-implementation` が source repository への access なしで synthetic target に対する必須 resource resolution、generic validation、package tests を完了する。
2. bundled validator は explicit target repository を要求して canonical absolute path へ解決し、CWD や validator 所在 repository から target を推定しない。
3. bundled validator を package から除く negative test は、target deficiency ではなく `broken skill installation` で mutation 前に失敗する。
4. portable `SKILL.md`、validator、prompt、reference、fixture に、この repository 固有の commit / blob hash、canonical wiki path、migration marker、個人の絶対 path が存在しない。
5. `f07aebc` three-report baseline、marker parent / authorized introduction / cleanup deletion lineage、introduction 時の exact path / mode / blob、cleanup 後の再導入禁止、canonical-plan parity は portable package に存在せず、この repository の root-owned validator / regression tests / fixture に保持される。`.github/workflows/skill-architecture.yml` がそれらを fresh 実行し、`scripts/test_skill_ci_workflow.py` が invocation の欠落を失敗にする。
6. generic validator の mechanical invocation point は normative gate table の三つだけである。各 gate の common / point-specific mandatory input、nominated tree と current index / HEAD の一致、scratch state、positive / negative result、event ごとの exactly-once invocation、mutation 後の evidence invalidation が isolated test で観測できる。
7. package closure test が mandatory resource の欠落、package 外参照、source topology 依存を検出する。
8. SDD の public contract は generic worktree allocation / fallback / TDD / review / finishing を再定義せず、Superpowers ownership と repository-local override を参照する。
9. required runtime capabilities と unavailable 時の pre-mutation stop が contract test で固定される。
10. parallel eligibility の independence evidence、unknown 時の sequential fallback、Human authority boundary が contract test で固定される。
11. source checkout の全 relevant tests、isolated installed-copy tests、repository validators、CI contract tests が fresh run で成功する。
12. implementation diff は既存 owner / surface の修正に限定され、新しい adapter seam、scheduler、state、telemetry、protocol を追加しない。

## Migration と supersession

Human approval 後、実装は次の順序で移行する。

1. generic validator を skill-relative package に追加し、explicit target interface と isolated tests を先に成立させる。
2. package tests / fixtures から repository-specific canonical plan、history、absolute path を分離し、既存 canonical-plan parity coverage と one-off migration / history regression coverage を root-owned test / fixture に移す。移動中も coverage を削除または optional 化しない。
3. root validator から generic concern を package validator へ寄せる一方、`f07aebc` three-report baseline、marker parent / authorized introduction / cleanup deletion lineage、introduction 時の exact path / mode / blob、cleanup 後の再導入禁止は root validator に隔離して残す。root regression tests、`.github/workflows/skill-architecture.yml` の invocation、`scripts/test_skill_ci_workflow.py` の invocation contract が GREEN になるまで cutover しない。
4. `SKILL.md`、prompts、references の重複 gate と lifecycle / worktree prose を一つの portable contract へ収束する。
5. isolated package closure と repository full suite の双方が GREEN になってから旧 package-external dependency を除去する。

承認された時点で、本仕様は以下の current conflict に限って後勝ちする。

- `sdd-first-write-worktree-migration-spec.md` の Human opt-in / Human-approved issue-plan 要求は supersede し、Human-approved Written Spec 内の parallel eligibility を agent / repository-owned とする。
- `sdd-plan-ownership-alignment.md` の「Human approval は North Star / Written Spec、issue plan は agent-owned」という authority を維持し、本仕様が parallel fallback を具体化する。
- `sdd-implementation-skill-design.md` の Superpowers ownership / thin integration を維持し、portable package と repository-local override の境界を本仕様で具体化する。
- 現行 public skill と test に残る repository-specific migration contract、重複 lifecycle / gate prose、package-external validator dependency は、本仕様の implementation により置換する。

過去の仕様、plan、migration evidence は historical record として保持し、current executable instruction としては参照しない。本仕様が `proposed` の間は既存 authority を変更しない。

## Stop conditions

- Human Written Spec approval 前は implementation、supersession、index / log sync に進まない。
- resolved spec path が planning worktree 外、original checkout、planning sibling、issue siblingへ向く場合は write しない。
- installed package closure、explicit target identity、write authority、required capability のいずれかを証明できなければ、最初の該当 write 前に停止する。
- material scope / architecture / authority の変更が必要なら、spec 差分を Human に戻して再承認を待つ。
- repository-local policy と generic method が両立しなければ、portable skill が override せず repository owner の判断まで停止する。
- remote push、PR 作成・更新、merge、release、live install は、別途明示された authorization がなければ実行しない。
- fresh isolated package test と repository verification が揃うまで completion を宣言しない。

## Confirmed Decisions

1. install 済み `sdd-implementation` は、この source repository への hidden dependency なしに任意の明示 target repository で実行できる。repository-specific Git / migration / CI policy は各 repository owner が所有する。
2. generic validator は skill-relative に bundle し、target repository を明示必須とする。欠落は target deficiency ではなく broken skill installation とする。one-off migration / history behavior は root-owned validator / CI に隔離し、generic validator の mechanical execution point は exceptional local scratch pre-write、pre-commit candidate、final closeout に限定する。isolated package-closure tests を追加する。
3. repository-specific hash / canonical fixture / policy の portable contract への leakage、曖昧または重複した gate、package closure gap、lifecycle / worktree ownership の重複、未宣言 runtime capability を同じ revision で修復する。既存の最小 owner / surface を使い、新しい repository validation adapter、scheduler、state、telemetry、protocol は作らない。
4. Human-approved Written Spec 内の parallel issue eligibility は agent / repository-owned とする。dependency / conflict evidence が unknown なら sequential に戻す。Human は material Written Spec change と別途 authorization が必要な remote action を決定し、execution method または issue plan の追加承認は不要とする。
5. generic lifecycle / worktree methodology は Superpowers が所有し、SDD は必要な local composition と repository-independent behavior だけを持つ。

## Open Decisions

なし。

## Review verdict

独立再レビューの verdict は `complete/ready_for_human_review`。前回の agent-repairable finding は、(1) 三つの generic validation gate を必須 input、検査対象、pass / fail invariant、diagnostic、block boundary、exactly-once / invalidation test を持つ normative contract にしたこと、(2) root-owned の one-off migration/history validator、regression、CI invocation の保持を必須化したことで解消した。新たな decision request と material risk はない。status は引き続き `proposed` とし、Human の Written Spec approval まで activation、supersession、implementation、index / log sync は行わない。

## Provenance

- advisory research report: `/private/tmp/sdd-portable-validation-research.P4mhzZ/research-report.md`
- audited baseline: `82dcd32157ff9690ae038f982f3916009e449f80`
- planning worktree: `/private/tmp/skills-sdd-portable-validation-simplification`
- original checkout: `/Users/omitsuhashi/repos/omitsuhashi/skills`、starting branch `main`、captured status clean
- authority: Human-confirmed decisions を保持した advisory synthesis。raw report / transcript は durable page へ複製していない。
