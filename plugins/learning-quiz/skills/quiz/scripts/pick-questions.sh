#!/bin/bash
# pick-questions.sh [出題数 (default: 5)] [トピック (省略時: 全トピック)]
# 進捗を踏まえて次に出題すべき問題を選び、JSON配列で出力する。
# 優先順位: 未出題 → 苦手（連続正解が少ない・正答率が低い）→ 最後に解いてから時間が経ったもの。
# 習熟済み（連続3回以上正解）は後回しにする。
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ensure_workspace

COUNT="${1:-5}"
TOPIC="${2:-}"

python3 - "$QUESTIONS_FILE" "$PROGRESS_FILE" "$COUNT" "$TOPIC" <<'PY'
import json, sys

questions_file, progress_file, count, topic = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
questions = json.load(open(questions_file))
progress = json.load(open(progress_file))

if topic:
    questions = [q for q in questions if q["topic"] == topic]

if not questions:
    scope = f"トピック '{topic}' の" if topic else ""
    sys.exit(f"error: {scope}問題がバンクにありません。先に問題を生成してください。")

MASTERY_STREAK = 3

def sort_key(q):
    p = progress.get(q["id"])
    if p is None:
        # 未出題を最優先。バンク登録順で安定させる
        return (0, 0, 0, "")
    accuracy = p["correct"] / p["attempts"] if p["attempts"] else 0
    mastered = 1 if p["streak"] >= MASTERY_STREAK else 0
    return (1 + mastered, p["streak"], accuracy, p.get("last_answered_at", ""))

selected = sorted(questions, key=sort_key)[:count]
print(json.dumps(selected, ensure_ascii=False, indent=2))
PY
