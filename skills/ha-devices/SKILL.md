---
name: ha-devices
description: Use when user asks about "device", "integration", "entity", "add device", "new device", "just added", "device setup", "Zigbee", "Z-Wave", "WiFi devices", mentions device types, integration configuration, or needs help understanding Home Assistant device and integration concepts.
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, AskUserQuestion, Task
---

# Home Assistant Devices and Integrations

> **Safety Invariant #1:** Before suggesting automations/scenes for devices, get a capability snapshot.
> See the ha-resolver skill for the procedure.

This skill provides guidance on Home Assistant devices, integrations, and entity management.

## Capability Snapshot Contract

**Before generating YAML that controls a device, you MUST:**

1. Resolve the entity_id via `hass-cli state list`
2. Get capabilities via `hass-cli state get <entity_id>`
3. Check `supported_features`, `supported_color_modes`, `hvac_modes`, etc.
4. Only emit attributes the device actually supports

**Example for a light:**
```bash
hass-cli state get light.living_room
# Check: supported_color_modes, min_mireds, max_mireds, supported_features
```

If `supported_color_modes` only includes `brightness`, do NOT include `color_temp` or `rgb_color` in scenes/automations.

## Concepts

### Devices vs Entities vs Integrations

- **Integration**: Connection method (Zigbee, Z-Wave, WiFi, cloud)
- **Device**: Physical hardware (bulb, sensor, switch)
- **Entity**: Controllable/readable aspect of a device

One device can have multiple entities:
```
Device: "Living Room Motion Sensor"
├── binary_sensor.living_room_motion (motion detection)
├── sensor.living_room_motion_temperature (temperature)
├── sensor.living_room_motion_lux (light level)
└── sensor.living_room_motion_battery (battery level)
```

## Common Integration Types

### Zigbee
**Via:** Zigbee2MQTT, ZHA, deCONZ

**Pros:**
- Low power, long battery life
- Mesh networking (devices relay signals)
- Local control, no cloud required
- Wide device compatibility

**Cons:**
- Requires coordinator hardware
- Can have pairing complexity

**Common devices:** Sensors, bulbs, switches, buttons

### Z-Wave
**Via:** Z-Wave JS, Z-Wave JS UI

**Pros:**
- Mature, reliable protocol
- Strong mesh networking
- No WiFi interference (different frequency)
- Good security

**Cons:**
- More expensive devices
- Requires hub/stick
- Regional frequency differences

**Common devices:** Locks, sensors, switches, thermostats

### WiFi
**Via:** Direct integration, Tuya, ESPHome

**Pros:**
- No additional hub needed
- Often cheaper devices
- Easy setup

**Cons:**
- Clogs WiFi network
- Usually requires cloud
- Higher power consumption (no battery)

**Common devices:** Plugs, bulbs, cameras

### Matter/Thread
**Via:** Matter integration

**Pros:**
- Cross-platform standard
- Local control
- Future-proof
- Thread mesh networking

**Cons:**
- New standard, evolving
- Limited device selection currently

### Local API
**Via:** Device-specific integrations

Examples: Philips Hue, LIFX, Shelly, Tasmota

**Pros:**
- Full local control
- Rich features
- Reliable

**Cons:**
- Device-specific setup

## Device Categories

### Lighting

**Types:**
- Bulbs (color, white, dimmable)
- Light strips
- Switches (smart switches, dimmers)
- Controllers

**Entities created:**
- `light.*` - Main control
- `sensor.*_power` - Power consumption
- `binary_sensor.*_update` - Firmware status

**Common automations:**
- Motion-activated
- Time-based scenes
- Sunrise/sunset dimming

### Sensors

**Types:**
- Motion (PIR, mmWave)
- Temperature/humidity
- Contact (door/window)
- Presence
- Light level (lux)
- Air quality

**Entities created:**
- `binary_sensor.*` - On/off states
- `sensor.*` - Measurements

**Common automations:**
- Motion → lights
- Temperature → HVAC
- Contact → security alerts

### Climate

**Types:**
- Thermostats
- Smart vents
- Fans
- Space heaters

**Entities created:**
- `climate.*` - Main control
- `sensor.*_temperature` - Current temp
- `sensor.*_humidity` - Humidity

