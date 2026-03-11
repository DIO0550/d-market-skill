#!/usr/bin/env python3
"""
Skill Packager - スキルフォルダを配布可能な .skill ファイルにパッケージ化

Usage:
    python scripts/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python scripts/package_skill.py /path/to/my-skill
    python scripts/package_skill.py /path/to/my-skill ./dist
"""

import fnmatch
import sys
import zipfile
from pathlib import Path

# パッケージから除外するパターン
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", ".venv", "venv"}
EXCLUDE_GLOBS = {"*.pyc", "*.pyo", "*.egg-info"}
EXCLUDE_FILES = {".DS_Store", ".gitignore", "Thumbs.db"}
ROOT_EXCLUDE_DIRS = {"evals", "workspace", "test-output"}


def should_exclude(rel_path: Path) -> bool:
    """パッケージから除外すべきパスかどうかを判定"""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def validate_basic(skill_path: Path) -> tuple:
    """基本的なバリデーション（quick_validate.pyの簡易版）"""
    import re
    import yaml

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md が見つかりません"

    content = skill_md.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return False, "YAML フロントマターがありません"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "YAML フロントマターの形式が不正です"

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, "フロントマターは YAML 辞書である必要があります"
    except yaml.YAMLError as e:
        return False, f"YAML パースエラー: {e}"

    if 'name' not in frontmatter:
        return False, "'name' フィールドが必須です"
    if 'description' not in frontmatter:
        return False, "'description' フィールドが必須です"

    name = str(frontmatter['name']).strip()
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name '{name}' は小文字・数字・ハイフンのみ使用可能です"
    if len(name) > 64:
        return False, f"name が長すぎます（{len(name)}文字、最大64）"

    desc = str(frontmatter['description']).strip()
    if len(desc) > 1024:
        return False, f"description が長すぎます（{len(desc)}文字、最大1024）"
    if '<' in desc or '>' in desc:
        return False, "description に XML タグを含めることはできません"

    return True, "バリデーション通過"


def package_skill(skill_path, output_dir=None):
    """スキルフォルダを .skill ファイルにパッケージ化"""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"❌ エラー: フォルダが見つかりません: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ エラー: ディレクトリではありません: {skill_path}")
        return None

    # バリデーション
    print("🔍 バリデーション中...")
    valid, message = validate_basic(skill_path)
    if not valid:
        print(f"❌ バリデーション失敗: {message}")
        return None
    print(f"✅ {message}\n")

    # 出力先
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # .skill ファイル作成（zip形式）
    try:
        file_count = 0
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(skill_path.rglob('*')):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"  ⏭ スキップ: {arcname}")
                    continue
                zipf.write(file_path, arcname)
                print(f"  📄 追加: {arcname}")
                file_count += 1

        print(f"\n✅ パッケージ完了: {skill_filename}")
        print(f"   ファイル数: {file_count}")
        print(f"   サイズ: {skill_filename.stat().st_size / 1024:.1f} KB")
        return skill_filename

    except Exception as e:
        print(f"❌ パッケージ作成エラー: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/package_skill.py <path/to/skill-folder> [output-directory]")
        print("\nExample:")
        print("  python scripts/package_skill.py ./my-skill")
        print("  python scripts/package_skill.py ./my-skill ./dist")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 パッケージング: {skill_path}")
    if output_dir:
        print(f"   出力先: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)
