# Scene YAML Syntax Reference

## Basic Structure

```yaml
- name: "Scene Name"
  entities:
    light.living_room:
      state: "on"
      brightness: 200
    light.kitchen:
      state: "off"
```

## Common Patterns

### Movie Night

```yaml
- name: "Movie Night"
  entities:
    light.living_room_main:
      state: "off"
    light.living_room_accent:
      state: "on"
      brightness: 50
      color_temp: 400
    media_player.tv:
      state: "on"
    cover.living_room_blinds:
      state: "closed"
```

### Good Morning

```yaml
- name: "Good Morning"
  entities:
    light.bedroom:
      state: "on"
      brightness: 255
      color_temp: 300
    light.bathroom:
      state: "on"
      brightness: 200
    cover.bedroom_blinds:
      state: "open"
```

### Goodnight

```yaml
- name: "Goodnight"
  entities:
    light.living_room:
      state: "off"
    light.kitchen:
      state: "off"
    light.bedroom:
      state: "on"
      brightness: 30
    lock.front_door:
      state: "locked"
    cover.all_blinds:
      state: "closed"
```

### Away Mode

```yaml
- name: "Away Mode"
  entities:
    light.all_lights:
      state: "off"
    climate.thermostat:
      state: "auto"
      temperature: 65
    lock.front_door:
      state: "locked"
```

### Romantic Dinner

```yaml
- name: "Romantic Dinner"
  entities:
    light.dining_room:
      state: "on"
      brightness: 80
      rgb_color: [255, 180, 100]
    light.kitchen:
      state: "on"
      brightness: 150
    media_player.speaker:
      state: "playing"
      source: "Romantic Playlist"
```

## Entity State Options

### Lights
- `state`: "on" or "off"
- `brightness`: 0-255
- `brightness_pct`: 0-100
- `color_temp`: Kelvin value or mired
- `rgb_color`: [R, G, B] (0-255 each)
- `hs_color`: [hue, saturation]
- `xy_color`: [x, y] CIE color space

### Covers (blinds, shades, garage doors)
- `state`: "open", "closed"
- `position`: 0-100 (0=closed, 100=open)
- `tilt_position`: 0-100

### Climate (thermostats)
- `state`: "heat", "cool", "auto", "off", "fan_only"
- `temperature`: target temperature
- `target_temp_high`: for auto mode
- `target_temp_low`: for auto mode
- `hvac_mode`: same as state

### Locks
- `state`: "locked", "unlocked"

### Media Players
- `state`: "on", "off", "playing", "paused", "idle"
- `source`: input source name
- `volume_level`: 0.0-1.0

### Fans
- `state`: "on", "off"
- `percentage`: 0-100 (speed)
- `preset_mode`: "auto", "smart", etc.

### Switches
- `state`: "on", "off"
