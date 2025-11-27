#!/bin/bash
# Usage: .kiro/commands/translate-opensearch-blog.sh <URL1> [URL2] [URL3] ...

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

kiro-cli chat --agent enomott --model claude-opus-4.5 --trust-all-tools --no-interactive "指定した URL の blog を翻訳して zenn に公開したい。本リポジトリ内に翻訳ドラフトを作成して。全角と半角文字の間は半角スペースで分けて。カッコ () やブラケット [] は半角を使うこと。原文の文末のコロン(:) は、日本語訳では句点(。)に置き換えること。初めに npx zenn new:article コマンドでファイルを作って、そこに翻訳内容を追加して。slug は opensearch- を prefix とし、 12〜50 文字の範囲で作成すること。title の先頭には [翻訳] と付与すること。publication_name は opensearch、topics は [\"opensearch\"]、type は tech。published_at は必ず HTML の HEAD 要素内の meta タグ property=\"article:published_time\" の content 属性から curl と grep で取得して YYYY-MM-DD 形式で記載すること。元記事の画像ファイルはダウンロードして images/<slug-id>/ 配下に格納。md ファイル内の画像のリンクパスは /images/<slug-id>/<filename> として。先頭の / は必ず入れて。翻訳の正確性より、技術的な正確さと日本語の文章として読みやすさを重視してください。文章の冒頭には、:::message 本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。 ::: のブロックを入れ、その下に元記事の URL を一行空けて記入してください。その後更に 1 行空けてから本文を書いてください。ファイルが生成できたら、再度自然な日本語表現であるかをセルフチェックし、修正してください。 URLs:$VALID_URLS"


