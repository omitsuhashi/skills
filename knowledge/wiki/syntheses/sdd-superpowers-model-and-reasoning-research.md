---
summary: Superpowers v6.2.0 のモデル選択、思考強度と host adapter 境界を一次情報から調べた結果を確認できる。
knowledge_status: historical
aliases:
- 思考強度とモデル選択
---
# Superpowers SDD のモデル選択・Reasoning・Host 境界調査

## 適用範囲と履歴

当時の SDD 設計・実装証跡であり、本文の current / active / 実行可能は当時の範囲を指す。SDD 既定ルートは [PR #58](https://github.com/omitsuhashi/skills/pull/58)、KIS / decide-in-order 本体は commit `99fdaf2` で削除されている。現行の作業ツリー保全規約は repository root の `AGENTS.md` を参照する。部分的な仕様置換と当時の承認・未承認の区別は本文に保持する。

## 調査条件

- 調査日: 2026-07-27
- 対象: `obra/superpowers` の current `main` と最新 release `v6.2.0`
- 一次情報: 公式 GitHub repository の source、README、release notes、commit history のみ
- current `main` の最新 commit は release commit `3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9` であり、GitHub 上の latest release は `v6.2.0` である。したがって、本調査時点では current `main` と latest release の結論は同じである。
  出典: [main commit history](https://github.com/obra/superpowers/commits/main/)、[release commit](https://github.com/obra/superpowers/commit/3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9)、[v6.2.0 release](https://github.com/obra/superpowers/releases/tag/v6.2.0)

## 結論

| 問い | 結論 |
|---|---|
| dispatch ごとのモデル選択 | **ある。** SDD は全 subagent dispatch で model を明示するよう要求し、task / role / risk に応じて相対的な capability tier を選ばせる。 |
| Thinking Effort / `reasoning_effort` | **ない。** model とは独立した reasoning effort の選択値、伝播、fallback、escalation contract は定義されていない。 |
| Host-specific dispatch | **action-level core + host adapter。** SDD 本体は `Subagent (general-purpose)` という抽象 action を書き、host 固有 tool / lifecycle は reference 側で解決する。Codex の mapping はあるが、Hermes の公式 mapping はない。 |
| spec / plan / implementation の分担 | `brainstorming` が design/spec と Human approval、`writing-plans` が実行可能 plan、SDD が plan execution と review を担当する。 |

## 1. dispatch ごとのモデル選択

### 現行仕様

現行 SDD には明示的な `Model Selection` section があり、次の相対 tier を task ごとに選ぶ。

- clear spec の 1〜2 file mechanical implementation: fast / cheap
- multi-file integration、pattern matching、debugging: standard
- architecture / design、final whole-branch review: most capable available
- task review: diff の size / complexity / risk に比例
- small scoped re-review: cheap-to-mid
- fix loop rounds 4〜5: 行き詰まった implementer より少なくとも一段上

さらに、すべての subagent dispatch で model を明示することを必須とし、省略時は session model を継承して cost 制御が崩れると説明している。
出典: [`subagent-driven-development/SKILL.md` Model Selection](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L140-L171)

この model 指定は説明上の推奨だけではない。implementer、task reviewer、scoped re-reviewer の各 dispatch template が `[MODEL — REQUIRED]` field を持つ。
出典: [implementer template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/implementer-prompt.md#L4-L10)、[task reviewer template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/task-reviewer-prompt.md#L8-L14)、[re-review template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/re-review-prompt.md#L8-L14)

### 粒度と抽象度

選択粒度は「run 全体で一つ」ではなく、implementer / task reviewer / re-reviewer / final reviewer という **dispatch 単位**である。一方、仕様は `Claude Opus` や `gpt-*` のような具体 model catalog を持たず、`cheap`、`standard`、`most capable available` という **host 相対の capability class** に留めている。template も具体名ではなく `[MODEL]` placeholder である。
出典: [`Model Selection`](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L140-L171)、[`[MODEL]` placeholder contract](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/task-reviewer-prompt.md#L153-L169)

model routing は `v5.0.0` で task type 別 guidance として導入され、`v6.0.0` で「every dispatch states its model」が template-level requirement になった。したがって、「現状の Superpowers に subagent model 選択がない」という認識は現在は正しくない。
出典: [`v5.0.0` model selection release note](https://github.com/obra/superpowers/blob/v6.2.0/RELEASE-NOTES.md#L421-L424)、[`v6.0.0` every-dispatch requirement](https://github.com/obra/superpowers/blob/v6.2.0/RELEASE-NOTES.md#L83-L93)

## 2. Thinking Effort / reasoning effort

current `v6.2.0` の SDD skill、三つの dispatch template、Codex mapping、README、release notes には、`reasoning_effort`、`thinking_effort`、`reasoning_level` またはそれに相当する独立した dispatch parameter がない。dispatch template の control fields は `description`、`model`、`prompt` であり、effort field は定義されていない。
確認対象: [SDD skill](https://github.com/obra/superpowers/tree/v6.2.0/skills/subagent-driven-development)、[implementer template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/implementer-prompt.md#L4-L10)、[task reviewer template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/task-reviewer-prompt.md#L8-L14)、[re-review template](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/re-review-prompt.md#L8-L14)、[Codex reference](https://github.com/obra/superpowers/blob/v6.2.0/skills/using-superpowers/references/codex-tools.md)

SDD は、implementer が task により多くの reasoning を要する場合には「より capable な model で再 dispatch」する。つまり現行の escalation 軸は **reasoning effort を同一 model 内で上げることではなく、model capability を上げること**である。
出典: [`BLOCKED` handling](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L210-L222)、[`fix-loop` model escalation](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L285-L297)

task reviewer output にある `**Reasoning:**` は verdict の根拠を 1〜2 文で書く出力 field であり、推論強度の runtime setting ではない。
出典: [task reviewer output format](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/task-reviewer-prompt.md#L147-L155)

したがって、host が提供する Thinking Effort / `reasoning_effort` を role・risk ごとに選択・伝播・escalate する契約は、repo-local extension として追加する余地がある。ただし、これは upstream Superpowers の既存 model selection と別の軸として扱う必要がある。

## 3. Host-specific dispatch boundary

Superpowers は core skill を vendor-neutral な action vocabulary で記述し、host ごとの reference が action を実際の tool に写像する設計である。`v6.0.0` release notes は、旧 Claude 固有表現を「dispatch a subagent」等の action に置き換え、per-harness reference で runtime tool に mapping すると明記している。
出典: [`v6.0.0` One Set of Skills, Every Harness](https://github.com/obra/superpowers/blob/v6.2.0/RELEASE-NOTES.md#L109-L116)

### Claude Code

SDD template は `Subagent (general-purpose)` を共通 dispatch form として使う。`v6.1.0` では、Claude Code と Copilot の reference は host-specific な差分が残っていないとして削除された。よって Claude 固有 model ID や thinking setting は SDD core に固定されず、host の native dispatch 解決に委ねられている。
出典: [generic implementer dispatch form](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/implementer-prompt.md#L4-L10)、[`v6.1.0` harness-reference pruning](https://github.com/obra/superpowers/blob/v6.2.0/RELEASE-NOTES.md#L40-L48)

### Codex

Codex reference が規定するのは、`multi_agent = true` により `spawn_agent` / `wait_agent` / `close_agent` を有効にすることと、reviewer を review 後に close し、implementer は fix loop が終わるまで resume 可能な状態で保持する lifecycle である。model 名の tier 対応表や reasoning effort の設定・伝播はない。
出典: [`codex-tools.md`](https://github.com/obra/superpowers/blob/v6.2.0/skills/using-superpowers/references/codex-tools.md#L1-L10)

### Hermes Agent

公式 README が列挙する install / support 対象に Hermes Agent はなく、`using-superpowers` の host reference set にも Hermes mapping はない。本調査対象の公式 source からは、Hermes の dispatch tool、model selector、reasoning effort、resume lifecycle を Superpowers action に対応付ける contract を確認できなかった。これは「Hermes では実行不可能」という断定ではなく、**upstream が Hermes integration boundary を所有していない**という意味である。
出典: [README Quickstart host list](https://github.com/obra/superpowers/blob/v6.2.0/README.md#L10-L20)、[`using-superpowers` Platform Adaptation](https://github.com/obra/superpowers/blob/v6.2.0/skills/using-superpowers/SKILL.md#L52-L62)、[host reference directory](https://github.com/obra/superpowers/tree/v6.2.0/skills/using-superpowers/references)

## 4. brainstorming / writing-plans / SDD の責任分割

### `brainstorming`

rough idea から questions、constraints、success criteria、2〜3 approaches、design sections を詰め、design/spec を文書化し、self-review と Human written-spec approval を通す。terminal state は `writing-plans` の invocation であり、implementation skill を起動しない。
出典: [`brainstorming` overview and hard gate](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md#L1-L14)、[checklist and transition](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md#L15-L26)、[written spec and Human review gate](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md#L87-L113)

### `writing-plans`

承認済み spec / requirements を入力に、exact files、interfaces、test steps、code、verification、commits を含む実行可能 plan へ分解する。spec coverage の self-review は行うが、要求を新規定義する owner ではない。完了後は SDD または `executing-plans` へ handoff する。
出典: [`writing-plans` input and purpose](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md#L1-L19)、[task and interface structure](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md#L28-L81)、[spec coverage review and execution handoff](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md#L121-L141)

### `subagent-driven-development`

入口条件は implementation plan があること、tasks が概ね独立していること、同一 session で進めることである。SDD は plan を pre-flight し、fresh implementer、task review、fix loop、final whole-branch review を実行する。plan の矛盾や reviewer finding と plan text の衝突は Human に戻すが、ここで spec をゼロから定義し直さない。
出典: [`When to Use`](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L13-L35)、[SDD process](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L36-L95)、[pre-flight conflict handling](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md#L127-L139)

この分担は README の basic workflow でも、`brainstorming` → `writing-plans` → `subagent-driven-development` / `executing-plans` として明示されている。
出典: [README Basic Workflow](https://github.com/obra/superpowers/blob/v6.2.0/README.md#L184-L197)

## 関連ページ

- [SDD Implementation Skill 設計](https://github.com/omitsuhashi/skills/blob/9106339aee6aba76cb92a1d74a13cf000c25a531/knowledge/wiki/syntheses/sdd-implementation-skill-design.md) — 本調査結果を反映した当時の repo-local composition skill の設計（Git 履歴）。
- [Planning Authority Policy 仕様](https://github.com/omitsuhashi/skills/blob/9106339aee6aba76cb92a1d74a13cf000c25a531/knowledge/wiki/syntheses/planning-authority-policy/spec.md) — concrete model / reasoning choice を durable artifact に保存せず host runtime に委ねた当時の方針（Git 履歴）。

## 出典

- [obra/superpowers v6.2.0](https://github.com/obra/superpowers/tree/v6.2.0)
- [Superpowers v6.2.0 release notes](https://github.com/obra/superpowers/blob/v6.2.0/RELEASE-NOTES.md)
- [Subagent-Driven Development skill](https://github.com/obra/superpowers/blob/v6.2.0/skills/subagent-driven-development/SKILL.md)
- [Brainstorming skill](https://github.com/obra/superpowers/blob/v6.2.0/skills/brainstorming/SKILL.md)
- [Writing Plans skill](https://github.com/obra/superpowers/blob/v6.2.0/skills/writing-plans/SKILL.md)
- [Codex tool mapping](https://github.com/obra/superpowers/blob/v6.2.0/skills/using-superpowers/references/codex-tools.md)

## 切替前の補足情報

2026-09-10 の探索方式切替時に旧目録から回収した当時の説明（現行判定は上記の適用範囲を優先する）：

Superpowers v6.2.0のdispatch model選択、reasoning effort不在、Codex/Hermes adapter境界、brainstorming・planning・SDDの責任分割を一次情報で確認した調査。
