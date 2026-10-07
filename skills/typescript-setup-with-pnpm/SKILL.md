---
name: typescript-setup-with-pnpm
description: Set up TypeScript projects with pnpm and a reproducible development baseline for CLI, API, or frontend development only when the user explicitly invokes typescript-setup-with-pnpm.
---

# TypeScript Setup With pnpm

## 適用条件

利用環境が認識する明示的な skill 呼び出し（例: `$typescript-setup-with-pnpm` や skill 選択機能）で使用を指示された場合だけ、本文・参照資料の読み込みと手順の実行を行う。TypeScript や pnpm に関する話題、一般的なプロジェクト作成・セットアップの依頼からは採用を推定しない。

## 入力・出力・必要な能力

- 入力: 対象ディレクトリ、用途と実行環境（未定でも可）、既存設定、依頼されたセットアップ範囲。
- 出力: 依頼範囲のプロジェクト設定・開発依存・lock file と、採用バージョン、実施した検証、未完了事項。
- 必要な能力: ファイル読取・編集、コマンド実行、利用可能な Node.js と pnpm。バージョン確認・依存取得にはネットワーク、hook 導入には Git が必要。能力が足りなければ該当操作を未実施と示し、設定案や実行可能な手順を渡す。

## 適用と既定値

新規の継続開発では `Node.js LTS + pnpm + TypeScript + Biome + Vitest + Lefthook` を既定とする。共通の開発基盤を整え、CLI・API・フロントエンドは必要になった用途だけを追加する。用途未定なら Node.js 向けの型チェック設定を出発点とし、フロントエンドを追加するときにその環境の設定を用意する。

既存プロジェクトでは manifest、lock file、Node バージョン、`tsconfig`、scripts、lint・format・テスト・hook の設定を読み、同じ役割の仕組みを尊重する。初期セットアップを理由にツール移行や major 更新を行わない。相談のみなら推奨を示し、セットアップを依頼されていれば実行する。

- `typescript`: `strict` を有効にした型チェック。実行・テスト・ビルドが通っても型チェック済みとは扱わない。
- `@biomejs/biome`: lint・format・import 整理。既存の ESLint / Prettier や用途固有のルールがあれば、その設定を優先する。
- `vitest`: 継続開発のテスト入口。使い捨てスクリプトでは省略できる。
- `lefthook`: Git を使う継続開発のコミット前検査。Git を使わない実験では省略し、既存 hook があればその仕組みに統合する。
- `@types/node`: Node.js 向けのコード・設定に追加し、採用した Node.js と同じ major の最新安定版を選び、解決した完全なバージョン番号で追加する。

API / UI フレームワーク、monorepo、CI、公開・デプロイ設定は依頼されたときに追加する。コマンド整理は `package.json` の scripts を使う。

## バージョンと再現性

新規では、セットアップ時点の最新 LTS の Node.js と、各ツールの最新安定版を公式配布情報で確認する。Node.js の Current や prerelease は、ユーザーの指定または要件がある場合に選ぶ。

- Node.js は既存の管理方法を使う。新規で指定がなければ、選んだ実バージョンを `.node-version` に記録する。このファイルだけで Node.js が切り替わるわけではないため、実行中の `node --version` も確認する。
- pnpm は最新安定版を選び、`packageManager` に実バージョンを記録する。既存の pnpm が古ければ、プロジェクト内で使える版を用意する。マシン全体の設定変更は依頼範囲に合わせる。
- 開発ツールは `--save-exact` で記録し、`pnpm-lock.yaml` を Git 管理する。`@latest` は初回の選択だけに使い、以後は manifest と lock file に従う。
- バージョン・peer dependency に非互換があれば確認した互換版を選び、理由を示す。TypeScript compiler API を使うツールは、最新 TypeScript と対応しているか確認する。

## セットアップ

### 共通基盤

未初期化のプロジェクトでは、選んだ pnpm で初期化する。未公開のアプリ・実験では `private: true` とし、ライセンスはユーザーや既存方針に合わせる。

```bash
pnpm init --init-type module --init-package-manager
pnpm add --save-dev --save-exact typescript@latest @biomejs/biome@latest vitest@latest
pnpm exec biome init
```

既存ファイルに対して `init` を繰り返さず、必要な項目を統合する。Node.js 向けには、この時点で対応する `@types/node` も開発依存へ追加する。

