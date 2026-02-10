# Home Assistant Log Patterns

> **Resolver-First Approach:** When you see entity-related errors, use the ha-resolver skill
> to verify entity IDs before assuming typos. Entities may have been renamed, disabled, or
> the device may be offline.

## Common Error Messages

### Entity Not Found
```
ERROR (MainThread) [homeassistant.helpers.service] Entity light.wrong_name not found
```
**Diagnosis Steps:**
1. **Resolve first**: Use `hass-cli state list | grep -i "light"` to find actual entity IDs
2. Check if entity was renamed (common after device re-pairing)
3. Check if entity is disabled in Settings → Entities

**Portable Commands:**
```bash
# Bash/PowerShell
hass-cli state list | Select-String "light"  # PowerShell
hass-cli state list | grep -i "light"        # Bash/Git Bash
```

### Service Not Found
```
ERROR (MainThread) [homeassistant.components.automation] Error executing script. Service light.turn_onn not found
```
**Cause**: Service name typo
**Fix**: Verify service exists:
```bash
hass-cli service list | grep "light"
```

### Automation Disabled
```
INFO (MainThread) [homeassistant.components.automation] Automation bedroom_light already disabled
```
**Cause**: Automation was turned off (intentionally or by error)
**Diagnosis:**
```bash
hass-cli state get automation.bedroom_light
# Look for: state: off
```
**Fix**: Enable via UI or:
```bash
hass-cli service call automation.turn_on --arguments entity_id=automation.bedroom_light
```

### Template Error
```
ERROR (MainThread) [homeassistant.helpers.template] TemplateError: UndefinedError: 'states' is undefined
```
**Cause**: Invalid Jinja2 template syntax or referencing non-existent entity
**Diagnosis:**
1. Check template syntax in Developer Tools → Template
2. Verify all entities in template exist
3. Look for missing quotes or incorrect filter syntax

### Connection Issues
```
ERROR (MainThread) [homeassistant.components.mqtt] Unable to connect to broker
```
**Cause**: Integration connectivity issue (network, credentials, service down)
**Diagnosis:**
1. Check if service is reachable (ping, telnet to port)
2. Verify credentials in integration config
3. Check if service requires restart

### Entity Unavailable
```
WARNING (MainThread) [homeassistant.components.automation] Automation could not be triggered, entity unavailable
```
**Cause**: Device offline, integration issue, or entity disabled
**Diagnosis:**
```bash
hass-cli state get entity.id
# Look for: state: unavailable
```
**Common Fixes:**
- Zigbee/Z-Wave: Check mesh connectivity, device battery
- WiFi: Check device power, network connectivity
- Cloud: Check API status, re-authenticate

## Automation Trace Analysis

Traces show exactly what happened during automation execution.

**Get trace via API:**
```bash
# Note: Replace automation.name with actual automation ID
MSYS_NO_PATHCONV=1 hass-cli raw get /api/trace/automation.name
```

**What traces show:**
| Section | Information |
|---------|-------------|
| Trigger | What started it, timestamp, entity state |
| Conditions | Which passed/failed, why |
| Actions | What executed, errors, timing |
| Variables | Context variables at each step |

## Debugging Checklist

Use this systematic approach instead of guessing:

### 1. Is automation enabled?
```bash
hass-cli state get automation.name
```
Look for `state: on`

### 2. Did trigger entity reach trigger state?
```bash
# Check recent history
MSYS_NO_PATHCONV=1 hass-cli raw get "/api/history/period?filter_entity_id=binary_sensor.motion"
```

### 3. Were conditions met at trigger time?
- Check automation trace for condition evaluation
- Verify time/sun conditions match actual time

### 4. Did actions execute?
- Check trace for action results
- Look for service call errors

### 5. Any errors in logs?
```bash
MSYS_NO_PATHCONV=1 hass-cli raw get /api/error_log
```

## Time-Based Issues

### Sun Conditions
- Depend on location settings (lat/long)
- Check: Settings → System → General → Location
- Verify sunrise/sunset times match expectations

### Time Conditions
- Times use local timezone configured in HA
- Check: Settings → System → General → Time Zone
- Format: `"HH:MM:SS"` (24-hour)

### Weekday Conditions
Use lowercase day abbreviations:
```yaml
weekday:
  - mon
  - tue
  - wed
  - thu
  - fri
  - sat
  - sun
```

## State-Based Issues

### State vs Attribute
```yaml
# Check main state
condition: state
entity_id: light.kitchen
state: "on"

# Check attribute - use template
condition: template
value_template: "{{ state_attr('light.kitchen', 'brightness') > 100 }}"
```

### Numeric States
- Use `numeric_state` trigger for number comparisons
- States are strings - numeric triggers do the conversion
- `above` and `below` are exclusive (not inclusive)

### State "for" Duration
```yaml
trigger:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"  # Must stay "off" for full 5 minutes
```
- If state changes before duration completes, trigger is cancelled
- This is **correct behavior for inactivity detection**

## Evidence Table Template

When reporting troubleshooting results, include:

| Check | Result | Evidence |
|-------|--------|----------|
| Automation enabled | ✅/❌ | `state: on/off` |
| Trigger entity exists | ✅/❌ | Found via `hass-cli state list` |
| Trigger state reached | ✅/❌ | History shows state change |
| Conditions met | ✅/❌ | Trace shows condition result |
| Actions executed | ✅/❌ | Trace shows action result |
| Error in logs | ✅/❌ | Error message: "..." |
