#!/usr/bin/env bash
# Subscription pathway: retrieval + prompt-stuffing run in the container,
# generation runs through the host's Claude Code CLI (billed to the Claude
# subscription — human-in-the-loop experimentation only). The API path
# (`rag ask`) sends the byte-identical prompt once ANTHROPIC_API_KEY has
# credits; this wrapper is the temporary last mile, not the product.
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: ./ask.sh \"your question\" [k]"; exit 1; }
Q="$1"
K="${2:-8}"
# buffer fully before invoking claude — `claude -p` abandons stdin after 3s,
# and container startup + query embedding take longer than that
PROMPT="$(docker run --rm --env-file .env -v "$PWD:/workspaces/RRRAG" -w /workspaces/RRRAG \
  rrrag-dev uv run rag prompt "$Q" -k "$K")"
printf '%s' "$PROMPT" | claude -p
