# Lovelace & Dashboard PR 1 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add storage-mode dashboard support to ha-lovelace — save contract enforcement, sections view mutation rules, entity preflight validation, and custom-card research workflow.

**Architecture:** Four new/modified files. A Python WebSocket helper (`lovelace-dashboard.py`) handles dashboard fetch/save/verify operations with deterministic exit codes. A WebSocket API reference (`dashboard-api.md`) documents the contract. A card/layout reference (`dashboard-guide.md`) adapted from ha-mcp replaces outdated card examples. SKILL.md is restructured: reference material moves out, four new workflow sections added.

**Tech Stack:** Python 3 (websockets library), Markdown, JSON eval harness

**Spec:** `docs/superpowers/specs/2026-03-14-lovelace-dashboard-pr1-design.md`

---

## Chunk 1: Helper + API Reference

### Task 1: Create `lovelace-dashboard.py` with `fetch` subcommand

**Files:**
- Create: `helpers/lovelace-dashboard.py`

- [ ] **Step 1: Create helper with boilerplate and `fetch` subcommand**

Copy WebSocket boilerplate from `helpers/entity-registry.py` (`build_ws_url`, `ws_connect_and_auth`, `ws_command`) and add the `fetch` command.

```python
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
```

- [ ] **Step 2: Verify Python syntax**

Run: `python -c "import py_compile; py_compile.compile('helpers/lovelace-dashboard.py', doraise=True)"`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add helpers/lovelace-dashboard.py
git commit -m "feat(helper): add lovelace-dashboard.py with fetch subcommand"
```

---

### Task 2: Add `save-and-verify` subcommand

**Files:**
- Modify: `helpers/lovelace-dashboard.py`

- [ ] **Step 1: Add `save-and-verify` function**

Add after the `cmd_fetch` function:

```python
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
```

- [ ] **Step 2: Add command dispatch for `save-and-verify`**

In the `main()` function, replace the comment placeholder with:

```python
    elif command == "save-and-verify":
        if len(sys.argv) < 4:
            print("Error: save-and-verify requires <url_path> and <config_file>.")
            print("Usage: lovelace-dashboard.py save-and-verify <url_path> <config_file>")
            sys.exit(1)
        asyncio.run(cmd_save_and_verify(sys.argv[2], sys.argv[3]))
```

- [ ] **Step 3: Verify Python syntax**

Run: `python -c "import py_compile; py_compile.compile('helpers/lovelace-dashboard.py', doraise=True)"`
Expected: No output (success)

- [ ] **Step 4: Commit**

```bash
git add helpers/lovelace-dashboard.py
git commit -m "feat(helper): add save-and-verify subcommand with read-after-write verification"
```

---

### Task 3: Add `find-entities` subcommand

**Files:**
- Modify: `helpers/lovelace-dashboard.py`

- [ ] **Step 1: Add entity extraction function and `find-entities` command**

Add after `cmd_save_and_verify`:

```python
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
```

- [ ] **Step 2: Add command dispatch for `find-entities`**

In the `main()` function, add before the `else` clause:

```python
    elif command == "find-entities":
        url_path = sys.argv[2] if len(sys.argv) > 2 else "lovelace"
        asyncio.run(cmd_find_entities(url_path))
