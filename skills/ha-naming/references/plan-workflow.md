# ha-naming — Plan Workflow

Based on audit results, create a detailed plan for renaming entities, devices, and other named items.

## Input

If convention argument provided, use as the target naming convention:
- `area_device` - {area}_{device_type} pattern
- `device_area` - {device_type}_{area} pattern
- `custom` - Ask user for custom pattern

If no arguments, analyze existing patterns and suggest the most common one.

## Planning Process

### Step 1: Load Audit Results

Review findings from the most recent naming audit. If no audit has been run, suggest running `/ha-naming` first.

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

### Step 4: Dependency Analysis

#### Investigating Unknown Devices (MANDATORY before blocking)

When the plan includes entities whose purpose is unclear (e.g., `zwave_js.node_4`, generic device names):

**Investigation is MANDATORY before using `new_id: null` / BLOCKED.** Do NOT mark entities as blocked without completing these steps:

1. **Check device registry** (prefetched in `.claude/ha-prefetch-devices.json`): manufacturer, model, area assignment
2. **Query entity state and attributes:** `hass-cli -o json state get <entity_id>` — check device_class, manufacturer, model
3. **Check if alive or dead:** last_seen, node_status attributes
4. **Search config files** for references to understand how it's used
5. **Cross-reference area assignment** from device registry with entity prefix

A single `hass-cli -o json state get` call often resolves the device identity. This takes seconds, not minutes.

**Then ask WITH context:** Present what you found and ask the user to confirm or clarify:
"I found `zwave_js.node_4` — it appears to be a Zooz ZEN27 dimmer (alive, last seen 2 min ago) in the Rec Room area. It's referenced in 2 automations. Should I rename it to `light.rec_room_dimmer`?"

**Never ask bare questions like** "What is Node 4?" without first investigating.

**Only use `new_id: null` with reason "BLOCKED"** if investigation yields genuinely ambiguous results (e.g., device offline with no attributes, no config references, no area assignment).

#### Dependency Mapping

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

### Step 5: Create Execution Plan

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
    # Blocked entry — investigated but unresolvable
    - from: zwave_js.node_99
      to_id: null
      reason: "BLOCKED: device offline, no attributes, no config references"
  # ... more renames

# Area operations (optional — included when audit finds mismatches)
area_operations:
  create_areas:
    - name: "Storage Room"
      proposed_id: storage_room
      reason: "Entities use storage_room_* prefix but no area exists"
  delete_areas:
    - area_id: old_unused_area
      reason: "Zero entities assigned, confirmed unused"
  rename_areas:
    - current_id: ll_bath
      new_name: "Downstairs Bathroom"
      reason: "Mismatch: area ID 'll_bath' vs entity prefix 'downstairs_bathroom_*'"

execution:
  estimated_changes: 47
  high_risk_items: 3
  phases: 5

status: pending
```

**Schema notes:**
- `to_id: null` means the rename is blocked — `/ha-apply-naming` must skip these and report them
- `area_operations` is optional — only present when the audit identifies area mismatches
- `create_areas`, `delete_areas`, `rename_areas` are all optional subsections

### Step 7: Validate Plan YAML

After writing or updating `.claude/naming-plan.yaml`, always validate it parses correctly:

```bash
python -c "import yaml; yaml.safe_load(open('.claude/naming-plan.yaml')); print('Plan YAML valid')"
```

If the Python command is not `python`, use the detected Python from `.claude/ha-python.txt`:
```bash
PY="$(cat .claude/ha-python.txt 2>/dev/null || command -v python3 || command -v python || command -v py)"
$PY -c "import yaml; yaml.safe_load(open('.claude/naming-plan.yaml')); print('Plan YAML valid')"
```

If validation fails, fix the YAML syntax before proceeding. A malformed plan will cause `/ha-apply-naming` to fail.

## User Review Points

Ask user to confirm:
1. Is the naming convention acceptable?
2. Any entities to exclude from renaming?
3. Priority order for renames
4. Acceptable to update all dependencies?

## Plan Output

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
