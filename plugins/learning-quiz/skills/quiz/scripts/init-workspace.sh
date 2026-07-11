#!/bin/bash
# init-workspace.sh
# クイズワークスペースを初期化し、パスと問題バンクの現状を表示する。
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ensure_workspace

python3 - "$QUESTIONS_FILE" "$PROGRESS_FILE" "$QUIZ_DIR" <<'PY'
import json, sys
from collections import Counter

questions_file, progress_file, quiz_dir = sys.argv[1], sys.argv[2], sys.argv[3]
questions = json.load(open(questions_file))
progress = json.load(open(progress_file))

topics = Counter(q["topic"] for q in questions)
attempted = sum(1 for q in questions if q["id"] in progress)

print(f"workspace: {quiz_dir}")
print(f"questions: {len(questions)} (attempted: {attempted})")
if topics:
    print("topics:")
    for topic, count in sorted(topics.items()):
        print(f"  - {topic}: {count}")
else:
    print("topics: (empty — 問題バンクが空です。問題生成から始めてください)")
PY
