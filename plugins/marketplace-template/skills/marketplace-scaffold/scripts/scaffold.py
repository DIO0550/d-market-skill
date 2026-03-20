#!/usr/bin/env python3
"""
Marketplace Scaffold - Skills Marketplaceのフォルダ構造を生成

ディレクトリ構造とJSON設定ファイルのみを生成する。
SKILL.mdなどのコンテンツファイルは生成しない。

Usage:
    python scripts/scaffold.py <output-dir> [options]

Options:
    --name <name>        Marketplace名（デフォルト: ディレクトリ名）
    --owner <owner>      オーナー名（デフォルト: git config user.name）
    --plugin <name>      初期プラグイン名（指定時のみ作成）
    --add-plugin <name>  既存Marketplaceにプラグインを追加
    --add-skill <p/s>    既存プラグインにスキルディレクトリを追加（plugin-name/skill-name）

Examples:
    python scripts/scaffold.py ./my-marketplace --name my-skills --owner user1
    python scripts/scaffold.py ./my-marketplace --plugin my-first-plugin
    python scripts/scaffold.py ./my-marketplace --add-plugin new-plugin
    python scripts/scaffold.py ./my-marketplace --add-skill my-plugin/my-skill
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


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


def create_dir(path):
    """ディレクトリを作成"""
    path.mkdir(parents=True, exist_ok=True)
    print(f"  + ディレクトリ: {path}")


def create_marketplace(output_dir, name, owner):
    """Marketplace の基本フォルダ構造を生成"""
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
    create_dir(root / 'plugins')

    # .gitignore
    gi_path = root / '.gitignore'
    if write_file(gi_path, GITIGNORE_TEMPLATE):
        files_created += 1

    return files_created


def add_plugin(output_dir, plugin_name, owner=None, description=None):
    """プラグインのフォルダ構造を追加"""
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
    create_dir(plugin_dir / 'skills')

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


def add_skill(output_dir, plugin_name, skill_name):
    """スキルのディレクトリ構造を追加（SKILL.mdは生成しない）"""
    root = Path(output_dir).resolve()

    if not validate_name(skill_name):
        return 0

    plugin_dir = root / 'plugins' / plugin_name
    if not plugin_dir.exists():
        print(f"エラー: プラグイン '{plugin_name}' が見つかりません: {plugin_dir}")
        return 0

    skill_dir = plugin_dir / 'skills' / skill_name

    # ディレクトリのみ作成
    create_dir(skill_dir)
    for subdir in ['references', 'scripts']:
        create_dir(skill_dir / subdir)

    return 0  # ファイルは作成しない


def main():
    parser = argparse.ArgumentParser(
        description='Claude Code Skills Marketplace のフォルダ構造を生成'
    )
    parser.add_argument('output_dir', help='出力先ディレクトリ')
    parser.add_argument('--name', help='Marketplace名（デフォルト: ディレクトリ名）')
    parser.add_argument('--owner', help='オーナー名（デフォルト: git user.name）')
    parser.add_argument('--plugin', help='初期プラグイン名')
    parser.add_argument('--add-plugin', metavar='NAME', help='既存Marketplaceにプラグインを追加')
    parser.add_argument('--add-skill', metavar='PLUGIN/SKILL', help='既存プラグインにスキルディレクトリを追加')

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
        print(f"\n📁 スキルディレクトリ追加: {plugin_name}/{skill_name}")
        add_skill(str(output_dir), plugin_name, skill_name)
        print("\n完了: ディレクトリ作成")
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

    print(f"\n{'='*50}")
    print(f"✅ スキャフォールド完了！ {total_files} ファイル作成")
    print(f"\n次のステップ:")
    if not args.plugin:
        print(f"  1. プラグインを追加: python scripts/scaffold.py {output_dir} --add-plugin <name>")
    else:
        print(f"  1. skills/ 内にスキルディレクトリを作成")
        print(f"  2. SKILL.md を作成（YAML フロントマター + 本文）")


if __name__ == "__main__":
    main()
