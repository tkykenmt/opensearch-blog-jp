#!/bin/bash
set -euo pipefail

PROMPTS_DIR=".kiro/prompts"
BASE_PROMPT="$PROMPTS_DIR/write-session-article.md"

usage() {
  echo "Usage: $0 --urls <URL1> [URL2] ..." >&2
  echo "       $0 --playlist <Playlist URL>" >&2
  echo "       $0 --publish <slug>" >&2
  exit 1
}

[[ $# -eq 0 ]] && usage
[[ ! -f "$BASE_PROMPT" ]] && { echo "Error: $BASE_PROMPT not found" >&2; exit 1; }

case "$1" in
  --urls)
    shift
    [[ $# -eq 0 ]] && { echo "Error: No URLs provided" >&2; exit 1; }
    URLS=()
    for arg in "$@"; do
      [[ "$arg" =~ ^https?://(www\.)?youtube\.com/watch ]] && URLS+=("$arg") || echo "Skipping: $arg" >&2
    done
    [[ ${#URLS[@]} -eq 0 ]] && { echo "Error: No valid YouTube URLs" >&2; exit 1; }
    MODE_PROMPT="$PROMPTS_DIR/session-from-urls.md"
    [[ ! -f "$MODE_PROMPT" ]] && { echo "Error: $MODE_PROMPT not found" >&2; exit 1; }
    PROMPT="$(cat "$BASE_PROMPT")

$(sed "s|{{URLS}}|${URLS[*]}|" "$MODE_PROMPT")"
    ;;
  --playlist)
    shift
    [[ $# -eq 0 ]] && { echo "Error: No playlist URL provided" >&2; exit 1; }
    PLAYLIST_URL="$1"
    [[ ! "$PLAYLIST_URL" =~ ^https?://(www\.)?youtube\.com/(playlist\?list=|watch\?.*list=) ]] && { echo "Error: Invalid playlist URL" >&2; exit 1; }
    MODE_PROMPT="$PROMPTS_DIR/session-from-playlist.md"
    [[ ! -f "$MODE_PROMPT" ]] && { echo "Error: $MODE_PROMPT not found" >&2; exit 1; }
    PROMPT="$(cat "$BASE_PROMPT")

$(sed "s|{{PLAYLIST_URL}}|${PLAYLIST_URL}|" "$MODE_PROMPT")"
    ;;
  --publish)
    shift
    [[ $# -eq 0 ]] && { echo "Error: No slug provided" >&2; exit 1; }
    SLUG="$1"
    MODE_PROMPT="$PROMPTS_DIR/session-publish.md"
    [[ ! -f "$MODE_PROMPT" ]] && { echo "Error: $MODE_PROMPT not found" >&2; exit 1; }
    PROMPT="$(sed "s|{{SLUG}}|${SLUG}|" "$MODE_PROMPT")"
    ;;
  *)
    usage
    ;;
esac

kiro-cli chat --agent opensearchcon-session-writer --model claude-opus-4.5 \
  --trust-all-tools --no-interactive "$PROMPT"
