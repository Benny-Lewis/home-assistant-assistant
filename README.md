# Home Assistant Assistant

A Claude Code plugin for natural language management of Home Assistant configurations.

## Features

- Create automations, scripts, and scenes through conversation
- Validate configurations before deployment
- Git-based version control with easy rollback
- Troubleshoot why automations didn't trigger
- Works with your existing HA config repository

## Prerequisites

1. Home Assistant instance with API access
2. hass-cli installed: `pip install homeassistant-cli`
3. Your HA config directory as a git repository

## Setup

1. Install the plugin in Claude Code
2. Run `/ha-connect` to configure your connection
3. Start creating automations!

## Commands

- `/ha-connect` - Set up connection to Home Assistant
- `/ha-deploy` - Deploy changes with validation
- `/ha-rollback` - Revert to a previous configuration

## Example Usage

"When motion is detected in the hallway, turn on the hallway light for 2 minutes, but only after sunset"

"Create a script that turns off all lights and locks the front door"

"Why didn't my bedroom automation trigger last night?"

## Configuration

Settings are stored in `.claude/home-assistant-assistant.md`:

- `auto_deploy`: Skip confirmation when deploying (default: false)
- `auto_push`: Push to remote after commit (default: true)
- `validate_on_edit`: Validate while creating (default: true)

See templates/home-assistant-assistant.md for all options.
