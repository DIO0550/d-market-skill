#!/bin/bash
# add-questions.sh <生成済み問題のJSONファイル>
# サブエージェントが生成した問題（JSON配列）を検証して問題バンクにマージする。
# IDは問題文のハッシュから自動採番し、問題文の重複はスキップする。
set -eu

if [ $# -lt 1 ] || [ ! -f "$1" ]; then
  echo "usage: add-questions.sh <questions.json (array)>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$SCRIPT_DIR/lib.sh"

ensure_workspace

python3 - "$1" "$QUESTIONS_FILE" <<'PY'
import hashlib, json, re, sys

incoming_file, bank_file = sys.argv[1], sys.argv[2]

try:
    incoming = json.load(open(incoming_file))
except json.JSONDecodeError as e:
    sys.exit(f"error: {incoming_file} は妥当なJSONではありません: {e}")
if not isinstance(incoming, list):
    sys.exit("error: 入力はJSON配列である必要があります")

bank = json.load(open(bank_file))

def norm(text):
    return re.sub(r"\s+", "", text.lower())

existing = {norm(q["question"]) for q in bank}
added, skipped, errors = 0, 0, []

VALID_TYPES = {"multiple_choice", "free_text"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}

for i, q in enumerate(incoming):
    missing = [k for k in ("topic", "question", "answer", "explanation") if not q.get(k)]
    if missing:
        errors.append(f"[{i}] 必須フィールド欠落: {missing}")
        continue
    qtype = q.get("type", "multiple_choice")
    if qtype not in VALID_TYPES:
        errors.append(f"[{i}] 不正なtype: {qtype}")
        continue
    if qtype == "multiple_choice":
        choices = q.get("choices")
        if not isinstance(choices, list) or len(choices) < 2:
            errors.append(f"[{i}] multiple_choiceにはchoices（2件以上の配列）が必要")
            continue
        if q["answer"] not in choices:
            errors.append(f"[{i}] answerがchoicesに含まれていない: {q['answer']!r}")
            continue
    difficulty = q.get("difficulty", "medium")
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = "medium"

    key = norm(q["question"])
    if key in existing:
        skipped += 1
        continue
    existing.add(key)

    digest = hashlib.sha1(q["question"].encode()).hexdigest()[:8]
    slug = re.sub(r"[^a-z0-9]+", "-", q["topic"].lower()).strip("-") or "general"
    bank.append({
        "id": f"{slug}-{digest}",
        "topic": q["topic"],
        "type": qtype,
        "difficulty": difficulty,
        "question": q["question"],
        "choices": q.get("choices"),
        "answer": q["answer"],
        "explanation": q["explanation"],
        "source": q.get("source"),
    })
    added += 1

with open(bank_file, "w") as f:
    json.dump(bank, f, ensure_ascii=False, indent=2)

print(f"added: {added}, skipped(duplicate): {skipped}, invalid: {len(errors)}, bank_total: {len(bank)}")
for e in errors:
    print(f"  invalid {e}")
PY
