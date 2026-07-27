---
kind: synthesis
created: 2026-07-17
updated: 2026-07-28
---

# Codex / Hermes Dual-host Authoring Contract 設計

## 状態

本書の **skill behavior**（Codex / Hermes の名称ごとに discovery、dispatch、fallback、verification を選ぶ guidance）は、2026-07-28 の agent-agnostic runtime contract により historical / superseded である。current skill behavior は [SDD Implementation Skill 設計](sdd-implementation-skill-design.md) と shared `SKILL.md` の inputs、applicable dependencies、required capabilities だけから解決し、本書を active-runtime preflight の根拠にしてはならない。

一方、plugin packaging の manifest、registration、paired package validation という境界は依然として skill behavior とは別であり、current repository compatibility validation に残る。本書の plugin packaging evidence と live discovery / load evidence は、その別境界または過去の検証記録を調べるためにだけ参照する。2026-07-17 の plugin 前提の task-management 記録は、2026-07-23 の standalone skill migration により historical / superseded となった。current repository surface は `skills/task-management/SKILL.md` と4つの参照Markdownだけであり、task-management の plugin manifest、registration、runtime code、smoke scriptは残っていない。今回のmigrationは `local_only` であり、live `~/.hermes/config.yaml` の変更と `hermes skills list` による可視性確認は実施していない。

## 実装・ローカル検証証跡

`.github/workflows/skill-architecture.yml` は Python 3.9 / 3.12 matrix でauthoring guidance、CI workflow contract、repository compatibility validator、repository-wide compatibility、standalone `decide-in-order`、standalone `task-management` のcontract testsを実行する。通常CIはlive home、profile、config、credential、skill / plugin installationを変更しない。

以下は2026-07-17時点の最終ローカル検証結果を保存したhistorical evidenceである。表中のtask-management plugin manifest、registration、plugin validator、plugin suite、smoke testはすべて2026-07-23 standalone migrationによりsupersededされ、current implementationやcurrent verification commandではない。

