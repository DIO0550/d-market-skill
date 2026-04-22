#!/bin/bash
# log-skill-invocation.sh
# PostToolUse フックで、Skill ツールの発火を記録する。
# ユーザー明示呼び出し・Claude 自動発火の両方をキャプチャする。

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
SESSION_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/plugin-workspace/sessions/${SAFE_SESSION_ID}"
mkdir -p "$SESSION_DIR"

LOG_FILE="${SESSION_DIR}/skill-invocations.jsonl"

echo "$INPUT" | jq -c --arg ts "$TIMESTAMP" '. + {timestamp: $ts}' >> "$LOG_FILE"

exit 0
