#!/bin/bash
set -euo pipefail

PROMPTS_DIR=".kiro/prompts"
BASE_PROMPT="$PROMPTS_DIR/translate-opensearch-blog.md"

usage() {
  echo "Usage: $0 -u|--url|--urls <URL1> [URL2] ..." >&2
  echo "       $0 -i|--from-issues" >&2
  exit 1
}

[[ $# -eq 0 ]] && usage
[[ ! -f "$BASE_PROMPT" ]] && { echo "Error: $BASE_PROMPT not found" >&2; exit 1; }

case "$1" in
  -i|--from-issues)
    MODE_PROMPT="$PROMPTS_DIR/translate-from-issues.md"
    [[ ! -f "$MODE_PROMPT" ]] && { echo "Error: $MODE_PROMPT not found" >&2; exit 1; }
    PROMPT="$(cat "$BASE_PROMPT")

$(cat "$MODE_PROMPT")"
    ;;
  -u|--url|--urls)
    shift
    [[ $# -eq 0 ]] && { echo "Error: No URLs provided" >&2; exit 1; }
    URLS=()
    for arg in "$@"; do
      [[ "$arg" =~ ^https?:// ]] && URLS+=("$arg") || echo "Skipping: $arg" >&2
    done
    [[ ${#URLS[@]} -eq 0 ]] && { echo "Error: No valid URLs" >&2; exit 1; }
    MODE_PROMPT="$PROMPTS_DIR/translate-from-urls.md"
    [[ ! -f "$MODE_PROMPT" ]] && { echo "Error: $MODE_PROMPT not found" >&2; exit 1; }
    PROMPT="$(cat "$BASE_PROMPT")

$(sed "s|{{URLS}}|${URLS[*]}|" "$MODE_PROMPT")"
    ;;
  *)
    usage
    ;;
esac

kiro-cli chat --agent opensearch-blog-translator --model claude-opus-4.5 \
  --trust-all-tools --no-interactive "$PROMPT"