```

- [ ] **Step 3: Verify Python syntax**

Run: `python -c "import py_compile; py_compile.compile('helpers/lovelace-dashboard.py', doraise=True)"`
Expected: No output (success)

- [ ] **Step 4: Test `extract_entities` with inline JSON**

Run:
```bash
python -c "
from helpers import lovelace_dashboard
# Can't import directly due to hyphens in filename, test extract_entities logic
import importlib.util, sys
spec = importlib.util.spec_from_file_location('ld', 'helpers/lovelace-dashboard.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

config = {
    'views': [{
        'type': 'sections',
        'badges': ['person.john', {'entity': 'sensor.temp'}],
        'sections': [{'cards': [
            {'type': 'tile', 'entity': 'light.kitchen'},
            {'type': 'entities', 'entities': ['sensor.a', {'entity': 'sensor.b'}]},
            {'type': 'vertical-stack', 'cards': [
                {'type': 'conditional', 'card': {'type': 'tile', 'entity': 'lock.front'}},
                {'type': 'picture-elements', 'elements': [{'entity': 'light.hall'}]}
            ]}
        ]}]
    }]
}
result = sorted(mod.extract_entities(config))
expected = ['light.hall', 'light.kitchen', 'lock.front', 'person.john', 'sensor.a', 'sensor.b', 'sensor.temp']
assert result == expected, f'Got: {result}'
print('extract_entities: PASS')
"
```
Expected: `extract_entities: PASS`

- [ ] **Step 5: Commit**

```bash
git add helpers/lovelace-dashboard.py
git commit -m "feat(helper): add find-entities subcommand with recursive card traversal"
```

---

### Task 4: Create `references/dashboard-api.md`

**Files:**
- Create: `references/dashboard-api.md`

- [ ] **Step 1: Write the API contract reference**

```markdown
# Storage Dashboard WebSocket API Contract

Reference for storage-mode Lovelace dashboard operations via the Home Assistant WebSocket API.

> This is a pure reference document. For operational workflows, see `skills/ha-lovelace/SKILL.md`.

## WebSocket Commands

| Command | Purpose | Success Response | Failure Response |
|---------|---------|-----------------|-----------------|
| `lovelace/config` | Fetch dashboard config | `{success: true, result: {views: [...]}}` | `{success: false, error: {code, message}}` |
| `lovelace/config/save` | Save dashboard config | `{success: true, result: null}` | `{success: false, error: {code, message}}` |
| `lovelace/dashboards/list` | List all storage dashboards | `{success: true, result: [...]}` | -- |

## Key Fields

- **`url_path`**: Identifies the target dashboard. Omit or use `"lovelace"` for the default dashboard.
- **`force: true`**: On fetch commands, bypasses HA's config cache to get current state. Always use this after saves.

## Critical: Save Response Contract

A successful `lovelace/config/save` returns:

```json
{"id": 1, "type": "result", "success": true, "result": null}
```

**`result: null` is correct** — it is NOT an error. This is the expected success response.

A failed save returns:

```json
{"id": 1, "type": "result", "success": false, "error": {"code": 3, "message": "..."}}
```

The `error` object contains:
- `code` (integer): Error code (e.g., 3 for invalid config)
- `message` (string): Human-readable error description

## Dashboard Identity

- **`url_path`**: URL-facing identifier used in dashboard URLs (e.g., `/lovelace/my-dashboard`)
- **`dashboard_id`**: Internal identifier returned on dashboard creation
- New dashboard `url_path` values must be valid slugs: lowercase, alphanumeric, hyphens, and underscores. Convention: use hyphens for readability (e.g., `my-dashboard`).
- `"lovelace"` and `"default"` both target the built-in default dashboard.

## Fetch Example

```json
{"id": 1, "type": "lovelace/config", "url_path": "my-dashboard", "force": true}
```

Response:
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "views": [
      {
        "title": "Overview",
        "path": "home",
        "type": "sections",
        "sections": [...]
      }
    ]
  }
}
```

## Save Example

```json
{"id": 2, "type": "lovelace/config/save", "url_path": "my-dashboard", "config": {"views": [...]}}
```

Response (success):
```json
{"id": 2, "type": "result", "success": true, "result": null}
```

## Helper

The plugin provides `helpers/lovelace-dashboard.py` for programmatic dashboard operations with built-in save verification. See the helper's docstring for usage.
```

- [ ] **Step 2: Commit**

```bash
git add references/dashboard-api.md
git commit -m "docs: add WebSocket API contract reference for storage dashboards"
```

