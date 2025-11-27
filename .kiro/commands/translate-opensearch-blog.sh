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

kiro chat "指定した URL のblog を翻訳して zenn に公開したい。本リポジトリ内に翻訳ドラフトを作成して。全角と半角文字の間は半角スペースで分けて。カッコ()やブラケット[]は半角を使うこと。初めに npx zenn コマンドでファイルを作って、そこに翻訳内容を追加て。publication_name は opensearch、topics は opensearch のみ、type は tech。published_at は HTML 内の published_time から取得して付与して。元記事の画像ファイルはダウンロードして images/<slug-id>/ 配下に格納。md ファイル内の画像のリンクパスは /images/<slug-id>/<filename> として。 先頭の / は必ず入れて。 URLs:$VALID_URLS"


