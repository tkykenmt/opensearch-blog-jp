#!/bin/bash
# Usage: .kiro/commands/translate-opensearch-blog.sh <URL1> [URL2] [URL3] ...
#
# 環境変数:
#   GITHUB_TOKEN - GitHub Personal Access Token (push に必要)
#
# 事前設定例:
#   export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

if [ $# -eq 0 ]; then
  echo "Usage: .kiro/commands/translate-opensearch-blog.sh <URL1> [URL2] [URL3] ..."
  exit 1
fi

VALID_URLS=""
for arg in "$@"; do
  if [[ "$arg" =~ ^https?:// ]]; then
    VALID_URLS="$VALID_URLS $arg"
  else
    echo "Skipping invalid URL: $arg"
  fi
done

if [ -z "$VALID_URLS" ]; then
  echo "Error: No valid URLs provided"
  exit 1
fi

# GitHub Token のチェック
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Warning: GITHUB_TOKEN is not set. Git push will require manual authentication."
fi

kiro-cli chat --agent enomott --model claude-opus-4.5 --trust-all-tools --no-interactive "指定した URL の blog を翻訳して zenn に公開したい。翻訳済みであるかを status.json を元に確認し、未対応の場合のみ作業を実施せよ。本リポジトリ内に翻訳ドラフトを作成して。全角と半角文字の間は半角スペースで分けて。カッコ () やブラケット [] は半角を使うこと。原文の文末のコロン(:) は、日本語訳では句点(。)に置き換えること。初めに npx zenn new:article コマンドでファイルを作って、そこに翻訳内容を追加して。slug は opensearch- を prefix とし、 12〜50 文字の範囲で作成すること。title の先頭には [翻訳] と付与すること。publication_name は opensearch、topics はリスト型で、最大 5 つまで適切なものを付与して。opensearch は必ず含めること。適切なトピックが無い場合は、新規トピックの追加を提案して。type は tech。published_at は必ず HTML の HEAD 要素内の meta タグ property=\"article:published_time\" の content 属性から curl と grep で取得して YYYY-MM-DD 形式で記載すること。元記事の画像ファイルはダウンロードして images/<slug-id>/ 配下に格納。md ファイル内の画像のリンクパスは /images/<slug-id>/<filename> として。先頭の / は必ず入れて。翻訳の正確性より、技術的な正確さと日本語の文章として読みやすさを重視してください。文章の冒頭には、:::message 本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。 ::: のブロックを入れ、その下に元記事の URL を一行空けて記入してください。その後更に 1 行空けてから本文を書いてください。

日本語表現のルール:
- 「今後の展望」→「今後の予定」
- 「ご覧ください」→「参照してください」
- 「本ブログ」「このブログ記事」「ブログ記事」→「本記事」または「記事」
- 「可観測性」→「オブザーバビリティ」
- 「字句検索」→「テキスト検索」
- 「以下の図は〜を示しています」→「以下の図に〜を示します」
- 「以下の手順に従ってください」→「以下の手順で行います」
- 「開示:」→「**注意事項:**」

ファイルが生成できたら、上記ルールに従って自然な日本語表現であるかをセルフチェックし、修正してください。作業の各工程で随時 status.json を更新して。

最終チェック完了後:
1. reviewed ステータスの記事を最終確認
2. 問題なければ published: true に設定
3. git add -A && git commit
4. 環境変数 GITHUB_TOKEN が設定されていれば git push (https://\${GITHUB_TOKEN}@github.com/... 形式)
5. status.json の status を published に更新して再度 push

URLs:$VALID_URLS"
