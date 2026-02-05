# Common Automation Patterns

## Motion-Activated Light

```yaml
- alias: "Motion Light - [Room]"
  description: "Turn on light when motion detected, off after delay"
  trigger:
    - platform: state
      entity_id: binary_sensor.[room]_motion
      to: "on"
  condition:
    - condition: sun
      after: sunset
  action:
    - service: light.turn_on
      target:
        entity_id: light.[room]
    - delay: "00:02:00"
    - service: light.turn_off
      target:
        entity_id: light.[room]
```

## Time-Based Actions

```yaml
- alias: "Morning Routine"
  description: "Turn on lights at specific time on weekdays"
  trigger:
    - platform: time
      at: "06:30:00"
  condition:
    - condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
  action:
    - service: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 50
```

## Presence-Based

```yaml
- alias: "Welcome Home"
  description: "Turn on lights when arriving home"
  trigger:
    - platform: state
      entity_id: person.user
      to: "home"
  condition:
    - condition: sun
      after: sunset
  action:
    - service: light.turn_on
      target:
        entity_id:
          - light.entryway
          - light.living_room
```

## Temperature-Based

```yaml
- alias: "Too Hot Alert"
  description: "Notify when temperature exceeds threshold"
  trigger:
    - platform: numeric_state
      entity_id: sensor.indoor_temperature
      above: 78
  action:
    - service: notify.mobile_app
      data:
        title: "Temperature Alert"
        message: "Indoor temp is {{ states('sensor.indoor_temperature') }}F"
```

## Door/Window Sensors

```yaml
- alias: "Door Left Open"
  description: "Alert if door open for too long"
  trigger:
    - platform: state
      entity_id: binary_sensor.front_door
      to: "on"
      for: "00:05:00"
  action:
    - service: notify.mobile_app
      data:
        title: "Door Alert"
        message: "Front door has been open for 5 minutes"
```
