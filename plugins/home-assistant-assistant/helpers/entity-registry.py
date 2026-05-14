#!/usr/bin/env python3
"""Entity registry operations for Home Assistant via WebSocket API.

Uses Python websockets library directly because:
  - hass-cli has no `entity delete` command
  - hass-cli `entity update --name ""` doesn't clear name overrides
  - hass-cli `raw ws` is broken on HA 2026.2+ (returns "Unknown command")

Requires: HASS_SERVER and HASS_TOKEN environment variables.
Requires: websockets library (installed with hass-cli's Python).

Usage:
    python entity-registry.py remove <entity_id> [entity_id...]
    python entity-registry.py clear-name <entity_id> [entity_id...]

Examples:
    python entity-registry.py remove sensor.old_stale_entity
    python entity-registry.py remove sensor.stale_1 sensor.stale_2 sensor.stale_3
    python entity-registry.py clear-name sensor.front_yard_sconces_node_status
    python entity-registry.py clear-name light.kitchen_1 light.kitchen_2
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

    # Expect auth_required
    msg = json.loads(await ws.recv())
    if msg.get("type") != "auth_required":
        raise RuntimeError(f"Expected auth_required, got: {msg.get('type')}")

    # Send auth
    await ws.send(json.dumps({"type": "auth", "access_token": token}))

    # Expect auth_ok or auth_invalid
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

    # Read messages until we find our response (id matches)
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
        data = json.loads(raw)
        if data.get("id") == msg_id and data.get("type") == "result":
            return data
        # Ignore other messages (events, pings, etc.)


async def cmd_remove(entity_ids: list[str]) -> None:
    """Remove entities from the entity registry."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    ws_url = build_ws_url(hass_server)

    try:
        ws = await ws_connect_and_auth(ws_url, token)
    except ConnectionRefusedError:
        print(f"Error: Connection refused to {ws_url}")
        print(f"Check that HASS_SERVER ({hass_server}) is correct and reachable.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    succeeded = 0
    failed = 0
    msg_id = 0

    try:
        for entity_id in entity_ids:
            msg_id += 1
            result = await ws_command(
                ws, msg_id, "config/entity_registry/remove",
                entity_id=entity_id,
            )

            if result.get("success"):
                print(f"  Removed: {entity_id}")
                succeeded += 1
            else:
                error = result.get("error", {})
                msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
                print(f"  FAILED:  {entity_id} — {msg}")
                failed += 1
    finally:
        await ws.close()

    print(f"\nDone: {succeeded} removed, {failed} failed (of {len(entity_ids)} total)")
    if failed > 0:
        sys.exit(1)


async def cmd_clear_name(entity_ids: list[str]) -> None:
    """Clear custom name overrides from entities (reverts to device default).

    Sends name=None via config/entity_registry/update, which removes
    the custom name override and lets has_entity_name device inheritance
    take effect.
    """
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    ws_url = build_ws_url(hass_server)

    try:
        ws = await ws_connect_and_auth(ws_url, token)
    except ConnectionRefusedError:
        print(f"Error: Connection refused to {ws_url}")
        print(f"Check that HASS_SERVER ({hass_server}) is correct and reachable.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    succeeded = 0
    failed = 0
    msg_id = 0

    try:
        for entity_id in entity_ids:
            msg_id += 1
            # Send name=None to clear the custom override
            # This lets has_entity_name device inheritance take effect
            message = {
                "id": msg_id,
                "type": "config/entity_registry/update",
                "entity_id": entity_id,
                "name": None,
            }
            await ws.send(json.dumps(message))

            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
                data = json.loads(raw)
                if data.get("id") == msg_id and data.get("type") == "result":
                    break

            if data.get("success"):
                print(f"  Cleared: {entity_id}")
                succeeded += 1
            else:
                error = data.get("error", {})
                msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
                print(f"  FAILED:  {entity_id} — {msg}")
                failed += 1
    finally:
        await ws.close()

    print(f"\nDone: {succeeded} cleared, {failed} failed (of {len(entity_ids)} total)")
    if failed > 0:
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "remove":
        if len(sys.argv) < 3:
            print("Error: remove requires at least one entity_id.")
            print("Usage: entity-registry.py remove <entity_id> [entity_id...]")
            sys.exit(1)
        asyncio.run(cmd_remove(sys.argv[2:]))

    elif command == "clear-name":
        if len(sys.argv) < 3:
            print("Error: clear-name requires at least one entity_id.")
            print("Usage: entity-registry.py clear-name <entity_id> [entity_id...]")
            sys.exit(1)
        asyncio.run(cmd_clear_name(sys.argv[2:]))

    else:
        print(f'Unknown command: "{command}"')
        print("Commands: remove, clear-name")
        sys.exit(1)


if __name__ == "__main__":
    main()
