# JSONスキーマ定義（steering-audit）

監査の各フェーズが出力するJSONの定義。すべて `steering-audit-workspace/` 配下に配置する。

## Contents

- inventory.json（Phase 1）
- findings/<primitive>.json（Phase 2）
- fit.json（Phase 3）
- audit.json（Phase 4）

---

## inventory.json（Phase 1: inventory-scout）

発見した全ステアリング成果物の目録。

```json
{
  "target": "/path/to/repo",
  "scanned_at": "2026-06-24T10:00:00Z",
  "artifacts": [
    {
      "id": "skill:steering-audit",
      "type": "skill",
      "path": "plugins/steering-auditor/skills/steering-audit/SKILL.md",
      "name": "steering-audit",
      "summary": "ステアリング設定を監査するスキル",
      "related_paths": ["references/", "agents/"]
    },
    {
      "id": "hook:skill-grower",
      "type": "hook",
      "path": "plugins/skill-grower/hooks/hooks.json",
      "name": "skill-grower hooks",
      "summary": "PermissionRequest/UserPromptSubmit/PostToolUse/Stop の4イベントをロギング",
      "related_paths": ["scripts/log-user-prompt.sh", "scripts/export-session-log.sh"]
    }
  ],
  "counts": {
    "skill": 6,
    "hook": 1,
    "claude_md": 1,
    "subagent": 4,
    "slash_command": 0,
    "output_style": 0,
    "mcp": 0
  },
  "notes": []
}
```

**フィールド:**
- `type`: `"skill"` | `"hook"` | `"claude_md"` | `"rule"` | `"subagent"` | `"slash_command"` | `"output_style"` | `"mcp"` | `"settings"` | `"plugin_manifest"`
- `id`: `<type>:<name>` 形式の一意識別子
- `summary`: 1行の内容要約（成果物を開かずに何かを把握できる程度）
- `related_paths`: 関連する参照ファイル/スクリプト/ディレクトリ

---

## findings/<primitive>.json（Phase 2: primitive-evaluator）

primitiveタイプ1つ分の評価結果。`findings/skill.json` のようにタイプ別に保存。

```json
{
  "primitive": "skill",
  "evaluated": ["skill:steering-audit", "skill:skill-evaluator"],
  "findings": [
    {
      "artifact_id": "skill:example",
      "rubric_item": "descriptionのトリガー精度",
      "severity": "high",
      "evidence": "description が『スキルを評価』のみで、トリガー語・use/not-use境界がない（SKILL.md:3）",
      "recommendation": "トリガー語と『いつ使わないか』を追記し、近接スキルとの境界を明示する",
      "primitive_fit_note": null
    },
    {
      "artifact_id": "skill:deploy",
      "rubric_item": "手順的か（primitive適合）",
      "severity": "medium",
      "evidence": "内容は常時の命名規約のみで手順要素がない（SKILL.md全体）",
      "recommendation": "発火を待つ必要がない助言なので CLAUDE.md/rules を検討",
      "primitive_fit_note": "claude_md または rule の候補。Phase 3 で判定"
    }
  ],
  "scores": {
    "skill:steering-audit": {"design": 9, "fit": 10},
    "skill:example": {"design": 5, "fit": 8}
  },
  "summary": "2件中1件で description のトリガー精度に高重大度の問題"
}
```

**フィールド:**
- `findings[].severity`: `"critical"` | `"high"` | `"medium"` | `"low"`
- `findings[].evidence`: ファイル:行 を含む具体的な根拠（必須）
- `findings[].primitive_fit_note`: 別primitiveの可能性に気づいた場合のメモ（最終判断は Phase 3）。なければ `null`
- `scores.<artifact_id>.design`: 設計品質 0-10
- `scores.<artifact_id>.fit`: primitive適合の予備スコア 0-10

---

## fit.json（Phase 3: fit-checker）

「正しいprimitiveを選んでいるか」の横断判定。

```json
{
  "mismatches": [
    {
      "artifact_id": "claude_md:root",
      "current": "claude_md",
      "recommended": "hook",
      "severity": "high",
      "what": "『コミット前に必ずnpm testを実行』という決定的要求がCLAUDE.mdに文章で書かれている",
      "why": "advisoryなのでモデルが状況により飛ばしうる。必ず走らせたいなら決定的なhookにすべき",
      "where": "CLAUDE.md:42-45",
      "suggested_action": "PreToolUse(Bash matcher) または Stop hook でテスト実行を強制する"
    }
  ],
  "duplications": [
    {
      "instruction": "出力は日本語で書く",
      "locations": ["CLAUDE.md:10", "skills/foo/SKILL.md:20"],
      "severity": "low",
      "suggested_action": "CLAUDE.md を単一の出典にし、skill側の重複を削除"
    }
  ],
  "summary": "1件のhook化推奨と1件の重複を検出"
}
```

**フィールド:**
- `mismatches[].current` / `recommended`: 現在と推奨の primitive type
- `mismatches[].why`: ブログの決定軸に基づく理由（必須）
- `duplications[]`: 複数箇所に重複した指示

---

## audit.json（Phase 4: report-synthesizer）

統合された機械可読の監査結果。`audit-report.md`（人間可読）と対で出力。

```json
{
  "target": "/path/to/repo",
  "generated_at": "2026-06-24T10:30:00Z",
  "health": {
    "overall_score": 7.8,
    "by_primitive": {
      "skill": {"score": 8.5, "count": 6, "critical": 0, "high": 1},
      "hook": {"score": 7.0, "count": 1, "critical": 0, "high": 0},
      "claude_md": {"score": 6.5, "count": 1, "critical": 0, "high": 1}
    }
  },
  "top_findings": [
    {"artifact_id": "claude_md:root", "severity": "high", "summary": "必須テスト実行がhook化されていない"}
  ],
  "fit_mismatches": [
    {"artifact_id": "claude_md:root", "current": "claude_md", "recommended": "hook", "severity": "high"}
  ],
  "roadmap": [
    {"priority": 1, "action": "コミット前テストをStop hookに移す", "primitive": "hook", "severity": "high"},
    {"priority": 2, "action": "example skill の description にトリガー語を追加", "primitive": "skill", "severity": "high"}
  ],
  "counts": {"critical": 0, "high": 2, "medium": 3, "low": 4}
}
```

**フィールド:**
- `health.overall_score`: 全体健全性 0-10（primitive別スコアの加重平均）。**ステアリング成果物が1件も無い場合は `0` ではなく `null`** とする（`0` は「悪い設定が存在する」という誤った含意を持つため。設定の不在は「品質が低い」ではなく「未着手」）。あわせて `status: "no_artifacts_found"` を付け、`top_findings`・`fit_mismatches`・`counts` は空/ゼロにする
- `roadmap[]`: 優先度順の改善計画。ブログ推奨（skills→hooks→subagents）の順序感を加味
- `counts`: 重大度別の所見総数
