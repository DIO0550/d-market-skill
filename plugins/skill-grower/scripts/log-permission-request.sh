#!/bin/bash
# log-permission-request.sh
# PermissionRequest フックで、リクエストされた内容をそのまま記録する。
# 権限判定には介入しない（exit 0で通常フローを継続）。

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/resolve-output-root.sh"
SESSION_DIR="${OUTPUT_ROOT}/.claude/plugin-workspace/sessions/${SAFE_SESSION_ID}"
mkdir -p "$SESSION_DIR"

LOG_FILE="${SESSION_DIR}/approved-commands.jsonl"

# もらった値にタイムスタンプだけ足してそのまま書き出す
echo "$INPUT" | jq -c --arg ts "$TIMESTAMP" '. + {timestamp: $ts}' >> "$LOG_FILE"

exit 0
