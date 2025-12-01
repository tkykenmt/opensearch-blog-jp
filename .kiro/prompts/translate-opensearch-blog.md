# OpenSearch Blog 翻訳タスク

指定した URL の blog を翻訳して zenn に公開したい。

## 事前確認

- 翻訳済みであるかを status.json を元に確認
- 未対応の場合のみ作業を実施

## 翻訳ファイル作成

1. `npx zenn new:article` コマンドでファイルを作成
2. 翻訳内容を追加

### Front Matter 設定

- **slug**: `opensearch-` を prefix とし、12〜50 文字の範囲で作成
- **title**: 先頭に `[翻訳]` を付与
- **publication_name**: `opensearch`
- **topics**: リスト型で最大 5 つまで適切なものを付与（`opensearch` は必須）
  - 適切なトピックが無い場合は新規トピック追加を提案
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

## 進捗管理

作業の各工程で随時 status.json を更新。

## 最終チェック完了後

1. reviewed ステータスの記事を最終確認
2. 問題なければ `published: true` に設定
3. `git add -A && git commit` (コミットメッセージは Conventional Commits 形式で)
4. GitHub MCP ツールを使用して変更を push (owner: tkykenmt, repo: opensearch-blog-jp, branch: main)
5. status.json の status を published に更新して再度 commit & push
