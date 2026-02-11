---
name: ha-config
description: This skill should be used when the user asks about "configuration.yaml", "HA config structure", "packages", "includes", "secrets.yaml", "splitting config files", "YAML organization", mentions Home Assistant configuration organization, or needs help structuring their Home Assistant setup. Provides comprehensive guidance on Home Assistant configuration file organization and best practices.
user-invocable: true
version: 0.1.0
allowed-tools: Read, Grep, Glob
---

# Home Assistant Configuration Patterns

> **This skill is REFERENCE ONLY.** It provides guidance on config organization.
> To modify configuration files, use the appropriate skill:
> - `ha-automations` for automations.yaml
> - `ha-scripts` for scripts.yaml
> - `ha-scenes` for scenes.yaml
> See file-target rules below.

This skill provides guidance on organizing and structuring Home Assistant configuration files effectively.

## File-Target Rules

| File | Owner Skill | Notes |
|------|-------------|-------|
| `configuration.yaml` | Manual/Advanced | Core config, rarely needs changes |
| `automations.yaml` | `ha-automations` | Use automation skill for changes |
| `scripts.yaml` | `ha-scripts` | Use scripts skill for changes |
| `scenes.yaml` | `ha-scenes` | Use scenes skill for changes |
| `secrets.yaml` | NEVER | Never read or write secrets |
| `packages/*.yaml` | Manual/Advanced | Packages are user-organized |
| `.storage/*` | NEVER | Internal HA state, never touch |

## Core Configuration Structure

Home Assistant configuration lives in the config directory, typically `/config` on HAOS or a user-specified path on other installations.

### Essential Files

| File | Purpose | Required |
|------|---------|----------|
| `configuration.yaml` | Main config entry point | Yes |
| `secrets.yaml` | Sensitive data (tokens, passwords) | Recommended |
| `automations.yaml` | UI-created automations | Auto-created |
| `scripts.yaml` | UI-created scripts | Auto-created |
| `scenes.yaml` | UI-created scenes | Auto-created |

### Directory Structure

A well-organized HA config follows this pattern:

```
config/
├── configuration.yaml      # Main entry, imports everything
├── secrets.yaml            # API keys, passwords, tokens
├── automations.yaml        # UI automations (auto-managed)
├── scripts.yaml            # UI scripts (auto-managed)
├── scenes.yaml             # UI scenes (auto-managed)
├── packages/               # Modular config packages
│   ├── climate.yaml
│   ├── lighting.yaml
│   └── security.yaml
├── integrations/           # Integration-specific configs
│   ├── mqtt.yaml
│   └── influxdb.yaml
├── dashboards/             # Lovelace YAML dashboards
│   ├── main.yaml
│   └── mobile.yaml
├── blueprints/             # Automation blueprints
│   └── automation/
├── custom_components/      # HACS and manual integrations
├── www/                    # Static web assets
└── .storage/               # Internal state (do not edit)
```

## Configuration Splitting

### Using !include

Split large configuration files using YAML includes:

```yaml
# configuration.yaml
homeassistant:
  name: Home
  unit_system: metric

# Include single files
automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

# Include integration configs
mqtt: !include integrations/mqtt.yaml
influxdb: !include integrations/influxdb.yaml
```

### Using !include_dir_list

Include all files in a directory as a list (for automations, scripts):

```yaml
# configuration.yaml
automation: !include_dir_list automations/
```

Each file in `automations/` contains one automation without the `automation:` key:

```yaml
# automations/motion_lights.yaml
alias: Motion Lights
trigger:
  - platform: state
    entity_id: binary_sensor.motion_living_room
    to: "on"
action:
  - service: light.turn_on
    target:
      entity_id: light.living_room
```

### Using !include_dir_merge_list

Merge multiple files where each contains a list:

```yaml
# configuration.yaml
automation: !include_dir_merge_list automations/
```

Each file can contain multiple items as a list:

```yaml
# automations/living_room.yaml
- alias: Motion On
  trigger: ...
- alias: Motion Off
  trigger: ...
```

### Using !include_dir_named

Include directory contents as a dictionary (for scripts, input helpers):

```yaml
# configuration.yaml
script: !include_dir_named scripts/
```

Each filename becomes the key:

```yaml
# scripts/morning_routine.yaml (becomes script.morning_routine)
alias: Morning Routine
sequence:
  - service: light.turn_on
    target:
      area_id: bedroom
```

### Using !include_dir_merge_named

Merge multiple files as dictionaries:

```yaml
# configuration.yaml
input_boolean: !include_dir_merge_named input_booleans/
```

## Packages Pattern

Packages group related configuration by domain or room, keeping everything together.

### Enabling Packages

```yaml
# configuration.yaml
homeassistant:
  packages: !include_dir_named packages/
```

### Package Structure

A package file contains all configuration for a specific domain:

