---
name: ha-lovelace
description: This skill should be used when the user asks about "dashboard", "lovelace", "card", "view", "theme", "UI", mentions dashboard design, card configuration, dashboard layout, or needs help with Home Assistant Lovelace dashboard creation and customization.
version: 0.1.0
allowed-tools: Read, Grep, Glob
---

# Home Assistant Lovelace Dashboards

This skill provides guidance on creating effective Lovelace dashboards.

## Important: Templating in Lovelace

**Most Lovelace cards do NOT support Jinja2 templating.**

If you type `{{ states('sensor.x') }}` in an Entities card, Button card, or most other cards,
it will display as literal text - NOT the sensor value.

**Exception: Markdown Card** - The Markdown Card renders templates server-side. This is one of
the few native cards that supports Jinja. See the Markdown Card section below.

For dynamic values in other cards, use one of these approaches:
1. **Template entities** - Create a template sensor/binary_sensor, display that entity
2. **Custom cards** - Install cards like `button-card` that implement their own templating

See `ha-jinja` skill for templating reference.

## Dashboard Structure

Dashboards contain views, views contain cards.

```yaml
views:
  - title: Home
    path: home
    icon: mdi:home
    cards:
      - type: entities
        entities:
          - light.living_room
```

## View Configuration

### Basic View
```yaml
views:
  - title: "Living Room"
    path: living-room
    icon: mdi:sofa
    badges: []
    cards: []
```

### View Options
```yaml
views:
  - title: "Main"
    path: main
    icon: mdi:home
    theme: dark  # Optional theme override
    background: "center / cover no-repeat url('/local/bg.jpg')"
    panel: false  # true = single card fills view
    badges:
      - entity: person.john
      - entity: sensor.temperature
    cards: []
```

## Common Card Types

### Entities Card
List entities with states:
```yaml
type: entities
title: Living Room
entities:
  - entity: light.living_room
    name: Main Light
  - entity: switch.tv
  - type: divider
  - entity: climate.living_room
```

### Entity Card
Single entity display:
```yaml
type: entity
entity: sensor.temperature
name: Temperature
icon: mdi:thermometer
```

### Button Card
Tap to trigger action:
```yaml
type: button
entity: light.bedroom
name: Bedroom Light
icon: mdi:lightbulb
tap_action:
  action: toggle
```

### Light Card
Control lights with brightness:
```yaml
type: light
entity: light.living_room
name: Living Room
```

### Thermostat Card
Climate control:
```yaml
type: thermostat
entity: climate.main
```

### Weather Card
Weather display:
```yaml
type: weather-forecast
entity: weather.home
show_forecast: true
```

### Picture Elements Card
Image with overlays:
```yaml
type: picture-elements
image: /local/floorplan.png
elements:
  - type: state-icon
    entity: light.kitchen
    style:
      top: 30%
      left: 40%
```

### History Graph Card
State history:
```yaml
type: history-graph
title: Temperature History
hours_to_show: 24
entities:
  - entity: sensor.temperature
  - entity: sensor.humidity
```

### Gauge Card
Visual gauge:
```yaml
type: gauge
entity: sensor.cpu_usage
name: CPU
min: 0
max: 100
severity:
  green: 0
  yellow: 50
  red: 80
```

### Glance Card
Compact entity display:
```yaml
type: glance
title: Family
entities:
  - entity: person.john
  - entity: person.jane
  - entity: person.kids
```

### Horizontal/Vertical Stack
Layout cards:
```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: button
        entity: light.one
      - type: button
        entity: light.two
  - type: entities
    entities:
      - sensor.temperature
```

### Grid Card
Responsive grid layout:
```yaml
type: grid
columns: 3
square: false
cards:
  - type: button
    entity: light.one
  - type: button
    entity: light.two
  - type: button
    entity: light.three
```

### Conditional Card
Show based on state:
```yaml
type: conditional
conditions:
  - entity: input_boolean.show_details
    state: "on"
card:
  type: entities
  entities:
    - sensor.details
```

### Markdown Card (Supports Templates!)
Rich text content with Jinja2 - **this is the exception** where Jinja works natively:
```yaml
type: markdown
title: Welcome
content: |
  ## Good {{ 'morning' if now().hour < 12 else 'afternoon' }}!

  Temperature: {{ states('sensor.temperature') }}°F
```
Note: Templates are rendered server-side. Other cards do NOT support this.

## Tap Actions

Available on most cards:
```yaml
tap_action:
  action: toggle  # toggle entity state

tap_action:
  action: call-service
  service: light.turn_on
  service_data:
    entity_id: light.bedroom
    brightness_pct: 50

tap_action:
  action: navigate
  navigation_path: /lovelace/settings

tap_action:
  action: url
  url_path: https://example.com

tap_action:
  action: more-info  # Show entity details

tap_action:
  action: none  # Disable tap
```

Also: `hold_action`, `double_tap_action`

## Dashboard Organization

### By Room
```yaml
views:
  - title: Living Room
    path: living-room
    cards: [...]
  - title: Kitchen
    path: kitchen
    cards: [...]
  - title: Bedroom
    path: bedroom
    cards: [...]
```

### By Function
```yaml
views:
  - title: Lights
    path: lights
    cards: [...]
  - title: Climate
    path: climate
    cards: [...]
  - title: Security
    path: security
    cards: [...]
```

### By User
```yaml
views:
  - title: Overview
    path: home
  - title: Admin
    path: admin
    visible:
      - user: admin_user_id
```

## Responsive Design

### Masonry Layout (Default)
Cards automatically arrange based on screen size.

### Grid Layout
Control columns:
```yaml
type: grid
columns: 3
cards: [...]
```

### Panel Mode
Single card fills view:
```yaml
views:
  - title: Floor Plan
    panel: true
    cards:
      - type: picture-elements
        image: /local/floor.png
```

### Mobile Considerations
- Use vertical stacks for mobile-first design
- Larger tap targets (buttons over toggles)
- Fewer columns on mobile

## Themes

### Apply Theme
```yaml
views:
  - title: Dark Mode
    theme: dark
    cards: [...]
```

### Custom Theme
```yaml
# In configuration.yaml
frontend:
  themes:
    my_theme:
      primary-color: "#1E88E5"
      accent-color: "#FF4081"
      card-background-color: "#333"
```

## YAML Mode vs UI Mode

### Enable YAML Mode
In dashboard settings, enable "Edit in YAML"

### Dashboard File
```yaml
# ui-lovelace.yaml
title: My Home
views:
  - title: Home
    cards: [...]
```

Reference in configuration.yaml:
```yaml
lovelace:
  mode: yaml
  resources:
    - url: /local/card.js
      type: module
```

## Best Practices

1. **Group related entities**: Use cards to organize by room/function
2. **Use icons consistently**: Same icon family (mdi:)
3. **Provide feedback**: Use state colors, badges
4. **Mobile-first**: Design for smallest screen first
5. **Use sections**: Add headers between card groups
6. **Don't overcrowd**: Better to have more views than cluttered views
7. **Use conditional cards**: Hide irrelevant information
8. **Test on multiple devices**: Check responsive behavior
