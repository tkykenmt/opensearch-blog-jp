#!/bin/bash
set -euo pipefail

# 設定
PROMPTS_DIR=".kiro/prompts"
TRANSLATE_PROMPT="$PROMPTS_DIR/translate-only.md"
REVIEW_PROMPT="$PROMPTS_DIR/review-translation.md"

# 認証付き Git URL
REPO_URL="https://${GITHUB_TOKEN}@github.com/$(git config --get remote.origin.url | sed 's|.*github.com[:/]||' | sed 's|\.git$||').git"

usage() {
  echo "Usage: $0 <URL> [SLUG]" >&2
  echo "  URL:  OpenSearch Blog の記事 URL" >&2
  echo "  SLUG: 省略時は自動生成（要確認）" >&2
  exit 1
}

[[ $# -lt 1 ]] && usage
[[ ! "$1" =~ ^https?:// ]] && { echo "Error: Invalid URL" >&2; exit 1; }

URL="$1"

# SLUG 決定
if [[ $# -ge 2 ]]; then
  SLUG="$2"
else
  # URL から仮 SLUG 生成
  SLUG="opensearch-$(echo "$URL" | sed 's|.*/||' | sed 's|/$||' | tr '[:upper:]' '[:lower:]')"
  echo "SLUG: $SLUG"
  read -p "この SLUG で続行しますか？ [y/N] " confirm
  [[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "中止しました"; exit 0; }
fi

echo "=== 1. ブランチ作成 ==="
git checkout main
git pull "$REPO_URL" main
git checkout -b "translate/$SLUG"

echo "=== 2. 翻訳実行 ==="
PROMPT=$(sed -e "s|{{URL}}|$URL|g" -e "s|{{SLUG}}|$SLUG|g" "$TRANSLATE_PROMPT")
kiro-cli chat --agent blog-translator --trust-all-tools --no-interactive "$PROMPT"

echo "=== 3. レビュー実行 ==="
REVIEW=$(sed "s|{{FILE}}|articles/$SLUG.md|g" "$REVIEW_PROMPT")
kiro-cli chat --agent blog-reviewer --trust-all-tools --no-interactive "$REVIEW"

echo "=== 4. 確認 ==="
echo "翻訳ファイル: articles/$SLUG.md"
read -p "PR を作成しますか？ [y/N] " confirm
[[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "PR 作成をスキップしました"; exit 0; }

echo "=== 5. コミット・プッシュ ==="
git add -A
git commit -m "feat: add translation for $SLUG"
git push "$REPO_URL" "translate/$SLUG"

echo "=== 6. PR 作成 ==="
OWNER=$(echo "$REPO_URL" | sed 's|.*github.com/||' | cut -d'/' -f1)
REPO=$(echo "$REPO_URL" | sed 's|.*github.com/||' | cut -d'/' -f2 | sed 's|\.git$||')

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$OWNER/$REPO/pulls" \
  -d @- <<EOF
{
  "title": "[Translation] $SLUG",
  "head": "translate/$SLUG",
  "base": "main",
  "body": "Translated from: $URL"
}
EOF

echo ""
echo "完了しました"
