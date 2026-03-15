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


async def cmd_save_and_verify(url_path: str, config_file: str) -> None:
    """Save dashboard config and verify with read-after-write."""
    # Read config from file or stdin
    if config_file == "-":
        config_data = sys.stdin.read()
    else:
        try:
            with open(config_file, "r") as f:
                config_data = f.read()
        except FileNotFoundError:
            print(f"Error: Config file not found: {config_file}", file=sys.stderr)
            sys.exit(1)

    try:
        config = json.loads(config_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)

    hass_server, token = get_connection_params()
    ws = await connect(hass_server, token)
    msg_id = 0

    try:
        # Save config
        msg_id += 1
        save_params = {"config": config}
        if url_path and url_path != "lovelace":
            save_params["url_path"] = url_path

        save_result = await ws_command(ws, msg_id, "lovelace/config/save", **save_params)

        if not save_result.get("success"):
            error = save_result.get("error", {})
            msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            print(f"SAVE FAILED: {msg}", file=sys.stderr)
            sys.exit(1)

        print("Save: OK (result: null — success)")

        # Read-after-write verification
        msg_id += 1
        verify_params = {"force": True}
        if url_path and url_path != "lovelace":
            verify_params["url_path"] = url_path

        verify_result = await ws_command(ws, msg_id, "lovelace/config", **verify_params)

        if not verify_result.get("success"):
            error = verify_result.get("error", {})
            msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            print(f"VERIFY FAILED: Could not re-fetch config: {msg}", file=sys.stderr)
            sys.exit(1)

        fetched_config = verify_result.get("result", {})

        # Compare view count
        saved_views = config.get("views", [])
        fetched_views = fetched_config.get("views", [])

        if len(saved_views) != len(fetched_views):
            print(
                f"VERIFY FAILED: View count mismatch — saved {len(saved_views)}, "
                f"fetched {len(fetched_views)}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Compare view paths (where explicitly set in saved config)
        mismatches = []
        for i, saved_view in enumerate(saved_views):
            saved_path = saved_view.get("path")
            if saved_path is not None and i < len(fetched_views):
                fetched_path = fetched_views[i].get("path")
                if saved_path != fetched_path:
                    mismatches.append(
                        f"  View {i}: saved path='{saved_path}', "
                        f"fetched path='{fetched_path}'"
                    )

        if mismatches:
            print("VERIFY FAILED: View path mismatches:", file=sys.stderr)
            for m in mismatches:
                print(m, file=sys.stderr)
            sys.exit(1)

        print(f"Verify: OK ({len(fetched_views)} views confirmed)")

    finally:
        await ws.close()


def extract_entities(obj) -> set:
    """Recursively extract entity IDs from a dashboard config object."""
    entities = set()

    if isinstance(obj, dict):
        # Direct entity reference
        if "entity" in obj and isinstance(obj["entity"], str):
            entities.add(obj["entity"])

        # Entity list (entities card, etc.)
        if "entities" in obj and isinstance(obj["entities"], list):
            for item in obj["entities"]:
                if isinstance(item, str):
                    entities.add(item)
                elif isinstance(item, dict) and "entity" in item:
                    entities.add(item["entity"])

        # Recurse into nested card structures
        # cards: stacks, grids
        if "cards" in obj and isinstance(obj["cards"], list):
            for card in obj["cards"]:
                entities.update(extract_entities(card))

        # card: conditional card
        if "card" in obj and isinstance(obj["card"], dict):
            entities.update(extract_entities(obj["card"]))

        # elements: picture-elements card
        if "elements" in obj and isinstance(obj["elements"], list):
            for elem in obj["elements"]:
                entities.update(extract_entities(elem))

        # sections: sections view
        if "sections" in obj and isinstance(obj["sections"], list):
            for section in obj["sections"]:
                entities.update(extract_entities(section))

        # badges: view-level entity references
        if "badges" in obj and isinstance(obj["badges"], list):
            for badge in obj["badges"]:
                if isinstance(badge, str):
                    entities.add(badge)
                elif isinstance(badge, dict) and "entity" in badge:
                    entities.add(badge["entity"])

        # views: top-level
        if "views" in obj and isinstance(obj["views"], list):
            for view in obj["views"]:
                entities.update(extract_entities(view))

    return entities


async def cmd_find_entities(url_path: str) -> None:
    """Find all entity IDs referenced in a dashboard."""
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
        entities = extract_entities(config)

        for entity_id in sorted(entities):
            print(entity_id)
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

    elif command == "save-and-verify":
        if len(sys.argv) < 4:
            print("Error: save-and-verify requires <url_path> and <config_file>.")
            print("Usage: lovelace-dashboard.py save-and-verify <url_path> <config_file>")
            sys.exit(1)
        asyncio.run(cmd_save_and_verify(sys.argv[2], sys.argv[3]))

    elif command == "find-entities":
        url_path = sys.argv[2] if len(sys.argv) > 2 else "lovelace"
        asyncio.run(cmd_find_entities(url_path))

    else:
        print(f'Unknown command: "{command}"')
        print("Commands: fetch, save-and-verify, find-entities")
        sys.exit(1)


if __name__ == "__main__":
    main()
