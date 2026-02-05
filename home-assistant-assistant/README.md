# Home Assistant Toolkit for Claude Code

A comprehensive Claude Code plugin for Home Assistant end-users. Generate configurations, manage naming, deploy changes, and get smart suggestions for your smart home.

## Features

### Commands

| Command | Description |
|---------|-------------|
| `/ha:onboard` | First-time setup wizard - configure hass-cli, git sync, and verify connectivity |
| `/ha:setup` | Reconfigure settings (URL, token, paths) |
| `/ha:new-device` | Guided workflow when adding new devices |
| `/ha:generate <type>` | Generate YAML configs (automation, dashboard, scene, script, template) |
| `/ha:validate` | Check configuration for errors |
| `/ha:deploy` | Push changes to Home Assistant via git |
| `/ha:audit-naming` | Analyze naming consistency across entities |
| `/ha:plan-naming` | Create a detailed rename plan |
| `/ha:apply-naming` | Execute the naming plan |
| `/ha:analyze` | Get analysis and improvement suggestions |

### Skills

The plugin provides specialized knowledge in:
- **ha-config** - Configuration structure, packages, secrets
- **ha-automation** - Automation triggers, conditions, actions
- **ha-lovelace** - Dashboard design, card types, layouts
- **ha-jinja** - Template syntax and patterns
- **ha-naming** - Naming conventions and best practices
- **ha-devices** - Device types, integrations, entity management

### Agents

- **config-debugger** - Analyzes and fixes configuration errors
- **naming-analyzer** - Deep analysis of naming patterns and dependencies
- **device-advisor** - Helps set up new devices with automations and dashboards

## Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    home-assistant-assistant Plugin                     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  YAML Configs (Git)      â”‚  Registry Ops (hass-cli)    â”‚
â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€   â”‚  â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€      â”‚
â”‚  â€¢ Edit locally          â”‚  â€¢ Entity renaming          â”‚
â”‚  â€¢ Git push to remote    â”‚  â€¢ Device management        â”‚
â”‚  â€¢ HA Git Pull add-on    â”‚  â€¢ Area assignments         â”‚
â”‚  â€¢ Auto-reload           â”‚  â€¢ State queries            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
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
4. Use `/ha:generate automation "your description"` to create automations

## Configuration

Settings are stored in `.claude/home-assistant-assistant.local.md` (gitignored).

```yaml
---
ha_url: "http://homeassistant.local:8123"
config_repo_path: "/path/to/your/ha-config"
config_repo_remote: "git@github.com:user/ha-config.git"
setup_complete: true
---
```

## Workflow Examples

### Adding a New Device

```
/ha:new-device motion sensor in kitchen
```

The plugin will:
1. Suggest naming following your conventions
2. Recommend automations (motion-triggered lights)
3. Offer dashboard integration
4. Check for related devices

### Generating an Automation

```
/ha:generate automation turn on kitchen lights when motion detected after sunset
```

### Deploying Changes

```
/ha:deploy
```

Commits your changes, pushes to git, and Home Assistant pulls the updates.

### Fixing Naming Issues

```
/ha:audit-naming        # See what's inconsistent
/ha:plan-naming         # Create a rename plan
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
