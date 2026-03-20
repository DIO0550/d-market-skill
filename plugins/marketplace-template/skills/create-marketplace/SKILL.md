---
name: create-marketplace
description: "Claude Code Skills Marketplaceのフォルダ構造を生成するスキル。.claude-plugin/marketplace.json、plugins/ディレクトリ、plugin.json、skills/ディレクトリを含むMarketplaceのディレクトリ構造をスキャフォールドする。「マーケットプレイスを作りたい」「Marketplace雛形」「スキルマーケットプレイス作成」「marketplace template」「プラグインリポジトリの初期化」「スキル配布基盤を構築」「marketplace scaffold」「新しいmarketplaceを立ち上げる」などのキーワードでトリガー。Marketplace構造の新規作成、既存リポジトリへのMarketplace構造追加、いずれの場面でも積極的に使用すること。"
disable-model-invocation: true
---

# Marketplace Scaffold

Claude Code Skills Marketplaceのフォルダ構造を生成する。
ファイルの中身（SKILL.md等）は生成しない。ディレクトリとJSON設定ファイルのみを作成する。

---

## ワークフロー

### Step 1: 要件ヒアリング

以下を確認する：

1. **Marketplace名** — リポジトリ/プロジェクト名（例: `my-skills-marketplace`）
2. **オーナー名** — GitHub ユーザー名または組織名
3. **初期プラグイン名** — 最初に作成するプラグインの名前（省略可）
4. **対象ディレクトリ** — 出力先パス（デフォルト: カレントディレクトリ）

省略された項目はデフォルト値を使用する。全項目省略でも実行可能。

### Step 2: フォルダ構造の作成

ヒアリング結果に基づき、以下の構造を作成する：

```
<output-dir>/
├── .claude-plugin/
│   └── marketplace.json       # Marketplaceレジストリ
├── plugins/                   # プラグイン格納ディレクトリ
│   └── <plugin-name>/        # （プラグイン指定時）
│       ├── plugin.json
│       └── skills/            # スキル格納ディレクトリ（空）
└── .gitignore
```

**marketplace.json の形式：**

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

**plugin.json の形式：**

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

プラグインを作成した場合、marketplace.json の plugins 配列にも登録する。

### Step 3: 動作確認

作成後、以下を確認する：

1. **marketplace.json** — 必須フィールド（name, owner, plugins）が揃っているか
2. **plugin.json** — skills パスが `./skills` になっているか
3. **ディレクトリ構造** — plugins/ 以下の階層が正しいか

---

## 命名規則

- プラグイン名・スキル名は **小文字・数字・ハイフンのみ**（`[a-z0-9-]+`）
- 最大64文字
- ハイフンで開始/終了不可、連続ハイフン不可

---

## 注意事項

- marketplace.json は `.claude-plugin/` ディレクトリ内に配置する（ルート直下ではない）
- 既存のファイルがある場合、上書きしない
- SKILL.md やスクリプトの内容はこのスキルの範囲外

---

## 参照ファイル

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/marketplace-structure.md](references/marketplace-structure.md) | Marketplace構造の詳細仕様 | 構造をカスタマイズしたい場合 |