---

## Chunk 2: Dashboard Guide Reference

### Task 5: Create `skills/ha-lovelace/references/dashboard-guide.md`

**Files:**
- Create: `skills/ha-lovelace/references/dashboard-guide.md`

This is the largest single deliverable. Adapt content from `~/dev/ha-mcp/src/ha_mcp/resources/dashboard_guide.md`, converting to YAML examples, removing MCP-specific tool references, and adding `grid_options.rows` sizing guidance from BL-020.

- [ ] **Step 1: Create the references directory**

```bash
mkdir -p skills/ha-lovelace/references
```

- [ ] **Step 2: Write the dashboard guide**

Read `C:\Users\Ben\dev\ha-mcp\src\ha_mcp\resources\dashboard_guide.md` for source content, then create the adapted version:

```markdown
# Dashboard Guide

Card types, layout options, and examples for Home Assistant Lovelace dashboards.

> **Note:** Storage-mode dashboards use JSON internally (via WebSocket API). Examples below use YAML for readability and consistency with YAML-mode dashboards. When working with storage-mode dashboards, the JSON equivalent applies.

## Dashboard Structure

Modern Home Assistant dashboards (2024+) use:
- **Sections view type** (recommended) with grid-based layouts
- **Tile cards** with integrated features for quick controls
- **Grid cards** for organizing content into columns
- **Multiple views** with navigation and deep linking

Legacy patterns to avoid:
- Single-view dashboards with all cards in one long scroll
- Excessive vertical-stack/horizontal-stack instead of grid
- Masonry view (auto-layout) — use sections for precise control
- Putting all entities in generic "entities" cards

### View Types

| Type | Use For |
|------|---------|
| `sections` | Most dashboards (RECOMMENDED) — grid-based, responsive |
| `panel` | Full-screen single cards (maps, cameras, iframes) |
| `sidebar` | Two-column layouts with primary/secondary content |
| `masonry` | Legacy — auto-arranges cards, less control |

### View Configuration

```yaml
views:
  - title: Overview
    path: home
    type: sections
    icon: mdi:home
    max_columns: 4
    badges:
      - entity: person.john
      - entity: sensor.temperature
    sections:
      - title: Climate
        cards: []
      - title: Lights
        cards: []
```

### Sections and Grid Sizing

**`max_columns`** controls how many section columns render:

| Content type | Recommended `max_columns` |
|---|---|
| Tile cards (compact) | 4 |
| Custom cards with legends (mini-graph-card, apexcharts) | 3 |
| Dense multi-entity cards | 2-3 |

**`grid_options.rows`** controls card height within sections:

| Card content | Recommended `rows` |
|---|---|
| Single entity, no extras | 1 (default) |
| Entity with legend or name | 2 |
| Multi-entity with legend + extrema | 3 |
| Graph card with 3+ entities | 3-4 |

Example with explicit sizing:

```yaml
type: custom:mini-graph-card
entities:
  - sensor.living_room_temperature
  - sensor.bedroom_temperature
  - sensor.kitchen_temperature
grid_options:
  columns: 12
  rows: 3
```

---

## Built-in Cards

### Card Categories

| Category | Cards |
|----------|-------|
| **Modern Primary** | tile, area, button, grid |
| **Container** | vertical-stack, horizontal-stack, grid |
| **Logic** | conditional, entity-filter |
| **Display** | sensor, history-graph, statistics-graph, gauge, energy, calendar |
| **Content** | markdown (supports Jinja2 templates), picture-elements, map |
| **Legacy Control** | entity, entities, light, thermostat (use tile instead) |

**Recommendation:** Use `tile` card for most entities.

### Tile Card (Modern Entity Control)

```yaml
type: tile
entity: climate.bedroom
name: Master Bedroom
icon: mdi:thermostat
features:
  - type: target-temperature
  - type: climate-hvac-modes
    style: dropdown
