# Common Automation Patterns

## Motion-Activated Light (Timer Pattern - Recommended)

Use timer helpers for delays > 30 seconds. Survives HA restarts.

### timer.yaml

```yaml
[room]_light_auto_off:
  name: "[Room] Light Auto-Off Timer"
  duration: "00:05:00"
  restore: true
```

### automations.yaml - Turn on and start timer

```yaml
- id: [room]_motion_light_on
  alias: "[Room]: Motion → Light On"
  description: "Turn on light when motion detected, start auto-off timer"
  mode: restart
  triggers:
    - trigger: state
      entity_id: binary_sensor.[room]_motion
      to: "on"
  conditions:
    - condition: state
      entity_id: sun.sun
      state: "below_horizon"
  actions:
    - action: light.turn_on
      target:
        entity_id: light.[room]
    - action: timer.start
      target:
        entity_id: timer.[room]_light_auto_off
```

### automations.yaml - Turn off when timer finishes

```yaml
- id: [room]_light_timer_expired_off
  alias: "[Room]: Light Timer Expired → Off"
  description: "Turn off light when auto-off timer finishes"
  triggers:
    - trigger: event
      event_type: timer.finished
      event_data:
        entity_id: timer.[room]_light_auto_off
  conditions:
    - condition: state
      entity_id: light.[room]
      state: "on"
  actions:
    - action: light.turn_off
      target:
        entity_id: light.[room]
```

**Why timer helpers?**
- `restore: true` survives HA restarts
- Visible countdown on dashboard
- Can be canceled/extended programmatically
- `mode: restart` resets timer on re-trigger (motion continues)

## Time-Based Actions

```yaml
- id: bedroom_morning_routine_light_on
  alias: "Bedroom: Morning Routine → Light On"
  description: "Turn on lights at specific time on weekdays"
  triggers:
    - trigger: time
      at: "06:30:00"
  conditions:
    - condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
  actions:
    - action: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 50
```

## Presence-Based

```yaml
- id: home_arrival_if_dark_lights_on
  alias: "Home: Arrival If Dark → Lights On"
  description: "Turn on lights when arriving home after sunset"
  triggers:
    - trigger: state
      entity_id: person.user
      to: "home"
  conditions:
    - condition: sun
      after: sunset
  actions:
    - action: light.turn_on
      target:
        entity_id:
          - light.entryway
          - light.living_room
```

## Temperature-Based

```yaml
- id: home_temperature_high_alert
  alias: "Home: Temperature High → Alert"
  description: "Notify when temperature exceeds threshold"
  triggers:
    - trigger: numeric_state
      entity_id: sensor.indoor_temperature
      above: 78
  actions:
    - action: notify.mobile_app
      data:
        title: "Temperature Alert"
        message: "Indoor temp is {{ states('sensor.indoor_temperature') }}F"
```

## Door/Window Sensors

```yaml
- id: front_door_open_too_long_alert
  alias: "Front Door: Open Too Long → Alert"
  description: "Alert if door open for too long"
  triggers:
    - trigger: state
      entity_id: binary_sensor.front_door
      to: "on"
      for: "00:05:00"
  actions:
    - action: notify.mobile_app
      data:
        title: "Door Alert"
        message: "Front door has been open for 5 minutes"
```

## Short Delays (< 30 seconds)

For brief delays where restart-safety isn't critical, inline delay is acceptable:

```yaml
- id: hallway_motion_light_flash
  alias: "Hallway: Motion → Light Flash"
  description: "Brief light flash for visual feedback"
  triggers:
    - trigger: state
      entity_id: binary_sensor.hallway_motion
      to: "on"
  actions:
    - action: light.turn_on
      target:
        entity_id: light.hallway
    - delay:
        seconds: 5
    - action: light.turn_off
      target:
        entity_id: light.hallway
```

Use this pattern for:
- Brief visual feedback (flash lights)
- Sequential device commands
- Non-critical timing
- Delays < 30 seconds (or below `conventions.timer_threshold_seconds`)
