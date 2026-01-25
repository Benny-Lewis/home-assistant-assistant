# Home Assistant Log Patterns

## Common Error Messages

### Entity Not Found
```
ERROR (MainThread) [homeassistant.helpers.service] Entity light.wrong_name not found
```
**Cause**: Entity ID is incorrect or entity doesn't exist
**Fix**: Check correct entity ID with `hass-cli state list`

### Service Not Found
```
ERROR (MainThread) [homeassistant.components.automation] Error executing script. Service light.turn_onn not found
```
**Cause**: Service name typo
**Fix**: Check correct service name with `hass-cli service list`

### Automation Disabled
```
INFO (MainThread) [homeassistant.components.automation] Automation bedroom_light already disabled
```
**Cause**: Automation was turned off
**Fix**: Enable via HA UI or `hass-cli service call automation.turn_on --arguments entity_id=automation.name`

### Template Error
```
ERROR (MainThread) [homeassistant.helpers.template] TemplateError: UndefinedError: 'states' is undefined
```
**Cause**: Invalid Jinja2 template syntax
**Fix**: Check template syntax in automation

### Connection Issues
```
ERROR (MainThread) [homeassistant.components.mqtt] Unable to connect to broker
```
**Cause**: Integration connectivity issue
**Fix**: Check integration configuration and network

### Entity Unavailable
```
WARNING (MainThread) [homeassistant.components.automation] Automation could not be triggered, entity unavailable
```
**Cause**: Device offline or integration issue
**Fix**: Check device connectivity, restart integration

## Automation Trace Analysis

Use traces to see exactly what happened:
```bash
hass-cli raw get /api/trace/automation.name
```

Trace shows:
- **Trigger details**: What started it, when, what entity state
- **Condition results**: Which conditions passed/failed and why
- **Action results**: What executed, any errors
- **Timing**: How long each step took

## Debugging Checklist

1. **Is automation enabled?**
   ```bash
   hass-cli state get automation.name
   ```
   Look for `state: on`

2. **Did trigger entity reach trigger state?**
   ```bash
   hass-cli raw get "/api/history/period?filter_entity_id=binary_sensor.motion"
   ```

3. **Were conditions met at trigger time?**
   Check trace for condition evaluation results

4. **Did actions execute?**
   Check trace for action execution or errors

5. **Any errors in logs?**
   ```bash
   hass-cli raw get /api/error_log | grep -i "automation_name"
   ```

## Time-Based Issues

### Sun Conditions
- `after: sunset` / `before: sunrise` depend on location settings
- Check Settings > System > General for correct location

### Time Conditions
- Times are in local timezone
- Check HA timezone matches your actual timezone

### Weekday Conditions
- Uses lowercase: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`

## State-Based Issues

### State vs Attribute
- `state` checks main state ("on", "off", "home", "away")
- Attributes need different syntax: `{{ state_attr('entity', 'attribute') }}`

### Numeric States
- Numeric comparisons need `numeric_state` trigger, not `state`
- Values must be numbers, not strings

### State "for" Duration
- `for: "00:05:00"` means entity must stay in state for 5 minutes
- If state changes before duration, trigger won't fire
