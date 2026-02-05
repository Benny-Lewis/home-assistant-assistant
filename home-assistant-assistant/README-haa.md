# Home Assistant Assistant

> **Manage your Home Assistant with natural language.** Create automations, scripts, and scenes by simply describing what you want.

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that brings conversational AI to Home Assistant configuration management. No more YAML wrestling or UI clicking—just tell Claude what you want your smart home to do.

## Why Use This Plugin?

**Before**: Manually editing YAML, looking up entity IDs, debugging syntax errors, hoping you don't break your config.

**After**: "When motion is detected in the hallway after sunset, turn on the light for 2 minutes."

The plugin handles entity resolution, YAML generation, validation, git commits, and deployment—all through conversation.

## Features

### Natural Language Automation

Create complex automations by describing them in plain English:

```
"Turn on the porch light at sunset and off at sunrise"

"When the front door opens and nobody is home, send me a notification"

"If the temperature goes above 75°F between 6 PM and 9 PM, turn on the AC"
```

### Scripts & Scenes

**Scripts** for reusable action sequences:
```
"Create a script that dims all lights to 20%, pauses for 5 seconds, then turns them off"
```

**Scenes** for device state presets:
```
"Create a 'Movie Night' scene: living room lights at 10%, TV bias lighting on, blinds closed"
```

### Safe Deployment Workflow

Every change goes through a safety pipeline:

1. **Validate** - Syntax checking, entity verification, service validation
2. **Preview** - See the diff before anything changes
3. **Confirm** - Explicit approval required (configurable)
4. **Deploy** - Git commit, push, and reload Home Assistant
5. **Verify** - Confirms changes appear in HA

### Git-Based Version Control

Your configuration is always safe:

- Every change is committed to git with a descriptive message
- View history and see exactly what changed
- Rollback to any previous state with one command
- Works with your existing HA config repository

### Intelligent Troubleshooting

When automations don't work as expected:

```
"Why didn't my bedroom automation trigger last night?"
```

The plugin analyzes:
- Automation state and enablement
- Trigger conditions and whether they occurred
- Execution traces and error logs
- Entity history and state changes

Then provides findings and suggestions to fix the issue.

## Quick Start

### Prerequisites

1. **Home Assistant** instance accessible on your network
2. **Claude Code** installed ([docs](https://docs.anthropic.com/en/docs/claude-code))
3. **hass-cli** installed:
   ```bash
   pip install homeassistant-cli
   ```
4. Your HA config directory set up as a **git repository**

### Installation

Install the plugin in Claude Code:

```bash
claude plugins add home-assistant-assistant
```

### Setup

Run the connection wizard:

```
/ha-connect
```

This will:
1. Guide you through creating a Long-Lived Access Token in HA
2. Store your credentials securely
3. Validate the connection
4. Show you a summary of your entities

**That's it!** Start creating automations:

```
"Create an automation that turns on the kitchen light when motion is detected"
```

## Commands

| Command | Description |
|---------|-------------|
| `/ha-connect` | Set up connection to Home Assistant |
| `/ha-deploy` | Validate and deploy pending changes |
| `/ha-rollback` | Revert to a previous configuration state |

## Usage Examples

### Automations

**Motion-activated lighting**
```
"When motion is detected in the garage, turn on the garage light.
Turn it off 5 minutes after motion stops."
```

**Time-based schedules**
```
"Every weekday at 7:00 AM, gradually increase bedroom light brightness
from 0 to 100% over 10 minutes"
```

**Presence detection**
```
"When everyone leaves home, turn off all lights, set thermostat to away mode,
and lock all doors"
```

**Multi-condition logic**
```
"If the front door has been open for more than 5 minutes and the
temperature outside is below 40°F, send me a notification"
```

### Scripts

**Multi-step sequences**
```
"Create a 'Goodnight' script that: locks all doors, closes the garage,
turns off all lights except the bedroom, and sets the thermostat to 68°F"
```

**Gradual transitions**
```
"Create a script that slowly dims the living room lights to 0% over 30 seconds"
```

### Scenes

**Mood presets**
```
"Create a 'Romantic Dinner' scene: dining room light at 30% warm white,
living room lights off, kitchen under-cabinet lights at 20%"
```

**Activity modes**
```
"Create a 'Work From Home' scene: office light on at 80% cool white,
office fan on medium, living room blinds closed"
```

### Troubleshooting

**Diagnosing issues**
```
"My hallway light automation hasn't been working. Can you figure out why?"
```

**Checking history**
```
"Did my 'Away Mode' automation trigger when I left this morning?"
```

## Configuration

Settings are stored in `.claude/home-assistant-assistant.md`. Create this file or run `/ha-connect` to generate a template.

### Available Options

| Setting | Default | Description |
|---------|---------|-------------|
| `ha_url` | - | Your Home Assistant URL |
| `auto_deploy` | `false` | Skip confirmation when deploying |
| `auto_commit` | `true` | Automatically commit after creating |
| `auto_push` | `true` | Push to remote after commit |
| `auto_reload` | `true` | Reload HA services automatically |
| `validate_on_edit` | `true` | Validate while creating |
| `validate_on_deploy` | `true` | Validate before deployment |
| `skip_entity_confirmation` | `false` | Skip entity confirmation prompts |
| `check_conflicts` | `true` | Check for conflicting automations |
| `log_history_hours` | `24` | Hours of logs to analyze for troubleshooting |
| `history_count` | `5` | Number of commits shown in rollback |
| `create_backup` | `false` | Create backup before deploying |

### Example Configuration

```markdown
# Home Assistant Assistant Settings

ha_url: http://homeassistant.local:8123
auto_deploy: false
auto_commit: true
auto_push: true
commit_prefix: "[HA]"
```

## How It Works

### Architecture

The plugin consists of:

- **Skills** for creating automations, scripts, and scenes
- **Agents** for entity resolution, config validation, and log analysis
- **Commands** for connection setup, deployment, and rollback

### Entity Resolution

When you say "hallway light," the plugin:

1. Searches your HA entities by name, room, and type
2. Shows you the matches for confirmation
3. Uses the correct entity ID in the generated YAML

### Validation Pipeline

Before any config reaches Home Assistant:

1. **YAML Syntax** - Parses the YAML to catch syntax errors
2. **Entity Check** - Verifies every referenced entity exists
3. **Service Check** - Confirms all service calls are valid
4. **HA Config Check** - Uses HA's built-in validator

Errors include line numbers, suggestions, and typo detection.

## Requirements

| Requirement | Details |
|-------------|---------|
| Home Assistant | Modern version with API access |
| Claude Code | Latest version |
| hass-cli | `pip install homeassistant-cli` |
| Git | Config directory must be a git repo |
| Network | Client must reach HA instance |

## Troubleshooting

### "hass-cli not found"

Install it with:
```bash
pip install homeassistant-cli
```

### "Connection refused" or "401 Unauthorized"

1. Verify your HA URL is correct and accessible
2. Check that your Long-Lived Access Token is valid
3. Ensure the token has appropriate permissions

### "Entity not found"

The entity ID may have changed or the device is unavailable. Run:
```
"List all entities matching 'living room'"
```

### Automation not triggering

Ask Claude to diagnose:
```
"Why isn't my [automation name] working?"
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT

---

**Made for the Home Assistant community.**
