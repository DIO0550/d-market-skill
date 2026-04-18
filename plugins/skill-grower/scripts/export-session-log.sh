#!/bin/bash
# export-session-log.sh
# Stop フックで、セッション中のやり取り・使用コマンドをファイルに書き出すようAIに指示する。
# stdoutに出力した内容がAIへの指示となり、AIがログを生成する。

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
# hook 実行時のプロジェクトルート。CLAUDE_PROJECT_DIR は環境変数として
# 保証されないため、stdin JSON の .cwd を優先して使う。
PROJECT_DIR=$(echo "$INPUT" | jq -r '.cwd // empty')
if [ -z "$PROJECT_DIR" ]; then
  PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
fi
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE_STR=$(date -u +"%Y%m%d_%H%M%S")

LOG_DIR="${PROJECT_DIR}/.claude/plugin-workspace/session-logs"
SAFE_SESSION_ID=$(echo "$SESSION_ID" | sed 's/[^a-zA-Z0-9_-]/_/g')
LOG_FILE="${LOG_DIR}/${DATE_STR}_${SAFE_SESSION_ID}.md"

cat <<EOF
[Session Export Hook] セッションログを書き出してください。

以下の手順で、今回のセッション内容をファイルに記録してください:

1. ディレクトリ \`${LOG_DIR}\` を作成する（存在しない場合）
2. ファイル \`${LOG_FILE}\` に以下のMarkdown形式で書き出す:

---

# Session Log

- **Session ID**: ${SESSION_ID}
- **Timestamp**: ${TIMESTAMP}

## 目的・概要
今回のセッションで何を目的に作業したかを1-3文で要約。

## 使用したツール・コマンド
今回実行した主なツール（Bash, Edit, Write, Read, Grep, Glob等）とその内容を箇条書きで記録。
具体的なコマンドやファイルパスを含めること。

## やり取りの流れ
ユーザーからの依頼内容と、それに対して行った作業の流れを時系列で簡潔に記録。

## 繰り返しパターン・注目点
セッション中に繰り返し行った操作や、スキル化できそうなパターンがあれば記録。

---

3. 書き出しが完了したら、書き出したファイルパスをユーザーに伝える。
4. 簡潔に完了報告する（長い説明は不要）。
EOF

exit 0
