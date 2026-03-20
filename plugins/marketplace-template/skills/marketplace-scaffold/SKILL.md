---
name: marketplace-scaffold
description: "Claude Code Skills Marketplaceの雛形プロジェクトを生成するスキル。.claude-plugin/marketplace.json、プラグインディレクトリ構造、SKILL.mdテンプレート、バリデーション・パッケージングスクリプトを含む完全なMarketplace構造をスキャフォールドする。「マーケットプレイスを作りたい」「Marketplace雛形」「スキルマーケットプレイス作成」「marketplace template」「プラグインリポジトリの初期化」「スキル配布基盤を構築」「marketplace scaffold」「新しいmarketplaceを立ち上げる」などのキーワードでトリガー。Marketplace構造の新規作成、既存リポジトリへのMarketplace構造追加、いずれの場面でも積極的に使用すること。"
---

# Marketplace Scaffold

Claude Code Skills Marketplaceの雛形プロジェクトを生成する。
ユーザーのリポジトリに完全なMarketplace構造をスキャフォールドし、すぐにスキル開発を始められる状態にする。

---

## ワークフロー概要

```
進捗:
- [ ] Step 1: 要件ヒアリング
- [ ] Step 2: スキャフォールド実行
- [ ] Step 3: 初期プラグイン作成
- [ ] Step 4: 動作確認
```

---

## Step 1: 要件ヒアリング

以下を確認する：

1. **Marketplace名** — リポジトリ/プロジェクト名（例: `my-skills-marketplace`）
2. **オーナー名** — GitHub ユーザー名または組織名
3. **初期プラグイン** — 最初に作成するプラグインの名前と概要（省略可）
4. **対象ディレクトリ** — 出力先パス（デフォルト: カレントディレクトリ）

省略された項目はデフォルト値を使用する。全項目省略の場合でもスキャフォールドは実行可能。

---

## Step 2: スキャフォールド実行

スキャフォールドスクリプトを実行する：

```bash
python scripts/scaffold.py <output-dir> --name <marketplace-name> --owner <owner-name>
```

**オプション:**
- `--name` : Marketplace名（デフォルト: ディレクトリ名）
- `--owner` : オーナー名（デフォルト: git config の user.name）
- `--plugin` : 初期プラグイン名（指定時のみ作成）
- `--with-example` : サンプルスキルを含める

スクリプトが生成するファイル構造：

```
<output-dir>/
├── .claude-plugin/
│   └── marketplace.json       # Marketplaceレジストリ
├── plugins/                   # プラグイン格納ディレクトリ
│   └── <plugin-name>/        # （--plugin指定時）
│       ├── plugin.json
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md
│               ├── references/
│               ├── scripts/
│               └── templates/
├── .gitignore
└── README.md
```

---

## Step 3: 初期プラグイン作成

Step 2で `--plugin` を指定しなかった場合、ここでプラグインを追加する。

### プラグイン追加

```bash
python scripts/scaffold.py <output-dir> --add-plugin <plugin-name>
```

追加されるファイル：
- `plugins/<plugin-name>/plugin.json`
- `plugins/<plugin-name>/skills/` （空ディレクトリ）
- `marketplace.json` への登録

### スキル追加

```bash
python scripts/scaffold.py <output-dir> --add-skill <plugin-name>/<skill-name>
```

追加されるファイル：
- `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`（テンプレート）
- `plugins/<plugin-name>/skills/<skill-name>/references/`
- `plugins/<plugin-name>/skills/<skill-name>/scripts/`

---

## Step 4: 動作確認

スキャフォールド後、以下を確認する：

1. **marketplace.json の構造確認** — 必須フィールドがすべて揃っているか
2. **plugin.json の確認** — skills パスが正しいか
3. **SKILL.md の確認** — フロントマターが正しい形式か

テンプレートの SKILL.md はプレースホルダーを含む。ユーザーにカスタマイズを促す。

---

## 生成ファイルの仕様

### marketplace.json

```json
{
  "name": "<marketplace-name>",
  "owner": {
    "name": "<owner-name>"
  },
  "metadata": {
    "description": "Claude Code Skills Marketplace",
    "version": "1.0.0"
  },
  "plugins": []
}
```

### plugin.json

```json
{
  "name": "<plugin-name>",
  "version": "1.0.0",
  "description": "<plugin-description>",
  "author": {
    "name": "<owner-name>"
  },
  "skills": "./skills"
}
```

### SKILL.md テンプレート

[templates/skill-template.md](templates/skill-template.md) を参照。

---

## スキャフォールド後のガイダンス

生成完了後、ユーザーに以下を伝える：

1. **SKILL.md を編集** — プレースホルダーを実際の内容に置き換える
2. **description を充実させる** — トリガーキーワードを豊富に含める
3. **references/ にドキュメントを追加** — 詳細なガイドやAPI仕様
4. **scripts/ にツールを追加** — バリデーション、変換などの自動化スクリプト

---

## 注意事項

- marketplace.json は `.claude-plugin/` ディレクトリ内に配置する（ルート直下ではない）
- プラグイン名・スキル名は小文字・数字・ハイフンのみ
- 既存のファイルがある場合、上書きせずスキップする
- `--with-example` は学習用のサンプルスキルを含め、実運用時は削除を推奨

---

## 参照ファイル

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/marketplace-structure.md](references/marketplace-structure.md) | Marketplace構造の詳細仕様 | 構造をカスタマイズしたい場合 |
| [templates/skill-template.md](templates/skill-template.md) | 生成されるSKILL.mdのテンプレート | テンプレート内容を確認・変更したい場合 |
| [templates/gitignore-template.md](templates/gitignore-template.md) | 生成される.gitignoreのテンプレート | .gitignoreの内容を確認したい場合 |
