#!/usr/bin/env python3
"""Fetch automation/script traces from Home Assistant via WebSocket API.

Uses Python websockets library directly because:
  - /api/trace REST endpoint does not exist (returns 404)
  - hass-cli raw ws is broken on HA 2026.2+ (returns "Unknown command")

Requires: HASS_SERVER and HASS_TOKEN environment variables.
Requires: websockets library (installed with hass-cli's Python).

Usage:
    python trace-fetch.py list <entity_id>
    python trace-fetch.py get <entity_id> <run_id>

Examples:
    python trace-fetch.py list automation.downstairs_bathroom_motion_light_on
    python trace-fetch.py get automation.motion_light 1705312800.123456-abc
"""

import asyncio
import json
import os
import sys
from urllib.parse import urlparse


def format_timestamp(timestamp: str) -> str:
    """Render an HA timestamp without dropping timezone information."""
    if not timestamp:
        return "?"

    normalized = str(timestamp).replace("T", " ")
    if normalized.endswith("Z"):
        return f"{normalized[:-1]}+00:00"
    return normalized


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


async def resolve_item_id(ws, entity_id: str, object_id: str) -> str:
    """Resolve entity_id to the unique_id used for trace storage.

    HA stores traces by unique_id (not entity_id). Falls back to object_id.
    """
    result = await ws_command(ws, 1, "config/entity_registry/get", entity_id=entity_id)
    if result.get("success") and result.get("result"):
        unique_id = result["result"].get("unique_id")
        if unique_id:
            return unique_id
    return object_id


async def cmd_list(entity_id: str) -> None:
    """List recent traces for an automation or script."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    # Determine domain
    if entity_id.startswith("automation."):
        domain = "automation"
    elif entity_id.startswith("script."):
        domain = "script"
    else:
        print(f"Error: entity_id must start with 'automation.' or 'script.' — got: {entity_id}")
        sys.exit(1)

    object_id = entity_id.split(".", 1)[1]
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

    try:
        item_id = await resolve_item_id(ws, entity_id, object_id)

        result = await ws_command(ws, 2, "trace/list", domain=domain, item_id=item_id)

        if not result.get("success"):
            error = result.get("error", {})
            print(f"Error from HA: {error.get('message', error)}")
            sys.exit(1)

        traces = result.get("result", [])

        if not traces:
            print(f"No traces found for {entity_id}.")
            print("Possible reasons:")
            print("  - Automation has never run")
            print("  - Automation lacks an 'id:' field (required for trace storage)")
            print("  - Traces cleared on HA restart (traces are in-memory)")
            print("  - stored_traces set to 0 in automation config")
            return

        print(f"Traces for {entity_id} ({len(traces)} found):\n")
        print(f"{'run_id':<40}  {'timestamp':<30}  {'state':<10}  trigger")
        print("-" * 100)
        for t in traces:
            run_id = str(t.get("run_id", "?"))
            # timestamp is a dict with start/finish keys; show start for list view
            ts_raw = t.get("timestamp", {})
            if isinstance(ts_raw, dict):
                timestamp = format_timestamp(ts_raw.get("start", str(ts_raw)))
            else:
                timestamp = format_timestamp(str(ts_raw))
            state = str(t.get("state", "?"))
            trigger = str(t.get("trigger", ""))
            print(f"{run_id:<40}  {timestamp:<30}  {state:<10}  {trigger}")

    finally:
        await ws.close()


async def cmd_get(entity_id: str, run_id: str) -> None:
    """Get full trace data for a specific run."""
    hass_server = os.environ.get("HASS_SERVER", "").rstrip("/")
    token = os.environ.get("HASS_TOKEN", "")

    if not hass_server or not token:
        print("Error: HASS_SERVER and HASS_TOKEN environment variables must be set.")
        print("Run /ha-onboard to configure.")
        sys.exit(1)

    # Determine domain
    if entity_id.startswith("automation."):
        domain = "automation"
    elif entity_id.startswith("script."):
        domain = "script"
    else:
        print(f"Error: entity_id must start with 'automation.' or 'script.' — got: {entity_id}")
        sys.exit(1)

    object_id = entity_id.split(".", 1)[1]
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

    try:
        item_id = await resolve_item_id(ws, entity_id, object_id)

        result = await ws_command(
            ws, 2, "trace/get", domain=domain, item_id=item_id, run_id=run_id
        )

        if not result.get("success"):
            error = result.get("error", {})
            msg = error.get("message", str(error)) if isinstance(error, dict) else str(error)
            print(f"Error from HA: {msg}")
            if "not found" in msg.lower():
                print(f"Hint: run_id '{run_id}' may be expired or incorrect.")
                print(f"      Use 'list {entity_id}' to see available run_ids.")
            sys.exit(1)

        trace_data = result.get("result", {})
        # Full trace is too complex for tabular display — print as formatted JSON
        print(json.dumps(trace_data, indent=2, default=str))

    finally:
        await ws.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        if len(sys.argv) < 3:
            print("Error: list requires an entity_id.")
            print("Usage: trace-fetch.py list <entity_id>")
            sys.exit(1)
        asyncio.run(cmd_list(sys.argv[2]))

    elif command == "get":
        if len(sys.argv) < 4:
            print("Error: get requires entity_id and run_id.")
            print("Usage: trace-fetch.py get <entity_id> <run_id>")
            sys.exit(1)
        asyncio.run(cmd_get(sys.argv[2], sys.argv[3]))

    else:
        print(f'Unknown command: "{command}"')
        print("Commands: list, get")
        sys.exit(1)


if __name__ == "__main__":
    main()
