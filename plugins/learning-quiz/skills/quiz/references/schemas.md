# データスキーマ

ワークスペースは `.claude/plugin-workspace/quiz/`（git worktree 内で実行された場合もメインワークツリー側に解決される）。

```
.claude/plugin-workspace/quiz/
├── questions.json   # 問題バンク（配列）
├── progress.json    # 問題IDごとの進捗（オブジェクト）
├── history.jsonl    # 全回答の履歴（1行1回答、監査用）
└── incoming/        # サブエージェントが生成した問題の置き場（マージ後は残っていてよい）
```

**これらのファイルを直接編集しないこと。** 読み書きはすべて `scripts/` を経由する。

## questions.json（問題バンク）

```json
[
  {
    "id": "typescript-a1b2c3d4",
    "topic": "TypeScript",
    "type": "multiple_choice",
    "difficulty": "medium",
    "question": "問題文",
    "choices": ["A", "B", "C", "D"],
    "answer": "B",
    "explanation": "解説",
    "source": "docs/foo.md:12"
  }
]
```

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | string | `<topicスラグ>-<問題文sha1先頭8桁>`。`add-questions.sh` が採番 |
| `topic` | string | トピック名。進捗集計・出題フィルタの単位 |
| `type` | `multiple_choice` \| `free_text` | 記述式は `choices` なし |
| `difficulty` | `easy` \| `medium` \| `hard` | 省略時 medium |
| `question` | string | 自己完結した問題文 |
| `choices` | string[] \| null | multiple_choice のみ必須（2件以上、通常4件） |
| `answer` | string | multiple_choice では choices のいずれかと完全一致 |
| `explanation` | string | 正解の理由＋誤答が違う理由 |
| `source` | string \| null | 出題根拠（ファイルパス:行 など）。一般知識なら null |

## progress.json（進捗）

問題IDをキーとするオブジェクト。`record-answer.sh` だけが更新する。

```json
{
  "typescript-a1b2c3d4": {
    "attempts": 3,
    "correct": 2,
    "streak": 2,
    "last_result": "correct",
    "last_answered_at": "2026-07-11T10:30:00Z"
  }
}
```

- `streak`: 連続正解数。不正解で0にリセット。**3以上で習熟済み**とみなし出題優先度が下がる
- 正答率は `correct / attempts`。60%未満（2回以上回答）で「苦手問題」

## history.jsonl（回答履歴）

```json
{"ts": "2026-07-11T10:30:00Z", "question_id": "typescript-a1b2c3d4", "result": "correct"}
```

progress.json が壊れた場合はこのファイルから再構築できる。

## スクリプト一覧

| スクリプト | 引数 | 役割 |
|---|---|---|
| `init-workspace.sh` | なし | ワークスペース初期化＋バンク現状表示 |
| `add-questions.sh` | `<JSONファイル>` | 生成問題を検証・採番してバンクへマージ（重複スキップ） |
| `pick-questions.sh` | `[出題数] [トピック]` | 未出題→苦手→習熟済みの優先度で出題対象を選定 |
| `record-answer.sh` | `<question_id> <correct\|incorrect>` | 1問分の結果を記録 |
| `show-progress.sh` | `[トピック]` | 進捗サマリ（トピック別・苦手問題一覧）を集計表示 |
