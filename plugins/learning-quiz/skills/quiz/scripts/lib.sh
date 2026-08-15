#!/bin/bash
# lib.sh
# source して使う共通ヘルパー。QUIZ_DIR にクイズワークスペースの絶対パスをセットする。
# git worktree 内では CLAUDE_PROJECT_DIR がワークツリーを指すため、
# メインワークツリーに解決して進捗データの消失を防ぐ（skill-grower と同方式）。

OUTPUT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

if command -v git >/dev/null 2>&1; then
  _main_worktree=$(git -C "${CLAUDE_PROJECT_DIR:-.}" worktree list --porcelain 2>/dev/null | head -1 | sed 's/^worktree //')
  if [ -n "$_main_worktree" ]; then
    OUTPUT_ROOT="$_main_worktree"
  fi
  unset _main_worktree
fi

QUIZ_DIR="$OUTPUT_ROOT/.claude/plugin-workspace/quiz"
QUESTIONS_FILE="$QUIZ_DIR/questions.json"
PROGRESS_FILE="$QUIZ_DIR/progress.json"
HISTORY_FILE="$QUIZ_DIR/history.jsonl"
INCOMING_DIR="$QUIZ_DIR/incoming"

ensure_workspace() {
  mkdir -p "$QUIZ_DIR" "$INCOMING_DIR"
  [ -f "$QUESTIONS_FILE" ] || echo "[]" > "$QUESTIONS_FILE"
  [ -f "$PROGRESS_FILE" ] || echo "{}" > "$PROGRESS_FILE"
  [ -f "$HISTORY_FILE" ] || : > "$HISTORY_FILE"
}
