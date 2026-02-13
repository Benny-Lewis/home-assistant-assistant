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

## Quick Reference

| Task | Quick Command | Full Procedure |
|------|--------------|----------------|
| System overview | `hass-cli area list` + domain counts | `references/system-overview.md` |
| Search by area/room | `hass-cli raw ws entity_registry` | `references/area-search.md` |
| Search by name | `hass-cli state list \| grep -i` | `references/enhanced-search.md` |
| Capability snapshot | `hass-cli -o json state get` | Inline below |
| Service discovery | `hass-cli service list` | Inline below |

## System Overview

Run an overview first when you need orientation on the user's HA setup.

**Minimal inventory** (~3 commands):

```bash
# Domain distribution
hass-cli state list --no-headers | awk -F'.' '{print $1}' | sort | uniq -c | sort -rn

# Areas
hass-cli area list

# Total entity count
hass-cli state list --no-headers | wc -l
```

For standard (adds system info, device/service counts) or full (adds per-area
entity distribution via registries), see `references/system-overview.md`.

## Entity Resolution Procedure

### Step 1: Search for Entities

**Quick search** (start here):

```bash
# Domain + keyword (most common)
hass-cli state list | grep "^light\." | grep -i "kitchen"

# Case-insensitive broad search
hass-cli state list | grep -i "<search_term>"
```

**If user mentions a room/area**, use area-based search instead — see
`references/area-search.md`.

**If quick search returns nothing**, escalate through search tiers (domain
filter → multi-term → broad → JSON friendly_name → registry). See
`references/enhanced-search.md`.

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

## Area-Based Entity Search

Find all entities in a specific room/area using HA registries.

> **Why registries:** Entity-to-area assignment lives in the entity registry
> (direct `area_id`) or device registry (via `device_id`). State attributes
> are NOT authoritative for area membership.

**Quick area search:**

```bash
# List areas
hass-cli area list

# Get entity registry (all entity-to-area assignments)
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/entity_registry/list"}'
```

Filter entity registry results by `area_id`. For entities without a direct
area_id, check their device's area_id via the device registry.

**Resolution priority:** Entity area_id > Device area_id > No area assigned

For the full procedure (device registry fallback, domain grouping, multi-area
search, grep fallback), see `references/area-search.md`.

**Grep fallback** (when WebSocket unavailable):

```bash
hass-cli state list | grep -i "<area_name>"
```

Note in evidence table: "Area search: grep fallback (registry unavailable)"

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

# Filter by domain
hass-cli service list | grep "^light\."

# Count services
hass-cli service list --no-headers | wc -l
```

### Validate a Specific Service

```bash
hass-cli service list | grep "light.turn_on"
```

### Service Validation Evidence

| Service | Exists | Domain | Notes |
|---------|--------|--------|-------|
| light.turn_on | Yes | light | Standard service |
| notify.mobile_app | Yes | notify | Check target device |
| custom.invalid | No | custom | Domain not found |

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

## Composable Procedure Pipeline

Procedures compose in sequence. Use the lightest path that fits:

```
1. System Overview    → Understand what exists (domains, areas, counts)
2. Area-Based Search  → Narrow to entities in the target area
3. Entity Resolution  → Match user description to specific entity_ids
4. Capability Snapshot → Verify device features before generating YAML
```

**Skip guidance:**
- Quick entity resolution → skip to step 3
- "What's in my kitchen?" → steps 1 + 2
- Creating an automation → steps 3 + 4 (add step 1 if unfamiliar with setup)
- Comprehensive audit → all steps

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

## References

- `references/system-overview.md` — Full system orientation procedure (3 detail levels)
- `references/area-search.md` — Area-based entity discovery via registries
- `references/enhanced-search.md` — Tiered search escalation beyond simple grep
