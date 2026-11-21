# LikeC4とPlannotatorを使う場合

既存モデル・利用可能なツールを確認し、対応する公式スキルがあれば実行環境のdiscoveryで解決する。この参照はDSLマニュアルや特定ホストの設定を複製せず、図とレビューをつなぐ要点を扱う。

## モデルを用意する

既存の`.c4` / `.likec4`とproject configを再利用する。新規モデルの構文の出発点が必要なら[小さな開始用モデル](../assets/starter.c4)を使う。これは架空の例なので、要求にあるノード・接続へ置き換え、保管先等を例のまま設計へ持ち込まない。project configを新規に置く場合の最小例は`{"name":"interface-map"}`。既存configは置き換えない。

DSLを生成・変更する際は、その版の公式資料や利用可能なドキュメント取得能力で構文を確認する。Node等の実行要件も選んだパッケージの要件に合わせる。道具の取得は現在の許可範囲でタスク用に行い、恒久的なhooksやエージェント設定を必要条件にしない。

- ノードと関係の`metadata.reviewId`等に永続IDを保持する。FQNは改名・移動で変わり得るモデル参照として、永続IDと分ける。
- `call`と`data`を別のrelationship kindにし、ラベルにも種類と操作・payloadを出す。`multiple true`で必要な関係を個別表示し、collapsed viewでも戻りデータと呼出が混ざっていないか見る。
- scoped viewは`view … of …`で明示する。`include *`はそのスコープと直下の子を基本にする。必要な外部の相手も含め、親契約と子の接続を照合できる図にする。
- 同じノードの内部図を参照し、図ごとに別ノードとして作り直さない。既存の内部図へのナビゲーションを確認する。未設計の内部を空の自動図で設計済みに見せない。
- ノードkindのstyleに形を定義し、四角・円柱・ブラウザ形などを一貫させる。エッジの種類と確実性の状態は別の凡例にする。

以下はCLIを利用できるshellでの例。山括弧部分は実際のタスクのパスに置き換え、既存のlauncherや依存関係を優先する。

```sh
likec4 validate --json --no-layout <model-dir>
likec4 export json --skip-layout --pretty -o <snapshot-model.json> <model-dir>
likec4 start --listen 127.0.0.1 --port <available-port> <model-dir>
```

validationは構文・参照の確認、exportは版の意味比較に使う。CLIの成功だけで親契約や表示の正しさを証明しない。ソースsnapshotも一緒に残す。モデルの内側へ置いた過去版の`.c4`は一緒に読み込まれることがあるため、履歴snapshotは別の読み込み範囲に置く。

サーバーが返す実URLを開き、`/view/<view-id>/`で対象図に到達する。既存図の内部を開き、外部の相手、ラベル、矢印、文字の重なりを実画面で確認する。

## 注釈と受け取り

Plannotatorの利用可能な連携やCLIを確認し、live-app annotationで当該モデルを開く。ローカルCLIの例:

```sh
PLANNOTATOR_DATA_DIR=<task-data-dir> PLANNOTATOR_REMOTE=0 \
PLANNOTATOR_AI=disabled PLANNOTATOR_SHARE=disabled \
plannotator annotate http://localhost:<model-port>/view/<view-id>/ \
  --app --gate --json --result-file <new-result.json>
```

利用中の版の`--help`を確認する。自動ブラウザ起動を使わない場合は、対応する版で`PLANNOTATOR_BROWSER=none`として返されたURLを開ける。上記の設定は試行・専用セッションの例であり、既存のユーザー設定を変更する指示ではない。

閲覧はInteract、指摘はAnnotateに切り替える。ノードにカーソルを置くとLikeC4のNavigate to viewを使える。注釈はノード・エッジを選択して書く。下書きはそのまま修正へ適用せず、Send Feedback等で返された内容を読む。

CLIが継続実行できる環境では結果を待って同じ作業を続ける。非同期の受け取り能力がない場合は、結果ファイル／出力の場所と再開方法をユーザーに示す。ツールが返すJSONの`feedback`が文章の場合もあるので、構造化targetが常に含まれると仮定しない。

受け取る際はdecisionも確認する。試行した版では`annotated`は指摘あり、`dismissed`は送信せず閉じた結果だった。`approved`等の確認も当該レビューの範囲に限る。既存result fileがある場合は内容と進行中セッションを確認し、再レビューは新しい結果先にする。

## 変更後に持ち越すもの

編集前のexportから、選択viewとテキスト・モデル参照を永続reviewIdへ対応づける。ノードのdata-testidがFQNを含む場合も、エッジのDOM selectorが描画順だけを示す場合もある。照合が一意でなければ、候補と対象図を示して確認を戻す。

ノード・エッジのツール内部IDは、別要素の追加等でも変わり得る。source/target/kind/payloadと永続reviewIdで前後を比較し、生成IDの違いだけで削除・追加と判定しない。

修正前のピンが新しい図へ戻るとは限らない。元コメント、対象ID、修正内容、対象viewへのURLを記録に残して確認を返す。ピンの自動修復まで必要なら、別途adapterや注釈ツールの改善として扱う。

## 確認した条件と参照

2026-11-06にLikeC4 1.60.0とPlannotator 0.28.50の実UIで、二段階の内部図、ノード／エッジ注釈、CLIへの返却、モデル修正後の表示を確認した。同条件の復元試行ではコメント本文は残っても旧ピンは戻らなかった。これを全バージョン・全操作の性質とはしない。

- [LikeC4公式スキル](https://github.com/likec4/likec4/blob/main/skills/likec4-dsl/SKILL.md)
- [Scoped views](https://likec4.dev/dsl/views/)、[Relationships](https://likec4.dev/dsl/relationships/)、[Styling](https://likec4.dev/dsl/styling/)
- [Plannotator 0.28.50の注釈動作](https://github.com/backnotprop/plannotator/blob/v0.28.50/docs/agent-guides/annotate.md)
- [元の試行・設計判断](https://github.com/omitsuhashi/skills/issues/85)
