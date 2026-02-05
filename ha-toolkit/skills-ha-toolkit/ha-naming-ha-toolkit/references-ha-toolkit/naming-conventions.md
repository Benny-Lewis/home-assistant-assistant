# Naming Conventions Reference

Detailed tables and examples for entity naming. See `SKILL-naming-ha-toolkit.md` for overview.

## Area Abbreviations

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
| Basement | basement, bsmt |
| Attic | attic |
| Hallway | hallway, hall |
| Laundry | laundry |
| Porch | porch |
| Patio | patio |
| Yard | yard |

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
| Thermostat | thermostat, thermo |
| Speaker | speaker, spkr |
| Television | tv |

## Naming by Domain

### Lights
```
light.{area}_{type}_{qualifier}

light.living_room_ceiling
light.living_room_lamp_floor
light.bedroom_nightstand_left
light.bedroom_nightstand_right
light.kitchen_under_cabinet
light.office_desk
light.garage_overhead
light.porch_entry
```

### Sensors
```
sensor.{area}_{measurement}

sensor.living_room_temperature
sensor.living_room_humidity
sensor.outdoor_temperature
sensor.kitchen_motion_lux
sensor.office_air_quality
sensor.basement_water_leak
```

### Binary Sensors
```
binary_sensor.{area}_{type}

binary_sensor.front_door_contact
binary_sensor.living_room_motion
binary_sensor.kitchen_window
binary_sensor.garage_door
binary_sensor.basement_flood
binary_sensor.office_occupancy
```

### Switches
```
switch.{area}_{device}_{qualifier}

switch.living_room_fan
switch.garage_outlet_1
switch.office_computer
switch.bedroom_heater
switch.kitchen_disposal
```

### Climate
```
climate.{area}

climate.main
climate.upstairs
climate.basement
climate.garage
```

### Covers
```
cover.{area}_{type}

cover.living_room_blinds
cover.bedroom_curtains
cover.garage_door
cover.kitchen_shade
```

### Media Players
```
media_player.{area}_{device}

media_player.living_room_tv
media_player.kitchen_speaker
media_player.office_sonos
media_player.bedroom_echo
```

### Locks
```
lock.{location}

lock.front_door
lock.garage_entry
lock.back_door
```

### Cameras
```
camera.{location}_{view}

camera.front_porch
camera.backyard
camera.garage_interior
camera.driveway
```

## Input Helper Naming

### Input Booleans
```
input_boolean.{purpose}

input_boolean.guest_mode
input_boolean.vacation_mode
input_boolean.automation_enabled
input_boolean.night_mode
input_boolean.party_mode
```

### Input Numbers
```
input_number.{target}_{setting}

input_number.living_room_brightness_default
input_number.thermostat_away_temp
input_number.motion_light_timeout
input_number.alarm_code_retries
```

### Input Selects
```
input_select.{purpose}

input_select.house_mode
input_select.alarm_status
input_select.lighting_scene
input_select.hvac_preset
```

### Input Datetimes
```
input_datetime.{purpose}

input_datetime.morning_alarm
input_datetime.vacation_start
input_datetime.vacation_end
```

## Automation Naming Patterns

### Pattern A: `{Trigger}: {Area} {Action}`
```yaml
alias: "Motion: Living Room Lights On"
alias: "Sunset: Outdoor Lights On"
alias: "Schedule: Morning HVAC"
alias: "Presence: Away Mode Enable"
```

### Pattern B: `{Area} - {Description}`
```yaml
alias: "Living Room - Motion Lights"
alias: "Kitchen - Stove Timer Alert"
alias: "Bedroom - Goodnight Routine"
```

### Pattern C: `{Category}: {Description}`
```yaml
alias: "Lighting: Motion-activated hallway"
alias: "Security: Door open alert"
alias: "Climate: Away mode temperature"
```

## Script and Scene Naming

### Scripts (action-focused)
```yaml
script.turn_off_all_lights
script.goodnight_routine
script.morning_routine
script.movie_mode
script.flash_lights_alert
script.announce_visitor
```

### Scenes (state-focused)
```yaml
scene.movie_night
scene.dinner_party
scene.good_morning
scene.all_lights_off
scene.romantic_dinner
scene.work_from_home
scene.bright_cleaning
```

## Timer Naming

```
timer.{area}_{purpose}

timer.kitchen_cooking
timer.bathroom_fan_shutoff
timer.living_room_motion_cooldown
timer.garage_door_warning
```
