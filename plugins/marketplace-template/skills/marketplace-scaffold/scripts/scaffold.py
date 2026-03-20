#!/usr/bin/env python3
"""
Marketplace Scaffold - Skills Marketplaceの雛形プロジェクトを生成

Usage:
    python scripts/scaffold.py <output-dir> [options]

Options:
    --name <name>        Marketplace名（デフォルト: ディレクトリ名）
    --owner <owner>      オーナー名（デフォルト: git config user.name）
    --plugin <name>      初期プラグイン名（指定時のみ作成）
    --with-example       サンプルスキルを含める
    --add-plugin <name>  既存Marketplaceにプラグインを追加
    --add-skill <p/s>    既存プラグインにスキルを追加（plugin-name/skill-name）

Examples:
    python scripts/scaffold.py ./my-marketplace --name my-skills --owner user1
    python scripts/scaffold.py ./my-marketplace --plugin my-first-plugin --with-example
    python scripts/scaffold.py ./my-marketplace --add-plugin new-plugin
    python scripts/scaffold.py ./my-marketplace --add-skill my-plugin/my-skill
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


SKILL_TEMPLATE = '''---
name: {skill_name}
description: "スキルの主要機能の説明。具体的なトリガー条件を記述する。関連キーワードでは積極的に使用すること。"
---

# {skill_title}

スキルの目的を1-2行で説明。

---

## ワークフロー

### Step 1: [最初のステップ]

[具体的な指示]

### Step 2: [次のステップ]

[具体的な指示]

### Step 3: [最後のステップ]

[具体的な指示]

---

## 出力形式

[期待する出力のテンプレートまたは説明]

---

## 例

**例1:**
Input: [入力例]
Output: [出力例]

---

## 注意事項

- [重要なルール1]
- [重要なルール2]
'''

EXAMPLE_SKILL_TEMPLATE = '''---
name: hello-world
description: "サンプルスキル。Marketplaceの動作確認用。「hello」「サンプル」「テスト」などのキーワードでトリガー。Marketplace構造の学習・動作確認に使用すること。"
---

# Hello World

Marketplace の動作確認用サンプルスキル。
このスキルは学習用であり、実運用時は削除を推奨する。

---

## ワークフロー

### Step 1: 挨拶

ユーザーに挨拶を返す。

### Step 2: Marketplace情報の表示

このMarketplaceに登録されているプラグインとスキルの一覧を表示する。

---

## 出力形式

```
こんにちは！このMarketplaceには以下のスキルが登録されています：
- [プラグイン名] / [スキル名]: [説明]
```

---

## 注意事項

- このスキルは学習・動作確認用
- 実運用時は削除すること
'''

GITIGNORE_TEMPLATE = """# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Build
dist/
*.skill

# Test
test-output/
workspace/
"""

README_TEMPLATE = """# {name}

Claude Code Skills Marketplace

## 構造

```
{name}/
├── .claude-plugin/
│   └── marketplace.json    # Marketplaceレジストリ
└── plugins/                # プラグイン格納ディレクトリ
    └── <plugin-name>/
        ├── plugin.json     # プラグインメタデータ
        └── skills/
            └── <skill-name>/
                ├── SKILL.md       # メイン指示
                ├── references/    # 参照資料
                ├── scripts/       # 実行スクリプト
                └── templates/     # テンプレート
```

## プラグイン一覧

{plugin_list}

## スキルの追加方法

