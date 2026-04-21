# d-market-skill

Claude Code Skills Marketplace。複数のプラグインを管理するリポジトリ。

## バージョン管理ルール

プラグインの内容（SKILL.md、agents/、references/、templates/、scripts/、hooks/など）を変更した場合、以下の2箇所のバージョンを更新すること:

1. **plugin.json** — 該当プラグインの `"version"` フィールド
2. **marketplace.json** — `.claude-plugin/marketplace.json` 内の該当プラグインエントリの `"version"` フィールド

semverに従う:
- 破壊的変更（スキーマ変更、既存フィールド削除など） → メジャー
- 機能追加（新しいステップ、新しいスキーマ、新しいエージェント指示など） → マイナー
- バグ修正、文言修正、軽微な改善 → パッチ
