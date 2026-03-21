---
name: skill-authoring-guide
description: "Agent Skillの設計・作成・改善・評価を支援するスキル。SKILL.mdの構成、YAMLフロントマター、段階的開示パターン、ワークフロー設計、評価・イテレーション・ベンチマークのベストプラクティスを網羅。「スキルを作りたい」「SKILL.mdの書き方」「スキル設計」「カスタムSkill作成」「スキルのベストプラクティス」「スキルの改善」「スキルをパッケージ化」「スキルのテスト」「スキル構造」「evalを回す」「スキルの評価」「description最適化」などのキーワードでトリガー。新規スキル作成、既存スキルの改善、スキル設計のレビュー、スキルのパッケージング、いずれの場面でも積極的に使用すること。"
---

# Skill Authoring Guide

Agent Skillの設計・作成・改善を体系的に支援するガイド。
Anthropic公式ドキュメントのベストプラクティスに基づく。

全体のフローは以下の通り：

- スキルの目的と大まかなアプローチを決める
- ドラフトを書く
- テストプロンプトを作成し、スキル付きClaudeで実行する
- ユーザーと一緒に結果を定性的・定量的に評価する
  - ラン実行中にアサーションを作成し、`eval-viewer/generate_review.py` でユーザーに結果を見せる
- フィードバックに基づいてスキルを改善する
- 満足するまで繰り返す
- テストセットを拡大して再試行

ユーザーがこのプロセスのどこにいるかを判断し、適切な地点から支援する。既にドラフトがあれば評価・改善から。「evalはいらない、一緒にバイブスで」と言われたらそれでもOK。

---

## ユーザーとのコミュニケーション

このスキルはコーディング経験の幅広い層に使われる可能性がある。技術的なリテラシーのコンテキスト手がかりに注意して、コミュニケーションを適応する。

デフォルトの目安：
- 「evaluation」「benchmark」はボーダーラインだが概ねOK
- 「JSON」「assertion」はユーザーが知っていることを確認してから使う

疑わしい場合は簡単に用語を定義してから使う。

---

## Phase 1: 意図の把握

以下を確認してユーザーの意図を明確化する：

1. **このスキルで何ができるようになるか？** — Claudeに追加される具体的な能力
2. **いつトリガーすべきか？** — ユーザーが使う言い回し、コンテキスト
3. **期待するアウトプット形式は？** — ファイル形式、構造、品質基準
4. **テストケースは必要か？** — 客観的に検証可能な出力があるスキルはテスト推奨。主観的な出力（文体、デザイン）は不要なことが多い

会話の中で既にワークフローが確立されている場合（例：「これをスキルにして」）、使ったツール、手順、修正点をまず会話履歴から抽出する。エッジケース、入出力フォーマット、成功基準について積極的に質問する。

利用可能なMCPがあれば研究に活用する。

---

## Phase 2: 構造設計

### 基本構造

```
skill-name/
├── SKILL.md              # メイン指示（トリガー時に読み込み）
├── references/           # 参照資料（必要時に読み込み）
├── scripts/              # 実行スクリプト（コンテキスト非消費）
├── templates/            # テンプレートファイル
└── assets/               # アセット（画像、フォント等）
```

### 3段階の読み込みモデル（段階的開示）

| レベル | タイミング | コスト | 内容 |
|--------|----------|-------|------|
| **L1: メタデータ** | 常に | ~100トークン | `name`と`description` |
| **L2: 本文** | トリガー時 | 5k未満推奨 | SKILL.md本文 |
| **L3: リソース** | 必要時 | 実質無制限 | references/, scripts/, assets/ |

**設計原則：**
- SKILL.md本文は **500行以内**。超えそうなら詳細をreferencesに分離
- スクリプトは**実行**されるためコンテキストを消費しない
- 参照ファイルへのリンクは **1階層のみ**
- 300行超の参照ファイルには目次を含める

構造設計の詳細パターンは [references/structure-patterns.md](references/structure-patterns.md) を参照。

---

## Phase 3: SKILL.md執筆

### YAMLフロントマター（必須）

```yaml
---
name: your-skill-name
description: "何をするか＋いつ使うべきかの両方を含める。"
---
```

**nameの制約:** 最大64文字、小文字・数字・ハイフンのみ、XMLタグ禁止、予約語（anthropic/claude）禁止

**descriptionの制約:** 最大1024文字、空不可、XMLタグ禁止、三人称で記述

**descriptionの書き方のコツ：**
- Claudeは100以上のスキルからdescriptionのみで選択 — 十分な具体性が必要
- やや積極的（pushy）にする — Claudeはスキルを使わない方向にバイアスがある
- トリガーキーワードとコンテキストを豊富に含める
- トリガー条件情報は全てここに入れる（本文ではない）

