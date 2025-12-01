#!/bin/bash
set -euo pipefail

PROMPT_FILE=".kiro/prompts/translate-opensearch-blog.md"

[[ $# -eq 0 ]] && { echo "Usage: $0 <URL1> [URL2] ..." >&2; exit 1; }
[[ ! -f "$PROMPT_FILE" ]] && { echo "Error: $PROMPT_FILE not found" >&2; exit 1; }

URLS=()
for arg in "$@"; do
  [[ "$arg" =~ ^https?:// ]] && URLS+=("$arg") || echo "Skipping: $arg" >&2
done

[[ ${#URLS[@]} -eq 0 ]] && { echo "Error: No valid URLs" >&2; exit 1; }

kiro-cli chat --agent opensearch-blog-translator --model claude-opus-4.5 \
  --trust-all-tools --no-interactive "$(cat "$PROMPT_FILE")

URLs: ${URLS[*]}"
