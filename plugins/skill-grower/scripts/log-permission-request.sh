#!/bin/bash
# log-permission-request.sh
# PermissionRequest フックで、リクエストされた内容をそのまま記録する。
# 権限判定には介入しない（exit 0で通常フローを継続）。

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/plugin-workspace/approved-commands"
mkdir -p "$LOG_DIR"

SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE="${LOG_DIR}/${SAFE_SESSION_ID}.jsonl"

# もらった値にタイムスタンプだけ足してそのまま書き出す
echo "$INPUT" | jq -c --arg ts "$TIMESTAMP" '. + {timestamp: $ts}' >> "$LOG_FILE"

exit 0
