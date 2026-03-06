#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PY="$(cat "$PLUGIN_ROOT/.claude/ha-python.txt" 2>/dev/null || command -v python3 || command -v py || command -v python)"

if [ -z "$PY" ]; then
  echo "docs-check: FAILED (python is required)" >&2
  exit 1
fi

exec "$PY" "$SCRIPT_DIR/docs-check.py"
