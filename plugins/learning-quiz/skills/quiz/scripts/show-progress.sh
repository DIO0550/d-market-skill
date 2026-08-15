#!/bin/bash
# show-progress.sh [トピック (省略時: 全体)]
# progress.json から進捗サマリを集計して表示する。
# 進捗の数値はこのスクリプトの出力をそのまま使い、モデル側で再計算しないこと。
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ensure_workspace

TOPIC="${1:-}"

python3 - "$QUESTIONS_FILE" "$PROGRESS_FILE" "$TOPIC" <<'PY'
import json, sys
from collections import defaultdict

questions_file, progress_file, topic_filter = sys.argv[1], sys.argv[2], sys.argv[3]
questions = json.load(open(questions_file))
progress = json.load(open(progress_file))

if topic_filter:
    questions = [q for q in questions if q["topic"] == topic_filter]

if not questions:
    scope = f"トピック '{topic_filter}' の" if topic_filter else ""
    sys.exit(f"{scope}問題がバンクにありません。")

MASTERY_STREAK = 3
by_topic = defaultdict(lambda: {"total": 0, "attempted": 0, "correct": 0, "attempts": 0, "mastered": 0})
weak = []

for q in questions:
    t = by_topic[q["topic"]]
    t["total"] += 1
    p = progress.get(q["id"])
    if not p:
        continue
    t["attempted"] += 1
    t["correct"] += p["correct"]
    t["attempts"] += p["attempts"]
    if p["streak"] >= MASTERY_STREAK:
        t["mastered"] += 1
    accuracy = p["correct"] / p["attempts"]
    if p["attempts"] >= 2 and accuracy < 0.6:
        weak.append((q["topic"], q["id"], q["question"], round(accuracy * 100), p["attempts"]))

total = sum(t["total"] for t in by_topic.values())
attempted = sum(t["attempted"] for t in by_topic.values())
attempts = sum(t["attempts"] for t in by_topic.values())
correct = sum(t["correct"] for t in by_topic.values())
mastered = sum(t["mastered"] for t in by_topic.values())

print("## 進捗サマリ")
print(f"- 問題数: {total} / 着手済み: {attempted} ({round(attempted/total*100)}%) / 習熟済み(連続{MASTERY_STREAK}回正解): {mastered}")
if attempts:
    print(f"- 総回答数: {attempts} / 正答率: {round(correct/attempts*100)}%")
else:
    print("- まだ回答履歴がありません")

print()
print("| トピック | 問題数 | 着手 | 習熟 | 正答率 |")
print("|---|---|---|---|---|")
for name, t in sorted(by_topic.items()):
    acc = f"{round(t['correct']/t['attempts']*100)}%" if t["attempts"] else "-"
    print(f"| {name} | {t['total']} | {t['attempted']} | {t['mastered']} | {acc} |")

if weak:
    print()
    print("## 苦手問題（正答率60%未満・2回以上回答）")
    for topic, qid, question, acc, n in sorted(weak, key=lambda w: w[3]):
        print(f"- [{topic}] {question} (id: {qid}, 正答率 {acc}%, {n}回)")
PY
