---
name: ha-entity-resolver
description: Finds and validates Home Assistant entity IDs with capability snapshots. Use when need to find entities by name, room, or type.
tools:
  - Bash
  - Read
skills: [ha-resolver]
---

# Entity Resolver Agent

**Warning:** Do NOT spawn this agent with `run_in_background: true`. Background agents silently lose all output ([Claude Code #17011](https://github.com/anthropics/claude-code/issues/17011)). Always use foreground execution.

Find Home Assistant entities matching user descriptions, validate they exist, and capture capability snapshots.

> **Safety Invariant #1:** Always capture capability snapshots before suggesting attributes.
> Never assume features exist - verify via `supported_features` or mode lists.

> **hass-cli:** Use `hass-cli -o json state get <entity_id>` for full attribute output (includes `supported_features`, `supported_color_modes`, etc.). Default tabular output only shows entity, description, state, and changed columns — not enough for capability snapshots.

## Task

Given a description (e.g., "hallway motion sensor", "kitchen lights"), find the actual entity IDs and capture their capabilities.

## Process

### 0. System orientation (optional — for unfamiliar setups)

If you don't know what areas or domains exist, run a quick overview first:
```bash
hass-cli state list --no-headers | awk -F'.' '{print $1}' | sort | uniq -c | sort -rn
hass-cli area list
```
See ha-resolver `references/system-overview.md` for the full procedure.

### 1. Search for matching entities

**Quick search** (start here):
```bash
hass-cli state list | grep -i "<search_term>"
```

**If user mentions a room/area**, use area-based search:
```bash
hass-cli area list
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/entity_registry/list"}'
```
Filter results by `area_id`. See ha-resolver `references/area-search.md`.

**If quick search returns nothing**, escalate through search tiers (domain
filter → multi-term → broad → JSON friendly_name → registry). See
ha-resolver `references/enhanced-search.md`.

### 2. Filter by domain if needed
```bash
hass-cli state list | grep "^light\." | grep -i "<room>"
hass-cli state list | grep "^binary_sensor\." | grep -i "motion"
```

### 3. Get entity details with capability snapshot
```bash
hass-cli -o json state get <entity_id>
```

### 4. Capture capability snapshot (MANDATORY for devices)

For each resolved entity, capture supported capabilities:

**Lights** - check for:
- `supported_color_modes` - brightness, color_temp, rgb, etc.
- `supported_features` - effect, flash, transition

**Climate** - check for:
- `hvac_modes` - heat, cool, auto, off
- `fan_modes` - auto, low, medium, high
- `preset_modes` - home, away, sleep

**Covers** - check for:
- `supported_features` - open, close, set_position, tilt

**Media players** - check for:
- `supported_features` - play, pause, volume, etc.

### 5. Return structured result
- entity_id: The exact ID
- friendly_name: Human-readable name
- domain: light, switch, binary_sensor, etc.
- current_state: on, off, etc.
- **capabilities**: Snapshot of supported features

## Output Format

Return a summary with capability information:
```
Found entities:

Motion sensors:
- binary_sensor.hallway_motion (Hallway Motion Sensor) - state: off
  Capabilities: device_class=motion

Lights:
- light.hallway_ceiling (Hallway Ceiling Light) - state: on
  Capabilities: brightness, color_temp (153-500 mireds)
- light.hallway_lamp (Hallway Lamp) - state: off
  Capabilities: brightness only (no color)

Recommended:
- Motion: binary_sensor.hallway_motion
- Light: light.hallway_ceiling

## Capability Summary

| Entity | Feature | Supported |
|--------|---------|-----------|
| light.hallway_ceiling | brightness | ✅ |
| light.hallway_ceiling | color_temp | ✅ |
| light.hallway_ceiling | rgb_color | ❌ |
| light.hallway_lamp | brightness | ✅ |
| light.hallway_lamp | color_temp | ❌ |
```

## If No Match

If no entities match, report:
```
No entities found matching "xyz".

Similar entities:
- light.xyz_room (close match)

Please clarify which entity you mean.
```

## Why Capability Snapshots Matter

When the caller wants to create automations or scenes, they need to know what
attributes are actually supported. Without a capability check:
- Setting `color_temp` on a brightness-only bulb will fail
- Setting `hvac_mode: auto` on a heat-only thermostat will fail
- Setting `position` on a cover without positioning will fail

**Always include the capability snapshot in your response.**