tap_action:
  action: more-info
```

### Grid Card (Layout Tool)

```yaml
type: grid
columns: 3
square: false
cards:
  - type: tile
    entity: light.kitchen
  - type: tile
    entity: light.dining
  - type: tile
    entity: light.hallway
```

### Features (Quick Controls)

Available on: tile, area, humidifier, thermostat cards.

**Climate:** climate-hvac-modes, climate-fan-modes, climate-preset-modes, target-temperature
**Light:** light-brightness, light-color-temp
**Cover:** cover-open-close, cover-position, cover-tilt
**Fan:** fan-speed, fan-direction, fan-oscillate
**Media:** media-player-playback, media-player-volume-slider
**Other:** toggle, button, alarm-modes, lock-commands, numeric-input

Feature `style` options: `dropdown` or `icons`

### Actions

```yaml
tap_action:
  action: toggle

hold_action:
  action: more-info

double_tap_action:
  action: navigate
  navigation_path: /lovelace/lights
```

Action types: `toggle`, `call-service`, `more-info`, `navigate`, `url`, `none`

### Visibility Conditions

```yaml
visibility:
  - condition: user
    users:
      - abc123def456
  - condition: state
    entity: sun.sun
    state: above_horizon
```

### Conditional Card

```yaml
type: conditional
conditions:
  - entity: input_boolean.show_details
    state: "on"
card:
  type: entities
  entities:
    - sensor.details
```

### Markdown Card (Supports Jinja2)

The Markdown Card is one of the few native cards that renders Jinja2 templates server-side:

```yaml
type: markdown
title: Welcome
content: |
  ## Good {{ 'morning' if now().hour < 12 else 'afternoon' }}!
  Temperature: {{ states('sensor.temperature') }}°F
```

Other cards do NOT support Jinja2 — see `ha-jinja` skill for alternatives.

### History Graph and Statistics

```yaml
type: history-graph
title: Temperature History
hours_to_show: 24
entities:
  - entity: sensor.temperature
  - entity: sensor.humidity
```

```yaml
type: statistics-graph
title: Weekly Temperature
entities:
  - sensor.temperature
period: day
days_to_show: 7
stat_types:
  - mean
  - min
  - max
```

### Gauge Card

```yaml
type: gauge
entity: sensor.cpu_usage
name: CPU
min: 0
max: 100
severity:
  green: 0
  yellow: 50
  red: 80
```

---

## Custom Cards

### Using Custom Cards

Custom cards use the `custom:` prefix:

```yaml
type: custom:mini-graph-card
entity: sensor.temperature
```

### Post-Install Availability

After installing a custom card via HACS, the HA frontend must reload before the card type is recognized. The user should:
1. Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
2. If that doesn't work, restart Home Assistant

### Popular HACS Cards

| Card | Repository | Use For |
|------|-----------|---------|
| **Mushroom** | piitaya/lovelace-mushroom | Modern, clean card collection (chips, title, template, etc.) |
| **mini-graph-card** | kalkih/mini-graph-card | Compact sensor graphs with extrema, legends |
| **button-card** | custom-cards/button-card | Highly customizable buttons with templates |
| **card-mod** | thomasloven/lovelace-card-mod | CSS styling for any card |
| **apexcharts-card** | RomRider/apexcharts-card | Professional charts and graphs |
| **layout-card** | thomasloven/lovelace-layout-card | Advanced layout control |

### Custom Card Option Pitfall

Each custom card has its own configuration schema. Do NOT guess option names from other cards — always check the card's README for supported options.

---

## CSS Styling

### Theme Variables

```yaml
# In configuration.yaml
frontend:
  themes:
    my_theme:
      primary-color: "#1E88E5"
      accent-color: "#FF4081"
      card-background-color: "#333"
```

### card-mod (Per-Card Styling)

Requires the card-mod HACS component:

```yaml
type: entities
card_mod:
  style: |
    ha-card {
      --ha-card-background: teal;
      color: var(--primary-color);
    }
