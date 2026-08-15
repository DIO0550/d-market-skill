#!/bin/bash
# record-answer.sh <question_id> <correct|incorrect>
# 1問分の回答結果を progress.json に記録し、history.jsonl に追記する。
# 出題のたびに必ず呼ぶこと。これを呼ばない限り進捗は一切保存されない。
set -eu

if [ $# -lt 2 ]; then
  echo "usage: record-answer.sh <question_id> <correct|incorrect>" >&2
  exit 1
fi
case "$2" in
  correct|incorrect) ;;
  *) echo "error: 第2引数は correct か incorrect" >&2; exit 1 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ensure_workspace

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

python3 - "$QUESTIONS_FILE" "$PROGRESS_FILE" "$HISTORY_FILE" "$1" "$2" "$TS" <<'PY'
import json, sys

questions_file, progress_file, history_file, qid, result, ts = sys.argv[1:7]

questions = json.load(open(questions_file))
if not any(q["id"] == qid for q in questions):
    sys.exit(f"error: 問題ID '{qid}' がバンクに存在しません。pick-questions.sh の出力のidを使ってください。")

progress = json.load(open(progress_file))
entry = progress.get(qid, {"attempts": 0, "correct": 0, "streak": 0})
entry["attempts"] += 1
if result == "correct":
    entry["correct"] += 1
    entry["streak"] += 1
else:
    entry["streak"] = 0
entry["last_result"] = result
entry["last_answered_at"] = ts
progress[qid] = entry

with open(progress_file, "w") as f:
    json.dump(progress, f, ensure_ascii=False, indent=2)
with open(history_file, "a") as f:
    f.write(json.dumps({"ts": ts, "question_id": qid, "result": result}, ensure_ascii=False) + "\n")

accuracy = round(entry["correct"] / entry["attempts"] * 100)
print(f"recorded: {qid} -> {result} (attempts: {entry['attempts']}, accuracy: {accuracy}%, streak: {entry['streak']})")
PY
