#!/usr/bin/env python3
"""Codex PreToolUse guard for environment dumps and broken HA commands."""

from __future__ import annotations

import json
import re
import sys


ENV_DUMP_PATTERNS = [
    re.compile(r"(^|\|[ \t]*)(env|printenv|set|export[ \t]+-p)([ \t]|\||$)", re.IGNORECASE),
    re.compile(r"\b(get-childitem|gci|dir|ls|get-item|gi)\s+env:", re.IGNORECASE),
    re.compile(r"\[(system\.)?environment\]::getenvironmentvariables\s*\(", re.IGNORECASE),
]

RAW_WS_PATTERN = re.compile(r"\bhass-cli\s+raw\s+ws\b", re.IGNORECASE)


def extract_command(raw: str) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(payload, dict):
        command = payload.get("command")
        if isinstance(command, str):
            return command
    return raw


def main() -> int:
    command = extract_command(sys.stdin.read())

    if any(pattern.search(command) for pattern in ENV_DUMP_PATTERNS):
        print(
            "BLOCKED: This command would dump environment variables, risking HASS_TOKEN or HOMEASSISTANT_TOKEN exposure "
            "(Safety Invariant #4). Use a token length/presence check instead of printing environment values.",
            file=sys.stderr,
        )
        return 2

    if RAW_WS_PATTERN.search(command):
        print(
            "BLOCKED: hass-cli raw ws is broken on HA 2026.2+ and returns 'Unknown command' for all message types. "
            "Use hass-cli -o json built-in commands or Python websocket helpers instead.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
