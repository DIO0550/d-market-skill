---
name: your-skill-name
description: "スキルの主要機能の説明。具体的なトリガー条件。関連キーワードでは積極的に使用すること。"
---

# スキル名

スキルの目的を1-2行で説明。

---

## ワークフロー

以下のチェックリストをコピーして進捗を追跡する：

```
進捗:
- [ ] Step 1: [ステップ名] (script_name.py)
- [ ] Step 2: [ステップ名]
- [ ] Step 3: [ステップ名] (validate.py)
- [ ] Step 4: [ステップ名] (process.py)
- [ ] Step 5: [ステップ名] (verify.py)
```

### Step 1: [入力解析]

実行: `python scripts/analyze.py <input_file>`

出力: `result.json` に解析結果が保存される

### Step 2: [設定/マッピング]

`result.json` を確認・編集する。

### Step 3: [バリデーション]

実行: `python scripts/validate.py result.json`

バリデーションエラーがあればStep 2に戻って修正。

### Step 4: [メイン処理]

実行: `python scripts/process.py <input_file> result.json <output_file>`

### Step 5: [出力検証]

実行: `python scripts/verify.py <output_file>`

検証失敗の場合、Step 2に戻る。

---

## ユーティリティスクリプト

| スクリプト | 用途 | 使い方 |
|-----------|------|--------|
| `scripts/analyze.py` | 入力ファイル解析 | `python scripts/analyze.py <input>` |
| `scripts/validate.py` | 中間結果の検証 | `python scripts/validate.py <json>` |
| `scripts/process.py` | メイン処理実行 | `python scripts/process.py <in> <json> <out>` |
| `scripts/verify.py` | 最終出力の検証 | `python scripts/verify.py <output>` |

---

## エラーハンドリング

- バリデーション失敗時: エラーメッセージを確認し、該当フィールドを修正
- 処理失敗時: 入力ファイルの形式を確認
- 検証失敗時: Step 2のマッピングを見直す

---

## 参照ファイル

| ファイル | 内容 | 読むタイミング |
|---------|------|---------------|
| [references/format-spec.md](references/format-spec.md) | 入出力形式の詳細仕様 | 形式エラー発生時 |
| [references/advanced.md](references/advanced.md) | 高度な設定オプション | カスタマイズが必要な場合 |
