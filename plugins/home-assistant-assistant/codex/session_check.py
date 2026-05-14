#!/usr/bin/env python3
"""Codex SessionStart environment check for Home Assistant Assistant."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def detect_python() -> str:
    for candidate in ("python3", "python", "py"):
        if shutil.which(candidate):
            return candidate
    return ""


def safe_write(path: Path, value: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value + "\n", encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    plugin_root = Path(__file__).resolve().parent.parent
    cwd = Path.cwd()
    python_cmd = detect_python()

    # Runtime breadcrumbs are gitignored and contain no secrets. Shared skill
    # snippets use them to find helpers when Codex runs from an HA config repo.
    if python_cmd:
        safe_write(cwd / ".claude" / "ha-python.txt", python_cmd)
    safe_write(cwd / ".claude" / "ha-plugin-root.txt", str(plugin_root))

    print("Home Assistant Assistant for Codex")

    if not (cwd / "configuration.yaml").is_file():
        print("- configuration.yaml not found in this directory. Run Codex from your Home Assistant config repository.")

    if os.environ.get("HASS_SERVER") and os.environ.get("HASS_TOKEN"):
        print("- hass-cli environment: configured")
    else:
        print("- hass-cli environment: HASS_SERVER or HASS_TOKEN missing. Use $ha-onboard for setup.")

    if os.environ.get("HOMEASSISTANT_URL") and os.environ.get("HOMEASSISTANT_TOKEN"):
        print("- Home Assistant MCP environment: configured")

    if python_cmd:
        print(f"- Python command: {python_cmd}")
    else:
        print("- Python command not found. Some helper workflows need Python.")

    print("- Use $ha-validate before deployment and $ha-deploy only after explicit confirmation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
