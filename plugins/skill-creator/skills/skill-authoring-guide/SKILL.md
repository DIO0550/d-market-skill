---
name: skill-authoring-guide
description: "Agent Skillの設計・作成・改善を支援するスキル。SKILL.mdの構成、YAMLフロントマター、段階的開示パターン、ワークフロー設計、評価・イテレーションのベストプラクティスを網羅。「スキルを作りたい」「SKILL.mdの書き方」「スキル設計」「カスタムSkill作成」「スキルのベストプラクティス」「スキルの改善」「スキルをパッケージ化」「スキルのテスト」「スキル構造」などのキーワードでトリガー。新規スキル作成、既存スキルの改善、スキル設計のレビュー、スキルのパッケージング、いずれの場面でも積極的に使用すること。"
---

# Skill Authoring Guide

Agent Skillの設計・作成・改善を体系的に支援するガイド。
Anthropic公式ドキュメントのベストプラクティスに基づく。

---

## ワークフロー概要

スキル作成は以下のフェーズで進行する：

1. **意図の把握** — 何を実現するスキルか、いつトリガーすべきかを明確化
2. **構造設計** — ディレクトリ構成、段階的開示戦略の決定
3. **SKILL.md執筆** — フロントマター + 本文の作成
4. **リソース作成** — 参照ファイル、スクリプト、テンプレートの準備
5. **テスト・評価** — 実タスクでの検証とイテレーション
6. **パッケージング** — .skillファイルへの梱包と配布

ユーザーがどのフェーズにいるかを判断し、適切なステップから支援を開始する。

---

## Phase 1: 意図の把握

以下を確認してユーザーの意図を明確化する：

1. **このスキルで何ができるようになるか？** — Claudeに追加される具体的な能力
2. **いつトリガーすべきか？** — ユーザーが使う言い回し、コンテキスト
3. **期待するアウトプット形式は？** — ファイル形式、構造、品質基準
4. **テストケースは必要か？** — 客観的に検証可能な出力があるスキルはテスト推奨

会話の中で既にワークフローが確立されている場合（例：「これをスキルにして」）、使ったツール、手順、修正点をまず会話履歴から抽出する。

---

## Phase 2: 構造設計

### 基本構造

```
skill-name/
├── SKILL.md              # メイン指示（トリガー時に読み込み）
├── references/           # 参照資料（必要時に読み込み）
│   ├── guide.md
│   └── api-reference.md
├── scripts/              # 実行スクリプト（実行のみ、コンテキスト非消費）
│   ├── validate.py
│   └── process.py
├── templates/            # テンプレートファイル
│   └── output-template.md
└── assets/               # アセット（画像、フォント等）
```

### 3段階の読み込みモデル（段階的開示）

スキルの内容は3レベルに分かれ、それぞれ異なるタイミングで読み込まれる：

| レベル | 読み込みタイミング | トークンコスト | 内容 |
|--------|-------------------|---------------|------|
| **L1: メタデータ** | 常に（起動時） | ~100トークン/スキル | YAMLの`name`と`description` |
| **L2: 本文** | トリガー時 | 5kトークン未満推奨 | SKILL.md本文（指示・ワークフロー） |
| **L3: リソース** | 必要時のみ | 実質無制限 | references/, scripts/, assets/ |

**設計原則：**
- SKILL.md本文は **500行以内** に収める
- 500行を超えそうなら、詳細を参照ファイルに分離する
- スクリプトは**実行**されるためコンテキストを消費しない
- 参照ファイルへのリンクは **SKILL.mdから1階層のみ** （深いネストは避ける）

### ドメイン別構成パターン

複数ドメインをサポートするスキルの場合：

```
cloud-deploy/
├── SKILL.md (概要 + ナビゲーション)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Claudeは関連するドメインのファイルだけを読み込む。

構造設計の詳細パターンは [references/structure-patterns.md](references/structure-patterns.md) を参照。

---

## Phase 3: SKILL.md執筆

### YAMLフロントマター（必須）

```yaml
---
name: your-skill-name
description: "スキルの説明。何をするか＋いつ使うべきかの両方を含める。"
---
```

**nameフィールドの制約：**
- 最大64文字
- 小文字・数字・ハイフンのみ
- XMLタグ禁止
- 予約語禁止：「anthropic」「claude」

**descriptionフィールドの制約：**
- 最大1024文字、空不可
- XMLタグ禁止
- **何をするか** と **いつ使うべきか** の両方を含める
- 三人称で記述する（「Processes...」ではなく「I can help...」は避ける）

**descriptionの書き方のコツ：**
- Claudeは100以上のスキルからdescriptionで選択する — 十分な具体性が必要
- トリガーキーワードを豊富に含める
- やや積極的（pushy）な表現にする — Claudeはスキルを使わない方向にバイアスがかかりやすい

```yaml
# 良い例
description: "PDFファイルからテキスト・表を抽出し、フォーム入力・結合を行う。PDFファイル操作、フォーム入力、ドキュメント抽出に関する依頼で使用。.pdfファイルが言及された場合は積極的に使用すること。"

