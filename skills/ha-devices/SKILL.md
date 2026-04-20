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

> **When NOT to use:** If the user has an existing device that is unavailable, unresponsive,
> or not working correctly, route to `ha-troubleshooting` instead. This skill is for **new device
> setup and device knowledge**, not diagnosing problems with existing devices.

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

## Best Practices

1. **Use local integrations** when possible
2. **Organize by area** from the start
3. **Name consistently** (see ha-naming skill)
4. **Document devices** in README or notes
5. **Update firmware** regularly
6. **Monitor mesh health** for Zigbee/Z-Wave
7. **Backup before changes** to device configs

## Workflow Index

Protocol tradeoffs, category reference tables, setup procedures, and the new-device workflow live in per-skill references:

- `references/integrations.md` — Common integration types (Zigbee, Z-Wave, WiFi, Matter/Thread, Local API) with pros/cons and typical device classes
- `references/device-categories.md` — Reference for Lighting, Sensors, Climate, Security, and Media device categories — the entities they create and the automations they commonly participate in
- `references/workflow.md` — Adding Devices (general + per-protocol), Entity Management, Area Organization, Device Groups, setup-phase Troubleshooting, and the full multi-step New Device Setup Workflow including the device-advisor agent integration and Quick Mode

Related skills: `ha-resolver` (capability snapshot procedure), `ha-naming` (naming conventions applied during device setup), `ha-troubleshooting` (diagnosing problems with existing devices, as noted in "When NOT to use" above).
