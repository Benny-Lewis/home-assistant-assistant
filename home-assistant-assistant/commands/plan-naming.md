---
name: ha:plan-naming
description: Create a detailed plan for renaming entities and devices
allowed-tools: Read, Write, Bash, Glob, Grep, AskUserQuestion
argument-hint: [convention]
---

# Create Naming Plan

Based on audit results from `/ha:audit-naming`, create a detailed plan for renaming entities, devices, and other named items.

## Input

If $ARGUMENTS provided, use as the target naming convention:
- `area_device` - {area}_{device_type} pattern
- `device_area` - {device_type}_{area} pattern
- `custom` - Ask user for custom pattern

If no arguments, analyze existing patterns and suggest the most common one.

## Process

### Step 1: Load Audit Results

Review findings from the most recent naming audit. If no audit has been run, suggest running `/ha:audit-naming` first.

### Step 2: Define Target Convention

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

### Step 3: Generate Rename Mappings

For each item that needs renaming, create a mapping:

```yaml
entity_renames:
  - current: light.light_1
    new_id: light.living_room_ceiling
    new_friendly: "Living Room Ceiling"
    reason: "Generic name → descriptive"

  - current: light.bedroom_light_ceiling
    new_id: light.bedroom_ceiling
    new_friendly: "Bedroom Ceiling"
    reason: "Remove redundant 'light'"

automation_renames:
  - current: "turn on lights"
    new_name: "Motion: Living Room Lights On"
    reason: "Add context and trigger type"

device_renames:
  - current: "Hue Bulb 1"
    new_name: "Living Room Ceiling Light"
    reason: "Replace device name with location"
```

### Step 4: Dependency Analysis

For each rename, identify dependencies:

```yaml
- rename: light.light_1 → light.living_room_ceiling
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

### Step 5: Create Execution Plan

Order renames to minimize disruption:

```yaml
execution_plan:
  phase_1_preparation:
    - Create backup of current config
    - Document current state

  phase_2_entity_renames:
    batch_1:  # Independent entities
      - light.light_1 → light.living_room_ceiling
      - light.light_2 → light.living_room_lamp
    batch_2:  # After batch_1 dependencies updated
      - switch.switch_1 → switch.living_room_fan

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

### Step 6: Write Plan File

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

## User Review Points

Ask user to confirm:
1. Is the naming convention acceptable?
2. Any entities to exclude from renaming?
3. Priority order for renames
4. Acceptable to update all dependencies?

## Output

```
Naming Plan Created
═══════════════════

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
To execute: /ha:apply-naming
To modify: Edit the plan file or re-run this command
```