entities:
  - light.bed_light
```

---

## HACS Integration

HACS (Home Assistant Community Store) provides 700+ custom cards.

### When to Use HACS vs Built-in

| Use Case | Solution |
|----------|----------|
| Popular community card | HACS install |
| Minor CSS tweaks | card-mod + theme variables |
| Standard entity display | Built-in tile/grid cards |

### Checking Installed HACS Cards

```bash
# List installed frontend resources
hass-cli raw get /api/lovelace/resources
```

---

## Complete Examples

### Multi-View Sections Dashboard

```yaml
title: My Home
views:
  - title: Overview
    path: home
    type: sections
    icon: mdi:home
    max_columns: 4
    badges:
      - entity: person.john
      - entity: person.jane
    sections:
      - title: Quick Actions
        cards:
          - type: grid
            columns: 4
            square: false
            cards:
              - type: button
                name: Lights
                icon: mdi:lightbulb
                tap_action:
                  action: navigate
                  navigation_path: /lovelace/lights
              - type: button
                name: Climate
                icon: mdi:thermostat
                tap_action:
                  action: navigate
                  navigation_path: /lovelace/climate
      - title: Favorites
        cards:
          - type: grid
            columns: 3
            square: false
            cards:
              - type: tile
                entity: light.living_room
                features:
                  - type: light-brightness
              - type: tile
                entity: climate.bedroom
                features:
                  - type: target-temperature
              - type: tile
                entity: lock.front_door

  - title: Lights
    path: lights
    type: sections
    icon: mdi:lightbulb
    max_columns: 3
    sections:
      - title: Living Room
        cards:
          - type: grid
            columns: 3
            cards:
              - type: tile
                entity: light.overhead
                features:
                  - type: light-brightness
              - type: tile
                entity: light.lamp
                features:
                  - type: light-brightness
              - type: tile
                entity: light.accent
                features:
                  - type: light-color-temp
```

### Dashboard Organization Patterns

**By Room:**
```yaml
views:
  - title: Living Room
    path: living-room
  - title: Kitchen
    path: kitchen
  - title: Bedroom
    path: bedroom
```

**By Function:**
```yaml
views:
  - title: Lights
    path: lights
  - title: Climate
    path: climate
  - title: Security
    path: security
```

**By User (visibility control):**
```yaml
views:
  - title: Overview
    path: home
  - title: Admin
    path: admin
    visible:
      - user: admin_user_id
```

- [ ] **Step 3: Commit**

```bash
git add skills/ha-lovelace/references/dashboard-guide.md
git commit -m "docs: add dashboard guide reference adapted from ha-mcp"
```

---

## Chunk 3: SKILL.md Restructure + Eval Cases

### Task 6: Restructure SKILL.md — move reference content out, add new sections

**Files:**
- Modify: `skills/ha-lovelace/SKILL.md`

This is the core task. We'll replace the current file contents with the restructured version that:
1. Updates frontmatter (`allowed-tools` adds Bash)
2. Keeps Jinja warning, organization guidance, and mode overview
3. Removes card reference content (now in `references/dashboard-guide.md`)
4. Adds four new workflow sections (BL-021, BL-019, BL-020, BL-022)

- [ ] **Step 1: Read current SKILL.md**

Read: `skills/ha-lovelace/SKILL.md`
Note current structure and content for reference.

- [ ] **Step 2: Write the restructured SKILL.md**

Replace the entire file with:

```markdown
---
name: ha-lovelace
description: This skill should be used when the user asks about "dashboard", "lovelace", "card", "view", "theme", "UI", mentions dashboard design, card configuration, dashboard layout, or needs help with Home Assistant Lovelace dashboard creation and customization.
user-invocable: true
version: 0.2.0
allowed-tools: Read, Grep, Glob, Bash(hass-cli:*,python*,py:*)
---