**Common automations:**
- Schedule-based
- Presence-based
- Window-open detection

### Security

**Types:**
- Cameras
- Door locks
- Alarm panels
- Video doorbells

**Entities created:**
- `camera.*` - Video feed
- `lock.*` - Lock control
- `alarm_control_panel.*` - Arm/disarm
- `binary_sensor.*` - Sensors

**Common automations:**
- Lock on departure
- Notifications on events
- Recording triggers

### Media

**Types:**
- TVs
- Speakers
- Media players
- Streaming devices

**Entities created:**
- `media_player.*` - Playback control
- `remote.*` - Remote control

**Common automations:**
- Voice announcements
- Media-triggered lighting
- Sleep timers

## Adding Devices

### General Process

1. **Physical setup**: Power on, put in pairing mode
2. **Add integration**: Settings → Devices & Services → Add Integration
3. **Discover device**: Auto-discover or manual add
4. **Configure**: Set area, name, options
5. **Test**: Verify entities work

### Zigbee Devices (via ZHA)

1. Enable ZHA integration
2. Go to ZHA → Add Device
3. Put device in pairing mode (usually hold button)
4. Wait for discovery
5. Device appears with entities

### Z-Wave Devices

1. Enable Z-Wave JS integration
2. Put controller in inclusion mode
3. Put device in inclusion mode
4. Complete secure inclusion if prompted
5. Device appears with entities

### WiFi Devices

1. Set up device with manufacturer app
2. Find integration in HA (Settings → Add Integration)
3. Enter credentials/link accounts
4. Devices import automatically

### ESPHome Devices

1. Flash device with ESPHome firmware
2. Configure YAML with sensors/outputs
3. HA auto-discovers device
4. Adopt device in ESPHome integration

## Entity Management

### Customize Entities

Via UI or YAML:
```yaml
homeassistant:
  customize:
    light.living_room:
      friendly_name: "Living Room Light"
      icon: mdi:ceiling-light
```

### Hide Entities

```yaml
homeassistant:
  customize:
    sensor.unneeded:
      hidden: true
```

Or disable in entity settings.

### Entity Registry

Entities are registered in `.storage/core.entity_registry`

To rename entity_id:
1. Settings → Devices & Services → Entities
2. Find entity → Settings icon
3. Change entity ID

Or via hass-cli:
```bash
hass-cli entity rename old_id new_id
```

### Device Registry

Devices registered in `.storage/core.device_registry`

Customize device:
1. Settings → Devices & Services → Devices
2. Find device → Edit
3. Change name, area, etc.

## Area Organization

### Create Areas

Settings → Areas & Zones → Create Area

### Assign Devices to Areas

1. Go to device page
2. Click area dropdown
3. Select or create area

### Benefits of Areas

- Dashboard organization
- Voice control: "Turn off living room"
- Area-based automations
- Grouped statistics

## Device Groups

### Light Groups
```yaml
light:
  - platform: group
    name: "Living Room Lights"
    entities:
      - light.living_room_ceiling
      - light.living_room_lamp_1
      - light.living_room_lamp_2
```

### Cover Groups
```yaml
cover:
  - platform: group
    name: "All Blinds"
    entities:
      - cover.living_room_blinds
      - cover.bedroom_blinds
```

## Troubleshooting

### Device Unavailable

1. Check physical device power
2. Check network/hub connectivity
3. Reload integration
4. Check device logs
5. Re-pair if necessary

### Entity Missing

1. Check device page for all entities
2. Some may be disabled by default
3. Enable in entity settings

### Slow Response

1. Check network latency
2. Zigbee: Check mesh quality
3. WiFi: Check signal strength
4. Cloud: Check API status

### Device Not Pairing

1. Move closer to coordinator
2. Reset device
3. Check coordinator firmware
4. Try different pairing method

## Best Practices

1. **Use local integrations** when possible
2. **Organize by area** from the start
3. **Name consistently** (see ha-naming skill)
4. **Document devices** in README or notes
5. **Update firmware** regularly
6. **Monitor mesh health** for Zigbee/Z-Wave
7. **Backup before changes** to device configs

---

## New Device Setup Workflow

