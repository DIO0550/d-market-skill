# ディレクトリ構成の詳細パターン

スキルの構造設計パターン集。用途に応じて最適なパターンを選択する。

## Contents

- パターン1: ハイレベルガイド＋参照ファイル
- パターン2: ドメイン別構成
- パターン3: 条件付き詳細
- パターン4: ワークフロー中心
- パターン5: オーケストレーターパターン（大規模スキル）
- スクリプト関連の構成ガイド
- 参照ファイルの構成ルール
- agents/ディレクトリの活用

---

## パターン1: ハイレベルガイド＋参照ファイル

最も一般的なパターン。SKILL.mdをナビゲーションハブとし、詳細を別ファイルに配置。

```
pdf-processing/
├── SKILL.md              # クイックスタート + 参照リンク
├── FORMS.md              # フォーム入力ガイド
├── REFERENCE.md          # APIリファレンス
└── EXAMPLES.md           # 使用例集
```

````markdown
# SKILL.md の書き方

# PDF Processing

## クイックスタート

pdfplumberでテキストを抽出する：
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## 高度な機能

**フォーム入力**: [FORMS.md](FORMS.md) を参照
**APIリファレンス**: [REFERENCE.md](REFERENCE.md) を参照
**使用例**: [EXAMPLES.md](EXAMPLES.md) を参照
````

Claudeはタスクに応じて必要なファイルだけを読み込む。

---

## パターン2: ドメイン別構成

複数のドメイン/フレームワークをサポートするスキル向け。無関係なコンテキストの読み込みを回避。

```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md        # 収益、請求指標
    ├── sales.md          # 商談、パイプライン
    ├── product.md        # API利用、機能
    └── marketing.md      # キャンペーン、アトリビューション
```

````markdown
# SKILL.md の書き方

# BigQuery Data Analysis

## 利用可能なデータセット

**Finance**: 収益、ARR、請求 → [reference/finance.md](reference/finance.md) を参照
**Sales**: 商談、パイプライン → [reference/sales.md](reference/sales.md) を参照
**Product**: API利用、機能 → [reference/product.md](reference/product.md) を参照

## クイック検索

特定のメトリクスをgrepで検索：
```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
```
````

ユーザーが売上について質問した場合、Claudeはsales.mdだけを読み込む。

---

## パターン3: 条件付き詳細

基本コンテンツを表示し、高度なコンテンツにリンク：

```
docx-processing/
├── SKILL.md              # 基本操作
├── REDLINING.md          # トラッキング変更の詳細
└── OOXML.md              # OOXML仕様の詳細
```

```markdown
# SKILL.md の書き方

# DOCX Processing

## ドキュメント作成
docx-jsで新規ドキュメントを作成する。[DOCX-JS.md](DOCX-JS.md) を参照。

## ドキュメント編集
単純な編集はXMLを直接修正する。

**トラッキング変更**: [REDLINING.md](REDLINING.md) を参照
**OOXML詳細**: [OOXML.md](OOXML.md) を参照
```

トラッキング変更が不要なタスクでは REDLINING.md は読み込まれない。

---

## パターン4: ワークフロー中心

スクリプト実行を中心としたスキル向け。ステップバイステップのワークフローを主軸に。

```
form-filler/
├── SKILL.md              # ワークフロー定義
└── scripts/
    ├── analyze_form.py   # フォーム解析
    ├── validate_fields.py # フィールド検証
    ├── fill_form.py      # フォーム入力
    └── verify_output.py  # 出力検証
```

````markdown
# SKILL.md の書き方

# PDF Form Filler

## ワークフロー

```
進捗:
- [ ] Step 1: フォーム解析 (analyze_form.py)
- [ ] Step 2: フィールドマッピング (fields.json編集)
- [ ] Step 3: マッピング検証 (validate_fields.py)
- [ ] Step 4: フォーム入力 (fill_form.py)
- [ ] Step 5: 出力検証 (verify_output.py)
```

**Step 1: フォーム解析**
実行: `python scripts/analyze_form.py input.pdf`
出力: `fields.json` にフォームフィールドと位置が保存される

**Step 2: フィールドマッピング**
`fields.json` を編集し各フィールドに値を設定する

**Step 3: マッピング検証**
実行: `python scripts/validate_fields.py fields.json`
バリデーションエラーがあれば修正してから続行

**Step 4: フォーム入力**
実行: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: 出力検証**
実行: `python scripts/verify_output.py output.pdf`
検証失敗の場合、Step 2に戻る
````

---

## パターン5: オーケストレーターパターン（大規模スキル）

SKILL.md本文が100〜200行の目安を超えそうな場合に使用。SKILL.mdをワークフローのルーティングハブに特化させ、各フェーズの詳細を参照ファイルに分離する。

### 判断基準

各セクションについて問う：
- **「次に何をするか決めるために必要か？」** → SKILL.mdに残す
- **「作業を実行するために必要か？」** → references/に移す

