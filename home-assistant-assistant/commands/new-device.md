---
name: ha:new-device
description: Workflow for adding and configuring a new device in Home Assistant
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion, Task
---

# New Device Setup Workflow

> **Safety Invariant #1:** Before suggesting automations for the device,
> get a capability snapshot. See `modules/resolver.md`.

Guide the user through setting up a new device in Home Assistant: naming, automations, dashboard integration, and related configurations.

## Capability Check (Mandatory)

**Before suggesting any automations or scenes, get device capabilities:**

```bash
# Resolve actual entity_id
hass-cli state list | grep -i "<device_name>"

# Get capability snapshot
hass-cli state get <entity_id>
```

Check for:
- `supported_features` - What the device can do
- `supported_color_modes` - For lights
- `hvac_modes` - For climate devices

**Only suggest automations using supported capabilities.**

## Trigger the Device Advisor Agent

This command launches the `device-advisor` agent to provide comprehensive assistance.

Use the Task tool to spawn the device-advisor agent with the following context:

```
Help the user set up a new device in Home Assistant.

Context from the user: $ARGUMENTS

Process:
1. Identify what device was added
2. Check existing naming conventions
3. Suggest appropriate naming
4. Recommend automations for this device type
5. Offer dashboard integration
6. Check for device groups/relationships
```

## Workflow Overview

### Step 1: Device Identification

Ask the user:
- What device did you add? (type, brand, integration)
- What room/area is it in?
- What is its current name in HA?

Or detect automatically if hass-cli available:
```bash
# Check recently added entities (last 24 hours would need entity history)
hass-cli entity list --domain [device_domain]
```

### Step 2: Naming Consultation

Based on the device and existing naming conventions:
- Suggest entity_id following established pattern
- Suggest friendly_name
- Assign to appropriate area

### Step 3: Common Automations

Based on device type, suggest relevant automations:

**Lights:**
- Motion-activated on/off
- Time-based schedules
- Brightness based on time of day
- Away mode simulation

**Motion Sensors:**
- Trigger lights
- Security alerts when away
- Occupancy tracking

**Door/Window Sensors:**
- Security alerts when open too long
- Climate control (pause HVAC when windows open)
- Arrival/departure detection

**Climate (Thermostat):**
- Schedule-based temperature
- Presence-based adjustment
- Energy-saving modes

**Switches/Plugs:**
- Schedule-based on/off
- Energy monitoring alerts
- Device protection (auto-off)

**Cameras:**
- Motion detection notifications
- Recording triggers
- Privacy mode automations

### Step 4: Dashboard Integration

Offer to add the device to a dashboard:
- Identify relevant dashboard
- Suggest appropriate card type
- Generate card YAML
- Position in logical location

### Step 5: Device Relationships

Check for related devices:
- Same room devices (group lights)
- Complementary devices (motion sensor + light)
- Device groups (all bedroom devices)

Suggest creating groups or scenes.

### Step 6: Testing

After setup:
- Test entity accessibility
- Test automations (if created)
- Verify dashboard display

## Device Type Templates

### Light Device
```yaml
suggested_automations:
  - Motion-activated (if motion sensor in same area)
  - Sunset turn on
  - Bedtime turn off
dashboard_card: light
groups: "{area}_lights"
```

### Sensor Device
```yaml
suggested_automations:
  - Alert on threshold
  - History graph
  - Average calculations
dashboard_card: sensor, history-graph
```

### Switch Device
```yaml
suggested_automations:
  - Schedule-based
  - Integration with related devices
dashboard_card: button, entities
```

## Output

```
New Device Setup Complete
═════════════════════════

Device: Philips Hue Bulb
Type: Light
Area: Living Room

Naming Applied:
  entity_id: light.living_room_ceiling
  friendly_name: Living Room Ceiling
  area: Living Room

Automations Created:
  ✓ Motion: Living Room Lights On
  ✓ Sunset: Living Room Lights Dim

Dashboard Updated:
  ✓ Added to "Main" dashboard, Living Room section

Groups:
  ✓ Added to group.living_room_lights

Next Steps:
  - Test the motion automation
  - Adjust brightness levels if needed
  - Run /ha:deploy to sync changes
```

## Quick Mode

For experienced users, support quick setup:
```
/ha:new-device light kitchen ceiling
```

This would:
1. Create entity with naming convention applied
2. Skip automation suggestions
3. Offer quick dashboard add
