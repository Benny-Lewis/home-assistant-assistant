---
description: Generate Home Assistant YAML configurations from descriptions
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion, Glob, Grep
argument-hint: [type] [description]
---

# Generate Home Assistant Configuration

Generate YAML configuration for Home Assistant based on natural language descriptions.

## Supported Types

- **automation** - Automations with triggers, conditions, actions
- **script** - Scripts with sequences of actions
- **scene** - Scenes that set entity states
- **template** - Template sensors and binary sensors
- **dashboard** - Lovelace dashboard cards and views
- **helper** - Input helpers (input_boolean, input_number, etc.)

## Usage Patterns

```
/ha:generate automation turn on kitchen lights when motion detected
/ha:generate script good night routine that turns off all lights
/ha:generate scene movie night with dim lights and TV on
/ha:generate template sensor that shows average temperature
/ha:generate dashboard climate control card for living room
```

## Process

1. **Parse Request**: Identify the type ($1) and description ($2 onwards or $ARGUMENTS)

2. **Gather Context**:
   - Read relevant existing config to match style
   - Check for referenced entities (verify they exist if hass-cli available)
   - Identify naming conventions in use

3. **Generate YAML**:
   - Follow Home Assistant best practices
   - Use consistent naming with existing config
   - Include comments explaining the configuration
   - Add appropriate entity_id, friendly_name, icon

4. **Present to User**:
   - Show the generated YAML
   - Explain what it does
   - Note any assumptions made
   - Ask if they want to write it to a file

5. **Write Configuration** (if requested):
   - Determine appropriate file location
   - For automations: Add to automations.yaml or packages/
   - For scripts: Add to scripts.yaml or packages/
   - Preserve existing content, append new config

## Type-Specific Patterns

### Automation
```yaml
alias: [Descriptive Name]
description: [What this automation does]
trigger:
  - platform: [trigger_type]
    # trigger configuration
condition:
  - condition: [condition_type]
    # condition configuration (optional)
action:
  - service: [domain.service]
    target:
      entity_id: [target_entity]
mode: single  # or queued, restart, parallel
```

### Script
```yaml
alias: [Script Name]
description: [What this script does]
sequence:
  - service: [domain.service]
    target:
      entity_id: [target]
  - delay:
      seconds: 5
  # more steps
mode: single
icon: mdi:script
```

### Scene
```yaml
- name: [Scene Name]
  entities:
    light.living_room:
      state: on
      brightness: 128
    switch.tv:
      state: on
```

### Template Sensor
```yaml
- sensor:
    - name: [Sensor Name]
      unique_id: [unique_id]
      state: >
        {{ states('sensor.source') | float }}
      unit_of_measurement: "°F"
      device_class: temperature
```

## Entity Validation

If hass-cli is configured, validate referenced entities:
```bash
hass-cli entity list | grep -i "entity_name"
```

Warn if referenced entities don't exist and suggest alternatives.

## Style Matching

Before generating, check existing configs to match:
- Naming conventions (snake_case, areas prefix, etc.)
- Comment style
- Organization (packages vs single files)
- Indentation (2 spaces standard)

## Iteration

After presenting generated config:
- Ask if adjustments needed
- Offer to add more triggers/conditions/actions
- Suggest related configurations
- Provide option to test (if automation, can trigger manually)
