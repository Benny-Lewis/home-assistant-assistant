# Dashboard Guide

Card types, layout options, and examples for Home Assistant Lovelace dashboards.

> **Note:** Storage-mode dashboards use JSON internally (via WebSocket API). Examples below use YAML for readability and consistency with YAML-mode dashboards. When working with storage-mode dashboards, the JSON equivalent applies.

## Dashboard Structure

Modern Home Assistant dashboards (2024+) use:
- **Sections view type** (recommended) with grid-based layouts
- **Tile cards** with integrated features for quick controls
- **Grid cards** for organizing content into columns
- **Multiple views** with navigation and deep linking

Legacy patterns to avoid:
- Single-view dashboards with all cards in one long scroll
- Excessive vertical-stack/horizontal-stack instead of grid
- Masonry view (auto-layout) — use sections for precise control
- Putting all entities in generic "entities" cards

### View Types

| Type | Use For |
|------|---------|
| `sections` | Most dashboards (RECOMMENDED) — grid-based, responsive |
| `panel` | Full-screen single cards (maps, cameras, iframes) |
| `sidebar` | Two-column layouts with primary/secondary content |
| `masonry` | Legacy — auto-arranges cards, less control |

### View Configuration

```yaml
views:
  - title: Overview
    path: home
    type: sections
    icon: mdi:home
    max_columns: 4
    badges:
      - entity: person.john
      - entity: sensor.temperature
    sections:
      - title: Climate
        cards: []
      - title: Lights
        cards: []
```

### Sections and Grid Sizing

**`max_columns`** controls how many section columns render:

| Content type | Recommended `max_columns` |
|---|---|
| Tile cards (compact) | 4 |
| Custom cards with legends (mini-graph-card, apexcharts) | 3 |
| Dense multi-entity cards | 2-3 |

**`grid_options.rows`** controls card height within sections:

| Card content | Recommended `rows` |
|---|---|
| Single entity, no extras | 1 (default) |
| Entity with legend or name | 2 |
| Multi-entity with legend + extrema | 3 |
| Graph card with 3+ entities | 3-4 |

Example with explicit sizing:

```yaml
type: custom:mini-graph-card
entities:
  - sensor.living_room_temperature
  - sensor.bedroom_temperature
  - sensor.kitchen_temperature
grid_options:
  columns: 12
  rows: 3
```

---

## Built-in Cards

### Card Categories

| Category | Cards |
|----------|-------|
| **Modern Primary** | tile, area, button, grid |
| **Container** | vertical-stack, horizontal-stack, grid |
| **Logic** | conditional, entity-filter |
| **Display** | sensor, history-graph, statistics-graph, gauge, energy, calendar |
| **Content** | markdown (supports Jinja2 templates), picture-elements, map |
| **Legacy Control** | entity, entities, light, thermostat (use tile instead) |

**Recommendation:** Use `tile` card for most entities.

### Tile Card (Modern Entity Control)

```yaml
type: tile
entity: climate.bedroom
name: Master Bedroom
icon: mdi:thermostat
features:
  - type: target-temperature
  - type: climate-hvac-modes
    style: dropdown
tap_action:
  action: more-info
```

### Grid Card (Layout Tool)

```yaml
type: grid
columns: 3
square: false
cards:
  - type: tile
    entity: light.kitchen
  - type: tile
    entity: light.dining
  - type: tile
    entity: light.hallway
```

### Features (Quick Controls)

Available on: tile, area, humidifier, thermostat cards.

**Climate:** climate-hvac-modes, climate-fan-modes, climate-preset-modes, target-temperature
**Light:** light-brightness, light-color-temp
**Cover:** cover-open-close, cover-position, cover-tilt
**Fan:** fan-speed, fan-direction, fan-oscillate
**Media:** media-player-playback, media-player-volume-slider
**Other:** toggle, button, alarm-modes, lock-commands, numeric-input

Feature `style` options: `dropdown` or `icons`

### Actions

```yaml
tap_action:
  action: toggle

hold_action:
  action: more-info

double_tap_action:
  action: navigate
  navigation_path: /lovelace/lights
```

Action types: `toggle`, `call-service`, `more-info`, `navigate`, `url`, `none`

### Visibility Conditions

```yaml
visibility:
  - condition: user
    users:
      - abc123def456
  - condition: state
    entity: sun.sun
    state: above_horizon
```

### Conditional Card

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

### Markdown Card (Supports Jinja2)

The Markdown Card is one of the few native cards that renders Jinja2 templates server-side:

```yaml
type: markdown
title: Welcome
content: |
  ## Good {{ 'morning' if now().hour < 12 else 'afternoon' }}!
  Temperature: {{ states('sensor.temperature') }}°F
```

