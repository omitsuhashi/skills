# 言語・フレームワークへの対応例

採用技術に合う節だけ読む。以下はこのスキルの設計例で、各技術が要求する唯一の標準構成ではない。ファイルは必要になった時点で作り、単純な機能は一つのファイルでもよい。具体的な設定や予約規約は、対象バージョンの公式資料に照合する。

## Go

```text
go.mod
cmd/server/main.go              # 起動・組み立てが必要な場合
internal/
  orders/
    orders.go                   # 他モジュールに公開する窓口
    place_order.go
    place_order_test.go
    internal/                   # 別packageへの分離が必要な実装だけ
      postgres/store.go
  inventory/
    inventory.go
  platform/
    database.go
```

この例では `orders` は業務モジュールを指し、`go.mod` のGo moduleとは区別する。Goでは同じディレクトリの通常の実装ファイルは同じpackageなので、ファイルを分けただけではpackage境界にならない。

ネストした `orders/internal/` のpackageは、その親を根とするツリーの外からimportできない。この制約は兄弟モジュールから実装を隠すのに使える。一方、上位の `internal/` だけでは兄弟間の依存を禁止できず、モジュール間の許可関係には別の構造検証が必要。小さなCLIやライブラリには `cmd/` もこの階層も必須ではない。

根拠: [Go moduleの構成](https://go.dev/doc/modules/layout)、[internal packagesのimport規則](https://pkg.go.dev/cmd/go#hdr-Internal_packages)。

## Python・フレームワーク非依存

```text
pyproject.toml
src/product/
  __init__.py
  __main__.py                   # CLIの入口が必要な場合
  orders/
    __init__.py
    api.py                      # プロジェクトで定める公開窓口
    place_order.py
    persistence.py              # I/O分離が必要な場合
  platform/
    __init__.py
    database.py
tests/
  orders/test_place_order.py
```

`src/` は配置の選択例。既存のflat layoutやテスト配置を、構成方針だけを理由に全面変更しない。`api.py` はHTTP専用という意味ではなく、この例の公開Python APIを表す。命名はプロジェクトで一貫させる。

Pythonでは公開窓口の命名だけでは内部importを禁止できない。既存のimport検証や構造テストで依存境界を検証する。パッケージング・開発依存のセットアップはそのプロジェクトの既存手順に従い、このスキルでは特定のパッケージ管理ツールを要求しない。

### FastAPI等、組み立て式のWebアプリ

上の例に `main.py` と、必要なモジュールの `router.py` を追加できる。HTTP入力を業務操作へ渡し、起動・組み立て側でrouterを登録する。`routers/`・`services/`・`repositories/` を全業務横断の必須階層にせず、業務モジュール内で必要な責務を分ける。`APIRouter` はHTTPの構成手段であり、他モジュールが業務操作を呼ぶための公開窓口とは区別する。

FastAPI以外でも、対象フレームワークの起動・登録・検出規約を確認し、同じ責務を対応させる。

根拠: [FastAPI: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)。

### Django等、規約による検出を持つWebアプリ

```text
manage.py
config/                         # settings・ルートURL等
orders/
  __init__.py
  apps.py
  models.py
  views.py
  urls.py
  migrations/
  operations.py                 # 分離が必要な業務操作
  tests/
```

Django appを業務境界の候補とし、models・views・migration等の規約を維持する。単純なCRUDに別のdomain modelやrepositoryを必須としない。必要な業務公開窓口はapp内で定める。

appの移動はimport変更だけで完了としない。app登録、app label、既存migrationの参照とDBとの対応を確認し、移動をテーブル削除・再作成で解決しない。別appへのモデル関連やmigration上の参照はフレームワークが扱う関係として区別し、必要な依存と所有者を記録する。それを他モジュールのデータを自由に読み書きする許可にはしない。

根拠: [Django: Applications](https://docs.djangoproject.com/en/6.0/ref/applications/)、[モデルの関係](https://github.com/django/django/blob/main/docs/topics/db/models.md)、[他appを参照するmigration](https://docs.djangoproject.com/en/6.0/topics/migrations/#accessing-models-from-other-apps)。記載URLの版は適用先の版に合わせて確認する。

## TypeScript・React等のUI

```text
src/
  main.tsx                      # 採用ツールの入口に合わせる
  features/
    orders/
      index.ts                  # 意図的に公開する型・操作・UI
      place-order.ts
      order-form.tsx
      order-form.test.tsx
  shared/
    ui/
    platform/
```

`features/` は業務単位、`shared/` は業務所有者を持たない共有部品の例。Reactを使わないTypeScriptのサーバー・CLI・ライブラリでも、同じ責務を通常の `.ts` ファイルで配置できる。実際の入口と公開exportは採用するビルド・配布方式に合わせる。

公開 `index.ts` を経由しても、内部の循環や実行環境の混在は解消されない。公開exportは必要なものに絞り、依存検証はalias・相対import・再exportも含む実際の解決先を対象にする。UIに必要な公開データの契約と、サーバーの業務・永続化実装を区別する。

### Next.js App Router

```text
src/
  app/
    orders/page.tsx             # URLと画面の組み立て
    api/orders/route.ts         # HTTP endpointが必要な場合
  features/
    orders/
      client.ts                 # ブラウザー向け公開窓口の例
      server.ts                 # サーバー向け公開窓口の例
      order-form.tsx
      place-order.ts
```

`src/` とapp外の `features/` は選択肢で、Next.jsではapp内へのcolocationも可能。既存の選択を尊重し、ルーティング規約と業務の所有境界を両立させる。Pages Routerのプロジェクトを、この例に合わせるためだけにApp Routerへ移行しない。

`client.ts`・`server.ts` という名前自体は実行環境の境界を強制しない。両方を一つのbarrelから再exportせず、必要なサーバー専用の保護とビルド検証を選ぶ。フレームワークのクライアント・サーバー境界と、業務モジュール間の境界は別々に検証する。

根拠: [Next.js: Project structure](https://nextjs.org/docs/app/getting-started/project-structure)、[Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components#preventing-environment-poisoning)。

## 複数アプリ・言語のプロジェクト

独立した実行・配布単位が複数ある場合に `apps/` や `packages/` 等を導入する。言語が複数という理由だけで全体をmonorepo化しない。

各アプリ内を上の原則で整理し、境界を越えるAPI・schemaには所有者と正本を一つ定める。生成物は正本から再生成し、同じ契約を言語ごとに手編集する前提にしない。migrationは所有するアプリ・モジュールに合わせ、ルートの `db/` に統一する必要はない。
