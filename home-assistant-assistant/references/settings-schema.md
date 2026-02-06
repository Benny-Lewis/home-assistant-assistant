# Settings Schema Reference

This document defines the unified settings format for the HA Toolkit plugin.

## Settings File Location

Settings are stored in `.claude/settings.local.json` in the user's Home Assistant config repository.

**Important:**
- This file is user-managed, not shipped with the plugin
- Must be gitignored (add `.claude/` to `.gitignore`)
- Created on first run of `/ha:onboard`

## Schema

```json
{
  "ha_url": "string (required) - Home Assistant URL",
  "ha_token_env": "string (default: HASS_TOKEN) - env var name containing token",
  "config_path": "string (optional) - path to HA config directory",
  "auto_deploy": "boolean (default: false) - auto-deploy after generate",
  "auto_commit": "boolean (default: false) - auto-commit after changes",
  "git_remote": "string (optional) - git remote for push",
  "git_branch": "string (optional) - git branch for commits"
}
```

## Example

```json
{
  "ha_url": "http://homeassistant.local:8123",
  "ha_token_env": "HASS_TOKEN",
  "config_path": "/config",
  "auto_deploy": false,
  "auto_commit": false
}
```

## Migration from Legacy Formats

### From `.claude/ha-toolkit.local.md`

The old markdown format used `ha_url` and `ha_token` keys directly. Migrate by:
1. Reading values from the `.md` file
2. Creating `.claude/settings.local.json` with the schema above
3. Setting `ha_token_env` to `HASS_TOKEN` (prefer env vars over stored tokens)
4. Removing the old `.md` file

### From `.claude/home-assistant-assistant.md`

Same migration process. The old format also supported `auto_deploy` and `auto_commit`.

## Security Notes

- **Never store tokens directly** - use `ha_token_env` to reference an environment variable
- **Never print tokens** - even when echoing settings back to the user
- The `.claude/` directory must be gitignored to prevent accidental token exposure
