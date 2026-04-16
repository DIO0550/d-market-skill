---
name: command-logger
description: "Claude Codeのhooksを使って、セッション中に実行されたコマンド（Bash, Edit, Write等）をセッション別のJSONLファイルに自動記録するスキル。記録されたコマンドログは新しいスキル作成の素材として活用できる。Skillを自動的に成長させるための基盤。「承認コマンドを記録」「コマンドログを取りたい」「実行したコマンドを保存」「セッションのコマンド履歴」「スキル作成用にコマンドを収集」「hooks設定でコマンド記録」「approved commands logger」「command history hook」「スキルを成長させたい」などのキーワードでトリガー。"
---

# Command Logger

セッション中に実行されたコマンドをセッション別ファイルに自動記録する。

---

## 概要

PostToolUseフックを利用して、Bash・Edit・Write等のツール実行後にコマンド情報をJSONL形式で記録する。セッションIDごとにファイルが分かれるため、後からセッション単位でコマンドを振り返れる。

**用途:** 記録されたコマンドから繰り返しパターンを発見し、新しいスキルの素材にする。

---

## フックスクリプト

同梱の `scripts/save-approved-commands.sh` がPostToolUseフックとして動作する。

対象のプロジェクトの `.claude/settings.json` に以下のhooks設定を追加する:

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

---

## 記録先

```
<project-root>/.claude/plugin-data/approved-commands/<session-id>.jsonl
```

`.gitignore` にログディレクトリを追加する:

```
.claude/plugin-data/
```

---

## 記録フォーマット

各行はJSON形式:

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

## ログの活用

記録されたJSONLファイルから頻出パターンを分析し、スキル化の候補を特定する:

```bash
# 特定セッションのBashコマンドのみ抽出
jq -r 'select(.tool == "Bash") | .command' .claude/plugin-data/approved-commands/<session-id>.jsonl

# 全セッションで頻出するコマンドを集計
cat .claude/plugin-data/approved-commands/*.jsonl | jq -r 'select(.tool == "Bash") | .command' | sort | uniq -c | sort -rn | head -20
```

---

## 前提条件

- `jq` がインストールされていること（スクリプト内でJSON処理に使用）