```yaml
# packages/climate.yaml
input_number:
  target_temperature:
    name: Target Temperature
    min: 60
    max: 80
    step: 1
    unit_of_measurement: "°F"

sensor:
  - platform: template
    sensors:
      climate_status:
        friendly_name: Climate Status
        value_template: >
          {% if states('climate.main') == 'heat' %}
            Heating to {{ state_attr('climate.main', 'temperature') }}°
          {% else %}
            Idle
          {% endif %}

automation:
  - alias: Climate Away Mode
    trigger:
      - platform: state
        entity_id: input_boolean.away_mode
        to: "on"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.main
        data:
          temperature: 65
```

### Package Benefits

- **Modularity**: All climate-related config in one file
- **Portability**: Copy package to new installation
- **Organization**: Easy to find related configuration
- **Version control**: Track changes to specific domains

## Secrets Management

### secrets.yaml

Store sensitive values in `secrets.yaml`:

```yaml
# secrets.yaml
mqtt_password: "your-secure-password"
latitude: 40.7128
longitude: -74.0060
api_key_weather: "abc123xyz"
```

Reference secrets in configuration:

```yaml
# configuration.yaml
homeassistant:
  latitude: !secret latitude
  longitude: !secret longitude

mqtt:
  password: !secret mqtt_password
```

### Secrets Best Practices

1. **Never commit secrets.yaml to git** - Add to `.gitignore`
2. **Use example file** - Create `secrets.yaml.example` with placeholder values
3. **Document required secrets** - List all secrets in README
4. **Minimal scope** - Only store truly sensitive data

Example `.gitignore`:

```
secrets.yaml
*.db
*.log
.storage/
```

## Configuration Validation

### Check Before Restart

Always validate configuration before restarting:

**Via UI:** Developer Tools → YAML → Check Configuration

**Via CLI (HAOS/Supervised):**
```bash
ha core check
```

**Via hass-cli (remote):**
```bash
hass-cli service call homeassistant.check_config
```

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `found undefined alias` | Missing secret | Add to secrets.yaml |
| `mapping values not allowed` | Indentation error | Fix YAML spacing |
| `duplicate key` | Same key twice | Remove duplicate |
| `could not determine type` | Invalid template | Check Jinja syntax |

## Environment-Specific Configuration

### Using Customize

Set per-entity customizations:

```yaml
# configuration.yaml
homeassistant:
  customize:
    light.kitchen:
      friendly_name: Kitchen Lights
      icon: mdi:ceiling-light
    sensor.temperature:
      device_class: temperature
```

### Using Customize Glob

Apply to multiple entities:

```yaml
homeassistant:
  customize_glob:
    "light.*_ceiling":
      icon: mdi:ceiling-light
    "sensor.*_temperature":
      device_class: temperature
```

## Git Integration for HA Config

### Recommended .gitignore

```gitignore
# Secrets
secrets.yaml

# Database and logs
*.db
*.log
home-assistant.log*

# Internal storage (managed by HA)
.storage/

# Compiled Python
__pycache__/
*.py[cod]

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Backups
*.backup
```

### Git Pull Add-on Configuration

Configure the Git Pull add-on to sync from your repository:

```yaml
# Add-on configuration
git_branch: main
git_command: pull
git_remote: origin
repository: git@github.com:username/ha-config.git
auto_restart: true
repeat:
  active: true
  interval: 300
```

## Common Patterns

### Room-Based Organization

Organize packages by room:

```
packages/
├── living_room.yaml    # All living room entities
├── bedroom.yaml        # All bedroom entities
├── kitchen.yaml        # All kitchen entities
└── common.yaml         # Shared helpers, global automations
```

### Domain-Based Organization

Organize by functionality:

```
packages/
├── lighting.yaml       # All lighting config
├── climate.yaml        # HVAC, temperature
├── security.yaml       # Cameras, locks, alarms
├── media.yaml          # Speakers, TVs
└── presence.yaml       # Device trackers, zones
```

### Hybrid Organization

Combine both approaches:

```
packages/
├── areas/
│   ├── living_room.yaml
│   └── bedroom.yaml
├── domains/
│   ├── climate.yaml
│   └── security.yaml
└── global/
    ├── notifications.yaml
    └── presence.yaml
```

## Quick Reference

### Include Types

| Directive | Result | Use Case |
|-----------|--------|----------|
| `!include file.yaml` | Single file content | One config file |
| `!include_dir_list dir/` | List from files | Automations |
| `!include_dir_merge_list dir/` | Merged lists | Multiple automation files |
| `!include_dir_named dir/` | Dict from filenames | Scripts |
| `!include_dir_merge_named dir/` | Merged dicts | Input helpers |

### Required Reading

For hass-cli commands and git sync setup, ensure the user has completed `/ha-onboard` to configure the connection to their Home Assistant instance.