`.gitignore` に `node_modules/`、生成する `dist/`、`coverage/`、`.vitest/` を必要に応じて追加する。Biome の生成設定を基に、Git を使う場合は `vcs.enabled` と `vcs.useIgnoreFile` を有効にし、`.gitignore` を尊重させる。好みだけの大量のルールは追加しない。

scripts は導入したツールに合わせて統合する。次は完成形の一例であり、依存関係や既存 scripts を置き換えるための全 manifest ではない。

```json
{
  "private": true,
  "type": "module",
  "scripts": {
    "check": "biome check .",
    "fix": "biome check --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  }
}
```

### 型チェックと実行環境

Node.js で TypeScript を直接実行する場合の最小例:

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "lib": ["ESNext"],
    "module": "NodeNext",
    "types": ["node"],
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noEmit": true,
    "rewriteRelativeImportExtensions": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true
  },
  "include": ["src", "tests"]
}
```

対象パスは実際の構成に合わせる。テストも型チェック対象に含め、Vitest の API は `vitest` から明示的に import する。空のソース構成に対する型チェックを成功扱いしない。

Node.js の直接実行には対応する版が必要で、型を消すだけでは実行できない構文・JSX・`tsconfig` の paths は扱えない。Node 向けビルド、CLI / API の追加、フロントエンドのセットアップを依頼された場合は [用途別の設定](references/runtime-targets.md) を読む。

### Git hook

Lefthook を追加する前に `git config --get core.hooksPath` と `git rev-parse --git-path hooks` で実際の hook 経路と既存 hook を確認する。既存の pre-commit / Husky 等がある場合はその仕組みを使う。衝突する hook を上書きせず、影響しないセットアップを続ける。

新規に Lefthook を使う場合は、postinstall による自動 hook 書込みを無効に記録し、設定後に明示的に導入する。次のコマンドは `pnpm-workspace.yaml` の `allowBuilds` に `lefthook: false` を保存するため、そのファイルも Git 管理する。

```bash
pnpm add --save-dev --save-exact --allow-build='!lefthook' lefthook@latest
```

最小 `lefthook.yml`:

```yaml
pre-commit:
  commands:
    biome:
      run: pnpm exec biome check --no-errors-on-unmatched --files-ignore-unknown=true {staged_files}
```

```bash
pnpm exec lefthook install
```

標準構成は検査だけを行う。修正は `pnpm run fix` で実施し、差分を確認して再度 stage する。自動再ステージは依頼された場合にだけ検討する。pnpm で依存を追加しただけでは hook の有効化は保証されないため、導入後や clone 後に実際の hook を確認する。

## 検証と完了

導入した scripts に従って `pnpm run check`、`pnpm run typecheck`、テストがあれば `pnpm test` を実行する。必要なファイルだけに安全な修正を適用し、空のテスト実行を成功扱いしない。hook 経由で同じ検査を実行済みなら重複させない。

- manifest と lock file が整合することを `pnpm install --frozen-lockfile` で確認する。依存の build script が必要なら、そのパッケージと理由を確認して許可する。
- 実行・ビルドを導入した場合はその入口を確認する。frontend の build や Vitest は、別途の型チェックの代わりにはしない。
- hook を導入した場合は、実際の pre-commit 経路が動き、違反時に commit を止めることを一時的な Git repository で確認する。ユーザーの repository に検証用 commit は作らない。

採用バージョン、変更した設定、実施した検証、テストや用途が未作成で確認できない項目を伝える。依頼範囲の検証が通れば完了とし、新たな失敗や変更がない限り検証を広げない。

## References

- Node.js release policy: https://nodejs.org/en/about/previous-releases
- pnpm init / version pin: https://pnpm.io/cli/init
- pnpm frozen install: https://pnpm.io/cli/install
- pnpm dependency build policy: https://pnpm.io/cli/add#--allow-build
- TypeScript strict: https://www.typescriptlang.org/tsconfig/strict.html
- Biome quick start: https://biomejs.dev/installation/quick-start/
- Biome Git hooks: https://biomejs.dev/recipes/git-hooks/
- Vitest guide: https://vitest.dev/guide/
- Lefthook install: https://lefthook.dev/usage/commands/install/