# 悪い例
description: "ドキュメントを処理する"
```

### 本文の執筆原則

詳細は [references/writing-principles.md](references/writing-principles.md) を参照。主要原則：

1. **簡潔さが鍵** — Claudeは既に賢い。Claudeが既に知っていることは書かない
2. **自由度を適切に設定** — タスクの脆弱性に応じてlow/medium/highの自由度を選ぶ
3. **命令形を使う** — 「〜してください」ではなく「〜する」
4. **WHYを説明する** — ALWAYSやNEVERの連発より、理由を説明する方が効果的
5. **一貫した用語** — 同じ概念に異なる単語を混在させない
6. **時間依存情報を避ける** — 「2025年8月以降は〜」のような表現は使わない

### テンプレート集

スキルの用途に応じたSKILL.mdテンプレートは [templates/](templates/) ディレクトリを参照：
- `templates/instruction-only.md` — コードなしの指示スキル用
- `templates/with-scripts.md` — スクリプト付きスキル用
- `templates/multi-domain.md` — 複数ドメイン対応スキル用

---

## Phase 4: リソース作成

### 参照ファイル（references/）

- 100行以上のファイルには **目次（Contents）** を冒頭に追加
- SKILL.mdから参照する際は用途を明記する：
  ```markdown
  **フォーム入力の詳細**: [references/forms.md](references/forms.md) を参照
  **APIリファレンス**: [references/api.md](references/api.md) を参照
  ```

### スクリプト（scripts/）

スクリプトのメリット：
- 生成コードより**信頼性が高い**
- コンテキストを**消費しない**（出力のみ）
- **実行時間が短い**（生成不要）
- **一貫性を保証**

スクリプトの設計原則：
- エラーを適切に処理する（Claudeに丸投げしない）
- マジックナンバーを避け、定数の理由をコメントで説明する
- 実行方法を SKILL.md に明記する：
  ```markdown
  ## フォーム解析
  実行: `python scripts/analyze_form.py input.pdf`
  ```

---

## Phase 5: テスト・評価

### 評価駆動開発

**ドキュメントを書く前に評価を作る。** 手順：

1. スキルなしでClaudeにタスクを実行させ、失敗点を特定
2. 3つ以上の評価シナリオを作成
3. ベースライン（スキルなし）の性能を測定
4. 最小限のスキルを作成して評価を通す
5. イテレーション

### Claude A / Claude B パターン

最も効果的な開発プロセス：
- **Claude A**（設計者）：スキルの設計・改善を支援
- **Claude B**（実行者）：スキルを使って実タスクを実行
- Claude Bの振る舞いを観察し、Claude Aにフィードバックを持ち帰る

### テストケース構造

```json
{
  "skills": ["your-skill-name"],
  "query": "ユーザーが実際に入力しそうなプロンプト",
  "files": ["test-files/sample.pdf"],
  "expected_behavior": [
    "期待される動作1",
    "期待される動作2"
  ]
}
```

### テストのポイント

- 使用予定の**全モデル**でテスト（Haiku / Sonnet / Opus）
- テストシナリオは最低3つ
- チームからのフィードバックを収集
- Claudeがスキルのファイルをどの順序で読むか観察し、構造を改善

---

## Phase 6: パッケージング

### バリデーション

パッケージ化前にバリデーションスクリプトを実行：

```bash
python scripts/quick_validate.py /path/to/skill-directory
```

チェック項目：
- SKILL.mdの存在
- YAMLフロントマターのname/description
- nameの形式（小文字・数字・ハイフン、64文字以内）
- descriptionの長さ（1024文字以内）
- SKILL.md本文の行数（500行超で警告）

### パッケージ化

```bash
python scripts/package_skill.py /path/to/skill-directory
```

出力: `skill-name.skill` ファイル（zipアーカイブ）

---

## チェックリスト

スキルを共有する前の最終確認：

### コア品質
- [ ] descriptionが具体的でトリガーキーワードを含む
- [ ] descriptionに「何をするか」と「いつ使うか」の両方がある
- [ ] SKILL.md本文が500行以内
- [ ] 詳細は別ファイルに分離されている（必要に応じて）
- [ ] 時間依存情報がない
- [ ] 用語が一貫している
- [ ] 例が具体的
- [ ] ファイル参照が1階層のみ
- [ ] 段階的開示が適切に使われている
- [ ] ワークフローのステップが明確

### コード・スクリプト（該当する場合）
- [ ] スクリプトがエラーを適切に処理する
- [ ] マジックナンバーがない
- [ ] 依存パッケージがリストされている
- [ ] Windowsパスを使っていない（常にフォワードスラッシュ / を使用）

### テスト
- [ ] 3つ以上の評価シナリオを作成
- [ ] 使用予定の全モデルでテスト済み
- [ ] 実際の使用シナリオでテスト済み

---

## 参照ファイル一覧

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/writing-principles.md](references/writing-principles.md) | 執筆原則の詳細（簡潔さ、自由度、パターン集） | SKILL.md執筆時 |
| [references/structure-patterns.md](references/structure-patterns.md) | ディレクトリ構成の詳細パターン | 構造設計時 |
| [references/description-guide.md](references/description-guide.md) | description最適化ガイド | トリガー精度改善時 |
| [templates/instruction-only.md](templates/instruction-only.md) | コードなしスキルのテンプレート | 新規作成時 |
| [templates/with-scripts.md](templates/with-scripts.md) | スクリプト付きスキルのテンプレート | 新規作成時 |
| [templates/multi-domain.md](templates/multi-domain.md) | 複数ドメインスキルのテンプレート | 新規作成時 |
