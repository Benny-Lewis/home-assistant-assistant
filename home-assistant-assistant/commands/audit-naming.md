---
name: ha:audit-naming
description: Audit entity and device naming for consistency issues
allowed-tools: Read, Bash, Glob, Grep
---

# Audit Naming Consistency

> **This command is READ-ONLY.** It analyzes and reports, but does NOT modify.
> To apply changes, use `/ha:apply-naming` after reviewing the audit.

Scan all entities, devices, areas, automations, scripts, and scenes for naming inconsistencies.

## Data Source Citation

**Every finding must cite its source:**

```
Issue: light.light_1 has no descriptive name
Source: hass-cli entity list | grep "light.light"
```

Do NOT report issues for entities you haven't verified exist.

## What Gets Audited

1. **Entity IDs** (`entity_id`)
   - Format: `domain.identifier`
   - Check: lowercase, underscores only, no spaces

2. **Friendly Names** (`friendly_name`)
   - Human-readable display names
   - Check: consistent capitalization style

3. **Device Names**
   - Names assigned to physical devices
   - Check: consistent pattern across similar devices

4. **Area Names**
   - Room/zone assignments
   - Check: consistent naming style

5. **Automation Names** (`alias`)
   - Automation identifiers
   - Check: descriptive, consistent pattern

6. **Script Names**
   - Script identifiers
   - Check: action-oriented naming

7. **Scene Names**
   - Scene identifiers
   - Check: descriptive naming

## Data Collection

### From hass-cli (if available):
```bash
hass-cli entity list --output json
hass-cli area list --output json
hass-cli device list --output json
```

### From local config files:
- Parse automations.yaml for automation names
- Parse scripts.yaml for script names
- Parse scenes.yaml for scene names
- Scan packages/ for all entity definitions

## Analysis

### Pattern Detection

Identify existing naming patterns:
- Area prefix: `living_room_light`, `bedroom_fan`
- Device type suffix: `light_ceiling`, `sensor_temperature`
- Function-based: `motion_sensor`, `door_lock`
- Mixed patterns (inconsistent)

### Inconsistency Types

1. **Case Inconsistencies**
   - `Living Room` vs `living room` vs `LIVING ROOM`

2. **Separator Inconsistencies**
   - `living_room` vs `living-room` vs `livingroom`

3. **Pattern Inconsistencies**
   - `kitchen_light` but `light_bedroom`
   - `motion_living_room` but `bedroom_motion`

4. **Abbreviation Inconsistencies**
   - `temp` vs `temperature`
   - `lr` vs `living_room`

5. **Missing Context**
   - Generic names: `light.light`, `switch.switch_1`
   - No area association

## Report Format

```
Naming Audit Report
═══════════════════

Entities Scanned: 147
Issues Found: 23

Pattern Analysis
────────────────
Primary pattern detected: {area}_{device_type}
Coverage: 68% of entities follow this pattern

Issues by Category
──────────────────

🔴 Critical (blocking search/automation):
  - light.light_1 → No descriptive name
  - switch.switch → Duplicate generic name

🟡 Inconsistent Naming:
  - light.living_room_ceiling vs light.bedroom_light_ceiling
    Suggested: light.bedroom_ceiling (match pattern)
  - sensor.temp_outside vs sensor.temperature_inside
    Suggested: Use consistent temp/temperature

🔵 Missing Friendly Names:
  - binary_sensor.motion_1 → No friendly_name set
  - sensor.power_3 → No friendly_name set

🟢 Style Suggestions:
  - Automation "turn on lights" → "Motion: Living Room Lights On"
  - Scene "movie" → "Movie Night"

Summary
───────
Critical issues: 2
Inconsistencies: 12
Missing names: 5
Style suggestions: 4

Next Steps:
  1. Run /ha:plan-naming to create a rename plan
  2. Review and adjust the plan
  3. Run /ha:apply-naming to execute renames
```

## Recommendations

Based on audit findings:

1. **Suggest a naming convention** based on majority pattern
2. **Prioritize fixes** by impact (critical → style)
3. **Group related changes** (all lights, all sensors, etc.)
4. **Identify automation dependencies** that would break

## Output Options

- `--json` - Output as JSON for programmatic use
- `--brief` - Summary only, no details
- `--domain [domain]` - Audit specific domain only (lights, switches, etc.)
