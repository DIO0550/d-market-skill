# 静的レビュー（無駄な記述・フロントマター適合）

スキルを**実行せずに**ファイルだけを読んで判定する検査の基準。Phase 0 で使う。

- パート1: 無駄な記述の検出（leanness）
- パート2: フロントマター適合チェック
- 重大度の定義
- 誤検出を避けるための原則

---

## パート1: 無駄な記述の検出

### 判定の起点

**「この記述を削ったら、スキルなしのClaudeと違う結果になるか？」**

ならなければ削除候補。スキル本文は毎回コンテキストに丸ごと載る。読まれても挙動を変えない行は、コストだけを払っている。

もう一段の問いは**目的との釣り合い**：`description` が約束している範囲に対して、本文の指示量が見合っているか。指示は多いほど良いのではない。強調と分岐が増えるほど、1件あたりの指示の効力は下がる。

### 検出パターン

| ID | パターン | 症状 | 対処 |
|----|---------|------|------|
| `baseline_knowledge` | ベースライン知識の再記述 | 「git commit はコミットを作成する」「JSONは構造化データ形式」など、モデルが既に知っていること | 削除 |
| `out_of_scope` | 目的外の指示 | `description` が約束していないタスクの手順が本文にある | 削除、または別スキルへ分離 |
| `duplication` | 重複 | 同じ指示が複数セクションにある／SKILL.md と references の両方にある | 一箇所に正規化し、他は参照リンクにする |
| `unjustified_emphasis` | 無根拠の強調 | ALWAYS / NEVER / MUST / 必ず / 絶対 が理由（WHY）なしに並ぶ | 理由を1文添えるか、通常の記述に落とす |
| `redundant_example` | 過剰な例示 | 同じパターンを示す例が3つ以上 | 代表1つ＋差分のある例だけ残す |
| `over_decomposition` | 自明な手順の分解 | 1ステップで足りる作業が複数ステップに割られている | 統合 |
| `dead_branch` | 発火しない条件分岐 | 実際には起こらない前提の分岐、対応していない環境向けの記述 | 削除 |
| `preamble` | 前置き・メタ説明 | 「このスキルは非常に重要です」「以下で説明します」など内容のない文 | 削除 |
| `misplaced_detail` | references に置くべき詳細 | 参照頻度の低い長い詳細が SKILL.md 本文にある | references へ移し、読むタイミングを本文に1行で書く |
| `dead_file` | 参照されないリソース | references / scripts / templates が本文から一度も参照されていない | 参照を追加するか削除 |

### 規模の目安

絶対基準ではなく、パターン探索を始めるフラグとして使う。

- SKILL.md が **500行超** — 公式ガイドの上限。分割・references 移動を検討
- 目的が単一タスクなのに **200行超** — `out_of_scope` / `duplication` を疑う
- 強調語（ALWAYS/NEVER/MUST/必ず/絶対）が **10箇所超** — `unjustified_emphasis` を疑う

### 削ってはいけないもの

削減提案の誤検出は、パス率の低下という形で跳ね返る。以下は「冗長に見えても残す」：

- eval で `ambiguity_point` / `discretionary_fill` として実際に報告され、それを埋めるために追加された記述
- 失敗事例に基づく制約（`iteration_log.json` に導入理由が残っているもの）
- 短くても判断を変える1行（境界値、フォーマット指定、出力先、禁止事項）
- reference / script を「いつ読むか・いつ実行するか」を指示している行（これが無いと参照ファイルが読まれない）

削除提案は**必ず根拠とセットで出す**。「短くできる」だけでは根拠にならない。

### 提案の検証

削減は主観になりやすいので、可能なら実測で裏を取る。削減案を適用した版で Phase B を回し、**パス率を下げないまま** トークン数・ステップ数が減ることを確認する。パス率が下がったなら、その記述は無駄ではなかった — 差し戻す。

---

## パート2: フロントマター適合チェック

### 現行フィールド一覧

`SKILL.md` 冒頭の `---` で囲まれた YAML。**全フィールドが任意**で、推奨は `description` のみ。

| フィールド | 用途 | 備考 |
|-----------|------|------|
| `name` | スキル一覧での表示名 | 既定はディレクトリ名。**プラグインスキルではコマンドの最終セグメントになる**（`my-plugin/skills/review/` に `name: fancy` → `/my-plugin:fancy`） |
| `description` | 何をするか＋いつ使うか | 省略時は本文の最初の段落が使われる。`when_to_use` との**合計 1,536 文字で切り詰め**られる |
| `when_to_use` | トリガー文言・依頼例の追加 | `description` に連結される。1,536文字キャップに算入 |
| `argument-hint` | 補完時に出す引数ヒント | 例: `[issue-number]` |
| `arguments` | `$name` 置換用の名前付き位置引数 | スペース区切り文字列または YAML リスト |
| `disable-model-invocation` | Claudeによる自動起動を止める | `true` で `/name` 手動起動のみ。サブエージェントへのプリロードや scheduled task 起動も止まる。既定 `false` |
| `user-invocable` | `/` メニューからの非表示 | `false` で非表示。**メニュー表示のみの制御でSkillツール経由の起動は止まらない**。既定 `true` |
| `allowed-tools` | そのターンだけ許可を省略するツール | 次のユーザー発言で失効。スペース/カンマ区切りまたは YAML リスト |
| `disallowed-tools` | スキル有効中に取り上げるツール | 自律ループで `AskUserQuestion` を封じる等。次の発言で失効 |
| `model` | スキル有効中のモデル | ターン内のみ有効。`inherit` 可 |
| `effort` | スキル有効中の effort | `low` / `medium` / `high` / `xhigh` / `max` |
| `context` | `fork` でサブエージェント隔離実行 | 会話履歴は引き継がれない |
| `agent` | `context: fork` 時のサブエージェント種別 | — |
| `background` | `context: fork` 時に結果を待つか | `false` で同一ターン内待機。既定 `true` |
| `hooks` | スキルのライフサイクルに紐づくhook | — |
| `paths` | 自動起動をファイルglobで限定 | カンマ区切りまたは YAML リスト |
| `shell` | インラインコマンドのシェル | `bash`（既定）/ `powershell` |
| `metadata` | 自前ツール用の自由なキー値マップ | **マップ以外の値は破棄**される。`paths` など既存フィールド名をキーに再利用しない |
| `license` | ライセンス | Agent Skills spec。Claude Code は受け付けるが何もしない |
| `compatibility` | 動作環境要件 | Agent Skills spec。500文字以内の文字列 |

