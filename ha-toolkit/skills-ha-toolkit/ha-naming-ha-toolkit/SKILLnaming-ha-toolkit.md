---
name: Home Assistant Naming Conventions
description: This skill should be used when the user asks about "naming", "entity_id", "rename", "naming convention", "entity naming", "device naming", "consistent names", mentions organizing entities, standardizing names, or needs help with Home Assistant naming best practices.
version: 0.1.0
---

# Home Assistant Naming Conventions

This skill provides guidance on consistent naming for Home Assistant entities, devices, and configurations.

## Why Naming Matters

Good naming enables:
- **Findability**: Quickly locate entities
- **Automation**: Easier to reference in automations
- **Grouping**: Natural grouping by area/function
- **Maintenance**: Understand purpose at a glance
- **Voice Control**: Natural spoken commands

## Entity ID Structure

Entity IDs follow the pattern: `domain.identifier`

```
light.living_room_ceiling
sensor.kitchen_temperature
binary_sensor.front_door_contact
switch.garage_outlet_1
```

### Entity ID Rules
- Lowercase only
- Underscores for spaces (no hyphens, spaces)
- No special characters
- Maximum 255 characters
- Must be unique within domain

## Naming Patterns

### Pattern 1: Area First (Recommended)
`{domain}.{area}_{device_type}_{qualifier}`

```
light.living_room_ceiling_main
light.living_room_lamp_corner
sensor.kitchen_temperature
sensor.bedroom_humidity
switch.garage_outlet_1
```

**Benefits:**
- Entities group by area in lists
- Easy to find all devices in a room
- Natural for voice commands: "Turn on living room lights"

### Pattern 2: Device Type First
`{domain}.{device_type}_{area}_{qualifier}`

```
light.ceiling_living_room_main
light.lamp_living_room_corner
sensor.temperature_kitchen
sensor.humidity_bedroom
```

**Benefits:**
- Entities group by function
- Easy to find all sensors, all lights

### Pattern 3: Function First
`{domain}.{function}_{location}`

```
light.overhead_living_room
light.accent_living_room
sensor.temp_inside
sensor.temp_outside
```

**Best for:** Emphasis on what devices do

## Friendly Names

Friendly names are displayed in UI and can include:
- Proper capitalization
- Spaces
- Special characters
- Emojis (sparingly)

### Friendly Name Patterns

**Title Case:**
```yaml
friendly_name: "Living Room Ceiling Light"
friendly_name: "Kitchen Temperature"
```

**With Area Prefix:**
```yaml
friendly_name: "Living Room - Ceiling Light"
friendly_name: "Kitchen - Temperature Sensor"
```

**Concise:**
```yaml
friendly_name: "LR Ceiling"
friendly_name: "Kitchen Temp"
```

## Area Abbreviations

For consistency, use standard abbreviations:

| Full Name | Abbreviation |
|-----------|--------------|
| Living Room | living_room, lr |
| Bedroom | bedroom, br |
| Kitchen | kitchen, kit |
| Bathroom | bathroom, bath |
| Garage | garage, gar |
| Office | office, off |
| Dining Room | dining_room, dr |
| Master Bedroom | master_bedroom, mbr |
| Guest Room | guest_room, guest |

**Recommendation:** Use full names for clarity unless space is limited.

## Device Type Abbreviations

| Full Name | Abbreviation |
|-----------|--------------|
| Temperature | temperature, temp |
| Humidity | humidity, humid |
| Motion | motion |
| Contact | contact |
| Outlet | outlet |
| Dimmer | dimmer |
| Ceiling | ceiling |
| Lamp | lamp |
| Fan | fan |

## Naming by Domain

### Lights
```
light.{area}_{type}_{qualifier}

light.living_room_ceiling
light.living_room_lamp_floor
light.bedroom_nightstand_left
light.bedroom_nightstand_right
light.kitchen_under_cabinet
```

### Sensors
```
sensor.{area}_{measurement}

sensor.living_room_temperature
sensor.living_room_humidity
sensor.outdoor_temperature
sensor.kitchen_motion_lux
```

