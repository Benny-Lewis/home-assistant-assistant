# System Overview Procedure

Orientation step to understand a user's HA setup before resolving entities.
Three detail levels — use the lightest level that fits the task.

## Minimal (~3 commands)

Use for quick orientation when you just need to know what domains and areas exist.

```bash
# Domain distribution (sorted by count)
hass-cli state list --no-headers | awk -F'.' '{print $1}' | sort | uniq -c | sort -rn

# Areas
hass-cli area list

# Total entity count
hass-cli state list --no-headers | wc -l
```

### Output Format

```markdown
## System Overview (Minimal)

**Entities:** 247 total

| Domain | Count |
|--------|-------|
| sensor | 89 |
| binary_sensor | 34 |
| light | 23 |
| switch | 18 |
| automation | 15 |
| ... | ... |

**Areas:** Kitchen, Living Room, Bedroom, Bathroom, Office, Garage
```

## Standard (~5 commands)

Adds device/service counts and system info. Use when advising on setup or analyzing configuration.

Run the minimal commands above, plus:

```bash
# Device count
hass-cli device list --no-headers | wc -l

# Service count
hass-cli service list --no-headers | wc -l

# System config (version, location, timezone, loaded components)
MSYS_NO_PATHCONV=1 hass-cli -o json raw get /api/config
```

### Key Fields from /api/config

| Field | Description |
|-------|-------------|
| `version` | HA version (e.g., "2024.12.1") |
| `location_name` | Instance name |
| `time_zone` | Configured timezone |
| `latitude`/`longitude` | Location (for sun-based automations) |
| `elevation` | Altitude (for weather) |
| `unit_system` | Metric/imperial |
| `components` | List of loaded integrations |
| `state` | "RUNNING", "NOT_RUNNING", etc. |
| `safe_mode` | true/false |

### Output Format

```markdown
## System Overview (Standard)

**System:** Home Assistant 2024.12.1 — "My Home" — RUNNING
**Location:** US/Eastern, 40.7°N 74.0°W, 10m elevation
**Units:** Imperial

**Entities:** 247 | **Devices:** 52 | **Services:** 156 | **Areas:** 6

| Domain | Count |
|--------|-------|
| sensor | 89 |
| ... | ... |

**Areas:** Kitchen, Living Room, Bedroom, Bathroom, Office, Garage
```

## Full (N+5 commands)

Adds per-area entity distribution via registry queries. Use for comprehensive setup analysis or when planning area-based automations.

Run the standard commands above, plus:

```bash
# Area registry (full details: floor, icon, aliases)
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/area_registry/list"}'

# Entity registry (area_id per entity for distribution)
MSYS_NO_PATHCONV=1 hass-cli raw ws '{"type":"config/entity_registry/list"}'
```

Cross-reference entity registry `area_id` with area registry to build per-area breakdown.

### Output Format

```markdown
## System Overview (Full)

[...standard sections...]

### Per-Area Distribution

| Area | Lights | Sensors | Switches | Climate | Other | Total |
|------|--------|---------|----------|---------|-------|-------|
| Kitchen | 3 | 5 | 2 | 0 | 1 | 11 |
| Living Room | 4 | 3 | 1 | 1 | 2 | 11 |
| Bedroom | 2 | 2 | 1 | 1 | 0 | 6 |
| Unassigned | 5 | 12 | 3 | 0 | 8 | 28 |
```

## When to Use Each Level

| Level | Use When |
|-------|----------|
| Minimal | Quick orientation, entity search prep |
| Standard | Setup analysis, troubleshooting context, new device advice |
| Full | Comprehensive audit, area-based automation planning, naming review |