# Home Assistant Lovelace Dashboards

This skill provides workflow procedures for creating and managing Lovelace dashboards.

For card types, layout options, and examples, read `references/dashboard-guide.md`.

## Important: Templating in Lovelace

**Most Lovelace cards do NOT support Jinja2 templating.**

If you type `{{ states('sensor.x') }}` in an Entities card, Button card, or most other cards,
it will display as literal text — NOT the sensor value.

**Exception: Markdown Card** — renders templates server-side.

For dynamic values in other cards:
1. **Template entities** — create a template sensor/binary_sensor, display that entity
2. **Custom cards** — install cards like `button-card` that implement their own templating

See `ha-jinja` skill for templating reference.

## Dashboard Modes

### YAML Mode
File-managed dashboards deployed via git. Edit `ui-lovelace.yaml` (or per-dashboard YAML files) and deploy with `/ha-deploy`.

```yaml
# configuration.yaml
lovelace:
  mode: yaml
  resources:
    - url: /local/card.js
      type: module
```

### Storage Mode
UI-managed dashboards mutated via the WebSocket API. Use `helpers/lovelace-dashboard.py` for programmatic operations. See `references/dashboard-api.md` for the API contract.

## Dashboard Organization

Organize dashboards by room, function, or user — see `references/dashboard-guide.md` for examples of each pattern.

**General principles:**
- Group related entities in the same section
- Use consistent icon families (mdi:)
- Design for smallest screen first (mobile-first)
- Prefer more views over cluttered views
- Use conditional cards to hide irrelevant information

---

## Entity Preflight Validation

> Addresses BL-021: Dashboard entity preflight validation.

**Before any dashboard save that adds or changes entity references, validate every entity ID.**

### Workflow

1. **Extract entity IDs** from the proposed dashboard config. During in-progress editing, scan the JSON directly. For auditing existing dashboards:
   ```bash
   PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
   PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt)"
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" find-entities <url_path>
   ```

2. **Validate each entity** against live state:
   ```bash
   hass-cli state get <entity_id>
   ```
   If "not found", resolve using `ha-resolver` patterns (area search, name search, capability snapshot).

3. **Suggest corrections** for near-misses. Common pattern: abbreviated entity name vs full device-qualified name (e.g., `sensor.fan_vent_temperature` → `sensor.upstairs_hallway_whole_house_fan_temperature`).

4. **Do NOT save until all entities resolve.** A single wrong entity renders the card as "Entity not found" in the UI.

---

## Storage Dashboard Save Contract

> Addresses BL-019: Storage-mode dashboard save contract with success/failure detection.

**Every storage-mode dashboard mutation MUST follow this workflow.**

### Mandatory Save Workflow

1. **Fetch current config:**
   ```bash
   PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
   PLUGIN_ROOT="$(cat .claude/ha-plugin-root.txt)"
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" fetch <url_path> > current.json
   ```

2. **Modify the JSON** — edit `current.json` with the desired changes.

3. **Save and verify:**
   ```bash
   "$PY" "$PLUGIN_ROOT/helpers/lovelace-dashboard.py" save-and-verify <url_path> current.json
   ```

4. **Check exit code:**
   - Exit 0 = save confirmed (view count and paths verified)
   - Exit non-zero = **save failed or verification failed — do NOT claim success**

5. **Visual verification:** Ask the user to open the dashboard URL in their browser and confirm it renders correctly.

### Common Mistake

A successful save returns `result: null`. This is correct — **null is not an error**. A failure returns `success: false` with an `error` object. See `references/dashboard-api.md` for full response format.

---

## Sections View Mutation Rules

> Addresses BL-020: Sections view safe-edit playbook.

### One Section at a Time

**Never replace the entire `sections` array in a single save.** Instead:

1. Fetch current config
2. Modify ONE section (add, edit, or remove)
3. Save and verify
4. Confirm the view renders correctly
5. Proceed to the next section

