#!/usr/bin/env python3
"""Lovelace dashboard operations for Home Assistant via WebSocket API.

Provides fetch, save-and-verify, and find-entities operations for
storage-mode dashboards.

Requires: HASS_SERVER and HASS_TOKEN environment variables.
Requires: websockets library (installed with hass-cli's Python).

Usage:
    python lovelace-dashboard.py fetch [url_path]
    python lovelace-dashboard.py save-and-verify <url_path> <config_file>
    python lovelace-dashboard.py find-entities [url_path]

Examples:
    python lovelace-dashboard.py fetch lovelace
    python lovelace-dashboard.py fetch my-dashboard
    python lovelace-dashboard.py save-and-verify my-dashboard config.json
    python lovelace-dashboard.py save-and-verify my-dashboard -
    python lovelace-dashboard.py find-entities my-dashboard
"""

import asyncio
import json
import os
import sys
from urllib.parse import urlparse


def build_ws_url(hass_server: str) -> str:
    """Convert http(s)://host to ws(s)://host/api/websocket."""
    parsed = urlparse(hass_server.rstrip("/"))
    scheme = "wss" if parsed.scheme == "https" else "ws"
    if parsed.path and parsed.path != "/":
        base_path = parsed.path.rstrip("/")
        return f"{scheme}://{parsed.netloc}{base_path}/api/websocket"
    return f"{scheme}://{parsed.netloc}/api/websocket"


async def ws_connect_and_auth(ws_url: str, token: str):
    """Connect to HA WebSocket and authenticate. Returns websocket object."""
    try:
        import websockets
    except ImportError:
        print("Error: websockets library not found. Install: pip install websockets")
        sys.exit(1)

    ws = await websockets.connect(
        ws_url,
        ping_interval=30,
        ping_timeout=10,
        max_size=20 * 1024 * 1024,
    )

    msg = json.loads(await ws.recv())
    if msg.get("type") != "auth_required":
        raise RuntimeError(f"Expected auth_required, got: {msg.get('type')}")

    await ws.send(json.dumps({"type": "auth", "access_token": token}))

    msg = json.loads(await ws.recv())
    if msg.get("type") == "auth_invalid":
        raise RuntimeError("Authentication failed: invalid token")
    if msg.get("type") != "auth_ok":
        raise RuntimeError(f"Expected auth_ok, got: {msg.get('type')}")

    return ws


async def ws_command(ws, msg_id: int, command_type: str, **params) -> dict:
    """Send a command and wait for its result response."""
    message = {"id": msg_id, "type": command_type, **params}
    await ws.send(json.dumps(message))

    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
        data = json.loads(raw)
        if data.get("id") == msg_id and data.get("type") == "result":
            return data


def get_connection_params():
    """Get and validate HASS_SERVER and HASS_TOKEN from environment."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    return hass_server, token


async def connect(hass_server: str, token: str):
    """Connect and authenticate, with error handling."""
    ws_url = build_ws_url(hass_server)
    try:
        return await ws_connect_and_auth(ws_url, token)
    except ConnectionRefusedError:
        print(f"Error: Connection refused to {ws_url}")
        print(f"Check that HASS_SERVER ({hass_server}) is correct and reachable.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def cmd_fetch(url_path: str) -> None:
    """Fetch and print dashboard config as JSON."""
    hass_server, token = get_connection_params()
    ws = await connect(hass_server, token)

    try:
        params = {"force": True}
        if url_path and url_path != "lovelace":
            params["url_path"] = url_path

        result = await ws_command(ws, 1, "lovelace/config", **params)

        if not result.get("success"):
            error = result.get("error", {})
            msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            print(f"Error fetching dashboard '{url_path}': {msg}", file=sys.stderr)
            sys.exit(1)

        config = result.get("result", {})
        print(json.dumps(config, indent=2))
    finally:
        await ws.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "fetch":
        url_path = sys.argv[2] if len(sys.argv) > 2 else "lovelace"
        asyncio.run(cmd_fetch(url_path))

    # save-and-verify and find-entities added in subsequent tasks

    else:
        print(f'Unknown command: "{command}"')
        print("Commands: fetch, save-and-verify, find-entities")
        sys.exit(1)


if __name__ == "__main__":
    main()
