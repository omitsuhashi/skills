# 用途別の設定

Node 向けビルド、CLI / API の追加、フロントエンドをセットアップする場合だけ読む。共通の開発基盤は [SKILL.md](../SKILL.md) に従い、選んだ用途に必要な設定だけ追加する。

## Node.js の CLI・スクリプト・API

型を消すだけで動くコードを対応する Node.js で実行するなら、共通基盤の `tsconfig` と `"type": "module"` を使う。相対 import に `.ts` 拡張子を付け、型だけの import は `import type` にする。

```bash
node src/main.ts
node --watch src/main.ts
```

実際に存在する入口を `start` / `dev` scripts へ登録する。Node.js 24 系では v24.12.0 以降の type stripping が安定しているが、`tsconfig` は実行時に読まれず、JSX、enum、parameter properties、decorator、paths による alias などはこの経路で変換されない。必要ならその要件に対応する runner / compiler を選び、型チェックは別途維持する。

API のフレームワークや CLI 引数 parser は、依頼された機能・デプロイ先・既存設定から選ぶ。開発基盤だけの依頼で API サーバーや CLI を先に生成しない。

### JavaScript を配布・実行する場合

公開する CLI、TypeScript を直接扱えないデプロイ先などでは JavaScript を出力する。Node で出力を実行するなら module resolution は Node に合わせる。

`tsconfig.build.json` の例:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "noEmit": false,
    "rootDir": "src",
    "outDir": "dist"
  },
  "include": ["src"],
  "exclude": ["tests", "**/*.test.ts", "**/*.spec.ts"]
}
```

```bash
pnpm exec tsc -p tsconfig.build.json
node dist/main.js
```

`rewriteRelativeImportExtensions` により、相対 `.ts` import は出力で `.js` へ書き換わる。`target` はデプロイ先の Node が実行できる値に合わせる。TypeScript 固有の変換構文が必要なら `erasableSyntaxOnly` を見直す。`paths` だけを設定しても出力の import は書き換わらない。

テストを含む型チェックと、配布するソースだけの build を分ける。npm 公開・`bin`・shebang・宣言ファイル等は配布が依頼された範囲で整える。

## フロントエンド

選んだフレームワークの公式 generator と生成された `tsconfig` を基にする。React 等のフレームワーク自体は共通基盤の既定値にしない。既存の source を持つディレクトリへ generator を無条件に実行しない。

bundler が JavaScript を生成する構成では、`moduleResolution: "Bundler"` と bundler に合う `module`（`"Preserve"` / `"ESNext"`）、`noEmit: true`、`strict: true` を使う。ブラウザ用 `lib`（DOM 等）・JSX・環境型はそのフレームワークの設定に従う。Node 用の `types: ["node"]` だけでブラウザの型環境を代用しない。

Node.js の設定・API とブラウザのコードが同居するなら、それぞれの `tsconfig` で環境を表す。生成済みの project references や typecheck scripts を尊重し、一つの `tsconfig` に全環境の globals を混ぜない。

Vitest は既存の Vite 設定を使える。DOM を必要とするテストがあるときに、その対象に合う browser / DOM 環境を追加する。ブラウザ操作を含む E2E は依頼されたときに導入する。

ユーザーが Vite+ を選んだ場合は、提供される Oxlint / Oxfmt / Vitest を使い、同じ役割のツールを重ねて導入しない。既存の Vite+ も尊重する。共通基盤の依頼だけでは Vite+ への移行や global CLI の導入を行わない。

最後にフレームワークの型チェック、テストがあればテスト、production build を確認する。generator の出力に lint 違反が残る場合は、その出力も確認して解消する。generator が成功しただけでは検証完了とは扱わない。

## References

- Node.js TypeScript support: https://nodejs.org/api/typescript.html
- TypeScript module options by environment: https://www.typescriptlang.org/docs/handbook/modules/guides/choosing-compiler-options.html
- Relative import extension rewrite: https://www.typescriptlang.org/tsconfig/rewriteRelativeImportExtensions.html
- Vite scaffolding: https://vite.dev/guide/
- Vitest configuration: https://vitest.dev/guide/
- Vite+ local CLI: https://viteplus.dev/guide/local-cli
