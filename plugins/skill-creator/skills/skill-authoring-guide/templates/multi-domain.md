---
name: your-skill-name
description: "複数ドメインにまたがるスキルの説明。各ドメインのキーワードを列挙。関連する質問では積極的に使用すること。"
---

# スキル名

スキルの目的を1-2行で説明。
複数のドメイン/フレームワーク/プラットフォームに対応。

---

## 対応ドメイン

| ドメイン | 概要 | 参照ファイル |
|---------|------|-------------|
| **Domain A** | [概要] | [references/domain-a.md](references/domain-a.md) |
| **Domain B** | [概要] | [references/domain-b.md](references/domain-b.md) |
| **Domain C** | [概要] | [references/domain-c.md](references/domain-c.md) |

## ドメイン選択

リクエスト内容から適切なドメインを判断し、該当する参照ファイルを読み込む。

**判断基準：**
- [キーワードA]、[用語A] → Domain A
- [キーワードB]、[用語B] → Domain B
- [キーワードC]、[用語C] → Domain C
- 不明確な場合 → ユーザーに確認

## 共通ワークフロー

全ドメインに共通する手順：

1. ドメインを特定する
2. 該当する参照ファイルを読み込む
3. 参照ファイルの指示に従って処理する
4. 結果を出力する

## クイック検索

特定の情報をgrepで検索：

```bash
grep -i "<keyword>" references/domain-a.md
grep -i "<keyword>" references/domain-b.md
```

---

## 参照ファイル

各ドメインの参照ファイルには以下を含める：

- ドメイン固有のワークフロー
- 設定値・パラメータ
- コード例
- よくあるエラーと対処法
