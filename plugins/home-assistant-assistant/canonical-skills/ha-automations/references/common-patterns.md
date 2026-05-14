# Common Automation Patterns

## Motion-Activated Light

```yaml
- alias: "Motion Light - [Room]"
  description: "Turn on light when motion detected, off after delay"
  triggers:
    - trigger: state
      entity_id: binary_sensor.[room]_motion
      to: "on"
  conditions:
    - condition: sun
      after: sunset
  actions:
    - action: light.turn_on
      target:
        entity_id: light.[room]
    - delay: "00:02:00"
    - action: light.turn_off
      target:
        entity_id: light.[room]
```

## Time-Based Actions

```yaml
- alias: "Morning Routine"
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
- alias: "Welcome Home"
  description: "Turn on lights when arriving home"
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
- alias: "Too Hot Alert"
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
- alias: "Door Left Open"
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
