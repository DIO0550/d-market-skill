---
name: steering-audit
description: "Claude Codeプロジェクトのステアリング設定（CLAUDE.md/rules・skills・subagents・hooks・slash commands・output styles・MCP・settings.json）を監査・評価するスキル。Anthropicの『Steering Claude Code』の枠組みに基づき、各成果物が(1)正しいprimitiveで実装されているか（advisory→CLAUDE.md / mandatory→hook / procedural→skill / context isolation→subagent の使い分け）、(2)設計ベストプラクティスに沿っているかを、サブエージェントに並列評価させて重大度付きの監査レポートと改善提案を生成する。「skillやhookの評価」「Claude Code設定をレビュー」「ステアリング監査」「primitiveの使い分けが正しいか」「CLAUDE.mdが肥大化していないか」「hookにすべきものがCLAUDE.mdにある」「.claudeディレクトリの健全性チェック」「プラグインの設計レビュー」などでトリガー。リポジトリ全体やプラグインの設定品質を横断評価したいときに使用すること。単一スキルの振る舞いをeval/ベンチマークで測るのは skill-evaluator が担当する（本スキルは静的な設計・適合監査）。"
---

# Steering Audit

Claude Codeプロジェクトの**ステアリング設定全体**を静的に監査し、各成果物が正しいprimitiveで・ベストプラクティスに沿って実装されているかを評価するスキル。Anthropic公式『Steering Claude Code: skills, hooks, rules, subagents and more』の枠組みに基づく。

**評価作業はサブエージェントに委譲する。** メインスレッドはオーケストレーションに徹し、発見・評価・統合の各フェーズを専門サブエージェントに並列実行させる。これによりメインのコンテキストを汚さず、各primitiveを独立した観点で評価できる。

## skill-evaluator との違い

- **skill-evaluator**: 単一スキルを実際に動かし、eval/ベンチマークで**振る舞いの品質**を測る（動的・定量）。
- **steering-audit（本スキル）**: 動かさずにファイルを読み、**設計の適合性**を横断監査する（静的・定性）。「正しいprimitiveを選んでいるか」「肥大化・重複・MUST連発はないか」を見る。

「作ったスキルの精度を上げたい／ベンチマークを回したい」なら skill-evaluator。「設定全体が整っているか診断したい」なら本スキル。

---

## ユーザーとのコミュニケーション

最初に2点を確認する：

1. **監査対象** — リポジトリルートか、特定プラグイン／`.claude` ディレクトリか。複数プラグインがある場合は対象を絞るか全体かを確認。
2. **目的** — 一度きりの診断か、リリース前のチェックか、特定primitive（例：hookだけ）に絞るか。

不明な場合はリポジトリルートを対象に全primitiveを監査する。

---

## フェーズ概要

| フェーズ | 担当 | 出力 |
|---------|------|------|
| 1. インベントリ作成 | `inventory-scout` サブエージェント | `inventory.json` |
| 2. primitive別評価 | `primitive-evaluator` サブエージェント（並列） | `findings/<primitive>.json` |
| 3. 適合チェック（横断） | `fit-checker` サブエージェント | `fit.json` |
| 4. レポート統合 | `report-synthesizer` サブエージェント | `audit-report.md` + `audit.json` |

作業ディレクトリは対象の兄弟に `steering-audit-workspace/` を作成して整理する。

---

## Phase 1: インベントリ作成

[agents/inventory-scout.md](agents/inventory-scout.md) を読み、その指示で**1つのサブエージェント**を起動する。対象ディレクトリを渡し、全ステアリング成果物を発見・分類させる。

スカウトは以下を探す（詳細は [references/steering-primitives.md](references/steering-primitives.md)）：

- `CLAUDE.md` / `CLAUDE.local.md`（ルート・サブディレクトリ・`.claude/`）
- `.claude/rules/`・path-scoped ルール
- skills（`**/SKILL.md`、`skills/` 配下）
- subagents（`**/agents/*.md`、`.claude/agents/`）
- hooks（`hooks.json`・`settings.json` の `hooks` ブロック・スクリプト）
- slash commands（`.claude/commands/*.md`）
- output styles（`.claude/output-styles/`）
- MCP 設定（`.mcp.json`・settings の `mcpServers`）
- `settings.json` / `settings.local.json`・`plugin.json`・`marketplace.json`

結果を `inventory.json` に保存（スキーマは [references/schemas.md](references/schemas.md)）。各エントリに `type`・`path`・`summary` を記録。

> 成果物が1件も見つからない場合はユーザーに報告し、対象パスが正しいか確認する。

---

## Phase 2: primitive別評価（並列）

インベントリに存在する**primitiveタイプごと**に [agents/primitive-evaluator.md](agents/primitive-evaluator.md) でサブエージェントを起動する。**同じターンで全タイプを並列起動**してコンテキストを汚さず高速に評価する。