Bulk section replacement risks validation conflicts and blank views.

### `max_columns` Tuning

| Content type | Recommended `max_columns` |
|---|---|
| Tile cards (compact) | 4 |
| Custom cards with legends | 3 |
| Dense multi-entity cards | 2-3 |

Overly wide layouts cause cards to render too narrow, especially custom cards with legends or multiple entities.

### `grid_options.rows` Sizing

| Card content | Recommended `rows` |
|---|---|
| Single entity, no extras | 1 (default) |
| Entity with legend or name | 2 |
| Multi-entity with legend + extrema | 3 |
| Graph card with 3+ entities | 3-4 |

If legends overlap or cards look cramped, increase `rows`.

### Blank View Recovery

If a structural edit produces a blank view:
1. The sections array is likely malformed
2. Re-fetch the current config from HA (it may have reverted)
3. Compare against the last known-good state
4. Fix the structure and re-save

### Visual Verification

After EVERY structural mutation, ask the user to verify the view renders before making the next change. Do not batch structural changes.

---

## Custom Card Research Workflow

> Addresses BL-022: Stable workflow for researching custom card capabilities.

### Documentation Lookup Order

When the user asks about custom card options or capabilities, follow this stable fallback order:

1. **Plugin reference first:** Check `references/dashboard-guide.md` popular cards section for common cards (Mushroom, mini-graph-card, button-card, card-mod, apexcharts-card, layout-card).

2. **HACS / installed resources:** Check what's installed:
   ```bash
   hass-cli raw get /api/lovelace/resources
   ```

3. **GitHub API:** Fetch the card's README directly:
   ```bash
   gh api repos/<owner>/<repo>/readme --jq .content | base64 -d
   ```
   Examples:
   - `gh api repos/kalkih/mini-graph-card/readme --jq .content | base64 -d`
   - `gh api repos/piitaya/lovelace-mushroom/readme --jq .content | base64 -d`

4. **Web search (last resort):** Only if the above fail or return rate-limited responses.

### Post-Install Availability

After installing a custom card via HACS, the HA frontend must reload before the new card type is recognized:
1. Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
2. If that doesn't work, restart Home Assistant

Do NOT attempt to use a newly installed card type in a dashboard save until the user confirms the frontend has reloaded.

### Common Mistake

Each custom card has its own configuration schema. Do NOT guess option names based on other cards or built-in cards. Always check the card's README for supported options.
```

- [ ] **Step 3: Verify the file renders correctly**

Read the written file back to confirm structure and completeness.

- [ ] **Step 4: Commit**

```bash
git add skills/ha-lovelace/SKILL.md
git commit -m "feat(ha-lovelace): restructure SKILL.md with storage-mode workflows

Move card reference content to references/dashboard-guide.md.
Add four new workflow sections:
- Entity Preflight Validation (BL-021)
- Storage Dashboard Save Contract (BL-019)
- Sections View Mutation Rules (BL-020)
- Custom Card Research Workflow (BL-022)

