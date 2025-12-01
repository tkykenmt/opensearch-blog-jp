# OpenSearch Blog 翻訳タスク

指定した URL の blog を翻訳して zenn に公開したい。

## ワークフロー

1. **Issue 作成**: GitHub MCP ツールで Translation Request Issue を作成 (owner: tkykenmt, repo: opensearch-blog-jp)
2. **翻訳作業**: 翻訳ファイルを作成し、レビュー依頼
3. **Pull Request 作成**: レビュー完了後、GitHub MCP ツールで PR 作成
4. **セルフチェック**: PR 内容を確認
5. **Merge**: 問題なければ GitHub MCP ツールで PR をマージ

## 事前確認

- GitHub Issues で既存の翻訳リクエストを確認
- 未対応の場合のみ作業を実施

## 翻訳ファイル作成

1. `npx zenn new:article --slug　<slug>` コマンドでファイルを作成。<slug> は `opensearch-` を prefix とし、12〜50 文字の範囲で指定。
2. 翻訳内容を追加

### Front Matter 設定

- **title**: 先頭に `[翻訳]` を付与
- **emoji**: 適切な絵文字を選択(例: 🔍)
- **publication_name**: `opensearch`
- **topics**: リスト型で最大 5 つまで適切なものを付与（`opensearch` は必須）
- **type**: `tech`
- **published_at**: HTML の HEAD 要素内の meta タグ `property="article:published_time"` の content 属性から curl と grep で取得し、YYYY-MM-DD 形式で記載

### 画像処理

- 元記事の画像ファイルをダウンロードして `images/<slug-id>/` 配下に格納
- md ファイル内の画像リンクパスは `/images/<slug-id>/<filename>` とする（先頭の `/` は必須）

### 文章構成

文章の冒頭に以下のブロックを配置:

```
:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

<元記事の URL>

<本文>
```

## 翻訳ルール

### 基本方針

- 翻訳の正確性より、技術的な正確さと日本語の文章としての読みやすさを重視
- 全角と半角文字の間は半角スペースで分ける
- カッコ `()` やブラケット `[]` は半角を使用
- 原文の文末のコロン `:` は日本語訳では句点 `。` に置き換え

### 用語統一

- 「今後の展望」→「今後の予定」
- 「ご覧ください」→「参照してください」
- 「本ブログ」「このブログ記事」「ブログ記事」→「本記事」または「記事」
- 「可観測性」→「オブザーバビリティ」
- 「字句検索」→「テキスト検索」
- 「以下の図は〜を示しています」→「以下の図に〜を示します」
- 「以下の手順に従ってください」→「以下の手順で行います」
- 「開示:」→「**注意事項:**」

## セルフチェック

ファイル生成後、上記ルールに従って自然な日本語表現であるかをセルフチェックし、修正する。

## ステップ 1: Issue 作成

GitHub MCP ツールで Issue を作成:

- Title: `[Translation] <記事タイトル>`
- Body: Original URL を記載
- Labels: `translation`

## ステップ 2: 翻訳作業

### ブランチ作成

- ブランチ名: `translate/<slug-id>`
- GitHub MCP ツールでブランチ作成 (from: main)

### 翻訳ファイル作成

1. `npx zenn new:article` コマンドでファイルを作成
2. 翻訳内容を追加
3. セルフチェックして修正
4. `git add -A && git commit` (コミットメッセージは Conventional Commits 形式、Issue 番号を含める)
5. GitHub MCP ツールで push

### レビュー依頼

翻訳完了後、ユーザーにレビューを依頼し、フィードバックを待つ。

## ステップ 3: Pull Request 作成

レビュー完了後:

1. `published: true` に設定
2. `git add -A && git commit`
3. GitHub MCP ツールで push
4. GitHub MCP ツールで PR 作成:
   - Title: `[Translation] <記事タイトル>`
   - Body: `Closes #<Issue番号>` を含める
   - Base: main
   - Head: translate/<slug-id>

## ステップ 4: セルフチェック

PR 内容を確認し、問題があれば修正。

## ステップ 5: Merge

問題なければ GitHub MCP ツールで PR をマージ。