| コマンド | 実測結果 |
| --- | --- |
| `python3 scripts/test_dual_host_authoring_guidance.py` | 3 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 scripts/test_dual_host_ci_workflow.py` | 3 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 scripts/test_validate_dual_host_compatibility.py` | 25 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 scripts/validate_dual_host_compatibility.py --all` | Python 3.9.6 / 3.12 とも repository compatibility OK |
| `python3 scripts/validate_skill_architecture.py --all` | Python 3.9.6 / 3.12 とも `repository-change-loop` policy OK |
| `python3 scripts/validate_skill_context.py --all` | Python 3.9.6 / 3.12 とも 3 context contracts、成功 |
| `python3 -m unittest discover -s skills/llm-wiki/tests` | 6 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 -m unittest discover -s skills/decide-in-order/tests` | 7 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 plugins/task-management/tests/test_decision_support_policy.py` | 6 tests、成功 |
| `python3 plugins/task-management/tests/test_hermes_plugin_manifest.py` | 11 tests、Python 3.9.6 / 3.12 とも成功、PyYAML dependency なし |
| `python3 -m unittest discover -s plugins/task-management/tests` | 94 tests、Python 3.9.6 / 3.12 とも成功 |
| `python3 plugins/task-management/scripts/smoke_test_hermes_read.py` | Python 3.9.6 で 1 normalized snapshot、成功 |
| skill-creator quick validation（standalone / bundled） | Python 3.9.6 で両方成功 |
| plugin-creator validation（task-management） | Python 3.9.6 で成功 |
| `git diff --check` / Goal audit | 成功 / tracked・untracked・ignored の `goals/**/*.json` は各 0件 |

Python command はすべて `PYTHONPYCACHEPREFIX=/tmp/skills-pycache` 付きで実行した。本 review で追加・変更した CI matrix suite はローカルでも Python 3.9.6 / 3.12 の両方で再検証した。installed Hermes runtime と system skill/plugin creator のローカル Python 3.12 環境には外部 PyYAML がないため、これら外部 tool の smoke / creator validation は repository default の Python 3.9.6 で検証した。repository validator と focused CI tests には非標準依存を追加していない。

## 結論

`decide-in-order` とcurrent `task-management` は、どちらも共有 `SKILL.md` をentrypointとするstandalone skillである。

- `decide-in-order` は Hermes が読む標準 `SKILL.md` と YAML frontmatter の `name` / `description` を持ち、リポジトリ上の基本形式は互換である。
- Hermes に `description.md` は不要であり、説明は `SKILL.md` frontmatter の `description` が正本となる。
- 2026-07-17時点の`task-management` pluginは複数manifestとregistrationを持っていたが、これはhistorical evidenceであり、current treeからは削除済みである。
- `agents/openai.yaml` は Codex の UI metadata であり、それ単独では Hermes の discovery を成立させない。

不足していたのは、作成物の基本形式ではなく、すべての新規 skill / plugin が Hermes でも発見・ロードできることを作成ルールと検証で保証する契約である。既存 `skill-creator` は標準 `SKILL.md` を要求するため結果的に Hermes と互換になりやすいが、Hermes discovery や live visibility までは保証しない。既存 `plugin-creator` は Codex manifest を中心とするため、Hermes plugin の構造を共通必須条件にはしていない。

## 現状確認

この節は2026-07-17時点の実ファイルとlive CLIを分けたhistorical observationである。task-management pluginのmanifest / registration / version観測は2026-07-23 migrationによりsupersededされ、current availabilityを示さない。

| 対象 | リポジトリ上の状態 | live Hermes の状態 | 判定 |
| --- | --- | --- | --- |
| `skills/decide-in-order` | `SKILL.md` に `name` / `description` あり | `hermes skills list` に未表示 | 形式互換、未導入 |
| `plugins/task-management`（historical / deleted） | 当時はCodex manifestとHermes manifest / registrationあり、version `0.3.0` | 当時の`hermes plugins list`はenabled version `0.1.0` | superseded。current repository surfaceではない |
| repo-wide guidance | repo root の薄い router に dual-host authoring requirement あり | 該当なし | 実装・検証済み |
| directory guidance | `skills/AGENTS.md` / `plugins/AGENTS.md` に host 別最小契約あり | 該当なし | 実装・検証済み |

この表の「形式互換」「導入済み」「live load済み」は同義にしない。特に旧task-management live version観測をcurrent standalone skillの導入証拠に流用しない。

2026-07-17のread-only再確認では、`hermes skills list`はexit 0で42 enabled skillsを返したが`decide-in-order`は未表示だった。旧`hermes plugins list --plain --no-bundled`のtask-management version `0.1.0`観測はhistorical / supersededであり、current skillの状態を表さない。2026-07-23 migrationではlive configもlistも確認しておらず、導入確認は明示承認を要する別follow-upとする。

## 設計原則

### 1. 三段階を分離する

1. **Repository compatibility**: 必要なファイル、manifest、registration、metadata が正しい。
2. **Distribution / discovery**: Hermes の install、tap、hub、または `skills.external_dirs` から対象を発見できる。
3. **Live load**: 実際の対象 profile で list / load / smoke が成功し、期待 version が動いている。

repo validator は第1段階を保証する。第2・第3段階は環境依存なので、導入手順と opt-in smoke contract を定義するが、通常の repo CI が user の live config を変更して保証したことにはしない。

### 2. 指示は薄く、検証は共通化する

Hermes 対応のために各 skill / plugin へ説明ファイルを増殖させない。

- repo root `AGENTS.md` には「ここで作る skill / plugin は Codex と Hermes Agent の双方で読み込めることが必須」という短い非交渉条件と、下位 guidance への router だけを置く。
- `skills/AGENTS.md` と `plugins/AGENTS.md` に、それぞれ固有の最小契約だけを置く。
- 反復する機械判定は共通 validator と test に集約する。
- host 公式仕様の長い説明を `AGENTS.md` に複製しない。

### 3. 互換性と露出複雑性を分ける

dual-host 対応は、ユーザーに常に二つの実行経路や schema を見せることを意味しない。skill 本文は標準 `SKILL.md` を共有し、plugin は host ごとの薄い manifest / registration adapter を持つ。ユーザー向け動作は一つに保ち、host 差は packaging と verification の境界へ閉じ込める。

## Standalone skill の repository-level discovery route

このcheckoutのstandalone skillsは、`~/.hermes/config.yaml`の`skills.external_dirs`から発見させる。`SKILLS_REPO`はcheckout rootの絶対path（このcheckoutでは`/Users/omitsuhashi/repos/omitsuhashi/skills`）へ展開される環境変数とし、相対pathを指定しない。

```yaml
skills:
  external_dirs:
    - ${SKILLS_REPO}/skills
