---
kind: synthesis
created: 2026-06-10
updated: 2026-06-10
source_files:
  - knowledge/AGENTS.md
  - knowledge/wiki/syntheses/LLM Wiki Draft Review And Canonicalize Goal Spec.md
---

# Portfolio OS Install Review And Procedure

## 目的

`skills` repository に Portfolio OS 関連の余計な runtime 責務が混入していないかを確認し、Portfolio OS を導入する際の手順を repo-local な運用文書として残す。

この文書は `skills/llm-wiki` 本体の仕様ではない。`llm-wiki` は Portfolio OS などの固有 runtime から独立した汎用 Markdown wiki skill として維持する。

## レビュー結果

- レビュー対象は `origin/main` と同一の tracked tree であり、Portfolio OS 導入用の未反映差分ではなく、現行 repository 状態の静的レビューとして確認した。
- `skills/llm-wiki/` 本体には Portfolio OS, Hermes, commander, council, registry-core, governance-core, companies, profile-set などの固有 runtime 語彙は入っていない。
- Portfolio OS に触れているのは `knowledge/` 配下の source / synthesis 文書であり、汎用 skill 本体の実装責務には混入していない。
- repo-root `AGENTS.md` は thin router のままで、durable な計画・設計・手順は `knowledge/wiki/...` に置く方針と整合している。
- `.idea/` は tracked だが、Portfolio OS 導入物ではない。IDE 設定を repo に保持するかは別判断として扱う。

## 導入しないもの

この `skills` repo 側では、Portfolio OS 導入のために次を追加しない。

- Portfolio OS runtime script
- Hermes profile
- commander / council profile
- runtime registry
- profile-set
- target repository への live install 結果
- `skills/llm-wiki/` への Portfolio OS 固有手順

Portfolio OS 固有の lifecycle 実装と検証は、導入対象の runtime repository 側で管理する。

## インストール手順

### 1. 導入対象を確定する

- Portfolio OS を入れる対象 repository と target root を明示する。
- `skills` repository は汎用 skill の配布元として扱い、Portfolio OS runtime の install target にはしない。
- 対象 repository の `AGENTS.md` / knowledge root guidance / installer documentation を先に読む。
- `git status --short --branch` で作業ツリーの状態を確認し、既存のユーザー変更を巻き込まない。

### 2. 既存状態を確認する

- 既存の commander / profile / managed state があるか確認する。
- 既存 install がある場合、`install` を自動で `update` 相当に切り替えない。
- user-modified managed file がある場合、上書き・削除せず conflict として扱う。
- runtime registry / skill cache / dependency lock など global state と、local managed profile state を分けて確認する。

### 3. dry-run で差分を確認する

- 対象 repository の installer が提供する dry-run または diff command を使い、書き込み前に生成・変更・削除予定を確認する。
- lifecycle surface は `install`, `update`, `diff`, `uninstall` のように明示的な操作名へ分ける。
- `diff` は update の dry-run として扱い、missing managed file を成功扱いしない。
- `repair` のような曖昧な自動修復分岐は避ける。

### 4. apply を実行する

- dry-run / diff の結果が妥当な場合だけ apply する。
- `install` は未導入状態の初回導入だけに使う。
- 既存導入を更新する場合は `update` を使う。
- user-modified managed file は digest や同等の管理情報で判定し、modified state を消さない。
- live runtime への書き込み、外部送信、権限変更を伴う場合は事前に明示確認する。

### 5. 導入後に検証する

- 対象 repository の installer tests / validator / lint / compile check を実行する。
- Portfolio OS 固有語彙が汎用 skill 本体へ混入していないことを `rg` で確認する。
- `git diff --check` を実行する。
- 導入結果、検証結果、未検証項目を対象 repository の knowledge root または maintained documentation に記録する。

## `skills` repo での確認コマンド

```bash
git status --short --branch
git diff --stat origin/main...HEAD
rg -n "Portfolio OS|PortfolioOS|Hermes|work_unit|commander|council|registry-core|governance-core|companies|Kanban|profile-set" skills/llm-wiki
git diff --check
```

期待値:

- branch / working tree に意図しない差分がない。
- `skills/llm-wiki` に Portfolio OS 固有語彙が出ない。
- whitespace error がない。

## 判断

現行の `skills` repo は、Portfolio OS 固有 runtime を `llm-wiki` 本体へ混ぜないという設計意図を維持している。今後 Portfolio OS 導入手順を更新する場合も、この文書の更新に留め、汎用 skill 本体には対象 repository 固有の lifecycle 手順を入れない。
