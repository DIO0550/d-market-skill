---
name: suggest-skills
description: "PermissionRequestフックで記録された承認コマンドログ（.claude/plugin-workspace/sessions/*/approved-commands.jsonl）を分析し、新しいスキルの候補を提案するスキル。繰り返し承認しているコマンドパターンを検出し、スキル化すべきワークフローを具体的に提案する。「おすすめスキル」「スキル提案」「どんなスキルを作るべき？」「コマンドログを分析」「承認パターンを確認」「スキルを成長させたい」「suggest skills」「skill recommendation」「analyze commands」などのキーワードでトリガー。コマンドログが存在するプロジェクトで積極的に使用すること。"
disable-model-invocation: true
---

# Suggest Skills

承認コマンドログを分析し、スキル化すべきワークフローを提案する。

---

## データソース

`${CLAUDE_PROJECT_DIR}/.claude/plugin-workspace/sessions/<session_id>/approved-commands.jsonl`

各JSONLファイルはPermissionRequestフックの入力にtimestampを付与したもの。1行1イベント。

---

## ワークフロー

### Step 1: ログの読み込み

`.claude/plugin-workspace/sessions/` 配下の全 `approved-commands.jsonl` を列挙して読み込む:

```bash
find .claude/plugin-workspace/sessions -name approved-commands.jsonl
```

**ログが存在しない場合の扱い:**
- ディレクトリが存在しない、または JSONL が 0 件の場合は分析せず、hooks が有効になっているか確認を促して終了する
- 対象セッション数が 3 未満の場合は「サンプルが少ないため提案の精度は低い」と明示した上で続行する

### Step 2: パターン分析

読み込んだログから以下の観点で分析する。**各観点の結果は独立に集計し、Step 3 で重みを付けて統合する。**

#### 2-1. 頻出コマンド
- `tool_name` ごとに `tool_input.command` または `tool_input.file_path` を抽出
- **コマンドの正規化**: 以下のルールで等価コマンドを同一視する
  - サブコマンドまで一致すれば同一視 (`npm test` と `npm test -- --watch` は同一)
  - 引数のパス・数値・URL は `<path>` `<num>` `<url>` にマスクして集計
  - `sudo` 等の接頭辞は除去して比較
- 出現回数と出現セッション数 (unique session count) の両方を記録

#### 2-2. コマンドの連鎖
- 同一セッション内で連続して (timestamp 順で隣接して) 承認されたコマンドの 2-gram / 3-gram を抽出
- 複数セッションに跨って繰り返される連鎖を優先する

#### 2-3. ツール別の傾向
- Bash / Edit / Write のどれが多いか、特定作業でどのツール組み合わせが使われるか

#### 2-4. プロジェクト固有の操作
- `cwd` に関係なく繰り返される操作 (汎用) と、特定 `cwd` でのみ発生する操作 (プロジェクト固有) を区別する

### Step 3: スキル候補の提案

分析結果を元に、具体的なスキル候補を提案する。

**優先度の算出ルール:**
- **高**: 3 セッション以上 かつ 合計 10 回以上の出現
- **中**: 2 セッション以上 かつ 合計 5 回以上の出現
- **低**: それ未満だが構造的に繰り返しパターンと判断できるもの

各提案には以下を含める:

- **スキル名**: kebab-case の具体的な名前
- **解決する課題**: 毎回承認している手間が何か
- **スキルの内容**: そのスキルが何をするか
- **根拠**: どのコマンドパターンから導出したか (session_id と出現回数、代表例 1-2 行を引用)
- **優先度**: 上記ルールに従って付与

### Step 4: ユーザーと対話

提案を見せた上で:
- 「このスキルを作りますか？」と聞く
- ユーザーが選んだスキルについて詳細設計に進む
- skill-creator プラグインがあればそちらと連携してスキルを作成する

---

## ログのフォーマット

各JSONLファイルの行例:

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

## 提案の出力例

```
## スキル候補

### 1. run-tests（優先度: 高）
- 課題: `npm test` を毎セッション平均3回承認している
- 内容: テスト実行を自動承認するhooksルール、またはテスト実行＋結果確認のワークフロースキル
- 根拠: 12セッションで計38回の `npm test` 承認を検出 (session abc123, def456, ...)

### 2. lint-and-format（優先度: 中）
- 課題: `eslint --fix` → `prettier --write` の連鎖を毎回手動承認
- 内容: lint＋format を一括実行するスキル
- 根拠: 8セッションで同一 2-gram を検出
```

---

## 前提条件

- `.claude/plugin-workspace/sessions/<id>/approved-commands.jsonl` にログが存在すること
- `jq` がインストールされていること (JSONL 解析に使用)

## セキュリティ上の注意

`tool_input.command` には API キー・token・パスワードなどが含まれる可能性がある。
出力例として引用する際は、以下のパターンを `[REDACTED]` に置換すること:
- `Bearer\s+\S+` / `token[=:]\s*\S+` / `password[=:]\s*\S+`
- `ghp_[A-Za-z0-9]+` / `sk-[A-Za-z0-9]+` 等の典型的な API キー形式
- `.env` ファイルの内容を cat した結果

検出時はユーザーに「ログに機密情報が含まれている可能性がある」と警告する。