1. `plugins/<plugin-name>/skills/` にスキルディレクトリを作成
2. `SKILL.md` を作成（YAML フロントマター + 本文）
3. `marketplace.json` にプラグインを登録（未登録の場合）
"""


def validate_name(name):
    """名前のバリデーション"""
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"エラー: 名前 '{name}' は小文字・数字・ハイフンのみ使用可能です")
        return False
    if len(name) > 64:
        print(f"エラー: 名前 '{name}' が長すぎます（最大64文字）")
        return False
    if name.startswith('-') or name.endswith('-') or '--' in name:
        print(f"エラー: 名前 '{name}' はハイフンで開始/終了できず、連続ハイフンも不可です")
        return False
    return True


def get_git_user():
    """git config から user.name を取得"""
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return "your-name"


def write_file(path, content, overwrite=False):
    """ファイルを書き込む（既存ファイルはスキップ）"""
    if path.exists() and not overwrite:
        print(f"  -> スキップ（既存）: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"  + 作成: {path}")
    return True


def create_marketplace(output_dir, name, owner):
    """Marketplace の基本構造を生成"""
    root = Path(output_dir).resolve()

    marketplace_json = {
        "name": name,
        "owner": {"name": owner},
        "metadata": {
            "description": "Claude Code Skills Marketplace",
            "version": "1.0.0"
        },
        "plugins": []
    }

    files_created = 0

    # .claude-plugin/marketplace.json
    mp_path = root / '.claude-plugin' / 'marketplace.json'
    if write_file(mp_path, json.dumps(marketplace_json, indent=2, ensure_ascii=False) + '\n'):
        files_created += 1

    # plugins/ ディレクトリ
    plugins_dir = root / 'plugins'
    plugins_dir.mkdir(parents=True, exist_ok=True)

    # .gitignore
    gi_path = root / '.gitignore'
    if write_file(gi_path, GITIGNORE_TEMPLATE):
        files_created += 1

    # README.md
    readme_path = root / 'README.md'
    readme_content = README_TEMPLATE.format(
        name=name,
        plugin_list="（まだプラグインが登録されていません）"
    )
    if write_file(readme_path, readme_content):
        files_created += 1

    return files_created


def add_plugin(output_dir, plugin_name, owner=None, description=None):
    """プラグインを追加"""
    root = Path(output_dir).resolve()

    if not validate_name(plugin_name):
        return 0

    # marketplace.json の読み込み・更新
    mp_path = root / '.claude-plugin' / 'marketplace.json'
    if not mp_path.exists():
        print(f"エラー: marketplace.json が見つかりません: {mp_path}")
        print("先に Marketplace を作成してください")
        return 0

    marketplace = json.loads(mp_path.read_text(encoding='utf-8'))
    if owner is None:
        owner = marketplace.get('owner', {}).get('name', 'your-name')
    if description is None:
        description = f"{plugin_name} プラグインの説明。"

    # 重複チェック
    existing_names = [p['name'] for p in marketplace.get('plugins', [])]
    if plugin_name in existing_names:
        print(f"エラー: プラグイン '{plugin_name}' は既に登録されています")
        return 0

    # plugin.json 作成
    plugin_dir = root / 'plugins' / plugin_name
    plugin_json = {
        "name": plugin_name,
        "version": "1.0.0",
        "description": description,
        "author": {"name": owner},
        "skills": "./skills"
    }

    files_created = 0

    pj_path = plugin_dir / 'plugin.json'
    if write_file(pj_path, json.dumps(plugin_json, indent=2, ensure_ascii=False) + '\n'):
        files_created += 1

    # skills/ ディレクトリ
    skills_dir = plugin_dir / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)

    # marketplace.json にプラグインを追加
    marketplace['plugins'].append({
        "name": plugin_name,
        "source": f"./plugins/{plugin_name}",
        "description": description,
        "version": "1.0.0",
        "category": "productivity",
        "tags": []
    })
    write_file(mp_path, json.dumps(marketplace, indent=2, ensure_ascii=False) + '\n', overwrite=True)

    return files_created


def add_skill(output_dir, plugin_name, skill_name, with_example=False):
    """スキルを追加"""
    root = Path(output_dir).resolve()

    if not validate_name(skill_name):
        return 0

    plugin_dir = root / 'plugins' / plugin_name
    if not plugin_dir.exists():
        print(f"エラー: プラグイン '{plugin_name}' が見つかりません: {plugin_dir}")
        return 0

    skill_dir = plugin_dir / 'skills' / skill_name
    files_created = 0

    # SKILL.md
    skill_title = skill_name.replace('-', ' ').title()
    if with_example and skill_name == 'hello-world':
        content = EXAMPLE_SKILL_TEMPLATE
    else:
        content = SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)

    sm_path = skill_dir / 'SKILL.md'
    if write_file(sm_path, content):
        files_created += 1

    # サブディレクトリ
    for subdir in ['references', 'scripts', 'templates']:
        (skill_dir / subdir).mkdir(parents=True, exist_ok=True)

    return files_created


def main():
    parser = argparse.ArgumentParser(
        description='Claude Code Skills Marketplace の雛形を生成'
    )
    parser.add_argument('output_dir', help='出力先ディレクトリ')
    parser.add_argument('--name', help='Marketplace名（デフォルト: ディレクトリ名）')
    parser.add_argument('--owner', help='オーナー名（デフォルト: git user.name）')
    parser.add_argument('--plugin', help='初期プラグイン名')
    parser.add_argument('--with-example', action='store_true', help='サンプルスキルを含める')
    parser.add_argument('--add-plugin', metavar='NAME', help='既存Marketplaceにプラグインを追加')
    parser.add_argument('--add-skill', metavar='PLUGIN/SKILL', help='既存プラグインにスキルを追加')

    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    name = args.name or output_dir.name
    owner = args.owner or get_git_user()

    # プラグイン追加モード
    if args.add_plugin:
        print(f"\n📦 プラグイン追加: {args.add_plugin}")
        count = add_plugin(str(output_dir), args.add_plugin, owner)
        print(f"\n完了: {count} ファイル作成")
        return

    # スキル追加モード
    if args.add_skill:
        parts = args.add_skill.split('/')
        if len(parts) != 2:
            print("エラー: --add-skill は 'plugin-name/skill-name' の形式で指定してください")
            sys.exit(1)
        plugin_name, skill_name = parts
        print(f"\n📝 スキル追加: {plugin_name}/{skill_name}")
        count = add_skill(str(output_dir), plugin_name, skill_name)
        print(f"\n完了: {count} ファイル作成")
        return

    # 新規 Marketplace 作成
    if not validate_name(name):
        sys.exit(1)

    print(f"\n🏗️  Marketplace スキャフォールド")
    print(f"   名前: {name}")
    print(f"   オーナー: {owner}")
    print(f"   出力先: {output_dir}\n")

    total_files = 0

    # 基本構造
    print("--- 基本構造 ---")
    total_files += create_marketplace(str(output_dir), name, owner)

    # 初期プラグイン
    if args.plugin:
        if not validate_name(args.plugin):
            sys.exit(1)
        print(f"\n--- プラグイン: {args.plugin} ---")
        total_files += add_plugin(str(output_dir), args.plugin, owner)

        # サンプルスキル
        if args.with_example:
            print(f"\n--- サンプルスキル: hello-world ---")
            total_files += add_skill(str(output_dir), args.plugin, 'hello-world', with_example=True)

    print(f"\n{'='*50}")
    print(f"✅ スキャフォールド完了！ {total_files} ファイル作成")
    print(f"\n次のステップ:")
    if not args.plugin:
        print(f"  1. プラグインを追加: python scripts/scaffold.py {output_dir} --add-plugin <name>")
        print(f"  2. スキルを追加: python scripts/scaffold.py {output_dir} --add-skill <plugin>/<skill>")
    else:
        print(f"  1. SKILL.md を編集してスキルの内容を記述")
        print(f"  2. description にトリガーキーワードを追加")
        print(f"  3. references/ や scripts/ に必要なファイルを追加")


if __name__ == "__main__":
    main()
