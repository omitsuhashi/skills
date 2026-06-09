# Single Root Topology

1 つの knowledge root だけを扱う時の topology です。single-root の query や ingest では multi-root reference を読まない。

## Rule

root registry を作らない。knowledge-root `AGENTS.md` を authority source として扱い、owner / write boundary / draft target / local overrides をそこに置く。

## Entrypoints

- dedicated wiki repo: repo root が knowledge root でよい。
- mixed repo: repo root `AGENTS.md` は thin router として、knowledge-root `AGENTS.md` への導線だけを置く。
- knowledge-root `AGENTS.md` は `llm-wiki` skill への導線と local contract だけを書く。

汎用 wiki 運用ルールは skill 側を canonical とし、local `AGENTS.md` に複写しない。

## Local Contract Fields

knowledge-root `AGENTS.md` に最低限次を置く。

- knowledge root path
- Canonical Owner
- Write Boundary: `owned`, `propose`, or `closed`
- Non-owner proposal target / Draft Target
- durable doc routing override
- local naming, page type, frontmatter, link convention の override

## Write Boundary

- `Write: owned`: owner actor だけが verified claim を直接更新できる。non-owner actor は `Read: allowed` かつ Draft Target がある場合だけ proposed note を書く。
- `Write: propose`: routine actor は verified claim を直接更新できない。Draft Target がある場合だけ proposed note を書く。owner `draft-review` / `canonicalize` でも canonical page へ直接反映しない。
- `Write: closed`: verified claim も proposed note も書かない。

direct canonical update は、actor が canonical owner であり、`Write: owned` であり、local contract が許す場合だけ行う。それ以外の durable proposal は draft note に route する。

## Draft Target

Draft Target は knowledge root 内の root-relative directory として解決する。通常は `wiki/drafts/` を使う。absolute path、`~`、`..`、root 外へ解決される path は使わない。

Draft Target が未設定、未解決、または root 外へ解決される場合は proposed note を書かず、session user に確認する。

## Bootstrap Notes

single-root bootstrap では:

1. knowledge root を確定する。
2. root registry を作らないことを local contract に明記する。
3. owner, write boundary, non-owner proposal target を knowledge-root `AGENTS.md` に書く。
4. mixed repo なら repo root `AGENTS.md` を thin router にする。
5. `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を knowledge root の内側に揃える。

## Common Mistakes

- single-root 作業なのに root registry を作ること。
- owner / write boundary / draft target を local contract に置かないこと。
- repo root `AGENTS.md` に汎用 wiki 運用ルールを長く複写すること。
- non-owner actor が canonical page を直接更新すること。
