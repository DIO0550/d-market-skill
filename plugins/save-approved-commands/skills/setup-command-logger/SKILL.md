---
name: setup-command-logger
description: "Claude Codeのhooksを使って、セッション中にユーザーが承認したコマンド（Bash, Edit, Write等）をセッション別のJSONLファイルに自動記録する設定を行うスキル。記録されたコマンドログは新しいスキル作成の素材として活用できる。「承認コマンドを記録」「コマンドログを取りたい」「実行したコマンドを保存」「セッションのコマンド履歴」「スキル作成用にコマンドを収集」「hooks設定でコマンド記録」「approved commands logger」「command history hook」などのキーワードでトリガー。"
---

# Setup Command Logger

Claude Codeのhooks機能を使い、セッション中に実行されたコマンドをセッション別ファイルに自動記録する設定を行う。

---

## 概要

PostToolUseフックを利用して、Bash・Edit・Write等のツール実行後にコマンド情報をJSONL形式で記録する。セッションIDごとにファイルが分かれるため、後からセッション単位でコマンドを振り返れる。

**用途:** 記録されたコマンドから繰り返しパターンを発見し、新しいスキルの素材にする。

---

## セットアップ手順

### Step 1: フックスクリプトの配置

このスキルに同梱されている `scripts/save-approved-commands.sh` をユーザーのプロジェクトにコピーする。

```
<project-root>/
└── .claude/
    └── hooks/
        └── save-approved-commands.sh
```

スクリプトの配置先: `<project-root>/.claude/hooks/save-approved-commands.sh`

実行権限を付与する:
```bash
chmod +x .claude/hooks/save-approved-commands.sh
```

### Step 2: settings.json にフック設定を追加

`<project-root>/.claude/settings.json` に以下を追加する。既にファイルが存在する場合はhooksキーをマージする。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/save-approved-commands.sh\""
          }
        ]
      }
    ]
  }
}
```

**matcherのカスタマイズ:** Bashコマンドのみ記録したい場合は `"matcher": "Bash"` に変更する。

### Step 3: .gitignore に記録ディレクトリを追加

コマンドログはコミットすべきでないため、`.gitignore` に追加する:

```
.claude/approved-commands/
```

### Step 4: 動作確認

設定後、新しいセッションでBashコマンドを実行すると `.claude/approved-commands/<session-id>.jsonl` にログが記録される。

---

## 記録フォーマット

各行はJSON形式で以下のフィールドを持つ:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "session": "session-abc123",
  "tool": "Bash",
  "command": "npm install express",
  "input": {"command": "npm install express"}
}
```

| フィールド | 説明 |
|-----------|------|
| timestamp | UTC タイムスタンプ |
| session | セッションID |
| tool | ツール名（Bash, Edit, Write等） |
| command | 人間が読みやすい形式のコマンド概要 |
| input | ツールへの生の入力（JSON） |

---

## ログの活用方法

記録されたJSONLファイルから頻出パターンを分析し、スキル化の候補を特定する:

```bash
# 特定セッションのBashコマンドのみ抽出
jq -r 'select(.tool == "Bash") | .command' .claude/approved-commands/<session-id>.jsonl

# 全セッションで頻出するコマンドを集計
cat .claude/approved-commands/*.jsonl | jq -r 'select(.tool == "Bash") | .command' | sort | uniq -c | sort -rn | head -20
```

---

## 前提条件

- `jq` がインストールされていること（スクリプト内でJSON処理に使用）
- Claude Codeのhooks機能が有効であること
