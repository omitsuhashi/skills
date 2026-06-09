# Bootstrap Mode

新規 local Markdown wiki を作るとき、または既存の Markdown repo / vault を LLM Wiki pattern へ寄せるときに使います。

Read first: `references/core.md`, chosen topology reference, then this file.

## Goal

raw source を不変に保ちつつ、knowledge root, wiki の page 種別, `AGENTS.md` の local contract が明確で、汎用運用は `llm-wiki` skill に集約された構成を作る。加えて、他 workflow が作る durable な spec / ADR / plan / roadmap の保存先も knowledge root に寄せる。

## Check First

- 既存の local Markdown wiki または Markdown repo はあるか。
- dedicated wiki repo か、mixed repo 内の subdirectory wiki か。
- wiki topology は `single-root` か `multi-root` か。
- knowledge root はどこに置くべきか。
- `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` は既にあるか。
- owner, write boundary, draft target をどこで解決するか。
- 既存の naming convention を維持すべきか。
- 他 workflow が durable doc をどこへ書くべきか。

## Default Procedure

1. dedicated wiki repo か mixed repo かを決める。
2. `single-root` / `multi-root` topology を判定し、target knowledge root を確定する。
3. `single-root` なら root registry は作らず、repo root または knowledge root の `AGENTS.md` を entrypoint にし、canonical owner, write boundary, non-owner proposal target を local contract に書く。
4. `multi-root` なら system-specific root registry adapter を用意し、各 router `AGENTS.md` から adapter と canonical root へ辿れるようにする。Markdown registry を採用する場合だけ `assets/templates/root-registry.md` を元にしてよい。
5. mixed repo なら `assets/templates/root-AGENTS.md` を元に repo root に thin router `AGENTS.md` を置き、knowledge root への導線と durable doc routing だけを書く。
6. 無ければ knowledge root に `assets/templates/AGENTS.md`, `index.md`, `log.md` をコピーする。
7. `references/core.md` の default layout に従って必要な subdirectory を knowledge root 配下に作る。
8. roadmap, ADR, spec, design doc, implementation plan の default 保存先を `wiki/syntheses/` にするか、project 固有の subdirectory を使うか決めて `AGENTS.md` に明記する。
9. YAML frontmatter を使うか決める。
10. 初期構成を knowledge root の `index.md` に記録する。`multi-root` の場合は registry の所在地と root id も記録する。
11. knowledge root の `log.md` に `bootstrap` entry を追加する。

## Pause And Align When

- directory layout や naming に複数の妥当案があり、後で rename / relink が多発しそう。
- `single-root` / `multi-root` のどちらにするかで owner / access / durable doc routing が変わる。
- repo root を knowledge root のまま使うべきか、subdirectory に切り出すべきかで運用コストが変わる。
- 既存 wiki と新規ルールのどちらを canonical にするかで運用コストが変わる。
- 1 回の bootstrap で広範囲の page 再配置を伴う。
- 既存 workflow が repo-root `docs/` など別の durable doc 置き場に強く依存しており、routing 変更の影響が読めない。

## Output Expectations

- knowledge root に local contract と entrypoint がある。
- repo root から wiki に辿りやすい entrypoint がある。
- `single-root` の場合は root registry なしで entrypoint と write authority が分かる。
- `multi-root` の場合は adapter があり、root id / URI / owner / read-write policy / draft target が解決できる。
- 後続 session が ingest / query / lint のやり方を再発明せずに済む。
