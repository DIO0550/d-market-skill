#!/bin/bash
# save-approved-commands.sh
# PostToolUse フックで実行されたコマンド系ツールをセッション別ファイルに記録する。
# 記録されたコマンドは、新しいスキル作成の素材として活用できる。

set -euo pipefail

# stdin から JSON を読み取る
INPUT=$(cat)

# 必要なフィールドを抽出
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
TOOL_INPUT=$(echo "$INPUT" | jq -c '.tool_input // {}')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# ログ出力先ディレクトリ
LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/plugin-data/approved-commands"
mkdir -p "$LOG_DIR"

# セッションIDからファイル名を生成（安全な文字のみ）
SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE="${LOG_DIR}/${SAFE_SESSION_ID}.jsonl"

# ツール種別に応じてコマンド情報を抽出
case "$TOOL_NAME" in
  Bash)
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // ""')
    ;;
  Edit)
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // ""')
    COMMAND="[Edit] ${FILE_PATH}"
    ;;
  Write)
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // ""')
    COMMAND="[Write] ${FILE_PATH}"
    ;;
  *)
    COMMAND="[${TOOL_NAME}] $(echo "$TOOL_INPUT" | jq -c '.')"
    ;;
esac

# JSONL 形式で追記
jq -n -c \
  --arg ts "$TIMESTAMP" \
  --arg session "$SESSION_ID" \
  --arg tool "$TOOL_NAME" \
  --arg cmd "$COMMAND" \
  --argjson input "$TOOL_INPUT" \
  '{timestamp: $ts, session: $session, tool: $tool, command: $cmd, input: $input}' \
  >> "$LOG_FILE"

exit 0
