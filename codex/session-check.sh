#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

detect_python() {
  if command -v python3 >/dev/null 2>&1; then
    printf '%s\n' "python3"
  elif command -v python >/dev/null 2>&1; then
    printf '%s\n' "python"
  elif command -v py >/dev/null 2>&1; then
    printf '%s\n' "py"
  else
    printf '%s\n' ""
  fi
}

PYTHON_CMD="$(detect_python)"

mkdir -p .claude 2>/dev/null || true
if [ -n "$PYTHON_CMD" ]; then
  printf '%s\n' "$PYTHON_CMD" > .claude/ha-python.txt 2>/dev/null || true
fi
printf '%s\n' "$ROOT_DIR" > .claude/ha-plugin-root.txt 2>/dev/null || true

echo "Home Assistant Assistant for Codex"

if [ ! -f "configuration.yaml" ]; then
  echo "- configuration.yaml not found in this directory. Run Codex from your Home Assistant config repository."
fi

if [ -n "${HASS_SERVER:-}" ] && [ -n "${HASS_TOKEN:-}" ]; then
  echo "- hass-cli environment: configured"
else
  echo "- hass-cli environment: HASS_SERVER or HASS_TOKEN missing. Use \$ha-onboard for setup."
fi

if [ -n "${HOMEASSISTANT_URL:-}" ] && [ -n "${HOMEASSISTANT_TOKEN:-}" ]; then
  echo "- Home Assistant MCP environment: configured"
fi

if [ -n "$PYTHON_CMD" ]; then
  echo "- Python command: $PYTHON_CMD"
else
  echo "- Python command not found. Some helper workflows need Python."
fi

echo "- Use \$ha-validate before deployment and \$ha-deploy only after explicit confirmation."
