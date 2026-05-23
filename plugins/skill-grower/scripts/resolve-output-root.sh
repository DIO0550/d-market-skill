#!/bin/bash
# resolve-output-root.sh
# source して使う。OUTPUT_ROOT にメインワークツリーのルートをセットする。
# git worktree 内では CLAUDE_PROJECT_DIR がワークツリーを指すため、
# メインワークツリーに解決してセッションデータの消失を防ぐ。

OUTPUT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

if command -v git >/dev/null 2>&1; then
  _main_worktree=$(git -C "${CLAUDE_PROJECT_DIR:-.}" worktree list --porcelain 2>/dev/null | head -1 | sed 's/^worktree //')
  if [ -n "$_main_worktree" ]; then
    OUTPUT_ROOT="$_main_worktree"
  fi
  unset _main_worktree
fi
