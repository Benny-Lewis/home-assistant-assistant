# Script YAML Syntax Reference

## Basic Structure

```yaml
script_name:
  alias: "Friendly Name"
  description: "What this script does"
  mode: single
  sequence:
    - service: domain.service
      target:
        entity_id: entity.id
```

## Mode Options

- `single` (default): Script runs once, ignores additional triggers while running
- `restart`: Stop current run and start new one
- `queued`: Queue additional runs (max_queued: N)
- `parallel`: Run multiple instances simultaneously (max: N)

## Common Patterns

### Multi-Step Sequence

```yaml
movie_mode:
  alias: "Movie Mode"
  description: "Set up living room for movie watching"
  sequence:
    - service: light.turn_off
      target:
        entity_id: light.living_room_main
    - service: light.turn_on
      target:
        entity_id: light.living_room_accent
      data:
        brightness_pct: 20
    - service: media_player.turn_on
      target:
        entity_id: media_player.tv
```

### With Variables (fields)

```yaml
announce:
  alias: "Announce Message"
  description: "Play announcement on speakers"
  fields:
    message:
      description: "Message to announce"
      example: "Dinner is ready"
  sequence:
    - service: tts.speak
      target:
        entity_id: media_player.kitchen_speaker
      data:
        message: "{{ message }}"
```

### With Delays

```yaml
gradual_wakeup:
  alias: "Gradual Wake Up"
  description: "Slowly increase light brightness"
  sequence:
    - service: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 10
    - delay: "00:05:00"
    - service: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 50
    - delay: "00:05:00"
    - service: light.turn_on
      target:
        entity_id: light.bedroom
      data:
        brightness_pct: 100
```

### With Conditions (choose)

```yaml
smart_lights:
  alias: "Smart Lights"
  description: "Adjust lights based on time of day"
  sequence:
    - choose:
        - conditions:
            - condition: sun
              before: sunrise
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.bedroom
              data:
                brightness_pct: 30
        - conditions:
            - condition: sun
              after: sunset
          sequence:
            - service: light.turn_on
              target:
                entity_id: light.bedroom
              data:
                brightness_pct: 80
      default:
        - service: light.turn_on
          target:
            entity_id: light.bedroom
          data:
            brightness_pct: 100
```

### With Wait

```yaml
garage_check:
  alias: "Garage Door Check"
  description: "Close garage if still open after delay"
  sequence:
    - delay: "00:10:00"
    - condition: state
      entity_id: cover.garage_door
      state: "open"
    - service: cover.close_cover
      target:
        entity_id: cover.garage_door
```
