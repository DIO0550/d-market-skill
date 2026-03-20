---
name: marketplace-scaffold
description: "Claude Code Skills Marketplaceのフォルダ構造を生成するスキル。.claude-plugin/marketplace.json、plugins/ディレクトリ、plugin.json、skills/ディレクトリを含むMarketplaceのディレクトリ構造をスキャフォールドする。「マーケットプレイスを作りたい」「Marketplace雛形」「スキルマーケットプレイス作成」「marketplace template」「プラグインリポジトリの初期化」「スキル配布基盤を構築」「marketplace scaffold」「新しいmarketplaceを立ち上げる」などのキーワードでトリガー。Marketplace構造の新規作成、既存リポジトリへのMarketplace構造追加、いずれの場面でも積極的に使用すること。"
disable-model-invocation: true
---

# Marketplace Scaffold

Claude Code Skills Marketplaceのフォルダ構造を生成する。
ファイルの中身（SKILL.md等）は生成しない。ディレクトリとJSON設定ファイルのみを作成する。

---

## ワークフロー概要

```
進捗:
- [ ] Step 1: 要件ヒアリング
- [ ] Step 2: スキャフォールド実行
- [ ] Step 3: 動作確認
```

---

## Step 1: 要件ヒアリング

以下を確認する：

1. **Marketplace名** — リポジトリ/プロジェクト名（例: `my-skills-marketplace`）
2. **オーナー名** — GitHub ユーザー名または組織名
3. **初期プラグイン名** — 最初に作成するプラグインの名前（省略可）
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

生成されるフォルダ構造：

```
<output-dir>/
├── .claude-plugin/
│   └── marketplace.json       # Marketplaceレジストリ
├── plugins/                   # プラグイン格納ディレクトリ
│   └── <plugin-name>/        # （--plugin指定時）
│       ├── plugin.json
│       └── skills/            # スキル格納ディレクトリ（空）
└── .gitignore
```

### プラグイン追加

```bash
python scripts/scaffold.py <output-dir> --add-plugin <plugin-name>
```

### スキルディレクトリ追加

```bash
python scripts/scaffold.py <output-dir> --add-skill <plugin-name>/<skill-name>
```

生成されるディレクトリ：
- `plugins/<plugin-name>/skills/<skill-name>/`
- `plugins/<plugin-name>/skills/<skill-name>/references/`
- `plugins/<plugin-name>/skills/<skill-name>/scripts/`

SKILL.md などの中身のファイルは生成しない。ディレクトリのみ。

---

## Step 3: 動作確認

スキャフォールド後、以下を確認する：

1. **marketplace.json** — 必須フィールド（name, owner, plugins）が揃っているか
2. **plugin.json** — skills パスが `./skills` になっているか
3. **ディレクトリ構造** — plugins/ 以下の階層が正しいか

---

## 注意事項

- marketplace.json は `.claude-plugin/` ディレクトリ内に配置する（ルート直下ではない）
- プラグイン名・スキル名は小文字・数字・ハイフンのみ
- 既存のファイルがある場合、上書きせずスキップする
- SKILL.md やスクリプトの内容はこのスキルの範囲外。別途作成する

---

## 参照ファイル

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/marketplace-structure.md](references/marketplace-structure.md) | Marketplace構造の詳細仕様 | 構造をカスタマイズしたい場合 |
