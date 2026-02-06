# Home Assistant Toolkit for Claude Code

A comprehensive Claude Code plugin for Home Assistant end-users. Generate configurations, manage naming, deploy changes, and get smart suggestions for your smart home.

## Features

### Skills (Slash Commands)

| Skill | Description |
|-------|-------------|
| `/ha:onboard` | First-time setup wizard - configure hass-cli, git sync, connection, and settings |
| `/ha:validate` | Check configuration for errors with evidence tables |
| `/ha:deploy` | Push changes to Home Assistant via git, or rollback |
| `/ha:analyze` | Get analysis and improvement suggestions |
| `/ha:apply-naming` | Execute a naming plan to rename entities |

The plugin also provides domain knowledge skills that activate automatically:
- **ha-automations** - Automation triggers, conditions, actions
- **ha-scripts** - Script sequences and modes
- **ha-scenes** - Scene creation with capability checks
- **ha-config** - Configuration structure, packages, secrets
- **ha-lovelace** - Dashboard design, card types, layouts
- **ha-jinja** - Template syntax and patterns
- **ha-naming** - Naming conventions, audit, and rename planning
- **ha-devices** - Device types, integrations, new device workflow
- **ha-troubleshooting** - Debugging and log analysis
- **ha-resolver** - Entity resolution (used by agents)

### Agents

- **config-debugger** - Analyzes and fixes configuration errors
- **naming-analyzer** - Deep analysis of naming patterns and dependencies
- **device-advisor** - Helps set up new devices with automations and dashboards

## Architecture

```
+----------------------------------------------------------+
|                    home-assistant-assistant Plugin        |
+----------------------------------------------------------+
|  YAML Configs (Git)      |  Registry Ops (hass-cli)     |
|  ---------------------   |  ---------------------        |
|  - Edit locally          |  - Entity renaming            |
|  - Git push to remote    |  - Device management          |
|  - HA Git Pull add-on    |  - Area assignments           |
|  - Auto-reload           |  - State queries              |
+----------------------------------------------------------+
```

## Prerequisites

### On Your Local Machine
- **Git** - For version control of HA configs
- **hass-cli** - Home Assistant CLI for API access
  ```bash
  pip install homeassistant-cli
  ```

### On Home Assistant
- **Git Pull Add-on** - To sync configs from your git repository
- **Long-Lived Access Token** - For hass-cli authentication

## Quick Start

1. Install the plugin
2. Run `/ha:onboard` to set up your environment
3. Try `/ha:analyze` to get suggestions for your setup
4. Ask me to create automations, scripts, or scenes by describing what you want

## Configuration

Settings are stored in `.claude/settings.local.json` (gitignored).

## Workflow Examples

### Adding a New Device

```
Tell Claude: "I just added a motion sensor in the kitchen"
```

The plugin will:
1. Suggest naming following your conventions
2. Recommend automations (motion-triggered lights)
3. Offer dashboard integration
4. Check for related devices

### Creating an Automation

```
Tell Claude: "Create an automation to turn on kitchen lights when motion is detected after sunset"
```

### Deploying Changes

```
/ha:deploy
```

Commits your changes, pushes to git, and Home Assistant pulls the updates.

### Fixing Naming Issues

```
/ha:naming audit        # See what's inconsistent
/ha:naming plan         # Create a rename plan
/ha:apply-naming        # Execute the plan
```

## Environment Variables

For hass-cli to work, set these environment variables:

```bash
export HASS_SERVER="http://homeassistant.local:8123"
export HASS_TOKEN="your-long-lived-access-token"
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR on the repository.