Update allowed-tools to include Bash for helper and hass-cli access."
```

---

### Task 7: Add regression eval cases

**Files:**
- Modify: `dev/testing/evals/regression/phase3-findings-regression.json`

- [ ] **Step 1: Read current regression eval cases**

Read: `dev/testing/evals/regression/phase3-findings-regression.json`
Note the existing case structure and last ID used.

- [ ] **Step 2: Add eval cases for the new content**

Append these cases to the `cases` array:

```json
    {
      "id": "REG-014",
      "name": "ha-lovelace allowed-tools includes Bash",
      "description": "SKILL.md must allow Bash for helper and hass-cli access after BL-019/BL-021.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "Bash(hass-cli:*,python*,py:*)"
        }
      ]
    },
    {
      "id": "REG-015",
      "name": "ha-lovelace references dashboard-guide",
      "description": "SKILL.md must reference the dashboard-guide.md for card types and layout.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "references/dashboard-guide.md"
        }
      ]
    },
    {
      "id": "REG-016",
      "name": "ha-lovelace save contract requires lovelace-dashboard.py",
      "description": "SKILL.md save workflow must use the helper, not ad hoc WebSocket calls.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "lovelace-dashboard.py"
        },
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "save-and-verify"
        }
      ]
    },
    {
      "id": "REG-017",
      "name": "ha-lovelace entity preflight before save",
      "description": "SKILL.md must require entity validation before dashboard saves.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "Do NOT save until all entities resolve"
        }
      ]
    },
    {
      "id": "REG-018",
      "name": "ha-lovelace sections one-at-a-time rule",
      "description": "SKILL.md must prohibit bulk section replacement.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "Never replace the entire"
        }
      ]
    },
    {
      "id": "REG-019",
      "name": "ha-lovelace custom card fallback order",
      "description": "SKILL.md must define a stable documentation lookup order for custom cards.",
      "checks": [
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "Plugin reference first"
        },
        {
          "path": "skills/ha-lovelace/SKILL.md",
          "contains": "GitHub API"
        }
      ]
    },
    {
      "id": "REG-020",
      "name": "dashboard-api.md documents null success contract",
      "description": "The API reference must document that null result on save is success.",
      "checks": [
        {
          "path": "references/dashboard-api.md",
          "contains": "result: null"
        },
        {
          "path": "references/dashboard-api.md",
          "contains": "NOT an error"
        }
      ]
    },
    {
      "id": "REG-021",
      "name": "lovelace-dashboard.py has all three subcommands",
      "description": "Helper must expose fetch, save-and-verify, and find-entities.",
      "checks": [
        {
          "path": "helpers/lovelace-dashboard.py",
          "contains": "cmd_fetch"
        },
        {
          "path": "helpers/lovelace-dashboard.py",
          "contains": "cmd_save_and_verify"
        },
        {
          "path": "helpers/lovelace-dashboard.py",
          "contains": "cmd_find_entities"
        }
      ]
    },
    {
      "id": "REG-022",
      "name": "dashboard-guide.md covers grid_options.rows sizing",
      "description": "Dashboard guide must include the rows sizing table from BL-020.",
      "checks": [
        {
          "path": "skills/ha-lovelace/references/dashboard-guide.md",
          "contains": "grid_options"
        },
        {
          "path": "skills/ha-lovelace/references/dashboard-guide.md",
          "contains": "Recommended `rows`"
        }
      ]
    }
```

- [ ] **Step 3: Verify JSON syntax**

Run: `python -c "import json; json.load(open('dev/testing/evals/regression/phase3-findings-regression.json'))"`
Expected: No output (valid JSON)

- [ ] **Step 4: Run eval harness**

Run:
```powershell
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite regression -Passes 1
```
Expected: All new cases (REG-014 through REG-022) pass.

- [ ] **Step 5: Commit**

```bash
git add dev/testing/evals/regression/phase3-findings-regression.json
git commit -m "test: add regression eval cases for lovelace dashboard PR 1 (REG-014–022)"
```

---

### Task 8: Final verification

- [ ] **Step 1: Run full eval harness**

```powershell
powershell -ExecutionPolicy Bypass -File dev/testing/scripts/eval-harness.ps1 -Suite all -Passes 1
```
Expected: All suites pass (both capability and regression).

- [ ] **Step 2: Verify file structure**

Confirm all expected files exist:
```bash
ls -la helpers/lovelace-dashboard.py references/dashboard-api.md skills/ha-lovelace/references/dashboard-guide.md skills/ha-lovelace/SKILL.md
```

- [ ] **Step 3: Review git log**

```bash
git log --oneline lovelace-dashboard-pr1 --not main
```
Expected: 8 commits (spec + 7 implementation commits).
