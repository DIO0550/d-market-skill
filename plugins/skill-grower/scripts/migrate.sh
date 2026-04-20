#!/bin/bash
# migrate.sh
# 旧構造 (v1.x) から新構造 (sessions/<session_id>/) へのマイグレーション。
#
# 旧:
#   .claude/plugin-workspace/approved-commands/<session_id>.jsonl
#   .claude/plugin-workspace/session-logs/<timestamp>_<session_id>.md
# 新:
#   .claude/plugin-workspace/sessions/<session_id>/approved-commands.jsonl
#   .claude/plugin-workspace/sessions/<session_id>/session-log.md
#
# 使い方: migrate.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
  echo "[DRY RUN] 変更は行わず、実行予定の操作のみ表示します。"
fi

WORKSPACE="${CLAUDE_PROJECT_DIR:-.}/.claude/plugin-workspace"
OLD_CMD_DIR="${WORKSPACE}/approved-commands"
OLD_LOG_DIR="${WORKSPACE}/session-logs"
NEW_SESSIONS_DIR="${WORKSPACE}/sessions"

if [ ! -d "$OLD_CMD_DIR" ] && [ ! -d "$OLD_LOG_DIR" ]; then
  echo "旧構造のディレクトリが見つかりません。マイグレーション不要です。"
  exit 0
fi

run() {
  if [ "$DRY_RUN" = "1" ]; then
    echo "  [dry-run] $*"
  else
    eval "$@"
  fi
}

migrated=0

# approved-commands/<session_id>.jsonl → sessions/<session_id>/approved-commands.jsonl
if [ -d "$OLD_CMD_DIR" ]; then
  echo "==> approved-commands を移行..."
  shopt -s nullglob
  for src in "$OLD_CMD_DIR"/*.jsonl; do
    session_id=$(basename "$src" .jsonl)
    dst_dir="${NEW_SESSIONS_DIR}/${session_id}"
    dst="${dst_dir}/approved-commands.jsonl"
    echo "  ${src} -> ${dst}"
    run "mkdir -p \"${dst_dir}\""
    if [ -f "$dst" ]; then
      # 既に新構造側にファイルがある場合は append (ログなので重複は許容、順序は壊れる可能性あり)
      run "cat \"${src}\" >> \"${dst}\""
    else
      run "cp \"${src}\" \"${dst}\""
    fi
    migrated=$((migrated + 1))
  done
  shopt -u nullglob
fi

# session-logs/<timestamp>_<session_id>.md → sessions/<session_id>/session-log.md
# 同一 session_id に複数のログがある場合は session-log.md に連結
if [ -d "$OLD_LOG_DIR" ]; then
  echo "==> session-logs を移行..."
  shopt -s nullglob
  for src in "$OLD_LOG_DIR"/*.md; do
    base=$(basename "$src" .md)
    # <timestamp>_<session_id> から session_id を取り出す
    # timestamp は YYYYMMDD_HHMMSS 形式なので先頭2アンダースコアを除去
    session_id=$(echo "$base" | sed -E 's/^[0-9]{8}_[0-9]{6}_//')
    dst_dir="${NEW_SESSIONS_DIR}/${session_id}"
    dst="${dst_dir}/session-log.md"
    echo "  ${src} -> ${dst}"
    run "mkdir -p \"${dst_dir}\""
    if [ -f "$dst" ]; then
      run "printf '\n\n---\n\n' >> \"${dst}\""
      run "cat \"${src}\" >> \"${dst}\""
    else
      run "cp \"${src}\" \"${dst}\""
    fi
    migrated=$((migrated + 1))
  done
  shopt -u nullglob
fi

if [ "$DRY_RUN" = "0" ] && [ "$migrated" -gt 0 ]; then
  echo ""
  echo "マイグレーション完了: ${migrated} ファイル移行"
  echo ""
  echo "旧ディレクトリは残してあります。内容を確認後、手動で削除してください:"
  echo "  rm -rf \"${OLD_CMD_DIR}\" \"${OLD_LOG_DIR}\""
else
  echo ""
  echo "対象ファイル数: ${migrated}"
fi
