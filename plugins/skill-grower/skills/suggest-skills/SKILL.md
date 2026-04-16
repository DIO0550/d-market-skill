---
name: suggest-skills
description: "PermissionRequestフックで記録された承認コマンドログ（.claude/plugin-data/approved-commands/*.jsonl）を分析し、新しいスキルの候補を提案するスキル。繰り返し承認しているコマンドパターンを検出し、スキル化すべきワークフローを具体的に提案する。「おすすめスキル」「スキル提案」「どんなスキルを作るべき？」「コマンドログを分析」「承認パターンを確認」「スキルを成長させたい」「suggest skills」「skill recommendation」「analyze commands」などのキーワードでトリガー。コマンドログが存在するプロジェクトで積極的に使用すること。"
---

# Suggest Skills

承認コマンドログを分析し、スキル化すべきワークフローを提案する。

---

## ワークフロー

### Step 1: ログの読み込み

`.claude/plugin-data/approved-commands/` 配下のJSONLファイルを全て読み込む。

ファイルが存在しない場合は、まだコマンドが記録されていない旨を伝え、プラグインのhooksが有効になっているか確認を促す。

### Step 2: パターン分析

読み込んだログから以下の観点で分析する:

1. **頻出コマンド**: 複数セッションで繰り返し承認されている同一・類似コマンド
2. **コマンドの連鎖**: 毎回同じ順序で承認されるコマンド群（ワークフロー）
3. **ツール別の傾向**: Bash / Edit / Write それぞれの利用パターン
4. **プロジェクト固有の操作**: そのプロジェクト特有の繰り返し作業

### Step 3: スキル候補の提案

分析結果を元に、具体的なスキル候補を提案する。各提案には以下を含める:

- **スキル名**: kebab-caseの具体的な名前
- **解決する課題**: 毎回承認している手間が何か
- **スキルの内容**: そのスキルが何をするか
- **根拠**: どのコマンドパターンから導出したか（実データを引用）
- **優先度**: 頻度と手間から判断した優先度（高/中/低）

### Step 4: ユーザーと対話

提案を見せた上で:
- 「このスキルを作りますか？」と聞く
- ユーザーが選んだスキルについて詳細設計に進む
- skill-creator プラグインがあればそちらと連携してスキルを作成する

---

## ログのフォーマット

各JSONLファイルの行はPermissionRequestフックの入力にタイムスタンプを付与したもの:

```json
{
  "session_id": "abc123",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {"command": "npm install express", "description": "Install express"},
  "permission_mode": "default",
  "cwd": "/home/user/my-project",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 提案の出力例

```
## スキル候補

### 1. run-tests（優先度: 高）
- 課題: `npm test` を毎セッション平均3回承認している
- 内容: テスト実行を自動承認するhooksルール、またはテスト実行＋結果確認のワークフロースキル
- 根拠: 12セッションで計38回の `npm test` 承認を検出

### 2. lint-and-format（優先度: 中）
- 課題: `eslint --fix` → `prettier --write` の連鎖を毎回手動承認
- 内容: lint＋format を一括実行するスキル
- 根拠: 8セッションで同一パターンを検出
```

---

## 前提条件

- `.claude/plugin-data/approved-commands/` にログが存在すること
- `jq` がインストールされていること（ログ解析に使用）
