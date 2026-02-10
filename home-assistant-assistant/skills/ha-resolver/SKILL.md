---
name: ha-resolver
description: Entity resolution and capability snapshot procedures for Home Assistant
user-invocable: false
allowed-tools: Bash(hass-cli:*)
---

# Resolver Module

Shared procedures for entity resolution and capability discovery in Home Assistant.

> **Safety Invariant #1:** No unsupported attributes written without explicit override.
> See `references/safety-invariants.md` for full details.

## Purpose

Before generating YAML that references entities, services, or device capabilities, **always resolve first**. This prevents:
- Referencing non-existent entities
- Using unsupported service attributes
- Creating automations for unavailable capabilities

## Entity Resolution Procedure

### Step 1: List Available Entities

```bash
# Get all entities (may be large)
hass-cli state list

# Filter by domain
hass-cli state list | grep "^light\."
hass-cli state list | grep "^switch\."
hass-cli state list | grep "^sensor\."
```

### Step 2: Get Entity Details

```bash
# Get specific entity state and attributes
hass-cli state get light.living_room
```

### Step 3: Validate Entity Exists

Before using an entity_id in generated YAML:
1. Run `hass-cli state get <entity_id>`
2. If error/not found, ask user for correct entity
3. Never guess or assume entity names

## Capability Snapshot Procedure

Before emitting YAML attributes for a device, capture its actual capabilities.

> **Use `-o json` for full attributes.** Default tabular output omits attributes like `supported_features` and `supported_color_modes`.

### For Lights

```bash
hass-cli -o json state get light.example_light
```

Check `supported_features` and `supported_color_modes` in attributes:
- `brightness` - can dim
- `color_temp` - can change temperature
- `rgb_color` / `hs_color` - can change color

**Only emit attributes the device actually supports.**

### For Climate

```bash
hass-cli -o json state get climate.example_thermostat
```

Check `hvac_modes` and `supported_features`:
- Available modes: `heat`, `cool`, `heat_cool`, `off`, `auto`
- Features: `target_temperature`, `target_humidity`, `fan_mode`

### For Media Players

```bash
hass-cli -o json state get media_player.example
```

Check `supported_features` bitmask for:
- Volume control
- Play/pause/stop
- Source selection

## Service Discovery

### List Available Services

```bash
hass-cli service list
```

### Get Service Schema

```bash
hass-cli service list | grep "light.turn_on"
```

## Missing Helper Detection

When an automation needs a helper (timer, input_boolean, counter, etc.):

1. Check if helper exists:
   ```bash
   hass-cli state list | grep "^timer\."
   hass-cli state list | grep "^input_boolean\."
   ```

2. If missing, create a **safe creation plan**:
   - Document the helper needed
   - Provide YAML to add to `configuration.yaml`
   - Do NOT auto-create without user confirmation

## Output Contract

When resolution completes, provide:

```markdown
## Entity Resolution Results

| Requested | Found | Status |
|-----------|-------|--------|
| "kitchen light" | light.kitchen_main | Resolved |
| "garage door" | cover.garage | Resolved |
| "bedroom fan" | - | Not found |

### Capabilities Snapshot

**light.kitchen_main**
- Brightness: Yes
- Color temp: Yes (153-500 mireds)
- RGB color: No

### Missing Helpers

- `timer.kitchen_motion_delay` - needed for inactivity automation
  - Action required: Add to configuration.yaml
```

## Integration Points

- **ha-entity-resolver agent**: Calls this skill for complex resolution
- **ha-automations skill**: Must resolve before generating
- **ha-scenes skill**: Must snapshot capabilities before emitting
- **ha-scripts skill**: Must verify services exist