### 本文の執筆原則

詳細は [references/writing-principles.md](references/writing-principles.md) を参照。主要原則：

1. **簡潔さが鍵** — Claudeが既に知っていることは書かない
2. **WHYを説明する** — ALWAYS/NEVERの連発より理由の説明が効果的。Theory of mindを活用
3. **命令形を使う** — 「〜してください」ではなく「〜する」
4. **自由度を適切に設定** — タスクの脆弱性に応じてlow/medium/highを選ぶ
5. **一貫した用語** — 同じ概念に異なる単語を混在させない
6. **時間依存情報を避ける**

### テンプレート集

[templates/](templates/) ディレクトリを参照：
- `templates/instruction-only.md` — コードなしの指示スキル用
- `templates/with-scripts.md` — スクリプト付きスキル用
- `templates/multi-domain.md` — 複数ドメイン対応スキル用

---

## Phase 4: リソース作成

### 参照ファイル（references/）

- 100行以上のファイルには**目次**を冒頭に追加
- 用途を明記してリンク: `**フォーム詳細**: [references/forms.md](references/forms.md) を参照`

### スクリプト（scripts/）

スクリプトのメリット：生成コードより信頼性が高い、コンテキスト非消費、実行が速い、一貫性保証

設計原則：
- エラーを適切に処理する（Claudeに丸投げしない）
- マジックナンバーを避け、定数の理由をコメントで説明
- 実行方法を SKILL.md に明記する

---

## Phase 5: テスト・評価

### テストケースの作成

スキルドラフト作成後、2-3個のリアルなテストプロンプトを作成。ユーザーに確認してから実行。テストケースは `evals/evals.json` に保存（スキーマは [references/schemas.md](references/schemas.md) 参照）。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {"id": 1, "prompt": "タスクプロンプト", "expected_output": "期待結果", "files": []}
  ]
}
```

### テスト実行ワークフロー（一連の流れで止めない）

結果は `<skill-name>-workspace/` にスキルディレクトリの兄弟として配置。iteration-N/eval-N/ で整理。

**Step 1: 全ランを同時に起動（スキルあり＋ベースライン）**

各テストケースに対して、同じターンで2つのサブエージェントを起動:
- **スキルありラン**: スキルパス、タスク、入力ファイル、出力先を指定
- **ベースラインラン**: 新規スキルなら「スキルなし」、改善ならスナップショットした旧版

各テストケースに `eval_metadata.json` を作成（記述的な名前を付ける）。

**Step 2: ラン実行中にアサーションを作成**

待機中に定量的アサーションをドラフトし、ユーザーに説明する。良いアサーションは客観的に検証可能で記述的な名前を持つ。主観的スキルには無理にアサーションを当てはめない。

**Step 3: ラン完了時にタイミングデータをキャプチャ**

サブエージェント完了通知から `total_tokens` と `duration_ms` を即座に `timing.json` に保存。これが唯一のキャプチャ機会。

**Step 4: 採点・集計・ビューアー起動**

1. **採点**: `agents/grader.md` を読んで各アサーションを評価。`grading.json` に保存。`text`, `passed`, `evidence` フィールド必須
2. **集計**: `python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`
3. **分析**: `agents/analyzer.md` を参照してベンチマークデータのパターンを分析
4. **ビューアー起動**:
   ```bash
   nohup python eval-viewer/generate_review.py <workspace>/iteration-N \
     --skill-name "my-skill" --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   ```
   iteration 2以降: `--previous-workspace <workspace>/iteration-<N-1>` を追加

**Step 5: フィードバックを読む**

ユーザーが完了したら `feedback.json` を読む。空のフィードバック = 問題なし。具体的な不満があるテストケースに改善を集中する。

---

## スキルの改善

### 改善の考え方

1. **フィードバックから汎化する** — スキルは数百万回使われる可能性がある。少数の例への過剰適合やMUSTの連発ではなく、異なるメタファーやパターンを試す
2. **プロンプトをリーンに保つ** — 役に立っていない部分は削除する。トランスクリプトを読み、スキルが非生産的な作業をさせていないか確認
3. **WHYを説明する** — 大文字のALWAYS/NEVERや超厳格な構造はイエローフラグ。理由を説明してモデルの理解を促すほうが効果的
4. **テストケース間の繰り返し作業を見つける** — 全テストケースで独自に似たスクリプトを書いている場合、それをスキルにバンドルすべきサイン

### イテレーションループ

1. スキルを改善
2. 全テストケースを新しい `iteration-<N+1>/` に再実行（ベースライン含む）
3. `--previous-workspace` でビューアー起動
4. ユーザーのレビューを待つ
5. フィードバックを読み、再改善

終了条件: ユーザーが満足 / フィードバックが全て空 / 有意な進歩がない

---

## ブラインド比較（上級）

2つのスキルバージョンのより厳密な比較が必要な場合に使用。独立したエージェントにどちらがどのバージョンか知らせずに品質を判定させる。

詳細は `agents/comparator.md` と `agents/analyzer.md` を参照。

オプション機能であり、サブエージェントが必要。通常はヒューマンレビューループで十分。

---

## description自動最適化

スキル作成・改善後にdescriptionのトリガー精度を最適化する。

### Step 1: トリガー評価クエリを生成

20個の評価クエリ（should-trigger / should-not-trigger の混合）を作成。具体的でリアルなクエリにする（ファイルパス、個人コンテキスト、カジュアルな表現を含む）。

should-not-trigger のクエリは**ニアミス**が最も価値がある — キーワードは共有するが実際は別のことが必要なケース。

### Step 2: ユーザーにレビューしてもらう

`assets/eval_review.html` テンプレートを使用して評価セットをHTMLで表示。ユーザーが編集・エクスポートできるようにする。

### Step 3: 最適化ループを実行

```bash
python -m scripts.run_loop \
  --eval-set <path-to-eval-set.json> \
  --skill-path <path-to-skill> \
  --model <model-id> \
  --max-iterations 5 --verbose
