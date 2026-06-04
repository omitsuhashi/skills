# Federated Knowledge Roots

## Purpose

複数の knowledge root を持つ system で、どの知識をどこへ保存するかを決める。

## Core Rule

各 knowledge root は、独立した llm-wiki root として扱う。

- 各 root は `raw/`, `wiki/`, `index.md`, `log.md`, `AGENTS.md` を持つ。
- `raw/` は root ごとに不変 source として扱う。
- `wiki/` は root ごとの maintained knowledge として扱う。
- `index.md` は root 内の lookup surface として扱う。
- `log.md` は root 内の append-only ledger として扱う。

## Root Types

### Global Root

system 全体で共有する運用知識、agent 設計、共通失敗例、共通 policy を置く。

### Profile Root

特定 profile が繰り返し使う経験知、失敗例、調査 pattern、review pattern を置く。

### Role Root

CMO / CTO / COO など role 固有の判断軸、playbook、strategy pattern を置く。

### Project Root

特定 project の顧客、商品、業務、stakeholder、source、claim、decision を置く。

### Project-Role Root

特定 project x role の施策、最終判断、成果物、実験ログを置く。

## Routing Rules

- project 固有 claim を global root や profile root に置かない。
- role 固有 strategy を project domain root に混ぜない。
- profile の作業改善知は profile root に置く。
- source note は、その source が支える claim の所属 root に置く。
- 複数 root にまたがる場合は、canonical root を 1 つ決め、他 root から link する。

## Canonical Owner

各 root は canonical owner を持つ。owner 以外の profile は draft / proposed note を作ってよいが、verified claim への昇格は owner が行う。

## Cross-Root Links

root 間 link は許可するが、copy-paste による重複 canonical page は避ける。

## Common Mistakes

- project 固有の事実を common wiki に書くこと。
- role 固有の判断を project domain wiki に書くこと。
- profile root に一回限りの project 調査結果を溜めること。
- root ごとの `index.md` / `log.md` を更新しないこと。
