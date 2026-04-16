---
name: command-logger
description: "Claude Codeのhooksを使って、セッション中にユーザーに承認が求められたコマンド（Bash, Edit, Write等）をセッション別のJSONLファイルに自動記録するスキル。PermissionRequestフックにより、承認ダイアログが表示されたコマンドのみを記録する。記録されたコマンドログは新しいスキル作成の素材として活用できる。Skillを自動的に成長させるための基盤。「承認コマンドを記録」「コマンドログを取りたい」「実行したコマンドを保存」「セッションのコマンド履歴」「スキル作成用にコマンドを収集」「hooks設定でコマンド記録」「approved commands logger」「command history hook」「スキルを成長させたい」などのキーワードでトリガー。"
hooks:
  PermissionRequest:
    - matcher: "Bash|Edit|Write"
      hooks:
        - type: command
          command: "./scripts/save-approved-commands.sh"
---

# Command Logger

セッション中にユーザーに承認が求められたコマンドをセッション別ファイルに自動記録する。

---

## 概要

PermissionRequestフックを利用して、承認ダイアログが表示されたタイミングでコマンド情報をJSONL形式で記録する。自動承認されたコマンドは記録されず、ユーザーに承認を求めたコマンドのみが対象となる。

セッションIDごとにファイルが分かれるため、後からセッション単位でコマンドを振り返れる。

**用途:** 記録されたコマンドから繰り返しパターンを発見し、新しいスキルの素材にする。

---

## 動作の仕組み

1. Claudeがツール（Bash, Edit, Write等）を実行しようとする
2. 権限が必要な場合、PermissionRequestイベントが発火
3. 同梱の `scripts/save-approved-commands.sh` がコマンド情報を記録
4. スクリプトは `exit 0` で終了し、通常の承認ダイアログがそのまま表示される

スクリプトは記録のみ行い、権限判定には一切介入しない。

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
