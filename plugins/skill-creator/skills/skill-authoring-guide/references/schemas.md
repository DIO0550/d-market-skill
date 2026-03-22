# JSONスキーマ定義

スキル作成で使用するJSONスキーマの定義。

## Contents

- evals.json
- grading.json
- timing.json
- benchmark.json
- comparison.json
- analysis.json
- history.json
- metrics.json

---

## evals.json

スキルの評価ケースを定義する。スキルディレクトリ内の `evals/evals.json` に配置。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "ユーザーのタスクプロンプト",
      "expected_output": "期待結果の説明",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "出力にXが含まれている",
        "スキルがスクリプトYを使用した"
      ]
    }
  ]
}
```

**フィールド:**
- `skill_name`: スキルのフロントマター name と一致
- `evals[].id`: 一意の整数識別子
- `evals[].prompt`: 実行するタスク
- `evals[].expected_output`: 成功の人間可読な説明
- `evals[].files`: 入力ファイルパスのリスト（スキルルートからの相対）（オプション）
- `evals[].expectations`: 検証可能な文のリスト

---

## grading.json

採点エージェントの出力。`<run-dir>/grading.json` に配置。

```json
{
  "expectations": [
    {
      "text": "出力に 'John Smith' という名前が含まれている",
      "passed": true,
      "evidence": "トランスクリプト Step 3 で発見"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {"Read": 5, "Write": 2, "Bash": 8},
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "フォームには12個の入力可能フィールドがある",
      "type": "factual",
      "verified": true,
      "evidence": "field_info.json で12フィールドを確認"
    }
  ],
  "user_notes_summary": {
    "uncertainties": [],
    "needs_review": [],
    "workarounds": []
  },
  "eval_feedback": {
    "suggestions": [],
    "overall": "評価項目に問題なし"
  }
}
```

**フィールド:**
- `expectations[]`: エビデンス付きの採点済み期待値
  - `text`, `passed`, `evidence` が必須
- `summary`: 集計パス/フェイルカウント
- `execution_metrics`: ツール使用量と出力サイズ（executor の metrics.json から）
- `timing`: 実行時間（timing.json から）
- `claims`: 出力から抽出・検証されたクレーム
- `user_notes_summary`: 実行者がフラグした問題
- `eval_feedback`:（オプション）評価項目の改善提案

---

## metrics.json

実行エージェントの出力。`<run-dir>/outputs/metrics.json` に配置。

```json
{
  "tool_calls": {"Read": 5, "Write": 2, "Bash": 8, "Edit": 1, "Glob": 2, "Grep": 0},
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

---

## timing.json

ランの実行時間。`<run-dir>/timing.json` に配置。

**キャプチャ方法:** サブエージェントタスクが完了すると、タスク通知に `total_tokens` と `duration_ms` が含まれる。即座に保存すること — 他の場所には保存されず、後から回復できない。

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

ベンチマークの出力。`<workspace>/iteration-N/benchmark.json` に配置。

```json
{
  "metadata": {
    "skill_name": "my-skill",
    "skill_path": "/path/to/skill",
    "executor_model": "claude-sonnet-4-20250514",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "テスト名",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": []
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": []
}
```

**重要:** `config` の代わりに `configuration` を使い、`pass_rate` は `result` の中にネストする。このスキーマを参照して benchmark.json を生成すること。

**フィールド:**
- `metadata`: ベンチマーク実行の情報
- `runs[]`: 個別のラン結果
  - `configuration`: `"with_skill"` または `"without_skill"`
  - `result`: ネストオブジェクト（`pass_rate`, `passed`, `total`, `time_seconds`, `tokens`, `errors`）
- `run_summary`: 構成別の統計集計
  - `delta`: 差分文字列（`"+0.50"`, `"+13.0"` など）
- `notes`: アナライザーからの自由形式観察

---

## comparison.json

ブラインド比較の出力。`<grading-dir>/comparison-N.json` に配置。

```json
{
  "winner": "A",
  "reasoning": "出力Aが完全なソリューションを提供...",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {"score": 9, "strengths": [], "weaknesses": []},
    "B": {"score": 5, "strengths": [], "weaknesses": []}
  }
}
```

---

## analysis.json

事後分析の出力。`<grading-dir>/analysis.json` に配置。

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "パス",
    "loser_skill": "パス",
    "comparator_reasoning": "理由の概要"
  },
  "winner_strengths": [],
  "loser_weaknesses": [],
  "instruction_following": {
    "winner": {"score": 9, "issues": []},
    "loser": {"score": 6, "issues": []}
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "具体的な改善内容",
      "expected_impact": "期待される影響"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "実行パターンの説明",
    "loser_execution_pattern": "実行パターンの説明"
  }
}
```

---

## history.json

改善モードでのバージョン進行を追跡。ワークスペースルートに配置。

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "my-skill",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```
