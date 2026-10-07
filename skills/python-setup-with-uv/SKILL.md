---
name: python-setup-with-uv
description: Set up Python projects with uv and minimal development tooling only when the user explicitly invokes python-setup-with-uv.
---

# Python Setup With uv

## 適用条件

利用環境が認識する明示的な skill 呼び出し（例: `$python-setup-with-uv` や skill 選択機能）で使用を指示された場合だけ、本文・参照資料の読み込みと手順の実行を行う。Python や uv に関する話題、一般的なプロジェクト作成・セットアップの依頼からは採用を推定しない。

## 入力・出力・必要な能力

- 入力: 対象ディレクトリ、Python プロジェクトの用途、既存設定、依頼されたセットアップ範囲。
- 出力: 依頼範囲のプロジェクト設定・依存関係・lock file と、実施した検証・未完了事項。
- 必要な能力: ファイル読取・編集、コマンド実行、利用可能な `uv`。依存取得にはネットワーク、Git hook 導入には Git が必要。利用できない能力があれば該当操作を未実施と示し、設定案や実行可能な手順を渡す。

## 適用と既定値

新規の継続開発プロジェクトでは `uv + ruff + pytest + pre-commit` を既定とする。既存プロジェクトでは `pyproject.toml`、lock file、テスト・hook 設定を確認し、同じ役割の仕組みを尊重する。相談のみなら推奨を示し、セットアップを依頼されていれば実行する。

- `ruff`: lint と format。
- `pytest`: テストの入口。使い捨てスクリプトでは省略できる。
- `pre-commit`: Git を使う継続開発でコミット前に Ruff を実行。Git を使わない実験では省略する。
- `mypy`: 型注釈を保守対象にするときだけ追加。
- `poethepoet`: `uv run ...` のコマンド整理が必要になったときだけ追加。

### セットアップ手順

1. 未初期化のプロジェクトを初期化する

```bash
uv init
```

Python バージョンはこの skill では固定しません。プロジェクト要件があるときだけ `uv python pin <version>` を使います。

2. 用途に合う開発依存を入れる。次は新規の継続開発プロジェクトの例であり、省略条件や既存設定に合わせて選ぶ

```bash
uv add --dev ruff pytest pre-commit
```

3. 上記の条件を満たすツールだけ追加する

```bash
uv add --dev mypy
uv add --dev poethepoet
```

4. 環境を同期する。Git hook を導入する場合は、下記の `.pre-commit-config.yaml` を用意し、既存 hook と `git config --get core.hooksPath` を確認してからインストールする

```bash
uv sync
uv run pre-commit install --install-hooks
```

`pre-commit install` はリポジトリごとに必要です。`pyproject.toml` に `pre-commit` を入れただけでは Git commit 時には実行されません。

既存の hook 経路と衝突する場合は上書きせず、影響しないセットアップを続ける。自動修正を同じ commit に含める運用を依頼された場合、または hook が期待どおり動かない場合だけ [Git hook の診断と自動再ステージ](references/git-hooks.md) を読む。通常のセットアップでその方式を選ばせる確認は不要。

5. 導入した設定を検証する

Ruff を pre-commit に設定した場合は `uv run pre-commit run --all-files --show-diff-on-failure` で確認する。hook を使わない場合は `uv run ruff check .` と `uv run ruff format --check .` を使う。同じ検証を両方の経路で繰り返す必要はない。

テストがあれば `uv run pytest`、型チェックを導入した場合は対象に対して `uv run mypy` を実行する。テスト未作成は未検証として伝え、空のテスト実行を成功扱いしない。必要な検証が通れば完了とし、新たな失敗や変更がない限り検証範囲を広げない。

## 具体例

### 最小 `pyproject.toml` のイメージ

`uv add --dev ...` を使えば自動で更新されますが、完成形のイメージは次です。

```toml
[project]
name = "example"
version = "0.1.0"

[dependency-groups]
dev = [
  "ruff",
  "pytest",
  "pre-commit",
  # "mypy",
  # "poethepoet",
]

[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

`requires-python` も必須ではありません。公開パッケージにする、対応バージョンを明示したい、といった要件があるときだけ追加します。

### 最小 `.pre-commit-config.yaml`

コミットを遅くしすぎないため、最初は `ruff` だけを hook に載せます。

標準の `pre-commit` 挙動でよい場合、つまり自動修正が入ったら commit を止めて人間が確認し、再度 `git add` する運用なら次を使います。

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: vX.Y.Z
    hooks:
      - id: ruff-check
        args: [--fix]
        types_or: [python, pyi]
      - id: ruff-format
        types_or: [python, pyi]
```

`rev` は固定値ではなく、その時点の最新安定版へ更新してください。導入後も `pre-commit autoupdate` で追従します。

## References

- `uv init`, `.python-version`, `uv.lock`: https://docs.astral.sh/uv/guides/projects/
- `uv add --dev`, dependency groups: https://docs.astral.sh/uv/concepts/projects/dependencies/
- `uv python pin`: https://docs.astral.sh/uv/concepts/python-versions/
- Ruff overview: https://docs.astral.sh/ruff/
- Ruff formatter: https://docs.astral.sh/ruff/formatter/
- pytest get started: https://docs.pytest.org/en/stable/getting-started.html
- pre-commit usage: https://pre-commit.com/
- mypy getting started: https://mypy.readthedocs.io/en/stable/getting_started.html
- Poe the Poet: https://poethepoet.natn.io/
