---
name: ha-naming
description: Use when user asks about "naming", "entity_id", "rename", "naming convention", "audit naming", "plan naming", mentions organizing entities, standardizing names, or needs help with Home Assistant naming best practices, audits, or rename planning.
user-invocable: true
allowed-tools: Read, Write, Bash, Glob, Grep, AskUserQuestion
---

# Home Assistant Naming Conventions

This skill provides guidance on consistent naming for Home Assistant entities, devices, and configurations.

**Detailed reference tables:** `references/naming-conventions.md`

## Why Naming Matters

Good naming enables:
- **Findability**: Quickly locate entities
- **Automation**: Easier to reference in automations
- **Grouping**: Natural grouping by area/function
- **Maintenance**: Understand purpose at a glance
- **Voice Control**: Natural spoken commands

## Entity ID Structure

Entity IDs follow the pattern: `domain.identifier`

```
light.living_room_ceiling
sensor.kitchen_temperature
binary_sensor.front_door_contact
```

### Entity ID Rules
- Lowercase only
- Underscores for spaces (no hyphens, spaces)
- No special characters
- Maximum 255 characters
- Must be unique within domain

## Recommended Pattern: Area First

`{domain}.{area}_{device_type}_{qualifier}`

```
light.living_room_ceiling_main
sensor.kitchen_temperature
switch.garage_outlet_1
```

**Benefits:**
- Entities group by area in lists
- Easy to find all devices in a room
- Natural for voice commands: "Turn on living room lights"

## Friendly Names

Friendly names (displayed in UI) can include:
- Proper capitalization
- Spaces
- Special characters

**Example:** `friendly_name: "Living Room Ceiling Light"`

## Anti-Patterns to Avoid

| Bad | Good | Why |
|-----|------|-----|
| `light.light_1` | `light.living_room_ceiling` | Generic names are meaningless |
| `light.lr_cl_1` | `light.living_room_ceiling_1` | Abbreviations without context |
| `light.living_room_main_ceiling_light_above_couch` | `light.living_room_ceiling_main` | Overly long |
| Mixed patterns across entities | Consistent pattern everywhere | Inconsistency creates confusion |

## Migration Strategy

When renaming existing entities:

1. **Audit current naming**: Use `/ha-naming`
2. **Choose convention**: Pick pattern that fits majority
3. **Plan changes**: Use `/ha-naming`
4. **Update dependencies**: Find all references in automations/scripts
5. **Execute carefully**: Use `/ha-apply-naming`
6. **Test thoroughly**: Verify automations work

## Best Practices

1. **Be consistent**: Choose a pattern and stick to it
2. **Be descriptive**: Names should explain what/where
3. **Use areas**: Prefix with location for natural grouping
4. **Avoid numbers when possible**: Use qualifiers (left, right, main)
5. **Plan for growth**: Leave room for additional devices
6. **Document conventions**: Record your naming rules

## References

- `references/naming-conventions.md` - Complete tables for areas, devices, domains
- `ha-conventions` skill - Detect naming patterns from your existing config

---

## Audit Workflow

> **This workflow is READ-ONLY.** It analyzes and reports, but does NOT modify.
> To apply changes, use `/ha-apply-naming` after reviewing the audit.

Scan all entities, devices, areas, automations, scripts, and scenes for naming inconsistencies.