> **Safety Invariant #1:** Before suggesting automations for the device,
> get a capability snapshot. See the ha-resolver skill.

Guide the user through setting up a new device in Home Assistant: naming, automations, dashboard integration, and related configurations.

### Capability Check (Mandatory)

**Before suggesting any automations or scenes, get device capabilities:**

```bash
# Resolve actual entity_id
hass-cli state list | grep -i "<device_name>"

# Get capability snapshot
hass-cli state get <entity_id>
```

Check for:
- `supported_features` - What the device can do
- `supported_color_modes` - For lights
- `hvac_modes` - For climate devices

**Only suggest automations using supported capabilities.**

### Trigger the Device Advisor Agent

This workflow launches the `device-advisor` agent to provide comprehensive assistance.

Use the Task tool to spawn the device-advisor agent with the following context:

```
Help the user set up a new device in Home Assistant.

Context from the user: $ARGUMENTS

Process:
1. Identify what device was added
2. Check existing naming conventions
3. Suggest appropriate naming
4. Recommend automations for this device type
5. Offer dashboard integration
6. Check for device groups/relationships
```

### New Device Steps

#### Step 1: Device Identification

Ask the user:
- What device did you add? (type, brand, integration)
- What room/area is it in?
- What is its current name in HA?

Or detect automatically if hass-cli available:
```bash
# Check recently added entities
hass-cli entity list --domain [device_domain]
```

#### Step 2: Naming Consultation

Based on the device and existing naming conventions:
- Suggest entity_id following established pattern
- Suggest friendly_name
- Assign to appropriate area

#### Step 3: Common Automations by Device Type

Based on device type, suggest relevant automations:

**Lights:**
- Motion-activated on/off
- Time-based schedules
- Brightness based on time of day
- Away mode simulation

**Motion Sensors:**
- Trigger lights
- Security alerts when away
- Occupancy tracking

**Door/Window Sensors:**
- Security alerts when open too long
- Climate control (pause HVAC when windows open)
- Arrival/departure detection

**Climate (Thermostat):**
- Schedule-based temperature
- Presence-based adjustment
- Energy-saving modes

**Switches/Plugs:**
- Schedule-based on/off
- Energy monitoring alerts
- Device protection (auto-off)

**Cameras:**
- Motion detection notifications
- Recording triggers
- Privacy mode automations

#### Step 4: Dashboard Integration

Offer to add the device to a dashboard:
- Identify relevant dashboard
- Suggest appropriate card type
- Generate card YAML
- Position in logical location

#### Step 5: Device Relationships

Check for related devices:
- Same room devices (group lights)
- Complementary devices (motion sensor + light)
- Device groups (all bedroom devices)

Suggest creating groups or scenes.

#### Step 6: Testing

After setup:
- Test entity accessibility
- Test automations (if created)
- Verify dashboard display

### Device Type Templates

**Light Device:**
```yaml
suggested_automations:
  - Motion-activated (if motion sensor in same area)
  - Sunset turn on
  - Bedtime turn off
dashboard_card: light
groups: "{area}_lights"
```

**Sensor Device:**
```yaml
suggested_automations:
  - Alert on threshold
  - History graph
  - Average calculations
dashboard_card: sensor, history-graph
```

**Switch Device:**
```yaml
suggested_automations:
  - Schedule-based
  - Integration with related devices
dashboard_card: button, entities
```

### New Device Output

```
New Device Setup Complete

Device: Philips Hue Bulb
Type: Light
Area: Living Room

Naming Applied:
  entity_id: light.living_room_ceiling
  friendly_name: Living Room Ceiling
  area: Living Room

Automations Created:
  Motion: Living Room Lights On
  Sunset: Living Room Lights Dim

Dashboard Updated:
  Added to "Main" dashboard, Living Room section

Groups:
  Added to group.living_room_lights

Next Steps:
  - Test the motion automation
  - Adjust brightness levels if needed
  - Run /ha-deploy to sync changes
```

### Quick Mode

For experienced users, support quick setup:
```
/ha-devices light kitchen ceiling
```

This would:
1. Create entity with naming convention applied
2. Skip automation suggestions
3. Offer quick dashboard add
