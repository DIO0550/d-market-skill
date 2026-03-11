#!/usr/bin/env python3
"""
Skill Validator - SKILL.md のバリデーションとベストプラクティスチェック

Usage:
    python scripts/quick_validate.py <skill_directory>

公式ドキュメントの制約とベストプラクティスに基づく検証：
- YAML フロントマターの必須フィールドと形式
- name/description の制約チェック
- SKILL.md 本文の行数チェック
- ファイル構成のベストプラクティスチェック
"""

import sys
import os
import re
import yaml
from pathlib import Path


def validate_skill(skill_path):
    """スキルの包括的なバリデーション"""
    skill_path = Path(skill_path)
    errors = []
    warnings = []

    # === 必須チェック ===

    # SKILL.md の存在
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, ["SKILL.md が見つかりません"], []

    content = skill_md.read_text(encoding='utf-8')

    # YAML フロントマターの存在
    if not content.startswith('---'):
        return False, ["YAML フロントマターがありません（---で開始する必要があります）"], []

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, ["YAML フロントマターの形式が不正です"], []

    # YAML パース
    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, ["フロントマターは YAML 辞書である必要があります"], []
    except yaml.YAMLError as e:
        return False, [f"YAML パースエラー: {e}"], []

    # 許可されたプロパティ
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        errors.append(
            f"不明なキー: {', '.join(sorted(unexpected_keys))}。"
            f"許可されたキー: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # === name フィールド ===

    if 'name' not in frontmatter:
        errors.append("'name' フィールドが必須です")
    else:
        name = frontmatter['name']
        if not isinstance(name, str):
            errors.append(f"name は文字列である必要があります（{type(name).__name__} が指定されました）")
        else:
            name = name.strip()
            if not name:
                errors.append("name は空にできません")
            elif len(name) > 64:
                errors.append(f"name が長すぎます（{len(name)}文字）。最大64文字です")
            elif not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"name '{name}' は小文字・数字・ハイフンのみ使用可能です")
            elif name.startswith('-') or name.endswith('-') or '--' in name:
                errors.append(f"name '{name}' はハイフンで開始/終了できず、連続ハイフンも使用できません")

            # 予約語チェック
            reserved = ['anthropic', 'claude']
            for word in reserved:
                if word in name.lower():
                    errors.append(f"name に予約語 '{word}' を含めることはできません")

            # XMLタグチェック
            if '<' in name or '>' in name:
                errors.append("name に XML タグ（< >）を含めることはできません")

    # === description フィールド ===

    if 'description' not in frontmatter:
        errors.append("'description' フィールドが必須です")
    else:
        desc = frontmatter['description']
        if not isinstance(desc, str):
            errors.append(f"description は文字列である必要があります（{type(desc).__name__} が指定されました）")
        else:
            desc = desc.strip()
            if not desc:
                errors.append("description は空にできません")
            elif len(desc) > 1024:
                errors.append(f"description が長すぎます（{len(desc)}文字）。最大1024文字です")

            if '<' in desc or '>' in desc:
                errors.append("description に XML タグ（< >）を含めることはできません")

            # ベストプラクティスの警告
            if len(desc) < 50:
                warnings.append("description が短すぎる可能性があります。何をするか＋いつ使うかの両方を含めてください")

            # 一人称チェック
            first_person = ['I can', 'I will', 'I help', '私は', '私が']
            for phrase in first_person:
                if phrase in desc:
                    warnings.append(f"description は三人称で記述してください（'{phrase}' を検出）")
                    break

    # === SKILL.md 本文のチェック ===

    body = content[match.end():]
    body_lines = body.strip().split('\n')
    line_count = len(body_lines)

    if line_count > 500:
        warnings.append(
            f"SKILL.md 本文が {line_count} 行あります（推奨: 500行以内）。"
            "詳細を別ファイルに分離することを検討してください"
        )
    elif line_count > 400:
        warnings.append(
            f"SKILL.md 本文が {line_count} 行あります。500行の上限に近づいています"
        )

    if not body.strip():
        warnings.append("SKILL.md 本文が空です")

    # === ファイル構成チェック ===

    # 参照ファイルの深さチェック
    for ref_file in skill_path.rglob('*.md'):
        if ref_file.name == 'SKILL.md':
            continue
        rel = ref_file.relative_to(skill_path)
        if len(rel.parts) > 2:
            warnings.append(
                f"参照ファイル '{rel}' が深い階層にあります。"
                "SKILL.md から1階層のみの参照を推奨します"
            )

    # Windows パスチェック
    if '\\' in content:
        warnings.append("SKILL.md に Windows パス区切り（\\）が含まれています。/ を使用してください")

    # スクリプトの実行権限チェック
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.py'):
            if not os.access(script, os.R_OK):
                warnings.append(f"スクリプト '{script.name}' に読み取り権限がありません")

    # === 結果 ===

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def print_results(is_valid, errors, warnings, skill_path):
    """結果を見やすく出力"""
    print(f"\n{'='*60}")
    print(f"  Skill Validation: {skill_path}")
    print(f"{'='*60}\n")

    if errors:
        print("❌ エラー（修正必須）:")
        for i, err in enumerate(errors, 1):
            print(f"   {i}. {err}")
        print()

    if warnings:
        print("⚠️  警告（改善推奨）:")
        for i, warn in enumerate(warnings, 1):
            print(f"   {i}. {warn}")
        print()

    if is_valid:
        if warnings:
            print("✅ バリデーション通過（警告あり）")
        else:
            print("✅ バリデーション通過！")
    else:
        print("❌ バリデーション失敗 — エラーを修正してください")

    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/quick_validate.py <skill_directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    is_valid, errors, warnings = validate_skill(skill_path)
    print_results(is_valid, errors, warnings, skill_path)
    sys.exit(0 if is_valid else 1)
