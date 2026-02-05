# Automation YAML Syntax Reference

## Basic Structure

```yaml
- alias: "Descriptive Name"
  description: "What this automation does"
  trigger:
    - platform: <trigger_type>
      # trigger config
  condition:
    - condition: <condition_type>
      # condition config (optional)
  action:
    - service: <domain>.<service>
      # action config
```

## Trigger Types

### State Trigger
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"  # optional
    for: "00:01:00"  # optional, must be in state for duration
```

### Time Trigger
```yaml
trigger:
  - platform: time
    at: "07:00:00"
```

### Sun Trigger
```yaml
trigger:
  - platform: sun
    event: sunset
    offset: "-00:30:00"  # 30 min before sunset
```

### Numeric State Trigger
```yaml
trigger:
  - platform: numeric_state
    entity_id: sensor.temperature
    above: 75
    below: 85
```

## Condition Types

### State Condition
```yaml
condition:
  - condition: state
    entity_id: binary_sensor.someone_home
    state: "on"
```

### Sun Condition
```yaml
condition:
  - condition: sun
    after: sunset
    before: sunrise
```

### Time Condition
```yaml
condition:
  - condition: time
    after: "22:00:00"
    before: "06:00:00"
```

### And/Or Conditions
```yaml
condition:
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
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 100
      color_temp: 350
```

### Delay
```yaml
action:
  - delay: "00:05:00"
```

### Wait for Trigger
```yaml
action:
  - wait_for_trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "off"
    timeout: "00:10:00"
```

### Choose (Conditional)
```yaml
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_boolean.guest_mode
            state: "on"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.guest_room
    default:
      - service: light.turn_off
        target:
          entity_id: light.guest_room
```
