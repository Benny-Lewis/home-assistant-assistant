---
name: ha-automation
description: This skill should be used when the user asks about "automation", "trigger", "condition", "action", "blueprint", "automation mode", "automation trace", mentions creating automations, debugging automations, or needs help with Home Assistant automation patterns and best practices.
version: 0.1.0
---

# Home Assistant Automation Patterns

This skill provides guidance on creating effective Home Assistant automations.

## Automation Structure

Every automation consists of:
- **alias**: Descriptive name
- **description**: What the automation does
- **trigger**: What starts the automation
- **condition**: Requirements that must be met (optional)
- **action**: What happens when triggered
- **mode**: How to handle overlapping runs

```yaml
automation:
  - alias: "Motion: Living Room Lights On"
    description: "Turn on living room lights when motion detected"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    condition:
      - condition: sun
        after: sunset
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
    mode: single
```

## Trigger Types

### State Trigger
React to entity state changes:
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"  # Optional: specify previous state
    for: "00:05:00"  # Optional: state must persist
```

### Time Trigger
Trigger at specific times:
```yaml
trigger:
  - platform: time
    at: "07:00:00"
  # Or multiple times
  - platform: time
    at:
      - "07:00:00"
      - "19:00:00"
```

### Sun Trigger
Trigger on sunrise/sunset:
```yaml
trigger:
  - platform: sun
    event: sunset
    offset: "-00:30:00"  # 30 min before sunset
```

### Event Trigger
React to HA events:
```yaml
trigger:
  - platform: event
    event_type: call_service
    event_data:
      domain: light
      service: turn_on
```

### Template Trigger
Trigger on template evaluation:
```yaml
trigger:
  - platform: template
    value_template: "{{ states('sensor.temp') | float > 75 }}"
```

### Device Trigger
Device-specific triggers (from integrations):
```yaml
trigger:
  - platform: device
    device_id: abc123
    domain: zwave_js
    type: pressed
    subtype: button_1
```

### Multiple Triggers
Combine triggers (OR logic):
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion_living
    to: "on"
  - platform: state
    entity_id: binary_sensor.motion_kitchen
    to: "on"
```

## Condition Types

### State Condition
Check entity state:
```yaml
condition:
  - condition: state
    entity_id: input_boolean.guest_mode
    state: "off"
```

### Numeric State Condition
Check numeric values:
```yaml
condition:
  - condition: numeric_state
    entity_id: sensor.temperature
    above: 60
    below: 80
```

### Time Condition
Check time of day:
```yaml
condition:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
```

### Sun Condition
Check sun position:
```yaml
condition:
  - condition: sun
    after: sunset
    before: sunrise
```

### Template Condition
Custom condition logic:
```yaml
condition:
  - condition: template
    value_template: >
      {{ states('person.john') == 'home' or
         states('person.jane') == 'home' }}
```

### AND/OR Conditions
Combine conditions:
```yaml
condition:
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.automation_enabled
        state: "on"
      - condition: or
        conditions:
          - condition: state
            entity_id: person.john
            state: "home"
          - condition: state
            entity_id: person.jane
            state: "home"
```

## Action Types

### Service Call
Call a Home Assistant service:
```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      color_temp: 350
```

### Targeting
Different ways to target entities:
```yaml
# Single entity
target:
  entity_id: light.kitchen

# Multiple entities
target:
  entity_id:
    - light.kitchen
    - light.living_room

# Area-based
target:
  area_id: living_room

# Device-based
target:
  device_id: abc123
```

### Delay
Wait between actions:
```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.bedroom
  - delay:
      seconds: 30
  - service: light.turn_off
    target:
      entity_id: light.bedroom
```

### Wait for Trigger
Wait for a condition:
```yaml
action:
  - service: light.turn_on
    target:
      entity_id: light.porch
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:05:00"
    timeout: "00:30:00"
  - service: light.turn_off
    target:
      entity_id: light.porch
```

### Choose (If/Then)
Conditional actions:
```yaml
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_boolean.night_mode
            state: "on"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.nightlight
            data:
              brightness_pct: 10
      - conditions:
          - condition: sun
            after: sunset
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.living_room
            data:
              brightness_pct: 80
    default:
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          brightness_pct: 100
```

### Variables
Set and use variables:
```yaml
action:
  - variables:
      brightness: "{{ 100 if is_state('sun.sun', 'above_horizon') else 50 }}"
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: "{{ brightness }}"
```

## Automation Modes

| Mode | Behavior |
|------|----------|
| `single` | Don't start new if already running |
| `restart` | Stop current run, start new |
| `queued` | Queue new runs, execute sequentially |
| `parallel` | Run multiple instances simultaneously |

```yaml
mode: queued
max: 5  # For queued/parallel: max concurrent runs
```

## Trigger Variables

Access trigger information in actions:
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    id: "motion_trigger"

action:
  - service: notify.mobile
    data:
      message: >
        Motion detected by {{ trigger.entity_id }}
        at {{ trigger.to_state.last_changed }}
        Trigger ID: {{ trigger.id }}
```

## Common Patterns

### Motion Light with Timeout
```yaml
alias: "Motion Light"
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"
action:
  - service: light.turn_on
    target:
      entity_id: light.hallway
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
        for: "00:02:00"
  - service: light.turn_off
    target:
      entity_id: light.hallway
mode: restart
```

### Presence-Based Climate
```yaml
alias: "Away Mode HVAC"
trigger:
  - platform: state
    entity_id: group.family
    to: "not_home"
    for: "00:15:00"
action:
  - service: climate.set_temperature
    target:
      entity_id: climate.main
    data:
      temperature: 65
```

### Notification with Actionable Response
```yaml
alias: "Door Left Open Alert"
trigger:
  - platform: state
    entity_id: binary_sensor.front_door
    to: "on"
    for: "00:05:00"
action:
  - service: notify.mobile_app
    data:
      message: "Front door has been open for 5 minutes"
      data:
        actions:
          - action: "DISMISS"
            title: "Dismiss"
          - action: "LOCK"
            title: "Lock Door"
```

## Best Practices

1. **Use descriptive aliases**: "Motion: Living Room Lights On" not "Automation 1"
2. **Add descriptions**: Document what the automation does
3. **Use trigger IDs**: When multiple triggers, identify which fired
4. **Choose appropriate mode**: Prevent overlapping runs causing issues
5. **Test with traces**: Use automation traces to debug
6. **Group related automations**: Use packages for organization
7. **Use input helpers**: For configurable values (thresholds, delays)
