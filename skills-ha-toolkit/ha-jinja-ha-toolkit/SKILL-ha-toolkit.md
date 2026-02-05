---
name: Home Assistant Jinja Templating
description: This skill should be used when the user asks about "template", "jinja", "jinja2", "template sensor", "value_template", "state_attr", "states()", mentions Jinja syntax, template debugging, or needs help with Home Assistant templating patterns.
version: 0.1.0
---

# Home Assistant Jinja2 Templating

This skill provides guidance on Jinja2 templating in Home Assistant.

## Template Basics

Templates allow dynamic values in configurations using Jinja2 syntax.

### Syntax
- `{{ }}` - Output expression result
- `{% %}` - Statements (if, for, set)
- `{# #}` - Comments

### Where Templates Work
- Template sensors/binary sensors
- Automation conditions and actions
- Scripts
- Notifications
- Lovelace cards (with card-mod or custom cards)

## State Access

### Get Entity State
```jinja
{{ states('sensor.temperature') }}
{{ states('light.living_room') }}  # Returns 'on' or 'off'
```

### Get State with Default
```jinja
{{ states('sensor.temperature') | default('unknown') }}
{{ states('sensor.temp') | float(0) }}  # Default to 0 if not a number
```

### Get Attribute
```jinja
{{ state_attr('light.living_room', 'brightness') }}
{{ state_attr('climate.main', 'current_temperature') }}
```

### Check State
```jinja
{{ is_state('light.living_room', 'on') }}
{{ is_state_attr('climate.main', 'hvac_mode', 'heat') }}
```

## Filters

### Type Conversion
```jinja
{{ states('sensor.temp') | float }}
{{ states('sensor.count') | int }}
{{ value | string }}
{{ value | bool }}
```

### Rounding
```jinja
{{ states('sensor.temp') | float | round(1) }}
{{ 3.14159 | round(2) }}  # 3.14
```

### Default Values
```jinja
{{ states('sensor.missing') | default('N/A') }}
{{ value | default(0, true) }}  # true = also replace empty strings
```

### String Manipulation
```jinja
{{ 'hello world' | upper }}  # HELLO WORLD
{{ 'HELLO' | lower }}  # hello
{{ 'hello' | capitalize }}  # Hello
{{ 'hello world' | title }}  # Hello World
{{ 'hello' | replace('l', 'x') }}  # hexxo
```

### Time Filters
```jinja
{{ now().strftime('%H:%M') }}  # Current time as HH:MM
{{ as_timestamp(states.sensor.time.last_changed) | timestamp_custom('%Y-%m-%d') }}
{{ states('sensor.timestamp') | as_datetime }}
```

### Math Filters
```jinja
{{ [1, 2, 3, 4] | sum }}  # 10
{{ [1, 2, 3, 4] | max }}  # 4
{{ [1, 2, 3, 4] | min }}  # 1
{{ [1, 2, 3, 4] | average }}  # 2.5
```

## Control Structures

### If/Else
```jinja
{% if is_state('light.living_room', 'on') %}
  Light is on
{% elif is_state('light.living_room', 'off') %}
  Light is off
{% else %}
  Light state unknown
{% endif %}
```

### Ternary (Inline If)
```jinja
{{ 'On' if is_state('light.living_room', 'on') else 'Off' }}
```

### For Loops
```jinja
{% for light in states.light %}
  {{ light.entity_id }}: {{ light.state }}
{% endfor %}
```

### Set Variables
```jinja
{% set temp = states('sensor.temperature') | float %}
{% set is_hot = temp > 80 %}
{{ 'Hot!' if is_hot else 'Comfortable' }}
```

## Time and Date

### Current Time
```jinja
{{ now() }}  # Full datetime
{{ now().hour }}  # Current hour (0-23)
{{ now().minute }}  # Current minute
{{ now().day }}  # Day of month
{{ now().weekday() }}  # 0=Monday, 6=Sunday
```

### Time Comparisons
```jinja
{% if now().hour >= 22 or now().hour < 6 %}
  Nighttime
{% endif %}
```

### Time Since
```jinja
{{ (now() - states.binary_sensor.motion.last_changed).total_seconds() }}
{{ (now() - states.binary_sensor.motion.last_changed).seconds / 60 }}  # Minutes
```