Other cards do NOT support Jinja2 — see `ha-jinja` skill for alternatives.

### History Graph and Statistics

```yaml
type: history-graph
title: Temperature History
hours_to_show: 24
entities:
  - entity: sensor.temperature
  - entity: sensor.humidity
```

```yaml
type: statistics-graph
title: Weekly Temperature
entities:
  - sensor.temperature
period: day
days_to_show: 7
stat_types:
  - mean
  - min
  - max
```

### Gauge Card

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

---

## Custom Cards

### Using Custom Cards

Custom cards use the `custom:` prefix:

```yaml
type: custom:mini-graph-card
entity: sensor.temperature
```

### Post-Install Availability

After installing a custom card via HACS, the HA frontend must reload before the card type is recognized. The user should:
1. Hard-refresh the browser (Ctrl+Shift+R / Cmd+Shift+R)
2. If that doesn't work, restart Home Assistant

### Popular HACS Cards

| Card | Repository | Use For |
|------|-----------|---------|
| **Mushroom** | piitaya/lovelace-mushroom | Modern, clean card collection (chips, title, template, etc.) |
| **mini-graph-card** | kalkih/mini-graph-card | Compact sensor graphs with extrema, legends |
| **button-card** | custom-cards/button-card | Highly customizable buttons with templates |
| **card-mod** | thomasloven/lovelace-card-mod | CSS styling for any card |
| **apexcharts-card** | RomRider/apexcharts-card | Professional charts and graphs |
| **layout-card** | thomasloven/lovelace-layout-card | Advanced layout control |

### Custom Card Option Pitfall

Each custom card has its own configuration schema. Do NOT guess option names from other cards — always check the card's README for supported options.

---

## CSS Styling

### Theme Variables

```yaml
# In configuration.yaml
frontend:
  themes:
    my_theme:
      primary-color: "#1E88E5"
      accent-color: "#FF4081"
      card-background-color: "#333"
```

### card-mod (Per-Card Styling)

Requires the card-mod HACS component:

```yaml
type: entities
card_mod:
  style: |
    ha-card {
      --ha-card-background: teal;
      color: var(--primary-color);
    }
entities:
  - light.bed_light
```

---

## HACS Integration

HACS (Home Assistant Community Store) provides 700+ custom cards.

### When to Use HACS vs Built-in

| Use Case | Solution |
|----------|----------|
| Popular community card | HACS install |
| Minor CSS tweaks | card-mod + theme variables |
| Standard entity display | Built-in tile/grid cards |

### Checking Installed HACS Cards

```bash
# List installed frontend resources
hass-cli raw get /api/lovelace/resources
```

---

## Complete Examples

### Multi-View Sections Dashboard

```yaml
title: My Home
views:
  - title: Overview
    path: home
    type: sections
    icon: mdi:home
    max_columns: 4
    badges:
      - entity: person.john
      - entity: person.jane
    sections:
      - title: Quick Actions
        cards:
          - type: grid
            columns: 4
            square: false
            cards:
              - type: button
                name: Lights
                icon: mdi:lightbulb
                tap_action:
                  action: navigate
                  navigation_path: /lovelace/lights
              - type: button
                name: Climate
                icon: mdi:thermostat
                tap_action:
                  action: navigate
                  navigation_path: /lovelace/climate
      - title: Favorites
        cards:
          - type: grid
            columns: 3
            square: false
            cards:
              - type: tile
                entity: light.living_room
                features:
                  - type: light-brightness
              - type: tile
                entity: climate.bedroom
                features:
                  - type: target-temperature
              - type: tile
                entity: lock.front_door

  - title: Lights
    path: lights
    type: sections
    icon: mdi:lightbulb
    max_columns: 3
    sections:
      - title: Living Room
        cards:
          - type: grid
            columns: 3
            cards:
              - type: tile
                entity: light.overhead
                features:
                  - type: light-brightness
              - type: tile
                entity: light.lamp
                features:
                  - type: light-brightness
              - type: tile
                entity: light.accent
                features:
                  - type: light-color-temp
```

### Dashboard Organization Patterns

**By Room:**
```yaml
views:
  - title: Living Room
    path: living-room
  - title: Kitchen
    path: kitchen
  - title: Bedroom
    path: bedroom
```

**By Function:**
```yaml
views:
  - title: Lights
    path: lights
  - title: Climate
    path: climate
  - title: Security
    path: security
```

**By User (visibility control):**
```yaml
views:
  - title: Overview
    path: home
  - title: Admin
    path: admin
    visible:
      - user: admin_user_id
```
