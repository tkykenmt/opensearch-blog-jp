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

PROMPT_FILE=".kiro/prompts/translate-opensearch-blog.md"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

PROMPT=$(cat "$PROMPT_FILE")

kiro-cli chat --agent opensearch-blog-translator --model claude-opus-4.5 --trust-all-tools --no-interactive "$PROMPT

URLs:$VALID_URLS"