### 分解前（モノリシック、280行）

````markdown
# Complex Skill

## Phase 1: 分析
入力ファイルを読み込み、以下の手順で分析する：
1. ヘッダーを解析...（20行の詳細手順）
2. データを検証...（15行のバリデーションルール）
3. レポートを生成...（25行のフォーマット仕様）

## Phase 2: 変換
分析結果に基づいて変換する：
1. マッピング定義...（30行の詳細）
...
````

### 分解後（オーケストレーター、120行 + 参照ファイル）

```
complex-skill/
├── SKILL.md                        # ルーティング（~120行）
└── references/
    ├── phase1-analysis.md          # 分析の詳細手順
    ├── phase2-transform.md         # 変換の詳細手順
    └── validation-rules.md         # バリデーションルール
```

````markdown
# SKILL.md（オーケストレーター）

## 全体フロー

1. Phase 1: 分析 → Phase 2: 変換 → Phase 3: 出力
2. Phase 1でエラーならユーザーに報告して終了

## Phase 1: 分析

入力ファイルを読み込み、構造を分析する。

**詳細手順**: [references/phase1-analysis.md](references/phase1-analysis.md) を参照

成果物: `analysis.json`

## Phase 2: 変換

`analysis.json` に基づいて変換を実行する。

**詳細手順**: [references/phase2-transform.md](references/phase2-transform.md) を参照
**バリデーション**: [references/validation-rules.md](references/validation-rules.md) を参照

成果物: 変換済みファイル
````

### SKILL.mdに残すべきもの

- ワークフロー全体のステップ順序と分岐ロジック
- 各フェーズの1-2行の要約（何をするか）
- どのフェーズでどの参照ファイルを読むかのルーティング
- フェーズ間の成果物（何が次のフェーズへの入力になるか）
- 全フェーズ共通の制約やガードレール

### references/に移すべきもの

- フェーズごとの詳細な手順（ステップバイステップ）
- フォーマット仕様、スキーマ定義、具体例
- 特定の分岐でのみ必要なドメイン知識
- 長いコード例やテンプレート

---

## スクリプト関連の構成ガイド

### 実行 vs 参照の明確化

SKILL.md内でスクリプトの使い方を明確にする：

```markdown
# 実行する場合（最も一般的）
「`analyze_form.py` を実行してフィールドを抽出する」

# 参照として読む場合（複雑なロジックの理解用）
「アルゴリズムの詳細は `analyze_form.py` を参照」
```

ほとんどの場合、**実行が推奨** — より信頼性が高く効率的。

### 中間出力を検証可能にする

複雑な操作では「計画→検証→実行」パターンを使用：

```
1. 解析 → plan.json を生成
2. plan.json を検証スクリプトで検証
3. 検証通過後に plan.json に基づいて実行
4. 最終出力を検証
```

バリデーションスクリプトのエラーメッセージは具体的にする：
```
✗ 「バリデーション失敗」
✓ 「フィールド 'signature_date' が見つかりません。利用可能: customer_name, order_total, signature_date_signed」
```

---

## 参照ファイルの構成ルール

1. **1階層ルール**: SKILL.md → 参照ファイル（直接）。参照ファイル → 別の参照ファイルの連鎖は避ける
2. **100行超にはContents**: 長い参照ファイルの冒頭に目次を置く
3. **説明的なファイル名**: `doc2.md` ではなく `form_validation_rules.md`
4. **ドメイン別/機能別に整理**: `reference/finance.md` > `docs/file1.md`
5. **前方スラッシュのみ**: パスには `/` を使用（`\` は避ける）

---

## agents/ディレクトリの活用

agents/とreferences/はどちらもSKILL.mdから参照されるが、役割が異なる。

### references/ vs agents/ の使い分け

| 観点 | references/ | agents/ |
|------|------------|---------|
| **読み込み方** | コンテキストに読み込む | サブエージェントとして起動する |
| **コンテキスト消費** | あり（読んだ分だけ消費） | なし（別コンテキストで実行） |
| **用途** | 情報・仕様・ルールの提供 | 独立したサブタスクの実行 |
| **前提条件** | なし（どこでも使える） | サブエージェント機能が必要 |

### agents/に適したタスク

- **独立実行可能**: 入力と出力が明確で、本体のワークフローと並列に実行できる
- **レビュー・検証**: 成果物を第三者視点でチェックする（本体のコンテキストに影響されないほうがよい）
- **反復的サブタスク**: 複数の入力に対して同じ処理を繰り返す（並列起動で高速化）

### SKILL.mdからの参照パターン

```markdown
# references/ — 読み込み
**詳細手順**: [references/phase1-details.md](references/phase1-details.md) を参照

# agents/ — サブエージェント起動
`agents/reviewer.md` を読んでサブエージェントを起動し、品質をレビューする。
```
