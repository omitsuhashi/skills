# Git hook の診断と自動再ステージ

標準 hook の不具合調査、またはユーザーが自動修正を同じ commit へ含める運用を依頼した場合だけ読む。通常の初期セットアップでは [SKILL.md](../SKILL.md) の標準設定を使う。既存の hook や `core.hooksPath` がある場合はその所有者と用途を確認し、上書きせず統合する。

自動修正を同じ commit へ含める運用を選ぶ場合、[標準の自動修正設定](../SKILL.md)は commit hook として使いません。`pre-commit run --all-files` や CI で状態確認しやすいよう、check-only にします。

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: vX.Y.Z
    hooks:
      - id: ruff-check
        types_or: [python, pyi]
      - id: ruff-format
        args: [--check]
        types_or: [python, pyi]
```

### コミット時の期待挙動

標準の `pre-commit` では、hook がファイルを自動修正した場合、そのコミットは失敗します。これは異常ではなく、修正後の差分を人間が確認して `git add` し直すための安全な挙動です。

期待される流れは次です。

```bash
git add .
git commit -m "change"
# ruff-check --fix または ruff-format がファイルを更新したら commit は止まる
git diff
git add .
git commit -m "change"
```

`ruff` や `ruff-format` が走ってファイルが変更されたにもかかわらず commit が成立する場合は、設定ではなく hook 実行経路を疑います。

確認点は次です。

- `.git/hooks/pre-commit` が存在するか
- `git config --get core.hooksPath` で別の hook ディレクトリへ向いていないか
- GUI / IDE の commit が Git hook を無視する設定になっていないか
- `git commit --no-verify` 相当で実行されていないか
- 独自の hook wrapper が `pre-commit` の終了コードを握りつぶしていないか

最低限の診断コマンドは次です。

```bash
test -f .git/hooks/pre-commit && sed -n '1,80p' .git/hooks/pre-commit
git config --get core.hooksPath
uv run pre-commit run --all-files --show-diff-on-failure
```

### 自動修正を同じコミットへ含めたい場合

「自動修正できるものは修正して、その修正後の内容を同じコミットに含める」挙動は、標準の `pre-commit` 設定だけでは実現しません。実現するなら project-local な Git hook を明示的に管理します。

ただしこの方式は、部分 staging との相性が悪いです。未 stage の変更まで formatter が触れて同じ commit に混ざるリスクがあるため、同じファイルに staged / unstaged の両方の変更がある場合は commit を止めます。

このモードを選ぶ場合の基本方針は次です。

- `.pre-commit-config.yaml` は check-only にする
- commit 時の自動修正と `git add` は `.githooks/pre-commit` が担当する
- `.githooks/pre-commit` は repo に commit する
- `git config core.hooksPath .githooks` は clone ごとの初期設定として実行する
- 同じファイルに staged / unstaged の両方がある場合は commit を止める

`.githooks/pre-commit` 例:

```bash
#!/usr/bin/env bash
set -euo pipefail

files=()
while IFS= read -r -d '' file; do
  files+=("$file")
done < <(git diff --cached --name-only --diff-filter=ACMR -z -- '*.py' '*.pyi')

if [ "${#files[@]}" -eq 0 ]; then
  exit 0
fi

for file in "${files[@]}"; do
  if ! git diff --quiet -- "$file"; then
    echo "error: $file has both staged and unstaged changes."
    echo "Stage or stash the unstaged changes before committing."
    exit 1
  fi
done

uv run ruff check --fix --exit-zero --force-exclude -- "${files[@]}"
uv run ruff format --force-exclude -- "${files[@]}"
git add -- "${files[@]}"

uv run ruff check --force-exclude -- "${files[@]}"
uv run ruff format --check --force-exclude -- "${files[@]}"
```

有効化:

```bash
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

チームで同じ挙動を共有したい場合は、`.githooks/pre-commit` をリポジトリ管理し、初期セットアップ手順に `git config core.hooksPath .githooks` を含めます。

この方式を採用した repo では、次の確認を必ず行います。

```bash
git config --get core.hooksPath
test -x .githooks/pre-commit
.githooks/pre-commit
uv run pre-commit run --all-files --show-diff-on-failure
```

`core.hooksPath` を設定すると、標準の `.git/hooks/pre-commit` は使われません。`.git/hooks/pre-commit` と `.githooks/pre-commit` の両方を見て判断すると誤診しやすいため、必ず `git config --get core.hooksPath` を先に見ます。

`pytest` や `mypy` は、次のどちらかで回すのが無難です。

- 手元で `uv run pytest`, `uv run mypy .`
- CI で常時実行
