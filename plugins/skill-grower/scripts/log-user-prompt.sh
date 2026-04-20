#!/bin/bash
# log-user-prompt.sh
# UserPromptSubmit フックで、ユーザーの発言を記録する。
# 発言内容の加工はせず、そのまま保存する（sanitize や解析は skill 側の責務）。

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
SESSION_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/plugin-workspace/sessions/${SAFE_SESSION_ID}"
mkdir -p "$SESSION_DIR"

LOG_FILE="${SESSION_DIR}/user-prompts.jsonl"

# もらった値にタイムスタンプだけ足してそのまま書き出す
echo "$INPUT" | jq -c --arg ts "$TIMESTAMP" '. + {timestamp: $ts}' >> "$LOG_FILE"

exit 0
