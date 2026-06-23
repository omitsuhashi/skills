# Issue Implementation Loop Context Policy Spec

## 目的

`issue-implementation-loop` の長時間実行で、親 coordinator の context 消費、worker packet の肥大化、別セッション/worker dispatch の誤解を減らす。

この変更では、実装 scheduler や runtime state の挙動は変えない。入口 skill の読込量を抑え、Execution Envelope に context policy を追加し、worker へ渡す情報を paths-first / bounded packet として明示する。

## Epic ID

`issue-implementation-loop-context-policy`

## 受け入れた判断

- `issue-implementation-loop` の親 coordinator は同じ会話/実行文脈で残る。
- worker / reviewer dispatch は isolated implementation / review task に限定し、ユーザー-owned Codex thread を自動作成しない。
- parallel worker が使えない場合は、Execution Envelope の `serial_fallback_preapproved` に従って同一 coordinator が serial に続行できる。
- `SKILL.md` の description は trigger-only にし、workflow 要約を避ける。
- `SKILL.md` 本体は 520 words 以下に抑え、細部は mode-specific reference に寄せる。
- Execution Envelope は `context_policy` を必須 section とし、worker packet / report の word budget と paths-first 方針を持つ。
- worker packet は spec / issue ledger / ADR / glossary の全文を貼らず、durable path と必要最小の要約を渡す。
- review や completion で必要な証跡は report file / runtime state に残し、coordinator が会話 context だけに依存しない。

## 実装範囲

- `skills/issue-implementation-loop/SKILL.md`
  - trigger-only description へ短縮する。
  - top-level に session / worker semantics を明示する。
  - scripts / stop / completion の詳細列挙を圧縮し、mode references へ委譲する。
- `skills/issue-implementation-loop/references/execution-envelope.md`
  - `context_policy` を required section として説明する。
- `skills/issue-implementation-loop/references/worker-contract.md`
  - paths-first packet、word budget、report budget を追加する。
- `skills/issue-implementation-loop/assets/templates/execution-envelope.json`
  - `context_policy` の既定例を追加する。
- `skills/issue-implementation-loop/assets/schemas/execution-envelope.schema.json`
  - `context_policy` schema を追加する。
- `skills/issue-implementation-loop/scripts/_common.py`
  - `context_policy` validation を追加する。
- `skills/issue-implementation-loop/tests/test_issue_implementation_loop.py`
  - skill entrypoint word budget / trigger-only description / session semantics / context policy validation の回帰テストを追加する。

## 非目標

- scheduler、dependency calculation、runtime recovery の仕様変更はしない。
- GitHub issue、push、PR、merge は実行しない。
- worker を必ず parallel / subagent 実行する契約にはしない。
- standalone context manager skill は作らない。
- 既存 branch policy の実行履歴を書き換えない。

## Acceptance Criteria

- `SKILL.md` の description が trigger-only で、workflow 要約語を含まない。
- `SKILL.md` 本体が 520 words 以下である。
- `SKILL.md` が「親 coordinator は同じセッションに残る」「ユーザー-owned Codex thread を自動作成しない」「parallel worker 不在時は承認済み serial fallback で続行できる」を明記している。
- `execution-envelope` reference / schema / template が `context_policy` を持つ。
- `validate_execution_envelope.py` が `context_policy` 欠落と不正 budget を拒否する。
- `worker-contract` が durable paths-first packet と全文貼り付け禁止を説明している。
- 既存の branch/base/commit policy tests が引き続き通る。
- skill validation が `issue-implementation-loop` を通す。

## 検証コマンド

```bash
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 -m unittest discover -s skills/issue-implementation-loop/tests
UV_CACHE_DIR=/private/tmp/uv-cache uv run --isolated --python 3.12 --with 'PyYAML==6.0.2' python /Users/omitsuhashi/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/issue-implementation-loop
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/grill-to-pr-loop/scripts/check_prereqs.py --phase execution --json
PYTHONPYCACHEPREFIX=/tmp/skills-pycache python3 skills/issue-implementation-loop/scripts/validate_input_packet.py knowledge/wiki/syntheses/issue-implementation-loop-context-policy-input-packet.json
```

## Stop Conditions

- `SKILL.md` を 520 words 以下にすると必要な gate / safety rule が消える。
- `context_policy` 追加が既存 envelope validation と互換しない。
- worker packet の budget が実際の issue review / verification 証跡に不足する。
- tests が既存 branch/base/commit policy の契約を破る。
- external write が必要になる。

## 関連ページ

- [Grill To PR Loop Skill Split V2 Spec](grill-to-pr-loop-skill-split-v2-spec.md)
- [Grill To PR Loop Branch Policy Spec](grill-to-pr-loop-branch-policy-spec.md)

## 出典

- `../../../skills/issue-implementation-loop/SKILL.md`
- `../../../skills/issue-implementation-loop/references/execution-envelope.md`
- `../../../skills/issue-implementation-loop/references/worker-contract.md`