**Agent usage:** If spawning the naming-analyzer agent, do NOT use `run_in_background: true` — background agents silently lose all output ([Claude Code #17011](https://github.com/anthropics/claude-code/issues/17011)). Always use foreground execution.

### Data Source Citation

**Every finding must cite its source:**

```
Issue: light.light_1 has no descriptive name
Source: hass-cli entity list | grep "light.light"
```

Do NOT report issues for entities you haven't verified exist.

### What Gets Audited

1. **Entity IDs** (`entity_id`) - Format: `domain.identifier`, lowercase, underscores only
2. **Friendly Names** (`friendly_name`) - Consistent capitalization style
3. **Device Names** - Consistent pattern across similar devices
4. **Area Names** - Consistent naming style
5. **Automation Names** (`alias`) - Descriptive, consistent pattern
6. **Script Names** - Action-oriented naming
7. **Scene Names** - Descriptive naming

### Existing Conventions Check

Before collecting entity data, scan for existing naming specs:

Glob patterns: `**/naming*`, `**/convention*`, `**/*style*guide*`
Also check: `.claude/ha.conventions.json`

If found, read them and report: "Found existing naming conventions at {path}. Incorporating into audit."

### Data Collection

**From hass-cli (if available):**
```bash
# For large setups (>500 entities), state list is faster than entity list
hass-cli state list
hass-cli area list
hass-cli device list
```

> Use Bash tool with `timeout: 60000` if entity count exceeds 500.
> Output is tabular text, not JSON. See `references/hass-cli.md` for parsing patterns.

**From local config files:**
- Parse automations.yaml for automation names
- Parse scripts.yaml for script names
- Parse scenes.yaml for scene names
- Scan packages/ for all entity definitions

### Pattern Detection

Identify existing naming patterns:
- Area prefix: `living_room_light`, `bedroom_fan`
- Device type suffix: `light_ceiling`, `sensor_temperature`
- Function-based: `motion_sensor`, `door_lock`
- Mixed patterns (inconsistent)

### Inconsistency Types

1. **Case Inconsistencies** - `Living Room` vs `living room` vs `LIVING ROOM`
2. **Separator Inconsistencies** - `living_room` vs `living-room` vs `livingroom`
3. **Pattern Inconsistencies** - `kitchen_light` but `light_bedroom`
4. **Abbreviation Inconsistencies** - `temp` vs `temperature`
5. **Missing Context** - Generic names: `light.light`, `switch.switch_1`

### Audit Report Format

```
Naming Audit Report

Entities Scanned: 147
Issues Found: 23

Pattern Analysis
Primary pattern detected: {area}_{device_type}
Coverage: 68% of entities follow this pattern

Issues by Category

Critical (blocking search/automation):
  - light.light_1 - No descriptive name
  - switch.switch - Duplicate generic name

Inconsistent Naming:
  - light.living_room_ceiling vs light.bedroom_light_ceiling
    Suggested: light.bedroom_ceiling (match pattern)

Missing Friendly Names:
  - binary_sensor.motion_1 - No friendly_name set

Style Suggestions:
  - Automation "turn on lights" - suggest "Motion: Living Room Lights On"

Summary
  Critical issues: 2
  Inconsistencies: 12
  Missing names: 5
  Style suggestions: 4

Next Steps:
  1. Run /ha-naming to create a rename plan
  2. Review and adjust the plan
  3. Run /ha-apply-naming to execute renames
```

### Audit Recommendations

Based on audit findings:
1. **Suggest a naming convention** based on majority pattern
2. **Prioritize fixes** by impact (critical -> style)
3. **Group related changes** (all lights, all sensors, etc.)
4. **Identify automation dependencies** that would break

### Audit Options

- `--json` - Output as JSON for programmatic use
- `--brief` - Summary only, no details
- `--domain [domain]` - Audit specific domain only (lights, switches, etc.)

---

## Plan Workflow

Based on audit results, create a detailed plan for renaming entities, devices, and other named items.

### Input

If convention argument provided, use as the target naming convention:
- `area_device` - {area}_{device_type} pattern
- `device_area` - {device_type}_{area} pattern
- `custom` - Ask user for custom pattern

If no arguments, analyze existing patterns and suggest the most common one.

### Planning Process

#### Step 1: Load Audit Results

Review findings from the most recent naming audit. If no audit has been run, suggest running `/ha-naming` first.

#### Step 2: Define Target Convention

Work with user to establish the naming convention:

**Entity IDs:**
- Pattern: `{domain}.{area}_{device_type}_{qualifier}`
- Example: `light.living_room_ceiling_main`

**Friendly Names:**
- Pattern: `{Area} {Device Type} {Qualifier}`
- Example: `Living Room Ceiling Main`

**Automations:**
- Pattern: `{Trigger}: {Area} {Action}`
- Example: `Motion: Living Room Lights On`

**Scripts:**
- Pattern: `{Action} {Target}`
- Example: `Turn Off All Lights`

**Scenes:**
- Pattern: `{Descriptive Name}`
- Example: `Movie Night`, `Good Morning`

#### Step 3: Generate Rename Mappings

For each item that needs renaming, create a mapping:

```yaml
entity_renames:
  - current: light.light_1
    new_id: light.living_room_ceiling
    new_friendly: "Living Room Ceiling"
    reason: "Generic name -> descriptive"

automation_renames:
  - current: "turn on lights"
    new_name: "Motion: Living Room Lights On"
    reason: "Add context and trigger type"

device_renames:
  - current: "Hue Bulb 1"
    new_name: "Living Room Ceiling Light"
    reason: "Replace device name with location"
```

#### Step 4: Dependency Analysis

##### Investigating Unknown Devices

When the plan includes entities whose purpose is unclear (e.g., `zwave_js.node_4`, generic device names):

**Always investigate BEFORE asking the user:**
1. Query entity state and attributes: `hass-cli -o json state get <entity_id>`
2. Check device class, manufacturer, model from attributes
3. Check if the node/device is alive or dead (last_seen, node_status)
4. Search config files for references to understand how it's used

**Then ask WITH context:** Present what you found and ask the user to confirm or clarify:
"I found `zwave_js.node_4` — it appears to be a Zooz ZEN27 dimmer (alive, last seen 2 min ago) in the Rec Room area. It's referenced in 2 automations. Should I rename it to `light.rec_room_dimmer`?"

**Never ask bare questions like** "What is Node 4?" without first investigating.

##### Dependency Mapping

For each rename, identify dependencies:

```yaml
- rename: light.light_1 -> light.living_room_ceiling
  dependencies:
    automations:
      - "Motion lights automation" (line 45)
      - "Goodnight routine" (line 12)
    scripts:
      - "flash_lights" (line 8)
    dashboards:
      - "main.yaml" (line 156)
    scenes:
      - "Movie Night" (entity list)
  impact: HIGH - 5 references need updating
```

#### Step 5: Create Execution Plan

Order renames to minimize disruption:

```yaml
execution_plan:
  phase_1_preparation:
    - Create backup of current config
    - Document current state

  phase_2_entity_renames:
    batch_1:  # Independent entities
      - light.light_1 -> light.living_room_ceiling
      - light.light_2 -> light.living_room_lamp
    batch_2:  # After batch_1 dependencies updated
      - switch.switch_1 -> switch.living_room_fan

  phase_3_automation_updates:
    - Update all automation entity references
    - Update automation names

  phase_4_config_updates:
    - Update dashboard references
    - Update script references
    - Update scene entity lists

  phase_5_verification:
    - Validate all configs
    - Test key automations
    - Verify dashboard displays
```

#### Step 6: Write Plan File

Save the plan to `.claude/naming-plan.yaml`:

```yaml
# HA Toolkit Naming Plan
# Generated: YYYY-MM-DD
# Convention: {area}_{device_type}

convention:
  entity_id: "{area}_{device_type}_{qualifier}"
  friendly_name: "{Area} {Device Type} {Qualifier}"
  automation: "{Trigger}: {Area} {Action}"

renames:
  entities:
    - from: light.light_1
      to_id: light.living_room_ceiling
      to_name: "Living Room Ceiling"
      dependencies: [automation.motion_lights]
  # ... more renames

execution:
  estimated_changes: 47
  high_risk_items: 3
  phases: 5

status: pending
```

### User Review Points

Ask user to confirm:
1. Is the naming convention acceptable?
2. Any entities to exclude from renaming?
3. Priority order for renames
4. Acceptable to update all dependencies?

### Plan Output

```
Naming Plan Created

Convention: {area}_{device_type}

Planned Changes:
  Entity renames: 23
  Automation updates: 15
  Script updates: 8
  Dashboard updates: 12
  Scene updates: 5

High-Risk Changes (require careful testing):
  - light.living_room_main (used in 12 automations)
  - switch.garage_door (security-related)

Plan saved to: .claude/naming-plan.yaml

To review: Read .claude/naming-plan.yaml
To execute: /ha-apply-naming
To modify: Edit the plan file or re-run /ha-naming
```
