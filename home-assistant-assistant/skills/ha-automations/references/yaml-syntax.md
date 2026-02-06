# Automation YAML Syntax Reference

> **Schema Version:** Home Assistant 2024+ (current)
> Uses `triggers:`/`conditions:`/`actions:` (plural) with `trigger:`/`condition:`/`action:` inside.

## Basic Structure

```yaml
- id: unique_automation_id
  alias: "Descriptive Name"
  description: "What this automation does"
  triggers:
    - trigger: state
      entity_id: binary_sensor.motion
      to: "on"
  conditions:
    - condition: state
      entity_id: input_boolean.enabled
      state: "on"
  actions:
    - action: light.turn_on
      target:
        entity_id: light.living_room
```

## Trigger Types

### State Trigger
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"  # optional
    for: "00:05:00"  # optional - must be in state for duration (use for inactivity!)
```

### Time Trigger
```yaml
triggers:
  - trigger: time
    at: "07:00:00"
```

### Sun Trigger
```yaml
triggers:
  - trigger: sun
    event: sunset
    offset: "-00:30:00"  # 30 min before sunset
```

### Numeric State Trigger
```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 75
    below: 85
```

### Event Trigger
```yaml
triggers:
  - trigger: event
    event_type: timer.finished
    event_data:
      entity_id: timer.kitchen_delay
```

## Condition Types

### State Condition
```yaml
conditions:
  - condition: state
    entity_id: binary_sensor.someone_home
    state: "on"
```

### Sun Condition
```yaml
conditions:
  - condition: sun
    after: sunset
    before: sunrise
```

### Time Condition
```yaml
conditions:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
```

### And/Or Conditions
```yaml
conditions:
  - condition: and
    conditions:
      - condition: state
        entity_id: light.kitchen
        state: "off"
      - condition: sun
        after: sunset
```

## Action Types

### Service Call
```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 100
      # Only include attributes device supports! (Invariant #1)
```

### Delay (Pure Delay Only)
```yaml
actions:
  - delay: "00:05:00"
```

**Note:** For inactivity patterns, use `for:` in the trigger instead of `delay:` in actions.

### Wait for Trigger
```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "00:10:00"
    continue_on_timeout: true
```

### Choose (Conditional)
```yaml
actions:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_boolean.guest_mode
            state: "on"
        sequence:
          - action: light.turn_on
            target:
              entity_id: light.guest_room
    default:
      - action: light.turn_off
        target:
          entity_id: light.guest_room
```

### Variables
```yaml
actions:
  - variables:
      brightness_level: "{{ states('input_number.default_brightness') | int }}"
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness: "{{ brightness_level }}"
```

## Inactivity Pattern (Correct Way)

**Use `for:` in trigger, NOT delay/timer in actions:**

```yaml
- id: motion_light_off_after_inactivity
  alias: "Turn off light after no motion"
  triggers:
    - trigger: state
      entity_id: binary_sensor.kitchen_motion
      to: "off"
      for: "00:05:00"  # Only fires if motion stays off for 5 min
  actions:
    - action: light.turn_off
      target:
        entity_id: light.kitchen
```

## Automation Modes

```yaml
- id: example_automation
  alias: "Example"
  mode: single  # single, restart, queued, parallel
  max: 10  # only for queued/parallel
  triggers: [...]
  actions: [...]
```

| Mode | Behavior |
|------|----------|
| single | Ignore new triggers while running (default) |
| restart | Stop current run, start new |
| queued | Queue new triggers, run sequentially |
| parallel | Run multiple instances simultaneously |

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `platform: state` (old) | `trigger: state` (2024+) |
| `service:` | `action:` (2024+) |
| Using `delay:` for inactivity | Use `for:` in trigger |
| Including `color_temp` on brightness-only light | Check `supported_color_modes` first |
| `automation:` as root key in file | File should be list `- id: ...` |
