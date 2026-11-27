# Agent Skills

AIエージェント向けの、設計・開発・運用で使うスキル集です。各スキルの入口は `skills/<skill-name>/SKILL.md` です。利用環境へ取り込むときは、相対リンクで参照する補助資料やスクリプトと一緒にスキルのディレクトリを取り込みます。

## 設計・構成

| やりたいこと | スキル |
| --- | --- |
| 利用者の目的から、振る舞い・業務ルール・外部接続を設計する | [usecase-design](skills/usecase-design/SKILL.md) |
| コードの配置と依存方向を決め、採用済みの構成を適用・維持する | [project-structure](skills/project-structure/SKILL.md) |
| 設計資料の正本・読み順と実装の対応を整え、レイヤーの README から辿れるようにする | [clean-architecture-docs](skills/clean-architecture-docs/SKILL.md) |
| 読み手に求める行動から、資料の目的・中心の問い・構成を決める | [design-document-purpose](skills/design-document-purpose/SKILL.md) |

## エージェント運用・知識

| やりたいこと | スキル |
| --- | --- |
| 解くべき問いを選ぶ、または実装 Issue の内容・粒度・依存を整える | [frame-issues](skills/frame-issues/SKILL.md) |
| エージェントへの依頼・引き継ぎで検証と操作範囲を揃え、観測した失敗から運用を改善する | [agent-workflow](skills/agent-workflow/SKILL.md) |
| Markdown Wiki を作る、出典を取り込む、知識を探す、整合性を点検する | [llm-wiki](skills/llm-wiki/SKILL.md) |

## GitHub

| やりたいこと | スキル |
| --- | --- |
| 指定マイルストーンの Issue を依存順に進め、レビュー・CI・マージから完了確認まで行う | [github-milestone-run](skills/github-milestone-run/SKILL.md) |
| ブランチ保護・マージ・リリースなどのリポジトリ変更管理を設定する | [github-repo-setup](skills/github-repo-setup/SKILL.md)（明示呼び出し） |

## 開発環境・ライブラリ

| やりたいこと | スキル |
| --- | --- |
| Python の開発環境を uv でセットアップする | [python-setup-with-uv](skills/python-setup-with-uv/SKILL.md)（明示呼び出し） |
| TypeScript の開発環境を pnpm でセットアップする | [typescript-setup-with-pnpm](skills/typescript-setup-with-pnpm/SKILL.md)（明示呼び出し） |
| Tailwind Plus Elements を HTML や React に組み込む、またはコンポーネントの仕様を調べる | [tailwindplus-elements](skills/tailwindplus-elements/SKILL.md) |

スキルの追加・変更は [スキルの作成規約](skills/AGENTS.md) を参照してください。このリポジトリでの作業手順は [AGENTS.md](AGENTS.md) にあります。
