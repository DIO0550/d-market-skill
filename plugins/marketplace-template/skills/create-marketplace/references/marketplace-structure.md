# Marketplace 構造の詳細仕様

Marketplace の各構成要素の仕様と設計指針。

---

## Contents

1. [ディレクトリ構造](#ディレクトリ構造)
2. [marketplace.json 仕様](#marketplacejson-仕様)
3. [plugin.json 仕様](#pluginjson-仕様)
4. [SKILL.md 仕様](#skillmd-仕様)
5. [段階的開示モデル](#段階的開示モデル)
6. [命名規則](#命名規則)

---

## ディレクトリ構造

```
marketplace-root/
├── .claude-plugin/
│   └── marketplace.json          # レジストリ（必須）
├── plugins/
│   ├── plugin-a/
│   │   ├── plugin.json           # プラグインメタデータ（必須）
│   │   └── skills/
│   │       ├── skill-1/
│   │       │   ├── SKILL.md      # メイン指示（必須）
│   │       │   ├── references/   # 参照資料（任意）
│   │       │   ├── scripts/      # 実行スクリプト（任意）
│   │       │   ├── templates/    # テンプレート（任意）
│   │       │   └── assets/       # アセット（任意）
│   │       └── skill-2/
│   │           └── SKILL.md
│   └── plugin-b/
│       ├── plugin.json
│       └── skills/
│           └── ...
├── .gitignore
└── README.md
```

### ポイント

- `.claude-plugin/` はルート直下に配置
- プラグインは `plugins/` ディレクトリ内に格納
- 各プラグインは独立したディレクトリ
- スキルは `skills/` サブディレクトリ内に格納
- 参照ファイルは SKILL.md から1階層のみ

---

## marketplace.json 仕様

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "owner-name"
  },
  "metadata": {
    "description": "Marketplace の説明",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugins/plugin-name",
      "description": "プラグインの説明",
      "version": "1.0.0",
      "category": "productivity",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | Yes | Marketplace の識別名 |
| `owner.name` | Yes | オーナー名 |
| `metadata.description` | Yes | Marketplace の説明 |
| `metadata.version` | Yes | バージョン（semver） |
| `plugins` | Yes | 登録プラグインの配列 |
| `plugins[].name` | Yes | プラグイン名 |
| `plugins[].source` | Yes | プラグインディレクトリへの相対パス |
| `plugins[].description` | Yes | プラグインの説明 |
| `plugins[].version` | Yes | プラグインバージョン |
| `plugins[].category` | No | カテゴリ |
| `plugins[].tags` | No | タグの配列 |

---

## plugin.json 仕様

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "プラグインの説明",
  "author": {
    "name": "author-name"
  },
  "skills": "./skills"
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | Yes | プラグイン名（marketplace.json と一致） |
| `version` | Yes | バージョン（semver） |
| `description` | Yes | プラグインの説明 |
| `author.name` | Yes | 作者名 |
| `skills` | Yes | スキルディレクトリへの相対パス |

---

## SKILL.md 仕様

### YAMLフロントマター

```yaml
---
name: skill-name
description: "スキルの説明"
---
```

**name の制約:**
- 最大64文字
- 小文字・数字・ハイフンのみ（`[a-z0-9-]+`）
- ハイフンで開始/終了不可、連続ハイフン不可
- 予約語不可: `anthropic`, `claude`
- XMLタグ不可

**description の制約:**
- 最大1024文字、空不可
- XMLタグ不可
- 「何をするか」+「いつ使うか」の両方を含める
- 三人称で記述
- トリガーキーワードを豊富に含める

### 本文

- 500行以内を推奨
- 超える場合は references/ に分離
- 命令形で記述

---

## 段階的開示モデル

| レベル | 読み込み | トークンコスト | 内容 |
|--------|---------|---------------|------|
| L1: メタデータ | 常に | ~100/スキル | YAML frontmatter |
| L2: 本文 | トリガー時 | <5k推奨 | SKILL.md本文 |
| L3: リソース | 必要時のみ | 実質無制限 | references/, scripts/ |

---

## 命名規則

- **Marketplace名**: 小文字・数字・ハイフン（例: `my-skills-marketplace`）
- **プラグイン名**: 小文字・数字・ハイフン（例: `pdf-tools`）
- **スキル名**: 小文字・数字・ハイフン（例: `form-filler`）
- **参照ファイル**: ケバブケース（例: `api-reference.md`）
- **スクリプト**: スネークケース（例: `validate_form.py`）