```

60%/40%でtrain/test分割し、過学習を防ぐ。各descriptionを3回実行して信頼性のあるトリガー率を取得。

### Step 4: 結果を適用

`best_description` をスキルのフロントマターに更新。ユーザーに before/after とスコアを報告。

詳細は [references/description-guide.md](references/description-guide.md) を参照。

---

## Phase 6: パッケージング

### バリデーション

```bash
python scripts/quick_validate.py /path/to/skill-directory
```

### パッケージ化

```bash
python scripts/package_skill.py /path/to/skill-directory
```

出力: `skill-name.skill` ファイル（zipアーカイブ）

---

## Claude.ai固有の指示

Claude.aiではサブエージェントがないため一部の手順が変わる：

- **テスト実行**: 並列実行不可。スキルのSKILL.mdを読んで自分でタスクを実行する。ベースラインランは省略
- **結果レビュー**: ブラウザが使えない場合はビューアーを省略し、会話内で結果を直接提示
- **ベンチマーク**: 定量ベンチマークは省略。定性フィードバックに集中
- **description最適化**: `claude -p` が必要なため省略
- **既存スキルの更新**: インストール済みパスは読み取り専用の場合あり。`/tmp/skill-name/` にコピーして編集

---

## Cowork固有の指示

- サブエージェントが使えるので主要ワークフローは全て動作する
- ブラウザ/ディスプレイがないため `--static <output_path>` で静的HTMLを生成
- `eval-viewer/generate_review.py` でテスト後に**必ず**eval viewerを生成してからスキルを修正する
- フィードバックは「Submit All Reviews」ボタンで `feedback.json` としてダウンロードされる
- description最適化（`run_loop.py` / `run_eval.py`）はCoworkで問題なく動作するが、スキルが完成してユーザーが承認するまで待つ

---

## チェックリスト

### コア品質
- [ ] descriptionが具体的でトリガーキーワードを含む
- [ ] descriptionに「何をするか」と「いつ使うか」の両方がある
- [ ] SKILL.md本文が500行以内
- [ ] WHYの説明がMUST/NEVERの連発より優先されている
- [ ] 時間依存情報がない
- [ ] 用語が一貫している

### テスト
- [ ] 3つ以上の評価シナリオを作成
- [ ] eval viewerでユーザーにレビューしてもらった
- [ ] 使用予定の全モデルでテスト済み

---

## 参照ファイル一覧

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/writing-principles.md](references/writing-principles.md) | 執筆原則の詳細 | SKILL.md執筆時 |
| [references/structure-patterns.md](references/structure-patterns.md) | ディレクトリ構成パターン | 構造設計時 |
| [references/description-guide.md](references/description-guide.md) | description最適化ガイド | トリガー精度改善時 |
| [references/schemas.md](references/schemas.md) | JSONスキーマ定義 | eval/ベンチマーク実装時 |
| [agents/grader.md](agents/grader.md) | 採点エージェントの指示 | テスト採点時 |
| [agents/comparator.md](agents/comparator.md) | ブラインド比較エージェント | バージョン比較時 |
| [agents/analyzer.md](agents/analyzer.md) | ベンチマーク分析エージェント | 結果分析時 |
| [templates/instruction-only.md](templates/instruction-only.md) | コードなしスキルのテンプレート | 新規作成時 |
| [templates/with-scripts.md](templates/with-scripts.md) | スクリプト付きスキルのテンプレート | 新規作成時 |
| [templates/multi-domain.md](templates/multi-domain.md) | 複数ドメインスキルのテンプレート | 新規作成時 |
