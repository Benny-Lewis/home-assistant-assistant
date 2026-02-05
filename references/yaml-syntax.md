# Home Assistant YAML Syntax Reference

> **Schema Version:** Home Assistant 2024+ (current)
> Uses `triggers:`/`conditions:`/`actions:` (plural) with `trigger:`/`condition:`/`action:` inside each item.

This consolidated reference covers automations, scripts, and scenes YAML syntax.

## Safety Reminders

Before generating YAML:
1. **Capability Snapshot** (Invariant #1): Verify device supports attributes via `hass-cli state get`
2. **Inactivity vs Delay** (Invariant #2): Use `for:` in trigger for inactivity, NOT delay/timer

---

## Automations

### Basic Structure

```yaml
- id: unique_automation_id
  alias: "Descriptive Name"
  description: "What this automation does"
  mode: single  # single, restart, queued, parallel
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

### Trigger Types

**State Trigger**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"        # optional
    for: "00:05:00"    # optional - INACTIVITY PATTERN: triggers only if state holds
```

**Time Trigger**
```yaml
triggers:
  - trigger: time
    at: "07:00:00"
```

**Sun Trigger**
```yaml
triggers:
  - trigger: sun
    event: sunset
    offset: "-00:30:00"  # 30 min before
```

**Numeric State Trigger**
```yaml
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 75
    below: 85
```

**Event Trigger**
```yaml
triggers:
  - trigger: event
    event_type: timer.finished
    event_data:
      entity_id: timer.kitchen_delay
```

### Condition Types

**State Condition**
```yaml
conditions:
  - condition: state
    entity_id: binary_sensor.someone_home
    state: "on"
```

**Time Condition**
```yaml
conditions:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
```

**Sun Condition**
```yaml
conditions:
  - condition: sun
    after: sunset
    before: sunrise
```

**And/Or Conditions**
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

### Action Types

**Service Call**
```yaml
actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 100
      # Only include attributes the device actually supports!
```

**Delay (Pure Delay Only)**
```yaml
actions:
  - delay: "00:05:00"
```
⚠️ For inactivity (turn off after no motion), use `for:` in trigger instead!

**Wait for Trigger**
```yaml
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "00:10:00"
    continue_on_timeout: true
```

**Choose (Conditional)**
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

**Variables**
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

### Automation Modes

| Mode | Behavior |
|------|----------|
| single | Ignore new triggers while running (default) |
| restart | Stop current run, start new |
| queued | Queue new triggers, run sequentially (max: N) |
| parallel | Run multiple instances simultaneously (max: N) |

### Inactivity Pattern (Correct Way)

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

---

## Scripts

### Basic Structure

```yaml
script_name:
  alias: "Friendly Name"
  description: "What this script does"
  mode: single
  sequence:
    - action: domain.service
      target:
        entity_id: entity.id
```

### With Input Fields

```yaml
announce:
  alias: "Announce Message"
  description: "Play announcement on speakers"
  fields:
    message:
      description: "Message to announce"
      example: "Dinner is ready"
  sequence:
    - action: tts.speak
      target:
        entity_id: media_player.kitchen_speaker
      data:
        message: "{{ message }}"
```

### With Delays (Pure Delay Only)

```yaml
gradual_wakeup:
  alias: "Gradual Wake Up"
  sequence:
    - action: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 10
    - delay: "00:05:00"
    - action: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 50
    - delay: "00:05:00"
    - action: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 100
```

### With Conditions (choose)

```yaml
smart_lights:
  alias: "Smart Lights"
  sequence:
    - choose:
        - conditions:
            - condition: sun
              before: sunrise
          sequence:
            - action: light.turn_on
              target:
                entity_id: light.bedroom
              data:
                brightness_pct: 30
      default:
        - action: light.turn_on
          target:
            entity_id: light.bedroom
          data:
            brightness_pct: 100
```

---

## Scenes

### Basic Structure

```yaml
- name: "Scene Name"
  entities:
    light.living_room:
      state: "on"
      brightness: 200
    light.kitchen:
      state: "off"
```

### Common Scene Patterns

**Movie Night**
```yaml
- name: "Movie Night"
  entities:
    light.living_room_main:
      state: "off"
    light.living_room_accent:
      state: "on"
      brightness: 50
    media_player.tv:
      state: "on"
    cover.living_room_blinds:
      state: "closed"
```

**Goodnight**
```yaml
- name: "Goodnight"
  entities:
    light.living_room:
      state: "off"
    light.bedroom:
      state: "on"
      brightness: 30
    lock.front_door:
      state: "locked"
```

### Entity State Options by Domain

**Lights**
- `state`: "on" or "off"
- `brightness`: 0-255
- `brightness_pct`: 0-100
- `color_temp`: Kelvin or mired (check `supported_color_modes`!)
- `rgb_color`: [R, G, B] (check `supported_color_modes`!)

**Covers**
- `state`: "open", "closed"
- `position`: 0-100

**Climate**
- `state` / `hvac_mode`: "heat", "cool", "auto", "off"
- `temperature`: target temp
- `target_temp_high` / `target_temp_low`: for auto mode

**Locks**
- `state`: "locked", "unlocked"

**Media Players**
- `state`: "on", "off", "playing", "paused"
- `volume_level`: 0.0-1.0

**Fans**
- `state`: "on", "off"
- `percentage`: 0-100

---

## Common Mistakes

| Mistake | Correct |
|---------|---------|
| `platform: state` (old) | `trigger: state` (2024+) |
| `service:` | `action:` (2024+) |
| Using `delay:` for inactivity | Use `for:` in trigger |
| Including `color_temp` on brightness-only light | Check `supported_color_modes` first |
| `automation:` as root key in file | File should be list `- id: ...` |