boolean フィールドは `true` / `false` に加えて `yes` `no` `on` `off` `1` `0`（大文字小文字不問）も受理される（v2.1.218以降）。古いバージョンとの互換を優先するなら `true` / `false` を使う。

### 配布先による制約（重要）

Claude Code は上表の全フィールドを受け付けるが、**Claude Code の外へ配布する場合は Agent Skills spec の6フィールドしか使えない**：

`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`

対象となる配布経路: claude.ai へのスキルアップロード、Skills API、`package_skill.py` でのパッケージング、およびパーソナルスキルを Cowork／クラウドセッション（Routine を含む）で使う場合。

spec 外のフィールドが1つでもあると、無視ではなく**ハードエラー**になる：

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

したがって監査では「このスキルの配布先はどこか」を先に決める。Claude Code 内だけなら全フィールド可、claude.ai / API にも出すなら6フィールドに絞る。

### チェック項目

**適合（規約違反 — 直す必要がある）**

1. 未知のフィールドが無いか（`version` `author` `tags` `category` などは**フロントマターではなく `plugin.json` 側**のフィールド。SKILL.md に書いても効かない）
2. 配布先が claude.ai / Skills API / `package_skill.py` を含むなら、spec 外フィールドが無いか
3. `metadata` がマップになっているか（文字列・配列は破棄される）
4. `compatibility` が500文字以内か
5. プラグインスキルで `name` とディレクトリ名が食い違っていないか（食い違うとコマンド名が変わる。意図的なら可）
6. `description` と `when_to_use` の合計が 1,536 文字を超えていないか（超過分は一覧から切り捨てられ、トリガーに効かない）

**改善（もっと良い書き方があるか — 提案する）**

7. `description` が「何をするか」だけで**「いつ使うか」が無い** → トリガーしない最大の原因。用途・トリガー文言を入れる
8. 重要な用途が `description` の**先頭**に来ているか（切り詰めは後ろから起きる）
9. 副作用を伴うスキル（deploy / commit / 送信 / 破壊的操作）に `disable-model-invocation: true` が付いているか
10. `disable-model-invocation: true` なのに `description` にトリガーキーワードを詰め込んでいないか — **このフィールドを付けると description は文脈に載らない**ので、トリガー語は効かない死んだ記述になる。手動起動専用なら description は「何をするスキルか」を簡潔に書けば足りる
11. 背景知識としてのみ使い、直接呼ばれたくないスキルに `user-invocable: false` を検討したか
12. 毎回同じ許可プロンプトが出るスキルに `allowed-tools` を検討したか。バンドルスクリプトは `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)` と本文の `${CLAUDE_SKILL_DIR}` を揃えると無プロンプトで実行できる（v2.1.129以降）
13. 自律実行・バックグラウンド用途で呼ばせたくないツールに `disallowed-tools` を検討したか
14. 大量の探索や長い調査を伴い、メインの文脈を汚すスキルに `context: fork` を検討したか
15. 特定のファイル種別を扱うときだけ起動すべきスキルに `paths` を検討したか
16. 引数を取るスキルに `argument-hint` / `arguments` があるか

7〜16 は**提案であって違反ではない**。現状のままが妥当な場合も多いので、「なぜそのフィールドが要るか」を1文で書けないなら提案しない。

---

## 重大度の定義

| severity | 意味 | 例 |
|----------|------|-----|
| `critical` | スキルが正しくロード／トリガーされない | 配布先で禁止されているフィールドがある、`description` が無くトリガーしない |
| `high` | 挙動または品質に実害がある | 1,536文字超で用途が切り捨てられる、`disable-model-invocation` と description の矛盾、目的外の指示（`out_of_scope`） |
| `medium` | コスト・保守性の問題 | 重複、過剰な例示、references に移すべき詳細、無根拠の強調の連発 |
| `low` | 好みの範囲・軽微 | 前置き文、`argument-hint` 未設定 |

---

## 誤検出を避けるための原則

- **根拠のない削除提案を出さない。** 各 finding には対象箇所（行番号またはセクション名）と、削って良い理由を書く
- **履歴を尊重する。** `iteration_log.json` があるなら先に読む。過去のイテレーションが特定の失敗に対処するために足した記述を、無自覚に削り戻さない
- **削減幅を目標にしない。** 「何行削れたか」は成果ではない。パス率を維持したままトークンが減ったかが成果
- **静的レビューは eval の代替ではない。** ここで出るのは仮説。確定させるのは Phase B の実測