各サブエージェントへのプロンプトに必ず含める：

- 評価対象の primitive type（`skill` / `hook` / `claude_md` / `subagent` / `slash_command` / `output_style` / `mcp`）
- 評価対象成果物のパス一覧（inventory から）
- ルーブリックの参照先 [references/rubric.md](references/rubric.md)（該当セクションを読む）
- 出力先 `findings/<primitive>.json`

各評価で見るのは2軸（[references/rubric.md](references/rubric.md) 参照）：

1. **design 品質** — そのprimitive固有のベストプラクティス（例：skillならprogressive disclosure・description精度・WHY説明・自己完結性）。
2. **primitive 適合の予備所見** — 「これは別のprimitiveであるべきでは？」という気づきをメモ（最終判断は Phase 3）。

各findingに `severity`（`critical`/`high`/`medium`/`low`）・`evidence`（具体的な引用）・`recommendation` を付ける。エビデンスのない指摘は出さない。

---

## Phase 3: 適合チェック（横断）

ブログの核心は「**正しい乗り物を選んでいるか**」。Phase 2 の所見と inventory 全体を渡し、[agents/fit-checker.md](agents/fit-checker.md) で**1つのサブエージェント**を起動して横断的なミスマッチを判定させる。

主な検出パターン（[references/steering-primitives.md](references/steering-primitives.md) の決定表に基づく）：

- **必ず実行すべき処理がCLAUDE.md/skillにある** → hook にすべき（モデルが飛ばしうる）
- **advisoryな方針がhookに埋め込まれている** → CLAUDE.md/rules にすべき
- **長い手順書がCLAUDE.mdにある** → skill に切り出すべき（常時コンテキストを圧迫）
- **常時onの方針がskillになっている** → CLAUDE.md/rules にすべき（発火を待つ必要がない）
- **探索・検索の重い処理が本体skillに同梱** → subagent に隔離すべき
- **同じ指示がCLAUDE.md・skill・rulesに重複** → 単一の出典に統合
- **slash commandが既存skillと不整合・重複**

結果を `fit.json` に保存（各ミスマッチに `current`・`recommended`・`why`・`severity`）。

---

## Phase 4: レポート統合

`inventory.json`・`findings/*.json`・`fit.json` を渡し、[agents/report-synthesizer.md](agents/report-synthesizer.md) で**1つのサブエージェント**を起動して統合レポートを生成させる。

出力：

- **`audit-report.md`** — 人間可読。サマリ（primitive別スコア・健全性）、重大度順の所見、適合ミスマッチ、優先度付き改善ロードマップ。
- **`audit.json`** — 機械可読（スキーマは [references/schemas.md](references/schemas.md)）。

統合後、ユーザーに要点を提示する：

- 全体健全性スコアと primitive 別の内訳
- `critical`/`high` の所見（最優先で直すべきもの）
- 適合ミスマッチのトップ3（「これはhookにすべき」等）
- 次の一手の提案

> ユーザーが「直して」と言った場合のみ修正に進む。監査は読み取り専用が基本。修正する場合は本リポジトリの [CLAUDE.md バージョン管理ルール] に従い plugin.json と marketplace.json を更新する。

---

## 環境固有の指示

### サブエージェントが使えない環境（Claude.ai 等）
- 並列起動の代わりに、メインスレッドが各フェーズを順に自分で実行する。
- ルーブリックとprimitivesガイドを自分で読み、同じ評価基準を適用する。
- レポートはファイル出力できない場合、会話内に直接提示する。

### Cowork / Claude Code
- サブエージェントが使えるため Phase 2 を並列実行できる。
- ブラウザ/ディスプレイがない場合はレポートをファイルに出力してユーザーに共有する。

---

## 参照ファイル一覧

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/steering-primitives.md](references/steering-primitives.md) | 7つのprimitiveの定義・決定表・使い分け基準 | インベントリ分類・適合判定時 |
| [references/rubric.md](references/rubric.md) | primitive別の評価チェックリスト | primitive評価時 |
| [references/schemas.md](references/schemas.md) | inventory/findings/fit/audit のJSONスキーマ | 各JSON出力時 |
| [agents/inventory-scout.md](agents/inventory-scout.md) | 発見・分類サブエージェント | Phase 1 |
| [agents/primitive-evaluator.md](agents/primitive-evaluator.md) | primitive別評価サブエージェント | Phase 2 |
| [agents/fit-checker.md](agents/fit-checker.md) | 適合（正しいprimitive）判定サブエージェント | Phase 3 |
| [agents/report-synthesizer.md](agents/report-synthesizer.md) | レポート統合サブエージェント | Phase 4 |

スキルの新規作成・構造設計は `skill-authoring-guide`、単一スキルの振る舞い評価は `skill-evaluator` を参照。
