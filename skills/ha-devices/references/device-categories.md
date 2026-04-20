# ha-devices — Device Categories

Reference for the main device classes, the entities they typically expose in Home Assistant, and the automations they commonly participate in.

## Lighting

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

## Sensors

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

## Climate

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

## Security

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

## Media

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