```

この設定によりcurrent `skills/task-management/SKILL.md`をrepositoryから直接scanできる。ただし、external directoryはwrite-protection boundaryではない。checkoutをread-onlyに保つ必要がある場合はfilesystem permissionで書き込みを拒否するか、書き込みcapabilityを持たない別profile / toolsetを使う。

2026-07-23 migrationではrepository compatibilityだけを検証した。live `~/.hermes/config.yaml`は変更せず、`hermes skills list`によるcurrent visibilityも確認していない。

## Repo guidance の変更

### Repo root `AGENTS.md`

次の意味を短く追記する。

> このリポジトリで作成・変更する skill と plugin は、Codex と Hermes Agent の双方を対象とし、Hermes Agent が discovery / load できる構造を必須とする。詳細は `skills/AGENTS.md` または `plugins/AGENTS.md` に従う。

root guidance はこの router を超えて長くしない。

### `skills/AGENTS.md`

最低限、次を契約化する。

- skill entrypoint は `<skill-dir>/SKILL.md` とし、YAML frontmatter に非空の `name` と `description` を持つ。
- `description.md` を discovery requirement として作らない。
- `agents/openai.yaml` は Codex metadata であり、Hermes compatibility の代替ではない。
- directory 名、frontmatter `name`、登録名の不一致を作らない。
- Hermes に存在しない tool 名や Codex 固有 UI / tool assumption を本文へ無条件に埋め込まない。host 差がある場合は capability check、代替経路、明示的な platform boundary を記載する。
- standalone skill の配布経路を install / tap / hub / `skills.external_dirs` のいずれかとして文書化し、live verification 時は `hermes skills list` で可視性を確認する。
- Hermes 固有 metadata は必要な場合だけ追加し、`name` / `description` 以外を一律必須にはしない。

### `plugins/AGENTS.md`

最低限、次を契約化する。

- Codex 用 `.codex-plugin/plugin.json` と Hermes 用 `plugin.yaml` をそれぞれ持ち、name / version / description の整合を保つ。
- Hermes plugin は import 可能な `__init__.py` と `register(ctx)` を持つ。
- 同梱 skill は `ctx.register_skill(...)` で登録する。
- 登録 tool は安定した名前、説明、input schema、safe error boundary を持ち、manifest の宣言と一致させる。
- standalone companion skill に依存する場合は、暗黙に利用可能とみなさず、別 install prerequisite と unavailable fallback を文書化する。
- live verification 時は対象 profile で plugin enable / list / expected version / smoke を確認する。

## 機械検証

共通 validator を追加し、既存 skill / plugin 固有 test と重複しない静的条件だけを担当させる。

### Skill checks

- `skills/*/SKILL.md` の存在。
- YAML frontmatter の非空 `name` / `description`。
- directory 名と `name` の一致。
- Hermes discovery 用の別ファイルとして `description.md` を追加していないこと。本文中の単なる言及は機械判定しない。
- Hermes compatibility を主張する場合に、Codex metadata だけを根拠にしていないこと。

tool vocabulary や対話品質のように機械判定で誤検知しやすい事項は、validator が雑に採点せず、review checklist と対象 skill の behavior test で扱う。

### Plugin checks

- `.codex-plugin/plugin.json`、`plugin.yaml`、`__init__.py` の存在。
- host manifests 間の name / version / description の整合。
- `register(ctx)` の存在。
- 同梱 skill ごとに、validated frontmatter `name` と一致する literal name を持つ `ctx.register_skill(...)` が exact `ctx` receiver から呼ばれること。
- `skills_root` / `plugins_root` のどちらかが directory でなければ repository validation を fail closed にすること。
- Codex / Hermes の version を比較前にそれぞれ非空 string として検証し、YAML block marker だけの required scalar を拒否すること。
- manifest が宣言する tool / toolset と registration の整合を、plugin 固有 contract test で確認できること。

Python source の文字列検索だけで runtime registration の正しさを断定しない。静的 validator は欠落を早期検出し、import / fake context / Hermes smoke test が動作を確認する二層構成にする。

### CI integration

共通 validator と unit tests を既存 skill architecture workflow に追加する。live Hermes home や user config を CI で変更せず、Hermes runtime を必要とする smoke は hermetic temporary home または明示的な local verification とする。

## 既存成果物への適用

### `decide-in-order`

skill 本体は作り直さない。次を追加する。

- Hermes 互換形式であることと、実際の discovery には install / tap / external directory 設定のいずれかが必要であることを配布文書へ記載する。
- Hermes からの可視性確認手順を記載する。
- `agents/openai.yaml` を Hermes 用ファイルと誤認させない。

### `task-management`

2026-07-23 migration後はstandalone `skills/task-management/SKILL.md`だけをcurrent surfaceとする。旧plugin manifest / registration / smoke testを復元せず、repository-level `skills.external_dirs`でcheckoutの`skills` directoryを発見させる。current task-managementは`decide-in-order`をdependencyにせず、自身のtask contractだけで完結する。

## 非目標

- Hermes 用 `description.md` を新設すること。
- 全 skill に Hermes 固有の任意 metadata を強制すること。
- 各 skill / plugin に同じ host 説明を複製すること。
- standalone skill を plugin 内へコピーして source of truth を二重化すること。
- repo CI や本変更が `~/.hermes/config.yaml`、live plugin、credential、profile を変更すること。
- repository compatibility test の成功だけで live install 済みと表現すること。

## 受け入れ条件

- repo root、`skills/`、`plugins/` の guidance から「Hermes で読めることが必須」と必要条件を発見できる。
- `description.md` は不要で、`SKILL.md` frontmatter が必要であることが明記される。
- standard skill、Codex metadata、Hermes discovery の役割が区別される。
- Codex / Hermes plugin manifests と Hermes registration requirements が明記される。
- validator / tests が代表的な missing file、frontmatter、manifest drift、registration 欠落を fail させる。
- validator は live install 済みという虚偽の保証をしない。
- `decide-in-order` と `task-management` のstandalone discovery routeが文書化される。
- `task-management` のstandalone contract testsと全repo validationが通る。
- live stateを変更せず、repository compatibilityと未実施のlive config / list verificationを区別できる。

## 実装順序

1. guidance の failing contract tests を追加する。
2. repo root、`skills/AGENTS.md`、`plugins/AGENTS.md` を最小記述で実装する。
3. dual-host validator と fixture-based tests を追加する。
4. `decide-in-order` と `task-management` の distribution / dependency 文書と既存 test を補強する。
5. CI、skill / plugin validators、Hermes hermetic smoke、wiki checks を通す。
6. live install / update は別作業として、明示承認後に実施する。

## 関連ページ

- [Decide In Order Skill 設計](decide-in-order-skill-design.md) — standalone skill と task-management integration の責務境界。
- [Decide In Order Skill 実装計画](2026-07-17-decide-in-order-implementation-plan.md) — 現行 skill 実装時の test-first 手順と検証証跡。
- [GitHub Projects 直接接続型 Task Management Skill 仕様](direct-github-projects-task-management/spec.md) — current standalone task-management contract。
- [Portfolio OS Task Backend Plugin Skill Spec](portfolio-os-task-backend-plugin-skill-spec.md) — 2026-07-23 migrationでsupersedeされた旧plugin contractのhistorical evidence。

## 出典

- [Hermes Agent Skills System](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md)
- [Build a Hermes Plugin](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/build-a-hermes-plugin.md)
- [decide-in-order SKILL.md](../../../skills/decide-in-order/SKILL.md)
- [task-management SKILL.md](../../../skills/task-management/SKILL.md)
- historical source paths（current linksではない）: `plugins/task-management/plugin.yaml`、`plugins/task-management/__init__.py`、`plugins/task-management/.codex-plugin/plugin.json`
- 2026-07-17 read-only local evidence: `hermes skills list`（exit 0、42 enabled、`decide-in-order` row なし）
- 2026-07-17 historical / superseded read-only evidence: `hermes plugins list --plain --no-bundled`（exit 0、`enabled user 0.1.0 task-management`）