### Binary Sensors
```
binary_sensor.{area}_{type}

binary_sensor.front_door_contact
binary_sensor.living_room_motion
binary_sensor.kitchen_window
binary_sensor.garage_door
```

### Switches
```
switch.{area}_{device}_{qualifier}

switch.living_room_fan
switch.garage_outlet_1
switch.office_computer
```

### Climate
```
climate.{area}

climate.main
climate.upstairs
climate.basement
```

### Covers
```
cover.{area}_{type}

cover.living_room_blinds
cover.bedroom_curtains
cover.garage_door
```

### Media Players
```
media_player.{area}_{device}

media_player.living_room_tv
media_player.kitchen_speaker
media_player.office_sonos
```

## Automation Naming

### Pattern: `{Trigger}: {Area} {Action}`
```yaml
alias: "Motion: Living Room Lights On"
alias: "Sunset: Outdoor Lights On"
alias: "Schedule: Morning HVAC"
alias: "Presence: Away Mode Enable"
```

### Pattern: `{Area} - {Description}`
```yaml
alias: "Living Room - Motion Lights"
alias: "Kitchen - Stove Timer Alert"
alias: "Bedroom - Goodnight Routine"
```

### Pattern: `{Category}: {Description}`
```yaml
alias: "Lighting: Motion-activated hallway"
alias: "Security: Door open alert"
alias: "Climate: Away mode temperature"
```

## Script Naming

Scripts should describe the action:
```yaml
script.turn_off_all_lights
script.goodnight_routine
script.morning_routine
script.movie_mode
script.flash_lights_alert
```

## Scene Naming

Scenes should be descriptive and memorable:
```yaml
scene.movie_night
scene.dinner_party
scene.good_morning
scene.all_lights_off
scene.romantic_dinner
scene.work_from_home
```

## Input Helper Naming

### Input Booleans
```
input_boolean.{purpose}

input_boolean.guest_mode
input_boolean.vacation_mode
input_boolean.automation_enabled
input_boolean.night_mode
```

### Input Numbers
```
input_number.{target}_{setting}

input_number.living_room_brightness_default
input_number.thermostat_away_temp
input_number.motion_light_timeout
```

### Input Selects
```
input_select.{purpose}

input_select.house_mode
input_select.alarm_status
input_select.lighting_scene
```

## Migration Strategy

When renaming existing entities:

1. **Audit current naming**: Use `/ha:audit-naming`
2. **Choose convention**: Pick pattern that fits majority
3. **Plan changes**: Use `/ha:plan-naming`
4. **Update dependencies**: Find all references
5. **Execute carefully**: Use `/ha:apply-naming`
6. **Test thoroughly**: Verify automations work

## Anti-Patterns to Avoid

### Generic Names
```
# Bad
light.light_1
switch.switch
sensor.sensor_2

# Good
light.living_room_ceiling
switch.garage_fan
sensor.outdoor_temperature
```

### Inconsistent Patterns
```
# Bad (mixed patterns)
light.living_room_ceiling
light.lamp_bedroom
light.kit_light

# Good (consistent)
light.living_room_ceiling
light.bedroom_lamp
light.kitchen_overhead
```

### Overly Long Names
```
# Bad
light.living_room_main_ceiling_light_above_couch

# Good
light.living_room_ceiling_main
```

### Abbreviations Without Context
```
# Bad
light.lr_cl_1
sensor.t_o

# Good
light.living_room_ceiling_1
sensor.temperature_outdoor
```

## Best Practices Summary

1. **Be consistent**: Choose a pattern and stick to it
2. **Be descriptive**: Names should explain what/where
3. **Use areas**: Prefix with location for natural grouping
4. **Avoid numbers when possible**: Use qualifiers (left, right, main)
5. **Plan for growth**: Leave room for additional devices
6. **Document conventions**: Record your naming rules
7. **Automate enforcement**: Use hooks to validate new entities
