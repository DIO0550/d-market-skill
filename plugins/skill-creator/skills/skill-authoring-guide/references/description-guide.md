# description最適化ガイド

SKILL.mdのYAMLフロントマターにおける`description`フィールドの最適化方法。
descriptionはClaudeがスキルを選択する**唯一の判断基準**であり、最も重要なフィールド。

## Contents

- descriptionの役割
- 効果的なdescriptionの書き方
- 良い例・悪い例
- 命名規則（nameフィールド）
- トリガー精度の評価方法

---

## descriptionの役割

Claudeは100以上のスキルの中からdescriptionのみでどのスキルを使うか判断する。

### 含めるべき情報

1. **何をするか** — スキルの主要機能
2. **いつ使うべきか** — トリガー条件、ユーザーの典型的な言い回し
3. **具体的なキーワード** — ファイル形式、ツール名、ドメイン用語

### 記述ルール

- **三人称で書く** — descriptionはシステムプロンプトに挿入される
  - ✓ 「PDFファイルからテキストを抽出し、フォームを入力する」
  - ✗ 「PDFの処理をお手伝いします」
  - ✗ 「このスキルを使ってPDFを処理できます」
- **やや積極的に** — Claudeはスキルを使わない方向にバイアスがあるため
- **1024文字以内**
- **XMLタグ禁止**

---

## 効果的なdescriptionの書き方

### 構造テンプレート

```
[主要機能の簡潔な列挙]。[具体的なトリガー条件]。[エッジケースや追加トリガー]。
```

### 良い例

```yaml
# PDF処理スキル
description: "PDFファイルからテキスト・表を抽出し、フォーム入力、ドキュメント結合を行う。PDFファイル操作、フォーム入力、ドキュメント抽出に関するリクエストで使用。.pdfファイルへの言及がある場合は積極的に使用すること。"

# Excel分析スキル
description: "Excelスプレッドシートの分析、ピボットテーブル作成、グラフ生成を行う。Excelファイル、スプレッドシート、表形式データ、.xlsxファイルの分析時に使用。"

# Gitコミットヘルパー
description: "git diffを分析して説明的なコミットメッセージを生成する。コミットメッセージの作成支援やステージされた変更のレビュー依頼時に使用。"

# BigQueryデータ分析
description: "BigQueryでの分析を支援。テーブルスキーマ、フィルタリングルール、クエリパターンを提供。売上データ、収益レポート、パイプライン分析、SQLクエリの作成時に使用。データ分析やBQ関連の質問では積極的に使用すること。"
```

### 悪い例

```yaml
# 曖昧すぎる
description: "ドキュメントを処理する"
description: "データを処理する"
description: "ファイル関連の作業を行う"

# キーワード不足
description: "文書変換ツール"

# 主語が不適切
description: "私はPDFの処理をお手伝いできます"
```

---

## 命名規則（nameフィールド）

### 制約

- 最大64文字
- 小文字・数字・ハイフンのみ
- XMLタグ禁止
- 予約語禁止：「anthropic」「claude」

### 推奨パターン

**動名詞形（gerund）** が最も分かりやすい：
- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

**名詞句も可：**
- `pdf-processing`
- `spreadsheet-analysis`

**動作形も可：**
- `process-pdfs`
- `analyze-spreadsheets`

### 避けるべきパターン

- 曖昧な名前：`helper`, `utils`, `tools`
- 汎用的すぎる：`documents`, `data`, `files`
- 予約語を含む：`anthropic-helper`, `claude-tools`
- コレクション内での不統一

---

## トリガー精度の評価方法

### 評価セットの作成

20個の評価クエリを作成 — should-triggerとshould-not-triggerの混合：

```json
[
  {"query": "このPDFからテキストを抽出して要約して", "should_trigger": true},
  {"query": "Pythonでfor文を書いて", "should_trigger": false},
  {"query": "PDFのフォームに自動入力したい", "should_trigger": true},
  {"query": "画像をPNGに変換して", "should_trigger": false}
]
```

### 良いテストクエリの特徴

**should-trigger（8-10個）:**
- 異なる言い回しで同じ意図を表現
- 明示的にスキル名やファイル形式を言わないが明らかに必要なケース
- 珍しいユースケース
- 他のスキルと競合するが、このスキルが勝つべきケース

**should-not-trigger（8-10個）:**
- **最も価値があるのはニアミス** — キーワードは共有するが実際は別のことが必要
- 単純なキーワードマッチではトリガーするが、すべきでないケース
- 明らかに無関係なクエリ（例：フィボナッチ関数）は**テストとして無価値**

### テストクエリの品質基準

```
# 悪い例（抽象的すぎる）
"データをフォーマットして"
"PDFからテキストを抽出して"

# 良い例（具体的・リアル）
"上司からQ4の売上データのPDFが送られてきたんだけど、
各ページのテーブルからデータを抽出してCSVにまとめてくれない？
ファイルは ~/Downloads/Q4_sales_final_v2.pdf にあるよ"
```

テストクエリはカジュアルな表現、略語、タイポ、様々な長さを含めるべき。