### Formatting
```jinja
{{ now().strftime('%Y-%m-%d %H:%M:%S') }}  # 2024-01-15 14:30:00
{{ now().strftime('%A') }}  # Monday
{{ now().strftime('%B %d') }}  # January 15
```

## Entity Collections

### All Entities of Domain
```jinja
{% for light in states.light %}
  {{ light.entity_id }}
{% endfor %}
```

### Filter by State
```jinja
{% for light in states.light if light.state == 'on' %}
  {{ light.name }} is on
{% endfor %}
```

### Count Entities
```jinja
{{ states.light | selectattr('state', 'eq', 'on') | list | count }}
```

### Entity Attributes
```jinja
{% for sensor in states.sensor %}
  {% if sensor.attributes.device_class == 'temperature' %}
    {{ sensor.name }}: {{ sensor.state }}°
  {% endif %}
{% endfor %}
```

## Template Sensors

### Basic Template Sensor
```yaml
template:
  - sensor:
      - name: "Average Temperature"
        unit_of_measurement: "°F"
        state: >
          {% set temps = [
            states('sensor.living_room_temp') | float(0),
            states('sensor.bedroom_temp') | float(0),
            states('sensor.kitchen_temp') | float(0)
          ] %}
          {{ (temps | sum / temps | count) | round(1) }}
```

### Template Binary Sensor
```yaml
template:
  - binary_sensor:
      - name: "Someone Home"
        state: >
          {{ is_state('person.john', 'home') or
             is_state('person.jane', 'home') }}
```

### With Attributes
```yaml
template:
  - sensor:
      - name: "Climate Status"
        state: "{{ states('climate.main') }}"
        attributes:
          current_temp: "{{ state_attr('climate.main', 'current_temperature') }}"
          target_temp: "{{ state_attr('climate.main', 'temperature') }}"
          mode: "{{ state_attr('climate.main', 'hvac_mode') }}"
```

## Common Patterns

### Safe State Access
```jinja
{% set temp = states('sensor.temperature') %}
{% if temp not in ['unknown', 'unavailable'] %}
  {{ temp | float | round(1) }}°F
{% else %}
  Unavailable
{% endif %}
```

### Multi-Line Templates
```yaml
value_template: >
  {% set value = states('sensor.power') | float(0) %}
  {% if value > 1000 %}
    {{ (value / 1000) | round(2) }} kW
  {% else %}
    {{ value | round(0) }} W
  {% endif %}
```

### Area-Based Queries
```jinja
{% set lights_on = states.light
   | selectattr('state', 'eq', 'on')
   | selectattr('attributes.area_id', 'eq', 'living_room')
   | list | count %}
{{ lights_on }} lights on in living room
```

### Time-Based Values
```jinja
{% set hour = now().hour %}
{% if 6 <= hour < 12 %}
  Good morning
{% elif 12 <= hour < 18 %}
  Good afternoon
{% elif 18 <= hour < 22 %}
  Good evening
{% else %}
  Good night
{% endif %}
```

## Debugging Templates

### Developer Tools
Use Developer Tools → Template to test templates interactively.

### Common Errors

**"UndefinedError"**: Entity doesn't exist
```jinja
# Fix: Use default filter
{{ states('sensor.missing') | default('N/A') }}
```

**"ValueError"**: Can't convert to number
```jinja
# Fix: Use default with type
{{ states('sensor.temp') | float(0) }}
```

**"TemplateError"**: Syntax error
- Check for missing `%}` or `}}`
- Check quote matching
- Verify filter syntax

## Best Practices

1. **Always handle unavailable states**:
   ```jinja
   {{ states('sensor.x') | float(0) }}
   ```

2. **Use descriptive variable names**:
   ```jinja
   {% set living_room_temp = states('sensor.lr_temp') | float %}
   ```

3. **Break complex templates into steps**:
   ```jinja
   {% set raw_value = states('sensor.power') %}
   {% set power = raw_value | float(0) if raw_value not in ['unknown', 'unavailable'] else 0 %}
   {{ power | round(1) }}
   ```

4. **Test templates before deployment**: Use Developer Tools → Template

5. **Document complex logic**: Add comments explaining the template purpose
